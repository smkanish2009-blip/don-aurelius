import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ============================================================================
// DESIGN SYSTEM TOKENS
// ============================================================================
const TOKENS = {
  bgCanvas: "#030508",
  bgCard: "rgba(10, 14, 24, 0.82)",
  bgTerminal: "#04070D",
  borderGold: "rgba(245, 208, 97, 0.3)",
  borderGoldBright: "rgba(245, 208, 97, 0.85)",
  accentGold: "#F5D061",
  accentGoldDark: "#D4AF37",
  accentCyan: "#38BDF8",
  accentGreen: "#10B981",
  accentRed: "#EF4444",
  textWhite: "#F8FAFC",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  fontMono: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
  fontSans:
    '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif',
};

// ============================================================================
// SIMULATED LOGS & LIVE TICK DATA
// ============================================================================
const IPC_INIT_LOGS = [
  { text: "$ python scripts/check_live_mt5.py --symbol=XAUUSD --ipc-fast", color: TOKENS.textDim, delay: 10 },
  { text: "[*] Initializing MetaTrader 5 Python IPC Driver (Build 4410)...", color: TOKENS.accentCyan, delay: 35 },
  { text: "[+] MT5 Process Detected: terminal64.exe (PID: 14820)", color: TOKENS.textMuted, delay: 60 },
  { text: "[+] Memory Pipe: SharedBuffer\\MT5_IPC_Bridge_0 locked", color: TOKENS.textMuted, delay: 85 },
  { text: "[+] MetaTrader5.initialize(): SUCCESS -> Terminal Build 4410", color: TOKENS.accentGreen, delay: 110 },
  { text: "[+] Backtrader Feed Engine: Hooked via Sub-millisecond Memory Ring", color: TOKENS.accentCyan, delay: 135 },
  { text: "[+] Symbol: XAUUSD (Gold Spot) Subscribed | Digits: 2 | Contract: 100", color: TOKENS.accentGold, delay: 160 },
  { text: "[🚀] IPC HANDSHAKE COMPLETE: LATENCY 0.38ms • STREAMING LIVE TICKS", color: TOKENS.accentGreen, delay: 185 },
];

const GENERATED_TICKS = [
  { bid: "2648.35", ask: "2648.55", vol: "14.2", lat: "0.38ms", up: true },
  { bid: "2648.42", ask: "2648.62", vol: "22.5", lat: "0.34ms", up: true },
  { bid: "2648.38", ask: "2648.58", vol: "18.0", lat: "0.36ms", up: false },
  { bid: "2648.50", ask: "2648.70", vol: "31.4", lat: "0.37ms", up: true },
  { bid: "2648.62", ask: "2648.82", vol: "27.8", lat: "0.33ms", up: true },
  { bid: "2648.58", ask: "2648.78", vol: "19.6", lat: "0.35ms", up: false },
  { bid: "2648.75", ask: "2648.95", vol: "42.1", lat: "0.32ms", up: true },
  { bid: "2648.88", ask: "2649.08", vol: "38.3", lat: "0.36ms", up: true },
  { bid: "2648.82", ask: "2649.02", vol: "16.9", lat: "0.38ms", up: false },
  { bid: "2648.95", ask: "2649.15", vol: "51.0", lat: "0.31ms", up: true },
  { bid: "2649.10", ask: "2649.30", vol: "64.2", lat: "0.33ms", up: true },
  { bid: "2649.05", ask: "2649.25", vol: "28.4", lat: "0.35ms", up: false },
  { bid: "2649.25", ask: "2649.45", vol: "45.7", lat: "0.32ms", up: true },
  { bid: "2649.40", ask: "2649.60", vol: "73.1", lat: "0.29ms", up: true },
  { bid: "2649.35", ask: "2649.55", vol: "33.8", lat: "0.34ms", up: false },
  { bid: "2649.52", ask: "2649.72", vol: "58.6", lat: "0.30ms", up: true },
];

