"""
Unit tests for Autonomous Market Regime Classifier (The "Chameleon" Brain).
"""

import unittest
import numpy as np
import pandas as pd
from strategy.regime_classifier import MarketRegimeClassifier, MarketRegime


class TestMarketRegimeClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = MarketRegimeClassifier(
            trend_adx_threshold=23.0,
            compression_adx_threshold=18.0,
            shock_vol_ratio_threshold=2.1,
            max_allowable_spread=0.65,
        )

    def _generate_synthetic_df(self, n_bars: int, trend_slope: float, vol_scale: float, base_price: float = 2650.0):
        np.random.seed(42)
        close = []
        high = []
        low = []
        open_p = []
        curr = base_price

        for i in range(n_bars):
            step = trend_slope + np.random.normal(0, vol_scale)
            o = curr
            curr += step
            c = curr
            h = max(o, c) + abs(np.random.normal(0, vol_scale * 0.5))
            l = min(o, c) - abs(np.random.normal(0, vol_scale * 0.5))
            open_p.append(o)
            high.append(h)
            low.append(l)
            close.append(c)

        return pd.DataFrame({
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": [1200] * n_bars,
        })

    def _generate_oscillating_df(self, n_bars: int, base_price: float = 2650.0):
        np.random.seed(42)
        close = []
        high = []
        low = []
        open_p = []

        for i in range(n_bars):
            mid = base_price + 1.2 * np.sin(i * 0.4)
            noise = np.random.normal(0, 0.1)
            c = mid + noise
            o = mid - noise
            h = max(o, c) + 0.25
            l = min(o, c) - 0.25
            open_p.append(o)
            high.append(h)
            low.append(l)
            close.append(c)

        return pd.DataFrame({
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": [1200] * n_bars,
        })

    def test_liquidity_void_on_spread_spike(self):
        df_m5 = self._generate_synthetic_df(60, 0.0, 1.0)
        df_m15 = self._generate_synthetic_df(60, 0.0, 1.0)
        df_h1 = self._generate_synthetic_df(60, 0.0, 1.0)

        # Spread spike exceeds limit (e.g. 0.85 > 0.65)
        policy = self.classifier.classify(df_m5, df_m15, df_h1, current_spread=0.85)
        self.assertEqual(policy.regime, MarketRegime.LIQUIDITY_VOID)
        self.assertEqual(policy.risk_multiplier, 0.0)
        self.assertFalse(policy.allow_breakout)
        self.assertFalse(policy.allow_mean_reversion)

    def test_ranging_compression_on_oscillating_market(self):
        # Oscillating range-bound market with low trend
        df_m5 = self._generate_oscillating_df(80)
        df_m15 = self._generate_oscillating_df(80)
        df_h1 = self._generate_oscillating_df(80)

        policy = self.classifier.classify(df_m5, df_m15, df_h1, current_spread=0.18)
        self.assertEqual(policy.regime, MarketRegime.RANGING_COMPRESSION)
        self.assertEqual(policy.directional_bias, "NEUTRAL")
        self.assertTrue(policy.allow_mean_reversion)
        self.assertFalse(policy.allow_breakout)
        self.assertLessEqual(policy.target_rr_ratio, 2.0)

    def test_bullish_expansion(self):
        # Strong upward persistent trend
        df_m5 = self._generate_synthetic_df(80, 2.0, 0.5)
        df_m15 = self._generate_synthetic_df(80, 2.0, 0.5)
        df_h1 = self._generate_synthetic_df(80, 2.0, 0.5)

        policy = self.classifier.classify(df_m5, df_m15, df_h1, current_spread=0.18)
        self.assertEqual(policy.regime, MarketRegime.BULLISH_EXPANSION)
        self.assertEqual(policy.directional_bias, "BULLISH")
        self.assertTrue(policy.allow_breakout)
        self.assertGreaterEqual(policy.risk_multiplier, 1.0)
        self.assertGreaterEqual(policy.target_rr_ratio, 2.5)

    def test_bearish_expansion(self):
        # Strong downward persistent trend
        df_m5 = self._generate_synthetic_df(80, -2.0, 0.5)
        df_m15 = self._generate_synthetic_df(80, -2.0, 0.5)
        df_h1 = self._generate_synthetic_df(80, -2.0, 0.5)

        policy = self.classifier.classify(df_m5, df_m15, df_h1, current_spread=0.18)
        self.assertEqual(policy.regime, MarketRegime.BEARISH_EXPANSION)
        self.assertEqual(policy.directional_bias, "BEARISH")
        self.assertTrue(policy.allow_breakout)
        self.assertGreaterEqual(policy.risk_multiplier, 1.0)

    def test_volatility_shock(self):
        # Build DataFrame with quiet baseline then violent high range bar
        df_m5 = self._generate_synthetic_df(80, 0.0, 0.2)
        df_m15 = self._generate_synthetic_df(80, 0.0, 0.2)
        df_h1 = self._generate_synthetic_df(80, 0.0, 0.2)

        # Inject sudden massive range bars in recent bars
        for idx in range(-5, 0):
            df_m15.loc[df_m15.index[idx], "high"] += 25.0
            df_m15.loc[df_m15.index[idx], "low"] -= 25.0

        policy = self.classifier.classify(df_m5, df_m15, df_h1, current_spread=0.25)
        self.assertEqual(policy.regime, MarketRegime.VOLATILITY_SHOCK)
        self.assertEqual(policy.risk_multiplier, 0.5)  # Defensive risk clamp
        self.assertFalse(policy.allow_breakout)


if __name__ == "__main__":
    unittest.main()
