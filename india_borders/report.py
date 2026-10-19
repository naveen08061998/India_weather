"""
India Borders — Report Generator
===================================
Renders the Atlas-themed dashboard: a searchable grid of every Indian
state/UT with its land-border neighbours, international borders and
coastline status, plus a "border explorer" detail panel and leaderboard.

Theme: Topographic Atlas — parchment background, forest-green/teal ink,
serif display font, compass-rose motif. Distinct from every other agent's
theme in this hub (monochrome newsprint, maroon departure-board, amber
weather, navy+saffron parchment, dark glass stocks, blue/purple AQI).
"""

from __future__ import annotations

import json

CSS = """
:root {
  --bg: #f3ead3;
  --bg2: #ece0c2;
  --ink: #2b2118;
  --ink-soft: #5c4d3c;
  --accent: #1f5c47;
  --accent2: #9c6b2e;
  --line: #c9b78f;
  --card: #faf4e3;
  --shadow: 0 10px 24px rgba(43,33,24,0.12);
  --radius: 10px;
  font-family: 'Spectral', 'Georgia', serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background:
    repeating-linear-gradient(0deg, transparent, transparent 38px, rgba(201,183,143,0.35) 39px),
    repeating-linear-gradient(90deg, transparent, transparent 38px, rgba(201,183,143,0.25) 39px),
    linear-gradient(160deg, var(--bg), var(--bg2));
  color: var(--ink);
  font-family: 'Spectral', 'Georgia', serif;
  padding-bottom: 60px;
}
a { color: inherit; }

header.hero {
  padding: 36px 24px 28px;
  text-align: center;
  border-bottom: 3px double var(--accent);
  background: rgba(250,244,227,0.55);
}
.compass {
  font-size: 2.6rem;
  display: inline-block;
  margin-bottom: 6px;
  filter: drop-shadow(0 2px 2px rgba(0,0,0,0.15));
}
header.hero h1 {
  margin: 0;
  font-size: 2.4rem;
  letter-spacing: 1px;
  color: var(--accent);
  font-weight: 700;
}
header.hero p.sub {
  margin: 8px 0 0;
  color: var(--ink-soft);
  font-size: 1.05rem;
  font-style: italic;
}
header.hero p.meta {
  margin: 10px 0 0;
  color: var(--ink-soft);
  font-size: 0.82rem;
  letter-spacing: 0.5px;
}

.wrap { max-width: 1180px; margin: 0 auto; padding: 0 20px; }

.stats-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px;
  margin: 26px auto 10px;
}
.stat-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow);
  text-align: center;
}
.stat-card .num { font-size: 1.6rem; font-weight: 700; color: var(--accent); display: block; }
.stat-card .lbl { font-size: 0.78rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.6px; }
.stat-card .sub { font-size: 0.72rem; color: var(--ink-soft); margin-top: 2px; }

.toolbar {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  margin: 22px 0 14px;
}
#search {
  flex: 1; min-width: 220px;
  padding: 11px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--card);
  font-family: inherit; font-size: 0.95rem; color: var(--ink);
}
.chip {
  padding: 7px 14px;
  border: 1px solid var(--accent);
  border-radius: 20px;
  background: transparent;
  color: var(--accent);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}
.chip.active, .chip:hover { background: var(--accent); color: #fdf8ea; }

.legend { font-size: 0.74rem; color: var(--ink-soft); margin: 0 0 14px; }
.legend span { margin-right: 14px; }

#count-line { font-size: 0.82rem; color: var(--ink-soft); margin: 0 0 10px; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}
.region-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  position: relative;
}
.region-card:hover { transform: translateY(-3px); border-color: var(--accent); }
.region-card.selected { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(31,92,71,0.25), var(--shadow); }
.region-card.dimmed { opacity: 0.32; }
.region-card.neighbor-hl { border-color: var(--accent2); box-shadow: 0 0 0 3px rgba(156,107,46,0.3), var(--shadow); }

.region-card h3 { margin: 0 0 4px; font-size: 1.08rem; color: var(--ink); }
.badge-row { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0 8px; }
.badge {
  font-size: 0.66rem; padding: 2px 8px; border-radius: 10px;
  text-transform: uppercase; letter-spacing: 0.4px; font-weight: 600;
}
.badge.state { background: #e3ecd9; color: #355c2b; }
.badge.ut { background: #ead9ef; color: #6b2e8c; }
.badge.coastal { background: #d7ecf2; color: #15657d; }
.badge.intl { background: #f3dede; color: #a23b3b; }
.region-card .capital { font-size: 0.78rem; color: var(--ink-soft); margin-bottom: 4px; }
.region-card .nbr-count { font-size: 0.78rem; color: var(--accent); font-weight: 600; }

.detail-panel {
  display: none;
  margin-top: 22px;
  background: var(--card);
  border: 2px solid var(--accent);
  border-radius: var(--radius);
  padding: 22px 24px;
  box-shadow: var(--shadow);
}
.detail-panel.open { display: block; }
.detail-panel h2 { margin: 0 0 4px; color: var(--accent); font-size: 1.5rem; }
.detail-panel .dp-meta { font-size: 0.85rem; color: var(--ink-soft); margin-bottom: 12px; }
.detail-panel .dp-note { font-style: italic; color: var(--ink-soft); margin: 10px 0; font-size: 0.9rem; }
.dp-section { margin-top: 14px; }
.dp-section h4 { margin: 0 0 8px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.6px; color: var(--ink-soft); }
.chip-link {
  display: inline-block; margin: 0 6px 6px 0; padding: 6px 12px;
  background: #fdf8ea; border: 1px solid var(--line); border-radius: 16px;
  font-size: 0.82rem; cursor: pointer; transition: background 0.15s;
}
.chip-link:hover { background: #e3ecd9; border-color: var(--accent); }
.close-btn {
  float: right; background: none; border: none; font-size: 1.3rem; cursor: pointer; color: var(--ink-soft);
}

.leaderboard {
  margin-top: 34px;
}
.leaderboard h2 { color: var(--accent); font-size: 1.3rem; border-bottom: 2px solid var(--line); padding-bottom: 8px; }
.lb-row { display: flex; align-items: center; gap: 10px; margin: 8px 0; }
.lb-name { width: 150px; font-size: 0.85rem; flex-shrink: 0; }
.lb-bar-track { flex: 1; background: #e5dcc3; border-radius: 6px; overflow: hidden; height: 16px; }
.lb-bar { background: linear-gradient(90deg, var(--accent), var(--accent2)); height: 100%; border-radius: 6px; }
.lb-val { width: 26px; font-size: 0.8rem; text-align: right; color: var(--ink-soft); }

footer {
  text-align: center; margin-top: 40px; padding: 18px; color: var(--ink-soft); font-size: 0.78rem;
}
@media (max-width: 560px) {
  header.hero h1 { font-size: 1.7rem; }
  .lb-name { width: 100px; font-size: 0.75rem; }
}
"""


