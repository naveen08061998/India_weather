"""
Indian Railways — Live Status Simulator
=========================================
There is no free official real-time GPS feed for Indian Railways, so this
module SIMULATES a train's current position/delay by comparing the current
time against its public schedule (train_data.py). Delay is modeled as a
per-stop random walk, deterministically seeded from the train number +
service date + stop index, so the same train shows a consistent (but not
truly live) status throughout a given day — delay gradually drifts up and
down along the route (congestion adds it, timetable padding recovers it)
rather than being one fixed number for the whole journey. The odds of
gaining vs. recovering delay at each stop are biased by the train's
punctuality tier — premium named trains (Rajdhani/Shatabdi/Duronto/Vande
Bharat/Tejas) run closer to schedule than ordinary Mail/Express services,
matching IR's well-documented priority order — see _TIER_BY_TYPE below.

This is a DEMO tracker — for official live running status use NTES
(enquiry.indianrail.gov.in) or IRCTC.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timedelta, timezone

from indian_railways.train_data import CURATED_TRAIN_NUMBERS, STATION_ALIASES, STATION_COORDS, TRAINS, TRAINS_BY_NUMBER

IST = timezone(timedelta(hours=5, minutes=30))


def _enrich_route(route: list[dict]) -> list[dict]:
    """Attach lat/lon to each stop (when known) so the browser can match GPS to a station."""
    enriched = []
    for stop in route:
        coords = STATION_COORDS.get(stop["code"])
        enriched.append({**stop, "lat": coords[0] if coords else None, "lon": coords[1] if coords else None})
    return enriched


def _parse_time(hhmm: str) -> tuple[int, int]:
    h, m = hhmm.split(":")
    return int(h), int(m)


def _stop_dt(anchor_date: date, stop: dict, clock_field: str) -> datetime | None:
    """Absolute datetime for a stop's arr/dep clock time, anchored to anchor_date + (day-1)."""
    value = stop.get(clock_field)
    if value is None:
        return None
    h, m = _parse_time(value)
    d = anchor_date + timedelta(days=stop["day"] - 1)
    return datetime(d.year, d.month, d.day, h, m, tzinfo=IST)


# Punctuality tiers by train type, reflecting IR's well-documented operating
# priority order (premium named trains get signal precedence and run closer
# to schedule; ordinary Mail/Express services absorb more crossings/overtakes
# and slip more often). These are informed estimates from IR's known priority
# structure, not figures pulled from a live/official punctuality feed.
_TIER_BY_TYPE = {
    "Rajdhani": "premium", "Shatabdi": "premium", "Duronto": "premium",
    "Vande Bharat": "premium", "Tejas": "premium",
    "Garib Rath": "mid", "Superfast": "mid", "Sampark Kranti": "mid",
    "Jan Shatabdi": "mid", "Mail-Express": "mid",
    "Express": "regular", "Mail": "regular",
}


# (pct chance delay grows at a given stop, pct chance it shrinks, max late
# minutes, max early minutes). Early running is capped much tighter than
# late running — schedule padding lets a train gain a few minutes back, but
# it rarely arrives dramatically ahead of the timetable.
_TIER_WALK_PARAMS = {
    "premium": (10, 12, 40, 10),
    "mid":     (16, 9, 70, 8),
    "regular": (22, 6, 100, 6),
}


def _delay_series(train: dict, service_date: date) -> list[int]:
    """Cumulative simulated delay (minutes, may be negative = running early)
    at each stop along the route, modeled as a bounded random walk seeded
    per train+date+stop-index so delay realistically drifts over the
    journey — gained at some stops (congestion/signals), recovered at others
    (timetable padding), occasionally dipping slightly ahead of schedule —
    instead of being one fixed, never-negative number applied to the whole
    trip. This keeps "between station A and B" transitions from flipping on
    a hard, unrealistic minute boundary the way a single flat delay would."""
    tier = _TIER_BY_TYPE.get(train.get("type", ""), "mid")
    p_gain, p_recover, cap, early_cap = _TIER_WALK_PARAMS[tier]
    route = train["route"]
    number = train["number"]
    delays = [0]
    for i in range(1, len(route)):
        key = f"{number}:{service_date.isoformat()}:{i}"
        digest = hashlib.sha256(key.encode()).hexdigest()
        roll = int(digest[:4], 16) % 100
        step = 0
        if roll < p_gain:
            step = int(digest[4:6], 16) % 6 + 1       # +1..+6 min
        elif roll < p_gain + p_recover:
            step = -(int(digest[4:6], 16) % 4 + 1)     # -1..-4 min (recovered time)
        delays.append(max(-early_cap, min(cap, delays[-1] + step)))
    return delays


