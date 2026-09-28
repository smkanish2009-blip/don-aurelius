"""
Account-Level Risk Management & Kill Switches.
Enforces daily loss cap (2%), peak equity drawdown kill-switch (8%),
consecutive loss risk halving, and maximum daily trade limits.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Tuple
from config.settings import RiskParameters

logger = logging.getLogger("RiskManager")


class RiskManager:
    # Unchangeable Institutional Hard Policy Limits
    HARD_MAX_DAILY_DRAWDOWN_PCT: float = 5.0
    HARD_MAX_TOTAL_DRAWDOWN_PCT: float = 10.0

    def __init__(self, risk_params: RiskParameters):
        self.params = risk_params
        self.peak_equity: float = 0.0
        self.day_start_equity: float = 0.0
        self.daily_trades_taken: int = 0
        self.consecutive_losses: int = 0
        self.is_daily_limit_hit: bool = False
        self.is_kill_switch_activated: bool = False
        self.lockout_until: float = 0.0
        self.is_graceful_disconnect: bool = False

    def on_new_day(self, current_equity: float) -> None:
        """Initializes account baseline at 00:00 GMT."""
        self.day_start_equity = current_equity
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        self.daily_trades_taken = 0
        self.is_daily_limit_hit = False
        logger.info(f"New day initialized: Starting Equity=${self.day_start_equity:.2f} | Peak=${self.peak_equity:.2f}")

    def set_graceful_disconnect(self, active: bool) -> None:
        """Graceful Liquidation: Halts opening new trades while allowing active trades to exit."""
        self.is_graceful_disconnect = active
        if active:
            logger.warning("[RISK-MANAGER] Graceful Disconnect activated: No new trades allowed.")

    def update_equity(self, current_equity: float) -> Tuple[bool, str]:
        """
        Updates live equity, tracking peak equity and monitoring kill-switches.
        Returns: (is_blocked: bool, alert_message: str)
        """
        if current_equity is None or current_equity <= 100.0:
            return False, ""  # Guard against disconnected/zero/invalid equity

        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        # 1. Check Max Drawdown Kill Switch (Unchangeable Hard 10% or configured limit)
        effective_max_dd = min(self.HARD_MAX_TOTAL_DRAWDOWN_PCT, getattr(self.params, "MAX_DRAWDOWN_KILL_PERCENT", 8.0))
        if self.peak_equity > 0:
            dd_pct = ((self.peak_equity - current_equity) / self.peak_equity) * 100.0
            if dd_pct >= effective_max_dd:
                self.is_kill_switch_activated = True
                self.lockout_until = time.time() + 86400.0  # 24-hour lockout
                msg = (f"[RISK-MANAGER] CRITICAL: Hard Total Drawdown kill-switch triggered! Drawdown is {dd_pct:.2f}% "
                       f"(Hard Limit: {effective_max_dd}%). Positions flattened. Locked for 24 hours.")
                logger.critical(msg)
                return True, msg

        # 2. Check Daily Loss Limit (Unchangeable Hard 5% or configured limit)
        effective_daily_limit = min(self.HARD_MAX_DAILY_DRAWDOWN_PCT, getattr(self.params, "DAILY_LOSS_LIMIT_PERCENT", 2.0))
        if self.day_start_equity > 0:
            daily_loss_pct = ((self.day_start_equity - current_equity) / self.day_start_equity) * 100.0
            if daily_loss_pct >= effective_daily_limit:
                self.is_daily_limit_hit = True
                self.lockout_until = time.time() + 86400.0  # 24-hour lockout
                msg = (f"[RISK-MANAGER] WARNING: Hard Daily Drawdown breached! Loss is {daily_loss_pct:.2f}% "
                       f"(Hard Limit: {effective_daily_limit}%). Trading locked for 24 hours.")
                logger.warning(msg)
                return True, msg

        return False, ""

    def can_open_trade(self) -> Tuple[bool, str]:
        """Verifies if the bot is allowed to open a new trade today."""
        now = time.time()
        if now < self.lockout_until:
            rem_hours = (self.lockout_until - now) / 3600.0
            return False, f"Hard Drawdown 24-Hour Lockout Active: {rem_hours:.1f} hours remaining."
        if self.is_graceful_disconnect:
            return False, "Graceful Disconnect Active: Gas wallet is depleted ($0.00). New entries blocked."
        if self.is_kill_switch_activated:
            return False, "Max Drawdown Kill Switch is active."
        if self.is_daily_limit_hit:
            return False, "Daily loss limit has been breached."
        if self.daily_trades_taken >= self.params.MAX_TRADES_PER_DAY:
            return False, f"Maximum daily trade limit ({self.params.MAX_TRADES_PER_DAY}) reached."
        return True, "Risk checks passed."

    def get_effective_risk_pct(self) -> float:
        """Halves risk percentage if consecutive losses >= 3."""
        base_risk = self.params.RISK_PER_TRADE_PERCENT
        if self.consecutive_losses >= self.params.CONSECUTIVE_LOSS_HALVE_COUNT:
            reduced = base_risk * 0.50
            logger.info(f"Risk halved due to {self.consecutive_losses} consecutive losses: {base_risk}% -> {reduced}%")
            return reduced
        return base_risk

    def record_trade_result(self, profit_usd: float) -> None:
        """Updates win/loss streak counters."""
        self.daily_trades_taken += 1
        if profit_usd < 0:
            self.consecutive_losses += 1
            logger.info(f"Trade Loss recorded: ${profit_usd:.2f}. Consecutive losses: {self.consecutive_losses}")
        else:
            self.consecutive_losses = 0
            logger.info(f"Trade Win recorded: +${profit_usd:.2f}. Consecutive loss counter reset.")
