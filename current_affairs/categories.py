"""
Current Affairs — Category Registry
=====================================
Defines the 10 exam-relevant categories with curated free RSS feed sources.
Each category maps to one or more RSS URLs that are parsed by fetcher.py.

Categories are aligned with UPSC, SSC, State PSC, Banking, and Railway
competitive exam syllabi.
"""

from __future__ import annotations

# ── Category registry ──────────────────────────────────────────────────────
# Format:
#   key        : internal identifier
#   label      : display name shown on dashboard
#   color      : accent hex colour for the dashboard card
#   icon       : emoji icon
#   feeds      : list of RSS URLs (all free / no API key required)
#   description: short description shown to aspirants

CATEGORIES: list[dict] = [
    {
        "key": "national",
        "label": "National Affairs",
        "color": "#f97316",
        "icon": "🇮🇳",
        "description": "Government policies, Parliament, ministries, schemes & governance updates.",
        "feeds": [
            "https://feeds.feedburner.com/ndtvnews-india-news",
            "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
            "https://economictimes.indiatimes.com/rssfeeds/20989204.cms",
        ],
    },
    {
        "key": "international",
        "label": "International Affairs",
        "color": "#6366f1",
        "icon": "🌍",
        "description": "Bilateral relations, UN, global summits, geopolitics & foreign policy.",
        "feeds": [
            "https://feeds.feedburner.com/ndtvnews-world-news",
            "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        ],
    },
    {
        "key": "economy",
        "label": "Economy & Finance",
        "color": "#10b981",
        "icon": "💹",
        "description": "Budget, RBI, GDP, inflation, banking, trade & economic surveys.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/1977021501.cms",
            "https://www.livemint.com/rss/economy",
            "https://www.livemint.com/rss/markets",
        ],
    },
    {
        "key": "science_tech",
        "label": "Science & Technology",
        "color": "#3b82f6",
        "icon": "🔬",
        "description": "Space, ISRO, defence tech, AI, biotech, research & innovation.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/13357270.cms",
            "https://www.livemint.com/rss/science",
        ],
    },
    {
        "key": "environment",
        "label": "Environment & Ecology",
        "color": "#22c55e",
        "icon": "🌿",
        "description": "Climate change, biodiversity, wildlife, national parks & green policies.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/2647163.cms",
            "https://www.livemint.com/rss/science",
        ],
    },
    {
        "key": "polity",
        "label": "Governance & Polity",
        "color": "#a855f7",
        "icon": "⚖️",
        "description": "Supreme Court, elections, constitutional amendments, ECI & tribunals.",
        "feeds": [
            "https://www.livemint.com/rss/politics",
            "https://economictimes.indiatimes.com/rssfeeds/1052732854.cms",
            "https://feeds.feedburner.com/ndtvnews-india-news",
        ],
    },
    {
        "key": "defence",
        "label": "Defence & Security",
        "color": "#ef4444",
        "icon": "🛡️",
        "description": "Military exercises, defence acquisitions, DRDO, border & internal security.",
        "feeds": [
            "https://economictimes.indiatimes.com/rssfeeds/1052732854.cms",
            "https://economictimes.indiatimes.com/rssfeeds/20989204.cms",
        ],
    },
    {
        "key": "sports",
        "label": "Sports",
        "color": "#f59e0b",
        "icon": "🏅",
        "description": "Olympics, Commonwealth Games, cricket, tournaments & Indian sports achievements.",
        "feeds": [
            "https://www.livemint.com/rss/sports",
            "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        ],
    },
    {
        "key": "awards",
        "label": "Awards & Honours",
        "color": "#ec4899",
        "icon": "🏆",
        "description": "Padma awards, national honours, Nobel Prize, Bharat Ratna & key recognitions.",
        "feeds": [
            "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
            "https://feeds.feedburner.com/ndtvnews-india-news",
        ],
    },
    {
        "key": "art_culture",
        "label": "Art & Culture",
        "color": "#06b6d4",
        "icon": "🎭",
        "description": "Heritage, UNESCO listings, festivals, Indian history & cultural events.",
        "feeds": [
            "https://www.livemint.com/rss/leisure",
            "https://www.livemint.com/rss/news",
        ],
    },
]

# ── Shared feeds used for all state categories ─────────────────────────────
# City-specific feeds from IE/TOI/HT are inaccessible; we pull from broad
# India feeds and filter by state keywords in the fetcher.
_STATE_FEEDS = [
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://economictimes.indiatimes.com/rssfeeds/20989204.cms",
    "https://economictimes.indiatimes.com/rssfeeds/1977021501.cms",
    "https://economictimes.indiatimes.com/rssfeeds/1052732854.cms",
    "https://economictimes.indiatimes.com/rssfeeds/2647163.cms",
    "https://feeds.feedburner.com/ndtvnews-india-news",
    "https://feeds.feedburner.com/ndtvnews-world-news",
    "https://www.livemint.com/rss/politics",
    "https://www.livemint.com/rss/news",
    "https://www.livemint.com/rss/economy",
    "https://www.livemint.com/rss/companies",
]

