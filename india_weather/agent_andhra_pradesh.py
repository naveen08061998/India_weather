"""
Agent 01 — Andhra Pradesh Weather
Fetches current weather and 3-day forecast for all 26 districts of Andhra Pradesh
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Andhra Pradesh"
DISTRICTS = [
    "Alluri Sitharama Raju",
    "Anakapalli",
    "Ananthapuramu",
    "Annamayya",
    "Bapatla",
    "Chittoor",
    "Dr. B.R. Ambedkar Konaseema",
    "East Godavari",
    "Eluru",
    "Guntur",
    "Kakinada",
    "Krishna",
    "Kurnool",
    "Nandyal",
    "NTR",
    "Palnadu",
    "Parvathipuram Manyam",
    "Prakasam",
    "Sri Potti Sriramulu Nellore",
    "Sri Sathya Sai",
    "Srikakulam",
    "Tirupati",
    "Visakhapatnam",
    "Vizianagaram",
    "West Godavari",
    "YSR",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
