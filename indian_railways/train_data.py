"""
Indian Railways — Train Registry
=================================
Static schedule data for a curated set of well-known long-distance trains
(Rajdhani, Shatabdi, Duronto, Vande Bharat, Mail/Express).

NOTE: This is public-knowledge schedule data used to power a DEMO tracker.
Times/distances are approximate (not sourced from an official live feed).
There is no free official live-GPS API for Indian Railways, so
`ir_client.py` simulates a train's current position by comparing "now"
against this schedule (see that module for the simulation logic).

Each train dict:
    number   : str  — 5-digit train number
    name     : str  — train name
    type     : str  — Rajdhani / Shatabdi / Duronto / Vande Bharat / Mail-Express
    zone     : str  — originating railway zone code
    runs_on  : list[str] — weekday abbreviations the train departs its origin
    route    : list[dict] — ordered stops:
        code : station code
        name : station name
        day  : journey day number (1 = origin day, 2 = next day, ...)
        arr  : "HH:MM" scheduled arrival (None at origin)
        dep  : "HH:MM" scheduled departure (None at terminus)
        dist : cumulative distance in km from origin
"""

from __future__ import annotations

import json
from pathlib import Path

ALL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

CURATED_TRAINS: list[dict] = [
    # ── Mumbai Rajdhani Express ─────────────────────────────────────────
    {
        "number": "12951", "name": "Mumbai Rajdhani Express", "type": "Rajdhani", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",       "day": 1, "arr": None,    "dep": "16:55", "dist": 0},
            {"code": "KOTA", "name": "Kota Jn",          "day": 1, "arr": "21:33", "dep": "21:35", "dist": 465},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 2, "arr": "04:04", "dep": "04:06", "dist": 971},
            {"code": "ST",   "name": "Surat",            "day": 2, "arr": "05:23", "dep": "05:25", "dist": 1077},
            {"code": "BCT",  "name": "Mumbai Central",   "day": 2, "arr": "08:35", "dep": None,    "dist": 1384},
        ],
    },
    {
        "number": "12952", "name": "Mumbai Rajdhani Express", "type": "Rajdhani", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "BCT",  "name": "Mumbai Central",   "day": 1, "arr": None,    "dep": "17:00", "dist": 0},
            {"code": "ST",   "name": "Surat",            "day": 1, "arr": "20:08", "dep": "20:10", "dist": 307},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "21:29", "dep": "21:31", "dist": 413},
            {"code": "KOTA", "name": "Kota Jn",          "day": 2, "arr": "04:00", "dep": "04:05", "dist": 919},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "08:35", "dep": None,    "dist": 1384},
        ],
    },
    # ── Howrah Rajdhani Express ─────────────────────────────────────────
    {
        "number": "12301", "name": "Howrah Rajdhani Express", "type": "Rajdhani", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "HWH",  "name": "Howrah Jn",        "day": 1, "arr": None,    "dep": "16:50", "dist": 0},
            {"code": "DHN",  "name": "Dhanbad Jn",       "day": 1, "arr": "19:38", "dep": "19:40", "dist": 259},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 1, "arr": "21:33", "dep": "21:35", "dist": 422},
            {"code": "DDU",  "name": "Pt. Deen Dayal Upadhyaya Jn", "day": 1, "arr": "23:33", "dep": "23:38", "dist": 587},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 2, "arr": "03:32", "dep": "03:34", "dist": 1005},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "10:00", "dep": None,    "dist": 1447},
        ],
    },
    {
        "number": "12302", "name": "Howrah Rajdhani Express", "type": "Rajdhani", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "16:55", "dist": 0},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "22:38", "dep": "22:40", "dist": 442},
            {"code": "DDU",  "name": "Pt. Deen Dayal Upadhyaya Jn", "day": 2, "arr": "02:20", "dep": "02:25", "dist": 860},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 2, "arr": "04:15", "dep": "04:17", "dist": 1025},
            {"code": "DHN",  "name": "Dhanbad Jn",       "day": 2, "arr": "06:05", "dep": "06:07", "dist": 1188},
            {"code": "HWH",  "name": "Howrah Jn",        "day": 2, "arr": "10:05", "dep": None,    "dist": 1447},
        ],
    },
    # ── Sealdah Duronto Express ─────────────────────────────────────────
    {
        "number": "12259", "name": "Sealdah Duronto Express", "type": "Duronto", "zone": "ER",
        "runs_on": ["Mon", "Wed", "Thu", "Sat"],
        "route": [
            {"code": "SDAH", "name": "Sealdah",          "day": 1, "arr": None,    "dep": "20:20", "dist": 0},
            {"code": "PNBE", "name": "Patna Jn",         "day": 1, "arr": "01:55", "dep": "02:00", "dist": 536},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "06:10", "dep": "06:12", "dist": 986},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "08:15", "dep": None,    "dist": 1525},
        ],
    },
    {
        "number": "12260", "name": "Sealdah Duronto Express", "type": "Duronto", "zone": "ER",
        "runs_on": ["Tue", "Fri", "Sun"],
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "22:05", "dist": 0},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 2, "arr": "00:05", "dep": "00:07", "dist": 439},
            {"code": "PNBE", "name": "Patna Jn",         "day": 2, "arr": "04:20", "dep": "04:25", "dist": 989},
            {"code": "SDAH", "name": "Sealdah",          "day": 2, "arr": "10:00", "dep": None,    "dist": 1525},
        ],
    },
    # ── Tamil Nadu Express ───────────────────────────────────────────────
    {
        "number": "12621", "name": "Tamil Nadu Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "22:30", "dist": 0},
            {"code": "AGC",  "name": "Agra Cantt",       "day": 1, "arr": "01:12", "dep": "01:14", "dist": 188},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 1, "arr": "08:35", "dep": "08:45", "dist": 702},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "16:35", "dep": "16:45", "dist": 1094},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "03:45", "dep": "03:50", "dist": 1671},
            {"code": "MAS",  "name": "Chennai Central",  "day": 3, "arr": "07:15", "dep": None,    "dist": 2180},
        ],
    },
    {
        "number": "12622", "name": "Tamil Nadu Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "MAS",  "name": "Chennai Central",  "day": 1, "arr": None,    "dep": "22:00", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "02:20", "dep": "02:25", "dist": 509},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "13:35", "dep": "13:45", "dist": 1086},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "21:20", "dep": "21:30", "dist": 1478},
            {"code": "AGC",  "name": "Agra Cantt",       "day": 3, "arr": "04:35", "dep": "04:37", "dist": 1992},
            {"code": "NDLS", "name": "New Delhi",        "day": 3, "arr": "06:45", "dep": None,    "dist": 2180},
        ],
    },
    # ── Andhra Pradesh Express ───────────────────────────────────────────
    {
        "number": "12723", "name": "Andhra Pradesh Express", "type": "Mail-Express", "zone": "SCR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 1, "arr": None,    "dep": "06:40", "dist": 0},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 1, "arr": "14:05", "dep": "14:15", "dist": 708},
            {"code": "NGP",  "name": "Nagpur",           "day": 1, "arr": "20:55", "dep": "21:05", "dist": 1100},
            {"code": "KZJ",  "name": "Kazipet Jn",       "day": 2, "arr": "02:50", "dep": "02:55", "dist": 1425},
            {"code": "SC",   "name": "Secunderabad Jn",  "day": 2, "arr": "05:15", "dep": "05:25", "dist": 1562},
            {"code": "HYB",  "name": "Hyderabad Deccan", "day": 2, "arr": "06:00", "dep": None,    "dist": 1571},
        ],
    },
    {
        "number": "12724", "name": "Andhra Pradesh Express", "type": "Mail-Express", "zone": "SCR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "HYB",  "name": "Hyderabad Deccan", "day": 1, "arr": None,    "dep": "19:50", "dist": 0},
            {"code": "SC",   "name": "Secunderabad Jn",  "day": 1, "arr": "20:25", "dep": "20:35", "dist": 9},
            {"code": "KZJ",  "name": "Kazipet Jn",       "day": 1, "arr": "22:55", "dep": "23:00", "dist": 146},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "04:50", "dep": "05:00", "dist": 471},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "11:35", "dep": "11:45", "dist": 863},
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 2, "arr": "19:15", "dep": None,    "dist": 1571},
        ],
    },
    # ── Trivandrum Rajdhani Express ──────────────────────────────────────
    {
        "number": "12431", "name": "Trivandrum Rajdhani Express", "type": "Rajdhani", "zone": "NR",
        "runs_on": ["Mon", "Wed", "Thu", "Sat"],
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "11:00", "dist": 0},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "22:34", "dep": "22:36", "dist": 971},
            {"code": "MAO",  "name": "Madgaon Jn",       "day": 2, "arr": "09:05", "dep": "09:10", "dist": 1550},
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 2, "arr": "20:35", "dep": "20:45", "dist": 2350},
            {"code": "TVC",  "name": "Thiruvananthapuram Central", "day": 3, "arr": "04:25", "dep": None, "dist": 2649},
        ],
    },
    {
        "number": "12432", "name": "Trivandrum Rajdhani Express", "type": "Rajdhani", "zone": "NR",
        "runs_on": ["Tue", "Fri", "Sun"],
        "route": [
            {"code": "TVC",  "name": "Thiruvananthapuram Central", "day": 1, "arr": None, "dep": "19:15", "dist": 0},
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 1, "arr": "22:40", "dep": "22:50", "dist": 299},
            {"code": "MAO",  "name": "Madgaon Jn",       "day": 2, "arr": "10:05", "dep": "10:10", "dist": 1099},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 2, "arr": "20:45", "dep": "20:47", "dist": 1678},
            {"code": "NDLS", "name": "New Delhi",        "day": 3, "arr": "08:00", "dep": None,    "dist": 2649},
        ],
    },
    # ── Kerala Express ────────────────────────────────────────────────────
    {
        "number": "12625", "name": "Kerala Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "20:40", "dist": 0},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "05:35", "dep": "05:45", "dist": 702},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "12:55", "dep": "13:05", "dist": 1094},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 3, "arr": "00:15", "dep": "00:25", "dist": 1671},
            {"code": "MAS",  "name": "Chennai Central",  "day": 3, "arr": "05:15", "dep": "05:25", "dist": 2182},
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 3, "arr": "16:15", "dep": "16:25", "dist": 2907},
            {"code": "TVC",  "name": "Thiruvananthapuram Central", "day": 4, "arr": "00:10", "dep": None, "dist": 3149},
        ],
    },
    {
        "number": "12626", "name": "Kerala Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "TVC",  "name": "Thiruvananthapuram Central", "day": 1, "arr": None, "dep": "14:00", "dist": 0},
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 1, "arr": "21:45", "dep": "21:55", "dist": 242},
            {"code": "MAS",  "name": "Chennai Central",  "day": 2, "arr": "08:30", "dep": "08:40", "dist": 967},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "13:35", "dep": "13:45", "dist": 1478},
            {"code": "NGP",  "name": "Nagpur",           "day": 3, "arr": "01:00", "dep": "01:10", "dist": 2055},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 3, "arr": "08:10", "dep": "08:20", "dist": 2447},
            {"code": "NDLS", "name": "New Delhi",        "day": 3, "arr": "17:20", "dep": None,    "dist": 3149},
        ],
    },
    # ── Grand Trunk (GT) Express ──────────────────────────────────────────
    {
        "number": "12615", "name": "Grand Trunk Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "18:15", "dist": 0},
            {"code": "JHS",  "name": "Jhansi Jn",        "day": 1, "arr": "23:35", "dep": "23:40", "dist": 403},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "05:15", "dep": "05:20", "dist": 702},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "12:45", "dep": "12:55", "dist": 1094},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "23:35", "dep": "23:45", "dist": 1671},
            {"code": "MAS",  "name": "Chennai Central",  "day": 3, "arr": "07:30", "dep": None,    "dist": 2180},
        ],
    },
    {
        "number": "12616", "name": "Grand Trunk Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "MAS",  "name": "Chennai Central",  "day": 1, "arr": None,    "dep": "19:15", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 1, "arr": "23:35", "dep": "23:45", "dist": 509},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "11:00", "dep": "11:10", "dist": 1086},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "18:45", "dep": "18:55", "dist": 1478},
            {"code": "JHS",  "name": "Jhansi Jn",        "day": 2, "arr": "23:55", "dep": "00:00", "dist": 1777},
            {"code": "NDLS", "name": "New Delhi",        "day": 3, "arr": "06:40", "dep": None,    "dist": 2180},
        ],
    },
    # ── Golden Temple Mail ────────────────────────────────────────────────
    {
        "number": "12903", "name": "Golden Temple Mail", "type": "Mail-Express", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "BCT",  "name": "Mumbai Central",   "day": 1, "arr": None,    "dep": "21:15", "dist": 0},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "02:16", "dep": "02:18", "dist": 392},
            {"code": "RTM",  "name": "Ratlam Jn",        "day": 1, "arr": "06:00", "dep": "06:05", "dist": 679},
            {"code": "KOTA", "name": "Kota Jn",          "day": 1, "arr": "10:05", "dep": "10:10", "dist": 942},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "06:15", "dep": "06:35", "dist": 1478},
            {"code": "UMB",  "name": "Ambala Cant Jn",   "day": 2, "arr": "09:35", "dep": "09:40", "dist": 1656},
            {"code": "ASR",  "name": "Amritsar Jn",      "day": 2, "arr": "14:10", "dep": None,    "dist": 1857},
        ],
    },
    {
        "number": "12904", "name": "Golden Temple Mail", "type": "Mail-Express", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "ASR",  "name": "Amritsar Jn",      "day": 1, "arr": None,    "dep": "19:15", "dist": 0},
            {"code": "UMB",  "name": "Ambala Cant Jn",   "day": 1, "arr": "23:35", "dep": "23:40", "dist": 201},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "02:45", "dep": "03:05", "dist": 379},
            {"code": "KOTA", "name": "Kota Jn",          "day": 2, "arr": "09:00", "dep": "09:05", "dist": 858},
            {"code": "RTM",  "name": "Ratlam Jn",        "day": 2, "arr": "12:35", "dep": "12:40", "dist": 1121},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 2, "arr": "16:10", "dep": "16:12", "dist": 1408},
            {"code": "BCT",  "name": "Mumbai Central",   "day": 2, "arr": "21:15", "dep": None,    "dist": 1857},
        ],
    },
    # ── Paschim Express ───────────────────────────────────────────────────
    {
        "number": "12925", "name": "Paschim Express", "type": "Mail-Express", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "BDTS", "name": "Bandra Terminus",  "day": 1, "arr": None,    "dep": "11:35", "dist": 0},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "16:52", "dep": "16:54", "dist": 397},
            {"code": "KOTA", "name": "Kota Jn",          "day": 1, "arr": "23:45", "dep": "23:50", "dist": 947},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "07:20", "dep": "07:40", "dist": 1483},
            {"code": "ASR",  "name": "Amritsar Jn",      "day": 2, "arr": "16:15", "dep": None,    "dist": 1862},
        ],
    },
    {
        "number": "12926", "name": "Paschim Express", "type": "Mail-Express", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "ASR",  "name": "Amritsar Jn",      "day": 1, "arr": None,    "dep": "07:15", "dist": 0},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "15:50", "dep": "16:10", "dist": 379},
            {"code": "KOTA", "name": "Kota Jn",          "day": 1, "arr": "22:35", "dep": "22:40", "dist": 915},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 2, "arr": "03:55", "dep": "03:57", "dist": 1465},
            {"code": "BDTS", "name": "Bandra Terminus",  "day": 2, "arr": "09:05", "dep": None,    "dist": 1862},
        ],
    },
    # ── New Delhi – Bhopal Shatabdi ───────────────────────────────────────
    {
        "number": "12001", "name": "New Delhi Bhopal Shatabdi Express", "type": "Shatabdi", "zone": "WCR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "06:00", "dist": 0},
            {"code": "AGC",  "name": "Agra Cantt",       "day": 1, "arr": "07:59", "dep": "08:01", "dist": 188},
            {"code": "GWL",  "name": "Gwalior Jn",       "day": 1, "arr": "09:07", "dep": "09:09", "dist": 306},
            {"code": "JHS",  "name": "Jhansi Jn",        "day": 1, "arr": "10:12", "dep": "10:17", "dist": 403},
            {"code": "RKMP", "name": "Rani Kamalapati",  "day": 1, "arr": "12:50", "dep": None,    "dist": 702},
        ],
    },
    {
        "number": "12002", "name": "Bhopal New Delhi Shatabdi Express", "type": "Shatabdi", "zone": "WCR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "RKMP", "name": "Rani Kamalapati",  "day": 1, "arr": None,    "dep": "14:50", "dist": 0},
            {"code": "JHS",  "name": "Jhansi Jn",        "day": 1, "arr": "17:23", "dep": "17:28", "dist": 299},
            {"code": "GWL",  "name": "Gwalior Jn",       "day": 1, "arr": "18:23", "dep": "18:25", "dist": 396},
            {"code": "AGC",  "name": "Agra Cantt",       "day": 1, "arr": "19:33", "dep": "19:35", "dist": 514},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "21:40", "dep": None,    "dist": 702},
        ],
    },
    # ── New Delhi – Kalka Shatabdi ────────────────────────────────────────
    {
        "number": "12011", "name": "New Delhi Kalka Shatabdi Express", "type": "Shatabdi", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "07:40", "dist": 0},
            {"code": "UMB",  "name": "Ambala Cant Jn",   "day": 1, "arr": "10:35", "dep": "10:38", "dist": 200},
            {"code": "CDG",  "name": "Chandigarh",       "day": 1, "arr": "11:20", "dep": "11:25", "dist": 245},
            {"code": "KLK",  "name": "Kalka",            "day": 1, "arr": "12:10", "dep": None,    "dist": 298},
        ],
    },
    {
        "number": "12012", "name": "Kalka New Delhi Shatabdi Express", "type": "Shatabdi", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "KLK",  "name": "Kalka",            "day": 1, "arr": None,    "dep": "17:40", "dist": 0},
            {"code": "CDG",  "name": "Chandigarh",       "day": 1, "arr": "18:25", "dep": "18:30", "dist": 53},
            {"code": "UMB",  "name": "Ambala Cant Jn",   "day": 1, "arr": "19:10", "dep": "19:13", "dist": 98},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "22:20", "dep": None,    "dist": 298},
        ],
    },
    # ── Dehradun Shatabdi ─────────────────────────────────────────────────
    {
        "number": "12019", "name": "New Delhi Dehradun Shatabdi Express", "type": "Shatabdi", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "06:50", "dist": 0},
            {"code": "MTC",  "name": "Meerut City",      "day": 1, "arr": "08:07", "dep": "08:09", "dist": 79},
            {"code": "HW",   "name": "Haridwar Jn",      "day": 1, "arr": "10:50", "dep": "10:55", "dist": 200},
            {"code": "DDN",  "name": "Dehradun",         "day": 1, "arr": "12:25", "dep": None,    "dist": 230},
        ],
    },
    {
        "number": "12020", "name": "Dehradun New Delhi Shatabdi Express", "type": "Shatabdi", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "DDN",  "name": "Dehradun",         "day": 1, "arr": None,    "dep": "16:50", "dist": 0},
            {"code": "HW",   "name": "Haridwar Jn",      "day": 1, "arr": "18:15", "dep": "18:20", "dist": 30},
            {"code": "MTC",  "name": "Meerut City",      "day": 1, "arr": "21:00", "dep": "21:02", "dist": 151},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "22:30", "dep": None,    "dist": 230},
        ],
    },
    # ── Chennai – Bengaluru Shatabdi ──────────────────────────────────────
    {
        "number": "12027", "name": "Chennai Bengaluru Shatabdi Express", "type": "Shatabdi", "zone": "SR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "MAS",  "name": "Chennai Central",  "day": 1, "arr": None,    "dep": "06:00", "dist": 0},
            {"code": "KPD",  "name": "Katpadi Jn",       "day": 1, "arr": "08:07", "dep": "08:09", "dist": 130},
            {"code": "JTJ",  "name": "Jolarpettai Jn",   "day": 1, "arr": "08:47", "dep": "08:49", "dist": 175},
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 1, "arr": "11:00", "dep": None,    "dist": 362},
        ],
    },
    {
        "number": "12028", "name": "Bengaluru Chennai Shatabdi Express", "type": "Shatabdi", "zone": "SR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 1, "arr": None,    "dep": "16:25", "dist": 0},
            {"code": "JTJ",  "name": "Jolarpettai Jn",   "day": 1, "arr": "18:37", "dep": "18:39", "dist": 187},
            {"code": "KPD",  "name": "Katpadi Jn",       "day": 1, "arr": "19:22", "dep": "19:24", "dist": 232},
            {"code": "MAS",  "name": "Chennai Central",  "day": 1, "arr": "21:30", "dep": None,    "dist": 362},
        ],
    },
    # ── KSR Bengaluru – Hazrat Nizamuddin Rajdhani ──────────────────────
    {
        "number": "22691", "name": "KSR Bengaluru Hazrat Nizamuddin Rajdhani Express", "type": "Rajdhani", "zone": "SWR",
        "runs_on": ["Mon", "Wed", "Fri", "Sat"],
        "route": [
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 1, "arr": None,    "dep": "20:00", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "07:15", "dep": "07:20", "dist": 608},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "16:40", "dep": "16:50", "dist": 1338},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "21:55", "dep": "22:00", "dist": 1735},
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 3, "arr": "07:00", "dep": None,    "dist": 2444},
        ],
    },
    {
        "number": "22692", "name": "Hazrat Nizamuddin KSR Bengaluru Rajdhani Express", "type": "Rajdhani", "zone": "SWR",
        "runs_on": ["Tue", "Thu", "Sun"],
        "route": [
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 1, "arr": None,    "dep": "20:35", "dist": 0},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "05:40", "dep": "05:45", "dist": 709},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "10:55", "dep": "11:05", "dist": 1106},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "20:15", "dep": "20:20", "dist": 1836},
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 3, "arr": "07:40", "dep": None,    "dist": 2444},
        ],
    },
    # ── Coromandel Express ───────────────────────────────────────────────
    {
        "number": "12841", "name": "Coromandel Express", "type": "Mail-Express", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "HWH",  "name": "Howrah Jn",        "day": 1, "arr": None,    "dep": "14:50", "dist": 0},
            {"code": "KGP",  "name": "Kharagpur Jn",     "day": 1, "arr": "16:03", "dep": "16:05", "dist": 116},
            {"code": "BBS",  "name": "Bhubaneswar",      "day": 1, "arr": "20:08", "dep": "20:18", "dist": 439},
            {"code": "VSKP", "name": "Visakhapatnam Jn", "day": 2, "arr": "01:40", "dep": "01:55", "dist": 872},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "06:35", "dep": "06:40", "dist": 1109},
            {"code": "MAS",  "name": "Chennai Central",  "day": 2, "arr": "12:30", "dep": None,    "dist": 1659},
        ],
    },
    {
        "number": "12842", "name": "Coromandel Express", "type": "Mail-Express", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "MAS",  "name": "Chennai Central",  "day": 1, "arr": None,    "dep": "08:00", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 1, "arr": "13:15", "dep": "13:20", "dist": 550},
            {"code": "VSKP", "name": "Visakhapatnam Jn", "day": 1, "arr": "18:35", "dep": "18:50", "dist": 787},
            {"code": "BBS",  "name": "Bhubaneswar",      "day": 2, "arr": "00:20", "dep": "00:30", "dist": 1220},
            {"code": "KGP",  "name": "Kharagpur Jn",     "day": 2, "arr": "04:15", "dep": "04:17", "dist": 1543},
            {"code": "HWH",  "name": "Howrah Jn",        "day": 2, "arr": "05:35", "dep": None,    "dist": 1659},
        ],
    },
    # ── Vande Bharat Express (New Delhi – Varanasi) ─────────────────────
    {
        "number": "22435", "name": "New Delhi Varanasi Vande Bharat Express", "type": "Vande Bharat", "zone": "NR",
        "runs_on": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sun"],
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "06:00", "dist": 0},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "10:30", "dep": "10:32", "dist": 440},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 1, "arr": "12:20", "dep": "12:22", "dist": 633},
            {"code": "BSB",  "name": "Varanasi Jn",      "day": 1, "arr": "14:00", "dep": None,    "dist": 759},
        ],
    },
    {
        "number": "22436", "name": "Varanasi New Delhi Vande Bharat Express", "type": "Vande Bharat", "zone": "NR",
        "runs_on": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sun"],
        "route": [
            {"code": "BSB",  "name": "Varanasi Jn",      "day": 1, "arr": None,    "dep": "15:00", "dist": 0},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 1, "arr": "16:35", "dep": "16:37", "dist": 126},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "18:25", "dep": "18:27", "dist": 319},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "22:30", "dep": None,    "dist": 759},
        ],
    },
    # ── Karnataka Sampark Kranti Express (weekly-ish, for "not running today" demo) ──
    {
        "number": "12649", "name": "KSR Bengaluru Hazrat Nizamuddin Sampark Kranti Express", "type": "Sampark Kranti", "zone": "SWR",
        "runs_on": ["Mon", "Wed", "Fri"],
        "route": [
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 1, "arr": None,    "dep": "19:10", "dist": 0},
            {"code": "GTL",  "name": "Guntakal Jn",      "day": 1, "arr": "23:45", "dep": "23:50", "dist": 305},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 2, "arr": "14:20", "dep": "14:30", "dist": 1370},
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 3, "arr": "05:55", "dep": None,    "dist": 2077},
        ],
    },
    {
        "number": "12650", "name": "Hazrat Nizamuddin KSR Bengaluru Sampark Kranti Express", "type": "Sampark Kranti", "zone": "SWR",
        "runs_on": ["Tue", "Thu", "Sun"],
        "route": [
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 1, "arr": None,    "dep": "10:15", "dist": 0},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 1, "arr": "20:35", "dep": "20:45", "dist": 707},
            {"code": "GTL",  "name": "Guntakal Jn",      "day": 2, "arr": "11:20", "dep": "11:25", "dist": 1772},
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 2, "arr": "16:30", "dep": None,    "dist": 2077},
        ],
    },
    # ── Purushottam Express ──────────────────────────────────────────────
    {
        "number": "12801", "name": "Purushottam Express", "type": "Mail-Express", "zone": "ECoR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "10:40", "dist": 0},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "15:55", "dep": "15:57", "dist": 440},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 1, "arr": "18:10", "dep": "18:15", "dist": 633},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 2, "arr": "00:05", "dep": "00:10", "dist": 1000},
            {"code": "BBS",  "name": "Bhubaneswar",      "day": 2, "arr": "14:15", "dep": "14:25", "dist": 1730},
            {"code": "PURI", "name": "Puri",             "day": 2, "arr": "16:00", "dep": None,    "dist": 1786},
        ],
    },
    {
        "number": "12802", "name": "Purushottam Express", "type": "Mail-Express", "zone": "ECoR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "PURI", "name": "Puri",             "day": 1, "arr": None,    "dep": "10:15", "dist": 0},
            {"code": "BBS",  "name": "Bhubaneswar",      "day": 1, "arr": "11:50", "dep": "12:00", "dist": 56},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 1, "arr": "22:00", "dep": "22:05", "dist": 786},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 2, "arr": "04:00", "dep": "04:05", "dist": 1153},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 2, "arr": "06:15", "dep": "06:17", "dist": 1346},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "11:40", "dep": None,    "dist": 1786},
        ],
    },
    # ── Dibrugarh Rajdhani Express (longest-running Rajdhani route) ─────
    {
        "number": "12423", "name": "Dibrugarh Rajdhani Express", "type": "Rajdhani", "zone": "NFR",
        "runs_on": ["Mon", "Thu", "Sat"],
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "11:25", "dist": 0},
            {"code": "PNBE", "name": "Patna Jn",         "day": 1, "arr": "22:55", "dep": "23:05", "dist": 998},
            {"code": "NJP",  "name": "New Jalpaiguri",   "day": 2, "arr": "06:10", "dep": "06:20", "dist": 1425},
            {"code": "GHY",  "name": "Guwahati",         "day": 2, "arr": "12:30", "dep": "12:45", "dist": 1748},
            {"code": "DBRG", "name": "Dibrugarh",        "day": 2, "arr": "20:30", "dep": None,    "dist": 2100},
        ],
    },
    {
        "number": "12424", "name": "Dibrugarh New Delhi Rajdhani Express", "type": "Rajdhani", "zone": "NFR",
        "runs_on": ["Tue", "Fri", "Sun"],
        "route": [
            {"code": "DBRG", "name": "Dibrugarh",        "day": 1, "arr": None,    "dep": "07:15", "dist": 0},
            {"code": "GHY",  "name": "Guwahati",         "day": 1, "arr": "14:55", "dep": "15:10", "dist": 352},
            {"code": "NJP",  "name": "New Jalpaiguri",   "day": 1, "arr": "21:10", "dep": "21:20", "dist": 675},
            {"code": "PNBE", "name": "Patna Jn",         "day": 2, "arr": "04:35", "dep": "04:45", "dist": 1102},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "15:35", "dep": None,    "dist": 2100},
        ],
    },
    # ── Sealdah Rajdhani Express ─────────────────────────────────────────
    {
        "number": "12313", "name": "Sealdah Rajdhani Express", "type": "Rajdhani", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "SDAH", "name": "Sealdah",          "day": 1, "arr": None,    "dep": "16:35", "dist": 0},
            {"code": "PNBE", "name": "Patna Jn",         "day": 1, "arr": "22:20", "dep": "22:25", "dist": 486},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 2, "arr": "03:45", "dep": "03:47", "dist": 936},
            {"code": "NDLS", "name": "New Delhi",        "day": 2, "arr": "09:55", "dep": None,    "dist": 1445},
        ],
    },
    {
        "number": "12314", "name": "New Delhi Sealdah Rajdhani Express", "type": "Rajdhani", "zone": "ER",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": None,    "dep": "16:25", "dist": 0},
            {"code": "CNB",  "name": "Kanpur Central",   "day": 1, "arr": "22:35", "dep": "22:37", "dist": 509},
            {"code": "PNBE", "name": "Patna Jn",         "day": 2, "arr": "03:55", "dep": "04:00", "dist": 959},
            {"code": "SDAH", "name": "Sealdah",          "day": 2, "arr": "09:45", "dep": None,    "dist": 1445},
        ],
    },
    # ── Saraighat Express (Howrah – Guwahati) ────────────────────────────
    {
        "number": "12345", "name": "Saraighat Express", "type": "Superfast", "zone": "NFR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "HWH",  "name": "Howrah Jn",        "day": 1, "arr": None,    "dep": "15:50", "dist": 0},
            {"code": "NJP",  "name": "New Jalpaiguri",   "day": 2, "arr": "01:35", "dep": "01:45", "dist": 578},
            {"code": "GHY",  "name": "Guwahati",         "day": 2, "arr": "09:35", "dep": None,    "dist": 998},
        ],
    },
    {
        "number": "12346", "name": "Saraighat Express", "type": "Superfast", "zone": "NFR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "GHY",  "name": "Guwahati",         "day": 1, "arr": None,    "dep": "18:00", "dist": 0},
            {"code": "NJP",  "name": "New Jalpaiguri",   "day": 1, "arr": "01:55", "dep": "02:05", "dist": 420},
            {"code": "HWH",  "name": "Howrah Jn",        "day": 2, "arr": "11:40", "dep": None,    "dist": 998},
        ],
    },
    # ── Mangala Lakshadweep Express ──────────────────────────────────────
    {
        "number": "12617", "name": "Mangala Lakshadweep Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 1, "arr": None,    "dep": "11:15", "dist": 0},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 1, "arr": "19:40", "dep": "19:50", "dist": 708},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "02:20", "dep": "02:30", "dist": 1100},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "13:15", "dep": "13:20", "dist": 1677},
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 3, "arr": "08:15", "dep": None,    "dist": 2565},
        ],
    },
    {
        "number": "12618", "name": "Lakshadweep Mangala Express", "type": "Mail-Express", "zone": "NR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "ERS",  "name": "Ernakulam Jn",     "day": 1, "arr": None,    "dep": "17:30", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "12:35", "dep": "12:40", "dist": 888},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "23:30", "dep": "23:40", "dist": 1465},
            {"code": "BPL",  "name": "Bhopal Jn",        "day": 3, "arr": "06:10", "dep": "06:20", "dist": 1857},
            {"code": "NZM",  "name": "Hazrat Nizamuddin","day": 3, "arr": "14:50", "dep": None,    "dist": 2565},
        ],
    },
    # ── Andaman Express (Chennai – Jammu Tawi) ───────────────────────────
    {
        "number": "16031", "name": "Andaman Express", "type": "Mail-Express", "zone": "SR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "MS",   "name": "Chennai Egmore",    "day": 1, "arr": None,    "dep": "18:50", "dist": 0},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "01:35", "dep": "01:45", "dist": 434},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "13:15", "dep": "13:25", "dist": 1011},
            {"code": "NDLS", "name": "New Delhi",        "day": 3, "arr": "07:15", "dep": "07:30", "dist": 2005},
            {"code": "JAT",  "name": "Jammu Tawi",       "day": 3, "arr": "18:10", "dep": None,    "dist": 2429},
        ],
    },
    {
        "number": "16032", "name": "Andaman Express", "type": "Mail-Express", "zone": "SR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "JAT",  "name": "Jammu Tawi",       "day": 1, "arr": None,    "dep": "08:40", "dist": 0},
            {"code": "NDLS", "name": "New Delhi",        "day": 1, "arr": "19:40", "dep": "19:55", "dist": 424},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "13:00", "dep": "13:10", "dist": 1418},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 3, "arr": "01:05", "dep": "01:15", "dist": 1995},
            {"code": "MS",   "name": "Chennai Egmore",    "day": 3, "arr": "08:15", "dep": None,    "dist": 2429},
        ],
    },
    # ── Tejas Express (Mumbai CSMT – Madgaon) ────────────────────────────
    {
        "number": "22119", "name": "Mumbai Madgaon Tejas Express", "type": "Tejas", "zone": "CR",
        "runs_on": ["Mon", "Wed", "Thu", "Sat", "Sun"],
        "route": [
            {"code": "CSTM", "name": "Mumbai CSMT",       "day": 1, "arr": None,    "dep": "05:50", "dist": 0},
            {"code": "PNVL", "name": "Panvel",           "day": 1, "arr": "06:38", "dep": "06:40", "dist": 50},
            {"code": "RN",   "name": "Ratnagiri",        "day": 1, "arr": "10:03", "dep": "10:05", "dist": 340},
            {"code": "MAO",  "name": "Madgaon Jn",       "day": 1, "arr": "13:10", "dep": None,    "dist": 552},
        ],
    },
    {
        "number": "22120", "name": "Madgaon Mumbai Tejas Express", "type": "Tejas", "zone": "CR",
        "runs_on": ["Mon", "Wed", "Thu", "Sat", "Sun"],
        "route": [
            {"code": "MAO",  "name": "Madgaon Jn",       "day": 1, "arr": None,    "dep": "14:20", "dist": 0},
            {"code": "RN",   "name": "Ratnagiri",        "day": 1, "arr": "17:22", "dep": "17:24", "dist": 212},
            {"code": "PNVL", "name": "Panvel",           "day": 1, "arr": "20:35", "dep": "20:37", "dist": 502},
            {"code": "CSTM", "name": "Mumbai CSMT",       "day": 1, "arr": "21:25", "dep": None,    "dist": 552},
        ],
    },
    # ── Ahmedabad Shatabdi Express ────────────────────────────────────────
    {
        "number": "12009", "name": "Mumbai Ahmedabad Shatabdi Express", "type": "Shatabdi", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "BCT",  "name": "Mumbai Central",   "day": 1, "arr": None,    "dep": "06:25", "dist": 0},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "09:38", "dep": "09:40", "dist": 392},
            {"code": "ADI",  "name": "Ahmedabad Jn",     "day": 1, "arr": "11:35", "dep": None,    "dist": 493},
        ],
    },
    {
        "number": "12010", "name": "Ahmedabad Mumbai Shatabdi Express", "type": "Shatabdi", "zone": "WR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "ADI",  "name": "Ahmedabad Jn",     "day": 1, "arr": None,    "dep": "17:05", "dist": 0},
            {"code": "BRC",  "name": "Vadodara Jn",      "day": 1, "arr": "18:52", "dep": "18:54", "dist": 101},
            {"code": "BCT",  "name": "Mumbai Central",   "day": 1, "arr": "22:30", "dep": None,    "dist": 493},
        ],
    },
    # ── Sanghamitra Express (Bengaluru – Patna) ──────────────────────────
    {
        "number": "12295", "name": "Sanghamitra Express", "type": "Superfast", "zone": "SWR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 1, "arr": None,    "dep": "06:00", "dist": 0},
            {"code": "GTL",  "name": "Guntakal Jn",      "day": 1, "arr": "11:40", "dep": "11:45", "dist": 305},
            {"code": "SC",   "name": "Secunderabad Jn",  "day": 1, "arr": "16:30", "dep": "16:40", "dist": 693},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "02:15", "dep": "02:25", "dist": 1075},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 2, "arr": "14:35", "dep": "14:45", "dist": 1622},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 2, "arr": "19:55", "dep": "20:00", "dist": 1875},
            {"code": "PNBE", "name": "Patna Jn",         "day": 2, "arr": "22:45", "dep": None,    "dist": 1996},
        ],
    },
    {
        "number": "12296", "name": "Sanghamitra Express", "type": "Superfast", "zone": "SWR",
        "runs_on": ALL_DAYS,
        "route": [
            {"code": "PNBE", "name": "Patna Jn",         "day": 1, "arr": None,    "dep": "07:15", "dist": 0},
            {"code": "GAYA", "name": "Gaya Jn",          "day": 1, "arr": "09:55", "dep": "10:00", "dist": 121},
            {"code": "PRYJ", "name": "Prayagraj Jn",     "day": 1, "arr": "15:10", "dep": "15:20", "dist": 374},
            {"code": "NGP",  "name": "Nagpur",           "day": 2, "arr": "03:30", "dep": "03:40", "dist": 921},
            {"code": "SC",   "name": "Secunderabad Jn",  "day": 2, "arr": "13:05", "dep": "13:15", "dist": 1303},
            {"code": "GTL",  "name": "Guntakal Jn",      "day": 2, "arr": "17:50", "dep": "17:55", "dist": 1691},
            {"code": "SBC",  "name": "KSR Bengaluru",    "day": 3, "arr": "00:15", "dep": None,    "dist": 1996},
        ],
    },
    # ── Vivek Express (Dibrugarh – Kanyakumari, India's longest rail route) ──
    {
        "number": "15905", "name": "Dibrugarh Kanyakumari Vivek Express", "type": "Superfast", "zone": "NFR",
        "runs_on": ["Fri"],
        "route": [
            {"code": "DBRG", "name": "Dibrugarh",        "day": 1, "arr": None,    "dep": "21:40", "dist": 0},
            {"code": "GHY",  "name": "Guwahati",         "day": 2, "arr": "09:05", "dep": "09:25", "dist": 510},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 3, "arr": "18:35", "dep": "18:45", "dist": 2450},
            {"code": "MS",   "name": "Chennai Egmore",    "day": 4, "arr": "04:15", "dep": "04:25", "dist": 2884},
            {"code": "MDU",  "name": "Madurai Jn",       "day": 4, "arr": "11:10", "dep": "11:20", "dist": 3312},
            {"code": "CAPE", "name": "Kanyakumari",      "day": 4, "arr": "15:30", "dep": None,    "dist": 3532},
        ],
    },
    {
        "number": "15906", "name": "Kanyakumari Dibrugarh Vivek Express", "type": "Superfast", "zone": "NFR",
        "runs_on": ["Sun"],
        "route": [
            {"code": "CAPE", "name": "Kanyakumari",      "day": 1, "arr": None,    "dep": "11:00", "dist": 0},
            {"code": "MDU",  "name": "Madurai Jn",       "day": 1, "arr": "15:10", "dep": "15:20", "dist": 220},
            {"code": "MS",   "name": "Chennai Egmore",    "day": 1, "arr": "22:10", "dep": "22:20", "dist": 648},
            {"code": "BZA",  "name": "Vijayawada Jn",    "day": 2, "arr": "07:35", "dep": "07:45", "dist": 1082},
            {"code": "GHY",  "name": "Guwahati",         "day": 4, "arr": "01:15", "dep": "01:35", "dist": 3022},
            {"code": "DBRG", "name": "Dibrugarh",        "day": 4, "arr": "13:00", "dep": None,    "dist": 3532},
        ],
    },
]

