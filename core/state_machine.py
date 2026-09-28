"""
Bot State Machine Architecture.
Implements the 6 formal strategy states defined in Section 9 of the PDF:
IDLE, MEASURING, ARMED, IN_TRADE, NO_TRADE, DONE.
"""

from enum import Enum, auto
import logging

logger = logging.getLogger("StateMachine")


class BotState(Enum):
    IDLE = auto()        # Start of day (00:00 GMT). Reset counters, load news calendar
    MEASURING = auto()   # Inside Asian window (00:00 - 07:00 GMT). Track M5 high/low
    ARMED = auto()       # AsianEnd reached and range valid. Evaluate signals on each closed bar
    IN_TRADE = auto()    # Order filled. Active position management (BE, partial, trail, time stop)
    NO_TRADE = auto()    # Filters fail, daily loss limit hit, or kill switch activated
    DONE = auto()        # Session end reached (17:00 / 20:00 GMT). Positions flattened, log saved


class BotStateMachine:
    def __init__(self):
        self.state = BotState.IDLE
        self.current_trade_count = 0
        self.daily_pnl_usd = 0.0
        self.reason_for_no_trade = ""

    def transition_to(self, new_state: BotState, reason: str = "") -> None:
        if self.state != new_state:
            logger.info(f"State transition: [{self.state.name}] -> [{new_state.name}] | Reason: {reason}")
            self.state = new_state
            if new_state == BotState.NO_TRADE:
                self.reason_for_no_trade = reason

    def reset_day(self) -> None:
        logger.info("New trading day initialized. Resetting counters.")
        self.state = BotState.IDLE
        self.current_trade_count = 0
        self.daily_pnl_usd = 0.0
        self.reason_for_no_trade = ""