def _badge_row(r: dict) -> str:
    badges = [f'<span class="badge {"state" if r["type"]=="State" else "ut"}">{r["type"]}</span>']
    if r["coastal"]:
        badges.append('<span class="badge coastal">Coastal</span>')
    if r["countries"]:
        badges.append('<span class="badge intl">International</span>')
    return '<div class="badge-row">' + "".join(badges) + "</div>"


def _region_card(r: dict) -> str:
    nbr_count = len(r["land_neighbors"])
    nbr_text = "No land neighbours" if nbr_count == 0 else f"{nbr_count} neighbour{'s' if nbr_count != 1 else ''}"
    return f'''
<div class="region-card" data-key="{r['key']}" data-name="{r['name'].lower()}" data-type="{r['type']}"
     data-coastal="{str(r['coastal']).lower()}" data-intl="{str(bool(r['countries'])).lower()}"
     onclick="selectRegion('{r['key']}')">
  <h3>{r['name']}</h3>
  {_badge_row(r)}
  <div class="capital">Capital: {r['capital']}</div>
  <div class="nbr-count">{nbr_text}</div>
</div>'''


def _leaderboard_row(name: str, count: int, max_count: int) -> str:
    pct = round((count / max_count) * 100) if max_count else 0
    return f'''
<div class="lb-row">
  <div class="lb-name">{name}</div>
  <div class="lb-bar-track"><div class="lb-bar" style="width:{pct}%"></div></div>
  <div class="lb-val">{count}</div>
</div>'''


