//+------------------------------------------------------------------+
//|                                     Don_Aurelius_Sovereign.mq5   |
//|                    DON AURELIUS • Sovereign Quantum Syndicate   |
//|               24/7 Cloud MQL5 Engine with Native Telegram Alerts |
//+------------------------------------------------------------------+
#property copyright   "DON AURELIUS • Sovereign Quantum Syndicate"
#property link        "https://t.me"
#property version     "9.00"
#property description "DON AURELIUS Sovereign Matrix: 24/7 Cloud MQL5 Execution with Native Telegram WebRequest"

#include <Trade\Trade.mqh>

//--- Input Parameters
input group "=== 👑 Telegram Cloud Telemetry ==="
input bool            InpTelegramEnabled     = true;                                                   // Enable Telegram Alerts
input string          InpTelegramToken       = "8612051079:AAFx7jK-Duaxn4bRxqeNeQ2EZhvwrxON61c";      // Bot Token
input string          InpTelegramChatID      = "8775976760";                                           // Chat ID
input int             InpBriefingIntervalMin = 15;                                                     // Periodic Briefing Interval (Minutes)

input group "=== 🏛️ Institutional Risk Management ==="
input ulong           InpMagicNumber         = 20260926;    // Magic Number (Synchronized with Python)
input double          InpRiskPct             = 0.01;        // Risk per Trade (0.01 = 1%)
input double          InpMaxLotCap           = 5.00;        // Hard Max Lot Cap (Lots)
input int             InpMaxOpenPositions    = 2;           // Max Concurrent Positions
input double          InpMaxSpreadPips       = 5.0;         // Max Allowable Spread (Pips)

input group "=== ⚡ Aggressive Signal Engine ==="
input ENUM_TIMEFRAMES InpTimeframe           = PERIOD_M15;  // Trading Timeframe
input int             InpFastEMA             = 12;          // Fast EMA Period
input int             InpSlowEMA             = 26;          // Slow EMA Period
input int             InpATRPeriod           = 14;          // ATR Volatility Period
input int             InpRSIPeriod           = 14;          // RSI Momentum Period
input double          InpRSIOversold         = 35.0;        // RSI Oversold Threshold
input double          InpRSIOverbought       = 65.0;        // RSI Overbought Threshold

input group "=== 🛡️ Dynamic Trailing Stop Settings ==="
input int             InpTrailActivation     = 15;          // Trail Activation Pips ($1.50)
input int             InpTrailStep           = 5;           // Trail Step Pips ($0.50)

input group "=== 📡 Macro Intermarket Radar ==="
input string          InpDXYProxy            = "EURUSD";    // Inverted DXY Proxy Symbol

//--- Global Variables
CTrade   m_trade;
int      m_h_xau_fast;
int      m_h_xau_slow;
int      m_h_xau_atr;
int      m_h_xau_rsi;
int      m_h_dxy_fast;
int      m_h_dxy_slow;

bool     g_isActive          = true;
datetime m_last_bar_time     = 0;
datetime m_last_briefing     = 0;
string   g_macro_trend       = "NEUTRAL";
string   g_shield_status     = "CLEAR";

//--- HUD Object Identifiers
#define PANEL_BG     "AUREUS_HUD_BG"
#define LBL_TITLE    "AUREUS_HUD_TITLE"
#define LBL_STATUS   "AUREUS_HUD_STATUS"
#define LBL_MACRO    "AUREUS_HUD_MACRO"
#define LBL_SHIELD   "AUREUS_HUD_SHIELD"
#define LBL_EQUITY   "AUREUS_HUD_EQUITY"
#define BTN_TOGGLE   "AUREUS_BTN_TOGGLE"
#define BTN_PANIC    "AUREUS_BTN_PANIC"

//+------------------------------------------------------------------+
//| Forward Declarations                                             |
//+------------------------------------------------------------------+
int  SendTelegram(string message);
void DispatchPeriodicBriefing();
void ExecuteTrailingStops();
void EvaluateMacroRadar();
void EvaluateAndExecuteTrade();
void CloseAllPositions();
void CreateOnChartHUD();
void UpdateHUD();

