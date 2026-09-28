"""
Domain Models and Schemas for Monetization & Entitlement.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BillingTier(str, Enum):
    SAAS_MONTHLY = "SAAS_MONTHLY"          # $50/month recurring
    SAAS_ANNUAL = "SAAS_ANNUAL"            # $450/year recurring
    PROFIT_SHARE = "PROFIT_SHARE"          # High-Water Mark 20% + Gas Wallet
    LIFETIME_PERPETUAL = "LIFETIME_PERPETUAL"  # One-time payment with machine lock
    IB_AFFILIATE_FREE = "IB_AFFILIATE_FREE"    # Free tier for partner broker accounts


class LicenseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    GRACEFUL_DISCONNECT = "GRACEFUL_DISCONNECT"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class PaymentGateway(str, Enum):
    STRIPE = "STRIPE"
    CRYPTO_USDT = "CRYPTO_USDT"
    WHOP = "WHOP"
    IB_AFFILIATE = "IB_AFFILIATE"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class LicenseRecord(BaseModel):
    license_key: str
    user_email: str
    tier: BillingTier
    mt5_account_id: Optional[int] = None
    machine_fingerprint: Optional[str] = None
    status: LicenseStatus = LicenseStatus.ACTIVE
    expires_at: Optional[datetime] = None  # None for perpetual lifetime
    gas_balance_usd: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EntitlementToken(BaseModel):
    is_authorized: bool
    license_key: str
    tier: BillingTier
    status: LicenseStatus
    mt5_account_id: Optional[int] = None
    expires_at: Optional[str] = None
    gas_balance_usd: float = 0.0
    allows_new_trades: bool
    allows_position_management: bool
    reason: str
    timestamp: int
    hmac_signature: str


class CheckoutRequest(BaseModel):
    user_email: str
    tier: BillingTier
    mt5_account_id: Optional[int] = None
    gas_topup_amount_usd: Optional[float] = None
    gateway: PaymentGateway = PaymentGateway.STRIPE


class CryptoInvoice(BaseModel):
    invoice_id: str
    user_email: str
    tier: BillingTier
    amount_usdt: float
    network: str = "TRC20"  # TRC20, ERC20, BEP20
    deposit_address: str
    qr_code_intent: str
    status: PaymentStatus = PaymentStatus.PENDING
    expires_at: str
    created_at: str
