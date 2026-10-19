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

.state-finder { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.state-finder select {
  width: 100%; max-width: 340px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--bg2); color: var(--ink); font-family: inherit; font-size: 0.95rem; margin-bottom: 14px;
}
.state-nh-list { display: flex; flex-wrap: wrap; gap: 8px; }
.state-nh-chip {
  background: var(--bg2); border: 1px solid var(--yellow-dim); color: var(--yellow);
  border-radius: 4px; padding: 6px 12px; font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.state-nh-chip:hover { background: var(--yellow); color: #1b1d21; }

.lb-row { display: flex; align-items: center; gap: 10px; margin: 8px 0; }
.lb-name { width: 150px; font-size: 0.85rem; flex-shrink: 0; }
.lb-bar-track { flex: 1; background: var(--line); border-radius: 6px; overflow: hidden; height: 16px; }
.lb-bar { background: linear-gradient(90deg, var(--yellow-dim), var(--yellow)); height: 100%; border-radius: 6px; }
.lb-val { width: 40px; font-size: 0.8rem; text-align: right; color: var(--ink-soft); }

.corridor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.corridor-card { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--yellow); border-radius: var(--radius); padding: 16px 18px; box-shadow: var(--shadow); }
.corridor-card h4 { margin: 0 0 6px; color: var(--yellow); font-size: 1.05rem; }
.corridor-card .cn-note { font-size: 0.82rem; color: var(--ink-soft); margin-bottom: 10px; line-height: 1.5; }
.corridor-card .cn-members { font-size: 0.85rem; font-weight: 600; }

.renumber-table { width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow); }
.renumber-table th, .renumber-table td { padding: 11px 14px; text-align: left; font-size: 0.88rem; border-bottom: 1px solid var(--line); }
.renumber-table th { background: var(--bg2); color: var(--yellow); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }
.renumber-table .arrow { color: var(--yellow); font-weight: 700; }

