"""
Layer 4 Defense: Telegram Multi-Factor Authentication (MFA) Webhook.
Requires interactive secondary authorization via mobile Telegram
for any order risking more than a defined threshold ($250 or > 0.50 lots).
"""

import time
import secrets
import logging
from typing import Optional, Dict, Any, Tuple
from telemetry.telegram_bot import TelegramBot

logger = logging.getLogger("MFAWebhook")


class MFAWebhook:
    def __init__(self, telegram_bot: TelegramBot, mfa_risk_threshold_usd: float = 250.0, timeout_sec: int = 30):
        self.telegram = telegram_bot
        self.threshold_usd = mfa_risk_threshold_usd
        self.timeout_sec = timeout_sec
        self.pending_auths: Dict[str, Dict[str, Any]] = {}

    def requires_mfa(self, risk_usd: float, lots: float) -> bool:
        return risk_usd >= self.threshold_usd or lots >= 0.50

    def request_authorization(self, direction: str, symbol: str, lots: float,
                              entry: float, sl: float, tp: float, risk_usd: float) -> str:
        """Generates a secure 6-digit one-time token and sends Telegram MFA alert."""
        token = f"{secrets.randbelow(900000) + 100000}"
        expires_at = time.time() + self.timeout_sec

        self.pending_auths[token] = {
            "direction": direction, "symbol": symbol, "lots": lots,
            "entry": entry, "sl": sl, "tp": tp, "risk_usd": risk_usd,
            "expires_at": expires_at, "status": "PENDING"
        }

        if self.telegram.is_enabled:
            msg = (
                f"🚨 *MFA TRADE AUTHORIZATION REQUIRED*\n"
                f"• *Action:* `{direction} {lots:.2f} {symbol}`\n"
                f"• *Entry:* `${entry:.2f}` | *SL:* `${sl:.2f}` | *TP:* `${tp:.2f}`\n"
                f"• *Risk Capital:* `${risk_usd:.2f}`\n\n"
                f"👉 To approve, reply with: `/auth_{token}` within {self.timeout_sec} seconds."
            )
            self.telegram.send_message(msg)
            logger.info(f"MFA Challenge sent to Telegram for {direction} {lots} {symbol}. Token: {token}")
        else:
            logger.warning("Telegram disabled. MFA auto-approving in local demo mode.")
            self.pending_auths[token]["status"] = "APPROVED"

        return token

    def check_authorization(self, token: str) -> Tuple[bool, str]:
        """Polls token status."""
        auth = self.pending_auths.get(token)
        if not auth:
            return False, "Token not found."

        if auth["status"] == "APPROVED":
            del self.pending_auths[token]
            return True, "Trade Authorized via MFA."

        if time.time() > auth["expires_at"]:
            del self.pending_auths[token]
            return False, "MFA Authorization Timed Out (30s). Order Discarded."

        return False, "Pending Authorization."
