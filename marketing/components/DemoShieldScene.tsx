import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ============================================================================
// THEME & DESIGN TOKENS
// ============================================================================
const TOKENS = {
  bgCanvas: "#030508",
  bgCard: "rgba(9, 15, 26, 0.85)",
  borderGold: "rgba(245, 208, 97, 0.32)",
  borderGoldBright: "rgba(245, 208, 97, 0.85)",
  borderSafeGreen: "rgba(16, 185, 129, 0.55)",
  accentGold: "#F5D061",
  accentGoldDark: "#D4AF37",
  accentGreen: "#10B981",
  accentGreenGlow: "rgba(16, 185, 129, 0.35)",
  accentCyan: "#38BDF8",
  textWhite: "#F8FAFC",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  fontMono: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
  fontSans:
    '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif',
};

// ============================================================================
// GLOWING HOLOGRAPHIC SAFETY SHIELD SVG ICON
// ============================================================================
const HolographicShieldIcon: React.FC<{ pulse: number }> = ({ pulse }) => {
  return (
    <div
      style={{
        position: "relative",
        width: 130,
        height: 130,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Outer Radar Pulse Ring */}
      <div
        style={{
          position: "absolute",
          inset: -16,
          borderRadius: "50%",
          border: `1.5px solid rgba(16, 185, 129, ${0.4 * pulse})`,
          boxShadow: `0 0 35px rgba(16, 185, 129, ${0.3 * pulse})`,
          transform: `scale(${1 + (pulse - 1) * 0.12})`,
          pointerEvents: "none",
        }}
      />

      {/* SVG Shield Emblem */}
      <svg
        width="110"
        height="110"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          filter: `drop-shadow(0 0 22px rgba(16, 185, 129, 0.65)) drop-shadow(0 0 38px rgba(245, 208, 97, 0.35))`,
        }}
      >
        <path
          d="M12 2L3 6V11.5C3 17.02 6.84 22.14 12 23.5C17.16 22.14 21 17.02 21 11.5V6L12 2Z"
          fill="url(#shieldGrad)"
          stroke="#10B981"
          strokeWidth="1.2"
        />
        <path
          d="M9.5 12.2L11.2 13.9L14.8 9.5"
          stroke="#F8FAFC"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="12" cy="12" r="8" stroke="rgba(245, 208, 97, 0.3)" strokeWidth="0.8" />
        <defs>
          <linearGradient id="shieldGrad" x1="12" y1="2" x2="12" y2="23.5" gradientUnits="userSpaceOnUse">
            <stop stopColor="rgba(16, 185, 129, 0.35)" />
            <stop offset="0.65" stopColor="rgba(3, 5, 8, 0.85)" />
            <stop offset="1" stopColor="rgba(245, 208, 97, 0.25)" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
};

