import React from "react";
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export const Act2ApexReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Vertical 3D Creased Pillar entrance
  const pillarSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.9 },
  });
  const pillarScaleY = interpolate(pillarSpring, [0, 1], [0, 1]);

  // Center squircle card pop-in
  const cardStartFrame = 15;
  const cardSpring = spring({
    frame: frame - cardStartFrame,
    fps,
    config: { damping: 10, stiffness: 130, mass: 0.7 },
  });

  // Orbiting elements spring pop-in
  const orbitSpring = spring({
    frame: frame - cardStartFrame - 10,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.5 },
  });

  // Sine-wave levitation for the 4 3D badges
  const float1 = Math.sin(frame * 0.1) * 10;
  const float2 = Math.cos(frame * 0.12) * 12;
  const float3 = Math.sin(frame * 0.13 + 1.2) * 11;
  const float4 = Math.cos(frame * 0.09 + 2.1) * 9;

  // Typography spring bounce
  const textStartFrame = cardStartFrame + 20;
  const textSpring = spring({
    frame: frame - textStartFrame,
    fps,
    config: { damping: 9, stiffness: 140, mass: 0.6 },
  });
  const textWobble = Math.sin(frame * 0.15) * 1.5;

  // Floating Pills (Sub-features)
  const pillSpring1 = spring({ frame: frame - 180, fps, config: { damping: 12, stiffness: 160 } });
  const pillSpring2 = spring({ frame: frame - 240, fps, config: { damping: 12, stiffness: 160 } });

  // Camera zoom in phase 2 (frames 320 to 450)
  const cameraZoom = interpolate(frame, [300, 440], [1, 1.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Exit transition to Act 3
  const exitOpacity = interpolate(frame, [435, 450], [1, 0], {
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
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* Central Vertical 3D Creased Ribbon matching the iconic aesthetic */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          width: 420,
          display: "flex",
          transformOrigin: "center top",
          transform: `scaleY(${pillarScaleY})`,
          boxShadow: "0 0 60px rgba(124, 58, 237, 0.25)",
          zIndex: 1,
        }}
      >
        {/* Left Facet (Light Purple) */}
        <div
          style={{
            flex: 1,
            height: "100%",
            background:
              "linear-gradient(180deg, #8B5CF6 0%, #7C3AED 50%, #6D28D9 100%)",
          }}
        />
        {/* Right Facet (Darker Creased Purple for 3D depth) */}
        <div
          style={{
            flex: 1,
            height: "100%",
            background:
              "linear-gradient(180deg, #7C3AED 0%, #6D28D9 50%, #5B21B6 100%)",
          }}
        />
      </div>

      {/* Main container with dynamic camera zoom */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          zIndex: 3,
          transform: `scale(${cameraZoom})`,
        }}
      >
        {/* Floating 3D Orbiting Badges around the centerpiece */}
        {frame >= cardStartFrame + 6 && (
          <div
            style={{
              position: "absolute",
              width: 820,
              height: 640,
              zIndex: 3,
              pointerEvents: "none",
              transform: `scale(${orbitSpring})`,
            }}
          >
            {/* Top Left: 0.38ms Speed Core */}
            <div
              style={{
                position: "absolute",
                top: 50 + float1,
                left: 30,
                width: 100,
                height: 100,
                borderRadius: 28,
                backgroundColor: "#2E1065",
                boxShadow:
                  "0 20px 40px rgba(46, 16, 101, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: "rotate(-12deg)",
                gap: 4,
              }}
            >
              <span style={{ fontSize: 28 }}>⚡</span>
              <span style={{ fontSize: 13, fontWeight: 800, color: "#EDE9FE" }}>
                0.38ms
              </span>
            </div>

            {/* Mid Left: Quantum Neural Core */}
            <div
              style={{
                position: "absolute",
                top: 320 + float2,
                left: 50,
                width: 95,
                height: 95,
                borderRadius: 26,
                backgroundColor: "#3B0764",
                boxShadow:
                  "0 20px 40px rgba(59, 7, 100, 0.45), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: "rotate(8deg)",
                gap: 4,
              }}
            >
              <span style={{ fontSize: 26 }}>🧠</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: "#F5D0FE" }}>
                AI Core
              </span>
            </div>

            {/* Top Right: Capital Shield */}
            <div
              style={{
                position: "absolute",
                top: 80 + float3,
                right: 30,
                width: 100,
                height: 100,
                borderRadius: 28,
                backgroundColor: "#2E1065",
                boxShadow:
                  "0 20px 40px rgba(46, 16, 101, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: "rotate(14deg)",
                gap: 4,
              }}
            >
              <span style={{ fontSize: 28 }}>🛡️</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: "#EDE9FE" }}>
                Capital Shield
              </span>
            </div>

            {/* Mid Right: Smart Money Precision */}
            <div
              style={{
                position: "absolute",
                top: 340 + float4,
                right: 50,
                width: 95,
                height: 95,
                borderRadius: 26,
                backgroundColor: "#4C1D95",
                boxShadow:
                  "0 20px 40px rgba(76, 29, 149, 0.45), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: `rotate(${frame * 0.8}deg)`,
                gap: 4,
              }}
            >
              <span style={{ fontSize: 26 }}>📈</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: "#DDD6FE" }}>
                Smart Flow
              </span>
            </div>
          </div>
        )}

        {/* Centerpiece Squircle Card with 3D Avatar */}
        <div
          style={{
            width: 460,
            height: 460,
            borderRadius: 105,
            backgroundColor: "#FFFFFF",
            boxShadow:
              "0 40px 90px rgba(124, 58, 237, 0.35), 0 0 0 16px rgba(196, 181, 253, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            zIndex: 4,
            transform: `scale(${cardSpring})`,
            overflow: "hidden",
          }}
        >
          <img
            src={staticFile("assets/aurelius_avatar_head.jpg")}
            alt="Don Aurelius 3D Avatar"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "center 20%",
              transform: "scale(1.15)",
            }}
          />
        </div>

        {/* Stylized 3D Bubbly Kinetic Typography below Card */}
        {frame >= textStartFrame && (
          <div
            style={{
              marginTop: 44,
              zIndex: 6,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              transform: `scale(${textSpring}) rotate(${textWobble}deg)`,
              opacity: interpolate(textSpring, [0, 1], [0, 1]),
              lineHeight: 1.05,
            }}
          >
            {/* Top Line: Meet */}
            <div
              style={{
                fontSize: 68,
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: "-0.01em",
                textShadow:
                  "-6px -6px 0 #7C3AED, 6px -6px 0 #7C3AED, -6px 6px 0 #7C3AED, 6px 6px 0 #7C3AED, 0 16px 30px rgba(124, 58, 237, 0.5)",
              }}
            >
              Meet
            </div>

            {/* Bottom Line: DON AURELIUS */}
            <div
              style={{
                fontSize: 88,
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: "0.02em",
                textTransform: "uppercase",
                textShadow:
                  "-7px -7px 0 #7C3AED, 7px -7px 0 #7C3AED, -7px 7px 0 #7C3AED, 7px 7px 0 #7C3AED, 0 20px 35px rgba(124, 58, 237, 0.6)",
              }}
            >
              DON AURELIUS
            </div>
          </div>
        )}

        {/* Sub-Feature Capsule Pills Popping In */}
        <div
          style={{
            marginTop: 36,
            display: "flex",
            gap: 16,
            zIndex: 6,
          }}
        >
          {frame >= 180 && (
            <div
              style={{
                transform: `scale(${pillSpring1})`,
                backgroundColor: "#2E1065",
                color: "#FDE047",
                border: "2px solid rgba(253, 224, 71, 0.6)",
                borderRadius: 9999,
                padding: "10px 24px",
                fontSize: 20,
                fontWeight: 800,
                boxShadow: "0 10px 25px rgba(0, 0, 0, 0.2)",
              }}
            >
              ⚜️ XAU/USD SPECIALIST
            </div>
          )}

          {frame >= 240 && (
            <div
              style={{
                transform: `scale(${pillSpring2})`,
                backgroundColor: "#5B21B6",
                color: "#FFFFFF",
                borderRadius: 9999,
                padding: "10px 24px",
                fontSize: 20,
                fontWeight: 800,
                boxShadow: "0 10px 25px rgba(91, 33, 182, 0.3)",
              }}
            >
              ⚡ 89.4% WIN RATE
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
