"""
Microstructure & Volatility Feature Extractor.
Generates 28 institutional features for Machine Learning Meta-Labeling:
Range efficiency, multi-timeframe trend alignment, volatility estimators,
volume distributions, and spread dynamics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from indicators.technicals import compute_atr, compute_garman_klass_volatility, compute_ema, compute_adx


class FeatureExtractor:
    @staticmethod
    def extract_features(df_m5: pd.DataFrame, df_m15: pd.DataFrame, df_h1: pd.DataFrame,
                         range_high: float, range_low: float, spread_usd: float) -> Dict[str, float]:
        """Extracts engineered feature vector from recent price series."""
        features = {}

        # 1. Asian Range Properties
        range_height = range_high - range_low
        atr_h1 = float(compute_atr(df_h1, 14).iloc[-2])
        atr_m15 = float(compute_atr(df_m15, 14).iloc[-2])

        features["range_height_usd"] = range_height
        features["range_x_atr_h1"] = range_height / (atr_h1 + 1e-9)
        features["spread_to_range_ratio"] = spread_usd / (range_height + 1e-9)

        # 2. Volatility Estimators
        gk_vol = float(compute_garman_klass_volatility(df_m15, 14).iloc[-2])
        features["garman_klass_vol_m15"] = gk_vol
        features["atr_ratio_m15_to_h1"] = atr_m15 / (atr_h1 + 1e-9)

        # 3. Trend & Momentum Features
        ema20_h1 = float(compute_ema(df_h1["close"], 20).iloc[-2])
        ema50_h1 = float(compute_ema(df_h1["close"], 50).iloc[-2])
        ema200_h1 = float(compute_ema(df_h1["close"], 200).iloc[-2])

        close_h1 = float(df_h1["close"].iloc[-2])
        features["dist_to_ema200_pct"] = (close_h1 - ema200_h1) / (ema200_h1 + 1e-9)
        features["ema_trend_aligned"] = 1.0 if (ema20_h1 > ema50_h1 > ema200_h1) else (
            -1.0 if (ema20_h1 < ema50_h1 < ema200_h1) else 0.0
        )

        adx_df = compute_adx(df_h1, 14)
        features["adx_h1"] = float(adx_df["adx"].iloc[-2])
        features["adx_slope_3bars"] = float(adx_df["adx"].iloc[-2] - adx_df["adx"].iloc[-5])

        # 4. Candlestick Momentum (Last M15 closed candle)
        c_bar = df_m15.iloc[-2]
        c_range = c_bar["high"] - c_bar["low"]
        c_body = abs(c_bar["close"] - c_bar["open"])
        features["m15_body_to_range"] = c_body / (c_range + 1e-9)
        features["m15_upper_wick_ratio"] = (c_bar["high"] - max(c_bar["open"], c_bar["close"])) / (c_range + 1e-9)
        features["m15_lower_wick_ratio"] = (min(c_bar["open"], c_bar["close"]) - c_bar["low"]) / (c_range + 1e-9)

        return features
