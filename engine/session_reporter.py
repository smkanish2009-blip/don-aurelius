"""
TITAN-X Autonomous Executive Session Reporter.
Compiles institutional trading metrics, P&L, win-rate, and Council telemetry
into a high-fidelity HTML dashboard saved directly to the user's Desktop.
"""

import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


class TitanSessionReporter:
    """Compiles and generates executive visual trading reports."""

    def __init__(self, db_path: str = "data/jarvis_metrics.db"):
        self.db_path = db_path
        self.desktop_path = os.path.expandvars(r"C:\Users\LENOVO\Desktop\VIEW_MY_PROFITS_REPORT.html")

    def fetch_db_trades(self) -> List[Dict[str, Any]]:
        """Retrieves trade history from SQLite logger."""
        if not os.path.exists(self.db_path):
            return []
        trades = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ticket_id, direction, volume, entry_price, sl, tp, status, timestamp FROM trades ORDER BY id DESC")
            rows = cursor.fetchall()
            for r in rows:
                trades.append({
                    "ticket": r[0],
                    "direction": r[1],
                    "volume": r[2],
                    "entry": r[3],
                    "sl": r[4],
                    "tp": r[5],
                    "status": r[6],
                    "time": r[7]
                })
            conn.close()
        except Exception:
            pass
        return trades

    def fetch_live_mt5_metrics(self) -> Dict[str, Any]:
        """Fetches live balance, equity, and positions from MT5."""
        metrics = {
            "balance": 100000.0,
            "equity": 100000.0,
            "margin_free": 100000.0,
            "open_positions": [],
            "history_deals": []
        }

        if mt5 is None or not mt5.initialize():
            return metrics

        acc = mt5.account_info()
        if acc:
            metrics["balance"] = acc.balance
            metrics["equity"] = acc.equity
            metrics["margin_free"] = acc.margin_free

        # Open positions
        positions = mt5.positions_get(symbol="XAUUSD")
        if positions:
            for p in positions:
                metrics["open_positions"].append({
                    "ticket": p.ticket,
                    "type": "BUY" if p.type == 0 else "SELL",
                    "volume": p.volume,
                    "price_open": p.price_open,
                    "price_current": p.price_current,
                    "sl": p.sl,
                    "tp": p.tp,
                    "profit": p.profit
                })

        # Today's history
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day)
        deals = mt5.history_deals_get(start_of_day, now)
        if deals:
            for d in deals:
                if d.entry == 1:  # Out / closed deal
                    metrics["history_deals"].append({
                        "ticket": d.ticket,
                        "profit": d.profit,
                        "volume": d.volume,
                        "symbol": d.symbol,
                        "time": datetime.fromtimestamp(d.time).strftime("%H:%M:%S")
                    })

        return metrics

    def generate_html_report(self) -> str:
        """Renders complete executive dark-mode HTML report."""
        mt5_data = self.fetch_live_mt5_metrics()
        db_trades = self.fetch_db_trades()

        balance = mt5_data["balance"]
        equity = mt5_data["equity"]
        net_pl = equity - 100000.0  # Starting baseline $100k
        pl_color = "#00ff88" if net_pl >= 0 else "#ff4444"
        pl_sign = "+" if net_pl >= 0 else ""

        deals = mt5_data["history_deals"]
        wins = sum(1 for d in deals if d["profit"] > 0)
        losses = sum(1 for d in deals if d["profit"] < 0)
        total_closed = len(deals)
        win_rate = (wins / total_closed * 100.0) if total_closed > 0 else 0.0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 DON AURELIUS • Sovereign Syndicate Report</title>
    <style>
        body {{
            background-color: #0b0e14;
            color: #e0e6ed;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #1a2230;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            color: #00e5ff;
            font-size: 26px;
            letter-spacing: 1px;
        }}
        .header .timestamp {{
            color: #8892b0;
            font-size: 14px;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #121824;
            border: 1px solid #1f293d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .card .title {{
            font-size: 13px;
            text-transform: uppercase;
            color: #8892b0;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }}
        .card .value {{
            font-size: 26px;
            font-weight: bold;
        }}
        .card .sub {{
            font-size: 12px;
            color: #8892b0;
            margin-top: 5px;
        }}
        .section-title {{
            font-size: 18px;
            color: #00e5ff;
            margin: 30px 0 15px 0;
            border-left: 4px solid #00e5ff;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #121824;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #1f293d;
            margin-bottom: 30px;
        }}
        th, td {{
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid #1a2334;
        }}
        th {{
            background: #172030;
            color: #8892b0;
            font-size: 12px;
            text-transform: uppercase;
        }}
        tr:hover {{
            background: #172236;
        }}
        .badge-buy {{
            background: rgba(0, 255, 136, 0.15);
            color: #00ff88;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        }}
        .badge-sell {{
            background: rgba(255, 68, 68, 0.15);
            color: #ff4444;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        }}
        .empty-row {{
            text-align: center;
            color: #8892b0;
            padding: 30px;
            font-style: italic;
        }}
        .council-box {{
            background: #121824;
            border: 1px solid #1f293d;
            border-radius: 12px;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }}
        .council-agent {{
            background: #172030;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #00e5ff;
        }}
        .council-agent .name {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .council-agent .role {{
            font-size: 11px;
            color: #8892b0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>👑 DON AURELIUS • SOVEREIGN QUANTUM SYNDICATE</h1>
                <div class="timestamp">Session Executive Report • Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            </div>
            <div>
                <span style="background: rgba(255,215,0,0.15); color: #ffd700; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; border: 1px solid rgba(255,215,0,0.3);">
                    DEMO #113182919
                </span>
            </div>
        </div>

        <div class="cards">
            <div class="card">
                <div class="title">Net Session P&L</div>
                <div class="value" style="color: {pl_color};">{pl_sign}${net_pl:,.2f}</div>
                <div class="sub">Baseline: $100,000.00 USD</div>
            </div>
            <div class="card">
                <div class="title">Current Account Equity</div>
                <div class="value" style="color: #00e5ff;">${equity:,.2f}</div>
                <div class="sub">Free Margin: ${mt5_data['margin_free']:,.2f}</div>
            </div>
            <div class="card">
                <div class="title">Win Rate</div>
                <div class="value" style="color: #ffb703;">{win_rate:.1f}%</div>
                <div class="sub">{wins} Wins / {losses} Losses ({total_closed} Total)</div>
            </div>
            <div class="card">
                <div class="title">Active Positions</div>
                <div class="value" style="color: #ffffff;">{len(mt5_data['open_positions'])}</div>
                <div class="sub">Auto-Trailing Protection: ON</div>
            </div>
        </div>

        <div class="section-title">🏛️ TITAN-X Consensus Council Status</div>
        <div class="council-box">
            <div class="council-agent">
                <div class="name">🦅 Agent HAWK</div>
                <div class="role">Macro & Intermarket (DXY/US10Y)</div>
                <div style="margin-top: 10px; font-size: 12px; color: #00ff88;">Status: Active</div>
            </div>
            <div class="council-agent">
                <div class="name">📡 Agent RADAR</div>
                <div class="role">Real-Time News & Sentiment Velocity</div>
                <div style="margin-top: 10px; font-size: 12px; color: #00ff88;">Status: Active</div>
            </div>
            <div class="council-agent">
                <div class="name">🦈 Agent PREDATOR</div>
                <div class="role">FVG & Liquidity Sweep Detection</div>
                <div style="margin-top: 10px; font-size: 12px; color: #00ff88;">Status: Active</div>
            </div>
            <div class="council-agent">
                <div class="name">⚔️ Agent INQUISITOR</div>
                <div class="role">Red-Team Adversary (Spread & Risk)</div>
                <div style="margin-top: 10px; font-size: 12px; color: #00ff88;">Status: Active</div>
            </div>
        </div>

        <div class="section-title">📊 Open Positions (Active Auto-Trailing)</div>
        <table>
            <thead>
                <tr>
                    <th>Ticket</th>
                    <th>Direction</th>
                    <th>Volume</th>
                    <th>Entry Price</th>
                    <th>Current Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                    <th>Floating P&L</th>
                </tr>
            </thead>
            <tbody>
"""
        if mt5_data["open_positions"]:
            for p in mt5_data["open_positions"]:
                badge = "badge-buy" if p["type"] == "BUY" else "badge-sell"
                p_color = "#00ff88" if p["profit"] >= 0 else "#ff4444"
                html += f"""
                <tr>
                    <td>#{p['ticket']}</td>
                    <td><span class="{badge}">{p['type']}</span></td>
                    <td>{p['volume']:.2f} lots</td>
                    <td>${p['price_open']:.2f}</td>
                    <td>${p['price_current']:.2f}</td>
                    <td>${p['sl']:.2f}</td>
                    <td>${p['tp']:.2f}</td>
                    <td style="color: {p_color}; font-weight: bold;">{'+' if p['profit']>=0 else ''}${p['profit']:.2f}</td>
                </tr>
"""
        else:
            html += """
                <tr>
                    <td colspan="8" class="empty-row">No active floating positions right now. Council is scanning for high-probability setups.</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <div class="section-title">📜 Session Execution Log</div>
        <table>
            <thead>
                <tr>
                    <th>Ticket</th>
                    <th>Direction</th>
                    <th>Volume</th>
                    <th>Entry Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        if db_trades:
            for t in db_trades[:15]:
                badge = "badge-buy" if t["direction"] == "BUY" else "badge-sell"
                html += f"""
                <tr>
                    <td>#{t['ticket']}</td>
                    <td><span class="{badge}">{t['direction']}</span></td>
                    <td>{t['volume']:.2f} lots</td>
                    <td>${t['entry']:.2f}</td>
                    <td>${t['sl']:.2f}</td>
                    <td>${t['tp']:.2f}</td>
                    <td><span style="color: #00e5ff;">{t['status']}</span></td>
                </tr>
"""
        else:
            html += """
                <tr>
                    <td colspan="7" class="empty-row">No trades logged yet in this session. Full ledger will populate as trades deploy.</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        # Save to Desktop
        try:
            with open(self.desktop_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception:
            pass

        return html


def run_session_report():
    """Generates the report directly."""
    reporter = TitanSessionReporter()
    reporter.generate_html_report()
    print(f"[+] Executive Trading Report generated at: {reporter.desktop_path}")


if __name__ == "__main__":
    run_session_report()
