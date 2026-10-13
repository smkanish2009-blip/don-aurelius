import React from "react";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { TitleScene } from "./components/TitleScene";
import { FileExtractionScene } from "./components/FileExtractionScene";
import { MT5ConnectionScene } from "./components/MT5ConnectionScene";
import { DemoShieldScene } from "./components/DemoShieldScene";

// ============================================================================
// THEME & DESIGN TOKENS (Apple HIG + Imperial Obsidian Gold Standard)
// ============================================================================
export const THEME = {
  bg: "#030508", // Deep Obsidian Canvas
  bgCard: "rgba(11, 15, 25, 0.75)", // Translucent Frosted Glass Card
  bgCardHover: "rgba(18, 24, 38, 0.85)",
  borderGold: "rgba(245, 208, 97, 0.28)", // Imperial Gold Border
  borderGoldBright: "rgba(245, 208, 97, 0.75)",
  accentGold: "#F5D061", // Imperial Gold Core
  accentGoldDark: "#D4AF37", // Burnished Gold
  accentCyan: "#38BDF8", // Radar / Telemetry Cyan
  accentGreen: "#10B981", // Success / Emerald Live
  textWhite: "#F8FAFC",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "JetBrains Mono", sans-serif',
  fontMono: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
};

// ============================================================================
// TIMELINE METRICS (30 FPS, Exactly 60.00 Seconds = 1800 Frames)
// ============================================================================
export const TIMELINE = {
  FPS: 30,
  TOTAL_FRAMES: 1800, // 60.0s
  SCENE_1_TITLE: { from: 0, duration: 105 }, // 0.0s – 3.5s (105 frames)
  SCENE_2_EXTRACT: { from: 105, duration: 330 }, // 3.5s – 14.5s (330 frames)
  SCENE_3_MT5: { from: 435, duration: 615 }, // 14.5s – 35.0s (615 frames)
  SCENE_4_DEMO_SAFE: { from: 1050, duration: 750 }, // 35.0s – 60.0s (750 frames)
};

// ============================================================================
// REUSABLE HUD & AMBIENT COMPONENTS
// ============================================================================

/** Ambient Obsidian Glow & Subtle Animated Grid Background */
export const ObsidianCanvasBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = Math.sin(frame / 35) * 0.15 + 0.85;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: THEME.bg,
        backgroundImage: `
          radial-gradient(circle at 50% 20%, rgba(245, 208, 97, ${0.12 * pulse}) 0%, transparent 55%),
          radial-gradient(circle at 80% 80%, rgba(56, 189, 248, 0.06) 0%, transparent 45%),
          linear-gradient(rgba(245, 208, 97, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(245, 208, 97, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: "100% 100%, 100% 100%, 48px 48px, 48px 48px",
        overflow: "hidden",
      }}
    >
      {/* Top Vignette Layer */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at center, transparent 40%, rgba(3, 5, 8, 0.88) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

/** Global Progress Bar & Broadcast Timestamp Header */
export const GlobalTimelineHUD: React.FC = () => {
  const frame = useCurrentFrame();
  const progressPercent = Math.min(100, (frame / TIMELINE.TOTAL_FRAMES) * 100);
  const currentSeconds = Math.min(60, frame / TIMELINE.FPS);

  return (
    <div
      style={{
        position: "absolute",
        top: 48,
        left: 60,
        right: 60,
        zIndex: 100,
        display: "flex",
        flexDirection: "column",
        gap: 12,
        fontFamily: THEME.fontFamily,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: THEME.accentGreen,
              boxShadow: `0 0 12px ${THEME.accentGreen}`,
            }}
          />
          <span
            style={{
              fontSize: 22,
              fontWeight: 700,
              letterSpacing: "0.08em",
              color: THEME.accentGold,
              fontFamily: THEME.fontMono,
            }}
          >
            DON AURELIUS • MASTERCLASS
          </span>
        </div>
        <div
          style={{
            fontSize: 22,
            fontWeight: 600,
            color: THEME.textMuted,
            fontFamily: THEME.fontMono,
          }}
        >
          {currentSeconds.toFixed(1)}s / 60.0s
        </div>
      </div>

      {/* High-Contrast Dual-Track Progress Line */}
      <div
        style={{
          width: "100%",
          height: 6,
          backgroundColor: "rgba(255, 255, 255, 0.1)",
          borderRadius: 4,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${progressPercent}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${THEME.accentGoldDark}, ${THEME.accentGold})`,
            boxShadow: `0 0 16px ${THEME.accentGold}`,
          }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// SCENE 1: TITLE SCREEN (0:00 – 0:05.5 | Frames 0 – 165)
