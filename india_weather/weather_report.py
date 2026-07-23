"""
India Weather Report Orchestrator
Generates india_weather/weathers/india_weather_report.html — a self-contained
live dashboard that uses JavaScript to fetch wttr.in data directly in the
browser for all 28 Indian states and their major districts.
Auto-refreshes every 5 minutes with a visible countdown.
No server required.
"""

from __future__ import annotations
from pathlib import Path

OUTPUT_FILE = Path(__file__).parent / "weathers" / "india_weather_report.html"

# ── State registry ──────────────────────────────────────────────────────────
# Each entry: (module_id, display_name, accent_colour, [all official districts])
STATES = [
    ("andhra_pradesh", "Andhra Pradesh", "#e84393", [
        "Alluri Sitharama Raju","Anakapalli","Ananthapuramu","Annamayya","Bapatla",
        "Chittoor","Dr. B.R. Ambedkar Konaseema","East Godavari","Eluru","Guntur",
        "Kakinada","Krishna","Kurnool","Nandyal","NTR","Palnadu",
        "Parvathipuram Manyam","Prakasam","Sri Potti Sriramulu Nellore",
        "Sri Sathya Sai","Srikakulam","Tirupati","Visakhapatnam","Vizianagaram",
        "West Godavari","YSR",
    ]),
    ("arunachal_pradesh", "Arunachal Pradesh", "#6366f1", [
        "Anjaw","Bichom","Changlang","Dibang Valley","East Kameng","East Siang",
        "Itanagar","Kamle","Kra Daadi","Kurung Kumey","Lepa Rada",
        "Lohit","Longding","Lower Dibang Valley","Lower Siang","Lower Subansiri",
        "Namsai","Pakke-Kessang","Papum Pare","Shi Yomi","Siang","Tawang","Tirap",
        "Upper Siang","Upper Subansiri","West Kameng","West Siang",
    ]),
    ("assam", "Assam", "#10b981", [
        "Bajali","Baksa","Barpeta","Biswanath","Bongaigaon","Cachar","Charaideo",
        "Chirang","Darrang","Dhemaji","Dhubri","Dibrugarh","Dima Hasao","Goalpara",
        "Golaghat","Hailakandi","Hojai","Jorhat","Kamrup","Kamrup Metropolitan",
        "Karbi Anglong","Kokrajhar","Lakhimpur","Majuli","Marigaon","Morigaon",
        "Nagaon","Nalbari","Sivasagar","Sonitpur","South Salmara-Mankachar",
        "Tamulpur","Tinsukia","Udalguri","West Karbi Anglong",
    ]),
    ("bihar", "Bihar", "#f59e0b", [
        "Araria","Arwal","Aurangabad","Banka","Begusarai","Bhagalpur","Bhojpur",
        "Buxar","Darbhanga","Gaya","Gopalganj","Jamui","Jehanabad","Kaimur",
        "Katihar","Khagaria","Kishanganj","Lakhisarai","Madhepura","Madhubani",
        "Munger","Muzaffarpur","Nalanda","Nawada","Pashchim Champaran","Patna",
        "Purbi Champaran","Purnia","Rohtas","Saharsa","Samastipur","Saran",
        "Sheikhpura","Sheohar","Sitamarhi","Siwan","Supaul","Vaishali",
    ]),
    ("chhattisgarh", "Chhattisgarh", "#ef4444", [
        "Balod","Balodabazar-Bhatapara","Balrampur-Ramanujganj","Bastar","Bemetara",
        "Bijapur","Bilaspur","Dakshin Bastar Dantewada","Dhamtari","Durg",
        "Gariyaband","Gaurela-Pendra-Marwahi","Janjgir-Champa","Jashpur",
        "Kabirdham","Khairagarh-Chhindgarh-Gandai","Kondagaon","Korba","Korea",
        "Mahasamund","Manendragarh-Chirmiri-Bharatpur",
        "Mohla","Mungeli","Narayanpur","Raigarh","Raipur",
        "Rajnandgaon","Sakti","Sarangarh-Bilaigarh","Sukma","Surajpur","Surguja",
    ]),
    ("goa", "Goa", "#06b6d4", [
        "North Goa","South Goa",
    ]),
    ("gujarat", "Gujarat", "#f97316", [
        "Ahmedabad","Amreli","Anand","Arvalli","Banas Kantha","Bharuch","Bhavnagar",
        "Botad","Chhota Udaipur","Dahod","Dangs","Devbhumi Dwarka","Gandhinagar",
        "Gir Somnath","Jamnagar","Junagadh","Kachchh","Kheda","Mahesana",
        "Mahisagar","Morbi","Narmada","Navsari","Panch Mahals","Patan","Porbandar",
        "Rajkot","Sabarkantha","Surat","Surendranagar","Tapi","Vadodara","Valsad",
    ]),
    ("haryana", "Haryana", "#84cc16", [
        "Ambala","Bhiwani","Charkhi Dadri","Faridabad","Fatehabad","Gurugram",
        "Hisar","Jhajjar","Jind","Kaithal","Karnal","Kurukshetra","Mahendragarh",
        "Nuh","Palwal","Panchkula","Panipat","Rewari","Rohtak","Sirsa","Sonipat",
        "Yamunanagar",
    ]),
    ("himachal_pradesh", "Himachal Pradesh", "#3b82f6", [
        "Bilaspur","Chamba","Hamirpur","Kangra","Kinnaur","Kullu",
        "Lahaul and Spiti","Mandi","Shimla","Sirmaur","Solan","Una",
    ]),
    ("jharkhand", "Jharkhand", "#a855f7", [
        "Bokaro","Chatra","Deoghar","Dhanbad","Dumka","East Singhbhum","Garhwa",
        "Giridih","Godda","Gumla","Hazaribagh","Jamtara","Khunti","Koderma",
        "Latehar","Lohardaga","Pakur","Palamu","Ramgarh","Ranchi","Sahebganj",
        "Saraikela Kharsawan","Simdega","West Singhbhum",
    ]),
    ("karnataka", "Karnataka", "#ec4899", [
        "Bagalkote","Ballari","Belagavi","Bengaluru Rural","Bengaluru Urban",
        "Bidar","Chamarajanagara","Chikkaballapura","Chikkamagaluru","Chitradurga",
        "Dakshina Kannada","Davanagere","Dharwad","Gadag","Hassan","Haveri",
        "Kalaburagi","Kodagu","Kolar","Koppal","Mandya","Mysuru","Raichur",
        "Ramanagara","Shivamogga","Tumakuru","Udupi","Uttara Kannada","Vijayapura",
        "Vijayanagara","Yadgir",
    ]),
    ("kerala", "Kerala", "#14b8a6", [
        "Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam","Kottayam",
        "Kozhikode","Malappuram","Palakkad","Pathanamthitta","Thiruvananthapuram",
        "Thrissur","Wayanad",
    ]),
    ("madhya_pradesh", "Madhya Pradesh", "#f43f5e", [
        "Agar-Malwa","Alirajpur","Anuppur","Ashoknagar","Balaghat","Barwani",
        "Betul","Bhind","Bhopal","Burhanpur","Chhatarpur","Chhindwara","Damoh",
        "Datia","Dewas","Dhar","Dindori","Guna","Gwalior","Harda","Indore",
        "Jabalpur","Jhabua","Katni","Khandwa","Khargone","Maihar","Mandla",
        "Mandsaur","Mauganj","Morena","Nagda","Narsinghpur","Niwari","Panna",
        "Pandhurna","Raisen","Rajgarh","Ratlam","Rewa","Sagar","Satna","Sehore",
        "Seoni","Shahdol","Shajapur","Sheopur","Shivpuri","Sidhi","Singrauli",
        "Tikamgarh","Ujjain","Umaria","Vidisha","Chachaura",
    ]),
    ("maharashtra", "Maharashtra", "#8b5cf6", [
        "Ahilyanagar","Akola","Amravati","Beed","Bhandara","Buldhana","Chandrapur",
        "Chhatrapati Sambhajinagar","Dharashiv","Dhule","Gadchiroli","Gondia",
        "Hingoli","Jalgaon","Jalna","Kolhapur","Latur","Mumbai","Mumbai Suburban",
        "Nagpur","Nanded","Nandurbar","Nashik","Palghar","Parbhani","Pune",
        "Raigad","Ratnagiri","Sangli","Satara","Sindhudurg","Solapur","Thane",
        "Wardha","Washim","Yavatmal",
    ]),
    ("manipur", "Manipur", "#0ea5e9", [
        "Bishnupur","Chandel","Churachandpur","Imphal East","Imphal West",
        "Jiribam","Kakching","Kamjong","Kangpokpi","Noney","Pherzawl","Senapati",
        "Tamenglong","Tengnoupal","Thoubal","Ukhrul",
    ]),
    ("meghalaya", "Meghalaya", "#22c55e", [
        "East Garo Hills","East Jaintia Hills","East Khasi Hills",
        "Eastern West Khasi Hills","North Garo Hills","Ri Bhoi","South Garo Hills",
        "South West Garo Hills","South West Khasi Hills","West Garo Hills",
        "West Jaintia Hills","West Khasi Hills",
    ]),
    ("mizoram", "Mizoram", "#eab308", [
        "Aizawl","Champhai","Hnahthial","Khawzawl","Kolasib","Lawngtlai","Lunglei",
        "Mamit","Saitual","Serchhip","Siaha",
    ]),
    ("nagaland", "Nagaland", "#64748b", [
        "Chumoukedima","Dimapur","Kiphire","Kohima","Longleng","Mokokchung","Mon Nagaland",
        "Niuland","Noklak","Peren","Phek","Shamator","Tseminyu","Tuensang","Wokha",
        "Zunheboto",
    ]),
    ("odisha", "Odisha", "#fb923c", [
        "Angul","Balangir","Balasore","Bargarh","Bhadrak","Boudh","Cuttack",
        "Deogarh","Dhenkanal","Gajapati","Ganjam","Jagatsinghpur","Jajpur",
        "Jharsuguda","Kalahandi","Kandhamal","Kendrapara","Kendujhar","Khordha",
        "Koraput","Malkangiri","Mayurbhanj","Nabarangpur","Nayagarh","Nuapada",
        "Puri","Rayagada","Sambalpur","Subarnapur","Sundargarh",
    ]),
    ("punjab", "Punjab", "#facc15", [
        "Amritsar","Barnala","Bathinda","Faridkot","Fatehgarh Sahib","Fazilka",
        "Ferozepur","Gurdaspur","Hoshiarpur","Jalandhar","Kapurthala","Ludhiana",
        "Malerkotla","Mansa","Moga","Pathankot","Patiala","Rupnagar","S.A.S. Nagar",
        "Sangrur","Shahid Bhagat Singh Nagar","Sri Muktsar Sahib","Tarn Taran",
    ]),
    ("rajasthan", "Rajasthan", "#f97316", [
        "Ajmer","Alwar","Anupgarh","Balotra","Banswara","Baran","Barmer","Beawar",
        "Bharatpur","Bhilwara","Bikaner","Bundi","Chittorgarh","Churu","Dausa",
        "Deeg","Dholpur","Didwana-Kuchaman","Dudu","Dungarpur","Gangapur City",
        "Hanumangarh","Jaipur","Jaipur Rural","Jaisalmer","Jalore","Jhalawar",
        "Jhunjhunu","Jodhpur","Jodhpur Rural","Karauli","Kekri","Khairthal-Tijara",
        "Kota","Kotputli-Behror","Nagaur","Neem Ka Thana","Pali","Phalodi",
        "Pratapgarh","Rajsamand","Salumbar","Sanchore","Sawai Madhopur","Shahpura",
        "Sikar","Sirohi","Sri Ganganagar","Tonk","Udaipur",
    ]),
    ("sikkim", "Sikkim", "#2dd4bf", [
        "East Sikkim","North Sikkim","Pakyong","Soreng","South Sikkim","West Sikkim",
    ]),
    ("tamil_nadu", "Tamil Nadu", "#0ea5e9", [
        "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore","Dharmapuri",
        "Dindigul","Erode","Kallakurichi","Kancheepuram","Kanyakumari","Karur",
        "Krishnagiri","Madurai","Mayiladuthurai","Nagapattinam","Namakkal",
        "Nilgiris","Perambalur","Pudukkottai","Ramanathapuram","Ranipet","Salem",
        "Sivaganga","Tenkasi","Thanjavur","Theni","Thoothukudi","Tiruchirappalli",
        "Tirunelveli","Tirupattur","Tiruppur","Tiruvallur","Tiruvannamalai",
        "Tiruvarur","Vellore","Viluppuram","Virudhunagar",
    ]),
    ("telangana", "Telangana", "#dc2626", [
        "Adilabad","Bhadradri Kothagudem","Hanumakonda","Hyderabad","Jagitial",
        "Jangaon","Jayashankar Bhupalpally","Jogulamba Gadwal","Kamareddy",
        "Karimnagar","Khammam","Kumuram Bheem Asifabad","Mahabubabad","Mahbubnagar",
        "Mancherial","Medak","Medchal-Malkajgiri","Mulugu","Nagarkurnool","Nalgonda",
        "Narayanpet","Nirmal","Nizamabad","Peddapalli","Rajanna Sircilla",
        "Ranga Reddy","Sangareddy","Siddipet","Suryapet","Vikarabad","Wanaparthy",
        "Warangal Rural","Yadadri Bhuvanagiri",
    ]),
    ("tripura", "Tripura", "#7c3aed", [
        "Dhalai","Gomati","Khowai","North Tripura","Sepahijala","South Tripura",
        "Unakoti","West Tripura",
    ]),
    ("uttar_pradesh", "Uttar Pradesh", "#16a34a", [
        "Agra","Aligarh","Ambedkar Nagar","Amethi","Amroha","Auraiya","Ayodhya",
        "Azamgarh","Baghpat","Bahraich","Ballia","Balrampur","Banda Uttar Pradesh","Barabanki",
        "Bareilly","Basti","Bhadohi","Bijnor","Budaun","Bulandshahr","Chandauli",
        "Chitrakoot","Deoria","Etah","Etawah","Farrukhabad","Fatehpur","Firozabad",
        "Gautam Buddha Nagar","Ghaziabad","Ghazipur","Gonda","Gorakhpur","Hamirpur",
        "Hapur","Hardoi","Hathras","Jalaun","Jaunpur","Jhansi","Kannauj",
        "Kanpur Dehat","Kanpur Nagar","Kasganj","Kaushambi","Lakhimpur Kheri",
        "Kushinagar","Lalitpur","Lucknow","Maharajganj","Mahoba","Mainpuri",
        "Mathura","Mau","Meerut","Mirzapur","Moradabad","Muzaffarnagar","Pilibhit",
        "Pratapgarh","Prayagraj","Raebareli","Rampur","Saharanpur","Sambhal",
        "Sant Kabir Nagar","Shahjahanpur","Shamli","Shravasti","Siddharthnagar",
        "Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi",
    ]),
    ("uttarakhand", "Uttarakhand", "#0369a1", [
        "Almora","Bageshwar","Chamoli","Champawat","Dehradun","Haridwar","Nainital",
        "Pauri Garhwal","Pithoragarh","Rudraprayag","Tehri Garhwal",
        "Udham Singh Nagar","Uttarkashi",
    ]),
    ("west_bengal", "West Bengal", "#be185d", [
        "Alipurduar","Bankura","Birbhum","Cooch Behar","Dakshin Dinajpur",
        "Darjeeling","Hooghly","Howrah","Jalpaiguri","Jhargram","Kalimpong",
        "Kolkata","Malda","Murshidabad","Nadia","North 24 Parganas",
        "Paschim Bardhaman","Paschim Medinipur","Purba Bardhaman","Purba Medinipur",
        "Purulia","South 24 Parganas","Uttar Dinajpur",
    ]),
]

