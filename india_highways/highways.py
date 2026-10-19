"""
India Highways — Curated Reference Data
===========================================
Static reference data on National Highways (NH) and State Highways (SH),
grounded in publicly published figures (MoRTH / NHAI / Wikipedia) rather
than invented numbers. Where only aggregate or partial data is publicly
available, that limitation is stated explicitly instead of guessing.

Sources consulted (see research notes): Wikipedia "Roads in India",
"State highways in India", "List of National Highways in India by state",
"National Highways Authority of India" — all public-domain aggregate
statistics, current as of the cited year.

In 2010 MoRTH consolidated hundreds of shorter, disconnected National
Highways into fewer, longer continuous corridors with new numbers — many
of today's "historic" highways (old NH1, NH2, NH5, NH7, NH8, NH17) now
live on as segments of new NH44, NH19, NH16, NH66 and NH48. Both are
included below where notable, clearly labelled.
"""

from __future__ import annotations

# ── National Highways (curated — notable major corridors, not exhaustive) ──
NATIONAL_HIGHWAYS: list[dict] = [
    {
        "number": "NH44", "status": "current",
        "route": "Srinagar (J&K) → Kanyakumari (Tamil Nadu)",
        "length_km": 3745,
        "states": ["Jammu & Kashmir", "Punjab", "Haryana", "Delhi", "Uttar Pradesh",
                   "Madhya Pradesh", "Maharashtra", "Telangana", "Andhra Pradesh",
                   "Karnataka", "Tamil Nadu"],
        "note": "India's longest National Highway — runs the full length of the country, north to south. Formed in 2010 by merging old NH1, NH1A, NH2(part), NH3, NH75, NH26, NH7 and others into one continuous number.",
    },
    {
        "number": "NH27", "status": "current",
        "route": "Porbandar (Gujarat) → Silchar (Assam)",
        "length_km": 3507,
        "states": ["Gujarat", "Rajasthan", "Madhya Pradesh", "Uttar Pradesh",
                   "Bihar", "West Bengal", "Assam"],
        "note": "India's longest east–west corridor, nicknamed the 'East-West Corridor' highway — connects the Arabian Sea coast to the Northeast.",
    },
    {
        "number": "NH48", "status": "current",
        "route": "Delhi → Chennai (via Jaipur, Ahmedabad, Mumbai, Pune, Bengaluru)",
        "length_km": 2807,
        "states": ["Delhi", "Haryana", "Rajasthan", "Gujarat", "Maharashtra",
                   "Karnataka", "Tamil Nadu"],
        "note": "India's busiest commercial corridor, carrying the heaviest truck/freight traffic of any NH. The Delhi–Mumbai stretch was historically numbered NH8.",
    },
    {
        "number": "NH52", "status": "current",
        "route": "Sangrur (Punjab) → Ankola (Karnataka)",
        "length_km": 2317,
        "states": ["Punjab", "Haryana", "Rajasthan", "Madhya Pradesh", "Maharashtra", "Karnataka"],
        "note": "A long inland north–south link through central India, connecting Punjab's grain belt to Karnataka's west coast.",
    },
    {
        "number": "NH30", "status": "current",
        "route": "Sitarganj (Uttarakhand) → Ibrahimpatnam (Andhra Pradesh)",
        "length_km": 2010,
        "states": ["Uttarakhand", "Uttar Pradesh", "Chhattisgarh", "Telangana", "Andhra Pradesh"],
        "note": "Runs via Lucknow, Prayagraj (Allahabad), Varanasi and Raipur — a major central-India north–south spine.",
    },
    {
        "number": "NH16", "status": "current",
        "route": "Chennai (Tamil Nadu) → Kolkata (West Bengal)",
        "length_km": 1711,
        "states": ["Tamil Nadu", "Andhra Pradesh", "Odisha", "West Bengal"],
        "note": "The east-coast arm of the original Golden Quadrilateral project, passing through Vijayawada and Bhubaneswar. Formerly numbered NH5.",
    },
    {
        "number": "NH66", "status": "current",
        "route": "Panvel (Maharashtra) → Kanyakumari (Tamil Nadu)",
        "length_km": 1622,
        "states": ["Maharashtra", "Goa", "Karnataka", "Kerala", "Tamil Nadu"],
        "note": "India's principal west-coast highway, hugging the Konkan and Malabar coastlines. Formerly numbered NH17.",
    },
    {
        "number": "NH19", "status": "current",
        "route": "Delhi → Kolkata (via Agra, Kanpur, Varanasi)",
        "length_km": 1435,
        "states": ["Delhi", "Haryana", "Uttar Pradesh", "Bihar", "Jharkhand", "West Bengal"],
        "note": "Follows the historic Grand Trunk Road / Sher Shah Suri Marg alignment, one of South Asia's oldest major trade routes. Formerly numbered NH2.",
    },
    {
        "number": "NH65", "status": "current",
        "route": "Pune (Maharashtra) → Machilipatnam (Andhra Pradesh)",
        "length_km": 841,
        "states": ["Maharashtra", "Karnataka", "Telangana", "Andhra Pradesh"],
        "note": "Key link between Pune, Solapur, Hyderabad and the Andhra coast via Vijayawada.",
    },
    {
        "number": "NH33", "status": "current",
        "route": "Varanasi (UP) → Baharagora (Jharkhand/Odisha/WB border)",
        "length_km": 948,
        "states": ["Uttar Pradesh", "Jharkhand", "West Bengal"],
        "note": "Runs through the Chota Nagpur mineral belt via Ranchi and Jamshedpur — vital for steel and coal freight.",
    },
    {
        "number": "NH37", "status": "current",
        "route": "Goalpara → Jorabat → Numaligarh (Assam)",
        "length_km": 730,
        "states": ["Assam"],
        "note": "A lifeline highway running along the Brahmaputra valley, linking Guwahati to Upper Assam's tea and oil belt.",
    },
    # ── Notable pre-2010 ("historic") numbering, now absorbed into the above ──
    {
        "number": "NH1 (historic)", "status": "historic",
        "route": "Delhi → Amritsar → Attari (Wagah border)",
        "length_km": 456,
        "states": ["Delhi", "Punjab"],
        "note": "Now part of NH44. The Grand Trunk Road's northern stretch, ending at the Pakistan border crossing at Wagah/Attari.",
    },
    {
        "number": "NH8 (historic)", "status": "historic",
        "route": "Delhi → Mumbai",
        "length_km": 1428,
        "states": ["Delhi", "Haryana", "Rajasthan", "Gujarat", "Maharashtra"],
        "note": "Now part of NH48. Was the original Golden Quadrilateral's west arm and one of India's most recognisable highway numbers pre-2010.",
    },
    {
        "number": "NH7 (historic)", "status": "historic",
        "route": "Varanasi (UP) → Kanyakumari (Tamil Nadu)",
        "length_km": 2369,
        "states": ["Uttar Pradesh", "Madhya Pradesh", "Maharashtra", "Telangana",
                   "Andhra Pradesh", "Karnataka", "Tamil Nadu"],
        "note": "Now part of NH44. Was India's longest NH before the 2010 renumbering folded it (and others) into NH44.",
    },
    {
        "number": "NH5 (historic)", "status": "historic",
        "route": "Kolkata (West Bengal) → Chennai (Tamil Nadu)",
        "length_km": 1533,
        "states": ["West Bengal", "Odisha", "Andhra Pradesh", "Tamil Nadu"],
        "note": "Now part of NH16. Golden Quadrilateral's east/south-east coastal arm.",
    },
    {
        "number": "NH2 (historic)", "status": "historic",
        "route": "Delhi → Kolkata",
        "length_km": 1465,
        "states": ["Delhi", "Haryana", "Uttar Pradesh", "Bihar", "Jharkhand", "West Bengal"],
        "note": "Now part of NH19. The Grand Trunk Road's eastern stretch, one of the oldest continuously-used trade routes in South Asia.",
    },
    {
        "number": "NH17 (historic)", "status": "historic",
        "route": "Panvel (Maharashtra) → Edapally (Kochi, Kerala)",
        "length_km": 1269,
        "states": ["Maharashtra", "Goa", "Karnataka", "Kerala"],
        "note": "Now part of NH66. The original west-coast highway numbering.",
    },
]

