"""
Current Affairs — History Agent
================================
Archives the previous day's important news automatically.

Every time the orchestrator fetches a fresh batch, this agent compares
the date of the *existing* cached payload against the *incoming* one.
If they differ (i.e. a new calendar day has begun), the existing payload
is archived as that date's historical digest before it is overwritten.

Storage layout
--------------
    current_affairs/news/history/
        2026-07-29.json   ← archived snapshot for 29 Jul
        2026-07-28.json
        …

"Important" articles
--------------------
Only national-level categories are archived (no state tabs).
Up to TOP_PER_CAT articles are kept per category, deduplicated globally
by lowercase title so the same story does not appear twice.

Public API
----------
    maybe_archive(existing_payload, incoming_payload) → str | None
    load_snapshot(date_key)          → dict | None
    list_dates()                     → list[str]   (newest-first)
    today_snapshot(payload)          → saves today's data (always)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

IST = timezone(timedelta(hours=5, minutes=30))

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
NEWS_DIR    = BASE_DIR / "news"
HISTORY_DIR = NEWS_DIR / "history"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
TOP_PER_CAT = 5   # max articles kept per category in the archive

# Only these national-level categories contribute (state tabs are excluded)
NATIONAL_KEYS = frozenset({
    "national", "international", "economy", "science_tech",
    "environment", "polity", "defence", "sports", "awards", "art_culture",
})


# ── Internal helpers ─────────────────────────────────────────────────────────

def _date_key(payload: dict) -> str:
    """Extract a YYYY-MM-DD string from the payload's generated_at field."""
    gen = payload.get("generated_at", "")
    try:
        dt = datetime.strptime(gen, "%Y-%m-%d %H:%M IST")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now(IST).strftime("%Y-%m-%d")


def _pick_important(categories: dict) -> dict:
    """
    For each national-level category, keep the top TOP_PER_CAT articles.
    Articles are globally deduplicated by lowercase title across categories.
    Returns a new dict with only the picked articles.
    """
    seen: set[str] = set()
    result: dict = {}

    # Preserve the canonical category order defined in NATIONAL_KEYS
    ordered_keys = [
        "national", "international", "economy", "science_tech",
        "environment", "polity", "defence", "sports", "awards", "art_culture",
    ]
    for key in ordered_keys:
        if key not in categories:
            continue
        cat_data = categories[key]
        picked: list[dict] = []
        for art in cat_data.get("articles", []):
            norm = art.get("title", "").lower().strip()
            if norm and norm not in seen:
                seen.add(norm)
                picked.append(art)
            if len(picked) >= TOP_PER_CAT:
                break
        if picked:
            result[key] = {**cat_data, "articles": picked}

    return result


def _write_snapshot(payload: dict, date_key_str: str) -> None:
    """Serialise and write a snapshot to disk."""
    dest = HISTORY_DIR / f"{date_key_str}.json"
    important_cats = _pick_important(payload.get("categories", {}))
    total = sum(len(v.get("articles", [])) for v in important_cats.values())
    snapshot = {
        "date"          : payload.get("date", date_key_str),
        "date_key"      : date_key_str,
        "generated_at"  : payload.get("generated_at", ""),
        "archived_at"   : datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "total_articles": total,
        "categories"    : important_cats,
    }
    dest.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [History] Saved {date_key_str} → {total} important articles  ({dest.name})")


# ── Public API ───────────────────────────────────────────────────────────────

def maybe_archive(existing_payload: dict, incoming_payload: dict) -> Optional[str]:
    """
    Archive *existing_payload* as that date's history when the incoming
    payload belongs to a different calendar date.

    Call this BEFORE overwriting the cached JSON, passing the old data as
    `existing_payload` and the freshly fetched data as `incoming_payload`.

    Returns the archived date string (YYYY-MM-DD) or None if nothing was
    archived (same-day refresh or already archived).
    """
    existing_date = _date_key(existing_payload)
    incoming_date = _date_key(incoming_payload)

    if existing_date == incoming_date:
        return None  # same-day refresh — nothing to archive

    dest = HISTORY_DIR / f"{existing_date}.json"
    if dest.exists():
        return None  # already archived for that date

    _write_snapshot(existing_payload, existing_date)
    return existing_date


def today_snapshot(payload: dict) -> None:
    """
    Unconditionally save (or overwrite) today's important-news snapshot.
    Useful when you want a fresh mid-day checkpoint without changing the date.
    """
    date_key_str = _date_key(payload)
    _write_snapshot(payload, date_key_str)


def load_snapshot(date_key: str) -> Optional[dict]:
    """
    Load the historical snapshot for the given YYYY-MM-DD key.
    Returns None if that date has not been archived yet.
    """
    path = HISTORY_DIR / f"{date_key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_dates() -> list[str]:
    """
    Return all archived date keys (YYYY-MM-DD strings) sorted newest-first.
    """
    return sorted(
        (p.stem for p in HISTORY_DIR.glob("*.json")),
        reverse=True,
    )


def generate_static_pages() -> None:
    """
    Generate a static HTML page for every archived snapshot, plus an
    index.html that redirects to the most recent date.

    Intended for use in GitHub Actions / GitHub Pages deployments where
    there is no Flask server to serve /history/<date> routes dynamically.

    Output: current_affairs/news/history/<date>.html  (one per archive)
            current_affairs/news/history/index.html   (redirect → latest)
    """
    from current_affairs.history_report import build_history_html

    dates = list_dates()
    if not dates:
        print("  [History] No archived dates found — static pages skipped.")
        return

    for date_key in dates:
        snapshot = load_snapshot(date_key)
        if snapshot is None:
            continue
        html = build_history_html(snapshot, dates, static_mode=True)
        dest = HISTORY_DIR / f"{date_key}.html"
        dest.write_text(html, encoding="utf-8")
        print(f"  [History] Generated {dest.name}")

    # Index redirects to the most recent date
    latest = dates[0]
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta http-equiv="refresh" content="0;url=./{latest}.html"/>
<title>History Archive — Redirecting…</title>
<style>body{{font-family:sans-serif;text-align:center;padding:60px;background:#070c1b;color:#e8edf5}}</style>
</head>
<body>
<p>Redirecting to <a href="./{latest}.html" style="color:#818cf8">{latest}</a>…</p>
</body>
</html>"""
    (HISTORY_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  [History] Generated index.html → {latest}")
