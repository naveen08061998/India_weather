"""
Short News — RSS Fetcher & Crisp Summariser
===============================================
Parses RSS/Atom feeds (feedparser, no API key) and condenses each article's
description down to a strict ~60-word "crisp summary" — the same bite-sized
format popularised by apps like Inshorts — so a reader gets the complete
gist of a story in a few seconds, without needing to open the full article.

No AI/LLM summarisation is used (this repo only uses free, keyless public
APIs/feeds) — the crispening is purely extractive: clean the RSS
description's HTML, then hard-cap at MAX_WORDS, trimmed to the nearest
sentence boundary where possible.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

IST = timezone(timedelta(hours=5, minutes=30))

try:
    import feedparser  # type: ignore
except ImportError as e:
    raise ImportError("feedparser is required. Install it with: pip install feedparser") from e

import requests

REQUEST_TIMEOUT = 15
MAX_ARTICLES    = 12
MAX_WORDS       = 60          # Inshorts-style hard cap per story
READ_WPS        = 3           # assumed reading speed: ~180 words/minute
USER_AGENT = "ShortNewsBot/1.0 (quick-read-digest; contact: admin@example.com)"

_SOURCE_MAP = {
    "feeds.feedburner.com": "NDTV",
    "economictimes.indiatimes.com": "Economic Times",
    "www.livemint.com": "Livemint",
    "livemint.com": "Livemint",
}


def _source_name(url: str) -> str:
    host = urlparse(url).hostname or url
    if host in _SOURCE_MAP:
        return _SOURCE_MAP[host]
    host = host.replace("www.", "")
    return host.split(".")[0].replace("-", " ").title()


def _parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
        return dt.strftime("%Y-%m-%d %H:%M IST")
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
        return dt.strftime("%Y-%m-%d %H:%M IST")
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")


def _clean_html(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def crisp_summary(raw_text: str | None, max_words: int = MAX_WORDS) -> tuple[str, int]:
    """Condense raw text to <= max_words, ending at a sentence boundary when possible.

    Returns (summary_text, word_count).
    """
    text = _clean_html(raw_text)
    words = text.split()
    if len(words) <= max_words:
        return text, len(words)

    truncated = " ".join(words[:max_words])
    # Prefer cutting at the last sentence-ending punctuation within the cap.
    last_stop = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
    if last_stop >= int(max_words * 0.5):  # only use it if it isn't too early
        truncated = truncated[:last_stop + 1]
    else:
        truncated = truncated.rstrip(",;:- ") + "…"
    return truncated, len(truncated.split())


def read_time_label(word_count: int) -> str:
    seconds = max(5, round(word_count / READ_WPS))
    if seconds < 60:
        return f"~{seconds} sec read"
    minutes = seconds / 60
    return f"~{minutes:.1f} min read".replace(".0 min", " min")


def fetch_feed(url: str, limit: int = MAX_ARTICLES) -> list[dict]:
    articles = []
    source = _source_name(url)
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:limit]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue
            raw_summary = getattr(entry, "summary", None) or getattr(entry, "description", None)
            summary, word_count = crisp_summary(raw_summary)
            if not summary:
                # Fall back to a crisped version of the title itself rather than skip the story.
                summary, word_count = crisp_summary(title)
            articles.append({
                "title": title,
                "summary": summary,
                "word_count": word_count,
                "read_time": read_time_label(word_count),
                "link": link,
                "published": _parse_date(entry),
                "source": source,
            })
    except Exception as exc:
        print(f"  [WARN] Feed failed ({source}): {exc}")
    return articles


def fetch_category(category: dict) -> dict:
    all_articles: list[dict] = []
    seen_titles: set[str] = set()

    for url in category["feeds"]:
        items = fetch_feed(url)
        for art in items:
            key = art["title"].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                art["category_key"] = category["key"]
                art["category_label"] = category["label"]
                art["category_icon"] = category["icon"]
                art["category_color"] = category["color"]
                all_articles.append(art)
        time.sleep(0.3)  # polite crawl delay between feeds

    all_articles.sort(key=lambda a: a["published"], reverse=True)
    kept = all_articles[:MAX_ARTICLES * 2]
    total_seconds = sum(max(5, round(a["word_count"] / READ_WPS)) for a in kept)

    return {
        "key": category["key"],
        "label": category["label"],
        "icon": category["icon"],
        "color": category["color"],
        "description": category.get("description", ""),
        "articles": kept,
        "total_read_seconds": total_seconds,
        "fetched_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "error": None if kept else "No articles fetched",
    }
