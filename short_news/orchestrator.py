"""
Short News — Orchestrator
============================
Fetches all categories concurrently and writes:
  • short_news/digest/short_news_data.json
  • short_news/digest/short_news_report.html

Usage
-----
python -m short_news.orchestrator
python -m short_news.orchestrator --workers 6
python -m short_news.orchestrator --output html   # regenerate HTML from cached JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))

from short_news.categories import CATEGORIES
from short_news.fetcher import fetch_category

BASE_DIR    = Path(__file__).parent
DIGEST_DIR  = BASE_DIR / "digest"
OUTPUT_JSON = DIGEST_DIR / "short_news_data.json"
OUTPUT_HTML = DIGEST_DIR / "short_news_report.html"

DIGEST_DIR.mkdir(exist_ok=True)


def fetch_all(workers: int = 6) -> dict:
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_category, cat): cat["key"] for cat in CATEGORIES}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                print(f"  [WARN] Category failed ({key}): {exc}")

    ordered = [results[c["key"]] for c in CATEGORIES if c["key"] in results]
    total_articles = sum(len(c["articles"]) for c in ordered)
    total_seconds = sum(c["total_read_seconds"] for c in ordered)

    return {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date": datetime.now(IST).strftime("%d %B %Y"),
        "categories": ordered,
        "stats": {
            "total_articles": total_articles,
            "total_categories": len(ordered),
            "total_read_minutes": round(total_seconds / 60, 1),
        },
    }


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from short_news.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Short News Orchestrator")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", choices=["all", "json", "html"], default="all")
    args = parser.parse_args()

    if args.output == "html":
        if not OUTPUT_JSON.exists():
            payload = fetch_all(workers=args.workers)
            save_json(payload)
        else:
            payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = fetch_all(workers=args.workers)
    print(f"[Short News] {payload['stats']['total_articles']} stories across "
          f"{payload['stats']['total_categories']} categories "
          f"(~{payload['stats']['total_read_minutes']} min total read time).")

    if args.output in ("all", "json"):
        save_json(payload)
    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
