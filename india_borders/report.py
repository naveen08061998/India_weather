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

.nbr-row { margin: 0 0 8px; }
.nbr-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.district-toggle {
  background: none; border: 1px dashed var(--line); color: var(--ink-soft); border-radius: 12px;
  padding: 3px 10px; font-size: 0.72rem; cursor: pointer; font-family: inherit;
}
.district-toggle:hover { border-color: var(--accent2); color: var(--accent2); }
.district-box {
  display: none; margin: 6px 0 0 4px; padding: 8px 12px; background: #fdf8ea;
  border-left: 3px solid var(--accent2); border-radius: 0 8px 8px 0; font-size: 0.8rem; line-height: 1.6;
}
.district-box.show { display: block; }
.district-box .d-side { margin-bottom: 4px; }
.district-box .d-label { font-weight: 600; color: var(--accent2); }
.district-box .d-empty { font-style: italic; color: var(--ink-soft); }

.district-disclaimer {
  font-size: 0.72rem; color: var(--ink-soft); font-style: italic; margin-top: 10px;
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
.lb-rows.collapsed .lb-row:nth-child(n+9) { display: none; }
.show-more-btn {
  margin-top: 10px; background: none; border: 1px solid var(--accent); color: var(--accent);
  border-radius: 16px; padding: 6px 14px; font-size: 0.8rem; cursor: pointer; font-family: inherit;
}

h2.section-title2 {
  color: var(--accent); font-size: 1.3rem; border-bottom: 2px solid var(--line); padding-bottom: 8px; margin: 34px 0 16px;
}
.country-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.country-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); }
.country-card h4 { margin: 0 0 8px; color: var(--accent2); font-size: 1.05rem; }
.country-card .c-states { font-size: 0.82rem; line-height: 1.6; }

.length-rows .lb-row .lb-name { width: 120px; }

.checkpoint-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
.checkpoint-card { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent2); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); }
.checkpoint-card h4 { margin: 0 0 4px; font-size: 1rem; color: var(--ink); }
.checkpoint-card .cp-meta { font-size: 0.76rem; color: var(--accent2); margin-bottom: 6px; font-weight: 600; }
.checkpoint-card .cp-note { font-size: 0.82rem; color: var(--ink-soft); line-height: 1.5; }