def build_html(payload: dict) -> str:
    regions = payload["regions"]
    stats = payload["stats"]

    cards_html = "\n".join(_region_card(r) for r in sorted(regions.values(), key=lambda x: x["name"]))

    ranked = sorted(regions.values(), key=lambda x: len(x["land_neighbors"]), reverse=True)[:8]
    max_count = len(ranked[0]["land_neighbors"]) if ranked else 1
    leaderboard_html = "\n".join(_leaderboard_row(r["name"], len(r["land_neighbors"]), max_count) for r in ranked)

    most_borders = regions[stats["most_borders_key"]]
    most_countries = regions[stats["most_countries_key"]]
    island_names = ", ".join(regions[k]["name"] for k in stats["island_only"]) or "None"

    regions_json = json.dumps(regions, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>India Borders Atlas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header class="hero">
  <div class="compass">🧭</div>
  <h1>India Borders Atlas</h1>
  <p class="sub">Which state or union territory shares a border with which — mapped, searched and explored.</p>
  <p class="meta">Compiled {payload['date']} &middot; {stats['total_regions']} states &amp; union territories</p>
</header>

<div class="wrap">

  <div class="stats-strip">
    <div class="stat-card">
      <span class="num">{stats['total_regions']}</span>
      <span class="lbl">States &amp; UTs</span>
    </div>
    <div class="stat-card">
      <span class="num">{stats['most_borders_count']}</span>
      <span class="lbl">Most Borders</span>
      <div class="sub">{most_borders['name']}</div>
    </div>
    <div class="stat-card">
      <span class="num">{stats['coastal_count']}</span>
      <span class="lbl">Coastal</span>
    </div>
    <div class="stat-card">
      <span class="num">{stats['most_countries_count']}</span>
      <span class="lbl">Most Countries Bordered</span>
      <div class="sub">{most_countries['name']}</div>
    </div>
    <div class="stat-card">
      <span class="num">{len(stats['island_only'])}</span>
      <span class="lbl">No Land Borders</span>
      <div class="sub">{island_names}</div>
    </div>
  </div>

  <div class="toolbar">
    <input id="search" type="text" placeholder="Search a state or union territory…" oninput="filterRegions()">
    <button class="chip active" data-filter="all" onclick="setFilter('all', this)">All</button>
    <button class="chip" data-filter="State" onclick="setFilter('State', this)">States</button>
    <button class="chip" data-filter="Union Territory" onclick="setFilter('Union Territory', this)">UTs</button>
    <button class="chip" data-filter="coastal" onclick="setFilter('coastal', this)">Coastal</button>
    <button class="chip" data-filter="intl" onclick="setFilter('intl', this)">International Border</button>
  </div>

  <div class="legend">
    <span><strong>Tip:</strong> click any card to see its full neighbour list</span>
  </div>

  <p id="count-line"></p>

  <div class="grid" id="grid">
    {cards_html}
  </div>

  <div class="detail-panel" id="detail-panel">
    <button class="close-btn" onclick="closeDetail()">✕</button>
    <div id="detail-content"></div>
  </div>

  <div class="leaderboard">
    <h2>Border Leaderboard — Most Neighbouring States/UTs</h2>
    {leaderboard_html}
  </div>

</div>

<footer>India Borders Atlas &middot; Static geographic reference data &middot; Generated {payload['generated_at']}</footer>

<script>
const REGIONS = {regions_json};
let currentFilter = 'all';
let selectedKey = null;

function cardEls() {{ return document.querySelectorAll('.region-card'); }}

function setFilter(f, btn) {{
  currentFilter = f;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  filterRegions();
}}

function filterRegions() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  let shown = 0;
  cardEls().forEach(card => {{
    const name = card.dataset.name;
    const type = card.dataset.type;
    const coastal = card.dataset.coastal === 'true';
    const intl = card.dataset.intl === 'true';
    let pass = name.includes(q);
    if (pass) {{
      if (currentFilter === 'State' || currentFilter === 'Union Territory') pass = type === currentFilter;
      else if (currentFilter === 'coastal') pass = coastal;
      else if (currentFilter === 'intl') pass = intl;
    }}
    card.style.display = pass ? '' : 'none';
    if (pass) shown++;
  }});
  document.getElementById('count-line').textContent = `Showing ${{shown}} of {stats['total_regions']}`;
}}

function selectRegion(key) {{
  selectedKey = key;
  const region = REGIONS[key];
  cardEls().forEach(card => {{
    card.classList.remove('selected', 'dimmed', 'neighbor-hl');
    if (card.dataset.key === key) card.classList.add('selected');
    else if (region.land_neighbors.includes(card.dataset.key)) card.classList.add('neighbor-hl');
    else card.classList.add('dimmed');
  }});
  renderDetail(region);
  document.getElementById('detail-panel').classList.add('open');
  document.getElementById('detail-panel').scrollIntoView({{behavior: 'smooth', block: 'center'}});
}}

function closeDetail() {{
  selectedKey = null;
  cardEls().forEach(card => card.classList.remove('selected', 'dimmed', 'neighbor-hl'));
  document.getElementById('detail-panel').classList.remove('open');
}}

function renderDetail(region) {{
  const neighborChips = region.land_neighbors.length
    ? region.land_neighbors.map(k => `<span class="chip-link" onclick="selectRegion('${{k}}')">${{REGIONS[k].name}}</span>`).join('')
    : '<em>No land neighbours — surrounded entirely by sea.</em>';
  const countryChips = region.countries.length
    ? region.countries.map(c => `<span class="chip-link" style="cursor:default">🌍 ${{c}}</span>`).join('')
    : '<em>None</em>';
  const noteHtml = region.note ? `<p class="dp-note">${{region.note}}</p>` : '';
  document.getElementById('detail-content').innerHTML = `
    <h2>${{region.name}}</h2>
    <div class="dp-meta">${{region.type}} &middot; Capital: ${{region.capital}} ${{region.coastal ? '&middot; Coastal' : ''}}</div>
    ${{noteHtml}}
    <div class="dp-section">
      <h4>Shares a border with (${{region.land_neighbors.length}})</h4>
      ${{neighborChips}}
    </div>
    <div class="dp-section">
      <h4>International borders</h4>
      ${{countryChips}}
    </div>
  `;
}}

filterRegions();
</script>

</body>
</html>'''
