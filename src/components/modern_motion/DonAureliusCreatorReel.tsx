import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { Scene1Hook } from "./Scene1Hook";
import { Scene2BentoCards } from "./Scene2BentoCards";
import { Scene3AvatarCenterpiece } from "./Scene3AvatarCenterpiece";
import { Scene4FewSpotsLeft } from "./Scene4FewSpotsLeft";
import { Scene5Outro } from "./Scene5Outro";

export const DonAureliusCreatorReel: React.FC = () => {
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
      {/* 100% Synchronized Reference Audio Soundtrack */}
      <Audio src={staticFile("audio/reel_soundtrack.mp3")} volume={1.0} />

      {/* Scene 1: Glitch Pixels & Kinetic Text "hey do you need" (Frames 0 - 66 | 0s - 2.2s) */}
      <Sequence from={0} durationInFrames={66}>
        <Scene1Hook />
      </Sequence>

      {/* Scene 2: Floating Bento Squircle Cards & "better trades" (Frames 64 - 144 | 2.13s - 4.8s) */}
      <Sequence from={64} durationInFrames={82}>
        <Scene2BentoCards />
      </Sequence>

      {/* Scene 3: Vertical 3D Purple Ribbon, 3D Trader Avatar, Orbiting Badges & "Deploy AURELIUS" (Frames 142 - 224 | 4.73s - 7.47s) */}
      <Sequence from={142} durationInFrames={82}>
        <Scene3AvatarCenterpiece />
      </Sequence>

      {/* Scene 4: Soft Radiating Rays, "few spots left..." Button & Click (Frames 220 - 264 | 7.33s - 8.8s) */}
      <Sequence from={220} durationInFrames={46}>
        <Scene4FewSpotsLeft />
      </Sequence>

      {/* Scene 5: Studio White Outro "see you in my 💬" (Frames 260 - 298 | 8.67s - 9.93s) */}
      <Sequence from={260} durationInFrames={38}>
        <Scene5Outro />
      </Sequence>
    </div>
  );
};
