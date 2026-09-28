"""
Setup B: Liquidity Sweep & Stop-Hunt Reversal ("Judas Swing").
Captures liquidity grabs beyond the Asian range with an immediate M5 reclaim.
"""

import logging
from typing import Optional
import pandas as pd
from config.settings import StrategyParameters
from strategy.models import TradeSignal, SignalDirection, SetupType
from indicators.technicals import compute_atr

logger = logging.getLogger("SetupB")


class SetupBSweepReclaim:
    def __init__(self, params: StrategyParameters):
        self.params = params

    def evaluate(self, df_m5: pd.DataFrame, df_h1: pd.DataFrame,
                 range_high: float, range_low: float) -> Optional[TradeSignal]:
        """
        Evaluates Setup B on closed M5 bars:
        High Sweep: price traded above range_high, then M5 candle closes back inside range with bearish body.
        Low Sweep: price traded below range_low, then M5 candle closes back inside range with bullish body.
        """
        if len(df_m5) < 5 or len(df_h1) < 15:
            return None

        atr_h1 = float(compute_atr(df_h1, 14).iloc[-2])

        min_sweep = self.params.B_SWEEP_MIN_X_ATR * atr_h1
        max_sweep = self.params.B_SWEEP_MAX_X_ATR * atr_h1

        # Closed bar is index -2
        bar = df_m5.iloc[-2]
        c_open, c_high, c_low, c_close = bar["open"], bar["high"], bar["low"], bar["close"]
        c_range = c_high - c_low
        c_body = abs(c_close - c_open)

        if c_range <= 0 or (c_body / c_range) < self.params.B_REJECTION_BODY_MIN:
            return None

        # 1. Bearish Reclaim (Swept Asian High)
        if c_high > range_high:
            sweep_dist = c_high - range_high
            # Sweep must be within min/max bounds and candle must close BACK INSIDE range
            if min_sweep <= sweep_dist <= max_sweep and c_close < range_high and c_close < c_open:
                entry = c_close
                stop_loss = c_high + (self.params.B_SL_BUFFER_X_ATR * atr_h1)
                risk_dist = stop_loss - entry

                # Target 1: Range midpoint (50%), Target 2: Range Low
                take_profit = range_high - (0.50 * (range_high - range_low))

                return TradeSignal(
                    direction=SignalDirection.SELL,
                    setup_type=SetupType.SETUP_B,
                    entry_price=entry,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_r=risk_dist,
                    confidence_score=0.60,
                    rationale=f"Setup B Bearish Sweep: Asian High swept by {sweep_dist:.2f} and reclaimed with M5 rejection body"
                )

        # 2. Bullish Reclaim (Swept Asian Low)
        if c_low < range_low:
            sweep_dist = range_low - c_low
            # Sweep must be within min/max bounds and candle must close BACK INSIDE range
            if min_sweep <= sweep_dist <= max_sweep and c_close > range_low and c_close > c_open:
                entry = c_close
                stop_loss = c_low - (self.params.B_SL_BUFFER_X_ATR * atr_h1)
                risk_dist = entry - stop_loss

                # Target 1: Range midpoint (50%)
                take_profit = range_low + (0.50 * (range_high - range_low))

                return TradeSignal(
                    direction=SignalDirection.BUY,
                    setup_type=SetupType.SETUP_B,
                    entry_price=entry,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_r=risk_dist,
                    confidence_score=0.60,
                    rationale=f"Setup B Bullish Sweep: Asian Low swept by {sweep_dist:.2f} and reclaimed with M5 rejection body"
                )

        return None
