"""
India Highways — Standalone Flask Server
===========================================
Serves the National/State Highway reference dashboard. Data is static
(published MoRTH/NHAI figures) so there is no refresh scheduler — the
report is built once on first request if missing.

Run:
    python india_highways/app.py
    python india_highways/app.py --port 5006

Endpoints:
    GET  /              → HTML dashboard
    GET  /api/highways   → Full JSON (NH list + SH summary + network stats)
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
NETWORK_DIR  = BASE_DIR / "network"
NETWORK_JSON = NETWORK_DIR / "india_highways_data.json"
NETWORK_HTML = NETWORK_DIR / "india_highways_report.html"

NETWORK_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
_lock = threading.Lock()
_building = {"running": False}


def _build_once() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _building["running"] = True
        subprocess.run(
            [sys.executable, "-m", "india_highways.orchestrator"],
            cwd=str(BASE_DIR.parent), capture_output=True, text=True, timeout=60,
        )
    finally:
        _building["running"] = False
        _lock.release()


@app.route("/")
def index():
    if not NETWORK_HTML.exists():
        if not _building["running"]:
            threading.Thread(target=_build_once, daemon=True).start()
        return Response(
            "<html><body style='font-family:sans-serif;text-align:center;"
            "padding:60px;background:#1b1d21;color:#f2f3f0'>"
            "<h2>🛣️ India Highways</h2>"
            "<p>Compiling the highway network… Please refresh in a few seconds.</p>"
            "</body></html>", mimetype="text/html",
        )
    resp = send_from_directory(str(NETWORK_DIR), "india_highways_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/highways")
def api_highways():
    if not NETWORK_JSON.exists():
        return jsonify({"error": "Not built yet. Try again shortly."}), 503
    return jsonify(json.loads(NETWORK_JSON.read_text(encoding="utf-8")))


def main() -> None:
    parser = argparse.ArgumentParser(description="India Highways Flask Server")
    parser.add_argument("--port", type=int, default=5006)
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  🛣️   India Highways Server")
    print("=" * 55)
    if not NETWORK_JSON.exists():
        print("  Building highways data for the first time…")
        _build_once()
    print(f"  Dashboard: http://127.0.0.1:{args.port}/")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
