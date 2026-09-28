"""
Unsupervised Market Regime Classifier.
Identifies whether the market is in Compression, Trend Expansion, Choppy/Sweep, or News Chaos.
"""

from enum import Enum
import pandas as pd
from typing import Tuple


class MarketRegime(Enum):
    COMPRESSION = "COMPRESSION"          # Asian range buildup
    CLEAN_EXPANSION = "CLEAN_EXPANSION"  # Ideal for Setup A breakouts
    CHOP_SWEEP = "CHOP_SWEEP"            # Ideal for Setup B stop-hunts
    NEWS_CHAOS = "NEWS_CHAOS"            # Prohibited trading zone


class RegimeDetector:
    @staticmethod
    def detect_regime(df_h1: pd.DataFrame, range_x_atr: float, adx: float, spread_usd: float) -> MarketRegime:
        if spread_usd > 0.50:
            return MarketRegime.NEWS_CHAOS

        if range_x_atr < 0.8:
            return MarketRegime.COMPRESSION
        elif range_x_atr > 3.0 or adx < 18.0:
            return MarketRegime.CHOP_SWEEP
        elif adx >= 22.0:
            return MarketRegime.CLEAN_EXPANSION

        return MarketRegime.CHOP_SWEEP
