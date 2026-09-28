"""
Agent 36 — Puducherry Weather
Fetches current weather and 3-day forecast for all 4 regions/districts of
Puducherry using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Puducherry"
DISTRICTS = [
    "Karaikal",
    "Mahe",
    "Puducherry",
    "Yanam",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
