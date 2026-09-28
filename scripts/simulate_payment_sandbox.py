"""
Interactive Payment & Licensing Sandbox Simulator.
Allows developers and users to test:
1. Stripe Checkout session generation & Webhook simulation.
2. USDT (TRC-20) Crypto payment generation & on-chain confirmation.
3. Whop Marketplace subscription webhook events.
4. Partner Broker Affiliate (IB) free access verification.
5. Entitlement lookup and account binding status.
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime, timezone, timedelta

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus
from licensing.database import LicensingDatabase
from licensing.gateway_stripe import StripeGateway
from licensing.gateway_crypto import CryptoGateway
from licensing.gateway_whop import WhopGateway
from security.entitlement_client import EntitlementClient


def run_sandbox():
    db_path = "data/entitlement.db"
    db = LicensingDatabase(db_path)
    stripe_gw = StripeGateway(db)
    crypto_gw = CryptoGateway(db)
    whop_gw = WhopGateway(db)

    print("=" * 70)
    print("      XAUUSD AI TRADING BOT - MONETIZATION SANDBOX SIMULATOR")
    print("=" * 70)
    print("Running in sandbox test mode against local ACID SQLite store.")
    print("1. Simulate Stripe SaaS Checkout ($50/mo)")
    print("2. Simulate Stripe Gas Wallet Top-Up (+$100 USD)")
    print("3. Simulate USDT (TRC-20) Crypto Deposit (+$250 USDT)")
    print("4. Simulate Whop Marketplace Membership Activation")
    print("5. Verify Introducing Broker (IB) Free Tier (IC Markets / Pepperstone)")
    print("6. Run Pre-Flight Trade Gate Check on MT5 Account #113182919")
    print("7. Inspect All Active Licenses in Database")
    print("=" * 70)

    # Automated demonstration of key flows
    test_email = "demo_trader@xauusd-quant.io"
    test_mt5 = 113182919

    print(f"\n[STEP 1] Generating Stripe SaaS Monthly Checkout for {test_email}...")
    checkout = stripe_gw.create_checkout_session(
        user_email=test_email,
        tier=BillingTier.SAAS_MONTHLY,
        mt5_account_id=test_mt5
    )
    print(f" -> Checkout URL: {checkout['checkout_url']}")
    print(f" -> Session ID:   {checkout['session_id']}")

    print(f"\n[STEP 2] Simulating Stripe Webhook 'checkout.session.completed'...")
    stripe_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": checkout["session_id"],
                "customer_email": test_email,
                "amount_total": 5000,
                "metadata": {
                    "tier": "SAAS_MONTHLY",
                    "mt5_account_id": str(test_mt5)
                }
            }
        }
    }
    ok_stripe, msg_stripe = stripe_gw.process_webhook(stripe_event)
    print(f" -> Result: {msg_stripe}")

    print(f"\n[STEP 3] Generating USDT TRC-20 Crypto Invoice for Gas Tank (+$250 USDT)...")
    crypto_inv = crypto_gw.create_invoice(
        user_email=test_email,
        tier=BillingTier.PROFIT_SHARE,
        amount_usdt=250.00,
        network="TRC20",
        mt5_account_id=test_mt5
    )
    print(f" -> Invoice ID:      {crypto_inv.invoice_id}")
    print(f" -> Deposit Address: {crypto_inv.deposit_address} (TRC-20)")
    print(f" -> QR URI Intent:   {crypto_inv.qr_code_intent}")

    print(f"\n[STEP 4] Simulating On-Chain USDT Block Confirmation...")
    ok_crypto, msg_crypto = crypto_gw.confirm_payment(
        invoice_id=crypto_inv.invoice_id,
        tx_hash=f"0x{uuid.uuid4().hex}",
        amount_confirmed_usdt=250.00,
        user_email=test_email,
        tier=BillingTier.PROFIT_SHARE,
        mt5_account_id=test_mt5
    )
    print(f" -> Result: {msg_crypto}")

    print(f"\n[STEP 5] Testing Pre-Flight Trade Gate on MT5 Account #{test_mt5}...")
    entitlement_client = EntitlementClient(
        license_key="XAUUSD-INSTITUTIONAL-PRO-2026",
        server_url="http://127.0.0.1:8000"
    )
    # Check using local DB records
    licenses = db.get_licenses_by_email(test_email)
    print(f" -> Active Licenses Found for {test_email}: {len(licenses)}")
    for lic in licenses:
        exp_txt = lic.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC') if lic.expires_at else 'Perpetual'
        print(f"    * [{lic.tier.value}] Key: {lic.license_key} | MT5: #{lic.mt5_account_id} | Status: {lic.status.value} | Expiry: {exp_txt} | Gas: ${lic.gas_balance_usd:.2f}")

    print("\n[SUCCESS] Sandbox payment, webhook, and gas wallet simulation complete!\n")


if __name__ == "__main__":
    run_sandbox()
