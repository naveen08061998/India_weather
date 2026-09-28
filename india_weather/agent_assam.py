"""
Agent 03 — Assam Weather
Fetches current weather and 3-day forecast for all 35 districts of Assam
using the OpenWeatherMap API.
"""

from india_weather.owm_client import fetch_all as _fetch_all

STATE = "Assam"
DISTRICTS = [
    "Bajali",
    "Baksa",
    "Barpeta",
    "Biswanath",
    "Bongaigaon",
    "Cachar",
    "Charaideo",
    "Chirang",
    "Darrang",
    "Dhemaji",
    "Dhubri",
    "Dibrugarh",
    "Dima Hasao",
    "Goalpara",
    "Golaghat",
    "Hailakandi",
    "Hojai",
    "Jorhat",
    "Kamrup",
    "Kamrup Metropolitan",
    "Karbi Anglong",
    "Kokrajhar",
    "Lakhimpur",
    "Majuli",
    "Marigaon",
    "Morigaon",
    "Nagaon",
    "Nalbari",
    "Sivasagar",
    "Sonitpur",
    "South Salmara-Mankachar",
    "Tamulpur",
    "Tinsukia",
    "Udalguri",
    "West Karbi Anglong",
]


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts (parallel)."""
    return _fetch_all(DISTRICTS, STATE)


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
