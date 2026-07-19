"""Scrape all district names from igod.gov.in for all 28 Indian states."""
import requests
from bs4 import BeautifulSoup
import json, time, re

STATE_CODES = {
    "Andhra Pradesh":    "AP",
    "Arunachal Pradesh": "AR",
    "Assam":             "AS",
    "Bihar":             "BR",
    "Chhattisgarh":      "CG",
    "Goa":               "GA",
    "Gujarat":           "GJ",
    "Haryana":           "HR",
    "Himachal Pradesh":  "HP",
    "Jharkhand":         "JH",
    "Karnataka":         "KA",
    "Kerala":            "KL",
    "Madhya Pradesh":    "MP",
    "Maharashtra":       "MH",
    "Manipur":           "MN",
    "Meghalaya":         "ML",
    "Mizoram":           "MZ",
    "Nagaland":          "NL",
    "Odisha":            "OD",
    "Punjab":            "PB",
    "Rajasthan":         "RJ",
    "Sikkim":            "SK",
    "Tamil Nadu":        "TN",
    "Telangana":         "TS",
    "Tripura":           "TR",
    "Uttar Pradesh":     "UP",
    "Uttarakhand":       "UK",
    "West Bengal":       "WB",
}

SKIP_HREFS = {
    "igod.gov.in", "india.gov.in", "data.gov.in", "mygov.in",
    "guidelines.india", "s3waas", "pmindia", "pgportal",
    "digitalindia", "services.india", "nic.in/", "passportindia",
    "hgvms.hp", "ipass.telangana", "invest.telangana", "organic.apeda",
}

SKIP_TEXTS = {
    "More Sites", "Suggest A Site", "Share Feedback", "Home Guards",
    "Telangana Industrial", "Invest Telangana", "Organic Agriculture",
    "Passport Seva", "In Focus", "National Portal", "Open Government",
    "Guidelines", "Secure", "Prime Minister", "Centralised", "MyGov",
    "National Government",
}

results = {}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for state, code in STATE_CODES.items():
    url = f"https://igod.gov.in/sg/{code}/E042/organizations"
    try:
        r = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the main content area (the results block)
        districts = []
        seen = set()

        # Method 1: anchor tags pointing to district websites
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if not text or len(text) > 55 or len(text) < 2:
                continue
            if any(s in href for s in SKIP_HREFS):
                continue
            if any(t in text for t in SKIP_TEXTS):
                continue
            if "igod.gov.in" in href:
                continue
            # Must be a .gov.in or .nic.in district link
            if ".gov.in" in href or ".nic.in" in href:
                clean = text.strip()
                if clean not in seen and len(clean.split()) <= 6:
                    districts.append(clean)
                    seen.add(clean)

        # Method 2: Look for district names that have no website (plain text)
        # They appear before "SUB DISTRICTS" links; find all text nodes
        full_text = soup.get_text("\n", strip=True)
        # Grab the results block between "Results" and "HELP US"
        m = re.search(r"\d+ Results\s*(.*?)HELP US", full_text, re.DOTALL)
        if m:
            block = m.group(1)
            # Each line that is a district name (not a link label like SUB DISTRICTS/BLOCKS)
            for line in block.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line in ("SUB DISTRICTS", "BLOCKS", "More Sites"):
                    continue
                if re.match(r"^\d+ Results", line):
                    continue
                if any(t in line for t in SKIP_TEXTS):
                    continue
                if len(line) > 55 or len(line) < 2:
                    continue
                if line not in seen and len(line.split()) <= 6:
                    districts.append(line)
                    seen.add(line)

        results[state] = districts
        print(f"{state}: {len(districts)} → {districts[:5]}...", flush=True)
        time.sleep(0.4)
    except Exception as e:
        print(f"ERROR {state}: {e}", flush=True)
        results[state] = []

# Save to file
with open("india_weather/all_districts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nSaved to india_weather/all_districts.json")
