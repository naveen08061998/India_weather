"""
India Highways — Report Generator
====================================
Renders the Highway-Signage themed dashboard: searchable/sortable National
Highway corridors, a State Highway share breakdown (honest about data
limits), and wider road-network context stats.

Theme: Highway Signage — asphalt dark background, yellow road-marking
accents, hexagonal highway-shield badges, condensed signage font. Distinct
from every other agent's theme in this hub.
"""

from __future__ import annotations

import json

CSS = """
:root {
  --bg: #1b1d21;
  --bg2: #24262b;
  --asphalt: #2d3036;
  --ink: #f2f3f0;
  --ink-soft: #a7acb5;
  --yellow: #ffc93c;
  --yellow-dim: #cfa32b;
  --green: #2e7d4f;
  --red: #c0392b;
  --card: #26282e;
  --line: #3a3d44;
  --shadow: 0 10px 26px rgba(0,0,0,0.45);
  --radius: 10px;
  font-family: 'Rajdhani', 'Arial Narrow', sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background:
    repeating-linear-gradient(90deg, transparent, transparent 70px, rgba(255,201,60,0.06) 70px, rgba(255,201,60,0.06) 110px),
    linear-gradient(180deg, var(--bg), var(--bg2));
  color: var(--ink);
  font-family: 'Rajdhani', 'Arial Narrow', sans-serif;
  padding-bottom: 60px;
}

header.hero {
  padding: 34px 24px 26px;
  text-align: center;
  background: var(--asphalt);
  border-bottom: 6px solid var(--yellow);
  position: relative;
}
header.hero::after {
  content: "";
  position: absolute; left: 0; right: 0; bottom: -3px; height: 3px;
  background: repeating-linear-gradient(90deg, var(--ink) 0 30px, transparent 30px 55px);
  opacity: 0.5;
}
.shield {
  display: inline-flex; align-items: center; justify-content: center;
  width: 58px; height: 52px;
  background: var(--yellow); color: #1b1d21;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  font-weight: 800; font-size: 1.1rem; margin-bottom: 10px;
}
header.hero h1 {
  margin: 0; font-size: 2.5rem; letter-spacing: 1.5px; font-weight: 700;
  color: var(--ink); text-transform: uppercase;
}
header.hero p.sub { margin: 8px 0 0; color: var(--ink-soft); font-size: 1.05rem; }
header.hero p.meta { margin: 10px 0 0; color: var(--yellow-dim); font-size: 0.82rem; letter-spacing: 0.6px; text-transform: uppercase; }

.wrap { max-width: 1180px; margin: 0 auto; padding: 0 20px; }

.stats-strip {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px; margin: 26px auto 10px;
}
.stat-card {
  background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--yellow);
  border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow);
}
.stat-card .num { font-size: 1.7rem; font-weight: 700; color: var(--yellow); display: block; }
.stat-card .lbl { font-size: 0.76rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.6px; }
.stat-card .sub { font-size: 0.74rem; color: var(--ink-soft); margin-top: 3px; }

h2.section-title {
  color: var(--yellow); font-size: 1.4rem; text-transform: uppercase; letter-spacing: 1px;
  border-bottom: 3px solid var(--line); padding-bottom: 8px; margin: 34px 0 16px;
}

.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 14px; }
#search {
  flex: 1; min-width: 220px; padding: 11px 14px; border: 1px solid var(--line);
  border-radius: 8px; background: var(--card); font-family: inherit; font-size: 1rem; color: var(--ink);
}
.chip {
  padding: 7px 16px; border: 1px solid var(--yellow); border-radius: 4px;
  background: transparent; color: var(--yellow); font-size: 0.85rem; font-weight: 600;
  cursor: pointer; font-family: inherit; text-transform: uppercase; letter-spacing: 0.4px;
  transition: background 0.15s, color 0.15s;
}
.chip.active, .chip:hover { background: var(--yellow); color: #1b1d21; }
select#sort-select {
  padding: 9px 12px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--card); color: var(--ink); font-family: inherit; font-size: 0.85rem;
}

#count-line { font-size: 0.82rem; color: var(--ink-soft); margin: 0 0 10px; }

.nh-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.nh-card {
  background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 14px 16px; box-shadow: var(--shadow); cursor: pointer; transition: transform 0.15s, border-color 0.15s;
}
.nh-card:hover { transform: translateY(-3px); border-color: var(--yellow); }
.nh-card .nh-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.nh-shield {
  flex-shrink: 0; width: 46px; height: 40px;
  background: var(--yellow); color: #1b1d21; font-weight: 800; font-size: 0.78rem;
  display: flex; align-items: center; justify-content: center; text-align: center;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  line-height: 1.05;
}
.nh-card.historic .nh-shield { background: var(--ink-soft); }
.nh-route { font-size: 0.92rem; font-weight: 600; line-height: 1.3; }
.nh-length { color: var(--yellow); font-weight: 700; font-size: 1rem; }
.nh-card.historic .nh-length { color: var(--ink-soft); }
.nh-states { font-size: 0.78rem; color: var(--ink-soft); margin-top: 6px; }
.tag-historic {
  display: inline-block; margin-top: 6px; font-size: 0.68rem; padding: 2px 8px; border-radius: 10px;
  background: #4a4d55; color: #d7dae0; text-transform: uppercase; letter-spacing: 0.5px;
}

.detail-panel {
  display: none; margin-top: 20px; background: var(--card); border: 2px solid var(--yellow);
  border-radius: var(--radius); padding: 22px 24px; box-shadow: var(--shadow);
}
.detail-panel.open { display: block; }
.detail-panel h3 { margin: 0 0 4px; color: var(--yellow); font-size: 1.4rem; }
.detail-panel .dp-meta { font-size: 0.88rem; color: var(--ink-soft); margin-bottom: 10px; }
.detail-panel .dp-note { font-size: 0.92rem; margin: 10px 0; }
.close-btn { float: right; background: none; border: none; font-size: 1.3rem; cursor: pointer; color: var(--ink-soft); }

.sh-wrap { display: grid; grid-template-columns: 1.3fr 1fr; gap: 20px; }
@media (max-width: 760px) { .sh-wrap { grid-template-columns: 1fr; } }
.sh-bars { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.sh-row { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
.sh-name { width: 120px; font-size: 0.88rem; flex-shrink: 0; font-weight: 600; }
.sh-track { flex: 1; background: var(--line); border-radius: 6px; overflow: hidden; height: 18px; }
.sh-bar { background: linear-gradient(90deg, var(--yellow-dim), var(--yellow)); height: 100%; }
.sh-bar.unlisted { background: var(--ink-soft); }
.sh-val { width: 54px; text-align: right; font-size: 0.85rem; color: var(--ink-soft); }
.sh-info { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.sh-info .big { font-size: 1.8rem; color: var(--yellow); font-weight: 700; }
.sh-info .note { font-size: 0.82rem; color: var(--ink-soft); margin-top: 10px; line-height: 1.5; }

.network-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 6px; }
.net-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 18px; box-shadow: var(--shadow); }
.net-card .num { font-size: 1.5rem; color: var(--yellow); font-weight: 700; }
.net-card .lbl { font-size: 0.78rem; color: var(--ink-soft); margin-top: 4px; }

footer { text-align: center; margin-top: 40px; padding: 18px; color: var(--ink-soft); font-size: 0.78rem; }
@media (max-width: 560px) { header.hero h1 { font-size: 1.8rem; } }
"""


