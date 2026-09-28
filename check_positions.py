import MetaTrader5 as mt5

if not mt5.initialize():
    print("MT5 Init Failed")
    quit()

positions = mt5.positions_get(symbol="XAUUSD")
acc = mt5.account_info()
tot_profit = sum(p.profit for p in positions) if positions else 0.0

print(f"Total Open Positions: {len(positions) if positions else 0}")
print(f"Total Floating Profit: ${tot_profit:.2f}")
print(f"Account Equity: ${acc.equity:.2f}")
print(f"Account Balance: ${acc.balance:.2f}")

for p in (positions or []):
    direction = "BUY" if p.type == 0 else "SELL"
    print(f"Ticket #{p.ticket}: {direction} {p.volume:.2f}L | Entry: ${p.price_open:.2f} | Current: ${p.price_current:.2f} | PnL: ${p.profit:.2f} | SL: ${p.sl:.2f} | TP: ${p.tp:.2f}")

mt5.shutdown()
