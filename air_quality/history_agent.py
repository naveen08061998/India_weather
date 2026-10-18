"""
Air Quality — History Agent
==============================
Archives a compact daily snapshot (city -> AQI value) so the dashboard can
show a short trend sparkline per city. Much lighter than current_affairs'
history_agent.py (just numbers, not full article payloads) since AQI only
needs one data point per city per day.

Storage layout
--------------
    air_quality/aqi/history/
        2026-07-29.json   ← {"date_key": "...", "cities": {"Delhi": 151, ...}}
        2026-07-28.json
        …

Public API
----------
    archive_today(payload)        → saves today's city->AQI map (idempotent)
    load_trend(city_name, days=14) → [(date_key, aqi), ...] oldest-first
    list_dates()                   → all archived dates, newest-first
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

BASE_DIR    = Path(__file__).parent
AQI_DIR     = BASE_DIR / "aqi"
HISTORY_DIR = AQI_DIR / "history"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)

MAX_DAYS_KEPT = 30   # prune anything older than this


def _today_key() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


def archive_today(payload: dict) -> str:
    """
    Save today's city->AQI snapshot (overwrites if already archived today,
    so repeated same-day runs just refresh the latest value). Also prunes
    snapshots older than MAX_DAYS_KEPT days. Returns the date key saved.
    """
    date_key = _today_key()
    cities_aqi = {
        c["name"]: c["reading"]["us_aqi"]
        for c in payload.get("cities", [])
        if "error" not in c.get("reading", {}) and c["reading"].get("us_aqi") is not None
    }
    snapshot = {
        "date_key": date_key,
        "archived_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "cities": cities_aqi,
    }
    (HISTORY_DIR / f"{date_key}.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    all_dates = sorted(p.stem for p in HISTORY_DIR.glob("*.json"))
    for stale in all_dates[:-MAX_DAYS_KEPT]:
        (HISTORY_DIR / f"{stale}.json").unlink(missing_ok=True)

    return date_key


def list_dates() -> list[str]:
    """All archived dates, newest-first."""
    return sorted((p.stem for p in HISTORY_DIR.glob("*.json")), reverse=True)


def load_trend(city_name: str, days: int = 14) -> list[tuple[str, float]]:
    """Return up to `days` (date_key, aqi) points for one city, oldest-first."""
    points: list[tuple[str, float]] = []
    for date_key in sorted(list_dates())[-days:]:
        try:
            data = json.loads((HISTORY_DIR / f"{date_key}.json").read_text(encoding="utf-8"))
            aqi = data.get("cities", {}).get(city_name)
            if aqi is not None:
                points.append((date_key, aqi))
        except Exception:
            continue
    return points


def load_all_trends(city_names: list[str], days: int = 14) -> dict[str, list[tuple[str, float]]]:
    """Load trends for multiple cities at once (reads each history file only once)."""
    dates = sorted(list_dates())[-days:]
    trends: dict[str, list[tuple[str, float]]] = {name: [] for name in city_names}
    for date_key in dates:
        try:
            data = json.loads((HISTORY_DIR / f"{date_key}.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        cities_aqi = data.get("cities", {})
        for name in city_names:
            aqi = cities_aqi.get(name)
            if aqi is not None:
                trends[name].append((date_key, aqi))
    return trends
