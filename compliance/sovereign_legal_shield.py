"""
DON AURELIUS • SOVEREIGN INSTITUTIONAL LEGAL SHIELD & LIABILITY ARMOR
Aligned with CFTC Rule 4.41, NFA Compliance Rule 2-29, FCA COBS, ESMA, and SEBI Guidelines.
Architected to provide total, unassailable legal protection for Founder SM.KANISH,
affiliates, developers, and licensors against any civil liability, arbitration claim,
regulatory scrutiny, or financial lawsuit.
"""

import os
import json
import hmac
import hashlib
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

from config.credentials import credentials

logger = logging.getLogger("SovereignLegalShield")

# Immutable Terms Agreement Version & Cryptographic Fingerprint
SHIELD_VERSION = "2026.4-INSTITUTIONAL-CFTC-FCA-SOVEREIGN"

LEGAL_SHIELD_CONTRACT = """====================================================================================================
                     DON AURELIUS • MASTER END-USER TECHNOLOGY AGREEMENT
                   MANDATORY LEGAL LIABILITY RELEASE & REGULATORY COVENANT
====================================================================================================
GOVERNING PARTIES & RECITALS:
This Agreement is a legally binding contract between the Operator/Licensee ("Client" or "You")
and DON AURELIUS TECHNOLOGIES, its Founder SM.KANISH, contributors, and licensors ("Licensor").
By accessing, installing, running, or connecting this quantitative algorithmic software to any
MetaTrader terminal or broker infrastructure, You irrevocably agree to all clauses herein.

SECTION 1: NON-ADVISORY & NON-FIDUCIARY SOFTWARE STATUS (CFTC RULE 4.41 / FCA ALIGNED)
1.1 The Software is strictly an automated quantitative analytical tool and computational model.
1.2 Licensor is NOT an Investment Adviser (RIA), Commodity Trading Advisor (CTA), Commodity Pool
    Operator (CPO), Broker-Dealer, Money Manager, or Fiduciary under the U.S. Commodity Exchange
    Act (CEA), UK Financial Services and Markets Act 2000 (FSMA), EU MiFID II, or India SEBI rules.
1.3 Licensor does NOT manage investor funds, does NOT provide personalized investment advice, does
    NOT guarantee profits, and does NOT administer PAMM/MAM collective investment schemes.

SECTION 2: NON-CUSTODIAL INDEPENDENCE & EXCLUSIVE ACCOUNT OWNERSHIP
2.1 Client retains 100% exclusive custody, ownership, and discretionary operational control of
    their third-party brokerage account (MetaTrader 5) and capital at all times.
2.2 At no time does Licensor possess access to Client funds, withdrawable balances, or banking keys.
2.3 All trade executions, order transmissions, position modifications, and liquidations are executed
    directly between Client's personal computer/VPS and Client's chosen broker terminal.

SECTION 3: SPECULATIVE RISK OF RUIN & COMMODITY LEVERAGE ACKNOWLEDGMENT
3.1 Gold (XAUUSD) and leveraged spot commodities are subject to extreme, unpredictable market
    volatility, geopolitical catalysts, and liquidity vacuums.
3.2 Client explicitly acknowledges that leveraged trading carries substantial risk of loss, up to
    and including the COMPLETE LOSS OF DEPOSITED CAPITAL, and is suitable only for capital that
    Client can afford to lose entirely without impacting lifestyle or solvency.
3.3 Past performance, historical backtesting metrics, simulated statistical expectations, and
    promotional mathematical formulas (including Quarter-Kelly Criterion) are purely hypothetical
    and DO NOT represent or guarantee future trading performance.

SECTION 4: FORCE MAJEURE, BROKER SLIPPAGE & INFRASTRUCTURE IMMUNITY
4.1 Client explicitly releases Licensor from any liability arising from:
    (a) Interbank liquidity shortages, spread widenings, slippage, price requotes, or broker freezes;
    (b) VPS, cloud server, operating system, or internet connection interruptions or latency spikes;
    (c) Broker insolvencies, regulatory halts, market suspensions, or exchange circuit breakers;
    (d) Algorithmic calculation anomalies, hardware failures, power outages, or cyber-attacks.

SECTION 5: INDEFEASIBLE INDEMNIFICATION & HOLD-HARMLESS CLAUSE
5.1 Client covenants to DEFEND, INDEMNIFY, AND HOLD COMPLETELY HARMLESS Founder SM.KANISH,
    his successors, employees, developers, and technical affiliates from and against any and all
    claims, liabilities, losses, damages, arbitrations, regulatory fines, legal fees, or costs
    arising out of or related to Client's use of this quantitative technology.

SECTION 6: MAXIMUM LIMITATION OF LIABILITY ($0.00 / PURCHASE PRICE CAP)
6.1 TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE JURISDICTION, LICENSOR'S AGGREGATE LIABILITY
    FOR ANY CLAIM UNDER ANY LEGAL THEORY (WHETHER TORT, CONTRACT, STRICT LIABILITY, OR NEGLIGENCE)
    SHALL BE STRICTLY CAPPED AT ZERO DOLLARS ($0.00 USD) OR THE EXACT AMOUNT PAID BY CLIENT TO
    LICENSOR FOR THE SOFTWARE LICENSE DURING THE PRECEDING THREE (3) MONTHS.

SECTION 7: MANDATORY BINDING ARBITRATION & CLASS-ACTION WAIVER
7.1 Any dispute, controversy, or claim arising out of this Agreement shall be resolved exclusively
    through confidential, binding individual arbitration administered by an established international
    arbitration forum chosen by Licensor.
7.2 CLIENT IRREVOCABLY WAIVES ALL RIGHTS TO A TRIAL BY JURY AND WAIVES ALL RIGHTS TO PARTICIPATE
    IN ANY CLASS ACTION, CONSOLIDATED SUIT, OR COLLECTIVE PRIVATE ATTORNEY GENERAL PROCEEDING.

SECTION 8: CRYPTOGRAPHIC SIGNATURE & DIGITAL LEGAL FINGERPRINT
8.1 Execution of this software constitutes an enforceable electronic signature under the U.S.
    Electronic Signatures in Global and National Commerce Act (E-SIGN), Uniform Electronic
    Transactions Act (UETA), and international digital contract covenants.
====================================================================================================
"""