STATE_CATEGORIES: list[dict] = [
    {
        "key": "state_delhi",
        "label": "Delhi / NCR",
        "color": "#e11d48",
        "icon": "🏛️",
        "description": "Delhi governance, LG, MCD, NCR development & political updates.",
        "feeds": _STATE_FEEDS,
        "keywords": ["delhi", "ncr", "noida", "gurgaon", "gurugram", "faridabad",
                     "mcd", "new delhi", "dwarka", "rohini"],
        "group": "state",
    },
    {
        "key": "state_maharashtra",
        "label": "Maharashtra",
        "color": "#f97316",
        "icon": "🌆",
        "description": "Mumbai, Pune, Nagpur — state politics, economy & development news.",
        "feeds": _STATE_FEEDS,
        "keywords": ["maharashtra", "mumbai", "pune", "nagpur", "nashik", "thane",
                     "aurangabad", "mpsc", "maha"],
        "group": "state",
    },
    {
        "key": "state_tamil_nadu",
        "label": "Tamil Nadu",
        "color": "#0891b2",
        "icon": "🏯",
        "description": "Chennai, state politics, TNPSC, education, industry & cultural news.",
        "feeds": _STATE_FEEDS,
        "keywords": ["tamil nadu", "tamilnadu", "chennai", "coimbatore", "madurai",
                     "trichy", "tirunelveli", "salem", "erode", "vellore",
                     "tnpsc", "dmk", "aiadmk", "mk stalin"],
        "group": "state",
    },
    {
        "key": "state_karnataka",
        "label": "Karnataka",
        "color": "#7c3aed",
        "icon": "🌉",
        "description": "Bengaluru, KPSC, tech hub, Vidhana Soudha & state governance.",
        "feeds": _STATE_FEEDS,
        "keywords": ["karnataka", "bengaluru", "bangalore", "mysuru", "mysore",
                     "kpsc", "hubli", "mangaluru", "siddaramaiah"],
        "group": "state",
    },
    {
        "key": "state_andhra_telangana",
        "label": "AP & Telangana",
        "color": "#0d9488",
        "icon": "🌾",
        "description": "Hyderabad, APPSC, TSPSC, state bifurcation issues & development.",
        "feeds": _STATE_FEEDS,
        "keywords": ["andhra", "telangana", "hyderabad", "amaravati", "vizag",
                     "visakhapatnam", "appsc", "tspsc", "revanth"],
        "group": "state",
    },
    {
        "key": "state_west_bengal",
        "label": "West Bengal",
        "color": "#b45309",
        "icon": "🐯",
        "description": "Kolkata, WBPSC, state politics, Sundarbans & cultural heritage.",
        "feeds": _STATE_FEEDS,
        "keywords": ["west bengal", "kolkata", "calcutta", "wbpsc", "mamata",
                     "trinamool", "tmc", "howrah", "sundarbans"],
        "group": "state",
    },
    {
        "key": "state_gujarat",
        "label": "Gujarat",
        "color": "#d97706",
        "icon": "🦁",
        "description": "Ahmedabad, GPSC, GIFT City, trade, industry & state governance.",
        "feeds": _STATE_FEEDS,
        "keywords": ["gujarat", "ahmedabad", "surat", "vadodara", "gandhinagar",
                     "gpsc", "gift city"],
        "group": "state",
    },
    {
        "key": "state_uttar_pradesh",
        "label": "Uttar Pradesh",
        "color": "#16a34a",
        "icon": "🕌",
        "description": "Lucknow, UPPSC, religious cities, expressways & UP development projects.",
        "feeds": _STATE_FEEDS,
        "keywords": ["uttar pradesh", "lucknow", "noida", "kanpur", "varanasi",
                     "agra", "prayagraj", "uppsc", "yogi"],
        "group": "state",
    },
    {
        "key": "state_rajasthan",
        "label": "Rajasthan",
        "color": "#ea580c",
        "icon": "🏜️",
        "description": "Jaipur, RPSC, desert regions, tourism, minerals & heritage sites.",
        "feeds": _STATE_FEEDS,
        "keywords": ["rajasthan", "jaipur", "jodhpur", "udaipur", "kota",
                     "ajmer", "bikaner", "alwar", "rpsc", "bhajanlal", "gehlot"],
        "group": "state",
    },
    {
        "key": "state_punjab_haryana",
        "label": "Punjab & Haryana",
        "color": "#84cc16",
        "icon": "🌾",
        "description": "Chandigarh, agriculture, PPSC, HPSC & border state developments.",
        "feeds": _STATE_FEEDS,
        "keywords": ["punjab", "haryana", "chandigarh", "amritsar", "ludhiana",
                     "gurugram", "faridabad", "ppsc", "hpsc"],
        "group": "state",
    },
    {
        "key": "state_madhya_pradesh",
        "label": "Madhya Pradesh",
        "color": "#8b5cf6",
        "icon": "🐆",
        "description": "Bhopal, MPPSC, tiger reserves, tribal affairs & Narmada projects.",
        "feeds": _STATE_FEEDS,
        "keywords": ["madhya pradesh", "bhopal", "indore", "jabalpur", "gwalior",
                     "ujjain", "rewa", "satna", "mppsc", "narmada", "mohan yadav", "mp govt"],
        "group": "state",
    },
    {
        "key": "state_bihar",
        "label": "Bihar & Jharkhand",
        "color": "#f59e0b",
        "icon": "🪔",
        "description": "Patna, BPSC, JPSC, Ganga plains, tribal regions & social schemes.",
        "feeds": _STATE_FEEDS,
        "keywords": ["bihar", "jharkhand", "patna", "ranchi", "gaya", "muzaffarpur",
                     "bpsc", "jpsc", "nitish", "hemant"],
        "group": "state",
    },
]

# ── Combined registry ──────────────────────────────────────────────────────
ALL_CATEGORIES: list[dict] = CATEGORIES + STATE_CATEGORIES

# Quick lookup by key
CATEGORY_MAP: dict[str, dict] = {c["key"]: c for c in ALL_CATEGORIES}

