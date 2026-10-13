import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Act4RiskMatrix: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const mainSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.8 },
  });

  // Animated Monte Carlo trajectories progress
  const simProgress = interpolate(frame, [20, 160], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Floating shield rotation/bobbing
  const shieldFloat = Math.sin(frame * 0.1) * 8;
  const shieldGlow = (Math.sin(frame * 0.15) + 1) * 0.5;

  // Probability counter rolling up
  const probCount = interpolate(frame, [30, 140], [80.0, 99.4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Typography spring
  const textSpring = spring({ frame: frame - 220, fps, config: { damping: 10, stiffness: 160 } });

  // Exit transition to Act 5
  const exitOpacity = interpolate(frame, [490, 510], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitScale = interpolate(frame, [480, 510], [1, 1.08], {
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
      {/* Background radial gold/emerald glow */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(16, 185, 129, 0.22) 0%, rgba(253, 224, 71, 0.12) 40%, rgba(7, 8, 13, 0) 75%)",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Top Header */}
      <div
        style={{
          zIndex: 5,
          textAlign: "center",
          marginBottom: 32,
        }}
      >
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
            marginBottom: 12,
            textTransform: "uppercase",
          }}
        >
          Institutional Risk Engine
        </div>
        <div
          style={{
            fontSize: 58,
            fontWeight: 900,
            color: "#FFFFFF",
            letterSpacing: "-0.03em",
            textShadow: "0 0 35px rgba(255, 255, 255, 0.3)",
          }}
        >
          MONTE CARLO PROOF MATRIX
        </div>
      </div>

      {/* Dashboard Card Container */}
      <div
        style={{
          zIndex: 4,
          display: "flex",
          flexDirection: "column",
          gap: 24,
          width: "90%",
          maxWidth: 960,
          transform: `scale(${mainSpring})`,
        }}
      >
        {/* Card 1: 10,000 Monte Carlo Simulation Fan */}
        <div
          style={{
            backgroundColor: "#111424",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            borderRadius: 44,
            padding: "32px 30px",
            boxShadow:
              "0 25px 60px rgba(0, 0, 0, 0.7), 0 0 45px rgba(16, 185, 129, 0.2)",
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 13, color: "#94A3B8", fontWeight: 700 }}>
                10,000 TRAJECTORY SIMULATIONS (2020 - 2026)
              </span>
              <div style={{ fontSize: 36, fontWeight: 900, color: "#10B981", marginTop: 4 }}>
                {probCount.toFixed(1)}% PROFITABLE OUTCOMES
              </div>
            </div>
            <div
              style={{
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                padding: "8px 20px",
                borderRadius: 9999,
                color: "#34D399",
                fontSize: 14,
                fontWeight: 800,
              }}
            >
              MAX DD: 1.84%
            </div>
          </div>

          {/* Monte Carlo Fan SVG */}
          <div style={{ width: "100%", height: 160, position: "relative" }}>
            <svg width="100%" height="160" viewBox="0 0 540 160">
              {/* Baseline */}
              <line x1="20" y1="140" x2="520" y2="140" stroke="#334155" strokeWidth="2" />
              {/* Animated Fan Trajectories */}
              {[
                { d: "M 20 140 Q 150 120 280 80 T 520 20", stroke: "#10B981", w: 4 },
                { d: "M 20 140 Q 160 125 300 90 T 520 35", stroke: "#34D399", w: 2.5 },
                { d: "M 20 140 Q 140 115 270 70 T 520 15", stroke: "#FDE047", w: 3 },
                { d: "M 20 140 Q 170 130 320 100 T 520 50", stroke: "#06B6D4", w: 2 },
                { d: "M 20 140 Q 150 128 290 95 T 520 40", stroke: "#A78BFA", w: 2 },
                { d: "M 20 140 Q 180 135 340 110 T 520 65", stroke: "#10B981", w: 1.5 },
              ].map((path, idx) => (
                <path
                  key={idx}
                  d={path.d}
                  fill="none"
                  stroke={path.stroke}
                  strokeWidth={path.w}
                  strokeLinecap="round"
                  strokeDasharray="600"
                  strokeDashoffset={600 - simProgress * 600}
                />
              ))}
            </svg>
          </div>
        </div>

        {/* Card 2: Automatic News Blackout & Kelly Criterion Protection */}
        <div
          style={{
            backgroundColor: "#13172E",
            border: "1px solid rgba(124, 58, 237, 0.4)",
            borderRadius: 44,
            padding: "28px 30px",
            boxShadow: "0 25px 60px rgba(0, 0, 0, 0.7)",
            display: "flex",
            alignItems: "center",
            gap: 28,
          }}
        >
          {/* Animated 3D Shield Icon */}
          <div
            style={{
              width: 100,
              height: 100,
              borderRadius: 30,
              backgroundColor: "#2E1065",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 48,
              boxShadow: `0 0 ${30 + shieldGlow * 30}px rgba(167, 139, 250, 0.6)`,
              transform: `translateY(${shieldFloat}px)`,
              border: "2px solid rgba(167, 139, 250, 0.5)",
              flexShrink: 0,
            }}
          >
            🛡️
          </div>

          {/* Feature Breakdown */}
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#FFFFFF" }}>
              AUTOMATIC NEWS DEFENSE PROTOCOL
            </div>
            <div style={{ fontSize: 15, color: "#94A3B8", marginTop: 4, lineHeight: 1.4 }}>
              Bot enters auto-sleep mode 15 minutes before NFP, CPI & FOMC rate decisions. Zero volatile liquidation exposure.
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 14 }}>
              <span
                style={{
                  backgroundColor: "rgba(124, 58, 237, 0.25)",
                  padding: "6px 14px",
                  borderRadius: 9999,
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#DDD6FE",
                }}
              >
                🔒 Strict Kelly Criterion
              </span>
              <span
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.25)",
                  padding: "6px 14px",
                  borderRadius: 9999,
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#6EE7B7",
                }}
              >
                🔒 Max 0.75% Risk Per Trade
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Kinetic Typography Bottom */}
      {frame >= 220 && (
        <div
          style={{
            position: "absolute",
            bottom: 70,
            zIndex: 6,
            textAlign: "center",
            transform: `scale(${textSpring})`,
            opacity: interpolate(textSpring, [0, 1], [0, 1]),
          }}
        >
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              color: "#FDE047",
              letterSpacing: "-0.02em",
              textShadow: "0 0 35px rgba(253, 224, 71, 0.7)",
            }}
          >
            MATHEMATICAL RIGOR. ZERO GAMBLING.
          </div>
        </div>
      )}
    </div>
  );
};
