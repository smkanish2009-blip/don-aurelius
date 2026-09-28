"""
Unit Test Suite for TITAN-X:
- Agent PREDATOR (Fair Value Gaps & Institutional Liquidity Sweeps)
- Agent INQUISITOR (Red-Team Adversarial Stress Tester)
- TitanWarRoom (3/4 Supermajority Consensus Council & Fractional Kelly Sizing)
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone

from intelligence import (
    AgentPredator,
    AgentInquisitor,
    EconomicCalendarShield,
    TitanWarRoom,
    ConsensusVerdict,
)
from engine.strategy import JarvisStrategyEngine
from intelligence.agent_radar import AgentRadar


class TestTitanWarRoom(unittest.TestCase):

    def setUp(self):
        # Create deterministic synthetic M15 gold bars (50 bars)
        dates = pd.date_range("2026-09-25 00:00", periods=50, freq="15min")
        base_price = 2650.0

        # Realistic healthy bullish trend with natural oscillations & healthy ATR
        prices = [base_price + (i * 0.15) + (0.50 if i % 2 == 0 else -0.50) for i in range(50)]
        self.df_bullish = pd.DataFrame({
            "time": dates,
            "open": [p - 0.40 for p in prices],
            "high": [p + 1.20 for p in prices],
            "low": [p - 1.20 for p in prices],
            "close": prices,
        })

        # Realistic healthy bearish trend with natural oscillations
        down_prices = [base_price - (i * 0.15) - (0.50 if i % 2 == 0 else -0.50) for i in range(50)]
        self.df_bearish = pd.DataFrame({
            "time": dates,
            "open": [p + 0.40 for p in down_prices],
            "high": [p + 1.20 for p in down_prices],
            "low": [p - 1.20 for p in down_prices],
            "close": down_prices,
        })

    # =========================================================================
    # PART 1: AGENT PREDATOR TESTS
    # =========================================================================

    def test_predator_detects_bullish_fair_value_gap(self):
        predator = AgentPredator(fvg_min_size_pips=5.0)  # 5 pips = $0.50
        df = self.df_bullish.copy()

        # Inject Unmitigated Bullish FVG at bars 46-48:
        # Bar 46 High = 2652.0
        # Bar 47 Impulse = Open 2653.0, Close 2658.0
        # Bar 48 Low = 2655.0 (> Bar 46 High by $3.00 = 30 pips)
        # Bar 49 Low = 2656.0 (Remains above Bar 46 High, unmitigated)
        df.loc[46, "high"] = 2652.0
        df.loc[47, "open"] = 2653.0
        df.loc[47, "close"] = 2658.0
        df.loc[48, "low"] = 2655.0
        df.loc[48, "close"] = 2657.0
        df.loc[49, "low"] = 2656.0
        df.loc[49, "close"] = 2657.5

        gaps = predator.detect_fair_value_gaps(df)
        bullish_gaps = [g for g in gaps if g["type"] == "BULLISH_FVG"]
        self.assertGreater(len(bullish_gaps), 0)
        self.assertAlmostEqual(bullish_gaps[0]["bottom"], 2652.0)
        self.assertAlmostEqual(bullish_gaps[0]["top"], 2655.0)
        self.assertEqual(bullish_gaps[0]["size_pips"], 30.0)

    def test_predator_detects_liquidity_sweep(self):
        predator = AgentPredator()

        # Create structured ranging price series
        dates = pd.date_range("2026-09-25 00:00", periods=50, freq="15min")
        df_sweep = pd.DataFrame({
            "time": dates,
            "open": [2650.0] * 50,
            "high": [2655.0] * 50,
            "low": [2648.0] * 50,
            "close": [2651.0] * 50,
        })

        # Bar 48 is neutral within range
        df_sweep.loc[48, "open"] = 2650.0
        df_sweep.loc[48, "high"] = 2652.0
        df_sweep.loc[48, "low"] = 2649.0
        df_sweep.loc[48, "close"] = 2650.5

        # Bar 49 sweeps sell-side liquidity below 2648.0 to 2645.0, then aggressively closes at 2651.0
        df_sweep.loc[49, "open"] = 2650.0
        df_sweep.loc[49, "high"] = 2651.5
        df_sweep.loc[49, "low"] = 2645.0  # Sweeps 30 pips below 2648.0
        df_sweep.loc[49, "close"] = 2651.0 # Closes safely above swing low

        sweep = predator.detect_liquidity_sweep(df_sweep, swing_lookback=15)
        self.assertTrue(sweep["sweep_detected"])
        self.assertEqual(sweep["direction"], "BULLISH_SWEEP_REVERSAL")
        self.assertAlmostEqual(sweep["swept_level"], 2648.0)
        self.assertGreater(sweep["confidence"], 0.70)

    # =========================================================================
    # PART 2: AGENT INQUISITOR TESTS
    # =========================================================================

    def test_inquisitor_hard_veto_on_spread_expansion(self):
        calendar = EconomicCalendarShield()
        inquisitor = AgentInquisitor(max_spread_pips=3.0, calendar_shield=calendar)

        verdict = inquisitor.stress_test_proposal(
            df=self.df_bullish,
            proposed_direction="BUY",
            entry_price=float(self.df_bullish["close"].iloc[-1]),
            sl_pips=25.0,
            tp_pips=75.0,
            current_spread_pips=4.5  # Blowout spread
        )
        self.assertTrue(verdict.hard_veto)
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Spread blowout" in r for r in verdict.veto_reasons))

    def test_inquisitor_hard_veto_on_economic_embargo(self):
        calendar = EconomicCalendarShield()
        now = datetime.now(timezone.utc)
        # 5 minutes before FOMC
        calendar.register_event("FOMC Rate Decision", now + timedelta(minutes=5), impact="HIGH")

        inquisitor = AgentInquisitor(calendar_shield=calendar)
        verdict = inquisitor.stress_test_proposal(
            df=self.df_bullish,
            proposed_direction="BUY",
            entry_price=float(self.df_bullish["close"].iloc[-1]),
            sl_pips=25.0,
            tp_pips=75.0,
            current_spread_pips=1.8
        )
        self.assertTrue(verdict.hard_veto)
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Economic Event Embargo" in r for r in verdict.veto_reasons))

    def test_inquisitor_hard_veto_on_poor_risk_reward(self):
        calendar = EconomicCalendarShield()
        inquisitor = AgentInquisitor(min_rr_ratio=1.5, calendar_shield=calendar)

        # TP 20 pips, SL 30 pips -> R:R = 0.67:1 (terrible)
        verdict = inquisitor.stress_test_proposal(
            df=self.df_bullish,
            proposed_direction="BUY",
            entry_price=float(self.df_bullish["close"].iloc[-1]),
            sl_pips=30.0,
            tp_pips=20.0,
            current_spread_pips=1.8
        )
        self.assertTrue(verdict.hard_veto)
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Unfavorable Risk/Reward" in r for r in verdict.veto_reasons))

    def test_inquisitor_approves_pristine_trade(self):
        calendar = EconomicCalendarShield()
        inquisitor = AgentInquisitor(calendar_shield=calendar)

        verdict = inquisitor.stress_test_proposal(
            df=self.df_bullish,
            proposed_direction="BUY",
            entry_price=float(self.df_bullish["close"].iloc[-1]),
            sl_pips=25.0,
            tp_pips=75.0,
            current_spread_pips=1.8
        )
        self.assertFalse(verdict.hard_veto)
        self.assertTrue(verdict.approved)
        self.assertLess(verdict.risk_score, 0.40)

    # =========================================================================
    # PART 3: TITAN WAR ROOM CONSENSUS & KELLY SIZING TESTS
    # =========================================================================

    def test_war_room_supermajority_4_of_4_buy_consensus(self):
        radar = AgentRadar(cache_ttl_seconds=0)
        inquisitor = AgentInquisitor()
        predator = AgentPredator()
        hawk = JarvisStrategyEngine()

        war_room = TitanWarRoom(
            hawk=hawk,
            radar=radar,
            predator=predator,
            inquisitor=inquisitor,
            base_risk_pct=0.01
        )

        # Feed bullish news
        bullish_news = [
            "Fed signals aggressive rate cuts ahead as inflation cools rapidly",
            "Central banks accelerate massive physical gold accumulation"
        ]

        verdict = war_room.convene_council(
            xau_df=self.df_bullish,
            simulated_headlines=bullish_news,
            current_spread_pips=1.8
        )

        self.assertTrue(verdict.consensus_achieved)
        self.assertEqual(verdict.final_decision, "BUY")
        self.assertGreaterEqual(verdict.supermajority_count, 3)
        self.assertFalse(verdict.veto_triggered)
        # Kelly sizing verification
        self.assertGreater(verdict.kelly_fraction, 0.0)
        self.assertGreaterEqual(verdict.recommended_risk_pct, 0.005)
        self.assertLessEqual(verdict.recommended_risk_pct, 0.015)

    def test_war_room_inquisitor_veto_overrules_supermajority(self):
        # Create an inquisitor with active news embargo
        calendar = EconomicCalendarShield()
        now = datetime.now(timezone.utc)
        calendar.register_event("CPI Inflation Report", now + timedelta(minutes=4), impact="HIGH")
        inquisitor = AgentInquisitor(calendar_shield=calendar)

        war_room = TitanWarRoom(inquisitor=inquisitor)

        bullish_news = [
            "Fed delivers unexpected rate cut as gold surges to record highs"
        ]

        verdict = war_room.convene_council(
            xau_df=self.df_bullish,
            simulated_headlines=bullish_news,
            current_spread_pips=1.8
        )

        # Must be VETOED by Inquisitor despite bullish news and trend
        self.assertFalse(verdict.consensus_achieved)
        self.assertEqual(verdict.final_decision, "HOLD")
        self.assertTrue(verdict.veto_triggered)
        self.assertEqual(verdict.recommended_risk_pct, 0.0)
        self.assertIn("TRADE VETOED BY INQUISITOR", verdict.rationale)

    def test_war_room_insufficient_consensus_defaults_to_hold(self):
        radar = AgentRadar(cache_ttl_seconds=0)
        war_room = TitanWarRoom(radar=radar)

        # Provide conflicting bearish news while price is bullish
        bearish_news = [
            "US Dollar jumps to multi-month high on surging Treasury yields",
            "Fed officials push back against interest rate cut expectations"
        ]

        # Use flat range data
        flat_prices = [2650.0 + ((-1)**i * 0.10) for i in range(50)]
        df_flat = pd.DataFrame({
            "time": pd.date_range("2026-09-25 00:00", periods=50, freq="15min"),
            "open": flat_prices,
            "high": [p + 0.30 for p in flat_prices],
            "low": [p - 0.30 for p in flat_prices],
            "close": flat_prices,
        })

        verdict = war_room.convene_council(
            xau_df=df_flat,
            simulated_headlines=bearish_news,
            current_spread_pips=1.8
        )

        self.assertFalse(verdict.consensus_achieved)
        self.assertEqual(verdict.final_decision, "HOLD")
        self.assertLess(verdict.supermajority_count, 3)


if __name__ == "__main__":
    unittest.main()
