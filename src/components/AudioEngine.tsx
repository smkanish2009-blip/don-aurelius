import React from "react";
import { Audio, Sequence, staticFile, interpolate, useCurrentFrame } from "remotion";

export const AudioEngine: React.FC = () => {
  const frame = useCurrentFrame();

  // Volume calculation with hard silence gate at frame 4860 (81.0s)
  const masterVolume = (f: number) => {
    // DEAD SILENCE drop between 4860 and 4920 (81s - 82s)
    if (f >= 4860 && f < 4920) {
      return 0.0;
    }
    // Act V sovereign resolution (82s - 90s)
    if (f >= 4920) {
      return interpolate(f, [4920, 5000, 5320, 5400], [0.2, 0.75, 0.75, 0.0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }
    // Acts I - IV progressive build
    return interpolate(f, [0, 120, 3600, 4800, 4860], [0.25, 0.65, 0.8, 1.0, 0.0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  };

  const tickingVolume = (f: number) => {
    if (f >= 4860) return 0.0;
    return interpolate(f, [0, 60, 3600, 4800, 4860], [0.2, 0.45, 0.55, 0.8, 0.0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  };

  return (
    <>
      {/* 1. Master Nolan Orchestral Score */}
      <Audio
        src={staticFile("audio/nolan_master_score_90s.wav")}
        volume={masterVolume}
      />

      {/* 2. Synchronized Ticking Clock Layer (Cuts to dead silence at 4860) */}
      <Sequence from={0} durationInFrames={4860}>
        <Audio
          src={staticFile("audio/ticking_clock_90s.wav")}
          volume={tickingVolume}
        />
      </Sequence>

      {/* 3. Act I Transition Sub-Bass Braam (Frames 1050 - 1320) */}
      <Sequence from={1050} durationInFrames={270}>
        <Audio
          src={staticFile("audio/nolan_braam.wav")}
          volume={(f) =>
            interpolate(f, [0, 20, 200, 270], [0.7, 0.9, 0.7, 0.0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>

      {/* 4. Act II Transition Sub-Bass Braam (Frames 2130 - 2400) */}
      <Sequence from={2130} durationInFrames={270}>
        <Audio
          src={staticFile("audio/nolan_braam.wav")}
          volume={(f) =>
            interpolate(f, [0, 20, 200, 270], [0.75, 0.95, 0.7, 0.0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>

      {/* 5. Act III Transition Sub-Bass Braam (Frames 3570 - 3840) */}
      <Sequence from={3570} durationInFrames={270}>
        <Audio
          src={staticFile("audio/nolan_braam.wav")}
          volume={(f) =>
            interpolate(f, [0, 20, 200, 270], [0.8, 1.0, 0.75, 0.0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>

      {/* 6. Act IV Escalating Orchestral Rise (Frames 3600 - 4860) */}
      <Sequence from={3600} durationInFrames={1260}>
        <Audio
          src={staticFile("audio/orchestral_rise.wav")}
          volume={(f) =>
            interpolate(f, [0, 400, 1000, 1250, 1260], [0.15, 0.45, 0.85, 1.0, 0.0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>
    </>
  );
};
