"""
Indian Railways Tracker — Standalone Flask Server
=================================================
Serves the Railways tracker independently from weather/current-affairs.

Run:
    python -m indian_railways.app
    python -m indian_railways.app --port 5002

Endpoints:
    GET  /                   -> Railways dashboard HTML
    GET  /api/trains         -> Summary + curated trains payload
    GET  /api/trains/search  -> Search by train number/name
    GET  /api/trains/route   -> Search by source/destination
    GET  /api/trains/<no>    -> Live status for one train
    POST /api/refresh        -> Rebuild cached payload and HTML
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from indian_railways.ir_client import get_status_for_number, search_by_route, search_trains
from indian_railways.orchestrator import build_payload, generate_html, save_json

BASE_DIR = Path(__file__).parent
TRAINS_DIR = BASE_DIR / "trains"
HTML_FILE = TRAINS_DIR / "railways_report.html"

_CACHE_TTL_S = 30
_cache: dict = {"ts": 0.0, "payload": None}

app = Flask(__name__)


def _rebuild_payload() -> dict:
    payload = build_payload()
    save_json(payload)
    generate_html(payload)
    _cache["payload"] = payload
    _cache["ts"] = time.time()
    return payload


def _ensure_dashboard() -> None:
    TRAINS_DIR.mkdir(parents=True, exist_ok=True)
    if not HTML_FILE.exists():
        _rebuild_payload()


@app.route("/")
def index():
    _ensure_dashboard()
    return send_from_directory(str(TRAINS_DIR), "railways_report.html")


@app.route("/api/trains")
def api_trains():
    now = time.time()
    if _cache["payload"] is None or now - _cache["ts"] > _CACHE_TTL_S:
        _cache["payload"] = build_payload()
        _cache["ts"] = now
    return jsonify(_cache["payload"])


@app.route("/api/trains/search")
def api_trains_search():
    q = request.args.get("q", "")
    return jsonify({"query": q, "results": search_trains(q)})


@app.route("/api/trains/route")
def api_trains_route():
    from_q = request.args.get("from", "")
    to_q = request.args.get("to", "")
    return jsonify({"from": from_q, "to": to_q, "results": search_by_route(from_q, to_q)})


@app.route("/api/trains/<train_number>")
def api_train_detail(train_number: str):
    result = get_status_for_number(train_number)
    if result is None:
        return jsonify({"error": f"Unknown train number '{train_number}'"}), 404
    return jsonify(result)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    payload = _rebuild_payload()
    return jsonify({
        "status": "ok",
        "generated_at": payload.get("generated_at"),
        "total_trains": payload.get("total_trains"),
        "running_now": payload.get("running_now"),
    })


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Indian Railways standalone server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5002)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    print("\n" + "=" * 55)
    print("  Indian Railways Tracker")
    print("=" * 55)
    print(f"  Dashboard -> http://localhost:{args.port}/")
    print(f"  API       -> http://localhost:{args.port}/api/trains")
    print("=" * 55 + "\n")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
