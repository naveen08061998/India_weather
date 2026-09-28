"""
Agent 29 — Andaman and Nicobar Islands Weather
Fetches current weather and 3-day forecast for all 3 districts of
Andaman and Nicobar Islands using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Andaman and Nicobar Islands"
DISTRICTS = [
    "Nicobars",
    "North and Middle Andaman",
    "South Andaman",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
