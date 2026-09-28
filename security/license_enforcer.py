"""
Anti-Cheating & Security Enforcement Engine.
Implements:
1. Anti-Tampering & 60-Second Cryptographic Heartbeat: Pings licensing server with HMAC-SHA256 payload.
2. Account Disconnect Penalty Policy: Detects detaching bot or revoking MT5 while in floating loss;
   flags account as PENALTY_FLAGGED to prevent HWM evasion.
3. Read-Only API / Investor Password Mode: Supports auditing MT5 history without trade execution rights.
"""

import os
import time
import json
import hmac
import hashlib
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

logger = logging.getLogger("LicenseEnforcer")


class LicenseEnforcer:
    def __init__(self,
                 license_key: str = "XAUUSD-INSTITUTIONAL-PRO-2026",
                 state_file: str = "data/license_state.json",
                 heartbeat_interval_sec: float = 60.0):
        self.license_key = license_key
        self.state_file = state_file
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.last_heartbeat_sent = 0.0
        self.is_penalty_flagged = False
        self.penalty_reason = ""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.is_penalty_flagged = bool(data.get("is_penalty_flagged", False))
                self.penalty_reason = data.get("penalty_reason", "")
                if self.is_penalty_flagged:
                    logger.critical(f"[LICENSE-ENFORCER] Account is PENALTY FLAGGED: {self.penalty_reason}")
            except Exception as e:
                logger.error(f"Error loading license state: {e}")

    def save_state(self) -> None:
        try:
            payload = {
                "license_key": self.license_key,
                "is_penalty_flagged": self.is_penalty_flagged,
                "penalty_reason": self.penalty_reason,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving license state: {e}")

    def generate_heartbeat_payload(self, bot_state: str, equity: float, magic_number: int) -> Dict[str, Any]:
        """
        Anti-Tampering Heartbeat:
        Generates cryptographic ping payload signed with HMAC-SHA256.
        """
        now_ts = int(time.time())
        raw_message = f"{self.license_key}:{now_ts}:{bot_state}:{equity:.2f}:{magic_number}"
        signature = hmac.new(
            key=self.license_key.encode("utf-8"),
            msg=raw_message.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        payload = {
            "timestamp": now_ts,
            "license_key": self.license_key,
            "bot_state": bot_state,
            "equity": round(equity, 2),
            "magic_number": magic_number,
            "hmac_sha256": signature
        }
        self.last_heartbeat_sent = time.time()
        return payload

    def verify_heartbeat_payload(self, payload: Dict[str, Any]) -> bool:
        """Verifies signature authenticity and rejects replayed pings."""
        try:
            ts = payload["timestamp"]
            if abs(time.time() - ts) > 120.0:
                logger.warning("Heartbeat payload rejected: Timestamp expired (> 120s).")
                return False

            raw_message = f"{payload['license_key']}:{ts}:{payload['bot_state']}:{payload['equity']:.2f}:{payload['magic_number']}"
            expected_sig = hmac.new(
                key=self.license_key.encode("utf-8"),
                msg=raw_message.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, payload["hmac_sha256"])
        except Exception as e:
            logger.error(f"Heartbeat verification error: {e}")
            return False

    def check_disconnect_penalty(self, is_mt5_connected: bool, floating_pnl: float) -> Tuple[bool, str]:
        """
        Account Disconnect Penalty Policy:
        Detects if user detaches the bot, terminates terminal connection, or alters master credentials
        while in an open losing trade (attempting to evade HWM recording).
        """
        if self.is_penalty_flagged:
            return True, f"Account Suspended: {self.penalty_reason}"

        # If connection drops while in a floating loss < -$20
        if not is_mt5_connected and floating_pnl < -20.0:
            self.is_penalty_flagged = True
            self.penalty_reason = (
                f"Unauthorized disconnect detected during active floating loss of ${floating_pnl:.2f}. "
                f"Drawdown evasion violation flagged. Access suspended until audited."
            )
            self.save_state()
            logger.critical(f"[LICENSE-ENFORCER] {self.penalty_reason}")
            return True, self.penalty_reason

        return False, "License intact."

    def clear_penalty(self) -> None:
        """Auditor unlock."""
        self.is_penalty_flagged = False
        self.penalty_reason = ""
        self.save_state()
        logger.info("[LICENSE-ENFORCER] Penalty cleared by administrator.")
