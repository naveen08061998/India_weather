"""
Agent 21 — Rajasthan Weather
Fetches current weather and 3-day forecast for all 50 districts of Rajasthan
using the wttr.in JSON API (no API key required).
"""

import requests

STATE = "Rajasthan"
DISTRICTS = [
    "Ajmer",
    "Alwar",
    "Anupgarh",
    "Balotra",
    "Banswara",
    "Baran",
    "Barmer",
    "Beawar",
    "Bharatpur",
    "Bhilwara",
    "Bikaner",
    "Bundi",
    "Chittorgarh",
    "Churu",
    "Dausa",
    "Deeg",
    "Dholpur",
    "Didwana-Kuchaman",
    "Dudu",
    "Dungarpur",
    "Gangapur City",
    "Hanumangarh",
    "Jaipur",
    "Jaipur Rural",
    "Jaisalmer",
    "Jalore",
    "Jhalawar",
    "Jhunjhunu",
    "Jodhpur",
    "Jodhpur Rural",
    "Karauli",
    "Kekri",
    "Khairthal-Tijara",
    "Kota",
    "Kotputli-Behror",
    "Nagaur",
    "Neem Ka Thana",
    "Pali",
    "Phalodi",
    "Pratapgarh",
    "Rajsamand",
    "Salumbar",
    "Sanchore",
    "Sawai Madhopur",
    "Shahpura",
    "Sikar",
    "Sirohi",
    "Sri Ganganagar",
    "Tonk",
    "Udaipur",
]


def fetch(city: str) -> dict:
    """Return raw weather JSON for a city."""
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def get_summary(city: str) -> dict:
    """Return a simplified summary dict for a city."""
    data = fetch(city)
    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    forecast = data["weather"]
    return {
        "city": city,
        "state": STATE,
        "region": area["region"][0]["value"],
        "country": area["country"][0]["value"],
        "temperature_c": current["temp_C"],
        "feels_like_c": current["FeelsLikeC"],
        "humidity": current["humidity"],
        "description": current["weatherDesc"][0]["value"],
        "wind_kmph": current["windspeedKmph"],
        "wind_dir": current["winddir16Point"],
        "visibility_km": current["visibility"],
        "pressure_mb": current["pressure"],
        "uv_index": current["uvIndex"],
        "cloud_cover": current["cloudcover"],
        "observation_time": current.get("localObsDateTime") or current.get("observation_time", "N/A"),
        "forecast": [
            {
                "date": day["date"],
                "max_c": day["maxtempC"],
                "min_c": day["mintempC"],
                "description": day["hourly"][4]["weatherDesc"][0]["value"],
            }
            for day in forecast
        ],
    }


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts."""
    results = []
    for city in DISTRICTS:
        try:
            results.append(get_summary(city))
        except Exception as exc:
            results.append({"city": city, "state": STATE, "error": str(exc)})
    return results


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
