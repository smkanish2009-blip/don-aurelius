import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface TextCardProps {
  startFrame: number;
  endFrame: number;
  text: string;
  subtext?: string;
  goldAccent?: boolean;
}

const TextCard: React.FC<TextCardProps> = ({
  startFrame,
  endFrame,
  text,
  subtext,
  goldAccent = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  const localFrame = frame - startFrame;
  const duration = endFrame - startFrame;

  // Spring physics from 95% to 100% scale
  const springProgress = spring({
    frame: localFrame,
    fps,
    config: {
      damping: 24,
      mass: 1.2,
      stiffness: 70,
    },
  });

  const baseScale = interpolate(springProgress, [0, 1], [0.95, 1.0]);
  // Continuous slow cinematic drift forward
  const drift = interpolate(localFrame, [0, duration], [0, 0.035], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const currentScale = baseScale + drift;

  // Fade from darkness (first 18 frames), hold, then abrupt hard musical cut at end
  const opacity = interpolate(
    localFrame,
    [0, 18, duration - 6, duration],
    [0.0, 1.0, 1.0, 0.0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "1080px",
        height: "1920px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 60px",
        boxSizing: "border-box",
        textAlign: "center",
        opacity,
        transform: `scale(${currentScale})`,
        pointerEvents: "none",
        zIndex: 40,
      }}
    >
      {/* Background Radial Chiaroscuro Shadow to ensure supreme readability */}
      <div
        style={{
          position: "absolute",
          width: "900px",
          height: "600px",
          background:
            "radial-gradient(ellipse at center, rgba(3, 4, 7, 0.88) 0%, rgba(3, 4, 7, 0.5) 50%, transparent 80%)",
          filter: "blur(20px)",
          zIndex: -1,
        }}
      />

      {/* Main Heavy All-Caps Serif Typography */}
      <h1
        style={{
          fontFamily:
            "'Cinzel', 'Playfair Display', 'Didot', 'Bodoni MT', 'Georgia', serif",
          fontWeight: 900,
          fontSize: text.length > 25 ? "54px" : "68px",
          lineHeight: 1.15,
          letterSpacing: "0.22em",
          color: goldAccent ? "#F5D061" : "#FFFFFF",
          textTransform: "uppercase",
          margin: 0,
          textShadow: goldAccent
            ? "0 0 35px rgba(240, 199, 94, 0.65), 0 4px 16px rgba(0,0,0,0.9)"
            : "0 0 40px rgba(255, 255, 255, 0.35), 0 4px 20px rgba(0,0,0,0.95)",
        }}
      >
        {text}
      </h1>

      {subtext && (
        <p
          style={{
            fontFamily:
              "'Cinzel', 'Trajan Pro', 'Bodoni MT', 'Georgia', serif",
            fontWeight: 400,
            fontSize: "24px",
            letterSpacing: "0.3em",
            color: "rgba(235, 240, 255, 0.75)",
            textTransform: "uppercase",
            marginTop: "24px",
            textShadow: "0 2px 10px rgba(0,0,0,0.9)",
          }}
        >
          {subtext}
        </p>
      )}
    </div>
  );
};

export const KineticTypography: React.FC = () => {
  return (
    <>
      {/* ===================================================================== */}
      {/* NARRATIVE TEXT MAP (Matching exact user timeline requirements)        */}
      {/* ===================================================================== */}

      {/* Frame 300: "MARKETS FAIL." */}
      <TextCard
        startFrame={300}
        endFrame={570}
        text="MARKETS FAIL."
        subtext="THE ILLUSION OF MANUAL CERTAINTY"
      />

      {/* Frame 600: "HUMANS HESITATE." */}
      <TextCard
        startFrame={600}
        endFrame={870}
        text="HUMANS HESITATE."
        subtext="EMOTIONAL BIAS DESTROYS CAPITAL"
      />

      {/* Frame 900: "GOLD REMAINS." */}
      <TextCard
        startFrame={900}
        endFrame={1080}
        text="GOLD REMAINS."
        subtext="XAU/USD SOVEREIGN STANDARD"
        goldAccent
      />

      {/* Frame 1200: "INTRODUCING DON AURELIUS" */}
      <TextCard
        startFrame={1200}
        endFrame={1560}
        text="INTRODUCING DON AURELIUS"
        subtext="AUTONOMOUS QUANTITATIVE SYNDICATE"
        goldAccent
      />

      {/* Frame 2400: "89.4% WIN RATE OVER 2,150 TRADES" */}
      <TextCard
        startFrame={2400}
        endFrame={2760}
        text="89.4% WIN RATE OVER 2,150 TRADES"
        subtext="MATHEMATICAL LIQUIDITY DOMINANCE"
        goldAccent
      />

      {/* Frame 3000: "DEEP LIQUIDITY BOT OPTIMIZATION" */}
      <TextCard
        startFrame={3000}
        endFrame={3360}
        text="DEEP LIQUIDITY BOT OPTIMIZATION"
        subtext="SUB-MILLIS TIER-1 ORDER ROUTING"
      />

      {/* Frame 3700: "DEPLOY IN SECONDS" */}
      <TextCard
        startFrame={3700}
        endFrame={3960}
        text="DEPLOY IN SECONDS"
        subtext="INSTANT CLOUD EXECUTION"
        goldAccent
      />
    </>
  );
};
