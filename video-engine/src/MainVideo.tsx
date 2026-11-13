import React from 'react';
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Audio,
  staticFile,
} from 'remotion';

export interface Scene {
  id: number;
  tag: string;
  text: string;
  visual_type: string;
  hud_callout?: string;
  metric_val?: string;
  duration?: number;
}

export interface VideoData {
  title?: string;
  hook?: string;
  narration?: string;
  scenes?: Scene[];
  caption?: string;
}

const DEFAULT_SCENES: Scene[] = [
  { id: 1, tag: "HOOK // LEAK", text: "Your website isn't broken,", visual_type: "shock_leak_hook", hud_callout: "ALERT: MONEY LEAK DETECTED", duration: 2.1 },
  { id: 2, tag: "BOUNCE // 68%", text: "it's silently bleeding your highest-paying clients", visual_type: "hero_bounce_gauge", hud_callout: "BOUNCE RATE: 68%", metric_val: "68%", duration: 2.7 },
  { id: 3, tag: "JUNCTION // LOSS", text: "before they ever reach out.", visual_type: "pipeline_junction_loss", hud_callout: "LOST PIPELINE: $45K/MO", duration: 2.0 },
  { id: 4, tag: "STEP 01 // 3.8s", text: "Step one: kill the three-second load lag", visual_type: "hero_load_lag", hud_callout: "STEP 01: LOAD LAG 3.8s", metric_val: "3.8s", duration: 3.0 },
  { id: 5, tag: "PURGE BLOAT", text: "and heavy bloated scripts that destroy first impressions on mobile.", visual_type: "exploded_stack_laser", hud_callout: "4.8MB UNUSED JS PURGED", duration: 3.7 },
  { id: 6, tag: "STEP 02 // CLARITY", text: "Step two: replace vague corporate jargon", visual_type: "clarity_filter", hud_callout: "STEP 02: 5-SEC CLARITY", duration: 2.0 },
  { id: 7, tag: "PROOF // 99/100", text: "with an instant value proposition", visual_type: "pagespeed_proof_beat", hud_callout: "GOOGLE PAGESPEED: 99/100", duration: 2.7 },
  { id: 8, tag: "VALUE SLAB", text: "above the fold in under five words.", visual_type: "gold_value_monolith", hud_callout: "CORE OFFER // < 5 WORDS", duration: 2.8 },
  { id: 9, tag: "STEP 03 // 1-TAP", text: "Step three: embed a direct one-tap booking flow.", visual_type: "direct_booking_conduit", hud_callout: "STEP 03: 1-TAP INBOUND", duration: 2.5 },
  { id: 10, tag: "TURBO // 0.8s", text: "Fix these three bottlenecks today", visual_type: "hero_speed_countdown", hud_callout: "SPEED: 3.8s -> 0.8s", metric_val: "0.8s", duration: 2.7 },
  { id: 11, tag: "CTA // @mwd1504", text: "to double your qualified inbound leads.", visual_type: "cta_reveal_slab", hud_callout: "BOOK A CALL // @mwd1504", duration: 2.888 }
];

