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

# ── District-level border detail ──
# Best-effort, non-exhaustive reference: the major/well-established districts that lie
# directly along each state-to-state or state-to-UT border. India's states periodically
# carve out new districts (e.g. Andhra Pradesh went from 13 to 26 districts in 2022;
# Assam, Chhattisgarh, Madhya Pradesh, Uttar Pradesh and others have also split districts
# in recent years) — this list uses commonly-referenced, long-established district names
# and may not capture every newly created district exactly. Keyed by the two region keys
# joined with "|" in alphabetical order; look up via border_districts_for().
BORDER_DISTRICTS: dict[str, dict] = {
    "andhra_pradesh|odisha": {"andhra_pradesh": ["Srikakulam", "Vizianagaram"], "odisha": ["Gajapati", "Rayagada", "Koraput", "Malkangiri"]},
    "andhra_pradesh|chhattisgarh": {"andhra_pradesh": ["Visakhapatnam (Agency area)"], "chhattisgarh": ["Sukma", "Bijapur"]},
    "andhra_pradesh|telangana": {"andhra_pradesh": ["Guntur", "Prakasam", "Krishna"], "telangana": ["Khammam", "Nalgonda", "Suryapet"]},
    "andhra_pradesh|karnataka": {"andhra_pradesh": ["Anantapur", "Kurnool"], "karnataka": ["Ballari", "Raichur"]},
    "andhra_pradesh|tamil_nadu": {"andhra_pradesh": ["Chittoor", "SPSR Nellore"], "tamil_nadu": ["Vellore", "Tiruvallur", "Tiruvannamalai"]},
    "andhra_pradesh|puducherry": {"andhra_pradesh": ["East Godavari"], "puducherry": ["Yanam"]},
    "arunachal_pradesh|assam": {"arunachal_pradesh": ["Tirap", "Changlang", "Papum Pare", "Lower Subansiri", "Siang"], "assam": ["Dhemaji", "Lakhimpur", "Sonitpur", "Charaideo", "Tinsukia"]},
    "arunachal_pradesh|nagaland": {"arunachal_pradesh": ["Tirap", "Changlang"], "nagaland": ["Mon", "Tuensang"]},
    "assam|nagaland": {"assam": ["Sivasagar", "Charaideo", "Jorhat", "Golaghat"], "nagaland": ["Mon", "Wokha", "Zunheboto"]},
    "assam|manipur": {"assam": ["Cachar", "Karbi Anglong"], "manipur": ["Tamenglong", "Jiribam"]},
    "assam|mizoram": {"assam": ["Cachar", "Hailakandi"], "mizoram": ["Kolasib", "Mamit"]},
    "assam|tripura": {"assam": ["Cachar", "Karimganj"], "tripura": ["Dhalai", "Unakoti", "North Tripura"]},
    "assam|meghalaya": {"assam": ["Kamrup", "Kamrup Metropolitan", "Goalpara", "Dhubri", "Karbi Anglong", "Cachar"], "meghalaya": ["West Garo Hills", "South Garo Hills", "Ri Bhoi", "East Khasi Hills", "Jaintia Hills"]},
    "assam|west_bengal": {"assam": ["Dhubri", "Kokrajhar"], "west_bengal": ["Cooch Behar", "Alipurduar", "Jalpaiguri"]},
    "bihar|uttar_pradesh": {"bihar": ["West Champaran", "East Champaran", "Siwan", "Gopalganj", "Kaimur", "Buxar", "Rohtas"], "uttar_pradesh": ["Maharajganj", "Kushinagar", "Deoria", "Ballia", "Ghazipur", "Sonbhadra"]},
    "bihar|jharkhand": {"bihar": ["Banka", "Jamui", "Nawada", "Gaya", "Aurangabad", "Rohtas"], "jharkhand": ["Deoghar", "Godda", "Dumka", "Giridih", "Hazaribagh", "Chatra", "Palamu"]},
    "bihar|west_bengal": {"bihar": ["Kishanganj", "Purnia", "Katihar"], "west_bengal": ["Uttar Dinajpur", "Malda"]},
    "chhattisgarh|madhya_pradesh": {"chhattisgarh": ["Kabirdham", "Balod", "Rajnandgaon", "Mungeli", "Surguja", "Korea"], "madhya_pradesh": ["Balaghat", "Dindori", "Anuppur", "Shahdol", "Sidhi"]},
    "chhattisgarh|uttar_pradesh": {"chhattisgarh": ["Korea"], "uttar_pradesh": ["Sonbhadra"]},
    "chhattisgarh|jharkhand": {"chhattisgarh": ["Jashpur", "Surguja"], "jharkhand": ["Gumla", "Simdega", "Latehar"]},
    "chhattisgarh|odisha": {"chhattisgarh": ["Raigarh", "Jashpur", "Mahasamund", "Bastar"], "odisha": ["Jharsuguda", "Sundargarh", "Nuapada", "Bargarh", "Nabarangpur", "Kalahandi"]},
    "chhattisgarh|telangana": {"chhattisgarh": ["Bijapur", "Sukma"], "telangana": ["Bhadradri Kothagudem", "Mulugu"]},
    "chhattisgarh|maharashtra": {"chhattisgarh": ["Rajnandgaon", "Balod", "Gariaband", "Bastar"], "maharashtra": ["Gondia", "Gadchiroli"]},
    "goa|maharashtra": {"goa": ["North Goa"], "maharashtra": ["Sindhudurg"]},
    "goa|karnataka": {"goa": ["North Goa", "South Goa"], "karnataka": ["Belagavi", "Uttara Kannada"]},
    "gujarat|rajasthan": {"gujarat": ["Banaskantha", "Patan"], "rajasthan": ["Sirohi", "Barmer", "Jalore"]},
    "gujarat|madhya_pradesh": {"gujarat": ["Chhota Udepur", "Dahod", "Panchmahal"], "madhya_pradesh": ["Jhabua", "Alirajpur", "Dhar"]},
    "gujarat|maharashtra": {"gujarat": ["Valsad", "Dang", "Tapi", "Surat"], "maharashtra": ["Nashik", "Dhule", "Nandurbar"]},
    "dnh_dd|gujarat": {"dnh_dd": ["Dadra & Nagar Haveli", "Daman"], "gujarat": ["Valsad"]},
    "haryana|punjab": {"haryana": ["Ambala", "Fatehabad", "Sirsa"], "punjab": ["Patiala", "Sangrur", "Mansa", "Bathinda"]},
    "haryana|himachal_pradesh": {"haryana": ["Panchkula", "Yamunanagar"], "himachal_pradesh": ["Sirmaur", "Solan"]},
    "haryana|uttar_pradesh": {"haryana": ["Faridabad", "Panipat", "Yamunanagar"], "uttar_pradesh": ["Saharanpur", "Muzaffarnagar", "Baghpat", "Meerut", "Gautam Buddh Nagar"]},
    "haryana|rajasthan": {"haryana": ["Mahendragarh", "Bhiwani", "Sirsa"], "rajasthan": ["Jhunjhunu", "Churu", "Hanumangarh"]},
    "delhi|haryana": {"haryana": ["Faridabad", "Gurugram", "Jhajjar", "Sonipat"], "delhi": ["North West Delhi", "South West Delhi", "South Delhi", "East Delhi"]},
    "chandigarh|haryana": {"haryana": ["Panchkula"], "chandigarh": ["Chandigarh (UT)"]},
    "himachal_pradesh|jammu_kashmir": {"himachal_pradesh": ["Chamba"], "jammu_kashmir": ["Kishtwar", "Doda", "Udhampur"]},
    "himachal_pradesh|ladakh": {"himachal_pradesh": ["Lahaul & Spiti"], "ladakh": ["Kargil", "Leh"]},
    "himachal_pradesh|punjab": {"himachal_pradesh": ["Una", "Hamirpur", "Kangra"], "punjab": ["Hoshiarpur", "Rupnagar"]},
    "himachal_pradesh|uttarakhand": {"himachal_pradesh": ["Sirmaur"], "uttarakhand": ["Dehradun", "Uttarkashi"]},
    "jharkhand|west_bengal": {"jharkhand": ["Sahibganj", "Pakur", "Dumka", "East Singhbhum"], "west_bengal": ["Malda", "Birbhum", "Bankura", "Purulia", "West Medinipur"]},
    "jharkhand|odisha": {"jharkhand": ["West Singhbhum", "Saraikela Kharsawan"], "odisha": ["Mayurbhanj", "Kendujhar", "Sundargarh"]},
    "jharkhand|uttar_pradesh": {"jharkhand": ["Garhwa"], "uttar_pradesh": ["Sonbhadra"]},
    "karnataka|maharashtra": {"karnataka": ["Belagavi", "Bidar", "Kalaburagi"], "maharashtra": ["Kolhapur", "Sangli", "Solapur", "Latur"]},
    "karnataka|telangana": {"karnataka": ["Raichur", "Kalaburagi", "Bidar"], "telangana": ["Narayanpet", "Vikarabad", "Jogulamba Gadwal"]},
    "karnataka|tamil_nadu": {"karnataka": ["Chamarajanagar", "Bengaluru Rural", "Kolar"], "tamil_nadu": ["Dharmapuri", "Krishnagiri", "Nilgiris", "Coimbatore"]},
    "karnataka|kerala": {"karnataka": ["Dakshina Kannada", "Kodagu", "Mysuru"], "kerala": ["Kasaragod", "Wayanad", "Kannur"]},
    "kerala|tamil_nadu": {"kerala": ["Palakkad", "Idukki", "Wayanad"], "tamil_nadu": ["Coimbatore", "Theni", "Nilgiris"]},
    "kerala|puducherry": {"kerala": ["Kozhikode"], "puducherry": ["Mahe"]},
    "madhya_pradesh|uttar_pradesh": {"madhya_pradesh": ["Sidhi", "Panna", "Chhatarpur", "Tikamgarh"], "uttar_pradesh": ["Mirzapur", "Banda", "Chitrakoot", "Mahoba"]},
    "madhya_pradesh|maharashtra": {"madhya_pradesh": ["Betul", "Chhindwara", "Balaghat"], "maharashtra": ["Amravati", "Nagpur", "Bhandara"]},
    "madhya_pradesh|rajasthan": {"madhya_pradesh": ["Neemuch", "Mandsaur", "Jhabua"], "rajasthan": ["Chittorgarh", "Pratapgarh", "Banswara"]},
    "maharashtra|telangana": {"maharashtra": ["Chandrapur", "Gadchiroli", "Nanded"], "telangana": ["Adilabad", "Komaram Bheem Asifabad"]},
    "dnh_dd|maharashtra": {"dnh_dd": ["Dadra & Nagar Haveli"], "maharashtra": ["Palghar"]},
    "manipur|nagaland": {"manipur": ["Senapati", "Tamenglong"], "nagaland": ["Phek", "Kiphire"]},
    "manipur|mizoram": {"manipur": ["Churachandpur"], "mizoram": ["Champhai"]},
    "mizoram|tripura": {"mizoram": ["Mamit"], "tripura": ["South Tripura", "Dhalai"]},
    "odisha|west_bengal": {"odisha": ["Balasore", "Mayurbhanj"], "west_bengal": ["Paschim Medinipur", "Jhargram"]},
    "jammu_kashmir|punjab": {"punjab": ["Gurdaspur", "Pathankot"], "jammu_kashmir": ["Kathua"]},
    "punjab|rajasthan": {"punjab": ["Fazilka", "Sri Muktsar Sahib"], "rajasthan": ["Sri Ganganagar"]},
    "chandigarh|punjab": {"punjab": ["Sahibzada Ajit Singh Nagar (Mohali)"], "chandigarh": ["Chandigarh (UT)"]},
    "rajasthan|uttar_pradesh": {"rajasthan": ["Dholpur", "Bharatpur", "Karauli"], "uttar_pradesh": ["Agra", "Etah", "Mainpuri"]},
    "sikkim|west_bengal": {"sikkim": ["South Sikkim", "West Sikkim"], "west_bengal": ["Darjeeling", "Kalimpong"]},
    "puducherry|tamil_nadu": {"tamil_nadu": ["Villupuram", "Cuddalore"], "puducherry": ["Puducherry", "Karaikal"]},
    "uttar_pradesh|uttarakhand": {"uttar_pradesh": ["Saharanpur", "Bijnor", "Pilibhit", "Lakhimpur Kheri"], "uttarakhand": ["Dehradun", "Udham Singh Nagar", "Nainital"]},
    "delhi|uttar_pradesh": {"uttar_pradesh": ["Ghaziabad", "Gautam Buddh Nagar"], "delhi": ["North East Delhi", "East Delhi", "South East Delhi"]},
    "jammu_kashmir|ladakh": {"jammu_kashmir": ["Ganderbal", "Kishtwar"], "ladakh": ["Kargil", "Leh"]},
}


