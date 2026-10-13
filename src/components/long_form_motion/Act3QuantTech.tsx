import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Act3QuantTech: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for cards
  const gridSpring = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 120, mass: 0.8 },
  });

  // Radar sweep angle
  const radarSweep = (frame * 5) % 360;

  // Candlestick trade trigger progress
  const tradeTrigger = frame >= 120;
  const pipsCounter = interpolate(frame, [120, 240], [0, 480.4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const profitCounter = interpolate(frame, [120, 240], [0, 6840], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Kinetic typography switches
  const isTextPhase2 = frame >= 260;
  const text1Spring = spring({ frame: frame - 20, fps, config: { damping: 10, stiffness: 160 } });
  const text2Spring = spring({ frame: frame - 280, fps, config: { damping: 10, stiffness: 160 } });

  // Floating levitation
  const floatY = Math.sin(frame * 0.08) * 8;

  // Exit transition
  const exitOpacity = interpolate(frame, [520, 540], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitScale = interpolate(frame, [510, 540], [1, 1.1], {
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
        transform: `scale(${exitScale})`,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* Luminous violet / cyan ambient bloom */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(124, 58, 237, 0.28) 0%, rgba(6, 182, 212, 0.15) 45%, rgba(7, 8, 13, 0) 75%)",
          filter: "blur(50px)",
          pointerEvents: "none",
        }}
      />

      {/* Top Section Header */}
      <div
        style={{
          zIndex: 5,
          textAlign: "center",
          marginBottom: 36,
          transform: `scale(${text1Spring})`,
          opacity: interpolate(text1Spring, [0, 1], [0, 1]),
        }}
      >
        <div
          style={{
            display: "inline-block",
            padding: "8px 24px",
            borderRadius: 9999,
            backgroundColor: "rgba(124, 58, 237, 0.2)",
            border: "1px solid rgba(167, 139, 250, 0.4)",
            color: "#C4B5FD",
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: "0.08em",
            marginBottom: 12,
            textTransform: "uppercase",
          }}
        >
          Proprietary Quant Architecture
        </div>
        <div
          style={{
            fontSize: 60,
            fontWeight: 900,
            color: "#FFFFFF",
            letterSpacing: "-0.03em",
            textShadow: "0 0 35px rgba(255, 255, 255, 0.3)",
          }}
        >
          ORDER FLOW INTELLIGENCE
        </div>
      </div>

      {/* Bento Grid Container */}
      <div
        style={{
          zIndex: 4,
          display: "flex",
          flexDirection: "column",
          gap: 24,
          width: "90%",
          maxWidth: 960,
          transform: `scale(${gridSpring}) translateY(${floatY}px)`,
        }}
      >
        {/* Top Row: Dual Bento Cards */}
        <div style={{ display: "flex", gap: 24, width: "100%" }}>
          {/* Card 1: Liquidity Void Radar (Left) */}
          <div
            style={{
              flex: 1,
              backgroundColor: "#111322",
              border: "1px solid rgba(124, 58, 237, 0.4)",
              borderRadius: 44,
              padding: "28px 26px",
              boxShadow:
                "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(124, 58, 237, 0.2)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              height: 380,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 800,
                  color: "#94A3B8",
                  letterSpacing: "0.06em",
                }}
              >
                LIQUIDITY VOID RADAR
              </span>
              <span
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  color: "#10B981",
                  padding: "4px 12px",
                  borderRadius: 9999,
                  fontSize: 12,
                  fontWeight: 800,
                }}
              >
                SCANNING
              </span>
            </div>

            {/* Scanning Radar Graphic */}
            <div
              style={{
                width: "100%",
                height: 180,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
              }}
            >
              {/* Radar Rings */}
              <div
                style={{
                  width: 170,
                  height: 170,
                  borderRadius: "50%",
                  border: "1px solid rgba(124, 58, 237, 0.4)",
                  position: "relative",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    width: 110,
                    height: 110,
                    borderRadius: "50%",
                    border: "1px dashed rgba(6, 182, 212, 0.5)",
                  }}
                />
                <div
                  style={{
                    width: 50,
                    height: 50,
                    borderRadius: "50%",
                    border: "1px solid rgba(124, 58, 237, 0.7)",
                  }}
                />
                {/* Rotating Sweep Needle */}
                <div
                  style={{
                    position: "absolute",
                    width: "50%",
                    height: 2,
                    background:
                      "linear-gradient(90deg, rgba(6, 182, 212, 0) 0%, #06B6D4 100%)",
                    top: "50%",
                    left: "50%",
                    transformOrigin: "left center",
                    transform: `rotate(${radarSweep}deg)`,
                    boxShadow: "0 0 12px #06B6D4",
                  }}
                />
                {/* Detected Target Blip */}
                <div
                  style={{
                    position: "absolute",
                    top: 45,
                    right: 45,
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    backgroundColor: "#FDE047",
                    boxShadow: "0 0 16px #FDE047",
                  }}
                />
              </div>
            </div>

            {/* Detection Info Footer */}
            <div style={{ backgroundColor: "rgba(0, 0, 0, 0.3)", padding: 14, borderRadius: 20 }}>
              <div style={{ fontSize: 13, color: "#94A3B8" }}>IMBALANCE ZONE</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: "#FFFFFF", marginTop: 2 }}>
                XAU/USD FVG: 2,642.10
              </div>
            </div>
          </div>

          {/* Card 2: 0.38ms Direct Institutional Bridge (Right) */}
          <div
            style={{
              flex: 1,
              background:
                "linear-gradient(145deg, #1A1333 0%, #0F172A 100%)",
              border: "1px solid rgba(6, 182, 212, 0.4)",
              borderRadius: 44,
              padding: "28px 26px",
              boxShadow:
                "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(6, 182, 212, 0.15)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              height: 380,
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 800,
                  color: "#94A3B8",
                  letterSpacing: "0.06em",
                }}
              >
                MT5 HIGH-SPEED BRIDGE
              </span>
              <span
                style={{
                  backgroundColor: "rgba(6, 182, 212, 0.2)",
                  color: "#38BDF8",
                  padding: "4px 12px",
                  borderRadius: 9999,
                  fontSize: 12,
                  fontWeight: 800,
                }}
              >
                LD4 EQUINIX
              </span>
            </div>

            {/* Glowing Latency Display */}
            <div style={{ textAlign: "center", margin: "auto 0" }}>
              <div
                style={{
                  fontSize: 76,
                  fontWeight: 900,
                  color: "#38BDF8",
                  letterSpacing: "-0.04em",
                  textShadow: "0 0 40px rgba(56, 189, 248, 0.6)",
                }}
              >
                0.38ms
              </div>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: "#E2E8F0",
                  marginTop: 6,
                }}
              >
                Direct FIX Protocol Latency
              </div>
            </div>

            {/* Metrics Grid */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-around",
                backgroundColor: "rgba(0, 0, 0, 0.3)",
                padding: 14,
                borderRadius: 20,
              }}
            >
              <div>
                <div style={{ fontSize: 11, color: "#94A3B8" }}>FILL RATE</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: "#10B981" }}>99.98%</div>
              </div>
              <div>
                <div style={{ fontSize: 11, color: "#94A3B8" }}>SLIPPAGE</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: "#38BDF8" }}>0.0 Pips</div>
              </div>
              <div>
                <div style={{ fontSize: 11, color: "#94A3B8" }}>SERVER</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: "#E2E8F0" }}>London</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Full-Width Card: Live Snipe Execution */}
        <div
          style={{
            width: "100%",
            backgroundColor: "#131627",
            border: "1px solid rgba(253, 224, 71, 0.5)",
            borderRadius: 44,
            padding: "28px 32px",
            boxShadow:
              "0 20px 50px rgba(0, 0, 0, 0.7), 0 0 45px rgba(253, 224, 71, 0.2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span
                style={{
                  backgroundColor: "#15803D",
                  color: "#FFFFFF",
                  padding: "4px 14px",
                  borderRadius: 9999,
                  fontSize: 13,
                  fontWeight: 800,
                }}
              >
                LIVE SNIPE
              </span>
              <span style={{ fontSize: 16, fontWeight: 700, color: "#94A3B8" }}>
                XAU/USD M5 • BUY ENTRY 2,642.50
              </span>
            </div>
            <div
              style={{
                fontSize: 48,
                fontWeight: 900,
                color: "#10B981",
                marginTop: 8,
                letterSpacing: "-0.02em",
                textShadow: "0 0 30px rgba(16, 185, 129, 0.5)",
              }}
            >
              +{pipsCounter.toFixed(1)} Pips (+${profitCounter.toFixed(2)})
            </div>
          </div>

          <div
            style={{
              padding: "16px 28px",
              borderRadius: 24,
              backgroundColor: "rgba(253, 224, 71, 0.15)",
              border: "1px solid #FDE047",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 800, color: "#FDE047" }}>STATUS</div>
            <div style={{ fontSize: 20, fontWeight: 900, color: "#FFFFFF", marginTop: 4 }}>
              TAKE PROFIT HIT 🎯
            </div>
          </div>
        </div>
      </div>

      {/* Kinetic Typography Switch for Phase 2 */}
      {isTextPhase2 && (
        <div
          style={{
            position: "absolute",
            bottom: 80,
            zIndex: 6,
            textAlign: "center",
            transform: `scale(${text2Spring})`,
            opacity: interpolate(text2Spring, [0, 1], [0, 1]),
          }}
        >
          <div
            style={{
              fontSize: 52,
              fontWeight: 900,
              color: "#FDE047",
              textShadow: "0 0 35px rgba(253, 224, 71, 0.7)",
            }}
          >
            FRONT-RUNNING WALL STREET ALGORITHMS
          </div>
        </div>
      )}
    </div>
  );
};
