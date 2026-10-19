"""
Stock Market — History Agent
================================
Archives a compact daily snapshot (symbol -> closing price) so the
dashboard can show a trend sparkline per index/stock. Same lightweight
pattern as air_quality/history_agent.py — just numbers, one point/day.

Storage layout
--------------
    stock_market/market/history/
        2026-07-29.json   ← {"date_key": "...", "prices": {"^NSEI": 23146.15, ...}}
        2026-07-28.json
        …

Public API
----------
    archive_today(payload)          → saves today's symbol->price map
    load_all_trends(symbols, days)  → {symbol: [(date_key, price), ...]}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

BASE_DIR    = Path(__file__).parent
MARKET_DIR  = BASE_DIR / "market"
HISTORY_DIR = MARKET_DIR / "history"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)

MAX_DAYS_KEPT = 30


def _today_key() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


def archive_today(payload: dict) -> str:
    """Save today's symbol->price snapshot (indices + stocks) and prune old ones."""
    date_key = _today_key()
    prices: dict[str, float] = {}
    for idx in payload.get("indices", []):
        q = idx.get("quote", {})
        if "error" not in q and q.get("price") is not None:
            prices[idx["symbol"]] = q["price"]
    for s in payload.get("stocks", []):
        q = s.get("quote", {})
        if "error" not in q and q.get("price") is not None:
            prices[s["symbol"]] = q["price"]

    snapshot = {
        "date_key": date_key,
        "archived_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "prices": prices,
    }
    (HISTORY_DIR / f"{date_key}.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    all_dates = sorted(p.stem for p in HISTORY_DIR.glob("*.json"))
    for stale in all_dates[:-MAX_DAYS_KEPT]:
        (HISTORY_DIR / f"{stale}.json").unlink(missing_ok=True)

    return date_key


def list_dates() -> list[str]:
    return sorted((p.stem for p in HISTORY_DIR.glob("*.json")), reverse=True)


def load_all_trends(symbols: list[str], days: int = 14) -> dict[str, list[tuple[str, float]]]:
    """Load trends for multiple symbols at once (reads each history file only once)."""
    dates = sorted(list_dates())[-days:]
    trends: dict[str, list[tuple[str, float]]] = {sym: [] for sym in symbols}
    for date_key in dates:
        try:
            data = json.loads((HISTORY_DIR / f"{date_key}.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        prices = data.get("prices", {})
        for sym in symbols:
            price = prices.get(sym)
            if price is not None:
                trends[sym].append((date_key, price))
    return trends
