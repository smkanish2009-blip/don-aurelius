import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { Act1ChaosRetail } from "./Act1ChaosRetail";
import { Act2ApexReveal } from "./Act2ApexReveal";
import { Act3QuantTech } from "./Act3QuantTech";
import { Act4RiskMatrix } from "./Act4RiskMatrix";
import { Act5TerminalTelemetry } from "./Act5TerminalTelemetry";
import { Act6ViralOutro } from "./Act6ViralOutro";

export const DonAureliusMegaReel90s: React.FC = () => {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#07080D",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* 90-Second Continuous Modern Motion Soundtrack */}
      <Audio src={staticFile("audio/reel_soundtrack_90s.mp3")} volume={1.0} />

      {/* ACT 1: The Hook & Brutal Reality of Retail Trading (Frames 0 - 450 | 0s - 15s) */}
      <Sequence from={0} durationInFrames={450}>
        <Act1ChaosRetail />
      </Sequence>

      {/* ACT 2: The Apex Reveal – Don Aurelius Sovereign Core (Frames 445 - 905 | 14.8s - 30.1s) */}
      <Sequence from={445} durationInFrames={460}>
        <Act2ApexReveal />
      </Sequence>

      {/* ACT 3: Crazy Quant Tech & Live Order Flow Heatmap (Frames 900 - 1445 | 30.0s - 48.1s) */}
      <Sequence from={900} durationInFrames={545}>
        <Act3QuantTech />
      </Sequence>

      {/* ACT 4: Monte Carlo 10,000 Vectors & Capital Defense Shield (Frames 1440 - 1955 | 48.0s - 65.1s) */}
      <Sequence from={1440} durationInFrames={515}>
        <Act4RiskMatrix />
      </Sequence>

      {/* ACT 5: Live Verified Telemetry & 1-Click Terminal Deployment (Frames 1950 - 2465 | 65.0s - 82.1s) */}
      <Sequence from={1950} durationInFrames={515}>
        <Act5TerminalTelemetry />
      </Sequence>

      {/* ACT 6: Scarcity Call-To-Action & Viral Outro (Frames 2460 - 2700 | 82.0s - 90.0s) */}
      <Sequence from={2460} durationInFrames={240}>
        <Act6ViralOutro />
      </Sequence>
    </div>
  );
};
