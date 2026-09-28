"""
Agent 35 — Lakshadweep Weather
Fetches current weather and 3-day forecast for Lakshadweep
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Lakshadweep"
DISTRICTS = [
    "Kavaratti",
    "Agatti",
    "Minicoy",
    "Amini",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
