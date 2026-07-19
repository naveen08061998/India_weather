"""
Update all 28 state agent files with complete, official district lists
sourced from igod.gov.in (scraped + supplemented from official knowledge).
"""
import re
from pathlib import Path

BASE = Path(__file__).parent

# Complete official district lists for all 28 states
ALL_DISTRICTS = {
    "Andhra Pradesh": [
        "Alluri Sitharama Raju", "Anakapalli", "Ananthapuramu", "Annamayya",
        "Bapatla", "Chittoor", "Dr. B.R. Ambedkar Konaseema", "East Godavari",
        "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Nandyal", "NTR",
        "Palnadu", "Parvathipuram Manyam", "Prakasam",
        "Sri Potti Sriramulu Nellore", "Sri Sathya Sai", "Srikakulam",
        "Tirupati", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR",
    ],
    "Arunachal Pradesh": [
        "Anjaw", "Bichom", "Changlang", "Dibang Valley", "East Kameng",
        "East Siang", "Itanagar Capital Complex", "Kamle", "Kra Daadi",
        "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley",
        "Lower Siang", "Lower Subansiri", "Namsai", "Pakke-Kessang",
        "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang",
        "Upper Subansiri", "West Kameng", "West Siang",
    ],
    "Assam": [
        "Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar",
        "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh",
        "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat",
        "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Kokrajhar",
        "Lakhimpur", "Majuli", "Marigaon", "Morigaon", "Nagaon", "Nalbari",
        "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tamulpur",
        "Tinsukia", "Udalguri", "West Karbi Anglong",
    ],
    "Bihar": [
        "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur",
        "Bhojpur", "Buxar", "Darbhanga", "Gaya", "Gopalganj", "Jamui",
        "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj",
        "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur",
        "Nalanda", "Nawada", "Pashchim Champaran", "Patna", "Purbi Champaran",
        "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura",
        "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali",
    ],
    "Chhattisgarh": [
        "Balod", "Balodabazar-Bhatapara", "Balrampur-Ramanujganj", "Bastar",
        "Bemetara", "Bijapur", "Bilaspur", "Dakshin Bastar Dantewada",
        "Dhamtari", "Durg", "Gariyaband", "Gaurela-Pendra-Marwahi",
        "Janjgir-Champa", "Jashpur", "Kabirdham",
        "Khairagarh-Chhindgarh-Gandai", "Kondagaon", "Korba", "Korea",
        "Mahasamund", "Manendragarh-Chirmiri-Bharatpur",
        "Mohla-Manpur-Ambagarh Chouki", "Mungeli", "Narayanpur", "Raigarh",
        "Raipur", "Rajnandgaon", "Sakti", "Sarangarh-Bilaigarh", "Sukma",
        "Surajpur", "Surguja",
    ],
    "Goa": [
        "North Goa", "South Goa",
    ],
    "Gujarat": [
        "Ahmedabad", "Amreli", "Anand", "Arvalli", "Banas Kantha", "Bharuch",
        "Bhavnagar", "Botad", "Chhotaudepur", "Dahod", "Dangs",
        "Devbhumi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar",
        "Junagadh", "Kachchh", "Kheda", "Mahesana", "Mahisagar", "Morbi",
        "Narmada", "Navsari", "Panch Mahals", "Patan", "Porbandar", "Rajkot",
        "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad",
    ],
    "Haryana": [
        "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad",
        "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal",
        "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat",
        "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar",
    ],
    "Himachal Pradesh": [
        "Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu",
        "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una",
    ],
    "Jharkhand": [
        "Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum",
        "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara",
        "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu",
        "Ramgarh", "Ranchi", "Sahebganj", "Saraikela Kharsawan", "Simdega",
        "West Singhbhum",
    ],
    "Karnataka": [
        "Bagalkote", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
        "Bidar", "Chamarajanagara", "Chikkaballapura", "Chikkamagaluru",
        "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag",
        "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal",
        "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru",
        "Udupi", "Uttara Kannada", "Vijayapura", "Vijayanagara", "Yadgir",
    ],
    "Kerala": [
        "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam",
        "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta",
        "Thiruvananthapuram", "Thrissur", "Wayanad",
    ],
    "Madhya Pradesh": [
        "Agar-Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat",
        "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur",
        "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna",
        "Gwalior", "Harda", "Indore", "Jabalpur", "Jhabua", "Katni",
        "Khandwa", "Khargone", "Maihar", "Mandla", "Mandsaur", "Mauganj",
        "Morena", "Nagda", "Narsinghpur", "Niwari", "Panna", "Pandhurna",
        "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore",
        "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi",
        "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha",
        "Chachaura",
    ],
    "Maharashtra": [
        "Ahilyanagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana",
        "Chandrapur", "Chhatrapati Sambhajinagar", "Dharashiv", "Dhule",
        "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
        "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar",
        "Nashik", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri",
        "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha",
        "Washim", "Yavatmal",
    ],
    "Manipur": [
        "Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West",
        "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl",
        "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul",
    ],
    "Meghalaya": [
        "East Garo Hills", "East Jaintia Hills", "East Khasi Hills",
        "Eastern West Khasi Hills", "North Garo Hills", "Ri Bhoi",
        "South Garo Hills", "South West Garo Hills", "South West Khasi Hills",
        "West Garo Hills", "West Jaintia Hills", "West Khasi Hills",
    ],
    "Mizoram": [
        "Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai",
        "Lunglei", "Mamit", "Saitual", "Serchhip", "Siaha",
    ],
    "Nagaland": [
        "Chumoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng",
        "Mokokchung", "Mon", "Niuland", "Noklak", "Peren", "Phek",
        "Shamator", "Tseminyu", "Tuensang", "Wokha", "Zunheboto",
    ],
    "Odisha": [
        "Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh",
        "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur",
        "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara",
        "Kendujhar", "Khordha", "Koraput", "Cuttack", "Malkangiri",
        "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri",
        "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh",
    ],
    "Punjab": [
        "Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib",
        "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar",
        "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga", "Pathankot",
        "Patiala", "Rupnagar", "S.A.S. Nagar", "Sangrur",
        "Shahid Bhagat Singh Nagar", "Sri Muktsar Sahib", "Tarn Taran",
    ],
    "Rajasthan": [
        "Ajmer", "Alwar", "Anupgarh", "Balotra", "Banswara", "Baran",
        "Barmer", "Beawar", "Bharatpur", "Bhilwara", "Bikaner", "Bundi",
        "Chittorgarh", "Churu", "Dausa", "Deeg", "Dholpur",
        "Didwana-Kuchaman", "Dudu", "Dungarpur", "Gangapur City",
        "Hanumangarh", "Jaipur", "Jaipur Rural", "Jaisalmer", "Jalore",
        "Jhalawar", "Jhunjhunu", "Jodhpur", "Jodhpur Rural", "Karauli",
        "Kekri", "Khairthal-Tijara", "Kota", "Kotputli-Behror", "Nagaur",
        "Neem Ka Thana", "Pali", "Phalodi", "Pratapgarh", "Rajsamand",
        "Salumbar", "Sanchore", "Sawai Madhopur", "Shahpura", "Sikar",
        "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur",
    ],
    "Sikkim": [
        "East Sikkim", "North Sikkim", "Pakyong", "Soreng",
        "South Sikkim", "West Sikkim",
    ],
    "Tamil Nadu": [
        "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
        "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
        "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
        "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
        "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
        "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
        "Tirupattur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
        "Vellore", "Viluppuram", "Virudhunagar",
    ],
    "Telangana": [
        "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad",
        "Jagitial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal",
        "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem Asifabad",
        "Mahabubabad", "Mahbubnagar", "Mancherial", "Medak",
        "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda",
        "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla",
        "Ranga Reddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad",
        "Wanaparthy", "Warangal Rural", "Yadadri Bhuvanagiri",
    ],
    "Tripura": [
        "Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala",
        "South Tripura", "Unakoti", "West Tripura",
    ],
    "Uttar Pradesh": [
        "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya",
        "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur",
        "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor",
        "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah",
        "Etawah", "Farrukhabad", "Fatehpur", "Firozabad",
        "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur",
        "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur",
        "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj",
        "Kaushambi", "Lakhimpur Kheri", "Kushinagar", "Lalitpur", "Lucknow",
        "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut",
        "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh",
        "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal",
        "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti",
        "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao",
        "Varanasi",
    ],
    "Uttarakhand": [
        "Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar",
        "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag",
        "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi",
    ],
    "West Bengal": [
        "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur",
        "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram",
        "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia",
        "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur",
        "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas",
        "Uttar Dinajpur",
    ],
}