.pathfinder-box { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.pf-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
.pf-row select {
  flex: 1; min-width: 180px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px;
  background: #fdf8ea; color: var(--ink); font-family: inherit; font-size: 0.9rem;
}
.pf-btn {
  background: var(--accent); color: #fdf8ea; border: none; border-radius: 8px;
  padding: 10px 18px; font-size: 0.88rem; cursor: pointer; font-family: inherit; font-weight: 600;
}
.pf-result { font-size: 0.92rem; line-height: 1.8; }
.pf-chip { display: inline-flex; align-items: center; gap: 6px; background: #fdf8ea; border: 1px solid var(--line); border-radius: 16px; padding: 5px 12px; margin: 0 4px 6px 0; font-size: 0.84rem; }
.pf-arrow { color: var(--accent2); font-weight: 700; }

.quiz-box { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.quiz-q { font-size: 0.98rem; font-weight: 600; margin-bottom: 12px; }
.quiz-opts { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.quiz-opt {
  text-align: left; padding: 10px 14px; border: 1px solid var(--line); border-radius: 8px;
  background: #fdf8ea; cursor: pointer; font-family: inherit; font-size: 0.88rem; color: var(--ink);
}
.quiz-opt:hover { border-color: var(--accent); }
.quiz-opt.correct { background: #e3ecd9; border-color: #355c2b; }
.quiz-opt.wrong { background: #f3dede; border-color: #a23b3b; }
.quiz-progress { font-size: 0.78rem; color: var(--ink-soft); margin-bottom: 6px; }
.quiz-next-btn { display: none; }
.quiz-next-btn.show { display: inline-block; }

.modal-overlay {
  display: none; position: fixed; inset: 0; background: rgba(43,33,24,0.55); z-index: 1000;
  align-items: center; justify-content: center; padding: 20px;
}
.modal-overlay.show { display: flex; }
.compare-modal {
  background: var(--bg); border: 2px solid var(--accent); border-radius: var(--radius);
  padding: 24px; max-width: 640px; width: 100%; max-height: 85vh; overflow: auto; box-shadow: var(--shadow);
}
.compare-modal h3 { color: var(--accent); margin-bottom: 14px; }
.compare-selects { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.compare-selects select {
  flex: 1; min-width: 160px; padding: 10px; border: 1px solid var(--line); border-radius: 8px;
  background: #fdf8ea; color: var(--ink); font-family: inherit;
}
.compare-table { width: 100%; border-collapse: collapse; }
.compare-table th, .compare-table td { padding: 9px 10px; font-size: 0.85rem; border-bottom: 1px solid var(--line); text-align: left; }

#map-view { display: none; height: 560px; border-radius: var(--radius); overflow: hidden; margin-bottom: 18px; border: 1px solid var(--line); }
#map-view.show { display: block; }
.grid.map-hidden { display: none; }

.skip-link {
  position: absolute; left: -999px; top: 0; background: var(--accent); color: #fdf8ea;
  padding: 10px 16px; z-index: 2000; border-radius: 0 0 8px 0; font-size: 0.85rem;
}
.skip-link:focus { left: 0; }
.visually-hidden {
  position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap;
}

.dist-result { font-size: 0.95rem; margin-top: 10px; }
.dist-result strong { color: var(--accent); }

.interior-list { display: flex; flex-wrap: wrap; gap: 8px; }
.interior-chip {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 7px 14px;
  font-size: 0.86rem; cursor: pointer;
}
.interior-chip:hover { border-color: var(--accent); background: #e3ecd9; }

.enclave-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.enclave-card { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent2); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); }
.enclave-card h4 { margin: 0 0 6px; font-size: 1rem; color: var(--ink); }
.enclave-card p { font-size: 0.85rem; color: var(--ink-soft); line-height: 1.5; margin: 0; }
.enclave-card .ec-link { font-size: 0.78rem; color: var(--accent); cursor: pointer; margin-top: 8px; display: inline-block; }

.ndist-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 760px) { .ndist-cols { grid-template-columns: 1fr; } }
.ndist-col h4 { color: var(--accent2); font-size: 0.95rem; margin: 0 0 10px; }
.ndist-row { display: flex; justify-content: space-between; font-size: 0.85rem; padding: 7px 0; border-bottom: 1px dashed var(--line); }
.ndist-row .ndist-val { color: var(--accent); font-weight: 600; }
.ndist-note { font-size: 0.74rem; color: var(--ink-soft); font-style: italic; margin-top: 10px; }

.print-btn {
  background: none; border: 1px solid var(--accent2); color: var(--accent2); border-radius: 16px;
  padding: 5px 12px; font-size: 0.76rem; cursor: pointer; font-family: inherit; margin-left: 8px;
}
@media print {
  body * { visibility: hidden; }
  .detail-panel, .detail-panel * { visibility: visible; }
  .detail-panel { position: absolute; left: 0; top: 0; width: 100%; border: none; box-shadow: none; }
  .close-btn, .print-btn { display: none; }
}

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


def _country_card(country: str, states: list) -> str:
    chips = "".join(f'<div>&bull; {s}</div>' for s in states)
    return f'''
<div class="country-card">
  <h4>🌍 {country} <span style="font-weight:400;font-size:0.8rem;color:var(--ink-soft)">({len(states)} state{'s' if len(states) != 1 else ''})</span></h4>
  <div class="c-states">{chips}</div>
</div>'''


def _checkpoint_card(cp: dict, region_name: str) -> str:
    return f'''
<div class="checkpoint-card">
  <h4>{cp['name']}</h4>
  <div class="cp-meta">{region_name} &harr; {cp['country']}</div>
  <div class="cp-note">{cp['note']}</div>
</div>'''


def build_html(payload: dict) -> str:
    regions = payload["regions"]
    stats = payload["stats"]
    leaderboard = payload["leaderboard"]
    country_groups = payload["country_groups"]
    border_lengths = payload["border_lengths"]
    checkpoints = payload["border_checkpoints"]
    enclaves = payload["enclaves"]
    neighbor_distances = payload["neighbor_distances"]
    interior_regions = payload["interior_regions"]

    cards_html = "\n".join(_region_card(r) for r in sorted(regions.values(), key=lambda x: x["name"]))

    max_count = leaderboard[0]["count"] if leaderboard else 1
    leaderboard_html = "\n".join(_leaderboard_row(r["name"], r["count"], max_count) for r in leaderboard)

    country_html = "\n".join(
        _country_card(country, states)
        for country, states in sorted(country_groups.items(), key=lambda kv: len(kv[1]), reverse=True)
    )

    max_length = border_lengths[0]["length_km"]
    length_html = "\n".join(
        f'''<div class="lb-row"><div class="lb-name">{b['country']}</div>
<div class="lb-bar-track"><div class="lb-bar" style="width:{round(b['length_km']/max_length*100)}%"></div></div>
<div class="lb-val">{b['length_km']}</div></div>'''
        for b in border_lengths
    )
    length_notes_html = "\n".join(f"<p><strong>{b['country']}:</strong> {b['note']}</p>" for b in border_lengths)

    checkpoint_html = "\n".join(_checkpoint_card(cp, regions[cp["state_key"]]["name"]) for cp in checkpoints)

    most_borders = regions[stats["most_borders_key"]]
    most_countries = regions[stats["most_countries_key"]]
    island_names = ", ".join(regions[k]["name"] for k in stats["island_only"]) or "None"

    region_options = "".join(
        f'<option value="{r["key"]}">{r["name"]}</option>' for r in sorted(regions.values(), key=lambda x: x["name"])
    )

    enclave_html = "\n".join(
        f'''<div class="enclave-card">
  <h4>{e['title']}</h4>
  <p>{e['description']}</p>
  <span class="ec-link" onclick="selectRegion('{e['region_key']}');document.getElementById('detail-panel').scrollIntoView({{behavior:'smooth',block:'center'}})">View on map \u2192</span>
</div>'''
        for e in enclaves
    )

    shortest10 = neighbor_distances[:10]
    longest10 = neighbor_distances[-10:][::-1]
    shortest_html = "\n".join(
        f'<div class="ndist-row"><span>{r["a"]} \u2194 {r["b"]}</span><span class="ndist-val">{r["distance_km"]:,.0f} km</span></div>'
        for r in shortest10
    )
    longest_html = "\n".join(
        f'<div class="ndist-row"><span>{r["a"]} \u2194 {r["b"]}</span><span class="ndist-val">{r["distance_km"]:,.0f} km</span></div>'
        for r in longest10
    )

    interior_html = "".join(
        f'<span class="interior-chip" onclick="selectByName(\'{name}\')">{name}</span>' for name in interior_regions
    )

    regions_json = json.dumps(regions, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>India Borders Atlas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>{CSS}</style>
</head>
<body>

<a class="skip-link" href="#main-content">Skip to main content</a>
<a href="../" title="Back to India Agents Hub" aria-label="Back to India Agents Hub" style="position:fixed;top:14px;left:14px;z-index:1500;background:rgba(0,0,0,0.55);color:#fff;padding:8px 14px;border-radius:20px;font-family:system-ui,sans-serif;font-size:0.82rem;text-decoration:none;backdrop-filter:blur(4px);box-shadow:0 4px 10px rgba(0,0,0,0.25);">🏠 Home</a>

<header class="hero">
  <div class="compass">🧭</div>
  <h1>India Borders Atlas</h1>
  <p class="sub">Which state or union territory shares a border with which — mapped, searched and explored.</p>
  <p class="meta">Compiled {payload['date']} &middot; {stats['total_regions']} states &amp; union territories</p>
</header>

<main id="main-content" class="wrap">

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
    <label for="search" class="visually-hidden">Search a state or union territory</label>
    <input id="search" type="text" placeholder="Search a state or union territory…" oninput="filterRegions()">
    <button class="chip active" data-filter="all" onclick="setFilter('all', this)">All</button>
    <button class="chip" data-filter="State" onclick="setFilter('State', this)">States</button>
    <button class="chip" data-filter="Union Territory" onclick="setFilter('Union Territory', this)">UTs</button>
    <button class="chip" data-filter="coastal" onclick="setFilter('coastal', this)">Coastal</button>
    <button class="chip" data-filter="intl" onclick="setFilter('intl', this)">International Border</button>
    <button class="chip" id="map-toggle-btn" onclick="toggleMap()" aria-expanded="false">🗺️ Map View</button>
    <button class="chip" onclick="openCompare()">⚖️ Compare</button>
    <button class="chip" onclick="surpriseMe()">🎲 Surprise Me</button>
  </div>

  <div class="legend">
    <span><strong>Tip:</strong> click any card to see its full neighbour list</span>
  </div>

  <p id="count-line" role="status" aria-live="polite"></p>

  <div id="map-view"></div>

  <div class="grid" id="grid">
    {cards_html}
  </div>

  <div class="detail-panel" id="detail-panel">
    <button class="close-btn" onclick="closeDetail()">✕</button>
    <div id="detail-content"></div>
  </div>

  <div class="leaderboard">
    <h2>Border Leaderboard — All States/UTs by Neighbour Count</h2>
    <div class="lb-rows collapsed" id="lb-rows">
      {leaderboard_html}
    </div>
    <button class="show-more-btn" id="lb-toggle-btn" onclick="toggleLeaderboard()">Show all {stats['total_regions']} ▾</button>
  </div>

  <h2 class="section-title2">Who Borders Which Country</h2>
  <div class="country-grid">
    {country_html}
  </div>

  <h2 class="section-title2">International Border Lengths</h2>
  <div class="leaderboard" style="margin-top:0">
    <div class="length-rows">
      {length_html}
    </div>
    <div style="margin-top:14px;font-size:0.82rem;color:var(--ink-soft);line-height:1.6">
      {length_notes_html}
      <p style="margin-top:8px;font-style:italic">Approximate figures from published MEA/BSF sources; the China border is the Line of Actual Control (LAC), not a mutually demarcated boundary.</p>
    </div>
  </div>

  <h2 class="section-title2">Major Border Checkpoints</h2>
  <div class="checkpoint-grid">
    {checkpoint_html}
  </div>

  <h2 class="section-title2">Enclaves &amp; Exclaves</h2>
  <div class="enclave-grid">
    {enclave_html}
  </div>

  <h2 class="section-title2">Fully Interior — No Sea or International Border</h2>
  <div class="interior-list">
    {interior_html}
  </div>

  <h2 class="section-title2">Nearest &amp; Farthest Bordering Capitals</h2>
  <div class="ndist-cols">
    <div class="ndist-col">
      <h4>Closest neighbouring capitals</h4>
      {shortest_html}
    </div>
    <div class="ndist-col">
      <h4>Farthest neighbouring capitals</h4>
      {longest_html}
    </div>
  </div>
  <p class="ndist-note">Straight-line distance between each pair's official capitals. Some pairs show 0 km because they literally share the same capital city (Chandigarh serves as the joint capital of Punjab and Haryana, and is itself a separate UT).</p>

  <h2 class="section-title2">Capital-to-Capital Distance Calculator</h2>
  <div class="pathfinder-box">
    <div class="pf-row">
      <label for="dist-a" class="visually-hidden">First state/UT</label>
      <select id="dist-a"><option value="">Choose…</option>{region_options}</select>
      <label for="dist-b" class="visually-hidden">Second state/UT</label>
      <select id="dist-b"><option value="">Choose…</option>{region_options}</select>
      <button class="pf-btn" onclick="calcDistance()">Calculate Distance</button>
    </div>
    <div class="dist-result" id="dist-result">Pick any two states/UTs to see the straight-line distance between their capitals.</div>
  </div>

  <h2 class="section-title2">Border Path Finder</h2>
  <div class="pathfinder-box">
    <div class="pf-row">
      <label for="pf-from" class="visually-hidden">From</label>
      <select id="pf-from"><option value="">From…</option>{region_options}</select>
      <label for="pf-to" class="visually-hidden">To</label>
      <select id="pf-to"><option value="">To…</option>{region_options}</select>
      <button class="pf-btn" onclick="findPath()">Find Shortest Land Path</button>
    </div>
    <div class="pf-result" id="pf-result" role="status" aria-live="polite">Pick two states/UTs to find the shortest chain of shared land borders between them.</div>
  </div>

  <h2 class="section-title2">Border Trivia Quiz</h2>
  <div class="quiz-box" id="quiz-box"></div>

</main>

<footer role="contentinfo">India Borders Atlas &middot; Static geographic reference data &middot; Generated {payload['generated_at']}</footer>

<div class="modal-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title">
  <div class="compare-modal">
    <h3 id="compare-title">⚖️ Compare Two States/UTs</h3>
    <div class="compare-selects">
      <select id="compare-a">{region_options}</select>
      <select id="compare-b">{region_options}</select>
    </div>
    <table class="compare-table" id="compare-table"></table>
    <button class="show-more-btn" style="margin-top:16px" onclick="closeCompare()">Close</button>
  </div>
</div>

<script>
const REGIONS = {regions_json};
let currentFilter = 'all';
let selectedKey = null;

function cardEls() {{ return document.querySelectorAll('.region-card'); }}

function haversineKm(lat1, lon1, lat2, lon2) {{
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}}

function selectByName(name) {{
  const entry = Object.values(REGIONS).find(r => r.name === name);
  if (entry) {{
    selectRegion(entry.key);
    document.getElementById('detail-panel').scrollIntoView({{behavior: 'smooth', block: 'center'}});
  }}
}}

function surpriseMe() {{
  const keys = Object.keys(REGIONS);
  const pick = keys[Math.floor(Math.random() * keys.length)];
  selectRegion(pick);
}}

function calcDistance() {{
  const a = REGIONS[document.getElementById('dist-a').value];
  const b = REGIONS[document.getElementById('dist-b').value];
  const out = document.getElementById('dist-result');
  if (!a || !b) {{ out.innerHTML = 'Please choose both states/UTs.'; return; }}
  if (a.key === b.key) {{ out.innerHTML = 'Choose two different states/UTs.'; return; }}
  const km = haversineKm(a.lat, a.lon, b.lat, b.lon);
  out.innerHTML = `Straight-line distance between <strong>${{a.capital}}</strong> (${{a.name}}) and <strong>${{b.capital}}</strong> (${{b.name}}): <strong>${{km.toFixed(0)}} km</strong>`;
}}

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
  const neighborRows = region.land_neighbors.length
    ? region.land_neighbors.map(k => {{
        const nb = REGIONS[k];
        const bd = (region.border_districts || {{}})[k];
        const boxId = `district-box-${{region.key}}-${{k}}`;
        const districtBtn = bd
          ? `<button class="district-toggle" onclick="toggleDistricts('${{boxId}}', this)">Districts \u25be</button>`
          : '';
        const boxHtml = bd ? `
          <div class="district-box" id="${{boxId}}">
            <div class="d-side"><span class="d-label">${{region.name}}:</span> ${{bd.own.join(', ')}}</div>
            <div class="d-side"><span class="d-label">${{nb.name}}:</span> ${{bd.their.join(', ')}}</div>
          </div>` : '';
        return `<div class="nbr-row">
          <div class="nbr-head">
            <span class="chip-link" onclick="selectRegion('${{k}}')">${{nb.name}}</span>
            ${{districtBtn}}
          </div>
          ${{boxHtml}}
        </div>`;
      }}).join('')
    : '<em>No land neighbours — surrounded entirely by sea.</em>';
  const countryChips = region.countries.length
    ? region.countries.map(c => `<span class="chip-link" style="cursor:default">🌍 ${{c}}</span>`).join('')
    : '<em>None</em>';
  const noteHtml = region.note ? `<p class="dp-note">${{region.note}}</p>` : '';
  const nhChips = (region.national_highways || []).map(n => `<span class="chip-link" style="cursor:default">🛣️ ${{n}}</span>`).join('');
  const ewChips = (region.expressways || []).map(n => `<span class="chip-link" style="cursor:default">🛤️ ${{n}}</span>`).join('');
  const highwaysHtml = (nhChips || ewChips)
    ? `<div class="dp-section"><h4>Highways through this state</h4>${{nhChips}}${{ewChips}}
         <div class="district-disclaimer">Cross-referenced from the India Highways agent (National Highways + Expressways data).</div></div>`
    : '';
  document.getElementById('detail-content').innerHTML = `
    <h2>${{region.name}} <button class="print-btn" onclick="window.print()">🖨️ Print</button></h2>
    <div class="dp-meta">${{region.type}} &middot; Capital: ${{region.capital}} ${{region.coastal ? '&middot; Coastal' : ''}}</div>
    ${{noteHtml}}
    <div class="dp-section">
      <h4>Shares a border with (${{region.land_neighbors.length}})</h4>
      ${{neighborRows}}
      ${{region.land_neighbors.length ? '<div class="district-disclaimer">District lists are a best-effort reference (major, long-established districts along each border) — not exhaustive, and may not include every newly created district.</div>' : ''}}
    </div>
    <div class="dp-section">
      <h4>International borders</h4>
      ${{countryChips}}
    </div>
    ${{highwaysHtml}}
  `;
}}

function toggleDistricts(boxId, btn) {{
  const box = document.getElementById(boxId);
  const showing = box.classList.toggle('show');
  btn.textContent = showing ? 'Districts \u25b4' : 'Districts \u25be';
  btn.setAttribute('aria-expanded', showing ? 'true' : 'false');
}}

// ── Leaderboard show-all toggle ──
function toggleLeaderboard() {{
  const rows = document.getElementById('lb-rows');
  const btn = document.getElementById('lb-toggle-btn');
  const collapsed = rows.classList.toggle('collapsed');
  btn.textContent = collapsed ? 'Show all {stats["total_regions"]} \u25be' : 'Show top 8 \u25b4';
  btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
}}

// ── Path finder (BFS over land_neighbors) ──
function findPath() {{
  const from = document.getElementById('pf-from').value;
  const to = document.getElementById('pf-to').value;
  const out = document.getElementById('pf-result');
  if (!from || !to) {{ out.innerHTML = 'Please choose both a starting and ending state/UT.'; return; }}
  if (from === to) {{ out.innerHTML = 'Choose two different states/UTs.'; return; }}
  const queue = [[from]];
  const seen = new Set([from]);
  let path = null;
  while (queue.length) {{
    const p = queue.shift();
    const last = p[p.length - 1];
    if (last === to) {{ path = p; break; }}
    for (const nb of REGIONS[last].land_neighbors) {{
      if (!seen.has(nb)) {{ seen.add(nb); queue.push([...p, nb]); }}
    }}
  }}
  if (!path) {{
    out.innerHTML = `<em>No land-border path exists between ${{REGIONS[from].name}} and ${{REGIONS[to].name}} \u2014 one or both are only reachable by sea/air, or sit on separate landmasses.</em>`;
    return;
  }}
  const chips = path.map(k => `<span class="pf-chip">${{REGIONS[k].name}}</span>`).join('<span class="pf-arrow"> \u2192 </span>');
  let totalKm = 0;
  for (let i = 0; i < path.length - 1; i++) {{
    const a = REGIONS[path[i]], b = REGIONS[path[i + 1]];
    totalKm += haversineKm(a.lat, a.lon, b.lat, b.lon);
  }}
  out.innerHTML = `Shortest path (${{path.length - 1}} border crossing${{path.length - 1 !== 1 ? 's' : ''}}, approx. ${{totalKm.toFixed(0)}} km capital-to-capital): ${{chips}}`;
}}


// ── Compare modal ──
function openCompare() {{
  document.getElementById('compare-overlay').classList.add('show');
  renderCompare();
}}
function closeCompare() {{
  document.getElementById('compare-overlay').classList.remove('show');
}}
function renderCompare() {{
  const a = REGIONS[document.getElementById('compare-a').value];
  const b = REGIONS[document.getElementById('compare-b').value];
  const rows = [
    ['Type', a.type, b.type],
    ['Capital', a.capital, b.capital],
    ['Land neighbours', a.land_neighbors.length, b.land_neighbors.length],
    ['Countries bordered', a.countries.length ? a.countries.join(', ') : 'None', b.countries.length ? b.countries.join(', ') : 'None'],
    ['Coastal', a.coastal ? 'Yes' : 'No', b.coastal ? 'Yes' : 'No'],
    ['Shares border with each other?', a.land_neighbors.includes(b.key) ? 'Yes' : 'No', b.land_neighbors.includes(a.key) ? 'Yes' : 'No'],
  ];
  document.getElementById('compare-table').innerHTML =
    `<tr><th></th><th>${{a.name}}</th><th>${{b.name}}</th></tr>` +
    rows.map(r => `<tr><td><strong>${{r[0]}}</strong></td><td>${{r[1]}}</td><td>${{r[2]}}</td></tr>`).join('');
}}
document.getElementById('compare-a').addEventListener('change', renderCompare);
document.getElementById('compare-b').addEventListener('change', renderCompare);
document.getElementById('compare-overlay').addEventListener('click', e => {{
  if (e.target.id === 'compare-overlay') closeCompare();
}});

// ── Trivia quiz (generated from real REGIONS data) ──
const QUIZ_QUESTIONS = (function buildQuiz() {{
  const all = Object.values(REGIONS);
  const mostNbr = all.reduce((m, r) => r.land_neighbors.length > m.land_neighbors.length ? r : m);
  const islands = all.filter(r => r.land_neighbors.length === 0);
  const china = all.filter(r => r.countries.includes('China'));
  const bhutan = all.filter(r => r.countries.includes('Bhutan'));
  function wrongNames(correctKeys, n) {{
    const pool = all.filter(r => !correctKeys.includes(r.key)).map(r => r.name);
    const picked = [];
    while (picked.length < n && pool.length) {{
      const i = Math.floor(Math.random() * pool.length);
      picked.push(pool.splice(i, 1)[0]);
    }}
    return picked;
  }}
  const qs = [];
  qs.push({{
    q: 'Which state/UT has the most land-bordering neighbours?',
    options: shuffle([mostNbr.name, ...wrongNames([mostNbr.key], 3)]),
    answer: mostNbr.name,
  }});
  qs.push({{
    q: `How many of India's states/UTs have no land border with any other state/UT or country?`,
    options: shuffle([String(islands.length), String(islands.length + 2), String(Math.max(islands.length - 1, 0)), String(islands.length + 5)]),
    answer: String(islands.length),
  }});
  qs.push({{
    q: 'Which of these shares a border with China?',
    options: shuffle([china[Math.floor(Math.random() * china.length)].name, ...wrongNames(china.map(r => r.key), 3)]),
    answer: null,
  }});
  qs[2].answer = qs[2].options.find(o => china.some(r => r.name === o));
  if (bhutan.length) {{
    qs.push({{
      q: 'Which of these shares a border with Bhutan?',
      options: shuffle([bhutan[Math.floor(Math.random() * bhutan.length)].name, ...wrongNames(bhutan.map(r => r.key), 3)]),
      answer: null,
    }});
    qs[3].answer = qs[3].options.find(o => bhutan.some(r => r.name === o));
  }}
  qs.push({{
    q: `${{REGIONS['puducherry'].name}} is famously made up of non-contiguous enclaves inside which states?`,
    options: shuffle(['Tamil Nadu, Andhra Pradesh & Kerala', 'Tamil Nadu & Karnataka only', 'Kerala & Karnataka only', 'Andhra Pradesh & Odisha only']),
    answer: 'Tamil Nadu, Andhra Pradesh & Kerala',
  }});
  return qs;
}})();
function shuffle(arr) {{
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }}
  return a;
}}
let quizIdx = 0;
let quizScore = 0;
function renderQuiz() {{
  const box = document.getElementById('quiz-box');
  if (quizIdx >= QUIZ_QUESTIONS.length) {{
    box.innerHTML = `<div class="quiz-q">Quiz complete! You scored ${{quizScore}} / ${{QUIZ_QUESTIONS.length}}.</div>
      <button class="pf-btn" onclick="quizIdx=0;quizScore=0;renderQuiz()">Try Again</button>`;
    return;
  }}
  const cur = QUIZ_QUESTIONS[quizIdx];
  box.innerHTML = `
    <div class="quiz-progress">Question ${{quizIdx + 1}} of ${{QUIZ_QUESTIONS.length}} &middot; Score: ${{quizScore}}</div>
    <div class="quiz-q">${{cur.q}}</div>
    <div class="quiz-opts">${{cur.options.map((o, i) => `<button class="quiz-opt" onclick="answerQuiz(this, ${{i}})">${{o}}</button>`).join('')}}</div>
    <button class="pf-btn quiz-next-btn" id="quiz-next" onclick="quizIdx++;renderQuiz()">Next \u2192</button>
  `;
}}
function answerQuiz(btn, idx) {{
  const cur = QUIZ_QUESTIONS[quizIdx];
  const picked = cur.options[idx];
  document.querySelectorAll('.quiz-opt').forEach(o => {{
    o.disabled = true;
    if (o.textContent === cur.answer) o.classList.add('correct');
    else if (o === btn) o.classList.add('wrong');
  }});
  if (picked === cur.answer) quizScore++;
  document.getElementById('quiz-next').classList.add('show');
}}
renderQuiz();

// ── Interactive Leaflet map (node-graph of capitals + border connections) ──
let mapInstance = null;
function toggleMap() {{
  const mapDiv = document.getElementById('map-view');
  const grid = document.getElementById('grid');
  const showing = mapDiv.classList.toggle('show');
  grid.classList.toggle('map-hidden', showing);
  document.getElementById('map-toggle-btn').classList.toggle('active', showing);
  if (showing && !mapInstance) initMap();
  else if (showing && mapInstance) setTimeout(() => mapInstance.invalidateSize(), 50);
}}
function initMap() {{
  mapInstance = L.map('map-view').setView([22.9, 82.8], 5);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors', maxZoom: 9,
  }}).addTo(mapInstance);
  const drawn = new Set();
  Object.values(REGIONS).forEach(r => {{
    r.land_neighbors.forEach(nk => {{
      const edgeKey = [r.key, nk].sort().join('|');
      if (drawn.has(edgeKey)) return;
      drawn.add(edgeKey);
      const nb = REGIONS[nk];
      L.polyline([[r.lat, r.lon], [nb.lat, nb.lon]], {{ color: '#9c6b2e', weight: 1.5, opacity: 0.6 }}).addTo(mapInstance);
    }});
  }});
  Object.values(REGIONS).forEach(r => {{
    const n = r.land_neighbors.length;
    const radius = 5 + Math.min(n, 8) * 1.4;
    const color = r.countries.length ? '#a23b3b' : (n === 0 ? '#355c2b' : '#1f5c47');
    const marker = L.circleMarker([r.lat, r.lon], {{
      radius, color, fillColor: color, fillOpacity: 0.75, weight: 1.5,
    }}).addTo(mapInstance);
    marker.bindPopup(`<strong>${{r.name}}</strong><br>${{n}} land neighbour${{n !== 1 ? 's' : ''}}${{r.countries.length ? '<br>Borders: ' + r.countries.join(', ') : ''}}`);
    marker.on('click', () => {{
      toggleMap();
      selectRegion(r.key);
    }});
  }});
}}

filterRegions();
</script>

</body>
</html>'''
