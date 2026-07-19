"""
Agent 2 — Chennai Weather
Fetches current weather and 3-day forecast for Chennai
using the wttr.in JSON API (no API key required).
"""

import requests

CITY = "Chennai"
_API_URL = f"https://wttr.in/{CITY}?format=j1"


def fetch() -> dict:
    """Return raw weather JSON for Chennai."""
    response = requests.get(_API_URL, timeout=15)
    response.raise_for_status()
    return response.json()


def get_summary() -> dict:
    """Return a simplified summary dict for Chennai."""
    data = fetch()
    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    forecast = data["weather"]

    return {
        "city": CITY,
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


if __name__ == "__main__":
    import json
    print(json.dumps(get_summary(), indent=2))
