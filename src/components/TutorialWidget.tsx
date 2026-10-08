import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const TutorialWidget: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Active during Act IV (Frames 3600 - 4860)
  if (frame < 3600 || frame > 4860) {
    return null;
  }

  const localFrame = frame - 3600; // 0 to 1260 frames

  // Entrance spring animation for the glassmorphic card
  const cardScale = spring({
    frame: localFrame,
    fps,
    config: {
      damping: 16,
      mass: 0.8,
      stiffness: 80,
    },
  });

  const cardOpacity = interpolate(localFrame, [0, 40, 1200, 1260], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Step 1: Git clone command typing (Frames 40 - 240)
  const fullCommand1 = "git clone https://github.com/smkanish2009-blip/don-aurelius.git";
  const typedLength1 = Math.floor(
    interpolate(localFrame, [40, 220], [0, fullCommand1.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const text1 = fullCommand1.substring(0, typedLength1);

  // Step 2: Loading bar (Frames 260 - 520)
  const loadProgress = interpolate(localFrame, [260, 520], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Step 3: npm install && npm run start:bot typing (Frames 540 - 720)
  const fullCommand2 = "npm install && npm run start:bot";
  const typedLength2 = Math.floor(
    interpolate(localFrame, [540, 700], [0, fullCommand2.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const text2 = fullCommand2.substring(0, typedLength2);

  // Step 4: Golden pulse and engine activation (Frames 880 - 1260)
  const pulsePhase = localFrame >= 880 ? (localFrame - 880) / 45 : 0;
  const pulseScale = localFrame >= 880 ? 1.0 + Math.sin(pulsePhase * Math.PI) * 0.025 : 1.0;
  const pulseGlow = localFrame >= 880 ? Math.min(1.0, (localFrame - 880) / 40) : 0.0;

  // Blinking cursor
  const cursorBlink = Math.floor(localFrame / 15) % 2 === 0;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "1080px",
        height: "1920px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px",
        boxSizing: "border-box",
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      {/* Glassmorphic IDE Terminal Container */}
      <div
        style={{
          width: "980px",
          height: "1280px",
          backgroundColor: "rgba(10, 14, 24, 0.85)",
          borderRadius: "28px",
          border: `1px solid ${
            pulseGlow > 0 ? "rgba(240, 199, 94, 0.85)" : "rgba(255, 255, 255, 0.16)"
          }`,
          boxShadow:
            pulseGlow > 0
              ? "0 30px 90px rgba(0, 0, 0, 0.8), 0 0 80px rgba(240, 199, 94, 0.45)"
              : "0 30px 90px rgba(0, 0, 0, 0.75), 0 0 30px rgba(0, 210, 255, 0.15)",
          backdropFilter: "blur(32px)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          transform: `scale(${cardScale * pulseScale})`,
          opacity: cardOpacity,
          fontFamily:
            "'SF Mono', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
          transition: "border 0.3s ease, box-shadow 0.3s ease",
        }}
      >
        {/* Terminal Header Bar */}
        <div
          style={{
            height: "70px",
            backgroundColor: "rgba(15, 20, 32, 0.95)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            alignItems: "center",
            padding: "0 28px",
            justifyContent: "space-between",
          }}
        >
          {/* Traffic Light Window Controls */}
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <div
              style={{
                width: "16px",
                height: "16px",
                borderRadius: "50%",
                backgroundColor: "#FF5F56",
                boxShadow: "0 0 8px rgba(255, 95, 86, 0.5)",
              }}
            />
            <div
              style={{
                width: "16px",
                height: "16px",
                borderRadius: "50%",
                backgroundColor: "#FFBD2E",
                boxShadow: "0 0 8px rgba(255, 189, 46, 0.5)",
              }}
            />
            <div
              style={{
                width: "16px",
                height: "16px",
                borderRadius: "50%",
                backgroundColor: "#27C93F",
                boxShadow: "0 0 8px rgba(39, 201, 63, 0.5)",
              }}
            />
          </div>

          {/* Window Title & Architecture */}
          <div
            style={{
              fontSize: "19px",
              letterSpacing: "0.08em",
              color: "rgba(220, 230, 245, 0.7)",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <span style={{ color: "rgba(240, 199, 94, 0.9)" }}>●</span>
            don-aurelius — zsh — 980x1280 — arm64
          </div>

          {/* Live Cloud Status */}
          <div
            style={{
              fontSize: "16px",
              color: "#00E5FF",
              border: "1px solid rgba(0, 229, 255, 0.35)",
              padding: "4px 14px",
              borderRadius: "20px",
              backgroundColor: "rgba(0, 229, 255, 0.08)",
              letterSpacing: "0.05em",
            }}
          >
            MT5 BRIDGE READY
          </div>
        </div>

        {/* Terminal Shell Body */}
        <div
          style={{
            flex: 1,
            padding: "36px 36px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            color: "#E2E8F0",
            fontSize: "23px",
            lineHeight: 1.6,
          }}
        >
          {/* STEP 1: Git Clone Input */}
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "12px", fontSize: "21px" }}>
            <span style={{ color: "#F0C75E", fontWeight: "bold" }}>user@quantum-node:~$</span>
            <span
              style={{
                color: "#FFFFFF",
                wordBreak: "break-all",
                textShadow: "0 0 12px rgba(240, 199, 94, 0.7), 0 0 24px rgba(0, 229, 255, 0.5)",
              }}
            >
              {text1}
            </span>
            {localFrame < 240 && cursorBlink && (
              <span style={{ color: "#F0C75E", fontWeight: "bold", textShadow: "0 0 10px #F0C75E" }}>▌</span>
            )}
          </div>

          {/* Step 1 Output Logs */}
          {localFrame >= 240 && (
            <div
              style={{
                color: "rgba(180, 195, 215, 0.75)",
                fontSize: "20px",
                paddingLeft: "10px",
                borderLeft: "2px solid rgba(240, 199, 94, 0.3)",
              }}
            >
              <div>Cloning into 'don-aurelius'...</div>
              <div>remote: Enumerating objects: 2,150, done.</div>
              <div>remote: Compressing objects: 100% (890/890), done.</div>
            </div>
          )}

          {/* STEP 2: Progress Loading Bar */}
          {localFrame >= 260 && (
            <div
              style={{
                marginTop: "10px",
                display: "flex",
                flexDirection: "column",
                gap: "10px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "19px",
                  color: "#F0C75E",
                }}
              >
                <span>PACKING GOLD QUANTUM ARTIFACTS</span>
                <span>{Math.floor(loadProgress)}%</span>
              </div>
              {/* Gold Progress Track */}
              <div
                style={{
                  width: "100%",
                  height: "14px",
                  backgroundColor: "rgba(255, 255, 255, 0.08)",
                  borderRadius: "7px",
                  overflow: "hidden",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    width: `${loadProgress}%`,
                    height: "100%",
                    background:
                      "linear-gradient(90deg, #F0C75E 0%, #FFDF80 50%, #E5A93C 100%)",
                    boxShadow: "0 0 16px rgba(240, 199, 94, 0.7)",
                    borderRadius: "7px",
                    transition: "width 0.1s linear",
                  }}
                />
              </div>
              <div
                style={{
                  fontSize: "18px",
                  color: "rgba(160, 180, 205, 0.7)",
                }}
              >
                Receiving objects: 100% (2150/2150), 24.8 MiB | 42.1 MiB/s, done.
              </div>
            </div>
          )}

          {/* STEP 3: npm install && npm run start:bot */}
          {localFrame >= 520 && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "14px",
                marginTop: "15px",
              }}
            >
              <span style={{ color: "#F0C75E", fontWeight: "bold" }}>
                user@quantum-node:~/don-aurelius$
              </span>
              <span
                style={{
                  color: "#FFFFFF",
                  textShadow: "0 0 12px rgba(240, 199, 94, 0.7), 0 0 24px rgba(0, 229, 255, 0.5)",
                }}
              >
                {text2}
              </span>
              {localFrame >= 540 && localFrame < 720 && cursorBlink && (
                <span style={{ color: "#F0C75E", fontWeight: "bold", textShadow: "0 0 10px #F0C75E" }}>▌</span>
              )}
            </div>
          )}

          {/* Step 3 Kernel Execution Logs */}
          {localFrame >= 720 && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                fontSize: "19px",
                color: "rgba(195, 210, 235, 0.85)",
                backgroundColor: "rgba(5, 8, 15, 0.6)",
                padding: "18px",
                borderRadius: "14px",
                border: "1px solid rgba(255, 255, 255, 0.05)",
              }}
            >
              <div style={{ color: "#00E5FF" }}>
                [KERNEL] MetaTrader 5 Bridge connected (TCP :443) → 0.38ms Latency
              </div>
              <div style={{ color: "#A7F3D0" }}>
                [NEURAL] XAU/USD Deep Liquidity Engine v4.8 loaded [WEIGHTS: 1.2GB]
              </div>
              <div style={{ color: "#FDE047" }}>
                [RISK] Monte Carlo 5,000 Path Simulation Engine: ARMED
              </div>
              <div style={{ color: "#E0E7FF" }}>
                [SECURITY] Hardware-locked RSA-4096 sovereign key verified.
              </div>
            </div>
          )}

          {/* STEP 4: Golden Activation Shockwave & Success Banner */}
          {localFrame >= 880 && (
            <div
              style={{
                marginTop: "auto",
                padding: "26px",
                borderRadius: "18px",
                background:
                  "linear-gradient(135deg, rgba(240, 199, 94, 0.18) 0%, rgba(15, 22, 38, 0.85) 100%)",
                border: "1px solid rgba(240, 199, 94, 0.6)",
                boxShadow: "0 0 50px rgba(240, 199, 94, 0.3)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                gap: "14px",
                transform: `scale(${pulseScale})`,
              }}
            >
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "10px",
                  backgroundColor: "rgba(240, 199, 94, 0.2)",
                  padding: "6px 20px",
                  borderRadius: "30px",
                  border: "1px solid rgba(240, 199, 94, 0.5)",
                }}
              >
                <div
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: "#F0C75E",
                    boxShadow: "0 0 12px #F0C75E",
                  }}
                />
                <span
                  style={{
                    fontSize: "17px",
                    fontWeight: "bold",
                    color: "#F0C75E",
                    letterSpacing: "0.15em",
                  }}
                >
                  SYSTEM DEPLOYED & OPERATIONAL
                </span>
              </div>

              <div
                style={{
                  fontSize: "36px",
                  fontWeight: "bold",
                  color: "#FFFFFF",
                  letterSpacing: "0.08em",
                  textShadow: "0 0 30px rgba(240, 199, 94, 0.5)",
                }}
              >
                DON AURELIUS ENGINE ACTIVE
              </div>

              <div
                style={{
                  fontSize: "20px",
                  color: "rgba(220, 230, 245, 0.8)",
                  letterSpacing: "0.04em",
                }}
              >
                Sovereign Gold Trading Terminal · 89.4% Win Rate · 0.38ms MT5 Bridge
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