# ── State Highway aggregate summary (only publicly-published figures used) ──
# Total length figure varies slightly by source (both cite ~31 March 2020):
#   176,528 km per one MoRTH-derived citation, 186,528 km per another.
# We show the range honestly rather than picking one arbitrarily.
STATE_HIGHWAY_SUMMARY: dict = {
    "as_of": "31 March 2020",
    "total_km_low": 176528,
    "total_km_high": 186528,
    "source_note": (
        "Published aggregate figures for India's total state-highway length differ "
        "slightly by source (both citing ~31 March 2020 MoRTH data) — shown here as "
        "a range rather than a single invented number."
    ),
    # Only these 5 states have an individually-published % share in the sources
    # consulted. The remaining ~41.7% is spread across all other states/UTs with
    # no granular public breakdown available — explicitly NOT estimated here.
    "top_states_by_share": [
        {"state": "Maharashtra", "share_pct": 22.14},
        {"state": "Karnataka",   "share_pct": 11.11},
        {"state": "Gujarat",     "share_pct": 9.76},
        {"state": "Rajasthan",   "share_pct": 8.62},
        {"state": "Tamil Nadu",  "share_pct": 6.67},
    ],
    "unlisted_share_pct": round(100 - (22.14 + 11.11 + 9.76 + 8.62 + 6.67), 2),
}