def _next_run_date(train: dict, from_date: date) -> date:
    """Next date (>= from_date) on which the train departs its origin."""
    for offset in range(0, 8):
        d = from_date + timedelta(days=offset)
        if d.strftime("%a") in train["runs_on"]:
            return d
    return from_date  # unreachable — runs_on is always non-empty


def _delay_phrase(delay: int) -> str:
    """Human-readable suffix for a (possibly negative = early) delay value."""
    if delay > 0:
        return f"{delay} min late"
    if delay < 0:
        return f"{-delay} min early"
    return "on time"


def _position_within_journey(train: dict, service_date: date, now: datetime) -> dict:
    route = train["route"]
    delays = _delay_series(train, service_date)
    origin, destination = route[0], route[-1]
    total_dist = destination["dist"] or 1

    last_idx = 0
    for i, stop in enumerate(route):
        stop_time = _stop_dt(service_date, stop, "dep") or _stop_dt(service_date, stop, "arr")
        if stop_time and stop_time + timedelta(minutes=delays[i]) <= now:
            last_idx = i
        else:
            break

    delay = delays[last_idx]
    last_stop = route[last_idx]
    arr_dt = _stop_dt(service_date, last_stop, "arr")
    dep_dt = _stop_dt(service_date, last_stop, "dep")
    offset = timedelta(minutes=delay)
    at_station = bool(arr_dt and dep_dt and arr_dt + offset <= now < dep_dt + offset)

    if last_idx == len(route) - 1:
        label = f"Arrived at {destination['name']} — {_delay_phrase(delay)}"
        return {
            "status": "arrived", "status_label": label, "delay_min": delay,
            "last_station": destination["name"], "next_station": None, "eta": None,
            "percent_complete": 100.0, "origin": origin["name"], "destination": destination["name"],
            "service_date": service_date.isoformat(),
        }

    next_stop = route[last_idx + 1]
    next_delay = delays[last_idx + 1]
    next_arr_dt = _stop_dt(service_date, next_stop, "arr") or _stop_dt(service_date, next_stop, "dep")

    if at_station:
        pct_dist = last_stop["dist"]
        label = f"Halted at {last_stop['name']}"
    else:
        seg_start = (dep_dt or arr_dt)
        seg_start = seg_start + offset if seg_start else None
        seg_end = next_arr_dt + timedelta(minutes=next_delay) if next_arr_dt else None
        frac = 0.0
        if seg_start and seg_end and seg_end > seg_start:
            frac = max(0.0, min(1.0, (now - seg_start).total_seconds() / (seg_end - seg_start).total_seconds()))
        pct_dist = last_stop["dist"] + frac * (next_stop["dist"] - last_stop["dist"])
        label = f"Between {last_stop['name']} and {next_stop['name']}"

    label += f" — running {_delay_phrase(delay)}"
    eta = (next_arr_dt + timedelta(minutes=next_delay)).strftime("%H:%M") if next_arr_dt else None

    return {
        "status": "at_station" if at_station else "running",
        "status_label": label, "delay_min": delay,
        "last_station": last_stop["name"], "next_station": next_stop["name"],
        "eta": eta, "percent_complete": round((pct_dist / total_dist) * 100, 1),
        "origin": origin["name"], "destination": destination["name"],
        "service_date": service_date.isoformat(),
    }


def compute_status(train: dict, now: datetime | None = None) -> dict:
    """Simulated live status for `train` at time `now` (IST, defaults to current time)."""
    now = now.astimezone(IST) if now else datetime.now(IST)
    route = train["route"]
    origin, destination = route[0], route[-1]
    max_day = route[-1]["day"]

    for offset in range(-max_day, 1):
        candidate_date = now.date() + timedelta(days=offset)
        if candidate_date.strftime("%a") not in train["runs_on"]:
            continue
        start_dt = _stop_dt(candidate_date, origin, "dep")
        end_dt = _stop_dt(candidate_date, destination, "arr")
        if start_dt and end_dt and start_dt <= now <= end_dt:
            return _position_within_journey(train, candidate_date, now)

    next_date = _next_run_date(train, now.date())
    next_start = _stop_dt(next_date, origin, "dep")
    if next_start and next_start < now:
        next_date = _next_run_date(train, now.date() + timedelta(days=1))
        next_start = _stop_dt(next_date, origin, "dep")

    return {
        "status": "not_running",
        "status_label": (
            f"Not running now — next departs {origin['name']} "
            f"{next_date.strftime('%a %d %b')} {next_start.strftime('%H:%M') if next_start else ''}"
        ),
        "delay_min": 0, "last_station": None, "next_station": origin["name"], "eta": None,
        "percent_complete": 0.0, "origin": origin["name"], "destination": destination["name"],
        "service_date": None,
        "next_departure": next_start.isoformat() if next_start else None,
    }


