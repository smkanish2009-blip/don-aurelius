"""
Setup A: Confirmed Breakout Strategy.
Trades confirmed expansion outside Asian range aligned with H1 EMA200 trend and ADX strength.
"""

import logging
from typing import Optional
import pandas as pd
from config.settings import StrategyParameters
from strategy.models import TradeSignal, SignalDirection, SetupType
from indicators.technicals import compute_ema, compute_adx, compute_atr

logger = logging.getLogger("SetupA")


class SetupABreakout:
    def __init__(self, params: StrategyParameters):
        self.params = params

    def evaluate_h1_bias(self, df_h1: pd.DataFrame) -> Tuple[Optional[SignalDirection], bool]:
        """
        Determines H1 directional bias:
        Bull: close > EMA200, EMA200 rising over EMA_Slope_Bars, ADX(14) >= ADX_Min.
        Bear: close < EMA200, EMA200 falling over EMA_Slope_Bars, ADX(14) >= ADX_Min.
        """
        if len(df_h1) < self.params.TREND_EMA_PERIOD + 10:
            return None, False

        df = df_h1.copy()
        df["ema200"] = compute_ema(df["close"], self.params.TREND_EMA_PERIOD)
        adx_df = compute_adx(df, self.params.ADX_PERIOD)
        df["adx"] = adx_df["adx"]

        # Use index -2 for last closed bar
        last_closed = df.iloc[-2]
        prev_slope_bar = df.iloc[-2 - self.params.EMA_SLOPE_BARS]

        ema_rising = last_closed["ema200"] > prev_slope_bar["ema200"]
        ema_falling = last_closed["ema200"] < prev_slope_bar["ema200"]
        adx_strong = last_closed["adx"] >= self.params.ADX_MIN

        if last_closed["close"] > last_closed["ema200"] and ema_rising and adx_strong:
            return SignalDirection.BUY, True
        elif last_closed["close"] < last_closed["ema200"] and ema_falling and adx_strong:
            return SignalDirection.SELL, True

        return None, False

    def evaluate(self, df_m15: pd.DataFrame, df_h1: pd.DataFrame,
                 range_high: float, range_low: float) -> Optional[TradeSignal]:
        """Evaluates Setup A breakout on the most recent closed M15 candle."""
        bias, bias_confirmed = self.evaluate_h1_bias(df_h1)
        if not bias_confirmed:
            return None

        # Calculate M15 and H1 ATR
        atr_m15 = float(compute_atr(df_m15, 14).iloc[-2])
        atr_h1 = float(compute_atr(df_h1, 14).iloc[-2])

        # Last closed M15 bar (index -2)
        bar = df_m15.iloc[-2]
        candle_open = bar["open"]
        candle_high = bar["high"]
        candle_low = bar["low"]
        candle_close = bar["close"]
        candle_range = candle_high - candle_low
        candle_body = abs(candle_close - candle_open)

        # Body must be >= 50% of range
        if candle_range <= 0 or (candle_body / candle_range) < self.params.A_MIN_BODY_RATIO:
            return None

        # LONG SETUP
        if bias == SignalDirection.BUY:
            buffer_req = self.params.A_BREAKOUT_BUFFER_X_ATR * atr_m15
            max_ext_allowed = self.params.A_MAX_EXTENSION_X_ATR * atr_m15

            # 1. Close must be beyond range high + buffer
            if candle_close <= (range_high + buffer_req):
                return None
            # 2. Do not chase if extended
            if candle_close > (range_high + max_ext_allowed):
                return None
            # 3. Close must be in top 30% of candle
            close_percentile = (candle_close - candle_low) / candle_range
            if close_percentile < (1.0 - self.params.A_TOP_CLOSE_PERCENTILE):
                return None

            entry = candle_close
            sl_dist = self.params.A_SL_MULT_ATR * atr_h1
            stop_loss = entry - sl_dist
            # Stop loss not beyond opposite range edge
            if stop_loss < range_low:
                stop_loss = range_low - (0.05 * atr_m15)

            risk_dist = entry - stop_loss
            take_profit = entry + (self.params.A_TP_RR * risk_dist)

            return TradeSignal(
                direction=SignalDirection.BUY,
                setup_type=SetupType.SETUP_A,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_r=self.params.A_TP_RR,
                confidence_score=0.65,
                rationale="Setup A Bullish Breakout: Closed M15 candle outside Asian High with momentum body"
            )

        # SHORT SETUP
        elif bias == SignalDirection.SELL:
            buffer_req = self.params.A_BREAKOUT_BUFFER_X_ATR * atr_m15
            max_ext_allowed = self.params.A_MAX_EXTENSION_X_ATR * atr_m15

            # 1. Close must be below range low - buffer
            if candle_close >= (range_low - buffer_req):
                return None
            # 2. Do not chase if extended
            if candle_close < (range_low - max_ext_allowed):
                return None
            # 3. Close must be in bottom 30% of candle
            close_percentile = (candle_close - candle_low) / candle_range
            if close_percentile > self.params.A_TOP_CLOSE_PERCENTILE:
                return None

            entry = candle_close
            sl_dist = self.params.A_SL_MULT_ATR * atr_h1
            stop_loss = entry + sl_dist
            if stop_loss > range_high:
                stop_loss = range_high + (0.05 * atr_m15)

            risk_dist = stop_loss - entry
            take_profit = entry - (self.params.A_TP_RR * risk_dist)

            return TradeSignal(
                direction=SignalDirection.SELL,
                setup_type=SetupType.SETUP_A,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_r=self.params.A_TP_RR,
                confidence_score=0.65,
                rationale="Setup A Bearish Breakout: Closed M15 candle outside Asian Low with momentum body"
            )

        return None
