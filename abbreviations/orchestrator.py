"""
Abbreviations — Orchestrator
===============================
Builds the payload from the static ABBREVIATIONS registry (no live
data — this is a curated general-knowledge reference) and writes:
  • abbreviations/lexicon/abbreviations_data.json
  • abbreviations/lexicon/abbreviations_report.html

Usage
-----
python -m abbreviations.orchestrator
python -m abbreviations.orchestrator --output html
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from abbreviations.data import ABBREVIATIONS, CATEGORIES

BASE_DIR     = Path(__file__).parent
LEXICON_DIR  = BASE_DIR / "lexicon"
OUTPUT_JSON  = LEXICON_DIR / "abbreviations_data.json"
OUTPUT_HTML  = LEXICON_DIR / "abbreviations_report.html"

LEXICON_DIR.mkdir(exist_ok=True)


def build_payload() -> dict:
    entries = sorted(ABBREVIATIONS, key=lambda e: e["abbr"].upper())

    category_counts: dict[str, int] = {c: 0 for c in CATEGORIES}
    for e in entries:
        category_counts[e["category"]] = category_counts.get(e["category"], 0) + 1

    az_index: dict[str, int] = {}
    for e in entries:
        letter = e["abbr"][0].upper()
        az_index[letter] = az_index.get(letter, 0) + 1

    # Deterministic "today's" pick — same all day, changes daily, no cron needed.
    day_of_year = datetime.now(IST).timetuple().tm_yday
    featured = entries[day_of_year % len(entries)]

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "entries"     : entries,
        "categories"  : CATEGORIES,
        "category_counts": category_counts,
        "az_index"    : az_index,
        "featured"    : featured,
        "stats": {
            "total": len(entries),
            "total_categories": len(CATEGORIES),
        },
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from abbreviations.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Abbreviations Orchestrator")
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            payload = build_payload()
            save_json(payload)
        else:
            payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = build_payload()
    print(f"[Abbreviations] {payload['stats']['total']} entries across {payload['stats']['total_categories']} categories compiled.")

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
