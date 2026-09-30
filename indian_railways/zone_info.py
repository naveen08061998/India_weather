"""
Indian Railways — Zone Reference Data
=======================================
Curated, hand-written facts (no network calls) about each railway zone
present in this app's train dataset — name, headquarters, and (for the one
non-IR-zone entry, Konkan Railway) a clarifying note. Train counts per zone
are computed live from the actual dataset (see ir_client.zone_counts()),
not hardcoded here.
"""

from __future__ import annotations

DISCLAIMER = (
    "Zone headquarters are current public information; a train's zone reflects which "
    "zone administers/operates it, not necessarily where its route runs."
)

ZONE_INFO: dict[str, dict] = {
    "NR":   {"name": "Northern Railway", "headquarters": "New Delhi"},
    "SCR":  {"name": "South Central Railway", "headquarters": "Secunderabad"},
    "SR":   {"name": "Southern Railway", "headquarters": "Chennai"},
    "CR":   {"name": "Central Railway", "headquarters": "Mumbai (CSMT)"},
    "WR":   {"name": "Western Railway", "headquarters": "Mumbai (Churchgate)"},
    "ER":   {"name": "Eastern Railway", "headquarters": "Kolkata"},
    "SER":  {"name": "South Eastern Railway", "headquarters": "Kolkata (Garden Reach)"},
    "NFR":  {"name": "Northeast Frontier Railway", "headquarters": "Guwahati (Maligaon)"},
    "SWR":  {"name": "South Western Railway", "headquarters": "Hubballi"},
    "NER":  {"name": "North Eastern Railway", "headquarters": "Gorakhpur"},
    "NWR":  {"name": "North Western Railway", "headquarters": "Jaipur"},
    "ECR":  {"name": "East Central Railway", "headquarters": "Hajipur"},
    "ECoR": {"name": "East Coast Railway", "headquarters": "Bhubaneswar"},
    "NCR":  {"name": "North Central Railway", "headquarters": "Prayagraj (Allahabad)"},
    "SECR": {"name": "South East Central Railway", "headquarters": "Bilaspur"},
    "WCR":  {"name": "West Central Railway", "headquarters": "Jabalpur"},
    "KR":   {"name": "Konkan Railway", "headquarters": "Navi Mumbai",
             "note": "A separate government corporation (Konkan Railway Corporation Ltd.), "
                     "not one of Indian Railways' 17 standard zones."},
}
