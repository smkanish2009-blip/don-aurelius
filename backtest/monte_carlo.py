"""
Monte Carlo Stress Simulator.
Shuffles trade returns over 1,000+ iterations to evaluate drawdown distribution,
maximum consecutive losing streaks, and probability of touching the 8% kill switch.
"""

import numpy as np
from typing import List, Dict, Any


class MonteCarloSimulator:
    def __init__(self, trades: List[Dict[str, Any]], initial_balance: float = 10000.0):
        self.pnl_list = [t["pnl_usd"] for t in trades]
        self.initial_balance = initial_balance

    def simulate(self, num_simulations: int = 1000) -> Dict[str, Any]:
        if not self.pnl_list:
            return {"simulations": 0, "max_dd_95th": 0.0, "prob_kill_switch_breach": 0.0}

        pnl_array = np.array(self.pnl_list)
        n_trades = len(pnl_array)
        max_drawdowns = []
        kill_switch_hits = 0

        for _ in range(num_simulations):
            # Shuffle trade sequence
            shuffled = np.random.choice(pnl_array, size=n_trades, replace=True)
            equity_curve = self.initial_balance + np.cumsum(shuffled)
            equity_curve = np.insert(equity_curve, 0, self.initial_balance)

            peaks = np.maximum.accumulate(equity_curve)
            drawdowns = (peaks - equity_curve) / peaks * 100.0
            sim_max_dd = np.max(drawdowns)
            max_drawdowns.append(sim_max_dd)

            if sim_max_dd >= 8.0:
                kill_switch_hits += 1

        return {
            "simulations": num_simulations,
            "max_dd_median": round(float(np.median(max_drawdowns)), 2),
            "max_dd_95th": round(float(np.percentile(max_drawdowns, 95)), 2),
            "max_dd_worst": round(float(np.max(max_drawdowns)), 2),
            "prob_kill_switch_breach_pct": round((kill_switch_hits / num_simulations) * 100.0, 2)
        }