# ── Imported open dataset (optional) ─────────────────────────────────────────
# indian_railways/tools/build_dataset.py converts the DataMeet Indian Railways
# open dataset (CC0, ~2016, https://github.com/datameet/railways) into
# data/all_trains.json + data/all_stations.json. When present, those trains
# are merged in alongside the curated set above (curated entries win on
# number collisions, since they're hand-verified and include modern trains
# like Vande Bharat that predate the 2016 dataset). The imported dataset has
# no weekday info, so those trains default to running every day.
DATA_DIR = Path(__file__).parent / "data"


def _load_imported_trains() -> list[dict]:
    path = DATA_DIR / "all_trains.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def _load_imported_stations() -> dict:
    path = DATA_DIR / "all_stations.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


_curated_numbers = {t["number"] for t in CURATED_TRAINS}
CURATED_TRAIN_NUMBERS: frozenset[str] = frozenset(_curated_numbers)
_imported_trains = [t for t in _load_imported_trains() if t["number"] not in _curated_numbers]

TRAINS: list[dict] = CURATED_TRAINS + _imported_trains

TRAINS_BY_NUMBER: dict[str, dict] = {t["number"]: t for t in TRAINS}

# ── Station coordinates ──────────────────────────────────────────────────────
# Approximate lat/lon per station code, used to match a rider's phone GPS
# to the nearest stop on their train's route ("Trip Mode" — see ir_client.py).
_CURATED_STATION_COORDS: dict[str, tuple[float, float]] = {
    "NDLS": (28.6431, 77.2197), "KOTA": (25.1804, 75.8648), "BRC": (22.3072, 73.1812),
    "ST": (21.2049, 72.8311), "BCT": (18.9694, 72.8194), "HWH": (22.5839, 88.3425),
    "DHN": (23.7957, 86.4304), "GAYA": (24.7955, 84.9994), "DDU": (25.2822, 83.2412),
    "CNB": (26.4499, 80.3319), "SDAH": (22.5675, 88.3707), "PNBE": (25.6093, 85.1376),
    "AGC": (27.1591, 78.0092), "BPL": (23.2685, 77.4126), "NGP": (21.1533, 79.0833),
    "BZA": (16.5175, 80.6252), "MAS": (13.0827, 80.2757), "NZM": (28.5877, 77.2534),
    "KZJ": (17.9926, 79.5539), "SC": (17.4344, 78.5025), "HYB": (17.3903, 78.4622),
    "MAO": (15.2734, 73.9862), "ERS": (9.9686, 76.2864), "TVC": (8.4875, 76.9525),
    "JHS": (25.4520, 78.5690), "RTM": (23.3315, 75.0367), "UMB": (30.3641, 76.8016),
    "ASR": (31.6340, 74.8723), "BDTS": (19.0648, 72.8397), "GWL": (26.2183, 78.1828),
    "CDG": (30.7333, 76.7794), "KLK": (30.8395, 76.9354), "MTC": (28.9767, 77.7061),
    "HW": (29.9457, 78.1642), "DDN": (30.3165, 78.0322), "KPD": (12.9698, 79.1489),
    "JTJ": (12.5765, 78.5751), "SBC": (12.9767, 77.5713), "VSKP": (17.7231, 83.3013),
    "KGP": (22.3302, 87.3237), "BBS": (20.2680, 85.8360), "BSB": (25.3236, 82.9938),
    "PRYJ": (25.4484, 81.8546), "GTL": (15.1670, 77.3667), "PURI": (19.8135, 85.8312),
    "DBRG": (27.4728, 94.9120), "GHY": (26.1858, 91.7086), "NJP": (26.6839, 88.4380),
    "ADI": (23.0225, 72.5714), "JAT": (32.6926, 74.8580), "MS": (13.0732, 80.2609),
    "CAPE": (8.0790, 77.5410), "CSTM": (18.9401, 72.8352), "PNVL": (18.9894, 73.1175),
    "RN": (16.9902, 73.3120), "MDU": (9.9252, 78.1198), "RKMP": (23.2141, 77.4160),
}

