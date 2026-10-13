import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene2BentoCards: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for cards
  const cardsEntrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.8 },
  });

  // Outward glide when text pops
  const textPopFrame = 22; // relative to scene start
  const textSpring = spring({
    frame: frame - textPopFrame,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.6 },
  });

  // Outward expansion of cards
  const cardSpread = interpolate(
    frame,
    [textPopFrame, textPopFrame + 18],
    [0, 260],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Floating levitation for the cards & badge
  const floatY = Math.sin(frame * 0.1) * 6;
  const badgeFloatY = Math.cos(frame * 0.12) * 8;

  // Arc progress for radar widget in left card
  const arcProgress = interpolate(frame % 40, [0, 40], [0, 100]);

  // Exit transition
  const exitOpacity = interpolate(frame, [76, 84], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitScale = interpolate(frame, [74, 84], [1, 1.06], {
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
      {/* Luminous violet ambient glow */}
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(124, 58, 237, 0.32) 0%, rgba(99, 102, 241, 0.15) 40%, rgba(7, 8, 13, 0) 70%)",
          filter: "blur(40px)",
          pointerEvents: "none",
        }}
      />

      {/* Cards container */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 24,
          position: "relative",
          zIndex: 2,
          transform: `scale(${cardsEntrance}) translateY(${floatY}px)`,
        }}
      >
        {/* Left Card: Pure White Squircle with Live Radar Widget */}
        <div
          style={{
            width: 330,
            height: 330,
            borderRadius: 52,
            backgroundColor: "#FFFFFF",
            boxShadow:
              "0 25px 60px -12px rgba(0, 0, 0, 0.6), 0 0 45px rgba(139, 92, 246, 0.25)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: 22,
            position: "relative",
            transform: `rotate(-2deg) translateX(${-cardSpread}px)`,
          }}
        >
          {/* Inner dark pod */}
          <div
            style={{
              width: "100%",
              height: "100%",
              backgroundColor: "#10131F",
              borderRadius: 36,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "20px 18px",
              boxShadow: "inset 0 2px 6px rgba(255, 255, 255, 0.1)",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
              }}
            >
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: "#94A3B8",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}
              >
                XAU/USD MT5
              </span>
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: "#10B981",
                  boxShadow: "0 0 8px #10B981",
                }}
              />
            </div>

            {/* Glowing Semicircular Arc (matching ref_frame_5) */}
            <div
              style={{
                width: 170,
                height: 85,
                position: "relative",
                display: "flex",
                alignItems: "flex-end",
                justifyContent: "center",
              }}
            >
              <svg width="170" height="90" viewBox="0 0 170 90">
                <path
                  d="M 15 80 A 70 70 0 0 1 155 80"
                  fill="none"
                  stroke="#1E293B"
                  strokeWidth="8"
                  strokeLinecap="round"
                />
                <path
                  d="M 15 80 A 70 70 0 0 1 155 80"
                  fill="none"
                  stroke="url(#arcGradient)"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray="220"
                  strokeDashoffset={220 - (arcProgress / 100) * 220}
                />
                <defs>
                  <linearGradient
                    id="arcGradient"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="0%"
                  >
                    <stop offset="0%" stopColor="#38BDF8" />
                    <stop offset="50%" stopColor="#818CF8" />
                    <stop offset="100%" stopColor="#C084FC" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Glowing Indicator Dot at Arc Base */}
              <div
                style={{
                  position: "absolute",
                  bottom: -6,
                  width: 18,
                  height: 18,
                  borderRadius: "50%",
                  backgroundColor: "#38BDF8",
                  boxShadow:
                    "0 0 16px #38BDF8, 0 0 30px rgba(56, 189, 248, 0.8)",
                  border: "3px solid #FFFFFF",
                }}
              />
            </div>

            {/* Metric Footer */}
            <div style={{ textAlign: "center", marginTop: 4 }}>
              <div
                style={{
                  fontSize: 22,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  letterSpacing: "-0.02em",
                }}
              >
                0.38ms Latency
              </div>
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#38BDF8",
                  marginTop: 2,
                }}
              >
                Direct Institutional Bridge
              </div>
            </div>
          </div>
        </div>

        {/* Floating Pill Badge above Right Card (matching ref_frame_6) */}
        <div
          style={{
            position: "absolute",
            right: 40 - cardSpread,
            top: -55 + badgeFloatY,
            backgroundColor: "#2E1065",
            border: "1px solid rgba(167, 139, 250, 0.5)",
            borderRadius: 9999,
            padding: "8px 20px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            boxShadow: "0 10px 25px rgba(124, 58, 237, 0.4)",
            zIndex: 10,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              backgroundColor: "#A855F7",
              boxShadow: "0 0 8px #A855F7",
            }}
          />
          <span
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: "#EDE9FE",
              letterSpacing: "0.02em",
            }}
          >
            Alpha Engine
          </span>
        </div>

        {/* Right Card: Soft Lavender/Violet Squircle with Live Candlestick & Profit */}
        <div
          style={{
            width: 330,
            height: 330,
            borderRadius: 52,
            background:
              "linear-gradient(145deg, #7C3AED 0%, #6366F1 50%, #4F46E5 100%)",
            boxShadow:
              "0 25px 60px -12px rgba(99, 102, 241, 0.5), 0 0 45px rgba(124, 58, 237, 0.3)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "space-between",
            padding: 24,
            position: "relative",
            transform: `rotate(2deg) translateX(${cardSpread}px)`,
            overflow: "hidden",
          }}
        >
          {/* Subtle specular glass highlight */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "40%",
              background:
                "linear-gradient(180deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 100%)",
              borderRadius: "52px 52px 0 0",
              pointerEvents: "none",
            }}
          />

          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              zIndex: 2,
            }}
          >
            <span
              style={{
                fontSize: 13,
                fontWeight: 800,
                color: "#E0E7FF",
                letterSpacing: "0.06em",
              }}
            >
              WIN RATE 89.4%
            </span>
            <span
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                padding: "3px 10px",
                borderRadius: 9999,
                fontSize: 11,
                fontWeight: 700,
                color: "#FFFFFF",
              }}
            >
              LIVE
            </span>
          </div>

          {/* Golden Profit Wave Curve */}
          <div style={{ width: "100%", height: 110, position: "relative" }}>
            <svg width="100%" height="110" viewBox="0 0 280 110">
              <defs>
                <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FDE047" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#FDE047" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path
                d="M 10 90 Q 70 70 120 75 T 200 40 T 270 15 L 270 110 L 10 110 Z"
                fill="url(#profitGrad)"
              />
              <path
                d="M 10 90 Q 70 70 120 75 T 200 40 T 270 15"
                fill="none"
                stroke="#FDE047"
                strokeWidth="4"
                strokeLinecap="round"
              />
              <circle
                cx="270"
                cy="15"
                r="6"
                fill="#FFFFFF"
                stroke="#FDE047"
                strokeWidth="3"
              />
            </svg>
          </div>

          {/* Metric Bottom */}
          <div style={{ textAlign: "center", zIndex: 2, width: "100%" }}>
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: "-0.03em",
                textShadow: "0 2px 10px rgba(0, 0, 0, 0.3)",
              }}
            >
              +380.4 Pips
            </div>
            <div
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: "#DDD6FE",
                marginTop: 2,
              }}
            >
              Gold Momentum Harvest
            </div>
          </div>
        </div>
      </div>

      {/* Kinetic Centered Text: "better trades" (matching "better motion") */}
      {frame >= textPopFrame && (
        <div
          style={{
            position: "absolute",
            zIndex: 5,
            fontSize: 64,
            fontWeight: 700,
            color: "#EDE9FE",
            letterSpacing: "-0.03em",
            textAlign: "center",
            opacity: interpolate(textSpring, [0, 1], [0, 1]),
            transform: `scale(${textSpring})`,
            textShadow:
              "0 0 35px rgba(167, 139, 250, 0.9), 0 4px 15px rgba(0, 0, 0, 0.8)",
          }}
        >
          better trades
        </div>
      )}
    </div>
  );
};
