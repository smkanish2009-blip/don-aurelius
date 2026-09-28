"""
Client-Side Pre-Flight Entitlement & Trade Authorization Gate.
Protects the bot against unauthorized usage, expired subscriptions, and account spoofing.
Implements:
1. Pre-flight execution gate before any MT5 order is dispatched.
2. Anti-Piracy MT5 Account ID & Machine Fingerprint locking.
3. Fail-Safe Cryptographic Offline Lease: 24-hour grace window using HMAC-SHA256 signature verification.
4. Gas Wallet integration for profit-sharing tier.
"""

import os
import time
import json
import uuid
import platform
import hmac
import hashlib
import logging
from typing import Tuple, Dict, Any, Optional
import requests

from licensing.models import BillingTier, LicenseStatus, EntitlementToken
from licensing.server import SERVER_MASTER_SIGNING_KEY

logger = logging.getLogger("EntitlementClient")


class EntitlementClient:
    def __init__(self,
                 license_key: str = "XAUUSD-INSTITUTIONAL-PRO-2026",
                 server_url: str = "http://127.0.0.1:8000",
                 lease_cache_file: str = "data/entitlement_lease.json",
                 offline_grace_period_sec: int = 86400):  # 24 hours
        self.license_key = license_key
        self.server_url = server_url.rstrip("/")
        self.lease_cache_file = lease_cache_file
        self.offline_grace_period_sec = offline_grace_period_sec
        self.cached_token: Optional[Dict[str, Any]] = None
        self.machine_fingerprint = self._generate_machine_fingerprint()
        os.makedirs(os.path.dirname(self.lease_cache_file), exist_ok=True)
        self._load_cached_lease()

    def _generate_machine_fingerprint(self) -> str:
        raw = f"{platform.node()}:{platform.machine()}:{uuid.getnode()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _load_cached_lease(self) -> None:
        if os.path.exists(self.lease_cache_file):
            try:
                with open(self.lease_cache_file, "r", encoding="utf-8") as f:
                    self.cached_token = json.load(f)
            except Exception as e:
                logger.error(f"Error loading cached lease: {e}")

    def _save_cached_lease(self, token_data: Dict[str, Any]) -> None:
        try:
            with open(self.lease_cache_file, "w", encoding="utf-8") as f:
                json.dump(token_data, f, indent=2)
            self.cached_token = token_data
        except Exception as e:
            logger.error(f"Error saving lease cache: {e}")

    def verify_token_signature(self, token: Dict[str, Any]) -> bool:
        """Verifies the HMAC-SHA256 signature stamped by the licensing server."""
        try:
            sig = token.get("hmac_signature", "")
            lic_key = token.get("license_key", "")
            tier = token.get("tier", "")
            status = token.get("status", "")
            mt5_acc = token.get("mt5_account_id") or 0
            exp = token.get("expires_at") or "none"
            gas_bal = float(token.get("gas_balance_usd", 0.0))
            allows_new = bool(token.get("allows_new_trades", True))
            ts = int(token.get("timestamp", 0))

            raw = f"{lic_key}:{tier}:{status}:{mt5_acc}:{exp}:{gas_bal:.2f}:{allows_new}:{ts}"
            expected_sig = hmac.new(
                key=SERVER_MASTER_SIGNING_KEY.encode("utf-8"),
                msg=raw.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, sig)
        except Exception as e:
            logger.error(f"Signature check failed: {e}")
            return False

    def sync_entitlement(self, mt5_account_id: int) -> Tuple[bool, Dict[str, Any], str]:
        """
        Synchronizes license entitlement with the central licensing server.
        Falls back cleanly to offline cryptographic lease if server is unreachable.
        """
        endpoint = f"{self.server_url}/api/v1/license/validate"
        payload = {
            "license_key": self.license_key,
            "mt5_account_id": mt5_account_id,
            "machine_fingerprint": self.machine_fingerprint
        }

        try:
            resp = requests.post(endpoint, json=payload, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                if self.verify_token_signature(data):
                    self._save_cached_lease(data)
                    logger.info(f"[ENTITLEMENT] Online validation SUCCESS: Tier={data.get('tier')} | Status={data.get('status')}")
                    return True, data, "Online validation passed."
                else:
                    return False, data, "Server lease signature invalid! Tampering detected."
            else:
                err_data = resp.json() if resp.headers.get("content-type") == "application/json" else {}
                reason = err_data.get("reason", f"Server HTTP {resp.status_code}")
                logger.warning(f"[ENTITLEMENT] Validation rejected: {reason}")
                return False, err_data, reason

        except Exception as e:
            logger.warning(f"[ENTITLEMENT] Server unreachable ({e}). Attempting offline grace verification...")
            return self._verify_offline_grace(mt5_account_id)

    def _verify_offline_grace(self, mt5_account_id: int) -> Tuple[bool, Dict[str, Any], str]:
        """
        Offline Grace Period Policy:
        Allows bot to trade and manage positions for up to 24 hours using a cached signed lease.
        """
        if not self.cached_token:
            return False, {}, "No cached license lease found. Initial online activation required."

        if not self.verify_token_signature(self.cached_token):
            return False, {}, "Cached lease signature is invalid or tampered with."

        cached_ts = self.cached_token.get("timestamp", 0)
        age_sec = time.time() - cached_ts

        if age_sec > self.offline_grace_period_sec:
            msg = f"Offline lease expired (Age: {age_sec/3600:.1f}h > {self.offline_grace_period_sec/3600:.1f}h). Internet reconnection required."
            logger.critical(f"[ENTITLEMENT] {msg}")
            return False, self.cached_token, msg

        # Check account match
        bound_acc = self.cached_token.get("mt5_account_id")
        if bound_acc and bound_acc != mt5_account_id:
            msg = f"Account mismatch in offline lease: Bound #{bound_acc} vs Running #{mt5_account_id}."
            return False, self.cached_token, msg

        logger.info(f"[ENTITLEMENT] Offline grace active ({age_sec/3600:.1f}h remaining). Trade execution permitted.")
        return True, self.cached_token, "Offline grace lease verified."

    def pre_flight_trade_gate(self, mt5_account_id: int) -> Tuple[bool, str]:
        """
        MANDATORY PRE-FLIGHT GATE:
        Called immediately before executing ANY trade order in MT5.
        Returns:
            (True, "Trade Authorized") if permitted,
            (False, "<Reason>") if blocked.
        """
        # Quick validation using cached/fresh token
        if self.cached_token and self.verify_token_signature(self.cached_token):
            token = self.cached_token
            # Verify account lock
            bound_acc = token.get("mt5_account_id")
            if bound_acc and bound_acc != mt5_account_id:
                return False, f"[ENTITLEMENT_REJECTED] Anti-Piracy Lock: Bot is licensed for MT5 #{bound_acc}, not #{mt5_account_id}."

            # Verify status
            status = token.get("status")
            if status in (LicenseStatus.REVOKED.value, LicenseStatus.SUSPENDED.value, LicenseStatus.EXPIRED.value):
                return False, f"[ENTITLEMENT_REJECTED] License is {status}. Renew subscription to resume trading."

            # Verify gas wallet if on Profit-Share tier
            if token.get("tier") == BillingTier.PROFIT_SHARE.value:
                gas_bal = float(token.get("gas_balance_usd", 0.0))
                if gas_bal <= 0.0:
                    return False, "[ENTITLEMENT_REJECTED] Gas balance is $0.00. Read-only mode: new trades blocked."

            if not token.get("allows_new_trades", True):
                return False, f"[ENTITLEMENT_REJECTED] New trades not permitted: {token.get('reason')}"

            return True, "Trade Authorized"

        # If no valid token cached, force sync
        ok, token, msg = self.sync_entitlement(mt5_account_id)
        if not ok:
            return False, f"[ENTITLEMENT_REJECTED] {msg}"

        return True, "Trade Authorized"

    def allows_position_management(self) -> bool:
        """Always permits server-side position trailing, stops, and emergency flattens."""
        return True
