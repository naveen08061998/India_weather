"""
Air Quality — Open-Meteo Client
===================================
Fully free, no API key. Uses Open-Meteo's Air Quality API:
    https://air-quality-api.open-meteo.com/v1/air-quality

Classifies readings on the US EPA AQI scale (0-500) since Open-Meteo
returns `us_aqi` directly (no conversion needed).
"""

from __future__ import annotations

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
_TIMEOUT = 20
_MAX_RETRIES = 4
_RETRY_BACKOFF_S = 3

# ── US EPA AQI bands ────────────────────────────────────────────────────────
_BANDS = [
    (50,  "Good",                             "#22c55e"),
    (100, "Moderate",                         "#eab308"),
    (150, "Unhealthy for Sensitive Groups",   "#f97316"),
    (200, "Unhealthy",                        "#ef4444"),
    (300, "Very Unhealthy",                   "#a855f7"),
    (500, "Hazardous",                        "#7f1d1d"),
]


def classify_aqi(us_aqi: float | None) -> tuple[str, str]:
    """Return (label, color_hex) for a US AQI value."""
    if us_aqi is None:
        return "Unknown", "#64748b"
    for threshold, label, color in _BANDS:
        if us_aqi <= threshold:
            return label, color
    return "Hazardous", "#7f1d1d"


def fetch_city_aqi(city: dict) -> dict:
    """
    Fetch current air quality for a single city dict ({name, state, lat, lon}).
    Retries a few times with backoff — free-tier Open-Meteo calls occasionally
    time out or get rate-limited under CI's shared/bursty network conditions.
    """
    last_error: str = "unknown error"
    for attempt in range(_MAX_RETRIES):
        try:
            resp = requests.get(
                _AQI_URL, timeout=_TIMEOUT,
                params={
                    "latitude": city["lat"], "longitude": city["lon"],
                    "current": "us_aqi,pm2_5,pm10,european_aqi,ozone,"
                               "nitrogen_dioxide,carbon_monoxide,sulphur_dioxide",
                    "timezone": "Asia/Kolkata",
                },
            )
            resp.raise_for_status()
            cur = resp.json().get("current", {})
            us_aqi = cur.get("us_aqi")
            label, color = classify_aqi(us_aqi)
            return {
                "us_aqi": us_aqi,
                "european_aqi": cur.get("european_aqi"),
                "pm2_5": cur.get("pm2_5"),
                "pm10": cur.get("pm10"),
                "ozone": cur.get("ozone"),
                "no2": cur.get("nitrogen_dioxide"),
                "co": cur.get("carbon_monoxide"),
                "so2": cur.get("sulphur_dioxide"),
                "label": label,
                "color": color,
                "fetched_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
            }
        except Exception as exc:
            last_error = str(exc)
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BACKOFF_S * (attempt + 1))
    return {"error": last_error}


def fetch_all(cities: list[dict], workers: int = 6) -> dict[str, dict]:
    """
    Fetch AQI for all cities concurrently. Returns {city_name: reading}.
    Any city still failing after the concurrent batch (e.g. a request that
    exhausted its retries while the network was especially busy) gets one
    more sequential, low-concurrency attempt — isolating it from whatever
    caused the original burst of failures.
    """
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(fetch_city_aqi, c): c["name"] for c in cities}
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = {"error": str(exc)}

    failed = [c for c in cities if "error" in results.get(c["name"], {})]
    if failed:
        time.sleep(5)   # let any upstream congestion clear before retrying
        for city in failed:
            results[city["name"]] = fetch_city_aqi(city)

    return results
