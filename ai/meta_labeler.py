"""
Machine Learning Meta-Labeling Gatekeeper.
Implements Marcos López de Prado's Meta-Labeling framework to predict trade success probability.
Supports dual operational regimes:
  1. TRAINED_ML: Pure Python/NumPy inference from a trained walk-forward regularized model
     (models/meta_classifier.json) when real forward-test/historical labeled samples exist.
  2. HEURISTIC_WARMUP: High-conviction empirical rules while forward-test samples are collecting.
Acts as a dynamic filter: blocks false breakouts and scales high-conviction setups.
"""

import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np

from config.settings import AISettings

logger = logging.getLogger("MetaLabeler")


class MetaLabeler:
    def __init__(self, ai_settings: AISettings, model_path: str = "models/meta_classifier.json"):
        self.settings = ai_settings
        self.model_path = model_path
        self.model_data: Optional[Dict[str, Any]] = None
        self.load_model()

    def load_model(self) -> bool:
        """
        Attempts to load a trained ML classifier from disk.
        Returns True if loaded successfully and enters TRAINED_ML mode; False otherwise.
        """
        if not os.path.exists(self.model_path):
            self.model_data = None
            logger.info(f"No trained meta-classifier found at '{self.model_path}'. Running in HEURISTIC_WARMUP mode.")
            return False

        try:
            with open(self.model_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate required schema
            required_keys = ["weights", "bias", "feature_names", "means", "stds"]
            if not all(k in data for k in required_keys):
                logger.warning(f"Meta-classifier '{self.model_path}' is missing required fields. Falling back to heuristic.")
                self.model_data = None
                return False

            self.model_data = data
            n_samples = data.get("train_samples", "unknown")
            auc = data.get("metrics", {}).get("cv_roc_auc", "N/A")
            logger.info(f"Loaded trained Meta-Classifier ML model ({len(data['feature_names'])} features, {n_samples} samples, CV AUC: {auc}). Operating in TRAINED_ML mode.")
            return True
        except Exception as e:
            logger.error(f"Error loading meta-classifier from '{self.model_path}': {e}. Using HEURISTIC_WARMUP.")
            self.model_data = None
            return False

    @property
    def model_mode(self) -> str:
        """Returns the active operational mode: TRAINED_ML or HEURISTIC_WARMUP."""
        return "TRAINED_ML" if self.model_data is not None else "HEURISTIC_WARMUP"

    def predict_success_probability(self, features: Dict[str, float]) -> float:
        """
        Calculates calibrated trade success probability P(Win) in [0.05, 0.95].
        Uses trained ML parameters if model file is active; otherwise uses the warmup heuristic.
        """
        if self.model_data is not None:
            return self._predict_ml(features)
        return self._predict_heuristic(features)

    def _predict_ml(self, features: Dict[str, float]) -> float:
        """Executes standardized regularized logistic inference with optional Platt scaling."""
        feat_names = self.model_data["feature_names"]
        weights = np.array(self.model_data["weights"], dtype=float)
        bias = float(self.model_data["bias"])
        means = np.array(self.model_data["means"], dtype=float)
        stds = np.array(self.model_data["stds"], dtype=float)

        raw_vec = np.array([float(features.get(k, 0.0)) for k in feat_names], dtype=float)
        # Z-score standardization with epsilon
        z = (raw_vec - means) / np.where(stds > 1e-6, stds, 1.0)

        # Logit
        logit = float(np.dot(z, weights) + bias)

        # Platt scaling if calibrated
        platt_a = self.model_data.get("platt_a")
        platt_b = self.model_data.get("platt_b")
        if platt_a is not None and platt_b is not None:
            calibrated_logit = float(platt_a * logit + platt_b)
        else:
            calibrated_logit = logit

        # Bounded sigmoid
        clipped = np.clip(calibrated_logit, -8.0, 8.0)
        p_win = 1.0 / (1.0 + np.exp(-clipped))
        return float(round(max(0.05, min(p_win, 0.95)), 4))

    def _predict_heuristic(self, features: Dict[str, float]) -> float:
        """
        Heuristic scoring warmup based on institutional microstructure logic.
        Used until sufficient clean forward-test data is gathered for walk-forward CV.
        """
        score = 0.50  # Prior base rate (~45-50% on gold breakouts)

        # Factor 1: Clean Asian range compression (0.8 - 2.2 x ATR is the sweet spot)
        range_atr = features.get("range_x_atr_h1", 1.5)
        if 0.9 <= range_atr <= 2.2:
            score += 0.08
        elif range_atr > 2.8:
            score -= 0.12  # Over-expanded range: high probability of exhaustion

        # Factor 2: Strong H1 trend alignment
        trend_aligned = features.get("ema_trend_aligned", 0.0)
        if abs(trend_aligned) > 0.5:
            score += 0.07

        # Factor 3: ADX momentum strength & rising slope
        adx = features.get("adx_h1", 20.0)
        adx_slope = features.get("adx_slope_3bars", 0.0)
        if adx >= 25.0 and adx_slope > 0:
            score += 0.06
        elif adx < 18.0:
            score -= 0.08  # Weak trend / chop

        # Factor 4: Breakout candle quality (clean body with minimal opposing wick)
        body_ratio = features.get("m15_body_to_range", 0.5)
        if body_ratio >= 0.65:
            score += 0.06
        elif body_ratio < 0.40:
            score -= 0.09

        # Factor 5: Spread drag
        spread_ratio = features.get("spread_to_range_ratio", 0.01)
        if spread_ratio > 0.05:
            score -= 0.10

        # Bound probability between 0.10 and 0.95
        p_win = max(0.10, min(score, 0.95))
        return float(round(p_win, 4))

    def filter_trade(self, features: Dict[str, float]) -> Tuple[bool, float, float]:
        """
        Determines whether to execute trade candidate and provides risk scaling factor.
        Returns: (allow_trade: bool, p_win: float, risk_multiplier: float)
        """
        p_win = self.predict_success_probability(features)

        if p_win < self.settings.META_MODEL_MIN_PROBABILITY:
            logger.info(f"AI Meta-Labeler [{self.model_mode}] BLOCKED trade: P(Win)={p_win:.2f} < Threshold={self.settings.META_MODEL_MIN_PROBABILITY:.2f}")
            return False, p_win, 0.0

        risk_mult = 1.0
        if p_win >= self.settings.HIGH_CONFIDENCE_THRESHOLD:
            risk_mult = self.settings.HIGH_CONFIDENCE_RISK_SCALE
            logger.info(f"AI Meta-Labeler [{self.model_mode}] HIGH CONFIDENCE: P(Win)={p_win:.2f}. Scaling risk to {risk_mult}x")
        else:
            logger.info(f"AI Meta-Labeler [{self.model_mode}] APPROVED trade: P(Win)={p_win:.2f}")

        return True, p_win, risk_mult

    def get_status(self) -> Dict[str, Any]:
        """Returns metadata regarding active classifier state."""
        return {
            "mode": self.model_mode,
            "model_path": self.model_path,
            "has_model_file": self.model_data is not None,
            "feature_count": len(self.model_data["feature_names"]) if self.model_data else 0,
            "train_samples": self.model_data.get("train_samples") if self.model_data else 0,
            "metrics": self.model_data.get("metrics", {}) if self.model_data else None
        }
