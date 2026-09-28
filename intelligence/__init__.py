"""
TITAN-X Intelligence Module.
Houses:
- Agent HAWK (Intermarket & Macro Regime) via engine.strategy
- Agent RADAR (OSINT & Real-time Sentiment Velocity)
- Agent PREDATOR (Institutional Order Flow, FVGs & Sweeps)
- Agent INQUISITOR (Red-Team Adversarial Stress Tester)
- TitanWarRoom (Autonomous Multi-Agent Consensus Council & Kelly Sizing)
- EconomicCalendarShield (Tier-1 News Embargo Protection)
"""

from .agent_radar import AgentRadar, SentimentSnapshot
from .economic_calendar import EconomicCalendarShield
from .agent_predator import AgentPredator
from .agent_inquisitor import AgentInquisitor, StressTestVerdict
from .war_room import TitanWarRoom, ConsensusVerdict, CouncilVote

__all__ = [
    "AgentRadar",
    "SentimentSnapshot",
    "EconomicCalendarShield",
    "AgentPredator",
    "AgentInquisitor",
    "StressTestVerdict",
    "TitanWarRoom",
    "ConsensusVerdict",
    "CouncilVote",
]
