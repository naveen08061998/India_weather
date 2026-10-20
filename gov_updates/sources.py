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

# ── Glossary of common govt scheme / exam / institution terms ─────────────
# Curated, static reference data — short, neutral, factual definitions only.
GLOSSARY: list[dict] = [
    {"term": "PIB", "full": "Press Information Bureau", "category": "institution",
     "desc": "The nodal agency that disseminates official Government of India press releases to the media."},
    {"term": "DBT", "full": "Direct Benefit Transfer", "category": "scheme",
     "desc": "Mechanism that sends subsidy/benefit payments directly into a beneficiary's bank account, cutting out middlemen."},
    {"term": "RTI", "full": "Right to Information", "category": "term",
     "desc": "A law letting any citizen formally request information held by a public authority."},
    {"term": "UIDAI", "full": "Unique Identification Authority of India", "category": "institution",
     "desc": "The statutory body that issues the 12-digit Aadhaar number."},
    {"term": "PMAY", "full": "Pradhan Mantri Awas Yojana", "category": "scheme",
     "desc": "Housing-for-all scheme providing financial assistance for construction/purchase of homes."},
    {"term": "PM-KISAN", "full": "Pradhan Mantri Kisan Samman Nidhi", "category": "scheme",
     "desc": "Income-support scheme giving small/marginal farmers ₹6,000/year in three instalments via DBT."},
    {"term": "Ayushman Bharat", "full": "Ayushman Bharat — PM-JAY", "category": "scheme",
     "desc": "Health insurance scheme covering up to ₹5 lakh/family/year for secondary and tertiary hospital care."},
    {"term": "MGNREGA", "full": "Mahatma Gandhi National Rural Employment Guarantee Act", "category": "scheme",
     "desc": "Guarantees 100 days of wage employment per year to rural households that demand it."},
    {"term": "GST", "full": "Goods and Services Tax", "category": "term",
     "desc": "A unified indirect tax on the supply of goods and services, replacing most earlier central/state levies."},
    {"term": "NITI Aayog", "full": "National Institution for Transforming India", "category": "institution",
     "desc": "The government's policy think-tank that replaced the Planning Commission in 2015."},
    {"term": "RBI", "full": "Reserve Bank of India", "category": "institution",
     "desc": "India's central bank — regulates monetary policy, currency issue and the banking system."},
    {"term": "SEBI", "full": "Securities and Exchange Board of India", "category": "institution",
     "desc": "The regulator for securities and commodity markets in India."},
    {"term": "EPFO", "full": "Employees' Provident Fund Organisation", "category": "institution",
     "desc": "Manages retirement savings (provident fund, pension, insurance) for organised-sector employees."},
    {"term": "NPS", "full": "National Pension System", "category": "scheme",
     "desc": "A voluntary, defined-contribution retirement savings scheme open to all Indian citizens."},
    {"term": "NTA", "full": "National Testing Agency", "category": "institution",
     "desc": "Conducts major entrance exams such as JEE Main, NEET and UGC NET."},
    {"term": "UPSC", "full": "Union Public Service Commission", "category": "institution",
     "desc": "Conducts the Civil Services Examination and recruits for All-India and Central Services."},
    {"term": "SSC", "full": "Staff Selection Commission", "category": "institution",
     "desc": "Recruits staff for most Group B and Group C posts in central government ministries/departments."},
    {"term": "IBPS", "full": "Institute of Banking Personnel Selection", "category": "institution",
     "desc": "Conducts common recruitment exams (PO/Clerk) for public sector banks."},
    {"term": "Admit Card", "full": "Admission / Hall Ticket", "category": "term",
     "desc": "The document issued to a candidate confirming exam eligibility and venue, required for entry."},
    {"term": "Cut-off", "full": "Qualifying Cut-off Marks", "category": "term",
     "desc": "The minimum marks/rank a candidate must score to clear a stage of a competitive exam."},
    {"term": "Gazette Notification", "full": "Official Gazette Notification", "category": "term",
     "desc": "A formal public notice published by the government that gives a rule, appointment or scheme legal effect."},
    {"term": "Lok Sabha", "full": "House of the People", "category": "institution",
     "desc": "The directly-elected lower house of India's Parliament."},
    {"term": "Rajya Sabha", "full": "Council of States", "category": "institution",
     "desc": "The indirectly-elected upper house of India's Parliament, with members elected by state legislatures."},
    {"term": "Finance Commission", "full": "Finance Commission of India", "category": "institution",
     "desc": "A constitutional body, set up every 5 years, that recommends how tax revenue is shared between the Centre and states."},
    {"term": "CBSE", "full": "Central Board of Secondary Education", "category": "institution",
     "desc": "A national board of school education for public and private schools, under the Union Government."},
    {"term": "Ujjwala Yojana", "full": "Pradhan Mantri Ujjwala Yojana", "category": "scheme",
     "desc": "Provides free LPG gas connections to women from below-poverty-line households."},
    {"term": "Jan Dhan Yojana", "full": "Pradhan Mantri Jan Dhan Yojana", "category": "scheme",
     "desc": "Financial-inclusion scheme providing universal access to zero-balance bank accounts."},
]
