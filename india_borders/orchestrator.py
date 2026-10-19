"""
India Borders — Orchestrator
===============================
Builds the payload from the static REGIONS registry (no live data — this
is settled public geography) and writes:
  • india_borders/borders/india_borders_data.json
  • india_borders/borders/india_borders_report.html

Usage
-----
python -m india_borders.orchestrator
python -m india_borders.orchestrator --output html
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

from india_borders.regions import REGIONS, CAPITAL_COORDS, BORDER_LENGTHS_KM, BORDER_CHECKPOINTS

BASE_DIR     = Path(__file__).parent
BORDERS_DIR  = BASE_DIR / "borders"
OUTPUT_JSON  = BORDERS_DIR / "india_borders_data.json"
OUTPUT_HTML  = BORDERS_DIR / "india_borders_report.html"

BORDERS_DIR.mkdir(exist_ok=True)


def build_payload() -> dict:
    regions_out = {
        key: {**data, "key": key, "lat": CAPITAL_COORDS[key][0], "lon": CAPITAL_COORDS[key][1]}
        for key, data in REGIONS.items()
    }

    most_borders = max(REGIONS.items(), key=lambda kv: len(kv[1]["land_neighbors"]))
    island_only = [k for k, v in REGIONS.items() if not v["land_neighbors"]]
    most_countries = max(REGIONS.items(), key=lambda kv: len(kv[1]["countries"]))
    coastal_count = sum(1 for v in REGIONS.values() if v["coastal"])

    # Full ranking, every region (not just the top one) — for the leaderboard.
    leaderboard = sorted(
        ({"key": k, "name": v["name"], "count": len(v["land_neighbors"])} for k, v in REGIONS.items()),
        key=lambda r: r["count"], reverse=True,
    )

    # Reverse index: country -> [region names that border it].
    country_groups: dict[str, list[str]] = {}
    for v in REGIONS.values():
        for country in v["countries"]:
            country_groups.setdefault(country, []).append(v["name"])
    for names in country_groups.values():
        names.sort()

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "regions"     : regions_out,
        "leaderboard" : leaderboard,
        "country_groups": country_groups,
        "border_lengths": BORDER_LENGTHS_KM,
        "border_checkpoints": BORDER_CHECKPOINTS,
        "stats": {
            "total_regions": len(REGIONS),
            "most_borders_key": most_borders[0],
            "most_borders_count": len(most_borders[1]["land_neighbors"]),
            "island_only": island_only,
            "most_countries_key": most_countries[0],
            "most_countries_count": len(most_countries[1]["countries"]),
            "coastal_count": coastal_count,
        },
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from india_borders.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="India Borders Orchestrator")
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
    print(f"[India Borders] {payload['stats']['total_regions']} states/UTs compiled.")

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
