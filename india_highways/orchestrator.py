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

from india_highways.highways import (
    NATIONAL_HIGHWAYS, STATE_HIGHWAY_SUMMARY, ROAD_NETWORK_STATS,
    EXPRESSWAYS, CORRIDOR_MAP, CORRIDOR_NOTES, RENUMBERING,
    CITY_COORDS, HIGHWAY_ENDPOINTS, HIGHWAY_VIA,
)

BASE_DIR     = Path(__file__).parent
NETWORK_DIR  = BASE_DIR / "network"
OUTPUT_JSON  = NETWORK_DIR / "india_highways_data.json"
OUTPUT_HTML  = NETWORK_DIR / "india_highways_report.html"

NETWORK_DIR.mkdir(exist_ok=True)


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    from math import radians, sin, cos, asin, sqrt
    lat1, lon1, lat2, lon2 = radians(a[0]), radians(a[1]), radians(b[0]), radians(b[1])
    d_lat, d_lon = lat2 - lat1, lon2 - lon1
    h = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return round(2 * 6371 * asin(sqrt(h)), 1)


def build_payload() -> dict:
    current = [h for h in NATIONAL_HIGHWAYS if h["status"] == "current"]
    historic = [h for h in NATIONAL_HIGHWAYS if h["status"] == "historic"]
    longest = max(current, key=lambda h: h["length_km"])
    shortest = min(current, key=lambda h: h["length_km"])

    # Merge endpoint coordinates + corridor tag + straight-line detour factor into each highway record.
    highways_out = []
    for h in NATIONAL_HIGHWAYS:
        out = dict(h)
        ends = HIGHWAY_ENDPOINTS.get(h["number"])
        if ends:
            out["start_city"], out["end_city"] = ends
            out["start_coords"] = CITY_COORDS[ends[0]]
            out["end_coords"] = CITY_COORDS[ends[1]]
            straight_km = _haversine_km(out["start_coords"], out["end_coords"])
            out["straight_line_km"] = round(straight_km)
            out["detour_factor"] = round(h["length_km"] / straight_km, 2) if straight_km else None
        out["corridor"] = CORRIDOR_MAP.get(h["number"])
        out["via"] = HIGHWAY_VIA.get(h["number"], [])
        out["via_coords"] = [CITY_COORDS[c] for c in out["via"]]
        highways_out.append(out)

    # State -> list of current highway numbers passing through it.
    state_index: dict[str, list[str]] = {}
    for h in current:
        for state in h["states"]:
            state_index.setdefault(state, []).append(h["number"])
    state_leaderboard = sorted(
        ({"state": s, "count": len(nums)} for s, nums in state_index.items()),
        key=lambda r: r["count"], reverse=True,
    )

    # Named-corridor grouping (current highways only).
    corridor_groups: dict[str, list[str]] = {}
    for h in current:
        corridor = CORRIDOR_MAP.get(h["number"])
        if corridor:
            corridor_groups.setdefault(corridor, []).append(h["number"])

    length_leaderboard = sorted(
        ({"number": h["number"], "route": h["route"], "length_km": h["length_km"]} for h in current),
        key=lambda r: r["length_km"], reverse=True,
    )

    # Total published length per named corridor (current highways only).
    corridor_totals = {
        name: sum(h["length_km"] for h in current if h["number"] in members)
        for name, members in corridor_groups.items()
    }

    # Expressway state -> list of expressway names (reverse index, same idea as state_index).
    expwy_state_index: dict[str, list[str]] = {}
    for e in EXPRESSWAYS:
        for state in e["states"]:
            expwy_state_index.setdefault(state, []).append(e["name"])
    expwy_state_leaderboard = sorted(
        ({"state": s, "count": len(names)} for s, names in expwy_state_index.items()),
        key=lambda r: r["count"], reverse=True,
    )

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "national_highways": highways_out,
        "state_highway_summary": STATE_HIGHWAY_SUMMARY,
        "road_network_stats": ROAD_NETWORK_STATS,
        "expressways": EXPRESSWAYS,
        "corridor_groups": corridor_groups,
        "corridor_notes": CORRIDOR_NOTES,
        "corridor_totals": corridor_totals,
        "renumbering": RENUMBERING,
        "state_index": state_index,
        "state_leaderboard": state_leaderboard,
        "length_leaderboard": length_leaderboard,
        "expwy_state_index": expwy_state_index,
        "expwy_state_leaderboard": expwy_state_leaderboard,
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
