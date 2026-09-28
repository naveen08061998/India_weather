"""
Agent 31 — Dadra and Nagar Haveli and Daman and Diu Weather
Fetches current weather and 3-day forecast for all 3 districts of
Dadra and Nagar Haveli and Daman and Diu using the wttr.in JSON API
(no API key required).
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Dadra and Nagar Haveli and Daman and Diu"
DISTRICTS = [
    "Dadra and Nagar Haveli",
    "Daman",
    "Diu",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
