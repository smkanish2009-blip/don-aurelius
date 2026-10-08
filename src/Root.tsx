import React from "react";
import { Composition } from "remotion";
import { MasterComposition } from "./Composition";

export const Root: React.FC = () => {
  return (
    <>
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
