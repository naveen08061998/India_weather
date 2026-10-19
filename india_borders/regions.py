"""
India Borders — State & UT Adjacency Registry
=================================================
Curated, static reference data (no live API — this is settled public
geography, like current_affairs' PIB-adjacent facts or indian_railways'
history_content.py). Covers all 28 states + 8 union territories: which
other states/UTs each one shares a land border with, which countries (if
any) it borders, and whether it has a coastline.

Data is administrative/geographic fact only (current Indian state/UT
boundaries as reorganised in 2019 with J&K/Ladakh as separate UTs) — no
territorial commentary.
"""

from __future__ import annotations

# key -> {name, type (state/UT), land_neighbors (keys), countries (names), coastal (bool), capital, note}
REGIONS: dict[str, dict] = {
    "andhra_pradesh": {
        "name": "Andhra Pradesh", "type": "State", "capital": "Amaravati",
        "land_neighbors": ["odisha", "chhattisgarh", "telangana", "karnataka", "tamil_nadu", "puducherry"],
        "countries": [], "coastal": True,
        "note": "Puducherry's Yanam enclave is surrounded by Andhra Pradesh.",
    },
    "arunachal_pradesh": {
        "name": "Arunachal Pradesh", "type": "State", "capital": "Itanagar",
        "land_neighbors": ["assam", "nagaland"],
        "countries": ["China", "Myanmar", "Bhutan"], "coastal": False, "note": "",
    },
    "assam": {
        "name": "Assam", "type": "State", "capital": "Dispur",
        "land_neighbors": ["arunachal_pradesh", "nagaland", "manipur", "mizoram",
                           "tripura", "meghalaya", "west_bengal"],
        "countries": ["Bhutan", "Bangladesh"], "coastal": False,
        "note": "The main gateway connecting the Northeast to the rest of India (the 'Chicken's Neck' / Siliguri Corridor links it to West Bengal).",
    },
    "bihar": {
        "name": "Bihar", "type": "State", "capital": "Patna",
        "land_neighbors": ["uttar_pradesh", "jharkhand", "west_bengal"],
        "countries": ["Nepal"], "coastal": False, "note": "",
    },
    "chhattisgarh": {
        "name": "Chhattisgarh", "type": "State", "capital": "Raipur",
        "land_neighbors": ["madhya_pradesh", "uttar_pradesh", "jharkhand", "odisha",
                           "telangana", "andhra_pradesh", "maharashtra"],
        "countries": [], "coastal": False,
        "note": "Borders 7 states — tied for the most of any Indian state.",
    },
    "goa": {
        "name": "Goa", "type": "State", "capital": "Panaji",
        "land_neighbors": ["maharashtra", "karnataka"],
        "countries": [], "coastal": True, "note": "India's smallest state by area.",
    },
    "gujarat": {
        "name": "Gujarat", "type": "State", "capital": "Gandhinagar",
        "land_neighbors": ["rajasthan", "madhya_pradesh", "maharashtra", "dnh_dd"],
        "countries": ["Pakistan"], "coastal": True,
        "note": "Has India's longest coastline of any state.",
    },
    "haryana": {
        "name": "Haryana", "type": "State", "capital": "Chandigarh",
        "land_neighbors": ["punjab", "himachal_pradesh", "uttar_pradesh",
                           "rajasthan", "delhi", "chandigarh"],
        "countries": [], "coastal": False,
        "note": "Surrounds Delhi on three sides.",
    },
    "himachal_pradesh": {
        "name": "Himachal Pradesh", "type": "State", "capital": "Shimla",
        "land_neighbors": ["jammu_kashmir", "ladakh", "punjab", "haryana", "uttarakhand"],
        "countries": ["China"], "coastal": False, "note": "",
    },
    "jharkhand": {
        "name": "Jharkhand", "type": "State", "capital": "Ranchi",
        "land_neighbors": ["bihar", "west_bengal", "odisha", "chhattisgarh", "uttar_pradesh"],
        "countries": [], "coastal": False, "note": "",
    },
    "karnataka": {
        "name": "Karnataka", "type": "State", "capital": "Bengaluru",
        "land_neighbors": ["goa", "maharashtra", "telangana", "andhra_pradesh", "tamil_nadu", "kerala"],
        "countries": [], "coastal": True, "note": "",
    },
    "kerala": {
        "name": "Kerala", "type": "State", "capital": "Thiruvananthapuram",
        "land_neighbors": ["karnataka", "tamil_nadu", "puducherry"],
        "countries": [], "coastal": True,
        "note": "Puducherry's Mahe enclave lies within Kerala.",
    },
    "madhya_pradesh": {
        "name": "Madhya Pradesh", "type": "State", "capital": "Bhopal",
        "land_neighbors": ["uttar_pradesh", "chhattisgarh", "maharashtra", "gujarat", "rajasthan"],
        "countries": [], "coastal": False,
        "note": "India's 2nd largest state by area; borders 5 states.",
    },
    "maharashtra": {
        "name": "Maharashtra", "type": "State", "capital": "Mumbai",
        "land_neighbors": ["gujarat", "madhya_pradesh", "chhattisgarh", "telangana",
                           "karnataka", "goa", "dnh_dd"],
        "countries": [], "coastal": True, "note": "",
    },
    "manipur": {
        "name": "Manipur", "type": "State", "capital": "Imphal",
        "land_neighbors": ["nagaland", "assam", "mizoram"],
        "countries": ["Myanmar"], "coastal": False, "note": "",
    },
    "meghalaya": {
        "name": "Meghalaya", "type": "State", "capital": "Shillong",
        "land_neighbors": ["assam"],
        "countries": ["Bangladesh"], "coastal": False,
        "note": "Borders only one other Indian state (Assam), making it almost an enclave within the Northeast.",
    },
    "mizoram": {
        "name": "Mizoram", "type": "State", "capital": "Aizawl",
        "land_neighbors": ["assam", "manipur", "tripura"],
        "countries": ["Myanmar", "Bangladesh"], "coastal": False, "note": "",
    },
    "nagaland": {
        "name": "Nagaland", "type": "State", "capital": "Kohima",
        "land_neighbors": ["assam", "manipur", "arunachal_pradesh"],
        "countries": ["Myanmar"], "coastal": False, "note": "",
    },
    "odisha": {
        "name": "Odisha", "type": "State", "capital": "Bhubaneswar",
        "land_neighbors": ["west_bengal", "jharkhand", "chhattisgarh", "andhra_pradesh"],
        "countries": [], "coastal": True, "note": "",
    },
    "punjab": {
        "name": "Punjab", "type": "State", "capital": "Chandigarh",
        "land_neighbors": ["jammu_kashmir", "himachal_pradesh", "haryana", "rajasthan", "chandigarh"],
        "countries": ["Pakistan"], "coastal": False, "note": "",
    },
    "rajasthan": {
        "name": "Rajasthan", "type": "State", "capital": "Jaipur",
        "land_neighbors": ["punjab", "haryana", "uttar_pradesh", "madhya_pradesh", "gujarat"],
        "countries": ["Pakistan"], "coastal": False,
        "note": "India's largest state by area.",
    },
    "sikkim": {
        "name": "Sikkim", "type": "State", "capital": "Gangtok",
        "land_neighbors": ["west_bengal"],
        "countries": ["Nepal", "China", "Bhutan"], "coastal": False,
        "note": "Borders 3 countries but only 1 Indian state — the most international neighbours relative to its size.",
    },
    "tamil_nadu": {
        "name": "Tamil Nadu", "type": "State", "capital": "Chennai",
        "land_neighbors": ["andhra_pradesh", "karnataka", "kerala", "puducherry"],
        "countries": [], "coastal": True,
        "note": "Puducherry's own region plus its Karaikal enclave both lie within Tamil Nadu.",
    },
    "telangana": {
        "name": "Telangana", "type": "State", "capital": "Hyderabad",
        "land_neighbors": ["maharashtra", "chhattisgarh", "andhra_pradesh", "karnataka"],
        "countries": [], "coastal": False,
        "note": "Formed in 2014 by bifurcation from Andhra Pradesh.",
    },
    "tripura": {
        "name": "Tripura", "type": "State", "capital": "Agartala",
        "land_neighbors": ["assam", "mizoram"],
        "countries": ["Bangladesh"], "coastal": False,
        "note": "Bangladesh surrounds roughly 84% of Tripura's border.",
    },
    "uttar_pradesh": {
        "name": "Uttar Pradesh", "type": "State", "capital": "Lucknow",
        "land_neighbors": ["uttarakhand", "haryana", "delhi", "rajasthan",
                           "madhya_pradesh", "chhattisgarh", "jharkhand", "bihar"],
        "countries": ["Nepal"], "coastal": False,
        "note": "Borders the most states/UTs of any in India (8).",
    },
    "uttarakhand": {
        "name": "Uttarakhand", "type": "State", "capital": "Dehradun",
        "land_neighbors": ["himachal_pradesh", "uttar_pradesh"],
        "countries": ["Nepal", "China"], "coastal": False, "note": "",
    },
    "west_bengal": {
        "name": "West Bengal", "type": "State", "capital": "Kolkata",
        "land_neighbors": ["odisha", "jharkhand", "bihar", "sikkim", "assam"],
        "countries": ["Nepal", "Bhutan", "Bangladesh"], "coastal": True,
        "note": "The narrow Siliguri Corridor ('Chicken's Neck') here is the only land link between the Northeast and the rest of India.",
    },
    # ── Union Territories ───────────────────────────────────────────────────
    "andaman_nicobar": {
        "name": "Andaman & Nicobar Islands", "type": "Union Territory", "capital": "Port Blair",
        "land_neighbors": [], "countries": [], "coastal": True,
        "note": "An island territory with no land borders — closer to Myanmar/Indonesia than mainland India.",
    },
    "chandigarh": {
        "name": "Chandigarh", "type": "Union Territory", "capital": "Chandigarh",
        "land_neighbors": ["punjab", "haryana"],
        "countries": [], "coastal": False,
        "note": "Serves as the joint capital of both Punjab and Haryana.",
    },
    "dnh_dd": {
        "name": "Dadra & Nagar Haveli and Daman & Diu", "type": "Union Territory", "capital": "Daman",
        "land_neighbors": ["gujarat", "maharashtra"],
        "countries": [], "coastal": True,
        "note": "Merged into a single UT in 2020; Dadra & Nagar Haveli is landlocked while Daman & Diu are coastal.",
    },
    "delhi": {
        "name": "Delhi (NCT)", "type": "Union Territory", "capital": "New Delhi",
        "land_neighbors": ["haryana", "uttar_pradesh"],
        "countries": [], "coastal": False, "note": "",
    },
    "jammu_kashmir": {
        "name": "Jammu & Kashmir", "type": "Union Territory", "capital": "Srinagar (summer) / Jammu (winter)",
        "land_neighbors": ["ladakh", "himachal_pradesh", "punjab"],
        "countries": ["Pakistan"], "coastal": False,
        "note": "Became a separate UT (split from Ladakh) in 2019.",
    },
    "ladakh": {
        "name": "Ladakh", "type": "Union Territory", "capital": "Leh",
        "land_neighbors": ["jammu_kashmir", "himachal_pradesh"],
        "countries": ["China", "Pakistan"], "coastal": False,
        "note": "India's highest and most sparsely populated UT; became separate from J&K in 2019.",
    },
    "lakshadweep": {
        "name": "Lakshadweep", "type": "Union Territory", "capital": "Kavaratti",
        "land_neighbors": [], "countries": [], "coastal": True,
        "note": "India's smallest UT — a coral-island archipelago with no land borders.",
    },
    "puducherry": {
        "name": "Puducherry", "type": "Union Territory", "capital": "Puducherry",
        "land_neighbors": ["tamil_nadu", "andhra_pradesh", "kerala"],
        "countries": [], "coastal": True,
        "note": "Made of 4 non-contiguous enclaves: Puducherry & Karaikal (in Tamil Nadu), Yanam (in Andhra Pradesh), Mahe (in Kerala).",
    },
}

