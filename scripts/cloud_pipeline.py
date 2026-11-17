#!/usr/bin/env python3
"""
scripts/cloud_pipeline.py - Deterministic cloud video pipeline (no AI agent CLI).

Replaces runner.js + `agy` on the cloud. Steps:
  1. Pick next topic (rotation; synced to Supabase if configured)
  2. Write .pipeline/script.json from the 11-scene template
  3. Render with render_engine.py (needs ffmpeg + Pillow + fonts)
  4. Review with scripts/review_video.py
  5. Upload final.mp4 to Supabase Storage (if SUPABASE_* env vars set)
  6. Log the job to Supabase (if configured)

Usage:
  python3 scripts/cloud_pipeline.py [--dry-run] [--topic "Custom topic"]

Env vars (all optional except for Supabase upload):
  SUPABASE_URL, SUPABASE_SERVICE_KEY  - Supabase project + service role key
  SUPABASE_BUCKET                     - storage bucket (default: videos)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / ".pipeline"
OUTPUT = PIPELINE / "output"
SCRIPT_FILE = PIPELINE / "script.json"
REVIEW_FILE = PIPELINE / "review.json"
FINAL_MP4 = OUTPUT / "final.mp4"
AUDIO_FILE = ROOT / "video-engine" / "public" / "audio.mp3"

TOPIC_POOL = [
    "Why your business website is losing you high-paying clients and how to fix it in 3 steps",
    "The 3 silent conversion killers on small business landing pages",
    "Why relying solely on social media pages instead of an official website hurts your brand trust",
    "How page load speed under 2 seconds directly doubles your customer inquiries",
    "How an automated booking and menu system frees up 15 hours a week for local business owners",
]

# 11-scene template matching render_engine.py visual_types + MainVideo.tsx defaults
SCENE_TEMPLATE = [
    {"id": 1, "tag": "HOOK // LEAK", "text": "Your website isn't broken,", "visual_type": "shock_leak_hook", "hud_callout": "ALERT: MONEY LEAK DETECTED", "duration": 2.1},
    {"id": 2, "tag": "BOUNCE // 68%", "text": "it's silently bleeding your highest-paying clients", "visual_type": "hero_bounce_gauge", "hud_callout": "BOUNCE RATE: 68%", "metric_val": "68%", "duration": 2.7},
    {"id": 3, "tag": "JUNCTION // LOSS", "text": "before they ever reach out.", "visual_type": "pipeline_junction_loss", "hud_callout": "LOST PIPELINE: $45K/MO", "duration": 2.0},
    {"id": 4, "tag": "STEP 01 // 3.8s", "text": "Step one: kill the three-second load lag", "visual_type": "hero_load_lag", "hud_callout": "STEP 01: LOAD LAG 3.8s", "metric_val": "3.8s", "duration": 3.0},
    {"id": 5, "tag": "PURGE BLOAT", "text": "and heavy bloated scripts that destroy first impressions on mobile.", "visual_type": "exploded_stack_laser", "hud_callout": "4.8MB UNUSED JS PURGED", "duration": 3.7},
    {"id": 6, "tag": "STEP 02 // CLARITY", "text": "Step two: replace vague corporate jargon", "visual_type": "clarity_filter", "hud_callout": "STEP 02: 5-SEC CLARITY", "duration": 2.0},
    {"id": 7, "tag": "PROOF // 99/100", "text": "with an instant value proposition", "visual_type": "pagespeed_proof_beat", "hud_callout": "GOOGLE PAGESPEED: 99/100", "duration": 2.7},
    {"id": 8, "tag": "VALUE SLAB", "text": "above the fold in under five words.", "visual_type": "gold_value_monolith", "hud_callout": "CORE OFFER // < 5 WORDS", "duration": 2.8},
    {"id": 9, "tag": "STEP 03 // 1-TAP", "text": "Step three: embed a direct one-tap booking flow.", "visual_type": "direct_booking_conduit", "hud_callout": "STEP 03: 1-TAP INBOUND", "duration": 2.5},
    {"id": 10, "tag": "TURBO // 0.8s", "text": "Fix these three bottlenecks today", "visual_type": "hero_speed_countdown", "hud_callout": "SPEED: 3.8s -> 0.8s", "metric_val": "0.8s", "duration": 2.7},
    {"id": 11, "tag": "CTA // @mwd1504", "text": "to double your qualified inbound leads.", "visual_type": "cta_reveal_slab", "hud_callout": "BOOK A CALL // @mwd1504", "duration": 2.888},
]


def log(msg):
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def supabase_configured():
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"))


def supabase_request(method, path, body=None):
    """Minimal Supabase REST call (no SDK needed)."""
    url = os.environ["SUPABASE_URL"].rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("apikey", os.environ["SUPABASE_SERVICE_KEY"])
    req.add_header("Authorization", f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode() or "null")


def get_next_topic(override=None):
    if override:
        return override
    idx = 0
    if supabase_configured():
        try:
            rows = supabase_request("GET", "/rest/v1/topic_state?id=eq.1&select=index")
            if rows:
                idx = int(rows[0].get("index", 0))
            supabase_request("PATCH", "/rest/v1/topic_state?id=eq.1",
                             {"index": idx + 1, "updated_at": datetime.now(timezone.utc).isoformat()})
            log(f"Topic index from Supabase: {idx}")
        except Exception as e:
            log(f"[warn] Supabase topic sync failed ({e}); using local file")
    if not supabase_configured() or True:
        f = PIPELINE / "topic_index.txt"
        if f.exists():
            try:
                idx = int(f.read_text().strip() or 0)
            except ValueError:
                idx = 0
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(str(idx + 1))
    return TOPIC_POOL[idx % len(TOPIC_POOL)]


def write_script(topic):
    PIPELINE.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    script = {
        "title": topic,
        "hook": "Your website isn't broken,",
        "narration": " ".join(s["text"] for s in SCENE_TEMPLATE),
        "caption": "#shorts #business #growth #webdesign",
        "scenes": SCENE_TEMPLATE,
    }
    SCRIPT_FILE.write_text(json.dumps(script, indent=2))
    log(f"Wrote {SCRIPT_FILE} for topic: {topic!r}")


def run(cmd, cwd=ROOT):
    log(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd))
    if r.returncode != 0:
        raise SystemExit(f"Command failed ({r.returncode}): {' '.join(cmd)}")
    return r


def upload_to_supabase():
    if not supabase_configured():
        log("SUPABASE_* not set — skipping cloud upload (video stays as workflow artifact).")
        return None
    bucket = os.environ.get("SUPABASE_BUCKET", "videos")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    object_name = f"final_{ts}.mp4"
    url = f"{os.environ['SUPABASE_URL'].rstrip('/')}/storage/v1/object/{bucket}/{object_name}"
    data = FINAL_MP4.read_bytes()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("apikey", os.environ["SUPABASE_SERVICE_KEY"])
    req.add_header("Authorization", f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}")
    req.add_header("Content-Type", "video/mp4")
    with urllib.request.urlopen(req, timeout=300) as resp:
        log(f"Uploaded to Supabase Storage: {bucket}/{object_name} ({resp.status})")
    return object_name


def log_job(topic, status, rating=None, object_name=None, error=None):
    if not supabase_configured():
        return
    try:
        supabase_request("POST", "/rest/v1/jobs", {
            "topic": topic, "status": status, "rating": rating,
            "storage_object": object_name, "error": error,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        log(f"[warn] Could not log job to Supabase: {e}")


def main():
    ap = argparse.ArgumentParser(description="Cloud video pipeline (no agy required)")
    ap.add_argument("--dry-run", action="store_true", help="Write script + verify inputs, skip render")
    ap.add_argument("--topic", default=None, help="Override topic rotation")
    args = ap.parse_args()

    if not AUDIO_FILE.exists():
        raise SystemExit(f"Missing audio: {AUDIO_FILE} (expected video-engine/public/audio.mp3)")
    if not shutil_which("ffmpeg"):
        log("[warn] ffmpeg not found — render step will fail. Install ffmpeg first.")

    topic = get_next_topic(args.topic)
    write_script(topic)

    if args.dry_run:
        log("Dry run complete — script written, inputs verified. Skipping render.")
        return

    try:
        run([sys.executable, str(ROOT / "render_engine.py"), str(FINAL_MP4)])
        run([sys.executable, str(ROOT / "scripts" / "review_video.py"), str(FINAL_MP4)])
        rating = None
        if REVIEW_FILE.exists():
            rating = json.loads(REVIEW_FILE.read_text()).get("rating")
        obj = upload_to_supabase()
        log_job(topic, "done", rating=rating, object_name=obj)
        log(f"✅ Pipeline complete. Rating: {rating}/10. Video: {FINAL_MP4}")
    except SystemExit as e:
        log_job(topic, "failed", error=str(e))
        raise


def shutil_which(name):
    import shutil
    return shutil.which(name)


if __name__ == "__main__":
    main()
