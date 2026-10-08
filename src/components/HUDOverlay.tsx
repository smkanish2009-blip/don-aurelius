import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const HUDOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Determine current narrative Act
  let actBadge = "ACT I: THE CHAOS";
  if (frame >= 1080 && frame < 2160) {
    actBadge = "ACT II: THE PARADIGM SHIFT";
  } else if (frame >= 2160 && frame < 3600) {
    actBadge = "ACT III: LIVE INTELLIGENCE";
  } else if (frame >= 3600 && frame < 4860) {
    actBadge = "ACT IV: MASTERCLASS INSTALLATION";
  } else if (frame >= 4860) {
    actBadge = "ACT V: SOVEREIGN RESOLUTION";
  }

  // Timecode calculation
  const totalSeconds = frame / fps;
  const mm = Math.floor(totalSeconds / 60);
  const ss = Math.floor(totalSeconds % 60);
  const ff = Math.floor(frame % fps);
  const timecode = `${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}:${String(ff).padStart(2, "0")}`;

  // Gold Spot price fluctuation simulation
  const goldPrice = (2648.5 + Math.sin(frame * 0.08) * 1.85).toFixed(2);

  // Fade out HUD during Act V title card (after 4860) to keep it pure cinema
  const hudOpacity = interpolate(
    frame,
    [0, 60, 4800, 4860],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Act V Title Card Animation (4860 - 5400)
  const act5Local = frame - 4860;
  const act5Spring = spring({
    frame: Math.max(0, act5Local - 60), // Starts at 4920 (after 1s dead silence)
    fps,
    config: {
      damping: 20,
      mass: 1.5,
      stiffness: 60,
    },
  });

  const titleScale = interpolate(act5Spring, [0, 1], [0.92, 1.0]);
  const titleOpacity = interpolate(
    act5Local,
    [60, 100, 480, 540],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <>
      {/* ===================================================================== */}
      {/* TOP & BOTTOM MINIMALIST CINEMATIC HUD                                  */}
      {/* ===================================================================== */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "1080px",
          height: "1920px",
          pointerEvents: "none",
          opacity: hudOpacity,
          zIndex: 35,
          fontFamily:
            "'SF Mono', 'Fira Code', 'Consolas', monospace",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "50px 48px",
          boxSizing: "border-box",
        }}
      >
        {/* Top Header Bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Left Brand Badge */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              backgroundColor: "rgba(10, 14, 24, 0.82)",
              padding: "10px 22px",
              borderRadius: "24px",
              border: "1px solid rgba(240, 199, 94, 0.35)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
            }}
          >
            <div
              style={{
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                backgroundColor: "#F0C75E",
                boxShadow: "0 0 10px #F0C75E",
              }}
            />
            <span
              style={{
                fontSize: "17px",
                fontWeight: 700,
                color: "#FFFFFF",
                letterSpacing: "0.15em",
              }}
            >
              DON AURELIUS • {actBadge}
            </span>
          </div>

          {/* Right Timecode & Technical Spec */}
          <div
            style={{
              backgroundColor: "rgba(10, 14, 24, 0.82)",
              padding: "10px 22px",
              borderRadius: "24px",
              border: "1px solid rgba(0, 229, 255, 0.3)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
              color: "#00E5FF",
              fontSize: "17px",
              letterSpacing: "0.1em",
              fontWeight: 600,
            }}
          >
            {timecode} / 01:30:00 • 60 FPS
          </div>
        </div>

        {/* Bottom Telemetry Bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Live XAU/USD Quote */}
          <div
            style={{
              backgroundColor: "rgba(10, 14, 24, 0.82)",
              padding: "10px 22px",
              borderRadius: "24px",
              border: "1px solid rgba(240, 199, 94, 0.3)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              gap: "14px",
            }}
          >
            <span style={{ color: "#F0C75E", fontWeight: 700, fontSize: "16px" }}>
              XAU/USD
            </span>
            <span style={{ color: "#FFFFFF", fontSize: "17px", fontWeight: 600 }}>
              ${goldPrice}
            </span>
            <span style={{ color: "#22C55E", fontSize: "15px" }}>+1.42%</span>
          </div>

          {/* MT5 Sub-millis Latency */}
          <div
            style={{
              backgroundColor: "rgba(10, 14, 24, 0.82)",
              padding: "10px 22px",
              borderRadius: "24px",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              color: "rgba(230, 240, 255, 0.85)",
              fontSize: "16px",
            }}
          >
            <span style={{ color: "#00E5FF" }}>⚡ 0.38ms</span>
            <span>|</span>
            <span>MONTE CARLO 5K PATHS</span>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* ACT V: GRAND TITLE CARD & CALL-TO-ACTION (Frames 4860 - 5400)         */}
      {/* ===================================================================== */}
      {frame >= 4860 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "1080px",
            height: "1920px",
            backgroundColor: frame < 4920 ? "#000000" : "transparent",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "0 60px",
            boxSizing: "border-box",
            textAlign: "center",
            opacity: frame < 4920 ? 1 : titleOpacity,
            transform: `scale(${frame < 4920 ? 1 : titleScale})`,
            zIndex: 60,
            pointerEvents: "none",
          }}
        >
          {frame >= 4920 && (
            <>
              {/* Sovereign Imperial Emblem */}
              <div
                style={{
                  width: "110px",
                  height: "110px",
                  borderRadius: "50%",
                  border: "2px solid #F0C75E",
                  boxShadow: "0 0 50px rgba(240, 199, 94, 0.7)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "36px",
                  background:
                    "radial-gradient(circle, rgba(240, 199, 94, 0.25) 0%, rgba(10, 14, 24, 0.9) 70%)",
                }}
              >
                <span
                  style={{
                    fontSize: "52px",
                    color: "#F0C75E",
                    fontFamily: "'Cinzel', serif",
                    fontWeight: 900,
                  }}
                >
                  ⚜
                </span>
              </div>

              {/* Main Grand Title */}
              <h1
                style={{
                  fontFamily:
                    "'Cinzel', 'Playfair Display', 'Didot', 'Georgia', serif",
                  fontSize: "82px",
                  fontWeight: 900,
                  letterSpacing: "0.28em",
                  color: "#FFFFFF",
                  margin: "0 0 16px 0",
                  textShadow:
                    "0 0 50px rgba(240, 199, 94, 0.7), 0 4px 20px rgba(0,0,0,0.9)",
                }}
              >
                DON AURELIUS
              </h1>

              {/* Tagline */}
              <h2
                style={{
                  fontFamily:
                    "'Cinzel', 'Trajan Pro', 'Bodoni MT', 'Georgia', serif",
                  fontSize: "20px",
                  fontWeight: 700,
                  letterSpacing: "0.18em",
                  color: "#F0C75E",
                  margin: "0 0 40px 0",
                  textShadow: "0 0 25px rgba(240, 199, 94, 0.5)",
                }}
              >
                THE SOVEREIGN ALGORITHMIC GOLD SYNDICATE
              </h2>

              {/* Glassmorphic Call-To-Action Card */}
              <div
                style={{
                  width: "860px",
                  backgroundColor: "rgba(10, 15, 26, 0.88)",
                  borderRadius: "24px",
                  border: "1px solid rgba(240, 199, 94, 0.5)",
                  boxShadow:
                    "0 20px 60px rgba(0,0,0,0.8), 0 0 40px rgba(240, 199, 94, 0.25)",
                  backdropFilter: "blur(24px)",
                  padding: "36px 30px",
                  boxSizing: "border-box",
                  display: "flex",
                  flexDirection: "column",
                  gap: "20px",
                }}
              >
                <div
                  style={{
                    fontSize: "17px",
                    letterSpacing: "0.18em",
                    color: "rgba(220, 235, 255, 0.75)",
                    fontFamily: "'SF Mono', monospace",
                  }}
                >
                  CLAIM YOUR SOVEREIGN TERMINAL ACCESS
                </div>

                <div
                  style={{
                    fontSize: "21px",
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                    color: "#FFFFFF",
                    backgroundColor: "rgba(240, 199, 94, 0.15)",
                    padding: "14px 20px",
                    borderRadius: "14px",
                    border: "1px solid rgba(240, 199, 94, 0.4)",
                    fontFamily: "'SF Mono', monospace",
                    whiteSpace: "nowrap",
                  }}
                >
                  github.com/smkanish2009-blip/don-aurelius
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    gap: "30px",
                    fontSize: "17px",
                    letterSpacing: "0.15em",
                    color: "rgba(200, 215, 240, 0.7)",
                    fontFamily: "'Cinzel', serif",
                  }}
                >
                  <span>METATRADER 5 VERIFIED</span>
                  <span>•</span>
                  <span>AES-256 HARDWARE LOCKED</span>
                  <span>•</span>
                  <span>89.4% WIN RATE</span>
                </div>
              </div>

              {/* Director Credit */}
              <div
                style={{
                  marginTop: "60px",
                  fontSize: "18px",
                  letterSpacing: "0.35em",
                  color: "rgba(180, 195, 215, 0.6)",
                  fontFamily: "'Cinzel', serif",
                  textTransform: "uppercase",
                }}
              >
                CONCEIVED & ARCHITECTED BY SM.KANISH
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};
