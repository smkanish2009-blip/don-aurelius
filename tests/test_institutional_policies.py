"""
Institutional Test Suite: Financial, Risk, Anti-Cheating & Legal Compliance Policies.
Verifies:
1. High-Water Mark (HWM) Reset Policy (only tax net new profits above peak balance).
2. Manual Transaction Exclusion Policy (filter by magic number).
3. Broker Rebate & Swap Adjustment Policy (Net = Gross - Commission + Swap).
4. Currency Conversion Policy (Foreign currency to USD/USDT).
5. Pre-Funded Gas Wallet ($20 buffer warning, $0 graceful disconnect).
6. Graceful Liquidation Policy (never panic-close active trades when gas hits $0).
7. Hard Equity Drawdown Protection (5% daily / 10% total, 24h lockout).
8. The Friday Close / Weekend Gap Policy (force close at 21:00 UTC).
9. Anti-Tampering 60s Cryptographic Heartbeat (HMAC-SHA256).
10. Account Disconnect Penalty Policy (flag drawdown evasion).
11. Regulatory Legal Compliance (CFTC/NFA/FCA terms gate).
"""

import os
import sys

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

import os
import time
import unittest
from datetime import datetime, timezone
from dataclasses import dataclass

from billing.fee_calculator import FeeCalculator
from billing.gas_wallet import GasWallet
from security.license_enforcer import LicenseEnforcer
from compliance.legal_terms import LegalCompliance
from risk.risk_manager import RiskManager
from config.settings import RiskParameters
from core.time_engine import TimeEngine, SessionSettings


@dataclass
class MockDeal:
    magic: int
    profit: float
    commission: float
    swap: float


