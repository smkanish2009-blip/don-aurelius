import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ============================================================================
// DESIGN SYSTEM TOKENS
// ============================================================================
const TOKENS = {
  bgCanvas: "#030508",
  bgCard: "rgba(9, 15, 26, 0.86)",
  borderGold: "rgba(245, 208, 97, 0.3)",
  borderGoldBright: "rgba(245, 208, 97, 0.85)",
  borderGreen: "rgba(16, 185, 129, 0.5)",
  accentGold: "#F5D061",
  accentGoldDark: "#D4AF37",
  accentGreen: "#10B981",
  accentCyan: "#38BDF8",
  accentPurple: "#A855F7",
  textWhite: "#F8FAFC",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  fontMono: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
  fontSans:
    '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif',
};

// ============================================================================
// SCRIPT FILE METADATA & TREE NODES
// ============================================================================
const TREE_NODES = [
  {
    type: "folder",
    name: "config/",
    desc: "Environment & Terminal Configuration",
    delay: 70,
    children: [
      {
        type: "file",
        name: "settings.py",
        badge: "CORE CONFIG",
        desc: "MT5 Credentials, Risk Multipliers, Symbol Parameters",
        color: TOKENS.accentGold,
        highlight: true,
        delay: 95,
      },
    ],
  },
  {
    type: "folder",
    name: "execution/",
    desc: "Order Routing & Slippage Guards",
    delay: 115,
    children: [
      {
        type: "file",
        name: "order_manager.py",
        badge: "EXECUTION ENGINE",
        desc: "Sub-ms Bracket Orders, Stop Loss & Take Profit Routing",
        color: TOKENS.accentCyan,
        highlight: true,
        delay: 140,
      },
    ],
  },
  {
    type: "folder",
    name: "risk/",
    desc: "Circuit Breakers & Prop Shield",
    delay: 160,
    children: [
      {
        type: "file",
        name: "circuit_breaker.py",
        badge: "PROTECTION",
        desc: "Automated Drawdown Clamps & 3-Loss Cooldown",
        color: TOKENS.accentGreen,
        highlight: false,
        delay: 180,
      },
    ],
  },
  {
    type: "file",
    name: "main.py",
    badge: "SYSTEM ENTRYPOINT",
    desc: "Asynchronous Tick Loop & Multi-Agent Consensus Orchestrator",
    color: TOKENS.accentGold,
    highlight: true,
    delay: 200,
  },
  {
    type: "file",
    name: ".env",
    badge: "SECRETS ACTIVE",
    desc: "Renamed from .env.example (Local Environment Unlocked)",
    color: TOKENS.accentGreen,
    highlight: false,
    delay: 230,
  },
];

