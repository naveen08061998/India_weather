"""
India Borders Atlas — Standalone Flask Server
================================================
Serves the state/UT border-adjacency dashboard. Data is static (settled
public geography) so there is no refresh scheduler — the report is built
once on first request if missing, same as any other static agent.

Run:
    python india_borders/app.py
    python india_borders/app.py --port 5005

Endpoints:
    GET  /              → HTML dashboard
    GET  /api/borders    → Full JSON (all states/UTs + stats)
    GET  /api/regions/<key> → Single region's data
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, Response

BASE_DIR     = Path(__file__).parent
BORDERS_DIR  = BASE_DIR / "borders"
BORDERS_JSON = BORDERS_DIR / "india_borders_data.json"
BORDERS_HTML = BORDERS_DIR / "india_borders_report.html"

BORDERS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
_lock = threading.Lock()
_building = {"running": False}


def _build_once() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _building["running"] = True
        subprocess.run(
            [sys.executable, "-m", "india_borders.orchestrator"],
            cwd=str(BASE_DIR.parent), capture_output=True, text=True, timeout=60,
        )
    finally:
        _building["running"] = False
        _lock.release()


@app.route("/")
def index():
    if not BORDERS_HTML.exists():
        if not _building["running"]:
            threading.Thread(target=_build_once, daemon=True).start()
        return Response(
            "<html><body style='font-family:serif;text-align:center;"
            "padding:60px;background:#f3ead3;color:#2b2118'>"
            "<h2>🧭 India Borders Atlas</h2>"
            "<p>Compiling the atlas… Please refresh in a few seconds.</p>"
            "</body></html>", mimetype="text/html",
        )
    resp = send_from_directory(str(BORDERS_DIR), "india_borders_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/borders")
def api_borders():
    if not BORDERS_JSON.exists():
        return jsonify({"error": "Not built yet. Try again shortly."}), 503
    return jsonify(json.loads(BORDERS_JSON.read_text(encoding="utf-8")))


@app.route("/api/regions/<key>")
def api_region(key: str):
    if not BORDERS_JSON.exists():
        return jsonify({"error": "Not built yet."}), 503
    data = json.loads(BORDERS_JSON.read_text(encoding="utf-8"))
    region = data["regions"].get(key)
    if not region:
        return jsonify({"error": "Unknown region key"}), 404
    return jsonify(region)


def main() -> None:
    parser = argparse.ArgumentParser(description="India Borders Atlas Flask Server")
    parser.add_argument("--port", type=int, default=5005)
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  🧭  India Borders Atlas Server")
    print("=" * 55)
    if not BORDERS_JSON.exists():
        print("  Building atlas data for the first time…")
        _build_once()
    print(f"  Dashboard: http://127.0.0.1:{args.port}/")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