//+------------------------------------------------------------------+
//| Expert Initialization Function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   m_trade.SetExpertMagicNumber(InpMagicNumber);
   m_trade.SetMarginMode();
   m_trade.SetTypeFillingBySymbol(_Symbol);

   // Indicators Initialization
   m_h_xau_fast = iMA(_Symbol, InpTimeframe, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   m_h_xau_slow = iMA(_Symbol, InpTimeframe, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   m_h_xau_atr  = iATR(_Symbol, InpTimeframe, InpATRPeriod);
   m_h_xau_rsi  = iRSI(_Symbol, InpTimeframe, InpRSIPeriod, PRICE_CLOSE);

   if(m_h_xau_fast == INVALID_HANDLE || m_h_xau_slow == INVALID_HANDLE || 
      m_h_xau_atr == INVALID_HANDLE  || m_h_xau_rsi == INVALID_HANDLE)
   {
      Print("[AUREUS-ERR] Failed to create indicator handles for ", _Symbol);
      return(INIT_FAILED);
   }

   // EURUSD Proxy
   if(SymbolSelect(InpDXYProxy, true))
   {
      m_h_dxy_fast = iMA(InpDXYProxy, InpTimeframe, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
      m_h_dxy_slow = iMA(InpDXYProxy, InpTimeframe, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   }
   else
   {
      m_h_dxy_fast = INVALID_HANDLE;
      m_h_dxy_slow = INVALID_HANDLE;
   }

   // Initialize Timer for 15-Minute Telegram Briefings (check every 60 seconds)
   EventSetTimer(60);

   // On-Chart HUD
   CreateOnChartHUD();
   UpdateHUD();

   Print("[+] DON AURELIUS Sovereign MQL5 Initialized. 24/7 Cloud Armed.");

   // Send boot alert to Telegram
   if(InpTelegramEnabled)
   {
      double eq = AccountInfoDouble(ACCOUNT_EQUITY);
      string boot_msg = "👑 *DON AURELIUS • SOVEREIGN MQL5 ONLINE*\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "⚡ *Status*: 24/7 Cloud Matrix Armed\n"
                        "💰 *Treasury Equity*: $" + DoubleToString(eq, 2) + " USD\n"
                        "🥇 *Target*: " + _Symbol + " (" + EnumToString(InpTimeframe) + ")\n"
                        "🛡️ *Trailing Stop*: " + IntegerToString(InpTrailActivation) + " pips activation\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "🏛️ *Autonomous Cloud Protection Active*";
      SendTelegram(boot_msg);
      m_last_briefing = TimeCurrent();
   }

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert Deinitialization Function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();

   IndicatorRelease(m_h_xau_fast);
   IndicatorRelease(m_h_xau_slow);
   IndicatorRelease(m_h_xau_atr);
   IndicatorRelease(m_h_xau_rsi);
   if(m_h_dxy_fast != INVALID_HANDLE) IndicatorRelease(m_h_dxy_fast);
   if(m_h_dxy_slow != INVALID_HANDLE) IndicatorRelease(m_h_dxy_slow);

   ObjectsDeleteAll(0, "AUREUS_");
   ChartRedraw(0);
   Print("[-] DON AURELIUS Deinitialized.");
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Dynamic Trailing Stops on Active Positions
   ExecuteTrailingStops();

   // 2. Bar Close Evaluation (Reduces noise)
   datetime current_bar = iTime(_Symbol, InpTimeframe, 0);
   if(current_bar == m_last_bar_time)
   {
      return;
   }
   m_last_bar_time = current_bar;

   // 3. Macro Radar & HUD Update
   EvaluateMacroRadar();
   UpdateHUD();

   // 4. Trade Execution Gate
   if(!g_isActive || !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
   {
      return;
   }

   // 5. Evaluate and Execute Trades
   EvaluateAndExecuteTrade();
}

//+------------------------------------------------------------------+
//| Timer Event Function: Dispatches 15-Minute Briefings             |
//+------------------------------------------------------------------+
void OnTimer()
{
   if(!InpTelegramEnabled) return;

   datetime now = TimeCurrent();
   int interval_sec = InpBriefingIntervalMin * 60;
   if(now - m_last_briefing >= interval_sec)
   {
      DispatchPeriodicBriefing();
      m_last_briefing = now;
   }
}

//+------------------------------------------------------------------+
//| Dispatch 15-Minute Telegram Telemetry Briefing                   |
//+------------------------------------------------------------------+
void DispatchPeriodicBriefing()
{
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread_pips = (ask - bid) / 0.10;

   int open_count = 0;
   double total_profit = 0.0;
   string contract_details = "";

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) == _Symbol)
      {
         open_count++;
         double profit = PositionGetDouble(POSITION_PROFIT);
         total_profit += profit;
         ulong ticket = PositionGetInteger(POSITION_TICKET);
         ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
         string dir = (type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
         double vol = PositionGetDouble(POSITION_VOLUME);
         double p_open = PositionGetDouble(POSITION_PRICE_OPEN);
         double p_cur = PositionGetDouble(POSITION_PRICE_CURRENT);
         double sl = PositionGetDouble(POSITION_SL);
         double tp = PositionGetDouble(POSITION_TP);
         string p_sign = (profit >= 0) ? "+" : "";

         contract_details += "\n   • 📋 `#" + IntegerToString(ticket) + "`: *" + dir + " " + DoubleToString(vol, 2) + "L* @ $" + DoubleToString(p_open, 2) +
                             "\n     Cur: $" + DoubleToString(p_cur, 2) + " | P&L: `" + p_sign + "$" + DoubleToString(profit, 2) + "`" +
                             "\n     🛡️ SL: $" + DoubleToString(sl, 2) + " | 🎯 TP: $" + DoubleToString(tp, 2);
      }
   }

   string pl_sign = (total_profit >= 0) ? "+" : "";
   string time_str = TimeToString(TimeCurrent(), TIME_MINUTES);

   string msg = "👑 *DON AURELIUS • 15-MIN CLOUD BRIEFING* (" + time_str + ")\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💰 *Treasury Equity*: `$" + DoubleToString(equity, 2) + " USD`\n"
                "💼 *Account Balance*: `$" + DoubleToString(balance, 2) + " USD`\n"
                "⚡ *Active Contracts*: `" + IntegerToString(open_count) + "` | Floating P&L: `" + pl_sign + "$" + DoubleToString(total_profit, 2) + "`" +
                contract_details + "\n"
                "🥇 *XAUUSD (Gold)*: `$" + DoubleToString(bid, 2) + "` (Spread: `" + DoubleToString(spread_pips, 1) + " pips`)\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📡 *Macro Trend*: `" + g_macro_trend + "`\n"
                "🛡️ *Shield Status*: `" + g_shield_status + "`\n"
                "🏛️ *24/7 Cloud Engine*: **OPERATIONAL**";

   SendTelegram(msg);
}

//+------------------------------------------------------------------+
//| Evaluate Macro Intermarket Radar                                 |
//+------------------------------------------------------------------+
void EvaluateMacroRadar()
{
   if(m_h_dxy_fast == INVALID_HANDLE || m_h_dxy_slow == INVALID_HANDLE)
   {
      g_macro_trend   = "STANDALONE";
      g_shield_status = "CLEAR";
      return;
   }

   double dxy_fast[2], dxy_slow[2];
   if(CopyBuffer(m_h_dxy_fast, 0, 0, 2, dxy_fast) < 2 || CopyBuffer(m_h_dxy_slow, 0, 0, 2, dxy_slow) < 2)
   {
      return;
   }

   bool eur_rising = (dxy_fast[1] > dxy_slow[1]);
   g_macro_trend   = (!eur_rising) ? "DOLLAR BULLISH" : "DOLLAR BEARISH";
}

//+------------------------------------------------------------------+
//| Evaluates Signal and Executes Trade                              |
//+------------------------------------------------------------------+
void EvaluateAndExecuteTrade()
{
   // Count open bot positions
   int bot_positions = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
      {
         bot_positions++;
      }
   }

   if(bot_positions >= InpMaxOpenPositions)
   {
      return;
   }

   // Spread Check
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread_pips = (ask - bid) / 0.10;
   if(spread_pips > InpMaxSpreadPips)
   {
      g_shield_status = "SPREAD BLOWOUT (" + DoubleToString(spread_pips, 1) + " pips)";
      return;
   }

   // Indicator Buffers
   double ema_fast[2], ema_slow[2], atr_buf[1], rsi_buf[2];
   if(CopyBuffer(m_h_xau_fast, 0, 0, 2, ema_fast) < 2 ||
      CopyBuffer(m_h_xau_slow, 0, 0, 2, ema_slow) < 2 ||
      CopyBuffer(m_h_xau_atr, 0, 0, 1, atr_buf) < 1  ||
      CopyBuffer(m_h_xau_rsi, 0, 0, 2, rsi_buf) < 2)
   {
      return;
   }

   double xau_fast = ema_fast[1];
   double xau_slow = ema_slow[1];
   double atr_val  = atr_buf[0];
   double rsi_val  = rsi_buf[1];

   bool dollar_rising  = (g_macro_trend == "DOLLAR BULLISH");
   bool dollar_falling = (g_macro_trend == "DOLLAR BEARISH");

   string signal = "HOLD";

   // Precision Confluence Logic
   if(xau_fast > xau_slow && rsi_val < InpRSIOverbought && rsi_val > 40.0)
   {
      if(dollar_rising)
      {
         g_shield_status = "BULL TRAP (DOLLAR STRONG)";
         return;
      }
      signal = "BUY";
      g_shield_status = "CLEAR (BUY CONFLUENCE)";
   }
   else if(xau_fast < xau_slow && rsi_val > InpRSIOversold && rsi_val < 60.0)
   {
      if(dollar_falling)
      {
         g_shield_status = "BEAR TRAP (DOLLAR WEAK)";
         return;
      }
      signal = "SELL";
      g_shield_status = "CLEAR (SELL CONFLUENCE)";
   }

   if(signal == "HOLD") return;

   // Stop Loss & Take Profit ($1 Gold = 10 pips = $0.10/pip)
   double pip_size = 0.10;
   int sl_pips = (int)MathMax(15.0, (atr_val * 2.5) * 10.0);
   int tp_pips = sl_pips * 3; // 1:3 asymmetric reward ratio

   double sl_dist = sl_pips * pip_size;
   double tp_dist = tp_pips * pip_size;

   // Precision Lot Size
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double risk_capital = equity * InpRiskPct;
   double cost_per_lot_sl = sl_pips * 10.0;
   double computed_lot = (cost_per_lot_sl > 0) ? (risk_capital / cost_per_lot_sl) : 0.01;
   computed_lot = MathMin(computed_lot, InpMaxLotCap);
   computed_lot = MathMax(computed_lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   computed_lot = NormalizeDouble(computed_lot, 2);

   // Order Execution
   bool success = false;
   double entry_price = 0.0;
   double final_sl = 0.0;
   double final_tp = 0.0;

   if(signal == "BUY")
   {
      entry_price = ask;
      final_sl    = NormalizeDouble(entry_price - sl_dist, _Digits);
      final_tp    = NormalizeDouble(entry_price + tp_dist, _Digits);
      success     = m_trade.Buy(computed_lot, _Symbol, entry_price, final_sl, final_tp, "DON AURELIUS BUY");
   }
   else if(signal == "SELL")
   {
      entry_price = bid;
      final_sl    = NormalizeDouble(entry_price + sl_dist, _Digits);
      final_tp    = NormalizeDouble(entry_price - tp_dist, _Digits);
      success     = m_trade.Sell(computed_lot, _Symbol, entry_price, final_sl, final_tp, "DON AURELIUS SELL");
   }

   if(success)
   {
      Print("[🚀 AUREUS MQL5 DEPLOYED] ", signal, " ", computed_lot, " lots @ $", entry_price);
      if(InpTelegramEnabled)
      {
         string alert = "🎯 *DON AURELIUS • CLOUD TRADE EXECUTION*\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "⚡ *Action*: *" + signal + "* " + DoubleToString(computed_lot, 2) + " Lots\n"
                        "🥇 *Symbol*: " + _Symbol + " @ `$" + DoubleToString(entry_price, 2) + "`\n"
                        "🛡️ *Stop Loss*: `$" + DoubleToString(final_sl, 2) + "` (-" + IntegerToString(sl_pips) + " pips)\n"
                        "🎯 *Take Profit*: `$" + DoubleToString(final_tp, 2) + "` (+" + IntegerToString(tp_pips) + " pips)\n"
                        "💰 *Risk Capital*: $" + DoubleToString(risk_capital, 2) + " (" + DoubleToString(InpRiskPct * 100, 1) + "%)\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "🏛️ *Executed via 24/7 Cloud Syndicate*";
         SendTelegram(alert);
      }
   }
}

//+------------------------------------------------------------------+
//| Dynamic Trailing Stop Engine                                     |
//+------------------------------------------------------------------+
void ExecuteTrailingStops()
{
   double pip_size = 0.10;
   double activation_dist = InpTrailActivation * pip_size;
   double step_dist       = InpTrailStep * pip_size;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber && InpMagicNumber != 0) continue;

      ulong ticket            = PositionGetInteger(POSITION_TICKET);
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double open_price       = PositionGetDouble(POSITION_PRICE_OPEN);
      double current_sl       = PositionGetDouble(POSITION_SL);
      double current_tp       = PositionGetDouble(POSITION_TP);

      if(type == POSITION_TYPE_BUY)
      {
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         if((bid - open_price) >= activation_dist)
         {
            double new_sl = NormalizeDouble(bid - step_dist, _Digits);
            if(new_sl > current_sl + (step_dist * 0.5) || current_sl == 0)
            {
               if(m_trade.PositionModify(ticket, new_sl, current_tp))
               {
                  Print("[🛡️ AUREUS TRAIL] BUY #", ticket, " SL Advanced to $", new_sl);
                  if(InpTelegramEnabled && new_sl > open_price && current_sl <= open_price)
                  {
                     SendTelegram("🛡️ *DON AURELIUS • PROFIT LOCKED*\nContract `#" + IntegerToString(ticket) + "` (BUY) Stop Loss trailed to `$" + DoubleToString(new_sl, 2) + "` (Risk-Free Trade!)");
                  }
               }
            }
         }
      }
      else if(type == POSITION_TYPE_SELL)
      {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         if((open_price - ask) >= activation_dist)
         {
            double new_sl = NormalizeDouble(ask + step_dist, _Digits);
            if(new_sl < current_sl - (step_dist * 0.5) || current_sl == 0)
            {
               if(m_trade.PositionModify(ticket, new_sl, current_tp))
               {
                  Print("[🛡️ AUREUS TRAIL] SELL #", ticket, " SL Advanced to $", new_sl);
                  if(InpTelegramEnabled && new_sl < open_price && (current_sl >= open_price || current_sl == 0))
                  {
                     SendTelegram("🛡️ *DON AURELIUS • PROFIT LOCKED*\nContract `#" + IntegerToString(ticket) + "` (SELL) Stop Loss trailed to `$" + DoubleToString(new_sl, 2) + "` (Risk-Free Trade!)");
                  }
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Emergency Clean Slate Liquidation                                |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) == _Symbol)
      {
         ulong ticket = PositionGetInteger(POSITION_TICKET);
         m_trade.PositionClose(ticket);
      }
   }
   if(InpTelegramEnabled)
   {
      SendTelegram("🚨 *DON AURELIUS • CLEAN SLATE PROTOCOL*\nAll active contracts on " + _Symbol + " liquidated immediately via On-Chart emergency trigger.");
   }
}

//+------------------------------------------------------------------+
//| Native Telegram WebRequest Transmitter                           |
//+------------------------------------------------------------------+
int SendTelegram(string message)
{
   if(InpTelegramToken == "" || InpTelegramChatID == "") return -1;

   string url = "https://api.telegram.org/bot" + InpTelegramToken + "/sendMessage";
   string headers = "Content-Type: application/json\r\n";

   // Escape quotes and newlines for valid JSON
   string escaped_msg = message;
   StringReplace(escaped_msg, "\\", "\\\\");
   StringReplace(escaped_msg, "\"", "\\\"");
   StringReplace(escaped_msg, "\n", "\\n");
   StringReplace(escaped_msg, "\r", "");

   string json_payload = "{\"chat_id\":\"" + InpTelegramChatID + "\",\"text\":\"" + escaped_msg + "\",\"parse_mode\":\"Markdown\"}";

   char post_data[];
   char result_data[];
   string result_headers;

   StringToCharArray(json_payload, post_data, 0, WHOLE_ARRAY, CP_UTF8);
   int post_size = ArraySize(post_data) - 1; // Exclude null terminator
   if(post_size <= 0) return -1;
   ArrayResize(post_data, post_size);

   ResetLastError();
   int res = WebRequest("POST", url, headers, 15000, post_data, result_data, result_headers);
   if(res == -1)
   {
      int err = GetLastError();
      Print("[TELEGRAM-WARN] WebRequest failed. Error code: ", err);
      return err;
   }
   return res;
}

//+------------------------------------------------------------------+
//| OnChartEvent for handling Button Clicks                          |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_OBJECT_CLICK)
   {
      if(sparam == BTN_TOGGLE)
      {
         g_isActive = !g_isActive;
         Print("[AUREUS-BUTTON] Syndicate state -> ", g_isActive ? "ACTIVE" : "PAUSED");
         UpdateHUD();
         ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_STATE, false);
         ChartRedraw(0);
      }
      else if(sparam == BTN_PANIC)
      {
         Print("[AUREUS-PANIC] Emergency Liquidation clicked!");
         CloseAllPositions();
         UpdateHUD();
         ObjectSetInteger(0, BTN_PANIC, OBJPROP_STATE, false);
         ChartRedraw(0);
      }
   }
}

