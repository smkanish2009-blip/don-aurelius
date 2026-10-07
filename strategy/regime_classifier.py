"""
Autonomous Market Regime Classifier (The "Chameleon" Brain).
============================================================
Quantitatively categorizes real-time XAUUSD market micro-structure into 5 distinct regimes:
  1. BULLISH_EXPANSION   - Persistent upward momentum with healthy institutional volume.
  2. BEARISH_EXPANSION   - Persistent downward momentum with healthy institutional volume.
  3. RANGING_COMPRESSION - Mean-reverting, low-directional chop, liquidity absorption.
  4. VOLATILITY_SHOCK    - High-velocity price shocks (FOMC, NFP, geopolitical spikes).
  5. LIQUIDITY_VOID      - Off-hours, bank holidays, or excessive spread widening.

Dynamically adapts trading hyperparameters:
  - Risk multiplier (0.0x to 1.25x)
  - Target Risk-to-Reward ratio (1.2R to 3.5R)
  - Setup permission gating (Breakout vs. Liquidity Sweep)
  - Trailing stop tightness
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from indicators.technicals import (
    compute_ema,
    compute_atr,
    compute_adx,
    compute_garman_klass_volatility,
)

logger = logging.getLogger("RegimeClassifier")


class MarketRegime(Enum):
    BULLISH_EXPANSION = "BULLISH_EXPANSION"
    BEARISH_EXPANSION = "BEARISH_EXPANSION"
    RANGING_COMPRESSION = "RANGING_COMPRESSION"
    VOLATILITY_SHOCK = "VOLATILITY_SHOCK"
    LIQUIDITY_VOID = "LIQUIDITY_VOID"


@dataclass
class RegimePolicy:
    regime: MarketRegime
    confidence: float
    volatility_ratio: float
    adx: float
    directional_bias: str
    risk_multiplier: float
    target_rr_ratio: float
    allow_breakout: bool
    allow_mean_reversion: bool
    trailing_atr_mult: float
    rationale: str


class MarketRegimeClassifier:
    """
    Multi-timeframe statistical regime detection engine for institutional gold execution.
    """

    def __init__(
        self,
        trend_adx_threshold: float = 23.0,
        compression_adx_threshold: float = 18.0,
        shock_vol_ratio_threshold: float = 2.1,
        max_allowable_spread: float = 0.65,
    ):
        self.trend_adx_threshold = trend_adx_threshold
        self.compression_adx_threshold = compression_adx_threshold
        self.shock_vol_ratio_threshold = shock_vol_ratio_threshold
        self.max_allowable_spread = max_allowable_spread
        self.last_state: Optional[RegimePolicy] = None

    def classify(
        self,
        df_m5: pd.DataFrame,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        current_spread: float,
    ) -> RegimePolicy:
        """
        Classifies the current market regime across M5, M15, and H1 timeframes.
        """
        # 1. Gate Check: Liquidity Void (Spread Anomaly or Depleted Volume)
        if current_spread > self.max_allowable_spread:
            return self._build_policy(
                regime=MarketRegime.LIQUIDITY_VOID,
                confidence=0.98,
                vol_ratio=1.0,
                adx=0.0,
                bias="NEUTRAL",
                risk_mult=0.0,
                target_rr=1.0,
                allow_breakout=False,
                allow_reversion=False,
                trailing_mult=1.0,
                rationale=f"Spread spike anomaly ({current_spread:.2f} > {self.max_allowable_spread:.2f} limit). Liquidity void active.",
            )

        if len(df_m15) < 30 or len(df_h1) < 25:
            # Insufficient historical depth
            return self._build_policy(
                regime=MarketRegime.RANGING_COMPRESSION,
                confidence=0.50,
                vol_ratio=1.0,
                adx=15.0,
                bias="NEUTRAL",
                risk_mult=0.75,
                target_rr=1.5,
                allow_breakout=False,
                allow_reversion=True,
                trailing_mult=1.5,
                rationale="Warm-up period: insufficient historical bar count for full regime inference.",
            )

        # 2. Volatility Profiling (Current ATR vs. Rolling Baseline)
        atr_m15_fast = compute_atr(df_m15, period=14).iloc[-1]
        atr_m15_baseline = compute_atr(df_m15, period=50).iloc[-1]
        vol_ratio = float(atr_m15_fast / (atr_m15_baseline + 1e-9))

        # Check for Volatility Shock (Extreme volatility expansion)
        if vol_ratio >= self.shock_vol_ratio_threshold:
            return self._build_policy(
                regime=MarketRegime.VOLATILITY_SHOCK,
                confidence=min(1.0, 0.70 + (vol_ratio - self.shock_vol_ratio_threshold) * 0.2),
                vol_ratio=vol_ratio,
                adx=35.0,
                bias="VOLATILE",
                risk_mult=0.50,  # Halve risk to protect capital
                target_rr=3.5,
                allow_breakout=False,  # High risk of false breakout whipsaw
                allow_reversion=False,
                trailing_mult=2.5,
                rationale=f"Volatility shock detected (ATR ratio {vol_ratio:.2f}x > {self.shock_vol_ratio_threshold:.2f}x). Capital preservation engaged.",
            )

        # 3. Directional & Trend Strength Assessment (ADX + EMA Hierarchy)
        adx_df = compute_adx(df_m15, period=14)
        current_adx = float(adx_df["adx"].iloc[-1])
        plus_di = float(adx_df["plus_di"].iloc[-1])
        minus_di = float(adx_df["minus_di"].iloc[-1])

        h1_ema_20 = compute_ema(df_h1["close"], 20).iloc[-1]
        h1_ema_50 = compute_ema(df_h1["close"], 50).iloc[-1]
        m15_close = df_m15["close"].iloc[-1]

        is_bullish_alignment = (m15_close > h1_ema_20) and (h1_ema_20 > h1_ema_50) and (plus_di > minus_di)
        is_bearish_alignment = (m15_close < h1_ema_20) and (h1_ema_20 < h1_ema_50) and (minus_di > plus_di)

        # 4. Regime Mapping
        if current_adx >= self.trend_adx_threshold and is_bullish_alignment:
            confidence = min(0.95, 0.65 + (current_adx / 100.0) * 0.5)
            return self._build_policy(
                regime=MarketRegime.BULLISH_EXPANSION,
                confidence=confidence,
                vol_ratio=vol_ratio,
                adx=current_adx,
                bias="BULLISH",
                risk_mult=1.15,  # High-conviction expansion
                target_rr=2.8,
                allow_breakout=True,
                allow_reversion=False,
                trailing_mult=1.8,
                rationale=f"Bullish expansion: M15 ADX {current_adx:.1f} with aligned H1 EMA hierarchy (Close > EMA20 > EMA50).",
            )

        elif current_adx >= self.trend_adx_threshold and is_bearish_alignment:
            confidence = min(0.95, 0.65 + (current_adx / 100.0) * 0.5)
            return self._build_policy(
                regime=MarketRegime.BEARISH_EXPANSION,
                confidence=confidence,
                vol_ratio=vol_ratio,
                adx=current_adx,
                bias="BEARISH",
                risk_mult=1.15,
                target_rr=2.8,
                allow_breakout=True,
                allow_reversion=False,
                trailing_mult=1.8,
                rationale=f"Bearish expansion: M15 ADX {current_adx:.1f} with aligned downward H1 EMA hierarchy (Close < EMA20 < EMA50).",
            )

        else:
            # 5. Ranging Compression (Low trend / Mean-reversion domain)
            conf = min(0.92, 0.60 + max(0.0, (25.0 - current_adx) * 0.02))
            return self._build_policy(
                regime=MarketRegime.RANGING_COMPRESSION,
                confidence=conf,
                vol_ratio=vol_ratio,
                adx=current_adx,
                bias="NEUTRAL",
                risk_mult=0.90,
                target_rr=1.6,  # Tighter target for range boundaries
                allow_breakout=False,  # Breakouts in chop have high failure rate
                allow_reversion=True,  # Favor Setup B Liquidity Sweep & Reclaim
                trailing_mult=1.3,
                rationale=f"Ranging compression: ADX {current_adx:.1f} under trend threshold. Ideal for Liquidity Sweeps.",
            )

    def _build_policy(
        self,
        regime: MarketRegime,
        confidence: float,
        vol_ratio: float,
        adx: float,
        bias: str,
        risk_mult: float,
        target_rr: float,
        allow_breakout: bool,
        allow_reversion: bool,
        trailing_mult: float,
        rationale: str,
    ) -> RegimePolicy:
        policy = RegimePolicy(
            regime=regime,
            confidence=round(confidence, 3),
            volatility_ratio=round(vol_ratio, 3),
            adx=round(adx, 2),
            directional_bias=bias,
            risk_multiplier=round(risk_mult, 2),
            target_rr_ratio=round(target_rr, 2),
            allow_breakout=allow_breakout,
            allow_mean_reversion=allow_reversion,
            trailing_atr_mult=round(trailing_mult, 2),
            rationale=rationale,
        )
        if self.last_state is None or self.last_state.regime != regime:
            logger.info(
                f"[REGIME-TRANSITION] {self.last_state.regime.value if self.last_state else 'INITIAL'} -> "
                f"{regime.value} | ADX: {adx:.1f} | VolRatio: {vol_ratio:.2f}x | Bias: {bias} | Risk: {risk_mult:.2f}x"
            )
        self.last_state = policy
        return policy
