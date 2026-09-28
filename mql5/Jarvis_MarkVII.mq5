//+------------------------------------------------------------------+
//|                                             Jarvis_MarkVII.mq5   |
//|                                  Copyright 2026, JARVIS Mark-VII |
//|                                     Autonomous Trading Framework |
//+------------------------------------------------------------------+
#property copyright   "DON AURELIUS • Sovereign Quantum Syndicate"
#property link        "https://github.com"
#property version     "8.00"
#property description "DON AURELIUS Sovereign Quantum Matrix with 1-Click Institutional Controls"

#include <Trade\Trade.mqh>

//--- Input Parameters
input group "=== Institutional Risk Management ==="
input double          InpRiskPct         = 0.01;        // Risk per Trade (0.01 = 1%)
input double          InpMaxLotCap       = 5.00;        // Hard Max Lot Cap (Lots)

input group "=== Algorithmic Engine Settings ==="
input int             InpFastEMA         = 12;          // Fast EMA Period
input int             InpSlowEMA         = 26;          // Slow EMA Period
input int             InpATRPeriod       = 14;          // ATR Volatility Period
input ENUM_TIMEFRAMES InpTimeframe       = PERIOD_M15;  // Trading Timeframe

input group "=== Dynamic Trailing Stop Settings ==="
input int             InpTrailActivation = 15;          // Trail Activation Pips ($1.50)
input int             InpTrailStep       = 5;           // Trail Step Pips ($0.50)

input group "=== Macro Intermarket Radar ==="
input string          InpDXYProxy        = "EURUSD";    // DXY Proxy Symbol (Inverted)

//--- Global Variables
CTrade   m_trade;
int      m_h_xau_fast;
int      m_h_xau_slow;
int      m_h_xau_atr;
int      m_h_dxy_fast;
int      m_h_dxy_slow;

bool     g_isActive         = true;
datetime m_last_bar_time    = 0;
string   g_macro_trend      = "NEUTRAL";
string   g_shield_status    = "CLEAR";

//--- HUD Object Names
#define PANEL_BG     "JARVIS_HUD_BG"
#define LBL_TITLE    "JARVIS_HUD_TITLE"
#define LBL_STATUS   "JARVIS_HUD_STATUS"
#define LBL_MACRO    "JARVIS_HUD_MACRO"
#define LBL_SHIELD   "JARVIS_HUD_SHIELD"
#define LBL_EQUITY   "JARVIS_HUD_EQUITY"
#define BTN_TOGGLE   "JARVIS_BTN_TOGGLE"
#define BTN_PANIC    "JARVIS_BTN_PANIC"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   m_trade.SetExpertMagicNumber(777007);
   m_trade.SetMarginMode();
   m_trade.SetTypeFillingBySymbol(_Symbol);

   // Initialize Indicators
   m_h_xau_fast = iMA(_Symbol, InpTimeframe, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   m_h_xau_slow = iMA(_Symbol, InpTimeframe, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   m_h_xau_atr  = iATR(_Symbol, InpTimeframe, InpATRPeriod);

   if(m_h_xau_fast == INVALID_HANDLE || m_h_xau_slow == INVALID_HANDLE || m_h_xau_atr == INVALID_HANDLE)
   {
      Print("[JARVIS-ERR] Failed to create indicator handles for ", _Symbol);
      return(INIT_FAILED);
   }

   // Initialize DXY Proxy Indicator on EURUSD
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

   // Build On-Chart Visual HUD & One-Click Button
   CreateOnChartHUD();
   UpdateHUD();

   Print("[+] JARVIS Mark-VII Initialized Successfully. One-Click Controls Active.");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release indicators
   IndicatorRelease(m_h_xau_fast);
   IndicatorRelease(m_h_xau_slow);
   IndicatorRelease(m_h_xau_atr);
   if(m_h_dxy_fast != INVALID_HANDLE) IndicatorRelease(m_h_dxy_fast);
   if(m_h_dxy_slow != INVALID_HANDLE) IndicatorRelease(m_h_dxy_slow);

   // Remove HUD Objects from chart
   ObjectsDeleteAll(0, "JARVIS_");
   ChartRedraw(0);
   Print("[-] JARVIS Mark-VII Deinitialized. HUD Cleaned.");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Manage Dynamic Trailing Stops on Active Positions
   ExecuteTrailingStops();

   // 2. Check for New Bar Formation (Avoid mid-candle noise)
   datetime current_bar = iTime(_Symbol, InpTimeframe, 0);
   if(current_bar == m_last_bar_time)
   {
      return;
   }
   m_last_bar_time = current_bar;

   // 3. Update Macro Readings & Evaluate Radar
   EvaluateMacroRadar();
   UpdateHUD();

   // 4. Check if Algo Trading is Active
   if(!g_isActive || !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
   {
      return;
   }

   // 5. Evaluate Signal and Execute Entry
   EvaluateAndExecuteTrade();
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
         Print("[JARVIS-BUTTON] User toggled JARVIS state -> ", g_isActive ? "ACTIVE" : "PAUSED");
         UpdateHUD();
         ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_STATE, false);
         ChartRedraw(0);
      }
      else if(sparam == BTN_PANIC)
      {
         Print("[JARVIS-PANIC] Clean Slate Emergency Liquidation clicked!");
         CloseAllPositions();
         UpdateHUD();
         ObjectSetInteger(0, BTN_PANIC, OBJPROP_STATE, false);
         ChartRedraw(0);
      }
   }
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

   double dxy_fast_buf[2], dxy_slow_buf[2];
   if(CopyBuffer(m_h_dxy_fast, 0, 0, 2, dxy_fast_buf) < 2 || CopyBuffer(m_h_dxy_slow, 0, 0, 2, dxy_slow_buf) < 2)
   {
      return;
   }

   // EURUSD is inversely correlated to DXY
   // If EURUSD is falling (fast < slow), Dollar is rising (BULLISH)
   bool eur_rising = (dxy_fast_buf[1] > dxy_slow_buf[1]);
   g_macro_trend   = (!eur_rising) ? "DOLLAR BULLISH" : "DOLLAR BEARISH";
}