export const MainVideo: React.FC<{ data?: VideoData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  const scenes: Scene[] = (data?.scenes && data.scenes.length > 0) ? data.scenes : DEFAULT_SCENES;
  const totalEst = scenes.reduce((acc, s) => acc + (s.duration || 2.5), 0);

  let accumulatedFrames = 0;
  const sceneTimeline = scenes.map((s) => {
    const durRatio = (s.duration || 2.5) / totalEst;
    const sceneFrames = Math.round(durRatio * durationInFrames);
    const start = accumulatedFrames;
    const end = start + sceneFrames;
    accumulatedFrames = end;
    return { ...s, start, end, sceneFrames };
  });

  if (sceneTimeline.length > 0) {
    sceneTimeline[sceneTimeline.length - 1].end = durationInFrames;
    sceneTimeline[sceneTimeline.length - 1].sceneFrames =
      durationInFrames - sceneTimeline[sceneTimeline.length - 1].start;
  }

  const activeIndex = sceneTimeline.findIndex(
    (s) => frame >= s.start && frame < s.end
  );
  const currentSceneIndex = activeIndex === -1 ? sceneTimeline.length - 1 : activeIndex;
  const currentScene = sceneTimeline[currentSceneIndex];
  const sceneFrame = frame - currentScene.start;
  const sceneProgress = Math.min(1.0, Math.max(0.0, sceneFrame / (currentScene.sceneFrames || 1)));

  // Continuous Camera Movement (Orbit Yaw, Pitch, Push-in, Pull-back)
  const isCta = currentScene.visual_type === 'cta_reveal_slab';
  const camZoom = isCta
    ? interpolate(sceneProgress, [0, 1], [1.25, 0.95])
    : interpolate(sceneProgress, [0, 1], [1.05, 1.22]);

  const camOrbit = interpolate(sceneProgress, [0, 1], [-6, 6]);
  const progressRatio = frame / durationInFrames;

  // Split words for 3-5 word caption display
  const words = currentScene.text.split(' ');
  const activeWordIdx = Math.floor(sceneProgress * words.length);

  return (
    <div
      style={{
        width,
        height,
        backgroundColor: '#0A0C12',
        color: '#FFFFFF',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <Audio src={staticFile('audio.mp3')} />

      {/* 3D Isometric Perspective Space with Continuous Camera Movement */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${camZoom}) rotate(${camOrbit}deg)`,
          transformOrigin: '540px 960px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Cyber Floor Grid with Radial Warm Vignette */}
        <div
          style={{
            position: 'absolute',
            width: '2000px',
            height: '2000px',
            backgroundImage:
              'linear-gradient(to right, rgba(0, 242, 254, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 242, 254, 0.08) 1px, transparent 1px)',
            backgroundSize: '80px 80px',
            transform: 'rotateX(60deg) rotateZ(45deg)',
          }}
        />

        {/* Lit 3D Conversion Pipeline Geometry / Visual Centers */}
        {currentScene.visual_type === 'shock_leak_hook' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(20deg) rotateY(-15deg)' }}>
            <div
              style={{
                width: 440,
                height: 280,
                background: 'linear-gradient(135deg, rgba(32, 42, 64, 0.95), rgba(14, 18, 30, 0.95))',
                border: '3px solid #00F2FE',
                borderRadius: 24,
                boxShadow: '0 30px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 242, 254, 0.25)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                position: 'relative',
              }}
            >
              <div style={{ color: '#FF2D55', fontSize: 26, fontWeight: 'bold', letterSpacing: 2 }}>
                ⚠️ ALERT: MONEY LEAK DETECTED
              </div>
              <div style={{ color: '#FFB020', fontSize: 18, marginTop: 12, letterSpacing: 1 }}>
                CONVERSION PIPELINE COMPROMISED
              </div>
            </div>
          </div>
        )}

        {currentScene.visual_type === 'hero_bounce_gauge' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(15deg) rotateY(-10deg)' }}>
            <div
              style={{
                width: 520,
                height: 320,
                background: 'linear-gradient(135deg, rgba(40, 16, 26, 0.95), rgba(18, 12, 20, 0.95))',
                border: '3px solid #FF2D55',
                borderRadius: 28,
                boxShadow: '0 35px 70px rgba(0, 0, 0, 0.8), 0 0 50px rgba(255, 45, 85, 0.3)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <div style={{ fontSize: 110, fontWeight: 900, color: '#FF2D55', lineHeight: 1 }}>
                68%
              </div>
              <div style={{ color: '#FFB020', fontSize: 24, fontWeight: 'bold', marginTop: 14 }}>
                BOUNCE RATE DETECTED
              </div>
              <div style={{ color: '#94A3B8', fontSize: 18, marginTop: 8 }}>
                LOST INBOUND: $45K/MO
              </div>
            </div>
          </div>
        )}

        {currentScene.visual_type === 'hero_load_lag' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(20deg) rotateY(-15deg)' }}>
            <div
              style={{
                width: 520,
                height: 320,
                background: 'linear-gradient(135deg, rgba(50, 18, 22, 0.95), rgba(20, 12, 16, 0.95))',
                border: '3px solid #FFB020',
                borderRadius: 28,
                boxShadow: '0 35px 70px rgba(0, 0, 0, 0.8), 0 0 50px rgba(255, 176, 32, 0.3)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <div style={{ fontSize: 110, fontWeight: 900, color: '#FF2D55', lineHeight: 1 }}>
                3.8s
              </div>
              <div style={{ color: '#FFB020', fontSize: 24, fontWeight: 'bold', marginTop: 14 }}>
                MOBILE LOAD LAG
              </div>
              <div style={{ color: '#FFFFFF', fontSize: 18, marginTop: 8 }}>
                STEP 01: KILL CODE BLOAT
              </div>
            </div>
          </div>
        )}

        {currentScene.visual_type === 'pagespeed_proof_beat' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(15deg) rotateY(-5deg)' }}>
            <div
              style={{
                width: 600,
                height: 380,
                background: 'linear-gradient(135deg, rgba(16, 24, 38, 0.95), rgba(10, 16, 28, 0.95))',
                border: '3px solid #10B981',
                borderRadius: 28,
                boxShadow: '0 40px 80px rgba(0, 0, 0, 0.8), 0 0 50px rgba(16, 185, 129, 0.3)',
                padding: 36,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#4285F4' }} />
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#EA4335' }} />
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#FBBC05' }} />
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#34A853' }} />
                <div style={{ fontSize: 22, fontWeight: 'bold', letterSpacing: 1 }}>
                  GOOGLE PAGESPEED INSIGHTS
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 24 }}>
                <div style={{ fontSize: 88, fontWeight: 900, color: '#10B981' }}>99</div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ color: '#10B981', fontWeight: 'bold', fontSize: 20 }}>
                    CORE WEB VITALS: PASSED
                  </div>
                  <div style={{ color: '#94A3B8', fontSize: 16 }}>LCP: 0.8s // CLS: 0.00</div>
                </div>
              </div>
              <div style={{ background: 'rgba(255, 176, 32, 0.1)', border: '1px solid #FFB020', padding: 12, borderRadius: 10, fontSize: 16, color: '#FFB020' }}>
                “53% of mobile visits abandoned if pages take &gt;3s” — Think With Google
              </div>
            </div>
          </div>
        )}

        {currentScene.visual_type === 'hero_speed_countdown' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(15deg) rotateY(-8deg)' }}>
            <div
              style={{
                width: 580,
                height: 320,
                background: 'linear-gradient(135deg, rgba(14, 40, 32, 0.95), rgba(10, 24, 20, 0.95))',
                border: '3px solid #10B981',
                borderRadius: 28,
                boxShadow: '0 35px 70px rgba(0, 0, 0, 0.8), 0 0 50px rgba(16, 185, 129, 0.35)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <div style={{ fontSize: 96, fontWeight: 900, color: '#10B981', lineHeight: 1 }}>
                0.8s
              </div>
              <div style={{ color: '#FFD700', fontSize: 26, fontWeight: 'bold', marginTop: 14 }}>
                TURBO VELOCITY // +120% LEADS
              </div>
              <div style={{ color: '#FFFFFF', fontSize: 18, marginTop: 8 }}>
                ALL LEAKS PERMANENTLY SEALED
              </div>
            </div>
          </div>
        )}

        {currentScene.visual_type === 'cta_reveal_slab' && (
          <div style={{ textAlign: 'center', transform: 'rotateX(15deg) rotateY(-5deg)' }}>
            <div
              style={{
                width: 620,
                height: 340,
                background: 'linear-gradient(135deg, rgba(18, 24, 44, 0.95), rgba(12, 16, 30, 0.95))',
                border: '3px solid #FFD700',
                borderRadius: 32,
                boxShadow: '0 40px 80px rgba(0, 0, 0, 0.8), 0 0 50px rgba(255, 215, 0, 0.3)',
                padding: 40,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  background: '#10B981',
                  color: '#0A0C12',
                  fontSize: 44,
                  fontWeight: 900,
                  padding: '16px 48px',
                  borderRadius: 20,
                  border: '2px solid #FFD700',
                }}
              >
                BOOK A CALL
              </div>
              <div style={{ color: '#00F2FE', fontSize: 32, fontWeight: 'bold', marginTop: 24 }}>
                @mwd1504 <span style={{ color: '#10B981' }}>✓</span>
              </div>
              <div style={{ color: '#94A3B8', fontSize: 18, marginTop: 8 }}>
                Fix Your Website Pipeline // Double Inbound Leads
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Top Dynamic HUD Tabs (Changes with every scene) */}
      <div
        style={{
          position: 'absolute',
          top: 110,
          left: 60,
          right: 60,
          height: 85,
          background: 'rgba(13, 17, 28, 0.92)',
          border: '2px solid rgba(0, 242, 254, 0.3)',
          borderRadius: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 28px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#00F2FE' }} />
          <div style={{ fontSize: 20, fontWeight: 'bold', letterSpacing: 1.5, color: '#F1F5F9' }}>
            PIPELINE OS // {currentScene.tag}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {scenes.map((s, idx) => (
            <div
              key={s.id}
              style={{
                width: 26,
                height: 24,
                borderRadius: 4,
                background: idx === currentSceneIndex ? '#00F2FE' : 'rgba(30, 41, 59, 0.6)',
                border: idx === currentSceneIndex ? '1px solid #00F2FE' : '1px solid rgba(71, 85, 105, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 13,
                fontWeight: 'bold',
                color: idx === currentSceneIndex ? '#0A0C12' : '#94A3B8',
              }}
            >
              {idx + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Big Safe-Zone Captions (3-5 words at a time, bottom-center, spoken word highlighted, NO box) */}
      <div
        style={{
          position: 'absolute',
          bottom: 220,
          left: 60,
          right: 60,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 16,
          flexWrap: 'wrap',
          textAlign: 'center',
        }}
      >
        {words.map((w, wIdx) => {
          const isCurrent = wIdx === activeWordIdx;
          return (
            <span
              key={wIdx}
              style={{
                fontSize: 48,
                fontWeight: 800,
                color: isCurrent ? '#FFD700' : '#FFFFFF',
                textShadow: isCurrent
                  ? '0 0 20px rgba(255, 215, 0, 0.8), 2px 2px 4px rgba(0, 0, 0, 0.9)'
                  : '2px 2px 6px rgba(0, 0, 0, 0.9)',
                borderBottom: isCurrent ? '4px solid #FFB020' : 'none',
                paddingBottom: 4,
              }}
            >
              {w}
            </span>
          );
        })}
      </div>

      {/* Bottom Continuous Progress Bar */}
      <div
        style={{
          position: 'absolute',
          bottom: 130,
          left: 80,
          right: 80,
          height: 8,
          background: 'rgba(30, 41, 59, 0.6)',
          borderRadius: 4,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${progressRatio * 100}%`,
            background: '#00F2FE',
            borderRadius: 4,
          }}
        />
      </div>
    </div>
  );
};
