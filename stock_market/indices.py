"""
Stock Market — Index & Stock Registry
========================================
Curated list of major Indian indices and large-cap stocks tracked by the
dashboard. All symbols use Yahoo Finance's free, no-key chart API ticker
format (".NS" = NSE, "^" prefix = index).
"""

from __future__ import annotations

# ── Headline indices ───────────────────────────────────────────────────────
INDICES: list[dict] = [
    {"symbol": "^NSEI",    "name": "NIFTY 50",      "exchange": "NSE"},
    {"symbol": "^BSESN",   "name": "SENSEX",         "exchange": "BSE"},
    {"symbol": "^NSEBANK", "name": "NIFTY BANK",     "exchange": "NSE"},
    {"symbol": "^CNXIT",   "name": "NIFTY IT",       "exchange": "NSE"},
]

# ── Curated large-cap stocks (used for the "Top Movers" board) ────────────
STOCKS: list[dict] = [
    {"symbol": "RELIANCE.NS",   "name": "Reliance Industries",   "sector": "Energy"},
    {"symbol": "TCS.NS",        "name": "Tata Consultancy Svcs",  "sector": "IT"},
    {"symbol": "HDFCBANK.NS",   "name": "HDFC Bank",              "sector": "Banking"},
    {"symbol": "ICICIBANK.NS",  "name": "ICICI Bank",             "sector": "Banking"},
    {"symbol": "INFY.NS",       "name": "Infosys",                "sector": "IT"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel",          "sector": "Telecom"},
    {"symbol": "ITC.NS",        "name": "ITC",                    "sector": "FMCG"},
    {"symbol": "SBIN.NS",       "name": "State Bank of India",    "sector": "Banking"},
    {"symbol": "LT.NS",         "name": "Larsen & Toubro",        "sector": "Infrastructure"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever",     "sector": "FMCG"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance",          "sector": "Finance"},
    {"symbol": "KOTAKBANK.NS",  "name": "Kotak Mahindra Bank",    "sector": "Banking"},
    {"symbol": "MARUTI.NS",     "name": "Maruti Suzuki",          "sector": "Auto"},
    {"symbol": "SUNPHARMA.NS",  "name": "Sun Pharma",             "sector": "Pharma"},
    {"symbol": "TITAN.NS",      "name": "Titan Company",          "sector": "Consumer"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints",           "sector": "Consumer"},
    {"symbol": "AXISBANK.NS",   "name": "Axis Bank",              "sector": "Banking"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement",       "sector": "Cement"},
    {"symbol": "NESTLEIND.NS",  "name": "Nestle India",           "sector": "FMCG"},
    {"symbol": "WIPRO.NS",      "name": "Wipro",                  "sector": "IT"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto",              "sector": "Auto"},
    {"symbol": "TATASTEEL.NS",  "name": "Tata Steel",             "sector": "Metals"},
    {"symbol": "POWERGRID.NS",  "name": "Power Grid Corp",        "sector": "Power"},
    {"symbol": "NTPC.NS",       "name": "NTPC",                   "sector": "Power"},
    {"symbol": "ONGC.NS",       "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "HCLTECH.NS",    "name": "HCL Technologies",       "sector": "IT"},
    {"symbol": "ADANIENT.NS",   "name": "Adani Enterprises",      "sector": "Diversified"},
    {"symbol": "JSWSTEEL.NS",   "name": "JSW Steel",              "sector": "Metals"},
    {"symbol": "COALINDIA.NS",  "name": "Coal India",             "sector": "Mining"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv",          "sector": "Finance"},
]
