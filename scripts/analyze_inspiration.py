#!/usr/bin/env python3
"""
scripts/analyze_inspiration.py - Measure an inspiration/sample video.

Usage:
    python3 scripts/analyze_inspiration.py [path/to/video.mp4]

If no path is given, it looks for the first video file in inspiration/.
Outputs:
    inspiration/analysis/report.md   - human-readable spec sheet
    inspiration/analysis/report.json - machine-readable measurements

Requires ffmpeg/ffprobe for full analysis. Without them it still
reports file info and prints a manual checklist.
"""

import json
import math
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTAKE = ROOT / "inspiration"
OUT = INTAKE / "analysis"
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def find_video(arg=None):
    if arg:
        p = Path(arg)
        if p.exists():
            return p
        print(f"[warn] {p} not found, falling back to inspiration/ folder")
    if INTAKE.exists():
        for ext in (".mp4", ".mov", ".webm", ".mkv"):
            hits = sorted(INTAKE.glob(f"*{ext}"))
            if hits:
                return hits[0]
    return None


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return r


def probe(video: Path):
    info = {"file": str(video), "size_mb": round(video.stat().st_size / 1e6, 2)}
    if not shutil.which("ffprobe"):
        info["ffprobe"] = "not installed"
        return info
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "stream=width,height,codec_type,codec_name,r_frame_rate,avg_frame_rate,duration,sample_rate,channels",
             "-show_entries", "format=duration,bit_rate",
             "-of", "json", str(video)])
    if r.returncode != 0:
        info["ffprobe_error"] = r.stderr.strip()[:500]
        return info
    data = json.loads(r.stdout)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    info.update({
        "width": v.get("width"), "height": v.get("height"),
        "video_codec": v.get("codec_name"),
        "fps_raw": v.get("avg_frame_rate") or v.get("r_frame_rate"),
        "duration_s": round(float(data.get("format", {}).get("duration", 0)), 2),
        "audio_codec": a.get("codec_name"),
        "audio_sample_rate": a.get("sample_rate"),
        "audio_channels": a.get("channels"),
    })
    try:
        num, den = info["fps_raw"].split("/")
        info["fps"] = round(int(num) / int(den), 2)
    except Exception:
        info["fps"] = info["fps_raw"]
    return info


def extract_frames(video: Path, outdir: Path):
    """Extract 1 frame/sec + scene-cut frames via ffmpeg. Returns list of frame paths."""
    frames = []
    if not shutil.which("ffmpeg"):
        return frames
    outdir.mkdir(parents=True, exist_ok=True)
    # 1 frame per second
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", "fps=1",
         str(outdir / "sec_%03d.png")])
    frames += sorted(outdir.glob("sec_*.png"))
    # Scene-cut frames (threshold tuned for hard cuts)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video),
         "-vf", "select='gt(scene,0.35)',showinfo", "-vsync", "vfr",
         str(outdir / "cut_%03d.png")])
    frames += sorted(outdir.glob("cut_*.png"))
    return frames


def palette(frames, n=6):
    """Dominant colours across frames via PIL quantize."""
    try:
        from PIL import Image
    except ImportError:
        return {"note": "Pillow not installed - pip install Pillow"}
    counter = Counter()
    used = 0
    for f in frames:
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((160, 160))
            q = im.quantize(colors=8, method=Image.MEDIANCUT)
            pal = q.getpalette()
            counts = sorted(q.getcolors(), reverse=True)[:4]
            for cnt, idx in counts:
                rgb = tuple(pal[idx * 3: idx * 3 + 3])
                counter[rgb] += cnt
            used += 1
            if used >= 12:
                break
        except Exception:
            continue
    total = sum(counter.values()) or 1
    return [{"hex": "#%02X%02X%02X" % rgb, "pct": round(c / total * 100, 1)}
            for rgb, c in counter.most_common(n)]


def audio_stats(video: Path):
    if not shutil.which("ffmpeg"):
        return {"note": "ffmpeg not installed"}
    r = run(["ffmpeg", "-i", str(video), "-af", "volumedetect",
             "-f", "null", "-"])
    out = r.stderr
    stats = {}
    for line in out.splitlines():
        if "mean_volume" in line:
            stats["mean_volume_db"] = line.split(":")[-1].strip()
        if "max_volume" in line:
            stats["max_volume_db"] = line.split(":")[-1].strip()
    return stats


def main():
    video = find_video(sys.argv[1] if len(sys.argv) > 1 else None)
    OUT.mkdir(parents=True, exist_ok=True)

    if video is None:
        print("No video found in inspiration/. Drop your sample video there first.")
        print("See inspiration/README.md")
        # Still write a checklist so the user knows what to answer manually.
        (OUT / "report.md").write_text(
            "# Inspiration analysis\n\n"
            "No video found yet. Add `inspiration/sample.mp4` and re-run:\n"
            "`python3 scripts/analyze_inspiration.py`\n\n"
            "## Manual checklist (answer these in chat)\n"
            "- [ ] Duration and resolution (e.g. 30s, 1080x1920)\n"
            "- [ ] How many scene cuts, and how long is each scene?\n"
            "- [ ] What is the main object / visual metaphor?\n"
            "- [ ] Caption style: font, size, colour, position, highlight?\n"
            "- [ ] Background colour and accent colour?\n"
            "- [ ] Music / sound effects present? Voiceover or text-only?\n"
            "- [ ] Ending CTA text?\n"
        )
        return

    print(f"Analyzing: {video}")
    info = probe(video)
    frames = extract_frames(video, OUT / "frames")
    info["frames_extracted"] = len(frames)
    info["palette"] = palette(frames)
    info["audio"] = audio_stats(video)

    (OUT / "report.json").write_text(json.dumps(info, indent=2))

    lines = [
        "# Inspiration video spec (measured)",
        "",
        f"- File: `{video.name}` ({info.get('size_mb')} MB)",
        f"- Resolution: {info.get('width')}x{info.get('height')}",
        f"- FPS: {info.get('fps')}",
        f"- Duration: {info.get('duration_s')}s",
        f"- Video codec: {info.get('video_codec')}",
        f"- Audio: {info.get('audio_codec')} "
        f"({info.get('audio_sample_rate')} Hz, {info.get('audio_channels')} ch) "
        f"{info.get('audio', {})}",
        f"- Frames extracted: {info['frames_extracted']} (see `frames/`)",
        "",
        "## Dominant colours",
        "",
    ]
    for c in info.get("palette", []):
        if isinstance(c, dict):
            lines.append(f"- `{c['hex']}` — {c['pct']}%")
        else:
            lines.append(f"- {c}")
    lines += [
        "",
        "## To fill in by watching the video",
        "- [ ] Scene count + cut times (compare with `frames/cut_*.png`)",
        "- [ ] Main object / metaphor per scene",
        "- [ ] Camera moves (orbit / push-in / pull-back / static?)",
        "- [ ] Caption font, size, position, highlight colour",
        "- [ ] Transitions between scenes",
        "- [ ] Music / SFX / voiceover notes",
        "- [ ] CTA text and end-card style",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT / 'report.md'} and {OUT / 'report.json'}")


if __name__ == "__main__":
    main()