.expwy-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.expwy-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); }
.expwy-card h4 { margin: 0 0 6px; font-size: 1rem; color: var(--ink); }
.expwy-card .ew-len { color: var(--yellow); font-weight: 700; font-size: 1rem; }
.expwy-card .ew-route { font-size: 0.85rem; color: var(--ink-soft); margin: 4px 0; }
.expwy-card .ew-note { font-size: 0.8rem; color: var(--ink-soft); line-height: 1.5; margin-top: 6px; }
.tag-uc { display: inline-block; margin-top: 6px; font-size: 0.68rem; padding: 2px 8px; border-radius: 10px; background: #6b4a1a; color: #ffd98a; text-transform: uppercase; letter-spacing: 0.5px; }

.quiz-box { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.quiz-q { font-size: 0.98rem; font-weight: 600; margin-bottom: 12px; }
.quiz-opts { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.quiz-opt { text-align: left; padding: 10px 14px; border: 1px solid var(--line); border-radius: 6px; background: var(--bg2); cursor: pointer; font-family: inherit; font-size: 0.88rem; color: var(--ink); }
.quiz-opt:hover { border-color: var(--yellow); }
.quiz-opt.correct { background: #1f4a2e; border-color: var(--green); }
.quiz-opt.wrong { background: #4a2420; border-color: var(--red); }
.quiz-progress { font-size: 0.78rem; color: var(--ink-soft); margin-bottom: 6px; }
.quiz-next-btn { display: none; }
.quiz-next-btn.show { display: inline-block; }
.pf-btn { background: var(--yellow); color: #1b1d21; border: none; border-radius: 6px; padding: 10px 18px; font-size: 0.88rem; cursor: pointer; font-family: inherit; font-weight: 700; }

.modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; padding: 20px; }
.modal-overlay.show { display: flex; }
.compare-modal { background: var(--bg2); border: 2px solid var(--yellow); border-radius: var(--radius); padding: 24px; max-width: 640px; width: 100%; max-height: 85vh; overflow: auto; box-shadow: var(--shadow); }
.compare-modal h3 { color: var(--yellow); margin-bottom: 14px; }
.compare-selects { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.compare-selects select { flex: 1; min-width: 160px; padding: 10px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--ink); font-family: inherit; }
.compare-table { width: 100%; border-collapse: collapse; }
.compare-table th, .compare-table td { padding: 9px 10px; font-size: 0.85rem; border-bottom: 1px solid var(--line); text-align: left; }
.close-modal-btn { margin-top: 16px; background: none; border: 1px solid var(--yellow); color: var(--yellow); border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; cursor: pointer; font-family: inherit; }

#map-view { display: none; height: 560px; border-radius: var(--radius); overflow: hidden; margin-bottom: 18px; border: 1px solid var(--line); }
#map-view.show { display: block; }
.nh-grid.map-hidden { display: none; }

.skip-link {
  position: absolute; left: -999px; top: 0; background: var(--yellow); color: #1b1d21;
  padding: 10px 16px; z-index: 2000; border-radius: 0 0 6px 0; font-size: 0.85rem; font-weight: 700;
}
.skip-link:focus { left: 0; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; }

.featured-banner {
  background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--yellow);
  border-radius: var(--radius); padding: 14px 18px; margin: 18px 0; box-shadow: var(--shadow);
  font-size: 0.9rem; cursor: pointer;
}
.featured-banner strong { color: var(--yellow); }

.detour-note { font-size: 0.82rem; color: var(--ink-soft); margin-top: 6px; }

.print-btn {
  background: none; border: 1px solid var(--yellow); color: var(--yellow); border-radius: 4px;
  padding: 5px 12px; font-size: 0.76rem; cursor: pointer; font-family: inherit; margin-left: 10px;
}
@media print {
  body * { visibility: hidden; }
  .detail-panel, .detail-panel * { visibility: visible; }
  .detail-panel { position: absolute; left: 0; top: 0; width: 100%; border: none; box-shadow: none; }
  .close-btn, .print-btn { display: none; }
}

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


def _lb_row(name: str, value, max_value, suffix: str = "") -> str:
    pct = round((value / max_value) * 100) if max_value else 0
    val_text = f"{value:,}{suffix}" if isinstance(value, int) else f"{value}{suffix}"
    return f'''
<div class="lb-row">
  <div class="lb-name">{name}</div>
  <div class="lb-bar-track"><div class="lb-bar" style="width:{pct}%"></div></div>
  <div class="lb-val">{val_text}</div>
</div>'''


def _corridor_card(name: str, members: list, note: str, total_km: int) -> str:
    return f'''
<div class="corridor-card">
  <h4>{name}</h4>
  <div class="ew-len">{total_km:,} km total</div>
  <div class="cn-note">{note}</div>
  <div class="cn-members">{", ".join(members)}</div>
</div>'''


def _expwy_card(e: dict) -> str:
    tag = '<span class="tag-uc">Under construction</span>' if e["status"] == "under_construction" else ''
    return f'''
<div class="expwy-card">
  <h4>{e['name']}</h4>
  <div class="ew-len">{e['length_km']:,} km</div>
  <div class="ew-route">{e['route']}</div>
  <div class="ew-note">{e['note']}</div>
  {tag}
</div>'''


def build_html(payload: dict) -> str:
    nh_list = payload["national_highways"]
    sh = payload["state_highway_summary"]
    net = payload["road_network_stats"]
    stats = payload["stats"]
    expressways = payload["expressways"]
    corridor_groups = payload["corridor_groups"]
    corridor_notes = payload["corridor_notes"]
    corridor_totals = payload["corridor_totals"]
    renumbering = payload["renumbering"]
    state_index = payload["state_index"]
    state_leaderboard = payload["state_leaderboard"]
    length_leaderboard = payload["length_leaderboard"]
    expwy_state_leaderboard = payload["expwy_state_leaderboard"]

    cards_html = "\n".join(_nh_card(h) for h in sorted(nh_list, key=lambda h: h["length_km"], reverse=True))

    top_states = sh["top_states_by_share"]
    max_pct = top_states[0]["share_pct"]
    sh_rows = "\n".join(_sh_row(s["state"], s["share_pct"], max_pct) for s in top_states)
    sh_rows += _sh_row("All other states/UTs", sh["unlisted_share_pct"], max_pct, unlisted=True)

    max_state_count = state_leaderboard[0]["count"] if state_leaderboard else 1
    state_lb_html = "\n".join(_lb_row(r["state"], r["count"], max_state_count) for r in state_leaderboard)

    max_length = length_leaderboard[0]["length_km"] if length_leaderboard else 1
    length_lb_html = "\n".join(_lb_row(r["number"], r["length_km"], max_length, suffix=" km") for r in length_leaderboard)

    corridor_html = "\n".join(
        _corridor_card(name, members, corridor_notes.get(name, ""), corridor_totals.get(name, 0))
        for name, members in sorted(corridor_groups.items(), key=lambda kv: len(kv[1]), reverse=True)
    )

    max_expwy_state = expwy_state_leaderboard[0]["count"] if expwy_state_leaderboard else 1
    expwy_state_lb_html = "\n".join(_lb_row(r["state"], r["count"], max_expwy_state) for r in expwy_state_leaderboard)

    renumber_rows = "\n".join(
        f'<tr><td>{r["old"]}</td><td class="arrow">\u2192</td><td>{r["new"]}</td><td>{r["note"]}</td></tr>'
        for r in renumbering
    )

    expwy_html = "\n".join(_expwy_card(e) for e in sorted(expressways, key=lambda e: e["length_km"], reverse=True))

    state_options = "".join(f'<option value="{s}">{s}</option>' for s in sorted(state_index.keys()))
    nh_select_options = "".join(
        f'<option value="{h["number"]}">{h["number"]} \u2014 {h["route"]}</option>'
        for h in sorted(nh_list, key=lambda h: h["number"])
    )

    nh_json = json.dumps(nh_list, ensure_ascii=False)
    state_index_json = json.dumps(state_index, ensure_ascii=False)
    renumbering_json = json.dumps(renumbering, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>India Highways</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>{CSS}</style>
</head>
<body>

<a class="skip-link" href="#main-content">Skip to main content</a>

<header class="hero">
  <div class="shield">NH</div>
  <h1>India Highways</h1>
  <p class="sub">Major National Highway corridors, state-highway shares &amp; the road network that connects a subcontinent.</p>
  <p class="meta">Compiled {payload['date']} &middot; MoRTH / NHAI published figures</p>
</header>

<main id="main-content" class="wrap">

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

  <div class="featured-banner" id="featured-banner" role="button" tabindex="0"></div>

  <h2 class="section-title">National Highway Corridors</h2>
  <div class="toolbar">
    <label for="search" class="visually-hidden">Search by number, city or route</label>
    <input id="search" type="text" placeholder="Search by number, city or route…" oninput="filterNh()">
    <button class="chip active" data-filter="all" onclick="setNhFilter('all', this)">All</button>
    <button class="chip" data-filter="current" onclick="setNhFilter('current', this)">Current</button>
    <button class="chip" data-filter="historic" onclick="setNhFilter('historic', this)">Historic</button>
    <select id="sort-select" onchange="sortNh()" aria-label="Sort highways">
      <option value="length-desc">Length: Longest first</option>
      <option value="length-asc">Length: Shortest first</option>
      <option value="number">Number</option>
    </select>
    <button class="chip" id="map-toggle-btn" onclick="toggleMap()" aria-expanded="false">Map View</button>
    <button class="chip" onclick="openCompare()">Compare</button>
  </div>
  <p id="count-line" role="status" aria-live="polite"></p>
  <div id="map-view"></div>
  <div class="nh-grid" id="nh-grid">
    {cards_html}
  </div>

  <div class="detail-panel" id="detail-panel">
    <button class="close-btn" onclick="closeDetail()">✕</button>
    <div id="detail-content"></div>
  </div>

  <h2 class="section-title">Find Highways By State</h2>
  <div class="state-finder">
    <label for="state-select" class="visually-hidden">Choose a state or union territory</label>
    <select id="state-select" onchange="showStateHighways()">
      <option value="">Choose a state/UT…</option>
      {state_options}
    </select>
    <div class="state-nh-list" id="state-nh-list"></div>
  </div>

  <h2 class="section-title">States With the Most National Highways</h2>
  <div class="sh-bars">
    {state_lb_html}
  </div>

  <h2 class="section-title">States With the Most Expressways</h2>
  <div class="sh-bars">
    {expwy_state_lb_html}
  </div>

  <h2 class="section-title">Highway Length Leaderboard</h2>
  <div class="sh-bars">
    {length_lb_html}
  </div>

  <h2 class="section-title">Named Megaproject Corridors</h2>
  <div class="corridor-grid">
    {corridor_html}
  </div>

  <h2 class="section-title">2010 Renumbering — Old → New</h2>
  <table class="renumber-table">
    <tr><th>Old Number</th><th></th><th>New Number</th><th>What Changed</th></tr>
    {renumber_rows}
  </table>

  <h2 class="section-title">Expressways</h2>
  <div class="expwy-grid">
    {expwy_html}
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

  <h2 class="section-title">Highway Trivia Quiz</h2>
  <div class="quiz-box" id="quiz-box"></div>

</main>

<footer role="contentinfo">India Highways &middot; Static reference data from published MoRTH/NHAI figures &middot; Generated {payload['generated_at']}</footer>

<div class="modal-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title">
  <div class="compare-modal">
    <h3 id="compare-title">Compare Two Highways</h3>
    <div class="compare-selects">
      <select id="compare-a">{nh_select_options}</select>
      <select id="compare-b">{nh_select_options}</select>
    </div>
    <table class="compare-table" id="compare-table"></table>
    <button class="close-modal-btn" onclick="closeCompare()">Close</button>
  </div>
</div>

<script>
const NH_DATA = {nh_json};
const STATE_INDEX = {state_index_json};
const RENUMBERING = {renumbering_json};
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
  const detourHtml = h.detour_factor
    ? `<div class="detour-note">Straight-line distance between endpoints: ~${{h.straight_line_km.toLocaleString()}} km &middot; actual route is ${{h.detour_factor}}× that (detour factor)</div>`
    : '';
  document.getElementById('detail-content').innerHTML = `
    <h3>${{h.number}} — ${{h.route}} <button class="print-btn" onclick="window.print()">🖨️ Print</button></h3>
    <div class="dp-meta">${{h.length_km.toLocaleString()}} km &middot; ${{h.states.length}} states/UTs crossed ${{h.status === 'historic' ? '&middot; Historic numbering' : ''}}</div>
    ${{detourHtml}}
    <p class="dp-note">${{h.note}}</p>
    <div class="dp-meta"><strong>States crossed:</strong> ${{h.states.join(', ')}}</div>
  `;
  document.getElementById('detail-panel').classList.add('open');
  document.getElementById('detail-panel').scrollIntoView({{behavior: 'smooth', block: 'center'}});
}}

function closeDetail() {{
  document.getElementById('detail-panel').classList.remove('open');
}}

// ── Featured highway of the day (deterministic daily rotation) ──
function dayOfYear() {{
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  return Math.floor((now - start) / 86400000);
}}
function renderFeaturedBanner() {{
  const current = NH_DATA.filter(h => h.status === 'current');
  const pick = current[dayOfYear() % current.length];
  document.getElementById('featured-banner').innerHTML =
    `🌟 Featured today: <strong>${{pick.number}}</strong> — ${{pick.route}} (${{pick.length_km.toLocaleString()}} km)`;
  document.getElementById('featured-banner').onclick = () => showNhDetail(pick.number);
}}
renderFeaturedBanner();

// ── State highway finder ──
function showStateHighways() {{
  const state = document.getElementById('state-select').value;
  const list = document.getElementById('state-nh-list');
  if (!state) {{ list.innerHTML = ''; return; }}
  const numbers = STATE_INDEX[state] || [];
  list.innerHTML = numbers.length
    ? numbers.map(n => `<span class="state-nh-chip" onclick="showNhDetail('${{n}}');document.getElementById('detail-panel').scrollIntoView({{behavior:'smooth',block:'center'}})">${{n}}</span>`).join('')
    : '<em>No current National Highways recorded for this state in this curated dataset.</em>';
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
  const a = NH_DATA.find(x => x.number === document.getElementById('compare-a').value);
  const b = NH_DATA.find(x => x.number === document.getElementById('compare-b').value);
  const rows = [
    ['Route', a.route, b.route],
    ['Length', a.length_km.toLocaleString() + ' km', b.length_km.toLocaleString() + ' km'],
    ['States/UTs crossed', a.states.length, b.states.length],
    ['Status', a.status, b.status],
    ['Corridor', a.corridor || 'None', b.corridor || 'None'],
  ];
  document.getElementById('compare-table').innerHTML =
    `<tr><th></th><th>${{a.number}}</th><th>${{b.number}}</th></tr>` +
    rows.map(r => `<tr><td><strong>${{r[0]}}</strong></td><td>${{r[1]}}</td><td>${{r[2]}}</td></tr>`).join('');
}}
document.getElementById('compare-a').addEventListener('change', renderCompare);
document.getElementById('compare-b').addEventListener('change', renderCompare);
document.getElementById('compare-overlay').addEventListener('click', e => {{
  if (e.target.id === 'compare-overlay') closeCompare();
}});

// ── Trivia quiz (generated from real NH_DATA) ──
function shuffle(arr) {{
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }}
  return a;
}}
const QUIZ_QUESTIONS = (function buildQuiz() {{
  const current = NH_DATA.filter(h => h.status === 'current');
  const historic = NH_DATA.filter(h => h.status === 'historic');
  const longest = current.reduce((m, h) => h.length_km > m.length_km ? h : m);
  const mostStates = current.reduce((m, h) => h.states.length > m.states.length ? h : m);
  function wrongNumbers(correct, pool, n) {{
    const choices = pool.filter(h => h.number !== correct).map(h => h.number);
    const picked = [];
    while (picked.length < n && choices.length) {{
      const i = Math.floor(Math.random() * choices.length);
      picked.push(choices.splice(i, 1)[0]);
    }}
    return picked;
  }}
  const qs = [];
  qs.push({{
    q: 'Which is the longest National Highway in India (current numbering)?',
    options: shuffle([longest.number, ...wrongNumbers(longest.number, current, 3)]),
    answer: longest.number,
  }});
  qs.push({{
    q: 'Which current National Highway crosses the most states/UTs?',
    options: shuffle([mostStates.number, ...wrongNumbers(mostStates.number, current, 3)]),
    answer: mostStates.number,
  }});
  const sampleHistoric = historic[Math.floor(Math.random() * historic.length)];
  const mapping = RENUMBERING.find(r => r.old === sampleHistoric.number.replace(' (historic)', ''));
  qs.push({{
    q: `What is the old "${{sampleHistoric.number}}" numbered as today?`,
    options: shuffle([mapping.new, ...wrongNumbers(mapping.new, current, 3)]),
    answer: mapping.new,
  }});
  qs.push({{
    q: 'India\\'s first major expressway, opened in 2002, connects which two cities?',
    options: shuffle(['Mumbai & Pune', 'Delhi & Jaipur', 'Chennai & Bengaluru', 'Ahmedabad & Vadodara']),
    answer: 'Mumbai & Pune',
  }});
  qs.push({{
    q: 'The Golden Quadrilateral megaproject links which 4 cities?',
    options: shuffle(['Delhi, Mumbai, Chennai & Kolkata', 'Delhi, Jaipur, Pune & Kochi', 'Mumbai, Goa, Bengaluru & Chennai', 'Kolkata, Patna, Lucknow & Delhi']),
    answer: 'Delhi, Mumbai, Chennai & Kolkata',
  }});
  const withDetour = current.filter(h => h.detour_factor);
  const mostDetour = withDetour.reduce((m, h) => h.detour_factor > m.detour_factor ? h : m);
  qs.push({{
    q: 'Which highway\\'s actual route length deviates the most from a straight line between its endpoints (highest "detour factor")?',
    options: shuffle([mostDetour.number, ...wrongNumbers(mostDetour.number, withDetour, 3)]),
    answer: mostDetour.number,
  }});
  qs.push({{
    q: 'Which expressway was built with a stretch usable as an emergency Indian Air Force airstrip?',
    options: shuffle(['Purvanchal Expressway', 'Mumbai\u2013Pune Expressway', 'Ahmedabad\u2013Vadodara Expressway', 'Eastern Peripheral Expressway']),
    answer: 'Purvanchal Expressway',
  }});
  return qs;
}})();
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

// ── Interactive Leaflet map (city-to-city lines for each highway's endpoints) ──
let mapInstance = null;
function toggleMap() {{
  const mapDiv = document.getElementById('map-view');
  const grid = document.getElementById('nh-grid');
  const showing = mapDiv.classList.toggle('show');
  grid.classList.toggle('map-hidden', showing);
  const btn = document.getElementById('map-toggle-btn');
  btn.classList.toggle('active', showing);
  btn.setAttribute('aria-expanded', showing ? 'true' : 'false');
  if (showing && !mapInstance) initMap();
  else if (showing && mapInstance) setTimeout(() => mapInstance.invalidateSize(), 50);
}}
function initMap() {{
  mapInstance = L.map('map-view').setView([22.9, 79.0], 5);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors', maxZoom: 9,
  }}).addTo(mapInstance);
  const cityMarkers = new Set();
  NH_DATA.forEach(h => {{
    if (!h.start_coords || !h.end_coords) return;
    const color = h.status === 'historic' ? '#a7acb5' : '#ffc93c';
    const points = [h.start_coords, ...(h.via_coords || []), h.end_coords];
    L.polyline(points, {{ color, weight: 3, opacity: 0.75 }})
      .addTo(mapInstance)
      .bindPopup(`<strong>${{h.number}}</strong><br>${{h.route}}<br>${{h.length_km.toLocaleString()}} km`)
      .on('click', () => {{ toggleMap(); showNhDetail(h.number); }});
    const named = [[h.start_city, h.start_coords], [h.end_city, h.end_coords]];
    (h.via || []).forEach((city, i) => named.push([city, h.via_coords[i]]));
    named.forEach(([name, coords]) => {{
      if (cityMarkers.has(name)) return;
      cityMarkers.add(name);
      L.circleMarker(coords, {{ radius: 6, color: '#ffc93c', fillColor: '#ffc93c', fillOpacity: 0.9, weight: 1.5 }})
        .addTo(mapInstance)
        .bindPopup(`<strong>${{name}}</strong>`);
    }});
  }});
}}

document.getElementById('featured-banner').addEventListener('keydown', e => {{
  if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); document.getElementById('featured-banner').click(); }}
}});

filterNh();
</script>

</body>
</html>'''
