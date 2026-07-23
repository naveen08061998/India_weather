"""
India Weather PWA — Flask Server
=================================
Serves the dashboard as a Progressive Web App with:
  • Auto-refresh of weather data every 30 minutes (background scheduler)
  • REST API  :  GET /api/weather   GET /api/alerts
  • PWA assets:  /manifest.json     /sw.js
  • Push notification subscription endpoints

Run:
    python app.py
    python app.py --port 8080 --refresh 30

Railway / cloud deployment:
    The PORT environment variable is respected automatically.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, Response

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
WEATHER_DIR = BASE_DIR / "india_weather" / "weathers"
WEATHER_JSON = WEATHER_DIR / "india_weather_data.json"
ALERTS_JSON  = WEATHER_DIR / "india_alerts.json"
HTML_FILE    = WEATHER_DIR / "india_weather_report.html"
STATIC_DIR   = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR))

# ── Scheduler (background data refresh) ───────────────────────────────────
_refresh_lock  = threading.Lock()
_refresh_status: dict = {"running": False, "last_run": None, "last_error": None}


def run_orchestrator() -> None:
    """Run the Python orchestrator in a subprocess to refresh all state data."""
    if _refresh_lock.locked():
        return  # already running
    with _refresh_lock:
        _refresh_status["running"] = True
        _refresh_status["last_error"] = None
        print(f"[{datetime.now():%H:%M:%S}] Auto-refresh started…", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "india_weather.orchestrator", "--workers", "8"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                _refresh_status["last_error"] = result.stderr[-500:]
            else:
                _refresh_status["last_run"] = datetime.now().isoformat(timespec="seconds")
                print(f"[{datetime.now():%H:%M:%S}] Auto-refresh complete.", flush=True)
        except Exception as exc:
            _refresh_status["last_error"] = str(exc)
        finally:
            _refresh_status["running"] = False


def start_scheduler(interval_minutes: int) -> None:
    """Start APScheduler to call run_orchestrator every `interval_minutes`."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            run_orchestrator,
            trigger="interval",
            minutes=interval_minutes,
            id="weather_refresh",
            max_instances=1,
        )
        scheduler.start()
        print(f"  Scheduler started — data refresh every {interval_minutes} min", flush=True)
    except ImportError:
        print("  APScheduler not installed — auto-refresh disabled", flush=True)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main dashboard HTML."""
    if not HTML_FILE.exists():
        # Cold start: generate a shell HTML immediately so the page loads,
        # then fetch live data in the background.
        _cold_start_generate()
    return send_from_directory(str(WEATHER_DIR), "india_weather_report.html")


@app.route("/api/weather")
def api_weather():
    """Return the latest baked weather JSON."""
    if not WEATHER_JSON.exists():
        return jsonify({"error": "No weather data yet"}), 503
    data = json.loads(WEATHER_JSON.read_text(encoding="utf-8"))
    return jsonify(data)


@app.route("/api/alerts")
def api_alerts():
    """Return the latest alerts JSON."""
    if not ALERTS_JSON.exists():
        return jsonify({"cyclones": [], "district_alerts": [], "generated_at": ""}), 200
    data = json.loads(ALERTS_JSON.read_text(encoding="utf-8"))
    return jsonify(data)


@app.route("/api/status")
def api_status():
    """Return scheduler/refresh status."""
    return jsonify({
        "scheduler_running": _refresh_status["running"],
        "last_refresh":      _refresh_status["last_run"],
        "last_error":        _refresh_status["last_error"],
        "weather_age_s": (
            round((datetime.now() - datetime.fromisoformat(
                json.loads(WEATHER_JSON.read_text())["generated_at"]
            )).total_seconds())
            if WEATHER_JSON.exists() else None
        ),
    })


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Manually trigger an immediate data refresh."""
    if _refresh_status["running"]:
        return jsonify({"status": "already_running"}), 202
    thread = threading.Thread(target=run_orchestrator, daemon=True)
    thread.start()
    return jsonify({"status": "started"}), 202


# ── PWA assets ─────────────────────────────────────────────────────────────

@app.route("/manifest.json")
def manifest():
    return send_from_directory(str(STATIC_DIR), "manifest.json")


@app.route("/sw.js")
def service_worker():
    """Serve the service worker with the correct MIME type and scope header."""
    resp = send_from_directory(str(STATIC_DIR), "sw.js")
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)


# ── CLI (local dev only) ──────────────────────────────────────────────────

def _cold_start_generate() -> None:
    """Generate HTML from whatever data exists (may be empty on first deploy)."""
    try:
        WEATHER_DIR.mkdir(parents=True, exist_ok=True)
        from india_weather.weather_report import generate
        generate()
        print("[Boot] HTML generated.", flush=True)
    except Exception as exc:
        print(f"[Boot] HTML generation failed: {exc}", flush=True)


def _boot_fetch() -> None:
    """On cold start: generate HTML shell, then fetch live data in background."""
    _cold_start_generate()
    print("[Boot] Starting initial data fetch in background…", flush=True)
    thread = threading.Thread(target=run_orchestrator, daemon=True)
    thread.start()


# ── Module-level init (runs under gunicorn AND python app.py) ──────────────
# Ensure directories exist
WEATHER_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
# Generate HTML if missing (cold Railway deploy) and kick off background fetch
if not HTML_FILE.exists():
    _boot_fetch()
# Start periodic auto-refresh scheduler
start_scheduler(int(os.environ.get("REFRESH_MINUTES", 30)))


# ── CLI (local dev only) ──────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="India Weather PWA Server")
    default_port = int(os.environ.get("PORT", 5000))
    p.add_argument("--port",    type=int, default=default_port)
    p.add_argument("--host",    default="0.0.0.0")
    p.add_argument("--refresh", type=int, default=30)
    p.add_argument("--no-refresh", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    print("\n" + "═" * 55)
    print("  India Weather PWA")
    print("═" * 55)
    print(f"  Dashboard → http://localhost:{args.port}/")
    print(f"  API       → http://localhost:{args.port}/api/weather")
    print(f"  Alerts    → http://localhost:{args.port}/api/alerts")
    print(f"  Status    → http://localhost:{args.port}/api/status")
    print("═" * 55 + "\n")

    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
