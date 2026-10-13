import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Glitch pixel boxes
  const glitchBoxes = [
    { x: -140, y: -90, w: 90, h: 44, color: "#6D28D9", delay: 0, dur: 18 },
    { x: 110, y: -60, w: 110, h: 50, color: "#4F46E5", delay: 3, dur: 16 },
    { x: -190, y: 30, w: 75, h: 48, color: "#7C3AED", delay: 1, dur: 20 },
    { x: -90, y: 10, w: 60, h: 65, color: "#5B21B6", delay: 4, dur: 15 },
    { x: 130, y: 20, w: 85, h: 55, color: "#6366F1", delay: 2, dur: 18 },
    { x: -20, y: -130, w: 100, h: 42, color: "#7C3AED", delay: 5, dur: 14 },
    { x: 80, y: 90, w: 70, h: 38, color: "#4338CA", delay: 6, dur: 16 },
  ];

  // Phase switch: frame 0-24 is "hey", frame 25+ is "hey do you need"
  const isExpanded = frame >= 24;

  // Spring animations for initial "hey"
  const heySpring = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 160, mass: 0.6 },
  });

  // Staggered springs for expanded words
  const expandedProgress = frame - 24;
  const wordSprings = ["hey", "do", "you", "need"].map((_, i) =>
    spring({
      frame: expandedProgress - i * 3,
      fps,
      config: { damping: 12, stiffness: 180, mass: 0.5 },
    })
  );

  // Exit transition
  const exitScale = interpolate(frame, [56, 66], [1, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitOpacity = interpolate(frame, [60, 66], [1, 0], {
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
      {/* Glitch pixel rects matching ref_frame_1 */}
      {frame < 30 &&
        glitchBoxes.map((box, i) => {
          const localFrame = frame - box.delay;
          if (localFrame < 0 || localFrame > box.dur) return null;
          const boxOpacity = interpolate(
            localFrame,
            [0, 2, box.dur - 4, box.dur],
            [0, 0.75, 0.75, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          );
          const jitterX = Math.sin(frame * 1.5 + i) * 3;
          const jitterY = Math.cos(frame * 1.2 + i) * 2;

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `calc(50% + ${box.x + jitterX}px)`,
                top: `calc(50% + ${box.y + jitterY}px)`,
                width: box.w,
                height: box.h,
                backgroundColor: box.color,
                borderRadius: 4,
                opacity: boxOpacity,
                mixBlendMode: "screen",
                boxShadow: `0 0 15px ${box.color}`,
              }}
            />
          );
        })}

      {/* Kinetic Typography */}
      {!isExpanded ? (
        <div
          style={{
            fontSize: 88,
            fontWeight: 700,
            color: "#FFFFFF",
            letterSpacing: "-0.03em",
            transform: `scale(${heySpring})`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            textShadow: "0 4px 20px rgba(124, 58, 237, 0.4)",
          }}
        >
          hey
        </div>
      ) : (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 16,
          }}
        >
          {["hey", "do", "you", "need"].map((word, idx) => {
            const sp = wordSprings[idx];
            const translateY = interpolate(sp, [0, 1], [30, 0]);
            const opacity = interpolate(sp, [0, 1], [0, 1]);
            return (
              <span
                key={idx}
                style={{
                  fontSize: 78,
                  fontWeight: 700,
                  color: "#FFFFFF",
                  letterSpacing: "-0.03em",
                  display: "inline-block",
                  opacity,
                  transform: `translateY(${translateY}px) scale(${sp})`,
                  textShadow: "0 4px 25px rgba(255, 255, 255, 0.2)",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
};
