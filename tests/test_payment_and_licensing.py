"""
Institutional Test Suite: Payments, Monetization, Webhooks & Licensing Entitlement.
Tests:
1. ACID SQLite Entitlement Database & Anti-Piracy Account Lock.
2. Stripe Gateway: Checkout, Signature Verification, Webhook Ingestion.
3. Crypto Gateway: Dynamic USDT (TRC-20) Invoices & On-Chain Confirmation.
4. Whop Marketplace Webhook Ingestion.
5. Starlette ASGI Server Endpoints (validate, activate, checkout, webhooks).
6. Client-Side Pre-Flight Trade Execution Gate.
7. Fail-Safe Offline Grace Period with HMAC-SHA256 verification.
8. Broker Affiliate (IB) Program Verification.
"""

import os
import time
import json
import uuid
import unittest
import tempfile
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from starlette.testclient import TestClient

from licensing.models import BillingTier, LicenseStatus, PaymentGateway, PaymentStatus
from licensing.database import LicensingDatabase
from licensing.gateway_stripe import StripeGateway
from licensing.gateway_crypto import CryptoGateway
from licensing.gateway_whop import WhopGateway
from licensing.server import create_app, SERVER_MASTER_SIGNING_KEY
from security.entitlement_client import EntitlementClient


class TestPaymentAndLicensing(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_entitlement.db")
        self.lease_path = os.path.join(self.temp_dir.name, "test_lease.json")
        self.db = LicensingDatabase(self.db_path)
        self.stripe_gw = StripeGateway(self.db)
        self.crypto_gw = CryptoGateway(self.db)
        self.whop_gw = WhopGateway(self.db)

    def tearDown(self):
        self.db.close()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # --- 1. Database & Anti-Piracy Tests ---
    def test_database_crud_and_account_lock(self):
        user_email = "trader@propfirm.com"
        lic_key = "XAU-TEST-KEY-001"
        self.db.create_license(
            license_key=lic_key,
            user_email=user_email,
            tier=BillingTier.LIFETIME_PERPETUAL,
            mt5_account_id=None
        )

        record = self.db.get_license(lic_key)
        self.assertIsNotNone(record)
        self.assertEqual(record.tier, BillingTier.LIFETIME_PERPETUAL)
        self.assertEqual(record.status, LicenseStatus.ACTIVE)

        # Bind to MT5 Account #113182919
        ok, msg = self.db.bind_account_and_machine(lic_key, 113182919, "mac-uuid-abc")
        self.assertTrue(ok)

        # Attempt to bind to a different account (Anti-Piracy Copy Protection)
        ok2, msg2 = self.db.bind_account_and_machine(lic_key, 999999999, "mac-uuid-xyz")
        self.assertFalse(ok2)
        self.assertIn("Anti-Piracy Violation", msg2)

    def test_database_gas_wallet_deduction_and_topup(self):
        lic_key = "XAU-GAS-001"
        self.db.create_license(
            license_key=lic_key,
            user_email="gasuser@quant.io",
            tier=BillingTier.PROFIT_SHARE,
            gas_balance_usd=50.0
        )

        bal = self.db.topup_gas(lic_key, 100.0)
        self.assertEqual(bal, 150.0)

        ok, remaining = self.db.deduct_gas(lic_key, 150.0)
        self.assertTrue(ok)
        self.assertEqual(remaining, 0.0)

        record = self.db.get_license(lic_key)
        self.assertEqual(record.status, LicenseStatus.GRACEFUL_DISCONNECT)

    # --- 2. Stripe Gateway Tests ---
    def test_stripe_checkout_and_signature_verification(self):
        session = self.stripe_gw.create_checkout_session(
            user_email="goldtrader@stripe.com",
            tier=BillingTier.SAAS_MONTHLY,
            mt5_account_id=113182919
        )
        self.assertIn("checkout_url", session)
        self.assertEqual(session["amount_usd"], 50.00)

        # Test HMAC-SHA256 signature verification
        payload = b'{"type": "checkout.session.completed"}'
        sig = self.stripe_gw.generate_sandbox_signature(payload)
        self.assertTrue(self.stripe_gw.verify_webhook_signature(payload, sig))

        # Tampered payload fails
        tampered_payload = b'{"type": "checkout.session.completed", "tampered": true}'
        self.assertFalse(self.stripe_gw.verify_webhook_signature(tampered_payload, sig))

    def test_stripe_webhook_checkout_completed_saas(self):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_12345",
                    "customer_email": "subscriber@gold.com",
                    "amount_total": 5000,
                    "metadata": {
                        "tier": "SAAS_MONTHLY",
                        "mt5_account_id": "113182919"
                    }
                }
            }
        }
        ok, msg = self.stripe_gw.process_webhook(event)
        self.assertTrue(ok)

        licenses = self.db.get_licenses_by_email("subscriber@gold.com")
        self.assertEqual(len(licenses), 1)
        self.assertEqual(licenses[0].tier, BillingTier.SAAS_MONTHLY)
        self.assertEqual(licenses[0].mt5_account_id, 113182919)
        self.assertIsNotNone(licenses[0].expires_at)

    def test_stripe_webhook_invoice_paid_and_subscription_deleted(self):
        # 1. First provision SaaS license
        event_init = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_001",
                    "customer_email": "recurring@gold.com",
                    "amount_total": 5000,
                    "metadata": {"tier": "SAAS_MONTHLY"}
                }
            }
        }
        self.stripe_gw.process_webhook(event_init)
        lic_before = self.db.get_licenses_by_email("recurring@gold.com")[0]

        # 2. Invoice paid (recurring monthly renewal)
        event_paid = {
            "type": "invoice.paid",
            "data": {
                "object": {
                    "id": "in_test_renewal",
                    "customer_email": "recurring@gold.com",
                    "amount_paid": 5000
                }
            }
        }
        ok, msg = self.stripe_gw.process_webhook(event_paid)
        self.assertTrue(ok)
        lic_after = self.db.get_licenses_by_email("recurring@gold.com")[0]
        self.assertGreater(lic_after.expires_at, lic_before.expires_at)

        # 3. Subscription deleted
        event_del = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_test",
                    "metadata": {"email": "recurring@gold.com"}
                }
            }
        }
        ok_del, _ = self.stripe_gw.process_webhook(event_del)
        self.assertTrue(ok_del)
        lic_cancelled = self.db.get_licenses_by_email("recurring@gold.com")[0]
        self.assertEqual(lic_cancelled.status, LicenseStatus.EXPIRED)

    # --- 3. Crypto Gateway (USDT TRC-20) Tests ---
    def test_crypto_invoice_and_confirmation(self):
        invoice = self.crypto_gw.create_invoice(
            user_email="cryptotrader@binance.com",
            tier=BillingTier.PROFIT_SHARE,
            amount_usdt=100.00,
            network="TRC20",
            mt5_account_id=113182919
        )
        self.assertEqual(invoice.amount_usdt, 100.0)
        self.assertEqual(invoice.network, "TRC20")
        self.assertTrue(invoice.deposit_address.startswith("TR7"))

        # Confirm on-chain deposit
        ok, msg = self.crypto_gw.confirm_payment(
            invoice_id=invoice.invoice_id,
            tx_hash="0xabcd1234ef5678",
            amount_confirmed_usdt=100.0,
            user_email="cryptotrader@binance.com",
            tier=BillingTier.PROFIT_SHARE,
            mt5_account_id=113182919
        )
        self.assertTrue(ok)
        lic = self.db.get_licenses_by_email("cryptotrader@binance.com")[0]
        self.assertEqual(lic.gas_balance_usd, 100.0)

    # --- 4. Whop Marketplace Tests ---
    def test_whop_webhook_lifecycle(self):
        event_valid = {
            "action": "membership.went_valid",
            "data": {
                "user": {"id": "whop_user_1", "email": "whopmember@discord.gg"},
                "plan": {"id": "plan_gold_tier"}
            }
        }
        ok, msg = self.whop_gw.process_webhook(event_valid)
        self.assertTrue(ok)
        lic = self.db.get_licenses_by_email("whopmember@discord.gg")[0]
        self.assertEqual(lic.status, LicenseStatus.ACTIVE)

        event_invalid = {
            "action": "membership.went_invalid",
            "data": {
                "user": {"id": "whop_user_1", "email": "whopmember@discord.gg"}
            }
        }
        ok_inv, _ = self.whop_gw.process_webhook(event_invalid)
        self.assertTrue(ok_inv)
        lic_exp = self.db.get_licenses_by_email("whopmember@discord.gg")[0]
        self.assertEqual(lic_exp.status, LicenseStatus.EXPIRED)

    # --- 5. ASGI Licensing Server Endpoints ---
    def test_licensing_server_endpoints_with_testclient(self):
        app = create_app(self.db_path)
        client = TestClient(app)

        # Health
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "healthy")

        # Provision a license in DB
        lic_key = "XAU-SRV-TEST"
        self.db.create_license(
            license_key=lic_key,
            user_email="srvtest@bot.com",
            tier=BillingTier.SAAS_MONTHLY,
            mt5_account_id=113182919,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )

        # Validate endpoint
        val_resp = client.post("/api/v1/license/validate", json={
            "license_key": lic_key,
            "mt5_account_id": 113182919,
            "machine_fingerprint": "mock-machine-1"
        })
        self.assertEqual(val_resp.status_code, 200)
        data = val_resp.json()
        self.assertTrue(data["is_authorized"])
        self.assertTrue(data["allows_new_trades"])
        self.assertIn("hmac_signature", data)

        # Mismatch MT5 account fails
        mismatch_resp = client.post("/api/v1/license/validate", json={
            "license_key": lic_key,
            "mt5_account_id": 88888888,
            "machine_fingerprint": "mock-machine-2"
        })
        self.assertEqual(mismatch_resp.status_code, 403)
        self.assertFalse(mismatch_resp.json()["is_authorized"])

        # Stripe Webhook Endpoint
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_live_webhook_test",
                    "customer_email": "webhooks@test.com",
                    "amount_total": 5000,
                    "metadata": {"tier": "SAAS_MONTHLY"}
                }
            }
        }).encode("utf-8")
        sig = self.stripe_gw.generate_sandbox_signature(payload)
        wh_resp = client.post(
            "/api/v1/webhooks/stripe",
            content=payload,
            headers={"stripe-signature": sig, "content-type": "application/json"}
        )
        self.assertEqual(wh_resp.status_code, 200)
        app.state.lic_app.db.close()

    # --- 6. Pre-Flight Execution Gate & Offline Grace Period ---
    def test_preflight_trade_gate_authorized_and_anti_piracy(self):
        # Create valid active license
        lic_key = "XAU-GATE-VALID"
        self.db.create_license(
            license_key=lic_key,
            user_email="gateuser@prop.com",
            tier=BillingTier.LIFETIME_PERPETUAL,
            mt5_account_id=113182919
        )

        # Initialize entitlement client with local mock lease
        client = EntitlementClient(
            license_key=lic_key,
            lease_cache_file=self.lease_path
        )

        # Manually create signed token from server key to simulate cache
        now_ts = int(time.time())
        raw = f"{lic_key}:{BillingTier.LIFETIME_PERPETUAL.value}:{LicenseStatus.ACTIVE.value}:113182919:none:0.00:True:{now_ts}"
        sig = hmac.new(
            key=SERVER_MASTER_SIGNING_KEY.encode("utf-8"),
            msg=raw.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        token = {
            "is_authorized": True,
            "license_key": lic_key,
            "tier": BillingTier.LIFETIME_PERPETUAL.value,
            "status": LicenseStatus.ACTIVE.value,
            "mt5_account_id": 113182919,
            "expires_at": None,
            "gas_balance_usd": 0.0,
            "allows_new_trades": True,
            "timestamp": now_ts,
            "hmac_signature": sig
        }
        client._save_cached_lease(token)

        # Pre-flight check with correct MT5 Account
        authorized, reason = client.pre_flight_trade_gate(113182919)
        self.assertTrue(authorized)
        self.assertEqual(reason, "Trade Authorized")

        # Pre-flight check with unauthorized MT5 Account (Anti-Piracy Violation)
        auth_bad, reason_bad = client.pre_flight_trade_gate(999999999)
        self.assertFalse(auth_bad)
        self.assertIn("Anti-Piracy Lock", reason_bad)

    def test_preflight_trade_gate_gas_depleted(self):
        lic_key = "XAU-GAS-DEPLETED"
        client = EntitlementClient(
            license_key=lic_key,
            lease_cache_file=self.lease_path
        )
        now_ts = int(time.time())
        raw = f"{lic_key}:{BillingTier.PROFIT_SHARE.value}:{LicenseStatus.GRACEFUL_DISCONNECT.value}:113182919:none:0.00:False:{now_ts}"
        sig = hmac.new(
            key=SERVER_MASTER_SIGNING_KEY.encode("utf-8"),
            msg=raw.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        token = {
            "is_authorized": True,
            "license_key": lic_key,
            "tier": BillingTier.PROFIT_SHARE.value,
            "status": LicenseStatus.GRACEFUL_DISCONNECT.value,
            "mt5_account_id": 113182919,
            "expires_at": None,
            "gas_balance_usd": 0.0,
            "allows_new_trades": False,
            "timestamp": now_ts,
            "hmac_signature": sig
        }
        client._save_cached_lease(token)

        # New trade must be blocked
        authorized, reason = client.pre_flight_trade_gate(113182919)
        self.assertFalse(authorized)
        self.assertIn("Gas balance is $0.00", reason)

        # But existing open positions can still be managed (trailing stops)
        self.assertTrue(client.allows_position_management())

    def test_introducing_broker_affiliate_verification(self):
        app = create_app(self.db_path)
        client = TestClient(app)

        resp = client.post("/api/v1/affiliate/verify", json={
            "mt5_account_id": 113182919,
            "broker_server": "ICMarketsSC-Demo",
            "user_email": "ib_trader@icmarkets.com"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["verified"])
        self.assertIn("XAU-IB-113182919", resp.json()["license_key"])
        app.state.lic_app.db.close()


if __name__ == "__main__":
    unittest.main()
