"""
Current Affairs PWA — Standalone Flask Server
===============================================
Serves the Current Affairs dashboard as a standalone web app.
Completely independent of the india_weather agent.

Run:
    python current_affairs/app.py
    python current_affairs/app.py --port 5001 --refresh 30

Endpoints:
    GET  /                      → HTML dashboard
    GET  /api/news              → Latest news JSON (all categories)
    GET  /api/news/<category>   → News for a specific category
    POST /api/refresh           → Manually trigger a news refresh
    GET  /api/status            → Scheduler & refresh status
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

from flask import Flask, jsonify, request, send_from_directory, Response

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
NEWS_DIR    = BASE_DIR / "news"
NEWS_JSON   = NEWS_DIR / "current_affairs_data.json"
NEWS_HTML   = NEWS_DIR / "current_affairs_report.html"

NEWS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

# ── Refresh state ──────────────────────────────────────────────────────────
_lock   = threading.Lock()
_status: dict = {"running": False, "last_run": None, "last_error": None}
_refresh_interval_min: int = 30   # updated by main() from --refresh arg


def _run_orchestrator() -> None:
    """Run orchestrator in a subprocess to fetch fresh news."""
    if not _lock.acquire(blocking=False):
        return  # another refresh is already in progress
    try:
        _status["running"]    = True
        _status["last_error"] = None
        now = datetime.now(IST).strftime("%H:%M:%S")
        print(f"[{now}] News refresh started…", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "current_affairs.orchestrator",
                 "--workers", "5"],
                cwd=str(BASE_DIR.parent),   # project root
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                _status["last_error"] = result.stderr[-500:]
                print(result.stderr[-500:], file=sys.stderr)
            else:
                _status["last_run"] = (
                    datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
                )
                now2 = datetime.now(IST).strftime("%H:%M:%S")
                print(f"[{now2}] News refresh complete.", flush=True)
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
            _run_orchestrator,
            trigger="interval",
            minutes=interval_minutes,
            id="news_refresh",
            max_instances=1,
        )
        scheduler.start()
        print(f"  Scheduler started — news refresh every {interval_minutes} min",
              flush=True)
    except ImportError:
        print("  APScheduler not installed — auto-refresh disabled", flush=True)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the current affairs dashboard."""
    if not NEWS_HTML.exists():
        # Cold start: fetch in background, serve a loading page
        if not _status["running"]:
            threading.Thread(target=_run_orchestrator, daemon=True).start()
        return Response(
            "<html><body style='font-family:sans-serif;text-align:center;"
            "padding:60px;background:#0f172a;color:#e2e8f0'>"
            "<h2>\U0001f4f0 Current Affairs Daily</h2>"
            "<p>Fetching today's news\u2026 Please refresh in 30 seconds.</p>"
            "</body></html>",
            mimetype="text/html",
        )
    # Auto-trigger a background refresh if cached data is stale
    if NEWS_JSON.exists() and not _status["running"]:
        try:
            gen = json.loads(NEWS_JSON.read_text(encoding="utf-8"))["generated_at"]
            dt  = datetime.strptime(gen, "%Y-%m-%d %H:%M IST").replace(tzinfo=IST)
            age_min = (datetime.now(IST) - dt).total_seconds() / 60
            if age_min > _refresh_interval_min:
                threading.Thread(target=_run_orchestrator, daemon=True).start()
        except Exception:
            pass
    resp = send_from_directory(str(NEWS_DIR), "current_affairs_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/api/news")
def api_news():
    """Return full news JSON payload."""
    if not NEWS_JSON.exists():
        return jsonify({"error": "No news data yet. Try again shortly."}), 503
    data = json.loads(NEWS_JSON.read_text(encoding="utf-8"))
    return jsonify(data)


