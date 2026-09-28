"""
Stripe Payment Gateway & Webhook Verification Engine.
Handles:
1. Stripe Checkout Sessions (SaaS Monthly/Annual, Lifetime, Gas Wallet Top-Up).
2. Cryptographic Webhook Signature Verification (HMAC-SHA256 over timestamp + payload).
3. Lifecycle Webhook Ingestion: checkout.session.completed, invoice.paid, customer.subscription.deleted.
4. Offline / Sandbox simulation mode.
"""

import time
import hmac
import hashlib
import json
import uuid
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta
from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus
from licensing.database import LicensingDatabase

logger = logging.getLogger("StripeGateway")


class StripeGateway:
    def __init__(self,
                 db: LicensingDatabase,
                 api_key: str = "sk_test_mock_xauusd_bot",
                 webhook_secret: str = "whsec_mock_secret_gold_bot"):
        self.db = db
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    def create_checkout_session(self,
                                user_email: str,
                                tier: BillingTier,
                                gas_amount_usd: Optional[float] = None,
                                mt5_account_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generates a checkout session payload/URL.
        In live production, calls https://api.stripe.com/v1/checkout/sessions.
        In sandbox/demo, returns a structured checkout session response.
        """
        session_id = f"cs_test_{uuid.uuid4().hex[:18]}"
        user_clean = user_email.lower().strip()

        # Pricing matrix
        pricing = {
            BillingTier.SAAS_MONTHLY: (50.00, "XAUUSD Bot SaaS Monthly Subscription ($50/mo)"),
            BillingTier.SAAS_ANNUAL: (450.00, "XAUUSD Bot SaaS Annual Subscription ($450/yr)"),
            BillingTier.PROFIT_SHARE: (gas_amount_usd or 100.00, f"Gas Wallet Pre-Funded Top-Up (${gas_amount_usd or 100.00:.2f})"),
            BillingTier.LIFETIME_PERPETUAL: (999.00, "XAUUSD Bot Lifetime License ($999)")
        }

        amount, desc = pricing.get(tier, (50.00, "XAUUSD Bot License"))

        checkout_url = f"https://checkout.stripe.com/c/pay/{session_id}"
        logger.info(f"[STRIPE] Generated Checkout Session: {session_id} for {user_clean} ({desc})")

        return {
            "session_id": session_id,
            "checkout_url": checkout_url,
            "amount_usd": amount,
            "currency": "usd",
            "tier": tier.value,
            "user_email": user_clean,
            "mt5_account_id": mt5_account_id,
            "status": "open"
        }

    def verify_webhook_signature(self,
                                 payload_bytes: bytes,
                                 signature_header: str,
                                 tolerance_sec: int = 300) -> bool:
        """
        Verifies Stripe-Signature: t=1234567890,v1=abcdef...
        Uses HMAC-SHA256(webhook_secret, timestamp + '.' + payload)
        """
        try:
            parts = dict(item.split("=", 1) for item in signature_header.split(","))
            timestamp = int(parts.get("t", 0))
            received_sig = parts.get("v1", "")

            # Check timestamp freshness
            now = int(time.time())
            if abs(now - timestamp) > tolerance_sec:
                logger.warning(f"[STRIPE] Webhook timestamp expired: {timestamp} vs current {now}")
                return False

            signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
            expected_sig = hmac.new(
                key=self.webhook_secret.encode("utf-8"),
                msg=signed_payload,
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, received_sig)
        except Exception as e:
            logger.error(f"[STRIPE] Signature verification exception: {e}")
            return False

    def generate_sandbox_signature(self, payload_bytes: bytes) -> str:
        """Helper to create a valid Stripe-Signature header for testing/sandbox."""
        timestamp = int(time.time())
        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        sig = hmac.new(
            key=self.webhook_secret.encode("utf-8"),
            msg=signed_payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={sig}"

    def process_webhook(self, event_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Ingests parsed Stripe webhook event.
        Dispatches to appropriate entitlement actions.
        """
        event_type = event_data.get("type", "")
        data_object = event_data.get("data", {}).get("object", {})

        logger.info(f"[STRIPE-WEBHOOK] Ingesting event: {event_type}")

        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(data_object)

        elif event_type == "invoice.paid":
            return self._handle_invoice_paid(data_object)

        elif event_type == "customer.subscription.deleted":
            return self._handle_subscription_deleted(data_object)

        elif event_type == "invoice.payment_failed":
            return self._handle_payment_failed(data_object)

        return True, f"Event {event_type} ignored (no entitlement action required)."

    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Tuple[bool, str]:
        user_email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        if not user_email:
            return False, "Missing customer_email in checkout session."

        metadata = session.get("metadata", {})
        tier_str = metadata.get("tier", BillingTier.SAAS_MONTHLY.value)
        tier = BillingTier(tier_str)
        mt5_account_id = int(metadata["mt5_account_id"]) if "mt5_account_id" in metadata and metadata["mt5_account_id"] else None
        gas_amount = float(metadata.get("gas_topup_amount_usd", 0.0))
        txn_id = session.get("id", f"txn_{uuid.uuid4().hex[:12]}")
        amount_total = float(session.get("amount_total", 5000)) / 100.0  # Stripe cents to dollars

        self.db.record_payment(
            transaction_id=txn_id,
            user_email=user_email,
            gateway=PaymentGateway.STRIPE,
            amount_usd=amount_total,
            tier=tier,
            status=PaymentStatus.COMPLETED
        )

        # Gas Wallet Top-Up
        if tier == BillingTier.PROFIT_SHARE or gas_amount > 0:
            topup_amt = gas_amount if gas_amount > 0 else amount_total
            # Find user's active profit-share license
            licenses = self.db.get_licenses_by_email(user_email)
            target_lic = next((l for l in licenses if l.tier == BillingTier.PROFIT_SHARE), None)
            if not target_lic:
                lic_key = f"XAU-GAS-{uuid.uuid4().hex[:12].upper()}"
                self.db.create_license(
                    license_key=lic_key,
                    user_email=user_email,
                    tier=BillingTier.PROFIT_SHARE,
                    mt5_account_id=mt5_account_id,
                    gas_balance_usd=topup_amt
                )
            else:
                self.db.topup_gas(target_lic.license_key, topup_amt)
            return True, f"Gas wallet credited with ${topup_amt:.2f}."

        # SaaS or Lifetime License
        existing = self.db.get_licenses_by_email(user_email)
        active_lic = next((l for l in existing if l.tier == tier), None)

        if tier == BillingTier.LIFETIME_PERPETUAL:
            lic_key = f"XAU-LIFE-{uuid.uuid4().hex[:12].upper()}"
            self.db.create_license(
                license_key=lic_key,
                user_email=user_email,
                tier=BillingTier.LIFETIME_PERPETUAL,
                mt5_account_id=mt5_account_id,
                expires_at=None
            )
            return True, f"Created Lifetime license {lic_key}."

        else:
            # SaaS (Monthly or Annual)
            days = 365 if tier == BillingTier.SAAS_ANNUAL else 30
            if active_lic:
                self.db.extend_license(active_lic.license_key, days)
                return True, f"Extended SaaS license {active_lic.license_key} by {days} days."
            else:
                lic_key = f"XAU-SAAS-{uuid.uuid4().hex[:12].upper()}"
                now = datetime.now(timezone.utc)
                exp = now + timedelta(days=days)
                self.db.create_license(
                    license_key=lic_key,
                    user_email=user_email,
                    tier=tier,
                    mt5_account_id=mt5_account_id,
                    expires_at=exp
                )
                return True, f"Provisioned new SaaS license {lic_key} expiring {exp.isoformat()}."

    def _handle_invoice_paid(self, invoice: Dict[str, Any]) -> Tuple[bool, str]:
        user_email = invoice.get("customer_email")
        if not user_email:
            return False, "Missing customer_email on invoice."

        # Recurring billing renewal
        licenses = self.db.get_licenses_by_email(user_email)
        saas_lic = next((l for l in licenses if l.tier in (BillingTier.SAAS_MONTHLY, BillingTier.SAAS_ANNUAL)), None)
        if saas_lic:
            days = 365 if saas_lic.tier == BillingTier.SAAS_ANNUAL else 30
            self.db.extend_license(saas_lic.license_key, days)
            self.db.record_payment(
                transaction_id=invoice.get("id", f"inv_{uuid.uuid4().hex[:8]}"),
                user_email=user_email,
                gateway=PaymentGateway.STRIPE,
                amount_usd=float(invoice.get("amount_paid", 5000)) / 100.0,
                tier=saas_lic.tier,
                status=PaymentStatus.COMPLETED
            )
            return True, f"Subscription renewed: Extended {saas_lic.license_key} by {days} days."

        return False, f"No active SaaS license found to renew for {user_email}."

    def _handle_subscription_deleted(self, sub: Dict[str, Any]) -> Tuple[bool, str]:
        # Cancelled or lapsed subscription
        customer_id = sub.get("customer")
        # In mock/sandbox, search licenses by metadata or email
        metadata = sub.get("metadata", {})
        user_email = metadata.get("email")

        if user_email:
            licenses = self.db.get_licenses_by_email(user_email)
            for lic in licenses:
                if lic.tier in (BillingTier.SAAS_MONTHLY, BillingTier.SAAS_ANNUAL):
                    self.db.update_license_status(lic.license_key, LicenseStatus.EXPIRED)
                    logger.warning(f"[STRIPE] Subscription deleted. License {lic.license_key} expired.")
            return True, f"Marked licenses expired for {user_email}."

        return False, "Could not determine user for subscription deletion."

    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> Tuple[bool, str]:
        user_email = invoice.get("customer_email")
        logger.warning(f"[STRIPE] Recurring invoice payment failed for {user_email}.")
        self.db.log_audit("PAYMENT_FAILED", None, f"Invoice {invoice.get('id')} failed for {user_email}.")
        return True, "Payment failure recorded."
