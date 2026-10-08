import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";

export const VFXBackground: React.FC = () => {
  const frame = useCurrentFrame();

  // 1. Act I Camera Physics (Frames 0 - 1080 | 0s - 18s)
  // Slow ominous push-in into molten clockwork gears
  const act1Scale = interpolate(frame, [0, 1080], [1.02, 1.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act1PanY = interpolate(frame, [0, 1080], [0, -35], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act1Opacity = interpolate(
    frame,
    [0, 60, 1020, 1080],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 2. Act II & III Camera Physics (Frames 1080 - 3600 | 18s - 60s)
  // Deep orbital drift across spinning golden particle sphere in void
  const act2Scale = interpolate(frame, [1080, 3600], [1.02, 1.28], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act2PanX = interpolate(frame, [1080, 3600], [-25, 25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act2PanY = interpolate(frame, [1080, 3600], [15, -20], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act2Opacity = interpolate(
    frame,
    [1060, 1120, 3540, 3600],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 3. Act IV & V Camera Physics (Frames 3600 - 5400 | 60s - 90s)
  // Macro rack focus onto dark developer desk and high-end terminal
  const act4Scale = interpolate(frame, [3600, 5400], [1.04, 1.18], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act4PanY = interpolate(frame, [3600, 5400], [-10, 20], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act4Opacity = interpolate(
    frame,
    [3580, 3640, 5340, 5400],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Nolan Chiaroscuro Lighting Pulse (Clock tick pulse every 30 frames)
  const pulsePhase = (frame % 30) / 30;
  const tickLightIntensity = Math.sin(pulsePhase * Math.PI) * 0.12;

  // Braam impact flash at act boundaries (1080, 2160, 3600)
  const isBraam1 = frame >= 1075 && frame <= 1110;
  const isBraam2 = frame >= 2155 && frame <= 2190;
  const isBraam3 = frame >= 3595 && frame <= 3630;
  const braamImpact = isBraam1 || isBraam2 || isBraam3 ? 0.35 : 0.0;

  // Film grain flicker
  const grainSeed = (frame * 17) % 100;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "1080px",
        height: "1920px",
        backgroundColor: "#050608",
        overflow: "hidden",
      }}
    >
      {/* ========================================================================= */}
      {/* ACT I: Clockwork Melting Gears (0 - 1080)                                  */}
      {/* Prompt: "Extreme close-up of a ticking mechanical clockwork gears melting   */}
      {/* into molten liquid gold, intense shadows, smoke, Christopher Nolan color    */}
      {/* grading, 8k, cinematic lighting."                                         */}
      {/* ========================================================================= */}
      {frame < 1140 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: act1Opacity,
            transform: `scale(${act1Scale}) translateY(${act1PanY}px)`,
            transformOrigin: "center 45%",
            filter: `contrast(1.22) brightness(${0.92 + tickLightIntensity}) saturate(1.15)`,
          }}
        >
          <Img
            src={staticFile("assets/act1_melting_clockwork.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}

      {/* ========================================================================= */}
      {/* ACT II & III: Golden Sphere in Dark Void (1080 - 3600)                    */}
      {/* Prompt: "A vast black room with a glowing, massive 3D golden sphere         */}
      {/* composed of complex particle lines spinning, sending waves of algorithmic  */}
      {/* code outward into a dark void, photorealistic, ray-traced."               */}
      {/* ========================================================================= */}
      {frame >= 1050 && frame < 3660 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: act2Opacity,
            transform: `scale(${act2Scale}) translate(${act2PanX}px, ${act2PanY}px)`,
            transformOrigin: "center center",
            filter: `contrast(1.28) brightness(${0.9 + tickLightIntensity}) saturate(1.2)`,
          }}
        >
          <Img
            src={staticFile("assets/act2_golden_sphere.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}

      {/* ========================================================================= */}
      {/* ACT IV & V: Macro Designer Terminal Desk (3600 - 5400)                     */}
      {/* Prompt: "A moody, hyper-realistic designer desk setup at night, macro lens  */}
      {/* focusing on a premium high-end monitor displaying a black terminal window  */}
      {/* executing lightning-fast script text lines."                              */}
      {/* ========================================================================= */}
      {frame >= 3550 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: act4Opacity,
            transform: `scale(${act4Scale}) translateY(${act4PanY}px)`,
            transformOrigin: "center 50%",
            filter: `contrast(1.18) brightness(${0.88 + tickLightIntensity}) saturate(1.12)`,
          }}
        >
          <Img
            src={staticFile("assets/act4_terminal_desk.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}

      {/* Anamorphic Blue & Gold Lens Flare Streaks */}
      <div
        style={{
          position: "absolute",
          top: "38%",
          left: 0,
          width: "100%",
          height: "2px",
          background:
            "linear-gradient(90deg, transparent 0%, rgba(0, 210, 255, 0.45) 45%, rgba(240, 199, 94, 0.6) 50%, rgba(0, 210, 255, 0.45) 55%, transparent 100%)",
          filter: "blur(2px)",
          opacity: 0.35 + tickLightIntensity * 2,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "62%",
          left: 0,
          width: "100%",
          height: "1px",
          background:
            "linear-gradient(90deg, transparent 0%, rgba(240, 199, 94, 0.3) 50%, transparent 100%)",
          filter: "blur(3px)",
          opacity: 0.25,
          pointerEvents: "none",
        }}
      />

      {/* Braam Impact Flash */}
      {braamImpact > 0 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(240, 199, 94, 0.25)",
            mixBlendMode: "color-dodge",
            pointerEvents: "none",
          }}
        />
      )}

      {/* Nolan Chiaroscuro Heavy Vignette Overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 50%, rgba(0,0,0,0.05) 30%, rgba(0,0,0,0.6) 75%, rgba(2,3,5,0.95) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Subtle 35mm Analog Film Grain Layer */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          opacity: 0.07,
          mixBlendMode: "overlay",
          backgroundImage: `radial-gradient(circle at ${grainSeed}% ${grainSeed}%, #fff 1px, transparent 1px)`,
          backgroundSize: "3px 3px",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
