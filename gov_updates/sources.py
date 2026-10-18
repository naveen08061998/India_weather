"""
Government Updates — Source Registry
=======================================
Free, no-key data sources:
  • General/policy English news RSS feeds (NDTV, Economic Times, Livemint —
    the same proven-reliable sources already used by current_affairs/).
    NOTE: PIB's own RSS feed (pib.gov.in) was tried first but its RssMain.aspx
    endpoint serves Hindi-language titles regardless of the documented
    Lang=1/Lang=2 query parameter, so it isn't usable here — the English
    feeds below are filtered by keyword instead.
  • A curated static calendar of major recurring competitive-exam cycles
    (hand-compiled public knowledge — notification windows vary year to
    year, treat as an approximate guide, not an official schedule).
"""

from __future__ import annotations

# ── Live feeds (filtered by keyword into "scheme" vs "exam" buckets) ──────
NEWS_FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-india-news",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://economictimes.indiatimes.com/rssfeeds/1052732854.cms",
    "https://www.livemint.com/rss/politics",
]

SCHEME_KEYWORDS = [
    "yojana", "scheme", "mission", "abhiyan", "programme", "program",
    "initiative", "subsidy", "pm-", "pradhan mantri", "portal launch",
    "welfare", "fund launched", "pmay", "pmkisan", "ayushman",
]

EXAM_KEYWORDS = [
    "exam", "examination", "recruitment", "vacancy", "notification",
    "admit card", "result declared", "upsc", "ssc", "ibps", "rrb",
    "nda", "cds", "neet", "jee", "ctet", "net ", "nta",
]

# ── Curated exam calendar (static reference data) ──────────────────────────
# notify_month / exam_month are TYPICAL months based on past cycles —
# actual dates vary each year; always verify on the official site.
EXAM_CALENDAR: list[dict] = [
    {
        "name": "UPSC Civil Services Examination (CSE)",
        "body": "Union Public Service Commission",
        "site": "https://upsc.gov.in",
        "level": "National", "category": "Civil Services",
        "notify_month": "February", "exam_month": "May–June (Prelims)",
        "note": "India's premier civil services exam for IAS/IPS/IFS and allied services.",
    },
    {
        "name": "UPSC NDA & NA Examination",
        "body": "Union Public Service Commission",
        "site": "https://upsc.gov.in",
        "level": "National", "category": "Defence",
        "notify_month": "December & June (twice yearly)", "exam_month": "April & September",
        "note": "Entry into the National Defence Academy and Naval Academy after Class 12.",
    },
    {
        "name": "SSC Combined Graduate Level (CGL)",
        "body": "Staff Selection Commission",
        "site": "https://ssc.gov.in",
        "level": "National", "category": "Graduate-level Govt Jobs",
        "notify_month": "June–July", "exam_month": "September",
        "note": "Group B/C posts across central government ministries & departments.",
    },
    {
        "name": "SSC Combined Higher Secondary Level (CHSL)",
        "body": "Staff Selection Commission",
        "site": "https://ssc.gov.in",
        "level": "National", "category": "12th-pass Govt Jobs",
        "notify_month": "October–November", "exam_month": "January–February",
        "note": "LDC/JSA/DEO posts for 12th-pass candidates.",
    },
    {
        "name": "IBPS PO (Probationary Officer)",
        "body": "Institute of Banking Personnel Selection",
        "site": "https://www.ibps.in",
        "level": "National", "category": "Banking",
        "notify_month": "August", "exam_month": "October–November (Prelims)",
        "note": "Common recruitment for Probationary Officers across public sector banks.",
    },
    {
        "name": "IBPS Clerk",
        "body": "Institute of Banking Personnel Selection",
        "site": "https://www.ibps.in",
        "level": "National", "category": "Banking",
        "notify_month": "September", "exam_month": "December (Prelims)",
        "note": "Common recruitment for Clerical cadre across public sector banks.",
    },
    {
        "name": "SBI PO / Clerk",
        "body": "State Bank of India",
        "site": "https://sbi.bank.in/web/careers",
        "level": "National", "category": "Banking",
        "notify_month": "April (PO) / November (Clerk)", "exam_month": "Varies",
        "note": "Direct recruitment drives for State Bank of India (separate from IBPS).",
    },
    {
        "name": "RRB NTPC (Non-Technical Popular Categories)",
        "body": "Railway Recruitment Boards",
        "site": "https://www.rrbapply.gov.in",
        "level": "National", "category": "Railways",
        "notify_month": "Irregular (every 2-4 yrs)", "exam_month": "Varies",
        "note": "Clerk, ticket examiner, station master and other non-technical railway posts.",
    },
    {
        "name": "RRB Group D",
        "body": "Railway Recruitment Boards",
        "site": "https://www.rrbapply.gov.in",
        "level": "National", "category": "Railways",
        "notify_month": "Irregular (every 2-4 yrs)", "exam_month": "Varies",
        "note": "Track maintainer, helper and other Level-1 railway posts.",
    },
    {
        "name": "CTET (Central Teacher Eligibility Test)",
        "body": "CBSE",
        "site": "https://ctet.nic.in",
        "level": "National", "category": "Teaching",
        "notify_month": "September & January (twice yearly)", "exam_month": "December & July",
        "note": "Eligibility test for teaching positions in central government schools.",
    },
    {
        "name": "UGC NET",
        "body": "National Testing Agency",
        "site": "https://nta.ac.in",
        "level": "National", "category": "Higher Education",
        "notify_month": "February & August (twice yearly)", "exam_month": "June & December",
        "note": "Eligibility for Assistant Professor / Junior Research Fellowship.",
    },
    {
        "name": "JEE Main",
        "body": "National Testing Agency",
        "site": "https://nta.ac.in",
        "level": "National", "category": "Engineering Entrance",
        "notify_month": "November", "exam_month": "January & April (two sessions)",
        "note": "Gateway to NITs/IIITs and JEE Advanced (IIT) eligibility.",
    },
    {
        "name": "NEET (UG)",
        "body": "National Testing Agency",
        "site": "https://nta.ac.in",
        "level": "National", "category": "Medical Entrance",
        "notify_month": "February", "exam_month": "May",
        "note": "Single entrance exam for MBBS/BDS admissions across India.",
    },
    {
        "name": "RBI Grade B Officer",
        "body": "Reserve Bank of India",
        "site": "https://rbi.org.in",
        "level": "National", "category": "Banking/Regulatory",
        "notify_month": "July–August", "exam_month": "September–October (Phase 1)",
        "note": "Entry-level officer recruitment directly into the RBI.",
    },
    {
        "name": "CDS (Combined Defence Services)",
        "body": "Union Public Service Commission",
        "site": "https://upsc.gov.in",
        "level": "National", "category": "Defence",
        "notify_month": "November & May (twice yearly)", "exam_month": "February & September",
        "note": "Entry into IMA, OTA, INA and AFA for graduates.",
    },
]
