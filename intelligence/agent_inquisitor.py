"""
TITAN-X Agent INQUISITOR (The Red-Team Adversarial AI).
Performs adversarial stress testing against proposed trades.
Actively searches for reasons to VETO trades (Spread blowout, news embargo,
volatility exhaustion, R:R asymmetry, or walking into institutional liquidity traps).
"""

import time
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .economic_calendar import EconomicCalendarShield

logger = logging.getLogger("TitanX.Inquisitor")


@dataclass
class StressTestVerdict:
    """Detailed verdict and forensic vulnerability breakdown from Agent Inquisitor."""
    approved: bool
    hard_veto: bool
    risk_score: float  # 0.0 (safest) to 1.0 (extreme danger)
    veto_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)


class AgentInquisitor:
    """
    Agent INQUISITOR is the supreme skeptic of the TITAN-X council.
    It does not look for profits; it hunts vulnerabilities and kills fragile setups.
    """

    def __init__(
        self,
        max_spread_pips: float = 5.0,
        min_rr_ratio: float = 1.5,
        max_atr_stretch: float = 2.8,
        calendar_shield: Optional[EconomicCalendarShield] = None
    ):
        self.max_spread_pips = max_spread_pips
        self.min_rr_ratio = min_rr_ratio
        self.max_atr_stretch = max_atr_stretch
        self.calendar_shield = calendar_shield or EconomicCalendarShield()
        self._last_log_msg: str = ""
        self._last_log_time: float = 0.0

    def stress_test_proposal(
        self,
        df: pd.DataFrame,
        proposed_direction: str,
        entry_price: float,
        sl_pips: float,
        tp_pips: float,
        current_spread_pips: float = 1.8,
        active_fvgs: Optional[List[Dict[str, Any]]] = None
    ) -> StressTestVerdict:
        """
        Subject the proposed trade to 5 rigorous adversarial trials:
        1. Spread & Execution Slippage Barrier
        2. Tier-1 Economic Event Embargo Barrier
        3. Asymmetric Risk/Reward Ratio Barrier
        4. Overextended Volatility Exhaustion Barrier (Mean Reversion Trap)
        5. Institutional Supply/Demand Trap Barrier (Walking into opposite FVG)
        """
        veto_reasons: List[str] = []
        warnings: List[str] = []
        hard_veto = False
        penalty_score = 0.0

        if proposed_direction not in ["BUY", "SELL"]:
            return StressTestVerdict(
                approved=False,
                hard_veto=True,
                risk_score=1.0,
                veto_reasons=[f"Invalid proposed direction: {proposed_direction}"]
            )

        # -------------------------------------------------------------
        # TRIAL 1: SPREAD & EXECUTION SLIPPAGE BARRIER
        # -------------------------------------------------------------
        if current_spread_pips > self.max_spread_pips:
            hard_veto = True
            reason = (
                f"[INQUISITOR-VETO] Spread blowout: Current spread {current_spread_pips:.1f} pips "
                f"exceeds ceiling {self.max_spread_pips:.1f} pips. High slippage penalty."
            )
            veto_reasons.append(reason)
            penalty_score += 0.40
        elif current_spread_pips > 2.5:
            warnings.append(f"Elevated spread ({current_spread_pips:.1f} pips). Margin buffer squeezed.")
            penalty_score += 0.15

        # -------------------------------------------------------------
        # TRIAL 2: ECONOMIC PROXIMITY EMBARGO BARRIER
        # -------------------------------------------------------------
        embargo_active, embargo_reason = self.calendar_shield.is_embargo_active()
        if embargo_active:
            hard_veto = True
            reason = f"[INQUISITOR-VETO] Economic Event Embargo: {embargo_reason}"
            veto_reasons.append(reason)
            penalty_score += 0.50

        # -------------------------------------------------------------
        # TRIAL 3: ASYMMETRIC RISK/REWARD RATIO BARRIER
        # -------------------------------------------------------------
        if sl_pips <= 0:
            hard_veto = True
            veto_reasons.append("[INQUISITOR-VETO] Stop Loss distance is non-positive.")
            penalty_score += 0.50
        else:
            rr_ratio = tp_pips / sl_pips
            if rr_ratio < self.min_rr_ratio:
                hard_veto = True
                reason = (
                    f"[INQUISITOR-VETO] Unfavorable Risk/Reward ratio: {rr_ratio:.2f}:1 "
                    f"(Minimum acceptable: {self.min_rr_ratio:.1f}:1)."
                )
                veto_reasons.append(reason)
                penalty_score += 0.35

        # -------------------------------------------------------------
        # TRIAL 4: VOLATILITY EXHAUSTION BARRIER (Mean Reversion Trap)
        # -------------------------------------------------------------
        atr = 1.50
        if len(df) >= 20 and 'close' in df:
            closes = df['close'].values
            highs = df['high'].values if 'high' in df else closes
            lows = df['low'].values if 'low' in df else closes

            # 20 EMA calculation
            ema20 = float(pd.Series(closes).ewm(span=20, adjust=False).mean().iloc[-1])

            # 14 ATR calculation
            tr1 = highs[1:] - lows[1:]
            tr2 = np.abs(highs[1:] - closes[:-1])
            tr3 = np.abs(lows[1:] - closes[:-1])
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = float(pd.Series(tr).rolling(14).mean().iloc[-1]) if len(tr) >= 14 else 1.50
            if np.isnan(atr) or atr <= 0:
                atr = 1.50

            distance_from_mean = entry_price - ema20
            atr_stretch = abs(distance_from_mean) / atr

            if proposed_direction == "BUY" and distance_from_mean > (self.max_atr_stretch * atr):
                reason = (
                    f"[INQUISITOR-VETO] Bullish Exhaustion Trap: Price ${entry_price:.2f} is stretched "
                    f"{atr_stretch:.2f}x ATR above 20 EMA (${ema20:.2f}). Chasing high risk top."
                )
                veto_reasons.append(reason)
                hard_veto = True
                penalty_score += 0.30
            elif proposed_direction == "SELL" and distance_from_mean < -(self.max_atr_stretch * atr):
                reason = (
                    f"[INQUISITOR-VETO] Bearish Exhaustion Trap: Price ${entry_price:.2f} is stretched "
                    f"{atr_stretch:.2f}x ATR below 20 EMA (${ema20:.2f}). Selling into oversold bottom."
                )
                veto_reasons.append(reason)
                hard_veto = True
                penalty_score += 0.30
            elif atr_stretch > 2.0:
                warnings.append(f"Price moderately stretched from 20 EMA ({atr_stretch:.1f}x ATR).")
                penalty_score += 0.15

        # -------------------------------------------------------------
        # TRIAL 5: INSTITUTIONAL SUPPLY/DEMAND TRAP (Opposing FVG)
        # -------------------------------------------------------------
        if active_fvgs:
            for fvg in active_fvgs:
                # If BUYing, ensure entry is not right below an unmitigated BEARISH FVG
                # (which serves as heavy institutional resistance)
                if proposed_direction == "BUY" and fvg.get("type") == "BEARISH_FVG":
                    fvg_bottom = fvg.get("bottom", 0.0)
                    if 0 < (fvg_bottom - entry_price) < (atr * 0.5):
                        warnings.append(
                            f"Buying directly into Bearish FVG overhead resistance at ${fvg_bottom:.2f}."
                        )
                        penalty_score += 0.20

                # If SELLing, ensure entry is not right above an unmitigated BULLISH FVG
                # (which serves as strong institutional support)
                elif proposed_direction == "SELL" and fvg.get("type") == "BULLISH_FVG":
                    fvg_top = fvg.get("top", 0.0)
                    if 0 < (entry_price - fvg_top) < (atr * 0.5):
                        warnings.append(
                            f"Selling directly into Bullish FVG floor support at ${fvg_top:.2f}."
                        )
                        penalty_score += 0.20

        # Calculate final risk score
        final_risk_score = min(1.0, max(0.0, penalty_score))
        approved = (not hard_veto) and (final_risk_score < 0.60)

        verdict = StressTestVerdict(
            approved=approved,
            hard_veto=hard_veto,
            risk_score=round(final_risk_score, 2),
            veto_reasons=veto_reasons,
            warnings=warnings,
            telemetry={
                "spread_pips": current_spread_pips,
                "atr": round(atr, 2),
                "proposed_direction": proposed_direction,
                "entry_price": entry_price
            }
        )

        now = time.time()
        if not approved:
            reject_msg = (
                f"[INQUISITOR-REJECT] Trade rejected. Risk: {final_risk_score:.2f} | "
                f"Reasons: {'; '.join(veto_reasons + warnings)}"
            )
            if reject_msg != self._last_log_msg or (now - self._last_log_time) >= 60.0:
                logger.warning(reject_msg)
                self._last_log_msg = reject_msg
                self._last_log_time = now
        else:
            pass_msg = f"[INQUISITOR-PASS] Trade cleared adversarial trials. Risk Score: {final_risk_score:.2f}"
            if pass_msg != self._last_log_msg or (now - self._last_log_time) >= 60.0:
                logger.info(pass_msg)
                self._last_log_msg = pass_msg
                self._last_log_time = now

        return verdict
