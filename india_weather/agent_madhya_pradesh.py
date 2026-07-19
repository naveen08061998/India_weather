"""
Agent 13 — Madhya Pradesh Weather
Fetches current weather and 3-day forecast for all 55 districts of Madhya Pradesh
using the wttr.in JSON API (no API key required).
"""

import requests

STATE = "Madhya Pradesh"
DISTRICTS = [
    "Agar-Malwa",
    "Alirajpur",
    "Anuppur",
    "Ashoknagar",
    "Balaghat",
    "Barwani",
    "Betul",
    "Bhind",
    "Bhopal",
    "Burhanpur",
    "Chhatarpur",
    "Chhindwara",
    "Damoh",
    "Datia",
    "Dewas",
    "Dhar",
    "Dindori",
    "Guna",
    "Gwalior",
    "Harda",
    "Indore",
    "Jabalpur",
    "Jhabua",
    "Katni",
    "Khandwa",
    "Khargone",
    "Maihar",
    "Mandla",
    "Mandsaur",
    "Mauganj",
    "Morena",
    "Nagda",
    "Narsinghpur",
    "Niwari",
    "Panna",
    "Pandhurna",
    "Raisen",
    "Rajgarh",
    "Ratlam",
    "Rewa",
    "Sagar",
    "Satna",
    "Sehore",
    "Seoni",
    "Shahdol",
    "Shajapur",
    "Sheopur",
    "Shivpuri",
    "Sidhi",
    "Singrauli",
    "Tikamgarh",
    "Ujjain",
    "Umaria",
    "Vidisha",
    "Chachaura",
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
