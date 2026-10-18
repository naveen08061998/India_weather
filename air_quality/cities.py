"""
Air Quality — City Registry
==============================
Curated list of Indian cities (metros, state/UT capitals, and major
district towns) with their coordinates, used to query Open-Meteo's free
Air Quality API. ~65 cities — a deliberate middle ground between the
original 32-metro set and full district-level coverage (789 districts,
as used by india_weather): wide enough to cover every state/UT capital
plus key industrial/pollution-hotspot towns, while keeping the orchestrator's
CI runtime and Open-Meteo call volume reasonable for a free public API.
"""

from __future__ import annotations

CITIES: list[dict] = [
    {"name": "Delhi",            "state": "Delhi",          "lat": 28.6139, "lon": 77.2090},
    {"name": "Mumbai",           "state": "Maharashtra",     "lat": 19.0760, "lon": 72.8777},
    {"name": "Bengaluru",        "state": "Karnataka",       "lat": 12.9716, "lon": 77.5946},
    {"name": "Chennai",          "state": "Tamil Nadu",      "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata",          "state": "West Bengal",     "lat": 22.5726, "lon": 88.3639},
    {"name": "Hyderabad",        "state": "Telangana",       "lat": 17.3850, "lon": 78.4867},
    {"name": "Ahmedabad",        "state": "Gujarat",         "lat": 23.0225, "lon": 72.5714},
    {"name": "Pune",             "state": "Maharashtra",     "lat": 18.5204, "lon": 73.8567},
    {"name": "Jaipur",           "state": "Rajasthan",       "lat": 26.9124, "lon": 75.7873},
    {"name": "Lucknow",          "state": "Uttar Pradesh",   "lat": 26.8467, "lon": 80.9462},
    {"name": "Patna",            "state": "Bihar",           "lat": 25.5941, "lon": 85.1376},
    {"name": "Bhopal",           "state": "Madhya Pradesh",  "lat": 23.2599, "lon": 77.4126},
    {"name": "Chandigarh",       "state": "Chandigarh",      "lat": 30.7333, "lon": 76.7794},
    {"name": "Guwahati",         "state": "Assam",           "lat": 26.1445, "lon": 91.7362},
    {"name": "Thiruvananthapuram","state": "Kerala",         "lat": 8.5241,  "lon": 76.9366},
    {"name": "Bhubaneswar",      "state": "Odisha",          "lat": 20.2961, "lon": 85.8245},
    {"name": "Raipur",           "state": "Chhattisgarh",    "lat": 21.2514, "lon": 81.6296},
    {"name": "Ranchi",           "state": "Jharkhand",       "lat": 23.3441, "lon": 85.3096},
    {"name": "Dehradun",         "state": "Uttarakhand",     "lat": 30.3165, "lon": 78.0322},
    {"name": "Shimla",           "state": "Himachal Pradesh","lat": 31.1048, "lon": 77.1734},
    {"name": "Srinagar",         "state": "Jammu & Kashmir", "lat": 34.0837, "lon": 74.7973},
    {"name": "Amritsar",         "state": "Punjab",          "lat": 31.6340, "lon": 74.8723},
    {"name": "Kanpur",           "state": "Uttar Pradesh",   "lat": 26.4499, "lon": 80.3319},
    {"name": "Nagpur",           "state": "Maharashtra",     "lat": 21.1458, "lon": 79.0882},
    {"name": "Indore",           "state": "Madhya Pradesh",  "lat": 22.7196, "lon": 75.8577},
    {"name": "Surat",            "state": "Gujarat",         "lat": 21.1702, "lon": 72.8311},
    {"name": "Visakhapatnam",    "state": "Andhra Pradesh",  "lat": 17.6868, "lon": 83.2185},
    {"name": "Kochi",            "state": "Kerala",          "lat": 9.9312,  "lon": 76.2673},
    {"name": "Coimbatore",       "state": "Tamil Nadu",      "lat": 11.0168, "lon": 76.9558},
    {"name": "Varanasi",         "state": "Uttar Pradesh",   "lat": 25.3176, "lon": 82.9739},
    {"name": "Noida",            "state": "Uttar Pradesh",   "lat": 28.5355, "lon": 77.3910},
    {"name": "Gurugram",         "state": "Haryana",         "lat": 28.4595, "lon": 77.0266},
    # ── Remaining state/UT capitals ────────────────────────────────────────
    {"name": "Panaji",           "state": "Goa",             "lat": 15.4909, "lon": 73.8278},
    {"name": "Puducherry",       "state": "Puducherry",      "lat": 11.9416, "lon": 79.8083},
    {"name": "Port Blair",       "state": "Andaman & Nicobar","lat": 11.6234,"lon": 92.7265},
    {"name": "Jammu",            "state": "Jammu & Kashmir", "lat": 32.7266, "lon": 74.8570},
    {"name": "Leh",              "state": "Ladakh",          "lat": 34.1526, "lon": 77.5771},
    {"name": "Agartala",         "state": "Tripura",         "lat": 23.8315, "lon": 91.2868},
    {"name": "Aizawl",           "state": "Mizoram",         "lat": 23.7271, "lon": 92.7176},
    {"name": "Imphal",           "state": "Manipur",         "lat": 24.8170, "lon": 93.9368},
    {"name": "Kohima",           "state": "Nagaland",        "lat": 25.6751, "lon": 94.1086},
    {"name": "Itanagar",         "state": "Arunachal Pradesh","lat": 27.0844,"lon": 93.6053},
    {"name": "Gangtok",          "state": "Sikkim",          "lat": 27.3389, "lon": 88.6065},
    {"name": "Shillong",         "state": "Meghalaya",       "lat": 25.5788, "lon": 91.8933},
    # ── Major industrial / pollution-hotspot towns ──────────────────────────
    {"name": "Rajkot",           "state": "Gujarat",         "lat": 22.3039, "lon": 70.8022},
    {"name": "Vadodara",         "state": "Gujarat",         "lat": 22.3072, "lon": 73.1812},
    {"name": "Jodhpur",          "state": "Rajasthan",       "lat": 26.2389, "lon": 73.0243},
    {"name": "Udaipur",          "state": "Rajasthan",       "lat": 24.5854, "lon": 73.7125},
    {"name": "Agra",             "state": "Uttar Pradesh",   "lat": 27.1767, "lon": 78.0081},
    {"name": "Prayagraj",        "state": "Uttar Pradesh",   "lat": 25.4358, "lon": 81.8463},
    {"name": "Meerut",           "state": "Uttar Pradesh",   "lat": 28.9845, "lon": 77.7064},
    {"name": "Ghaziabad",        "state": "Uttar Pradesh",   "lat": 28.6692, "lon": 77.4538},
    {"name": "Faridabad",        "state": "Haryana",         "lat": 28.4089, "lon": 77.3178},
    {"name": "Ludhiana",         "state": "Punjab",          "lat": 30.9010, "lon": 75.8573},
    {"name": "Jalandhar",        "state": "Punjab",          "lat": 31.3260, "lon": 75.5762},
    {"name": "Cuttack",          "state": "Odisha",          "lat": 20.4625, "lon": 85.8830},
    {"name": "Jamshedpur",       "state": "Jharkhand",       "lat": 22.8046, "lon": 86.2029},
    {"name": "Dhanbad",          "state": "Jharkhand",       "lat": 23.7957, "lon": 86.4304},
    {"name": "Siliguri",         "state": "West Bengal",     "lat": 26.7271, "lon": 88.3953},
    {"name": "Durgapur",         "state": "West Bengal",     "lat": 23.5204, "lon": 87.3119},
    {"name": "Madurai",          "state": "Tamil Nadu",      "lat": 9.9252,  "lon": 78.1198},
    {"name": "Tiruchirappalli",  "state": "Tamil Nadu",      "lat": 10.7905, "lon": 78.7047},
    {"name": "Vijayawada",       "state": "Andhra Pradesh",  "lat": 16.5062, "lon": 80.6480},
    {"name": "Mysuru",           "state": "Karnataka",       "lat": 12.2958, "lon": 76.6394},
    {"name": "Thane",            "state": "Maharashtra",     "lat": 19.2183, "lon": 72.9781},
    {"name": "Nashik",           "state": "Maharashtra",     "lat": 19.9975, "lon": 73.7898},
    {"name": "Gwalior",          "state": "Madhya Pradesh",  "lat": 26.2183, "lon": 78.1828},
    {"name": "Jabalpur",         "state": "Madhya Pradesh",  "lat": 23.1815, "lon": 79.9864},
    {"name": "Kota",             "state": "Rajasthan",       "lat": 25.2138, "lon": 75.8648},
]

