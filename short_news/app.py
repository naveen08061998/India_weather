"""
Short News PWA — Standalone Flask Server
============================================
Serves the "Quick Read" bite-sized news digest. Independent of the other
agents.

Run:
    python short_news/app.py
    python short_news/app.py --port 5007 --refresh 20

Endpoints:
    GET  /               → HTML dashboard
    GET  /api/news        → Full JSON (all categories + stories)
    POST /api/refresh     → Manually trigger a refresh
    GET  /api/status      → Scheduler & refresh status
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

from flask import Flask, jsonify, send_from_directory, Response

BASE_DIR    = Path(__file__).parent
DIGEST_DIR  = BASE_DIR / "digest"
DIGEST_JSON = DIGEST_DIR / "short_news_data.json"
DIGEST_HTML = DIGEST_DIR / "short_news_report.html"

DIGEST_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

_lock   = threading.Lock()
_status: dict = {"running": False, "last_run": None, "last_error": None}
_refresh_interval_min: int = 20


def _run_orchestrator() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _status["running"]    = True
        _status["last_error"] = None
        print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Short News refresh started…", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "short_news.orchestrator"],
                cwd=str(BASE_DIR.parent),
                capture_output=True, text=True, timeout=180,
            )
            if result.returncode != 0:
                _status["last_error"] = result.stderr[-500:]
                print(result.stderr[-500:], file=sys.stderr)
            else:
                _status["last_run"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
                print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Short News refresh complete.", flush=True)
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
            id="short_news_refresh", max_instances=1,
        )
        scheduler.start()
        print(f"  Scheduler started — Short News refresh every {interval_minutes} min", flush=True)
    except ImportError:
        print("  APScheduler not installed — auto-refresh disabled", flush=True)


@app.route("/")
def index():
    if not DIGEST_HTML.exists():
        if not _status["running"]:
            threading.Thread(target=_run_orchestrator, daemon=True).start()
        return Response(
            "<html><body style='font-family:sans-serif;text-align:center;"
            "padding:60px;background:linear-gradient(135deg,#ff6b6b,#feca57);color:#fff'>"
            "<h2>⚡ Short News — Quick Read</h2>"
            "<p>Fetching today's stories… Please refresh in 20 seconds.</p>"
            "</body></html>", mimetype="text/html",
        )
    if DIGEST_JSON.exists() and not _status["running"]:
        try:
            gen = json.loads(DIGEST_JSON.read_text(encoding="utf-8"))["generated_at"]
            dt  = datetime.strptime(gen, "%Y-%m-%d %H:%M IST").replace(tzinfo=IST)
            age_min = (datetime.now(IST) - dt).total_seconds() / 60
            if age_min > _refresh_interval_min:
                threading.Thread(target=_run_orchestrator, daemon=True).start()
        except Exception:
            pass
    resp = send_from_directory(str(DIGEST_DIR), "short_news_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/news")
def api_news():
    if not DIGEST_JSON.exists():
        return jsonify({"error": "No data yet. Try again shortly."}), 503
    return jsonify(json.loads(DIGEST_JSON.read_text(encoding="utf-8")))


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    if _status["running"]:
        return jsonify({"status": "already running"}), 202
    threading.Thread(target=_run_orchestrator, daemon=True).start()
    return jsonify({"status": "started"}), 202


@app.route("/api/status")
def api_status():
    return jsonify(_status)


def main() -> None:
    parser = argparse.ArgumentParser(description="Short News Flask Server")
    parser.add_argument("--port", type=int, default=5007)
    parser.add_argument("--refresh", type=int, default=20, help="Auto-refresh interval in minutes")
    args = parser.parse_args()

    global _refresh_interval_min
    _refresh_interval_min = args.refresh

    print("\n" + "=" * 55)
    print("  ⚡  Short News — Quick Read Server")
    print("=" * 55)
    if not DIGEST_JSON.exists():
        print("  Fetching today's stories for the first time…")
        _run_orchestrator()
    _start_scheduler(args.refresh)
    print(f"  Dashboard: http://127.0.0.1:{args.port}/")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
