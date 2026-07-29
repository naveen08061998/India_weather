"""
Current Affairs — RSS Feed Fetcher
====================================
Parses RSS/Atom feeds using the `feedparser` library (no API key required).
Returns a list of normalised article dicts for each category.

Each article dict:
    {
        "title"      : str,
        "summary"    : str,
        "link"       : str,
        "published"  : str,   # ISO-8601 or raw string from feed
        "source"     : str,   # Feed hostname
    }
"""

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
from urllib.parse import urlparse

try:
    import feedparser  # type: ignore
except ImportError as e:
    raise ImportError(
        "feedparser is required. Install it with: pip install feedparser"
    ) from e

import requests  # already in requirements.txt

# ── Constants ──────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15       # seconds per feed request
MAX_ARTICLES    = 10       # max articles returned per feed
USER_AGENT      = (
    "CurrentAffairsBot/1.0 (competitive-exam-portal; "
    "contact: admin@example.com)"
)


_SOURCE_MAP = {
    "feeds.feedburner.com": "NDTV",
    "economictimes.indiatimes.com": "Economic Times",
    "www.livemint.com": "Livemint",
    "livemint.com": "Livemint",
    "pib.gov.in": "PIB",
}

def _source_name(url: str) -> str:
    """Extract a readable source name from a feed URL."""
    host = urlparse(url).hostname or url
    if host in _SOURCE_MAP:
        return _SOURCE_MAP[host]
    host = host.replace("www.", "")
    return host.split(".")[0].replace("-", " ").title()


def _parse_date(entry) -> str:
    """Return an ISO-8601 date string from a feedparser entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
        return dt.strftime("%Y-%m-%d %H:%M IST")
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
        return dt.strftime("%Y-%m-%d %H:%M IST")
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")


def _clean_summary(text: str | None) -> str:
    """Strip HTML tags and truncate summary to 300 chars."""
    if not text:
        return ""
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300] + ("…" if len(text) > 300 else "")


def fetch_feed(url: str, limit: int = MAX_ARTICLES) -> list[dict]:
    """
    Fetch and parse a single RSS/Atom feed URL.
    Returns a list of normalised article dicts (up to `limit`).
    """
    articles = []
    source = _source_name(url)
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:limit]:
            title   = getattr(entry, "title", "").strip()
            summary = _clean_summary(getattr(entry, "summary", None)
                                     or getattr(entry, "description", None))
            link    = getattr(entry, "link", "").strip()
            if not title or not link:
                continue
            articles.append({
                "title"    : title,
                "summary"  : summary,
                "link"     : link,
                "published": _parse_date(entry),
                "source"   : source,
            })
    except Exception as exc:
        print(f"  [WARN] Feed failed ({source}): {exc}")
    return articles


def fetch_category(category: dict) -> dict:
    """
    Fetch all feeds for a category and return a combined result dict:
        {
            "key"      : str,
            "label"    : str,
            "color"    : str,
            "icon"     : str,
            "articles" : [...],   # deduplicated by title
            "fetched_at": str,
            "error"    : str | None,
        }
    """
    all_articles: list[dict] = []
    seen_titles: set[str] = set()
    keywords = [kw.lower() for kw in category.get("keywords", [])]
    # For keyword-filtered categories, fetch the full feed to maximise matches
    feed_limit = 200 if keywords else MAX_ARTICLES

    for url in category["feeds"]:
        items = fetch_feed(url, limit=feed_limit)
        for art in items:
            # If keywords are defined, article must match at least one
            if keywords:
                text = (art["title"] + " " + art["summary"]).lower()
                if not any(kw in text for kw in keywords):
                    continue
            key = art["title"].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(art)
        time.sleep(0.3)   # polite crawl delay between feeds

    # Sort newest-first (best-effort; not all feeds have reliable dates)
    all_articles.sort(key=lambda a: a["published"], reverse=True)

    return {
        "key"       : category["key"],
        "label"     : category["label"],
        "color"     : category["color"],
        "icon"      : category["icon"],
        "description": category.get("description", ""),
        "articles"  : all_articles[:MAX_ARTICLES * 2],   # cap overall
        "fetched_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "error"     : None if all_articles else "No articles fetched",
    }
