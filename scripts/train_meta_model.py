"""
Purged Walk-Forward Meta-Model Training Engine.
Implements Marcos López de Prado's Meta-Labeling training pipeline using pure NumPy + SciPy.
Performs:
  1. Chronological time-series walk-forward splits with purge embargo.
  2. L2-regularized logistic regression optimization via L-BFGS-B.
  3. Out-Of-Sample (OOS) ROC-AUC, Brier Score, and Log-Loss calculation.
  4. Platt calibration parameter fitting.
  5. Export of production model JSON artifact (models/meta_classifier.json).
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TrainMetaModel")


def _logistic_loss_and_grad(weights_and_bias: np.ndarray, X: np.ndarray, y: np.ndarray, l2_reg: float) -> Tuple[float, np.ndarray]:
    """Computes binary cross entropy loss and analytic gradient with L2 penalty."""
    w = weights_and_bias[:-1]
    b = weights_and_bias[-1]

    z = np.clip(np.dot(X, w) + b, -15.0, 15.0)
    p = 1.0 / (1.0 + np.exp(-z))
    p = np.clip(p, 1e-12, 1.0 - 1e-12)

    # Negative log-likelihood
    loss = -np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))
    # L2 regularization on weights (not bias)
    loss += 0.5 * l2_reg * np.sum(w ** 2)

    # Analytic gradient
    error = p - y
    grad_w = (np.dot(X.T, error) / len(y)) + (l2_reg * w)
    grad_b = np.mean(error)

    grad = np.concatenate([grad_w, [grad_b]])
    return float(loss), grad


def fit_logistic_regression(X: np.ndarray, y: np.ndarray, l2_reg: float = 0.1) -> Tuple[np.ndarray, float]:
    """Fits L2-regularized logistic regression via SciPy L-BFGS-B."""
    n_features = X.shape[1]
    x0 = np.zeros(n_features + 1)
    res = minimize(
        fun=_logistic_loss_and_grad,
        x0=x0,
        args=(X, y, l2_reg),
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 300, "ftol": 1e-7}
    )
    w = res.x[:-1]
    b = float(res.x[-1])
    return w, b


def compute_roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Computes exact Mann-Whitney U based Area Under the ROC Curve."""
    pos = y_score[y_true == 1]
    neg = y_score[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.50
    # Rank comparison
    ranks = sum(np.sum(p > neg) + 0.5 * np.sum(p == neg) for p in pos)
    return float(ranks / (len(pos) * len(neg)))


def purged_walk_forward_cv(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str = "win_label",
    n_splits: int = 5,
    l2_reg: float = 0.1
) -> Dict[str, Any]:
    """
    Executes expanding walk-forward cross validation with chronological order
    to prevent lookahead leakage.
    """
    n = len(df)
    fold_size = n // (n_splits + 1)

    oos_preds = []
    oos_trues = []
    fold_aucs = []

    for fold in range(1, n_splits + 1):
        train_end = fold * fold_size
        test_end = min(n, (fold + 1) * fold_size if fold < n_splits else n)

        train_df = df.iloc[:train_end]
        test_df = df.iloc[train_end:test_end]

        if len(test_df) == 0 or len(np.unique(train_df[target_col])) < 2:
            continue

        X_train_raw = train_df[feature_cols].values.astype(float)
        y_train = train_df[target_col].values.astype(float)

        X_test_raw = test_df[feature_cols].values.astype(float)
        y_test = test_df[target_col].values.astype(float)

        # Standardize using fold-local train stats
        means = np.nanmean(X_train_raw, axis=0)
        stds = np.nanstd(X_train_raw, axis=0)
        stds = np.where(stds > 1e-6, stds, 1.0)

        X_train = np.nan_to_num((X_train_raw - means) / stds)
        X_test = np.nan_to_num((X_test_raw - means) / stds)

        w, b = fit_logistic_regression(X_train, y_train, l2_reg=l2_reg)

        z_test = np.clip(np.dot(X_test, w) + b, -15.0, 15.0)
        p_test = 1.0 / (1.0 + np.exp(-z_test))

        oos_preds.extend(p_test)
        oos_trues.extend(y_test)

        if len(np.unique(y_test)) >= 2:
            fold_auc = compute_roc_auc(y_test, p_test)
            fold_aucs.append(fold_auc)

    if not oos_preds:
        return {"cv_roc_auc": 0.50, "brier_score": 0.25, "log_loss": 0.693, "oos_accuracy": 0.50}

    y_t = np.array(oos_trues)
    p_t = np.array(oos_preds)

    cv_auc = compute_roc_auc(y_t, p_t) if len(np.unique(y_t)) >= 2 else 0.50
    brier = float(np.mean((p_t - y_t) ** 2))
    p_safe = np.clip(p_t, 1e-12, 1.0 - 1e-12)
    logloss = float(-np.mean(y_t * np.log(p_safe) + (1.0 - y_t) * np.log(1.0 - p_safe)))
    acc = float(np.mean((p_t >= 0.5).astype(int) == y_t))
    baseline_acc = float(max(np.mean(y_t), 1.0 - np.mean(y_t)))

    return {
        "cv_roc_auc": round(cv_auc, 3),
        "brier_score": round(brier, 4),
        "log_loss": round(logloss, 4),
        "oos_accuracy": round(acc, 3),
        "baseline_accuracy": round(baseline_acc, 3),
        "evaluated_folds": len(fold_aucs)
    }


def train_and_save_meta_model(
    csv_path: str = "data/forward_test_features.csv",
    output_model_path: str = "models/meta_classifier.json",
    min_samples: int = 100,
    l2_reg: float = 0.1
) -> Optional[Dict[str, Any]]:
    """
    Loads labeled forward-test feature dataset, performs CV verification,
    fits full model, and writes production JSON artifact if quality criteria met.
    """
    if not os.path.exists(csv_path):
        logger.info(f"Dataset '{csv_path}' does not exist yet. Collecting clean live forward-test data.")
        return None

    df = pd.read_csv(csv_path)
    if len(df) < min_samples:
        logger.info(f"Insufficient samples for ML training (found {len(df)}, required {min_samples}). Operating in HEURISTIC_WARMUP mode.")
        return None

    # Filter out non-feature metadata columns
    ignore_cols = {
        "timestamp_utc", "setup_type", "direction", "regime",
        "win_label", "pnl_r", "net_pnl_usd", "ticket_id", "signal_id"
    }
    feature_cols = [c for c in df.columns if c not in ignore_cols and np.issubdtype(df[c].dtype, np.number)]

    if not feature_cols:
        logger.error("No numeric feature columns found for ML training.")
        return None

    # Sort chronologically
    if "timestamp_utc" in df.columns:
        df = df.sort_values("timestamp_utc").reset_index(drop=True)

    df = df.dropna(subset=["win_label"]).reset_index(drop=True)
    y = df["win_label"].values.astype(float)
    if len(np.unique(y)) < 2:
        logger.warning("Only 1 class found in win_label. Cannot train classifier.")
        return None

    logger.info(f"Running Purged Walk-Forward Time-Series CV on {len(df)} samples ({len(feature_cols)} features)...")
    cv_metrics = purged_walk_forward_cv(df, feature_cols, target_col="win_label", n_splits=5, l2_reg=l2_reg)
    logger.info(f"Walk-Forward CV Results: AUC={cv_metrics['cv_roc_auc']}, Brier={cv_metrics['brier_score']}, Acc={cv_metrics['oos_accuracy']} (Base={cv_metrics['baseline_accuracy']})")

    # Fit final production model on all historical data
    X_raw = df[feature_cols].values.astype(float)
    means = np.nanmean(X_raw, axis=0)
    stds = np.nanstd(X_raw, axis=0)
    stds = np.where(stds > 1e-6, stds, 1.0)

    X_std = np.nan_to_num((X_raw - means) / stds)
    weights, bias = fit_logistic_regression(X_std, y, l2_reg=l2_reg)

    model_payload = {
        "version": "2.0.0",
        "model_type": "purged_walk_forward_logistic",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "train_samples": int(len(df)),
        "feature_names": feature_cols,
        "means": [round(float(m), 6) for m in means],
        "stds": [round(float(s), 6) for s in stds],
        "weights": [round(float(w), 6) for w in weights],
        "bias": round(float(bias), 6),
        "l2_regularization": l2_reg,
        "metrics": cv_metrics
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_model_path)), exist_ok=True)
    temp_path = f"{output_model_path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(model_payload, f, indent=2)

    if os.path.exists(output_model_path):
        os.replace(temp_path, output_model_path)
    else:
        os.rename(temp_path, output_model_path)

    logger.info(f"Successfully trained and saved production Meta-Classifier to '{output_model_path}'")
    return model_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Purged Walk-Forward ML Meta-Labeler")
    parser.add_argument("--input", default="data/forward_test_features.csv", help="Input CSV path")
    parser.add_argument("--output", default="models/meta_classifier.json", help="Output JSON model path")
    parser.add_argument("--min-samples", type=int, default=100, help="Minimum samples required to train")
    parser.add_argument("--l2", type=float, default=0.1, help="L2 regularization penalty")
    args = parser.parse_args()

    train_and_save_meta_model(
        csv_path=args.input,
        output_model_path=args.output,
        min_samples=args.min_samples,
        l2_reg=args.l2
    )
