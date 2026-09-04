"""
One-off importer: converts the DataMeet Indian Railways open dataset
(CC0 / public domain — https://github.com/datameet/railways) into the
compact JSON format consumed by train_data.py.

Source dataset is from ~2016 and has no weekday/run-day info, so imported
trains default to running every day (a documented simplification).

Run manually to (re)build the bundled dataset:
    python -m indian_railways.tools.build_dataset
"""

from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

RAW_BASE = "https://raw.githubusercontent.com/datameet/railways/master"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR  = DATA_DIR / "raw"

# Long-distance categories worth tracking; commuter/local services (Pass,
# MEMU, DEMU, Toy) are excluded to keep the dataset a manageable size and
# focused on trains people actually search for. Keys are the dataset's own
# abbreviated "type" codes; values are the friendly display name we show.
TYPE_LABELS = {
    "Raj": "Rajdhani", "Drnt": "Duronto", "Shtb": "Shatabdi", "JShtb": "Jan Shatabdi",
    "SF": "Superfast", "GR": "Garib Rath", "SKr": "Sampark Kranti",
    "Exp": "Express", "Mail": "Mail", "Hyd": "Express", "": "Express",
}


def _download(name: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / name
    if dest.exists():
        print(f"  {name} already downloaded ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
    url = f"{RAW_BASE}/{name}"
    print(f"  Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"  Saved {name} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    return r * 2 * math.asin(math.sqrt(a))


def _clock(v: str | None) -> str | None:
    if not v or v == "None":
        return None
    return v[:5]


def _minutes(v: str | None) -> int | None:
    c = _clock(v)
    if not c:
        return None
    h, m = c.split(":")
    return int(h) * 60 + int(m)


def main() -> None:
    print("Downloading DataMeet Indian Railways open dataset (CC0)...")
    stations_path  = _download("stations.json")
    trains_path    = _download("trains.json")
    schedules_path = _download("schedules.json")

    print("Loading stations...")
    stations_geo = json.loads(stations_path.read_text(encoding="utf-8"))
    stations: dict[str, dict] = {}
    skipped_no_geo = 0
    for feat in stations_geo["features"]:
        p = feat["properties"]
        geom = feat.get("geometry")
        if not geom or not geom.get("coordinates"):
            skipped_no_geo += 1
            continue
        lon, lat = geom["coordinates"]
        stations[p["code"]] = {"name": p["name"].title(), "lat": lat, "lon": lon, "zone": p.get("zone", "")}
    print(f"  {len(stations)} stations ({skipped_no_geo} skipped — no coordinates)")

    print("Loading train metadata...")
    trains_geo = json.loads(trains_path.read_text(encoding="utf-8"))
    train_meta: dict[str, dict] = {f["properties"]["number"]: f["properties"] for f in trains_geo["features"]}
    print(f"  {len(train_meta)} trains")

    print("Loading schedules (this is the big one, ~78 MB)...")
    schedules = json.loads(schedules_path.read_text(encoding="utf-8"))
    print(f"  {len(schedules)} schedule rows")

    print("Grouping schedule rows by train...")
    by_train: dict[str, list[dict]] = {}
    for row in schedules:
        by_train.setdefault(row["train_number"], []).append(row)
    del schedules

    print("Building route timelines...")
    out_trains = []
    skipped_type = skipped_short = skipped_no_meta = 0
    for number, rows in by_train.items():
        meta = train_meta.get(number)
        if not meta:
            skipped_no_meta += 1
            continue
        ttype = (meta.get("type") or "").strip()
        if ttype not in TYPE_LABELS:
            skipped_type += 1
            continue

        def sort_key(r):
            t = _minutes(r.get("departure"))
            if t is None:
                t = _minutes(r.get("arrival")) or 0
            day = r.get("day") or 1
            return (day, t)

        rows_sorted = sorted(rows, key=sort_key)
        route = []
        cum_dist = 0.0
        prev = None
        for r in rows_sorted:
            code = r.get("station_code")
            st = stations.get(code)
            if not st:
                continue
            if prev:
                cum_dist += _haversine_km(prev[0], prev[1], st["lat"], st["lon"])
            prev = (st["lat"], st["lon"])
            route.append({
                "code": code, "name": st["name"], "day": r.get("day") or 1,
                "arr": _clock(r.get("arrival")), "dep": _clock(r.get("departure")),
                "dist": round(cum_dist),
            })
        if len(route) < 2:
            skipped_short += 1
            continue

        out_trains.append({
            "number": number,
            "name": (meta.get("name") or "").title(),
            "type": TYPE_LABELS.get(ttype, "Express"),
            "zone": meta.get("zone", ""),
            "runs_on": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "route": route,
        })

    print(f"  Kept {len(out_trains)} trains "
          f"(skipped {skipped_type} by type, {skipped_short} too-short, {skipped_no_meta} no metadata)")

    (DATA_DIR / "all_trains.json").write_text(
        json.dumps(out_trains, ensure_ascii=False), encoding="utf-8")
    (DATA_DIR / "all_stations.json").write_text(
        json.dumps(stations, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {DATA_DIR / 'all_trains.json'}")
    print(f"Wrote {DATA_DIR / 'all_stations.json'}")


if __name__ == "__main__":
    main()