FILE_MAP = {
    "Andhra Pradesh":    "agent_andhra_pradesh.py",
    "Arunachal Pradesh": "agent_arunachal_pradesh.py",
    "Assam":             "agent_assam.py",
    "Bihar":             "agent_bihar.py",
    "Chhattisgarh":      "agent_chhattisgarh.py",
    "Goa":               "agent_goa.py",
    "Gujarat":           "agent_gujarat.py",
    "Haryana":           "agent_haryana.py",
    "Himachal Pradesh":  "agent_himachal_pradesh.py",
    "Jharkhand":         "agent_jharkhand.py",
    "Karnataka":         "agent_karnataka.py",
    "Kerala":            "agent_kerala.py",
    "Madhya Pradesh":    "agent_madhya_pradesh.py",
    "Maharashtra":       "agent_maharashtra.py",
    "Manipur":           "agent_manipur.py",
    "Meghalaya":         "agent_meghalaya.py",
    "Mizoram":           "agent_mizoram.py",
    "Nagaland":          "agent_nagaland.py",
    "Odisha":            "agent_odisha.py",
    "Punjab":            "agent_punjab.py",
    "Rajasthan":         "agent_rajasthan.py",
    "Sikkim":            "agent_sikkim.py",
    "Tamil Nadu":        "agent_tamil_nadu.py",
    "Telangana":         "agent_telangana.py",
    "Tripura":           "agent_tripura.py",
    "Uttar Pradesh":     "agent_uttar_pradesh.py",
    "Uttarakhand":       "agent_uttarakhand.py",
    "West Bengal":       "agent_west_bengal.py",
}