//+------------------------------------------------------------------+
//| Evaluates Signal and Executes Trade                              |
//+------------------------------------------------------------------+
void EvaluateAndExecuteTrade()
{
   // Do not open new trades if position already open
   if(PositionsTotal() > 0)
   {
      return;
   }

   double xau_fast_buf[2], xau_slow_buf[2], atr_buf[1];
   if(CopyBuffer(m_h_xau_fast, 0, 0, 2, xau_fast_buf) < 2 ||
      CopyBuffer(m_h_xau_slow, 0, 0, 2, xau_slow_buf) < 2 ||
      CopyBuffer(m_h_xau_atr, 0, 0, 1, atr_buf) < 1)
   {
      return;
   }

   double xau_fast = xau_fast_buf[1];
   double xau_slow = xau_slow_buf[1];
   double atr_val  = atr_buf[0];

   bool dollar_rising  = (g_macro_trend == "DOLLAR BULLISH");
   bool dollar_falling = (g_macro_trend == "DOLLAR BEARISH");

   // Signal Evaluation
   string signal = "HOLD";

   if(xau_fast > xau_slow)
   {
      // Bull Trap Shield
      if(dollar_rising)
      {
         g_shield_status = "BULL TRAP (HOLD)";
         return;
      }
      signal = "BUY";
      g_shield_status = "CLEAR (BUY OK)";
   }
   else if(xau_fast < xau_slow)
   {
      // Bear Trap Shield
      if(dollar_falling)
      {
         g_shield_status = "BEAR TRAP (HOLD)";
         return;
      }
      signal = "SELL";
      g_shield_status = "CLEAR (SELL OK)";
   }

   if(signal == "HOLD")
   {
      return;
   }

   // Compute Stop Loss & Take Profit ($1 Gold = 10 pips = 100 points)
   double pip_size = 0.10; // $0.10 per pip
   int sl_pips = (int)MathMax(15.0, (atr_val * 2.5) * 10.0);
   int tp_pips = sl_pips * 3; // 1:3 asymmetric reward

   double sl_dist = sl_pips * pip_size;
   double tp_dist = tp_pips * pip_size;

   // Precision Lot Size Computation
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double risk_capital = equity * InpRiskPct;
   double cost_per_lot_sl = sl_pips * 10.0; // $10 per pip per standard lot
   double computed_lot = (cost_per_lot_sl > 0) ? (risk_capital / cost_per_lot_sl) : 0.01;
   computed_lot = MathMin(computed_lot, InpMaxLotCap);
   computed_lot = MathMax(computed_lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   computed_lot = NormalizeDouble(computed_lot, 2);

   // Transmit Order
   if(signal == "BUY")
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = NormalizeDouble(ask - sl_dist, _Digits);
      double tp  = NormalizeDouble(ask + tp_dist, _Digits);
      m_trade.Buy(computed_lot, _Symbol, ask, sl, tp, "JARVIS Mark-VII BUY");
   }
   else if(signal == "SELL")
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = NormalizeDouble(bid + sl_dist, _Digits);
      double tp  = NormalizeDouble(bid - tp_dist, _Digits);
      m_trade.Sell(computed_lot, _Symbol, bid, sl, tp, "JARVIS Mark-VII SELL");
   }
}