# ── Capital-city coordinates (approximate) — used for the interactive map ──
CAPITAL_COORDS: dict[str, tuple[float, float]] = {
    "andhra_pradesh": (16.5131, 80.5165), "arunachal_pradesh": (27.0844, 93.6053),
    "assam": (26.1445, 91.7362), "bihar": (25.5941, 85.1376),
    "chhattisgarh": (21.2514, 81.6296), "goa": (15.4909, 73.8278),
    "gujarat": (23.2156, 72.6369), "haryana": (30.7333, 76.7794),
    "himachal_pradesh": (31.1048, 77.1734), "jharkhand": (23.3441, 85.3096),
    "karnataka": (12.9716, 77.5946), "kerala": (8.5241, 76.9366),
    "madhya_pradesh": (23.2599, 77.4126), "maharashtra": (19.0760, 72.8777),
    "manipur": (24.8170, 93.9368), "meghalaya": (25.5788, 91.8933),
    "mizoram": (23.7271, 92.7176), "nagaland": (25.6751, 94.1086),
    "odisha": (20.2961, 85.8245), "punjab": (30.7333, 76.7794),
    "rajasthan": (26.9124, 75.7873), "sikkim": (27.3389, 88.6065),
    "tamil_nadu": (13.0827, 80.2707), "telangana": (17.3850, 78.4867),
    "tripura": (23.8315, 91.2868), "uttar_pradesh": (26.8467, 80.9462),
    "uttarakhand": (30.3165, 78.0322), "west_bengal": (22.5726, 88.3639),
    "andaman_nicobar": (11.6234, 92.7265), "chandigarh": (30.7333, 76.7794),
    "dnh_dd": (20.3974, 72.8328), "delhi": (28.6139, 77.2090),
    "jammu_kashmir": (34.0837, 74.7973), "ladakh": (34.1526, 77.5771),
    "lakshadweep": (10.5669, 72.6420), "puducherry": (11.9416, 79.8083),
}

