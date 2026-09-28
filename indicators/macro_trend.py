"""
Higher-Timeframe (H4 / Daily) Macro Trend Bias Filter.
Prevents fighting institutional runaway trends on Gold.
Enforces:
1. Setup A (Breakouts) must strictly align with H4 50/200 EMA trend slope.
2. Setup B (Liquidity Sweep Reversals) counter-trend sweeps require high rejection conviction (>= 60% wick).
"""

import logging
from enum import Enum
from typing import Tuple, Optional
import pandas as pd
from indicators.technicals import compute_ema
from config.settings import MacroTrendSettings

logger = logging.getLogger("MacroTrend")


class MacroTrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class MacroTrendFilter:
    def __init__(self, settings: Optional[MacroTrendSettings] = None):
        self.settings = settings or MacroTrendSettings()

    def get_macro_trend(self, df_h4: pd.DataFrame) -> Tuple[MacroTrendDirection, float, float]:
        """
        Calculates H4 50 EMA and 200 EMA to determine institutional trend direction.
        Returns: (MacroTrendDirection, ema_fast, ema_slow)
        """
        if df_h4 is None or len(df_h4) < self.settings.H4_EMA_SLOW:
            return MacroTrendDirection.NEUTRAL, 0.0, 0.0

        ema_50_series = compute_ema(df_h4["close"], self.settings.H4_EMA_FAST)
        ema_200_series = compute_ema(df_h4["close"], self.settings.H4_EMA_SLOW)

        latest_close = float(df_h4["close"].iloc[-1])
        ema_50 = float(ema_50_series.iloc[-1])
        ema_200 = float(ema_200_series.iloc[-1])

        # Strong Bullish Trend
        if latest_close > ema_50 and ema_50 > ema_200:
            return MacroTrendDirection.BULLISH, ema_50, ema_200

        # Strong Bearish Trend
        elif latest_close < ema_50 and ema_50 < ema_200:
            return MacroTrendDirection.BEARISH, ema_50, ema_200

        # Neutral / Consolidating
        return MacroTrendDirection.NEUTRAL, ema_50, ema_200

    def validate_setup_a(self, signal_direction: str, df_h4: pd.DataFrame) -> Tuple[bool, str]:
        """
        Setup A (Breakout) Policy:
        Never chase a breakout against the dominant higher-timeframe trend.
        - Buy Breakout: Allowed if H4 is BULLISH or NEUTRAL. Blocked if BEARISH.
        - Sell Breakout: Allowed if H4 is BEARISH or NEUTRAL. Blocked if BULLISH.
        """
        if not self.settings.ENABLED:
            return True, "Macro trend filter disabled."

        macro_dir, ema_50, ema_200 = self.get_macro_trend(df_h4)

        if signal_direction == "BUY" and macro_dir == MacroTrendDirection.BEARISH:
            msg = f"[MACRO-TREND-VETO] Setup A Buy Breakout blocked: H4 trend is BEARISH (Close < EMA50=${ema_50:.2f} < EMA200=${ema_200:.2f})."
            logger.warning(msg)
            return False, msg

        elif signal_direction == "SELL" and macro_dir == MacroTrendDirection.BULLISH:
            msg = f"[MACRO-TREND-VETO] Setup A Sell Breakout blocked: H4 trend is BULLISH (Close > EMA50=${ema_50:.2f} > EMA200=${ema_200:.2f})."
            logger.warning(msg)
            return False, msg

        return True, f"Setup A aligned with H4 Macro Trend ({macro_dir.value})."

    def validate_setup_b(self, signal_direction: str, rejection_wick_ratio: float,
                         ai_confidence: float, df_h4: pd.DataFrame) -> Tuple[bool, str]:
        """
        Setup B (Liquidity Sweep & Reclaim) Policy:
        Counter-trend mean reversion is permitted only if rejection candle displays high conviction
        (wick >= 60% of candle range) and AI confidence >= 0.65.
        """
        if not self.settings.ENABLED:
            return True, "Macro trend filter disabled."

        macro_dir, _, _ = self.get_macro_trend(df_h4)

        is_counter_trend = (
            (signal_direction == "BUY" and macro_dir == MacroTrendDirection.BEARISH) or
            (signal_direction == "SELL" and macro_dir == MacroTrendDirection.BULLISH)
        )

        if is_counter_trend:
            min_wick = self.settings.COUNTER_TREND_SWEEP_MIN_WICK_PCT
            if rejection_wick_ratio < min_wick or ai_confidence < 0.65:
                msg = (f"[MACRO-TREND-VETO] Counter-trend Setup B {signal_direction} sweep rejected: "
                       f"Rejection wick ({rejection_wick_ratio*100:.1f}%) < {min_wick*100:.0f}% or AI ({ai_confidence*100:.1f}%) < 65.0%.")
                logger.warning(msg)
                return False, msg

        return True, f"Setup B approved under H4 Macro Trend ({macro_dir.value})."
