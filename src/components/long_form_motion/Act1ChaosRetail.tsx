import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Act1ChaosRetail: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Glitch pixel matrix
  const glitchBoxes = [
    { x: -220, y: -160, w: 120, h: 48, color: "#6D28D9", delay: 0, dur: 35 },
    { x: 180, y: -90, w: 140, h: 56, color: "#4F46E5", delay: 8, dur: 40 },
    { x: -260, y: 70, w: 95, h: 60, color: "#EF4444", delay: 15, dur: 38 },
    { x: -110, y: 140, w: 110, h: 52, color: "#5B21B6", delay: 20, dur: 32 },
    { x: 200, y: 160, w: 130, h: 62, color: "#DC2626", delay: 28, dur: 36 },
    { x: -40, y: -240, w: 150, h: 50, color: "#7C3AED", delay: 35, dur: 30 },
  ];

  // Part 1: "hey" -> "still trading gold manually?" (0 - 150)
  const isPart1 = frame < 150;
  const heySpring = spring({ frame, fps, config: { damping: 10, stiffness: 150, mass: 0.6 } });
  const hookWords = ["still", "trading", "gold", "manually?"];
  const hookSprings = hookWords.map((_, i) =>
    spring({ frame: frame - 40 - i * 8, fps, config: { damping: 12, stiffness: 180, mass: 0.5 } })
  );

  // Part 2: Liquidation Card & Brutal Stat (150 - 300)
  const isPart2 = frame >= 140 && frame < 310;
  const alertCardSpring = spring({
    frame: frame - 145,
    fps,
    config: { damping: 11, stiffness: 140, mass: 0.7 },
  });
  const shakeX = frame >= 150 && frame < 280 ? Math.sin(frame * 1.8) * 8 : 0;
  const shakeY = frame >= 150 && frame < 280 ? Math.cos(frame * 2.2) * 6 : 0;

  // Loss counter in card
  const lossAmount = interpolate(frame, [155, 230], [0, 3450], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Part 3: The Hard Truth & Pivot (300 - 450)
  const isPart3 = frame >= 300;
  const p3Progress = frame - 300;
  const text1Spring = spring({ frame: p3Progress, fps, config: { damping: 10, stiffness: 160, mass: 0.6 } });
  const text2Spring = spring({ frame: p3Progress - 45, fps, config: { damping: 10, stiffness: 160, mass: 0.6 } });
  const text3Spring = spring({ frame: p3Progress - 90, fps, config: { damping: 10, stiffness: 170, mass: 0.6 } });

  // Act exit
  const exitScale = interpolate(frame, [430, 450], [1, 1.15], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitOpacity = interpolate(frame, [440, 450], [1, 0], {
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
      {/* Background ambient red/purple pulse for tension */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background:
            frame > 150
              ? "radial-gradient(circle, rgba(239, 68, 68, 0.22) 0%, rgba(124, 58, 237, 0.12) 50%, rgba(7, 8, 13, 0) 75%)"
              : "radial-gradient(circle, rgba(124, 58, 237, 0.25) 0%, rgba(7, 8, 13, 0) 70%)",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Glitch pixel rects */}
      {frame < 120 &&
        glitchBoxes.map((box, i) => {
          const localFrame = frame - box.delay;
          if (localFrame < 0 || localFrame > box.dur) return null;
          const boxOpacity = interpolate(
            localFrame,
            [0, 3, box.dur - 5, box.dur],
            [0, 0.8, 0.8, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          );
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `calc(50% + ${box.x}px)`,
                top: `calc(50% + ${box.y}px)`,
                width: box.w,
                height: box.h,
                backgroundColor: box.color,
                borderRadius: 6,
                opacity: boxOpacity,
                boxShadow: `0 0 25px ${box.color}`,
              }}
            />
          );
        })}

      {/* PART 1: The Hook */}
      {isPart1 && (
        <div style={{ textAlign: "center", zIndex: 5, padding: "0 60px" }}>
          {frame < 40 ? (
            <div
              style={{
                fontSize: 96,
                fontWeight: 800,
                color: "#FFFFFF",
                letterSpacing: "-0.04em",
                transform: `scale(${heySpring})`,
                textShadow: "0 4px 30px rgba(124, 58, 237, 0.6)",
              }}
            >
              hey
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 20,
              }}
            >
              <div
                style={{
                  fontSize: 76,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  letterSpacing: "-0.03em",
                  lineHeight: 1.15,
                }}
              >
                {hookWords.map((word, idx) => {
                  const sp = hookSprings[idx];
                  const translateY = interpolate(sp, [0, 1], [40, 0]);
                  const opacity = interpolate(sp, [0, 1], [0, 1]);
                  const isGold = word === "gold";
                  return (
                    <span
                      key={idx}
                      style={{
                        display: "inline-block",
                        margin: "0 10px",
                        opacity,
                        transform: `translateY(${translateY}px) scale(${sp})`,
                        color: isGold ? "#FDE047" : "#FFFFFF",
                        textShadow: isGold
                          ? "0 0 35px rgba(253, 224, 71, 0.8)"
                          : "0 4px 20px rgba(0, 0, 0, 0.5)",
                      }}
                    >
                      {word}
                    </span>
                  );
                })}
              </div>
              {frame >= 100 && (
                <div
                  style={{
                    marginTop: 30,
                    padding: "12px 28px",
                    borderRadius: 9999,
                    backgroundColor: "rgba(239, 68, 68, 0.2)",
                    border: "1px solid rgba(239, 68, 68, 0.5)",
                    color: "#FCA5A5",
                    fontSize: 24,
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                  }}
                >
                  ⚠️ 94.2% RETAIL TRADERS FAIL
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* PART 2: Brutal Liquidation Card */}
      {isPart2 && (
        <div
          style={{
            zIndex: 6,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            transform: `scale(${alertCardSpring}) translate(${shakeX}px, ${shakeY}px)`,
            opacity: interpolate(frame, [140, 150, 290, 310], [0, 1, 1, 0]),
            width: "90%",
            maxWidth: 820,
          }}
        >
          {/* Alarming Pill Badge */}
          <div
            style={{
              backgroundColor: "#DC2626",
              color: "#FFFFFF",
              padding: "10px 28px",
              borderRadius: 9999,
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: "0.06em",
              marginBottom: 24,
              boxShadow: "0 0 30px rgba(220, 38, 38, 0.8)",
            }}
          >
            LIQUIDATION CASCADE
          </div>

          {/* Dark Glass Liquidation Card */}
          <div
            style={{
              width: "100%",
              backgroundColor: "rgba(17, 24, 39, 0.95)",
              border: "2px solid rgba(239, 68, 68, 0.6)",
              borderRadius: 48,
              padding: "36px 32px",
              boxShadow:
                "0 25px 60px rgba(0, 0, 0, 0.8), 0 0 50px rgba(239, 68, 68, 0.35)",
              display: "flex",
              flexDirection: "column",
              gap: 24,
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
              <div>
                <div style={{ fontSize: 16, color: "#9CA3AF", fontWeight: 700 }}>
                  ACCOUNT BALANCE #88492
                </div>
                <div
                  style={{
                    fontSize: 48,
                    fontWeight: 900,
                    color: "#EF4444",
                    marginTop: 6,
                    letterSpacing: "-0.02em",
                  }}
                >
                  -${lossAmount.toFixed(2)}
                </div>
              </div>
              <div
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.2)",
                  padding: "8px 18px",
                  borderRadius: 14,
                  color: "#F87171",
                  fontSize: 16,
                  fontWeight: 800,
                }}
              >
                MARGIN CALL
              </div>
            </div>

            {/* Plunging Red Candlestick Chart SVG */}
            <div style={{ width: "100%", height: 160, position: "relative" }}>
              <svg width="100%" height="160" viewBox="0 0 500 160">
                <path
                  d="M 20 20 Q 150 30 240 60 T 360 110 L 480 150"
                  fill="none"
                  stroke="#EF4444"
                  strokeWidth="5"
                  strokeLinecap="round"
                />
                <circle cx="480" cy="150" r="8" fill="#EF4444" />
                <line x1="120" y1="15" x2="120" y2="40" stroke="#EF4444" strokeWidth="2" />
                <rect x="110" y="20" width="20" height="15" fill="#EF4444" />
                <line x1="280" y1="50" x2="280" y2="90" stroke="#EF4444" strokeWidth="2" />
                <rect x="270" y="60" width="20" height="25" fill="#EF4444" />
                <line x1="420" y1="100" x2="420" y2="155" stroke="#EF4444" strokeWidth="2" />
                <rect x="410" y="115" width="20" height="35" fill="#EF4444" />
              </svg>
            </div>

            {/* Telemetry Pills */}
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
              <span
                style={{
                  backgroundColor: "rgba(31, 41, 55, 0.8)",
                  padding: "8px 16px",
                  borderRadius: 12,
                  color: "#D1D5DB",
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                ❌ Manual Hesitation: 14.8s
              </span>
              <span
                style={{
                  backgroundColor: "rgba(31, 41, 55, 0.8)",
                  padding: "8px 16px",
                  borderRadius: 12,
                  color: "#D1D5DB",
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                ❌ Slippage: +42 Pips
              </span>
              <span
                style={{
                  backgroundColor: "rgba(31, 41, 55, 0.8)",
                  padding: "8px 16px",
                  borderRadius: 12,
                  color: "#D1D5DB",
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                ❌ Emotional Revenge Trade
              </span>
            </div>
          </div>
        </div>
      )}

      {/* PART 3: The Hard Truth & The Shift */}
      {isPart3 && (
        <div
          style={{
            zIndex: 7,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            gap: 28,
            padding: "0 60px",
          }}
        >
          {frame >= 300 && (
            <div
              style={{
                fontSize: 68,
                fontWeight: 900,
                color: "#9CA3AF",
                letterSpacing: "-0.02em",
                transform: `scale(${text1Spring})`,
                opacity: interpolate(text1Spring, [0, 1], [0, 1]),
              }}
            >
              HUMANS HESITATE.
            </div>
          )}

          {frame >= 345 && (
            <div
              style={{
                fontSize: 78,
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: "-0.03em",
                transform: `scale(${text2Spring})`,
                opacity: interpolate(text2Spring, [0, 1], [0, 1]),
                textShadow: "0 0 40px rgba(124, 58, 237, 0.8)",
              }}
            >
              ALGORITHMS EXECUTE.
            </div>
          )}

          {frame >= 390 && (
            <div
              style={{
                marginTop: 20,
                fontSize: 54,
                fontWeight: 800,
                color: "#FDE047",
                letterSpacing: "-0.02em",
                transform: `scale(${text3Spring})`,
                opacity: interpolate(text3Spring, [0, 1], [0, 1]),
                textShadow: "0 0 35px rgba(253, 224, 71, 0.7)",
              }}
            >
              WHAT IF YOU HAD AN UNFAIR ADVANTAGE?
            </div>
          )}
        </div>
      )}
    </div>
  );
};
