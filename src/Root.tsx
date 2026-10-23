import React from "react";
import { Composition } from "remotion";
import { MasterComposition } from "./Composition";
import { DonAureliusCreatorReel } from "./components/modern_motion/DonAureliusCreatorReel";
import { DonAureliusMegaReel90s } from "./components/long_form_motion/DonAureliusMegaReel90s";
import { TutorialVideoComposition } from "../marketing/video_composition";

export const Root: React.FC = () => {
  return (
    <>
      {/* 60-Second Installation Tutorial Masterclass (1800 frames @ 30 FPS = 60.00s) */}
      <Composition
        id="DonAureliusTutorial60s"
        component={TutorialVideoComposition}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />

      {/* 90-Second Ultra-High-Energy Crazy Motion Reel (2700 frames @ 30 FPS = 90.00s) */}
      <Composition
        id="DonAureliusMegaReel90s"
        component={DonAureliusMegaReel90s}
        durationInFrames={2700}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
      />

      {/* 10-Second Snappy Creator Reel */}
      <Composition
        id="DonAureliusCreatorReel"
        component={DonAureliusCreatorReel}
        durationInFrames={298}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
      />

      {/* Christopher Nolan Trailer Composition */}
      <Composition
        id="DonAureliusNolanTrailer"
        component={MasterComposition}
        durationInFrames={5400}
        fps={60}
        width={1080}
        height={1920}
        defaultProps={{}}
      />
    </>
  );
};
