#!/usr/bin/env python3
"""
fetch_web_ideas.py - Scrapes & synthesizes trending video ideas from live web feeds.
Sources: Google News RSS, Hacker News, Dev.to
Filters for website conversion, SEO, mobile UX, speed, and client acquisition.
"""

import sys
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent / ".pipeline"
CACHE_FILE = PIPELINE_DIR / "web_topics.json"

SEARCH_QUERIES = [
    "small business website conversion",
    "local business website SEO mobile",
    "website speed bounce rate revenue",
    "landing page conversion optimization",
    "business automation website booking",
    "ecommerce conversion checkout dropoff"
]

POSITIVE_KEYWORDS = [
    "website", "web", "landing page", "conversion", "seo", "bounce rate",
    "page speed", "mobile", "ecommerce", "e-commerce", "clients", "customers",
    "leads", "inquiries", "traffic", "web design", "online presence", "sales",
    "checkout", "booking", "ui", "ux", "funnel"
]

NEGATIVE_KEYWORDS = [
    "sagemaker", "gpu", "bedrock", "nvidia", "asp.net", "cpu spoofing",
    "dharma-ai", "multiple monitors", "dock", "ipo", "rsa", "quick agents",
    "c#", "c++", "linux kernel", "chuwi", "crypto", "bitcoin", "blockchain",
    "i built", "my childhood", "game about", "monuments in the", "fastapi 0.",
    "i let ai build", "nuxt cli v4"
]

DEFAULT_FALLBACKS = [
    "Why your business website is losing you high-paying clients and how to fix it in 3 steps",
    "The 3 silent conversion killers on small business landing pages",
    "Why relying solely on social media pages instead of an official website hurts your brand trust",
    "How page load speed under 2 seconds directly doubles your customer inquiries",
    "How an automated booking and menu system frees up 15 hours a week for local business owners",
    "Why mobile bounce rates kill local business leads and the 60-second fix",
    "How adding clear pricing and social proof instantly boosts website bookings"
]

def clean_title(title: str) -> str:
    """Removes publication source attribution, brackets, and extra whitespace."""
    title = re.sub(r'\s*[-|–—:]\s*[^-\|–—:]*$', '', title)
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
    title = re.sub(r'[\r\n\t]+', ' ', title)
    title = re.sub(r'\s{2,}', ' ', title).strip()
    return title

def is_relevant(text: str) -> bool:
    t = text.lower()
    if any(neg in t for neg in NEGATIVE_KEYWORDS):
        return False
    return any(pos in t for pos in POSITIVE_KEYWORDS)

def format_video_topic(raw_headline: str) -> str:
    raw = clean_title(raw_headline)
    lower = raw.lower()

    # If it's already an active question or actionable guide
    if any(lower.startswith(q) for q in ["how ", "why ", "what to ", "ways to ", "the 3 ", "5 reasons ", "stop "]):
        return raw.strip(".?")
    if lower.startswith("what "):
        return f"{raw.strip('.?')}: What local businesses should know"

    # Natural transformation
    if "bounce rate" in lower:
        return f"{raw.strip('.?')}: How high bounce rates are killing your online sales"
    if "speed" in lower or "performance" in lower:
        return f"{raw.strip('.?')}: Why slow load times lose high-paying clients"
    if "landing page" in lower or "conversion" in lower:
        return f"{raw.strip('.?')}: Quick landing page tweaks to double leads"
    if "seo" in lower:
        return f"{raw.strip('.?')}: Simple SEO moves to get found by local customers"

    return f"How to use '{raw.strip('.?')}' to get more clients"

def fetch_google_news() -> list:
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for q in SEARCH_QUERIES[:4]:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('./channel/item')[:5]:
                    t = item.find('title')
                    if t is not None and t.text:
                        c = clean_title(t.text)
                        if len(c) > 15 and is_relevant(c):
                            items.append(c)
        except Exception:
            continue
    return items

def fetch_hackernews() -> list:
    items = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://hn.algolia.com/api/v1/search?query=landing+page+conversion+OR+website+speed&tags=story&hitsPerPage=10"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for hit in data.get("hits", []):
                t = hit.get("title")
                if t:
                    c = clean_title(t)
                    if len(c) > 15 and is_relevant(c):
                        items.append(c)
    except Exception:
        pass
    return items

def generate_web_ideas() -> list:
    raw_ideas = []
    raw_ideas.extend(fetch_google_news())
    raw_ideas.extend(fetch_hackernews())

    seen = set()
    unique_topics = []
    for idea in raw_ideas:
        topic = format_video_topic(idea)
        simplified = re.sub(r'[^a-zA-Z0-9]', '', topic.lower())
        if simplified and simplified not in seen:
            seen.add(simplified)
            unique_topics.append(topic)

    if not unique_topics:
        unique_topics = DEFAULT_FALLBACKS

    return unique_topics

def get_next_idea(force_refresh=False) -> str:
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    cache = {"topics": [], "index": 0}

    if CACHE_FILE.exists() and not force_refresh:
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {"topics": [], "index": 0}

    topics = cache.get("topics", [])
    index = cache.get("index", 0)

    if not topics or index >= len(topics) or force_refresh:
        topics = generate_web_ideas()
        index = 0

    topic = topics[index % len(topics)]
    cache["topics"] = topics
    cache["index"] = index + 1

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

    return topic

if __name__ == "__main__":
    force = "--refresh" in sys.argv
    if "--list" in sys.argv:
        ideas = generate_web_ideas()
        print(json.dumps(ideas, indent=2))
    else:
        idea = get_next_idea(force_refresh=force)
        print(idea)