def _nh_card(h: dict) -> str:
    historic_cls = "historic" if h["status"] == "historic" else ""
    tag = '<span class="tag-historic">Historic / renumbered</span>' if h["status"] == "historic" else ""
    states_preview = ", ".join(h["states"][:3]) + (f" +{len(h['states'])-3} more" if len(h["states"]) > 3 else "")
    return f'''
<div class="nh-card {historic_cls}" data-number="{h['number'].lower()}" data-route="{h['route'].lower()}"
     data-status="{h['status']}" data-length="{h['length_km']}" onclick="showNhDetail('{h['number']}')">
  <div class="nh-head">
    <div class="nh-shield">{h['number'].replace(' (historic)', '').replace('NH', 'NH ')}</div>
    <div class="nh-route">{h['route']}</div>
  </div>
  <div class="nh-length">{h['length_km']:,} km</div>
  <div class="nh-states">{states_preview}</div>
  {tag}
</div>'''


def _sh_row(name: str, pct: float, max_pct: float, unlisted: bool = False) -> str:
    width = round((pct / max_pct) * 100) if max_pct else 0
    cls = "unlisted" if unlisted else ""
    return f'''
<div class="sh-row">
  <div class="sh-name">{name}</div>
  <div class="sh-track"><div class="sh-bar {cls}" style="width:{width}%"></div></div>
  <div class="sh-val">{pct}%</div>
</div>'''


