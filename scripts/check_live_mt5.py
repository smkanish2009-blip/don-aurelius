import sys
import os

try:
    import MetaTrader5 as mt5
except ImportError:
    print("[-] MetaTrader5 Python package not installed.")
    sys.exit(1)

if not mt5.initialize():
    print(f"[-] MT5 Initialize failed: {mt5.last_error()}")
    sys.exit(1)

term = mt5.terminal_info()
acc = mt5.account_info()

print("[+] MT5 Terminal Connection Verified!")
if term:
    print(f"  * Build: {term.build}")
    print(f"  * Connected: {term.connected}")
    print(f"  * Trade Allowed (Algo): {term.trade_allowed}")
    print(f"  * Path: {term.path}")

if acc:
    print("\n[+] Active Account Details:")
    print(f"  * Login ID: {acc.login}")
    print(f"  * Trade Server: {acc.server}")
    print(f"  * Account Name: {acc.name}")
    print(f"  * Balance: ${acc.balance:,.2f} {acc.currency}")
    print(f"  * Equity: ${acc.equity:,.2f} {acc.currency}")
    print(f"  * Free Margin: ${acc.margin_free:,.2f}")
    print(f"  * Leverage: 1:{acc.leverage}")
    mode_str = "HEDGING" if acc.margin_mode == 2 else ("NETTING" if acc.margin_mode == 0 else str(acc.margin_mode))
    print(f"  * Margin Mode: {mode_str}")

# Inspect Gold symbol availability
gold_symbols = [s.name for s in mt5.symbols_get() if "XAU" in s.name.upper() or "GOLD" in s.name.upper()]
print(f"\n[+] Detected Gold Symbols ({len(gold_symbols)}): {gold_symbols}")

if gold_symbols:
    sym = gold_symbols[0]
    mt5.symbol_select(sym, True)
    info = mt5.symbol_info(sym)
    tick = mt5.symbol_info_tick(sym)
    if info and tick:
        print(f"\n[+] Broker Execution Specs for [{sym}]:")
        print(f"  * Bid: ${tick.bid:.2f} | Ask: ${tick.ask:.2f} | Spread: {info.spread} points")
        print(f"  * Digits: {info.digits} | Point: {info.point}")
        print(f"  * Stops Level (Min SL Distance): {info.stops_level} points")
        print(f"  * Freeze Level: {info.freeze_level} points")
        print(f"  * Lot Size Range: Min={info.volume_min}, Max={info.volume_max}, Step={info.volume_step}")
        fill_modes = []
        if info.filling_mode & 1: fill_modes.append("FOK")
        if info.filling_mode & 2: fill_modes.append("IOC")
        fill_modes.append("RETURN")
        print(f"  * Supported Filling Modes: {', '.join(fill_modes)}")

mt5.shutdown()
