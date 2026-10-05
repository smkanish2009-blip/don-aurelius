"""
Unit Test Suite for TITAN-X Agent RADAR & Economic Calendar Shield.
Verifies real-time sentiment scoring, velocity delta, shock detection, and news embargoes.
"""

import os
import sys

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

import unittest
import time
from datetime import datetime, timedelta, timezone

from intelligence.agent_radar import AgentRadar, SentimentSnapshot
from intelligence.economic_calendar import EconomicCalendarShield


class TestAgentRadar(unittest.TestCase):

    def setUp(self):
        self.radar = AgentRadar(cache_ttl_seconds=0)
        self.calendar = EconomicCalendarShield(pre_embargo_minutes=15, post_embargo_minutes=15)

    # --- 1. Sentiment Scoring & Lexicon Tests ---

    def test_bullish_gold_headline_scoring(self):
        headline = "Fed delivers unexpected 50bps rate cut as safe haven gold demand surges"
        score = self.radar.score_headline(headline)
        self.assertGreater(score, 0.50)

    def test_bearish_gold_headline_scoring(self):
        headline = "Dollar surges and Treasury yields spike after hot CPI report beats expectations"
        score = self.radar.score_headline(headline)
        self.assertLess(score, -0.50)

    def test_negation_inversion(self):
        normal_cut = self.radar.score_headline("Fed plans rate cuts this year")
        negated_cut = self.radar.score_headline("Fed confirms no rate cuts this year")
        self.assertGreater(normal_cut, 0.0)
        self.assertLess(negated_cut, 0.0)

    def test_neutral_headline(self):
        headline = "European markets close quietly ahead of standard weekend routine"
        score = self.radar.score_headline(headline)
        self.assertEqual(score, 0.0)

    # --- 2. Sentiment Velocity & Shock Detection ---

    def test_sentiment_velocity_and_shock_detection(self):
        # Step 1: Initial neutral headlines
        neutral_batch = [
            "Market ranges sideways with low volume",
            "Gold steadies near support level"
        ]
        snap1 = self.radar.poll_and_evaluate(simulated_headlines=neutral_batch)
        self.assertEqual(snap1.gold_bias, "NEUTRAL")

        # Step 2: Inject sudden geopolitical crisis shock 10 seconds later
        crisis_batch = [
            "Massive geopolitical conflict escalation: Missile strike triggers emergency safe haven gold rush",
            "Dollar tumbles as central banks rush into physical gold reserves"
        ]
        # Simulate time shift
        self.radar._history.append((time.time() - 300, 0.0))  # 5 mins ago score was 0.0
        snap2 = self.radar.poll_and_evaluate(simulated_headlines=crisis_batch)

        self.assertEqual(snap2.gold_bias, "BULLISH")
        self.assertTrue(snap2.shock_event)
        self.assertGreater(snap2.raw_score, 0.5)

    def test_radar_telemetry_payload(self):
        telemetry = self.radar.get_radar_telemetry()
        self.assertIn("sentiment_score", telemetry)
        self.assertIn("sentiment_velocity", telemetry)
        self.assertIn("gold_bias", telemetry)
        self.assertIn("shock_event", telemetry)

    # --- 3. Economic Calendar Proximity Tests ---

    def test_economic_calendar_embargo_active_pre_release(self):
        now = datetime.now(timezone.utc)
        # Event scheduled in 8 minutes (within 15m pre-embargo)
        fomc_time = now + timedelta(minutes=8)
        self.calendar.register_event("FOMC Interest Rate Decision", fomc_time, impact="HIGH")

        is_embargo, reason = self.calendar.is_embargo_active(current_dt=now)
        self.assertTrue(is_embargo)
        self.assertIn("releases in 8m", reason)

    def test_economic_calendar_embargo_active_post_release(self):
        now = datetime.now(timezone.utc)
        # Event occurred 5 minutes ago (within 15m post-embargo)
        nfp_time = now - timedelta(minutes=5)
        self.calendar.register_event("US Non-Farm Payrolls", nfp_time, impact="HIGH")

        is_embargo, reason = self.calendar.is_embargo_active(current_dt=now)
        self.assertTrue(is_embargo)
        self.assertIn("released 5m ago", reason)

    def test_economic_calendar_embargo_inactive_safe_window(self):
        now = datetime.now(timezone.utc)
        # Event is 2 hours away (safe)
        future_time = now + timedelta(hours=2)
        self.calendar.register_event("ECB Monetary Policy Statement", future_time, impact="HIGH")

        is_embargo, reason = self.calendar.is_embargo_active(current_dt=now)
        self.assertFalse(is_embargo)
        self.assertIn("CLEAR", reason)


if __name__ == "__main__":
    unittest.main()
