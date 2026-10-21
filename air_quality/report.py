"""
Air Quality — HTML Dashboard Generator
=========================================
Atmospheric gauge aesthetic: soft rounded cards with circular conic-gradient
AQI dials and a sky-tinted background — deliberately distinct from the
other agents' flat card-grid dashboards.

Features: severe-AQI alert banner, dominant-pollutant + health-advisory
detail toggle per card, 5-day AQI forecast strip, historical trend
sparkline (once a few days of data have been archived), a Leaflet map
view, a 2-city compare modal, and a geolocation-based "AQI near me" button.
"""

from __future__ import annotations

import json

_SKY = {
    "#22c55e": ("#bbf7d0", "#064e3b"),   # Good        — clear sky green
    "#eab308": ("#fef08a", "#713f12"),   # Moderate    — hazy yellow
    "#f97316": ("#fed7aa", "#7c2d12"),   # Unhealthy SG— orange haze
    "#ef4444": ("#fecaca", "#450a0a"),   # Unhealthy   — red smog
    "#a855f7": ("#e9d5ff", "#3b0764"),   # Very Unhealthy — purple murk
    "#7f1d1d": ("#fda4af", "#1c0a0a"),   # Hazardous   — dark ash
}


def _gauge(aqi: float, color: str) -> str:
    pct = max(0, min(aqi / 300 * 100, 100))
    deg = pct * 3.6
    return f"""
      <div class="gauge" style="background:conic-gradient({color} {deg}deg, var(--ring-bg) {deg}deg)">
        <div class="gauge-inner">
          <div class="gauge-value" style="color:{color}">{aqi:.0f}</div>
          <div class="gauge-unit">AQI</div>
        </div>
      </div>"""


def _sparkline_svg(points: list, width: int = 150, height: int = 36) -> str:
    """Tiny inline SVG trend line from [[date, aqi], ...] points (oldest-first)."""
    if len(points) < 2:
        return '<div class="trend-empty">Building trend… check back after a few daily refreshes.</div>'
    values = [p[1] for p in points]
    lo, hi = min(values), max(values)
    span = max(hi - lo, 1)
    n = len(values)
    coords = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * (width - 4) + 2
        y = height - 2 - ((v - lo) / span) * (height - 4)
        coords.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(coords)
    last_color = "#38bdf8"
    return f"""
    <svg class="sparkline" viewBox="0 0 {width} {height}" preserveAspectRatio="none" aria-hidden="true">
      <polyline points="{polyline}" fill="none" stroke="{last_color}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div class="trend-range">{points[0][0][5:]} \u2192 {points[-1][0][5:]} &middot; {lo:.0f}\u2013{hi:.0f} AQI</div>"""


def _forecast_strip(forecast: list) -> str:
    if not forecast:
        return ""
    chips = "".join(
        f'<div class="fc-chip" style="border-color:{d["color"]}">'
        f'<span class="fc-day">{d["day"]}</span>'
        f'<span class="fc-aqi" style="color:{d["color"]}">{d["peak_aqi"]}</span>'
        f'</div>'
        for d in forecast
    )
    return f'<div class="forecast-strip">{chips}</div>'


def _pollutant_grid(r: dict) -> str:
    rows = [
        ("PM2.5", r.get("pm2_5"), "µg/m³"), ("PM10", r.get("pm10"), "µg/m³"),
        ("Ozone", r.get("ozone"), "µg/m³"), ("NO₂", r.get("no2"), "µg/m³"),
        ("CO", r.get("co"), "µg/m³"), ("SO₂", r.get("so2"), "µg/m³"),
    ]
    cells = "".join(
        f'<div class="pollutant-cell"><span class="p-name">{name}</span>'
        f'<span class="p-val">{val:.1f}' + f'</span><span class="p-unit">{unit}</span></div>'
        if val is not None else
        f'<div class="pollutant-cell"><span class="p-name">{name}</span><span class="p-val">—</span></div>'
        for name, val, unit in rows
    )
    return f'<div class="pollutant-grid">{cells}</div>'


