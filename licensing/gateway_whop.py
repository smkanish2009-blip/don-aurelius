"""
Whop Marketplace Webhook & Entitlement Ingestion.
Handles:
1. Whop Creator Marketplace webhook events (membership.went_valid, membership.went_invalid).
2. Maps Whop Experience / Plan IDs to Bot Tiers.
3. Automatically provisions and terminates licenses based on community membership status.
"""

import hmac
import hashlib
import uuid
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta
from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus
from licensing.database import LicensingDatabase

logger = logging.getLogger("WhopGateway")


class WhopGateway:
    def __init__(self,
                 db: LicensingDatabase,
                 webhook_secret: str = "whopsec_mock_secret_xauusd"):
        self.db = db
        self.webhook_secret = webhook_secret

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: str) -> bool:
        """Verifies Whop webhook signature."""
        try:
            expected_sig = hmac.new(
                key=self.webhook_secret.encode("utf-8"),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_sig, signature_header.strip())
        except Exception as e:
            logger.error(f"[WHOP] Signature error: {e}")
            return False

    def generate_sandbox_signature(self, payload_bytes: bytes) -> str:
        return hmac.new(
            key=self.webhook_secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

    def process_webhook(self, event_data: Dict[str, Any]) -> Tuple[bool, str]:
        action = event_data.get("action", "")
        data = event_data.get("data", {})

        logger.info(f"[WHOP-WEBHOOK] Ingesting Whop event: {action}")

        user = data.get("user", {})
        user_email = user.get("email")
        whop_user_id = user.get("id")

        if not user_email:
            return False, "Missing user.email in Whop payload."

        if action == "membership.went_valid":
            # Membership activated or renewed
            plan = data.get("plan", {})
            plan_id = plan.get("id", "plan_gold_monthly")

            # Link user
            self.db.get_or_create_user(email=user_email, whop_user_id=whop_user_id)

            # Find or create SaaS license
            licenses = self.db.get_licenses_by_email(user_email)
            active_lic = next((l for l in licenses if l.tier == BillingTier.SAAS_MONTHLY), None)

            if active_lic:
                self.db.extend_license(active_lic.license_key, 30)
                return True, f"Whop membership valid: Extended license {active_lic.license_key} by 30 days."
            else:
                lic_key = f"XAU-WHOP-{uuid.uuid4().hex[:12].upper()}"
                now = datetime.now(timezone.utc)
                exp = now + timedelta(days=30)
                self.db.create_license(
                    license_key=lic_key,
                    user_email=user_email,
                    tier=BillingTier.SAAS_MONTHLY,
                    expires_at=exp
                )
                return True, f"Whop membership valid: Provisioned license {lic_key}."

        elif action == "membership.went_invalid":
            # Membership cancelled or expired
            licenses = self.db.get_licenses_by_email(user_email)
            for lic in licenses:
                if "WHOP" in lic.license_key or lic.tier == BillingTier.SAAS_MONTHLY:
                    self.db.update_license_status(lic.license_key, LicenseStatus.EXPIRED)
            return True, f"Whop membership invalid: Expired licenses for {user_email}."

        return True, f"Whop event {action} processed."
