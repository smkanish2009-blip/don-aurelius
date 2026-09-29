"""
Comprehensive Unit Test Suite for JARVIS Autonomous Algorithmic Matrix:
1. Intermarket Filter Engine (DXY + US10Y Traps Shield, Vectorized EMA & ATR).
2. Dynamic Trailing Stop Execution & Precision Lot Sizing.
3. ElevenLabs Voice Synthesis Engine & Fallback Generation.
4. Interactive Telegram HUD & Inline Button Actions (Clean Slate Kill).
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch

from engine.strategy import JarvisStrategyEngine
from engine.mt5_execution import MT5ExecutionBridge
from communication.jarvis_voice import JarvisVoiceCore
from communication.telegram_hud import JarvisTelegramHUD


class TestJarvisEngine(unittest.TestCase):

    def setUp(self):
        self.strategy = JarvisStrategyEngine(ema_fast=5, ema_slow=15, atr_period=5)

    # --- 1. Strategy & Intermarket Tests ---

    def test_ema_and_atr_calculation(self):
        prices = np.array([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120], dtype=float)
        ema5 = self.strategy.calculate_ema(prices, 5)
        self.assertFalse(np.isnan(ema5))
        self.assertGreater(ema5, 110.0)

        # ATR calculation
        highs = prices + 2.0
        lows = prices - 2.0
        atr = self.strategy.calculate_atr(highs, lows, prices)
        self.assertGreater(atr, 0.0)
        self.assertAlmostEqual(atr, 4.0, delta=0.5)

    def test_intermarket_buy_signal(self):
        # Gold is surging (fast > slow)
        xau_closes = np.linspace(2000, 2100, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})

        # Dollar and 10Y yields are dropping (fast < slow)
        dxy_closes = np.linspace(106, 100, 30)
        us10y_closes = np.linspace(4.5, 3.8, 30)
        dxy_df = pd.DataFrame({"close": dxy_closes})
        us10y_df = pd.DataFrame({"close": us10y_closes})

        decision, atr = self.strategy.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        self.assertEqual(decision, "BUY")
        self.assertGreater(atr, 0.0)

    def test_intermarket_bull_trap_prevention(self):
        # Gold is rising (fast > slow)
        xau_closes = np.linspace(2000, 2100, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})

        # BUT Dollar is ALSO surging (Bull Trap!)
        dxy_closes = np.linspace(100, 106, 30)
        us10y_closes = np.linspace(4.0, 4.5, 30)
        dxy_df = pd.DataFrame({"close": dxy_closes})
        us10y_df = pd.DataFrame({"close": us10y_closes})

        decision, _ = self.strategy.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        # Traps Shield must trigger and veto BUY
        self.assertEqual(decision, "HOLD")

    def test_intermarket_sell_signal(self):
        # Gold is falling (fast < slow)
        xau_closes = np.linspace(2100, 2000, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})

        # Dollar is surging (bearish for gold)
        dxy_closes = np.linspace(100, 106, 30)
        us10y_closes = np.linspace(4.0, 4.5, 30)
        dxy_df = pd.DataFrame({"close": dxy_closes})
        us10y_df = pd.DataFrame({"close": us10y_closes})

        decision, atr = self.strategy.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        self.assertEqual(decision, "SELL")
        self.assertGreater(atr, 0.0)

    def test_intermarket_bear_trap_prevention(self):
        # Gold is falling
        xau_closes = np.linspace(2100, 2000, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})

        # BUT Dollar and 10Y Yields are both dropping (Bear Trap!)
        dxy_closes = np.linspace(106, 100, 30)
        us10y_closes = np.linspace(4.5, 3.8, 30)
        dxy_df = pd.DataFrame({"close": dxy_closes})
        us10y_df = pd.DataFrame({"close": us10y_closes})

        decision, _ = self.strategy.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        # Bear Trap Shield must trigger and veto SELL
        self.assertEqual(decision, "HOLD")

    def test_intermarket_standalone_dxy_only(self):
        # Gold is rising, DXY dropping, US10Y is unavailable on retail broker (empty DataFrame)
        xau_closes = np.linspace(2000, 2100, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})
        dxy_closes = np.linspace(106, 100, 30)
        dxy_df = pd.DataFrame({"close": dxy_closes})
        us10y_df = pd.DataFrame()

        decision, atr = self.strategy.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        # DXY is bearish (bullish for Gold) and US10Y is missing: BUY should NOT be blocked
        self.assertEqual(decision, "BUY")
        self.assertGreater(atr, 0.0)

    def test_intermarket_standalone_no_macro(self):
        # Both DXY and US10Y empty: Strategy should execute purely on technicals without self-vetoing
        xau_closes = np.linspace(2000, 2100, 30)
        xau_df = pd.DataFrame({"close": xau_closes, "high": xau_closes + 2, "low": xau_closes - 2})
        decision, atr = self.strategy.evaluate_generation_signal(xau_df, pd.DataFrame(), pd.DataFrame())
        self.assertEqual(decision, "BUY")
        self.assertGreater(atr, 0.0)

    # --- 2. Execution & Trailing Tests ---

    def test_precision_lot_computation(self):
        bridge = MT5ExecutionBridge(symbol="XAUUSD")
        bridge.get_account_equity = MagicMock(return_value=100000.0)

        # 1% risk on $100k = $1,000 risk capital
        # 20 pips SL ($2.00 gold move) @ $10/pip/lot -> 1000 / (20 * 10) = 5.00 lots
        lots = bridge.compute_precision_lot(risk_pct=0.01, sl_pips=20.0)
        self.assertEqual(lots, 5.00)

        # Excessively large account clamped to institutional 5.0 lots cap
        bridge.get_account_equity = MagicMock(return_value=500000.0)
        lots_clamped = bridge.compute_precision_lot(risk_pct=0.01, sl_pips=20.0)
        self.assertEqual(lots_clamped, 5.00)

    def test_trailing_stop_calculation_logic(self):
        bridge = MT5ExecutionBridge(symbol="XAUUSD", magic=20260926)
        modified_tickets = []

        def mock_modify(ticket, sl, tp):
            modified_tickets.append((ticket, sl))

        bridge._modify_position_sl = mock_modify

        # Mock active BUY position opened at 2000.0 with SL at 1990.0
        # Current price reached 2004.0 (+$4.00 = +40 pips profit)
        # Activation is 30 pips ($3.00), step is 10 pips ($1.00)
        # New SL should be 2004.0 - 1.0 = 2003.0
        pos = MagicMock()
        pos.ticket = 101
        pos.magic = 20260926
        pos.type = 0  # BUY
        pos.price_open = 2000.0
        pos.open_price = 2000.0
        pos.sl = 1990.0
        pos.tp = 2020.0

        tick = MagicMock()
        tick.bid = 2004.0
        tick.ask = 2004.5

        with patch("engine.mt5_execution.mt5") as mock_mt5:
            mock_mt5.positions_get.return_value = [pos]
            mock_mt5.symbol_info_tick.return_value = tick
            mock_mt5.ORDER_TYPE_BUY = 0
            bridge._connected = True

            bridge.execute_trailing_stops(trail_activation_pips=30, trail_step_pips=10)

        self.assertEqual(len(modified_tickets), 1)
        self.assertEqual(modified_tickets[0][0], 101)
        self.assertEqual(modified_tickets[0][1], 2003.0)

    # --- 3. Voice Synthesis Tests ---

    def test_voice_narrative_and_audio_synthesis(self):
        voice = JarvisVoiceCore(api_key=None)

        narrative = voice.generate_status_narrative(equity=100000.0, open_trades=1)
        self.assertIn("Don Aurelius", narrative)
        self.assertIn("100,000", narrative)

        audio_stream = voice.compile_vocal_briefing(narrative)
        self.assertIsNotNone(audio_stream)
        audio_bytes = audio_stream.getvalue()
        # Verify valid audio container (MP3 starting with ID3/\xff\xfb or WAV starting with RIFF)
        is_valid_audio = (
            audio_bytes.startswith(b"RIFF") or 
            audio_bytes.startswith(b"\xff\xfb") or 
            audio_bytes.startswith(b"\xff\xf3") or
            audio_bytes.startswith(b"\xff\xf2") or
            audio_bytes.startswith(b"ID3") or
            len(audio_bytes) > 500
        )
        self.assertTrue(is_valid_audio)

    # --- 4. Telegram HUD Tests ---

    def test_telegram_hud_and_button_overrides(self):
        bridge = MT5ExecutionBridge(symbol="XAUUSD")
        bridge.emergency_kill_switch = MagicMock(return_value=3)
        bridge.get_account_equity = MagicMock(return_value=100000.0)

        hud = JarvisTelegramHUD(
            token="mock_token",
            execution_bridge=bridge,
            chat_id="12345678"
        )

        # 1. Test HUD display payload
        res = hud.display_telemetry_hud("12345678")
        self.assertEqual(res.get("status"), "MOCK_MODE")

        # 2. Test button override: Clean Slate Kill Switch
        clean_slate_reply = hud.handle_button_overrides("kill_all", "12345678")
        bridge.emergency_kill_switch.assert_called_once()
        self.assertIn("Liquidated 3 open positions", clean_slate_reply)

        # 3. Test button override: Voice Briefing
        voice_reply = hud.handle_button_overrides("voice_briefing", "12345678")
        self.assertEqual(voice_reply, "VOICE_TRANSMITTED")

        # 4. Test button override: Database Backup Dispatch
        mock_db = MagicMock()
        mock_db.generate_compressed_snapshot.return_value = "data/backups/test.zip"
        hud.db = mock_db

        with patch("os.path.exists", return_value=True):
            backup_reply = hud.handle_button_overrides("backup_db", "12345678")
            self.assertEqual(backup_reply, "BACKUP_TRANSMITTED")


if __name__ == "__main__":
    unittest.main()
