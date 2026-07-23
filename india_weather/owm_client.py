"""
Open-Meteo Weather Client
=========================
Fully replaces the OpenWeatherMap client.
Uses only Open-Meteo APIs — completely free, no API key, no rate limits.

  Geocoding : https://geocoding-api.open-meteo.com/v1/search
  Forecast  : https://api.open-meteo.com/v1/forecast
              (current + 7-day daily + 3-hourly)

Update cadence: ~15 minutes for current conditions.
Output schema is identical to the old OWM-based client.
"""

from __future__ import annotations

import json
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Base URLs ──────────────────────────────────────────────────────────────
_GEO_BASE  = "https://geocoding-api.open-meteo.com/v1"
_WTHR_BASE = "https://api.open-meteo.com/v1"

# ── Paths ──────────────────────────────────────────────────────────────────
_BASE_DIR       = Path(__file__).parent
_GEO_CACHE_FILE = _BASE_DIR / "weathers" / "geo_cache.json"

# ── Timezone ───────────────────────────────────────────────────────────────
_IST = timezone(timedelta(hours=5, minutes=30))

# ── Geocoding coordinate cache (persisted to disk) ────────────────────────
_geo_cache: dict[str, dict] = {}


def _load_geo_cache() -> None:
    global _geo_cache
    if _GEO_CACHE_FILE.exists():
        try:
            _geo_cache = json.loads(_GEO_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            _geo_cache = {}


def _save_geo_cache() -> None:
    try:
        _GEO_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _GEO_CACHE_FILE.write_text(
            json.dumps(_geo_cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass


_load_geo_cache()

# ── District name fallbacks ────────────────────────────────────────────────
_FALLBACKS: dict[str, str] = {
    "Nicobars": "Port Blair", "North and Middle Andaman": "Port Blair",
    "South Andaman": "Port Blair",
    "Alluri Sitharama Raju": "Rajahmundry", "Anakapalli": "Visakhapatnam",
    "Ananthapuramu": "Anantapur", "Annamayya": "Tirupati",
    "Dr. B.R. Ambedkar Konaseema": "Amalapuram", "East Godavari": "Rajahmundry",
    "NTR": "Vijayawada", "Palnadu": "Guntur",
    "Parvathipuram Manyam": "Vizianagaram", "Prakasam": "Ongole",
    "Sri Potti Sriramulu Nellore": "Nellore", "Sri Sathya Sai": "Kadapa",
    "West Godavari": "Eluru", "YSR": "Kadapa",
    "Anjaw": "Dibrugarh", "Bichom": "Tezpur", "Dibang Valley": "Itanagar",
    "East Kameng": "Tezpur", "East Siang": "Itanagar", "Kamle": "Itanagar",
    "Kra Daadi": "Itanagar", "Kurung Kumey": "Itanagar",
    "Lepa Rada": "Itanagar", "Lohit": "Dibrugarh", "Longding": "Itanagar",
    "Lower Dibang Valley": "Itanagar", "Lower Siang": "Itanagar",
    "Lower Subansiri": "Itanagar", "Pakke-Kessang": "Itanagar",
    "Papum Pare": "Itanagar", "Shi Yomi": "Itanagar", "Siang": "Itanagar",
    "Upper Siang": "Itanagar", "Upper Subansiri": "Itanagar",
    "West Kameng": "Tezpur", "West Siang": "Itanagar",
    "Bajali": "Barpeta", "Baksa": "Guwahati", "Biswanath": "Tezpur",
    "Cachar": "Silchar", "Charaideo": "Sibsagar", "Chirang": "Bongaigaon",
    "Darrang": "Mangaldai", "Dima Hasao": "Haflong", "Kamrup": "Guwahati",
    "Kamrup Metropolitan": "Guwahati", "Karbi Anglong": "Diphu",
    "Majuli": "Jorhat", "Sivasagar": "Sibsagar", "Sonitpur": "Tezpur",
    "South Salmara-Mankachar": "Dhubri", "West Karbi Anglong": "Diphu",
    "Kaimur": "Sasaram", "Lakhisarai": "Munger", "Nalanda": "Bihar Sharif",
    "Pashchim Champaran": "Bettiah", "Purbi Champaran": "Motihari",
    "Saran": "Chapra",
    "Balodabazar-Bhatapara": "Raipur", "Balrampur-Ramanujganj": "Ambikapur",
    "Bastar": "Jagdalpur", "Dakshin Bastar Dantewada": "Jagdalpur",
    "Gariyaband": "Raipur", "Gaurela-Pendra-Marwahi": "Bilaspur",
    "Janjgir-Champa": "Bilaspur", "Jashpur": "Ambikapur",
    "Kabirdham": "Durg",
    "Khairagarh-Chhindgarh-Gandai": "Durg", "Korea": "Ambikapur",
    "Manendragarh-Chirmiri-Bharatpur": "Ambikapur", "Mohla": "Durg",
    "Rajnandgaon": "Durg",
    "Sarangarh-Bilaigarh": "Raigarh", "Surguja": "Ambikapur",
    "Central Delhi": "Delhi", "East Delhi": "Delhi", "North Delhi": "Delhi",
    "North East Delhi": "Delhi", "North West Delhi": "Delhi",
    "South Delhi": "Delhi", "South East Delhi": "Delhi",
    "South West Delhi": "Delhi", "West Delhi": "Delhi",
    "North Goa": "Panaji", "South Goa": "Panaji",
    "Arvalli": "Gandhinagar", "Banas Kantha": "Palanpur",
    "Dangs": "Surat", "Devbhumi Dwarka": "Jamnagar",
    "Gir Somnath": "Junagadh", "Kachchh": "Bhuj", "Mahisagar": "Vadodara",
    "Narmada": "Vadodara", "Panch Mahals": "Godhra",
    "Sabarkantha": "Idar", "Tapi": "Surat",
    "Kinnaur": "Shimla", "Lahaul and Spiti": "Manali",
    "Ganderbal": "Srinagar", "Shopian": "Srinagar",
    "Bandipora": "Srinagar", "Baramulla": "Srinagar", "Budgam": "Srinagar",
    "East Singhbhum": "Jamshedpur", "Koderma": "Hazaribagh",
    "Palamu": "Daltonganj", "Sahebganj": "Rajmahal",
    "Saraikela Kharsawan": "Jamshedpur", "West Singhbhum": "Chaibasa",
    "Bagalkote": "Bagalkot", "Bengaluru Rural": "Bangalore",
    "Bengaluru Urban": "Bangalore", "Dakshina Kannada": "Mangalore",
    "Kodagu": "Madikeri", "Uttara Kannada": "Karwar",
    "Chamarajanagara": "Mysuru", "Chikkaballapura": "Bangalore",
    "Davanagere": "Davangere",
    "Wayanad": "Kozhikode", "Kalpetta": "Kozhikode", "Kargil": "Leh",
    "Agatti": "Kavaratti", "Minicoy": "Kavaratti", "Amini": "Kavaratti",
    "Agar-Malwa": "Ujjain",
    "Ahilyanagar": "Ahmednagar",
    "Chhatrapati Sambhajinagar": "Aurangabad", "Dharashiv": "Osmanabad",
    "Gadchiroli": "Chandrapur", "Mumbai Suburban": "Mumbai",
    "Buldhana": "Akola",
    "Nanded": "Nanded", "Raigad": "Alibag", "Sindhudurg": "Ratnagiri",
    "Imphal East": "Imphal", "Imphal West": "Imphal", "Jiribam": "Imphal",
    "Kakching": "Imphal", "Kamjong": "Imphal", "Kangpokpi": "Imphal",
    "Noney": "Imphal", "Pherzawl": "Imphal", "Tamenglong": "Imphal",
    "Tengnoupal": "Imphal", "Ukhrul": "Imphal",
    "East Garo Hills": "Tura", "East Jaintia Hills": "Shillong",
    "East Khasi Hills": "Shillong", "Eastern West Khasi Hills": "Shillong",
    "North Garo Hills": "Tura", "Ri Bhoi": "Shillong",
    "South Garo Hills": "Tura", "South West Garo Hills": "Tura",
    "South West Khasi Hills": "Shillong", "West Garo Hills": "Tura",
    "West Jaintia Hills": "Shillong", "West Khasi Hills": "Shillong",
    "Champhai": "Aizawl", "Hnahthial": "Aizawl", "Khawzawl": "Aizawl",
    "Saitual": "Aizawl", "Siaha": "Aizawl",
    "Chumoukedima": "Dimapur", "Mon Nagaland": "Dimapur",
    "Niuland": "Dimapur", "Peren": "Kohima",
    "Boudh": "Sambalpur", "Kalahandi": "Bhawanipatna",
    "Kandhamal": "Phulbani", "Kendujhar": "Baripada",
    "Mayurbhanj": "Baripada", "Nabarangpur": "Koraput",
    "Gurdaspur": "Amritsar", "S.A.S. Nagar": "Chandigarh",
    "Fatehgarh Sahib": "Ropar", "Malerkotla": "Ludhiana",
    "Shahid Bhagat Singh Nagar": "Jalandhar", "Sri Muktsar Sahib": "Muktsar",
    "Chittorgarh": "Bhilwara", "Dholpur": "Agra",
    "Didwana-Kuchaman": "Nagaur", "Gangapur City": "Sawai Madhopur",
    "Jaipur Rural": "Jaipur", "Jodhpur Rural": "Jodhpur",
    "Khairthal-Tijara": "Alwar", "Kotputli-Behror": "Alwar",
    "East Sikkim": "Gangtok", "North Sikkim": "Gangtok",
    "Soreng": "Gangtok", "South Sikkim": "Namchi", "West Sikkim": "Gangtok",
    "Kallakurichi": "Salem", "Kancheepuram": "Chengalpattu",
    "Kanyakumari": "Tirunelveli",
    "Nilgiris": "Ooty", "Ranipet": "Vellore", "Tirupattur": "Vellore",
    "Tiruvarur": "Kumbakonam", "Virudhunagar": "Madurai", "Viluppuram": "Cuddalore",
    "Bhadradri Kothagudem": "Khammam", "Hanumakonda": "Warangal",
    "Jagitial": "Karimnagar", "Jayashankar Bhupalpally": "Warangal",
    "Jogulamba Gadwal": "Mahbubnagar", "Kamareddy": "Nizamabad",
    "Kumuram Bheem Asifabad": "Adilabad", "Medchal-Malkajgiri": "Hyderabad",
    "Mahabubabad": "Khammam", "Mulugu": "Warangal",
    "Nagarkurnool": "Mahbubnagar", "Rajanna Sircilla": "Karimnagar",
    "Ranga Reddy": "Hyderabad", "Sangareddy": "Hyderabad",
    "Wanaparthy": "Mahbubnagar",
    "Warangal Rural": "Warangal", "Yadadri Bhuvanagiri": "Nalgonda",
    "Dhalai": "Agartala", "Gomati": "Agartala", "Khowai": "Agartala",
    "North Tripura": "Agartala", "Sepahijala": "Agartala",
    "South Tripura": "Agartala", "Unakoti": "Agartala",
    "West Tripura": "Agartala",
    "Ambedkar Nagar": "Ayodhya", "Banda Uttar Pradesh": "Banda",
    "Gautam Buddha Nagar": "Noida", "Kanpur Dehat": "Kanpur",
    "Kanpur Nagar": "Kanpur", "Kaushambi": "Allahabad",
    "Lakhimpur Kheri": "Lakhimpur",
    "Prayagraj": "Allahabad", "Sant Kabir Nagar": "Gorakhpur",
    "Shravasti": "Bahraich", "Siddharthnagar": "Gorakhpur",
    "Sonbhadra": "Varanasi",
    "Chamoli": "Rishikesh", "Pauri Garhwal": "Lansdowne",
    "Tehri Garhwal": "Rishikesh", "Udham Singh Nagar": "Rudrapur",
    "Birbhum": "Bolpur", "Cooch Behar": "Koch Bihar",
    "Dakshin Dinajpur": "Balurghat", "Hooghly": "Chandannagar",
    "Alipurduar": "Jalpaiguri",
    "Nadia": "Krishnanagar", "North 24 Parganas": "Barasat",
    "Paschim Bardhaman": "Asansol", "Paschim Medinipur": "Kharagpur",
    "Purba Bardhaman": "Bardhaman", "Purba Medinipur": "Haldia",
    "Purulia": "Asansol", "South 24 Parganas": "Diamond Harbour",
    "Uttar Dinajpur": "Raiganj",
}

# ── Compass & WMO codes ────────────────────────────────────────────────────
_COMPASS = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]


def _deg_to_dir(deg: float | None) -> str:
    if deg is None:
        return "N/A"
    return _COMPASS[round(float(deg) / 22.5) % 16]


WMO_DESCRIPTIONS: dict[int, str] = {
    0:  "Clear sky",
    1:  "Mainly clear",        2:  "Partly cloudy",     3:  "Overcast",
    45: "Fog",                 48: "Icy fog",
    51: "Light drizzle",       53: "Moderate drizzle",  55: "Dense drizzle",
    61: "Slight rain",         63: "Moderate rain",     65: "Heavy rain",
    71: "Slight snow",         73: "Moderate snow",     75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers",      81: "Moderate showers",  82: "Heavy showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail", 99: "Thunderstorm, heavy hail",
}


# ── Geocoding ──────────────────────────────────────────────────────────────

def _geocode(city: str) -> dict[str, Any] | None:
    """Return {lat, lon, name} for a city, cached to disk.

    Tries in order:
      1. The city name as-is
      2. The fallback name from _FALLBACKS (if present)
      3. The city name suffixed with ", India" (for ambiguous/short names)
    """
    fallback = _FALLBACKS.get(city)
    names: list[str] = [city]
    if fallback and fallback != city:
        names.append(fallback)
    # Third attempt: append ", India" to improve geocoding accuracy
    india_suffix = f"{city}, India"
    if india_suffix not in names:
        names.append(india_suffix)

    for name in names:
        key = name.lower().strip()
        if key in _geo_cache:
            return _geo_cache[key]
        try:
            r = requests.get(
                f"{_GEO_BASE}/search",
                params={"name": name, "count": 5, "language": "en", "format": "json"},
                timeout=15, verify=False,
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            india   = [x for x in results if x.get("country_code") == "IN"]
            hit     = india[0] if india else (results[0] if results else None)
            if hit:
                # Cache under the original city key so it's found next time
                coord = {"lat": hit["latitude"], "lon": hit["longitude"],
                         "name": hit.get("name", name)}
                orig_key = city.lower().strip()
                _geo_cache[orig_key] = coord
                _geo_cache[key] = coord
                _save_geo_cache()
                return coord
        except Exception:
            continue
    return None


# ── Open-Meteo weather fetch ───────────────────────────────────────────────

def _fetch_weather(lat: float, lon: float) -> dict[str, Any]:
    r = requests.get(
        f"{_WTHR_BASE}/forecast",
        params={
            "latitude":   round(lat, 4),
            "longitude":  round(lon, 4),
            "current":    ("temperature_2m,relative_humidity_2m,apparent_temperature,"
                           "weathercode,cloud_cover,pressure_msl,visibility,"
                           "wind_speed_10m,wind_direction_10m"),
            "daily":      ("temperature_2m_max,temperature_2m_min,weathercode,"
                           "precipitation_probability_max"),
            "hourly":     ("temperature_2m,relative_humidity_2m,apparent_temperature,"
                           "precipitation_probability,weathercode,"
                           "wind_speed_10m,wind_direction_10m"),
            "forecast_days":   7,
            "timezone":        "Asia/Kolkata",
            "wind_speed_unit": "kmh",
        },
        timeout=15, verify=False,
    )
    r.raise_for_status()
    return r.json()


# ── wttr.in fallback (when Open-Meteo is rate-limited) ────────────────────

def _fetch_wttr(city: str) -> dict[str, Any]:
    """Fetch weather from wttr.in JSON API (free, no key)."""
    search = _FALLBACKS.get(city, city)
    r = requests.get(
        f"https://wttr.in/{search}?format=j1",
        timeout=15, verify=False,
        headers={"User-Agent": "IndiaWeatherAgent/1.0"},
    )
    r.raise_for_status()
    return r.json()


def _summary_from_wttr(city: str, state: str) -> dict[str, Any]:
    """Build the same normalised schema from a wttr.in response."""
    data = _fetch_wttr(city)
    cur  = data["current_condition"][0]
    area = data["nearest_area"][0]
    city_label = area["areaName"][0]["value"]
    obs_time = (
        datetime.fromisoformat(cur["localObsDateTime"].replace(" ", "T")).strftime("%d %b %Y %I:%M %p IST")
        if cur.get("localObsDateTime") else datetime.now(_IST).strftime("%d %b %Y %I:%M %p IST")
    )

    def _wttr_code(desc: str) -> str:
        return desc.capitalize() if desc else "Unknown"

    forecast = []
    for day in data.get("weather", [])[:7]:
        midday = day["hourly"][4] if len(day["hourly"]) > 4 else day["hourly"][0]
        forecast.append({
            "date":        day["date"],
            "max_c":       day["maxtempC"],
            "min_c":       day["mintempC"],
            "description": _wttr_code(midday["weatherDesc"][0]["value"]),
            "rain_pct":    midday["chanceofrain"],
            "hourly": [
                {
                    "time":           h["time"],
                    "temp_c":         h["tempC"],
                    "feels_like_c":   h["FeelsLikeC"],
                    "description":    _wttr_code(h["weatherDesc"][0]["value"]),
                    "wind_kmph":      h["windspeedKmph"],
                    "wind_dir":       h["winddir16Point"],
                    "humidity":       h["humidity"],
                    "chance_of_rain": h["chanceofrain"],
                }
                for h in day["hourly"]
            ],
        })

    wind_kmph = str(round(float(cur["windspeedKmph"]) * 1.60934)) if cur.get("windspeedKmph") else "0"

    return {
        "city":             city,
        "state":            state,
        "region":           city_label,
        "country":          "India",
        "temperature_c":    cur["temp_C"],
        "feels_like_c":     cur["FeelsLikeC"],
        "humidity":         cur["humidity"],
        "description":      _wttr_code(cur["weatherDesc"][0]["value"]),
        "wind_kmph":        cur["windspeedKmph"],
        "wind_dir":         cur["winddir16Point"],
        "visibility_km":    cur["visibility"],
        "pressure_mb":      cur["pressure"],
        "uv_index":         cur["uvIndex"],
        "cloud_cover":      cur["cloudcover"],
        "observation_time": obs_time,
        "forecast":         forecast,
    }


# ── Summary builder ────────────────────────────────────────────────────────

def get_summary(city: str, state: str) -> dict[str, Any]:
    """
    Fetch weather data. Tries Open-Meteo first (7-day, IST-aware).
    Falls back to wttr.in if Open-Meteo is rate-limited or unavailable.
    Returns the same normalised schema either way.
    """
    # ── Try Open-Meteo ─────────────────────────────────────────────────
    try:
        coord = _geocode(city)
        if not coord:
            raise ValueError(f"Could not geocode '{city}'")
        data       = _fetch_weather(coord["lat"], coord["lon"])
        cur        = data.get("current", {})
        cur_code   = int(cur.get("weathercode") or 0)
        city_label = coord["name"]

        obs_raw  = cur.get("time", "")
        obs_time = (datetime.fromisoformat(obs_raw).strftime("%d %b %Y %I:%M %p IST")
                    if obs_raw else datetime.now(_IST).strftime("%d %b %Y %I:%M %p IST"))

        hourly  = data.get("hourly", {})
        h_times = hourly.get("time", [])
        owm_days: dict[str, list[dict]] = {}
        for i, t in enumerate(h_times):
            hour = int(t[11:13])
            if hour % 3 != 0:
                continue
            date = t[:10]

            def _hv(key: str, default: Any = 0, idx: int = i) -> Any:
                arr = hourly.get(key, [])
                return arr[idx] if idx < len(arr) else default

            owm_days.setdefault(date, []).append({
                "time":           str(hour * 100),
                "temp_c":         str(round(_hv("temperature_2m"))),
                "feels_like_c":   str(round(_hv("apparent_temperature"))),
                "description":    WMO_DESCRIPTIONS.get(int(_hv("weathercode") or 0), "Unknown"),
                "wind_kmph":      str(round(_hv("wind_speed_10m"))),
                "wind_dir":       _deg_to_dir(_hv("wind_direction_10m")),
                "humidity":       str(int(_hv("relative_humidity_2m"))),
                "chance_of_rain": str(int(_hv("precipitation_probability"))),
            })

        daily    = data.get("daily", {})
        forecast: list[dict] = []
        for i, date in enumerate(daily.get("time", [])[:7]):
            def _dv(key: str, default: Any = 0, idx: int = i) -> Any:
                arr = daily.get(key, [])
                return arr[idx] if idx < len(arr) else default

            code = int(_dv("weathercode") or 0)
            forecast.append({
                "date":        date,
                "max_c":       str(round(_dv("temperature_2m_max"))),
                "min_c":       str(round(_dv("temperature_2m_min"))),
                "description": WMO_DESCRIPTIONS.get(code, "Variable clouds"),
                "rain_pct":    str(int(_dv("precipitation_probability_max") or 0)),
                "hourly":      owm_days.get(date, []),
            })

        return {
            "city":             city,
            "state":            state,
            "region":           city_label,
            "country":          "India",
            "temperature_c":    str(round(cur.get("temperature_2m") or 0)),
            "feels_like_c":     str(round(cur.get("apparent_temperature") or 0)),
            "humidity":         str(int(cur.get("relative_humidity_2m") or 0)),
            "description":      WMO_DESCRIPTIONS.get(cur_code, "Unknown"),
            "wind_kmph":        str(round(cur.get("wind_speed_10m") or 0)),
            "wind_dir":         _deg_to_dir(cur.get("wind_direction_10m")),
            "visibility_km":    str(round((cur.get("visibility") or 0) / 1000, 1)),
            "pressure_mb":      str(round(cur.get("pressure_msl") or 0)),
            "uv_index":         "N/A",
            "cloud_cover":      str(int(cur.get("cloud_cover") or 0)),
            "observation_time": obs_time,
            "forecast":         forecast,
        }

    except Exception:
        # Open-Meteo failed — fall back to wttr.in
        return _summary_from_wttr(city, state)


# ── Parallel batch fetch ────────────────────────────────────────────────────

def fetch_all(cities: list[str], state: str, workers: int = 8) -> list[dict]:
    """
    Fetch weather for *all* cities in parallel using a thread pool.

    Replaces the sequential ``for city in DISTRICTS`` loop inside each
    state agent, reducing total wall-clock time from O(N × latency) to
    roughly O(latency) for N districts.

    Args:
        cities:  Ordered list of district/city names.
        state:   State name (passed through to get_summary).
        workers: Max simultaneous HTTP requests (default 8).

    Returns:
        List of weather dicts in the same order as *cities*.
        On per-city failure the dict contains an ``error`` key.
    """
    results: list[dict | None] = [None] * len(cities)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {
            executor.submit(get_summary, city, state): i
            for i, city in enumerate(cities)
        }
        for future in as_completed(future_to_idx):
            i = future_to_idx[future]
            try:
                results[i] = future.result()
            except Exception as exc:
                results[i] = {"city": cities[i], "state": state, "error": str(exc)}
    return results  # type: ignore[return-value]

