"""
TITAN-X War Room: Multi-Agent Consensus Council & Dynamic Kelly Sizing.
Orchestrates:
1. Agent HAWK (Macro & Intermarket Regime)
2. Agent RADAR (OSINT & Real-time Sentiment Velocity)
3. Agent PREDATOR (Institutional Order Flow, FVGs & Sweeps)
4. Agent INQUISITOR (Red-Team Adversarial Stress Tester)

Enforces the 3/4 Supermajority Consensus Protocol and fractional Kelly risk sizing.
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple

from engine.strategy import JarvisStrategyEngine
from .agent_radar import AgentRadar, SentimentSnapshot
from .agent_predator import AgentPredator
from .agent_inquisitor import AgentInquisitor, StressTestVerdict
from .economic_calendar import EconomicCalendarShield

logger = logging.getLogger("TitanX.WarRoom")


@dataclass
class CouncilVote:
    """Individual agent ballot submitted to the Council."""
    agent_name: str
    vote: str           # "BUY", "SELL", "NEUTRAL", "VETO", "APPROVE"
    confidence: float   # 0.0 to 1.0
    thesis: str


@dataclass
class ConsensusVerdict:
    """Supreme ruling issued by the TITAN-X Consensus Council."""
    consensus_achieved: bool
    final_decision: str      # "BUY", "SELL", "HOLD"
    supermajority_count: int
    supermajority_ratio: str  # e.g., "3/4" or "4/4"
    recommended_risk_pct: float
    kelly_fraction: float
    veto_triggered: bool
    votes: Dict[str, CouncilVote] = field(default_factory=dict)
    rationale: str = ""
    telemetry: Dict[str, Any] = field(default_factory=dict)


class TitanWarRoom:
    """
    The High Council of TITAN-X.
    No trade ever executes without passing the 3/4 Supermajority Consensus
    and clearing Agent Inquisitor's adversarial gauntlet.
    """

    def __init__(
        self,
        hawk: Optional[JarvisStrategyEngine] = None,
        radar: Optional[AgentRadar] = None,
        predator: Optional[AgentPredator] = None,
        inquisitor: Optional[AgentInquisitor] = None,
        base_risk_pct: float = 0.01,
        kelly_fraction_multiplier: float = 0.25,  # Quarter-Kelly for institutional safety
        min_risk_pct: float = 0.005,             # 0.5% floor
        max_risk_pct: float = 0.015              # 1.5% ceiling
    ):
        self.hawk = hawk or JarvisStrategyEngine()
        self.radar = radar or AgentRadar()
        self.predator = predator or AgentPredator()
        self.inquisitor = inquisitor or AgentInquisitor()

        self.base_risk_pct = base_risk_pct
        self.kelly_fraction_multiplier = kelly_fraction_multiplier
        self.min_risk_pct = min_risk_pct
        self.max_risk_pct = max_risk_pct

    def calculate_fractional_kelly(
        self,
        win_probability: float,
        payout_ratio: float = 3.0
    ) -> Tuple[float, float]:
        """
        Calculates Fractional Kelly Criterion:
        f* = (p * (b + 1) - 1) / b
        Scaled by kelly_fraction_multiplier (Quarter-Kelly) to prevent drawdown ruin.
        Returns: (fractional_kelly, recommended_account_risk_pct)
        """
        b = max(1.0, payout_ratio)
        p = min(0.95, max(0.05, win_probability))
        q = 1.0 - p

        full_kelly = (b * p - q) / b
        if full_kelly <= 0:
            return 0.0, self.min_risk_pct

        fractional_k = full_kelly * self.kelly_fraction_multiplier

        # Scale base risk proportional to fractional Kelly
        # e.g., if Fractional K is ~0.10, recommended risk adjusts around base_risk_pct
        risk_adjustment = 0.75 + (fractional_k * 2.5)
        recommended_risk = self.base_risk_pct * risk_adjustment
        clamped_risk = round(min(self.max_risk_pct, max(self.min_risk_pct, recommended_risk)), 4)

        return round(fractional_k, 4), clamped_risk

    def convene_council(
        self,
        xau_df: pd.DataFrame,
        dxy_df: Optional[pd.DataFrame] = None,
        us10y_df: Optional[pd.DataFrame] = None,
        current_spread_pips: float = 1.8,
        simulated_headlines: Optional[List[str]] = None
    ) -> ConsensusVerdict:
        """
        Executes the full Council Consensus Protocol:
        1. Agent HAWK analyzes trend & macro filters
        2. Agent RADAR measures real-time sentiment velocity & geopolitical news
        3. Agent PREDATOR hunts institutional liquidity sweeps & Fair Value Gaps
        4. Agent INQUISITOR stress-tests the emergent direction
        5. Enforces the 3/4 Supermajority Protocol
        """
        votes: Dict[str, CouncilVote] = {}

        if len(xau_df) < 20 or 'close' not in xau_df:
            return ConsensusVerdict(
                consensus_achieved=False,
                final_decision="HOLD",
                supermajority_count=0,
                supermajority_ratio="0/4",
                recommended_risk_pct=0.0,
                kelly_fraction=0.0,
                veto_triggered=False,
                rationale="Insufficient bar data for Council consensus."
            )

        current_price = float(xau_df['close'].iloc[-1])

        # -------------------------------------------------------------
        # BALLOT 1: AGENT HAWK (Macro & Intermarket Regime)
        # -------------------------------------------------------------
        hawk_signal, atr = self.hawk.evaluate_generation_signal(xau_df, dxy_df, us10y_df)
        hawk_vote = "BUY" if hawk_signal == "BUY" else ("SELL" if hawk_signal == "SELL" else "NEUTRAL")
        hawk_conf = 0.70 if hawk_vote != "NEUTRAL" else 0.50
        votes["HAWK"] = CouncilVote(
            agent_name="HAWK",
            vote=hawk_vote,
            confidence=hawk_conf,
            thesis=f"Macro regime: {hawk_signal} (ATR: ${atr:.2f})"
        )

        # -------------------------------------------------------------
        # BALLOT 2: AGENT RADAR (OSINT Sentiment Velocity)
        # -------------------------------------------------------------
        radar_snap = self.radar.poll_and_evaluate(simulated_headlines=simulated_headlines)
        radar_vote = "BUY" if radar_snap.gold_bias == "BULLISH" else ("SELL" if radar_snap.gold_bias == "BEARISH" else "NEUTRAL")
        votes["RADAR"] = CouncilVote(
            agent_name="RADAR",
            vote=radar_vote,
            confidence=radar_snap.confidence,
            thesis=f"News sentiment score: {radar_snap.raw_score:+.2f}, Velocity: {radar_snap.sentiment_velocity:+.3f}/min"
        )

        # -------------------------------------------------------------
        # BALLOT 3: AGENT PREDATOR (Institutional Order Flow & Sweeps)
        # -------------------------------------------------------------
        order_flow = self.predator.evaluate_order_flow(xau_df)
        predator_bias = order_flow.get("bias", "NEUTRAL")
        predator_vote = "BUY" if predator_bias == "BULLISH" else ("SELL" if predator_bias == "BEARISH" else "NEUTRAL")
        predator_conf = order_flow.get("confidence", 0.50)
        active_fvgs = self.predator.detect_fair_value_gaps(xau_df)
        votes["PREDATOR"] = CouncilVote(
            agent_name="PREDATOR",
            vote=predator_vote,
            confidence=predator_conf,
            thesis=f"Order flow: {predator_bias} (Sweeps: {order_flow.get('sweep_detected')}, FVGs: {len(active_fvgs)})"
        )

        # -------------------------------------------------------------
        # DIRECTIONAL TALLY & PROPOSAL FORMATION
        # -------------------------------------------------------------
        prelim_buy_votes = sum(1 for v in [hawk_vote, radar_vote, predator_vote] if v == "BUY")
        prelim_sell_votes = sum(1 for v in [hawk_vote, radar_vote, predator_vote] if v == "SELL")

        proposed_direction = "HOLD"
        if prelim_buy_votes >= 2 and prelim_buy_votes > prelim_sell_votes:
            proposed_direction = "BUY"
        elif prelim_sell_votes >= 2 and prelim_sell_votes > prelim_buy_votes:
            proposed_direction = "SELL"

        # Calculate standard target distances for stress testing
        sl_calculated_pips = max(15, int((atr * 2.5) * 10))
        tp_calculated_pips = int(sl_calculated_pips * 3.0)

        # -------------------------------------------------------------
        # BALLOT 4: AGENT INQUISITOR (Red-Team Adversarial Gauntlet)
        # -------------------------------------------------------------
        if proposed_direction in ["BUY", "SELL"]:
            inquisitor_verdict = self.inquisitor.stress_test_proposal(
                df=xau_df,
                proposed_direction=proposed_direction,
                entry_price=current_price,
                sl_pips=sl_calculated_pips,
                tp_pips=tp_calculated_pips,
                current_spread_pips=current_spread_pips,
                active_fvgs=active_fvgs
            )

            if inquisitor_verdict.hard_veto or not inquisitor_verdict.approved:
                inquisitor_vote = "VETO"
                inquisitor_thesis = (
                    f"VETO ISSUED: Risk score {inquisitor_verdict.risk_score:.2f}. "
                    f"Reasons: {'; '.join(inquisitor_verdict.veto_reasons)}"
                )
            else:
                # Approves proposed direction
                inquisitor_vote = proposed_direction
                inquisitor_thesis = f"APPROVED: Trade cleared red-team gauntlet (Risk: {inquisitor_verdict.risk_score:.2f})"
        else:
            inquisitor_verdict = StressTestVerdict(approved=True, hard_veto=False, risk_score=0.0)
            inquisitor_vote = "NEUTRAL"
            inquisitor_thesis = "No directional trade proposed to stress test."

        votes["INQUISITOR"] = CouncilVote(
            agent_name="INQUISITOR",
            vote=inquisitor_vote,
            confidence=round(1.0 - inquisitor_verdict.risk_score, 2),
            thesis=inquisitor_thesis
        )

        # -------------------------------------------------------------
        # 3/4 SUPERMAJORITY DECISION MATRIX
        # -------------------------------------------------------------
        buy_total = sum(1 for v in votes.values() if v.vote == "BUY")
        sell_total = sum(1 for v in votes.values() if v.vote == "SELL")
        veto_present = any(v.vote == "VETO" for v in votes.values()) or inquisitor_verdict.hard_veto

        consensus_achieved = False
        final_decision = "HOLD"
        supermajority_count = 0
        supermajority_ratio = "0/4"
        recommended_risk = 0.0
        fractional_k = 0.0

        if veto_present:
            consensus_achieved = False
            final_decision = "HOLD"
            supermajority_count = max(buy_total, sell_total)
            supermajority_ratio = f"{supermajority_count}/4"
            rationale = f"TRADE VETOED BY INQUISITOR. {inquisitor_thesis}"
        elif buy_total >= 3:
            consensus_achieved = True
            final_decision = "BUY"
            supermajority_count = buy_total
            supermajority_ratio = f"{buy_total}/4"
            win_prob = 0.78 if buy_total == 4 else 0.68
            fractional_k, recommended_risk = self.calculate_fractional_kelly(win_prob, payout_ratio=3.0)
            rationale = (
                f"SUPERMAJORITY CONSENSUS REACHED ({buy_total}/4). "
                f"HAWK: {votes['HAWK'].vote} | RADAR: {votes['RADAR'].vote} | "
                f"PREDATOR: {votes['PREDATOR'].vote} | INQUISITOR: {votes['INQUISITOR'].vote}."
            )
        elif sell_total >= 3:
            consensus_achieved = True
            final_decision = "SELL"
            supermajority_count = sell_total
            supermajority_ratio = f"{sell_total}/4"
            win_prob = 0.78 if sell_total == 4 else 0.68
            fractional_k, recommended_risk = self.calculate_fractional_kelly(win_prob, payout_ratio=3.0)
            rationale = (
                f"SUPERMAJORITY CONSENSUS REACHED ({sell_total}/4). "
                f"HAWK: {votes['HAWK'].vote} | RADAR: {votes['RADAR'].vote} | "
                f"PREDATOR: {votes['PREDATOR'].vote} | INQUISITOR: {votes['INQUISITOR'].vote}."
            )
        else:
            final_decision = "HOLD"
            supermajority_count = max(buy_total, sell_total)
            supermajority_ratio = f"{supermajority_count}/4"
            rationale = (
                f"Consensus failed: Insufficient supermajority ({supermajority_count}/4 agreeing). "
                f"Need 3/4 alignment to fire."
            )

        logger.info(f"[WAR-ROOM] {supermajority_ratio} Consensus -> {final_decision}. {rationale}")

        return ConsensusVerdict(
            consensus_achieved=consensus_achieved,
            final_decision=final_decision,
            supermajority_count=supermajority_count,
            supermajority_ratio=supermajority_ratio,
            recommended_risk_pct=recommended_risk,
            kelly_fraction=fractional_k,
            veto_triggered=veto_present,
            votes=votes,
            rationale=rationale,
            telemetry={
                "current_price": current_price,
                "atr": round(atr, 2),
                "sl_pips": sl_calculated_pips,
                "tp_pips": tp_calculated_pips,
                "spread_pips": current_spread_pips
            }
        )
