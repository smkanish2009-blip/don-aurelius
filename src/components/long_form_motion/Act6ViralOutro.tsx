import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Act6ViralOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Part 1: Scarcity Button & Click (0 - 110)
  const isPart1 = frame < 115;
  const buttonSpring = spring({ frame, fps, config: { damping: 12, stiffness: 140, mass: 0.6 } });

  // Cursor animation
  const cursorX = interpolate(frame, [10, 42], [320, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY = interpolate(frame, [10, 42], [280, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const isClicking = frame >= 44 && frame <= 54;
  const clickScale = isClicking ? 0.93 : 1.0;

  // Ripple shockwave
  const rippleProgress = frame >= 44 ? frame - 44 : 0;
  const rippleScale = interpolate(rippleProgress, [0, 24], [1, 1.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rippleOpacity = interpolate(rippleProgress, [0, 24], [0.8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Radiating rays rotation
  const rayRotation = frame * 0.4;

  // Part 2: Studio White Outro (110 - 240)
  const isPart2 = frame >= 105;
  const outroFrame = frame - 110;
  const textSpring = spring({ frame: outroFrame, fps, config: { damping: 12, stiffness: 130, mass: 0.6 } });

  // 3D Speech bubble pop
  const bubbleFrame = outroFrame - 15;
  const bubbleSpring = spring({ frame: bubbleFrame, fps, config: { damping: 10, stiffness: 150, mass: 0.5 } });
  const bubbleWiggle =
    bubbleFrame > 0 ? Math.sin(bubbleFrame * 0.3) * (6 / (1 + bubbleFrame * 0.08)) : 0;

  // Golden Stamp drop
  const stampFrame = outroFrame - 35;
  const stampSpring = spring({ frame: stampFrame, fps, config: { damping: 8, stiffness: 180, mass: 0.7 } });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#FFFFFF",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* PART 1: Scarcity Button & Click */}
      {isPart1 && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: interpolate(frame, [95, 115], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {/* Rotating soft lavender radial rays */}
          <div
            style={{
              position: "absolute",
              width: 1500,
              height: 1500,
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `rotate(${rayRotation}deg)`,
              pointerEvents: "none",
            }}
          >
            <svg width="1500" height="1500" viewBox="0 0 1500 1500">
              {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
                <path
                  key={i}
                  d={`M 750 750 L ${
                    750 + 750 * Math.cos(((angle - 12) * Math.PI) / 180)
                  } ${
                    750 + 750 * Math.sin(((angle - 12) * Math.PI) / 180)
                  } L ${
                    750 + 750 * Math.cos(((angle + 12) * Math.PI) / 180)
                  } ${
                    750 + 750 * Math.sin(((angle + 12) * Math.PI) / 180)
                  } Z`}
                  fill="rgba(216, 180, 254, 0.28)"
                />
              ))}
            </svg>
          </div>

          {/* Button & Ripple Container */}
          <div
            style={{
              position: "relative",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `scale(${buttonSpring * clickScale})`,
              zIndex: 3,
            }}
          >
            {/* Ripple Wave */}
            {frame >= 44 && (
              <div
                style={{
                  position: "absolute",
                  width: "100%",
                  height: "100%",
                  borderRadius: 9999,
                  border: "4px solid #8B5CF6",
                  transform: `scale(${rippleScale})`,
                  opacity: rippleOpacity,
                  pointerEvents: "none",
                }}
              />
            )}

            {/* Stadium Pill Button */}
            <div
              style={{
                backgroundColor: "#5B21B6",
                background: "linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%)",
                borderRadius: 9999,
                padding: "26px 64px",
                display: "flex",
                alignItems: "center",
                gap: 16,
                boxShadow:
                  "0 25px 60px rgba(91, 33, 182, 0.5), 0 0 35px rgba(139, 92, 246, 0.35)",
                border: "1px solid rgba(255, 255, 255, 0.3)",
              }}
            >
              <span
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  backgroundColor: "#DDD6FE",
                  boxShadow: "0 0 15px #DDD6FE",
                }}
              />
              <span
                style={{
                  fontSize: 42,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  letterSpacing: "-0.01em",
                  textShadow: "0 2px 10px rgba(0, 0, 0, 0.3)",
                }}
              >
                few spots left...
              </span>
            </div>

            {/* Animated Pointer Cursor */}
            {frame >= 10 && (
              <div
                style={{
                  position: "absolute",
                  top: `calc(50% + ${cursorY}px)`,
                  left: `calc(50% + ${cursorX}px)`,
                  pointerEvents: "none",
                  zIndex: 10,
                  filter: "drop-shadow(0 10px 20px rgba(0, 0, 0, 0.4))",
                }}
              >
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 3L17 14.5L11.5 15.5L14.5 21.5L11.5 23L8.5 17L4 21V3Z"
                    fill="#1E1B4B"
                    stroke="#FFFFFF"
                    strokeWidth="1.5"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PART 2: Studio White Outro */}
      {isPart2 && (
        <div
          style={{
            zIndex: 5,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            gap: 28,
            padding: "0 60px",
            opacity: interpolate(outroFrame, [0, 15], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {/* Main Kinetic Outro Call */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 20,
              transform: `scale(${textSpring})`,
            }}
          >
            <span
              style={{
                fontSize: 72,
                fontWeight: 800,
                color: "#1E1B4B",
                letterSpacing: "-0.03em",
              }}
            >
              see you in my
            </span>

            {/* Glossy 3D Speech Bubble with 3 Message Dots */}
            <div
              style={{
                transform: `scale(${bubbleSpring}) rotate(${bubbleWiggle}deg)`,
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                filter: "drop-shadow(0 12px 25px rgba(0, 0, 0, 0.18))",
              }}
            >
              <svg width="86" height="86" viewBox="0 0 100 100">
                <defs>
                  <linearGradient id="bubbleGrad90" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#FFFFFF" />
                    <stop offset="60%" stopColor="#F1F5F9" />
                    <stop offset="100%" stopColor="#E2E8F0" />
                  </linearGradient>
                </defs>
                <path
                  d="M 20 20 C 20 10, 80 10, 80 20 C 80 50, 80 60, 70 65 L 75 82 L 58 68 C 25 70, 20 60, 20 40 Z"
                  fill="url(#bubbleGrad90)"
                  stroke="#CBD5E1"
                  strokeWidth="2.5"
                />
                <circle cx="40" cy="42" r="4.5" fill="#94A3B8" />
                <circle cx="50" cy="42" r="4.5" fill="#94A3B8" />
                <circle cx="60" cy="42" r="4.5" fill="#94A3B8" />
              </svg>
            </div>
          </div>

          {/* Subtitle Directive */}
          <div
            style={{
              fontSize: 36,
              fontWeight: 700,
              color: "#6D28D9",
              letterSpacing: "0.02em",
            }}
          >
            DM "GOLD" TO ACCESS THE ENGINE
          </div>

          {/* Golden Seal Stamp Landing */}
          {stampFrame >= 0 && (
            <div
              style={{
                marginTop: 20,
                transform: `scale(${stampSpring})`,
                backgroundColor: "#2E1065",
                border: "2px solid #FDE047",
                borderRadius: 9999,
                padding: "14px 38px",
                display: "flex",
                alignItems: "center",
                gap: 12,
                boxShadow: "0 15px 35px rgba(46, 16, 101, 0.35)",
              }}
            >
              <span style={{ fontSize: 28 }}>⚜️</span>
              <span
                style={{
                  fontSize: 24,
                  fontWeight: 900,
                  color: "#FDE047",
                  letterSpacing: "0.06em",
                }}
              >
                DON AURELIUS • AI GOLD BOT
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