# ── Union Territories registry ─────────────────────────────────────────────
# Each entry: (module_id, display_name, accent_colour, [all official districts])
UNION_TERRITORIES = [
    ("andaman_nicobar", "Andaman & Nicobar Islands", "#38bdf8", [
        "Nicobars", "North and Middle Andaman", "South Andaman",
    ]),
    ("chandigarh", "Chandigarh", "#a3e635", [
        "Chandigarh",
    ]),
    ("dnh_dd", "Dadra & Nagar Haveli and Daman & Diu", "#e879f9", [
        "Dadra and Nagar Haveli", "Daman", "Diu",
    ]),
    ("delhi", "Delhi (NCT)", "#f87171", [
        "Central Delhi","East Delhi","New Delhi","North Delhi",
        "North East Delhi","North West Delhi","Shahdara",
        "South Delhi","South East Delhi","South West Delhi","West Delhi",
    ]),
    ("jammu_kashmir", "Jammu and Kashmir", "#818cf8", [
        "Anantnag","Bandipora","Baramulla","Budgam","Doda","Ganderbal",
        "Jammu","Kathua","Kishtwar","Kulgam","Kupwara","Poonch","Pulwama",
        "Rajouri","Ramban","Reasi","Samba","Shopian","Srinagar","Udhampur",
    ]),
    ("ladakh", "Ladakh", "#94a3b8", [
        "Kargil", "Leh",
    ]),
    ("lakshadweep", "Lakshadweep", "#34d399", [
        "Kavaratti", "Agatti", "Minicoy", "Amini",
    ]),
    ("puducherry", "Puducherry", "#fb7185", [
        "Karaikal", "Mahe", "Puducherry", "Yanam",
    ]),
]

# Combined list for HTML generation (states first, then UTs)
ALL_REGIONS = STATES + UNION_TERRITORIES


