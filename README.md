# VidAgents: Autonomous Vertical Video Engine

An autonomous, multi-agent short-form video creation and publishing pipeline optimized for Termux/Linux environments.

---

## 📖 Video Quality Guidelines (Reusable for Any Topic)

See [`VIDEO_QUALITY_GUIDELINES.md`](VIDEO_QUALITY_GUIDELINES.md) for full specifications.

### 1. Core Rule
**Build the video around ONE visual metaphor that fits the topic.**
Every scene shows that metaphor changing. The visuals directly explain what the voiceover says.

### 2. Objects & Motion
- **Teardown sub-parts**: Real-world recognizable objects broken into labeled components, not generic boxes or flat wireframes.
- **Always moving**: Gears turning, parts sliding apart, particles streaming, gauges sweeping. Nothing sits still.
- **Before / After**: Show the problem state on the object, then visibly show the fix being applied to that same object.
- **Real scale cues**: Tiny stylized characters, hands, or props to establish scale.

### 3. Camera & Pacing
- **Cuts every 2–3 seconds**: 10+ distinct scenes across ~29s.
- **Continuous camera movement**: Constant slow orbits (yaw), elevation tilts (pitch), push-ins on components, and pull-backs on reveals. Never hold static view for >3s.
- **0–2s Hook & Clear CTA**: Shock line/visual in the first 2 seconds; end with punchy CTA (`"Book a call"` / `@mwd1504`).

### 4. Look & Materials
- **Lit 3D geometry**: Depth shading with 3-tone lighting, glassmorphism, glowing conduits, and soft multi-tier contact shadows.
- **Dark background with warm accent**: Obsidian (`#0A0C12`) with amber/gold (`#FFB020`, `#FFD700`) accents alongside cyan and crimson.

### 5. Typography & Numbers
- **Bottom-center captions**: 3–5 words at a time, big typography, active spoken word highlighted in gold. **No paragraph boxes.**
- **Big visual numbers**: Key metrics (`68%`, `3.8s ➔ 0.8s`) displayed as massive animated counters or gauges.

### 6. Proof Beat
- **Real audit proof**: Google PageSpeed 99/100 score badge, Core Web Vitals, or cited statistics (`Think With Google`).

### 7. Pre-Delivery Checklist ("BEFORE DELIVERING, CHECK")
- [x] Does each scene have a different angle, with parts moving?
- [x] Can you tell what each object is without reading its label?
- [x] Is there anything on screen for more than 3 seconds without changing?

---

## 🛠️ CLI Quickstart

```bash
# Render video with the lit 3D isometric engine
python render_engine.py

# Audit video against Video Quality Guidelines
python scripts/review_video.py

# Launch fully autonomous pipeline for a new topic
node runner.js
```
