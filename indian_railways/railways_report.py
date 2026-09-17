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

from indian_railways.train_data import ALL_STATION_NAMES, STATION_ALIASES


def build_html(payload: dict) -> str:
    generated_at  = payload.get("generated_at", "")
    date_label    = payload.get("date", "")
    total_trains  = payload.get("total_trains", 0)
    running_now   = payload.get("running_now", 0)
    trains        = payload.get("trains", [])
    station_names_json = json.dumps(ALL_STATION_NAMES, ensure_ascii=False)
    station_aliases_json = json.dumps({k: sorted(v) for k, v in STATION_ALIASES.items()}, ensure_ascii=False)

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
      <h1>Indian Railways Train Tracker</h1>
      <p>Search by train number/name, or find trains between two stations</p>
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
      <input type="text" id="search" placeholder="Train number or name…"
             oninput="onSearchInput(this.value)" autocomplete="off"/>
    </div>
    <button id="theme-btn" onclick="toggleTheme()">&#9728; Light</button>
  </div>
</header>

<div class="route-search-bar">
  <div class="rs-field">
    <label for="from-station">From</label>
    <input type="text" id="from-station" list="station-list" placeholder="Source station" autocomplete="off"/>
  </div>
  <div class="rs-field">
    <label for="to-station">To</label>
    <input type="text" id="to-station" list="station-list" placeholder="Destination station" autocomplete="off"/>
  </div>
  <datalist id="station-list"></datalist>
  <button id="route-search-btn" onclick="applyRouteSearch()">&#128269; Search</button>
  <button id="route-clear-btn" onclick="clearRouteSearch()">&#10005; Clear</button>
</div>

<main>
  <div class="cards-note" id="cards-note">Showing {len(trains)} popular trains &mdash; type a train number/name above, or use From/To, to search the full database of {total_trains} trains.</div>
  <div class="cards" id="cards"></div>
</main>

<footer>
  Indian Railways Train Tracker &mdash; demo dashboard<br/>
  <span style="opacity:.65">Status is SIMULATED from public schedules (not an official live GPS feed). For official real-time status use NTES / IRCTC.<br/>
  "Use My GPS" reads your device's own location in your browser only (never sent to a server) to show which stop you're nearest &mdash; useful only if you're actually riding that train.</span><br/>
  <span style="opacity:.65">Built by Naveen Alla</span>
</footer>

<script>
const CURATED_TRAINS = {trains_json};
const ALL_STATION_NAMES = {station_names_json};
const STATION_ALIASES = {station_aliases_json};
let TRAINS = CURATED_TRAINS.slice();

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
  try {{
    const r = await fetch(`${{REMOTE_API_BASE}}/api/trains`, {{ signal: AbortSignal.timeout(6000) }});
    if (r.ok) return 'remote';
  }} catch (_) {{}}
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
  const hay = `${{t.number}} ${{t.name}} ${{t.origin}} ${{t.destination}}`.toLowerCase();
  return hay.includes(q.toLowerCase().trim());
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
      const r = await fetch(`${{_apiBase(mode)}}/api/trains/search?q=${{encodeURIComponent(q)}}`, {{ signal: AbortSignal.timeout(6000) }});
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
  const mode = await _modeReady;
  if (mode !== 'static') {{
    try {{
      const params = new URLSearchParams();
      if (_fromFilter) params.set('from', _fromFilter);
      if (_toFilter) params.set('to', _toFilter);
      const r = await fetch(`${{_apiBase(mode)}}/api/trains/route?${{params.toString()}}`, {{ signal: AbortSignal.timeout(6000) }});
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

function renderCards(query) {{
  const container = document.getElementById('cards');
  const filtered = TRAINS
    .map(t => ({{ train: t, journey: routeMatch(t) }}))
    .filter(({{ train, journey }}) => journey !== false && matches(train, query || ''));

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
    const delayLabel = t.delay_min > 0 ? ` (+${{t.delay_min}}m)` : '';
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
    return `
    <div class="card" style="--cc:${{color}}">
      <div class="card-top">
        <span class="train-no">#${{t.number}}</span>
        <span class="type-badge" style="--cc:${{color}}">${{t.type}}</span>
      </div>
      <div class="train-name">${{t.name}}</div>
      <div class="route-line"><b>${{t.origin}}</b> &#8594; <b>${{t.destination}}</b></div>
      ${{journeyBanner}}
      <div class="status-label ${{statusClass}}">${{t.status_label}}${{delayLabel}}</div>
      <div class="progress-track"><div class="progress-fill" style="width:${{pct}}%"></div></div>
      <div class="route-line">${{nextInfo}}</div>
      <button class="gps-btn" onclick="locateOnTrain('${{t.number}}', this)">&#128205; Use My GPS (I'm on this train)</button>
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

function locateOnTrain(trainNumber, btnEl) {{
  if (!navigator.geolocation) {{
    alert('Geolocation is not supported by this browser.');
    return;
  }}
  if (_gpsWatchId !== null && _gpsTrainNumber === trainNumber) {{
    navigator.geolocation.clearWatch(_gpsWatchId);
    _gpsWatchId = null;
    _gpsTrainNumber = null;
    btnEl.textContent = "📍 Use My GPS (I'm on this train)";
    btnEl.classList.remove('active');
    const result = btnEl.parentElement.querySelector('.gps-result');
    if (result) result.remove();
    return;
  }}
  btnEl.textContent = '⏹ Stop GPS Tracking';
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
  document.getElementById('theme-btn').textContent = isLight ? '🌙 Dark' : '☀ Light';
  localStorage.setItem('ir_theme', isLight ? 'light' : 'dark');
}}
if (localStorage.getItem('ir_theme') === 'light') toggleTheme();

populateStationList();
renderCards('');

// If served via Flask, periodically refresh the header stats and (only when
// no search/filter is active) the default curated view.
setInterval(() => {{
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
