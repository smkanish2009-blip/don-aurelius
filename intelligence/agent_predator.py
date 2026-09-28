"""
TITAN-X Agent PREDATOR (Institutional Order Flow & Liquidity Predator).
Detects Fair Value Gaps (FVG), Equal Highs/Lows (EQH/EQL) Stop Hunts,
and Institutional Liquidity Sweeps on XAUUSD.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger("TitanX.Predator")


class AgentPredator:
    """
    Agent PREDATOR identifies smart money footprints, institutional liquidity pools,
    and engineered retail stop hunts.
    """

    def __init__(self, fvg_min_size_pips: float = 8.0, lookback_bars: int = 50):
        self.fvg_min_size = fvg_min_size_pips * 0.10  # $1 gold = 10 pips ($0.10/pip)
        self.lookback_bars = lookback_bars

    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detects 3-candle imbalance gaps (FVG) that act as institutional price magnets:
        - Bullish FVG: Low of candle 0 > High of candle 2 (gap between candle 0 low and candle 2 high)
        - Bearish FVG: High of candle 0 < Low of candle 2 (gap between candle 2 low and candle 0 high)
        """
        if len(df) < 5 or 'high' not in df or 'low' not in df:
            return []

        gaps: List[Dict[str, Any]] = []
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        n = len(df)

        # Scan recent bars for unmitigated FVGs
        start_idx = max(2, n - self.lookback_bars)
        for i in range(start_idx, n):
            # 1. Bullish FVG: Bar i (current in 3-bar sequence) Low > Bar i-2 High
            if lows[i] > highs[i - 2]:
                gap_size = lows[i] - highs[i - 2]
                if gap_size >= self.fvg_min_size:
                    # Check if mitigated by any subsequent bar
                    mitigated = False
                    for j in range(i + 1, n):
                        if lows[j] <= highs[i - 2]:
                            mitigated = True
                            break
                    if not mitigated:
                        gaps.append({
                            "type": "BULLISH_FVG",
                            "bar_index": i,
                            "top": round(lows[i], 2),
                            "bottom": round(highs[i - 2], 2),
                            "size_pips": round(gap_size / 0.10, 1),
                            "current_price": round(closes[-1], 2)
                        })

            # 2. Bearish FVG: Bar i High < Bar i-2 Low
            elif highs[i] < lows[i - 2]:
                gap_size = lows[i - 2] - highs[i]
                if gap_size >= self.fvg_min_size:
                    mitigated = False
                    for j in range(i + 1, n):
                        if highs[j] >= lows[i - 2]:
                            mitigated = True
                            break
                    if not mitigated:
                        gaps.append({
                            "type": "BEARISH_FVG",
                            "bar_index": i,
                            "top": round(lows[i - 2], 2),
                            "bottom": round(highs[i], 2),
                            "size_pips": round(gap_size / 0.10, 1),
                            "current_price": round(closes[-1], 2)
                        })

        return gaps

    def detect_liquidity_sweep(self, df: pd.DataFrame, swing_lookback: int = 15) -> Dict[str, Any]:
        """
        Detects Institutional Liquidity Sweeps (Turtle Soup / Stop Hunts):
        - Bullish Sweep: Price pierces below prior swing low (triggering retail stops),
          then aggressively rejects and closes back ABOVE the swing low.
        - Bearish Sweep: Price pierces above prior swing high, then closes back BELOW it.
        """
        if len(df) < swing_lookback + 2:
            return {"sweep_detected": False, "direction": "NONE", "confidence": 0.0}

        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        opens = df['open'].values

        # Prior swing levels (excluding current 2 candles)
        prior_highs = highs[-(swing_lookback + 2):-2]
        prior_lows = lows[-(swing_lookback + 2):-2]

        swing_high = float(np.max(prior_highs))
        swing_low = float(np.min(prior_lows))

        # Check last closed candle (index -2) and current candle (index -1)
        for check_idx in [-2, -1]:
            c_high = highs[check_idx]
            c_low = lows[check_idx]
            c_close = closes[check_idx]
            c_open = opens[check_idx]

            # 1. Bullish Liquidity Sweep (Swept sell-side liquidity below swing low)
            if c_low < swing_low and c_close > swing_low:
                wick_size = c_close - c_low
                body_size = abs(c_close - c_open)
                # Rejection wick must be prominent
                if wick_size >= 1.5 * max(0.2, body_size):
                    return {
                        "sweep_detected": True,
                        "direction": "BULLISH_SWEEP_REVERSAL",
                        "swept_level": round(swing_low, 2),
                        "sweep_low": round(c_low, 2),
                        "rejection_pips": round(wick_size / 0.10, 1),
                        "confidence": 0.85
                    }

            # 2. Bearish Liquidity Sweep (Swept buy-side liquidity above swing high)
            if c_high > swing_high and c_close < swing_high:
                wick_size = c_high - c_close
                body_size = abs(c_close - c_open)
                if wick_size >= 1.5 * max(0.2, body_size):
                    return {
                        "sweep_detected": True,
                        "direction": "BEARISH_SWEEP_REVERSAL",
                        "swept_level": round(swing_high, 2),
                        "sweep_high": round(c_high, 2),
                        "rejection_pips": round(wick_size / 0.10, 1),
                        "confidence": 0.85
                    }

        return {"sweep_detected": False, "direction": "NONE", "confidence": 0.0}

    def evaluate_order_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Synthesizes complete institutional order flow telemetry."""
        gaps = self.detect_fair_value_gaps(df)
        sweep = self.detect_liquidity_sweep(df)

        bullish_fvg_count = sum(1 for g in gaps if g["type"] == "BULLISH_FVG")
        bearish_fvg_count = sum(1 for g in gaps if g["type"] == "BEARISH_FVG")

        bias = "NEUTRAL"
        confidence = 0.50

        if sweep["sweep_detected"]:
            if sweep["direction"] == "BULLISH_SWEEP_REVERSAL":
                bias = "BULLISH"
                confidence = sweep["confidence"]
            elif sweep["direction"] == "BEARISH_SWEEP_REVERSAL":
                bias = "BEARISH"
                confidence = sweep["confidence"]
        elif bullish_fvg_count > bearish_fvg_count:
            bias = "BULLISH"
            confidence = 0.65
        elif bearish_fvg_count > bullish_fvg_count:
            bias = "BEARISH"
            confidence = 0.65

        return {
            "bias": bias,
            "confidence": confidence,
            "sweep_detected": sweep["sweep_detected"],
            "sweep_details": sweep,
            "active_fvgs_count": len(gaps),
            "bullish_fvgs": bullish_fvg_count,
            "bearish_fvgs": bearish_fvg_count
        }
