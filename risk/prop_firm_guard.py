"""
Prop-Firm Compliance & Anti-Disqualification Guard.
Enforces institutional prop-firm rules (FTMO, FundedNext, The5ers, Alpha Capital):
1. 120-Second Minimum Trade Duration: Prevents "toxic tick scalping" / latency arbitrage disqualifications.
2. Hard Single-Order Lot Cap: Clamps orders to maximum allowed contracts (default 5.00 lots).
3. Strict No-Hedging / Unidirectional Enforcement: Never opens opposite positions simultaneously.
4. Daily Profit Consistency Guard: Pauses trading if daily profit hits 45% of challenge target.
"""

import time
import logging
from typing import Dict, List, Tuple, Optional
from config.settings import PropFirmSettings

logger = logging.getLogger("PropFirmGuard")


class PropFirmGuard:
    def __init__(self, settings: Optional[PropFirmSettings] = None):
        self.settings = settings or PropFirmSettings()
        self.trade_open_timestamps: Dict[int, float] = {}  # ticket -> epoch_seconds
        self.daily_closed_profit = 0.0

    def record_trade_opened(self, ticket: int, open_time_sec: Optional[float] = None) -> None:
        """Records position entry timestamp for anti-scalping duration tracking."""
        self.trade_open_timestamps[ticket] = open_time_sec or time.time()
        logger.info(f"[PROP-FIRM] Registered ticket #{ticket} open timestamp for duration compliance.")

    def can_close_position(self, ticket: int, is_hard_stop_loss: bool = False) -> Tuple[bool, str]:
        """
        120-Second Anti-Scalping Policy:
        Prop firms disqualify accounts that close trades in < 60-120 seconds.
        Emergency Stop Loss triggers are exempt to preserve capital.
        """
        if not self.settings.PROP_FIRM_MODE:
            return True, "Prop firm mode inactive."

        if is_hard_stop_loss:
            return True, "Emergency server-side stop loss triggered (exempt from duration check)."

        open_ts = self.trade_open_timestamps.get(ticket)
        if not open_ts:
            return True, "Ticket timestamp not found (allowing exit)."

        elapsed_sec = time.time() - open_ts
        min_duration = self.settings.MIN_TRADE_DURATION_SEC

        if elapsed_sec < min_duration:
            msg = (f"[PROP-FIRM-ANTI-SCALPING] Ticket #{ticket} open for only {elapsed_sec:.1f}s "
                   f"(Minimum required: {min_duration}s). Hold position to prevent HFT scalping violation.")
            logger.warning(msg)
            return False, msg

        return True, f"Trade duration {elapsed_sec:.1f}s satisfies prop-firm rule (> {min_duration}s)."

    def clamp_lot_size(self, proposed_lots: float) -> Tuple[float, str]:
        """
        Hard Single-Order Lot Cap:
        Guarantees that lot size never exceeds prop-firm maximum exposure limits.
        """
        if not self.settings.PROP_FIRM_MODE:
            return proposed_lots, "Standard lot sizing."

        max_lots = self.settings.MAX_SINGLE_ORDER_LOTS
        if proposed_lots > max_lots:
            msg = f"[PROP-FIRM-LOT-CAP] Proposed {proposed_lots:.2f} lots clamped to max cap {max_lots:.2f} lots."
            logger.warning(msg)
            return max_lots, msg

        return proposed_lots, "Lot size within prop-firm limit."

    def validate_no_hedging(self, proposed_direction: str, open_positions: List[Dict]) -> Tuple[bool, str]:
        """
        Strict No-Hedging / Unidirectional Policy:
        Forbids opening Buy and Sell positions simultaneously on the same symbol.
        """
        if not self.settings.PROP_FIRM_MODE or self.settings.ALLOW_HEDGING:
            return True, "Hedging permitted."

        for pos in open_positions:
            # pos type: 0 = Buy, 1 = Sell
            pos_type = pos.get("type", 0) if isinstance(pos, dict) else getattr(pos, "type", 0)
            existing_dir = "BUY" if pos_type == 0 else "SELL"

            if proposed_direction != existing_dir:
                msg = f"[PROP-FIRM-NO-HEDGE] Cannot open {proposed_direction}: Active {existing_dir} position already open."
                logger.warning(msg)
                return False, msg

        return True, "No conflicting opposite positions."

    def check_profit_consistency(self, today_profit: float, challenge_target: float = 10000.0) -> Tuple[bool, str]:
        """
        Consistency Rule Guard:
        Prevents a single day from exceeding 45% of total evaluation target.
        """
        if not self.settings.PROP_FIRM_MODE or challenge_target <= 0:
            return True, "Consistency rule bypassed."

        max_pct = self.settings.CONSISTENCY_MAX_DAILY_PROFIT_PCT
        max_daily_allowed = challenge_target * (max_pct / 100.0)

        if today_profit >= max_daily_allowed:
            msg = (f"[PROP-FIRM-CONSISTENCY] Today's profit (+${today_profit:.2f}) has reached {max_pct}% "
                   f"of target (+${max_daily_allowed:.2f}). Pausing new trades for the day to preserve consistency.")
            logger.warning(msg)
            return False, msg

        return True, "Daily profit within consistency distribution."