# ── Metro-area aliases ───────────────────────────────────────────────────────
# Big cities have multiple stations (e.g. Bengaluru = SBC/YPR/BNC). Searching
# "Bengaluru" should match trains at ANY of that city's stations, not just
# whichever one happens to literally be named "Bengaluru".
STATION_ALIASES: dict[str, set[str]] = {
    "bengaluru": {"SBC", "YPR", "BNC", "KJM", "BNCE", "YNK", "BAND"},
    "bangalore": {"SBC", "YPR", "BNC", "KJM", "BNCE", "YNK", "BAND"},
    "mumbai": {"BCT", "CSTM", "BDTS", "LTT", "DR", "CLA", "MMCT"},
    "bombay": {"BCT", "CSTM", "BDTS", "LTT", "MMCT"},
    "delhi": {"NDLS", "NZM", "DLI", "ANVT", "DEE", "DSA", "DEC"},
    "chennai": {"MAS", "MS", "TBM", "VLCY"},
    "madras": {"MAS", "MS"},
    "hyderabad": {"HYB", "SC", "KCG", "BMT"},
    "secunderabad": {"SC"},
    "kolkata": {"HWH", "SDAH", "KOAA", "SHM"},
    "calcutta": {"HWH", "SDAH"},
}

_imported_stations = _load_imported_stations()
STATION_COORDS: dict[str, tuple[float, float]] = {
    **{code: (info["lat"], info["lon"]) for code, info in _imported_stations.items()},
    **_CURATED_STATION_COORDS,  # curated coordinates take precedence
}

# Sorted "CODE — Name" strings for search autocomplete. Leading with the code
# (rather than burying it in parentheses at the end) means typing a short code
# like "MAS" surfaces the exact station first, instead of getting buried among
# unrelated stations whose *name* happens to contain the same substring.
_station_code_to_name: dict[str, str] = {}
for _t in TRAINS:
    for _s in _t["route"]:
        _station_code_to_name.setdefault(_s["code"], _s["name"])
for _code, _info in _imported_stations.items():
    _station_code_to_name.setdefault(_code, _info["name"])

ALL_STATION_NAMES: list[str] = sorted(
    (f"{code} \u2014 {name}" for code, name in _station_code_to_name.items()),
    key=lambda s: s.split(" \u2014 ", 1)[0].lower(),
)
