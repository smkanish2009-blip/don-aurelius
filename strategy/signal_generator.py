"""
Master Signal Coordinator & Conflict Resolver.
Integrates Asian range measurement, Setup A breakout, Setup B liquidity sweep,
and AI Meta-Labeling into one unified decision pipeline.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
import pandas as pd
from config.settings import BotConfig
from strategy.models import TradeSignal, SignalDirection, SetupType
from strategy.setup_a_breakout import SetupABreakout
from strategy.setup_b_sweep import SetupBSweepReclaim
from indicators.technicals import compute_atr
from indicators.range_detector import RangeDetector, AsianRange
from indicators.macro_trend import MacroTrendFilter
from ai.feature_extractor import FeatureExtractor
from ai.meta_labeler import MetaLabeler

logger = logging.getLogger("SignalGenerator")


class SignalGenerator:
    def __init__(self, config: BotConfig):
        self.config = config
        self.setup_a = SetupABreakout(config.strategy)
        self.setup_b = SetupBSweepReclaim(config.strategy)
        self.range_detector = RangeDetector(config.strategy, config.sessions)
        self.meta_labeler = MetaLabeler(config.ai)
        self.macro_trend = MacroTrendFilter(config.macro_trend)
        self.current_range: Optional[AsianRange] = None
        self.setup_b_fired_today = False
        self.setup_a_fired_today = False

    def update_asian_range(self, df_m5: pd.DataFrame, df_h1: pd.DataFrame, target_date: datetime.date) -> Optional[AsianRange]:
        """Calculates and validates the Asian range at AsianEnd_GMT (07:00 GMT)."""
        if len(df_h1) < 20:
            return None
        h1_atr = float(compute_atr(df_h1, 14).iloc[-2])
        self.current_range = self.range_detector.calculate_range(df_m5, h1_atr, target_date)
        return self.current_range

    def evaluate_signals(self, df_m5: pd.DataFrame, df_m15: pd.DataFrame, df_h1: pd.DataFrame,
                         current_gmt: datetime, current_spread: float,
                         df_h4: Optional[pd.DataFrame] = None) -> Optional[Tuple[TradeSignal, float]]:
        """
        Coordinates signal generation based on active session time windows and macro trends.
        Returns: (TradeSignal, risk_multiplier) or None
        """
        if not self.current_range or not self.current_range.is_valid:
            return None

        r_high = self.current_range.high
        r_low = self.current_range.low
        t = current_gmt.time()

        # 1. Setup B (Sweep & Reclaim) Window: 07:45 - 10:30 GMT
        if self.config.sessions.SETUP_B_START_GMT <= t.strftime("%H:%M") <= self.config.sessions.SETUP_B_END_GMT:
            if not self.setup_b_fired_today:
                sig_b = self.setup_b.evaluate(df_m5, df_h1, r_high, r_low)
                if sig_b:
                    if df_h4 is not None:
                        ok_macro, macro_msg = self.macro_trend.validate_setup_b(
                            signal_direction=sig_b.direction.value,
                            rejection_wick_ratio=0.65,
                            ai_confidence=0.68,
                            df_h4=df_h4
                        )
                        if not ok_macro:
                            return None
                    self.setup_b_fired_today = True
                    return self._process_through_ai(sig_b, df_m5, df_m15, df_h1, r_high, r_low, current_spread)

        # 2. Setup A (Breakout) Windows: 08:00 - 11:30 and 13:00 - 16:30 GMT
        w1_active = self.config.sessions.SETUP_A_WINDOW_1_START <= t.strftime("%H:%M") <= self.config.sessions.SETUP_A_WINDOW_1_END
        w2_active = self.config.sessions.SETUP_A_WINDOW_2_START <= t.strftime("%H:%M") <= self.config.sessions.SETUP_A_WINDOW_2_END

        if w1_active or w2_active:
            if not self.setup_a_fired_today:
                sig_a = self.setup_a.evaluate(df_m15, df_h1, r_high, r_low)
                if sig_a:
                    if df_h4 is not None:
                        ok_macro, macro_msg = self.macro_trend.validate_setup_a(
                            signal_direction=sig_a.direction.value,
                            df_h4=df_h4
                        )
                        if not ok_macro:
                            return None
                    self.setup_a_fired_today = True
                    return self._process_through_ai(sig_a, df_m5, df_m15, df_h1, r_high, r_low, current_spread)

        return None

    def _process_through_ai(self, signal: TradeSignal, df_m5: pd.DataFrame, df_m15: pd.DataFrame,
                            df_h1: pd.DataFrame, r_high: float, r_low: float, spread: float) -> Optional[Tuple[TradeSignal, float]]:
        """Passes candidate trade through the AI Meta-Labeling engine."""
        if not self.config.ai.ENABLED:
            return signal, 1.0

        features = FeatureExtractor.extract_features(df_m5, df_m15, df_h1, r_high, r_low, spread)
        allowed, p_win, risk_mult = self.meta_labeler.filter_trade(features)

        if not allowed:
            return None

        signal.confidence_score = p_win
        return signal, risk_mult

    def reset_daily_flags(self) -> None:
        self.current_range = None
        self.setup_b_fired_today = False
        self.setup_a_fired_today = False
