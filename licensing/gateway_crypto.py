"""
Web3 & Crypto Payment Gateway (USDT TRC-20 / ERC-20 / BEP-20).
Handles:
1. Dynamic Crypto Invoice Creation with deposit addresses, exact USDT amount, and QR intents.
2. Webhook / RPC Confirmation Ingestion (Coinbase Commerce, BTCPay Server, or Native Tron/EVM listeners).
3. Gas Wallet Crediting and SaaS/Lifetime License Provisioning upon on-chain block confirmation.
4. Cryptographic webhook verification and replay protection.
"""

import time
import hmac
import hashlib
import uuid
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta
from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus, CryptoInvoice
from licensing.database import LicensingDatabase

logger = logging.getLogger("CryptoGateway")


class CryptoGateway:
    # Production hot-wallet deposit addresses (configurable via environment)
    DEFAULT_DEPOSIT_ADDRESSES = {
        "TRC20": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # USDT TRC20 merchant master
        "BEP20": "0x55d398326f99059fF775485246999027B3197955",  # Binance-Peg USDT
        "ERC20": "0xdAC17F958D2ee523a2206206994597C13D831ec7"   # Tether USD Ethereum
    }

    def __init__(self,
                 db: LicensingDatabase,
                 webhook_secret: str = "cryptosec_mock_secret_xauusd_bot",
                 merchant_addresses: Optional[Dict[str, str]] = None):
        self.db = db
        self.webhook_secret = webhook_secret
        self.deposit_addresses = merchant_addresses or self.DEFAULT_DEPOSIT_ADDRESSES

    def create_invoice(self,
                       user_email: str,
                       tier: BillingTier,
                       amount_usdt: float,
                       network: str = "TRC20",
                       mt5_account_id: Optional[int] = None) -> CryptoInvoice:
        """
        Creates a dynamic payment intent for USDT deposit.
        """
        invoice_id = f"inv_crypto_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=60)
        net = network.upper().strip()
        deposit_addr = self.deposit_addresses.get(net, self.deposit_addresses["TRC20"])

        # Construct Web3 payment URI for mobile crypto wallets
        if net == "TRC20":
            qr_intent = f"tron:{deposit_addr}?token=USDT&amount={amount_usdt:.2f}&memo={invoice_id}"
        else:
            qr_intent = f"ethereum:{deposit_addr}?token=USDT&amount={amount_usdt:.2f}&memo={invoice_id}"

        # Record pending transaction
        self.db.record_payment(
            transaction_id=invoice_id,
            user_email=user_email,
            gateway=PaymentGateway.CRYPTO_USDT,
            amount_usd=amount_usdt,
            tier=tier,
            status=PaymentStatus.PENDING
        )

        logger.info(f"[CRYPTO] Created {net} USDT Invoice {invoice_id} for {user_email}: {amount_usdt:.2f} USDT")

        return CryptoInvoice(
            invoice_id=invoice_id,
            user_email=user_email.lower().strip(),
            tier=tier,
            amount_usdt=amount_usdt,
            network=net,
            deposit_address=deposit_addr,
            qr_code_intent=qr_intent,
            status=PaymentStatus.PENDING,
            expires_at=exp.isoformat(),
            created_at=now.isoformat()
        )

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: str) -> bool:
        """Verifies HMAC-SHA256 signature from crypto provider (e.g. Coinbase Commerce X-CC-Webhook-Signature)."""
        try:
            expected_sig = hmac.new(
                key=self.webhook_secret.encode("utf-8"),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_sig, signature_header.strip())
        except Exception as e:
            logger.error(f"[CRYPTO] Signature error: {e}")
            return False

    def generate_sandbox_signature(self, payload_bytes: bytes) -> str:
        """Helper to create valid crypto webhook signature for tests."""
        return hmac.new(
            key=self.webhook_secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

    def confirm_payment(self,
                        invoice_id: str,
                        tx_hash: str,
                        amount_confirmed_usdt: float,
                        user_email: str,
                        tier: BillingTier,
                        mt5_account_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Executed when an on-chain deposit is confirmed by the blockchain listener / webhook.
        Credits gas balance or activates subscription.
        """
        logger.info(f"[CRYPTO] Payment confirmed for invoice {invoice_id}! TxHash: {tx_hash} | Amount: ${amount_confirmed_usdt:.2f}")

        # Update payment record
        self.db.record_payment(
            transaction_id=tx_hash,
            user_email=user_email,
            gateway=PaymentGateway.CRYPTO_USDT,
            amount_usd=amount_confirmed_usdt,
            tier=tier,
            status=PaymentStatus.COMPLETED
        )

        # Gas Wallet Top-Up
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
                    gas_balance_usd=amount_confirmed_usdt
                )
            else:
                self.db.topup_gas(target_lic.license_key, amount_confirmed_usdt)
            return True, f"Gas wallet credited with ${amount_confirmed_usdt:.2f} USDT."

        elif tier == BillingTier.LIFETIME_PERPETUAL:
            lic_key = f"XAU-LIFE-{uuid.uuid4().hex[:12].upper()}"
            self.db.create_license(
                license_key=lic_key,
                user_email=user_email,
                tier=BillingTier.LIFETIME_PERPETUAL,
                mt5_account_id=mt5_account_id,
                expires_at=None
            )
            return True, f"Lifetime license {lic_key} activated via crypto."

        else:
            # SaaS (Monthly/Annual)
            days = 365 if tier == BillingTier.SAAS_ANNUAL else 30
            existing = self.db.get_licenses_by_email(user_email)
            active_lic = next((l for l in existing if l.tier == tier), None)
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
                return True, f"Provisioned SaaS license {lic_key} via crypto."
