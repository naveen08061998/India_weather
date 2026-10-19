"""
India Highways — Orchestrator
================================
Builds the payload from the static highways registry (no live data — this
is settled/published MoRTH & NHAI reference data) and writes:
  • india_highways/network/india_highways_data.json
  • india_highways/network/india_highways_report.html

Usage
-----
python -m india_highways.orchestrator
python -m india_highways.orchestrator --output html
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

from india_highways.highways import NATIONAL_HIGHWAYS, STATE_HIGHWAY_SUMMARY, ROAD_NETWORK_STATS

BASE_DIR     = Path(__file__).parent
NETWORK_DIR  = BASE_DIR / "network"
OUTPUT_JSON  = NETWORK_DIR / "india_highways_data.json"
OUTPUT_HTML  = NETWORK_DIR / "india_highways_report.html"

NETWORK_DIR.mkdir(exist_ok=True)


def build_payload() -> dict:
    current = [h for h in NATIONAL_HIGHWAYS if h["status"] == "current"]
    historic = [h for h in NATIONAL_HIGHWAYS if h["status"] == "historic"]
    longest = max(current, key=lambda h: h["length_km"])
    shortest = min(current, key=lambda h: h["length_km"])

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "national_highways": NATIONAL_HIGHWAYS,
        "state_highway_summary": STATE_HIGHWAY_SUMMARY,
        "road_network_stats": ROAD_NETWORK_STATS,
        "stats": {
            "current_count": len(current),
            "historic_count": len(historic),
            "longest": {"number": longest["number"], "length_km": longest["length_km"], "route": longest["route"]},
            "shortest": {"number": shortest["number"], "length_km": shortest["length_km"], "route": shortest["route"]},
            "total_current_km": sum(h["length_km"] for h in current),
        },
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from india_highways.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="India Highways Orchestrator")
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
    print(f"[India Highways] {payload['stats']['current_count']} current + "
          f"{payload['stats']['historic_count']} historic highways compiled.")

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
