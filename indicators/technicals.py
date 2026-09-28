"""
Technical Indicator Calculations.
Vectorized implementations for EMA, ADX, True Range, ATR, and Volatility metrics.
"""

import numpy as np
import pandas as pd


def compute_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculates Exponential Moving Average (EMA)."""
    return series.ewm(span=period, adjust=False).mean()


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculates Average True Range (ATR) using Wilder's smoothing."""
    high = df["high"]
    low = df["low"]
    close_prev = df["close"].shift(1)

    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return true_range.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()


def compute_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculates Average Directional Index (ADX) along with +DI and -DI.
    Returns DataFrame with columns ['adx', 'plus_di', 'minus_di'].
    """
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)

    tr = compute_atr(df, period=1)  # 1-bar true range

    atr_smooth = pd.Series(tr).ewm(alpha=1.0 / period, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm).ewm(alpha=1.0 / period, adjust=False).mean() / atr_smooth)
    minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1.0 / period, adjust=False).mean() / atr_smooth)

    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9))
    adx = dx.ewm(alpha=1.0 / period, adjust=False).mean()

    return pd.DataFrame({"adx": adx, "plus_di": plus_di, "minus_di": minus_di})


def compute_garman_klass_volatility(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Computes Garman-Klass volatility estimator (superior estimator using OHLC)."""
    log_hl = np.log(df["high"] / df["low"]) ** 2
    log_co = np.log(df["close"] / df["open"]) ** 2
    gk = 0.5 * log_hl - (2 * np.log(2) - 1) * log_co
    return np.sqrt(gk.rolling(window=window).mean())
