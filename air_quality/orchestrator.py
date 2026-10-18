"""
Air Quality — Orchestrator
============================
Fetches AQI for all curated cities and writes:
  • air_quality/aqi/air_quality_data.json
  • air_quality/aqi/air_quality_report.html

Usage
-----
python -m air_quality.orchestrator
python -m air_quality.orchestrator --output json
python -m air_quality.orchestrator --output html
python -m air_quality.orchestrator --workers 12
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from air_quality.cities import CITIES
from air_quality.aqi_client import fetch_all as fetch_all_aqi

BASE_DIR    = Path(__file__).parent
AQI_DIR     = BASE_DIR / "aqi"
OUTPUT_JSON = AQI_DIR / "air_quality_data.json"
OUTPUT_HTML = AQI_DIR / "air_quality_report.html"

AQI_DIR.mkdir(exist_ok=True)


def fetch_all(workers: int = 10, verbose: bool = False) -> dict:
    print(f"\n[Air Quality] Fetching {len(CITIES)} cities with {workers} workers…")
    start = time.time()
    readings = fetch_all_aqi(CITIES, workers=workers)
    elapsed = time.time() - start

    cities_out = []
    ok_count = 0
    for c in CITIES:
        r = readings.get(c["name"], {"error": "missing"})
        cities_out.append({**c, "reading": r})
        if "error" not in r:
            ok_count += 1
            if verbose:
                print(f"  ✓ {c['name']:<20} AQI {r['us_aqi']:.0f} ({r['label']})")
        else:
            print(f"  ⚠ {c['name']:<20} {r['error']}", file=sys.stderr)

    print(f"  {ok_count}/{len(CITIES)} cities OK in {elapsed:.1f}s")

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "cities"      : cities_out,
        "elapsed_s"   : round(elapsed, 1),
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from air_quality.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="India Air Quality Orchestrator")
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            print("No cached JSON found. Run without --output html first.")
            sys.exit(1)
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = fetch_all(workers=args.workers, verbose=args.verbose)

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
