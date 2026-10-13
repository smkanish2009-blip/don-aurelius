import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene5Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for text
  const textSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.6 },
  });

  // Delayed spring bounce for speech bubble emoji
  const bubbleFrame = frame - 8;
  const bubbleSpring = spring({
    frame: bubbleFrame,
    fps,
    config: { damping: 10, stiffness: 150, mass: 0.5 },
  });

  // Wiggle for bubble
  const bubbleWiggle =
    bubbleFrame > 0 ? Math.sin(bubbleFrame * 0.3) * (5 / (1 + bubbleFrame * 0.1)) : 0;

  // Final graceful hold / fade out
  const outroOpacity = interpolate(frame, [32, 40], [1, 1], {
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
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        opacity: outroOpacity,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 18,
          transform: `scale(${textSpring})`,
          opacity: interpolate(textSpring, [0, 1], [0, 1]),
        }}
      >
        <span
          style={{
            fontSize: 68,
            fontWeight: 700,
            color: "#1E1B4B",
            letterSpacing: "-0.03em",
          }}
        >
          see you in my
        </span>

        {/* Glossy 3D Speech Bubble matching ref_frame_16 */}
        <div
          style={{
            transform: `scale(${bubbleSpring}) rotate(${bubbleWiggle}deg)`,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            filter: "drop-shadow(0 10px 20px rgba(0, 0, 0, 0.15))",
          }}
        >
          <svg width="76" height="76" viewBox="0 0 100 100">
            {/* Bubble Body with soft gradient */}
            <defs>
              <linearGradient
                id="bubbleGrad"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#FFFFFF" />
                <stop offset="60%" stopColor="#F1F5F9" />
                <stop offset="100%" stopColor="#E2E8F0" />
              </linearGradient>
            </defs>
            {/* Speech bubble rounded path with tail */}
            <path
              d="M 20 20 C 20 10, 80 10, 80 20 C 80 50, 80 60, 70 65 L 75 82 L 58 68 C 25 70, 20 60, 20 40 Z"
              fill="url(#bubbleGrad)"
              stroke="#CBD5E1"
              strokeWidth="2.5"
            />
            {/* 3 Message Dots */}
            <circle cx="40" cy="42" r="4" fill="#94A3B8" />
            <circle cx="50" cy="42" r="4" fill="#94A3B8" />
            <circle cx="60" cy="42" r="4" fill="#94A3B8" />
          </svg>
        </div>
      </div>
    </div>
  );
};