def _city_card(c: dict, trend_points: list) -> str:
    r = c.get("reading", {})
    if "error" in r or r.get("us_aqi") is None:
        return f"""
    <div class="city-card unknown" data-name="{c['name'].lower()}" data-state="{c['state'].lower()}" data-aqi="-1">
      <div class="city-name">{c['name']} <span class="city-state">{c['state']}</span></div>
      <div class="aqi-unknown">☁️ Data unavailable</div>
    </div>"""
    aqi = r["us_aqi"]
    dom = r.get("dominant_pollutant")
    safe_id = c["name"].replace(" ", "-").replace("&", "and")
    return f"""
    <div class="city-card" data-name="{c['name'].lower()}" data-state="{c['state'].lower()}" data-aqi="{aqi}">
      <button type="button" class="home-pin-btn" data-city="{c['name']}" aria-label="Set as home city" aria-pressed="false" onclick="toggleHomeCity(this)">📍</button>
      {_gauge(aqi, r['color'])}
      <div class="city-name">{c['name']} <span class="city-state">{c['state']}</span></div>
      <div class="aqi-label" style="color:{r['color']}">{r['label']}</div>
      {f'<div class="dominant-badge">Primary: {dom}</div>' if dom else ''}
      <div class="aqi-detail">PM2.5 {r.get('pm2_5', '—')} · PM10 {r.get('pm10', '—')} µg/m³</div>
      <button class="details-toggle" aria-expanded="false" aria-controls="details-{safe_id}"
              onclick="toggleDetails(this, 'details-{safe_id}')">Details ▾</button>
      <div class="city-details" id="details-{safe_id}" hidden>
        <div class="advisory-text">{r.get('advisory', '')}</div>
        {_pollutant_grid(r)}
        {_forecast_strip(r.get('forecast', []))}
        <div class="trend-wrap">{_sparkline_svg(trend_points)}</div>
      </div>
    </div>"""


