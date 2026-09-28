"""
Strategy data models for orders and signals.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SignalDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"


class SetupType(Enum):
    SETUP_A = "SETUP_A"  # Trend Breakout
    SETUP_B = "SETUP_B"  # Liquidity Sweep & Reclaim


@dataclass
class TradeSignal:
    direction: SignalDirection
    setup_type: SetupType
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_r: float
    confidence_score: float = 0.50
    rationale: str = ""
