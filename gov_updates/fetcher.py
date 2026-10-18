"""
Government Updates — News Fetcher
=====================================
Fetches the curated English news feeds once, then buckets articles into
"schemes" and "exam notifications" by keyword match (same approach as
current_affairs/fetcher.py).
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
    raise ImportError(
        "feedparser is required. Install it with: pip install feedparser"
    ) from e

import requests

from gov_updates.sources import NEWS_FEEDS, SCHEME_KEYWORDS, EXAM_KEYWORDS

REQUEST_TIMEOUT = 15
MAX_PER_FEED    = 200   # fetch full feed so keyword filtering has enough to match
# A plain bot UA gets a 403 from some of these hosts; a standard browser UA doesn't.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

_SOURCE_MAP = {
    "feeds.feedburner.com": "NDTV",
    "economictimes.indiatimes.com": "Economic Times",
    "www.livemint.com": "Livemint",
    "livemint.com": "Livemint",
}


def _source_name(url: str) -> str:
    host = urlparse(url).hostname or url
    return _SOURCE_MAP.get(host, host.replace("www.", "").split(".")[0].title())


def _clean_summary(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300] + ("…" if len(text) > 300 else "")


def _parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
        return dt.strftime("%Y-%m-%d %H:%M IST")
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")


def fetch_feed(url: str, limit: int = MAX_PER_FEED) -> list[dict]:
    """Fetch and parse a single RSS/Atom feed URL into normalised article dicts."""
    articles: list[dict] = []
    source = _source_name(url)
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:limit]:
            title = getattr(entry, "title", "").strip()
            link  = getattr(entry, "link", "").strip()
            if not title or not link:
                continue
            articles.append({
                "title"    : title,
                "summary"  : _clean_summary(getattr(entry, "summary", None)
                                             or getattr(entry, "description", None)),
                "link"     : link,
                "published": _parse_date(entry),
                "source"   : source,
            })
    except Exception as exc:
        print(f"  [WARN] Feed failed ({source}): {exc}")
    return articles


def _matches(article: dict, keywords: list[str]) -> bool:
    text = (article["title"] + " " + article["summary"]).lower()
    return any(kw in text for kw in keywords)


def fetch_categorised() -> dict:
    """
    Fetch all curated feeds once (deduplicated by title) and split into
    scheme / exam buckets. Returns
    {"schemes": [...], "exams": [...], "all_count": int}.
    """
    all_articles: list[dict] = []
    seen_titles: set[str] = set()
    for url in NEWS_FEEDS:
        for art in fetch_feed(url):
            key = art["title"].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(art)
        time.sleep(0.2)

    schemes = [a for a in all_articles if _matches(a, SCHEME_KEYWORDS)]
    exams   = [a for a in all_articles if _matches(a, EXAM_KEYWORDS)]
    return {
        "schemes": schemes,
        "exams": exams,
        "all_count": len(all_articles),
    }
