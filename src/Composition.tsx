import React from "react";
import {
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { AudioEngine } from "./components/AudioEngine";
import { VFXBackground } from "./components/VFXBackground";
import { TutorialWidget } from "./components/TutorialWidget";
import { KineticTypography } from "./components/KineticTypography";
import { HUDOverlay } from "./components/HUDOverlay";

export const MasterComposition: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Custom Nolan cinematic cubic-bezier easing curve
  const nolanCubicEase = Easing.bezier(0.25, 0.1, 0.25, 1.0);

  // =========================================================================
  // 5 NARRATIVE ACT TIMELINE ORCHESTRATION
  // Total: 5400 frames (90 seconds @ 60fps)
  // ACT I:   The Hook / Chaos (Frames 0 - 1080 | 0s - 18s)
  // ACT II:  The Paradigm Shift / The Reveal (Frames 1080 - 2160 | 18s - 36s)
  // ACT III: Core Features / Live Intelligence (Frames 2160 - 3600 | 36s - 60s)
  // ACT IV:  Masterclass Tutorial / Installation (Frames 3600 - 4860 | 60s - 81s)
  // ACT V:   Title Card & Call-To-Action (Frames 4860 - 5400 | 81s - 90s)
  // =========================================================================

  // Master Global Atmospheric Intensity across the 5 Acts
  const act1Transition = interpolate(frame, [0, 900, 1080], [1.0, 1.0, 0.0], {
    easing: nolanCubicEase,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const act2Transition = interpolate(
    frame,
    [1080, 1200, 2040, 2160],
    [0.0, 1.0, 1.0, 0.0],
    {
      easing: nolanCubicEase,
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const act3Transition = interpolate(
    frame,
    [2160, 2280, 3480, 3600],
    [0.0, 1.0, 1.0, 0.0],
    {
      easing: nolanCubicEase,
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const act4Transition = interpolate(
    frame,
    [3600, 3720, 4800, 4860],
    [0.0, 1.0, 1.0, 0.0],
    {
      easing: nolanCubicEase,
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const act5Transition = interpolate(frame, [4860, 4940, 5400], [0.0, 1.0, 1.0], {
    easing: nolanCubicEase,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Global Flash at Act Junctions (Braam Hits: 1080, 2160, 3600)
  const junctionFlash = (() => {
    if (frame >= 1076 && frame <= 1092) {
      return interpolate(frame, [1076, 1080, 1092], [0.0, 0.45, 0.0]);
    }
    if (frame >= 2156 && frame <= 2172) {
      return interpolate(frame, [2156, 2160, 2172], [0.0, 0.5, 0.0]);
    }
    if (frame >= 3596 && frame <= 3612) {
      return interpolate(frame, [3596, 3600, 3612], [0.0, 0.6, 0.0]);
    }
    return 0.0;
  })();

  // Dead Silence Drop at Frame 4860: Hard pitch-black fade for 1 second (4860 - 4920)
  const isSilenceBlackout = frame >= 4860 && frame < 4920;

  // Master Letterbox Framing (Classic Christopher Nolan Panavision 70mm styling)
  const letterboxHeight = 48; // Subtle top and bottom matte lines

  return (
    <div
      style={{
        position: "relative",
        width: "1080px",
        height: "1920px",
        backgroundColor: "#000000",
        overflow: "hidden",
      }}
    >
      {/* 1. Global Multi-Layer Audio Engine */}
      <AudioEngine />

      {/* 2. Visual Effects & 3D Background Imagery */}
      <VFXBackground />

      {/* 3. Act IV Masterclass Interactive Glassmorphic IDE Tutorial */}
      <TutorialWidget />

      {/* 4. Heavy All-Caps Kinetic Serif Typography */}
      <KineticTypography />

      {/* 5. Institutional Micro-HUD & Act V Grand Title Card */}
      <HUDOverlay />

      {/* 6. Act Junction Impact Flash */}
      {junctionFlash > 0 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(255, 235, 180, 0.7)",
            mixBlendMode: "color-dodge",
            pointerEvents: "none",
            zIndex: 90,
          }}
        />
      )}

      {/* 7. Dead Silence Drop Vacuum (Frame 4860 - 4920) */}
      {isSilenceBlackout && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "#000000",
            pointerEvents: "none",
            zIndex: 95,
          }}
        />
      )}

      {/* 8. Cinematic 70mm Matte Letterboxing */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: `${letterboxHeight}px`,
          backgroundColor: "#000000",
          zIndex: 100,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          width: "100%",
          height: `${letterboxHeight}px`,
          backgroundColor: "#000000",
          zIndex: 100,
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
