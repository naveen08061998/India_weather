"""
Indian Railways — News Ticker Client
======================================
Fetches recent Indian Railways-related headlines via Google News' free RSS
search feed (no API key, no scraping of individual publisher sites). This is
self-contained — it does NOT depend on the separate current_affairs service,
since indian_railways is deployed as its own independent web service
(see render.yaml) and can't rely on another service's local cache file.

Never raises — returns [] on any failure so the ticker just stays hidden.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

import requests

try:
    import feedparser  # type: ignore
except ImportError as e:
    raise ImportError("feedparser is required. Install it with: pip install feedparser") from e

IST = timezone(timedelta(hours=5, minutes=30))

_FEED_URL = "https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
_QUERY = "Indian Railways OR IRCTC OR Vande Bharat OR RRTS"
_TIMEOUT = 15
_MAX_ARTICLES = 12
_USER_AGENT = "IndianRailwaysTracker/1.0 (news ticker; contact: admin@example.com)"

_TITLE_SOURCE_RE = re.compile(r"^(.*)\s-\s([^-]+)$")


def _split_title(raw_title: str) -> tuple[str, str]:
    """Google News titles are formatted 'Headline - Source' — split them apart."""
    m = _TITLE_SOURCE_RE.match(raw_title)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return raw_title.strip(), ""




def _parse_datetime(entry) -> datetime:
    """Actual datetime for sorting (falls back to epoch so undated entries sort last)."""
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
    return datetime.min.replace(tzinfo=IST)


def fetch_railway_news(limit: int = _MAX_ARTICLES) -> list[dict]:
    """Recent railway-related headlines, newest first. Returns [] on failure.

    Google News' RSS feed is ordered by relevance, not strictly by recency —
    a same-day article can end up buried behind older but more "relevant"
    ones — so results are explicitly re-sorted by actual published time here
    rather than trusting feed order.
    """
    url = _FEED_URL.format(q=quote(_QUERY))
    try:
        resp = requests.get(url, headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT, verify=False)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception:
        return []

    parsed: list[tuple[datetime, dict]] = []
    for entry in feed.entries:
        raw_title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()
        if not raw_title or not link:
            continue
        title, source = _split_title(raw_title)
        when = _parse_datetime(entry)
        parsed.append((when, {
            "title": title,
            "source": source,
            "link": link,
            "published": when.strftime("%d %b, %H:%M IST") if when != datetime.min.replace(tzinfo=IST) else "",
        }))
    parsed.sort(key=lambda pair: pair[0], reverse=True)
    return [article for _, article in parsed[:limit]]
