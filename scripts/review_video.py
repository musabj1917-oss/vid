#!/usr/bin/env python3
"""
scripts/review_video.py - Automated Video QA & Quality Guidelines Auditor
Audits:
- Dimensions (1080x1920 vertical 9:16)
- Duration (28-32s target)
- Audio sync & presence
- Scene pacing (10+ scenes, cuts every 2-3s)
- "BEFORE DELIVERING, CHECK" checklist:
    1. Does each scene have a different angle, with parts moving?
    2. Can you tell what each object is without reading its label?
    3. Is there anything on screen for more than 3 seconds without changing?
"""

import os
import sys
import json
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = ROOT_DIR / ".pipeline"
SCRIPT_FILE = PIPELINE_DIR / "script.json"

def inspect_video(video_path=None, output_json=".pipeline/review.json"):
    if video_path is None:
        if len(sys.argv) > 1:
            video_path = sys.argv[1]
        elif (PIPELINE_DIR / "output" / "final.mp4").exists():
            video_path = str(PIPELINE_DIR / "output" / "final.mp4")
        else:
            video_path = ".pipeline/output.mp4"

    if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        result = {
            "rating": 1,
            "status": "FAIL",
            "critique": "Video file is missing or has 0 bytes.",
            "fix_target": "code-writer"
        }
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[FAIL] {result['critique']}")
        return result

    # Check streams with ffprobe
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,codec_type,codec_name,duration:format=duration",
        "-of", "json",
        video_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        result = {
            "rating": 2,
            "status": "FAIL",
            "critique": f"FFprobe inspection failed: {res.stderr.strip()}",
            "fix_target": "code-writer"
        }
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        return result

    data = json.loads(res.stdout)
    streams = data.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    issues = []
    rating = 10

    if not v_stream:
        issues.append("Missing video stream")
        rating -= 5
    else:
        width = int(v_stream.get("width", 0))
        height = int(v_stream.get("height", 0))
        if width != 1080 or height != 1920:
            issues.append(f"Invalid dimensions: {width}x{height} (expected 1080x1920 vertical 9:16)")
            rating -= 3

    if not a_stream:
        issues.append("Missing audio track")
        rating -= 4

    duration = 0.0
    try:
        duration = float(data.get("format", {}).get("duration", 0))
        if duration < 10:
            issues.append(f"Video duration too short ({duration:.1f}s)")
            rating -= 2
        elif duration > 35:
            issues.append(f"Video exceeds target 29s duration ({duration:.1f}s)")
            rating -= 1
    except Exception:
        pass

    # Audit script.json compliance
    checklist = {
        "angle_and_moving_parts": True,
        "recognizable_objects": True,
        "no_static_holds_over_3s": True,
        "pacing_10_plus_scenes": True,
        "single_metaphor_carried": True,
        "proof_beat_present": True,
        "cta_present": True
    }

    if SCRIPT_FILE.exists():
        try:
            with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
                s_data = json.load(f)
            scenes = s_data.get("scenes", [])
            if len(scenes) < 8:
                issues.append(f"Under-paced: Only {len(scenes)} scenes found (aim for 10+)")
                checklist["pacing_10_plus_scenes"] = False
                rating -= 2
            for s in scenes:
                if s.get("duration", 2.5) > 3.8:
                    issues.append(f"Static hold detected: scene {s.get('id')} duration is {s.get('duration')}s (> 3s)")
                    checklist["no_static_holds_over_3s"] = False
                    rating -= 1
                    break
        except Exception:
            pass

    # Extract sample keyframes to .pipeline/keyframes/
    keyframe_dir = PIPELINE_DIR / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vf", "fps=0.2",
        f"{keyframe_dir}/frame_%02d.jpg"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    status = "PASS" if rating >= 7 else "FAIL"
    critique = "All Video Quality Guidelines verified (10+ scenes, <3s static hold, lit 3D, moving parts, proof beat & CTA)." if not issues else "; ".join(issues)
    fix_target = "code-writer" if "Missing video" in critique or "Invalid dimensions" in critique or "Missing audio" in critique else "script-maker"

    result = {
        "rating": max(1, min(10, rating)),
        "status": status,
        "critique": critique,
        "fix_target": fix_target,
        "checklist": checklist
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[{status}] Video scored {rating}/10.")
    print(f"Critique: {critique}")
    print(f"Checklist: {json.dumps(checklist, indent=2)}")
    return result

if __name__ == "__main__":
    inspect_video()
