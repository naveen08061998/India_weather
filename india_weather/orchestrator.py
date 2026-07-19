"""
India Weather Orchestrator
==========================
Central controller for all 28 state weather agents.

Usage
-----
# Fetch all 28 states and regenerate HTML report
python india_weather/orchestrator.py

# Fetch specific state(s)
python india_weather/orchestrator.py --states Kerala
python india_weather/orchestrator.py --states "Tamil Nadu,Karnataka,Kerala"

# Only save JSON (skip HTML regeneration)
python india_weather/orchestrator.py --output json

# Only regenerate HTML (no live fetch, uses cached JSON)
python india_weather/orchestrator.py --output html

# Control concurrency
python india_weather/orchestrator.py --workers 10

# Verbose per-district output
python india_weather/orchestrator.py --states Goa --verbose
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
OUTPUT_JSON = BASE_DIR / "weathers" / "india_weather_data.json"
OUTPUT_HTML = BASE_DIR / "weathers" / "india_weather_report.html"

# ── Agent registry ─────────────────────────────────────────────────────────
# Auto-discovers every agent_*.py in this package
def _discover_agents() -> dict[str, Any]:
    """Return {state_name: module} for every agent_*.py found."""
    agents = {}
    for path in sorted(BASE_DIR.glob("agent_*.py")):
        mod_name = f"india_weather.{path.stem}"
        try:
            mod = importlib.import_module(mod_name)
            agents[mod.STATE] = mod
        except Exception as exc:
            print(f"[WARN] Could not load {path.name}: {exc}", file=sys.stderr)
    return agents


AGENTS: dict[str, Any] = _discover_agents()

# ── Core orchestration ─────────────────────────────────────────────────────

def fetch_state(state_name: str, verbose: bool = False) -> dict:
    """
    Fetch weather for all districts of a single state.
    Returns a result dict with keys: state, fetched_at, districts, errors.
    """
    if state_name not in AGENTS:
        raise ValueError(
            f"Unknown state '{state_name}'. "
            f"Available: {', '.join(sorted(AGENTS))}"
        )
    mod = AGENTS[state_name]
    start = time.time()
    summaries = mod.get_all_summaries()
    elapsed = round(time.time() - start, 2)

    ok     = [s for s in summaries if "error" not in s]
    errors = [s for s in summaries if "error" in s]

    if verbose:
        for s in ok:
            print(f"  ✓ {s['city']:30s} {s['temperature_c']}°C  {s['description']}")
        for s in errors:
            print(f"  ✗ {s['city']:30s} ERROR: {s['error']}", file=sys.stderr)

    return {
        "state":       state_name,
        "fetched_at":  datetime.now().isoformat(timespec="seconds"),
        "elapsed_s":   elapsed,
        "total":       len(summaries),
        "ok":          len(ok),
        "errors":      len(errors),
        "districts":   summaries,
    }


def fetch_states(
    state_names: list[str] | None = None,
    workers: int = 8,
    verbose: bool = False,
) -> list[dict]:
    """
    Fetch weather for multiple (or all) states in parallel.
    Returns a list of result dicts, one per state.
    """
    targets = state_names if state_names else list(AGENTS.keys())
    results: list[dict] = []
    total   = len(targets)
    done    = 0

    print(f"\n{'─'*60}")
    print(f"  India Weather Orchestrator — {total} state(s) | {workers} workers")
    print(f"{'─'*60}")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_state, state, verbose): state
            for state in targets
        }
        for future in as_completed(futures):
            state = futures[future]
            done += 1
            try:
                result = future.result()
                status = f"✓  {result['ok']}/{result['total']} districts  ({result['elapsed_s']}s)"
                print(f"  [{done:2d}/{total}] {state:28s}  {status}")
                results.append(result)
            except Exception as exc:
                print(f"  [{done:2d}/{total}] {state:28s}  ✗ FAILED: {exc}", file=sys.stderr)
                results.append({"state": state, "error": str(exc), "districts": []})

    # Sort back to original order
    order = {s: i for i, s in enumerate(targets)}
    results.sort(key=lambda r: order.get(r["state"], 999))
    return results


# ── Output helpers ─────────────────────────────────────────────────────────

def save_json(results: list[dict]) -> Path:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_states":  len(results),
        "total_districts": sum(r.get("total", 0) for r in results),
        "total_ok":       sum(r.get("ok", 0)    for r in results),
        "total_errors":   sum(r.get("errors", 0) for r in results),
        "states": results,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return OUTPUT_JSON


def regenerate_html() -> Path:
    """Import weather_report and regenerate the HTML dashboard."""
    import importlib, sys
    mod_name = "india_weather.weather_report"
    if mod_name in sys.modules:
        mod = importlib.reload(sys.modules[mod_name])
    else:
        mod = importlib.import_module(mod_name)
    mod.generate()
    return OUTPUT_HTML


# ── Summary printer ────────────────────────────────────────────────────────

def print_summary(results: list[dict]) -> None:
    total_d  = sum(r.get("total",  0) for r in results)
    total_ok = sum(r.get("ok",     0) for r in results)
    total_er = sum(r.get("errors", 0) for r in results)
    pct      = round(total_ok / total_d * 100, 1) if total_d else 0

    print(f"\n{'═'*60}")
    print(f"  Summary")
    print(f"{'─'*60}")
    print(f"  States fetched : {len(results)}")
    print(f"  Districts total: {total_d}")
    print(f"  Loaded OK      : {total_ok}  ({pct}%)")
    print(f"  Errors         : {total_er}")

    if total_er:
        print(f"\n  Failed districts:")
        for r in results:
            for d in r.get("districts", []):
                if "error" in d:
                    print(f"    {r['state']:25s}  {d['city']:30s}  {d['error']}")
    print(f"{'═'*60}\n")


# ── Convenience API (importable) ───────────────────────────────────────────

def get_state_weather(state_name: str) -> list[dict]:
    """Return a list of district weather summaries for the given state."""
    return fetch_state(state_name)["districts"]


def get_all_weather(workers: int = 8) -> dict[str, list[dict]]:
    """Return {state_name: [district_summary, ...]} for all 28 states."""
    results = fetch_states(workers=workers)
    return {r["state"]: r["districts"] for r in results}


# ── CLI ────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="orchestrator",
        description="India Weather Orchestrator — manages all 28 state agents",
    )
    p.add_argument(
        "--states",
        default=None,
        help='Comma-separated state names, e.g. "Kerala,Tamil Nadu". '
             "Omit for all 28 states.",
    )
    p.add_argument(
        "--output",
        choices=["json", "html", "both", "none"],
        default="both",
        help="Output format (default: both)",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel workers for state fetching (default: 8)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print each district's temperature as it is fetched",
    )
    p.add_argument(
        "--list-states",
        action="store_true",
        help="List all available states and exit",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    if args.list_states:
        print(f"\n{len(AGENTS)} registered agents:\n")
        for i, (state, mod) in enumerate(sorted(AGENTS.items()), 1):
            print(f"  {i:2d}. {state:28s}  ({len(mod.DISTRICTS)} districts)")
        print()
        return

    # Resolve target states
    if args.states:
        targets = [s.strip() for s in args.states.split(",")]
        for t in targets:
            if t not in AGENTS:
                print(f"[ERROR] Unknown state: '{t}'", file=sys.stderr)
                print(f"  Run with --list-states to see all options.", file=sys.stderr)
                sys.exit(1)
    else:
        targets = None   # all states

    # Fetch
    t0      = time.time()
    results = fetch_states(targets, workers=args.workers, verbose=args.verbose)
    elapsed = round(time.time() - t0, 1)

    print_summary(results)
    print(f"  Total time: {elapsed}s")

    # Save outputs
    if args.output in ("json", "both"):
        path = save_json(results)
        print(f"  JSON  → {path}")

    if args.output in ("html", "both"):
        path = regenerate_html()
        print(f"  HTML  → {path}")

    print()


if __name__ == "__main__":
    main()
