#!/usr/bin/env python3
"""
parse_vtt.py - Parses WebVTT into word-level timing JSON (.pipeline/word_timings.json)
"""

import os
import sys
import json
import re
from pathlib import Path

def parse_time(ts_str):
    """Converts 00:00:01,575 or 00:00:01.575 to seconds float."""
    ts_str = ts_str.strip().replace(",", ".")
    parts = ts_str.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    return float(ts_str)

def parse_vtt(vtt_path=".pipeline/subtitles.vtt", out_path=".pipeline/word_timings.json"):
    if not os.path.exists(vtt_path):
        print(f"Warning: {vtt_path} does not exist. Creating empty word_timings.json.")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Pattern for cues: 00:00:00,050 --> 00:00:01,575
    cue_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n(.*?)(?=\n\s*\n|\n\d+\s*\n|\Z)', re.DOTALL)

    words_data = []

    for match in cue_pattern.finditer(content):
        start_sec = parse_time(match.group(1))
        end_sec = parse_time(match.group(2))
        raw_text = match.group(3).strip()
        # Clean tags like <c> </c>
        clean_text = re.sub(r'<[^>]+>', '', raw_text)
        tokens = [w for w in clean_text.split() if w]
        if not tokens:
            continue

        cue_dur = max(0.1, end_sec - start_sec)
        token_dur = cue_dur / len(tokens)

        for i, word in enumerate(tokens):
            w_start = start_sec + (i * token_dur)
            w_end = w_start + token_dur
            words_data.append({
                "word": word,
                "start": round(w_start, 3),
                "end": round(w_end, 3)
            })

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(words_data, f, indent=2)

    print(f"✅ Extracted {len(words_data)} word timings -> {out_path}")
    return words_data

if __name__ == "__main__":
    vtt = sys.argv[1] if len(sys.argv) > 1 else ".pipeline/subtitles.vtt"
    out = sys.argv[2] if len(sys.argv) > 2 else ".pipeline/word_timings.json"
    parse_vtt(vtt, out)