//+------------------------------------------------------------------+
//| Dynamic Trailing Stop Engine                                     |
//+------------------------------------------------------------------+
void ExecuteTrailingStops()
{
   double pip_size = 0.10; // 1 pip = $0.10 gold move
   double activation_dist = InpTrailActivation * pip_size;
   double step_dist       = InpTrailStep * pip_size;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      string sym = PositionGetSymbol(i);
      if(sym != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != 777007) continue;

      ulong ticket      = PositionGetInteger(POSITION_TICKET);
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
      double current_sl = PositionGetDouble(POSITION_SL);

      if(type == POSITION_TYPE_BUY)
      {
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         if((bid - open_price) >= activation_dist)
         {
            double new_sl = NormalizeDouble(bid - activation_dist, _Digits);
            if(new_sl > current_sl + step_dist || current_sl == 0)
            {
               m_trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
               Print("[JARVIS-TRAIL] BUY #", ticket, " SL Advanced to ", new_sl);
            }
         }
      }
      else if(type == POSITION_TYPE_SELL)
      {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         if((open_price - ask) >= activation_dist)
         {
            double new_sl = NormalizeDouble(ask + activation_dist, _Digits);
            if(new_sl < current_sl - step_dist || current_sl == 0)
            {
               m_trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
               Print("[JARVIS-TRAIL] SELL #", ticket, " SL Advanced to ", new_sl);
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Emergency Liquidation                                            |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      string sym = PositionGetSymbol(i);
      if(sym != _Symbol) continue;
      ulong ticket = PositionGetInteger(POSITION_TICKET);
      m_trade.PositionClose(ticket);
   }
}

//+------------------------------------------------------------------+
//| Build Sleek On-Chart HUD & Control Panel                         |
//+------------------------------------------------------------------+
void CreateOnChartHUD()
{
   int x = 20;
   int y = 30;
   int w = 270;
   int h = 210;

   // 1. Background Panel
   ObjectCreate(0, PANEL_BG, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_XSIZE, w);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_YSIZE, h);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_BGCOLOR, C'14,18,26');
   ObjectSetInteger(0, PANEL_BG, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, PANEL_BG, OBJPROP_COLOR, C'255,215,0'); // Imperial Gold Border
   ObjectSetInteger(0, PANEL_BG, OBJPROP_CORNER, CORNER_LEFT_UPPER);

   // 2. Title Header
   CreateLabel(LBL_TITLE, x + 15, y + 12, "👑 DON AURELIUS • SYNDICATE", "Arial Bold", 10, C'255,215,0');

   // 3. Status Labels
   CreateLabel(LBL_STATUS, x + 15, y + 38, "STATUS: INITIALIZING...", "Segoe UI", 9, clrWhite);
   CreateLabel(LBL_MACRO,  x + 15, y + 58, "MACRO DXY: SCANNING...", "Segoe UI", 9, clrWhite);
   CreateLabel(LBL_SHIELD, x + 15, y + 78, "SHIELD: CHECKING...", "Segoe UI", 9, clrWhite);
   CreateLabel(LBL_EQUITY, x + 15, y + 98, "EQUITY: $0.00", "Segoe UI", 9, clrLightGreen);

   // 4. One-Click Toggle Button
   ObjectCreate(0, BTN_TOGGLE, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_YDISTANCE, y + 125);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_XSIZE, 240);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_YSIZE, 32);
   ObjectSetString(0, BTN_TOGGLE, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_CORNER, CORNER_LEFT_UPPER);

   // 5. Emergency Panic Button
   ObjectCreate(0, BTN_PANIC, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_XDISTANCE, x + 15);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_YDISTANCE, y + 165);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_XSIZE, 240);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_YSIZE, 28);
   ObjectSetString(0, BTN_PANIC, OBJPROP_TEXT, "🚨 CLEAN SLATE FLATTEN");
   ObjectSetString(0, BTN_PANIC, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_FONTSIZE, 8);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_BGCOLOR, C'160,20,30');
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_COLOR, clrWhite);
   ObjectSetInteger(0, BTN_PANIC, OBJPROP_CORNER, CORNER_LEFT_UPPER);
}

//+------------------------------------------------------------------+
//| Update On-Chart HUD Displays                                     |
//+------------------------------------------------------------------+
void UpdateHUD()
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   string eq_str = StringFormat("EQUITY: $%.2f USD", equity);

   ObjectSetString(0, LBL_EQUITY, OBJPROP_TEXT, eq_str);
   ObjectSetString(0, LBL_MACRO, OBJPROP_TEXT, "MACRO: " + g_macro_trend);
   ObjectSetString(0, LBL_SHIELD, OBJPROP_TEXT, "SHIELD: " + g_shield_status);

   if(g_isActive)
   {
      ObjectSetString(0, LBL_STATUS, OBJPROP_TEXT, "STATUS: 🟢 ACTIVE (SCANNING)");
      ObjectSetInteger(0, LBL_STATUS, OBJPROP_COLOR, C'0,255,128');

      ObjectSetString(0, BTN_TOGGLE, OBJPROP_TEXT, "⏸️ PAUSE DON AURELIUS");
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_BGCOLOR, C'180,80,20');
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_COLOR, clrWhite);
   }
   else
   {
      ObjectSetString(0, LBL_STATUS, OBJPROP_TEXT, "STATUS: 🔴 PAUSED (STANDBY)");
      ObjectSetInteger(0, LBL_STATUS, OBJPROP_COLOR, C'255,80,80');

      ObjectSetString(0, BTN_TOGGLE, OBJPROP_TEXT, "⚡ ACTIVATE DON AURELIUS");
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_BGCOLOR, C'0,160,70');
      ObjectSetInteger(0, BTN_TOGGLE, OBJPROP_COLOR, clrWhite);
   }

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Helper to create clean text labels                               |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, string font, int size, color col)
{
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetString(0, name, OBJPROP_FONT, font);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
   ObjectSetInteger(0, name, OBJPROP_COLOR, col);
   ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
}