def build_html(payload: dict) -> str:
    nh_list = payload["national_highways"]
    sh = payload["state_highway_summary"]
    net = payload["road_network_stats"]
    stats = payload["stats"]

    cards_html = "\n".join(_nh_card(h) for h in sorted(nh_list, key=lambda h: h["length_km"], reverse=True))

    top_states = sh["top_states_by_share"]
    max_pct = top_states[0]["share_pct"]
    sh_rows = "\n".join(_sh_row(s["state"], s["share_pct"], max_pct) for s in top_states)
    sh_rows += _sh_row("All other states/UTs", sh["unlisted_share_pct"], max_pct, unlisted=True)

    nh_json = json.dumps(nh_list, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>India Highways</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header class="hero">
  <div class="shield">NH</div>
  <h1>India Highways</h1>
  <p class="sub">Major National Highway corridors, state-highway shares &amp; the road network that connects a subcontinent.</p>
  <p class="meta">Compiled {payload['date']} &middot; MoRTH / NHAI published figures</p>
</header>

<div class="wrap">

  <div class="stats-strip">
    <div class="stat-card">
      <span class="num">{stats['current_count']}</span>
      <span class="lbl">Current NH Corridors</span>
    </div>
    <div class="stat-card">
      <span class="num">{stats['longest']['length_km']:,}</span>
      <span class="lbl">Longest — {stats['longest']['number']}</span>
      <div class="sub">{stats['longest']['route']}</div>
    </div>
    <div class="stat-card">
      <span class="num">{stats['shortest']['length_km']:,}</span>
      <span class="lbl">Shortest — {stats['shortest']['number']}</span>
      <div class="sub">{stats['shortest']['route']}</div>
    </div>
    <div class="stat-card">
      <span class="num">{stats['historic_count']}</span>
      <span class="lbl">Historic / Renumbered</span>
      <div class="sub">Pre-2010 MoRTH numbering</div>
    </div>
  </div>

  <h2 class="section-title">National Highway Corridors</h2>
  <div class="toolbar">
    <input id="search" type="text" placeholder="Search by number, city or route…" oninput="filterNh()">
    <button class="chip active" data-filter="all" onclick="setNhFilter('all', this)">All</button>
    <button class="chip" data-filter="current" onclick="setNhFilter('current', this)">Current</button>
    <button class="chip" data-filter="historic" onclick="setNhFilter('historic', this)">Historic</button>
    <select id="sort-select" onchange="sortNh()">
      <option value="length-desc">Length: Longest first</option>
      <option value="length-asc">Length: Shortest first</option>
      <option value="number">Number</option>
    </select>
  </div>
  <p id="count-line"></p>
  <div class="nh-grid" id="nh-grid">
    {cards_html}
  </div>

  <div class="detail-panel" id="detail-panel">
    <button class="close-btn" onclick="closeDetail()">✕</button>
    <div id="detail-content"></div>
  </div>

  <h2 class="section-title">State Highway Share (Top Published States)</h2>
  <div class="sh-wrap">
    <div class="sh-bars">
      {sh_rows}
    </div>
    <div class="sh-info">
      <div class="big">{sh['total_km_low']:,}–{sh['total_km_high']:,} km</div>
      <div class="lbl" style="color:var(--ink-soft);font-size:0.8rem;text-transform:uppercase;">Total State Highways (as of {sh['as_of']})</div>
      <div class="note">{sh['source_note']} Only the 5 states above have an individually-published share in the sources consulted — the remaining {sh['unlisted_share_pct']}% is known to be spread across all other states/UTs, but no granular public breakdown exists, so it is shown as a single "other" bar rather than invented per-state numbers.</div>
    </div>
  </div>

  <h2 class="section-title">Road Network Context</h2>
  <div class="network-stats">
    <div class="net-card"><div class="num">{net['total_road_network_km']:,} km</div><div class="lbl">Total Road Network — world's largest</div></div>
    <div class="net-card"><div class="num">{net['nh_expressway_km']:,} km</div><div class="lbl">NH + Expressways (as of {net['nh_expressway_as_of']})</div></div>
    <div class="net-card"><div class="num">{net['district_roads_km']:,} km</div><div class="lbl">District Roads</div></div>
    <div class="net-card"><div class="num">{net['rural_roads_share_pct']}%</div><div class="lbl">Share That Are Rural Roads</div></div>
  </div>

</div>

<footer>India Highways &middot; Static reference data from published MoRTH/NHAI figures &middot; Generated {payload['generated_at']}</footer>

<script>
const NH_DATA = {nh_json};
let nhFilter = 'all';

function setNhFilter(f, btn) {{
  nhFilter = f;
  document.querySelectorAll('.toolbar .chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  filterNh();
}}

function filterNh() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  let shown = 0;
  document.querySelectorAll('.nh-card').forEach(card => {{
    const matchesText = card.dataset.number.includes(q) || card.dataset.route.includes(q);
    const matchesFilter = nhFilter === 'all' || card.dataset.status === nhFilter;
    const pass = matchesText && matchesFilter;
    card.style.display = pass ? '' : 'none';
    if (pass) shown++;
  }});
  document.getElementById('count-line').textContent = `Showing ${{shown}} of {len(nh_list)} highways`;
}}

