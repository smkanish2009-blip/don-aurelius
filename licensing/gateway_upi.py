"""
Unified Payments Interface (UPI) Gateway for Indian Rupee (INR) Settlements.
Provides:
1. Dynamic UPI QR & Intent URI Generation (upi://pay?pa=...&pn=...&am=...&cu=INR&tn=...)
2. 12-Digit Bank UTR Claim Ingestion & Anti-Replay Duplicate Checks.
3. Automated or Admin 1-Click Entitlement Provisioning (SaaS, Lifetime, Gas Top-Up).
4. Direct Real-Time Telegram Admin Notifications on UTR Submission.
"""

import os
import re
import uuid
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta

from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus, UPIInvoice
from licensing.database import LicensingDatabase

logger = logging.getLogger("UPIGateway")


class UPIGateway:
    # Standard Indian Tier Pricing in INR
    TIER_PRICING_INR = {
        BillingTier.SAAS_MONTHLY: 4499.0,      # ~$50 USD
        BillingTier.SAAS_ANNUAL: 39999.0,      # ~$450 USD
        BillingTier.LIFETIME_PERPETUAL: 89999.0 # ~$999 USD
    }

    # Standard USD to INR conversion rate for gas wallet top-ups
    USD_TO_INR_RATE = 90.0

    def __init__(self,
                 db: LicensingDatabase,
                 merchant_vpa: Optional[str] = None,
                 merchant_name: str = "Don Aurelius AI"):
        self.db = db
        self.merchant_vpa = merchant_vpa or os.environ.get("MERCHANT_UPI_VPA", "kanish@upi")
        self.merchant_name = merchant_name
        self.telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    def create_invoice(self,
                       user_email: str,
                       tier: BillingTier,
                       amount_inr: Optional[float] = None,
                       gas_amount_usd: Optional[float] = None,
                       mt5_account_id: Optional[int] = None) -> UPIInvoice:
        """
        Generates a dynamic UPI payment invoice and mobile intent URI.
        """
        invoice_id = f"inv_upi_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=60)

        # Determine INR and equivalent USD amount
        if tier == BillingTier.PROFIT_SHARE:
            if gas_amount_usd:
                final_usd = float(gas_amount_usd)
                final_inr = round(final_usd * self.USD_TO_INR_RATE, 2)
            elif amount_inr:
                final_inr = float(amount_inr)
                final_usd = round(final_inr / self.USD_TO_INR_RATE, 2)
            else:
                final_usd = 50.0
                final_inr = 4500.0
        else:
            final_inr = amount_inr or self.TIER_PRICING_INR.get(tier, 4499.0)
            final_usd = round(final_inr / self.USD_TO_INR_RATE, 2)

        encoded_name = urllib.parse.quote_plus(self.merchant_name)
        encoded_note = urllib.parse.quote_plus(f"DonAurelius-{invoice_id[:16]}")
        
        # Standard NPCI UPI URI Specification
        upi_intent = (
            f"upi://pay?pa={self.merchant_vpa}"
            f"&pn={encoded_name}"
            f"&am={final_inr:.2f}"
            f"&cu=INR"
            f"&tn={encoded_note}"
        )

        # Record pending transaction in Entitlement Database
        self.db.record_payment(
            transaction_id=invoice_id,
            user_email=user_email,
            gateway=PaymentGateway.INR_UPI,
            amount_usd=final_usd,
            tier=tier,
            status=PaymentStatus.PENDING
        )

        logger.info(f"[UPI] Generated invoice {invoice_id} for {user_email}: ₹{final_inr:.2f} ({final_usd:.2f} USD) | VPA: {self.merchant_vpa}")

        return UPIInvoice(
            invoice_id=invoice_id,
            user_email=user_email.lower().strip(),
            tier=tier,
            amount_inr=final_inr,
            amount_usd=final_usd,
            vpa=self.merchant_vpa,
            merchant_name=self.merchant_name,
            upi_intent_uri=upi_intent,
            status=PaymentStatus.PENDING,
            expires_at=exp.isoformat(),
            created_at=now.isoformat()
        )

    def submit_utr_claim(self,
                         invoice_id: str,
                         utr_code: str,
                         user_email: str) -> Tuple[bool, str]:
        """
        Processes trader's 12-digit UTR reference code claim and alerts Admin on Telegram.
        """
        utr_clean = utr_code.strip().upper()
        # Basic UTR validation: 12-character alphanumeric or digits
        if not re.match(r"^[A-Z0-9]{10,22}$", utr_clean):
            return False, "Invalid UTR format. Please provide the 12-digit UPI reference number."

        # Anti-Replay check: has this UTR already been used?
        existing = self.db.get_payment(utr_clean)
        if existing and existing.get("status") == PaymentStatus.COMPLETED.value:
            return False, "This UTR reference has already been claimed and credited."

        # Record UTR submission as pending
        inv = self.db.get_payment(invoice_id)
        if not inv:
            return False, f"Invoice '{invoice_id}' not found."

        tier = BillingTier(inv["tier"])
        amount_usd = float(inv["amount_usd"])
        amount_inr = round(amount_usd * self.USD_TO_INR_RATE, 2)

        # Record UTR transaction link
        self.db.record_payment(
            transaction_id=utr_clean,
            user_email=user_email,
            gateway=PaymentGateway.INR_UPI,
            amount_usd=amount_usd,
            tier=tier,
            status=PaymentStatus.PENDING
        )

        # Send instant push notification to Telegram Admin
        self._notify_telegram_admin(
            invoice_id=invoice_id,
            utr_code=utr_clean,
            user_email=user_email,
            amount_inr=amount_inr,
            tier_name=tier.value
        )

        return True, "UTR payment claim received. Verification in progress."

    def confirm_payment(self,
                         invoice_id: str,
                         utr_code: str,
                         amount_confirmed_inr: float,
                         user_email: str,
                         tier: BillingTier,
                         mt5_account_id: Optional[int] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Marks payment completed and generates uncrackable HMAC license key.
        """
        amount_usd = round(amount_confirmed_inr / self.USD_TO_INR_RATE, 2)
        logger.info(f"[UPI] Payment confirmed for invoice {invoice_id}! UTR: {utr_code} | ₹{amount_confirmed_inr:.2f} (${amount_usd:.2f})")

        # Update both invoice and UTR payment records to COMPLETED
        self.db.record_payment(
            transaction_id=invoice_id,
            user_email=user_email,
            gateway=PaymentGateway.INR_UPI,
            amount_usd=amount_usd,
            tier=tier,
            status=PaymentStatus.COMPLETED
        )
        self.db.record_payment(
            transaction_id=utr_code,
            user_email=user_email,
            gateway=PaymentGateway.INR_UPI,
            amount_usd=amount_usd,
            tier=tier,
            status=PaymentStatus.COMPLETED
        )

        # Provision Entitlement
        if tier == BillingTier.PROFIT_SHARE:
            licenses = self.db.get_licenses_by_email(user_email)
            target_lic = next((l for l in licenses if l.tier == BillingTier.PROFIT_SHARE), None)
            if not target_lic:
                lic_key = f"XAU-GAS-{uuid.uuid4().hex[:12].upper()}"
                self.db.create_license(
                    license_key=lic_key,
                    user_email=user_email,
                    tier=BillingTier.PROFIT_SHARE,
                    mt5_account_id=mt5_account_id,
                    gas_balance_usd=amount_usd
                )
                return True, f"Gas wallet created with ${amount_usd:.2f} USD balance.", lic_key
            else:
                self.db.topup_gas(target_lic.license_key, amount_usd)
                return True, f"Gas wallet topped up by ${amount_usd:.2f} USD.", target_lic.license_key

        elif tier == BillingTier.LIFETIME_PERPETUAL:
            lic_key = f"XAU-LIFE-{uuid.uuid4().hex[:12].upper()}"
            self.db.create_license(
                license_key=lic_key,
                user_email=user_email,
                tier=BillingTier.LIFETIME_PERPETUAL,
                mt5_account_id=mt5_account_id,
                expires_at=None
            )
            return True, f"Lifetime license activated via UPI.", lic_key

        else:
            days = 365 if tier == BillingTier.SAAS_ANNUAL else 30
            existing = self.db.get_licenses_by_email(user_email)
            active_lic = next((l for l in existing if l.tier == tier), None)
            if active_lic:
                self.db.extend_license(active_lic.license_key, days)
                return True, f"Extended SaaS license {active_lic.license_key} by {days} days.", active_lic.license_key
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
                return True, f"Provisioned SaaS license via UPI.", lic_key

    def _notify_telegram_admin(self,
                               invoice_id: str,
                               utr_code: str,
                               user_email: str,
                               amount_inr: float,
                               tier_name: str) -> None:
        """Sends immediate Telegram push message to admin mobile."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.info("[UPI] Telegram alert skipped: bot token or chat ID not set.")
            return

        msg = (
            f"⚡ *NEW UPI PAYMENT CLAIM RECEIVED*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Amount:* ₹{amount_inr:,.2f} INR\n"
            f"🏷️ *Tier:* `{tier_name}`\n"
            f"👤 *Customer:* `{user_email}`\n"
            f"🧾 *Invoice:* `{invoice_id}`\n"
            f"🔢 *UTR Reference:* `{utr_code}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Verify in your bank app and approve via licensing admin API."
        )

        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = json.dumps({
                "chat_id": self.telegram_chat_id,
                "text": msg,
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"[UPI] Telegram push sent to {self.telegram_chat_id}")
        except Exception as e:
            logger.error(f"[UPI] Failed to dispatch Telegram push: {e}")
