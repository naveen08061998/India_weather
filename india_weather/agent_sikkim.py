"""
Agent 22 — Sikkim Weather
Fetches current weather and 3-day forecast for all 6 districts of Sikkim
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Sikkim"
DISTRICTS = [
    "East Sikkim",
    "North Sikkim",
    "Pakyong",
    "Soreng",
    "South Sikkim",
    "West Sikkim",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