# ── Wider national road-network context (all publicly published MoRTH figures) ──
ROAD_NETWORK_STATS: dict = {
    "total_road_network_km": 6617900,
    "total_road_network_note": "India's total road network (all categories) — the largest in the world.",
    "nh_expressway_km": 151019,
    "nh_expressway_as_of": "31 March 2021",
    "district_roads_km": 632154,
    "rural_roads_share_pct": 72.97,
}

# ── Expressways (a distinct, increasingly important network MoRTH tracks separately from NH) ──
EXPRESSWAYS: list[dict] = [
    {
        "name": "Delhi–Mumbai Expressway", "status": "operational",
        "route": "Delhi → Mumbai (via Jaipur, Kota, Indore)",
        "length_km": 1386,
        "states": ["Delhi", "Haryana", "Rajasthan", "Madhya Pradesh", "Gujarat", "Maharashtra"],
        "note": "India's longest expressway on full completion — an access-controlled greenfield corridor designed to cut Delhi-Mumbai travel time roughly in half.",
    },
    {
        "name": "Mumbai–Pune Expressway", "status": "operational",
        "route": "Mumbai → Pune",
        "length_km": 94,
        "states": ["Maharashtra"],
        "note": "India's first 6-lane access-controlled expressway, opened in 2002.",
    },
    {
        "name": "Yamuna Expressway", "status": "operational",
        "route": "Greater Noida → Agra",
        "length_km": 165,
        "states": ["Uttar Pradesh"],
        "note": "Links the NCR to Agra; also used as a test track and for motorsport events.",
    },
    {
        "name": "Eastern Peripheral Expressway", "status": "operational",
        "route": "Kundli → Palwal (bypassing Delhi)",
        "length_km": 135,
        "states": ["Haryana", "Uttar Pradesh"],
        "note": "Built to divert non-Delhi-bound traffic around the capital and ease pollution/congestion.",
    },
    {
        "name": "Ahmedabad–Vadodara Expressway", "status": "operational",
        "route": "Ahmedabad → Vadodara",
        "length_km": 93,
        "states": ["Gujarat"],
        "note": "One of India's earliest expressways, opened in phases from 2000-2004.",
    },
    {
        "name": "Bundelkhand Expressway", "status": "operational",
        "route": "Chitrakoot → Etawah",
        "length_km": 296,
        "states": ["Uttar Pradesh"],
        "note": "Built to spur industrial/economic development in the historically underdeveloped Bundelkhand region.",
    },
    {
        "name": "Purvanchal Expressway", "status": "operational",
        "route": "Lucknow → Ghazipur",
        "length_km": 341,
        "states": ["Uttar Pradesh"],
        "note": "Includes a stretch usable as an emergency airstrip for the Indian Air Force.",
    },
    {
        "name": "Bengaluru–Mysuru Expressway", "status": "operational",
        "route": "Bengaluru → Mysuru",
        "length_km": 118,
        "states": ["Karnataka"],
        "note": "Cut typical road travel time between the two cities roughly in half.",
    },
    {
        "name": "Ganga Expressway", "status": "under_construction",
        "route": "Meerut → Prayagraj",
        "length_km": 594,
        "states": ["Uttar Pradesh"],
        "note": "Planned to be one of India's longest expressways on completion; includes an airstrip segment, like Purvanchal.",
    },
]