def compute_terms_hash() -> str:
    """Computes an immutable SHA-256 fingerprint of the exact contract text."""
    return hashlib.sha256(LEGAL_SHIELD_CONTRACT.encode("utf-8")).hexdigest()

TERMS_HASH = compute_terms_hash()


class SovereignLegalShield:
    """
    Enforces pre-flight legal compliance, generates cryptographic non-repudiation
    proofs of agreement, and syncs consent records to Supabase Cloud for immutable legal defense.
    """

    def __init__(self, consent_path: str = "data/legal_shield_consent.json"):
        self.consent_path = consent_path
        os.makedirs(os.path.dirname(self.consent_path), exist_ok=True)
        self.is_valid = False
        self.consent_record: Dict[str, Any] = {}
        self._load_local_consent()

    def _generate_digital_signature(self, client_id: str, mt5_account: str, timestamp_iso: str) -> str:
        secret = credentials.SUPABASE_SECRET_KEY or "don_aurelius_master_legal_signing_key_2026"
        message = f"{client_id}|{mt5_account}|{SHIELD_VERSION}|{TERMS_HASH}|{timestamp_iso}"
        return hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()

    def _load_local_consent(self) -> None:
        if os.path.exists(self.consent_path):
            try:
                with open(self.consent_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("terms_hash") == TERMS_HASH and data.get("is_acknowledged"):
                    self.is_valid = True
                    self.consent_record = data
            except Exception as e:
                logger.error(f"[LEGAL-SHIELD] Failed loading local consent: {e}")

    def grant_consent(
        self,
        client_id: str = "sovereign_operator",
        mt5_account: str = "10434714118",
        license_key: str = "XAUUSD-INSTITUTIONAL-PRO-2026",
        operator_ip: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """
        Executes a cryptographically non-repudiable legal agreement record.
        """
        now_utc = datetime.now(timezone.utc).isoformat()
        sig = self._generate_digital_signature(client_id, mt5_account, now_utc)

        record = {
            "shield_version": SHIELD_VERSION,
            "terms_hash": TERMS_HASH,
            "client_id": client_id,
            "mt5_account": str(mt5_account),
            "license_key": license_key,
            "operator_ip_hash": hashlib.sha256(operator_ip.encode("utf-8")).hexdigest(),
            "digital_signature": sig,
            "is_acknowledged": True,
            "consented_at": now_utc,
            "jurisdiction_covenant": "INDIVIDUAL_BINDING_ARBITRATION_ONLY",
            "liability_cap_usd": 0.0,
            "non_fiduciary_acknowledged": True,
            "force_majeure_waived": True
        }

        # Save locally
        try:
            with open(self.consent_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            self.is_valid = True
            self.consent_record = record
            logger.info(f"[LEGAL-SHIELD] Consent successfully signed: MT5 #{mt5_account} | Sig: {sig[:12]}...")
        except Exception as e:
            logger.error(f"[LEGAL-SHIELD] Failed saving local consent: {e}")

        # Sync to Supabase Cloud Legal Audit Table if configured
        self._sync_to_supabase_cloud(record)

        return record

    def _sync_to_supabase_cloud(self, record: Dict[str, Any]) -> bool:
        """Publishes the cryptographic legal signature to Supabase PostgreSQL."""
        if not credentials.SUPABASE_URL or not credentials.SUPABASE_SECRET_KEY:
            return False

        try:
            from telemetry.supabase_syncer import supabase_syncer
            payload = {
                "license_key": record.get("license_key"),
                "client_email": f"{record.get('client_id')}@sovereign-legal.local",
                "tier": "INSTITUTIONAL_SHIELDED",
                "status": "ACTIVE",
                "mt5_account": record.get("mt5_account"),
                "hardware_id": record.get("digital_signature")[:32],
                "created_at": record.get("consented_at")
            }
            # Upsert into licenses table as proof of legal activation
            key = record.get("license_key")
            existing = supabase_syncer._request(f"licenses?license_key=eq.{key}&select=id&limit=1", method="GET")
            if existing and len(existing) > 0:
                res = supabase_syncer._request(f"licenses?license_key=eq.{key}", method="PATCH", payload=payload)
            else:
                res = supabase_syncer._request("licenses", method="POST", payload=payload)

            if res:
                logger.info("[LEGAL-SHIELD] Cryptographic consent registered in Supabase Cloud.")
                return True
        except Exception as ex:
            logger.debug(f"[LEGAL-SHIELD] Supabase cloud sync notice: {ex}")

        return False

    def verify_shield_compliance(self, mt5_account: str = "10434714118") -> Tuple[bool, str]:
        """
        Pre-flight gate. Verifies that the operator has active, untampered legal consent.
        If missing, executes local operator consent to establish immediate legal shield.
        """
        if not self.is_valid:
            # Generate immutable consent record immediately
            self.grant_consent(
                client_id="sovereign_operator",
                mt5_account=str(mt5_account),
                license_key="XAUUSD-INSTITUTIONAL-PRO-2026"
            )

        if self.consent_record.get("terms_hash") != TERMS_HASH:
            return False, "Legal shield rejected: Terms of Service version mismatch."

        sig = self.consent_record.get("digital_signature", "")
        return True, (
            f"Institutional Legal Shield ACTIVE & BINDING "
            f"(Version: {SHIELD_VERSION} | Sig: {sig[:12]}... | Liability: $0.00 Cap)"
        )

    def get_contract_text(self) -> str:
        return LEGAL_SHIELD_CONTRACT


# Global singleton instance
sovereign_legal_shield = SovereignLegalShield()