// ============================================================================
export const TitleScreen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.7 },
  });

  const subtitleSpring = spring({
    frame: frame - 12,
    fps,
    config: { damping: 15, stiffness: 110, mass: 0.8 },
  });

  const badgeSpring = spring({
    frame: frame - 22,
    fps,
    config: { damping: 12, stiffness: 130, mass: 0.6 },
  });

  const sealRotate = frame * 0.45;
  const sealScale = interpolate(frame, [0, 40], [0.85, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 64px",
        textAlign: "center",
        fontFamily: THEME.fontFamily,
      }}
    >
      {/* 3D Aurelius Golden Seal Stamp */}
      <div
        style={{
          width: 190,
          height: 190,
          borderRadius: "50%",
          border: `3px solid ${THEME.accentGold}`,
          boxShadow: `0 0 50px rgba(245, 208, 97, 0.35), inset 0 0 30px rgba(245, 208, 97, 0.25)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 44,
          transform: `scale(${sealScale}) rotate(${sealRotate}deg)`,
          background:
            "radial-gradient(circle, rgba(245, 208, 97, 0.18) 0%, rgba(3, 5, 8, 0.9) 70%)",
        }}
      >
        <span
          style={{
            fontSize: 74,
            fontWeight: 900,
            color: THEME.accentGold,
            letterSpacing: "-0.04em",
          }}
        >
          DA
        </span>
      </div>

      {/* Category Pill Badge */}
      <div
        style={{
          transform: `scale(${badgeSpring})`,
          opacity: badgeSpring,
          display: "inline-flex",
          alignItems: "center",
          gap: 10,
          padding: "10px 24px",
          borderRadius: 999,
          backgroundColor: "rgba(245, 208, 97, 0.12)",
          border: `1px solid ${THEME.borderGoldBright}`,
          marginBottom: 24,
        }}
      >
        <span style={{ fontSize: 18, color: THEME.accentGold }}>⚡</span>
        <span
          style={{
            fontSize: 20,
            fontWeight: 700,
            color: THEME.accentGold,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            fontFamily: THEME.fontMono,
          }}
        >
          Institutional Gold Deployment
        </span>
      </div>

      {/* Master Punchy Headline */}
      <h1
        style={{
          transform: `scale(${titleSpring}) translateY(${(1 - titleSpring) * 35}px)`,
          opacity: titleSpring,
          fontSize: 76,
          fontWeight: 800,
          letterSpacing: "-0.035em",
          lineHeight: 1.08,
          margin: "0 0 24px 0",
          color: THEME.textWhite,
          textShadow: "0 10px 30px rgba(0, 0, 0, 0.9)",
        }}
      >
        Deploy in{" "}
        <span
          style={{
            background: `linear-gradient(135deg, ${THEME.accentGold}, #FFF8E1)`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textShadow: "none",
          }}
        >
          Sixty Seconds.
        </span>
      </h1>

      {/* Subtitle / Value Prop */}
      <p
        style={{
          transform: `translateY(${(1 - subtitleSpring) * 20}px)`,
          opacity: subtitleSpring,
          fontSize: 32,
          fontWeight: 400,
          color: THEME.textMuted,
          lineHeight: 1.45,
          maxWidth: 820,
          margin: 0,
        }}
      >
        Zero manual analysis. Institutional multi-agent consensus. Hard-coded
        demo safety guardrails.
      </p>

      {/* Stat Bar Bottom Preview */}
      <div
        style={{
          marginTop: 64,
          display: "flex",
          gap: 28,
        }}
      >
        {[
          { label: "Execution Latency", val: "0.38 ms", color: THEME.accentCyan },
          { label: "Win Rate Audit", val: "89.4%", color: THEME.accentGold },
          { label: "Safety Sandbox", val: "100% Locked", color: THEME.accentGreen },
        ].map((item, idx) => (
          <div
            key={idx}
            style={{
              padding: "16px 28px",
              borderRadius: 16,
              backgroundColor: THEME.bgCard,
              border: `1px solid ${THEME.borderGold}`,
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            <span style={{ fontSize: 16, color: THEME.textDim }}>{item.label}</span>
            <span
              style={{
                fontSize: 26,
                fontWeight: 700,
                color: item.color,
                fontFamily: THEME.fontMono,
              }}
            >
              {item.val}
            </span>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// SCENE 2: FILE EXTRACTION & ENV CONFIG (0:05.5 – 0:14.5 | Frames 165 – 435)
// ============================================================================
export const FileExtraction: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.7 },
  });

  const renameTrigger = frame >= 75; // Trigger rename after 2.5 seconds in scene
  const renamePulse = renameTrigger
    ? Math.sin((frame - 75) / 10) * 0.2 + 0.8
    : 1;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 64px",
        fontFamily: THEME.fontFamily,
      }}
    >
      {/* Step Header Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 22px",
          borderRadius: 999,
          backgroundColor: "rgba(245, 208, 97, 0.12)",
          border: `1px solid ${THEME.borderGoldBright}`,
          marginBottom: 20,
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 800,
            color: THEME.accentGold,
            fontFamily: THEME.fontMono,
          }}
        >
          STEP 01 OF 03
        </span>
        <span style={{ color: THEME.borderGoldBright }}>•</span>
        <span style={{ fontSize: 18, fontWeight: 600, color: THEME.textWhite }}>
          EXTRACTION & LOCAL ENVIRONMENT
        </span>
      </div>

      <h2
        style={{
          fontSize: 54,
          fontWeight: 800,
          color: THEME.textWhite,
          margin: "0 0 36px 0",
          textAlign: "center",
        }}
      >
        Unpack & Initialize Config
      </h2>

      {/* Main Glassmorphic File Explorer Card */}
      <div
        style={{
          width: 860,
          borderRadius: 24,
          backgroundColor: THEME.bgCard,
          border: `1px solid ${THEME.borderGold}`,
          boxShadow: "0 30px 60px rgba(0,0,0,0.8), 0 0 40px rgba(245, 208, 97, 0.12)",
          backdropFilter: "blur(20px)",
          overflow: "hidden",
          transform: `scale(${cardSpring})`,
          opacity: cardSpring,
        }}
      >
        {/* Terminal / Explorer Window Titlebar */}
        <div
          style={{
            padding: "18px 28px",
            backgroundColor: "rgba(0, 0, 0, 0.45)",
            borderBottom: `1px solid ${THEME.borderGold}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: "#EF4444",
              }}
            />
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: "#F59E0B",
              }}
            />
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: "#10B981",
              }}
            />
            <span
              style={{
                marginLeft: 16,
                fontSize: 18,
                color: THEME.textMuted,
                fontFamily: THEME.fontMono,
              }}
            >
              Don_Aurelius_Setup/
            </span>
          </div>
          <span
            style={{
              fontSize: 16,
              color: THEME.accentGold,
              fontFamily: THEME.fontMono,
            }}
          >
            EXTRACTED VERIFIED
          </span>
        </div>

        {/* Directory Structure List */}
        <div style={{ padding: "32px 36px", display: "flex", flexDirection: "column", gap: 18 }}>
          {[
            { name: "📁 core/", desc: "Multi-Agent Neural Consensus Engine", color: THEME.textWhite },
            { name: "📁 execution/", desc: "Sub-Millisecond MetaTrader 5 Bridge", color: THEME.textWhite },
            { name: "📁 risk/", desc: "Prop Firm Guard & Triple Circuit Breakers", color: THEME.textWhite },
          ].map((dir, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "14px 20px",
                borderRadius: 12,
                backgroundColor: "rgba(255, 255, 255, 0.03)",
                border: "1px solid rgba(255, 255, 255, 0.06)",
              }}
            >
              <span
                style={{
                  fontSize: 22,
                  fontWeight: 600,
                  fontFamily: THEME.fontMono,
                  color: dir.color,
                }}
              >
                {dir.name}
              </span>
              <span style={{ fontSize: 18, color: THEME.textDim }}>{dir.desc}</span>
            </div>
          ))}

          {/* Interactive Renaming Highlight (.env.example -> .env) */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "18px 24px",
              borderRadius: 14,
              backgroundColor: renameTrigger
                ? "rgba(16, 185, 129, 0.12)"
                : "rgba(245, 208, 97, 0.1)",
              border: `2px solid ${
                renameTrigger ? THEME.accentGreen : THEME.accentGold
              }`,
              boxShadow: renameTrigger
                ? `0 0 24px rgba(16, 185, 129, 0.3 * ${renamePulse})`
                : `0 0 20px rgba(245, 208, 97, 0.2)`,
              transition: "all 0.3s ease",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 26 }}>⚙️</span>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span
                  style={{
                    fontSize: 24,
                    fontWeight: 700,
                    fontFamily: THEME.fontMono,
                    color: renameTrigger ? THEME.accentGreen : THEME.accentGold,
                  }}
                >
                  {renameTrigger ? "📄 .env" : "📄 .env.example"}
                </span>
                <span style={{ fontSize: 16, color: THEME.textMuted }}>
                  {renameTrigger
                    ? "Configuration Unlocked • Secrets Ready"
                    : "Rename to .env to unlock trading parameters"}
                </span>
              </div>
            </div>

            <div
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                backgroundColor: renameTrigger
                  ? "rgba(16, 185, 129, 0.25)"
                  : "rgba(245, 208, 97, 0.2)",
                color: renameTrigger ? THEME.accentGreen : THEME.accentGold,
                fontFamily: THEME.fontMono,
                fontSize: 16,
                fontWeight: 700,
              }}
            >
              {renameTrigger ? "ACTIVE" : "ACTION REQUIRED"}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// SCENE 3: MT5 / MQL5 CONNECTION (0:14.5 – 0:35.0 | Frames 435 – 1050)
// ============================================================================
export const MT5Connection: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subphase split: 0-300 frames is MT5 button toggle, 300+ is Python IPC bridge
  const isPythonBridgePhase = frame >= 300;

  const algoToggleActive = frame >= 120; // Algo trading button turns green
  const terminalScroll = interpolate(frame, [300, 580], [0, -180], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.7 },
  });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 64px",
        fontFamily: THEME.fontFamily,
      }}
    >
      {/* Step Header Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 22px",
          borderRadius: 999,
          backgroundColor: "rgba(245, 208, 97, 0.12)",
          border: `1px solid ${THEME.borderGoldBright}`,
          marginBottom: 20,
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 800,
            color: THEME.accentGold,
            fontFamily: THEME.fontMono,
          }}
        >
          STEP 02 OF 03
        </span>
        <span style={{ color: THEME.borderGoldBright }}>•</span>
        <span style={{ fontSize: 18, fontWeight: 600, color: THEME.textWhite }}>
          METATRADER 5 & PYTHON IPC BRIDGE
        </span>
      </div>

      <h2
        style={{
          fontSize: 54,
          fontWeight: 800,
          color: THEME.textWhite,
          margin: "0 0 32px 0",
          textAlign: "center",
        }}
      >
        {isPythonBridgePhase
          ? "Bridge Python / Backtrader to MT5"
          : "Activate MT5 Algorithmic Trading"}
      </h2>

      {/* Main Dual-View Showcase */}
      <div
        style={{
          width: 920,
          borderRadius: 24,
          backgroundColor: THEME.bgCard,
          border: `1px solid ${THEME.borderGold}`,
          boxShadow: "0 30px 60px rgba(0,0,0,0.8), 0 0 40px rgba(245, 208, 97, 0.15)",
          backdropFilter: "blur(20px)",
          overflow: "hidden",
          transform: `scale(${cardSpring})`,
        }}
      >
        {/* MT5 Top Toolbar Mockup */}
        <div
          style={{
            padding: "20px 28px",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            borderBottom: `1px solid ${THEME.borderGold}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <span
              style={{
                fontSize: 20,
                fontWeight: 700,
                color: THEME.textWhite,
                fontFamily: THEME.fontMono,
              }}
            >
              MetaTrader 5 • Terminal #849201
            </span>
            <span
              style={{
                padding: "4px 12px",
                borderRadius: 6,
                backgroundColor: "rgba(56, 189, 248, 0.15)",
                color: THEME.accentCyan,
                fontSize: 14,
                fontFamily: THEME.fontMono,
              }}
            >
              XAUUSD [M1]
            </span>
          </div>

          {/* Golden Spotlight on Algo Trading Button */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "10px 20px",
              borderRadius: 12,
              backgroundColor: algoToggleActive
                ? "rgba(16, 185, 129, 0.22)"
                : "rgba(239, 68, 68, 0.15)",
              border: `2px solid ${
                algoToggleActive ? THEME.accentGreen : "rgba(239, 68, 68, 0.5)"
              }`,
              boxShadow: algoToggleActive
                ? `0 0 24px ${THEME.accentGreen}`
                : "none",
            }}
          >
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: algoToggleActive
                  ? THEME.accentGreen
                  : "#EF4444",
                boxShadow: `0 0 10px ${
                  algoToggleActive ? THEME.accentGreen : "#EF4444"
                }`,
              }}
            />
            <span
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: algoToggleActive ? THEME.accentGreen : "#FCA5A5",
                fontFamily: THEME.fontMono,
              }}
            >
              {algoToggleActive ? "ALGO TRADING: ACTIVE" : "ALGO TRADING: OFF"}
            </span>
          </div>
        </div>

        {/* Console / Python IPC Log Section */}
        <div
          style={{
            padding: "28px 32px",
            backgroundColor: "#020408",
            minHeight: 280,
            fontFamily: THEME.fontMono,
            fontSize: 20,
            lineHeight: 1.7,
            color: "#A7F3D0",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div style={{ transform: `translateY(${terminalScroll}px)` }}>
            <div style={{ color: THEME.textDim }}>
              $ python scripts/check_live_mt5.py
            </div>
            <div style={{ color: THEME.accentGold, marginTop: 8 }}>
              [+] Connecting to local MetaTrader 5 IPC Socket...
            </div>
            <div style={{ color: THEME.accentGreen }}>
              [+] MetaTrader5.initialize(): SUCCESS (Build 4410)
            </div>
            <div style={{ color: THEME.accentCyan }}>
              [+] Symbol: XAU/USD (Gold Spot) Detected & Subscribed
            </div>
            <div style={{ color: "#E2E8F0" }}>
              [+] Backtrader Feed Engine: Real-Time Stream Synchronized
            </div>
            <div style={{ color: THEME.accentGold, fontWeight: 700 }}>
              [+] Tick Latency: 0.38ms • Direct Memory Pipe Armed
            </div>
            <div style={{ color: THEME.accentGreen }}>
              [+] STATUS: HIGH-FREQUENCY IPC BRIDGE FULLY OPERATIONAL
            </div>
          </div>

          {/* Glowing Scanline Overlay */}
          <div
            style={{
              position: "absolute",
              top: (frame % 80) * 4,
              left: 0,
              right: 0,
              height: 2,
              background:
                "linear-gradient(90deg, transparent, rgba(245, 208, 97, 0.4), transparent)",
              pointerEvents: "none",
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// SCENE 4: DEMO SAFE VERIFICATION & OUTRO (0:35.0 – 1:00.0 | Frames 1050 – 1800)
// ============================================================================
export const DemoSafeVerification: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subphases:
  // 0 – 300: Demo Safety Guardrail verification
  // 300 – 540: Bat file execution payoff
  // 540 – 750: Outro CTA card
  const isOutroPhase = frame >= 540;

  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.7 },
  });

  const ctaSpring = spring({
    frame: frame - 540,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.6 },
  });

  const shieldPulse = Math.sin(frame / 12) * 0.15 + 0.85;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 64px",
        fontFamily: THEME.fontFamily,
      }}
    >
      {!isOutroPhase ? (
        <>
          {/* Step Header Badge */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "8px 22px",
              borderRadius: 999,
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              border: `1px solid ${THEME.accentGreen}`,
              marginBottom: 20,
            }}
          >
            <span
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: THEME.accentGreen,
                fontFamily: THEME.fontMono,
              }}
            >
              STEP 03 OF 03
            </span>
            <span style={{ color: THEME.accentGreen }}>•</span>
            <span style={{ fontSize: 18, fontWeight: 600, color: THEME.textWhite }}>
              DEMO ACCOUNT SAFETY GUARDRAIL
            </span>
          </div>

          <h2
            style={{
              fontSize: 54,
              fontWeight: 800,
              color: THEME.textWhite,
              margin: "0 0 32px 0",
              textAlign: "center",
            }}
          >
            Zero Real Capital at Risk
          </h2>

          {/* Safety Shield Hologram Card */}
          <div
            style={{
              width: 880,
              borderRadius: 24,
              backgroundColor: THEME.bgCard,
              border: `2px solid ${THEME.accentGreen}`,
              boxShadow: `0 30px 60px rgba(0,0,0,0.8), 0 0 50px rgba(16, 185, 129, ${
                0.25 * shieldPulse
              })`,
              backdropFilter: "blur(20px)",
              padding: "36px 44px",
              transform: `scale(${cardSpring})`,
              display: "flex",
              flexDirection: "column",
              gap: 24,
            }}
          >
            {/* Hardcoded Guardrail Verification Banner */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "20px 28px",
                borderRadius: 16,
                backgroundColor: "rgba(16, 185, 129, 0.15)",
                border: "1px solid rgba(16, 185, 129, 0.4)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <span style={{ fontSize: 36 }}>🛡️</span>
                <div>
                  <div
                    style={{
                      fontSize: 22,
                      fontWeight: 800,
                      color: THEME.accentGreen,
                      fontFamily: THEME.fontMono,
                    }}
                  >
                    SAFETY GUARDRAIL: LOCKED
                  </div>
                  <div style={{ fontSize: 17, color: THEME.textMuted }}>
                    Account #849201 verified as VIRTUAL DEMO
                  </div>
                </div>
              </div>
              <div
                style={{
                  padding: "8px 18px",
                  borderRadius: 8,
                  backgroundColor: THEME.accentGreen,
                  color: "#022C22",
                  fontSize: 16,
                  fontWeight: 800,
                  fontFamily: THEME.fontMono,
                }}
              >
                100% SANDBOXED
              </div>
            </div>

            {/* Circuit Breakers Active Display */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 20,
              }}
            >
              {[
                { title: "Prop Firm Shield", val: "ACTIVE (5% Max Loss Cap)", icon: "🔒" },
                { title: "Daily Drawdown Limiter", val: "HARD-STOP AT 1.84%", icon: "🛑" },
                { title: "Consecutive Loss Cooldown", val: "3-LOSS AUTO-DISARM", icon: "⏸️" },
                { title: "Live Execution Payload", val: "Start_Don_Aurelius.bat READY", icon: "🚀" },
              ].map((rule, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "18px 22px",
                    borderRadius: 14,
                    backgroundColor: "rgba(255, 255, 255, 0.04)",
                    border: `1px solid ${THEME.borderGold}`,
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                  }}
                >
                  <span style={{ fontSize: 26 }}>{rule.icon}</span>
                  <div>
                    <div style={{ fontSize: 16, color: THEME.textDim }}>{rule.title}</div>
                    <div
                      style={{
                        fontSize: 19,
                        fontWeight: 700,
                        color: THEME.accentGold,
                        fontFamily: THEME.fontMono,
                      }}
                    >
                      {rule.val}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        /* Final High-Conversion Studio Outro */
        <div
          style={{
            transform: `scale(${ctaSpring})`,
            opacity: ctaSpring,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
          }}
        >
          {/* 3D Gold Seal Stamp */}
          <div
            style={{
              width: 160,
              height: 160,
              borderRadius: "50%",
              border: `3px solid ${THEME.accentGold}`,
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
                fontSize: 62,
                fontWeight: 900,
                color: THEME.accentGold,
              }}
            >
              DA
            </span>
          </div>

          <h2
            style={{
              fontSize: 68,
              fontWeight: 800,
              letterSpacing: "-0.03em",
              color: THEME.textWhite,
              margin: "0 0 20px 0",
            }}
          >
            Claim Your Free Demo
          </h2>

          <p
            style={{
              fontSize: 28,
              color: THEME.textMuted,
              maxWidth: 720,
              margin: "0 0 44px 0",
              lineHeight: 1.45,
            }}
          >
            Deploy Don Aurelius in complete safety. Inspect live session
            telemetry and algorithmic execution on your terminal today.
          </p>

          {/* High-Contrast Interactive CTA Button */}
          <div
            style={{
              padding: "24px 54px",
              borderRadius: 999,
              background: `linear-gradient(135deg, ${THEME.accentGold}, #D4AF37)`,
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
                fontFamily: THEME.fontFamily,
              }}
            >
              GET FREE DEMO ACCESS
            </span>
            <span style={{ fontSize: 28, color: "#030508" }}>→</span>
          </div>

          <span
            style={{
              marginTop: 28,
              fontSize: 20,
              color: THEME.textDim,
              fontFamily: THEME.fontMono,
            }}
          >
            donaurelius.ai • Documentation & Setup Package
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};