# ── Named megaproject corridors that several National Highways above belong to ──
CORRIDOR_MAP: dict[str, str] = {
    "NH44": "North–South Corridor", "NH7 (historic)": "North–South Corridor",
    "NH27": "East–West Corridor",
    "NH48": "Golden Quadrilateral", "NH8 (historic)": "Golden Quadrilateral",
    "NH16": "Golden Quadrilateral", "NH5 (historic)": "Golden Quadrilateral",
    "NH19": "Golden Quadrilateral", "NH2 (historic)": "Golden Quadrilateral",
    "NH66": "Golden Quadrilateral", "NH17 (historic)": "Golden Quadrilateral",
}
CORRIDOR_NOTES: dict[str, str] = {
    "Golden Quadrilateral": "A 1999-launched megaproject linking Delhi, Mumbai, Chennai and Kolkata in a single quadrilateral — India's first large-scale controlled-access highway programme.",
    "North–South Corridor": "Connects Srinagar in the far north to Kanyakumari at India's southern tip.",
    "East–West Corridor": "Connects Porbandar on the Arabian Sea coast to Silchar in the Northeast.",
}

# ── Pre-2010 → post-2010 National Highway renumbering (MoRTH's 2010 consolidation) ──
RENUMBERING: list[dict] = [
    {"old": "NH1", "new": "NH44", "note": "Delhi–Amritsar stretch folded into the new north-south NH44."},
    {"old": "NH7", "new": "NH44", "note": "Varanasi–Kanyakumari, formerly India's longest NH, became the southern half of NH44."},
    {"old": "NH8", "new": "NH48", "note": "The original Delhi–Mumbai Golden Quadrilateral arm, renumbered NH48."},
    {"old": "NH5", "new": "NH16", "note": "Kolkata–Chennai east-coast corridor, renumbered NH16."},
    {"old": "NH2", "new": "NH19", "note": "The historic Grand Trunk Road's Delhi–Kolkata stretch, renumbered NH19."},
    {"old": "NH17", "new": "NH66", "note": "The original west-coast highway, renumbered NH66."},
]

# ── Approximate city coordinates + each highway's end-to-end endpoints, for the map view ──
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Srinagar": (34.0837, 74.7973), "Kanyakumari": (8.0883, 77.5385),
    "Porbandar": (21.6417, 69.6293), "Silchar": (24.8333, 92.7789),
    "Delhi": (28.6139, 77.2090), "Chennai": (13.0827, 80.2707),
    "Sangrur": (30.2458, 75.8421), "Ankola": (14.6698, 74.3045),
    "Sitarganj": (28.9333, 79.7000), "Ibrahimpatnam": (16.5500, 80.4300),
    "Kolkata": (22.5726, 88.3639), "Panvel": (18.9894, 73.1175),
    "Pune": (18.5204, 73.8567), "Machilipatnam": (16.1875, 81.1389),
    "Varanasi": (25.3176, 82.9739), "Baharagora": (22.3667, 86.7500),
    "Goalpara": (26.1736, 90.6259), "Numaligarh": (26.6667, 93.7333),
    "Attari": (31.6000, 74.6333), "Mumbai": (19.0760, 72.8777),
    "Kochi": (9.9312, 76.2673), "Jaipur": (26.9124, 75.7873),
    "Ahmedabad": (23.0225, 72.5714), "Agra": (27.1767, 78.0081),
    "Kanpur": (26.4499, 80.3319), "Jorabat": (26.0667, 91.8333),
}
HIGHWAY_ENDPOINTS: dict[str, list[str]] = {
    "NH44": ["Srinagar", "Kanyakumari"],
    "NH27": ["Porbandar", "Silchar"],
    "NH48": ["Delhi", "Chennai"],
    "NH52": ["Sangrur", "Ankola"],
    "NH30": ["Sitarganj", "Ibrahimpatnam"],
    "NH16": ["Chennai", "Kolkata"],
    "NH66": ["Panvel", "Kanyakumari"],
    "NH19": ["Delhi", "Kolkata"],
    "NH65": ["Pune", "Machilipatnam"],
    "NH33": ["Varanasi", "Baharagora"],
    "NH37": ["Goalpara", "Numaligarh"],
    "NH1 (historic)": ["Delhi", "Attari"],
    "NH8 (historic)": ["Delhi", "Mumbai"],
    "NH7 (historic)": ["Varanasi", "Kanyakumari"],
    "NH5 (historic)": ["Kolkata", "Chennai"],
    "NH2 (historic)": ["Delhi", "Kolkata"],
    "NH17 (historic)": ["Panvel", "Kochi"],
}

# ── Known intermediate waypoint cities (only where explicitly named in the route text) ──
HIGHWAY_VIA: dict[str, list[str]] = {
    "NH48": ["Jaipur", "Ahmedabad", "Mumbai", "Pune"],
    "NH19": ["Agra", "Kanpur", "Varanasi"],
    "NH37": ["Jorabat"],
}


