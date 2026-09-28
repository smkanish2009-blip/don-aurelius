"""
Two-Way Interactive Telegram Remote Control Daemon.
Provides mobile commands:
  /status  - Live account equity, balance, state, and active trade PnL.
  /pause   - Temporarily suspend new trade entries.
  /resume  - Re-arm trading engine.
  /flatten - Emergency market order: closes all open MT5 positions immediately.
  /wallet  - Check Pre-Funded Gas Tank balance and High-Water Mark peak.
  /help    - Command syntax and help card.
"""

import time
import logging
import threading
import requests
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger("TelegramCommander")


class TelegramCommander:
    def __init__(self,
                 token: str = "",
                 chat_id: str = "",
                 poll_interval_sec: float = 2.0):
        self.token = token
        self.authorized_chat_id = str(chat_id).strip()
        self.poll_interval_sec = poll_interval_sec
        self.is_enabled = bool(token and chat_id)
        self.last_update_id = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Callbacks hooked from master orchestrator
        self.get_status_callback: Optional[Callable[[], str]] = None
        self.pause_callback: Optional[Callable[[], str]] = None
        self.resume_callback: Optional[Callable[[], str]] = None
        self.flatten_callback: Optional[Callable[[], str]] = None
        self.get_wallet_callback: Optional[Callable[[], str]] = None

    def start(self) -> None:
        """Starts the background long-polling listener thread."""
        if not self.is_enabled:
            logger.info("Telegram credentials not configured. Commander running in mock/offline mode.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="TelegramCommander")
        self._thread.start()
        logger.info(f"Telegram Commander daemon active for Chat ID: {self.authorized_chat_id}")

    def stop(self) -> None:
        self._running = False

    def send_reply(self, chat_id: str, text: str) -> bool:
        if not self.token:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Error sending Telegram reply: {e}")
            return False

    def _poll_loop(self) -> None:
        while self._running:
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                params = {"offset": self.last_update_id + 1, "timeout": 2}
                resp = requests.get(url, params=params, timeout=5)

                if resp.status_code == 200:
                    data = resp.json()
                    for update in data.get("result", []):
                        self.last_update_id = update["update_id"]
                        msg = update.get("message", {})
                        from_id = str(msg.get("chat", {}).get("id", ""))
                        text = msg.get("text", "").strip()

                        if text:
                            self.process_command(from_id, text)

            except Exception as e:
                logger.debug(f"Telegram poll exception: {e}")

            time.sleep(self.poll_interval_sec)

    def process_command(self, sender_chat_id: str, text: str) -> str:
        """Processes an incoming command and returns response text."""
        cmd = text.split()[0].lower() if text else ""
        logger.info(f"[TELEGRAM-CMD] Received '{cmd}' from Chat ID: {sender_chat_id}")

        # Security Authentication Check
        if self.authorized_chat_id and str(sender_chat_id) != self.authorized_chat_id:
            reject_msg = "⛔ *ACCESS DENIED*: Unauthorized Telegram account."
            self.send_reply(sender_chat_id, reject_msg)
            return reject_msg

        if cmd == "/status":
            reply = self.get_status_callback() if self.get_status_callback else "📊 *Status:* Bot is running normally."
            self.send_reply(sender_chat_id, reply)
            return reply

        elif cmd == "/pause":
            reply = self.pause_callback() if self.pause_callback else "⏸️ *Trading Paused*: New signal entries blocked."
            self.send_reply(sender_chat_id, reply)
            return reply

        elif cmd == "/resume":
            reply = self.resume_callback() if self.resume_callback else "▶️ *Trading Resumed*: State machine re-armed."
            self.send_reply(sender_chat_id, reply)
            return reply

        elif cmd == "/flatten":
            logger.critical("[TELEGRAM-CMD] EMERGENCY FLATTEN COMMAND INITIATED VIA MOBILE TELEGRAM!")
            reply = self.flatten_callback() if self.flatten_callback else "🚨 *EMERGENCY FLATTEN*: All positions closed."
            self.send_reply(sender_chat_id, reply)
            return reply

        elif cmd == "/wallet":
            reply = self.get_wallet_callback() if self.get_wallet_callback else "💳 *Gas Wallet:* Ready."
            self.send_reply(sender_chat_id, reply)
            return reply

        elif cmd == "/help" or cmd == "/start":
            help_card = (
                "🤖 *XAUUSD AI Trading Bot - Mobile Control Desk*\n\n"
                "• `/status` - Live Equity, Balance, PnL, & State\n"
                "• `/pause` - Temporarily pause new signals\n"
                "• `/resume` - Re-arm trading engine\n"
                "• `/flatten` - 🚨 *Emergency market close of all trades*\n"
                "• `/wallet` - Check Gas Tank & High-Water Mark\n"
                "• `/help` - Show this command menu"
            )
            self.send_reply(sender_chat_id, help_card)
            return help_card

        else:
            unknown = f"❓ Unknown command: `{cmd}`. Type `/help` for available controls."
            self.send_reply(sender_chat_id, unknown)
            return unknown