// ============================================================================
// MASTER 60-SECOND COMPOSITION
// ============================================================================
export const TutorialVideoComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: THEME.bg, overflow: "hidden" }}>
      {/* 1. Canvas Background */}
      <ObsidianCanvasBackground />

      {/* 2. Audio Track: Voiceover generated by Edge-TTS */}
      <Audio src={staticFile("audio/tutorial_voiceover.mp3")} volume={1.0} />

      {/* 3. Global Timeline Header HUD */}
      <GlobalTimelineHUD />

      {/* 4. Scene 1: Title Screen (Frames 0 – 105 | 0.0s – 3.5s) */}
      <Sequence
        from={TIMELINE.SCENE_1_TITLE.from}
        durationInFrames={TIMELINE.SCENE_1_TITLE.duration}
      >
        <TitleScene />
      </Sequence>

      {/* 5. Scene 2: File Extraction (Frames 105 – 435 | 3.5s – 14.5s) */}
      <Sequence
        from={TIMELINE.SCENE_2_EXTRACT.from}
        durationInFrames={TIMELINE.SCENE_2_EXTRACT.duration}
      >
        <FileExtractionScene />
      </Sequence>

      {/* 6. Scene 3: MT5 / MQL5 Connection (Frames 435 – 1050 | 14.5s – 35.0s) */}
      <Sequence
        from={TIMELINE.SCENE_3_MT5.from}
        durationInFrames={TIMELINE.SCENE_3_MT5.duration}
      >
        <MT5ConnectionScene />
      </Sequence>

      {/* 7. Scene 4: Demo Safe Verification & Outro (Frames 1050 – 1800 | 35.0s – 60.0s) */}
      <Sequence
        from={TIMELINE.SCENE_4_DEMO_SAFE.from}
        durationInFrames={TIMELINE.SCENE_4_DEMO_SAFE.duration}
      >
        <DemoShieldScene />
      </Sequence>
    </AbsoluteFill>
  );
};

// Default export alias matching standard naming conventions
export const DonAureliusTutorial60s = TutorialVideoComposition;
export default TutorialVideoComposition;
