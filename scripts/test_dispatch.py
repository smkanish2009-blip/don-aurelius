import requests
from config.credentials import load_credentials

creds = load_credentials()
token = creds.TELEGRAM_BOT_TOKEN
chat_id = creds.TELEGRAM_CHAT_ID

msg = (
    "👑 *DON AURELIUS • 15-MIN SYNDICATE BRIEFING* (07:30 PM)\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💰 *Treasury Equity*: `$100,000.00 USD`\n"
    "⚡ *Active Contracts*: `0` | Floating P&L: `+$0.00`\n"
    "🥇 *XAUUSD (Gold)*: `$2,658.20` (Spread: `4.0 pips`)\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏛️ *Council Radar* (2/4):\n"
    "   - 🦅 HAWK: `NEUTRAL`\n"
    "   - 📡 RADAR: `BUY`\n"
    "   - 🦈 PREDATOR: `BUY`\n"
    "   - ⚔️ INQUISITOR: `VETO`\n"
    "🎯 *Consensus State*: *HOLD*\n"
    "📝 *Directive*: Weekend spread blowout (4.0 pips). Inquisitor has frozen entries until Asian/London liquidity tightens the spread.\n\n"
    "🔒 _Auto-dispatch protocol locked: You will receive this live telemetry every 15 minutes continuously without lifting a finger._"
)

kb = {
    "inline_keyboard": [
        [
            {"text": "🎙️ Voice Briefing", "callback_data": "voice_briefing"},
            {"text": "📊 Full HUD", "callback_data": "refresh_hud"}
        ]
    ]
}

r = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": kb}
)
print("Status:", r.status_code, r.json().get("ok"))
