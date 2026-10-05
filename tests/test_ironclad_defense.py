"""
Institutional Test Suite: 4-Layer Ironclad Defense System.
Verifies all failsafes, guardrails, watchdogs, slippage limits, and security vaults.
"""

import os
import sys

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

import os
import time
import unittest
import pandas as pd
import numpy as np

from strategy.models import TradeSignal, SignalDirection, SetupType
from config.settings import StrategyParameters
from strategy.dual_model_validator import DualModelValidator
from risk.input_guardrails import InputGuardrails
from core.latency_guard import LatencyGuard
from risk.circuit_breaker import CircuitBreaker
from telemetry.watchdog import HeartbeatWatchdog
from execution.slippage_guard import SlippageGuard
from execution.liquidity_guard import LiquidityGuard
from telemetry.mfa_webhook import MFAWebhook
from telemetry.telegram_bot import TelegramBot
from core.vault_manager import VaultManager


class TestIroncladDefenseSystem(unittest.TestCase):

    def setUp(self):
        self.params = StrategyParameters()
        self.validator = DualModelValidator(self.params)
        self.guardrails = InputGuardrails()
        self.latency_guard = LatencyGuard(max_allowed_latency_ms=500.0)
        self.circuit_breaker = CircuitBreaker(max_consecutive_losses=3, cooldown_seconds=14400)
        self.slippage_guard = SlippageGuard(max_slippage_usd=0.30)
        self.liquidity_guard = LiquidityGuard(max_liquidity_share_pct=1.0)
        self.telegram = TelegramBot(token="", chat_id="")
        self.mfa = MFAWebhook(self.telegram, mfa_risk_threshold_usd=250.0, timeout_sec=30)
        self.vault = VaultManager(vault_path="data/test_secrets.vault")

        # Synthetic market data
        np.random.seed(42)
        n = 250
        dates_h1 = pd.date_range(end="2026-09-25 10:00:00", periods=n, freq="1h")
        self.df_h1 = pd.DataFrame({
            "time": dates_h1,
            "open": np.linspace(2600, 2650, n),
            "high": np.linspace(2605, 2655, n),
            "low": np.linspace(2595, 2645, n),
            "close": np.linspace(2602, 2652, n),
            "tick_volume": np.full(n, 1200)
        })

        dates_m15 = pd.date_range(end="2026-09-25 10:00:00", periods=n, freq="15min")
        self.df_m15 = pd.DataFrame({
            "time": dates_m15,
            "open": np.linspace(2640, 2650, n),
            "high": np.linspace(2642, 2652, n),
            "low": np.linspace(2638, 2648, n),
            "close": np.linspace(2641, 2651, n),
            "tick_volume": np.full(n, 500)
        })

    def tearDown(self):
        if os.path.exists("data/test_secrets.vault"):
            try:
                os.remove("data/test_secrets.vault")
            except Exception:
                pass
        if os.path.exists("data/test_pulse.pulse"):
            try:
                os.remove("data/test_pulse.pulse")
            except Exception:
                pass

    # ==========================================
    # LAYER 1: CODE-LEVEL & LOGICAL FAILSAFES
    # ==========================================

    def test_layer1_dual_model_validator_pass(self):
        signal = TradeSignal(
            setup_type=SetupType.SETUP_A,
            direction=SignalDirection.BUY,
            entry_price=2655.0,
            stop_loss=2645.0,     # Risk = $10.0
            take_profit=2675.0,    # Reward = $20.0 (2.0R)
            risk_r=1.0,
            confidence_score=0.72
        )
        passed, msg = self.validator.validate_handshake(
            signal=signal,
            ai_confidence=0.72,
            df_m15=self.df_m15,
            df_h1=self.df_h1,
            range_high=2650.0,
            range_low=2640.0
        )
        self.assertTrue(passed, f"Handshake should pass: {msg}")

    def test_layer1_dual_model_validator_ai_veto(self):
        signal = TradeSignal(
            setup_type=SetupType.SETUP_A,
            direction=SignalDirection.BUY,
            entry_price=2655.0,
            stop_loss=2645.0,
            take_profit=2675.0,
            risk_r=1.0,
            confidence_score=0.52   # Below 0.58 threshold
        )
        passed, msg = self.validator.validate_handshake(
            signal=signal,
            ai_confidence=0.52,
            df_m15=self.df_m15,
            df_h1=self.df_h1,
            range_high=2650.0,
            range_low=2640.0
        )
        self.assertFalse(passed)
        self.assertIn("Model A confidence (0.52) < 0.58", msg)

    def test_layer1_dual_model_validator_rules_veto_bad_rr(self):
        signal = TradeSignal(
            setup_type=SetupType.SETUP_A,
            direction=SignalDirection.BUY,
            entry_price=2655.0,
            stop_loss=2645.0,     # Risk = $10.0
            take_profit=2660.0,    # Reward = $5.0 (0.5R) -> VIOLATION
            risk_r=1.0,
            confidence_score=0.85
        )
        passed, msg = self.validator.validate_handshake(
            signal=signal,
            ai_confidence=0.85,
            df_m15=self.df_m15,
            df_h1=self.df_h1,
            range_high=2650.0,
            range_low=2640.0
        )
        self.assertFalse(passed)
        self.assertIn("below minimum 1.4R", msg)

    def test_layer1_input_guardrails_clean(self):
        ok, msg = self.guardrails.sanitize(
            direction=SignalDirection.BUY,
            entry=2650.00,
            sl=2640.00,
            tp=2670.00,
            lots=0.50,
            current_market_price=2650.10
        )
        self.assertTrue(ok)
        self.assertIn("Clean", msg)

    def test_layer1_input_guardrails_geometry_inversion(self):
        # Buy with Stop Loss ABOVE Entry
        ok, msg = self.guardrails.sanitize(
            direction=SignalDirection.BUY,
            entry=2650.00,
            sl=2660.00,  # Inversion
            tp=2670.00,
            lots=0.50,
            current_market_price=2650.00
        )
        self.assertFalse(ok)
        self.assertIn("Geometry Inversion", msg)

    def test_layer1_input_guardrails_erratic_price_deviation(self):
        # Market price is $2650, proposed entry is $2680 (1.13% deviation, limit 0.35%)
        ok, msg = self.guardrails.sanitize(
            direction=SignalDirection.BUY,
            entry=2680.00,
            sl=2670.00,
            tp=2700.00,
            lots=0.50,
            current_market_price=2650.00
        )
        self.assertFalse(ok)
        self.assertIn("Erratic Entry Price", msg)

    def test_layer1_latency_guard_fresh_vs_stale(self):
        current_time_ms = int(time.time() * 1000)
        # Fresh tick with 50ms latency
        fresh_tick_msc = current_time_ms - 50
        is_fresh, lat, msg = self.latency_guard.verify_tick_freshness(fresh_tick_msc)
        self.assertTrue(is_fresh)

        # Stale tick with 2000ms latency
        stale_tick_msc = current_time_ms - 2000
        is_fresh, lat, msg = self.latency_guard.verify_tick_freshness(stale_tick_msc)
        self.assertFalse(is_fresh)
        self.assertIn("Stale Data Rejected", msg)

    def test_layer1_circuit_breaker(self):
        cb = CircuitBreaker(max_consecutive_losses=3, cooldown_seconds=60)
        # Loss 1
        cb.record_outcome(is_win=False)
        locked, rem = cb.is_locked_out()
        self.assertFalse(locked)

        # Loss 2
        cb.record_outcome(is_win=False)
        locked, rem = cb.is_locked_out()
        self.assertFalse(locked)

        # Loss 3 -> Lockout triggered!
        cb.record_outcome(is_win=False)
        locked, rem = cb.is_locked_out()
        self.assertTrue(locked)
        self.assertGreater(rem, 0.0)

        # Reset on win
        cb.record_outcome(is_win=True)
        self.assertEqual(cb.consecutive_losses, 0)

    # ==========================================
    # LAYER 2: INFRASTRUCTURE & NETWORK REDUNDANCY
    # ==========================================

    def test_layer2_heartbeat_watchdog_pulse(self):
        test_pulse = "data/test_pulse.pulse"
        HeartbeatWatchdog.write_pulse(test_pulse)
        self.assertTrue(os.path.exists(test_pulse))
        with open(test_pulse, "r") as f:
            ts = float(f.read().strip())
        self.assertAlmostEqual(ts, time.time(), delta=2.0)

    # ==========================================
    # LAYER 3: EXECUTION & BROKER INTEGRITY
    # ==========================================

    def test_layer3_slippage_guard(self):
        # Slippage within tolerance ($0.15 <= $0.30)
        ok, slip, msg = self.slippage_guard.verify_execution_slippage(expected_price=2650.00, filled_price=2650.15)
        self.assertTrue(ok)
        self.assertEqual(round(slip, 2), 0.15)

        # Slippage exceeding tolerance ($0.65 > $0.30)
        ok, slip, msg = self.slippage_guard.verify_execution_slippage(expected_price=2650.00, filled_price=2650.65)
        self.assertFalse(ok)
        self.assertIn("Slippage Alert", msg)

    def test_layer3_liquidity_guard(self):
        # 1 lot on 500 tick volume (1 lot <= 5.0 allowed) -> True
        ok, msg = self.liquidity_guard.verify_volume_share(lots=1.0, recent_m5_tick_volume=500)
        self.assertTrue(ok)

        # 10 lots on 150 tick volume (10 lots > 1.5 allowed) -> False
        ok, msg = self.liquidity_guard.verify_volume_share(lots=10.0, recent_m5_tick_volume=150)
        self.assertFalse(ok)
        self.assertIn("Liquidity Veto", msg)

    # ==========================================
    # LAYER 4: ACCESS CONTROL & OPERATIONAL SECURITY
    # ==========================================

    def test_layer4_mfa_webhook(self):
        # Below threshold: No MFA required
        self.assertFalse(self.mfa.requires_mfa(risk_usd=100.0, lots=0.20))

        # Above threshold: MFA required
        self.assertTrue(self.mfa.requires_mfa(risk_usd=300.0, lots=0.20))
        self.assertTrue(self.mfa.requires_mfa(risk_usd=100.0, lots=0.80))

        # Test challenge issuance (in demo/disabled mode auto-approves)
        token = self.mfa.request_authorization("BUY", "XAUUSD", 1.0, 2650.0, 2640.0, 2670.0, 300.0)
        self.assertEqual(len(token), 6)
        ok, msg = self.mfa.check_authorization(token)
        self.assertTrue(ok)

    def test_layer4_encrypted_secrets_vault(self):
        sample_secrets = {
            "MT5_LOGIN": 113182919,
            "MT5_PASSWORD": "SuperSecretPassword99!",
            "MT5_SERVER": "MetaQuotes-Demo",
            "GEMINI_API_KEY": "AIzaSyA8899FakeKeyForTesting"
        }
        saved = self.vault.encrypt_and_save(sample_secrets)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists("data/test_secrets.vault"))

        # Inspect raw file content to ensure no plain-text password exists
        with open("data/test_secrets.vault", "r") as f:
            raw = f.read()
        self.assertNotIn("SuperSecretPassword99!", raw)
        self.assertNotIn("AIzaSyA8899FakeKeyForTesting", raw)

        # Decrypt and verify exact match
        decrypted = self.vault.load_and_decrypt()
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted["MT5_LOGIN"], sample_secrets["MT5_LOGIN"])
        self.assertEqual(decrypted["MT5_PASSWORD"], sample_secrets["MT5_PASSWORD"])
        self.assertEqual(decrypted["GEMINI_API_KEY"], sample_secrets["GEMINI_API_KEY"])


if __name__ == "__main__":
    unittest.main()