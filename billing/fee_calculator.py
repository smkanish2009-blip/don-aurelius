"""
Institutional Financial & Fee Calculation Engine.
Implements:
1. High-Water Mark (HWM) Reset Policy: Fees assessed strictly on net new profits above peak balance.
2. Manual Transaction Exclusion Policy: Filters orders by bot magic number; ignores manual trades.
3. Broker Rebate & Swap Adjustment Policy: Net Profit = Gross Profit - Commissions + Swaps.
4. Currency Conversion Policy: Converts foreign account currencies (EUR, GBP, AUD) to USD/USDT at trade closure timestamp.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import MetaTrader5 as mt5

logger = logging.getLogger("FeeCalculator")


class FeeCalculator:
    def __init__(self,
                 hwm_state_file: str = "data/hwm_state.json",
                 performance_fee_pct: float = 20.0,
                 bot_magic_number: int = 260925):
        self.hwm_state_file = hwm_state_file
        self.performance_fee_pct = performance_fee_pct
        self.bot_magic_number = bot_magic_number
        self.hwm = 0.0
        self.initial_balance = 0.0
        self.total_fees_collected_usd = 0.0
        os.makedirs(os.path.dirname(self.hwm_state_file), exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if os.path.exists(self.hwm_state_file):
            try:
                with open(self.hwm_state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.hwm = float(data.get("high_water_mark", 0.0))
                self.initial_balance = float(data.get("initial_balance", 0.0))
                self.total_fees_collected_usd = float(data.get("total_fees_collected_usd", 0.0))
                logger.info(f"Loaded High-Water Mark state: HWM=${self.hwm:.2f} | Total Fees=${self.total_fees_collected_usd:.2f}")
            except Exception as e:
                logger.error(f"Error loading HWM state file: {e}")

    def save_state(self) -> None:
        try:
            payload = {
                "high_water_mark": round(self.hwm, 2),
                "initial_balance": round(self.initial_balance, 2),
                "total_fees_collected_usd": round(self.total_fees_collected_usd, 2),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(self.hwm_state_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving HWM state file: {e}")

    def initialize_account(self, balance: float) -> None:
        """Initializes account baseline if first run."""
        if self.hwm <= 0.0:
            self.hwm = balance
            self.initial_balance = balance
            self.save_state()
            logger.info(f"Baseline High-Water Mark initialized to ${self.hwm:.2f}")

    def get_currency_conversion_rate(self, account_currency: str) -> float:
        """
        Currency Conversion Policy:
        Pulls exchange rate to convert foreign account currency (EUR, GBP, AUD, etc.) into USD/USDT.
        """
        curr = account_currency.upper().strip()
        if curr in ("USD", "USDT"):
            return 1.0

        pair_direct = f"{curr}USD"
        tick = mt5.symbol_info_tick(pair_direct)
        if tick and tick.bid > 0:
            return float(tick.bid)

        pair_inverse = f"USD{curr}"
        tick_inv = mt5.symbol_info_tick(pair_inverse)
        if tick_inv and tick_inv.ask > 0:
            return 1.0 / float(tick_inv.ask)

        logger.warning(f"Could not fetch live conversion for {curr}. Defaulting to 1.0.")
        return 1.0

    def process_closed_deal(self,
                            deal_magic: int,
                            deal_profit: float,
                            deal_commission: float,
                            deal_swap: float,
                            current_account_balance: float,
                            account_currency: str = "USD") -> Dict[str, Any]:
        """
        Evaluates a closed deal against all 4 financial policies.
        Returns detailed fee assessment dictionary.
        """
        # 1. Manual Transaction Exclusion Policy
        if deal_magic != self.bot_magic_number:
            logger.info(f"Deal with magic #{deal_magic} excluded (Manual or 3rd-party order).")
            return {
                "is_bot_trade": False,
                "reason": f"Excluded: Magic #{deal_magic} does not match bot magic #{self.bot_magic_number}",
                "net_profit_account_ccy": 0.0,
                "net_profit_usd": 0.0,
                "taxable_profit_usd": 0.0,
                "fee_charged_usd": 0.0,
                "hwm_before": self.hwm,
                "hwm_after": self.hwm,
                "hwm_reset": False
            }

        # 2. Broker Rebate & Swap Adjustment Policy
        # Net Profit = Gross Profit - Commissions + Swaps
        # Commissions in MT5 are typically negative expenses; we ensure costs are properly subtracted
        commission_cost = abs(float(deal_commission))
        swap_val = float(deal_swap)
        net_profit_raw = float(deal_profit) - commission_cost + swap_val

        # 3. Currency Conversion Policy
        fx_rate = self.get_currency_conversion_rate(account_currency)
        net_profit_usd = round(net_profit_raw * fx_rate, 2)
        balance_usd = round(current_account_balance * fx_rate, 2)

        # 4. High-Water Mark (HWM) Reset Policy
        hwm_before = self.hwm
        taxable_profit_usd = 0.0
        fee_charged_usd = 0.0
        hwm_reset = False

        if balance_usd > self.hwm:
            # Account printed a new all-time high!
            # Only tax the net delta above previous peak
            delta_above_hwm = balance_usd - self.hwm
            taxable_profit_usd = min(net_profit_usd, delta_above_hwm)
            if taxable_profit_usd > 0.0:
                fee_charged_usd = round(taxable_profit_usd * (self.performance_fee_pct / 100.0), 2)
                self.total_fees_collected_usd += fee_charged_usd
                self.hwm = balance_usd
                hwm_reset = True
                self.save_state()
                logger.info(f"[FEE-CALCULATOR] NEW HIGH-WATER MARK: ${self.hwm:.2f}! "
                            f"Taxable Net Profit: ${taxable_profit_usd:.2f} | Fee Collected: ${fee_charged_usd:.2f}")
            else:
                self.hwm = balance_usd
                self.save_state()
        else:
            logger.info(f"[FEE-CALCULATOR] Account Balance (${balance_usd:.2f}) <= HWM (${self.hwm:.2f}). "
                        f"Zero fee charged during drawdown recovery.")

        return {
            "is_bot_trade": True,
            "reason": "Bot trade processed successfully",
            "gross_profit_raw": deal_profit,
            "commission_cost": commission_cost,
            "swap": swap_val,
            "net_profit_account_ccy": round(net_profit_raw, 2),
            "fx_rate": fx_rate,
            "net_profit_usd": net_profit_usd,
            "taxable_profit_usd": round(taxable_profit_usd, 2),
            "fee_charged_usd": fee_charged_usd,
            "hwm_before": hwm_before,
            "hwm_after": self.hwm,
            "hwm_reset": hwm_reset
        }
