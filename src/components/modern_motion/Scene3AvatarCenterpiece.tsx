import React from "react";
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene3AvatarCenterpiece: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Vertical Pillar entrance
  const pillarProgress = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 100, mass: 0.9 },
  });
  const pillarScaleY = interpolate(pillarProgress, [0, 1], [0, 1]);

  // Center squircle card pop-in
  const cardStartFrame = 10;
  const cardSpring = spring({
    frame: frame - cardStartFrame,
    fps,
    config: { damping: 11, stiffness: 140, mass: 0.7 },
  });

  // Floating bobbing motion for orbiting elements
  const float1 = Math.sin(frame * 0.12) * 8;
  const float2 = Math.cos(frame * 0.14) * 10;
  const float3 = Math.sin(frame * 0.15 + 1) * 9;
  const float4 = Math.cos(frame * 0.11 + 2) * 7;

  // Orbiting elements spring pop-in
  const orbitSpring = spring({
    frame: frame - cardStartFrame - 8,
    fps,
    config: { damping: 12, stiffness: 160, mass: 0.5 },
  });

  // Typography spring bounce
  const textStartFrame = cardStartFrame + 14;
  const textSpring = spring({
    frame: frame - textStartFrame,
    fps,
    config: { damping: 9, stiffness: 150, mass: 0.6 },
  });
  const textWobble = Math.sin(frame * 0.18) * 1.5;

  // Exit transition to Scene 4
  const exitOpacity = interpolate(frame, [72, 82], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitScale = interpolate(frame, [70, 82], [1, 1.08], {
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
        transform: `scale(${exitScale})`,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* Central Vertical 3D Creased Ribbon/Pillar matching ref_frame_10 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          width: 380,
          display: "flex",
          transformOrigin: "center top",
          transform: `scaleY(${pillarScaleY})`,
          boxShadow: "0 0 50px rgba(124, 58, 237, 0.2)",
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

      {/* Floating 3D Orbiting Badges matching ref_frame_10 */}
      {frame >= cardStartFrame + 6 && (
        <div
          style={{
            position: "absolute",
            width: 740,
            height: 600,
            zIndex: 3,
            pointerEvents: "none",
            transform: `scale(${orbitSpring})`,
          }}
        >
          {/* Top Left: 3D Camera / Trading Terminal Badge */}
          <div
            style={{
              position: "absolute",
              top: 70 + float1,
              left: 40,
              width: 90,
              height: 90,
              borderRadius: 24,
              backgroundColor: "#2E1065",
              boxShadow:
                "0 20px 35px rgba(46, 16, 101, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: "rotate(-12deg)",
            }}
          >
            {/* 3D Camera SVG */}
            <svg width="48" height="48" viewBox="0 0 24 24" fill="#C4B5FD">
              <path d="M4 4h3l2-2h6l2 2h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm8 3a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 2a3 3 0 1 1 0 6 3 3 0 0 1 0-6z" />
            </svg>
          </div>

          {/* Mid Left: 3D Laptop / Candlestick Badge */}
          <div
            style={{
              position: "absolute",
              top: 280 + float2,
              left: 65,
              width: 82,
              height: 82,
              borderRadius: 22,
              backgroundColor: "#3B0764",
              boxShadow:
                "0 20px 35px rgba(59, 7, 100, 0.45), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: "rotate(8deg)",
            }}
          >
            {/* 3D Laptop SVG */}
            <svg width="44" height="44" viewBox="0 0 24 24" fill="#E9D5FF">
              <path d="M20 18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2h-4zM4 6h16v10H4V6z" />
            </svg>
          </div>

          {/* Top Right: 3D Camcorder / Scanner Badge */}
          <div
            style={{
              position: "absolute",
              top: 100 + float3,
              right: 40,
              width: 88,
              height: 88,
              borderRadius: 24,
              backgroundColor: "#2E1065",
              boxShadow:
                "0 20px 35px rgba(46, 16, 101, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: "rotate(15deg)",
            }}
          >
            {/* 3D Video Cam SVG */}
            <svg width="46" height="46" viewBox="0 0 24 24" fill="#DDD6FE">
              <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45-1 1-1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z" />
            </svg>
          </div>

          {/* Mid Right: 3D Metallic Precision Gear */}
          <div
            style={{
              position: "absolute",
              top: 310 + float4,
              right: 60,
              width: 82,
              height: 82,
              borderRadius: 22,
              backgroundColor: "#4C1D95",
              boxShadow:
                "0 20px 35px rgba(76, 29, 149, 0.45), inset 0 2px 4px rgba(255, 255, 255, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `rotate(${frame * 1.5}deg)`,
            }}
          >
            {/* 3D Gear SVG */}
            <svg width="46" height="46" viewBox="0 0 24 24" fill="#F5D0FE">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
            </svg>
          </div>
        </div>
      )}

      {/* Main Center Squircle Card with 3D Avatar */}
      <div
        style={{
          width: 440,
          height: 440,
          borderRadius: 96,
          backgroundColor: "#FFFFFF",
          boxShadow:
            "0 35px 80px rgba(124, 58, 237, 0.35), 0 0 0 14px rgba(196, 181, 253, 0.45)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          zIndex: 4,
          transform: `scale(${cardSpring})`,
          overflow: "hidden",
        }}
      >
        {/* The 3D Trader Avatar image perfectly framed */}
        <img
          src={staticFile("assets/aurelius_avatar_head.jpg")}
          alt="Don Aurelius 3D Avatar"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "center 20%",
            transform: "scale(1.12)",
          }}
        />
      </div>

      {/* Stylized 3D Bubbly Kinetic Typography below Card matching ref_frame_10 */}
      {frame >= textStartFrame && (
        <div
          style={{
            marginTop: 48,
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
          {/* Line 1: Deploy */}
          <div
            style={{
              fontSize: 82,
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "-0.01em",
              textTransform: "none",
              textShadow:
                "-6px -6px 0 #7C3AED, 6px -6px 0 #7C3AED, -6px 6px 0 #7C3AED, 6px 6px 0 #7C3AED, 0 16px 30px rgba(124, 58, 237, 0.5)",
            }}
          >
            Deploy
          </div>

          {/* Line 2: AURELIUS */}
          <div
            style={{
              fontSize: 94,
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "0.02em",
              textTransform: "uppercase",
              textShadow:
                "-7px -7px 0 #7C3AED, 7px -7px 0 #7C3AED, -7px 7px 0 #7C3AED, 7px 7px 0 #7C3AED, 0 20px 35px rgba(124, 58, 237, 0.6)",
            }}
          >
            AURELIUS
          </div>
        </div>
      )}
    </div>
  );
};
