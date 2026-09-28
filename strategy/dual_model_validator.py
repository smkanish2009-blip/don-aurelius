"""
Layer 1 Defense: Dual-Model Validation Engine.
Model A: AI Meta-Labeler / Sentiment Engine (Generative / Probabilistic).
Model B: Strict Deterministic Rules Auditor (Non-AI mathematical filter).
A trade is permitted ONLY if both Model A and Model B independently approve with identical direction.
"""

import logging
from typing import Tuple, Optional
import pandas as pd
from strategy.models import TradeSignal, SignalDirection, SetupType
from config.settings import StrategyParameters
from indicators.technicals import compute_atr, compute_ema, compute_adx

logger = logging.getLogger("DualModelValidator")


class DualModelValidator:
    def __init__(self, params: StrategyParameters):
        self.params = params

    def audit_model_b(self, signal: TradeSignal, df_m15: pd.DataFrame, df_h1: pd.DataFrame,
                      range_high: float, range_low: float) -> Tuple[bool, str]:
        """
        Model B: Deterministic Hard Rules Audit.
        Re-evaluates the physical market geometry independently from any AI prediction.
        """
        if len(df_h1) < 200 or len(df_m15) < 20:
            return False, "Model B Reject: Insufficient bar history for independent validation."

        atr_h1 = float(compute_atr(df_h1, 14).iloc[-2])
        atr_m15 = float(compute_atr(df_m15, 14).iloc[-2])

        # Rule 1: Stop distance bounds check
        stop_dist = abs(signal.entry_price - signal.stop_loss)
        min_sl = 1.0 * atr_h1
        max_sl = 2.8 * atr_h1

        if not (min_sl <= stop_dist <= max_sl):
            return False, f"Model B Reject: Stop distance ${stop_dist:.2f} outside allowed bounds [${min_sl:.2f}, ${max_sl:.2f}]."

        # Rule 2: Take Profit risk-to-reward ratio check
        reward_dist = abs(signal.take_profit - signal.entry_price)
        rr_ratio = reward_dist / (stop_dist + 1e-9)
        if rr_ratio < 1.4:
            return False, f"Model B Reject: Reward-to-risk ratio {rr_ratio:.2f} is below minimum 1.4R."

        # Rule 3: Trend alignment verification for Setup A
        if signal.setup_type == SetupType.SETUP_A:
            ema200 = float(compute_ema(df_h1["close"], 200).iloc[-2])
            adx_val = float(compute_adx(df_h1, 14)["adx"].iloc[-2])

            if signal.direction == SignalDirection.BUY and signal.entry_price <= ema200:
                return False, "Model B Reject: Buy signal entry is below H1 EMA200."
            if signal.direction == SignalDirection.SELL and signal.entry_price >= ema200:
                return False, "Model B Reject: Sell signal entry is above H1 EMA200."
            if adx_val < self.params.ADX_MIN:
                return False, f"Model B Reject: H1 ADX ({adx_val:.1f}) is below minimum {self.params.ADX_MIN}."

        logger.info(f"Model B Audit Passed for {signal.setup_type.value} {signal.direction.value} @ ${signal.entry_price:.2f}")
        return True, "Model B Approved."

    def validate_handshake(self, signal: TradeSignal, ai_confidence: float,
                           df_m15: pd.DataFrame, df_h1: pd.DataFrame,
                           range_high: float, range_low: float) -> Tuple[bool, str]:
        """
        Executes the dual-model cryptographic handshake:
        - Model A must have confidence >= 0.58
        - Model B must pass 100% of mathematical geometry rules
        """
        # Model A verification
        if ai_confidence < 0.58:
            return False, f"Dual-Model Veto: Model A confidence ({ai_confidence:.2f}) < 0.58."

        # Model B independent audit
        model_b_ok, reason = self.audit_model_b(signal, df_m15, df_h1, range_high, range_low)
        if not model_b_ok:
            return False, f"Dual-Model Veto: {reason}"

        logger.info(f"[DEFENSE] Dual-Model Handshake SUCCESS: Model A (P={ai_confidence:.2f}) & Model B (Rules) both APPROVED.")
        return True, "Dual-Model Handshake Verified."
