import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene4FewSpotsLeft: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for button
  const buttonSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.6 },
  });

  // Cursor animation
  // Cursor moves from (280, 240) to (0, 0) between frame 6 and 22
  const cursorX = interpolate(frame, [6, 22], [280, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY = interpolate(frame, [6, 22], [240, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Click event happens around frame 24
  const isClicking = frame >= 24 && frame <= 29;
  const clickScale = isClicking ? 0.93 : 1.0;

  // Ripple shockwave upon click
  const rippleProgress = frame >= 24 ? frame - 24 : 0;
  const rippleScale = interpolate(rippleProgress, [0, 16], [1, 1.45], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rippleOpacity = interpolate(rippleProgress, [0, 16], [0.8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Rotating background radial rays matching ref_frame_12
  const rayRotation = frame * 0.4;

  // Exit transition
  const exitOpacity = interpolate(frame, [40, 48], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
        opacity: exitOpacity,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* Soft lavender radiating rays matching ref_frame_12 */}
      <div
        style={{
          position: "absolute",
          width: 1400,
          height: 1400,
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `rotate(${rayRotation}deg)`,
          pointerEvents: "none",
        }}
      >
        <svg width="1400" height="1400" viewBox="0 0 1400 1400">
          {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
            <path
              key={i}
              d={`M 700 700 L ${
                700 + 700 * Math.cos(((angle - 12) * Math.PI) / 180)
              } ${
                700 + 700 * Math.sin(((angle - 12) * Math.PI) / 180)
              } L ${
                700 + 700 * Math.cos(((angle + 12) * Math.PI) / 180)
              } ${
                700 + 700 * Math.sin(((angle + 12) * Math.PI) / 180)
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
        {frame >= 24 && (
          <div
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              borderRadius: 9999,
              border: "3px solid #8B5CF6",
              transform: `scale(${rippleScale})`,
              opacity: rippleOpacity,
              pointerEvents: "none",
            }}
          />
        )}

        {/* Capsule Pill Button matching ref_frame_12 */}
        <div
          style={{
            backgroundColor: "#5B21B6",
            background: "linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%)",
            borderRadius: 9999,
            padding: "24px 60px",
            display: "flex",
            alignItems: "center",
            gap: 14,
            boxShadow:
              "0 22px 50px rgba(91, 33, 182, 0.45), 0 0 25px rgba(139, 92, 246, 0.3)",
            cursor: "pointer",
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          {/* Glowing Purple Bullet */}
          <span
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#DDD6FE",
              boxShadow: "0 0 12px #DDD6FE",
            }}
          />
          {/* Button Text */}
          <span
            style={{
              fontSize: 38,
              fontWeight: 700,
              color: "#FFFFFF",
              letterSpacing: "-0.01em",
              textShadow: "0 2px 8px rgba(0, 0, 0, 0.3)",
            }}
          >
            few spots left...
          </span>
        </div>

        {/* Animated Mouse Cursor */}
        {frame >= 6 && (
          <div
            style={{
              position: "absolute",
              top: `calc(50% + ${cursorY}px)`,
              left: `calc(50% + ${cursorX}px)`,
              pointerEvents: "none",
              zIndex: 10,
              filter: "drop-shadow(0 8px 16px rgba(0, 0, 0, 0.35))",
            }}
          >
            {/* macOS-style Cursor SVG */}
            <svg width="42" height="42" viewBox="0 0 24 24" fill="none">
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
  );
};