function sortNh() {{
  const mode = document.getElementById('sort-select').value;
  const grid = document.getElementById('nh-grid');
  const cards = Array.from(grid.children);
  cards.sort((a, b) => {{
    if (mode === 'length-desc') return b.dataset.length - a.dataset.length;
    if (mode === 'length-asc') return a.dataset.length - b.dataset.length;
    return a.dataset.number.localeCompare(b.dataset.number);
  }});
  cards.forEach(c => grid.appendChild(c));
}}

function showNhDetail(number) {{
  const h = NH_DATA.find(x => x.number === number);
  if (!h) return;
  document.getElementById('detail-content').innerHTML = `
    <h3>${{h.number}} — ${{h.route}}</h3>
    <div class="dp-meta">${{h.length_km.toLocaleString()}} km &middot; ${{h.states.length}} states/UTs crossed ${{h.status === 'historic' ? '&middot; Historic numbering' : ''}}</div>
    <p class="dp-note">${{h.note}}</p>
    <div class="dp-meta"><strong>States crossed:</strong> ${{h.states.join(', ')}}</div>
  `;
  document.getElementById('detail-panel').classList.add('open');
  document.getElementById('detail-panel').scrollIntoView({{behavior: 'smooth', block: 'center'}});
}}

function closeDetail() {{
  document.getElementById('detail-panel').classList.remove('open');
}}

filterNh();
</script>

</body>
</html>'''
