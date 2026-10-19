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
