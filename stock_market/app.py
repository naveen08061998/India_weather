"""
Stock Market PWA — Standalone Flask Server
=============================================
Serves the Indian Stock Market dashboard. Independent of the other agents.

Run:
    python stock_market/app.py
    python stock_market/app.py --port 5002 --refresh 15

Endpoints:
    GET  /                → HTML dashboard
    GET  /api/market       → Full market JSON (indices + stocks)
    POST /api/refresh      → Manually trigger a refresh
    GET  /api/status       → Scheduler & refresh status
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, Response

BASE_DIR    = Path(__file__).parent
MARKET_DIR  = BASE_DIR / "market"
MARKET_JSON = MARKET_DIR / "stock_market_data.json"
MARKET_HTML = MARKET_DIR / "stock_market_report.html"

MARKET_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

_lock   = threading.Lock()
_status: dict = {"running": False, "last_run": None, "last_error": None}
_refresh_interval_min: int = 15


def _run_orchestrator() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _status["running"]    = True
        _status["last_error"] = None
        now = datetime.now(IST).strftime("%H:%M:%S")
        print(f"[{now}] Market refresh started…", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "stock_market.orchestrator", "--workers", "8"],
                cwd=str(BASE_DIR.parent),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                _status["last_error"] = result.stderr[-500:]
                print(result.stderr[-500:], file=sys.stderr)
            else:
                _status["last_run"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
                print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Market refresh complete.", flush=True)
        except Exception as exc:
            _status["last_error"] = str(exc)
        finally:
            _status["running"] = False
    finally:
        _lock.release()


def _start_scheduler(interval_minutes: int) -> None:
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            _run_orchestrator, trigger="interval", minutes=interval_minutes,
            id="market_refresh", max_instances=1,
        )
        scheduler.start()
        print(f"  Scheduler started — market refresh every {interval_minutes} min", flush=True)
    except ImportError:
        print("  APScheduler not installed — auto-refresh disabled", flush=True)


@app.route("/")
def index():
    if not MARKET_HTML.exists():
        if not _status["running"]:
            threading.Thread(target=_run_orchestrator, daemon=True).start()
        return Response(
            "<html><body style='font-family:sans-serif;text-align:center;"
            "padding:60px;background:#070c1b;color:#e8edf5'>"
            "<h2>📈 Indian Stock Market Snapshot</h2>"
            "<p>Fetching live quotes… Please refresh in 20 seconds.</p>"
            "</body></html>", mimetype="text/html",
        )
    if MARKET_JSON.exists() and not _status["running"]:
        try:
            gen = json.loads(MARKET_JSON.read_text(encoding="utf-8"))["generated_at"]
            dt  = datetime.strptime(gen, "%Y-%m-%d %H:%M IST").replace(tzinfo=IST)
            age_min = (datetime.now(IST) - dt).total_seconds() / 60
            if age_min > _refresh_interval_min:
                threading.Thread(target=_run_orchestrator, daemon=True).start()
        except Exception:
            pass
    resp = send_from_directory(str(MARKET_DIR), "stock_market_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/market")
def api_market():
    if not MARKET_JSON.exists():
        return jsonify({"error": "No market data yet. Try again shortly."}), 503
    return jsonify(json.loads(MARKET_JSON.read_text(encoding="utf-8")))


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    if _status["running"]:
        return jsonify({"status": "already_running"}), 202
    threading.Thread(target=_run_orchestrator, daemon=True).start()
    return jsonify({"status": "started"}), 202


@app.route("/api/status")
def api_status():
    age_s = None
    if MARKET_JSON.exists():
        try:
            gen = json.loads(MARKET_JSON.read_text())["generated_at"]
            dt  = datetime.strptime(gen, "%Y-%m-%d %H:%M IST").replace(tzinfo=IST)
            age_s = round((datetime.now(IST) - dt).total_seconds())
        except Exception:
            pass
    return jsonify({
        "running": _status["running"], "last_run": _status["last_run"],
        "last_error": _status["last_error"], "data_age_s": age_s,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Stock Market Flask Server")
    parser.add_argument("--port", type=int, default=5002)
    parser.add_argument("--refresh", type=int, default=15,
                         help="Auto-refresh interval in minutes (default: 15)")
    parser.add_argument("--no-scheduler", action="store_true")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  📈  Indian Stock Market Snapshot Server")
    print(f"  URL  : http://localhost:{args.port}")
    print(f"  API  : http://localhost:{args.port}/api/market")
    print("=" * 55 + "\n")

    global _refresh_interval_min
    _refresh_interval_min = args.refresh

    if not args.no_scheduler:
        _start_scheduler(args.refresh)

    if not MARKET_JSON.exists():
        print("  Cold start — fetching initial market data…")
        threading.Thread(target=_run_orchestrator, daemon=True).start()

    import os
    port = int(os.environ.get("PORT", args.port))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