def get_status_for_number(train_number: str, now: datetime | None = None) -> dict | None:
    train = TRAINS_BY_NUMBER.get(train_number.strip())
    if not train:
        return None
    return {
        "number": train["number"], "name": train["name"], "type": train["type"],
        "zone": train["zone"], "route": _enrich_route(train["route"]),
        "route_note": train.get("route_note"),
        **compute_status(train, now),
    }


def get_all_statuses(now: datetime | None = None) -> list[dict]:
    return [get_status_for_number(t["number"], now) for t in TRAINS]


def get_curated_statuses(now: datetime | None = None) -> list[dict]:
    """Statuses for just the small hand-curated subset (fast — used for the
    dashboard's default view, since scanning all ~2,400 trains takes ~1s)."""
    return [get_status_for_number(n, now) for n in CURATED_TRAIN_NUMBERS]


# The imported open dataset (build_dataset.py) has real data-quality issues for
# a large subset of trains: many entries carry hundreds of raw wayside-halt
# "stops" per route (real for some slow passenger trains, but far too heavy to
# ship to a browser — a handful even have an implausible total distance from
# corrupted/merged source records). Cap both so the embedded set stays a
# reasonable page-load size while covering far more than the curated ~56.
_MAX_PLAUSIBLE_ROUTE_KM = 4500
_MAX_ROUTE_STOPS = 30


def get_static_statuses(now: datetime | None = None) -> list[dict]:
    """Statuses for every train that passes a basic data-quality/size check,
    for embedding into the no-backend (GitHub Pages) build so From/To and
    name search work against a much larger set than the hand-curated ~56
    without shipping a multi-megabyte payload or known-corrupted routes."""
    curated = set(CURATED_TRAIN_NUMBERS)
    numbers = list(CURATED_TRAIN_NUMBERS)
    for t in TRAINS:
        if t["number"] in curated:
            continue
        route = t["route"]
        if route and route[-1]["dist"] <= _MAX_PLAUSIBLE_ROUTE_KM and len(route) <= _MAX_ROUTE_STOPS:
            numbers.append(t["number"])
    return [get_status_for_number(n, now) for n in numbers]


def search_trains(query: str, now: datetime | None = None, limit: int = 200) -> list[dict]:
    """Search trains by number, (partial, case-insensitive) name, or any
    station code/name along the route — not just the origin/destination —
    so typing an intermediate station's code (e.g. "MAS") finds trains that
    merely pass through it."""
    q = query.strip().lower()
    if not q:
        return []
    matches = []
    for t in TRAINS:
        stops = " ".join(f"{s['code']} {s['name']}" for s in t["route"])
        haystack = f"{t['number']} {t['name']} {stops}".lower()
        if q in haystack:
            matches.append(get_status_for_number(t["number"], now))
            if len(matches) >= limit:
                break
    return matches


def search_by_route(from_query: str, to_query: str, now: datetime | None = None, limit: int = 200) -> list[dict]:
    """Find trains whose route passes through `from_query` before `to_query`
    (matched case-insensitively against station name or exact code). Either
    side may be blank to mean "origin"/"destination" of the train itself."""
    from_q = (from_query or "").strip().lower()
    to_q = (to_query or "").strip().lower()
    if not from_q and not to_q:
        return []

    def find_idx(route: list[dict], needle: str) -> int:
        # Metro areas have multiple stations (e.g. Bengaluru = SBC/YPR/BNC) —
        # match any of them, not just a station literally named that.
        alias_codes = STATION_ALIASES.get(needle)
        if alias_codes:
            return next((i for i, s in enumerate(route) if s["code"] in alias_codes), -1)
        # Accepts a plain name, a station code, or the datalist's "CODE — Name" format.
        code_match = re.match(r"^([a-z0-9]+)\s*[\u2014-]\s*", needle)
        code = code_match.group(1) if code_match else needle
        # Exact code match always wins first — otherwise a short code like "mas"
        # would spuriously substring-match unrelated names (e.g. "Masaipet").
        code_idx = next((i for i, s in enumerate(route) if s["code"].lower() == code), -1)
        if code_idx != -1:
            return code_idx
        return next((i for i, s in enumerate(route) if needle in s["name"].lower()), -1)

    matches = []
    for t in TRAINS:
        route = t["route"]
        from_idx = find_idx(route, from_q) if from_q else 0
        to_idx = find_idx(route, to_q) if to_q else len(route) - 1
        if from_idx == -1 or to_idx == -1 or from_idx >= to_idx:
            continue
        matches.append(get_status_for_number(t["number"], now))
        if len(matches) >= limit:
            break
    return matches
