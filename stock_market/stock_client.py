"""
Stock Market — Yahoo Finance Chart Client
============================================
Uses Yahoo Finance's free, public "chart" JSON endpoint (no API key, no
official SLA — the same widely-used free source already relied on by many
hobby finance dashboards). One request per symbol returns the latest quote.

    https://query1.finance.yahoo.com/v8/finance/chart/<SYMBOL>
"""

from __future__ import annotations

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_HEADERS   = {"User-Agent": "Mozilla/5.0 (StockMarketDashboard/1.0)"}
_TIMEOUT   = 12


def fetch_quote(symbol: str) -> dict:
    """
    Fetch the latest quote for a single symbol.
    Returns a dict with price/change/percent or an "error" key on failure.
    """
    try:
        resp = requests.get(
            _CHART_URL.format(symbol=symbol),
            headers=_HEADERS, timeout=_TIMEOUT,
            params={"interval": "1d", "range": "1d"},
        )
        resp.raise_for_status()
        data = resp.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return {"symbol": symbol, "error": "No data returned"}
        meta = result[0]["meta"]

        price      = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose", meta.get("previousClose"))
        if price is None or prev_close is None:
            return {"symbol": symbol, "error": "Incomplete quote data"}

        change     = round(price - prev_close, 2)
        change_pct = meta.get("regularMarketChangePercent")
        if change_pct is None:
            change_pct = (change / prev_close * 100) if prev_close else 0.0
        change_pct = round(change_pct, 2)

        return {
            "symbol":      symbol,
            "price":       round(price, 2),
            "prev_close":  round(prev_close, 2),
            "change":      change,
            "change_pct":  change_pct,
            "day_high":    round(meta.get("regularMarketDayHigh", price), 2),
            "day_low":     round(meta.get("regularMarketDayLow", price), 2),
            "year_high":   meta.get("fiftyTwoWeekHigh"),
            "year_low":    meta.get("fiftyTwoWeekLow"),
            "currency":    meta.get("currency", "INR"),
            "market_time": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        }
    except Exception as exc:
        return {"symbol": symbol, "error": str(exc)}


def fetch_many(symbols: list[str], workers: int = 8) -> dict[str, dict]:
    """Fetch quotes for multiple symbols concurrently. Returns {symbol: quote}."""
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(fetch_quote, sym): sym for sym in symbols}
        for future in as_completed(future_map):
            sym = future_map[future]
            try:
                results[sym] = future.result()
            except Exception as exc:
                results[sym] = {"symbol": sym, "error": str(exc)}
    return results


def fetch_intraday(symbol: str) -> list[float]:
    """
    Fetch today's intraday 5-minute closing prices for a mini sparkline chart.
    Returns a plain list of prices (nulls dropped), oldest-first. Empty list
    on any failure — this is a "nice to have" visual, never worth retrying.
    """
    try:
        resp = requests.get(
            _CHART_URL.format(symbol=symbol),
            headers=_HEADERS, timeout=_TIMEOUT,
            params={"interval": "5m", "range": "1d"},
        )
        resp.raise_for_status()
        result = resp.json().get("chart", {}).get("result")
        if not result:
            return []
        closes = result[0]["indicators"]["quote"][0].get("close", [])
        return [round(c, 2) for c in closes if c is not None]
    except Exception:
        return []


def fetch_many_intraday(symbols: list[str], workers: int = 8) -> dict[str, list[float]]:
    """Fetch intraday series for multiple symbols concurrently."""
    results: dict[str, list[float]] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(fetch_intraday, sym): sym for sym in symbols}
        for future in as_completed(future_map):
            sym = future_map[future]
            try:
                results[sym] = future.result()
            except Exception:
                results[sym] = []
    return results
