"""
Supabase Real-Time Cloud Telemetry Syncer for Don Aurelius.
Bridges local MT5 account telemetry, 4-agent war room consensus, and active trade signals
directly to Supabase Cloud PostgreSQL via high-speed REST endpoints.
No external third-party dependencies required; uses hardened Python stdlib urllib.
"""

import json
import logging
import threading
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from config.credentials import credentials

logger = logging.getLogger("SupabaseSyncer")


class SupabaseSyncer:
    """Thread-safe telemetry and consensus publisher for Supabase Cloud."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = (url or credentials.SUPABASE_URL).rstrip("/")
        # Prefer secret key if available for full database upsert capability
        self.key = (
            key
            or credentials.SUPABASE_SECRET_KEY
            or credentials.SUPABASE_PUBLISHABLE_KEY
        )
        self.is_configured = bool(self.url and self.key)

        if not self.is_configured:
            logger.warning("[SUPABASE] Credentials not configured. Telemetry sync disabled.")
        else:
            logger.info(f"[SUPABASE] Initialized cloud bridge to {self.url}")

    def _headers(self) -> Dict[str, str]:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation"
        }

    def _request(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        if not self.is_configured:
            return None

        target_url = f"{self.url}/rest/v1/{endpoint}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = self._headers()

        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = resp.read().decode("utf-8")
                if data:
                    return json.loads(data)
                return True
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            logger.error(f"[SUPABASE ERROR] {method} {endpoint} failed [{e.code}]: {err_msg}")
            return None
        except Exception as ex:
            logger.error(f"[SUPABASE EXCEPTION] {method} {endpoint}: {ex}")
            return None

    def sync_telemetry(
        self,
        account_number: str = "10434714118",
        balance: float = 100773.18,
        equity: float = 100398.97,
        floating_pnl: float = 0.0,
        realized_profit: float = 773.18,
        margin: float = 106.58,
        free_margin: float = 100292.39,
        open_positions_count: int = 3,
        win_rate: float = 88.4
    ) -> bool:
        """Upserts live account telemetry to public.live_telemetry."""
        payload = {
            "account_number": str(account_number),
            "balance": round(float(balance), 2),
            "equity": round(float(equity), 2),
            "floating_pnl": round(float(floating_pnl), 2),
            "realized_profit": round(float(realized_profit), 2),
            "margin": round(float(margin), 2),
            "free_margin": round(float(free_margin), 2),
            "open_positions_count": int(open_positions_count),
            "win_rate": round(float(win_rate), 2),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Check existing row
        existing = self._request("live_telemetry?select=id&limit=1", method="GET")
        if existing and len(existing) > 0:
            row_id = existing[0].get("id")
            res = self._request(f"live_telemetry?id=eq.{row_id}", method="PATCH", payload=payload)
        else:
            res = self._request("live_telemetry", method="POST", payload=payload)

        return bool(res)

    def sync_consensus(
        self,
        pair: str = "XAUUSD",
        direction: str = "BUY",
        confidence: float = 94.2,
        setup_grade: str = "A+",
        hawk_vote: str = "BUY",
        hawk_reason: str = "DXY -0.32% • Yields Fall",
        radar_vote: str = "BUY",
        radar_reason: str = "Asian Range Swept",
        predator_vote: str = "BUY",
        predator_reason: str = "Bullish FVG Retest",
        inquisitor_vote: str = "PASS",
        inquisitor_reason: str = "Spread 0.12p <= 5.0p Cap",
        entry_zone: str = "2662.50 - 2664.50",
        stop_loss: float = 2658.00,
        take_profit: float = 2678.00
    ) -> bool:
        """Upserts 4-agent consensus matrix to public.agent_consensus."""
        payload = {
            "pair": pair,
            "direction": direction,
            "confidence": round(float(confidence), 1),
            "setup_grade": setup_grade,
            "hawk_vote": hawk_vote,
            "hawk_reason": hawk_reason,
            "radar_vote": radar_vote,
            "radar_reason": radar_reason,
            "predator_vote": predator_vote,
            "predator_reason": predator_reason,
            "inquisitor_vote": inquisitor_vote,
            "inquisitor_reason": inquisitor_reason,
            "entry_zone": entry_zone,
            "stop_loss": round(float(stop_loss), 2),
            "take_profit": round(float(take_profit), 2),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        existing = self._request(f"agent_consensus?pair=eq.{pair}&select=id&limit=1", method="GET")
        if existing and len(existing) > 0:
            row_id = existing[0].get("id")
            res = self._request(f"agent_consensus?id=eq.{row_id}", method="PATCH", payload=payload)
        else:
            res = self._request("agent_consensus", method="POST", payload=payload)

        return bool(res)

    def sync_trade_signal(
        self,
        ticket: int,
        symbol: str = "XAUUSD",
        order_type: str = "BUY",
        lots: float = 0.50,
        open_price: float = 2664.00,
        stop_loss: Optional[float] = 2658.00,
        take_profit: Optional[float] = 2678.00,
        current_pnl: float = 0.0,
        status: str = "OPEN"
    ) -> bool:
        """Upserts an active or closed trade order to public.trade_signals."""
        payload = {
            "ticket": int(ticket),
            "symbol": symbol,
            "order_type": order_type,
            "lots": round(float(lots), 2),
            "open_price": round(float(open_price), 2),
            "stop_loss": round(float(stop_loss), 2) if stop_loss else None,
            "take_profit": round(float(take_profit), 2) if take_profit else None,
            "current_pnl": round(float(current_pnl), 2),
            "status": status,
            "opened_at": datetime.now(timezone.utc).isoformat()
        }

        existing = self._request(f"trade_signals?ticket=eq.{ticket}&select=id&limit=1", method="GET")
        if existing and len(existing) > 0:
            row_id = existing[0].get("id")
            res = self._request(f"trade_signals?id=eq.{row_id}", method="PATCH", payload=payload)
        else:
            res = self._request("trade_signals", method="POST", payload=payload)

        return bool(res)


# Global default instance
supabase_syncer = SupabaseSyncer()
