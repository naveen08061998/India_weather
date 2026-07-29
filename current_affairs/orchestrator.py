"""
Current Affairs — Orchestrator
================================
Fetches news for all 10 categories concurrently and writes:
  • current_affairs/news/current_affairs_data.json   (raw data)
  • current_affairs/news/current_affairs_report.html (dashboard)

Usage
-----
# Run from the project root
python -m current_affairs.orchestrator

# Fetch only specific categories
python -m current_affairs.orchestrator --categories national economy sports

# Skip HTML generation (JSON only)
python -m current_affairs.orchestrator --output json

# Regenerate HTML from cached JSON (no fetch)
python -m current_affairs.orchestrator --output html

# Control concurrency
python -m current_affairs.orchestrator --workers 5
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

# Ensure Unicode characters (✓, →, etc.) don't crash on Windows cp1252 terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IST = timezone(timedelta(hours=5, minutes=30))
from pathlib import Path

from current_affairs.categories import ALL_CATEGORIES, CATEGORY_MAP
from current_affairs.fetcher import fetch_category

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
NEWS_DIR    = BASE_DIR / "news"
OUTPUT_JSON = NEWS_DIR / "current_affairs_data.json"
OUTPUT_HTML = NEWS_DIR / "current_affairs_report.html"

NEWS_DIR.mkdir(exist_ok=True)


# ── Core orchestration ─────────────────────────────────────────────────────

def fetch_all(category_keys: list[str] | None = None,
              workers: int = 5,
              verbose: bool = False) -> dict:
    """
    Fetch all (or selected) categories concurrently.
    Returns the full data payload dict.
    """
    targets = (
        [CATEGORY_MAP[k] for k in category_keys if k in CATEGORY_MAP]
        if category_keys
        else ALL_CATEGORIES
    )

    print(f"\n[Current Affairs] Fetching {len(targets)} categories "
          f"with {workers} workers…")
    start = time.time()

    results: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {
            pool.submit(fetch_category, cat): cat["key"]
            for cat in targets
        }
        for future in as_completed(future_map):
            key = future_map[future]
            try:
                data = future.result()
                results[key] = data
                article_count = len(data.get("articles", []))
                status = "✓" if article_count else "⚠"
                print(f"  {status} {data['label']:<30} {article_count} articles")
                if verbose:
                    for art in data.get("articles", [])[:3]:
                        print(f"      • {art['title'][:80]}")
            except Exception as exc:
                print(f"  ✗ {key}: {exc}", file=sys.stderr)
                results[key] = {
                    "key": key, "articles": [], "error": str(exc)
                }

    elapsed = time.time() - start
    payload = {
        "generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "date"        : datetime.now(IST).strftime("%d %B %Y"),
        "categories"  : results,
        "total_articles": sum(
            len(v.get("articles", [])) for v in results.values()
        ),
        "elapsed_s"   : round(elapsed, 1),
    }

    print(f"\n  Total: {payload['total_articles']} articles "
          f"in {elapsed:.1f}s")
    return payload


def save_json(payload: dict) -> None:
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  JSON → {OUTPUT_JSON}")


def generate_html(payload: dict) -> None:
    from current_affairs.report import build_html
    html = build_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  HTML → {OUTPUT_HTML}")


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Current Affairs Orchestrator for Competitive Exams"
    )
    parser.add_argument(
        "--categories", nargs="*",
        help="Space-separated category keys to fetch (default: all)",
    )
    parser.add_argument(
        "--output", choices=["all", "json", "html"], default="all",
        help="What to produce: 'all' (default), 'json', or 'html'",
    )
    parser.add_argument(
        "--workers", type=int, default=5,
        help="Number of parallel fetch workers (default: 5)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.output == "html":
        # Re-use cached JSON; just regenerate HTML
        if not OUTPUT_JSON.exists():
            print("No cached JSON found. Run without --output html first.")
            sys.exit(1)
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        generate_html(payload)
        return

    payload = fetch_all(
        category_keys=args.categories,
        workers=args.workers,
        verbose=args.verbose,
    )

    if args.output in ("all", "json"):
        save_json(payload)

    if args.output in ("all", "html"):
        generate_html(payload)


if __name__ == "__main__":
    main()