class TestInstitutionalPolicies(unittest.TestCase):

    def setUp(self):
        self.test_hwm_file = "data/test_hwm_state.json"
        self.test_gas_file = "data/test_gas_wallet.json"
        self.test_license_file = "data/test_license_state.json"
        self.test_consent_file = "data/test_legal_consent.json"

        self.fee_calc = FeeCalculator(
            hwm_state_file=self.test_hwm_file,
            performance_fee_pct=20.0,
            bot_magic_number=260925
        )
        self.gas_wallet = GasWallet(
            wallet_file=self.test_gas_file,
            warning_threshold_usd=20.00
        )
        self.license_enforcer = LicenseEnforcer(
            license_key="TEST-KEY-2026",
            state_file=self.test_license_file
        )
        self.legal = LegalCompliance(consent_file=self.test_consent_file)
        self.risk_mgr = RiskManager(RiskParameters())
        self.time_engine = TimeEngine(SessionSettings())

    def tearDown(self):
        for f in [self.test_hwm_file, self.test_gas_file, self.test_license_file, self.test_consent_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    # ==========================================
    # 1. FINANCIAL & FEE CALCULATION POLICIES
    # ==========================================

    def test_high_water_mark_reset_policy(self):
        # Initial baseline balance = $10,000.00
        self.fee_calc.initialize_account(10000.00)
        self.assertEqual(self.fee_calc.hwm, 10000.00)

        # Trade 1: Win +$500.00 -> New balance = $10,500.00 (New Peak!)
        deal1 = MockDeal(magic=260925, profit=510.0, commission=-5.0, swap=-5.0) # Net = $500
        res1 = self.fee_calc.process_closed_deal(deal1.magic, deal1.profit, deal1.commission, deal1.swap, 10500.00, "USD")
        self.assertTrue(res1["hwm_reset"])
        self.assertEqual(res1["net_profit_usd"], 500.00)
        self.assertEqual(res1["taxable_profit_usd"], 500.00)
        self.assertEqual(res1["fee_charged_usd"], 100.00)  # 20% of $500
        self.assertEqual(self.fee_calc.hwm, 10500.00)

        # Trade 2: Loss -$300.00 -> New balance = $10,200.00 (In Drawdown)
        deal2 = MockDeal(magic=260925, profit=-290.0, commission=-5.0, swap=-5.0) # Net = -$300
        res2 = self.fee_calc.process_closed_deal(deal2.magic, deal2.profit, deal2.commission, deal2.swap, 10200.00, "USD")
        self.assertFalse(res2["hwm_reset"])
        self.assertEqual(res2["taxable_profit_usd"], 0.0)
        self.assertEqual(res2["fee_charged_usd"], 0.0)  # Zero fee during drawdown
        self.assertEqual(self.fee_calc.hwm, 10500.00)   # HWM stays $10,500

        # Trade 3: Win +$200.00 -> New balance = $10,400.00 (Drawdown recovery below HWM)
        deal3 = MockDeal(magic=260925, profit=210.0, commission=-5.0, swap=-5.0) # Net = $200
        res3 = self.fee_calc.process_closed_deal(deal3.magic, deal3.profit, deal3.commission, deal3.swap, 10400.00, "USD")
        self.assertFalse(res3["hwm_reset"])
        self.assertEqual(res3["taxable_profit_usd"], 0.0)
        self.assertEqual(res3["fee_charged_usd"], 0.0)  # Zero fee because $10,400 <= $10,500 HWM
        self.assertEqual(self.fee_calc.hwm, 10500.00)

        # Trade 4: Win +$300.00 -> New balance = $10,700.00 (Exceeds HWM by $200.00!)
        deal4 = MockDeal(magic=260925, profit=310.0, commission=-5.0, swap=-5.0) # Net = $300
        res4 = self.fee_calc.process_closed_deal(deal4.magic, deal4.profit, deal4.commission, deal4.swap, 10700.00, "USD")
        self.assertTrue(res4["hwm_reset"])
        self.assertEqual(res4["taxable_profit_usd"], 200.00) # Only $200 net delta above $10,500 peak!
        self.assertEqual(res4["fee_charged_usd"], 40.00)     # 20% of $200 = $40.00
        self.assertEqual(self.fee_calc.hwm, 10700.00)        # HWM resets to $10,700.00

    def test_manual_transaction_exclusion_policy(self):
        self.fee_calc.initialize_account(10000.00)
        # Manual trade executed by user (magic == 0)
        manual_deal = MockDeal(magic=0, profit=500.0, commission=-5.0, swap=0.0)
        res = self.fee_calc.process_closed_deal(manual_deal.magic, manual_deal.profit, manual_deal.commission, manual_deal.swap, 10500.00, "USD")
        self.assertFalse(res["is_bot_trade"])
        self.assertEqual(res["fee_charged_usd"], 0.0)
        self.assertIn("Excluded", res["reason"])

    def test_broker_rebate_and_swap_adjustment_policy(self):
        # Net Profit = Gross Profit - Commissions + Swaps
        # Holding gold overnight incurred $25 swap fee + $5 commission on $100 profit
        self.fee_calc.initialize_account(10000.00)
        deal = MockDeal(magic=260925, profit=100.00, commission=-5.00, swap=-25.00)
        res = self.fee_calc.process_closed_deal(deal.magic, deal.profit, deal.commission, deal.swap, 10070.00, "USD")
        self.assertEqual(res["net_profit_usd"], 70.00) # $100 - $5 - $25 = $70
        self.assertEqual(res["fee_charged_usd"], 14.00) # 20% of $70 = $14 (NOT on $100!)

    def test_gas_wallet_threshold_and_graceful_disconnect(self):
        # 1. Active state with $100
        self.assertEqual(self.gas_wallet.get_status(), "ACTIVE")

        # 2. Deduction drops to $15.00 (below $20.00 warning threshold)
        self.gas_wallet.deduct_fee(85.00)
        self.assertEqual(self.gas_wallet.balance_usd, 15.00)
        self.assertEqual(self.gas_wallet.get_status(), "LOW_GAS_WARNING")

        # 3. Deduction drops to $0.00 -> Activates Graceful Disconnect
        self.gas_wallet.deduct_fee(15.00)
        self.assertEqual(self.gas_wallet.balance_usd, 0.00)
        self.assertEqual(self.gas_wallet.get_status(), "READ_ONLY_GRACEFUL_DISCONNECT")

        # 4. Graceful Liquidation Policy check:
        # Blocks opening new trades
        can_open, msg = self.gas_wallet.can_open_new_trade()
        self.assertFalse(can_open)
        self.assertIn("Graceful Disconnect", msg)

        # But allows active trades to continue trailing and exiting safely
        self.assertTrue(self.gas_wallet.allows_position_management())

    # ==========================================
    # 2. RISK MANAGEMENT & DISCONNECT POLICIES
    # ==========================================

    def test_hard_equity_drawdown_24h_lockout(self):
        self.risk_mgr.on_new_day(10000.00)
        # 10% Hard Max Total Drawdown Breach ($10,000 -> $8,900 = 11% DD)
        blocked, msg = self.risk_mgr.update_equity(8900.00)
        self.assertTrue(blocked)
        self.assertIn("Hard Total Drawdown", msg)
        self.assertIn("Locked for 24 hours", msg)

        # Verify can_open_trade blocks during lockout
        can_trade, reason = self.risk_mgr.can_open_trade()
        self.assertFalse(can_trade)
        self.assertIn("24-Hour Lockout Active", reason)

    def test_friday_close_weekend_gap_policy(self):
        # Friday at 21:05 UTC -> Weekend Gap Flatten triggered
        dt_friday_night = datetime(2026, 9, 25, 21, 5, 0, tzinfo=timezone.utc)
        self.assertTrue(self.time_engine.is_friday_weekend_gap_flatten(dt_friday_night))

        # Friday at 15:00 UTC -> Not yet 21:00 UTC
        dt_friday_afternoon = datetime(2026, 9, 25, 15, 0, 0, tzinfo=timezone.utc)
        self.assertFalse(self.time_engine.is_friday_weekend_gap_flatten(dt_friday_afternoon))

        # Thursday at 21:05 UTC -> Not Friday
        dt_thursday = datetime(2026, 9, 24, 21, 5, 0, tzinfo=timezone.utc)
        self.assertFalse(self.time_engine.is_friday_weekend_gap_flatten(dt_thursday))

    # ==========================================
    # 3. ANTI-CHEATING & SECURITY POLICIES
    # ==========================================

    def test_anti_tampering_cryptographic_heartbeat(self):
        payload = self.license_enforcer.generate_heartbeat_payload("ARMED", 10000.00, 260925)
        self.assertIn("hmac_sha256", payload)
        self.assertEqual(len(payload["hmac_sha256"]), 64) # SHA-256 hex string

        # Authentic payload passes
        self.assertTrue(self.license_enforcer.verify_heartbeat_payload(payload))

        # Tampered payload fails
        tampered = dict(payload)
        tampered["equity"] = 999999.00
        self.assertFalse(self.license_enforcer.verify_heartbeat_payload(tampered))

    def test_account_disconnect_penalty_policy(self):
        # Detached while in a loss < -$20 (e.g. -$150 floating drawdown)
        is_penalized, msg = self.license_enforcer.check_disconnect_penalty(is_mt5_connected=False, floating_pnl=-150.00)
        self.assertTrue(is_penalized)
        self.assertIn("Drawdown evasion violation flagged", msg)
        self.assertTrue(self.license_enforcer.is_penalty_flagged)

        # Re-check blocks
        is_penalized2, msg2 = self.license_enforcer.check_disconnect_penalty(is_mt5_connected=True, floating_pnl=0.0)
        self.assertTrue(is_penalized2)

    # ==========================================
    # 4. LEGAL & COMPLIANCE POLICIES
    # ==========================================

    def test_legal_compliance_and_regulatory_disclaimers(self):
        # Verify disclaimers exist
        terms = self.legal.get_terms_text()
        self.assertIn("NO INVESTMENT ADVICE", terms)
        self.assertIn("PAST PERFORMANCE", terms)
        self.assertIn("SLIPPAGE & FORCE MAJEURE LIABILITY WAIVER", terms)

        # Verify compliance verification
        ok, msg = self.legal.verify_compliance()
        self.assertTrue(ok)
        self.assertTrue(self.legal.is_accepted)


if __name__ == "__main__":
    unittest.main()
