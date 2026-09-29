"""
High-Performance ASGI Webhook & Licensing Server.
Powered by Starlette & Uvicorn.
Provides:
1. /api/v1/license/validate - Pre-flight authorization with HMAC lease tokens.
2. /api/v1/license/activate - Hardware & MT5 account cryptographic locking.
3. /api/v1/billing/checkout - Stripe / Crypto payment session generation.
4. /api/v1/webhooks/stripe - Ingests Stripe events with HMAC verification.
5. /api/v1/webhooks/crypto - Ingests USDT block confirmations.
6. /api/v1/webhooks/whop - Ingests Whop creator events.
7. /api/v1/affiliate/verify - Introducing Broker (IB) verification.
8. /health - Healthcheck endpoint.
"""

import os
import sys
import time
import json
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from licensing.database import LicensingDatabase
from licensing.models import (
    BillingTier, LicenseStatus, EntitlementToken,
    PaymentGateway, PaymentStatus
)
from licensing.gateway_stripe import StripeGateway
from licensing.gateway_crypto import CryptoGateway
from licensing.gateway_whop import WhopGateway

logger = logging.getLogger("LicensingServer")

# Master cryptographic signing key & Admin key loaded securely from environment
SERVER_MASTER_SIGNING_KEY = os.environ.get("SERVER_MASTER_SIGNING_KEY") or os.environ.get("MASTER_SIGNING_KEY", "xauusd_master_hmac_license_secret_2026")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "sovereign_admin_secure_key_2026")


class InMemoryRateLimiter:
    """Sliding-window IP rate limiter to protect against brute-force and DoS attacks."""
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.history: Dict[str, list] = {}
        self.lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0
        with self.lock:
            if client_ip not in self.history:
                self.history[client_ip] = [now]
                return True
            self.history[client_ip] = [t for t in self.history[client_ip] if t > window_start]
            if len(self.history[client_ip]) >= self.rpm:
                return False
            self.history[client_ip].append(now)
            return True


rate_limiter = InMemoryRateLimiter(requests_per_minute=60)


