"""
Forward-Test Telemetry & Machine Learning Sample Tracker.
Logs every live trade candidate (executed or vetoed), feature vectors, and closed trade outcomes.
Calculates rigorous empirical forward-test metrics over rolling 30-day, 180-day (6-month),
and 365-day (12-month) horizons:
  - Annualized Sharpe Ratio (sqrt(252))
  - Sortino Ratio (downside deviation)
  - Peak-to-Trough Maximum Drawdown %
  - Calmar Ratio
  - Expectancy (R-multiple)
  - Profit Factor & Win Rate %
  - Sample Maturity Status & 6M/12M Verification Progress
Exports clean labeled datasets to CSV for Purged Walk-Forward ML training.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from contextlib import closing

import numpy as np
import pandas as pd

logger = logging.getLogger("ForwardTestTracker")


class ForwardTestTracker:
    """Institutional-grade forward-test logger and empirical performance auditor."""

    def __init__(self, db_path: str = "data/forward_test.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes SQLite schema for signal candidates, outcomes, and equity curve."""
        with closing(self._get_connection()) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS signal_logs (
                        signal_id TEXT PRIMARY KEY,
                        timestamp_utc TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        setup_type TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        stop_loss REAL NOT NULL,
                        take_profit REAL NOT NULL,
                        risk_r REAL NOT NULL,
                        spread_usd REAL NOT NULL,
                        regime TEXT NOT NULL,
                        meta_prob REAL NOT NULL,
                        model_mode TEXT NOT NULL,
                        status TEXT NOT NULL,
                        veto_reason TEXT,
                        features_json TEXT,
                        ticket_id INTEGER,
                        closed_at_utc TEXT,
                        exit_price REAL,
                        net_pnl_usd REAL,
                        pnl_r REAL,
                        slippage_usd REAL,
                        win_label INTEGER,
                        exit_reason TEXT
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sig_time ON signal_logs(timestamp_utc)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sig_ticket ON signal_logs(ticket_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sig_status ON signal_logs(status)")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS equity_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp_utc TEXT NOT NULL,
                        balance REAL NOT NULL,
                        equity REAL NOT NULL,
                        floating_pnl REAL NOT NULL,
                        drawdown_pct REAL NOT NULL,
                        source TEXT NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_eq_time ON equity_snapshots(timestamp_utc)")

    def record_signal_candidate(
        self,
        signal_id: str,
        symbol: str,
        setup_type: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_r: float,
        spread_usd: float,
        regime: str,
        meta_prob: float,
        model_mode: str,
        status: str,
        veto_reason: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        ticket_id: Optional[int] = None,
        timestamp_utc: Optional[str] = None
    ) -> str:
        """
        Logs a candidate evaluation point-in-time, whether executed or vetoed by risk/AI.
        """
        now_iso = timestamp_utc or datetime.now(timezone.utc).isoformat()
        feat_str = json.dumps(features or {})

        with closing(self._get_connection()) as conn:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO signal_logs (
                        signal_id, timestamp_utc, symbol, setup_type, direction,
                        entry_price, stop_loss, take_profit, risk_r, spread_usd,
                        regime, meta_prob, model_mode, status, veto_reason,
                        features_json, ticket_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal_id, now_iso, symbol, str(setup_type), str(direction),
                    float(entry_price), float(stop_loss), float(take_profit),
                    float(risk_r), float(spread_usd), str(regime),
                    float(meta_prob), str(model_mode), str(status),
                    veto_reason, feat_str, ticket_id
                ))
        return signal_id

    def record_outcome(
        self,
        ticket_id: int,
        exit_price: float,
        net_pnl_usd: float,
        pnl_r: float,
        exit_reason: str,
        closed_at_utc: Optional[str] = None,
        slippage_usd: float = 0.0
    ) -> bool:
        """
        Updates an existing trade candidate row when MT5 confirms position liquidation.
        """
        now_iso = closed_at_utc or datetime.now(timezone.utc).isoformat()
        win_label = 1 if net_pnl_usd > 0 else 0

        with closing(self._get_connection()) as conn:
            with conn:
                cur = conn.execute("""
                    UPDATE signal_logs
                    SET closed_at_utc = ?,
                        exit_price = ?,
                        net_pnl_usd = ?,
                        pnl_r = ?,
                        slippage_usd = ?,
                        win_label = ?,
                        exit_reason = ?
                    WHERE ticket_id = ?
                """, (
                    now_iso, float(exit_price), float(net_pnl_usd),
                    float(pnl_r), float(slippage_usd), win_label,
                    str(exit_reason), ticket_id
                ))
                updated = cur.rowcount > 0

        if not updated:
            # Standalone exit record if pre-signal was not captured
            sig_id = f"orphan_{ticket_id}_{int(datetime.now(timezone.utc).timestamp())}"
            with closing(self._get_connection()) as conn:
                with conn:
                    conn.execute("""
                        INSERT INTO signal_logs (
                            signal_id, timestamp_utc, symbol, setup_type, direction,
                            entry_price, stop_loss, take_profit, risk_r, spread_usd,
                            regime, meta_prob, model_mode, status, ticket_id,
                            closed_at_utc, exit_price, net_pnl_usd, pnl_r,
                            slippage_usd, win_label, exit_reason
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sig_id, now_iso, "XAUUSD", "UNKNOWN", "UNKNOWN",
                        0.0, 0.0, 0.0, 1.0, 0.0,
                        "UNKNOWN", 0.50, "HEURISTIC_WARMUP", "EXECUTED", ticket_id,
                        now_iso, float(exit_price), float(net_pnl_usd), float(pnl_r),
                        float(slippage_usd), win_label, str(exit_reason)
                    ))
        return True

    def record_equity_snapshot(
        self,
        balance: float,
        equity: float,
        floating_pnl: float = 0.0,
        source: str = "MT5",
        timestamp_utc: Optional[str] = None
    ) -> None:
        """Records a point-in-time account balance and equity snapshot."""
        now_iso = timestamp_utc or datetime.now(timezone.utc).isoformat()
        balance = float(balance)
        equity = float(equity)
        floating_pnl = float(floating_pnl)

        with closing(self._get_connection()) as conn:
            # Fetch high water mark to calculate current drawdown %
            cur = conn.execute("SELECT MAX(equity) as peak FROM equity_snapshots")
            row = cur.fetchone()
            peak = float(row["peak"]) if row and row["peak"] is not None else equity
            peak = max(peak, equity)
            dd_pct = ((peak - equity) / peak * 100.0) if peak > 0 else 0.0

            with conn:
                conn.execute("""
                    INSERT INTO equity_snapshots (
                        timestamp_utc, balance, equity, floating_pnl, drawdown_pct, source
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (now_iso, balance, equity, floating_pnl, dd_pct, source))

    def compute_metrics(self, window_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Computes institutional-grade metrics:
          - Annualized Sharpe Ratio (sqrt(252))
          - Sortino Ratio
          - Max Drawdown % (peak-to-trough)
          - Calmar Ratio
          - Expectancy (R)
          - Profit Factor, Win Rate, Sample Maturity
        """
        now = datetime.now(timezone.utc)
        filter_clause = ""
        params: List[Any] = []
        if window_days is not None:
            cutoff = (now - timedelta(days=window_days)).isoformat()
            filter_clause = "WHERE timestamp_utc >= ?"
            params.append(cutoff)

        with closing(self._get_connection()) as conn:
            # Query trade outcomes
            trade_query = f"""
                SELECT timestamp_utc, closed_at_utc, net_pnl_usd, pnl_r, win_label
                FROM signal_logs
                {filter_clause} AND win_label IS NOT NULL
                ORDER BY timestamp_utc ASC
            """ if filter_clause else """
                SELECT timestamp_utc, closed_at_utc, net_pnl_usd, pnl_r, win_label
                FROM signal_logs
                WHERE win_label IS NOT NULL
                ORDER BY timestamp_utc ASC
            """
            cur = conn.execute(trade_query, params)
            trade_rows = cur.fetchall()

            # Query equity snapshots
            eq_query = f"""
                SELECT timestamp_utc, balance, equity, drawdown_pct
                FROM equity_snapshots
                {filter_clause}
                ORDER BY timestamp_utc ASC
            """
            cur_eq = conn.execute(eq_query, params)
            eq_rows = cur_eq.fetchall()

        total_trades = len(trade_rows)
        wins = [r for r in trade_rows if r["win_label"] == 1]
        losses = [r for r in trade_rows if r["win_label"] == 0]

        total_net_pnl = float(sum(r["net_pnl_usd"] for r in trade_rows)) if total_trades > 0 else 0.0
        gross_profit = float(sum(r["net_pnl_usd"] for r in wins)) if wins else 0.0
        gross_loss = float(abs(sum(r["net_pnl_usd"] for r in losses))) if losses else 0.0

        win_rate_pct = round((len(wins) / total_trades) * 100.0, 2) if total_trades > 0 else 0.0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (
            round(gross_profit, 2) if gross_profit > 0 else 1.0
        )

        r_values = [float(r["pnl_r"]) for r in trade_rows if r["pnl_r"] is not None]
        expectancy_r = round(float(np.mean(r_values)), 3) if r_values else 0.0

        # Calculate time span
        start_ts = None
        end_ts = None
        if eq_rows:
            start_ts = eq_rows[0]["timestamp_utc"]
            end_ts = eq_rows[-1]["timestamp_utc"]
        elif trade_rows:
            start_ts = trade_rows[0]["timestamp_utc"]
            end_ts = trade_rows[-1]["timestamp_utc"]

        elapsed_days = 0.0
        if start_ts and end_ts:
            try:
                t0 = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(end_ts.replace("Z", "+00:00"))
                elapsed_days = max(0.0, (t1 - t0).total_seconds() / 86400.0)
            except Exception:
                elapsed_days = 0.0

        # Peak-to-trough Max Drawdown %
        max_drawdown_pct = 0.0
        if eq_rows:
            equities = np.array([float(r["equity"]) for r in eq_rows])
            peaks = np.maximum.accumulate(equities)
            drawdowns = np.where(peaks > 0, (peaks - equities) / peaks * 100.0, 0.0)
            max_drawdown_pct = round(float(np.max(drawdowns)), 2)
        elif trade_rows:
            cum_pnl = np.cumsum([float(r["net_pnl_usd"]) for r in trade_rows])
            peak_pnl = np.maximum.accumulate(cum_pnl)
            # Estimate off synthetic 100k equity if no snapshots
            dd_dollars = peak_pnl - cum_pnl
            max_dd_d = float(np.max(dd_dollars)) if len(dd_dollars) > 0 else 0.0
            max_drawdown_pct = round((max_dd_d / 100000.0) * 100.0, 2)

        # Daily Returns & Annualized Sharpe / Sortino
        sharpe_ratio: Optional[float] = None
        sortino_ratio: Optional[float] = None
        calmar_ratio: Optional[float] = None

        if eq_rows and len(eq_rows) >= 2:
            # Group into calendar days
            day_equities: Dict[str, float] = {}
            for r in eq_rows:
                d_key = r["timestamp_utc"][:10]
                day_equities[d_key] = float(r["equity"])

            sorted_days = sorted(day_equities.keys())
            if len(sorted_days) >= 5:
                daily_vals = np.array([day_equities[d] for d in sorted_days])
                daily_returns = np.diff(daily_vals) / daily_vals[:-1]

                mean_r = float(np.mean(daily_returns))
                std_r = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0

                if std_r > 1e-9:
                    sharpe_ratio = round(float((mean_r / std_r) * np.sqrt(252)), 2)

                # Sortino downside deviation (r < 0)
                downside = daily_returns[daily_returns < 0.0]
                if len(downside) > 0:
                    downside_dev = float(np.sqrt(np.mean(downside ** 2)))
                    if downside_dev > 1e-9:
                        sortino_ratio = round(float((mean_r / downside_dev) * np.sqrt(252)), 2)

                # Calmar Ratio
                if max_drawdown_pct > 0.01 and elapsed_days >= 30.0:
                    ann_return = mean_r * 252 * 100.0
                    calmar_ratio = round(ann_return / max_drawdown_pct, 2)

        # Maturity Classification
        if elapsed_days < 7.0 or total_trades < 10:
            maturity = "COLLECTING_DATA"
        elif elapsed_days < 60.0:
            maturity = "WARMUP_CALIBRATING"
        elif elapsed_days < 180.0:
            maturity = "INTERIM_FORWARD_TEST"
        elif elapsed_days < 365.0:
            maturity = "VALIDATED_6M"
        else:
            maturity = "VALIDATED_12M"

        progress_6m = min(100.0, round((elapsed_days / 180.0) * 100.0, 1))
        progress_12m = min(100.0, round((elapsed_days / 365.0) * 100.0, 1))

        return {
            "window_days": window_days or "all_time",
            "elapsed_days": round(elapsed_days, 1),
            "maturity_status": maturity,
            "progress_6m_pct": progress_6m,
            "progress_12m_pct": progress_12m,
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate_pct": win_rate_pct,
            "profit_factor": profit_factor,
            "expectancy_r": expectancy_r,
            "total_net_pnl_usd": round(total_net_pnl, 2),
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "first_record_utc": start_ts,
            "last_record_utc": end_ts
        }

    def get_horizon_report(self) -> Dict[str, Any]:
        """Generates comprehensive report across 30d, 180d, 365d, and all-time windows."""
        all_time = self.compute_metrics(window_days=None)
        rolling_30d = self.compute_metrics(window_days=30)
        rolling_180d = self.compute_metrics(window_days=180)
        rolling_365d = self.compute_metrics(window_days=365)

        # ML sample count
        with closing(self._get_connection()) as conn:
            cur = conn.execute("""
                SELECT COUNT(*) as cnt,
                       SUM(CASE WHEN win_label = 1 THEN 1 ELSE 0 END) as pos,
                       SUM(CASE WHEN win_label = 0 THEN 1 ELSE 0 END) as neg
                FROM signal_logs
                WHERE features_json IS NOT NULL AND win_label IS NOT NULL
            """)
            ml_row = cur.fetchone()

        labeled_samples = ml_row["cnt"] if ml_row and ml_row["cnt"] is not None else 0
        pos_samples = ml_row["pos"] if ml_row and ml_row["pos"] is not None else 0
        neg_samples = ml_row["neg"] if ml_row and ml_row["neg"] is not None else 0

        return {
            "all_time": all_time,
            "rolling_30d": rolling_30d,
            "rolling_180d": rolling_180d,
            "rolling_365d": rolling_365d,
            "ml_dataset": {
                "labeled_samples": labeled_samples,
                "positive_samples": pos_samples,
                "negative_samples": neg_samples,
                "ready_for_training": labeled_samples >= 100,
                "minimum_required": 100
            },
            "generated_at_utc": datetime.now(timezone.utc).isoformat()
        }

    def export_ml_dataset(self, csv_path: str = "data/forward_test_features.csv") -> int:
        """
        Exports point-in-time features and binary win labels for model retraining.
        Returns number of rows exported.
        """
        with closing(self._get_connection()) as conn:
            cur = conn.execute("""
                SELECT timestamp_utc, setup_type, direction, spread_usd, regime,
                       features_json, win_label, pnl_r, net_pnl_usd
                FROM signal_logs
                WHERE features_json IS NOT NULL AND win_label IS NOT NULL
                ORDER BY timestamp_utc ASC
            """)
            rows = cur.fetchall()

        if not rows:
            logger.info("No labeled ML samples to export.")
            return 0

        data = []
        for r in rows:
            feats = json.loads(r["features_json"])
            feats["setup_type"] = r["setup_type"]
            feats["direction"] = r["direction"]
            feats["spread_usd"] = r["spread_usd"]
            feats["regime"] = r["regime"]
            feats["win_label"] = r["win_label"]
            feats["pnl_r"] = r["pnl_r"]
            feats["net_pnl_usd"] = r["net_pnl_usd"]
            feats["timestamp_utc"] = r["timestamp_utc"]
            data.append(feats)

        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        df.to_csv(csv_path, index=False)
        logger.info(f"Exported {len(df)} ML training samples to {csv_path}")
        return len(df)

    def write_json_report(self, json_path: str = "data/forward_test_report.json") -> Dict[str, Any]:
        """Writes current horizon telemetry report to disk for dashboards and external auditing."""
        report = self.get_horizon_report()
        os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
        temp_path = f"{json_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        if os.path.exists(json_path):
            os.replace(temp_path, json_path)
        else:
            os.rename(temp_path, json_path)
        return report