//+------------------------------------------------------------------+
//| Build Sleek On-Chart HUD                                         |
//+------------------------------------------------------------------+
void CreateOnChartHUD()
{
   int x = 20, y = 30;

   // Background Panel
   ObjectCreate(0, PANEL_BG, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_XSIZE, 300);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_YSIZE, 180);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_BGCOLOR, C'10,12,18');
   ObjectSetInteger(0, PANEL_BG, OBJPROP_BORDER_COLOR, C'212,175,55'); // Imperial Gold
   ObjectSetInteger(0, PANEL_BG, OBJPROP_CORNER, CORNER_LEFT_UPPER);

   // Title Label
   ObjectCreate(0, LBL_TITLE, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, LBL_TITLE, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, LBL_TITLE, OBJPROP_YDISTANCE, y + 12);
   ObjectSetString(0, LBL_TITLE, OBJPROP_TEXT, "👑 DON AURELIUS • SOVEREIGN");
   ObjectSetString(0, LBL_TITLE, OBJPROP_FONT, "Segoe UI Semibold");
   ObjectSetInteger(0, LBL_TITLE, OBJPROP_FONTSIZE, 11);
   ObjectSetInteger(0, LBL_TITLE, OBJPROP_COLOR, C'212,175,55');

   // Status Label
   ObjectCreate(0, LBL_STATUS, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, LBL_STATUS, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, LBL_STATUS, OBJPROP_YDISTANCE, y + 38);
   ObjectSetString(0, LBL_STATUS, OBJPROP_FONT, "Segoe UI");
   ObjectSetInteger(0, LBL_STATUS, OBJPROP_FONTSIZE, 9);

   // Macro Radar Label
   ObjectCreate(0, LBL_MACRO, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, LBL_MACRO, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, LBL_MACRO, OBJPROP_YDISTANCE, y + 58);
   ObjectSetString(0, LBL_MACRO, OBJPROP_FONT, "Segoe UI");
   ObjectSetInteger(0, LBL_MACRO, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, LBL_MACRO, OBJPROP_COLOR, C'160,175,200');

   // Shield Status Label
   ObjectCreate(0, LBL_SHIELD, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, LBL_SHIELD, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, LBL_SHIELD, OBJPROP_YDISTANCE, y + 78);
   ObjectSetString(0, LBL_SHIELD, OBJPROP_FONT, "Segoe UI");
   ObjectSetInteger(0, LBL_SHIELD, OBJPROP_FONTSIZE, 9);

   // Equity Label
   ObjectCreate(0, LBL_EQUITY, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, LBL_EQUITY, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, LBL_EQUITY, OBJPROP_YDISTANCE, y + 98);
   ObjectSetString(0, LBL_EQUITY, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, LBL_EQUITY, OBJPROP_FONTSIZE, 10);
   ObjectSetInteger(0, LBL_EQUITY, OBJPROP_COLOR, clrWhite);

   // Arm / Pause Button
   ObjectCreate(0, BTN_TOGGLE, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_YDISTANCE, y + 130);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_XSIZE, 130);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_YSIZE, 30);
   ObjectSetString(0, BTN_TOGGLE, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_FONTSIZE, 9);

   // Emergency Panic Clean Slate Button
   ObjectCreate(0, BTN_PANIC, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_XDISTANCE, x + 155);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_YDISTANCE, y + 130);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_XSIZE, 130);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_YSIZE, 30);
   ObjectSetString(0, BTN_PANIC, OBJPROP_TEXT, "🚨 CLEAN SLATE");
   ObjectSetString(0, BTN_PANIC, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_COLOR, clrWhite);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_BGCOLOR, C'160,20,20');

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Refresh HUD Values on Chart                                      |
//+------------------------------------------------------------------+
void UpdateHUD()
{
   if(g_isActive)
   {
      ObjectSetString(0, LBL_STATUS, OBJPROP_TEXT, "● System: ARMED & ACTIVE (24/7)");
      ObjectSetInteger(0, LBL_STATUS, OBJPROP_COLOR, C'50,220,120');
      ObjectSetString(0, BTN_TOGGLE, OBJPROP_TEXT, "⏸️ PAUSE");
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_BGCOLOR, C'40,45,60');
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_COLOR, clrWhite);
   }
   else
   {
      ObjectSetString(0, LBL_STATUS, OBJPROP_TEXT, "● System: STANDBY (PAUSED)");
      ObjectSetInteger(0, LBL_STATUS, OBJPROP_COLOR, C'230,80,80');
      ObjectSetString(0, BTN_TOGGLE, OBJPROP_TEXT, "▶️ ARM ALGO");
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_BGCOLOR, C'30,120,60');
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_COLOR, clrWhite);
   }

   ObjectSetString(0, LBL_MACRO, OBJPROP_TEXT, "● Macro Radar: " + g_macro_trend);

   color shield_col = clrWhite;
   if(StringFind(g_shield_status, "CLEAR") >= 0) shield_col = C'50,220,120';
   else if(StringFind(g_shield_status, "TRAP") >= 0) shield_col = C'240,160,40';
   else shield_col = C'220,60,60';

   ObjectSetString(0, LBL_SHIELD, OBJPROP_TEXT, "● Shield Status: " + g_shield_status);
   ObjectSetInteger(0, LBL_SHIELD, OBJPROP_COLOR, shield_col);

   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   ObjectSetString(0, LBL_EQUITY, OBJPROP_TEXT, "● Imperial Equity: $" + DoubleToString(eq, 2) + " USD");

   ChartRedraw(0);
}
