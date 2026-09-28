"""
Asian Session Range Detector.
Identifies Asian session boundaries, computes range height, verifies ATR bounds,
and assesses range structure and cleanliness (touch counts).
"""

from dataclasses import dataclass
from datetime import datetime, time
import pandas as pd
from typing import Optional, Tuple
from config.settings import StrategyParameters, SessionSettings


@dataclass
class AsianRange:
    high: float
    low: float
    height: float
    is_valid: bool
    h1_atr: float
    touch_count_high: int
    touch_count_low: int
    rejection_ratio: float


class RangeDetector:
    def __init__(self, strategy_params: StrategyParameters, session_settings: SessionSettings):
        self.params = strategy_params
        self.sessions = session_settings

    def calculate_range(self, df_m5: pd.DataFrame, h1_atr: float, date_target: datetime.date) -> Optional[AsianRange]:
        """
        Extracts M5 bars between 00:00 and 07:00 GMT for the target date
        and computes the Asian range metrics.
        """
        start_time = time(0, 0)
        end_time = time(7, 0)

        # Filter M5 DataFrame for target date and Asian hours (UTC/GMT)
        mask = (
            (df_m5["time"].dt.date == date_target) &
            (df_m5["time"].dt.time >= start_time) &
            (df_m5["time"].dt.time < end_time)
        )
        asian_bars = df_m5[mask]

        if len(asian_bars) < 10:  # Incomplete Asian session data
            return None

        if self.params.RANGE_USES_WICKS:
            range_high = float(asian_bars["high"].max())
            range_low = float(asian_bars["low"].min())
        else:
            range_high = float(asian_bars[["open", "close"]].max().max())
            range_low = float(asian_bars[["open", "close"]].min().min())

        range_height = range_high - range_low

        # Validity test from Section 5:
        # MinRange_xATR * ATR_H1 <= RangeHeight <= MaxRange_xATR * ATR_H1
        min_allowed = self.params.MIN_RANGE_X_ATR * h1_atr
        max_allowed = self.params.MAX_RANGE_X_ATR * h1_atr
        is_valid = (min_allowed <= range_height <= max_allowed)

        # Touch count: number of bars whose wicks reached within 10% of high/low
        threshold_high = range_high - (0.10 * range_height)
        threshold_low = range_low + (0.10 * range_height)
        touch_high = int((asian_bars["high"] >= threshold_high).sum())
        touch_low = int((asian_bars["low"] <= threshold_low).sum())

        return AsianRange(
            high=range_high,
            low=range_low,
            height=range_height,
            is_valid=is_valid,
            h1_atr=h1_atr,
            touch_count_high=touch_high,
            touch_count_low=touch_low,
            rejection_ratio=min(touch_high, touch_low) / max(touch_high, touch_low, 1)
        )
