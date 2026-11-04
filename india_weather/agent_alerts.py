"""
India Weather Alerts Agent
==========================
Sources:
  1. GDACS RSS  — active tropical cyclones near India (Bay of Bengal / Arabian Sea)
  2. Rule-based — severity flags computed from the live OWM district weather data

Saves results to india_weather/weathers/india_alerts.json
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure Unicode characters don't crash on Windows cp1252 terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
WEATHER_JSON = BASE_DIR / "weathers" / "india_weather_data.json"
ALERTS_JSON  = BASE_DIR / "weathers" / "india_alerts.json"

# ── GDACS config ───────────────────────────────────────────────────────────
GDACS_RSS  = "https://www.gdacs.org/xml/rss.xml"
GDACS_NS   = "http://www.gdacs.org"
GEORSS_NS  = "http://www.georss.org/georss"

# India + surrounding ocean bounding box (Bay of Bengal + Arabian Sea + land)
# Include a wide buffer so approaching storms appear even before landfall.
LAT_MIN, LAT_MAX =  0.0,  35.0
LON_MIN, LON_MAX = 50.0, 110.0

# ── World tropical-cyclone basin classification ────────────────────────────
# Simplified/approximate bounding regions (good enough for grouping a live
# alert feed, NOT precise meteorological basin boundaries — real agency
# basin lines are irregular and vary by country/organisation). Same "state
# the approximation, don't fake precision" discipline as other curated
# datasets in this repo (e.g. india_highways' STATE_HIGHWAY_SUMMARY).
BASIN_COLORS = {
    "North Atlantic":            "#3b82f6",
    "Eastern Pacific":           "#8b5cf6",
    "Western Pacific":           "#f97316",
    "North Indian Ocean":        "#ef4444",
    "South-West Indian Ocean":   "#10b981",
    "Australian Region":         "#eab308",
    "South Pacific":             "#06b6d4",
    "Other / Unclassified":      "#94a3b8",
}


def classify_basin(lat: float | None, lon: float | None) -> str:
    """Return an approximate world tropical-cyclone basin name for a lat/lon."""
    if lat is None or lon is None:
        return "Other / Unclassified"
    if lat < 0:
        if 20 <= lon < 90:
            return "South-West Indian Ocean"
        if 90 <= lon < 160:
            return "Australian Region"
        if lon >= 160 or lon <= -120:
            return "South Pacific"
        return "Other / Unclassified"
    # Northern Hemisphere
    if 40 <= lon < 100:
        return "North Indian Ocean"
    if 100 <= lon <= 180:
        return "Western Pacific"
    if lon < -100:
        return "Eastern Pacific"
    if -100 <= lon < 40:
        return "North Atlantic"
    return "Other / Unclassified"


# ── GDACS cyclone fetch ────────────────────────────────────────────────────

def _text(el, tag: str, ns: str, default: str = "") -> str:
    node = el.find(f"{{{ns}}}{tag}")
    return node.text.strip() if node is not None and node.text else default


def fetch_gdacs_cyclones() -> list[dict]:
    """Return ALL active tropical cyclones worldwide from the GDACS RSS feed,
    each tagged with an approximate `basin` and a `near_india` flag (the
    latter preserves the original near-India-only behaviour for callers that
    still want just the Bay of Bengal / Arabian Sea region)."""
    try:
        r = requests.get(
            GDACS_RSS, timeout=15, verify=False,
            headers={"User-Agent": "IndiaWeatherAgent/1.0"},
        )
        r.raise_for_status()
    except Exception as exc:
        return [{"error": f"GDACS fetch failed: {exc}"}]

    root     = ET.fromstring(r.content)
    cyclones = []

    for item in root.findall(".//item"):
        if _text(item, "eventtype", GDACS_NS) != "TC":
            continue

        title   = item.findtext("title", "").strip()
        alevel  = _text(item, "alertlevel", GDACS_NS, "Green")
        sev     = _text(item, "severity",   GDACS_NS)
        pop     = _text(item, "population", GDACS_NS)
        link    = item.findtext("link", "").strip()
        pubdate = item.findtext("pubDate", "").strip()
        desc    = item.findtext("description", "").strip()

        # Coordinates from georss:point ("lat lon")
        lat = lon = None
        point = item.findtext(f"{{{GEORSS_NS}}}point", "").strip()
        if point:
            parts = point.split()
            if len(parts) == 2:
                try:
                    lat, lon = float(parts[0]), float(parts[1])
                except ValueError:
                    pass

        # Also try gdacs:lat / gdacs:lon
        if lat is None:
            try:
                lat = float(_text(item, "lat", GDACS_NS) or "")
                lon = float(_text(item, "lon", GDACS_NS) or "")
            except ValueError:
                lat = lon = None

        near_india = (
            lat is not None and lon is not None
            and LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX
        )

        # Extract name from title e.g. "Green notification for tropical cyclone BERTHA-26."
        name = title
        for marker in ("tropical cyclone ", "Tropical Cyclone ", "TROPICAL CYCLONE "):
            if marker in name:
                name = name.split(marker)[-1].split(".")[0].split(",")[0].strip()
                break

        cyclones.append({
            "name":       name,
            "title":      title,
            "level":      alevel,        # Green / Orange / Red
            "severity":   sev,
            "population": pop,
            "description": desc[:200],
            "lat":        lat,
            "lon":        lon,
            "basin":      classify_basin(lat, lon),
            "near_india": near_india,
            "url":        link,
            "pubDate":    pubdate,
        })

    return cyclones


# ── Rule-based district alerts ─────────────────────────────────────────────

# Each rule: (label, color_hex, emoji, condition_function)
RULES: list[tuple] = [
    ("Heat Wave",    "#ef4444", "🔥",
        lambda d: _f(d, "temperature_c") >= 40),
    ("Extreme Heat", "#f97316", "🌡",
        lambda d: 38 <= _f(d, "temperature_c") < 40),
    ("Thunderstorm", "#a855f7", "⚡",
        lambda d: "thunder" in _s(d, "description")),
    ("Heavy Rain",   "#3b82f6", "🌧",
        lambda d: "heavy" in _s(d, "description") and "rain" in _s(d, "description")),
    ("Strong Wind",  "#f59e0b", "💨",
        lambda d: _f(d, "wind_kmph") >= 50),
    ("Dense Fog",    "#94a3b8", "🌫",
        lambda d: any(k in _s(d, "description") for k in ("fog", "mist", "haze"))
                  and _f(d, "visibility_km") < 2),
]


def _f(d: dict, key: str) -> float:
    """Safely parse a float from a district data dict."""
    try:
        return float(d.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _s(d: dict, key: str) -> str:
    return (d.get(key) or "").lower()


def compute_district_alerts(weather_data: dict) -> list[dict]:
    """Scan all loaded districts and return those matching at least one alert rule."""
    alerts = []
    for state in weather_data.get("states", []):
        state_name = state.get("state", "")
        for district in state.get("districts", []):
            if "error" in district:
                continue
            for label, color, emoji, cond in RULES:
                try:
                    if cond(district):
                        alerts.append({
                            "state":    state_name,
                            "city":     district.get("city", ""),
                            "label":    label,
                            "color":    color,
                            "icon":     emoji,
                            "temp":     district.get("temperature_c", "N/A"),
                            "desc":     district.get("description", ""),
                            "wind":     district.get("wind_kmph", ""),
                            "vis":      district.get("visibility_km", ""),
                        })
                except Exception:
                    pass
    return alerts


# ── Main ───────────────────────────────────────────────────────────────────

def run() -> dict:
    """Fetch GDACS (worldwide) + compute district alerts. Save to india_alerts.json."""
    print("  [Alerts] Fetching GDACS cyclone feed (worldwide)...")
    all_cyclones   = fetch_gdacs_cyclones()
    ok_all         = [c for c in all_cyclones if "error" not in c]
    cyclones       = [c for c in all_cyclones if "error" in c or c.get("near_india")]
    global_cyclones = ok_all
    print(f"  [Alerts] Cyclones near India: {len([c for c in ok_all if c.get('near_india')])} "
          f"/ Active worldwide: {len(ok_all)}")

    district_alerts: list[dict] = []
    if WEATHER_JSON.exists():
        print("  [Alerts] Computing rule-based district alerts...")
        weather = json.loads(WEATHER_JSON.read_text(encoding="utf-8"))
        district_alerts = compute_district_alerts(weather)
        print(f"  [Alerts] District alerts triggered: {len(district_alerts)}")
    else:
        print("  [Alerts] No weather JSON found — skipping district alerts")

    result = {
        "generated_at":    datetime.now().isoformat(timespec="seconds"),
        "cyclones":        cyclones,
        "global_cyclones": global_cyclones,
        "district_alerts": district_alerts,
    }
    ALERTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    ALERTS_JSON.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  [Alerts] Saved -> {ALERTS_JSON.name}")
    return result


if __name__ == "__main__":
    import sys
    result = run()
    # Quick summary
    cycs = [c for c in result["cyclones"] if "error" not in c]
    g_cycs = [c for c in result["global_cyclones"] if "error" not in c]
    das  = result["district_alerts"]
    print(f"\nCyclones near India: {len(cycs)}")
    for c in cycs:
        print(f"  \U0001F300 {c['name']} [{c['level']}] lat={c['lat']} lon={c['lon']}")
    print(f"\nActive worldwide: {len(g_cycs)}")
    by_basin: dict[str, int] = {}
    for c in g_cycs:
        by_basin[c["basin"]] = by_basin.get(c["basin"], 0) + 1
    for k, v in sorted(by_basin.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nDistrict alerts: {len(das)}")
    by_label: dict[str, int] = {}
    for a in das:
        by_label[a["label"]] = by_label.get(a["label"], 0) + 1
    for k, v in sorted(by_label.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