// ============================================================================
// DEDICATED COMPONENT: MT5ConnectionScene
// ============================================================================
export const MT5ConnectionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // --------------------------------------------------------------------------
  // Connection Trigger Logic (Flips at Frame 185)
  // --------------------------------------------------------------------------
  const CONNECTION_TRIGGER_FRAME = 185;
  const isConnected = frame >= CONNECTION_TRIGGER_FRAME;

  // Toggle Switch Spring Animation
  const toggleSpring = spring({
    frame: frame - CONNECTION_TRIGGER_FRAME,
    fps,
    config: { damping: 13, stiffness: 150, mass: 0.5 },
  });

  const toggleProgress = isConnected
    ? Math.min(1, Math.max(0, toggleSpring))
    : 0;

  // Knob X displacement: 4px (off) -> 64px (on)
  const knobX = interpolate(toggleProgress, [0, 1], [4, 64]);

  // Track Color morph: Gray (#374151) -> Imperial Gold (#F5D061)
  const trackBg = isConnected
    ? `linear-gradient(135deg, ${TOKENS.accentGoldDark}, ${TOKENS.accentGold})`
    : "rgba(55, 65, 81, 0.65)";

  const toggleGlow = isConnected
    ? `0 0 28px rgba(245, 208, 97, ${0.45 * toggleProgress})`
    : "none";

  // Terminal scroll translation based on active frame
  const terminalScrollY = interpolate(
    frame,
    [185, 300, 480, 615],
    [0, -110, -320, -520],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Live Tick index calculator (runs starting frame 190)
  const tickIndex = Math.min(
    GENERATED_TICKS.length - 1,
    Math.max(0, Math.floor((frame - 190) / 24))
  );
  const currentTick = GENERATED_TICKS[tickIndex];

  // Micro pulse on live tick update
  const tickPulse = isConnected ? Math.sin(frame / 6) * 0.1 + 0.9 : 1;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 54px",
        fontFamily: TOKENS.fontSans,
      }}
    >
      {/* -------------------------------------------------------------------- */}
      {/* 1. Header Badges & Scene Identifier */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 24px",
          borderRadius: 999,
          backgroundColor: isConnected
            ? "rgba(245, 208, 97, 0.12)"
            : "rgba(100, 116, 139, 0.15)",
          border: `1px solid ${
            isConnected ? TOKENS.borderGoldBright : "rgba(100, 116, 139, 0.4)"
          }`,
          marginBottom: 16,
          transition: "all 0.3s ease",
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 800,
            color: isConnected ? TOKENS.accentGold : TOKENS.textMuted,
            fontFamily: TOKENS.fontMono,
          }}
        >
          STEP 02 OF 03
        </span>
        <span style={{ color: TOKENS.textDim }}>•</span>
        <span
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: TOKENS.textWhite,
            letterSpacing: "0.04em",
          }}
        >
          METATRADER 5 & PYTHON IPC BRIDGE
        </span>
      </div>

      <h2
        style={{
          fontSize: 52,
          fontWeight: 800,
          color: TOKENS.textWhite,
          letterSpacing: "-0.03em",
          margin: "0 0 28px 0",
          textAlign: "center",
        }}
      >
        Sub-Millisecond MT5 Telemetry Link
      </h2>

      {/* -------------------------------------------------------------------- */}
      {/* 2. Top Interactive Status Bar & Toggle Switch */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          width: 960,
          borderRadius: 20,
          backgroundColor: TOKENS.bgCard,
          border: `1px solid ${
            isConnected ? TOKENS.borderGoldBright : TOKENS.borderGold
          }`,
          boxShadow: isConnected
            ? `0 20px 50px rgba(0,0,0,0.8), 0 0 35px rgba(245, 208, 97, 0.18)`
            : "0 20px 40px rgba(0,0,0,0.7)",
          padding: "20px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 24,
          backdropFilter: "blur(20px)",
        }}
      >
        {/* Connection Status Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              backgroundColor: isConnected ? TOKENS.accentGold : "#6B7280",
              boxShadow: isConnected
                ? `0 0 16px ${TOKENS.accentGold}`
                : "none",
              transition: "all 0.3s ease",
            }}
          />
          <div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 800,
                color: isConnected ? TOKENS.accentGold : TOKENS.textMuted,
                fontFamily: TOKENS.fontMono,
                letterSpacing: "0.04em",
              }}
            >
              {isConnected
                ? "IPC BRIDGE: CONNECTED & ARMED"
                : "IPC BRIDGE: INITIALIZING..."}
            </div>
            <div style={{ fontSize: 16, color: TOKENS.textDim }}>
              {isConnected
                ? "Shared Memory Pipe: 0.38ms Latency • Backtrader Synchronized"
                : "Awaiting Socket Handshake with MT5 Terminal..."}
            </div>
          </div>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Dedicated Toggle Switch (Gray -> Imperial Gold #F5D061)           */}
        {/* ------------------------------------------------------------------ */}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span
            style={{
              fontSize: 16,
              fontWeight: 700,
              fontFamily: TOKENS.fontMono,
              color: isConnected ? TOKENS.accentGold : TOKENS.textDim,
              letterSpacing: "0.08em",
            }}
          >
            {isConnected ? "ACTIVE" : "OFFLINE"}
          </span>

          <div
            style={{
              width: 114,
              height: 54,
              borderRadius: 999,
              background: trackBg,
              border: `2px solid ${
                isConnected ? TOKENS.accentGold : "rgba(107, 114, 128, 0.6)"
              }`,
              boxShadow: toggleGlow,
              padding: 4,
              position: "relative",
              display: "flex",
              alignItems: "center",
              cursor: "pointer",
            }}
          >
            {/* Sliding Toggle Knob */}
            <div
              style={{
                position: "absolute",
                left: knobX,
                width: 42,
                height: 42,
                borderRadius: "50%",
                backgroundColor: isConnected ? "#030508" : "#9CA3AF",
                boxShadow: isConnected
                  ? "0 4px 12px rgba(0, 0, 0, 0.6), 0 0 10px rgba(245, 208, 97, 0.5)"
                  : "0 2px 6px rgba(0, 0, 0, 0.4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isConnected ? (
                <span
                  style={{
                    fontSize: 18,
                    fontWeight: 900,
                    color: TOKENS.accentGold,
                  }}
                >
                  ⚡
                </span>
              ) : (
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    backgroundColor: "#4B5563",
                  }}
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------- */}
      {/* 3. Live Price Telemetry Ribbon (Appears upon connection)             */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          width: 960,
          display: "grid",
          gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
          gap: 16,
          marginBottom: 20,
        }}
      >
        {[
          {
            label: "INSTRUMENT",
            val: "XAU/USD (Gold Spot)",
            sub: "MetaQuotes MT5 Feed",
            color: TOKENS.accentGold,
          },
          {
            label: "BID PRICE",
            val: isConnected ? currentTick.bid : "----.--",
            sub: "Sub-Tick Stream",
            color: isConnected ? TOKENS.accentGreen : TOKENS.textDim,
          },
          {
            label: "ASK PRICE",
            val: isConnected ? currentTick.ask : "----.--",
            sub: "Spread: 0.20 pts",
            color: isConnected ? TOKENS.accentGold : TOKENS.textDim,
          },
          {
            label: "IPC LATENCY",
            val: isConnected ? currentTick.lat : "-- ms",
            sub: "Direct Memory Pipe",
            color: isConnected ? TOKENS.accentCyan : TOKENS.textDim,
          },
        ].map((stat, idx) => (
          <div
            key={idx}
            style={{
              padding: "16px 20px",
              borderRadius: 16,
              backgroundColor: TOKENS.bgCard,
              border: `1px solid ${
                isConnected ? TOKENS.borderGold : "rgba(255, 255, 255, 0.05)"
              }`,
              transform: isConnected ? `scale(${tickPulse})` : "none",
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            <span style={{ fontSize: 14, color: TOKENS.textDim, fontFamily: TOKENS.fontMono }}>
              {stat.label}
            </span>
            <span
              style={{
                fontSize: 24,
                fontWeight: 800,
                color: stat.color,
                fontFamily: TOKENS.fontMono,
              }}
            >
              {stat.val}
            </span>
            <span style={{ fontSize: 13, color: TOKENS.textMuted }}>{stat.sub}</span>
          </div>
        ))}
      </div>

      {/* -------------------------------------------------------------------- */}
      {/* 4. Main Terminal UI (Scrolling Logs & Live Tick Stream)              */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          width: 960,
          height: 380,
          borderRadius: 20,
          backgroundColor: TOKENS.bgTerminal,
          border: `1px solid ${
            isConnected ? TOKENS.borderGold : "rgba(255, 255, 255, 0.1)"
          }`,
          boxShadow: "0 30px 60px rgba(0, 0, 0, 0.9), inset 0 0 20px rgba(0, 0, 0, 0.8)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Terminal Window Header Chrome */}
        <div
          style={{
            padding: "14px 22px",
            backgroundColor: "rgba(10, 14, 24, 0.95)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                backgroundColor: TOKENS.accentRed,
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                backgroundColor: TOKENS.accentGold,
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                backgroundColor: TOKENS.accentGreen,
              }}
            />
            <span
              style={{
                marginLeft: 14,
                fontSize: 16,
                color: TOKENS.textMuted,
                fontFamily: TOKENS.fontMono,
              }}
            >
              don-aurelius@terminal: ~/scripts/check_live_mt5.py
            </span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              fontFamily: TOKENS.fontMono,
              fontSize: 14,
            }}
          >
            <span style={{ color: TOKENS.textDim }}>PORT: 8282</span>
            <span style={{ color: TOKENS.textDim }}>•</span>
            <span style={{ color: isConnected ? TOKENS.accentGreen : TOKENS.accentGold }}>
              {isConnected ? "LIVE STREAMING" : "CONNECTING"}
            </span>
          </div>
        </div>

        {/* Console Body with Smooth Scrolling */}
        <div
          style={{
            flex: 1,
            padding: "20px 26px",
            fontFamily: TOKENS.fontMono,
            fontSize: 17,
            lineHeight: 1.65,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              transform: `translateY(${terminalScrollY}px)`,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {/* Initial Handshake Logs */}
            {IPC_INIT_LOGS.map((log, idx) => {
              const isVisible = frame >= log.delay;
              if (!isVisible) return null;
              return (
                <div key={idx} style={{ color: log.color, whiteSpace: "pre-wrap" }}>
                  {log.text}
                </div>
              );
            })}

            {/* Live XAUUSD Streaming Ticks */}
            {isConnected && (
              <div
                style={{
                  marginTop: 12,
                  paddingTop: 12,
                  borderTop: "1px dashed rgba(245, 208, 97, 0.25)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                <div style={{ color: TOKENS.accentGold, fontWeight: 700 }}>
                  {"[>>>] ACTIVE REAL-TIME TICK PIPE [XAUUSD]:"}
                </div>
                {GENERATED_TICKS.slice(0, tickIndex + 1).map((t, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 14,
                      color: "#E2E8F0",
                      fontSize: 16,
                      backgroundColor:
                        idx === tickIndex
                          ? "rgba(245, 208, 97, 0.1)"
                          : "transparent",
                      padding: "2px 8px",
                      borderRadius: 6,
                    }}
                  >
                    <span style={{ color: TOKENS.accentCyan }}>
                      {`[15:25:${(10 + idx).toString().padStart(2, "0")}.382]`}
                    </span>
                    <span style={{ color: TOKENS.textWhite, fontWeight: 700 }}>
                      TICK #{10490 + idx}
                    </span>
                    <span style={{ color: TOKENS.accentGold }}>XAUUSD</span>
                    <span style={{ color: TOKENS.accentGreen }}>
                      BID: {t.bid}
                    </span>
                    <span style={{ color: TOKENS.accentGold }}>
                      ASK: {t.ask}
                    </span>
                    <span style={{ color: TOKENS.textDim }}>
                      VOL: {t.vol}
                    </span>
                    <span style={{ color: TOKENS.accentCyan, marginLeft: "auto" }}>
                      ⚡ {t.lat}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Holographic Terminal Scanline Overlay */}
          <div
            style={{
              position: "absolute",
              top: (frame % 60) * 6,
              left: 0,
              right: 0,
              height: 2,
              background:
                "linear-gradient(90deg, transparent, rgba(245, 208, 97, 0.35), transparent)",
              pointerEvents: "none",
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default MT5ConnectionScene;