// ============================================================================
// DEDICATED COMPONENT: FileExtractionScene (Scene 2: 0:03.5 to 0:14.5)
// ============================================================================
export const FileExtractionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Support both Sequence-relative frame (0..330) and master absolute frame (105..435)
  const sceneRelativeFrame = frame >= 105 && frame <= 435 ? frame - 105 : frame;

  // --------------------------------------------------------------------------
  // Phase 1: Unzipping Simulation (Frames 0 - 85 | 0.0s - 2.8s)
  // --------------------------------------------------------------------------
  const unzipProgress = interpolate(sceneRelativeFrame, [12, 75], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const isExtractionDone = sceneRelativeFrame >= 75;

  const zipCardSpring = spring({
    frame: sceneRelativeFrame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.6 },
  });

  // Tree Card Master Expansion Spring (Frame 70 onwards)
  const treeExpandSpring = spring({
    frame: sceneRelativeFrame - 65,
    fps,
    config: { damping: 14, stiffness: 110, mass: 0.7 },
  });

  const treeOpacity = interpolate(treeExpandSpring, [0, 1], [0, 1]);
  const treeScale = interpolate(treeExpandSpring, [0, 1], [0.88, 1]);

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
      {/* -------------------------------------------------------------------- */}
      {/* Step Header Badge                                                    */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 24px",
          borderRadius: 999,
          backgroundColor: "rgba(245, 208, 97, 0.12)",
          border: `1px solid ${TOKENS.borderGoldBright}`,
          marginBottom: 16,
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 800,
            color: TOKENS.accentGold,
            fontFamily: TOKENS.fontMono,
          }}
        >
          STEP 01 OF 03
        </span>
        <span style={{ color: TOKENS.borderGoldBright }}>•</span>
        <span
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: TOKENS.textWhite,
            letterSpacing: "0.04em",
          }}
        >
          FILE EXTRACTION & DIRECTORY TOPOLOGY
        </span>
      </div>

      <h2
        style={{
          fontSize: 52,
          fontWeight: 800,
          color: TOKENS.textWhite,
          letterSpacing: "-0.03em",
          margin: "0 0 24px 0",
          textAlign: "center",
        }}
      >
        Unpack & Verify Script Placement
      </h2>

      {/* -------------------------------------------------------------------- */}
      {/* 1. Unzipping Progress Card                                           */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          width: 960,
          borderRadius: 20,
          backgroundColor: TOKENS.bgCard,
          border: `1px solid ${
            isExtractionDone ? TOKENS.borderGreen : TOKENS.borderGold
          }`,
          boxShadow: isExtractionDone
            ? "0 20px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(16, 185, 129, 0.2)"
            : "0 20px 45px rgba(0, 0, 0, 0.8), 0 0 35px rgba(245, 208, 97, 0.18)",
          padding: "20px 32px",
          marginBottom: 20,
          transform: `scale(${zipCardSpring})`,
          opacity: zipCardSpring,
          backdropFilter: "blur(20px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          {/* Animated Archive Icon */}
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              backgroundColor: isExtractionDone
                ? "rgba(16, 185, 129, 0.18)"
                : "rgba(245, 208, 97, 0.15)",
              border: `1.5px solid ${
                isExtractionDone ? TOKENS.accentGreen : TOKENS.accentGold
              }`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 28,
            }}
          >
            {isExtractionDone ? "📂" : "📦"}
          </div>

          <div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 800,
                color: TOKENS.textWhite,
                fontFamily: TOKENS.fontMono,
              }}
            >
              Don_Aurelius_Setup.zip
            </div>
            <div style={{ fontSize: 16, color: TOKENS.textMuted }}>
              {isExtractionDone
                ? "Package Decompressed -> 4 Modules Extracted Successfully"
                : "Decompressing institutional trading package..."}
            </div>
          </div>
        </div>

        {/* Unzipping Progress Bar Container */}
        <div
          style={{
            width: 320,
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 15,
              fontFamily: TOKENS.fontMono,
              fontWeight: 700,
              color: isExtractionDone ? TOKENS.accentGreen : TOKENS.accentGold,
            }}
          >
            <span>{isExtractionDone ? "EXTRACTION COMPLETE" : "UNZIPPING"}</span>
            <span>{Math.round(unzipProgress)}%</span>
          </div>

          <div
            style={{
              width: "100%",
              height: 10,
              backgroundColor: "rgba(255, 255, 255, 0.08)",
              borderRadius: 999,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${unzipProgress}%`,
                height: "100%",
                background: isExtractionDone
                  ? `linear-gradient(90deg, #10B981, #34D399)`
                  : `linear-gradient(90deg, ${TOKENS.accentGoldDark}, ${TOKENS.accentGold})`,
                boxShadow: `0 0 16px ${
                  isExtractionDone ? TOKENS.accentGreen : TOKENS.accentGold
                }`,
              }}
            />
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------- */}
      {/* 2. Sleek Animated Tree Layout (Highlighting Key Scripts)            */}
      {/* -------------------------------------------------------------------- */}
      <div
        style={{
          width: 960,
          borderRadius: 24,
          backgroundColor: TOKENS.bgCard,
          border: `1px solid ${TOKENS.borderGold}`,
          boxShadow: "0 30px 60px rgba(0, 0, 0, 0.9), inset 0 0 24px rgba(0, 0, 0, 0.8)",
          backdropFilter: "blur(24px)",
          padding: "28px 36px",
          transform: `scale(${treeScale})`,
          opacity: treeOpacity,
          display: "flex",
          flexDirection: "column",
          gap: 12,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Terminal Window Header Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingBottom: 16,
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            marginBottom: 6,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#EF4444" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: TOKENS.accentGold }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: TOKENS.accentGreen }} />
            <span
              style={{
                marginLeft: 14,
                fontSize: 16,
                fontFamily: TOKENS.fontMono,
                color: TOKENS.textMuted,
              }}
            >
              explorer: ~/don_aurelius_master/
            </span>
          </div>
          <span
            style={{
              fontSize: 15,
              fontWeight: 700,
              fontFamily: TOKENS.fontMono,
              color: TOKENS.accentGold,
            }}
          >
            VERIFIED LOCAL ASSETS
          </span>
        </div>

        {/* Tree Item: config/ -> settings.py */}
        <TreeFolderItem
          folderName="config/"
          desc="System Configuration & Terminal Settings"
          frame={sceneRelativeFrame}
          delay={TREE_NODES[0].delay}
          fps={fps}
        >
          <TreeFileItem
            fileName="settings.py"
            badge="CORE CONFIG"
            desc="MT5 Terminal Bridge & Parameter Registry"
            highlightColor={TOKENS.accentGold}
            frame={sceneRelativeFrame}
            delay={95}
            fps={fps}
          />
        </TreeFolderItem>

        {/* Tree Item: execution/ -> order_manager.py */}
        <TreeFolderItem
          folderName="execution/"
          desc="Sub-Millisecond Order Routing & Bracket Safety"
          frame={sceneRelativeFrame}
          delay={TREE_NODES[1].delay}
          fps={fps}
        >
          <TreeFileItem
            fileName="order_manager.py"
            badge="EXECUTION ENGINE"
            desc="Bracket Order Manager, SL/TP Routing & Lot Multiplier"
            highlightColor={TOKENS.accentCyan}
            frame={sceneRelativeFrame}
            delay={140}
            fps={fps}
          />
        </TreeFolderItem>

        {/* Tree Item: Root main.py */}
        <TreeFileItem
          fileName="main.py"
          badge="SYSTEM ENTRYPOINT"
          desc="Asynchronous Tick Loop & Multi-Agent Neural Consensus Engine"
          highlightColor={TOKENS.accentGold}
          frame={sceneRelativeFrame}
          delay={TREE_NODES[3].delay}
          fps={fps}
          isRootLevel
        />

        {/* Tree Item: .env Config Unlock */}
        <TreeFileItem
          fileName=".env"
          badge="SECRETS ACTIVE"
          desc="Renamed from .env.example (API Keys & Broker Guardrails Loaded)"
          highlightColor={TOKENS.accentGreen}
          frame={sceneRelativeFrame}
          delay={TREE_NODES[4].delay}
          fps={fps}
          isRootLevel
        />

        {/* Holographic Refraction Scanline */}
        <div
          style={{
            position: "absolute",
            top: (sceneRelativeFrame % 60) * 8,
            left: 0,
            right: 0,
            height: 2,
            background:
              "linear-gradient(90deg, transparent, rgba(245, 208, 97, 0.35), transparent)",
            pointerEvents: "none",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// HELPER SUBCOMPONENTS FOR TREE LAYOUT
// ============================================================================

interface TreeFolderProps {
  folderName: string;
  desc: string;
  frame: number;
  delay: number;
  fps: number;
  children: React.ReactNode;
}

const TreeFolderItem: React.FC<TreeFolderProps> = ({
  folderName,
  desc,
  frame,
  delay,
  fps,
  children,
}) => {
  const itemSpring = spring({
    frame: frame - delay,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  const isVisible = frame >= delay;
  if (!isVisible) return null;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
        transform: `translateY(${(1 - itemSpring) * 16}px)`,
        opacity: itemSpring,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 14px",
          borderRadius: 10,
          backgroundColor: "rgba(255, 255, 255, 0.03)",
        }}
      >
        <span style={{ fontSize: 20 }}>📁</span>
        <span
          style={{
            fontSize: 20,
            fontWeight: 700,
            color: TOKENS.textWhite,
            fontFamily: TOKENS.fontMono,
          }}
        >
          {folderName}
        </span>
        <span style={{ fontSize: 15, color: TOKENS.textDim, marginLeft: 8 }}>
          — {desc}
        </span>
      </div>

      {/* Indented Children Container */}
      <div
        style={{
          paddingLeft: 36,
          borderLeft: "2px solid rgba(245, 208, 97, 0.2)",
          marginLeft: 18,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        {children}
      </div>
    </div>
  );
};

interface TreeFileProps {
  fileName: string;
  badge: string;
  desc: string;
  highlightColor: string;
  frame: number;
  delay: number;
  fps: number;
  isRootLevel?: boolean;
}

const TreeFileItem: React.FC<TreeFileProps> = ({
  fileName,
  badge,
  desc,
  highlightColor,
  frame,
  delay,
  fps,
  isRootLevel = false,
}) => {
  const itemSpring = spring({
    frame: frame - delay,
    fps,
    config: { damping: 13, stiffness: 130, mass: 0.5 },
  });

  const isVisible = frame >= delay;
  if (!isVisible) return null;

  // Gentle continuous pulse on highlighted key scripts
  const pulse = Math.sin((frame - delay) / 8) * 0.15 + 0.85;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 18px",
        borderRadius: 12,
        backgroundColor: `rgba(15, 23, 42, 0.75)`,
        border: `1.5px solid ${highlightColor}`,
        boxShadow: `0 8px 24px rgba(0, 0, 0, 0.5), 0 0 20px ${highlightColor}28`,
        transform: `translateY(${(1 - itemSpring) * 16}px)`,
        opacity: itemSpring,
        marginLeft: isRootLevel ? 0 : 4,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={{ fontSize: 22 }}>📄</span>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span
              style={{
                fontSize: 21,
                fontWeight: 800,
                color: TOKENS.textWhite,
                fontFamily: TOKENS.fontMono,
              }}
            >
              {fileName}
            </span>
            <div
              style={{
                padding: "3px 10px",
                borderRadius: 6,
                backgroundColor: `${highlightColor}22`,
                border: `1px solid ${highlightColor}`,
                color: highlightColor,
                fontFamily: TOKENS.fontMono,
                fontSize: 13,
                fontWeight: 800,
                letterSpacing: "0.06em",
              }}
            >
              {badge}
            </div>
          </div>
          <div style={{ fontSize: 14, color: TOKENS.textMuted, marginTop: 2 }}>
            {desc}
          </div>
        </div>
      </div>

      {/* Status Active Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "6px 14px",
          borderRadius: 8,
          backgroundColor: "rgba(255, 255, 255, 0.04)",
          fontFamily: TOKENS.fontMono,
          fontSize: 14,
          fontWeight: 700,
          color: highlightColor,
        }}
      >
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            backgroundColor: highlightColor,
            boxShadow: `0 0 10px ${highlightColor}`,
          }}
        />
        <span>READY</span>
      </div>
    </div>
  );
};

export default FileExtractionScene;
