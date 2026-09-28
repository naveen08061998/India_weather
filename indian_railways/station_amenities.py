"""
Indian Railways — Station Facilities (curated reference data)
================================================================
Hand-written, general-knowledge facts about passenger facilities at a
selection of major/iconic stations — no network calls, no third-party API.
Not an exhaustive or official facilities directory (station redevelopment
frequently changes platform counts/amenities); see DISCLAIMER, also shown
on the page. Keyed by station code (see train_data.STATION_COORDS).
"""

from __future__ import annotations

DISCLAIMER = (
    "General-knowledge highlights for a selection of major stations, not an "
    "official or exhaustive facilities directory — platform counts and amenities "
    "change with ongoing station redevelopment."
)

# facilities: short list of commonly available passenger amenities.
# highlight: one notable/well-known fact about the station.
STATION_AMENITIES: dict[str, dict] = {
    "NDLS": {"name": "New Delhi", "category": "A1",
             "facilities": ["Retiring rooms", "AC & non-AC waiting halls", "Cloakroom", "Food plaza", "WiFi"],
             "highlight": "One of India's busiest stations, with 16 platforms and direct Airport Express Metro access."},
    "CSTM": {"name": "Chhatrapati Shivaji Maharaj Terminus (Mumbai)", "category": "A1",
             "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
             "highlight": "A UNESCO World Heritage Site — Victorian Gothic terminus built in 1887-88, still Central Railway's headquarters."},
    "HWH": {"name": "Howrah Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "One of India's oldest and largest terminals, with 23 platforms handling well over 20 million passengers a year."},
    "MAS": {"name": "Chennai Central", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "South India's main railway gateway, connected directly to Chennai Metro."},
    "SC": {"name": "Secunderabad Junction", "category": "A1",
           "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
           "highlight": "The twin-city hub for Hyderabad/Secunderabad and one of South Central Railway's busiest junctions."},
    "SBC": {"name": "KSR Bengaluru City Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Bengaluru's main terminus; the city is also served by Yesvantpur and other satellite stations to spread traffic."},
    "ADI": {"name": "Ahmedabad Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Gujarat's principal railway hub, undergoing modernisation as part of the redevelopment programme."},
    "PNBE": {"name": "Patna Junction", "category": "A1",
             "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
             "highlight": "Bihar's busiest station and a major East Central Railway hub."},
    "BZA": {"name": "Vijayawada Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "A key North-South Indian Railways junction where several major trunk routes converge."},
    "BSB": {"name": "Varanasi Junction (Manduadih/Cantt)", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Gateway to one of India's holiest cities, and the origin of the first Vande Bharat Express route."},
    "KGP": {"name": "Kharagpur Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Once held the record for the world's longest railway platform (over 1,000 metres)."},
    "GHY": {"name": "Guwahati", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "The main railway gateway to India's Northeast."},
    "TVC": {"name": "Thiruvananthapuram Central", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Kerala's southern terminus and headquarters of the Thiruvananthapuram railway division."},
    "JAT": {"name": "Jammu Tawi", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Northernmost major broad-gauge terminus, gateway to Kashmir via the Udhampur-Srinagar-Baramulla line."},
    "CNB": {"name": "Kanpur Central", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "One of the busiest junctions on the Delhi-Howrah trunk route, with heavy through-traffic."},
    "BPL": {"name": "Bhopal Junction (Habibganj/Rani Kamlapati)", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Nearby Rani Kamlapati station reopened in 2021 as India's first fully corporate-redeveloped, airport-style station."},
    "NGP": {"name": "Nagpur Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Sits near India's Zero Mile Marker and is a major junction linking north-south and east-west trunk routes."},
    "PURI": {"name": "Puri", "category": "A1",
             "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
             "highlight": "Pilgrimage-town terminus serving the Jagannath Temple, one of the Char Dham sites."},
    "ASR": {"name": "Amritsar Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "Gateway to the Golden Temple and the Attari-Wagah border."},
    "JHS": {"name": "Jhansi Junction", "category": "A1",
            "facilities": ["Retiring rooms", "Waiting halls", "Cloakroom", "Food plaza", "WiFi"],
            "highlight": "A major North Central Railway junction where the Delhi-Chennai and Delhi-Mumbai trunk routes cross."},
}
