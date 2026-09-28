"""
Pre-Funded Gas Wallet & Graceful Liquidation Engine.
Implements:
1. Gas Threshold Buffer: $20.00 warning threshold alerts user via Telegram.
2. Read-Only Mode: Balance = $0.00 disables opening any new positions.
3. Graceful Liquidation Policy: Never prematurely panic-close active trades when gas hits $0;
   allows open positions to trail and exit naturally via server-side stops.
"""

import os
import json
import logging
from typing import Tuple, Dict, Any
from datetime import datetime, timezone
from telemetry.telegram_bot import TelegramBot

logger = logging.getLogger("GasWallet")


class GasWallet:
    def __init__(self,
                 wallet_file: str = "data/gas_wallet.json",
                 telegram_bot: Optional[TelegramBot] = None,
                 warning_threshold_usd: float = 20.00):
        self.wallet_file = wallet_file
        self.telegram = telegram_bot
        self.warning_threshold_usd = warning_threshold_usd
        self.balance_usd = 0.0
        self.total_deposited_usd = 0.0
        self.total_deducted_usd = 0.0
        self.is_graceful_disconnect_active = False
        os.makedirs(os.path.dirname(self.wallet_file), exist_ok=True)
        self._load_wallet()

    def _load_wallet(self) -> None:
        if os.path.exists(self.wallet_file):
            try:
                with open(self.wallet_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.balance_usd = float(data.get("balance_usd", 0.0))
                self.total_deposited_usd = float(data.get("total_deposited_usd", 0.0))
                self.total_deducted_usd = float(data.get("total_deducted_usd", 0.0))
                self._update_state()
            except Exception as e:
                logger.error(f"Error loading gas wallet file: {e}")
        else:
            # Default pre-funded demo buffer
            self.balance_usd = 100.00
            self.total_deposited_usd = 100.00
            self.save_wallet()

    def save_wallet(self) -> None:
        try:
            payload = {
                "balance_usd": round(self.balance_usd, 2),
                "total_deposited_usd": round(self.total_deposited_usd, 2),
                "total_deducted_usd": round(self.total_deducted_usd, 2),
                "status": self.get_status(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(self.wallet_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving gas wallet: {e}")

    def _update_state(self) -> None:
        if self.balance_usd <= 0.0:
            self.is_graceful_disconnect_active = True
        else:
            self.is_graceful_disconnect_active = False

    def get_status(self) -> str:
        if self.balance_usd <= 0.0:
            return "READ_ONLY_GRACEFUL_DISCONNECT"
        elif self.balance_usd <= self.warning_threshold_usd:
            return "LOW_GAS_WARNING"
        return "ACTIVE"

    def deposit(self, amount_usd: float) -> float:
        """Top up gas wallet."""
        if amount_usd > 0:
            self.balance_usd += amount_usd
            self.total_deposited_usd += amount_usd
            self._update_state()
            self.save_wallet()
            logger.info(f"Gas Wallet Top-Up: +${amount_usd:.2f} | New Balance: ${self.balance_usd:.2f}")
        return self.balance_usd

    def deduct_fee(self, fee_usd: float) -> Tuple[bool, float, str]:
        """Deducts performance fee and checks threshold policies."""
        if fee_usd <= 0.0:
            return True, self.balance_usd, "No fee to deduct."

        self.balance_usd = max(0.0, self.balance_usd - fee_usd)
        self.total_deducted_usd += fee_usd
        self._update_state()
        self.save_wallet()

        logger.info(f"Gas Wallet Deducted: -${fee_usd:.2f} | Remaining: ${self.balance_usd:.2f}")

        # Check thresholds
        if self.balance_usd <= 0.0:
            msg = f"[GAS-WALLET] Gas balance reached $0.00! Entering READ-ONLY mode (Graceful Disconnect activated)."
            logger.critical(msg)
            if self.telegram and self.telegram.is_enabled:
                self.telegram.send_message(f"🚨 *GAS DEPLETED ($0.00)*: Trading switched to Read-Only mode. Active trades will trail to completion. Please top up your gas wallet.")
            return False, self.balance_usd, msg

        elif self.balance_usd <= self.warning_threshold_usd:
            msg = f"[GAS-WALLET] Low Gas Warning: ${self.balance_usd:.2f} remaining (Threshold: ${self.warning_threshold_usd:.2f})."
            logger.warning(msg)
            if self.telegram and self.telegram.is_enabled:
                self.telegram.send_message(f"⚠️ *LOW GAS WARNING*: Balance is ${self.balance_usd:.2f}. Please top up to prevent graceful trade interruption.")
            return True, self.balance_usd, msg

        return True, self.balance_usd, "Fee deducted successfully."

    def can_open_new_trade(self) -> Tuple[bool, str]:
        """
        Graceful Liquidation Policy:
        Blocks new trade submission if gas wallet is empty ($0.00).
        """
        if self.balance_usd <= 0.0:
            return False, "Graceful Disconnect Active: Gas wallet balance is $0.00. No new trades allowed."
        return True, "Gas wallet funded."

    def allows_position_management(self) -> bool:
        """
        Graceful Liquidation Policy:
        Always returns True to allow existing open trades to be managed to completion (Trailing Stop / TP / SL).
        """
        return True
