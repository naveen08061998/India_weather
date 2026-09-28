"""
Agent 20 — Punjab Weather
Fetches current weather and 3-day forecast for all 23 districts of Punjab
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Punjab"
DISTRICTS = [
    "Amritsar",
    "Barnala",
    "Bathinda",
    "Faridkot",
    "Fatehgarh Sahib",
    "Fazilka",
    "Ferozepur",
    "Gurdaspur",
    "Hoshiarpur",
    "Jalandhar",
    "Kapurthala",
    "Ludhiana",
    "Malerkotla",
    "Mansa",
    "Moga",
    "Pathankot",
    "Patiala",
    "Rupnagar",
    "S.A.S. Nagar",
    "Sangrur",
    "Shahid Bhagat Singh Nagar",
    "Sri Muktsar Sahib",
    "Tarn Taran",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