TEMPLATE = '''"""
Agent {num:02d} — {state} Weather
Fetches current weather and 3-day forecast for all {count} districts of {state}
using the wttr.in JSON API (no API key required).
"""

import requests

STATE = "{state}"
DISTRICTS = [
{districts_block}]


def fetch(city: str) -> dict:
    """Return raw weather JSON for a city."""
    url = f"https://wttr.in/{{city}}?format=j1"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def get_summary(city: str) -> dict:
    """Return a simplified summary dict for a city."""
    data = fetch(city)
    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    forecast = data["weather"]
    return {{
        "city": city,
        "state": STATE,
        "region": area["region"][0]["value"],
        "country": area["country"][0]["value"],
        "temperature_c": current["temp_C"],
        "feels_like_c": current["FeelsLikeC"],
        "humidity": current["humidity"],
        "description": current["weatherDesc"][0]["value"],
        "wind_kmph": current["windspeedKmph"],
        "wind_dir": current["winddir16Point"],
        "visibility_km": current["visibility"],
        "pressure_mb": current["pressure"],
        "uv_index": current["uvIndex"],
        "cloud_cover": current["cloudcover"],
        "observation_time": current.get("localObsDateTime") or current.get("observation_time", "N/A"),
        "forecast": [
            {{
                "date": day["date"],
                "max_c": day["maxtempC"],
                "min_c": day["mintempC"],
                "description": day["hourly"][4]["weatherDesc"][0]["value"],
            }}
            for day in forecast
        ],
    }}


def get_all_summaries() -> list:
    """Fetch and return weather summaries for all districts."""
    results = []
    for city in DISTRICTS:
        try:
            results.append(get_summary(city))
        except Exception as exc:
            results.append({{"city": city, "state": STATE, "error": str(exc)}})
    return results


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_summaries(), indent=2))
'''

STATE_ORDER = list(FILE_MAP.keys())

for idx, state in enumerate(STATE_ORDER, start=1):
    districts = ALL_DISTRICTS[state]
    fname = FILE_MAP[state]
    fpath = BASE / fname

    districts_block = "".join(f'    "{d}",\n' for d in districts)

    content = TEMPLATE.format(
        num=idx,
        state=state,
        count=len(districts),
        districts_block=districts_block,
    )

    fpath.write_text(content, encoding="utf-8")
    print(f"Updated {fname}  ({len(districts)} districts)")

print("\nAll 28 agents updated!")
