"""
Stock Market — Market News Client
=====================================
Fetches general business/market headlines from free English RSS feeds
(same proven-reliable sources used by current_affairs/gov_updates) and
keeps only the ones that look market-related by keyword match.
"""

from __future__ import annotations

import re
import requests
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

IST = timezone(timedelta(hours=5, minutes=30))

try:
    import feedparser  # type: ignore
except ImportError as e:
    raise ImportError(
        "feedparser is required. Install it with: pip install feedparser"
    ) from e

NEWS_FEEDS = [
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://economictimes.indiatimes.com/rssfeeds/1977021501.cms",   # markets/economy
    "https://www.livemint.com/rss/markets",
]

MARKET_KEYWORDS = [
    "nifty", "sensex", "bse", "nse", "stock", "share", "ipo", "rally",
    "selloff", "sell-off", "rupee", "market cap", "earnings", "q2 results",
    "quarterly results", "fii", "dii", "bull", "bear", "rbi", "repo rate",
    "mutual fund", "sebi",
]

REQUEST_TIMEOUT = 15
MAX_PER_FEED    = 100
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

_SOURCE_MAP = {
    "economictimes.indiatimes.com": "Economic Times",
    "www.livemint.com": "Livemint",
}


def _source_name(url: str) -> str:
    host = urlparse(url).hostname or url
    return _SOURCE_MAP.get(host, host.replace("www.", "").split(".")[0].title())


def _clean_summary(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:220] + ("…" if len(text) > 220 else "")


def _parse_datetime(entry) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
    return datetime.now(IST)


MAX_AGE_DAYS = 14   # ET's feed mixes in old "evergreen" articles that still match keywords


def fetch_market_news(limit: int = 12) -> list[dict]:
    """Fetch and keyword-filter market-related headlines, newest-first, deduped."""
    all_articles: list[dict] = []
    seen_titles: set[str] = set()
    cutoff = datetime.now(IST) - timedelta(days=MAX_AGE_DAYS)

    for url in NEWS_FEEDS:
        try:
            headers = {"User-Agent": USER_AGENT}
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            source = _source_name(url)
            for entry in feed.entries[:MAX_PER_FEED]:
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                if not title or not link:
                    continue
                key = title.lower()
                if key in seen_titles:
                    continue
                summary = _clean_summary(getattr(entry, "summary", None)
                                          or getattr(entry, "description", None))
                text = (title + " " + summary).lower()
                if not any(kw in text for kw in MARKET_KEYWORDS):
                    continue
                published_dt = _parse_datetime(entry)
                if published_dt < cutoff:
                    continue
                seen_titles.add(key)
                all_articles.append({
                    "title": title, "summary": summary, "link": link,
                    "published": published_dt.strftime("%Y-%m-%d %H:%M IST"),
                    "published_dt": published_dt, "source": source,
                })
        except Exception as exc:
            print(f"  [WARN] Market news feed failed ({url}): {exc}")

    all_articles.sort(key=lambda a: a["published_dt"], reverse=True)
    for a in all_articles:
        del a["published_dt"]
    return all_articles[:limit]