# ── Approximate international border lengths (published MEA/BSF figures) ──
BORDER_LENGTHS_KM: list[dict] = [
    {"country": "Bangladesh", "length_km": 4096, "note": "India's longest international border; fenced in most stretches."},
    {"country": "China", "length_km": 3488, "note": "The Line of Actual Control (LAC) — not a mutually agreed/demarcated boundary."},
    {"country": "Pakistan", "length_km": 3323, "note": "Includes the Line of Control (LoC) in Jammu & Kashmir."},
    {"country": "Nepal", "length_km": 1751, "note": "Largely open border — free movement permitted under the 1950 Treaty."},
    {"country": "Myanmar", "length_km": 1643, "note": "Runs through dense hill/forest terrain across the Northeast."},
    {"country": "Bhutan", "length_km": 699, "note": "India's shortest major land border, entirely in the Northeast/Sikkim."},
]

# ── Major official land border crossings / Integrated Check Posts (ICPs) ──
BORDER_CHECKPOINTS: list[dict] = [
    {
        "name": "Attari–Wagah", "state_key": "punjab", "country": "Pakistan",
        "note": "India's best-known land crossing; famous for the daily Beating Retreat ceremony. Main road/rail trade and pedestrian crossing on the Amritsar–Lahore route.",
    },
    {
        "name": "Petrapole–Benapole", "state_key": "west_bengal", "country": "Bangladesh",
        "note": "India's largest land port by trade volume, on the Kolkata–Dhaka route.",
    },
    {
        "name": "Akhaura–Agartala", "state_key": "tripura", "country": "Bangladesh",
        "note": "Key crossing linking Tripura's capital directly to eastern Bangladesh.",
    },
    {
        "name": "Dawki (Tamabil)", "state_key": "meghalaya", "country": "Bangladesh",
        "note": "Crossing near the Dawki river, used for both trade and limited passenger movement.",
    },
    {
        "name": "Raxaul–Birgunj", "state_key": "bihar", "country": "Nepal",
        "note": "One of the busiest India–Nepal trade routes, linking Bihar to Nepal's Birgunj dry port.",
    },
    {
        "name": "Sunauli", "state_key": "uttar_pradesh", "country": "Nepal",
        "note": "A major open-border crossing on the Gorakhpur–Kathmandu route.",
    },
    {
        "name": "Jaigaon–Phuentsholing", "state_key": "west_bengal", "country": "Bhutan",
        "note": "The principal road gateway into Bhutan, twin towns straddling the border.",
    },
    {
        "name": "Nathu La", "state_key": "sikkim", "country": "China",
        "note": "A historic Silk Route pass reopened in 2006 for limited, seasonal border trade only (not a general public crossing).",
    },
    {
        "name": "Moreh–Tamu", "state_key": "manipur", "country": "Myanmar",
        "note": "A land customs station and key link on the India–Myanmar–Thailand trilateral highway corridor.",
    },
    {
        "name": "Zokhawthar–Rih", "state_key": "mizoram", "country": "Myanmar",
        "note": "A border trade point linking Champhai district to Myanmar's Chin State.",
    },
]