// ============================================================================
// DEDICATED COMPONENT: DemoShieldScene (Scene 4: 0:35.0 to 1:00.0)
// ============================================================================
export const DemoShieldScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // --------------------------------------------------------------------------
  // Frame Alignment: Support both Relative Sequence (0-750) & Master (1050-1800)
  // Introductory zoom triggers smoothly at frame 1050 (or relative frame 0).
  // --------------------------------------------------------------------------
  const sceneRelativeFrame = frame >= 1050 ? frame - 1050 : frame;

  // Spring introductory zoom curve
  const zoomSpring = spring({
    frame: sceneRelativeFrame,
    fps,
    config: { damping: 14, stiffness: 115, mass: 0.65 },
  });

  const cardScale = interpolate(zoomSpring, [0, 1], [0.94, 1]);
  const cardOpacity = interpolate(zoomSpring, [0, 1], [0, 1]);
  const cardTranslateY = interpolate(zoomSpring, [0, 1], [16, 0]);

  // Sub-badges staggered entrance springs
  const badgeSpring1 = spring({
    frame: sceneRelativeFrame - 15,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  const badgeSpring2 = spring({
    frame: sceneRelativeFrame - 25,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  const badgeSpring3 = spring({
    frame: sceneRelativeFrame - 35,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  // Outro Phase Switch (Triggers at relative frame 520 / ~52.5s)
  const isOutroPhase = sceneRelativeFrame >= 520;
  const outroSpring = spring({
    frame: sceneRelativeFrame - 520,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.6 },
  });

  // Continuous subtle organic breathing pulse
  const shieldPulse = Math.sin(sceneRelativeFrame / 14) * 0.18 + 0.82;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 54px",
        fontFamily: TOKENS.fontSans,
      }}
    >
      {!isOutroPhase ? (
        <>
          {/* ------------------------------------------------------------------ */}
          {/* Header Step Badge                                                  */}
          {/* ------------------------------------------------------------------ */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "8px 24px",
              borderRadius: 999,
              backgroundColor: "rgba(16, 185, 129, 0.12)",
              border: `1px solid ${TOKENS.borderSafeGreen}`,
              marginBottom: 18,
              opacity: cardOpacity,
              transform: `translateY(${cardTranslateY * 0.5}px)`,
            }}
          >
            <span
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: TOKENS.accentGreen,
                fontFamily: TOKENS.fontMono,
              }}
            >
              STEP 03 OF 03
            </span>
            <span style={{ color: TOKENS.accentGreen }}>•</span>
            <span
              style={{
                fontSize: 18,
                fontWeight: 600,
                color: TOKENS.textWhite,
                letterSpacing: "0.04em",
              }}
            >
              SAFETY GUARDRAIL VERIFICATION
            </span>
          </div>

          <h2
            style={{
              fontSize: 52,
              fontWeight: 800,
              color: TOKENS.textWhite,
              letterSpacing: "-0.03em",
              margin: "0 0 32px 0",
              textAlign: "center",
              opacity: cardOpacity,
              transform: `translateY(${cardTranslateY * 0.5}px)`,
            }}
          >
            Zero Real Capital at Risk
          </h2>

          {/* ------------------------------------------------------------------ */}
          {/* 1. Centralized Holographic Safety Card                             */}
          {/* ------------------------------------------------------------------ */}
          <div
            style={{
              width: 940,
              borderRadius: 24,
              backgroundColor: TOKENS.bgCard,
              border: `2px solid ${TOKENS.borderSafeGreen}`,
              boxShadow: `
                0 35px 75px rgba(0, 0, 0, 0.9),
                0 0 50px rgba(16, 185, 129, ${0.28 * shieldPulse}),
                inset 0 0 30px rgba(16, 185, 129, 0.08)
              `,
              backdropFilter: "blur(24px)",
              padding: "44px 48px",
              transform: `scale(${cardScale}) translateY(${cardTranslateY}px)`,
              opacity: cardOpacity,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 28,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Holographic Shield Icon */}
            <HolographicShieldIcon pulse={shieldPulse} />

            {/* Bold Primary Mode Verification Label */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 8,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 16,
                  fontWeight: 700,
                  letterSpacing: "0.15em",
                  color: TOKENS.accentGreen,
                  fontFamily: TOKENS.fontMono,
                  textTransform: "uppercase",
                }}
              >
                HARD-CODED EXECUTION POLICY LOCKED
              </div>
              <div
                style={{
                  fontSize: 32,
                  fontWeight: 900,
                  letterSpacing: "0.02em",
                  color: TOKENS.textWhite,
                  fontFamily: TOKENS.fontMono,
                  textShadow: `0 0 20px rgba(16, 185, 129, 0.6)`,
                }}
              >
                ACCOUNT_MODE = DEMO (VIRTUAL CAPITAL ONLY)
              </div>
              <div
                style={{
                  fontSize: 18,
                  color: TOKENS.textMuted,
                  maxWidth: 680,
                  lineHeight: 1.4,
                }}
              >
                MetaTrader 5 Account #849201 authenticated. Virtual Sandbox balance
                $100,000.00 secured with zero real capital exposure.
              </div>
            </div>

            {/* ---------------------------------------------------------------- */}
            {/* 2. Clean Visual Sub-Badges (Prop Firm Shield & DD Limit)         */}
            {/* ---------------------------------------------------------------- */}
            <div
              style={{
                width: "100%",
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 18,
                marginTop: 8,
              }}
            >
              {/* Sub-Badge 1: 5% Prop Firm Shield */}
              <div
                style={{
                  padding: "18px 24px",
                  borderRadius: 16,
                  backgroundColor: "rgba(16, 185, 129, 0.08)",
                  border: `1.5px solid ${TOKENS.borderSafeGreen}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  transform: `scale(${Math.max(0, badgeSpring1)})`,
                  opacity: Math.max(0, badgeSpring1),
                  boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    backgroundColor: "rgba(16, 185, 129, 0.18)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 24,
                  }}
                >
                  🛡️
                </div>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span
                    style={{
                      fontSize: 15,
                      fontWeight: 700,
                      color: TOKENS.textDim,
                      fontFamily: TOKENS.fontMono,
                      letterSpacing: "0.06em",
                    }}
                  >
                    PROP FIRM SHIELD
                  </span>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: TOKENS.accentGreen,
                      fontFamily: TOKENS.fontMono,
                    }}
                  >
                    5.00% MAX LOSS CAP
                  </span>
                  <span style={{ fontSize: 13, color: TOKENS.textMuted }}>
                    FTMO / MFFU institutional compliance active
                  </span>
                </div>
              </div>

              {/* Sub-Badge 2: Daily Drawdown Limit */}
              <div
                style={{
                  padding: "18px 24px",
                  borderRadius: 16,
                  backgroundColor: "rgba(245, 208, 97, 0.08)",
                  border: `1.5px solid ${TOKENS.borderGoldBright}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  transform: `scale(${Math.max(0, badgeSpring2)})`,
                  opacity: Math.max(0, badgeSpring2),
                  boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    backgroundColor: "rgba(245, 208, 97, 0.18)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 24,
                  }}
                >
                  🛑
                </div>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span
                    style={{
                      fontSize: 15,
                      fontWeight: 700,
                      color: TOKENS.textDim,
                      fontFamily: TOKENS.fontMono,
                      letterSpacing: "0.06em",
                    }}
                  >
                    DAILY DRAWDOWN LIMIT
                  </span>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: TOKENS.accentGold,
                      fontFamily: TOKENS.fontMono,
                    }}
                  >
                    HARD-STOP AT 1.84%
                  </span>
                  <span style={{ fontSize: 13, color: TOKENS.textMuted }}>
                    Sub-tick auto circuit breaker disarm
                  </span>
                </div>
              </div>
            </div>

            {/* Sub-Badge 3: Consecutive Loss Cooldown Bar */}
            <div
              style={{
                width: "100%",
                padding: "14px 22px",
                borderRadius: 14,
                backgroundColor: "rgba(255, 255, 255, 0.03)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                transform: `scale(${Math.max(0, badgeSpring3)})`,
                opacity: Math.max(0, badgeSpring3),
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 20 }}>⏸️</span>
                <span
                  style={{
                    fontSize: 16,
                    fontWeight: 600,
                    color: TOKENS.textWhite,
                    fontFamily: TOKENS.fontMono,
                  }}
                >
                  Consecutive Loss Cooldown: 3-Loss Automated Pause (4hr Circuit Breaker)
                </span>
              </div>
              <span
                style={{
                  fontSize: 15,
                  fontWeight: 800,
                  color: TOKENS.accentCyan,
                  fontFamily: TOKENS.fontMono,
                }}
              >
                STATUS: ARMED
              </span>
            </div>

            {/* Glowing Refraction Scanline */}
            <div
              style={{
                position: "absolute",
                top: (sceneRelativeFrame % 70) * 8,
                left: 0,
                right: 0,
                height: 2,
                background:
                  "linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.4), transparent)",
                pointerEvents: "none",
              }}
            />
          </div>
        </>
      ) : (
        /* -------------------------------------------------------------------- */
        /* Outro Studio CTA Card (Concluding Phase of 60s Video)                */
        /* -------------------------------------------------------------------- */
        <div
          style={{
            transform: `scale(${outroSpring})`,
            opacity: outroSpring,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
          }}
        >
          {/* 3D Gold Seal Stamp */}
          <div
            style={{
              width: 170,
              height: 170,
              borderRadius: "50%",
              border: `3px solid ${TOKENS.accentGold}`,
              boxShadow: `0 0 60px rgba(245, 208, 97, 0.45)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 32,
              background:
                "radial-gradient(circle, rgba(245, 208, 97, 0.25) 0%, rgba(3, 5, 8, 0.95) 80%)",
            }}
          >
            <span
              style={{
                fontSize: 66,
                fontWeight: 900,
                color: TOKENS.accentGold,
                fontFamily: TOKENS.fontSans,
              }}
            >
              DA
            </span>
          </div>

          <h2
            style={{
              fontSize: 68,
              fontWeight: 800,
              letterSpacing: "-0.035em",
              color: TOKENS.textWhite,
              margin: "0 0 18px 0",
            }}
          >
            Claim Your Free Demo
          </h2>

          <p
            style={{
              fontSize: 28,
              color: TOKENS.textMuted,
              maxWidth: 720,
              margin: "0 0 42px 0",
              lineHeight: 1.45,
            }}
          >
            Deploy Don Aurelius in complete safety. Inspect live session telemetry
            and algorithmic execution on your terminal today.
          </p>

          {/* Glowing CTA Button */}
          <div
            style={{
              padding: "24px 54px",
              borderRadius: 999,
              background: `linear-gradient(135deg, ${TOKENS.accentGold}, ${TOKENS.accentGoldDark})`,
              boxShadow: `0 0 50px rgba(245, 208, 97, 0.5), 0 20px 40px rgba(0, 0, 0, 0.8)`,
              display: "flex",
              alignItems: "center",
              gap: 16,
              cursor: "pointer",
            }}
          >
            <span
              style={{
                fontSize: 26,
                fontWeight: 800,
                color: "#030508",
                letterSpacing: "0.04em",
                fontFamily: TOKENS.fontSans,
              }}
            >
              GET FREE DEMO ACCESS
            </span>
            <span style={{ fontSize: 28, color: "#030508" }}>→</span>
          </div>

          <span
            style={{
              marginTop: 26,
              fontSize: 20,
              color: TOKENS.textDim,
              fontFamily: TOKENS.fontMono,
            }}
          >
            donaurelius.ai • Documentation & Setup Package
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};

export default DemoShieldScene;