class SecurityHeadersAndRateLimitMiddleware(BaseHTTPMiddleware):
    """Applies IP rate limiting and injects OWASP/NIST-recommended security headers."""
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                {"error": "Too Many Requests: Rate limit exceeded. Try again in 60 seconds."},
                status_code=429,
                headers={"Retry-After": "60"}
            )

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class LicensingApp:
    def __init__(self, db_path: str = "data/entitlement.db"):
        self.db = LicensingDatabase(db_path)
        self.stripe_gw = StripeGateway(self.db)
        self.crypto_gw = CryptoGateway(self.db)
        self.whop_gw = WhopGateway(self.db)

    def sign_entitlement(self,
                         license_key: str,
                         tier: str,
                         status: str,
                         mt5_account_id: Optional[int],
                         expires_at: Optional[str],
                         gas_balance_usd: float,
                         allows_new_trades: bool,
                         timestamp: int) -> str:
        """Issues an untamperable HMAC-SHA256 signature for the client lease."""
        raw = f"{license_key}:{tier}:{status}:{mt5_account_id or 0}:{expires_at or 'none'}:{gas_balance_usd:.2f}:{allows_new_trades}:{timestamp}"
        return hmac.new(
            key=SERVER_MASTER_SIGNING_KEY.encode("utf-8"),
            msg=raw.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

    async def validate_license(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        license_key = body.get("license_key", "").strip()
        mt5_account_id = body.get("mt5_account_id")
        machine_fingerprint = body.get("machine_fingerprint", "")
        now_ts = int(time.time())

        if not license_key:
            return JSONResponse({"error": "Missing license_key"}, status_code=400)

        record = self.db.get_license(license_key)
        if not record:
            return JSONResponse({
                "is_authorized": False,
                "reason": f"License key '{license_key}' not found.",
                "status": LicenseStatus.REVOKED.value,
                "allows_new_trades": False,
                "allows_position_management": False,
                "timestamp": now_ts
            }, status_code=403)

        # 1. Check revocation / suspension
        if record.status in (LicenseStatus.REVOKED, LicenseStatus.SUSPENDED):
            return JSONResponse({
                "is_authorized": False,
                "reason": f"License is {record.status.value}.",
                "status": record.status.value,
                "allows_new_trades": False,
                "allows_position_management": False,
                "timestamp": now_ts
            }, status_code=403)

        # 2. Check expiration (for SaaS/temporary licenses)
        if record.expires_at:
            if datetime.now(timezone.utc) > record.expires_at:
                self.db.update_license_status(license_key, LicenseStatus.EXPIRED)
                return JSONResponse({
                    "is_authorized": False,
                    "reason": "License has expired. Please renew subscription.",
                    "status": LicenseStatus.EXPIRED.value,
                    "allows_new_trades": False,
                    "allows_position_management": True,
                    "timestamp": now_ts
                }, status_code=403)

        # 3. Check MT5 Account binding (anti-piracy)
        if mt5_account_id is not None:
            if record.mt5_account_id is None:
                # First time binding
                self.db.bind_account_and_machine(license_key, int(mt5_account_id), machine_fingerprint)
                record = self.db.get_license(license_key)
            elif record.mt5_account_id != int(mt5_account_id):
                return JSONResponse({
                    "is_authorized": False,
                    "reason": f"License is locked to MT5 Account #{record.mt5_account_id}. Cannot run on #{mt5_account_id}.",
                    "status": LicenseStatus.SUSPENDED.value,
                    "allows_new_trades": False,
                    "allows_position_management": False,
                    "timestamp": now_ts
                }, status_code=403)

        # 4. Profit-Sharing Gas Wallet check
        allows_new = True
        status_val = record.status.value
        reason_msg = "Authorized"

        if record.tier == BillingTier.PROFIT_SHARE:
            if record.gas_balance_usd <= 0.0:
                allows_new = False
                status_val = LicenseStatus.GRACEFUL_DISCONNECT.value
                reason_msg = "Gas wallet balance is $0.00. Read-only mode: new trades blocked."

        exp_str = record.expires_at.isoformat() if record.expires_at else None
        token_sig = self.sign_entitlement(
            license_key=record.license_key,
            tier=record.tier.value,
            status=status_val,
            mt5_account_id=record.mt5_account_id,
            expires_at=exp_str,
            gas_balance_usd=record.gas_balance_usd,
            allows_new_trades=allows_new,
            timestamp=now_ts
        )

        return JSONResponse({
            "is_authorized": True,
            "license_key": record.license_key,
            "tier": record.tier.value,
            "status": status_val,
            "mt5_account_id": record.mt5_account_id,
            "expires_at": exp_str,
            "gas_balance_usd": record.gas_balance_usd,
            "allows_new_trades": allows_new,
            "allows_position_management": True,
            "reason": reason_msg,
            "timestamp": now_ts,
            "hmac_signature": token_sig
        })

    async def activate_license(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        license_key = body.get("license_key")
        mt5_account_id = body.get("mt5_account_id")
        machine_fingerprint = body.get("machine_fingerprint", "default-machine")

        if not license_key or not mt5_account_id:
            return JSONResponse({"error": "Missing license_key or mt5_account_id"}, status_code=400)

        ok, msg = self.db.bind_account_and_machine(license_key, int(mt5_account_id), machine_fingerprint)
        if not ok:
            return JSONResponse({"success": False, "message": msg}, status_code=400)

        return JSONResponse({"success": True, "message": msg})

    async def create_checkout(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        user_email = body.get("user_email")
        tier_str = body.get("tier", BillingTier.SAAS_MONTHLY.value)
        gateway_str = body.get("gateway", PaymentGateway.STRIPE.value)
        gas_amount = body.get("gas_amount_usd")
        mt5_account_id = body.get("mt5_account_id")

        if not user_email:
            return JSONResponse({"error": "Missing user_email"}, status_code=400)

        try:
            tier = BillingTier(tier_str)
        except ValueError:
            return JSONResponse({"error": f"Invalid tier: {tier_str}"}, status_code=400)

        if gateway_str == PaymentGateway.CRYPTO_USDT.value:
            amount_usdt = float(gas_amount) if gas_amount else (50.0 if tier == BillingTier.SAAS_MONTHLY else 999.0)
            invoice = self.crypto_gw.create_invoice(
                user_email=user_email,
                tier=tier,
                amount_usdt=amount_usdt,
                network=body.get("network", "TRC20"),
                mt5_account_id=mt5_account_id
            )
            return JSONResponse({"gateway": "CRYPTO_USDT", "invoice": invoice.dict()})

        else:
            # Default to Stripe
            session = self.stripe_gw.create_checkout_session(
                user_email=user_email,
                tier=tier,
                gas_amount_usd=float(gas_amount) if gas_amount else None,
                mt5_account_id=mt5_account_id
            )
            return JSONResponse({"gateway": "STRIPE", "checkout": session})

    async def webhook_stripe(self, request: Request) -> Response:
        payload_bytes = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        if not sig_header:
            logger.warning("[STRIPE] Missing stripe-signature header")
            return Response("Missing signature", status_code=400)

        if not self.stripe_gw.verify_webhook_signature(payload_bytes, sig_header):
            logger.warning("[STRIPE] Invalid webhook signature")
            return Response("Invalid signature", status_code=400)

        try:
            event_data = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return Response("Invalid JSON payload", status_code=400)

        success, msg = self.stripe_gw.process_webhook(event_data)
        if not success:
            logger.error(f"[STRIPE] Webhook processing failed: {msg}")
            return Response(msg, status_code=500)

        return JSONResponse({"received": True, "message": msg})

    async def webhook_crypto(self, request: Request) -> Response:
        payload_bytes = await request.body()
        sig_header = request.headers.get("x-crypto-signature", "")

        if sig_header and not self.crypto_gw.verify_webhook_signature(payload_bytes, sig_header):
            return Response("Invalid crypto signature", status_code=400)

        try:
            body = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return Response("Invalid JSON", status_code=400)

        invoice_id = body.get("invoice_id")
        tx_hash = body.get("tx_hash", f"0x{time.time()}")
        amount = float(body.get("amount_usdt", 0.0))
        user_email = body.get("user_email")
        tier_str = body.get("tier", BillingTier.PROFIT_SHARE.value)
        mt5_acc = body.get("mt5_account_id")

        if not user_email or amount <= 0:
            return Response("Invalid transaction data", status_code=400)

        tier = BillingTier(tier_str)
        ok, msg = self.crypto_gw.confirm_payment(
            invoice_id=invoice_id or tx_hash,
            tx_hash=tx_hash,
            amount_confirmed_usdt=amount,
            user_email=user_email,
            tier=tier,
            mt5_account_id=int(mt5_acc) if mt5_acc else None
        )
        return JSONResponse({"success": ok, "message": msg})

    async def webhook_whop(self, request: Request) -> Response:
        payload_bytes = await request.body()
        sig_header = request.headers.get("x-whop-signature", "")

        if sig_header and not self.whop_gw.verify_webhook_signature(payload_bytes, sig_header):
            return Response("Invalid Whop signature", status_code=400)

        try:
            event_data = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return Response("Invalid JSON", status_code=400)

        ok, msg = self.whop_gw.process_webhook(event_data)
        return JSONResponse({"success": ok, "message": msg})

    async def verify_affiliate(self, request: Request) -> JSONResponse:
        """
        Broker Affiliate (Introducing Broker) Verification Endpoint:
        Verifies if an MT5 account was opened under partner IB group.
        """
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        mt5_account_id = body.get("mt5_account_id")
        broker_server = body.get("broker_server", "")
        user_email = body.get("user_email", "")

        if not mt5_account_id or not user_email:
            return JSONResponse({"error": "Missing mt5_account_id or user_email"}, status_code=400)

        # In production, check against broker IB API / database list
        # For demonstration/partner test, any account with IB prefix or designated broker is verified
        is_ib_member = "ICMarkets" in broker_server or "Pepperstone" in broker_server or body.get("is_partner_demo", False)

        if is_ib_member:
            lic_key = f"XAU-IB-{mt5_account_id}"
            record = self.db.create_license(
                license_key=lic_key,
                user_email=user_email,
                tier=BillingTier.IB_AFFILIATE_FREE,
                mt5_account_id=int(mt5_account_id),
                expires_at=None  # Free perpetual access as long as active with IB
            )
            return JSONResponse({
                "verified": True,
                "message": f"Account #{mt5_account_id} verified under Introducing Broker program! Free bot license provisioned.",
                "license_key": lic_key
            })

        return JSONResponse({
            "verified": False,
            "message": f"Account #{mt5_account_id} not registered under partner IB group."
        }, status_code=400)


    def _verify_admin(self, request: Request) -> bool:
        """Constant-time verification of Admin API key."""
        key = request.headers.get("X-Admin-Key", "")
        expected = os.environ.get("ADMIN_API_KEY", ADMIN_API_KEY)
        return bool(key) and hmac.compare_digest(key, expected)

    async def admin_list_licenses(self, request: Request) -> JSONResponse:
        """Protected Admin Route: Lists all issued licenses and system status."""
        if not self._verify_admin(request):
            return JSONResponse({"error": "Unauthorized: Invalid or missing X-Admin-Key"}, status_code=401)

        conn = self.db._get_connection()
        cursor = conn.execute("SELECT license_key, user_email, tier, mt5_account_id, status, expires_at, gas_balance_usd, created_at FROM licenses ORDER BY created_at DESC LIMIT 100")
        rows = [dict(r) for r in cursor.fetchall()]
        return JSONResponse({"success": True, "total_licenses": len(rows), "licenses": rows})

    async def admin_revoke_license(self, request: Request) -> JSONResponse:
        """Protected Admin Route: Revokes a rogue or leaked license key."""
        if not self._verify_admin(request):
            return JSONResponse({"error": "Unauthorized: Invalid or missing X-Admin-Key"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        license_key = body.get("license_key", "").strip()
        if not license_key:
            return JSONResponse({"error": "Missing license_key"}, status_code=400)

        ok = self.db.update_license_status(license_key, LicenseStatus.REVOKED)
        if ok:
            self.db.log_audit("ADMIN_REVOCATION", license_key, "Revoked via Protected Admin API")
            return JSONResponse({"success": True, "message": f"License '{license_key}' successfully revoked."})
        return JSONResponse({"error": "License not found or update failed"}, status_code=404)

    async def health(self, request: Request) -> JSONResponse:
        return JSONResponse({
            "status": "healthy",
            "service": "XAUUSD Institutional Licensing & Billing Server",
            "timestamp": int(time.time())
        })


def create_app(db_path: str = "data/entitlement.db") -> Starlette:
    lic_app = LicensingApp(db_path)
    routes = [
        Route("/health", lic_app.health, methods=["GET"]),
        Route("/api/v1/license/validate", lic_app.validate_license, methods=["POST"]),
        Route("/api/v1/license/activate", lic_app.activate_license, methods=["POST"]),
        Route("/api/v1/billing/checkout", lic_app.create_checkout, methods=["POST"]),
        Route("/api/v1/webhooks/stripe", lic_app.webhook_stripe, methods=["POST"]),
        Route("/api/v1/webhooks/crypto", lic_app.webhook_crypto, methods=["POST"]),
        Route("/api/v1/webhooks/whop", lic_app.webhook_whop, methods=["POST"]),
        Route("/api/v1/affiliate/verify", lic_app.verify_affiliate, methods=["POST"]),
        # Protected Admin Endpoints
        Route("/api/v1/admin/licenses", lic_app.admin_list_licenses, methods=["GET"]),
        Route("/api/v1/admin/license/revoke", lic_app.admin_revoke_license, methods=["POST"]),
    ]

    # Explicit CORS Whitelist
    raw_origins = os.environ.get(
        "ALLOWED_CORS_ORIGINS",
        "https://smkanish2009-blip.github.io,http://localhost:3000,http://127.0.0.1:8000"
    )
    allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    middleware = [
        Middleware(SecurityHeadersAndRateLimitMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-Admin-Key"],
            allow_credentials=False
        ),
    ]

    # Explicit Debug=False for production security
    app = Starlette(debug=False, routes=routes, middleware=middleware)
    app.state.lic_app = lic_app
    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    print("[SERVER] Starting Licensing & Webhook Server on http://127.0.0.1:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
