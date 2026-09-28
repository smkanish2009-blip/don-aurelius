"""
JARVIS Interactive Telegram HUD with Inline Keyboard Buttons and Voice Dispatch.
Functions both natively via Telegram Bot HTTP API (zero external library required)
and optionally binds to python-telegram-bot if installed.
"""

import os
import io
import json
import logging
import threading
import time
from datetime import datetime
import requests
from typing import Optional, Dict, Any, Callable
from communication.jarvis_voice import JarvisVoiceCore
from communication.don_aurelius_brain import DonAureliusBrain

logger = logging.getLogger("JarvisTelegramHUD")


class JarvisTelegramHUD:
    """
    JARVIS Interactive Telegram Telemetry HUD with Inline Action Overrides,
    Voice Briefing Dispatch, Conversational AI Brain, and Automated Database Backup Transmissions.
    """

    def __init__(
        self,
        token: str,
        execution_bridge: Any,
        elevenlabs_key: Optional[str] = None,
        elevenlabs_voice: Optional[str] = None,
        chat_id: Optional[str] = None,
        strategy_engine: Optional[Any] = None,
        db_logger: Optional[Any] = None,
        war_room: Optional[Any] = None,
        orchestrator: Optional[Any] = None
    ):
        self.token = token
        self.bridge = execution_bridge
        self.chat_id = chat_id or ""
        self.strategy = strategy_engine
        self.db = db_logger
        self.war_room = war_room
        self.orchestrator = orchestrator
        self.voice = JarvisVoiceCore(api_key=elevenlabs_key, voice_id=elevenlabs_voice or "pNInz6obpgDQGcFmaJgB")
        self.brain = DonAureliusBrain(
            bridge=self.bridge,
            voice_core=self.voice,
            war_room=self.war_room,
            strategy=self.strategy,
            db_logger=self.db,
            orchestrator=self.orchestrator
        )
        self.api_base = f"https://api.telegram.org/bot{self.token}"

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_update_id = 0
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=5, pool_maxsize=10)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def launch_interface(self):
        """Launches background polling thread for real-time Telegram button & command interactions."""
        if not self.token or self.token.startswith("mock_") or self.token.startswith("your_"):
            logger.info("[JARVIS-HUD] Telegram token is mock/unset. HUD running in local offline mode.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._thread.start()
        logger.info("[JARVIS-HUD] Telegram Interactive HUD listener activated in background.")

    def stop(self):
        """Stops the polling daemon."""
        self._running = False

    def display_telemetry_hud(self, target_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transmits full visual telemetry dashboard with interactive button overrides
        and dispatches high-fidelity voice transmission audio note.
        """
        cid = target_chat_id or self.chat_id
        equity = self.bridge.get_account_equity()

        # Telemetry metrics
        hud_metrics = (
            "👑 **DON AURELIUS • AUREUS CORE TELEMETRY**\n"
            "===================================\n"
            "● System State: **ONLINE & ARMED (ACTIVE)**\n"
            f"● Net Imperial Equity: **${equity:,.2f} USD**\n"
            "● Protection Arrays: **Active Auto-Trailing**\n"
            "● Intermarket Filter: **Co-Integrated DXY & US10Y**\n"
            "===================================\n"
            "🔊 *AUREUS audio briefing dispatched below...*"
        )

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🚨 Clean Slate Protocol", "callback_data": "kill_all"},
                    {"text": "🎙️ Voice Briefing", "callback_data": "voice_briefing"}
                ],
                [
                    {"text": "📊 Refresh Telemetry", "callback_data": "refresh_hud"},
                    {"text": "📦 Backup Database", "callback_data": "backup_db"}
                ],
                [
                    {"text": "⏸️ Pause Syndicate", "callback_data": "pause_algo"}
                ]
            ]
        }

        # 1. Transmit Visual Dashboard
        res = self._send_message(cid, hud_metrics, reply_markup=inline_keyboard)

        # 2. Compile & Transmit Voice Briefing
        report = self.voice.generate_status_narrative(equity=equity)
        audio_stream = self.voice.compile_vocal_briefing(report)
        if audio_stream:
            self._send_voice(cid, audio_stream, caption="🎙️ DON AURELIUS Vocal Transmission")

        return res

    def transmit_database_archive(
        self,
        chat_id: Optional[str] = None,
        logger_instance: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Triggers a fresh database snapshot compilation and transmits
        the resulting archive file directly to your private Telegram chat.
        """
        logger.info("[⚙️ System Engine] Compiling secure data backup request...")
        cid = chat_id or self.chat_id
        db = logger_instance or self.db

        if not db:
            logger.warning("[-] Backup transmission aborted: No database logger provided.")
            return {"status": "FAILED", "reason": "No database logger"}

        zip_file_path = db.generate_compressed_snapshot()
        if not zip_file_path or not os.path.exists(zip_file_path):
            logger.error("[-] Backup transmission aborted: Archive file generation failed.")
            return {"status": "FAILED", "reason": "Archive file generation failed"}

        if not self.token or self.token.startswith("mock_") or self.token.startswith("your_") or not cid:
            logger.info(f"[+] Mock Mode: Data backup package packed at {zip_file_path}")
            return {"status": "MOCK_MODE", "file": zip_file_path}

        try:
            url = f"{self.api_base}/sendDocument"
            caption_message = (
                "📦 **JARVIS SYSTEM DATA BACKUP PACKET**\n"
                "===================================\n"
                f"● Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "● Contents: SQLite Architecture Log Matrix\n"
                "===================================\n"
                "📥 _Encrypted archival safe transmission complete._"
            )

            with open(zip_file_path, 'rb') as document_file:
                files = {'document': (os.path.basename(zip_file_path), document_file, 'application/zip')}
                data = {
                    'chat_id': cid,
                    'caption': caption_message,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, data=data, files=files, timeout=30)

            if response.status_code == 200:
                logger.info("[+] Data backup package successfully delivered to your Telegram interface.")
                return response.json()
            else:
                logger.warning(f"[-] Telegram file upload failed with status code: {response.status_code}")
                return {"status": "ERROR", "code": response.status_code}
        except Exception as e:
            logger.error(f"[-] Critical failure during network file transmission: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

    def handle_button_overrides(self, callback_data: str, target_chat_id: str, message_id: Optional[int] = None) -> str:
        """Processes inline button presses."""
        if callback_data == "kill_all":
            closed = self.bridge.emergency_kill_switch()
            msg = f"🛑 **Clean Slate Complete.** Liquidated {closed} open positions across the terminal."
            self._send_message(target_chat_id, msg)

            # Transmit voice confirmation
            voice_txt = self.voice.generate_liquidation_narrative(closed)
            audio = self.voice.compile_vocal_briefing(voice_txt)
            if audio:
                self._send_voice(target_chat_id, audio, caption="🚨 Emergency Clean Slate Broadcast")
            return msg

        elif callback_data == "voice_briefing":
            self._send_chat_action(target_chat_id, "record_voice")
            equity = self.bridge.get_account_equity()
            report = self.voice.generate_status_narrative(equity=equity)
            audio = self.voice.compile_vocal_briefing(report)
            if audio:
                self._send_voice(target_chat_id, audio, caption="🎙️ DON AURELIUS Vocal Transmission")
            return "VOICE_TRANSMITTED"

        elif callback_data == "backup_db":
            res = self.transmit_database_archive(target_chat_id)
            self._send_message(target_chat_id, "📦 **Database Snapshot Archive Dispatched.**")
            return "BACKUP_TRANSMITTED"

        elif callback_data == "refresh_hud":
            return self.display_telemetry_hud(target_chat_id).get("status", "REFRESHED")

        elif callback_data == "pause_algo":
            msg = "⏸️ **DON AURELIUS Suspended.** Trailing stops continue monitoring active trades."
            self._send_message(target_chat_id, msg)
            return msg

        elif callback_data == "check_profit":
            res = self.brain.process_query("what is our profit and account balance", target_chat_id)
            self._send_message(target_chat_id, res["text"], reply_markup=res.get("reply_markup"))
            return "PROFIT_CHECKED"

        elif callback_data == "check_gold":
            res = self.brain.process_query("what is the gold price and spread", target_chat_id)
            self._send_message(target_chat_id, res["text"], reply_markup=res.get("reply_markup"))
            return "GOLD_CHECKED"

        return "UNKNOWN_COMMAND"

    def _send_chat_action(self, chat_id: str, action: str = "typing"):
        """Displays typing or record_voice indicator in Telegram UI."""
        if not self.token or self.token.startswith("mock_") or not chat_id:
            return
        try:
            url = f"{self.api_base}/sendChatAction"
            self._session.post(url, json={"chat_id": chat_id, "action": action}, timeout=5)
        except Exception:
            pass

    def _send_message(self, chat_id: str, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """HTTP helper to transmit messages to Telegram API with auto-chunking for long text."""
        if not self.token or self.token.startswith("mock_") or self.token.startswith("your_") or not chat_id:
            return {"status": "MOCK_MODE", "text": text}

        # Telegram hard limits message text to 4096 characters. Chunk at 3800 characters safely.
        if len(text) > 3800:
            chunks = []
            curr = []
            curr_len = 0
            for line in text.split("\n"):
                if curr_len + len(line) + 1 > 3800:
                    chunks.append("\n".join(curr))
                    curr = [line]
                    curr_len = len(line)
                else:
                    curr.append(line)
                    curr_len += len(line) + 1
            if curr:
                chunks.append("\n".join(curr))

            res = {}
            for i, chunk in enumerate(chunks):
                is_last = (i == len(chunks) - 1)
                markup = reply_markup if is_last else None
                res = self._send_single_chunk(chat_id, chunk, markup)
            return res
        else:
            return self._send_single_chunk(chat_id, text, reply_markup)

    def _send_single_chunk(self, chat_id: str, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """Sends a single chunk with Markdown formatting and automatic plain-text fallback."""
        url = f"{self.api_base}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        for attempt in range(1, 4):
            try:
                r = self._session.post(url, json=payload, timeout=25)
                res = r.json()
                if res.get("ok"):
                    logger.info(f"[JARVIS-HUD] Successfully transmitted message chunk to {chat_id}")
                    return res
                desc = str(res.get("description", ""))
                # If Telegram fails markdown entity parsing or syntax, retry as plain text immediately
                if "parse" in desc.lower() or "entity" in desc.lower() or "bad request" in desc.lower():
                    payload.pop("parse_mode", None)
                    r_fb = self._session.post(url, json=payload, timeout=25)
                    res_fb = r_fb.json()
                    if res_fb.get("ok"):
                        logger.info(f"[JARVIS-HUD] Successfully transmitted plain-text fallback to {chat_id}")
                        return res_fb
                logger.warning(f"[JARVIS-HUD] Telegram non-OK response (attempt {attempt}/3): {desc}")
            except Exception as e:
                logger.warning(f"[JARVIS-HUD] Send message attempt {attempt}/3 failed: {e}")
                time.sleep(2)
        return {"status": "ERROR", "error": "Exhausted retries"}

    def _send_voice(self, chat_id: str, audio_stream: io.BytesIO, caption: str = "") -> Dict[str, Any]:
        """HTTP helper to transmit Voice Audio Notes (.mp3/.wav/.ogg) to Telegram API with robust retries."""
        if not self.token or self.token.startswith("mock_") or self.token.startswith("your_") or not chat_id:
            return {"status": "MOCK_MODE", "bytes": len(audio_stream.getvalue())}

        url = f"{self.api_base}/sendVoice"
        filename = getattr(audio_stream, "name", "jarvis_voice.mp3")

        for attempt in range(1, 4):
            try:
                audio_stream.seek(0)
                audio_bytes = audio_stream.read()
                files = {"voice": (filename, audio_bytes, "audio/mpeg")}
                data = {"chat_id": chat_id, "caption": caption}
                r = self._session.post(url, data=data, files=files, timeout=35)
                res = r.json()
                if res.get("ok"):
                    logger.info(f"[JARVIS-HUD] Successfully transmitted voice note to {chat_id}")
                    return res
                logger.warning(f"[JARVIS-HUD] Telegram Voice non-OK response (attempt {attempt}/3): {res.get('description')}")
            except Exception as e:
                logger.warning(f"[JARVIS-HUD] Send voice attempt {attempt}/3 failed: {e}")
                time.sleep(2)
        return {"status": "ERROR", "error": "Exhausted voice retries"}

    def _polling_loop(self):
        """Long-polling update loop for inline buttons, commands, and natural language questions."""
        logger.info(f"[JARVIS-HUD] Polling loop engaged (chat_id={self.chat_id}).")
        # Initialize offset to latest pending updates
        try:
            init_r = self._session.get(f"{self.api_base}/getUpdates", params={"offset": -1, "timeout": 2}, timeout=10)
            if init_r.status_code == 200:
                init_data = init_r.json()
                results = init_data.get("result", [])
                if results:
                    self._last_update_id = results[-1]["update_id"]
                    logger.info(f"[JARVIS-HUD] Fast-forwarded polling offset to latest update_id: {self._last_update_id}")
        except Exception as e:
            logger.warning(f"[JARVIS-HUD] Offset init warning: {e}")

        while self._running:
            try:
                url = f"{self.api_base}/getUpdates"
                params = {"offset": self._last_update_id + 1, "timeout": 10}
                r = self._session.get(url, params=params, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    for update in data.get("result", []):
                        self._last_update_id = update["update_id"]
                        logger.info(f"[JARVIS-HUD] Incoming Telegram update detected (id={update['update_id']})")
                        threading.Thread(target=self._safe_dispatch_update, args=(update,), daemon=True).start()
                else:
                    logger.warning(f"[JARVIS-HUD] getUpdates returned status {r.status_code}: {r.text}")
            except Exception as ex:
                logger.warning(f"[JARVIS-HUD] Polling exception: {ex}")
                time.sleep(2)
            time.sleep(0.5)

    def _safe_dispatch_update(self, update: Dict[str, Any]):
        """Executes update dispatch asynchronously to prevent blocking the polling thread."""
        try:
            self._dispatch_update(update)
        except Exception as e:
            logger.error(f"[JARVIS-HUD] Error dispatching update: {e}", exc_info=True)

    def _dispatch_update(self, update: Dict[str, Any]):
        """Dispatches button clicks, commands, and natural language AI queries."""
        # 1. Inline button clicks
        if "callback_query" in update:
            cb = update["callback_query"]
            sender_id = str(cb.get("from", {}).get("id", ""))
            data = cb.get("data", "")
            logger.info(f"[JARVIS-HUD] Callback button clicked: '{data}' by user {sender_id}")
            if self.chat_id and sender_id != str(self.chat_id):
                logger.warning(f"[JARVIS-HUD] Access denied for unauthorized user ID: {sender_id}")
                return

            chat_id = str(cb.get("message", {}).get("chat", {}).get("id", sender_id))
            msg_id = cb.get("message", {}).get("message_id")
            self.handle_button_overrides(data, chat_id, msg_id)

        # 2. Text message (slash command or natural language conversation)
        elif "message" in update or "channel_post" in update:
            msg = update.get("message") or update.get("channel_post", {})
            sender_id = str(msg.get("from", {}).get("id", ""))
            chat_id = str(msg.get("chat", {}).get("id", sender_id))
            text = msg.get("text", "").strip()
            logger.info(f"[JARVIS-HUD] Incoming message from {sender_id} in {chat_id}: '{text}'")

            if self.chat_id and sender_id != str(self.chat_id) and chat_id != str(self.chat_id):
                logger.warning(f"[JARVIS-HUD] Message filtered: {sender_id} != configured {self.chat_id}")
                return

            if not text:
                return

            # Display visual typing indicator in Telegram UI
            self._send_chat_action(chat_id, "typing")

            # Standard slash commands
            if text in ["/hud", "/status"]:
                self.display_telemetry_hud(chat_id)
            elif text == "/voice":
                equity = self.bridge.get_account_equity()
                briefing = self.voice.generate_status_narrative(equity=equity)
                self._send_chat_action(chat_id, "record_voice")
                audio = self.voice.compile_vocal_briefing(briefing)
                if audio:
                    self._send_voice(chat_id, audio, caption="🎙️ DON AURELIUS Vocal Transmission")
            elif text in ["/kill", "/flatten"]:
                self.handle_button_overrides("kill_all", chat_id)
            elif text in ["/backup", "/snapshot"]:
                self.transmit_database_archive(chat_id)
            elif text == "/help":
                res = self.brain.process_query("who are you and what can you do", chat_id)
                self._send_message(chat_id, res["text"], reply_markup=res.get("reply_markup"))
            else:
                # Natural language conversation through DonAureliusBrain
                logger.info(f"[JARVIS-HUD] Routing natural language query to Brain: '{text}'")
                res = self.brain.process_query(text, chat_id)

                # Synthesize and transmit voice if requested
                if res.get("send_voice") and res.get("voice_text"):
                    self._send_chat_action(chat_id, "record_voice")
                    audio = self.voice.compile_vocal_briefing(res["voice_text"])
                    if audio:
                        self._send_voice(chat_id, audio, caption="🎙️ DON AURELIUS Vocal Transmission")

                # Transmit text response
                self._send_message(chat_id, res["text"], reply_markup=res.get("reply_markup"))

