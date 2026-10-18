"""
Government Updates — Orchestrator
===================================
Fetches PIB releases (bucketed into schemes/exam news) + the static exam
calendar, and writes:
  • gov_updates/updates/gov_updates_data.json
  • gov_updates/updates/gov_updates_report.html

Usage
-----
python -m gov_updates.orchestrator
python -m gov_updates.orchestrator --output json
python -m gov_updates.orchestrator --output html
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from gov_updates.sources import EXAM_CALENDAR
from gov_updates.fetcher import fetch_categorised

BASE_DIR    = Path(__file__).parent
UPDATES_DIR = BASE_DIR / "updates"
OUTPUT_JSON = UPDATES_DIR / "gov_updates_data.json"
OUTPUT_HTML = UPDATES_DIR / "gov_updates_report.html"

UPDATES_DIR.mkdir(exist_ok=True)


def fetch_all(verbose: bool = False) -> dict:
    print("\n[Gov Updates] Fetching news feeds…")
    cat = fetch_categorised()
    print(f"  ✓ {cat['all_count']} total articles fetched; "
          f"{len(cat['schemes'])} scheme-tagged, {len(cat['exams'])} exam-tagged")
    if verbose:
        for a in cat["schemes"][:5]:
            print(f"      [scheme] {a['title'][:80]}")
        for a in cat["exams"][:5]:
            print(f"      [exam]   {a['title'][:80]}")

    return {
        "generated_at" : datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"         : datetime.now(IST).strftime("%d %B %Y"),
        "schemes"      : cat["schemes"],
        "exams_news"   : cat["exams"],
        "exam_calendar": EXAM_CALENDAR,
        "total_fetched": cat["all_count"],
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from gov_updates.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Government Updates Orchestrator")
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            print("No cached JSON found. Run without --output html first.")
            sys.exit(1)
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = fetch_all(verbose=args.verbose)

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
