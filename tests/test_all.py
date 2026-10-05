"""
Comprehensive Automated Unit Test Suite.
Validates TimeEngine, PositionSizer, Asian Range Detector, and RiskManager.
"""

import os
import sys
import unittest
from datetime import datetime, timezone, time
import pandas as pd
import numpy as np

# Ensure repository root is in Python path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import SessionSettings, StrategyParameters, RiskParameters, BotConfig
from core.time_engine import TimeEngine
from risk.position_sizer import PositionSizer
from risk.risk_manager import RiskManager
from indicators.range_detector import RangeDetector
from indicators.technicals import compute_atr, compute_ema, compute_adx


class TestXAUUSDBot(unittest.TestCase):

    def setUp(self):
        self.config = BotConfig()
        self.time_engine = TimeEngine(self.config.sessions)
        self.sizer = PositionSizer(self.config.risk)
        self.risk_mgr = RiskManager(self.config.risk)

    def test_time_engine_sessions(self):
        """Validates that session detection accurately matches GMT hours."""
        # 03:00 GMT should be Asian session
        dt_asian = datetime(2026, 9, 25, 3, 0, tzinfo=timezone.utc)
        self.assertTrue(self.time_engine.is_in_asian_window(dt_asian))
        self.assertFalse(self.time_engine.is_in_setup_a_window(dt_asian))

        # 08:30 GMT should be Setup A and Setup B window
        dt_london = datetime(2026, 9, 25, 8, 30, tzinfo=timezone.utc)
        self.assertFalse(self.time_engine.is_in_asian_window(dt_london))
        self.assertTrue(self.time_engine.is_in_setup_a_window(dt_london))
        self.assertTrue(self.time_engine.is_in_setup_b_window(dt_london))

        # 20:30 GMT should be past session flatten
        dt_night = datetime(2026, 9, 25, 20, 30, tzinfo=timezone.utc)
        self.assertTrue(self.time_engine.is_past_session_flatten(dt_night))

    def test_position_sizer_worked_example(self):
        """
        Validates the exact worked example from Section 8 of the PDF:
        Equity $10,000, risk 0.5% = $50. ATR(H1) = $10, Setup A stop = 1.5 x 10 = $15.
        Loss per lot = 15 x 100 = $1,500. Lots = 50 / 1,500 = 0.033 -> 0.03 lots.
        """
        equity = 10000.0
        entry = 2650.0
        stop = 2635.0  # $15 stop
        tick_size = 0.01
        tick_value = 1.00  # $100 per lot move of $1.00

        lots, risk_usd = self.sizer.calculate_lots(
            equity=equity, entry_price=entry, stop_loss=stop,
            tick_size=tick_size, tick_value=tick_value,
            min_lot=0.01, max_lot=100.0, lot_step=0.01, risk_pct_override=0.50
        )
        self.assertEqual(lots, 0.03)
        self.assertAlmostEqual(risk_usd, 50.0)

    def test_risk_manager_kill_switch(self):
        """Validates that an 8% drawdown halts trading."""
        self.risk_mgr.on_new_day(10000.0)
        # Drop to 9100 (-9%)
        is_blocked, msg = self.risk_mgr.update_equity(9100.0)
        self.assertTrue(is_blocked)
        self.assertTrue("kill-switch" in msg.lower())

    def test_range_detector_validity(self):
        """Validates Asian range height constraints."""
        detector = RangeDetector(self.config.strategy, self.config.sessions)
        # Construct synthetic M5 bars for Asian session
        times = pd.date_range("2026-09-25 00:00", "2026-09-25 06:55", freq="5min", tz="UTC")
        df_m5 = pd.DataFrame({
            "time": times,
            "open": 2650.0,
            "high": 2660.0,  # $10 height
            "low": 2650.0,
            "close": 2655.0
        })
        h1_atr = 10.0  # Range height = 1.0x ATR (between 0.8 and 3.0)
        asian_range = detector.calculate_range(df_m5, h1_atr, datetime(2026, 9, 25).date())
        self.assertIsNotNone(asian_range)
        self.assertTrue(asian_range.is_valid)
        self.assertEqual(asian_range.height, 10.0)


if __name__ == "__main__":
    unittest.main()
