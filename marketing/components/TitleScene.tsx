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
  bgCard: "rgba(8, 13, 24, 0.8)",
  accentGold: "#F5D061",
  accentGoldDark: "#D4AF37",
  accentGoldGlow: "rgba(245, 208, 97, 0.45)",
  accentCyan: "#38BDF8",
  accentGreen: "#10B981",
  borderGold: "rgba(245, 208, 97, 0.28)",
  borderGoldBright: "rgba(245, 208, 97, 0.85)",
  textWhite: "#F8FAFC",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  fontMono: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
  fontSans:
    '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif',
};

// ============================================================================
// BACKGROUND: BLURRED MATRIX OF ALGORITHMIC PRICE LINES
// ============================================================================
interface PriceLineData {
  id: number;
  baseY: number;
  amplitude: number;
  frequency: number;
  speed: number;
  strokeWidth: number;
  opacity: number;
  color: string;
}

const AlgorithmicPriceLinesCanvas: React.FC = () => {
  const frame = useCurrentFrame();

  const lines: PriceLineData[] = useMemo(
    () => [
      { id: 1, baseY: 380, amplitude: 55, frequency: 0.008, speed: 0.8, strokeWidth: 2, opacity: 0.4, color: TOKENS.accentGold },
      { id: 2, baseY: 520, amplitude: 80, frequency: 0.006, speed: 1.2, strokeWidth: 2.5, opacity: 0.65, color: TOKENS.accentGold },
      { id: 3, baseY: 680, amplitude: 65, frequency: 0.009, speed: 0.6, strokeWidth: 1.8, opacity: 0.35, color: "#D4AF37" },
      { id: 4, baseY: 940, amplitude: 95, frequency: 0.005, speed: 1.0, strokeWidth: 3, opacity: 0.7, color: TOKENS.accentGold },
      { id: 5, baseY: 1180, amplitude: 70, frequency: 0.007, speed: 1.4, strokeWidth: 2, opacity: 0.45, color: TOKENS.accentCyan },
      { id: 6, baseY: 1420, amplitude: 85, frequency: 0.006, speed: 0.9, strokeWidth: 2.2, opacity: 0.5, color: TOKENS.accentGold },
    ],
    []
  );

  const width = 1080;
  const height = 1920;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        backgroundColor: TOKENS.bgCanvas,
        pointerEvents: "none",
      }}
    >
      {/* Ambient Radial Lighting Glows */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "50%",
          width: 800,
          height: 800,
          transform: "translate(-50%, -50%)",
          background: "radial-gradient(circle, rgba(245, 208, 97, 0.12) 0%, transparent 65%)",
          filter: "blur(60px)",
        }}
      />

      {/* SVG Canvas with Algorithmic Sine Splines */}
      <svg
        width={width}
        height={height}
        style={{
          position: "absolute",
          inset: 0,
          filter: "blur(3.5px)", // Blurred background aesthetic
        }}
      >
        <defs>
          <linearGradient id="goldSplineGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="rgba(245, 208, 97, 0.1)" />
            <stop offset="50%" stopColor="rgba(245, 208, 97, 0.85)" />
            <stop offset="100%" stopColor="rgba(212, 175, 55, 0.1)" />
          </linearGradient>
        </defs>

        {lines.map((line) => {
          const points: string[] = [];
          const step = 40;
          for (let x = -100; x <= width + 100; x += step) {
            const shiftX = x + frame * line.speed * 2;
            const y =
              line.baseY +
              Math.sin(shiftX * line.frequency) * line.amplitude +
              Math.cos((shiftX * line.frequency) / 2) * (line.amplitude * 0.4);
            points.push(`${x},${y.toFixed(1)}`);
          }
          const pathD = `M ${points.join(" L ")}`;

          return (
            <path
              key={line.id}
              d={pathD}
              fill="none"
              stroke="url(#goldSplineGrad)"
              strokeWidth={line.strokeWidth}
              strokeOpacity={line.opacity}
            />
          );
        })}
      </svg>

      {/* Subtle Matrix Order Dots Floating Across Chart */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            radial-gradient(circle at 50% 50%, rgba(245, 208, 97, 0.05) 1px, transparent 1px)
          `,
          backgroundSize: "44px 44px",
          opacity: 0.7,
        }}
      />
    </div>
  );
};

// ============================================================================
// DEDICATED COMPONENT: TitleScene (Scene 1: 0:00.0 to 0:03.5 | Frames 0 – 105)
// ============================================================================
export const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // --------------------------------------------------------------------------
  // Sharp Spring Scale-In Animation (Syncs with opening audio cue)
  // --------------------------------------------------------------------------
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.55 },
  });

  const subtitleSpring = spring({
    frame: frame - 8,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  const badgeSpring = spring({
    frame: frame - 16,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.6 },
  });

  // Scale in from 0.78 to 1.0, with slight continuous cinematic drift
  const scale = interpolate(titleSpring, [0, 1], [0.78, 1]) + frame * 0.0004;
  const opacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Subtle breathing pulse for gold glow
  const goldPulse = Math.sin(frame / 10) * 0.18 + 0.82;

  // Rotating outer ring for DA emblem
  const sealRotation = frame * 0.5;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 60px",
        fontFamily: TOKENS.fontSans,
        overflow: "hidden",
      }}
    >
      {/* 1. Algorithmic Background Canvas */}
      <AlgorithmicPriceLinesCanvas />

      {/* 2. Main Centralized Brand Container */}
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          zIndex: 10,
        }}
      >
        {/* Glowing DA Insignia Seal */}
        <div
          style={{
            position: "relative",
            width: 170,
            height: 170,
            marginBottom: 36,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Rotating Outer Dashed Gold Ring */}
          <div
            style={{
              position: "absolute",
              inset: -8,
              borderRadius: "50%",
              border: `2px dashed rgba(245, 208, 97, ${0.45 * goldPulse})`,
              transform: `rotate(${sealRotation}deg)`,
            }}
          />

          {/* Central Gold Medallion */}
          <div
            style={{
              width: 148,
              height: 148,
              borderRadius: "50%",
              border: `3px solid ${TOKENS.accentGold}`,
              boxShadow: `
                0 0 50px rgba(245, 208, 97, ${0.5 * goldPulse}),
                inset 0 0 30px rgba(245, 208, 97, 0.25)
              `,
              background:
                "radial-gradient(circle, rgba(245, 208, 97, 0.2) 0%, rgba(3, 5, 8, 0.95) 75%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              style={{
                fontSize: 62,
                fontWeight: 900,
                color: TOKENS.accentGold,
                letterSpacing: "-0.04em",
                fontFamily: TOKENS.fontSans,
              }}
            >
              DA
            </span>
          </div>
        </div>

        {/* Category Pill Tag */}
        <div
          style={{
            transform: `scale(${Math.max(0, badgeSpring)})`,
            opacity: Math.max(0, badgeSpring),
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 22px",
            borderRadius: 999,
            backgroundColor: "rgba(245, 208, 97, 0.12)",
            border: `1.5px solid ${TOKENS.borderGoldBright}`,
            marginBottom: 20,
            boxShadow: `0 0 20px rgba(245, 208, 97, 0.2)`,
          }}
        >
          <span style={{ fontSize: 16, color: TOKENS.accentGold }}>⚡</span>
          <span
            style={{
              fontSize: 17,
              fontWeight: 800,
              color: TOKENS.accentGold,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              fontFamily: TOKENS.fontMono,
            }}
          >
            INSTITUTIONAL QUANT PROTOCOL
          </span>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Brand Typography: "Don Aurelius"                                   */}
        {/* ------------------------------------------------------------------ */}
        <h1
          style={{
            fontSize: 92,
            fontWeight: 900,
            letterSpacing: "-0.04em",
            lineHeight: 1.05,
            margin: "0 0 16px 0",
            color: TOKENS.textWhite,
            textShadow: "0 10px 40px rgba(0, 0, 0, 0.95)",
            background: `linear-gradient(135deg, #FFFFFF 0%, #FFF5D6 50%, ${TOKENS.accentGold} 100%)`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Don Aurelius
        </h1>

        {/* ------------------------------------------------------------------ */}
        {/* Glowing Gold Subtitle: "Autonomous XAUUSD Engine"                  */}
        {/* ------------------------------------------------------------------ */}
        <div
          style={{
            transform: `translateY(${(1 - subtitleSpring) * 16}px)`,
            opacity: Math.max(0, subtitleSpring),
            display: "flex",
            alignItems: "center",
            gap: 14,
            padding: "10px 28px",
            borderRadius: 14,
            backgroundColor: "rgba(10, 16, 28, 0.65)",
            border: `1px solid rgba(245, 208, 97, 0.35)`,
            boxShadow: `0 0 35px rgba(245, 208, 97, ${0.35 * goldPulse})`,
          }}
        >
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: TOKENS.accentGold,
              boxShadow: `0 0 12px ${TOKENS.accentGold}`,
            }}
          />
          <span
            style={{
              fontSize: 26,
              fontWeight: 800,
              letterSpacing: "0.16em",
              color: TOKENS.accentGold,
              textTransform: "uppercase",
              fontFamily: TOKENS.fontMono,
              textShadow: `0 0 20px ${TOKENS.accentGoldGlow}`,
            }}
          >
            Autonomous XAUUSD Engine
          </span>
        </div>

        {/* Live Sub-Status Footer Bar */}
        <div
          style={{
            marginTop: 48,
            display: "flex",
            gap: 20,
            opacity: Math.max(0, badgeSpring),
          }}
        >
          {[
            { label: "Execution Engine", val: "Sub-0.4ms IPC", color: TOKENS.accentCyan },
            { label: "Target Asset", val: "XAU/USD Gold Spot", color: TOKENS.accentGold },
            { label: "Deployment Envelope", val: "60-Second Setup", color: TOKENS.accentGreen },
          ].map((item, idx) => (
            <div
              key={idx}
              style={{
                padding: "12px 22px",
                borderRadius: 12,
                backgroundColor: TOKENS.bgCard,
                border: `1px solid ${TOKENS.borderGold}`,
                display: "flex",
                flexDirection: "column",
                gap: 2,
              }}
            >
              <span style={{ fontSize: 13, color: TOKENS.textDim, fontFamily: TOKENS.fontMono }}>
                {item.label}
              </span>
              <span
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: item.color,
                  fontFamily: TOKENS.fontMono,
                }}
              >
                {item.val}
              </span>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default TitleScene;
