"""
Air Quality — Open-Meteo Client
===================================
Fully free, no API key. Uses Open-Meteo's Air Quality API:
    https://air-quality-api.open-meteo.com/v1/air-quality

Classifies readings on the US EPA AQI scale (0-500) since Open-Meteo
returns `us_aqi` directly (no conversion needed). A single request per
city also pulls a 5-day hourly `us_aqi` forecast (Open-Meteo's own model
only returns reliable values for ~5 of the 7 days it accepts), aggregated
here into one peak-AQI figure per calendar day.
"""

from __future__ import annotations

import time
import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
_TIMEOUT = 20
_MAX_RETRIES = 4
_RETRY_BACKOFF_S = 3
_FORECAST_DAYS = 5

# ── US EPA AQI bands ────────────────────────────────────────────────────────
_BANDS = [
    (50,  "Good",                             "#22c55e"),
    (100, "Moderate",                         "#eab308"),
    (150, "Unhealthy for Sensitive Groups",   "#f97316"),
    (200, "Unhealthy",                        "#ef4444"),
    (300, "Very Unhealthy",                   "#a855f7"),
    (500, "Hazardous",                        "#7f1d1d"),
]

# ── Short, actionable health guidance per band (simplified public-health
# messaging in the style used by AirNow/CPCB, not an official quote) ───────
HEALTH_ADVISORY = {
    "Good": "Air quality is satisfactory. Enjoy normal outdoor activities.",
    "Moderate": "Acceptable air quality. Unusually sensitive people should "
                "consider limiting prolonged outdoor exertion.",
    "Unhealthy for Sensitive Groups": "Children, the elderly, and people with "
                "asthma/heart or lung disease should reduce prolonged outdoor exertion.",
    "Unhealthy": "Everyone may begin to experience health effects. Sensitive "
                "groups should avoid prolonged outdoor exertion; consider a mask outdoors.",
    "Very Unhealthy": "Health alert: everyone should avoid prolonged outdoor "
                "exertion. Sensitive groups should stay indoors.",
    "Hazardous": "Health emergency: everyone should avoid all outdoor physical "
                "activity and stay indoors with windows closed.",
    "Unknown": "No current reading available for this location.",
}

# Rough 24h/8h reference guideline concentrations (µg/m³) used only to rank
# which pollutant is proportionally most elevated — a simplified heuristic,
# NOT an official EPA per-pollutant sub-index calculation.
_POLLUTANT_GUIDELINES = {
    "pm2_5": ("PM2.5", 15),
    "pm10":  ("PM10", 45),
    "ozone": ("Ozone", 100),
    "no2":   ("NO₂", 25),
    "so2":   ("SO₂", 40),
    "co":    ("CO", 4000),
}


def classify_aqi(us_aqi: float | None) -> tuple[str, str]:
    """Return (label, color_hex) for a US AQI value."""
    if us_aqi is None:
        return "Unknown", "#64748b"
    for threshold, label, color in _BANDS:
        if us_aqi <= threshold:
            return label, color
    return "Hazardous", "#7f1d1d"


def dominant_pollutant(reading: dict) -> str | None:
    """
    Best-effort guess at which pollutant is driving the AQI, by ranking each
    measured concentration against a reference guideline value. Returns a
    display name (e.g. "PM2.5") or None if no pollutant data is available.
    """
    best_name, best_ratio = None, 0.0
    for key, (display, guideline) in _POLLUTANT_GUIDELINES.items():
        value = reading.get(key)
        if value is None:
            continue
        ratio = value / guideline
        if ratio > best_ratio:
            best_ratio, best_name = ratio, display
    return best_name


def _aggregate_daily_forecast(hourly_time: list[str], hourly_aqi: list[float | None]) -> list[dict]:
    """Group hourly us_aqi values by calendar date and keep the daily peak."""
    by_date: dict[str, list[float]] = defaultdict(list)
    for ts, val in zip(hourly_time, hourly_aqi):
        if val is None:
            continue
        by_date[ts.split("T")[0]].append(val)

    forecast = []
    for date_key in sorted(by_date):
        values = by_date[date_key]
        # Skip days with too few valid hours to be a meaningful daily peak
        # (Open-Meteo's AQI model horizon is shorter than its weather horizon).
        if len(values) < 12:
            continue
        peak = max(values)
        label, color = classify_aqi(peak)
        forecast.append({
            "date": date_key,
            "day": datetime.strptime(date_key, "%Y-%m-%d").strftime("%a"),
            "peak_aqi": round(peak),
            "label": label,
            "color": color,
        })
    return forecast[:_FORECAST_DAYS]


def fetch_city_aqi(city: dict) -> dict:
    """
    Fetch current + 5-day forecast air quality for a single city dict
    ({name, state, lat, lon}) in one request. Retries a few times with
    backoff — free-tier Open-Meteo calls occasionally time out or get
    rate-limited under CI's shared/bursty network conditions.
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
                    "hourly": "us_aqi",
                    "forecast_days": _FORECAST_DAYS + 2,   # pad; trailing days are often null
                    "timezone": "Asia/Kolkata",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            cur = data.get("current", {})
            us_aqi = cur.get("us_aqi")
            label, color = classify_aqi(us_aqi)
            reading = {
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
            reading["advisory"] = HEALTH_ADVISORY.get(label, HEALTH_ADVISORY["Unknown"])
            reading["dominant_pollutant"] = dominant_pollutant(reading)
            hourly = data.get("hourly", {})
            reading["forecast"] = _aggregate_daily_forecast(
                hourly.get("time", []), hourly.get("us_aqi", [])
            )
            return reading
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
