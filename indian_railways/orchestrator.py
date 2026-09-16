"""
Indian Railways — Orchestrator
================================
Builds the full train-status payload and writes:
  • indian_railways/trains/railways_data.json    (raw data)
  • indian_railways/trains/railways_report.html  (dashboard)

Unlike the weather/news orchestrators, this one has no network calls —
statuses are computed locally from the schedule registry (see ir_client.py).

Usage
-----
python -m indian_railways.orchestrator
python -m indian_railways.orchestrator --output json
python -m indian_railways.orchestrator --output html
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from indian_railways.ir_client import get_all_statuses, get_static_statuses

BASE_DIR    = Path(__file__).parent
TRAINS_DIR  = BASE_DIR / "trains"
OUTPUT_JSON = TRAINS_DIR / "railways_data.json"
OUTPUT_HTML = TRAINS_DIR / "railways_report.html"

TRAINS_DIR.mkdir(exist_ok=True)


def build_payload() -> dict:
    now = datetime.now(IST)
    all_statuses = get_all_statuses(now)   # full scan (~1s), used only for the counts below
    return {
        "generated_at": now.strftime("%Y-%m-%d %H:%M IST"),
        "date":         now.strftime("%d %B %Y"),
        "total_trains": len(all_statuses),
        "running_now":  sum(1 for t in all_statuses if t["status"] in ("running", "at_station")),
        # Embedded set used by the dashboard's default view AND the no-backend
        # (GitHub Pages) search fallback — a size/quality-filtered ~300+ trains,
        # not just the ~56 hand-curated highlights.
        "trains":       get_static_statuses(now),
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from indian_railways.railways_report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Indian Railways Train Tracker Orchestrator")
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            print("No cached JSON found. Run without --output html first.")
            sys.exit(1)
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    print(f"\n[Indian Railways] Computing live status for all registered trains…")
    payload = build_payload()
    print(f"  {payload['total_trains']} trains  •  {payload['running_now']} currently en route")

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
