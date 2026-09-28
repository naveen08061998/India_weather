"""
Agent 30 — Chandigarh Weather
Fetches current weather and 3-day forecast for all 1 district of Chandigarh
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Chandigarh"
DISTRICTS = [
    "Chandigarh",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
