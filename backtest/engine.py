"""
Event-Driven Backtest Engine for XAUUSD (Gold).
Simulates realistic trade execution with bid/ask spreads, slippage,
break-even adjustments, partial profits, trailing stops, and time stops.
"""

import math
import numpy as np
import pandas as pd
from datetime import datetime, time, timezone
from typing import Dict, List, Any, Optional

from config.settings import BotConfig, StrategyParameters, RiskParameters, SessionSettings
from strategy.models import TradeSignal, SignalDirection, SetupType
from strategy.setup_a_breakout import SetupABreakout
from strategy.setup_b_sweep import SetupBSweepReclaim
from indicators.technicals import compute_atr, compute_ema, compute_adx
from indicators.range_detector import RangeDetector
from ai.feature_extractor import FeatureExtractor
from ai.meta_labeler import MetaLabeler
from risk.position_sizer import PositionSizer


class BacktestEngine:
    def __init__(self, config: Optional[BotConfig] = None):
        self.config = config or BotConfig()
        self.setup_a = SetupABreakout(self.config.strategy)
        self.setup_b = SetupBSweepReclaim(self.config.strategy)
        self.range_detector = RangeDetector(self.config.strategy, self.config.sessions)
        self.meta_labeler = MetaLabeler(self.config.ai)
        self.position_sizer = PositionSizer(self.config.risk)

    def run(self, df_m5: pd.DataFrame, initial_balance: float = 10000.0,
            spread_usd: float = 0.30, slippage_usd: float = 0.15) -> Dict[str, Any]:
        """
        Executes an event-driven backtest over historical M5 bars.
        df_m5 must contain ['time', 'open', 'high', 'low', 'close', 'tick_volume']
        where 'time' is UTC/GMT datetime.
        """
        # Resample H1 and M15 for indicators
        df_m5_indexed = df_m5.set_index("time")
        df_h1 = df_m5_indexed.resample("1h").agg({
            "open": "first", "high": "max", "low": "min", "close": "last"
        }).dropna().reset_index()
        df_m15 = df_m5_indexed.resample("15min").agg({
            "open": "first", "high": "max", "low": "min", "close": "last"
        }).dropna().reset_index()

        df_h1["atr"] = compute_atr(df_h1, 14)
        df_h1["ema200"] = compute_ema(df_h1["close"], 200)
        df_m15["atr"] = compute_atr(df_m15, 14)

        balance = initial_balance
        equity = initial_balance
        peak_equity = initial_balance
        trades = []
        open_trade = None

        current_date = None
        asian_range = None
        daily_trades_taken = 0
        setup_a_fired_today = False
        setup_b_fired_today = False

        # Iterate through M5 bars sequentially
        for idx in range(50, len(df_m5)):
            row = df_m5.iloc[idx]
            bar_time = row["time"]
            bar_date = bar_time.date()
            bar_t = bar_time.time()

            # 1. New Day Initialization
            if bar_date != current_date:
                current_date = bar_date
                asian_range = None
                daily_trades_taken = 0
                setup_a_fired_today = False
                setup_b_fired_today = False

            # 2. Asian Session End (07:00 GMT): Compute Range
            if bar_t >= time(7, 0) and asian_range is None:
                # Find corresponding H1 ATR
                h1_sub = df_h1[df_h1["time"] <= bar_time]
                if len(h1_sub) > 20:
                    h1_atr = float(h1_sub["atr"].iloc[-1])
                    asian_range = self.range_detector.calculate_range(df_m5.iloc[:idx+1], h1_atr, current_date)

            # 3. Active Position Management (if a trade is currently open)
            if open_trade is not None:
                # Update bar counter
                open_trade["bars_held"] += 1

                # Check high/low extremes
                high_p = row["high"]
                low_p = row["low"]
                entry_p = open_trade["entry_price"]
                sl_p = open_trade["sl"]
                tp_p = open_trade["tp"]
                risk_dist = open_trade["risk_dist"]
                is_buy = (open_trade["direction"] == SignalDirection.BUY)

                # Track best price seen
                if is_buy and high_p > open_trade["best_price"]:
                    open_trade["best_price"] = high_p
                elif not is_buy and low_p < open_trade["best_price"]:
                    open_trade["best_price"] = low_p

                # Current R multiple
                current_max_r = ((open_trade["best_price"] - entry_p) if is_buy else (entry_p - open_trade["best_price"])) / risk_dist

                # A. Break-Even Check (+1.0R)
                if not open_trade["is_breakeven"] and current_max_r >= self.config.strategy.BREAKEVEN_TRIGGER_R:
                    open_trade["sl"] = entry_p + (spread_usd + 0.10) if is_buy else entry_p - (spread_usd + 0.10)
                    open_trade["is_breakeven"] = True

                # B. Partial Profit Check (+1.5R)
                if not open_trade["is_partial_closed"] and current_max_r >= self.config.strategy.PARTIAL_CLOSE_TRIGGER_R:
                    partial_lots = open_trade["lots"] * self.config.strategy.PARTIAL_CLOSE_RATIO
                    partial_pnl = (1.5 * risk_dist * partial_lots * 100.0)
                    balance += partial_pnl
                    equity = balance
                    open_trade["lots"] -= partial_lots
                    open_trade["is_partial_closed"] = True
                    open_trade["banked_pnl"] += partial_pnl

                # C. Check Stop Loss
                is_stopped = (low_p <= sl_p) if is_buy else (high_p >= sl_p)
                if is_stopped:
                    exit_price = sl_p - slippage_usd if is_buy else sl_p + slippage_usd
                    pnl_per_oz = (exit_price - entry_p) if is_buy else (entry_p - exit_price)
                    final_pnl = (pnl_per_oz * open_trade["lots"] * 100.0) + open_trade["banked_pnl"]
                    balance += (pnl_per_oz * open_trade["lots"] * 100.0)
                    equity = balance
                    pnl_r = final_pnl / (open_trade["risk_money"] + 1e-9)

                    trades.append({
                        "setup": open_trade["setup"].value,
                        "direction": open_trade["direction"].value,
                        "entry": entry_p, "exit": exit_price,
                        "sl": open_trade["initial_sl"], "tp": tp_p,
                        "lots": open_trade["initial_lots"],
                        "pnl_usd": final_pnl, "pnl_r": pnl_r,
                        "bars_held": open_trade["bars_held"],
                        "outcome": "WIN" if final_pnl > 0 else "LOSS",
                        "exit_reason": "STOP_LOSS"
                    })
                    open_trade = None

                # D. Check Take Profit
                elif open_trade is not None and ((is_buy and high_p >= tp_p) or (not is_buy and low_p <= tp_p)):
                    exit_price = tp_p - slippage_usd if is_buy else tp_p + slippage_usd
                    pnl_per_oz = (exit_price - entry_p) if is_buy else (entry_p - exit_price)
                    final_pnl = (pnl_per_oz * open_trade["lots"] * 100.0) + open_trade["banked_pnl"]
                    balance += (pnl_per_oz * open_trade["lots"] * 100.0)
                    equity = balance
                    pnl_r = final_pnl / (open_trade["risk_money"] + 1e-9)

                    trades.append({
                        "setup": open_trade["setup"].value,
                        "direction": open_trade["direction"].value,
                        "entry": entry_p, "exit": exit_price,
                        "sl": open_trade["initial_sl"], "tp": tp_p,
                        "lots": open_trade["initial_lots"],
                        "pnl_usd": final_pnl, "pnl_r": pnl_r,
                        "bars_held": open_trade["bars_held"],
                        "outcome": "WIN",
                        "exit_reason": "TAKE_PROFIT"
                    })
                    open_trade = None

                # E. Time Stop (6 hours / 72 M5 bars)
                elif open_trade is not None and open_trade["bars_held"] >= 72:
                    current_r = ((row["close"] - entry_p) if is_buy else (entry_p - row["close"])) / risk_dist
                    if current_r < 0.5:
                        exit_price = row["close"]
                        pnl_per_oz = (exit_price - entry_p) if is_buy else (entry_p - exit_price)
                        final_pnl = (pnl_per_oz * open_trade["lots"] * 100.0) + open_trade["banked_pnl"]
                        balance += (pnl_per_oz * open_trade["lots"] * 100.0)
                        equity = balance
                        pnl_r = final_pnl / (open_trade["risk_money"] + 1e-9)

                        trades.append({
                            "setup": open_trade["setup"].value,
                            "direction": open_trade["direction"].value,
                            "entry": entry_p, "exit": exit_price,
                            "sl": open_trade["initial_sl"], "tp": tp_p,
                            "lots": open_trade["initial_lots"],
                            "pnl_usd": final_pnl, "pnl_r": pnl_r,
                            "bars_held": open_trade["bars_held"],
                            "outcome": "WIN" if final_pnl > 0 else "LOSS",
                            "exit_reason": "TIME_STOP"
                        })
                        open_trade = None

                # F. Session Close (20:00 GMT)
                elif open_trade is not None and bar_t >= time(20, 0):
                    exit_price = row["close"]
                    pnl_per_oz = (exit_price - entry_p) if is_buy else (entry_p - exit_price)
                    final_pnl = (pnl_per_oz * open_trade["lots"] * 100.0) + open_trade["banked_pnl"]
                    balance += (pnl_per_oz * open_trade["lots"] * 100.0)
                    equity = balance
                    pnl_r = final_pnl / (open_trade["risk_money"] + 1e-9)

                    trades.append({
                        "setup": open_trade["setup"].value,
                        "direction": open_trade["direction"].value,
                        "entry": entry_p, "exit": exit_price,
                        "sl": open_trade["initial_sl"], "tp": tp_p,
                        "lots": open_trade["initial_lots"],
                        "pnl_usd": final_pnl, "pnl_r": pnl_r,
                        "bars_held": open_trade["bars_held"],
                        "outcome": "WIN" if final_pnl > 0 else "LOSS",
                        "exit_reason": "SESSION_FLATTEN"
                    })
                    open_trade = None

            # 4. Entry Evaluation (if no open trade and trades remaining today)
            if open_trade is None and daily_trades_taken < self.config.risk.MAX_TRADES_PER_DAY:
                if asian_range and asian_range.is_valid:
                    sub_m5 = df_m5.iloc[:idx+1]
                    sub_h1 = df_h1[df_h1["time"] <= bar_time]
                    sub_m15 = df_m15[df_m15["time"] <= bar_time]

                    # Setup B Check (07:45 - 10:30 GMT)
                    if time(7, 45) <= bar_t <= time(10, 30) and not setup_b_fired_today:
                        sig_b = self.setup_b.evaluate(sub_m5, sub_h1, asian_range.high, asian_range.low)
                        if sig_b:
                            setup_b_fired_today = True
                            open_trade = self._execute_simulated_trade(
                                sig_b, sub_m5, sub_m15, sub_h1, asian_range, equity, spread_usd, slippage_usd
                            )
                            if open_trade:
                                daily_trades_taken += 1

                    # Setup A Check (08:00 - 11:30 and 13:00 - 16:30 GMT)
                    w1 = time(8, 0) <= bar_t <= time(11, 30)
                    w2 = time(13, 0) <= bar_t <= time(16, 30)
                    if (w1 or w2) and not setup_a_fired_today and open_trade is None:
                        sig_a = self.setup_a.evaluate(sub_m15, sub_h1, asian_range.high, asian_range.low)
                        if sig_a:
                            setup_a_fired_today = True
                            open_trade = self._execute_simulated_trade(
                                sig_a, sub_m5, sub_m15, sub_h1, asian_range, equity, spread_usd, slippage_usd
                            )
                            if open_trade:
                                daily_trades_taken += 1

            if equity > peak_equity:
                peak_equity = equity

        # Calculate Summary Metrics
        return self._calculate_metrics(trades, initial_balance, balance, peak_equity)

    def _execute_simulated_trade(self, signal: TradeSignal, df_m5, df_m15, df_h1,
                                 asian_range, equity: float, spread: float, slippage: float) -> Optional[Dict[str, Any]]:
        # Feature extraction and AI meta-labeling filter
        features = FeatureExtractor.extract_features(
            df_m5, df_m15, df_h1, asian_range.high, asian_range.low, spread
        )
        allowed, p_win, risk_mult = self.meta_labeler.filter_trade(features)
        if not allowed:
            return None

        # Position Sizing
        effective_risk = self.config.risk.RISK_PER_TRADE_PERCENT * risk_mult
        lots, risk_money = self.position_sizer.calculate_lots(
            equity=equity,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            tick_size=0.01,
            tick_value=1.00,
            risk_pct_override=effective_risk
        )
        if lots <= 0:
            return None

        # Apply spread and slippage to entry
        is_buy = (signal.direction == SignalDirection.BUY)
        real_entry = signal.entry_price + (spread / 2.0) + slippage if is_buy else signal.entry_price - (spread / 2.0) - slippage

        return {
            "setup": signal.setup_type,
            "direction": signal.direction,
            "entry_price": real_entry,
            "sl": signal.stop_loss,
            "initial_sl": signal.stop_loss,
            "tp": signal.take_profit,
            "lots": lots,
            "initial_lots": lots,
            "risk_dist": abs(real_entry - signal.stop_loss),
            "risk_money": risk_money,
            "best_price": real_entry,
            "is_breakeven": False,
            "is_partial_closed": False,
            "banked_pnl": 0.0,
            "bars_held": 0
        }

    def _calculate_metrics(self, trades: List[Dict], initial: float, final: float, peak: float) -> Dict[str, Any]:
        total_trades = len(trades)
        if total_trades == 0:
            return {
                "total_trades": 0, "net_profit_usd": 0.0, "return_pct": 0.0,
                "win_rate_pct": 0.0, "profit_factor": 0.0, "expectancy_r": 0.0
            }

        wins = [t for t in trades if t["pnl_usd"] > 0]
        losses = [t for t in trades if t["pnl_usd"] <= 0]

        gross_profit = sum(t["pnl_usd"] for t in wins)
        gross_loss = abs(sum(t["pnl_usd"] for t in losses))

        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        win_rate = (len(wins) / total_trades) * 100.0
        net_profit = final - initial
        return_pct = (net_profit / initial) * 100.0
        expectancy_r = sum(t["pnl_r"] for t in trades) / total_trades

        # Drawdown computation
        equity_curve = [initial]
        running = initial
        for t in trades:
            running += t["pnl_usd"]
            equity_curve.append(running)

        peaks = np.maximum.accumulate(equity_curve)
        dds = (peaks - equity_curve) / peaks * 100.0
        max_drawdown_pct = float(np.max(dds))

        recovery_factor = (net_profit / (initial * (max_drawdown_pct / 100.0) + 1e-9)) if max_drawdown_pct > 0 else 99.0

        return {
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy_r": round(expectancy_r, 2),
            "net_profit_usd": round(net_profit, 2),
            "return_pct": round(return_pct, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "recovery_factor": round(recovery_factor, 2),
            "trades": trades
        }
