import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Act5TerminalTelemetry: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Part 1: Telemetry Dashboard (0 - 250)
  const isPart1 = frame < 250;
  const card1Spring = spring({ frame, fps, config: { damping: 13, stiffness: 120, mass: 0.8 } });

  const profitCounter = interpolate(frame, [15, 140], [0, 148920.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const winRateCounter = interpolate(frame, [25, 120], [50, 89.4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Part 2: Terminal Deployment (230 - 510)
  const isPart2 = frame >= 220;
  const terminalFrame = frame - 230;
  const terminalSpring = spring({
    frame: terminalFrame,
    fps,
    config: { damping: 12, stiffness: 130, mass: 0.7 },
  });

  // Typewriter steps
  const typeStep1 = terminalFrame >= 20;
  const typeStep2 = terminalFrame >= 60;
  const typeStep3 = terminalFrame >= 100;
  const typeStep4 = terminalFrame >= 140;

  // Pulse wave on activation
  const pulseScale = interpolate(terminalFrame, [160, 220], [1, 1.05], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Animated cursor clicking activate
  const cursorX = interpolate(terminalFrame, [180, 210], [180, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY = interpolate(terminalFrame, [180, 210], [160, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const isClick = terminalFrame >= 210 && terminalFrame <= 220;

  // Exit transition
  const exitOpacity = interpolate(frame, [490, 510], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#07080D",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        opacity: exitOpacity,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* Background ambient lighting */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(124, 58, 237, 0.25) 0%, rgba(253, 224, 71, 0.1) 45%, rgba(7, 8, 13, 0) 75%)",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* PART 1: Verified Telemetry Card */}
      {isPart1 && (
        <div
          style={{
            zIndex: 5,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "90%",
            maxWidth: 960,
            transform: `scale(${card1Spring})`,
            opacity: interpolate(frame, [220, 250], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "inline-block",
              padding: "8px 24px",
              borderRadius: 9999,
              backgroundColor: "rgba(16, 185, 129, 0.2)",
              border: "1px solid rgba(16, 185, 129, 0.5)",
              color: "#6EE7B7",
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: "0.08em",
              marginBottom: 16,
              textTransform: "uppercase",
            }}
          >
            Verified Performance Matrix
          </div>
          <div
            style={{
              fontSize: 60,
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "-0.03em",
              marginBottom: 36,
              textAlign: "center",
            }}
          >
            DOCUMENTED LIVE RESULTS
          </div>

          {/* Telemetry Bento Card */}
          <div
            style={{
              width: "100%",
              backgroundColor: "#111425",
              border: "1px solid rgba(124, 58, 237, 0.4)",
              borderRadius: 48,
              padding: "40px 36px",
              boxShadow: "0 30px 70px rgba(0, 0, 0, 0.8), 0 0 50px rgba(124, 58, 237, 0.25)",
              display: "flex",
              flexDirection: "column",
              gap: 32,
            }}
          >
            {/* Top Stat Row */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 16, color: "#94A3B8", fontWeight: 700 }}>
                  TOTAL NET GAIN (MT5 LIVE AUDITED)
                </div>
                <div
                  style={{
                    fontSize: 64,
                    fontWeight: 900,
                    color: "#FDE047",
                    marginTop: 4,
                    letterSpacing: "-0.03em",
                    textShadow: "0 0 40px rgba(253, 224, 71, 0.6)",
                  }}
                >
                  +${profitCounter.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  border: "1px solid #10B981",
                  padding: "10px 22px",
                  borderRadius: 9999,
                  color: "#6EE7B7",
                  fontSize: 16,
                  fontWeight: 800,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span>✓</span> MYFXBOOK VERIFIED
              </div>
            </div>

            {/* Sub-Metrics Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
              <div style={{ backgroundColor: "#171B33", padding: 20, borderRadius: 24, textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#94A3B8", fontWeight: 700 }}>WIN RATE</div>
                <div style={{ fontSize: 36, fontWeight: 900, color: "#10B981", marginTop: 4 }}>
                  {winRateCounter.toFixed(1)}%
                </div>
                <div style={{ fontSize: 12, color: "#6EE7B7" }}>2,450 Trades</div>
              </div>

              <div style={{ backgroundColor: "#171B33", padding: 20, borderRadius: 24, textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#94A3B8", fontWeight: 700 }}>PROFIT FACTOR</div>
                <div style={{ fontSize: 36, fontWeight: 900, color: "#38BDF8", marginTop: 4 }}>
                  3.82
                </div>
                <div style={{ fontSize: 12, color: "#7DD3FC" }}>Institutional Alpha</div>
              </div>

              <div style={{ backgroundColor: "#171B33", padding: 20, borderRadius: 24, textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#94A3B8", fontWeight: 700 }}>SHARPE RATIO</div>
                <div style={{ fontSize: 36, fontWeight: 900, color: "#A855F7", marginTop: 4 }}>
                  4.15
                </div>
                <div style={{ fontSize: 12, color: "#D8B4FE" }}>Risk-Adjusted</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PART 2: Terminal 1-Click Deployment Shell */}
      {isPart2 && (
        <div
          style={{
            zIndex: 6,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "90%",
            maxWidth: 960,
            transform: `scale(${terminalSpring * pulseScale})`,
            opacity: interpolate(terminalFrame, [0, 15], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {/* Header */}
          <div
            style={{
              fontSize: 60,
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "-0.03em",
              marginBottom: 30,
              textAlign: "center",
            }}
          >
            DEPLOY IN SECONDS
          </div>

          {/* IDE Terminal Window */}
          <div
            style={{
              width: "100%",
              backgroundColor: "#0B0D17",
              border: "2px solid rgba(124, 58, 237, 0.6)",
              borderRadius: 36,
              overflow: "hidden",
              boxShadow: "0 35px 80px rgba(0, 0, 0, 0.9), 0 0 60px rgba(124, 58, 237, 0.35)",
            }}
          >
            {/* Window Titlebar */}
            <div
              style={{
                backgroundColor: "#16192B",
                padding: "16px 22px",
                display: "flex",
                alignItems: "center",
                gap: 10,
                borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
              }}
            >
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#EF4444" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#10B981" }} />
              <div
                style={{
                  flex: 1,
                  textAlign: "center",
                  fontSize: 14,
                  fontWeight: 600,
                  color: "#94A3B8",
                  fontFamily: "monospace",
                }}
              >
                bash ~ don-aurelius-deploy
              </div>
            </div>

            {/* Terminal Body */}
            <div
              style={{
                padding: "32px 30px",
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 18,
                lineHeight: 1.8,
                color: "#E2E8F0",
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              {typeStep1 && (
                <div style={{ color: "#FDE047" }}>
                  $ curl -fsSL https://get.donaurelius.ai | bash
                </div>
              )}
              {typeStep2 && (
                <div style={{ color: "#38BDF8" }}>
                  &gt; [AI CORE] Initializing Quantum Neural Engine... <span style={{ color: "#10B981" }}>[OK]</span>
                </div>
              )}
              {typeStep3 && (
                <div style={{ color: "#C084FC" }}>
                  &gt; [MT5 BRIDGE] Connected to London LD4 (0.38ms)... <span style={{ color: "#10B981" }}>[OK]</span>
                </div>
              )}
              {typeStep4 && (
                <div
                  style={{
                    backgroundColor: "rgba(16, 185, 129, 0.2)",
                    border: "1px solid #10B981",
                    padding: "12px 18px",
                    borderRadius: 16,
                    color: "#6EE7B7",
                    fontWeight: 700,
                    marginTop: 10,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <span>🟢 STATUS: LIVE TRADING ACTIVE - GENERATING ALPHA</span>
                  <span
                    style={{
                      backgroundColor: "#10B981",
                      color: "#000000",
                      padding: "4px 14px",
                      borderRadius: 9999,
                      fontSize: 12,
                      fontWeight: 900,
                    }}
                  >
                    100% PASS
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
