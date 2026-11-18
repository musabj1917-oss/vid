import React from 'react';
import { Composition } from 'remotion';
import { MainVideo } from './MainVideo';
import { Inspired3D } from './3d/Inspired3D';
import { FPS, TOTAL_FRAMES, SHOT_MIDS } from './3d/shots';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id='MainVideo'
        component={MainVideo}
        durationInFrames={1745} // 29.088s at 60 FPS matching audio.mp3
        fps={60}
        width={1080}
        height={1920}
        defaultProps={{}}
      />
      <Composition
        id='Inspired3D'
        component={Inspired3D}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ audio: null as string | null, mids: SHOT_MIDS }}
      />
    </>
  );
};
