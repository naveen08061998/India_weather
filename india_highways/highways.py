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