@app.route("/api/news/<category_key>")
def api_news_category(category_key: str):
    """Return news for a specific category."""
    if not NEWS_JSON.exists():
        return jsonify({"error": "No news data yet."}), 503
    data = json.loads(NEWS_JSON.read_text(encoding="utf-8"))
    cats = data.get("categories", {})
    if category_key not in cats:
        return jsonify({"error": f"Category '{category_key}' not found."}), 404
    return jsonify(cats[category_key])


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Manually trigger a news refresh."""
    if _status["running"]:
        return jsonify({"status": "already_running"}), 202
    threading.Thread(target=_run_orchestrator, daemon=True).start()
    return jsonify({"status": "started"}), 202


# ── History routes ──────────────────────────────────────────────────────────

@app.route("/history")
def history_index():
    """Redirect to the most recently archived day, or show an empty state."""
    from current_affairs.history_agent import list_dates
    from flask import redirect
    dates = list_dates()
    if not dates:
        return Response(
            "<html><body style='font-family:sans-serif;text-align:center;"
            "padding:60px;background:#0f172a;color:#e2e8f0'>"
            "<h2>📚 History Archive</h2>"
            "<p>No history yet. Come back after the first day rollover.</p>"
            "<p><a href='/' style='color:#818cf8'>← Back to Today</a></p>"
            "</body></html>",
            mimetype="text/html",
        )
    return redirect(f"/history/{dates[0]}")


@app.route("/history/<date_key>")
def history_day(date_key: str):
    """Render the historical digest for a specific YYYY-MM-DD date."""
    import re
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_key):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    from current_affairs.history_agent import load_snapshot, list_dates
    from current_affairs.history_report import build_history_html
    snapshot = load_snapshot(date_key)
    if snapshot is None:
        return Response(
            f"<html><body style='font-family:sans-serif;text-align:center;"
            f"padding:60px;background:#0f172a;color:#e2e8f0'>"
            f"<h2>📚 No archive for {date_key}</h2>"
            f"<p><a href='/history' style='color:#818cf8'>← Browse available dates</a></p>"
            f"</body></html>",
            mimetype="text/html",
        ), 404
    html = build_history_html(snapshot, list_dates())
    resp = Response(html, mimetype="text/html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/api/history")
def api_history_list():
    """List all available archived dates."""
    from current_affairs.history_agent import list_dates
    return jsonify({"dates": list_dates()})


@app.route("/api/history/<date_key>")
def api_history_day(date_key: str):
    """Return the archived news snapshot for a specific YYYY-MM-DD date."""
    import re
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_key):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    from current_affairs.history_agent import load_snapshot
    snapshot = load_snapshot(date_key)
    if snapshot is None:
        return jsonify({"error": f"No archive for {date_key}."}), 404
    return jsonify(snapshot)


@app.route("/api/status")
def api_status():
    """Return refresh/scheduler status."""
    age_s = None
    if NEWS_JSON.exists():
        try:
            gen = json.loads(NEWS_JSON.read_text())["generated_at"]
            # Parse "YYYY-MM-DD HH:MM IST"
            dt  = datetime.strptime(gen, "%Y-%m-%d %H:%M IST").replace(
                tzinfo=IST
            )
            age_s = round(
                (datetime.now(IST) - dt).total_seconds()
            )
        except Exception:
            pass
    return jsonify({
        "running"   : _status["running"],
        "last_run"  : _status["last_run"],
        "last_error": _status["last_error"],
        "data_age_s": age_s,
    })


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Current Affairs Flask Server"
    )
    parser.add_argument("--port",    type=int, default=5001)
    parser.add_argument("--refresh", type=int, default=30,
                        help="Auto-refresh interval in minutes (default: 30)")
    parser.add_argument("--no-scheduler", action="store_true",
                        help="Disable background scheduler")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  📰  Current Affairs Daily Server")
    print(f"  URL  : http://localhost:{args.port}")
    print(f"  API  : http://localhost:{args.port}/api/news")
    print("=" * 55 + "\n")

    global _refresh_interval_min
    _refresh_interval_min = args.refresh

    if not args.no_scheduler:
        _start_scheduler(args.refresh)

    # Fetch data on cold start if JSON is missing
    if not NEWS_JSON.exists():
        print("  Cold start — fetching initial news data…")
        threading.Thread(target=_run_orchestrator, daemon=True).start()

    import os
    port = int(os.environ.get("PORT", args.port))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