def border_districts_for(key_a: str, key_b: str) -> dict | None:
    """Look up the curated district lists for a border pair, regardless of key order."""
    return BORDER_DISTRICTS.get("|".join(sorted([key_a, key_b])))


# ── Enclaves & exclaves — territory of one state/UT surrounded by another ──
ENCLAVES: list[dict] = [
    {
        "title": "Puducherry's 4 non-contiguous regions",
        "region_key": "puducherry",
        "description": "Puducherry (the UT) is made of 4 separate pieces of land with no shared boundary: Puducherry town & Karaikal sit inside Tamil Nadu, Yanam sits inside Andhra Pradesh, and Mahe sits inside Kerala.",
    },
    {
        "title": "Yanam — inside Andhra Pradesh",
        "region_key": "andhra_pradesh",
        "description": "Yanam, a Puducherry enclave on the Godavari delta, is completely surrounded by Andhra Pradesh's East Godavari district.",
    },
    {
        "title": "Mahe — inside Kerala",
        "region_key": "kerala",
        "description": "Mahe, a Puducherry enclave on the Malabar coast, is completely surrounded by Kerala's Kozhikode district.",
    },
    {
        "title": "Karaikal — inside Tamil Nadu",
        "region_key": "tamil_nadu",
        "description": "Karaikal, a Puducherry enclave on the Coromandel coast, is completely surrounded by Tamil Nadu's Villupuram/Cuddalore districts.",
    },
    {
        "title": "Dadra & Nagar Haveli and Daman & Diu — a 2-part, non-contiguous UT",
        "region_key": "dnh_dd",
        "description": "Merged into a single UT in 2020, Dadra & Nagar Haveli (landlocked, surrounded by Gujarat/Maharashtra) and Daman & Diu (two separate coastal pockets on the Gujarat coast) still do not physically touch each other.",
    },
    {
        "title": "Chandigarh — a shared capital, but its own separate UT",
        "region_key": "chandigarh",
        "description": "Chandigarh serves as the joint capital of both Punjab and Haryana, yet is itself neither — a compact Union Territory wedged between the two states it administers for.",
    },
]