def _city_data_js(cities: list) -> str:
    """Compact JS array of city data for the map, compare modal, and near-me feature."""
    rows = []
    for c in cities:
        r = c.get("reading", {})
        if "error" in r or r.get("us_aqi") is None:
            continue
        rows.append({
            "name": c["name"], "state": c["state"], "lat": c["lat"], "lon": c["lon"],
            "aqi": r["us_aqi"], "label": r["label"], "color": r["color"],
            "advisory": r.get("advisory", ""), "dominant": r.get("dominant_pollutant"),
            "pm2_5": r.get("pm2_5"), "pm10": r.get("pm10"),
        })
    return json.dumps(rows, ensure_ascii=False)


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    cities       = payload.get("cities", [])
    trends       = payload.get("trends", {})
    severe_cities = payload.get("severe_cities", [])

    valid = [c for c in cities if "error" not in c.get("reading", {}) and c["reading"].get("us_aqi") is not None]
    cards = "\n".join(_city_card(c, trends.get(c["name"], [])) for c in cities)

    avg_aqi = payload.get("national_avg") or (round(sum(c["reading"]["us_aqi"] for c in valid) / len(valid), 1) if valid else 0)
    worst = max(valid, key=lambda c: c["reading"]["us_aqi"]) if valid else None
    best  = min(valid, key=lambda c: c["reading"]["us_aqi"]) if valid else None

    severe_lookup = {c["name"]: c["reading"]["us_aqi"] for c in valid if c["name"] in severe_cities}
    severe_html = ""
    if severe_cities:
        items = " &middot; ".join(f"{name} ({severe_lookup.get(name, '?'):.0f})" for name in severe_cities[:10])
        severe_html = f"""
  <div class="severe-banner" role="status" aria-live="polite">
    ⚠️ <b>Severe air quality alert</b> — {items}
  </div>"""

    # pick a sky tint roughly matching the average reading's band
    sky_light, sky_dark = ("#bbf7d0", "#064e3b")
    for c in valid:
        if abs(c["reading"]["us_aqi"] - avg_aqi) <= 1:
            sky_light, sky_dark = _SKY.get(c["reading"]["color"], (sky_light, sky_dark))
            break

    city_data_js = _city_data_js(cities)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>India Air Quality Dashboard — {date_label}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root {{
    --bg:#0b1522; --surface:rgba(255,255,255,.04); --card:rgba(255,255,255,.06); --card-h:rgba(255,255,255,.1);
    --accent:#38bdf8; --text:#eef4fb; --muted:#90a4bb; --border:rgba(255,255,255,.1);
    --ring-bg:rgba(255,255,255,.08);
    --radius:22px; --shadow:0 10px 30px rgba(0,0,0,.35);
    --sky-a:{sky_dark}; --sky-b:#0b1522;
  }}
  body.light {{
    --bg:#f3f8fd; --surface:#fff; --card:#fff; --card-h:#f0f6fc;
    --accent:#0284c7; --text:#0f2338; --muted:#5b7389; --border:#dbe7f3;
    --ring-bg:#e6eef6; --shadow:0 10px 26px rgba(15,35,56,.08);
    --sky-a:{sky_light}; --sky-b:#f3f8fd;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'Poppins','Segoe UI',system-ui,sans-serif; color:var(--text); min-height:100vh;
    background:
      radial-gradient(900px 400px at 15% -10%, var(--sky-a) 0%, transparent 60%),
      radial-gradient(700px 350px at 100% 0%, var(--sky-a) 0%, transparent 55%),
      var(--bg);
    transition:background .4s;
  }}
  header {{
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    background:var(--surface); border-bottom:1px solid var(--border); padding:16px 26px;
    display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;
    position:sticky; top:0; z-index:100;
  }}
  .brand {{ display:flex; align-items:center; gap:12px; }}
  .brand-icon {{
    width:46px; height:46px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:1.4rem; background:linear-gradient(135deg,#38bdf8 0%,#818cf8 100%); box-shadow:var(--shadow);
  }}
  .brand-text h1 {{ font-size:1.12rem; font-weight:700; }}
  .brand-text p {{ font-size:.72rem; color:var(--muted); }}
  .header-stats {{ display:flex; gap:8px; flex-wrap:wrap; }}
  .stat-chip {{
    background:var(--card); border:1px solid var(--border); border-radius:999px;
    padding:5px 14px; font-size:.74rem; color:var(--muted);
  }}
  .stat-chip b {{ color:var(--text); }}
  .header-btns {{ display:flex; gap:8px; }}
  #theme-btn, #install-btn {{
    background:var(--card); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:8px 14px; cursor:pointer; font-size:.8rem; font-family:inherit;
  }}
  main {{ max-width:1200px; margin:0 auto; padding:26px; }}
  .severe-banner {{
    background:rgba(239,68,68,.14); border:1px solid rgba(239,68,68,.4); color:#fecaca;
    border-radius:var(--radius); padding:12px 18px; font-size:.82rem; margin-bottom:18px;
  }}
  body.light .severe-banner {{ color:#991b1b; background:rgba(239,68,68,.08); }}
  .nearme-banner {{
    background:var(--card); border:1px solid var(--accent); border-radius:var(--radius);
    padding:14px 18px; font-size:.82rem; margin-bottom:18px; display:none;
  }}
  .nearme-banner.show {{ display:block; }}
  .home-banner {{
    background:var(--card); border:1px solid #f59e0b; border-radius:var(--radius);
    padding:14px 18px; font-size:.82rem; margin-bottom:18px; display:none;
  }}
  .home-banner.show {{ display:block; }}
  .home-banner b {{ color:#f59e0b; }}
  .legend {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:22px; }}
  .legend-item {{
    display:flex; align-items:center; gap:6px; font-size:.7rem; color:var(--muted);
    background:var(--card); border:1px solid var(--border); border-radius:999px; padding:5px 10px;
  }}
  .legend-dot {{ width:9px; height:9px; border-radius:50%; }}
  .toolbar {{ display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap; }}
  #search {{
    flex:1; min-width:200px; padding:10px 16px; border-radius:999px; border:1px solid var(--border);
    background:var(--card); color:var(--text); font-family:inherit; outline:none;
  }}
  .sort-btn {{
    background:var(--card); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:9px 16px; cursor:pointer; font-size:.78rem; font-family:inherit;
  }}
  .sort-btn.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .cities-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:16px; }}
  .city-card {{
    background:var(--card); border:1px solid var(--border); border-radius:var(--radius);
    padding:20px 16px; box-shadow:var(--shadow); text-align:center;
    display:flex; flex-direction:column; align-items:center; gap:4px;
    transition:transform .15s, background .15s; position:relative;
  }}
  .home-pin-btn {{
    position:absolute; top:10px; left:10px; background:none; border:none; cursor:pointer;
    font-size:1rem; color:var(--muted); line-height:1; padding:2px;
  }}
  .home-pin-btn[aria-pressed="true"] {{ color:#f59e0b; }}
  .city-card:hover {{ transform:translateY(-3px); background:var(--card-h); }}
  .gauge {{
    width:92px; height:92px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    margin-bottom:8px;
  }}
  .gauge-inner {{
    width:72px; height:72px; border-radius:50%; background:var(--bg);
    display:flex; flex-direction:column; align-items:center; justify-content:center;
  }}
  body.light .gauge-inner {{ background:#fff; }}
  .gauge-value {{ font-size:1.25rem; font-weight:800; line-height:1; }}
  .gauge-unit {{ font-size:.58rem; color:var(--muted); letter-spacing:.08em; margin-top:2px; }}
  .city-name {{ font-weight:700; font-size:.92rem; }}
  .city-state {{ font-size:.66rem; color:var(--muted); font-weight:400; display:block; margin-top:1px; }}
  .aqi-label {{ font-size:.76rem; font-weight:600; }}
  .dominant-badge {{
    font-size:.64rem; color:var(--muted); background:var(--card-h); border-radius:999px;
    padding:2px 9px; margin-top:2px;
  }}
  .aqi-detail {{ font-size:.66rem; color:var(--muted); }}
  .aqi-unknown {{ color:var(--muted); font-size:.8rem; margin-top:10px; }}
  .details-toggle {{
    margin-top:8px; background:none; border:1px solid var(--border); border-radius:999px;
    color:var(--accent); padding:4px 12px; font-size:.68rem; cursor:pointer; font-family:inherit;
  }}
  .city-details {{ width:100%; text-align:left; margin-top:10px; border-top:1px dashed var(--border); padding-top:10px; }}
  .advisory-text {{ font-size:.7rem; color:var(--muted); line-height:1.5; margin-bottom:10px; }}
  .pollutant-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-bottom:10px; }}
  .pollutant-cell {{ background:var(--bg); border-radius:10px; padding:6px 4px; text-align:center; }}
  body.light .pollutant-cell {{ background:var(--ring-bg); }}
  .p-name {{ display:block; font-size:.6rem; color:var(--muted); }}
  .p-val {{ display:block; font-size:.78rem; font-weight:700; }}
  .p-unit {{ font-size:.56rem; color:var(--muted); }}
  .forecast-strip {{ display:flex; gap:5px; margin-bottom:10px; justify-content:space-between; }}
  .fc-chip {{
    flex:1; border:1px solid; border-radius:8px; padding:4px 2px; text-align:center;
    display:flex; flex-direction:column; gap:2px;
  }}
  .fc-day {{ font-size:.58rem; color:var(--muted); }}
  .fc-aqi {{ font-size:.74rem; font-weight:700; }}
  .sparkline {{ width:100%; height:36px; display:block; }}
  .trend-empty {{ font-size:.64rem; color:var(--muted); font-style:italic; }}
  .trend-range {{ font-size:.6rem; color:var(--muted); margin-top:2px; }}
  footer {{ text-align:center; color:var(--muted); font-size:.72rem; padding:26px; }}
  .disclaimer {{
    background:var(--card); border:1px solid var(--border); border-radius:var(--radius);
    padding:16px 20px; font-size:.78rem; color:var(--muted); margin:24px 0;
  }}
  #map-view {{ display:none; height:560px; border-radius:var(--radius); overflow:hidden; margin-bottom:18px; }}
  #map-view.show {{ display:block; }}
  .cities-grid.hide {{ display:none; }}
  .modal-overlay {{
    display:none; position:fixed; inset:0; background:rgba(0,0,0,.6); z-index:1000;
    align-items:center; justify-content:center; padding:20px;
  }}
  .modal-overlay.show {{ display:flex; }}
  .compare-modal {{
    background:var(--bg); border:1px solid var(--border); border-radius:var(--radius);
    padding:24px; max-width:640px; width:100%; max-height:85vh; overflow:auto;
  }}
  .compare-modal h3 {{ margin-bottom:14px; }}
  .compare-selects {{ display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap; }}
  .compare-selects select {{
    flex:1; min-width:160px; padding:9px 12px; border-radius:10px; border:1px solid var(--border);
    background:var(--card); color:var(--text); font-family:inherit;
  }}
  .compare-table {{ width:100%; border-collapse:collapse; }}
  .compare-table th, .compare-table td {{
    text-align:left; padding:8px 10px; font-size:.78rem; border-bottom:1px solid var(--border);
  }}
  .close-modal {{
    background:var(--card); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:7px 16px; cursor:pointer; font-size:.78rem; margin-top:14px; font-family:inherit;
  }}
</style>
</head>
<body>
<a href="../" title="Back to India Agents Hub" aria-label="Back to India Agents Hub" style="position:fixed;top:14px;left:14px;z-index:1500;background:rgba(0,0,0,0.55);color:#fff;padding:8px 14px;border-radius:20px;font-family:system-ui,sans-serif;font-size:0.82rem;text-decoration:none;backdrop-filter:blur(4px);box-shadow:0 4px 10px rgba(0,0,0,0.25);">🏠 Home</a>
<header>
  <div class="brand">
    <div class="brand-icon">🌤️</div>
    <div class="brand-text">
      <h1>India Air Quality Dashboard</h1>
      <p>{date_label}</p>
    </div>
  </div>
  <div class="header-stats">
    <span class="stat-chip">Updated <b id="generated-at">{generated_at}</b></span>
    <span class="stat-chip">Avg AQI <b>{avg_aqi}</b></span>
    {f'<span class="stat-chip">😷 Worst <b>{worst["name"]}</b> ({worst["reading"]["us_aqi"]:.0f})</span>' if worst else ''}
    {f'<span class="stat-chip">🌿 Best <b>{best["name"]}</b> ({best["reading"]["us_aqi"]:.0f})</span>' if best else ''}
  </div>
  <div class="header-btns">
    <button id="theme-btn" onclick="toggleTheme()">🌙 Night</button>
  </div>
</header>
<main>
  {severe_html}
  <div class="home-banner" id="home-banner" role="status" aria-live="polite"></div>
  <div class="nearme-banner" id="nearme-banner"></div>
  <div class="legend">
    <span class="legend-item"><span class="legend-dot" style="background:#22c55e"></span>Good 0-50</span>
    <span class="legend-item"><span class="legend-dot" style="background:#eab308"></span>Moderate 51-100</span>
    <span class="legend-item"><span class="legend-dot" style="background:#f97316"></span>Unhealthy (SG) 101-150</span>
    <span class="legend-item"><span class="legend-dot" style="background:#ef4444"></span>Unhealthy 151-200</span>
    <span class="legend-item"><span class="legend-dot" style="background:#a855f7"></span>Very Unhealthy 201-300</span>
    <span class="legend-item"><span class="legend-dot" style="background:#7f1d1d"></span>Hazardous 300+</span>
  </div>
  <div class="toolbar">
    <input id="search" type="text" placeholder="🔍 Search city or state…" oninput="filterCities()"/>
    <button class="sort-btn active" id="sort-worst" onclick="sortCities('worst')">Worst First</button>
    <button class="sort-btn" id="sort-best" onclick="sortCities('best')">Best First</button>
    <button class="sort-btn" id="sort-az" onclick="sortCities('az')">A–Z</button>
    <button class="sort-btn" id="map-toggle-btn" onclick="toggleMap()">🗺️ Map View</button>
    <button class="sort-btn" onclick="findNearMe()">📍 AQI Near Me</button>
    <button class="sort-btn" onclick="openCompare()">⚖️ Compare Cities</button>
  </div>
  <div id="map-view"></div>
  <div class="cities-grid" id="cities-grid">
    {cards}
  </div>
  <div class="disclaimer">
    ⚠️ Air quality data from Open-Meteo's free Air Quality API (model-based estimates, not official CPCB
    monitoring station readings). US EPA AQI scale (0-500) shown. Forecast is a model-derived daily peak,
    typically reliable ~5 days out. Dominant pollutant is a simplified ratio-based estimate, not an
    official EPA sub-index. For general awareness only.
  </div>
</main>
<footer>Built with free public air-quality data · No API key required</footer>

<div class="modal-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title">
  <div class="compare-modal">
    <h3 id="compare-title">⚖️ Compare Cities</h3>
    <div class="compare-selects">
      <select id="compare-a"></select>
      <select id="compare-b"></select>
    </div>
    <table class="compare-table" id="compare-table"></table>
    <button class="close-modal" onclick="closeCompare()">Close</button>
  </div>
</div>

<script>
  const CITY_DATA = {city_data_js};

  function toggleTheme() {{
    document.body.classList.toggle('light');
    const btn = document.getElementById('theme-btn');
    btn.textContent = document.body.classList.contains('light') ? '☀️ Day' : '🌙 Night';
    localStorage.setItem('aqi_theme', document.body.classList.contains('light') ? 'light' : 'dark');
  }}
  if (localStorage.getItem('aqi_theme') === 'light') {{
    document.body.classList.add('light');
    document.getElementById('theme-btn').textContent = '☀️ Day';
  }}

  // ── Home city pin (localStorage, persists across visits) ────────────────
  function toggleHomeCity(btn) {{
    const city = btn.dataset.city;
    const current = localStorage.getItem('aqi_home_city');
    const newHome = current === city ? null : city;
    if (newHome) localStorage.setItem('aqi_home_city', newHome);
    else localStorage.removeItem('aqi_home_city');
    _syncHomePins();
    renderHomeBanner();
  }}

  function _syncHomePins() {{
    const home = localStorage.getItem('aqi_home_city');
    document.querySelectorAll('.home-pin-btn').forEach(b => {{
      const isHome = b.dataset.city === home;
      b.setAttribute('aria-pressed', String(isHome));
    }});
  }}

  function renderHomeBanner() {{
    const banner = document.getElementById('home-banner');
    const home = localStorage.getItem('aqi_home_city');
    if (!home) {{ banner.classList.remove('show'); banner.innerHTML = ''; return; }}
    const c = CITY_DATA.find(x => x.name === home);
    if (!c) {{ banner.classList.remove('show'); banner.innerHTML = ''; return; }}
    banner.innerHTML = `📍 <b>${{c.name}}</b> (home city) &middot; AQI <b style="color:${{c.color}}">${{c.aqi.toFixed ? c.aqi.toFixed(0) : c.aqi}}</b> — ${{c.label}}. ${{c.advisory || ''}}`;
    banner.classList.add('show');
  }}

  _syncHomePins();
  renderHomeBanner();

  function filterCities() {{
    const q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('.city-card').forEach(card => {{
      const match = card.dataset.name.includes(q) || card.dataset.state.includes(q);
      card.style.display = match ? '' : 'none';
    }});
  }}

  function sortCities(mode) {{
    ['worst','best','az'].forEach(m => document.getElementById('sort-'+m).classList.toggle('active', m === mode));
    const grid = document.getElementById('cities-grid');
    const cards = Array.from(grid.querySelectorAll('.city-card'));
    cards.sort((a, b) => {{
      if (mode === 'az') return a.dataset.name.localeCompare(b.dataset.name);
      const av = parseFloat(a.dataset.aqi), bv = parseFloat(b.dataset.aqi);
      return mode === 'worst' ? bv - av : av - bv;
    }});
    cards.forEach(c => grid.appendChild(c));
  }}
  sortCities('worst');

  function toggleDetails(btn, id) {{
    const panel = document.getElementById(id);
    const expanded = !panel.hidden;
    panel.hidden = expanded;
    btn.setAttribute('aria-expanded', String(!expanded));
    btn.textContent = expanded ? 'Details ▾' : 'Details ▴';
  }}

  // ── Map view (Leaflet) ───────────────────────────────────────────────────
  let _map = null;
  function toggleMap() {{
    const mapDiv = document.getElementById('map-view');
    const grid = document.getElementById('cities-grid');
    const showing = mapDiv.classList.toggle('show');
    grid.classList.toggle('hide', showing);
    if (showing && !_map) {{
      _map = L.map('map-view').setView([22.5, 80], 5);
      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap contributors', maxZoom: 10,
      }}).addTo(_map);
      CITY_DATA.forEach(c => {{
        L.circleMarker([c.lat, c.lon], {{
          radius: 8, color: c.color, fillColor: c.color, fillOpacity: .8, weight: 1,
        }}).addTo(_map).bindPopup(`<b>${{c.name}}</b><br/>AQI ${{c.aqi}} (${{c.label}})`);
      }});
    }}
    if (showing) setTimeout(() => _map.invalidateSize(), 100);
  }}

  // ── AQI near me (geolocation + direct client-side Open-Meteo call) ──────
  function findNearMe() {{
    const banner = document.getElementById('nearme-banner');
    if (!navigator.geolocation) {{
      banner.textContent = 'Geolocation is not supported by this browser.';
      banner.classList.add('show');
      return;
    }}
    banner.textContent = '📍 Locating you…';
    banner.classList.add('show');
    navigator.geolocation.getCurrentPosition(async (pos) => {{
      const {{ latitude, longitude }} = pos.coords;
      try {{
        const url = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${{latitude}}&longitude=${{longitude}}&current=us_aqi,pm2_5,pm10`;
        const resp = await fetch(url);
        const data = await resp.json();
        const aqi = data.current && data.current.us_aqi;
        if (aqi == null) {{ banner.textContent = 'Could not fetch AQI for your location.'; return; }}
        banner.innerHTML = `📍 <b>Your location</b>: AQI ${{Math.round(aqi)}} · PM2.5 ${{data.current.pm2_5}} · PM10 ${{data.current.pm10}} µg/m³`;
      }} catch (e) {{
        banner.textContent = 'Could not fetch AQI for your location.';
      }}
    }}, () => {{
      banner.textContent = 'Location access denied — enable it to use "AQI Near Me".';
    }});
  }}

  // ── Compare cities modal ─────────────────────────────────────────────────
  function openCompare() {{
    const a = document.getElementById('compare-a'), b = document.getElementById('compare-b');
    if (!a.options.length) {{
      CITY_DATA.forEach((c, i) => {{
        const optA = new Option(c.name, i), optB = new Option(c.name, i);
        a.add(optA); b.add(optB);
      }});
      b.selectedIndex = Math.min(1, CITY_DATA.length - 1);
      a.onchange = b.onchange = renderCompare;
    }}
    document.getElementById('compare-overlay').classList.add('show');
    renderCompare();
  }}
  function closeCompare() {{ document.getElementById('compare-overlay').classList.remove('show'); }}
  function renderCompare() {{
    const a = CITY_DATA[document.getElementById('compare-a').value || 0];
    const b = CITY_DATA[document.getElementById('compare-b').value || 1];
    if (!a || !b) return;
    const rows = [
      ['AQI', a.aqi, b.aqi], ['Category', a.label, b.label],
      ['Dominant pollutant', a.dominant || '—', b.dominant || '—'],
      ['PM2.5 (µg/m³)', a.pm2_5, b.pm2_5], ['PM10 (µg/m³)', a.pm10, b.pm10],
    ];
    document.getElementById('compare-table').innerHTML =
      `<tr><th>${{a.name}}</th><th>Metric</th><th>${{b.name}}</th></tr>` +
      rows.map(([label, av, bv]) => `<tr><td>${{av}}</td><td>${{label}}</td><td>${{bv}}</td></tr>`).join('');
  }}
</script>
</body>
</html>"""
