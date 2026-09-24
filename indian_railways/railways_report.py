"""
Indian Railways — HTML Dashboard Generator
============================================
Builds a self-contained dashboard with a search box: type a train number
(e.g. "12951") or name (e.g. "Rajdhani") to instantly filter matching
trains and see their simulated live tracking status.

Only a small curated set of trains is embedded directly in the page (fast,
works offline). The full database (~2,400 trains merged in from an open
dataset) is searched live via the Flask API (/api/trains/search,
/api/trains/route) when the page is served by app.py; opened as a plain
file it falls back to searching only the embedded curated set.
"""

from __future__ import annotations

import json

from indian_railways.train_data import ALL_STATION_NAMES, STATION_ALIASES, STATION_COORDS


def build_html(payload: dict) -> str:
    generated_at  = payload.get("generated_at", "")
    date_label    = payload.get("date", "")
    total_trains  = payload.get("total_trains", 0)
    running_now   = payload.get("running_now", 0)
    trains        = payload.get("trains", [])
    station_names_json = json.dumps(ALL_STATION_NAMES, ensure_ascii=False)
    station_aliases_json = json.dumps({k: sorted(v) for k, v in STATION_ALIASES.items()}, ensure_ascii=False)

    # Code -> {name, lat, lon} for "Find trains near me" (nearest-station lookup
    # from the rider's own device location, matched client-side).
    station_info: dict[str, dict] = {}
    for entry in ALL_STATION_NAMES:
        code, name = entry.split(" \u2014 ", 1)
        coords = STATION_COORDS.get(code)
        if coords:
            station_info[code] = {"name": name, "lat": coords[0], "lon": coords[1]}
    station_info_json = json.dumps(station_info, ensure_ascii=False)

    trains_json = json.dumps(trains, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Indian Railways Train Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root {{
    --bg: #070c1b; --surface: #0d1528; --card: #111e35; --card-h: #172543;
    --accent: #38bdf8; --accent-glow: rgba(56,189,248,.18);
    --ok: #22c55e; --warn: #f59e0b; --bad: #ef4444; --muted2: #64748b;
    --text: #e8edf5; --muted: #7b8899; --border: #1a2a45;
    --radius: 14px; --shadow: 0 8px 32px rgba(0,0,0,.5);
  }}
  body.light {{
    --bg: #eef2ff; --surface: #ffffff; --card: #ffffff; --card-h: #f4f6ff;
    --accent: #0284c7; --accent-glow: rgba(2,132,199,.1);
    --text: #0f172a; --muted: #64748b; --border: #dde3f0;
    --shadow: 0 4px 20px rgba(0,0,0,.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text); min-height: 100vh;
    transition: background .3s, color .3s;
  }}
  .tricolor {{
    height: 4px; position: sticky; top: 0; z-index: 200;
    background: linear-gradient(90deg, #f97316 0% 33.3%, #e2e8f0 33.3% 66.6%, #22c55e 66.6% 100%);
  }}
  header {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 12px 24px; display: flex; align-items: center;
    justify-content: space-between; gap: 12px; flex-wrap: wrap;
    position: sticky; top: 4px; z-index: 100; box-shadow: var(--shadow);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .brand-icon {{
    width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; box-shadow: 0 4px 12px rgba(14,165,233,.35);
  }}
  .brand-text h1 {{ font-size: 1.1rem; font-weight: 800; letter-spacing: -.025em; }}
  .brand-text p {{ font-size: .7rem; color: var(--muted); margin-top: 1px; }}
  .header-stats {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .stat-chip {{
    background: var(--card); border: 1px solid var(--border); border-radius: 999px;
    padding: 4px 12px; font-size: .74rem; color: var(--muted);
    display: inline-flex; align-items: center; gap: 5px;
  }}
  .stat-chip b {{ color: var(--text); font-weight: 600; }}
  .header-right {{ display: flex; align-items: center; gap: 8px; }}
  .search-wrap {{ position: relative; display: flex; align-items: center; }}
  .search-wrap svg {{
    position: absolute; left: 10px; width: 14px; height: 14px;
    color: var(--muted); pointer-events: none; flex-shrink: 0;
  }}
  #search {{
    padding: 7px 12px 7px 32px; border-radius: 10px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text); font-size: .85rem; width: 260px;
    outline: none; transition: border .2s, box-shadow .2s; font-family: inherit;
  }}
  #search:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }}
  #theme-btn {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); padding: 7px 12px; cursor: pointer; font-size: .8rem;
    transition: background .2s; white-space: nowrap; font-family: inherit;
  }}
  #theme-btn:hover {{ background: var(--card-h); }}
  .route-search-bar {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 10px 24px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    position: sticky; top: 66px; z-index: 90;
  }}
  .rs-field {{ display: flex; align-items: center; gap: 6px; }}
  .rs-field label {{ font-size: .74rem; color: var(--muted); font-weight: 600; }}
  .rs-field input {{
    padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text); font-size: .82rem; width: 180px;
    outline: none; transition: border .2s, box-shadow .2s; font-family: inherit;
  }}
  .rs-field input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }}
  #route-search-btn, #route-clear-btn {{
    border-radius: 8px; padding: 6px 14px; font-size: .8rem; cursor: pointer;
    font-family: inherit; border: 1px solid var(--border); background: var(--card); color: var(--text);
  }}
  #route-search-btn {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}
  #route-clear-btn:hover, #route-search-btn:hover {{ opacity: .85; }}
  #near-me-btn {{
    border-radius: 8px; padding: 6px 14px; font-size: .8rem; cursor: pointer;
    font-family: inherit; border: 1px solid var(--border); background: var(--card); color: var(--text);
  }}
  #near-me-btn:hover {{ border-color: var(--accent); }}
  .near-me-note {{
    padding: 6px 24px; font-size: .78rem; color: var(--muted); background: var(--surface);
    border-bottom: 1px solid var(--border);
  }}
  main {{ padding: 24px; max-width: 1280px; margin: 0 auto; }}
  .cards-note {{ font-size: .78rem; color: var(--muted); margin-bottom: 14px; }}
  .cards {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 16px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-left: 4px solid var(--cc, #38bdf8); border-radius: var(--radius);
    padding: 16px 18px; display: flex; flex-direction: column; gap: 10px;
    cursor: pointer; transition: transform .2s, box-shadow .2s;
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0,0,0,.35), 0 0 0 1px var(--cc, #38bdf8);
  }}
  .card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .train-no {{
    font-family: 'SFMono-Regular', Consolas, monospace; font-size: .78rem;
    color: var(--muted); font-weight: 600;
  }}
  .type-badge {{
    padding: 3px 10px; border-radius: 999px; font-size: .64rem; font-weight: 700;
    color: #fff; background: var(--cc, #38bdf8); letter-spacing: .02em; flex-shrink: 0;
  }}
  .train-name {{ font-size: .95rem; font-weight: 700; line-height: 1.35; }}
  .route-line {{ font-size: .78rem; color: var(--muted); display: flex; align-items: center; gap: 6px; }}
  .route-line b {{ color: var(--text); font-weight: 600; }}
  .status-label {{ font-size: .8rem; font-weight: 600; }}
  .status-running {{ color: var(--ok); }}
  .status-at_station {{ color: var(--accent); }}
  .status-arrived {{ color: var(--muted2); }}
  .status-not_running {{ color: var(--muted2); }}
  .status-delayed {{ color: var(--warn); }}
  .progress-track {{
    height: 6px; border-radius: 999px; background: var(--border); overflow: hidden;
  }}
  .progress-fill {{ height: 100%; background: var(--cc, #38bdf8); border-radius: 999px; transition: width .4s; }}
  .journey-banner {{
    background: var(--accent-glow); border: 1px solid var(--accent); border-radius: 8px;
    padding: 6px 10px; font-size: .74rem; color: var(--text); line-height: 1.5;
  }}
  .route-note {{
    background: rgba(245,158,11,.12); border: 1px solid var(--warn); border-radius: 8px;
    padding: 6px 10px; font-size: .7rem; color: var(--muted); line-height: 1.5;
  }}
  .card-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .map-btn, .fare-btn, .story-btn, .weather-btn {{
    align-self: flex-start; background: var(--card-h); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text); padding: 5px 10px; font-size: .72rem;
    cursor: pointer; font-family: inherit; transition: background .2s, border-color .2s;
  }}
  .map-btn:hover, .fare-btn:hover, .story-btn:hover, .weather-btn:hover {{ border-color: var(--accent); }}
  .route-map {{
    height: 220px; border-radius: 10px; border: 1px solid var(--border); overflow: hidden;
  }}
  .fare-box {{
    border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; font-size: .72rem;
    color: var(--muted); line-height: 1.6;
  }}
  .fare-box b {{ color: var(--text); }}
  .fare-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px 12px; margin-top: 4px; }}
  .fare-disclaimer {{ margin-top: 6px; font-style: italic; opacity: .8; }}
  .eco-row {{ margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--border); }}
  .story-box {{
    border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; font-size: .78rem;
    color: var(--text); line-height: 1.6; display: flex; gap: 10px;
  }}
  .story-box img {{ width: 84px; height: 84px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }}
  .story-box .story-muted {{ color: var(--muted); font-size: .72rem; }}
  .story-box a {{ color: var(--accent); }}
  .weather-box {{
    border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; font-size: .72rem;
    color: var(--muted); line-height: 1.6;
  }}
  .weather-box b {{ color: var(--text); }}
  .weather-icon {{ font-size: 1.05rem; margin-right: 2px; }}
  .runs-badge {{
    align-self: flex-start; display: inline-block; font-size: .68rem; color: var(--muted);
    background: var(--card-h); border: 1px solid var(--border); border-radius: 999px; padding: 2px 9px;
  }}
  .route-note-btn {{
    align-self: flex-start; background: rgba(245,158,11,.12); border: 1px solid var(--warn);
    border-radius: 999px; color: var(--muted); padding: 3px 10px; font-size: .68rem;
    cursor: pointer; font-family: inherit;
  }}
  .compare-btn {{
    align-self: flex-start; background: var(--card-h); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text); padding: 5px 10px; font-size: .72rem;
    cursor: pointer; font-family: inherit; transition: background .2s, border-color .2s;
  }}
  .compare-btn:hover {{ border-color: var(--accent); }}
  .compare-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .compare-bar {{
    display: none; position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: var(--card); border: 1px solid var(--border); border-radius: 999px;
    box-shadow: var(--shadow); padding: 10px 18px; gap: 12px; align-items: center;
    z-index: 300; font-size: .82rem; color: var(--text);
  }}
  .compare-bar button {{
    background: var(--accent); color: #fff; border: none; border-radius: 999px;
    padding: 6px 14px; font-size: .78rem; cursor: pointer; font-family: inherit;
  }}
  .compare-bar button:last-child {{ background: var(--card-h); color: var(--text); border: 1px solid var(--border); }}
  .compare-overlay {{
    position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 400;
    display: flex; align-items: center; justify-content: center; padding: 20px;
  }}
  .compare-modal {{
    background: var(--surface); border-radius: var(--radius); max-width: 700px; width: 100%;
    max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow);
  }}
  .compare-modal-head {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 14px 16px; border-bottom: 1px solid var(--border); color: var(--text);
    position: sticky; top: 0; background: var(--surface);
  }}
  .compare-modal-head button {{
    background: none; border: none; color: var(--muted); font-size: 1rem; cursor: pointer;
  }}
  .compare-table {{ width: 100%; border-collapse: collapse; font-size: .78rem; color: var(--text); }}
  .compare-table td, .compare-table th {{
    padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top;
  }}
  .compare-table td:first-child {{ color: var(--muted); font-weight: 600; white-space: nowrap; }}
  #lang-select, #sort-select {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); padding: 6px 10px; font-size: .8rem; font-family: inherit; cursor: pointer;
  }}
  .stops-detail {{
    margin-top: 6px; border-top: 1px dashed var(--border); padding-top: 10px;
    max-height: 220px; overflow-y: auto;
  }}
  .stop-row {{
    display: flex; justify-content: space-between; font-size: .72rem;
    color: var(--muted); padding: 3px 0;
  }}
  .stop-row.current {{ color: var(--accent); font-weight: 700; }}
  .stop-row b {{ color: var(--text); }}
  .gps-btn {{
    align-self: flex-start; background: var(--card-h); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text); padding: 5px 10px; font-size: .72rem;
    cursor: pointer; font-family: inherit; transition: background .2s, border-color .2s;
  }}
  .gps-btn:hover {{ border-color: var(--accent); }}
  .gps-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .gps-result {{ font-size: .72rem; color: var(--accent); line-height: 1.5; }}
  .no-results {{
    grid-column: 1/-1; text-align: center; padding: 56px 24px; color: var(--muted); font-size: .9rem;
  }}
  .no-results-icon {{ font-size: 2.5rem; margin-bottom: 10px; opacity: .4; }}
  footer {{
    text-align: center; padding: 28px 24px; font-size: .74rem; color: var(--muted);
    border-top: 1px solid var(--border); margin-top: 16px; line-height: 1.8;
  }}
  @media (max-width: 768px) {{ .header-stats {{ display: none; }} main {{ padding: 14px; }} .cards {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 500px) {{ header {{ padding: 10px 14px; }} .brand-text p {{ display: none; }} #search {{ width: 160px; }} }}
</style>
</head>
<body>

<div class="tricolor"></div>

<header>
  <div class="brand">
    <div class="brand-icon">&#128646;</div>
    <div class="brand-text">
      <h1 data-i18n="brand_title">Indian Railways Train Tracker</h1>
      <p data-i18n="brand_sub">Search by train number/name, or find trains between two stations</p>
    </div>
  </div>
  <div class="header-stats">
    <div class="stat-chip">&#128197; <b>{date_label}</b></div>
    <div class="stat-chip">&#128646; <b>{total_trains}</b> trains in database</div>
    <div class="stat-chip">&#128504; <b id="running-now">{running_now}</b> en route</div>
    <div class="stat-chip">&#128336; Updated: <b>{generated_at}</b></div>
  </div>
  <div class="header-right">
    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" id="search" data-i18n-placeholder="search_placeholder" placeholder="Train number or name…"
             oninput="onSearchInput(this.value)" autocomplete="off"/>
    </div>
    <select id="lang-select" onchange="applyLanguage(this.value)" data-i18n-title="language_label" title="Language">
      <option value="en">English</option>
      <option value="hi">हिन्दी</option>
      <option value="ta">தமிழ்</option>
      <option value="te">తెలుగు</option>
      <option value="kn">ಕನ್ನಡ</option>
      <option value="bn">বাংলা</option>
      <option value="ml">മലയാളം</option>
    </select>
    <button id="theme-btn" onclick="toggleTheme()">&#9728; Light</button>
  </div>
</header>

<div class="route-search-bar">
  <div class="rs-field">
    <label for="from-station" data-i18n="from_label">From</label>
    <input type="text" id="from-station" list="station-list" data-i18n-placeholder="from_placeholder" placeholder="Source station" autocomplete="off"/>
  </div>
  <div class="rs-field">
    <label for="to-station" data-i18n="to_label">To</label>
    <input type="text" id="to-station" list="station-list" data-i18n-placeholder="to_placeholder" placeholder="Destination station" autocomplete="off"/>
  </div>
  <datalist id="station-list"></datalist>
  <button id="route-search-btn" onclick="applyRouteSearch()">&#128269; <span data-i18n="btn_search">Search</span></button>
  <button id="route-clear-btn" onclick="clearRouteSearch()">&#10005; <span data-i18n="btn_clear">Clear</span></button>
  <select id="sort-select" onchange="renderCards(document.getElementById('search').value)">
    <option value="default" data-i18n="sort_default">Sort: Default</option>
    <option value="departure" data-i18n="sort_departure">Sort: Earliest departure</option>
    <option value="duration" data-i18n="sort_duration">Sort: Fastest (shortest duration)</option>
    <option value="stops" data-i18n="sort_stops">Sort: Fewest stops</option>
  </select>
  <button id="near-me-btn" onclick="findTrainsNearMe()" data-i18n="near_me_btn">&#128205; Find Trains Near Me</button>
</div>
<div class="near-me-note" id="near-me-note" style="display:none"></div>

<main>
  <div class="cards-note" id="cards-note">Showing {len(trains)} popular trains &mdash; type a train number/name above, or use From/To, to search the full database of {total_trains} trains.</div>
  <div class="cards" id="cards"></div>
</main>

<footer>
  Indian Railways Train Tracker &mdash; demo dashboard<br/>
  <span style="opacity:.65" data-i18n="footer_disclaimer">Status is SIMULATED from public schedules (not an official live GPS feed). For official real-time status use NTES / IRCTC.<br/>
  "Use My GPS" reads your device's own location in your browser only (never sent to a server) to show which stop you're nearest &mdash; useful only if you're actually riding that train.</span><br/>
  <span style="opacity:.65">Built by Naveen Alla</span>
</footer>

<script>
const CURATED_TRAINS = {trains_json};
const ALL_STATION_NAMES = {station_names_json};
const STATION_ALIASES = {station_aliases_json};
const STATION_INFO = {station_info_json};
let TRAINS = CURATED_TRAINS.slice();

// ── i18n ─────────────────────────────────────────────────────────────────
// Translates the static UI chrome only (labels, buttons, disclaimers) — not
// train names or simulated status text, which come from the (English-only)
// source schedule data and aren't feasible to translate without a full
// dataset translation.
const I18N = {{
  en: {{
    brand_title: 'Indian Railways Train Tracker',
    brand_sub: 'Search by train number/name, or find trains between two stations',
    search_placeholder: 'Train number or name…',
    from_label: 'From', to_label: 'To',
    from_placeholder: 'Source station', to_placeholder: 'Destination station',
    btn_search: 'Search', btn_clear: 'Clear',
    sort_default: 'Sort: Default', sort_departure: 'Sort: Earliest departure',
    sort_duration: 'Sort: Fastest (shortest duration)', sort_stops: 'Sort: Fewest stops',
    theme_light: '☀ Light', theme_dark: '🌙 Dark',
    gps_start: "📍 Use My GPS (I'm on this train)", gps_stop: '⏹ Stop GPS Tracking',
    map_show: '🗺️ View Route Map', map_hide: '🗺️ Hide Route Map',
    fare_show: '💰 Estimate Fare', fare_hide: '💰 Hide Fare Estimate',
    story_show: '📰 Train Story', story_hide: '📰 Hide Train Story',
    story_loading: 'Loading train history…', story_not_found: 'No published history found for this train.',
    story_source: 'Source: Wikipedia',
    story_learn_more: '🔎 Search more on Wikipedia',
    compare_add: '➕ Compare', compare_added: '✓ Comparing', compare_max: 'You can compare up to 3 trains at a time.',
    compare_selected: 'selected', compare_view: 'View Comparison', compare_clear: 'Clear', compare_title: 'Compare Trains',
    compare_type: 'Type', compare_route: 'Route', compare_distance: 'Distance', compare_duration: 'Duration',
    compare_stops: 'Stops', compare_status: 'Status', compare_fare: 'Fare (approx.)',
    near_me_btn: '📍 Find Trains Near Me', near_me_locating: 'Finding your location…', near_me_result: 'Nearest station:', near_me_error: 'Could not determine your location.',
    runs_label: 'Runs:', runs_daily: 'Runs daily',
    weather_show: '🌦️ Destination Weather', weather_hide: '🌦️ Hide Destination Weather',
    weather_loading: 'Loading weather…', weather_error: 'Could not load weather for this station.',
    weather_source: 'Source: Open-Meteo (free, no API key)',
    route_note_show: 'ℹ️ Route simplified — tap for details', route_note_hide: 'ℹ️ Hide details',
    footer_disclaimer: 'Status is SIMULATED from public schedules (not an official live GPS feed). For official real-time status use NTES / IRCTC.<br/>"Use My GPS" reads your device\\'s own location in your browser only (never sent to a server) to show which stop you\\'re nearest — useful only if you\\'re actually riding that train.',
  }},
  hi: {{
    brand_title: 'भारतीय रेल ट्रेन ट्रैकर',
    brand_sub: 'ट्रेन नंबर/नाम से खोजें, या दो स्टेशनों के बीच ट्रेनें ढूंढें',
    search_placeholder: 'ट्रेन नंबर या नाम…',
    from_label: 'से', to_label: 'तक',
    from_placeholder: 'स्रोत स्टेशन', to_placeholder: 'गंतव्य स्टेशन',
    btn_search: 'खोजें', btn_clear: 'साफ़ करें',
    sort_default: 'क्रम: डिफ़ॉल्ट', sort_departure: 'क्रम: सबसे पहले प्रस्थान',
    sort_duration: 'क्रम: सबसे तेज़ (कम समय)', sort_stops: 'क्रम: सबसे कम पड़ाव',
    theme_light: '☀ लाइट', theme_dark: '🌙 डार्क',
    gps_start: '📍 मेरा GPS उपयोग करें (मैं इस ट्रेन में हूँ)', gps_stop: '⏹ GPS ट्रैकिंग बंद करें',
    map_show: '🗺️ मार्ग मानचित्र देखें', map_hide: '🗺️ मार्ग मानचित्र छुपाएँ',
    fare_show: '💰 किराया अनुमान', fare_hide: '💰 किराया अनुमान छुपाएँ',
    story_show: '📰 ट्रेन की कहानी', story_hide: '📰 ट्रेन की कहानी छुपाएँ',
    story_loading: 'ट्रेन का इतिहास लोड हो रहा है…', story_not_found: 'इस ट्रेन के लिए कोई प्रकाशित इतिहास नहीं मिला।',
    story_source: 'स्रोत: विकिपीडिया',
    story_learn_more: '🔎 विकिपीडिया पर और खोजें',
    compare_add: '➕ तुलना करें', compare_added: '✓ तुलना में', compare_max: 'आप एक बार में अधिकतम 3 ट्रेनों की तुलना कर सकते हैं।',
    compare_selected: 'चयनित', compare_view: 'तुलना देखें', compare_clear: 'साफ़ करें', compare_title: 'ट्रेनों की तुलना करें',
    compare_type: 'प्रकार', compare_route: 'मार्ग', compare_distance: 'दूरी', compare_duration: 'अवधि',
    compare_stops: 'पड़ाव', compare_status: 'स्थिति', compare_fare: 'किराया (लगभग)',
    near_me_btn: '📍 मेरे पास ट्रेनें खोजें', near_me_locating: 'आपका स्थान ढूंढा जा रहा है…', near_me_result: 'निकटतम स्टेशन:', near_me_error: 'आपका स्थान निर्धारित नहीं किया जा सका।',
    runs_label: 'चलती है:', runs_daily: 'प्रतिदिन चलती है',
    weather_show: '🌦️ गंतव्य मौसम', weather_hide: '🌦️ गंतव्य मौसम छुपाएँ',
    weather_loading: 'मौसम लोड हो रहा है…', weather_error: 'इस स्टेशन के लिए मौसम लोड नहीं हो सका।',
    weather_source: 'स्रोत: Open-Meteo (निःशुल्क, बिना API कुंजी)',
    route_note_show: 'ℹ️ मार्ग सरल किया गया — विवरण के लिए टैप करें', route_note_hide: 'ℹ️ विवरण छुपाएँ',
    footer_disclaimer: 'स्थिति सार्वजनिक समय-सारणी से अनुकरण (SIMULATED) की गई है (आधिकारिक लाइव GPS फ़ीड नहीं)। आधिकारिक वास्तविक-समय स्थिति के लिए NTES / IRCTC का उपयोग करें।<br/>"मेरा GPS उपयोग करें" केवल आपके ब्राउज़र में आपके डिवाइस का स्थान पढ़ता है (कभी सर्वर पर नहीं भेजा जाता) ताकि यह दिखाया जा सके कि आप किस स्टेशन के सबसे नज़दीक हैं — यह तभी उपयोगी है जब आप वास्तव में उस ट्रेन में यात्रा कर रहे हों।',
  }},
  ta: {{
    brand_title: 'இந்திய ரயில்வே ரயில் டிராக்கர்',
    brand_sub: 'ரயில் எண்/பெயர் மூலம் தேடுங்கள், அல்லது இரு நிலையங்களுக்கு இடையே ரயில்களை கண்டறியுங்கள்',
    search_placeholder: 'ரயில் எண் அல்லது பெயர்…',
    from_label: 'இருந்து', to_label: 'வரை',
    from_placeholder: 'புறப்படும் நிலையம்', to_placeholder: 'சேரும் நிலையம்',
    btn_search: 'தேடு', btn_clear: 'அழி',
    sort_default: 'வரிசை: இயல்பு', sort_departure: 'வரிசை: முந்திய புறப்பாடு',
    sort_duration: 'வரிசை: வேகமான (குறைந்த நேரம்)', sort_stops: 'வரிசை: குறைந்த நிறுத்தங்கள்',
    theme_light: '☀ லைட்', theme_dark: '🌙 டார்க்',
    gps_start: '📍 எனது GPS-ஐ பயன்படுத்து (நான் இந்த ரயிலில் இருக்கிறேன்)', gps_stop: '⏹ GPS கண்காணிப்பை நிறுத்து',
    map_show: '🗺️ பாதை வரைபடத்தை காட்டு', map_hide: '🗺️ பாதை வரைபடத்தை மறை',
    fare_show: '💰 கட்டண மதிப்பீடு', fare_hide: '💰 கட்டண மதிப்பீட்டை மறை',
    story_show: '📰 ரயில் கதை', story_hide: '📰 ரயில் கதையை மறை',
    story_loading: 'ரயில் வரலாறு ஏற்றப்படுகிறது…', story_not_found: 'இந்த ரயிலுக்கு வெளியிடப்பட்ட வரலாறு எதுவும் இல்லை.',
    story_source: 'மூலம்: விக்கிபீடியா',
    story_learn_more: '🔎 விக்கிபீடியாவில் மேலும் தேடு',
    compare_add: '➕ ஒப்பிடு', compare_added: '✓ ஒப்பிடப்படுகிறது', compare_max: 'ஒரே நேரத்தில் அதிகபட்சம் 3 ரயில்களை ஒப்பிடலாம்.',
    compare_selected: 'தேர்ந்தெடுக்கப்பட்டது', compare_view: 'ஒப்பீட்டைக் காண்க', compare_clear: 'அழி', compare_title: 'ரயில்களை ஒப்பிடு',
    compare_type: 'வகை', compare_route: 'பாதை', compare_distance: 'தூரம்', compare_duration: 'கால அளவு',
    compare_stops: 'நிறுத்தங்கள்', compare_status: 'நிலை', compare_fare: 'கட்டணம் (தோராயமாக)',
    near_me_btn: '📍 அருகிலுள்ள ரயில்களைக் கண்டறியவும்', near_me_locating: 'உங்கள் இருப்பிடத்தைக் கண்டறிகிறது…', near_me_result: 'அருகிலுள்ள நிலையம்:', near_me_error: 'உங்கள் இருப்பிடத்தைக் கண்டறிய முடியவில்லை.',
    runs_label: 'இயக்கம்:', runs_daily: 'தினமும் இயக்கப்படுகிறது',
    weather_show: '🌦️ சேரும் இட வானிலை', weather_hide: '🌦️ சேரும் இட வானிலையை மறை',
    weather_loading: 'வானிலை ஏற்றப்படுகிறது…', weather_error: 'இந்த நிலையத்திற்கான வானிலையை ஏற்ற முடியவில்லை.',
    weather_source: 'மூலம்: Open-Meteo (இலவசம், API கீ தேவையில்லை)',
    route_note_show: 'ℹ️ பாதை எளிமையாக்கப்பட்டது — விவரங்களுக்கு தட்டவும்', route_note_hide: 'ℹ️ விவரங்களை மறை',
    footer_disclaimer: 'நிலை பொது கால அட்டவணையிலிருந்து உருவகப்படுத்தப்பட்டது (SIMULATED) (அதிகாரப்பூர்வ நேரடி GPS ஃபீட் அல்ல). அதிகாரப்பூர்வ நேரடி நிலைக்கு NTES / IRCTC-ஐ பயன்படுத்தவும்.<br/>"எனது GPS-ஐ பயன்படுத்து" உங்கள் சாதனத்தின் இருப்பிடத்தை உங்கள் உலாவியில் மட்டுமே படிக்கிறது (சேவையகத்திற்கு அனுப்பப்படாது) — நீங்கள் உண்மையில் அந்த ரயிலில் பயணிக்கும்போது மட்டுமே பயனுள்ளது.',
  }},
  te: {{
    brand_title: 'ఇండియన్ రైల్వేస్ ట్రైన్ ట్రాకర్',
    brand_sub: 'రైలు నంబర్/పేరు ద్వారా వెతకండి, లేదా రెండు స్టేషన్ల మధ్య రైళ్లను కనుగొనండి',
    search_placeholder: 'రైలు నంబర్ లేదా పేరు…',
    from_label: 'నుండి', to_label: 'వరకు',
    from_placeholder: 'మూల స్టేషన్', to_placeholder: 'గమ్య స్టేషన్',
    btn_search: 'వెతకండి', btn_clear: 'తొలగించు',
    sort_default: 'క్రమం: డిఫాల్ట్', sort_departure: 'క్రమం: ముందుగా బయలుదేరేది',
    sort_duration: 'క్రమం: వేగవంతమైనది (తక్కువ సమయం)', sort_stops: 'క్రమం: తక్కువ ఆగే స్టేషన్లు',
    theme_light: '☀ లైట్', theme_dark: '🌙 డార్క్',
    gps_start: '📍 నా GPS ఉపయోగించండి (నేను ఈ రైలులో ఉన్నాను)', gps_stop: '⏹ GPS ట్రాకింగ్ ఆపండి',
    map_show: '🗺️ మార్గం మ్యాప్ చూడండి', map_hide: '🗺️ మార్గం మ్యాప్ దాచండి',
    fare_show: '💰 చార్జీ అంచనా', fare_hide: '💰 చార్జీ అంచనా దాచండి',
    story_show: '📰 రైలు కథ', story_hide: '📰 రైలు కథను దాచండి',
    story_loading: 'రైలు చరిత్ర లోడ్ అవుతోంది…', story_not_found: 'ఈ రైలుకు ప్రచురించిన చరిత్ర కనుగొనబడలేదు.',
    story_source: 'మూలం: వికీపీడియా',
    story_learn_more: '🔎 వికీపీడియాలో ఇంకా వెతకండి',
    compare_add: '➕ పోల్చండి', compare_added: '✓ పోల్చబడుతోంది', compare_max: 'మీరు ఒకేసారి గరిష్టంగా 3 రైళ్లను పోల్చవచ్చు.',
    compare_selected: 'ఎంపిక చేయబడింది', compare_view: 'పోలికను చూడండి', compare_clear: 'తొలగించు', compare_title: 'రైళ్లను పోల్చండి',
    compare_type: 'రకం', compare_route: 'మార్గం', compare_distance: 'దూరం', compare_duration: 'వ్యవధి',
    compare_stops: 'ఆగే స్టేషన్లు', compare_status: 'స్థితి', compare_fare: 'చార్జీ (సుమారు)',
    near_me_btn: '📍 నా దగ్గర రైళ్లను కనుగొనండి', near_me_locating: 'మీ స్థానాన్ని కనుగొంటోంది…', near_me_result: 'సమీప స్టేషన్:', near_me_error: 'మీ స్థానాన్ని గుర్తించలేకపోయాము.',
    runs_label: 'నడుస్తుంది:', runs_daily: 'ప్రతిరోజూ నడుస్తుంది',
    weather_show: '🌦️ గమ్యస్థాన వాతావరణం', weather_hide: '🌦️ గమ్యస్థాన వాతావరణం దాచండి',
    weather_loading: 'వాతావరణం లోడ్ అవుతోంది…', weather_error: 'ఈ స్టేషన్ కోసం వాతావరణం లోడ్ చేయలేకపోయాము.',
    weather_source: 'మూలం: Open-Meteo (ఉచితం, API కీ అవసరం లేదు)',
    route_note_show: 'ℹ️ మార్గం సరళీకరించబడింది — వివరాల కోసం నొక్కండి', route_note_hide: 'ℹ️ వివరాలు దాచండి',
    footer_disclaimer: 'స్థితి బహిరంగ టైమ్‌టేబుల్ నుండి అనుకరించబడింది (SIMULATED) (అధికారిక లైవ్ GPS ఫీడ్ కాదు). అధికారిక రియల్-టైమ్ స్థితి కోసం NTES / IRCTC ఉపయోగించండి.<br/>"నా GPS ఉపయోగించండి" మీ పరికర స్థానాన్ని మీ బ్రౌజర్‌లో మాత్రమే చదువుతుంది (సర్వర్‌కు పంపబడదు) — మీరు నిజంగా ఆ రైలులో ప్రయాణిస్తున్నప్పుడు మాత్రమే ఉపయోగకరం.',
  }},
  kn: {{
    brand_title: 'ಭಾರತೀಯ ರೈಲ್ವೆ ರೈಲು ಟ್ರ್ಯಾಕರ್',
    brand_sub: 'ರೈಲು ಸಂಖ್ಯೆ/ಹೆಸರಿನ ಮೂಲಕ ಹುಡುಕಿ, ಅಥವಾ ಎರಡು ನಿಲ್ದಾಣಗಳ ನಡುವಿನ ರೈಲುಗಳನ್ನು ಹುಡುಕಿ',
    search_placeholder: 'ರೈಲು ಸಂಖ್ಯೆ ಅಥವಾ ಹೆಸರು…',
    from_label: 'ಇಂದ', to_label: 'ಗೆ',
    from_placeholder: 'ಮೂಲ ನಿಲ್ದಾಣ', to_placeholder: 'ಗಮ್ಯ ನಿಲ್ದಾಣ',
    btn_search: 'ಹುಡುಕಿ', btn_clear: 'ಅಳಿಸಿ',
    sort_default: 'ಕ್ರಮ: ಡೀಫಾಲ್ಟ್', sort_departure: 'ಕ್ರಮ: ಮೊದಲ ನಿರ್ಗಮನ',
    sort_duration: 'ಕ್ರಮ: ವೇಗದ (ಕಡಿಮೆ ಸಮಯ)', sort_stops: 'ಕ್ರಮ: ಕಡಿಮೆ ನಿಲುಗಡೆಗಳು',
    theme_light: '☀ ಲೈಟ್', theme_dark: '🌙 ಡಾರ್ಕ್',
    gps_start: '📍 ನನ್ನ GPS ಬಳಸಿ (ನಾನು ಈ ರೈಲಿನಲ್ಲಿದ್ದೇನೆ)', gps_stop: '⏹ GPS ಟ್ರ್ಯಾಕಿಂಗ್ ನಿಲ್ಲಿಸಿ',
    map_show: '🗺️ ಮಾರ್ಗ ನಕ್ಷೆ ನೋಡಿ', map_hide: '🗺️ ಮಾರ್ಗ ನಕ್ಷೆ ಮರೆಮಾಡಿ',
    fare_show: '💰 ದರ ಅಂದಾಜು', fare_hide: '💰 ದರ ಅಂದಾಜು ಮರೆಮಾಡಿ',
    story_show: '📰 ರೈಲು ಕಥೆ', story_hide: '📰 ರೈಲು ಕಥೆ ಮರೆಮಾಡಿ',
    story_loading: 'ರೈಲಿನ ಇತಿಹಾಸ ಲೋಡ್ ಆಗುತ್ತಿದೆ…', story_not_found: 'ಈ ರೈಲಿಗೆ ಪ್ರಕಟಿತ ಇತಿಹಾಸ ಕಂಡುಬಂದಿಲ್ಲ.',
    story_source: 'ಮೂಲ: ವಿಕಿಪೀಡಿಯಾ',
    story_learn_more: '🔎 ವಿಕಿಪೀಡಿಯಾದಲ್ಲಿ ಹೆಚ್ಚಿನ ಹುಡುಕಿ',
    compare_add: '➕ ಹೋಲಿಸಿ', compare_added: '✓ ಹೋಲಿಸಲಾಗುತ್ತಿದೆ', compare_max: 'ನೀವು ಒಂದೇ ಬಾರಿಗೆ ಗರಿಷ್ಠ 3 ರೈಲುಗಳನ್ನು ಹೋಲಿಸಬಹುದು.',
    compare_selected: 'ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ', compare_view: 'ಹೋಲಿಕೆ ವೀಕ್ಷಿಸಿ', compare_clear: 'ಅಳಿಸಿ', compare_title: 'ರೈಲುಗಳನ್ನು ಹೋಲಿಸಿ',
    compare_type: 'ಪ್ರಕಾರ', compare_route: 'ಮಾರ್ಗ', compare_distance: 'ದೂರ', compare_duration: 'ಅವಧಿ',
    compare_stops: 'ನಿಲುಗಡೆಗಳು', compare_status: 'ಸ್ಥಿತಿ', compare_fare: 'ದರ (ಅಂದಾಜು)',
    near_me_btn: '📍 ನನ್ನ ಬಳಿ ರೈಲುಗಳನ್ನು ತೋರಿಸಿ', near_me_locating: 'ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ…', near_me_result: 'ಹತ್ತಿರದ ನಿಲ್ದಾಣ:', near_me_error: 'ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ನಿರ್ಧರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.',
    runs_label: 'ಓಡುತ್ತದೆ:', runs_daily: 'ಪ್ರತಿದಿನ ಓಡುತ್ತದೆ',
    weather_show: '🌦️ ಗಮ್ಯಸ್ಥಾನ ಹವಾಮಾನ', weather_hide: '🌦️ ಗಮ್ಯಸ್ಥಾನ ಹವಾಮಾನ ಮರೆಮಾಡಿ',
    weather_loading: 'ಹವಾಮಾನ ಲೋಡ್ ಆಗುತ್ತಿದೆ…', weather_error: 'ಈ ನಿಲ್ದಾಣಕ್ಕೆ ಹವಾಮಾನ ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.',
    weather_source: 'ಮೂಲ: Open-Meteo (ಉಚಿತ, API ಕೀ ಅಗತ್ಯವಿಲ್ಲ)',
    route_note_show: 'ℹ️ ಮಾರ್ಗ ಸರಳೀಕರಿಸಲಾಗಿದೆ — ವಿವರಗಳಿಗಾಗಿ ಟ್ಯಾಪ್ ಮಾಡಿ', route_note_hide: 'ℹ️ ವಿವರಗಳನ್ನು ಮರೆಮಾಡಿ',
    footer_disclaimer: 'ಸ್ಥಿತಿಯನ್ನು ಸಾರ್ವಜನಿಕ ವೇಳಾಪಟ್ಟಿಯಿಂದ ಅನುಕರಿಸಲಾಗಿದೆ (SIMULATED) (ಅಧಿಕೃತ ಲೈವ್ GPS ಫೀಡ್ ಅಲ್ಲ). ಅಧಿಕೃತ ನೈಜ-ಸಮಯದ ಸ್ಥಿತಿಗಾಗಿ NTES / IRCTC ಬಳಸಿ.<br/>"ನನ್ನ GPS ಬಳಸಿ" ನಿಮ್ಮ ಸಾಧನದ ಸ್ಥಳವನ್ನು ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಮಾತ್ರ ಓದುತ್ತದೆ (ಸರ್ವರ್‌ಗೆ ಎಂದಿಗೂ ಕಳುಹಿಸುವುದಿಲ್ಲ) — ನೀವು ನಿಜವಾಗಿಯೂ ಆ ರೈಲಿನಲ್ಲಿ ಪ್ರಯಾಣಿಸುತ್ತಿರುವಾಗ ಮಾತ್ರ ಉಪಯುಕ್ತ.',
  }},
  bn: {{
    brand_title: 'ইন্ডিয়ান রেলওয়ে ট্রেন ট্র্যাকার',
    brand_sub: 'ট্রেন নম্বর/নাম দিয়ে খুঁজুন, অথবা দুটি স্টেশনের মধ্যে ট্রেন খুঁজুন',
    search_placeholder: 'ট্রেন নম্বর বা নাম…',
    from_label: 'থেকে', to_label: 'পর্যন্ত',
    from_placeholder: 'উৎস স্টেশন', to_placeholder: 'গন্তব্য স্টেশন',
    btn_search: 'খুঁজুন', btn_clear: 'পরিষ্কার',
    sort_default: 'সাজান: ডিফল্ট', sort_departure: 'সাজান: প্রথম ছাড়ার সময়',
    sort_duration: 'সাজান: দ্রুততম (কম সময়)', sort_stops: 'সাজান: সবচেয়ে কম স্টপ',
    theme_light: '☀ লাইট', theme_dark: '🌙 ডার্ক',
    gps_start: '📍 আমার GPS ব্যবহার করুন (আমি এই ট্রেনে আছি)', gps_stop: '⏹ GPS ট্র্যাকিং বন্ধ করুন',
    map_show: '🗺️ রুট ম্যাপ দেখুন', map_hide: '🗺️ রুট ম্যাপ লুকান',
    fare_show: '💰 ভাড়া অনুমান', fare_hide: '💰 ভাড়া অনুমান লুকান',
    story_show: '📰 ট্রেনের গল্প', story_hide: '📰 ট্রেনের গল্প লুকান',
    story_loading: 'ট্রেনের ইতিহাস লোড হচ্ছে…', story_not_found: 'এই ট্রেনের জন্য কোনো প্রকাশিত ইতিহাস পাওয়া যায়নি।',
    story_source: 'উৎস: উইকিপিডিয়া',
    story_learn_more: '🔎 উইকিপিডিয়ায় আরও খুঁজুন',
    compare_add: '➕ তুলনা করুন', compare_added: '✓ তুলনায়', compare_max: 'আপনি একবারে সর্বোচ্চ ৩টি ট্রেন তুলনা করতে পারেন।',
    compare_selected: 'নির্বাচিত', compare_view: 'তুলনা দেখুন', compare_clear: 'পরিষ্কার', compare_title: 'ট্রেন তুলনা করুন',
    compare_type: 'ধরন', compare_route: 'রুট', compare_distance: 'দূরত্ব', compare_duration: 'সময়কাল',
    compare_stops: 'স্টপ', compare_status: 'অবস্থা', compare_fare: 'ভাড়া (আনুমানিক)',
    near_me_btn: '📍 আমার কাছের ট্রেন খুঁজুন', near_me_locating: 'আপনার অবস্থান খুঁজছে…', near_me_result: 'নিকটতম স্টেশন:', near_me_error: 'আপনার অবস্থান নির্ধারণ করা যায়নি।',
    runs_label: 'চলে:', runs_daily: 'প্রতিদিন চলে',
    weather_show: '🌦️ গন্তব্যের আবহাওয়া', weather_hide: '🌦️ গন্তব্যের আবহাওয়া লুকান',
    weather_loading: 'আবহাওয়া লোড হচ্ছে…', weather_error: 'এই স্টেশনের জন্য আবহাওয়া লোড করা যায়নি।',
    weather_source: 'উৎস: Open-Meteo (বিনামূল্যে, API কী প্রয়োজন নেই)',
    route_note_show: 'ℹ️ রুট সরলীকৃত — বিস্তারিত জানতে ট্যাপ করুন', route_note_hide: 'ℹ️ বিস্তারিত লুকান',
    footer_disclaimer: 'অবস্থা পাবলিক সময়সূচী থেকে সিমুলেটেড (অফিসিয়াল লাইভ GPS ফিড নয়)। অফিসিয়াল রিয়েল-টাইম অবস্থার জন্য NTES / IRCTC ব্যবহার করুন।<br/>"আমার GPS ব্যবহার করুন" শুধুমাত্র আপনার ব্রাউজারে আপনার ডিভাইসের অবস্থান পড়ে (সার্ভারে পাঠানো হয় না) — শুধুমাত্র আপনি সত্যিই সেই ট্রেনে ভ্রমণ করলে উপযোগী।',
  }},
  ml: {{
    brand_title: 'ഇന്ത്യൻ റെയിൽവേ ട്രെയിൻ ട്രാക്കർ',
    brand_sub: 'ട്രെയിൻ നമ്പർ/പേര് ഉപയോഗിച്ച് തിരയുക, അല്ലെങ്കിൽ രണ്ട് സ്റ്റേഷനുകൾക്കിടയിലുള്ള ട്രെയിനുകൾ കണ്ടെത്തുക',
    search_placeholder: 'ട്രെയിൻ നമ്പർ അല്ലെങ്കിൽ പേര്…',
    from_label: 'നിന്ന്', to_label: 'വരെ',
    from_placeholder: 'പുറപ്പെടുന്ന സ്റ്റേഷൻ', to_placeholder: 'ലക്ഷ്യസ്ഥാന സ്റ്റേഷൻ',
    btn_search: 'തിരയുക', btn_clear: 'മായ്ക്കുക',
    sort_default: 'ക്രമം: സ്ഥിരസ്ഥിതി', sort_departure: 'ക്രമം: ആദ്യം പുറപ്പെടുന്നത്',
    sort_duration: 'ക്രമം: വേഗതയേറിയത് (കുറഞ്ഞ സമയം)', sort_stops: 'ക്രമം: കുറഞ്ഞ സ്റ്റോപ്പുകൾ',
    theme_light: '☀ ലൈറ്റ്', theme_dark: '🌙 ഡാർക്ക്',
    gps_start: '📍 എന്റെ GPS ഉപയോഗിക്കുക (ഞാൻ ഈ ട്രെയിനിലാണ്)', gps_stop: '⏹ GPS ട്രാക്കിംഗ് നിർത്തുക',
    map_show: '🗺️ റൂട്ട് മാപ്പ് കാണുക', map_hide: '🗺️ റൂട്ട് മാപ്പ് മറയ്ക്കുക',
    fare_show: '💰 നിരക്ക് കണക്കാക്കുക', fare_hide: '💰 നിരക്ക് കണക്ക് മറയ്ക്കുക',
    story_show: '📰 ട്രെയിൻ കഥ', story_hide: '📰 ട്രെയിൻ കഥ മറയ്ക്കുക',
    story_loading: 'ട്രെയിൻ ചരിത്രം ലോഡ് ചെയ്യുന്നു…', story_not_found: 'ഈ ട്രെയിനിന് പ്രസിദ്ധീകരിച്ച ചരിത്രം കണ്ടെത്തിയില്ല.',
    story_source: 'ഉറവിടം: വിക്കിപീഡിയ',
    story_learn_more: '🔎 വിക്കിപീഡിയയിൽ കൂടുതൽ തിരയുക',
    compare_add: '➕ താരതമ്യം ചെയ്യുക', compare_added: '✓ താരതമ്യത്തിൽ', compare_max: 'ഒരേസമയം പരമാവധി 3 ട്രെയിനുകൾ താരതമ്യം ചെയ്യാം.',
    compare_selected: 'തിരഞ്ഞെടുത്തു', compare_view: 'താരതമ്യം കാണുക', compare_clear: 'മായ്ക്കുക', compare_title: 'ട്രെയിനുകൾ താരതമ്യം ചെയ്യുക',
    compare_type: 'തരം', compare_route: 'റൂട്ട്', compare_distance: 'ദൂരം', compare_duration: 'ദൈർഘ്യം',
    compare_stops: 'സ്റ്റോപ്പുകൾ', compare_status: 'നില', compare_fare: 'നിരക്ക് (ഏകദേശം)',
    near_me_btn: '📍 എനിക്ക് സമീപമുള്ള ട്രെയിനുകൾ കണ്ടെത്തുക', near_me_locating: 'നിങ്ങളുടെ സ്ഥാനം കണ്ടെത്തുന്നു…', near_me_result: 'ഏറ്റവും അടുത്ത സ്റ്റേഷൻ:', near_me_error: 'നിങ്ങളുടെ സ്ഥാനം കണ്ടെത്താൻ കഴിഞ്ഞില്ല.',
    runs_label: 'ഓടുന്നു:', runs_daily: 'ദിവസവും ഓടുന്നു',
    weather_show: '🌦️ ലക്ഷ്യസ്ഥാന കാലാവസ്ഥ', weather_hide: '🌦️ ലക്ഷ്യസ്ഥാന കാലാവസ്ഥ മറയ്ക്കുക',
    weather_loading: 'കാലാവസ്ഥ ലോഡ് ചെയ്യുന്നു…', weather_error: 'ഈ സ്റ്റേഷനുള്ള കാലാവസ്ഥ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.',
    weather_source: 'ഉറവിടം: Open-Meteo (സൗജന്യം, API കീ ആവശ്യമില്ല)',
    route_note_show: 'ℹ️ റൂട്ട് ലളിതമാക്കി — വിശദാംശങ്ങൾക്ക് ടാപ്പ് ചെയ്യുക', route_note_hide: 'ℹ️ വിശദാംശങ്ങൾ മറയ്ക്കുക',
    footer_disclaimer: 'സ്ഥിതി പൊതു സമയക്രമത്തിൽ നിന്ന് അനുകരിച്ചതാണ് (SIMULATED) (ഔദ്യോഗിക തത്സമയ GPS ഫീഡ് അല്ല). ഔദ്യോഗിക തത്സമയ നിലയ്ക്കായി NTES / IRCTC ഉപയോഗിക്കുക.<br/>"എന്റെ GPS ഉപയോഗിക്കുക" നിങ്ങളുടെ ഉപകരണത്തിന്റെ സ്ഥാനം നിങ്ങളുടെ ബ്രൗസറിൽ മാത്രം വായിക്കുന്നു (സെർവറിലേക്ക് ഒരിക്കലും അയയ്ക്കില്ല) — നിങ്ങൾ ശരിക്കും ആ ട്രെയിനിൽ യാത്ര ചെയ്യുമ്പോൾ മാത്രം ഉപയോഗപ്രദമാണ്.',
  }},
}};
let CURRENT_LANG = localStorage.getItem('ir_lang') || 'en';

function applyLanguage(lang) {{
  if (!I18N[lang]) lang = 'en';
  CURRENT_LANG = lang;
  localStorage.setItem('ir_lang', lang);
  document.getElementById('lang-select').value = lang;
  const dict = I18N[lang];
  document.querySelectorAll('[data-i18n]').forEach(el => {{ el.innerHTML = dict[el.dataset.i18n] ?? el.innerHTML; }});
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {{ el.placeholder = dict[el.dataset.i18nPlaceholder] ?? el.placeholder; }});
  updateThemeButtonLabel();
  renderCards(document.getElementById('search').value);
}}

function tr(key) {{ return (I18N[CURRENT_LANG] || I18N.en)[key] || I18N.en[key] || key; }}


// Live backend used whenever this page isn't served by its own Flask app
// (static file, GitHub Pages, etc.) so search always covers every train,
// not just the small embedded set baked into the static page.
const REMOTE_API_BASE = 'https://indian-railways-5qpb.onrender.com';

// Detect where full-database search should come from:
//   'flask'  - this page is served by its own Flask app (same-origin API)
//   'remote' - reachable via the public Render backend (static/Pages hosting)
//   'static' - neither reachable; fall back to the embedded curated set
// Callers `await _modeReady` so a search triggered before detection
// finishes doesn't incorrectly fall back to curated-only results.
const _modeReady = (async () => {{
  if (window.location.protocol !== 'file:') {{
    try {{
      const r = await fetch('/api/trains', {{ signal: AbortSignal.timeout(4000) }});
      if (r.ok) return 'flask';
    }} catch (_) {{}}
  }}
  // Render's free tier spins the backend down after inactivity — a cold
  // start can take 30-50s to respond, so give it a generous timeout (and
  // one retry) before giving up and falling back to the embedded set.
  for (let attempt = 0; attempt < 2; attempt++) {{
    try {{
      const r = await fetch(`${{REMOTE_API_BASE}}/api/trains`, {{ signal: AbortSignal.timeout(45000) }});
      if (r.ok) return 'remote';
    }} catch (_) {{}}
  }}
  return 'static';
}})();

function _apiBase(mode) {{
  return mode === 'remote' ? REMOTE_API_BASE : '';
}}

const STATUS_CLASS = {{
  running: 'status-running', at_station: 'status-at_station',
  arrived: 'status-arrived', not_running: 'status-not_running',
}};
const TYPE_COLOR = {{
  'Rajdhani': '#f97316', 'Shatabdi': '#8b5cf6', 'Duronto': '#ec4899',
  'Vande Bharat': '#22c55e', 'Mail-Express': '#38bdf8', 'Sampark Kranti': '#eab308',
  'Superfast': '#0ea5e9', 'Tejas': '#d946ef', 'Express': '#38bdf8', 'Garib Rath': '#eab308',
  'Jan Shatabdi': '#8b5cf6', 'Mail': '#38bdf8',
}};

function matches(t, q) {{
  if (!q) return true;
  const needle = q.toLowerCase().trim();
  const stops = (t.route || []).map(s => `${{s.code}} ${{s.name}}`).join(' ');
  const hay = `${{t.number}} ${{t.name}} ${{t.origin}} ${{t.destination}} ${{stops}}`.toLowerCase();
  return hay.includes(needle);
}}

let _fromFilter = '';
let _toFilter = '';

function populateStationList() {{
  document.getElementById('station-list').innerHTML =
    ALL_STATION_NAMES.map(n => `<option value="${{n}}"></option>`).join('');
}}

// Returns null (no from/to filter active), false (train excluded), or the
// matched {{board, alight}} stops describing the requested leg of the journey.
function routeMatch(t) {{
  if (!_fromFilter && !_toFilter) return null;
  const route = t.route || [];
  // Accepts a plain name, a station code, the datalist's "Name (CODE)" format,
  // or a metro-area name like "Bengaluru" that spans multiple station codes.
  const findIdx = (needle) => {{
    const raw = needle.toLowerCase().trim();
    const aliasCodes = STATION_ALIASES[raw];
    if (aliasCodes) {{
      return route.findIndex(s => aliasCodes.includes(s.code));
    }}
    // Datalist entries are formatted "CODE — Name"; a plain typed code (no
    // dash) is used as-is.
    const codeAtStart = raw.match(/^([a-z0-9]+)\\s*[\u2014-]\\s*/i);
    const code = codeAtStart ? codeAtStart[1] : raw;
    // Exact code match always wins first — otherwise a short code like "mas"
    // would spuriously substring-match unrelated names (e.g. "Masaipet").
    const codeIdx = route.findIndex(s => s.code.toLowerCase() === code);
    if (codeIdx !== -1) return codeIdx;
    return route.findIndex(s => s.name.toLowerCase().includes(raw));
  }};
  const fromIdx = _fromFilter ? findIdx(_fromFilter) : 0;
  const toIdx = _toFilter ? findIdx(_toFilter) : route.length - 1;
  if (fromIdx === -1 || toIdx === -1 || fromIdx >= toIdx) return false;
  return {{ board: route[fromIdx], alight: route[toIdx] }};
}}

function setNote(text) {{
  document.getElementById('cards-note').textContent = text;
}}

let _searchDebounce = null;
function onSearchInput(value) {{
  clearTimeout(_searchDebounce);
  _searchDebounce = setTimeout(() => performSearch(value), 300);
}}

async function performSearch(query) {{
  const q = (query || '').trim();
  if (!q) {{
    TRAINS = CURATED_TRAINS.slice();
    setNote(`Showing ${{CURATED_TRAINS.length}} popular trains — type a train number/name above, or use From/To, to search the full database.`);
    renderCards('');
    return;
  }}
  const mode = await _modeReady;
  if (mode !== 'static') {{
    try {{
      const r = await fetch(`${{_apiBase(mode)}}/api/trains/search?q=${{encodeURIComponent(q)}}`, {{ signal: AbortSignal.timeout(45000) }});
      if (r.ok) {{
        const data = await r.json();
        TRAINS = data.results || [];
        setNote(`Found ${{TRAINS.length}} train(s) matching "${{q}}" across the full database.`);
        renderCards(q);
        return;
      }}
    }} catch (_) {{}}
  }}
  TRAINS = CURATED_TRAINS.slice();
  setNote(`Live search unavailable — searching ${{CURATED_TRAINS.length}} trains embedded in this page.`);
  renderCards(q);
}}

async function applyRouteSearch() {{
  _fromFilter = document.getElementById('from-station').value.trim();
  _toFilter = document.getElementById('to-station').value.trim();
  if (!_fromFilter && !_toFilter) return;
  // A From/To search replaces whatever free-text query was previously typed —
  // otherwise leftover text (e.g. a train number searched earlier) silently
  // filters out every route result and the page looks empty.
  document.getElementById('search').value = '';
  const mode = await _modeReady;
  if (mode !== 'static') {{
    try {{
      const params = new URLSearchParams();
      if (_fromFilter) params.set('from', _fromFilter);
      if (_toFilter) params.set('to', _toFilter);
      const r = await fetch(`${{_apiBase(mode)}}/api/trains/route?${{params.toString()}}`, {{ signal: AbortSignal.timeout(45000) }});
      if (r.ok) {{
        const data = await r.json();
        TRAINS = data.results || [];
        setNote(`Found ${{TRAINS.length}} train(s) from "${{_fromFilter || 'anywhere'}}" to "${{_toFilter || 'anywhere'}}" across the full database.`);
        renderCards(document.getElementById('search').value);
        return;
      }}
    }} catch (_) {{}}
  }}
  TRAINS = CURATED_TRAINS.slice();
  setNote(`Live search unavailable — searching ${{CURATED_TRAINS.length}} trains embedded in this page.`);
  renderCards(document.getElementById('search').value);
}}

function clearRouteSearch() {{
  document.getElementById('from-station').value = '';
  document.getElementById('to-station').value = '';
  _fromFilter = '';
  _toFilter = '';
  TRAINS = CURATED_TRAINS.slice();
  setNote(`Showing ${{CURATED_TRAINS.length}} popular trains — type a train number/name above, or use From/To, to search the full database.`);
  renderCards(document.getElementById('search').value);
}}

// ── Duration / stops-count helpers (used for sorting and fare estimation) ──
function parseHHMM(hhmm) {{
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}}
// Minutes from board to alight, accounting for the route's "day" numbers
// (a journey may span multiple calendar days).
function journeyDurationMin(board, alight) {{
  const startMin = parseHHMM(board.dep || board.arr);
  const endMin = parseHHMM(alight.arr || alight.dep);
  if (startMin == null || endMin == null) return null;
  return ((alight.day - board.day) * 1440) + (endMin - startMin);
}}
function formatDuration(min) {{
  if (min == null || min < 0) return '—';
  const h = Math.floor(min / 60), m = min % 60;
  return `${{h}}h ${{m}}m`;
}}
// The leg of the journey a card represents: the board/alight stops from an
// active From/To search, or the train's full origin→destination otherwise.
function journeyLeg(train, journey) {{
  if (journey) return journey;
  const route = train.route || [];
  if (route.length < 2) return null;
  return {{ board: route[0], alight: route[route.length - 1] }};
}}

// ── Fare estimator ──────────────────────────────────────────────────────────
// Rough distance-based estimate using IR's publicly known approximate fare
// structure (base rate/km per class + reservation charge + GST + a
// superfast surcharge for Rajdhani/Shatabdi/Duronto/Superfast/Vande Bharat
// trains). NOT an official quote — actual IRCTC fares depend on telescopic
// slabs, dynamic/flexi pricing, and other rules this does not model.
const FARE_RATES = {{ '2S': 0.35, SL: 0.55, CC: 1.10, '3A': 1.60, '2A': 2.30, '1A': 3.70 }};
const FARE_RESERVATION = {{ '2S': 15, SL: 20, CC: 40, '3A': 40, '2A': 50, '1A': 60 }};
const SUPERFAST_TYPES = new Set(['Rajdhani', 'Shatabdi', 'Duronto', 'Vande Bharat', 'Tejas', 'Superfast', 'Garib Rath']);

function estimateFares(train, distKm) {{
  const isSuperfast = SUPERFAST_TYPES.has(train.type);
  const surcharge = isSuperfast ? Math.min(75, Math.max(15, Math.round(distKm / 20))) : 0;
  const isAcTrain = ['Rajdhani', 'Shatabdi', 'Duronto', 'Vande Bharat', 'Tejas'].includes(train.type);
  const classes = isAcTrain ? ['CC', '3A', '2A', '1A'] : ['2S', 'SL', '3A', '2A'];
  const fares = {{}};
  classes.forEach(cls => {{
    const base = distKm * FARE_RATES[cls] + FARE_RESERVATION[cls] + surcharge;
    const withGst = ['3A', '2A', '1A', 'CC'].includes(cls) ? base * 1.05 : base;
    fares[cls] = Math.max(30, Math.round(withGst));
  }});
  return fares;
}}

// Illustrative CO2e-per-passenger-km factors (grams) — commonly cited rough
// averages for train/flight/car trip comparisons. Not a precise carbon
// accounting tool; actual figures vary by vehicle, load factor and fuel mix.
const CO2_G_PER_KM = {{ train: 28, flight: 255, car: 192 }};
function estimateCO2Kg(distKm) {{
  return {{
    train: (distKm * CO2_G_PER_KM.train / 1000).toFixed(1),
    flight: (distKm * CO2_G_PER_KM.flight / 1000).toFixed(1),
    car: (distKm * CO2_G_PER_KM.car / 1000).toFixed(1),
  }};
}}

function toggleFareBox(number, btnEl) {{
  const box = document.getElementById(`fare-${{number}}`);
  if (!box) return;
  const show = box.style.display === 'none';
  box.style.display = show ? 'block' : 'none';
  btnEl.textContent = show ? tr('fare_hide') : tr('fare_show');
}}

function toggleRouteNote(number, btnEl) {{
  const box = document.getElementById(`routenote-${{number}}`);
  if (!box) return;
  const show = box.style.display === 'none';
  box.style.display = show ? 'block' : 'none';
  btnEl.textContent = show ? tr('route_note_hide') : tr('route_note_show');
}}

// ── Destination weather (Open-Meteo — free, no API key, CORS-friendly) ─────
// Keyed by station code (not train number) since several trains often share
// a destination — one fetch per station is enough.
const _weatherCache = {{}};
const WMO_DESC = {{
  0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
  45: 'Fog', 48: 'Icy fog', 51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
  61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
  71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow', 77: 'Snow grains',
  80: 'Slight showers', 81: 'Moderate showers', 82: 'Heavy showers',
  85: 'Slight snow showers', 86: 'Heavy snow showers',
  95: 'Thunderstorm', 96: 'Thunderstorm with hail', 99: 'Thunderstorm, heavy hail',
}};
const WMO_ICON = {{
  0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️', 45: '🌫️', 48: '🌫️',
  51: '🌦️', 53: '🌦️', 55: '🌧️', 61: '🌧️', 63: '🌧️', 65: '🌧️',
  71: '🌨️', 73: '🌨️', 75: '❄️', 77: '🌨️', 80: '🌦️', 81: '🌧️',
  82: '⛈️', 85: '🌨️', 86: '❄️', 95: '⛈️', 96: '⛈️', 99: '⛈️',
}};

async function toggleWeatherBox(number, btnEl) {{
  const box = document.getElementById(`weather-${{number}}`);
  if (!box) return;
  const show = box.style.display === 'none';
  box.style.display = show ? 'block' : 'none';
  btnEl.textContent = show ? tr('weather_hide') : tr('weather_show');
  if (!show || box.dataset.loaded === '1') return;
  box.dataset.loaded = '1';
  const code = btnEl.dataset.code;
  const info = STATION_INFO[code];
  if (!info) {{ box.innerHTML = `<div>${{tr('weather_error')}}</div>`; return; }}
  box.innerHTML = `<div>${{tr('weather_loading')}}</div>`;
  if (_weatherCache[code]) {{ _renderWeather(box, _weatherCache[code], info); return; }}
  try {{
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${{info.lat}}&longitude=${{info.lon}}`
      + `&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=Asia%2FKolkata`;
    const r = await fetch(url, {{ signal: AbortSignal.timeout(10000) }});
    if (!r.ok) throw new Error('bad response');
    const data = await r.json();
    _weatherCache[code] = data;
    _renderWeather(box, data, info);
  }} catch (_) {{
    box.innerHTML = `<div>${{tr('weather_error')}}</div>`;
  }}
}}

function _renderWeather(box, data, info) {{
  const cur = data.current || {{}};
  const code = cur.weather_code ?? 0;
  box.innerHTML = `
    <div><span class="weather-icon">${{WMO_ICON[code] || '🌡️'}}</span> <b>${{info.name}}</b>: ${{cur.temperature_2m ?? '—'}}&deg;C, ${{WMO_DESC[code] || 'Unknown'}}</div>
    <div>Humidity ${{cur.relative_humidity_2m ?? '—'}}% &bull; Wind ${{cur.wind_speed_10m ?? '—'}} km/h</div>
    <div class="fare-disclaimer">${{tr('weather_source')}}</div>`;
}}

// ── Route map (Leaflet / OpenStreetMap — free, no API key) ─────────────────
let _mapInstances = {{}};
// renderCards() replaces the #cards DOM (including every map-<number> div) on
// every search/sort/language change, which would otherwise leave this cache
// pointing at detached, dead Leaflet instances — silently breaking any map
// that's reopened after a re-render (a blank box, since toggleRouteMap saw a
// cached entry and skipped re-creating the map in the new container).
function _destroyAllMaps() {{
  Object.values(_mapInstances).forEach(map => {{ try {{ map.remove(); }} catch (_) {{}} }});
  _mapInstances = {{}};
}}
function toggleRouteMap(number, btnEl) {{
  const container = document.getElementById(`map-${{number}}`);
  if (!container) return;
  const show = container.style.display === 'none';
  container.style.display = show ? 'block' : 'none';
  btnEl.textContent = show ? tr('map_hide') : tr('map_show');
  if (!show || _mapInstances[number]) {{
    if (show && _mapInstances[number]) setTimeout(() => _mapInstances[number].invalidateSize(), 50);
    return;
  }}
  const train = TRAINS.find(x => x.number === number);
  const stops = (train?.route || []).filter(s => s.lat != null && s.lon != null);
  if (stops.length < 2) {{
    container.innerHTML = '<div style="padding:10px;font-size:.72rem;color:var(--muted)">No station coordinates available for this route.</div>';
    return;
  }}
  setTimeout(() => {{
    const map = L.map(container).setView([stops[0].lat, stops[0].lon], 6);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 18,
    }}).addTo(map);
    const latlngs = stops.map(s => [s.lat, s.lon]);
    L.polyline(latlngs, {{ color: '#38bdf8', weight: 3 }}).addTo(map);
    stops.forEach(s => L.circleMarker([s.lat, s.lon], {{ radius: 4, color: '#38bdf8', fillOpacity: 1 }})
      .bindTooltip(`${{s.name}} (${{s.code}})`).addTo(map));
    map.fitBounds(latlngs, {{ padding: [20, 20] }});
    // Guard against the container's real size not being settled yet at
    // creation time (a common Leaflet gotcha) by re-fitting one more time
    // on the next frame.
    requestAnimationFrame(() => {{
      map.invalidateSize();
      map.fitBounds(latlngs, {{ padding: [20, 20] }});
    }});
    _mapInstances[number] = map;
  }}, 50);
}}

function renderCards(query) {{
  _destroyAllMaps();
  const container = document.getElementById('cards');
  let filtered = TRAINS
    .map(tn => ({{ train: tn, journey: routeMatch(tn) }}))
    .filter(({{ train, journey }}) => journey !== false && matches(train, query || ''));

  const sortMode = document.getElementById('sort-select')?.value || 'default';
  if (sortMode !== 'default') {{
    filtered = filtered.slice().sort((a, b) => {{
      const legA = journeyLeg(a.train, a.journey), legB = journeyLeg(b.train, b.journey);
      if (!legA || !legB) return 0;
      if (sortMode === 'departure') {{
        return (parseHHMM(legA.board.dep || legA.board.arr) ?? 9999) - (parseHHMM(legB.board.dep || legB.board.arr) ?? 9999);
      }}
      if (sortMode === 'duration') {{
        return (journeyDurationMin(legA.board, legA.alight) ?? 1e9) - (journeyDurationMin(legB.board, legB.alight) ?? 1e9);
      }}
      if (sortMode === 'stops') {{
        const countA = (a.train.route || []).indexOf(legA.alight) - (a.train.route || []).indexOf(legA.board);
        const countB = (b.train.route || []).indexOf(legB.alight) - (b.train.route || []).indexOf(legB.board);
        return countA - countB;
      }}
      return 0;
    }});
  }}

  if (!filtered.length) {{
    const label = (_fromFilter || _toFilter)
      ? `No trains found from "${{_fromFilter || 'anywhere'}}" to "${{_toFilter || 'anywhere'}}"`
      : `No trains found for "${{query}}"`;
    container.innerHTML = `<div class="no-results">
      <div class="no-results-icon">&#128269;</div>
      ${{label}}
    </div>`;
    return;
  }}
  container.innerHTML = filtered.map(({{ train: t, journey }}) => {{
    const color = TYPE_COLOR[t.type] || '#38bdf8';
    const delayLabel = t.delay_min > 0 ? ` (+${{t.delay_min}}m)` : (t.delay_min < 0 ? ` (${{t.delay_min}}m)` : '');
    const statusClass = STATUS_CLASS[t.status] || '';
    const pct = t.percent_complete || 0;
    const nextInfo = t.next_station
      ? `Next: <b>${{t.next_station}}</b>${{t.eta ? ' ETA ' + t.eta : ''}}`
      : (t.status === 'arrived' ? 'Journey complete' : '');
    const journeyBanner = journey
      ? `<div class="journey-banner">&#127939; Board <b>${{journey.board.name}} (${{journey.board.code}})</b> (dep ${{journey.board.dep || journey.board.arr || '—'}})
          &#8594; Alight <b>${{journey.alight.name}} (${{journey.alight.code}})</b> (arr ${{journey.alight.arr || '—'}})
          &bull; ${{Math.abs(journey.alight.dist - journey.board.dist)}} km</div>`
      : '';
    const routeNote = t.route_note
      ? `<div class="route-note-wrap">
          <button class="route-note-btn" onclick="toggleRouteNote('${{t.number}}', this)">${{tr('route_note_show')}}</button>
          <div class="route-note" id="routenote-${{t.number}}" style="display:none">&#8505; ${{t.route_note}}</div>
        </div>`
      : '';
    const runsBadge = (t.runs_on && t.runs_on.length < 7)
      ? `<div class="runs-badge">${{tr('runs_label')}} ${{t.runs_on.join(' ')}}</div>`
      : `<div class="runs-badge">${{tr('runs_daily')}}</div>`;
    const leg = journeyLeg(t, journey);
    const legDist = leg ? Math.abs(leg.alight.dist - leg.board.dist) : 0;
    const legDuration = leg ? journeyDurationMin(leg.board, leg.alight) : null;
    const fares = leg ? estimateFares(t, legDist) : {{}};
    const eco = leg ? estimateCO2Kg(legDist) : null;
    const fareBox = leg ? `
      <div class="fare-box" id="fare-${{t.number}}" style="display:none">
        <div>Distance: <b>${{legDist}} km</b> &bull; Duration: <b>${{formatDuration(legDuration)}}</b></div>
        <div class="fare-grid">
          ${{Object.entries(fares).map(([cls, amt]) => `<span>${{cls}}: <b>&#8377;${{amt}}</b></span>`).join('')}}
        </div>
        <div class="fare-disclaimer">Rough estimate only — not an official IRCTC fare quote.</div>
        <div class="eco-row">&#127793; Est. CO&#8322;: train <b>${{eco.train}} kg</b> vs flight <b>${{eco.flight}} kg</b> vs car <b>${{eco.car}} kg</b> (per passenger)</div>
        <div class="fare-disclaimer">Illustrative only, based on commonly cited average emission factors — actual figures vary by vehicle/occupancy/fuel mix.</div>
      </div>` : '';
    const weatherBtn = leg
      ? `<button class="weather-btn" data-code="${{leg.alight.code}}" onclick="toggleWeatherBox('${{t.number}}', this)">${{tr('weather_show')}}</button>`
      : '';
    const weatherBox = leg ? `<div class="weather-box" id="weather-${{t.number}}" style="display:none"></div>` : '';
    return `
    <div class="card" style="--cc:${{color}}">
      <div class="card-top">
        <span class="train-no">#${{t.number}}</span>
        <span class="type-badge" style="--cc:${{color}}">${{t.type}}</span>
      </div>
      <div class="train-name">${{t.name}}</div>
      <div class="route-line"><b>${{t.origin}}</b> &#8594; <b>${{t.destination}}</b></div>
      ${{runsBadge}}
      ${{journeyBanner}}
      <div class="status-label ${{statusClass}}">${{t.status_label}}${{delayLabel}}</div>
      <div class="progress-track"><div class="progress-fill" style="width:${{pct}}%"></div></div>
      <div class="route-line">${{nextInfo}}</div>
      ${{routeNote}}
      <div class="card-actions">
        <button class="gps-btn" onclick="locateOnTrain('${{t.number}}', this)">${{tr('gps_start')}}</button>
        <button class="map-btn" onclick="toggleRouteMap('${{t.number}}', this)">${{tr('map_show')}}</button>
        <button class="fare-btn" onclick="toggleFareBox('${{t.number}}', this)">${{tr('fare_show')}}</button>
        <button class="story-btn" onclick="toggleStoryBox('${{t.number}}', this)">${{tr('story_show')}}</button>
        ${{weatherBtn}}
        <button class="compare-btn ${{_compareTrains.has(t.number) ? 'active' : ''}}" onclick="toggleCompare('${{t.number}}', this)">${{_compareTrains.has(t.number) ? tr('compare_added') : tr('compare_add')}}</button>
      </div>
      <div class="route-map" id="map-${{t.number}}" style="display:none"></div>
      ${{fareBox}}
      <div class="story-box" id="story-${{t.number}}" style="display:none"></div>
      ${{weatherBox}}
      <div class="stops-detail">
        ${{(t.route || []).map(s => `
          <div class="stop-row ${{s.name === t.last_station ? 'current' : ''}}">
            <span><b>${{s.name}}</b> (${{s.code}})</span>
            <span>${{s.arr || '—'}} / ${{s.dep || '—'}}</span>
          </div>`).join('')}}
      </div>
    </div>`;
  }}).join('');
}}

// ── Train Story ──────────────────────────────────────────────────────────
// Two parts, both honest about what they are:
//  1. "About this train" — always shown, built only from data we actually
//     have (type/origin/destination/distance/stops/zone). Not a history.
//  2. A genuine live summary from Wikipedia's public REST API (free, no
//     key) keyed by train name, when a dedicated article exists (mostly
//     named premium trains — Rajdhani, Shatabdi, etc). Most of the ~2,400
//     imported trains have no article; rather than invent a "why/when it
//     started" story for those, we say so honestly and give a real search
//     link so the user can look further themselves.
const _storyCache = {{}};
function _aboutThisTrain(train) {{
  const route = train.route || [];
  const distKm = route.length ? Math.abs(route[route.length - 1].dist - route[0].dist) : 0;
  return `#${{train.number}} ${{train.name}} is a ${{train.type}} service connecting `
    + `${{train.origin}} and ${{train.destination}}, covering ${{distKm}} km via ${{route.length}} stops, `
    + `operated by the ${{train.zone}} zone.`;
}}
async function toggleStoryBox(number, btnEl) {{
  const box = document.getElementById(`story-${{number}}`);
  const train = TRAINS.find(x => x.number === number);
  if (!box || !train) return;
  const show = box.style.display === 'none';
  box.style.display = show ? 'flex' : 'none';
  btnEl.textContent = show ? tr('story_hide') : tr('story_show');
  if (!show || box.dataset.loaded) return;
  box.dataset.loaded = '1';
  const searchLink = `https://en.wikipedia.org/w/index.php?search=${{encodeURIComponent(train.name)}}`;
  const learnMore = `<div class="story-muted" style="margin-top:6px"><a href="${{searchLink}}" target="_blank" rel="noopener">${{tr('story_learn_more')}} ↗</a></div>`;
  box.innerHTML = `<div><div>${{_aboutThisTrain(train)}}</div>
    <div class="story-muted" style="margin-top:6px">${{tr('story_loading')}}</div></div>`;
  try {{
    let story = _storyCache[train.name];
    if (!story) {{
      const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(train.name.replace(/ /g, '_'))}}`;
      const r = await fetch(url, {{ signal: AbortSignal.timeout(8000) }});
      if (!r.ok) throw new Error('not found');
      const data = await r.json();
      if (data.type === 'disambiguation' || !data.extract) throw new Error('no extract');
      story = data;
      _storyCache[train.name] = story;
    }}
    const thumb = story.thumbnail?.source ? `<img src="${{story.thumbnail.source}}" alt=""/>` : '';
    const link = story.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${{encodeURIComponent(train.name.replace(/ /g, '_'))}}`;
    box.innerHTML = `
      ${{thumb}}
      <div>
        <div>${{_aboutThisTrain(train)}}</div>
        <div style="margin-top:8px">${{story.extract}}</div>
        <div class="story-muted" style="margin-top:6px">${{tr('story_source')}} &bull; <a href="${{link}}" target="_blank" rel="noopener">${{story.title}} ↗</a></div>
      </div>`;
  }} catch (_) {{
    box.innerHTML = `<div>
      <div>${{_aboutThisTrain(train)}}</div>
      <div class="story-muted" style="margin-top:8px">${{tr('story_not_found')}}</div>
      ${{learnMore}}
    </div>`;
  }}
}}

// ── Compare trains side-by-side ─────────────────────────────────────────────
// Session-only selection (not persisted) of up to 3 trains, compared on
// distance/duration/fare/stops using each train's full origin→destination
// journey (ignores any active From/To filter, since the comparison is about
// the trains themselves, not a specific searched leg). The train object is
// cached at selection time (not re-looked-up from the live TRAINS list),
// since TRAINS is replaced by every subsequent search/sort and would
// otherwise silently drop earlier picks from the comparison.
const _compareTrains = new Map();
const COMPARE_MAX = 3;

function toggleCompare(number, btnEl) {{
  if (_compareTrains.has(number)) {{
    _compareTrains.delete(number);
  }} else {{
    if (_compareTrains.size >= COMPARE_MAX) {{
      alert(tr('compare_max'));
      return;
    }}
    const train = TRAINS.find(t => t.number === number);
    if (train) _compareTrains.set(number, train);
  }}
  btnEl.classList.toggle('active', _compareTrains.has(number));
  btnEl.textContent = _compareTrains.has(number) ? tr('compare_added') : tr('compare_add');
  updateCompareBar();
}}

function updateCompareBar() {{
  let bar = document.getElementById('compare-bar');
  if (!bar) {{
    bar = document.createElement('div');
    bar.id = 'compare-bar';
    bar.className = 'compare-bar';
    document.body.appendChild(bar);
  }}
  if (_compareTrains.size === 0) {{
    bar.style.display = 'none';
    return;
  }}
  bar.style.display = 'flex';
  bar.innerHTML = `
    <span>${{_compareTrains.size}} ${{tr('compare_selected')}}</span>
    <button onclick="openCompareModal()">${{tr('compare_view')}}</button>
    <button onclick="clearCompare()">${{tr('compare_clear')}}</button>`;
}}

function clearCompare() {{
  _compareTrains.clear();
  updateCompareBar();
  closeCompareModal();
  renderCards(document.getElementById('search').value);
}}

function openCompareModal() {{
  const trains = [..._compareTrains.values()];
  const rows = trains.map(t => {{
    const route = t.route || [];
    const dist = route.length ? Math.abs(route[route.length - 1].dist - route[0].dist) : 0;
    const board = route[0], alight = route[route.length - 1];
    const duration = (board && alight) ? journeyDurationMin(board, alight) : null;
    const fares = estimateFares(t, dist);
    return {{ t, dist, duration, stops: route.length, fares }};
  }});
  const overlay = document.createElement('div');
  overlay.className = 'compare-overlay';
  overlay.id = 'compare-overlay';
  overlay.onclick = (e) => {{ if (e.target === overlay) closeCompareModal(); }};
  overlay.innerHTML = `
    <div class="compare-modal">
      <div class="compare-modal-head">
        <b>${{tr('compare_title')}}</b>
        <button onclick="closeCompareModal()">&#10005;</button>
      </div>
      <table class="compare-table">
        <tr><th></th>${{rows.map(r => `<th>#${{r.t.number}}<br/>${{r.t.name}}</th>`).join('')}}</tr>
        <tr><td>${{tr('compare_type')}}</td>${{rows.map(r => `<td>${{r.t.type}}</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_route')}}</td>${{rows.map(r => `<td>${{r.t.origin}} → ${{r.t.destination}}</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_distance')}}</td>${{rows.map(r => `<td>${{r.dist}} km</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_duration')}}</td>${{rows.map(r => `<td>${{formatDuration(r.duration)}}</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_stops')}}</td>${{rows.map(r => `<td>${{r.stops}}</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_status')}}</td>${{rows.map(r => `<td>${{r.t.status_label}}</td>`).join('')}}</tr>
        <tr><td>${{tr('compare_fare')}}</td>${{rows.map(r => `<td>${{Object.entries(r.fares).map(([c, a]) => `${{c}}: &#8377;${{a}}`).join('<br/>')}}</td>`).join('')}}</tr>
      </table>
      <div class="fare-disclaimer" style="padding:0 16px 12px">Fare figures are rough estimates only — not an official IRCTC quote.</div>
    </div>`;
  document.body.appendChild(overlay);
}}

function closeCompareModal() {{
  document.getElementById('compare-overlay')?.remove();
}}

// ── GPS Trip Mode ──────────────────────────────────────────────────────────
// Reads the rider's own device location in the browser only — never sent to
// a server. Matches it against the train's station coordinates to show the
// nearest stop. Only meaningful if you're actually on that train.
let _gpsWatchId = null;
let _gpsTrainNumber = null;
function haversineKm(lat1, lon1, lat2, lon2) {{
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}}

// ── Find Trains Near Me ─────────────────────────────────────────────────────
// Reads the device's own location in the browser only (never sent to a
// server) and matches it against the ~8,700-station coordinate set to find
// the nearest railway station, then runs a normal From/To search departing
// from there — reusing the existing route-search plumbing.
function findTrainsNearMe() {{
  if (!navigator.geolocation) {{
    alert('Geolocation is not supported by this browser.');
    return;
  }}
  const note = document.getElementById('near-me-note');
  note.style.display = 'block';
  note.textContent = tr('near_me_locating');
  navigator.geolocation.getCurrentPosition(
    pos => {{
      const {{ latitude: lat, longitude: lon }} = pos.coords;
      let nearestCode = null, nearestDist = Infinity;
      for (const [code, info] of Object.entries(STATION_INFO)) {{
        const d = haversineKm(lat, lon, info.lat, info.lon);
        if (d < nearestDist) {{ nearestDist = d; nearestCode = code; }}
      }}
      if (!nearestCode) {{
        note.textContent = tr('near_me_error');
        return;
      }}
      const info = STATION_INFO[nearestCode];
      note.textContent = `${{tr('near_me_result')}} ${{info.name}} (${{nearestCode}}) — ~${{nearestDist.toFixed(1)}} km`;
      document.getElementById('from-station').value = `${{nearestCode}} — ${{info.name}}`;
      document.getElementById('to-station').value = '';
      applyRouteSearch();
    }},
    err => {{ note.textContent = tr('near_me_error'); }},
    {{ enableHighAccuracy: true, timeout: 15000 }}
  );
}}

function locateOnTrain(trainNumber, btnEl) {{
  if (!navigator.geolocation) {{
    alert('Geolocation is not supported by this browser.');
    return;
  }}
  if (_gpsWatchId !== null && _gpsTrainNumber === trainNumber) {{
    navigator.geolocation.clearWatch(_gpsWatchId);
    _gpsWatchId = null;
    _gpsTrainNumber = null;
    btnEl.textContent = tr('gps_start');
    btnEl.classList.remove('active');
    const result = btnEl.parentElement.querySelector('.gps-result');
    if (result) result.remove();
    return;
  }}
  btnEl.textContent = tr('gps_stop');
  btnEl.classList.add('active');
  _gpsTrainNumber = trainNumber;
  _gpsWatchId = navigator.geolocation.watchPosition(
    pos => updateGpsResult(trainNumber, btnEl, pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy),
    err => alert('Could not get your location: ' + err.message),
    {{ enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }}
  );
}}

function updateGpsResult(trainNumber, btnEl, lat, lon, accuracy) {{
  const train = TRAINS.find(t => t.number === trainNumber);
  if (!train) return;
  const stops = (train.route || []).filter(s => s.lat != null && s.lon != null);
  if (!stops.length) return;
  const ranked = stops
    .map(s => ({{ ...s, gpsDist: haversineKm(lat, lon, s.lat, s.lon) }}))
    .sort((a, b) => a.gpsDist - b.gpsDist);
  const nearest = ranked[0];
  let result = btnEl.parentElement.querySelector('.gps-result');
  if (!result) {{
    result = document.createElement('div');
    result.className = 'gps-result';
    btnEl.insertAdjacentElement('afterend', result);
  }}
  result.textContent =
    `📍 You're nearest to ${{nearest.name}} (~${{nearest.gpsDist.toFixed(1)}} km away, GPS accuracy ±${{Math.round(accuracy)}}m)`;
}}

function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  updateThemeButtonLabel();
  localStorage.setItem('ir_theme', isLight ? 'light' : 'dark');
}}
function updateThemeButtonLabel() {{
  const isLight = document.body.classList.contains('light');
  document.getElementById('theme-btn').textContent = isLight ? tr('theme_dark') : tr('theme_light');
}}
if (localStorage.getItem('ir_theme') === 'light') document.body.classList.add('light');

populateStationList();
applyLanguage(CURRENT_LANG);
renderCards('');

// If served via Flask (same-origin API reachable), periodically refresh the
// header stats and (only when no search/filter is active) the default
// curated view. Skipped in 'remote'/'static' mode so a plain file:// open
// doesn't spam the console with 403s from a relative-path fetch.
setInterval(async () => {{
  const mode = await _modeReady;
  if (mode !== 'flask') return;
  fetch('/api/trains', {{ signal: AbortSignal.timeout(4000) }})
    .then(r => r.ok ? r.json() : null)
    .then(data => {{
      if (!data || !data.trains) return;
      document.getElementById('running-now').textContent = data.running_now;
      const q = document.getElementById('search').value.trim();
      if (!q && !_fromFilter && !_toFilter) {{
        CURATED_TRAINS.length = 0;
        CURATED_TRAINS.push(...data.trains);
        TRAINS = CURATED_TRAINS.slice();
        renderCards('');
      }}
    }})
    .catch(() => {{}});
}}, 60000);
</script>
</body>
</html>"""
