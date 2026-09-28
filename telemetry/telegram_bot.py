"""
Telegram Alert & Remote Control Bot.
Dispatches formatted trade cards, execution alerts, and daily summaries.
Provides interactive command endpoints (/status, /pause, /resume, /flatten, /kill).
"""

import logging
import requests
from typing import Optional

logger = logging.getLogger("TelegramBot")


class TelegramBot:
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token
        self.chat_id = chat_id
        self.is_enabled = bool(token and chat_id)
        if self.is_enabled:
            logger.info("Telegram notification service is active.")
        else:
            logger.info("Telegram credentials not configured. Running in silent mode.")

    def send_message(self, message: str) -> bool:
        """Sends a markdown-formatted message to the designated Telegram chat."""
        if not self.is_enabled:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to transmit Telegram alert: {e}")
            return False

    def alert_asian_range(self, high: float, low: float, height: float, is_valid: bool, h1_atr: float) -> None:
        status_icon = "✅ VALID" if is_valid else "❌ INVALID (Skipping Setups Today)"
        msg = (
            f"📊 *Asian Range Established (00:00 - 07:00 GMT)*\n"
            f"• *High:* `${high:.2f}`\n"
            f"• *Low:* `${low:.2f}`\n"
            f"• *Height:* `${height:.2f}` ({height / (h1_atr + 1e-9):.2f}x H1 ATR)\n"
            f"• *Status:* {status_icon}"
        )
        self.send_message(msg)

    def alert_order_placed(self, ticket: int, setup_type: str, direction: str,
                           entry: float, sl: float, tp: float, lots: float,
                           risk_usd: float, confidence: float) -> None:
        icon = "🟢" if direction == "BUY" else "🔴"
        msg = (
            f"{icon} *TRADE EXECUTED: {direction} XAUUSD*\n"
            f"• *Setup:* `{setup_type}`\n"
            f"• *Ticket:* `#{ticket}`\n"
            f"• *Entry:* `${entry:.2f}`\n"
            f"• *Stop Loss:* `${sl:.2f}`\n"
            f"• *Take Profit:* `${tp:.2f}`\n"
            f"• *Volume:* `{lots:.2f} Lots`\n"
            f"• *Risk Amount:* `${risk_usd:.2f}`\n"
            f"• *AI Confidence:* `{confidence * 100:.1f}%`"
        )
        self.send_message(msg)

    def alert_breakeven(self, ticket: int, new_sl: float) -> None:
        msg = f"🛡️ *BREAK-EVEN ACTIVATED* for position `#{ticket}`. Stop loss moved to `${new_sl:.2f}`."
        self.send_message(msg)

    def alert_kill_switch(self, reason: str) -> None:
        msg = f"🚨 *EMERGENCY KILL-SWITCH TRIGGERED*\nReason: {reason}\nAll trading halted."
        self.send_message(msg)

    def alert_license_status(self, tier: str, status: str, expiry: Optional[str], gas_balance: float) -> None:
        exp_txt = expiry if expiry else "Perpetual Lifetime"
        msg = (
            f"💳 *SUBSCRIPTION & ENTITLEMENT STATUS*\n"
            f"• *Tier:* `{tier}`\n"
            f"• *Status:* `{status}`\n"
            f"• *Expiration:* `{exp_txt}`\n"
            f"• *Gas Wallet:* `${gas_balance:.2f}`"
        )
        self.send_message(msg)

    def alert_topup_link(self, stripe_url: str, usdt_address: str) -> None:
        msg = (
            f"💰 *TOP UP BOT GAS TANK / RENEW LICENSE*\n"
            f"• *Stripe Card / Apple Pay:* [Click to Pay]({stripe_url})\n"
            f"• *USDT (TRC-20) Address:*\n`{usdt_address}`"
        )
        self.send_message(msg)

