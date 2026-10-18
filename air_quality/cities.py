"""
Air Quality — City Registry
==============================
Curated list of major Indian cities (metros + state capitals) with their
coordinates, used to query Open-Meteo's free Air Quality API.
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
]
