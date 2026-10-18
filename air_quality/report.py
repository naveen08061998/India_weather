"""
Air Quality — HTML Dashboard Generator
=========================================
Atmospheric gauge aesthetic: soft rounded cards with circular conic-gradient
AQI dials and a sky-tinted background — deliberately distinct from the
other agents' flat card-grid dashboards.
"""

from __future__ import annotations

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


def _city_card(c: dict) -> str:
    r = c.get("reading", {})
    if "error" in r or r.get("us_aqi") is None:
        return f"""
    <div class="city-card unknown" data-name="{c['name'].lower()}" data-state="{c['state'].lower()}" data-aqi="-1">
      <div class="city-name">{c['name']} <span class="city-state">{c['state']}</span></div>
      <div class="aqi-unknown">☁️ Data unavailable</div>
    </div>"""
    aqi = r["us_aqi"]
    return f"""
    <div class="city-card" data-name="{c['name'].lower()}" data-state="{c['state'].lower()}" data-aqi="{aqi}">
      {_gauge(aqi, r['color'])}
      <div class="city-name">{c['name']} <span class="city-state">{c['state']}</span></div>
      <div class="aqi-label" style="color:{r['color']}">{r['label']}</div>
      <div class="aqi-detail">PM2.5 {r.get('pm2_5', '—')} · PM10 {r.get('pm10', '—')} µg/m³</div>
    </div>"""


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    cities       = payload.get("cities", [])

    cards = "\n".join(_city_card(c) for c in cities)

    valid = [c for c in cities if "error" not in c.get("reading", {}) and c["reading"].get("us_aqi") is not None]
    avg_aqi = round(sum(c["reading"]["us_aqi"] for c in valid) / len(valid), 1) if valid else 0
    worst = max(valid, key=lambda c: c["reading"]["us_aqi"]) if valid else None
    best  = min(valid, key=lambda c: c["reading"]["us_aqi"]) if valid else None

    # pick a sky tint roughly matching the average reading's band
    sky_light, sky_dark = ("#bbf7d0", "#064e3b")
    for c in valid:
        if abs(c["reading"]["us_aqi"] - avg_aqi) <= 1:
            sky_light, sky_dark = _SKY.get(c["reading"]["color"], (sky_light, sky_dark))
            break

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>India Air Quality Dashboard — {date_label}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
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
  #theme-btn {{
    background:var(--card); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:8px 14px; cursor:pointer; font-size:.8rem; font-family:inherit;
  }}
  main {{ max-width:1200px; margin:0 auto; padding:26px; }}
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
    transition:transform .15s, background .15s;
  }}
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
  .aqi-detail {{ font-size:.66rem; color:var(--muted); }}
  .aqi-unknown {{ color:var(--muted); font-size:.8rem; margin-top:10px; }}
  footer {{ text-align:center; color:var(--muted); font-size:.72rem; padding:26px; }}
  .disclaimer {{
    background:var(--card); border:1px solid var(--border); border-radius:var(--radius);
    padding:16px 20px; font-size:.78rem; color:var(--muted); margin:24px 0;
  }}
</style>
</head>
<body>
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
  <button id="theme-btn" onclick="toggleTheme()">🌙 Night</button>
</header>
<main>
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
  </div>
  <div class="cities-grid" id="cities-grid">
    {cards}
  </div>
  <div class="disclaimer">
    ⚠️ Air quality data from Open-Meteo's free Air Quality API (model-based estimates, not official CPCB
    monitoring station readings). US EPA AQI scale (0-500) shown. For general awareness only.
  </div>
</main>
<footer>Built with free public air-quality data · No API key required</footer>
<script>
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
</script>
</body>
</html>"""
