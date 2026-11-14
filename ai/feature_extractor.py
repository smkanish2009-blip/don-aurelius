"""
Microstructure & Volatility Feature Extractor.
Generates comprehensive point-in-time institutional features for Machine Learning Meta-Labeling:
Range efficiency, multi-timeframe trend alignment, volatility estimators,
volume distributions, and spread dynamics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from indicators.technicals import compute_atr, compute_garman_klass_volatility, compute_ema, compute_adx


class FeatureExtractor:
    @staticmethod
    def extract_features(
        df_m5: pd.DataFrame,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        range_high: float,
        range_low: float,
        spread_usd: float,
        direction: Optional[str] = None,
        setup_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extracts engineered feature vector from recent price series.
        Safely handles boundary conditions, guards against NaNs, and produces
        point-in-time normalized indicators for ML training & inference.
        """
        features: Dict[str, float] = {}

        # 1. Asian Range Properties
        range_height = float(range_high - range_low)
        atr_h1_s = compute_atr(df_h1, 14)
        atr_m15_s = compute_atr(df_m15, 14)
        atr_h1 = float(atr_h1_s.iloc[-2]) if len(atr_h1_s) >= 2 else 2.50
        atr_m15 = float(atr_m15_s.iloc[-2]) if len(atr_m15_s) >= 2 else 1.20

        features["range_height_usd"] = range_height
        features["range_x_atr_h1"] = range_height / (atr_h1 + 1e-9)
        features["spread_to_range_ratio"] = float(spread_usd) / (range_height + 1e-9)

        # 2. Volatility Estimators
        gk_s = compute_garman_klass_volatility(df_m15, 14)
        gk_vol = float(gk_s.iloc[-2]) if len(gk_s) >= 2 else 0.005
        features["garman_klass_vol_m15"] = gk_vol
        features["atr_ratio_m15_to_h1"] = atr_m15 / (atr_h1 + 1e-9)

        # 3. Trend & Momentum Features
        ema20_s = compute_ema(df_h1["close"], 20)
        ema50_s = compute_ema(df_h1["close"], 50)
        ema20_h1 = float(ema20_s.iloc[-2]) if len(ema20_s) >= 2 else float(df_h1["close"].iloc[-1])
        ema50_h1 = float(ema50_s.iloc[-2]) if len(ema50_s) >= 2 else float(df_h1["close"].iloc[-1])

        # Guard against < 200 bars for EMA 200
        if len(df_h1) >= 200:
            ema200_s = compute_ema(df_h1["close"], 200)
            ema200_h1 = float(ema200_s.iloc[-2])
        else:
            # Fallback to longest available EMA
            ema200_s = compute_ema(df_h1["close"], len(df_h1) - 5)
            ema200_h1 = float(ema200_s.iloc[-2]) if len(ema200_s) >= 2 else ema50_h1

        close_h1 = float(df_h1["close"].iloc[-2]) if len(df_h1) >= 2 else float(df_h1["close"].iloc[-1])
        features["dist_to_ema200_pct"] = (close_h1 - ema200_h1) / (ema200_h1 + 1e-9)
        features["ema_trend_aligned"] = 1.0 if (ema20_h1 > ema50_h1 > ema200_h1) else (
            -1.0 if (ema20_h1 < ema50_h1 < ema200_h1) else 0.0
        )

        adx_df = compute_adx(df_h1, 14)
        if len(adx_df) >= 5:
            features["adx_h1"] = float(adx_df["adx"].iloc[-2])
            features["adx_slope_3bars"] = float(adx_df["adx"].iloc[-2] - adx_df["adx"].iloc[-5])
        else:
            features["adx_h1"] = 20.0
            features["adx_slope_3bars"] = 0.0

        # 4. Candlestick Momentum (Last M15 closed candle)
        c_bar = df_m15.iloc[-2] if len(df_m15) >= 2 else df_m15.iloc[-1]
        c_range = float(c_bar["high"] - c_bar["low"])
        c_body = float(abs(c_bar["close"] - c_bar["open"]))
        features["m15_body_to_range"] = c_body / (c_range + 1e-9)
        features["m15_upper_wick_ratio"] = float(c_bar["high"] - max(c_bar["open"], c_bar["close"])) / (c_range + 1e-9)
        features["m15_lower_wick_ratio"] = float(min(c_bar["open"], c_bar["close"]) - c_bar["low"]) / (c_range + 1e-9)

        # 5. Extended Quantitative Microstructure & Time-Harmonic Features
        close_m15 = float(c_bar["close"])
        features["dist_to_range_high_atr"] = (range_high - close_m15) / (atr_m15 + 1e-9)
        features["dist_to_range_low_atr"] = (close_m15 - range_low) / (atr_m15 + 1e-9)
        features["ema20_ema50_spread_atr"] = (ema20_h1 - ema50_h1) / (atr_h1 + 1e-9)

        if len(df_m5) >= 5:
            close_m5_last = float(df_m5["close"].iloc[-2])
            close_m5_prev = float(df_m5["close"].iloc[-5])
            features["m5_return_3bars"] = (close_m5_last - close_m5_prev) / (close_m5_prev + 1e-9)
        else:
            features["m5_return_3bars"] = 0.0

        # Cyclical Hour of Day (UTC)
        try:
            if "time" in df_m15.columns:
                last_time = pd.to_datetime(df_m15["time"].iloc[-1])
                hour = last_time.hour + last_time.minute / 60.0
            else:
                now_dt = datetime.now(timezone.utc)
                hour = now_dt.hour + now_dt.minute / 60.0
        except Exception:
            hour = 12.0

        features["hour_utc_sin"] = float(np.sin(2.0 * np.pi * hour / 24.0))
        features["hour_utc_cos"] = float(np.cos(2.0 * np.pi * hour / 24.0))

        # Contextual Categorical Flags
        features["is_buy_signal"] = 1.0 if str(direction).upper() in ["BUY", "SIGNALDIRECTION.BUY"] else 0.0
        features["setup_is_breakout"] = 1.0 if "BREAKOUT" in str(setup_type).upper() or "SETUP_A" in str(setup_type).upper() else 0.0

        # Sanitize all outputs (finite values only)
        sanitized: Dict[str, float] = {}
        for k, v in features.items():
            clean_v = float(np.nan_to_num(v, nan=0.0, posinf=1.0, neginf=-1.0))
            sanitized[k] = round(clean_v, 6)

        return sanitized
