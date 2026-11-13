import React from 'react';
import { Composition } from 'remotion';
import { MainVideo } from './MainVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MainVideo"
      component={MainVideo}
      durationInFrames={1745} // 29.088s at 60 FPS matching audio.mp3
      fps={60}
      width={1080}
      height={1920}
      defaultProps={{}}
    />
  );
};
