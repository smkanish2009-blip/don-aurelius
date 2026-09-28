"""
Unit Test Suite for Advanced Institutional Features:
1. Prop-Firm Compliance Guard (120s Anti-Scalping, Lot Cap, No-Hedging, 45% Consistency).
2. Two-Way Interactive Telegram Remote Control (/status, /pause, /resume, /flatten, /wallet).
3. Higher-Timeframe (H4 / Daily) Macro Trend Bias Filter.
4. Rollover Spread Spike (21:50-22:20 GMT) & Bank Holiday Blackout Manager.
5. Windows Auto-Recovery Launcher Script Integrity.
"""

import os
import time
import unittest
from datetime import datetime, timezone, date
import pandas as pd
import numpy as np

from config.settings import PropFirmSettings, MacroTrendSettings, HolidaySettings
from risk.prop_firm_guard import PropFirmGuard
from telemetry.telegram_commander import TelegramCommander
from indicators.macro_trend import MacroTrendFilter, MacroTrendDirection
from core.holiday_manager import HolidayManager


class TestInstitutionalAdvanced(unittest.TestCase):

    # --- 1. Prop-Firm Compliance Tests ---
    def test_anti_scalping_minimum_duration(self):
        guard = PropFirmGuard(PropFirmSettings(PROP_FIRM_MODE=True, MIN_TRADE_DURATION_SEC=120))
        ticket = 1001
        now = time.time()
        # Open 30 seconds ago
        guard.record_trade_opened(ticket, open_time_sec=now - 30.0)

        # Non-emergency exit must be BLOCKED
        can_close, msg = guard.can_close_position(ticket, is_hard_stop_loss=False)
        self.assertFalse(can_close)
        self.assertIn("HFT scalping violation", msg)

        # Emergency Stop Loss trigger is EXEMPT (capital protection)
        can_sl, _ = guard.can_close_position(ticket, is_hard_stop_loss=True)
        self.assertTrue(can_sl)

        # After 121 seconds, exit must be APPROVED
        guard.record_trade_opened(ticket, open_time_sec=now - 125.0)
        can_close_late, _ = guard.can_close_position(ticket, is_hard_stop_loss=False)
        self.assertTrue(can_close_late)

    def test_lot_cap_clamping(self):
        guard = PropFirmGuard(PropFirmSettings(PROP_FIRM_MODE=True, MAX_SINGLE_ORDER_LOTS=5.00))
        # 12.0 lots must clamp to 5.0
        lots, msg = guard.clamp_lot_size(12.0)
        self.assertEqual(lots, 5.0)
        self.assertIn("clamped", msg)

        # 2.5 lots within limits remains 2.5
        lots_ok, _ = guard.clamp_lot_size(2.5)
        self.assertEqual(lots_ok, 2.5)

    def test_no_hedging_rule(self):
        guard = PropFirmGuard(PropFirmSettings(PROP_FIRM_MODE=True, ALLOW_HEDGING=False))
        # Existing open position is BUY (type=0)
        open_pos = [{"type": 0, "ticket": 501}]

        # Propose another BUY: allowed
        ok_buy, _ = guard.validate_no_hedging("BUY", open_pos)
        self.assertTrue(ok_buy)

        # Propose a SELL: strictly BLOCKED by no-hedging rule
        ok_sell, msg = guard.validate_no_hedging("SELL", open_pos)
        self.assertFalse(ok_sell)
        self.assertIn("Active BUY position already open", msg)

    def test_profit_consistency_rule(self):
        guard = PropFirmGuard(PropFirmSettings(PROP_FIRM_MODE=True, CONSISTENCY_MAX_DAILY_PROFIT_PCT=45.0))
        # Challenge target = $10,000. 45% cap = $4,500.
        # $3,000 profit is safe
        ok_safe, _ = guard.check_profit_consistency(3000.0, challenge_target=10000.0)
        self.assertTrue(ok_safe)

        # $4,600 profit hits the 45% consistency rule -> pauses trading
        ok_breach, msg = guard.check_profit_consistency(4600.0, challenge_target=10000.0)
        self.assertFalse(ok_breach)
        self.assertIn("reached 45.0%", msg)

    # --- 2. Two-Way Interactive Telegram Remote Control Tests ---
    def test_telegram_commander_security_and_commands(self):
        commander = TelegramCommander(
            token="mock_token",
            chat_id="123456789"
        )
        commander.get_status_callback = lambda: "Equity: $100,000 | State: ARMED"
        commander.pause_callback = lambda: "TRADING_PAUSED"
        commander.resume_callback = lambda: "TRADING_RESUMED"
        commander.flatten_callback = lambda: "EMERGENCY_FLATTENED"
        commander.get_wallet_callback = lambda: "Gas: $500.00 | HWM: $100,000"

        # 1. Unauthorized sender rejected
        bad_reply = commander.process_command(sender_chat_id="999999999", text="/status")
        self.assertIn("ACCESS DENIED", bad_reply)

        # 2. Authorized /status
        status_reply = commander.process_command(sender_chat_id="123456789", text="/status")
        self.assertEqual(status_reply, "Equity: $100,000 | State: ARMED")

        # 3. Authorized /pause and /resume
        self.assertEqual(commander.process_command("123456789", "/pause"), "TRADING_PAUSED")
        self.assertEqual(commander.process_command("123456789", "/resume"), "TRADING_RESUMED")

        # 4. Authorized /flatten emergency kill
        self.assertEqual(commander.process_command("123456789", "/flatten"), "EMERGENCY_FLATTENED")

        # 5. Authorized /wallet
        self.assertEqual(commander.process_command("123456789", "/wallet"), "Gas: $500.00 | HWM: $100,000")

    # --- 3. Higher-Timeframe Macro Trend Filter Tests ---
    def test_macro_trend_filter(self):
        macro_filter = MacroTrendFilter(MacroTrendSettings(ENABLED=True))

        # Synthetic Bullish H4 data: 250 bars rising from 2000 to 2500
        closes = np.linspace(2000, 2500, 250)
        df_bull = pd.DataFrame({"close": closes})

        dir_bull, ema50, ema200 = macro_filter.get_macro_trend(df_bull)
        self.assertEqual(dir_bull, MacroTrendDirection.BULLISH)
        self.assertGreater(ema50, ema200)

        # Setup A: Buy allowed in Bullish, Sell BLOCKED
        ok_buy, _ = macro_filter.validate_setup_a("BUY", df_bull)
        self.assertTrue(ok_buy)
        ok_sell, msg_sell = macro_filter.validate_setup_a("SELL", df_bull)
        self.assertFalse(ok_sell)
        self.assertIn("H4 trend is BULLISH", msg_sell)

        # Synthetic Bearish H4 data: 250 bars falling from 2500 to 2000
        closes_bear = np.linspace(2500, 2000, 250)
        df_bear = pd.DataFrame({"close": closes_bear})

        dir_bear, _, _ = macro_filter.get_macro_trend(df_bear)
        self.assertEqual(dir_bear, MacroTrendDirection.BEARISH)

        # Setup A: Sell allowed in Bearish, Buy BLOCKED
        ok_buy_bear, msg_buy_bear = macro_filter.validate_setup_a("BUY", df_bear)
        self.assertFalse(ok_buy_bear)
        self.assertIn("H4 trend is BEARISH", msg_buy_bear)
        ok_sell_bear, _ = macro_filter.validate_setup_a("SELL", df_bear)
        self.assertTrue(ok_sell_bear)

        # Setup B: Counter-trend sweep requires >= 60% wick
        # Propose BUY sweep during Bearish trend with 40% wick -> REJECTED
        ok_b_weak, msg_b_weak = macro_filter.validate_setup_b("BUY", 0.40, 0.70, df_bear)
        self.assertFalse(ok_b_weak)
        self.assertIn("Rejection wick", msg_b_weak)

        # Propose BUY sweep during Bearish trend with 65% wick and high AI -> APPROVED
        ok_b_strong, _ = macro_filter.validate_setup_b("BUY", 0.65, 0.70, df_bear)
        self.assertTrue(ok_b_strong)

    # --- 4. Rollover Spread & Holiday Manager Tests ---
    def test_rollover_window_detection(self):
        mgr = HolidayManager(HolidaySettings(ROLLOVER_START_GMT="21:50", ROLLOVER_END_GMT="22:20"))

        # 21:55 GMT is INSIDE rollover window -> BLOCKED
        t_rollover = datetime(2026, 9, 25, 21, 55, tzinfo=timezone.utc)
        in_rollover, msg = mgr.is_rollover_window(t_rollover)
        self.assertTrue(in_rollover)
        self.assertIn("daily rollover window", msg)

        # 14:30 GMT is OUTSIDE rollover window -> ALLOWED
        t_normal = datetime(2026, 9, 25, 14, 30, tzinfo=timezone.utc)
        in_norm, _ = mgr.is_rollover_window(t_normal)
        self.assertFalse(in_norm)

    def test_bank_holiday_detection(self):
        mgr = HolidayManager()
        # Christmas Day
        xmas = datetime(2026, 12, 25, 10, 0, tzinfo=timezone.utc)
        is_xmas, msg_xmas = mgr.is_bank_holiday(xmas)
        self.assertTrue(is_xmas)
        self.assertIn("Christmas Day", msg_xmas)

        # US Independence Day
        july4 = datetime(2026, 7, 4, 10, 0, tzinfo=timezone.utc)
        is_july4, msg_july4 = mgr.is_bank_holiday(july4)
        self.assertTrue(is_july4)
        self.assertIn("US Independence Day", msg_july4)

        # Normal trading day
        normal_day = datetime(2026, 9, 23, 10, 0, tzinfo=timezone.utc)
        is_normal, _ = mgr.is_bank_holiday(normal_day)
        self.assertFalse(is_normal)

    def test_spread_gate(self):
        mgr = HolidayManager(HolidaySettings(MAX_ALLOWED_SPREAD_USD=0.40))
        # Normal spread ($0.25) -> APPROVED
        ok_spread, _ = mgr.verify_spread(0.25)
        self.assertTrue(ok_spread)

        # Blowout spread ($0.65) -> BLOCKED
        bad_spread, msg = mgr.verify_spread(0.65)
        self.assertFalse(bad_spread)
        self.assertIn("exceeds cap of $0.40", msg)

    # --- 5. Windows Auto-Recovery Launcher Script Integrity ---
    def test_launcher_script_exists(self):
        bat_path = "start_live_system.bat"
        self.assertTrue(os.path.exists(bat_path))
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("terminal64.exe", content)
        self.assertIn("licensing/server.py", content)
        self.assertIn("telemetry/watchdog.py", content)
        self.assertIn("bot_supervisor_loop", content)


if __name__ == "__main__":
    unittest.main()
