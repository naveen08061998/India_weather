"""
Stock Market — Orchestrator
=============================
Fetches headline indices + curated large-cap stocks and writes:
  • stock_market/market/stock_market_data.json
  • stock_market/market/stock_market_report.html

Usage
-----
python -m stock_market.orchestrator
python -m stock_market.orchestrator --output json
python -m stock_market.orchestrator --output html
python -m stock_market.orchestrator --workers 10
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from stock_market.indices import INDICES, STOCKS, COMMODITIES
from stock_market.stock_client import fetch_many, fetch_many_intraday
from stock_market import history_agent
from stock_market.news_client import fetch_market_news

BASE_DIR    = Path(__file__).parent
MARKET_DIR  = BASE_DIR / "market"
OUTPUT_JSON = MARKET_DIR / "stock_market_data.json"
OUTPUT_HTML = MARKET_DIR / "stock_market_report.html"

MARKET_DIR.mkdir(exist_ok=True)

# NSE regular trading session, Mon-Fri (IST) — a simple time-check, not a
# holiday calendar, so it can be wrong on market holidays.
_MARKET_OPEN  = (9, 15)
_MARKET_CLOSE = (15, 30)


def _market_status() -> dict:
    now = datetime.now(IST)
    open_t  = now.replace(hour=_MARKET_OPEN[0], minute=_MARKET_OPEN[1], second=0, microsecond=0)
    close_t = now.replace(hour=_MARKET_CLOSE[0], minute=_MARKET_CLOSE[1], second=0, microsecond=0)
    is_open = now.weekday() < 5 and open_t <= now <= close_t
    return {"is_open": is_open, "checked_at": now.strftime("%H:%M IST")}


def _sector_heatmap(stocks_out: list[dict]) -> list[dict]:
    buckets: dict[str, list[float]] = {}
    for s in stocks_out:
        q = s.get("quote", {})
        if "error" in q:
            continue
        buckets.setdefault(s["sector"], []).append(q["change_pct"])
    heatmap = [
        {"sector": sector, "avg_change_pct": round(sum(vals) / len(vals), 2), "count": len(vals)}
        for sector, vals in buckets.items()
    ]
    return sorted(heatmap, key=lambda h: h["avg_change_pct"], reverse=True)


def fetch_all(workers: int = 8, verbose: bool = False) -> dict:
    all_symbols = [i["symbol"] for i in INDICES] + [s["symbol"] for s in STOCKS]
    print(f"\n[Stock Market] Fetching {len(all_symbols)} symbols with {workers} workers…")
    start = time.time()
    quotes = fetch_many(all_symbols, workers=workers)
    elapsed = time.time() - start

    indices_out = []
    for i in INDICES:
        q = quotes.get(i["symbol"], {"error": "missing"})
        indices_out.append({**i, "quote": q})
        status = "✓" if "error" not in q else "⚠"
        print(f"  {status} {i['name']:<14} {q.get('price', q.get('error'))}")

    stocks_out = []
    ok_count = 0
    for s in STOCKS:
        q = quotes.get(s["symbol"], {"error": "missing"})
        stocks_out.append({**s, "quote": q})
        if "error" not in q:
            ok_count += 1
    if verbose:
        for s in stocks_out:
            q = s["quote"]
            if "error" not in q:
                print(f"      • {s['name']:<28} {q['price']} ({q['change_pct']:+.2f}%)")

    print(f"  {ok_count}/{len(STOCKS)} stocks OK in {elapsed:.1f}s")

    print("  Fetching commodities/currency…")
    commodity_quotes = fetch_many([c["symbol"] for c in COMMODITIES], workers=workers)
    commodities_out = [{**c, "quote": commodity_quotes.get(c["symbol"], {"error": "missing"})} for c in COMMODITIES]

    print("  Fetching index intraday charts…")
    intraday = fetch_many_intraday([i["symbol"] for i in INDICES], workers=workers)

    print("  Fetching market news…")
    try:
        news = fetch_market_news()
    except Exception as exc:
        print(f"  [WARN] Market news failed: {exc}", file=sys.stderr)
        news = []

    return {
        "generated_at" : datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"         : datetime.now(IST).strftime("%d %B %Y"),
        "indices"      : indices_out,
        "stocks"       : stocks_out,
        "commodities"  : commodities_out,
        "intraday"     : intraday,
        "market_status": _market_status(),
        "sector_heatmap": _sector_heatmap(stocks_out),
        "news"         : news,
        "elapsed_s"    : round(elapsed, 1),
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")
    date_key = history_agent.archive_today(payload)
    print(f"  History → archived as {date_key}")


def generate_html(payload: dict) -> None:
    from stock_market.report import build_html
    all_symbols = [i["symbol"] for i in payload.get("indices", [])] + [s["symbol"] for s in payload.get("stocks", [])]
    payload["trends"] = {
        sym: [[d, v] for d, v in points]
        for sym, points in history_agent.load_all_trends(all_symbols, days=14).items()
    }
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Indian Stock Market Orchestrator")
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            print("No cached JSON found. Run without --output html first.")
            sys.exit(1)
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = fetch_all(workers=args.workers, verbose=args.verbose)

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
