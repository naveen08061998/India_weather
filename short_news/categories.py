"""
Short News — Category Registry
=================================
General-audience (not exam-prep specific) news categories for the "Quick
Read" digest. Reuses the SAME free RSS feed URLs already proven reliable
elsewhere in this repo (current_affairs/categories.py, gov_updates/sources.py)
— no new/unverified feed sources introduced.
"""

from __future__ import annotations

CATEGORIES: list[dict] = [
    {
        "key": "top", "label": "Top Stories", "icon": "⚡", "color": "#ef4444",
        "description": "The biggest headlines right now, across every topic.",
        "feeds": [
            "https://feeds.feedburner.com/ndtvnews-india-news",
            "https://feeds.feedburner.com/ndtvnews-world-news",
            "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        ],
    },
    {
        "key": "india", "label": "India", "icon": "🇮🇳", "color": "#f97316",
        "description": "National news — government, states, society & public life.",
        "feeds": [
            "https://feeds.feedburner.com/ndtvnews-india-news",
            "https://economictimes.indiatimes.com/rssfeeds/1052732854.cms",
        ],
    },
    {
        "key": "world", "label": "World", "icon": "🌍", "color": "#6366f1",
        "description": "International affairs, diplomacy & global events.",
        "feeds": [
            "https://feeds.feedburner.com/ndtvnews-world-news",
        ],
    },
    {
        "key": "business", "label": "Business & Markets", "icon": "💹", "color": "#10b981",
        "description": "Markets, companies, economy & personal finance.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/1977021501.cms",
            "https://www.livemint.com/rss/markets",
            "https://www.livemint.com/rss/companies",
        ],
    },
    {
        "key": "technology", "label": "Technology", "icon": "💻", "color": "#3b82f6",
        "description": "Gadgets, AI, startups, space & scientific breakthroughs.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/13357270.cms",
            "https://www.livemint.com/rss/science",
        ],
    },
    {
        "key": "sports", "label": "Sports", "icon": "🏅", "color": "#eab308",
        "description": "Cricket, football, Olympics & every major sporting result.",
        "feeds": [
            "https://www.livemint.com/rss/sports",
        ],
    },
    {
        "key": "entertainment", "label": "Entertainment", "icon": "🎬", "color": "#ec4899",
        "description": "Movies, OTT, music & celebrity news.",
        "feeds": [
            "https://www.livemint.com/rss/leisure",
        ],
    },
    {
        "key": "health", "label": "Health & Lifestyle", "icon": "🩺", "color": "#22c55e",
        "description": "Wellness, medical research & everyday lifestyle news.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/2647163.cms",
            "https://www.livemint.com/rss/news",
        ],
    },
]

CATEGORY_MAP = {c["key"]: c for c in CATEGORIES}
