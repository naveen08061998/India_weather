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

from stock_market.indices import INDICES, STOCKS
from stock_market.stock_client import fetch_many

BASE_DIR    = Path(__file__).parent
MARKET_DIR  = BASE_DIR / "market"
OUTPUT_JSON = MARKET_DIR / "stock_market_data.json"
OUTPUT_HTML = MARKET_DIR / "stock_market_report.html"

MARKET_DIR.mkdir(exist_ok=True)


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

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "indices"     : indices_out,
        "stocks"      : stocks_out,
        "elapsed_s"   : round(elapsed, 1),
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from stock_market.report import build_html
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