def _build_states_js() -> str:
    """Return the JavaScript STATES + UNION_TERRITORIES array literals."""
    lines = ["  const STATES = ["]
    for sid, name, color, cities in ALL_REGIONS:
        cities_js = ", ".join(f'"{c}"' for c in cities)
        lines.append(f'    {{ id: "{sid}", name: "{name}", color: "{color}", cities: [{cities_js}] }},')
    lines.append("  ];")
    # Expose UT ids so the JS can render the separator
    ut_ids = [f'"{sid}"' for sid, *_ in UNION_TERRITORIES]
    lines.append(f"  const UT_IDS = new Set([{', '.join(ut_ids)}]);")
    return "\n".join(lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>India Weather Dashboard — 28 States &amp; 8 Union Territories</title>
  <meta name="theme-color" content="#6366f1"/>
  <meta name="mobile-web-app-capable" content="yes"/>
  <meta name="apple-mobile-web-app-capable" content="yes"/>
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
  <meta name="apple-mobile-web-app-title" content="IndiaWx"/>
  <link rel="manifest" href="/manifest.json"/>
  <link rel="apple-touch-icon" href="/static/icon-192.png"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: "Inter", "Segoe UI", system-ui, sans-serif;
      background: #060b18;
      min-height: 100vh;
      color: #e2e8f0;
      padding: 0 0 4rem;
      overflow-x: hidden;
    }}

    /* ── Animated mesh background ── */
    body::before {{
      content: "";
      position: fixed; inset: 0; z-index: -1; pointer-events: none;
      background:
        radial-gradient(ellipse 80% 60% at 20% 10%,  rgba(99,102,241,.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%,  rgba(16,185,129,.12) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 60% 30%,  rgba(245,158,11,.08) 0%, transparent 50%),
        linear-gradient(160deg, #060b18 0%, #0b1528 40%, #0c0c22 70%, #060b18 100%);
      animation: bg-shift 20s ease-in-out infinite alternate;
    }}
    @keyframes bg-shift {{
      0%   {{ background-position: 0% 0%, 100% 100%, 50% 30%; }}
      100% {{ background-position: 10% 5%, 90% 90%, 55% 25%; }}
    }}

    /* ── Header ── */
    header {{
      background: rgba(6,11,24,.72);
      border-bottom: 1px solid rgba(255,255,255,.07);
      padding: 1.1rem 1.75rem;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: .8rem;
      position: sticky; top: 0; z-index: 200;
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      box-shadow: 0 4px 24px rgba(0,0,0,.4);
    }}
    /* India tricolor accent line */
    header::after {{
      content: "";
      position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
      background: linear-gradient(90deg, #FF9933 0% 33%, #ffffff 33% 66%, #138808 66% 100%);
      opacity: .55;
    }}
    .header-left h1 {{
      font-size: 1.5rem; font-weight: 900; letter-spacing: -.6px;
      background: linear-gradient(135deg, #e2e8f0 0%, #a5b4fc 50%, #818cf8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .header-left p  {{ font-size: .74rem; color: #64748b; margin-top: .2rem; }}
    .header-right   {{ display: flex; align-items: center; gap: .65rem; flex-wrap: wrap; }}

    .status-pill {{
      display: flex; align-items: center; gap: .4rem;
      background: rgba(255,255,255,.05);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 999px; padding: .26rem .75rem;
      font-size: .72rem; color: #94a3b8; white-space: nowrap;
      backdrop-filter: blur(8px);
    }}
    .dot {{ width:8px; height:8px; border-radius:50%; background:#22c55e;
             box-shadow:0 0 8px #22c55e,0 0 16px rgba(34,197,94,.4);
             animation:pulse 2s infinite; flex-shrink:0; }}
    .dot.loading {{ background:#f59e0b; box-shadow:0 0 8px #f59e0b; }}
    @keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.5;transform:scale(.9)}} }}

    #refresh-btn {{
      background: linear-gradient(135deg,rgba(99,102,241,.3),rgba(139,92,246,.2));
      border: 1px solid rgba(139,92,246,.45);
      color: #c4b5fd; border-radius: 999px; padding: .32rem 1.1rem;
      font-size: .74rem; font-weight: 600; cursor: pointer;
      transition: all .2s; letter-spacing: .01em;
    }}
    #refresh-btn:hover    {{ background:linear-gradient(135deg,rgba(99,102,241,.5),rgba(139,92,246,.35)); box-shadow:0 0 12px rgba(139,92,246,.35); }}
    #refresh-btn:disabled {{ opacity: .4; cursor: not-allowed; }}

    /* ── State nav ── */
    #state-nav {{
      display: flex; flex-wrap: wrap; gap: .4rem;
      padding: 1.1rem 1.75rem .6rem; max-width: 1900px; margin: 0 auto;
    }}
    .state-btn {{
      border: 1px solid rgba(255,255,255,.1); color: #94a3b8;
      background: rgba(255,255,255,.04); border-radius: 999px;
      padding: .28rem .85rem; font-size: .72rem; font-weight: 500; cursor: pointer;
      transition: all .18s; white-space: nowrap;
    }}
    .state-btn:hover {{
      border-color: var(--c); color: var(--c);
      background: rgba(255,255,255,.07);
      box-shadow: 0 0 10px rgba(255,255,255,.05);
    }}
    .state-btn.active {{
      background: var(--c); color: #060b18; font-weight: 700;
      border-color: var(--c);
      box-shadow: 0 0 14px color-mix(in srgb, var(--c) 50%, transparent);
    }}
    .state-btn.ut-separator {{
      border: none; color: #334155; background: transparent;
      font-size: .62rem; text-transform: uppercase; letter-spacing: .1em;
      padding: .25rem .5rem; cursor: default; pointer-events: none;
    }}
    .state-btn.all-btn {{ border-color:rgba(99,102,241,.4); color:#818cf8; }}
    .state-btn.all-btn:hover {{ border-color:#818cf8; background:rgba(99,102,241,.12); color:#a5b4fc; }}
    .state-btn.all-btn.active {{ background:#818cf8; color:#060b18; }}

    /* ── State sections ── */
    .state-section  {{ max-width:1900px; margin:1.5rem auto 0; padding:0 1.75rem; }}
    .state-header   {{
      display:flex; align-items:center; gap:.75rem;
      margin-bottom:1rem; padding-bottom:.65rem;
      border-bottom:1px solid rgba(255,255,255,.07);
      position:relative;
    }}
    .state-header::before {{
      content:""; position:absolute; bottom:-1px; left:0;
      width:80px; height:2px;
      background:var(--accent);
      border-radius:99px;
      box-shadow:0 0 10px var(--accent);
    }}
    .state-header h2 {{ font-size:1.1rem; font-weight:800; color:var(--accent); }}
    .state-badge {{
      font-size:.68rem; background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.1);
      border-radius:.35rem; padding:.12rem .5rem; color:#64748b;
    }}
    .state-load-status {{ margin-left:auto; font-size:.68rem; color:#475569; }}

    /* ── City grid ── */
    .city-grid {{
      display:grid;
      grid-template-columns:repeat(auto-fill,minmax(268px,1fr));
      gap:1rem;
    }}

    /* ── City card ── */
    .city-card {{
      background: rgba(255,255,255,.035);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 1.1rem;
      padding: 1.15rem 1.1rem 1rem;
      transition: transform .22s cubic-bezier(.22,1,.36,1), box-shadow .22s, border-color .22s;
      min-height: 148px;
      position: relative; overflow: hidden;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }}
    /* Accent top-bar */
    .city-card::before {{
      content: ""; position: absolute; top: 0; left: 0; right: 0;
      height: 3px; background: var(--accent);
      border-radius: 1.1rem 1.1rem 0 0;
      box-shadow: 0 0 14px color-mix(in srgb, var(--accent) 60%, transparent);
    }}
    /* Subtle inner glow on hover */
    .city-card::after {{
      content: ""; position: absolute; inset: 0; border-radius: 1.1rem;
      background: radial-gradient(ellipse 80% 60% at 50% 0%, color-mix(in srgb, var(--accent) 12%, transparent) 0%, transparent 70%);
      opacity: 0; transition: opacity .25s;
      pointer-events: none;
    }}
    .city-card:hover::after   {{ opacity: 1; }}
    .city-card.refreshing {{ opacity: .35; pointer-events: none; }}
    .city-card:hover {{
      transform: translateY(-4px) scale(1.01);
      box-shadow: 0 12px 36px rgba(0,0,0,.45),
                  0 0 0 1px rgba(255,255,255,.11),
                  0 0 24px color-mix(in srgb, var(--accent) 20%, transparent);
      border-color: rgba(255,255,255,.14);
    }}
    .city-card.is-hottest {{
      border-color:rgba(251,146,60,.4)!important;
      box-shadow:0 0 22px rgba(251,146,60,.25)!important;
    }}
    .city-card.is-hottest::before {{ background:#f97316; box-shadow:0 0 16px rgba(249,115,22,.5); }}
    .city-card.is-coldest {{
      border-color:rgba(56,189,248,.35)!important;
      box-shadow:0 0 22px rgba(56,189,248,.2)!important;
    }}
    .city-card.is-coldest::before {{ background:#38bdf8; box-shadow:0 0 16px rgba(56,189,248,.45); }}

    .temp-badge {{
      display:inline-flex; align-items:center; gap:.2rem; font-size:.6rem;
      font-weight:700; border-radius:999px; padding:.12rem .45rem; margin-top:.2rem;
    }}
    .temp-badge.hot  {{ background:rgba(251,146,60,.15); color:#fb923c; border:1px solid rgba(251,146,60,.3); }}
    .temp-badge.cold {{ background:rgba(56,189,248,.12); color:#38bdf8;  border:1px solid rgba(56,189,248,.28); }}

    .city-card-top {{
      display:flex; justify-content:space-between; align-items:flex-start;
      margin-bottom:.55rem; position:relative; z-index:1;
    }}
    .city-name   {{ font-size:.93rem; font-weight:700; color:#f1f5f9; line-height:1.25; }}
    .city-region {{ font-size:.6rem; color:#475569; margin-top:.1rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:165px; }}
    .city-region.wrong-location {{ color:#f87171; font-weight:600; }}
    .city-obs    {{ font-size:.58rem; color:#94a3b8; margin-top:.15rem; }}
    .city-temp   {{
      font-size:1.65rem; font-weight:900; line-height:1;
      background:linear-gradient(160deg,#f8fafc 30%,#cbd5e1 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      background-clip:text;
    }}
    .city-icon   {{ font-size:1.5rem; text-align:right; line-height:1; }}
    .city-desc   {{ font-size:.72rem; color:#64748b; font-style:italic; margin-bottom:.7rem; position:relative; z-index:1; }}

    .city-metrics {{ display:grid; grid-template-columns:1fr 1fr; gap:.35rem; position:relative; z-index:1; }}
    .city-metric  {{ font-size:.67rem; color:#475569; }}
    .city-metric span {{ color:#94a3b8; font-weight:600; }}

    /* ── Forecast strip ── */
    .city-forecast {{
      margin-top:.7rem; padding-top:.55rem;
      border-top:1px solid rgba(255,255,255,.06);
      display:flex; gap:.3rem; overflow-x:hidden;
      position:relative; z-index:1;
    }}
    .fc-day {{
      flex:1 1 0; min-width:42px; text-align:center; font-size:.6rem;
      background:rgba(0,0,0,.25);
      border:1px solid rgba(255,255,255,.07);
      border-radius:.5rem; padding:.28rem .3rem;
    }}
    .fc-day .fc-date {{ color:#94a3b8; margin-bottom:.15rem; font-size:.55rem; }}
    .fc-day .fc-hi   {{ color:#fbbf24; font-weight:700; font-size:.7rem; }}
    .fc-day .fc-lo   {{ color:#60a5fa; font-size:.62rem; }}
    .fc-day .fc-icon {{ font-size:.8rem; margin:.1rem 0; }}

    /* ── Hourly strip ── */
    .hourly-toggle {{
      margin-top:.55rem; font-size:.64rem; color:#334155;
      cursor:pointer; user-select:none; text-align:center;
      padding:.2rem 0; border-top:1px solid rgba(255,255,255,.05);
      transition:color .15s; position:relative; z-index:1;
    }}
    .hourly-toggle:hover {{ color:#64748b; }}
    .hourly-strip {{
      display:none; overflow-x:auto; gap:.4rem; margin-top:.4rem; padding-bottom:.25rem;
    }}
    .hourly-strip.open {{ display:flex; }}
    .hr-slot {{
      flex:0 0 auto; text-align:center; font-size:.6rem;
      background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.07);
      border-radius:.45rem; padding:.32rem .45rem; min-width:52px;
    }}
    .hr-slot.hr-current {{ border-color:rgba(99,102,241,.5); background:rgba(99,102,241,.1); }}
    .hr-time {{ color:#475569; margin-bottom:.1rem; }}
    .hr-temp {{ color:#fbbf24; font-weight:700; margin:.1rem 0; }}
    .hr-rain {{ color:#60a5fa; }}

    /* ── Weather condition themes ── */
    .wt-clear   {{ background:linear-gradient(155deg,rgba(251,191,36,.1) 0%,rgba(253,224,71,.05) 100%); }}
    .wt-clear::after {{ background:radial-gradient(ellipse 70% 50% at 50% 0%,rgba(251,191,36,.14) 0%,transparent 70%)!important; }}
    .wt-cloudy  {{ background:linear-gradient(155deg,rgba(100,116,139,.1) 0%,rgba(71,85,105,.06) 100%); }}
    .wt-rain    {{ background:linear-gradient(155deg,rgba(59,130,246,.12) 0%,rgba(37,99,235,.05) 100%); }}
    .wt-drizzle {{ background:linear-gradient(155deg,rgba(96,165,250,.1)  0%,rgba(59,130,246,.04) 100%); }}
    .wt-thunder {{ background:linear-gradient(155deg,rgba(139,92,246,.14) 0%,rgba(109,40,217,.07) 100%); }}
    .wt-snow    {{ background:linear-gradient(155deg,rgba(186,230,253,.08) 0%,rgba(224,242,254,.04) 100%); }}
    .wt-mist    {{ background:linear-gradient(155deg,rgba(148,163,184,.08) 0%,rgba(100,116,139,.04) 100%); }}

    .wt-rain::before, .wt-drizzle::before {{
      content:''; position:absolute; inset:0; pointer-events:none; z-index:0;
      background:repeating-linear-gradient(105deg,transparent 0 7px,rgba(96,165,250,.06) 7px 8px);
      animation:rain-move .9s linear infinite;
    }}
    @keyframes rain-move {{ from{{background-position:0 0}} to{{background-position:10px 18px}} }}

    .wt-clear .city-icon   {{ animation:sun-pulse 3s ease-in-out infinite; }}
    @keyframes sun-pulse   {{ 0%,100%{{filter:drop-shadow(0 0 4px rgba(251,191,36,.4));transform:scale(1)}} 50%{{filter:drop-shadow(0 0 10px rgba(253,224,71,.9));transform:scale(1.15)}} }}

    .wt-thunder .city-temp {{ animation:lightning 6s ease-in-out infinite; }}
    @keyframes lightning   {{ 0%,92%,100%{{opacity:1;text-shadow:none}} 93%{{opacity:.5;text-shadow:0 0 14px #a78bfa}} 94%{{opacity:1;text-shadow:0 0 22px #a78bfa}} 95%{{opacity:.3}} 96%{{opacity:1}} }}

    .wt-snow .city-icon {{ animation:snow-spin 5s linear infinite; }}
    @keyframes snow-spin {{ from{{transform:rotate(0deg)}} to{{transform:rotate(360deg)}} }}

    /* ── Weather Particle Animations ── */
    .wx-particles {{ position:absolute; inset:0; pointer-events:none; z-index:0; overflow:hidden; border-radius:1.1rem; }}
    .wx-p {{ position:absolute; pointer-events:none; will-change:transform,opacity; }}
    @keyframes wx-rain  {{ 0%{{transform:translateY(-10px) rotate(12deg);opacity:.9}} 100%{{transform:translateY(220px) rotate(12deg);opacity:0}} }}
    @keyframes wx-snow  {{ 0%{{transform:translateY(-12px) translateX(0px) rotate(0deg);opacity:1}} 50%{{transform:translateY(100px) translateX(12px) rotate(200deg);opacity:.8}} 100%{{transform:translateY(220px) translateX(-5px) rotate(380deg);opacity:0}} }}
    @keyframes wx-heat  {{ 0%,100%{{transform:scaleX(1) translateY(0px);opacity:.5}} 50%{{transform:scaleX(1.06) translateY(-10px);opacity:.9}} }}
    @keyframes wx-bolt  {{ 0%,85%,100%{{opacity:0}} 86%{{opacity:1}} 87%{{opacity:0}} 88%{{opacity:.8}} 89%{{opacity:0}} }}
    @keyframes wx-fog   {{ 0%{{transform:translateX(-25%);opacity:0}} 30%{{opacity:.18}} 70%{{opacity:.18}} 100%{{transform:translateX(25%);opacity:0}} }}
    @keyframes wx-orb   {{ 0%,100%{{transform:scale(1);opacity:.35}} 50%{{transform:scale(1.3);opacity:.6}} }}

    /* Sparkline */
    .sparkline-wrap {{ margin-top:.6rem; padding-top:.45rem; border-top:1px solid rgba(255,255,255,.06); position:relative; z-index:1; }}
    .sparkline-label {{ font-size:.57rem; color:#334155; margin-bottom:.12rem; }}

    /* ── Weather detail modal ── */
    .w-modal {{ display:none; position:fixed; inset:0; z-index:9999; overflow-y:auto; background:rgba(0,0,0,.85); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); padding:1.5rem; align-items:flex-start; justify-content:center; }}
    .w-modal.open {{ display:flex; animation:wm-fade .2s ease; }}
    @keyframes wm-fade {{ from{{opacity:0}} to{{opacity:1}} }}
    .w-box {{ position:relative; width:min(680px,100%); margin:auto; border-radius:1.75rem; overflow:hidden; box-shadow:0 40px 120px rgba(0,0,0,.8),0 0 0 1px rgba(255,255,255,.08); animation:wm-slide .2s cubic-bezier(.22,1,.36,1); }}
    @keyframes wm-slide {{ from{{transform:translateY(28px) scale(.97)}} to{{transform:translateY(0) scale(1)}} }}
    .w-box.wt-clear   {{ background:linear-gradient(165deg,#f7931a,#ffd200,#f7931a); }}
    .w-box.wt-cloudy  {{ background:linear-gradient(165deg,#1e2a3a,#2d4258,#1e2a3a); }}
    .w-box.wt-rain    {{ background:linear-gradient(165deg,#071525,#0f2d50,#071525); }}
    .w-box.wt-drizzle {{ background:linear-gradient(165deg,#0d1f35,#1a3b5c,#0d1f35); }}
    .w-box.wt-thunder {{ background:linear-gradient(165deg,#080815,#160425,#080815); }}
    .w-box.wt-snow    {{ background:linear-gradient(165deg,#7eb5d6,#bbd9ef,#7eb5d6); }}
    .w-box.wt-mist    {{ background:linear-gradient(165deg,#3a4555,#5a6d82,#3a4555); }}
    .w-canvas {{ position:absolute; inset:0; pointer-events:none; z-index:1; }}
    .w-close {{ position:absolute; top:1rem; right:1rem; z-index:20; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2); color:#fff; border-radius:50%; width:38px; height:38px; font-size:1.05rem; cursor:pointer; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(8px); transition:all .2s; }}
    .w-close:hover {{ background:rgba(255,255,255,.25); transform:scale(1.08); }}
    .w-content {{ position:relative; z-index:10; padding:1.5rem; }}
    .w-hero {{ text-align:center; padding:.5rem 0 1.2rem; }}
    .w-city  {{ font-size:1.7rem; font-weight:900; color:#fff; letter-spacing:-.5px; }}
    .w-rgn   {{ font-size:.78rem; color:rgba(255,255,255,.5); margin-top:.1rem; }}
    .w-obs2  {{ font-size:.68rem; color:rgba(255,255,255,.75); margin:.25rem 0 .75rem; }}
    .w-bigic {{ font-size:5rem; line-height:1.1; filter:drop-shadow(0 4px 16px rgba(0,0,0,.4)); }}
    .w-bigT  {{ font-size:6rem; font-weight:900; color:#fff; line-height:1; letter-spacing:-4px; text-shadow:0 4px 24px rgba(0,0,0,.3); }}
    .w-dsc   {{ font-size:1.1rem; color:rgba(255,255,255,.72); text-transform:capitalize; margin-top:.35rem; }}
    .w-fl    {{ font-size:.8rem; color:rgba(255,255,255,.38); margin-top:.15rem; }}
    .w-tiles {{ display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin-top:1.1rem; }}
    .w-tile  {{ background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.13); border-radius:.9rem; padding:.85rem .55rem; text-align:center; backdrop-filter:blur(10px); transition:background .18s; }}
    .w-tile:hover {{ background:rgba(255,255,255,.16); }}
    .w-tile-i {{ font-size:1.25rem; }}
    .w-tile-l {{ font-size:.56rem; color:rgba(255,255,255,.38); text-transform:uppercase; letter-spacing:.07em; margin:.12rem 0; }}
    .w-tile-v {{ font-size:1.05rem; font-weight:700; color:#fff; }}
    .w-sec   {{ font-size:.66rem; color:rgba(255,255,255,.35); text-transform:uppercase; letter-spacing:.1em; margin:1.2rem 0 .5rem; }}
    .w-chart-svg {{ width:100%; display:block; overflow:visible; }}
    .w-fcs {{ display:flex; gap:.5rem; overflow-x:auto; padding-bottom:.4rem; }}
    .w-fc {{ flex:1; min-width:82px; background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.12); border-radius:.9rem; padding:.8rem .4rem; text-align:center; backdrop-filter:blur(10px); transition:background .18s; }}
    .w-fc:hover {{ background:rgba(255,255,255,.15); }}
    .w-fc-d {{ font-size:.63rem; color:rgba(255,255,255,.8); margin-bottom:.2rem; }}
    .w-fc-i {{ font-size:1.4rem; margin-bottom:.2rem; }}
    .w-fc-h {{ font-size:1.1rem; font-weight:700; color:#fbbf24; }}
    .w-fc-l {{ font-size:.85rem; color:#93c5fd; margin-top:.1rem; }}
    .w-fc-s {{ font-size:.56rem; color:rgba(255,255,255,.35); margin-top:.2rem; }}
    .city-card[data-clickable] {{ cursor:pointer; }}

    /* ── Alert ticker ── */
    #alert-bar {{
      background:linear-gradient(90deg,rgba(220,38,38,.15) 0%,rgba(239,68,68,.08) 50%,rgba(220,38,38,.15) 100%);
      border-top:1px solid rgba(239,68,68,.25); border-bottom:1px solid rgba(239,68,68,.15);
      padding:.42rem 1.4rem; display:flex; align-items:center; gap:.85rem;
      overflow:hidden; white-space:nowrap;
    }}
    #alert-bar.hidden {{ display:none; }}
    .alert-bar-label {{
      flex-shrink:0; font-size:.66rem; font-weight:800; color:#fca5a5;
      text-transform:uppercase; letter-spacing:.09em;
      border:1px solid rgba(239,68,68,.45); border-radius:4px; padding:.1rem .45rem;
      animation:pulse 2s infinite;
    }}
    .alert-ticker-wrap {{ overflow:hidden; flex:1; }}
    .alert-ticker {{ display:inline-block; animation:ticker-scroll 120s linear infinite; }}
    .alert-ticker:hover {{ animation-play-state:paused; }}
    @keyframes ticker-scroll {{ from{{transform:translateX(100vw)}} to{{transform:translateX(-100%)}} }}
    .atick-item {{ display:inline-flex; align-items:center; gap:.35rem; margin-right:3.5rem; font-size:.7rem; color:#fde68a; }}
    .atick-item .atick-badge {{ padding:.1rem .4rem; border-radius:999px; font-size:.6rem; font-weight:700; color:#fff; }}

    /* ── Cyclone panel ── */
    #cyclone-panel {{ max-width:1900px; margin:0 auto; padding:.8rem 1.75rem 0; }}
    #cyclone-panel.hidden {{ display:none; }}
    .cyclone-header {{ display:flex; align-items:center; gap:.6rem; font-size:.8rem; font-weight:700; color:#f87171; margin-bottom:.65rem; }}
    .cyclone-cards {{ display:flex; flex-wrap:wrap; gap:.7rem; }}
    .cyc-card {{ background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(239,68,68,.1)); border:1px solid rgba(239,68,68,.3); border-radius:.9rem; padding:.85rem 1.1rem; min-width:220px; max-width:320px; backdrop-filter:blur(12px); }}
    .cyc-name {{ font-size:1rem; font-weight:800; color:#f87171; }}
    .cyc-level {{ display:inline-block; padding:.1rem .5rem; border-radius:999px; font-size:.6rem; font-weight:700; color:#fff; margin:.2rem 0 .35rem; }}
    .cyc-level.Red{{background:#dc2626}} .cyc-level.Orange{{background:#ea580c}} .cyc-level.Green{{background:#16a34a}}
    .cyc-desc {{ font-size:.67rem; color:#94a3b8; line-height:1.45; }}
    .cyc-coords {{ font-size:.61rem; color:#64748b; margin-top:.3rem; }}
    .cyc-link {{ font-size:.61rem; color:#818cf8; text-decoration:none; }}
    .cyc-link:hover {{ text-decoration:underline; }}

    /* ── Alert badges on cards ── */
    .alert-badge {{ display:inline-flex; align-items:center; gap:.2rem; font-size:.58rem; font-weight:700; padding:.1rem .4rem; border-radius:999px; color:#fff; margin:.1rem .1rem 0 0; }}
    .city-alerts {{ margin:.25rem 0 .05rem; display:flex; flex-wrap:wrap; position:relative; z-index:1; }}

    /* ── Skeleton ── */
    .skeleton-line {{
      background:linear-gradient(90deg,rgba(255,255,255,.04) 25%,rgba(255,255,255,.09) 50%,rgba(255,255,255,.04) 75%);
      background-size:200% 100%;
      animation:shimmer 1.6s infinite;
      border-radius:.35rem; height:.85rem; margin:.38rem 0;
    }}
    .skeleton-line.w80{{width:80%}} .skeleton-line.w55{{width:55%}} .skeleton-line.w70{{width:70%}}
    @keyframes shimmer{{ 0%{{background-position:200% 0}} 100%{{background-position:-200% 0}} }}
    .error-msg {{ color:#f87171; font-size:.75rem; padding:.5rem .7rem; background:rgba(248,113,113,.08); border:1px solid rgba(248,113,113,.2); border-radius:.45rem; margin-top:.4rem; }}

    /* ── Footer ── */
    footer {{ text-align:center; margin-top:3rem; color:#1e293b; font-size:.72rem; }}
    footer a {{ color:#334155; }}
  </style>
</head>
<body>

<header>
  <div class="header-left">
    <h1>&#127868; India Weather Dashboard</h1>
      <p>Live weather for 28 states + 8 union territories &amp; 780+ districts &mdash; powered by Open-Meteo</p>
  </div>
  <div class="header-right">
    <div class="status-pill">
      <span class="dot" id="live-dot"></span>
      <span id="live-label">Live</span>
    </div>
    <div class="status-pill">&#128336; Refresh in <span id="countdown">5:00</span></div>
    <div class="status-pill" id="pill-last-updated" style="display:none">&#128260; Updated <span id="last-updated"></span></div>
    <div class="status-pill" id="pill-hot" style="display:none">&#128293; <span id="global-hot">&mdash;</span></div>
    <div class="status-pill" id="pill-cold" style="display:none">&#10052; <span id="global-cold">&mdash;</span></div>
    <button id="refresh-btn" onclick="triggerRefresh()">&#8635; Refresh Now</button>
    <button id="pwa-notif-btn" onclick="_requestNotifications()" style="display:inline-flex;align-items:center;gap:.35rem;padding:.4rem .85rem;border-radius:.6rem;border:1px solid rgba(99,102,241,.4);background:rgba(99,102,241,.12);color:#c7d2fe;font-size:.75rem;cursor:pointer">&#128276; Enable Alerts</button>
    <button id="pwa-install-btn" onclick="_installPWA()" style="display:none;align-items:center;gap:.35rem;padding:.4rem .85rem;border-radius:.6rem;border:1px solid rgba(16,185,129,.4);background:rgba(16,185,129,.12);color:#6ee7b7;font-size:.75rem;cursor:pointer">&#11015; Install App</button>
  </div>
</header>

<!-- Alert ticker -->
<div id="alert-bar" class="hidden">
  <span class="alert-bar-label">&#9888; Alerts</span>
  <div class="alert-ticker-wrap">
    <span class="alert-ticker" id="alert-ticker-inner"></span>
  </div>
</div>

<!-- Cyclone panel -->
<div id="cyclone-panel" class="hidden">
  <div class="cyclone-header">&#127744; Active Cyclones &mdash; Bay of Bengal / Arabian Sea</div>
  <div class="cyclone-cards" id="cyclone-cards"></div>
</div>

<div id="state-nav">
  <button class="state-btn all-btn active" style="--c:#64748b"
          onclick="filterState('all', this)">All States</button>
</div>

<div id="state-container"></div>

<div id="w-modal" class="w-modal" onclick="if(event.target===this)closeWeatherModal()">
  <div class="w-box" id="w-box">
    <canvas class="w-canvas" id="w-canvas"></canvas>
    <button class="w-close" onclick="closeWeatherModal()">&#10005;</button>
    <div class="w-content">
      <div class="w-hero">
        <div class="w-city" id="w-city"></div>
        <div class="w-rgn"  id="w-rgn"></div>
        <div class="w-obs2" id="w-obs2"></div>
        <div class="w-bigic" id="w-bigic"></div>
        <div class="w-bigT"  id="w-bigT"></div>
        <div class="w-dsc"  id="w-dsc"></div>
        <div class="w-fl"   id="w-fl"></div>
      </div>
      <div class="w-tiles" id="w-tiles"></div>
      <div class="w-sec">&#127777; Temperature &amp; Rain Forecast</div>
      <div id="w-chart"></div>
      <div class="w-sec" id="w-fcs-label">&#128197; Forecast</div>
      <div class="w-fcs" id="w-fcs"></div>
    </div>
  </div>
</div>

<footer>
  Data from <a href="https://open-meteo.com" target="_blank">Open-Meteo</a> (free, no API key) &bull;
  28 state agents + 8 UT agents &bull; Auto-refreshes every 10 min &bull; 15-min update cadence
</footer>

<script>
{STATES_JS}

  // ── Open-Meteo (no API key needed) ──────────────────────────────────────
  // WMO weather interpretation codes
  const WMO_DESC = {{
    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Fog", 48:"Icy fog",
    51:"Light drizzle", 53:"Moderate drizzle", 55:"Dense drizzle",
    61:"Slight rain", 63:"Moderate rain", 65:"Heavy rain",
    71:"Slight snow", 73:"Moderate snow", 75:"Heavy snow", 77:"Snow grains",
    80:"Slight showers", 81:"Moderate showers", 82:"Heavy showers",
    85:"Slight snow showers", 86:"Heavy snow showers",
    95:"Thunderstorm", 96:"Thunderstorm with hail", 99:"Thunderstorm, heavy hail"
  }};

  // District → OWM city fallback map (mirrors owm_client.py _FALLBACKS)
  // Used when OWM returns 404 for an administrative district name.
  const OWM_FALLBACKS = {{
    "Nicobars":"Port Blair","North and Middle Andaman":"Port Blair","South Andaman":"Port Blair",
    "Alluri Sitharama Raju":"Rajahmundry","Anakapalli":"Visakhapatnam","Ananthapuramu":"Anantapur",
    "Annamayya":"Tirupati","Dr. B.R. Ambedkar Konaseema":"Amalapuram","East Godavari":"Rajahmundry",
    "NTR":"Vijayawada","Palnadu":"Guntur","Parvathipuram Manyam":"Vizianagaram","Prakasam":"Ongole",
    "Sri Potti Sriramulu Nellore":"Nellore","Sri Sathya Sai":"Kadapa","West Godavari":"Eluru","YSR":"Kadapa",
    "Anjaw":"Dibrugarh","Bichom":"Tezpur","Dibang Valley":"Itanagar","East Kameng":"Tezpur",
    "East Siang":"Itanagar","Kamle":"Itanagar","Kra Daadi":"Itanagar","Kurung Kumey":"Itanagar",
    "Lepa Rada":"Itanagar","Lohit":"Dibrugarh","Longding":"Itanagar","Lower Dibang Valley":"Itanagar",
    "Lower Siang":"Itanagar","Lower Subansiri":"Itanagar","Pakke-Kessang":"Itanagar","Papum Pare":"Itanagar",
    "Shi Yomi":"Itanagar","Siang":"Itanagar","Upper Siang":"Itanagar","Upper Subansiri":"Itanagar",
    "West Kameng":"Tezpur","West Siang":"Itanagar",
    "Bajali":"Barpeta","Baksa":"Guwahati","Biswanath":"Tezpur","Cachar":"Silchar","Charaideo":"Sibsagar",
    "Chirang":"Bongaigaon","Darrang":"Mangaldai","Dima Hasao":"Haflong","Kamrup":"Guwahati",
    "Kamrup Metropolitan":"Guwahati","Karbi Anglong":"Diphu","Majuli":"Jorhat","Sivasagar":"Sibsagar",
    "Sonitpur":"Tezpur","South Salmara-Mankachar":"Dhubri","West Karbi Anglong":"Diphu",
    "Kaimur":"Sasaram","Nalanda":"Bihar Sharif","Pashchim Champaran":"Bettiah","Purbi Champaran":"Motihari","Saran":"Chapra",
    "Balodabazar-Bhatapara":"Raipur","Balrampur-Ramanujganj":"Ambikapur","Bastar":"Jagdalpur",
    "Dakshin Bastar Dantewada":"Jagdalpur","Gariyaband":"Raipur","Gaurela-Pendra-Marwahi":"Bilaspur",
    "Janjgir-Champa":"Bilaspur","Jashpur":"Ambikapur","Kabirdham":"Rajnandgaon",
    "Khairagarh-Chhindgarh-Gandai":"Rajnandgaon","Korea":"Ambikapur",
    "Manendragarh-Chirmiri-Bharatpur":"Ambikapur","Mohla":"Rajnandgaon",
    "Sarangarh-Bilaigarh":"Raigarh","Surguja":"Ambikapur",
    "Central Delhi":"Delhi","East Delhi":"Delhi","North Delhi":"Delhi","North East Delhi":"Delhi",
    "North West Delhi":"Delhi","South Delhi":"Delhi","South East Delhi":"Delhi",
    "South West Delhi":"Delhi","West Delhi":"Delhi",
    "North Goa":"Panaji","South Goa":"Panaji",
    "Arvalli":"Gandhinagar","Banas Kantha":"Palanpur","Dangs":"Surat","Devbhumi Dwarka":"Jamnagar",
    "Gir Somnath":"Junagadh","Kachchh":"Bhuj","Mahisagar":"Vadodara","Narmada":"Vadodara",
    "Panch Mahals":"Godhra","Sabarkantha":"Idar","Tapi":"Surat",
    "Kinnaur":"Shimla","Lahaul and Spiti":"Manali",
    "Ganderbal":"Srinagar","Shopian":"Srinagar",
    "East Singhbhum":"Jamshedpur","Koderma":"Hazaribagh","Palamu":"Daltonganj",
    "Sahebganj":"Rajmahal","Saraikela Kharsawan":"Jamshedpur","West Singhbhum":"Chaibasa",
    "Bagalkote":"Bagalkot","Bengaluru Rural":"Bangalore","Bengaluru Urban":"Bangalore",
    "Dakshina Kannada":"Mangalore","Kodagu":"Madikeri","Uttara Kannada":"Karwar",
    "Wayanad":"Kalpetta","Kargil":"Leh",
    "Agatti":"Kavaratti","Minicoy":"Kavaratti","Amini":"Kavaratti",
    "Agar-Malwa":"Ujjain",
    "Ahilyanagar":"Ahmednagar","Chhatrapati Sambhajinagar":"Aurangabad","Dharashiv":"Osmanabad",
    "Gadchiroli":"Chandrapur","Mumbai Suburban":"Mumbai","Nanded":"Nanded",
    "Raigad":"Alibag","Sindhudurg":"Ratnagiri",
    "Imphal East":"Imphal","Imphal West":"Imphal","Jiribam":"Imphal","Kakching":"Imphal",
    "Kamjong":"Imphal","Kangpokpi":"Imphal","Noney":"Imphal","Pherzawl":"Imphal",
    "Tamenglong":"Imphal","Tengnoupal":"Imphal","Ukhrul":"Imphal",
    "East Garo Hills":"Tura","East Jaintia Hills":"Shillong","East Khasi Hills":"Shillong",
    "Eastern West Khasi Hills":"Shillong","North Garo Hills":"Tura","Ri Bhoi":"Shillong",
    "South Garo Hills":"Tura","South West Garo Hills":"Tura","South West Khasi Hills":"Shillong",
    "West Garo Hills":"Tura","West Jaintia Hills":"Shillong","West Khasi Hills":"Shillong",
    "Champhai":"Aizawl","Hnahthial":"Aizawl","Khawzawl":"Aizawl","Saitual":"Aizawl","Siaha":"Aizawl",
    "Chumoukedima":"Dimapur","Mon Nagaland":"Dimapur","Niuland":"Dimapur","Peren":"Kohima",
    "Boudh":"Sambalpur","Kalahandi":"Bhawanipatna","Kandhamal":"Phulbani",
    "Kendujhar":"Baripada","Mayurbhanj":"Baripada","Nabarangpur":"Koraput",
    "Gurdaspur":"Amritsar","S.A.S. Nagar":"Chandigarh","Shahid Bhagat Singh Nagar":"Jalandhar",
    "Sri Muktsar Sahib":"Muktsar",
    "Chittorgarh":"Bhilwara","Dholpur":"Agra","Didwana-Kuchaman":"Nagaur",
    "Gangapur City":"Sawai Madhopur","Jaipur Rural":"Jaipur","Jodhpur Rural":"Jodhpur",
    "Khairthal-Tijara":"Alwar","Kotputli-Behror":"Alwar",
    "East Sikkim":"Gangtok","North Sikkim":"Gangtok","Soreng":"Gangtok",
    "South Sikkim":"Namchi","West Sikkim":"Gangtok",
    "Kallakurichi":"Salem","Kancheepuram":"Chengalpattu","Nilgiris":"Ooty",
    "Ranipet":"Vellore","Tirupattur":"Vellore","Tiruvarur":"Kumbakonam","Viluppuram":"Cuddalore",
    "Bhadradri Kothagudem":"Khammam","Hanumakonda":"Warangal","Jagitial":"Karimnagar",
    "Jayashankar Bhupalpally":"Warangal","Jogulamba Gadwal":"Mahbubnagar","Kamareddy":"Nizamabad",
    "Kumuram Bheem Asifabad":"Adilabad","Medchal-Malkajgiri":"Hyderabad","Mulugu":"Warangal",
    "Rajanna Sircilla":"Karimnagar","Ranga Reddy":"Hyderabad","Wanaparthy":"Mahbubnagar",
    "Warangal Rural":"Warangal","Yadadri Bhuvanagiri":"Nalgonda",
    "Dhalai":"Agartala","Gomati":"Agartala","Khowai":"Agartala","North Tripura":"Agartala",
    "Sepahijala":"Agartala","South Tripura":"Agartala","Unakoti":"Agartala","West Tripura":"Agartala",
    "Ambedkar Nagar":"Ayodhya","Banda Uttar Pradesh":"Banda Uttar Pradesh India","Gautam Buddha Nagar":"Noida",
    "Kanpur Dehat":"Kanpur","Kanpur Nagar":"Kanpur","Lakhimpur Kheri":"Lakhimpur",
    "Prayagraj":"Allahabad","Sant Kabir Nagar":"Gorakhpur","Shravasti":"Bahraich",
    "Siddharthnagar":"Gorakhpur","Sonbhadra":"Varanasi",
    "Chamoli":"Rishikesh","Pauri Garhwal":"Lansdowne","Tehri Garhwal":"Rishikesh",
    "Udham Singh Nagar":"Rudrapur",
    "Birbhum":"Bolpur","Cooch Behar":"Koch Bihar","Dakshin Dinajpur":"Balurghat",
    "Hooghly":"Chandannagar","Nadia":"Krishnanagar","North 24 Parganas":"Barasat",
    "Paschim Bardhaman":"Asansol","Paschim Medinipur":"Kharagpur","Purba Bardhaman":"Bardhaman",
    "Purba Medinipur":"Haldia","Purulia":"Asansol","South 24 Parganas":"Diamond Harbour",
    "Uttar Dinajpur":"Raiganj"
  }};

  // Resolve a district name to its OWM-queryable city (fallback if needed).
  function owmCity(city) {{
    return OWM_FALLBACKS[city] || city;
  }}

  // ── Constants ──────────────────────────────────────────────────────────────
  const REFRESH_SECS = 600;
  // ── Open-Meteo (no API key needed) ───────────────────────────────────
  // OWM_KEY kept for backward compat (not used for API calls anymore)
  const OWM_KEY = "";

  // Per-state loading only (never auto-loads all 789 cities at once).
  // 3 cities x 2 OM calls / 2.5s = 72 calls/min — within Open-Meteo fair-use.
  const BATCH_SIZE   = 3;
  const BATCH_DELAY  = 2500; // ms between batches
  const RETRY_429_MS = 35000;

  // ── State ──────────────────────────────────────────────────────────────────
  let countdown      = REFRESH_SECS;
  let timerID;
  let activeFilter   = "all";
  let abortCtrl      = null;   // current AbortController
  const dataCache    = {{}};    // city -> parsed object or null (error)

  // ── Weather icons ──────────────────────────────────────────────────────────
  const ICONS = {{
    sunny:"&#9728;&#65039;", clear:"&#9728;&#65039;", "partly cloudy":"&#9925;",
    cloudy:"&#9729;&#65039;", overcast:"&#9729;&#65039;", mist:"&#127787;&#65039;",
    fog:"&#127787;&#65039;", rain:"&#127783;&#65039;", drizzle:"&#127782;&#65039;",
    snow:"&#10052;&#65039;", sleet:"&#127784;&#65039;", thunder:"&#9928;&#65039;",
    blizzard:"&#127784;&#65039;", haze:"&#127787;&#65039;", smoke:"&#127787;&#65039;"
  }};
  function icon(desc) {{
    const d = (desc||"").toLowerCase();
    for (const [k,v] of Object.entries(ICONS)) if (d.includes(k)) return v;
    return "&#127777;&#65039;";
  }}

  // OWM time integer (0,300,...,2100) → "00:00", "03:00", etc.
  function fmtHour(t) {{
    const h = Math.floor(t / 100);
    return String(h).padStart(2, "0") + ":00";
  }}

  // Convert OWM UTC dt_txt ("YYYY-MM-DD HH:MM:SS") → IST display string.
  function utcToIST(dt_txt) {{
    if (!dt_txt) return "&mdash;";
    const d = new Date(dt_txt.replace(" ", "T") + "Z");
    return d.toLocaleString("en-IN", {{
      timeZone: "Asia/Kolkata",
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit", hour12: true
    }}) + " IST";
  }}

  // Wind bearing (°) → 16-point compass label.
  const _COMPASS = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"];
  function degToDir(deg) {{ return _COMPASS[Math.round((deg||0) / 22.5) % 16]; }}

  // m/s → km/h (rounded)
  function kmph(mps) {{ return Math.round((mps || 0) * 3.6); }}

  // ── DOM helpers ────────────────────────────────────────────────────────────
  function skeleton() {{
    return `<div class="skeleton-line w80"></div>
            <div class="skeleton-line w55"></div>
            <div class="skeleton-line w70"></div>`;
  }}

  // Parse an OWM /forecast response into the internal card data shape.
  // parseOWM takes TWO responses (OWM /forecast call removed from browser):
  //   wJson  = OWM /weather   (current conditions — 1 OWM call per city)
  //   omJson = Open-Meteo    (7-day daily + hourly — free, no rate limit)
  function parseOWM(wJson, omJson, cityName) {{
    const wrongLocation = wJson.sys?.country !== "IN";
    const resolvedName  = wJson.name || cityName;

    const wMain = wJson.main || {{}};
    const wWind = wJson.wind || {{}};

    // Build hourly slots from Open-Meteo hourly data
    let omHourlyByDate = {{}};
    if (omJson && omJson.hourly) {{
      const h = omJson.hourly;
      (h.time || []).forEach((t, i) => {{
        const date = t.slice(0, 10);
        if (!omHourlyByDate[date]) omHourlyByDate[date] = [];
        omHourlyByDate[date].push({{
          time: parseInt(t.slice(11, 13)) * 100,
          tempC: String(Math.round(h.temperature_2m?.[i] ?? 0)),
          desc:  WMO_DESC[h.weathercode?.[i] ?? 0] || "Unknown",
          rain:  String(h.precipitation_probability?.[i] ?? 0)
        }});
      }});
    }}

    // 7-day daily from Open-Meteo (or minimal fallback)
    let forecast = [];
    if (omJson && omJson.daily && omJson.daily.time) {{
      const d = omJson.daily;
      forecast = d.time.slice(0, 7).map((date, i) => {{
        const code = d.weathercode?.[i] ?? 0;
        return {{
          date,
          maxC: Math.round(d.temperature_2m_max?.[i] ?? 0),
          minC: Math.round(d.temperature_2m_min?.[i] ?? 0),
          desc: WMO_DESC[code] || "Variable clouds",
          rainPct: String(d.precipitation_probability_max?.[i] ?? 0),
          hourly: (omHourlyByDate[date] || []).filter((_,j) => j % 3 === 0) // every 3h
        }};
      }});
    }}

    return {{
      city: cityName, region: resolvedName,
      resolvedLabel: resolvedName + ", India" + (wrongLocation ? " (outside IN ⚠)" : ""),
      wrongLocation,
      temp:     String(Math.round(wMain.temp     ?? 0)),
      feelsLike:String(Math.round(wMain.feels_like ?? 0)),
      humidity: String(wMain.humidity ?? 0),
      desc:     wJson.weather?.[0]?.description ?? "N/A",
      wind:     String(kmph(wWind.speed)), windDir: degToDir(wWind.deg),
      vis:      String(Math.round((wJson.visibility||0)/1000)),
      pressure: String(wMain.pressure ?? 0),
      uv: "N/A", cloud: String(wJson.clouds?.all ?? 0),
      obsTime: new Date().toLocaleString("en-IN", {{
        timeZone:"Asia/Kolkata", day:"2-digit", month:"short",
        year:"numeric", hour:"2-digit", minute:"2-digit", hour12:true
      }}) + " IST",
      forecast,
    }};
  }}

  // ── Live Alerts ─────────────────────────────────────────────────────────
  const LEVEL_COLOR = {{ Red:"#dc2626", Orange:"#ea580c", Green:"#16a34a" }};

  // Alert rules (mirrors agent_alerts.py RULES) — evaluated against live dataCache
  const LIVE_ALERT_RULES = [
    {{ label:"Heat Wave",    color:"#ef4444", icon:"🔥",
       test: d => parseFloat(d.temp) >= 40 }},
    {{ label:"Extreme Heat", color:"#f97316", icon:"🌡",
       test: d => {{ const t = parseFloat(d.temp); return t >= 38 && t < 40; }} }},
    {{ label:"Thunderstorm", color:"#a855f7", icon:"⚡",
       test: d => d.desc.toLowerCase().includes("thunder") }},
    {{ label:"Heavy Rain",   color:"#3b82f6", icon:"🌧",
       test: d => d.desc.toLowerCase().includes("heavy") && d.desc.toLowerCase().includes("rain") }},
    {{ label:"Strong Wind",  color:"#f59e0b", icon:"💨",
       test: d => parseFloat(d.wind) >= 50 }},
    {{ label:"Dense Fog",    color:"#94a3b8", icon:"🌫",
       test: d => (d.desc.toLowerCase().includes("fog") || d.desc.toLowerCase().includes("mist")
                  || d.desc.toLowerCase().includes("haze")) && parseFloat(d.vis) < 2 }},
  ];

  // Live state: cyclones seed from baked data, updated by fetchLiveCyclones()
  let _liveCyclones = (ALERTS_DATA.cyclones || []).filter(c => !c.error);
  let _liveDistAlerts = [];

  // Helper: run alert rules against a data object from dataCache
  function _alertsFor(city, stateName, d) {{
    const results = [];
    for (const rule of LIVE_ALERT_RULES) {{
      try {{
        if (rule.test(d)) results.push({{ city, state: stateName, label: rule.label,
                                          color: rule.color, icon: rule.icon, temp: d.temp }});
      }} catch(_) {{}}
    }}
    return results;
  }}

  // Recompute district alerts from all loaded districts in dataCache
  function recomputeDistrictAlerts() {{
    _liveDistAlerts = [];
    STATES.forEach(state => {{
      state.cities.forEach(city => {{
        const d = dataCache[city];
        if (!d) return;
        _liveDistAlerts.push(..._alertsFor(city, state.name, d));
      }});
    }});
  }}

  // Update the ticker bar with current live alerts
  function rebuildAlertTicker() {{
    const bar    = document.getElementById("alert-bar");
    const ticker = document.getElementById("alert-ticker-inner");
    if (!bar || !ticker) return;

    // ── Cyclone panel
    const cyPanel = document.getElementById("cyclone-panel");
    const cyCards = document.getElementById("cyclone-cards");
    if (cyPanel && cyCards) {{
      if (_liveCyclones.length > 0) {{
        cyCards.innerHTML = _liveCyclones.map(c => `
          <div class="cyc-card">
            <div class="cyc-name">&#127744; ${{c.name}}</div>
            <span class="cyc-level ${{c.level}}">${{c.level}} Alert</span>
            <div class="cyc-desc">${{c.description || c.title || ""}}</div>
            ${{c.lat != null ? `<div class="cyc-coords">&#127759; ${{c.lat.toFixed(1)}}&deg;N, ${{c.lon.toFixed(1)}}&deg;E</div>` : ""}}
            ${{c.url ? `<a class="cyc-link" href="${{c.url}}" target="_blank">&#8599; GDACS details</a>` : ""}}
          </div>`).join("");
        cyPanel.classList.remove("hidden");
      }} else {{
        cyPanel.classList.add("hidden");
      }}
    }}

    const items = [];
    _liveCyclones.forEach(c => items.push(
      `<span class="atick-item">&#127744; <span class="atick-badge" style="background:${{LEVEL_COLOR[c.level]||"#dc2626"}}">${{c.level}}</span> Cyclone ${{c.name}}</span>`
    ));
    // Group district alerts by label to avoid repeating the same type for every district
    const _grouped = {{}};
    _liveDistAlerts.forEach(a => {{
      if (!_grouped[a.label]) _grouped[a.label] = {{ icon: a.icon, color: a.color, label: a.label, cities: [] }};
      _grouped[a.label].cities.push(`${{a.city}}, ${{a.state}} (${{a.temp}}\u00b0C)`);
    }});
    Object.values(_grouped).forEach(g => {{
      const shown = g.cities.join(" \u2022 ");
      items.push(`<span class="atick-item">${{g.icon}} <span class="atick-badge" style="background:${{g.color}}">${{g.label}}</span> ${{shown}}</span>`);
    }});

    if (items.length > 0) {{
      ticker.innerHTML = items.join("");
      bar.classList.remove("hidden");
    }} else {{
      bar.classList.add("hidden");
    }}
  }}

  // Fetch live cyclone data from GDACS RSS via a CORS proxy and refresh ticker
  async function fetchLiveCyclones() {{
    const GDACS_URL = "https://www.gdacs.org/xml/rss.xml";
    const PROXY     = "https://api.allorigins.win/raw?url=" + encodeURIComponent(GDACS_URL);
    try {{
      const r = await fetch(PROXY, {{ cache: "no-store" }});
      if (!r.ok) return;          // silently keep baked-in data
      const xml = await r.text();
      const doc = new DOMParser().parseFromString(xml, "text/xml");
      const NS  = "http://www.gdacs.org";
      const cyclones = [];
      for (const item of Array.from(doc.querySelectorAll("item"))) {{
        if (item.getElementsByTagNameNS(NS, "eventtype")[0]?.textContent !== "TC") continue;
        const lat = parseFloat(item.getElementsByTagNameNS(NS, "lat")[0]?.textContent || "");
        const lon = parseFloat(item.getElementsByTagNameNS(NS, "lon")[0]?.textContent || "");
        // Keep only events in the India + surrounding ocean region
        if (!isNaN(lat) && !isNaN(lon) && !(lat >= 0 && lat <= 35 && lon >= 50 && lon <= 110)) continue;
        const level = item.getElementsByTagNameNS(NS, "alertlevel")[0]?.textContent || "Green";
        const raw   = item.querySelector("title")?.textContent || "";
        const name  = raw.replace(/.*tropical cyclone\\s*/i, "").split(/[.,]/)[0].trim() || raw;
        cyclones.push({{ name, level, lat: isNaN(lat) ? null : lat, lon: isNaN(lon) ? null : lon,
                         description: item.querySelector("description")?.textContent?.slice(0, 200) || "",
                         url: item.querySelector("link")?.textContent || "" }});
      }}
      _liveCyclones = cyclones;
      rebuildAlertTicker();
    }} catch(_) {{ /* keep baked-in cyclone data on any error */ }}
  }}

  // Initial render from baked data, then start live cyclone fetch
  recomputeDistrictAlerts();
  rebuildAlertTicker();
  fetchLiveCyclones();

  // Auto-refresh alerts every 3 minutes independently of the weather refresh cycle
  const ALERT_REFRESH_MS = 3 * 60 * 1000;
  setInterval(() => {{
    recomputeDistrictAlerts();
    rebuildAlertTicker();
    fetchLiveCyclones();
  }}, ALERT_REFRESH_MS);

  // ── Weather theme helper ──────────────────────────────────────────────────
  const WT_CLASSES = ["wt-clear","wt-cloudy","wt-rain","wt-drizzle","wt-thunder","wt-snow","wt-mist"];
  function weatherTheme(desc) {{
    const d = (desc || "").toLowerCase();
    if (d.includes("thunder") || d.includes("storm")) return "wt-thunder";
    if (d.includes("snow") || d.includes("sleet") || d.includes("blizzard")) return "wt-snow";
    if (d.includes("rain") || d.includes("shower")) return "wt-rain";
    if (d.includes("drizzle")) return "wt-drizzle";
    if (d.includes("fog") || d.includes("mist") || d.includes("haze") || d.includes("smoke")) return "wt-mist";
    if (d.includes("cloud") || d.includes("overcast")) return "wt-cloudy";
    if (d.includes("clear") || d.includes("sunny")) return "wt-clear";
    return "wt-cloudy";
  }}

  // ── SVG temperature sparkline ─────────────────────────────────────────────
  function sparklineChart(slots) {{
    if (!slots || slots.length < 2) return "";
    const temps  = slots.map(h => parseFloat(h.tempC) || 0);
    const rains  = slots.map(h => parseFloat(h.rain)  || 0);
    const minT   = Math.min(...temps), maxT = Math.max(...temps);
    const rangeT = (maxT - minT) || 1;
    const W = 260, H = 52, PX = 8, PY = 6;
    const n = temps.length;
    const xStep = (W - PX * 2) / Math.max(n - 1, 1);

    // Coordinate for each point
    const pts = temps.map((t, i) => ({{
      x: PX + i * xStep,
      y: PY + ((maxT - t) / rangeT) * (H - PY * 2)
    }}));

    // Smooth cubic bezier path
    let path = `M ${{pts[0].x.toFixed(1)}} ${{pts[0].y.toFixed(1)}}`;
    for (let i = 1; i < pts.length; i++) {{
      const cp = (pts[i-1].x + pts[i].x) / 2;
      path += ` C ${{cp.toFixed(1)}} ${{pts[i-1].y.toFixed(1)}} ${{cp.toFixed(1)}} ${{pts[i].y.toFixed(1)}} ${{pts[i].x.toFixed(1)}} ${{pts[i].y.toFixed(1)}}`;
    }}

    // Filled area below line
    const area = path + ` L ${{pts[n-1].x.toFixed(1)}} ${{H}} L ${{pts[0].x.toFixed(1)}} ${{H}} Z`;

    // Rain probability bars (light blue, drawn behind line)
    const rainBars = rains.map((r, i) => {{
      if (r < 10) return "";
      const bh = (r / 100) * (H * 0.55);
      const x  = (PX + i * xStep - 3).toFixed(1);
      return `<rect x="${{x}}" y="${{(H - bh).toFixed(1)}}" width="6" height="${{bh.toFixed(1)}}" fill="rgba(96,165,250,0.28)" rx="2"/>`;
    }}).join("");

    // First & last temp labels
    const lblMin = `<text x="${{PX}}" y="${{H - 1}}" fill="rgba(255,255,255,.35)" font-size="8">${{Math.round(minT)}}&deg;</text>`;
    const lblMax = `<text x="${{(W/2 - 8).toFixed(0)}}" y="${{(PY + 1).toFixed(0)}}" fill="rgba(255,255,255,.35)" font-size="8">${{Math.round(maxT)}}&deg;</text>`;

    // Current-point dot
    const dot = `<circle cx="${{pts[0].x.toFixed(1)}}" cy="${{pts[0].y.toFixed(1)}}" r="3" fill="rgba(251,146,60,.9)"/>`;

    const uniqId = "sg" + Math.random().toString(36).slice(2, 7);
    return `
      <div class="sparkline-wrap">
        <div class="sparkline-label">&#127777; ${{n * 3}}h temp trend &nbsp;&#127783; rain chance</div>
        <svg viewBox="0 0 ${{W}} ${{H}}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:52px;display:block">
          <defs>
            <linearGradient id="${{uniqId}}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stop-color="rgba(251,146,60,.35)"/>
              <stop offset="100%" stop-color="rgba(251,146,60,.01)"/>
            </linearGradient>
          </defs>
          ${{rainBars}}
          <path d="${{area}}" fill="url(#${{uniqId}})" stroke="none"/>
          <path d="${{path}}" fill="none" stroke="rgba(251,146,60,.85)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          ${{dot}}${{lblMin}}${{lblMax}}
        </svg>
      </div>`;
  }}

  // ── Weather Detail Modal ───────────────────────────────────────────────────
  let _raf = null;

  function openWeatherModal(d) {{
    const modal  = document.getElementById("w-modal");
    const box    = document.getElementById("w-box");
    const canvas = document.getElementById("w-canvas");
    WT_CLASSES.forEach(c => box.classList.remove(c));
    const wt = weatherTheme(d.desc); if (wt) box.classList.add(wt);

    document.getElementById("w-city").textContent = displayName(d.city);
    document.getElementById("w-rgn").textContent   = d.resolvedLabel;
    document.getElementById("w-obs2").textContent  = d.obsTime;
    document.getElementById("w-bigic").innerHTML   = icon(d.desc);
    document.getElementById("w-bigT").textContent  = d.temp + "\u00b0C";
    document.getElementById("w-dsc").textContent   = d.desc;
    document.getElementById("w-fl").textContent    = "Feels like " + d.feelsLike + "\u00b0C";

    document.getElementById("w-tiles").innerHTML = [
      ["&#128167;","Humidity",  d.humidity+"%"],
      ["&#127788;","Wind",      d.wind+" km/h "+d.windDir],
      ["&#128065;","Visibility",d.vis+" km"],
      ["&#9729;",  "Cloud",     d.cloud+"%"],
      ["&#127897;","Pressure",  d.pressure+" mb"],
      ["&#127777;","Feels Like",d.feelsLike+"&deg;C"],
    ].map(([i,l,v])=>`<div class="w-tile"><div class="w-tile-i">${{i}}</div><div class="w-tile-l">${{l}}</div><div class="w-tile-v">${{v}}</div></div>`).join("");

    const allSlots = [];
    (d.forecast||[]).forEach(day=>(day.hourly||[]).forEach(h=>allSlots.push({{date:day.date,...h}})));
    document.getElementById("w-chart").innerHTML = modalChart(allSlots);

    const _fcDays = (d.forecast||[]).length;
    document.getElementById("w-fcs-label").textContent = `\\u{{1F4C5}} ${{_fcDays}}-Day Forecast`;
    document.getElementById("w-fcs").innerHTML = (d.forecast||[]).map(f=>`
      <div class="w-fc">
        <div class="w-fc-d">${{new Date(f.date+"T12:00:00").toLocaleDateString("en-US",{{weekday:"short"}})}} &bull; ${{f.date.slice(5)}}</div>
        <div class="w-fc-i">${{icon(f.desc)}}</div>
        <div class="w-fc-h">${{f.maxC}}&deg;</div>
        <div class="w-fc-l">${{f.minC}}&deg;</div>
        <div class="w-fc-s">${{f.desc}}</div>
      </div>`).join("");

    if (_raf) {{ cancelAnimationFrame(_raf); _raf=null; }}
    requestAnimationFrame(() => {{
      canvas.width  = box.offsetWidth;
      canvas.height = box.scrollHeight;
      _raf = startParticles(wt, canvas);
    }});
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }}

  function closeWeatherModal() {{
    document.getElementById("w-modal").classList.remove("open");
    document.body.style.overflow = "";
    if (_raf) {{ cancelAnimationFrame(_raf); _raf=null; }}
  }}
  document.addEventListener("keydown", e=>{{ if(e.key==="Escape") closeWeatherModal(); }});

  function startParticles(wt, canvas) {{
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0,0,canvas.width,canvas.height);

    if (["wt-rain","wt-drizzle","wt-thunder"].includes(wt)) {{
      const col = wt==="wt-thunder" ? "rgba(160,140,210," : "rgba(174,214,241,";
      const drops = Array.from({{length:wt==="wt-thunder"?80:130}}, ()=>({{x:Math.random()*canvas.width,y:Math.random()*canvas.height,len:Math.random()*20+8,spd:Math.random()*4+3,op:Math.random()*.35+.15}}));
      let fl=0;
      const fr=()=>{{ ctx.clearRect(0,0,canvas.width,canvas.height);
        if(wt==="wt-thunder"&&++fl%200<4){{ ctx.fillStyle="rgba(180,150,255,.1)"; ctx.fillRect(0,0,canvas.width,canvas.height); }}
        drops.forEach(d=>{{ ctx.beginPath(); ctx.moveTo(d.x,d.y); ctx.lineTo(d.x+1.5,d.y+d.len); ctx.strokeStyle=col+d.op+")"; ctx.lineWidth=1; ctx.stroke(); d.y+=d.spd; if(d.y>canvas.height+d.len){{ d.y=-d.len; d.x=Math.random()*canvas.width; }} }});
        return requestAnimationFrame(fr); }};
      return fr();
    }}
    if (wt==="wt-snow") {{
      const fl=Array.from({{length:70}},()=>({{x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*3+1,spd:Math.random()*1.2+.4,dr:(Math.random()-.5)*.7,op:Math.random()*.55+.3}}));
      const fr=()=>{{ ctx.clearRect(0,0,canvas.width,canvas.height);
        fl.forEach(f=>{{ ctx.beginPath(); ctx.arc(f.x,f.y,f.r,0,Math.PI*2); ctx.fillStyle=`rgba(255,255,255,${{f.op}})`; ctx.fill(); f.y+=f.spd; f.x+=f.dr;
          if(f.y>canvas.height){{ f.y=0; f.x=Math.random()*canvas.width; }}
          if(f.x>canvas.width) f.x=0; if(f.x<0) f.x=canvas.width; }});
        return requestAnimationFrame(fr); }};
      return fr();
    }}
    if (wt==="wt-clear") {{
      let ang=0;
      const cx=canvas.width*.72, cy=100, r0=42;
      const fr=()=>{{ ctx.clearRect(0,0,canvas.width,canvas.height); ang+=.004;
        for(let i=0;i<12;i++){{ const a=(i/12)*Math.PI*2+ang; const x1=cx+Math.cos(a)*(r0+6),y1=cy+Math.sin(a)*(r0+6);
          const rr=r0+30+Math.sin(ang*4+i)*12; const x2=cx+Math.cos(a)*rr,y2=cy+Math.sin(a)*rr;
          ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.strokeStyle="rgba(255,215,50,.28)"; ctx.lineWidth=2.5; ctx.stroke(); }}
        const g=ctx.createRadialGradient(cx,cy,0,cx,cy,r0+14); g.addColorStop(0,"rgba(255,230,80,.22)"); g.addColorStop(1,"rgba(255,200,50,0)");
        ctx.beginPath(); ctx.arc(cx,cy,r0+14,0,Math.PI*2); ctx.fillStyle=g; ctx.fill();
        return requestAnimationFrame(fr); }};
      return fr();
    }}
    return null;
  }}

  function modalChart(slots) {{
    if (!slots||slots.length<2) return "";
    const temps=slots.map(h=>parseFloat(h.tempC)||0), rains=slots.map(h=>parseFloat(h.rain)||0);
    const minT=Math.min(...temps), maxT=Math.max(...temps), rangeT=(maxT-minT)||1;
    const W=600,H=130,PX=32,PY=12,BP=24, n=slots.length;
    const xSt=(W-PX*2)/Math.max(n-1,1);
    const pts=temps.map((t,i)=>({{x:PX+i*xSt, y:PY+((maxT-t)/rangeT)*(H-PY-BP)}}));
    let path=`M ${{pts[0].x.toFixed(1)}} ${{pts[0].y.toFixed(1)}}`;
    for(let i=1;i<pts.length;i++){{ const cp=(pts[i-1].x+pts[i].x)/2; path+=` C ${{cp.toFixed(1)}} ${{pts[i-1].y.toFixed(1)}} ${{cp.toFixed(1)}} ${{pts[i].y.toFixed(1)}} ${{pts[i].x.toFixed(1)}} ${{pts[i].y.toFixed(1)}}`; }}
    const area=path+` L ${{pts[n-1].x.toFixed(1)}} ${{(H-BP).toFixed(1)}} L ${{pts[0].x.toFixed(1)}} ${{(H-BP).toFixed(1)}} Z`;
    const bars=rains.map((r,i)=>{{ if(r<5)return""; const bh=(r/100)*(BP*.8),x=(PX+i*xSt-4).toFixed(1); return `<rect x="${{x}}" y="${{(H-BP-bh).toFixed(1)}}" width="8" height="${{bh.toFixed(1)}}" fill="rgba(96,165,250,.35)" rx="2"/>` }}).join("");
    const dots=pts.map((p,i)=>{{ if(i%2!==0)return""; return `<circle cx="${{p.x.toFixed(1)}}" cy="${{p.y.toFixed(1)}}" r="2.5" fill="rgba(251,146,60,.8)"/><text x="${{p.x.toFixed(1)}}" y="${{(p.y-5).toFixed(1)}}" fill="rgba(255,255,255,.55)" font-size="8" text-anchor="middle">${{Math.round(temps[i])}}&deg;</text>`}}).join("");
    const xlbl=slots.map((h,i)=>{{ if(i%2!==0)return""; const x=(PX+i*xSt).toFixed(1); return `<text x="${{x}}" y="${{H}}" fill="rgba(255,255,255,.3)" font-size="8" text-anchor="middle">${{fmtHour(h.time)}}</text>`}}).join("");
    const uid="lc"+Math.random().toString(36).slice(2,7);
    return `<svg class="w-chart-svg" viewBox="0 0 ${{W}} ${{H}}" height="120">
      <defs><linearGradient id="${{uid}}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="rgba(251,146,60,.5)"/><stop offset="100%" stop-color="rgba(251,146,60,.02)"/></linearGradient></defs>
      ${{bars}}<path d="${{area}}" fill="url(#${{uid}})" stroke="none"/>
      <path d="${{path}}" fill="none" stroke="rgba(251,146,60,.95)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      ${{dots}}${{xlbl}}
      <text x="0" y="${{(H-BP+4).toFixed(1)}}" fill="rgba(255,255,255,.3)" font-size="9">${{Math.round(minT)}}&deg;</text>
      <text x="0" y="${{(PY+8).toFixed(1)}}" fill="rgba(255,255,255,.3)" font-size="9">${{Math.round(maxT)}}&deg;</text>
    </svg>`;
  }}

  function renderCard(el, d) {{
    const ic   = icon(d.desc);
    const rows = d.forecast.map(f=>`
      <div class="fc-day">
        <div class="fc-date">${{new Date(f.date+"T12:00:00").toLocaleDateString("en-US",{{weekday:"short"}})}} ${{f.date.slice(5)}}</div>
        <div>${{icon(f.desc)}}</div>
        <div class="fc-hi">${{f.maxC}}&deg;</div>
        <div class="fc-lo">${{f.minC}}&deg;</div>
      </div>`).join("");

    // Build next-24h hourly slots from current time
    const _now      = new Date();
    const _nowTime  = _now.getHours() * 100;
    const _todayISO = _now.toISOString().slice(0, 10);
    const _allSlots = [];
    (d.forecast || []).forEach(day => {{
      (day.hourly || []).forEach(h => _allSlots.push({{ date: day.date, ...h }}));
    }});
    const _upcoming = _allSlots.filter(h => {{
      if (h.date > _todayISO) return true;
      if (h.date === _todayISO) return h.time >= _nowTime;
      return false;
    }}).slice(0, 24);
    const hourlyRows = _upcoming.map((h, i) => `
      <div class="hr-slot${{i===0?' hr-current':''}}">
        <div class="hr-time">${{fmtHour(h.time)}}</div>
        <div>${{icon(h.desc)}}</div>
        <div class="hr-temp">${{h.tempC}}&deg;</div>
        <div class="hr-rain">&#127783;${{h.rain}}%</div>
      </div>`).join("");

    // SVG sparkline: use hourly slots when available, otherwise
    // synthesise two data points per day (max at 09:00, min at 21:00)
    // so cached daily-only data still produces a visible temperature curve.
    let _sparkSlots = _upcoming;
    if (_sparkSlots.length < 2) {{
      _sparkSlots = [];
      (d.forecast || []).forEach(f => {{
        _sparkSlots.push({{ date: f.date, time: 900,  tempC: String(f.maxC ?? 0), rain: f.rainPct || "0", desc: f.desc || "" }});
        _sparkSlots.push({{ date: f.date, time: 2100, tempC: String(f.minC ?? 0), rain: f.rainPct || "0", desc: f.desc || "" }});
      }});
    }}
    const sparkSvg = sparklineChart(_sparkSlots);

    // Alert badges: computed live from this card's weather data
    const _stateObj  = STATES.find(s => s.cities.includes(d.city));
    const distAlerts = _alertsFor(d.city, _stateObj?.name || "", d);
    const badgesHtml = distAlerts.length
      ? `<div class="city-alerts">${{distAlerts.map(a=>`<span class="alert-badge" style="background:${{a.color}}">${{a.icon}} ${{a.label}}</span>`).join("")}}</div>`
      : "";

    el.innerHTML = `
      <div class="city-card-top">
        <div>
          <div class="city-name">${{displayName(d.city)}}</div>
          <div class="city-region${{d.wrongLocation ? ' wrong-location' : ''}}">${{d.resolvedLabel}}${{d.wrongLocation ? ' &#9888;' : ''}}</div>
          <div class="city-obs">${{d.obsTime}}</div>
        </div>
        <div style="text-align:right">
          <div class="city-icon">${{ic}}</div>
          <div class="city-temp">${{d.temp}}&deg;C</div>
        </div>
      </div>
      ${{badgesHtml}}
      <div class="city-desc">${{d.desc}}</div>
      <div class="city-metrics">
        <div class="city-metric">&#128167; Humidity <span>${{d.humidity}}%</span></div>
        <div class="city-metric">&#127788; Wind <span>${{d.wind}} km/h ${{d.windDir}}</span></div>
        <div class="city-metric">&#128065; Visibility <span>${{d.vis}} km</span></div>
        <div class="city-metric">&#9729; Cloud <span>${{d.cloud}}%</span></div>
        <div class="city-metric">&#127774; UV Index <span>${{d.uv}}</span></div>
        <div class="city-metric">&#127897; Pressure <span>${{d.pressure}} mb</span></div>
      </div>
      <div class="city-forecast">${{rows}}</div>
      ${{sparkSvg}}
      <div class="hourly-toggle" onclick="this.nextElementSibling.classList.toggle('open')">&#9660; Hourly Detail</div>
      <div class="hourly-strip">${{hourlyRows}}</div>`;

    WT_CLASSES.forEach(c => el.classList.remove(c));
    el.classList.remove("refreshing");
    const wt = weatherTheme(d.desc);
    if (wt) el.classList.add(wt);
    el.setAttribute("data-clickable","1");
    el.onclick = () => openWeatherModal(d);
    injectParticles(el, wt, d.temp);
  }}

  // ── Weather Particle Effects ────────────────────────────────────────────────
  function injectParticles(card, theme, temp) {{
    card.querySelector(".wx-particles")?.remove();
    const wrap = document.createElement("div");
    wrap.className = "wx-particles";
    const t = parseFloat(temp) || 0;

    // ── Rain / Drizzle ──────────────────────────────────────────────────────
    if (theme === "wt-rain" || theme === "wt-drizzle") {{
      const count = theme === "wt-rain" ? 18 : 10;
      for (let i = 0; i < count; i++) {{
        const p = document.createElement("div"); p.className = "wx-p";
        const x   = Math.random() * 100;
        const h   = 7 + Math.random() * 10;
        const dur = 0.45 + Math.random() * 0.55;
        const del = Math.random() * 2.5;
        const op  = 0.45 + Math.random() * 0.45;
        p.style.cssText = `left:${{x}}%;top:-12px;width:1.5px;height:${{h}}px;`
          + `background:linear-gradient(180deg,transparent,rgba(96,165,250,${{op}}));`
          + `border-radius:0 0 2px 2px;`
          + `animation:wx-rain ${{dur}}s ${{del}}s linear infinite;`;
        wrap.appendChild(p);
      }}
    }}

    // ── Snow / Cold ─────────────────────────────────────────────────────────
    if (theme === "wt-snow" || card.classList.contains("is-coldest")) {{
      const glyphs = ["❄","❅","✦","·","✧","⋆"];
      for (let i = 0; i < 11; i++) {{
        const p = document.createElement("div"); p.className = "wx-p";
        const x   = 2 + Math.random() * 88;
        const sz  = 8 + Math.random() * 11;
        const dur = 2.5 + Math.random() * 3;
        const del = Math.random() * 5;
        p.style.cssText = `left:${{x}}%;top:-16px;font-size:${{sz}}px;line-height:1;`
          + `color:rgba(186,230,253,0.85);`
          + `animation:wx-snow ${{dur}}s ${{del}}s linear infinite;`;
        p.textContent = glyphs[i % glyphs.length];
        wrap.appendChild(p);
      }}
    }}

    // ── Heat / Sunny (≥ 36 °C) ──────────────────────────────────────────────
    if ((theme === "wt-clear" || card.classList.contains("is-hottest")) && t >= 36) {{
      // Rising shimmer waves
      for (let i = 0; i < 5; i++) {{
        const p = document.createElement("div"); p.className = "wx-p";
        const w   = 28 + Math.random() * 46;
        const x   = Math.random() * (100 - w);
        const bot = 4 + i * 9;
        const dur = 1.4 + Math.random() * 1.8;
        const del = Math.random() * 2.5;
        p.style.cssText = `left:${{x}}%;bottom:${{bot}}px;width:${{w}}%;height:3px;`
          + `background:linear-gradient(90deg,transparent,rgba(251,146,60,.3),rgba(253,224,71,.4),rgba(251,146,60,.3),transparent);`
          + `border-radius:50%;filter:blur(2.5px);`
          + `animation:wx-heat ${{dur}}s ${{del}}s ease-in-out infinite;`;
        wrap.appendChild(p);
      }}
      // Glowing heat orb (top-right corner)
      const orb = document.createElement("div"); orb.className = "wx-p";
      orb.style.cssText = `right:6px;top:6px;width:52px;height:52px;`
        + `background:radial-gradient(circle,rgba(251,146,60,.28) 0%,rgba(253,224,71,.14) 50%,transparent 70%);`
        + `border-radius:50%;filter:blur(5px);`
        + `animation:wx-orb 2.2s ease-in-out infinite;`;
      wrap.appendChild(orb);
    }}

    // ── Thunder ─────────────────────────────────────────────────────────────
    if (theme === "wt-thunder") {{
      for (let i = 0; i < 4; i++) {{
        const p = document.createElement("div"); p.className = "wx-p";
        const x   = 5 + Math.random() * 80;
        const y   = 4 + Math.random() * 55;
        const sz  = 11 + Math.random() * 12;
        const dur = 3 + Math.random() * 5;
        const del = Math.random() * 5;
        p.style.cssText = `left:${{x}}%;top:${{y}}%;font-size:${{sz}}px;line-height:1;`
          + `color:rgba(167,139,250,.95);filter:drop-shadow(0 0 4px #a78bfa);`
          + `animation:wx-bolt ${{dur}}s ${{del}}s ease-in-out infinite;`;
        p.textContent = "⚡";
        wrap.appendChild(p);
      }}
    }}

    // ── Mist / Fog / Haze ───────────────────────────────────────────────────
    if (theme === "wt-mist") {{
      for (let i = 0; i < 4; i++) {{
        const p = document.createElement("div"); p.className = "wx-p";
        const y   = 12 + i * 22;
        const h   = 14 + Math.random() * 18;
        const dur = 7 + Math.random() * 5;
        const del = i * 1.8;
        p.style.cssText = `left:-25%;top:${{y}}%;width:150%;height:${{h}}px;`
          + `background:linear-gradient(90deg,transparent,rgba(148,163,184,.14),rgba(148,163,184,.16),rgba(148,163,184,.14),transparent);`
          + `border-radius:50%;filter:blur(7px);`
          + `animation:wx-fog ${{dur}}s ${{del}}s ease-in-out infinite;`;
        wrap.appendChild(p);
      }}
    }}

    if (wrap.children.length > 0) card.insertBefore(wrap, card.firstChild);
  }}

  function setCardError(el, city, msg) {{
    el.innerHTML = `<div class="city-name">${{city}}</div>
                    <div class="error-msg">&#9888; ${{msg}}</div>`;
    el.classList.remove("refreshing");
  }}

  function updateStateStatus(stateId) {{
    const cards  = document.querySelectorAll(`#section-${{stateId}} .city-card`);
    const loaded = [...cards].filter(c => !c.classList.contains("refreshing")).length;
    const el = document.getElementById(`status-${{stateId}}`);
    if (el) el.textContent = `${{loaded}}/${{cards.length}} loaded`;
  }}

  // ── Temperature Extremes ────────────────────────────────────────────────────
  // Per-state: highlight hottest + coldest card; update state header
  function updateStateExtremes(stateId) {{
    const cards = Array.from(document.querySelectorAll(`#section-${{stateId}} .city-card`))
      .filter(c => !c.classList.contains("refreshing") && c.querySelector(".city-temp"));

    if (cards.length === 0) return;

    // Remove previous highlights
    cards.forEach(c => {{
      c.classList.remove("is-hottest","is-coldest");
      c.querySelectorAll(".temp-badge").forEach(b => b.remove());
    }});

    const temps = cards.map(c => ({{
      card: c,
      name: c.querySelector(".city-name")?.textContent || "",
      temp: parseFloat(c.querySelector(".city-temp")?.textContent || "0"),
    }}));

    const maxT = Math.max(...temps.map(t => t.temp));
    const minT = Math.min(...temps.map(t => t.temp));

    temps.forEach(t => {{
      if (t.temp === maxT) {{
        t.card.classList.add("is-hottest");
        const badge = document.createElement("span");
        badge.className = "temp-badge hot"; badge.textContent = "&#128293; Hottest in state";
        badge.innerHTML = "&#128293; Hottest in state";
        t.card.querySelector(".city-name")?.after(badge);
      }}
      if (t.temp === minT && minT !== maxT) {{
        t.card.classList.add("is-coldest");
        const badge = document.createElement("span");
        badge.className = "temp-badge cold";
        badge.innerHTML = "&#10052; Coldest in state";
        t.card.querySelector(".city-name")?.after(badge);
      }}
    }});

    // Update state header status to also show extremes
    const hotCard = temps.find(t => t.temp === maxT);
    const coldCard = temps.find(t => t.temp === minT);
    const el = document.getElementById(`status-${{stateId}}`);
    const loaded = cards.length;
    const total  = document.querySelectorAll(`#section-${{stateId}} .city-card`).length;
    if (el && hotCard && coldCard) {{
      el.innerHTML = `${{loaded}}/${{total}} loaded &nbsp;&#128293; <b style="color:#fb923c">${{hotCard.name}} ${{maxT}}°C</b> &nbsp;&#10052; <b style="color:#38bdf8">${{coldCard.name}} ${{minT}}°C</b>`;
    }}
  }}

  // Global: find hottest + coldest across all loaded districts
  function updateGlobalExtremes() {{
    const allCards = Array.from(document.querySelectorAll(".city-card"))
      .filter(c => !c.classList.contains("refreshing") && c.querySelector(".city-temp"));

    if (allCards.length < 2) return;

    const entries = allCards.map(c => {{
      // Determine state name from parent section
      const sec = c.closest(".state-section");
      const stateHeading = sec?.querySelector("h2")?.textContent || "";
      return {{
        name:  c.querySelector(".city-name")?.textContent || "",
        state: stateHeading,
        temp:  parseFloat(c.querySelector(".city-temp")?.textContent || "0"),
      }};
    }});

    const maxT = Math.max(...entries.map(e => e.temp));
    const minT = Math.min(...entries.map(e => e.temp));
    const hot  = entries.find(e => e.temp === maxT);
    const cold = entries.find(e => e.temp === minT);

    const pillHot  = document.getElementById("pill-hot");
    const pillCold = document.getElementById("pill-cold");
    const spanHot  = document.getElementById("global-hot");
    const spanCold = document.getElementById("global-cold");

    if (hot && pillHot && spanHot) {{
      pillHot.style.display = "";
      spanHot.textContent = `${{hot.name}}, ${{hot.state}} — ${{maxT}}°C`;
    }}
    if (cold && pillCold && spanCold) {{
      pillCold.style.display = "";
      spanCold.textContent = `${{cold.name}}, ${{cold.state}} — ${{minT}}°C`;
    }}

    // Rebuild live alert ticker every time global extremes update
    recomputeDistrictAlerts();
    rebuildAlertTicker();
  }}

  function setGlobalStatus(fetching) {{
    const dot   = document.getElementById("live-dot");
    const label = document.getElementById("live-label");
    const btn   = document.getElementById("refresh-btn");
    if (fetching) {{
      dot.classList.add("loading"); label.textContent = "Fetching…"; btn.disabled = true;
    }} else {{
      dot.classList.remove("loading"); label.textContent = "Live"; btn.disabled = false;
      const now = new Date();
      const timeStr = now.toLocaleTimeString("en-IN", {{hour:"2-digit",minute:"2-digit"}});
      const dateStr = now.toLocaleDateString("en-IN", {{day:"2-digit",month:"short"}});
      document.getElementById("last-updated").textContent = dateStr + ", " + timeStr;
      document.getElementById("pill-last-updated").style.display = "";
    }}
  }}

  // Strip state-qualifier suffixes before sending to OWM (e.g. "Mon Nagaland" → "Mon")
  const STATE_SUFFIXES = new RegExp("\\\\s+(Uttar Pradesh|Nagaland|Madhya Pradesh|West Bengal|Tamil Nadu|Andhra Pradesh|Himachal Pradesh|Arunachal Pradesh|Karnataka|Maharashtra|India)$", "i");
  function displayName(city) {{ return city.replace(STATE_SUFFIXES, '').trim(); }}

  // ── Core fetch ─────────────────────────────────────────────────────────────
  // Parse a wttr.in ?format=j1 response into the card data shape.
  function parseWttr(json, cityName) {{
    const cur  = json.current_condition?.[0] || {{}};
    const area = json.nearest_area?.[0] || {{}};
    const name = area.areaName?.[0]?.value || cityName;
    const forecast = (json.weather || []).map(d => ({{
      date: d.date,
      maxC: parseInt(d.maxtempC) || 0,
      minC: parseInt(d.mintempC) || 0,
      desc: d.hourly?.[4]?.weatherDesc?.[0]?.value || "",
      rainPct: d.hourly?.[4]?.chanceofrain || "0",
      hourly: (d.hourly || []).map(h => ({{
        time: parseInt(h.time) || 0,
        tempC: h.tempC || "0",
        desc:  h.weatherDesc?.[0]?.value || "",
        rain:  h.chanceofrain || "0"
      }}))
    }}));
    return {{
      city: cityName, region: name,
      resolvedLabel: name + ", India",
      wrongLocation: false,
      temp:     cur.temp_C || "N/A",
      feelsLike:cur.FeelsLikeC || "N/A",
      humidity: cur.humidity || "0",
      desc:     cur.weatherDesc?.[0]?.value || "N/A",
      wind:     cur.windspeedKmph || "0",
      windDir:  cur.winddir16Point || "N",
      vis:      cur.visibility || "N/A",
      pressure: cur.pressure || "N/A",
      uv:       cur.uvIndex || "N/A",
      cloud:    cur.cloudcover || "0",
      obsTime:  new Date().toLocaleString("en-IN",{{
        timeZone:"Asia/Kolkata",day:"2-digit",month:"short",
        year:"numeric",hour:"2-digit",minute:"2-digit",hour12:true
      }}) + " IST (wttr.in)",
      forecast,
    }};
  }}

  // Build card data from an Open-Meteo /forecast response.
  function buildFromOpenMeteo(omJson, cityName, resolvedCity) {{
    const cur  = omJson.current || {{}};
    const code = cur.weathercode ?? 0;

    const omHrByDate = {{}};
    if (omJson.hourly) {{
      const h = omJson.hourly;
      (h.time || []).forEach((t, i) => {{
        if (parseInt(t.slice(11,13)) % 3 !== 0) return;
        const date = t.slice(0,10);
        if (!omHrByDate[date]) omHrByDate[date] = [];
        omHrByDate[date].push({{
          time: parseInt(t.slice(11,13))*100,
          tempC: String(Math.round(h.temperature_2m?.[i]??0)),
          desc:  WMO_DESC[h.weathercode?.[i]??0]||"Unknown",
          rain:  String(h.precipitation_probability?.[i]??0)
        }});
      }});
    }}

    const forecast = (omJson.daily?.time||[]).slice(0,7).map((date,i) => {{
      const dc = omJson.daily.weathercode?.[i]??0;
      return {{
        date,
        maxC: Math.round(omJson.daily.temperature_2m_max?.[i]??0),
        minC: Math.round(omJson.daily.temperature_2m_min?.[i]??0),
        desc: WMO_DESC[dc]||"Variable clouds",
        rainPct: String(omJson.daily.precipitation_probability_max?.[i]??0),
        hourly: omHrByDate[date]||[]
      }};
    }});

    return {{
      city: cityName, region: resolvedCity,
      resolvedLabel: resolvedCity + ", India",
      wrongLocation: false,
      temp:      String(Math.round(cur.temperature_2m??0)),
      feelsLike: String(Math.round(cur.apparent_temperature??cur.temperature_2m??0)),
      humidity:  String(cur.relative_humidity_2m??0),
      desc:      WMO_DESC[code]||"Unknown",
      wind:      String(Math.round(cur.wind_speed_10m??0)),
      windDir:   degToDir(cur.wind_direction_10m),
      vis:       String(Math.round((cur.visibility??0)/1000)),
      pressure:  String(Math.round(cur.pressure_msl??0)),
      uv: "N/A", cloud: String(cur.cloud_cover??0),
      obsTime: new Date().toLocaleString("en-IN",{{
        timeZone:"Asia/Kolkata",day:"2-digit",month:"short",
        year:"numeric",hour:"2-digit",minute:"2-digit",hour12:true
      }}) + " IST",
      forecast,
    }};
  }}

  // Pure Open-Meteo fetch: geocode → weather (no OWM call).
  async function fetchCity(city, cardEl, signal) {{
    cardEl.classList.add("refreshing");
    cardEl.innerHTML = skeleton();
    const queryCity = owmCity(displayName(city));
    try {{
      // Step 1: coordinates from sessionStorage cache or OM geocoding
      let lat = null, lon = null, resolvedName = queryCity;
      const gcKey = "gc_" + queryCity;
      const gcHit = sessionStorage.getItem(gcKey);
      if (gcHit) {{
        const c = JSON.parse(gcHit); lat = c.lat; lon = c.lon; resolvedName = c.name || queryCity;
      }} else {{
        const gcR = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${{encodeURIComponent(queryCity)}}&count=5&language=en&format=json`,
          {{ cache:"force-cache", signal }}
        );
        if (gcR.ok) {{
          const gc   = await gcR.json();
          const hits = (gc.results||[]);
          const r0   = hits.find(r=>r.country_code==="IN") || hits[0];
          if (r0) {{
            lat = r0.latitude; lon = r0.longitude;
            resolvedName = r0.name || queryCity;
            sessionStorage.setItem(gcKey, JSON.stringify({{lat,lon,name:resolvedName}}));
          }}
        }}
      }}
      if (lat == null) {{
        // Geocoding failed — try wttr.in directly (no coordinates needed)
        return fetchCityFromWttr(city, cardEl, signal);
      }}

      // Step 2: Open-Meteo current + 7-day forecast
      const omUrl = `https://api.open-meteo.com/v1/forecast?latitude=${{lat}}&longitude=${{lon}}`
        + `&current=temperature_2m,relative_humidity_2m,apparent_temperature,weathercode,cloud_cover,pressure_msl,visibility,wind_speed_10m,wind_direction_10m`
        + `&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max`
        + `&hourly=temperature_2m,precipitation_probability,weathercode`
        + `&forecast_days=7&timezone=Asia%2FKolkata&wind_speed_unit=kmh`;
      const omR = await fetch(omUrl, {{ cache:"no-store", signal }});
      if (omR.status === 429) {{
        // Open-Meteo rate-limited — fall back to wttr.in (free, no key, no limit)
        return fetchCityFromWttr(city, cardEl, signal);
      }}
      if (!omR.ok) throw new Error(`Open-Meteo HTTP ${{omR.status}}`);
      const omJson = await omR.json();

      const data = buildFromOpenMeteo(omJson, city, resolvedName);
      dataCache[city] = data;
      renderCard(cardEl, data);
      return true;
    }} catch(e) {{
      if (e.name === "AbortError") {{ cardEl.innerHTML = skeleton(); cardEl.classList.add("refreshing"); return false; }}
      // Any Open-Meteo error → fall back to wttr.in
      return fetchCityFromWttr(city, cardEl, signal);
    }}
  }}

  // Fallback fetch using wttr.in (no API key, no rate limit).
  async function fetchCityFromWttr(city, cardEl, signal) {{
    const queryCity = owmCity(displayName(city));
    try {{
      const url  = `https://wttr.in/${{encodeURIComponent(queryCity)}}?format=j1`;
      const resp = await fetch(url, {{ cache:"no-store", signal }});
      if (!resp.ok) throw new Error(`wttr.in HTTP ${{resp.status}}`);
      const data = parseWttr(await resp.json(), city);
      dataCache[city] = data;
      renderCard(cardEl, data);
      return true;
    }} catch(e) {{
      if (e.name === "AbortError") {{ cardEl.innerHTML = skeleton(); cardEl.classList.add("refreshing"); return false; }}
      dataCache[city] = null;
      setCardError(cardEl, city, e.message);
      return false;
    }}
  }}

  // ── Load a single state (respects abort signal) ────────────────────────────
  async function loadState(state, signal, forceRefresh = false) {{
    const grid = document.getElementById(`grid-${{state.id}}`);
    if (!grid) return;

    const toFetch = [];
    state.cities.forEach((city, idx) => {{
      const card = grid.querySelectorAll(".city-card")[idx];
      if (!card) return;
      if (!forceRefresh && dataCache[city]) {{
        // Serve from cache immediately
        renderCard(card, dataCache[city]);
      }} else {{
        toFetch.push({{ city, card }});
      }}
    }});

    updateStateStatus(state.id);
    if (toFetch.length === 0) {{
      updateStateExtremes(state.id);
      updateGlobalExtremes();
      return;
    }}

    for (let i = 0; i < toFetch.length; i += BATCH_SIZE) {{
      if (signal && signal.aborted) return;
      const batch = toFetch.slice(i, i + BATCH_SIZE);
      await Promise.allSettled(batch.map(t => fetchCity(t.city, t.card, signal)));
      updateStateStatus(state.id);
      if (i + BATCH_SIZE < toFetch.length && !(signal && signal.aborted)) {{
        await new Promise(r => setTimeout(r, BATCH_DELAY));
      }}
    }}
    updateStateStatus(state.id);
    if (!(signal && signal.aborted)) {{
      updateStateExtremes(state.id);   // highlight hottest/coldest in this state
      updateGlobalExtremes();          // refresh India-wide extremes pill
    }}
  }}

  // ── Load all states in parallel (up to STATE_WORKERS at a time) ──────────
  const STATE_WORKERS = 5;
  async function loadAllStates(signal, forceRefresh = false) {{
    setGlobalStatus(true);
    // Run STATE_WORKERS state loads concurrently
    const queue = [...STATES];
    async function worker() {{
      while (queue.length > 0) {{
        if (signal && signal.aborted) return;
        const state = queue.shift();
        if (state) await loadState(state, signal, forceRefresh);
      }}
    }}
    const workers = Array.from({{ length: STATE_WORKERS }}, () => worker());
    await Promise.allSettled(workers);
    if (!(signal && signal.aborted)) setGlobalStatus(false);
  }}

  // ── Build DOM layout ───────────────────────────────────────────────────────
  function buildLayout() {{
    const nav = document.getElementById("state-nav");
    const container = document.getElementById("state-container");
    nav.innerHTML = `<button class="state-btn all-btn active" style="--c:#64748b"
                             onclick="filterState('all',this)">All States &amp; UTs</button>`;
    container.innerHTML = "";

    let utSeparatorAdded = false;
    STATES.forEach(state => {{
      // Insert UT separator before first UT
      if (!utSeparatorAdded && UT_IDS.has(state.id)) {{
        utSeparatorAdded = true;
        const sep = document.createElement("span");
        sep.className = "state-btn ut-separator";
        sep.textContent = "Union Territories";
        nav.appendChild(sep);
      }}
      const btn = document.createElement("button");
      btn.className = "state-btn";
      btn.style.setProperty("--c", state.color);
      btn.textContent = state.name;
      btn.onclick = () => filterState(state.id, btn);
      nav.appendChild(btn);

      const section = document.createElement("div");
      section.className = "state-section";
      section.id = `section-${{state.id}}`;
      section.innerHTML = `
        <div class="state-header" style="--accent:${{state.color}}">
          <h2 style="--accent:${{state.color}}">${{state.name}}</h2>
          <span class="state-badge">${{state.cities.length}} districts</span>
          <span class="state-load-status" id="status-${{state.id}}">Waiting&hellip;</span>
        </div>
        <div class="city-grid" id="grid-${{state.id}}"></div>`;
      container.appendChild(section);

      const grid = section.querySelector(".city-grid");
      state.cities.forEach(() => {{
        const card = document.createElement("div");
        card.className = "city-card";
        card.style.setProperty("--accent", state.color);
        card.innerHTML = skeleton();
        card.classList.add("refreshing");
        grid.appendChild(card);
      }});
    }});
  }}

  // ── Filter by state ────────────────────────────────────────────────────────
  function filterState(id, btnEl) {{
    // Remove "no cache" placeholder if still present
    const emptyMsg = document.getElementById("empty-msg");
    if (emptyMsg) emptyMsg.remove();

    // Update active button
    document.querySelectorAll(".state-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
    activeFilter = id;

    // Show/hide sections
    STATES.forEach(s => {{
      const sec = document.getElementById(`section-${{s.id}}`);
      if (sec) sec.style.display = (id === "all" || id === s.id) ? "" : "none";
    }});

    // Abort whatever is running
    if (abortCtrl) abortCtrl.abort();
    abortCtrl = new AbortController();
    const signal = abortCtrl.signal;

    if (id === "all") {{
      // Back to all: scroll top, resume loading everything from cache where possible
      window.scrollTo({{ top: 0, behavior: "smooth" }});
      loadAllStates(signal, false);
    }} else {{
      // Specific state: scroll into view, load just this state (fast)
      const target = document.getElementById(`section-${{id}}`);
      if (target) {{
        const headerH = document.querySelector("header")?.offsetHeight || 0;
        const top = target.getBoundingClientRect().top + window.scrollY - headerH - 12;
        window.scrollTo({{ top, behavior: "smooth" }});
      }}
      const state = STATES.find(s => s.id === id);
      if (state) {{
        setGlobalStatus(true);
        loadState(state, signal, false).then(() => {{
          if (!signal.aborted) setGlobalStatus(false);
        }});
      }}
    }}
  }}

  // ── Timer ──────────────────────────────────────────────────────────────────
  function startTimer() {{
    clearInterval(timerID);
    countdown = REFRESH_SECS;
    timerID = setInterval(() => {{
      countdown--;
      const m = String(Math.floor(countdown / 60)).padStart(1, "0");
      const s = String(countdown % 60).padStart(2, "0");
      const el = document.getElementById("countdown");
      if (el) el.textContent = `${{m}}:${{s}}`;
      if (countdown <= 0) triggerRefresh();
    }}, 1000);
  }}

  // ── Manual / auto refresh ──────────────────────────────────────────────────
  function triggerRefresh() {{
    startTimer();
    fetchLiveCyclones();           // refresh cyclone data on every cycle
    if (abortCtrl) abortCtrl.abort();
    abortCtrl = new AbortController();
    const signal = abortCtrl.signal;

    if (activeFilter === "all") {{
      // Clear entire cache, extremes, and reload everything
      Object.keys(dataCache).forEach(k => delete dataCache[k]);
      document.querySelectorAll(".is-hottest,.is-coldest").forEach(c => c.classList.remove("is-hottest","is-coldest"));
      document.querySelectorAll(".temp-badge").forEach(b => b.remove());
      document.getElementById("pill-hot").style.display  = "none";
      document.getElementById("pill-cold").style.display = "none";
      loadAllStates(signal, true);
    }} else {{
      // Clear only current state's cache and reload it
      const state = STATES.find(s => s.id === activeFilter);
      if (state) {{
        state.cities.forEach(c => delete dataCache[c]);
        setGlobalStatus(true);
        loadState(state, signal, true).then(() => {{
          if (!signal.aborted) setGlobalStatus(false);
        }});
      }}
    }}
  }}

  // ── Boot ───────────────────────────────────────────────────────────────────
  buildLayout();
  startTimer();
  abortCtrl = new AbortController();

  // On first load: render instantly from cached Python data (no API calls).
  // This avoids OWM rate-limit 429s on page open.
  // Live data is fetched when the user clicks "Refresh Now" or a state button.
  (function initialRender() {{
    if (typeof WEATHER_DATA === "undefined" || !WEATHER_DATA) {{
      loadAllStates(abortCtrl.signal, false); // no cache available, fetch live
      return;
    }}
    const genTime = WEATHER_DATA.generated_at || "";
    let loaded = 0, total = 0;
    (WEATHER_DATA.states || []).forEach(s => {{
      const stateObj = STATES.find(st => st.name === s.state ||
        st.id === s.state.toLowerCase().replace(/ /g,"_").replace(/[^a-z0-9_]/g,""));
      if (!stateObj) return;
      const grid = document.getElementById(`grid-${{stateObj.id}}`);
      if (!grid) return;
      const cards = grid.querySelectorAll(".city-card");
      (s.districts || []).forEach((d, idx) => {{
        if (!d || d.error) return;
        total++;
        const card = cards[stateObj.cities.indexOf(d.city)];
        if (!card) return;
        const mapped = {{
          city: d.city, region: d.region || d.city,
          resolvedLabel: (d.region || d.city) + ", India",
          wrongLocation: false,
          temp: d.temperature_c || "N/A",
          feelsLike: d.feels_like_c || "N/A",
          humidity: d.humidity || "N/A",
          desc: d.description || "N/A",
          wind: d.wind_kmph || "0",
          windDir: d.wind_dir || "N",
          vis: d.visibility_km || "N/A",
          pressure: d.pressure_mb || "N/A",
          uv: "N/A", cloud: d.cloud_cover || "0",
          obsTime: d.observation_time || genTime || "\u2014",
          forecast: (d.forecast || []).map(f => ({{
            date: f.date,
            maxC: parseInt(f.max_c) || 0, minC: parseInt(f.min_c) || 0,
            desc: f.description || "Unknown",
            rainPct: f.rain_pct || "0", hourly: []
          }}))
        }};
        dataCache[d.city] = mapped;
        renderCard(card, mapped);
        loaded++;
      }});
      updateStateStatus(stateObj.id);
      updateStateExtremes(stateObj.id);
    }});
    updateGlobalExtremes();
    setGlobalStatus(false);
    if (loaded > 0) {{
      // Pill stays hidden — it will appear with a live timestamp after the first fetch.
      // If data is stale (>15 min), kick off a live refresh immediately.
      const cacheAgeMs = genTime ? Date.now() - new Date(genTime).getTime() : Infinity;
      if (cacheAgeMs > 15 * 60 * 1000) {{
        startTimer(); // reset the countdown
        loadAllStates(abortCtrl.signal, true);
      }}
    }}
    if (loaded === 0) {{
      setGlobalStatus(false);
      document.getElementById("live-label").textContent = "Select a state";
      // Prepend message WITHOUT replacing the section DOM buildLayout() created,
      // so clicking a state button still finds its #section-{{id}} element.
      const cont = document.getElementById("state-container");
      if (cont) {{
        const msg = document.createElement("div");
        msg.id = "empty-msg";
        msg.style.cssText = "max-width:560px;margin:3rem auto;text-align:center;padding:1.75rem 1.5rem;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.25);border-radius:1rem";
        msg.innerHTML = `<div style="font-size:1.9rem;margin-bottom:.6rem">&#127868;</div>
          <div style="font-size:1rem;font-weight:700;color:#c7d2fe;margin-bottom:.5rem">No cached data</div>
          <div style="font-size:.82rem;color:#94a3b8;line-height:1.65">
            Click any <b style="color:#c7d2fe">state button above</b> to load live weather,
            or run the orchestrator to refresh all districts:<br>
            <code style="display:inline-block;margin-top:.5rem;background:rgba(255,255,255,.07);
              padding:.25rem .7rem;border-radius:.35rem;font-size:.78rem;color:#a5b4fc">
              .venv\\Scripts\\python -m india_weather.orchestrator</code>
          </div>`;
        cont.prepend(msg);
        cont.querySelectorAll(".state-section").forEach(s => s.style.display="none");
      }}
    }}
  }})();

  // ── PWA: Service Worker + Install prompt + Notifications ─────────────────
  (function initPWA() {{
    // Register service worker
    if ("serviceWorker" in navigator) {{
      navigator.serviceWorker.register("/sw.js", {{ scope: "/" }})
        .then(reg => {{
          console.log("[SW] Registered, scope:", reg.scope);
          // Check for updates every 10 minutes
          setInterval(() => reg.update(), 10 * 60 * 1000);
        }})
        .catch(err => console.warn("[SW] Registration failed:", err));
    }}

    // Install prompt ("Add to Home Screen")
    let _deferredInstall = null;
    window.addEventListener("beforeinstallprompt", e => {{
      e.preventDefault();
      _deferredInstall = e;
      const btn = document.getElementById("pwa-install-btn");
      if (btn) btn.style.display = "inline-flex";
    }});
    window.addEventListener("appinstalled", () => {{
      const btn = document.getElementById("pwa-install-btn");
      if (btn) btn.style.display = "none";
      _deferredInstall = null;
    }});
    window._installPWA = function() {{
      if (!_deferredInstall) return;
      _deferredInstall.prompt();
      _deferredInstall.userChoice.then(() => {{ _deferredInstall = null; }});
    }};

    // Push notification permission button
    window._requestNotifications = async function() {{
      if (!("Notification" in window)) return alert("Notifications not supported");
      const perm = await Notification.requestPermission();
      const btn = document.getElementById("pwa-notif-btn");
      if (perm === "granted") {{
        if (btn) btn.textContent = "\u2714 Alerts ON";
        if (btn) btn.style.opacity = ".6";
      }} else {{
        if (btn) btn.textContent = "\u26d4 Blocked";
      }}
    }};

    // Show notification button state on load
    window.addEventListener("load", () => {{
      const btn = document.getElementById("pwa-notif-btn");
      if (!btn) return;
      if (Notification.permission === "granted") {{
        btn.textContent = "\u2714 Alerts ON"; btn.style.opacity = ".6";
      }} else if (Notification.permission === "denied") {{
        btn.textContent = "\u26d4 Blocked"; btn.style.opacity = ".5";
      }}
    }});
  }})();
</script>
</body>
</html>
"""


def _build_slim_weather() -> str:
    """Slim cached weather JSON for instant page render."""
    import json as _j
    wp = OUTPUT_FILE.parent / "india_weather_data.json"
    if not wp.exists():
        return "const WEATHER_DATA = null;"
    raw  = _j.loads(wp.read_text(encoding="utf-8"))
    slim = {"generated_at": raw.get("generated_at", ""), "states": []}
    for state in raw.get("states", []):
        districts = [
            {
                "city": d.get("city"), "region": d.get("region"),
                "temperature_c": d.get("temperature_c"),
                "feels_like_c":  d.get("feels_like_c"),
                "humidity":      d.get("humidity"),
                "description":   d.get("description"),
                "wind_kmph":     d.get("wind_kmph"),
                "wind_dir":      d.get("wind_dir"),
                "visibility_km": d.get("visibility_km"),
                "pressure_mb":   d.get("pressure_mb"),
                "cloud_cover":   d.get("cloud_cover"),
                "observation_time": d.get("observation_time"),
                "forecast": [
                    {"date": f.get("date"), "max_c": f.get("max_c"),
                     "min_c": f.get("min_c"), "description": f.get("description"),
                     "rain_pct": f.get("rain_pct", "0")}
                    for f in d.get("forecast", [])
                ],
            }
            for d in state.get("districts", []) if "error" not in d
        ]
        if districts:
            slim["states"].append({"state": state.get("state"), "districts": districts})
    return f"const WEATHER_DATA = {_j.dumps(slim, ensure_ascii=False)};"


def generate() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    states_js = _build_states_js()
    weather_js = _build_slim_weather() + "\n"
    alerts_path = OUTPUT_FILE.parent / "india_alerts.json"
    if alerts_path.exists():
        alerts_data = alerts_path.read_text(encoding="utf-8")
    else:
        alerts_data = '{"cyclones":[],"district_alerts":[],"generated_at":""}'
    alerts_js = f"const ALERTS_DATA = {alerts_data};\n"
    html = HTML_TEMPLATE.format(STATES_JS=states_js + "\n  " + weather_js + "\n  " + alerts_js)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Report saved \u2192 {OUTPUT_FILE}")


if __name__ == "__main__":
    generate()
