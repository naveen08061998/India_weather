"""
The Lexicon (Abbreviations) — Standalone Flask Server
========================================================
Serves the general-abbreviations dashboard. Data is static (curated
reference facts) so there is no refresh scheduler — the report is built
once on first request if missing, same as india_borders/india_highways.

Run:
    python abbreviations/app.py
    python abbreviations/app.py --port 5006

Endpoints:
    GET  /                    → HTML dashboard
    GET  /api/abbreviations   → Full JSON (all entries + stats)
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
LEXICON_DIR  = BASE_DIR / "lexicon"
LEXICON_JSON = LEXICON_DIR / "abbreviations_data.json"
LEXICON_HTML = LEXICON_DIR / "abbreviations_report.html"

LEXICON_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
_lock = threading.Lock()
_building = {"running": False}


def _build_once() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _building["running"] = True
        subprocess.run(
            [sys.executable, "-m", "abbreviations.orchestrator"],
            cwd=str(BASE_DIR.parent), capture_output=True, text=True, timeout=60,
        )
    finally:
        _building["running"] = False
        _lock.release()


@app.route("/")
def index():
    if not LEXICON_HTML.exists():
        if not _building["running"]:
            threading.Thread(target=_build_once, daemon=True).start()
        return Response(
            "<html><body style='font-family:serif;text-align:center;"
            "padding:60px;background:#faf7f2;color:#2b1d22'>"
            "<h2>📖 The Lexicon</h2>"
            "<p>Compiling the reference… Please refresh in a few seconds.</p>"
            "</body></html>", mimetype="text/html",
        )
    resp = send_from_directory(str(LEXICON_DIR), "abbreviations_report.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/abbreviations")
def api_abbreviations():
    if not LEXICON_JSON.exists():
        return jsonify({"error": "Not built yet. Try again shortly."}), 503
    return jsonify(json.loads(LEXICON_JSON.read_text(encoding="utf-8")))


def main() -> None:
    parser = argparse.ArgumentParser(description="The Lexicon (Abbreviations) Flask Server")
    parser.add_argument("--port", type=int, default=5006)
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  📖  The Lexicon — Abbreviations Server")
    print("=" * 55)
    if not LEXICON_JSON.exists():
        print("  Building reference data for the first time…")
        _build_once()
    print(f"  Dashboard: http://127.0.0.1:{args.port}/")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
