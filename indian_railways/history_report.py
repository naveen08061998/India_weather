"""
Indian Railways — History & Technology HTML Page
==================================================
A self-contained, static HTML page (no backend calls) presenting a curated
timeline of notable trains introduced by Indian Railways and the technology
that shaped the network. Content lives in history_content.py; this module
only renders it. Shares the tracker's dark/light theme (same 'ir_theme'
localStorage key) so switching themes on one page carries over to the other.
"""

from __future__ import annotations

from indian_railways.history_content import DISCLAIMER, GLOSSARY, TECHNOLOGY, TIMELINE

_TAG_LABEL = {"milestone": "Milestone", "train": "Train", "technology": "Technology"}
_TAG_COLOR = {"milestone": "#f97316", "train": "#38bdf8", "technology": "#a855f7"}


def _timeline_card(entry: dict, idx: int) -> str:
    tag = entry["tag"]
    month_day = entry.get("month_day", "")
    return f"""
      <div class="tl-card" id="tl-card-{idx}" data-tag="{tag}" data-monthday="{month_day}">
        <div class="tl-year">{entry['year_label']}</div>
        <div class="tl-body">
          <span class="tl-tag" style="--tc:{_TAG_COLOR[tag]}">{entry['icon']} {_TAG_LABEL[tag]}</span>
          <h3>{entry['title']}</h3>
          <p>{entry['text']}</p>
          <p class="detail-text" style="display:none">{entry['detail']}</p>
          <button class="read-more-btn" onclick="toggleDetail(this)">Read more &#8595;</button>
        </div>
      </div>"""


def _tech_card(entry: dict) -> str:
    return f"""
      <div class="tech-card">
        <div class="tech-icon">{entry['icon']}</div>
        <h3>{entry['title']}</h3>
        <p>{entry['text']}</p>
        <p class="detail-text" style="display:none">{entry['detail']}</p>
        <button class="read-more-btn" onclick="toggleDetail(this)">Read more &#8595;</button>
      </div>"""


def _glossary_card(entry: dict) -> str:
    return f"""
      <div class="gl-card" data-cat="{entry['category']}" data-term="{entry['term'].lower()}">
        <h3>{entry['term']}</h3>
        <p>{entry['definition']}</p>
      </div>"""


def build_history_html() -> str:
    timeline_html = "\n".join(_timeline_card(e, i) for i, e in enumerate(TIMELINE))
    tech_html = "\n".join(_tech_card(e) for e in TECHNOLOGY)
    glossary_html = "\n".join(_glossary_card(e) for e in sorted(GLOSSARY, key=lambda e: e["term"].lower()))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Indian Railways — History &amp; Technology</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg: #070c1b; --surface: #0d1528; --card: #111e35; --card-h: #172543;
    --accent: #38bdf8; --accent-glow: rgba(56,189,248,.18);
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
  .header-right {{ display: flex; align-items: center; gap: 8px; }}
  .nav-link, #theme-btn {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); padding: 7px 12px; cursor: pointer; font-size: .8rem;
    transition: background .2s; white-space: nowrap; font-family: inherit;
    text-decoration: none; display: inline-flex; align-items: center; gap: 4px;
  }}
  .nav-link:hover, #theme-btn:hover {{ background: var(--card-h); }}
  main {{ max-width: 980px; margin: 0 auto; padding: 24px 20px 64px; }}
  .page-intro {{ margin-bottom: 18px; }}
  .page-intro h2 {{ font-size: 1.4rem; font-weight: 800; margin-bottom: 6px; }}
  .page-intro p {{ color: var(--muted); font-size: .85rem; line-height: 1.6; }}
  .disclaimer {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 14px; font-size: .74rem; color: var(--muted); line-height: 1.6;
    margin-bottom: 24px;
  }}
  .fact-bar {{
    background: var(--accent-glow); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 14px; font-size: .8rem; color: var(--text); margin-bottom: 14px;
    display: flex; align-items: center; gap: 10px;
  }}
  .tl-card.today {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }}
  .filters {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
  .filter-chip {{
    background: var(--card); border: 1px solid var(--border); border-radius: 999px;
    padding: 6px 14px; font-size: .78rem; color: var(--muted); cursor: pointer;
    font-family: inherit; transition: border-color .2s, color .2s;
  }}
  .filter-chip.active {{ border-color: var(--accent); color: var(--text); }}
  section {{ margin-bottom: 40px; }}
  section > h2 {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; }}
  .timeline {{ display: flex; flex-direction: column; gap: 14px; }}
  .tl-card {{
    display: flex; gap: 16px; background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 18px; box-shadow: var(--shadow);
  }}
  .tl-year {{
    flex-shrink: 0; width: 92px; font-weight: 800; color: var(--accent); font-size: .95rem;
    padding-top: 2px;
  }}
  .tl-body h3 {{ font-size: .95rem; margin: 4px 0 4px; }}
  .tl-body p {{ font-size: .8rem; color: var(--muted); line-height: 1.6; }}
  .tl-tag {{
    display: inline-block; font-size: .68rem; font-weight: 700; color: var(--tc);
    border: 1px solid var(--tc); border-radius: 999px; padding: 2px 8px;
  }}
  .read-more-btn {{
    margin-top: 8px; background: none; border: none; color: var(--accent);
    font-size: .74rem; font-weight: 600; cursor: pointer; padding: 0; font-family: inherit;
  }}
  .read-more-btn:hover {{ text-decoration: underline; }}
  .tech-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
  .tech-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 16px 18px; box-shadow: var(--shadow);
  }}
  .tech-icon {{ font-size: 1.6rem; margin-bottom: 8px; }}
  .tech-card h3 {{ font-size: .92rem; margin-bottom: 6px; }}
  .tech-card p {{ font-size: .8rem; color: var(--muted); line-height: 1.6; }}
  .gl-search {{
    width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text); font-size: .82rem; font-family: inherit;
    outline: none; margin-bottom: 16px; transition: border .2s;
  }}
  .gl-search:focus {{ border-color: var(--accent); }}
  .gl-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
  .gl-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 12px 16px; box-shadow: var(--shadow);
  }}
  .gl-card h3 {{ font-size: .85rem; margin-bottom: 4px; color: var(--accent); }}
  .gl-card p {{ font-size: .78rem; color: var(--muted); line-height: 1.5; }}
  footer {{ text-align: center; padding: 20px; font-size: .72rem; color: var(--muted); }}
</style>
</head>
<body>
<div class="tricolor"></div>
<header>
  <div class="brand">
    <div class="brand-icon">&#128220;</div>
    <div class="brand-text">
      <h1>Indian Railways — History &amp; Technology</h1>
      <p>Notable trains introduced over the years, and the technology behind them</p>
    </div>
  </div>
  <div class="header-right">
    <a class="nav-link" href="index.html">&#128646; Live Tracker</a>
    <button id="theme-btn" onclick="toggleTheme()">&#9728; Light</button>
  </div>
</header>

<main>
  <div class="page-intro">
    <h2>From the first steam train to Vande Bharat and beyond</h2>
    <p>A timeline of major trains Indian Railways has introduced, followed by the
       technology — traction, coaches, signalling and passenger systems — that has
       shaped the network since 1853.</p>
  </div>
  <div class="fact-bar" id="fact-bar" style="display:none">
    <span class="fact-bar-icon">&#128197;</span>
    <span class="fact-bar-text" id="fact-bar-text"></span>
  </div>
  <div class="disclaimer">&#8505;&#65039; {DISCLAIMER}</div>

  <section>
    <h2>&#128197; Timeline of Notable Trains &amp; Milestones</h2>
    <div class="filters">
      <button class="filter-chip active" data-filter="all" onclick="applyFilter('all', this)">All</button>
      <button class="filter-chip" data-filter="train" onclick="applyFilter('train', this)">&#128646; Trains</button>
      <button class="filter-chip" data-filter="technology" onclick="applyFilter('technology', this)">&#9889; Technology</button>
      <button class="filter-chip" data-filter="milestone" onclick="applyFilter('milestone', this)">&#127942; Milestones</button>
    </div>
    <div class="timeline" id="timeline">
      {timeline_html}
    </div>
  </section>

  <section>
    <h2>&#9881;&#65039; Technology Behind the Network</h2>
    <div class="tech-grid">
      {tech_html}
    </div>
  </section>

  <section>
    <h2>&#128214; Railway Glossary</h2>
    <input type="text" class="gl-search" id="gl-search" placeholder="Search terms (e.g. LHB, Tatkal, RAC)…" oninput="filterGlossary()"/>
    <div class="filters">
      <button class="filter-chip active" data-filter="all" onclick="applyGlossaryFilter('all', this)">All</button>
      <button class="filter-chip" data-filter="train_type" onclick="applyGlossaryFilter('train_type', this)">&#128646; Train Types</button>
      <button class="filter-chip" data-filter="term" onclick="applyGlossaryFilter('term', this)">&#128214; Terms</button>
    </div>
    <div class="gl-grid" id="glossary">
      {glossary_html}
    </div>
  </section>
</main>

<footer>Compiled from publicly available Indian Railways history — not an official IR publication.</footer>

<script>
function applyFilter(tag, btnEl) {{
  btnEl.parentElement.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
  btnEl.classList.add('active');
  document.querySelectorAll('#timeline .tl-card').forEach(card => {{
    card.style.display = (tag === 'all' || card.dataset.tag === tag) ? 'flex' : 'none';
  }});
}}
let _glossaryFilter = 'all';
function applyGlossaryFilter(cat, btnEl) {{
  _glossaryFilter = cat;
  btnEl.parentElement.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
  btnEl.classList.add('active');
  filterGlossary();
}}
function filterGlossary() {{
  const q = document.getElementById('gl-search').value.trim().toLowerCase();
  document.querySelectorAll('#glossary .gl-card').forEach(card => {{
    const matchesCat = _glossaryFilter === 'all' || card.dataset.cat === _glossaryFilter;
    const matchesQ = !q || card.dataset.term.includes(q) || card.textContent.toLowerCase().includes(q);
    card.style.display = (matchesCat && matchesQ) ? 'block' : 'none';
  }});
}}
function toggleDetail(btnEl) {{
  const wrap = btnEl.parentElement;
  const summary = wrap.querySelector('p:not(.detail-text)');
  const detail = wrap.querySelector('.detail-text');
  const show = detail.style.display === 'none';
  detail.style.display = show ? 'block' : 'none';
  summary.style.display = show ? 'none' : 'block';
  btnEl.innerHTML = show ? 'Show less &#8593;' : 'Read more &#8595;';
}}
function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent = isLight ? '🌙 Dark' : '☀ Light';
  localStorage.setItem('ir_theme', isLight ? 'light' : 'dark');
}}
if (localStorage.getItem('ir_theme') === 'light') {{
  document.body.classList.add('light');
  document.getElementById('theme-btn').textContent = '🌙 Dark';
}}

// ── On this day ── highlights the matching card (using the IST-shifted date so
// it lines up with the tracker page's identical logic) instead of duplicating
// the timeline data as a separate JSON blob.
(function() {{
  const istNow = new Date(Date.now() + 5.5 * 3600 * 1000);
  const monthDay = `${{String(istNow.getUTCMonth() + 1).padStart(2, '0')}}-${{String(istNow.getUTCDate()).padStart(2, '0')}}`;
  const match = document.querySelector(`.tl-card[data-monthday="${{monthDay}}"]`);
  if (!match) return;
  match.classList.add('today');
  const title = match.querySelector('h3').textContent;
  const year = match.querySelector('.tl-year').textContent;
  document.getElementById('fact-bar-text').innerHTML = `<b>On This Day:</b> ${{title}} (${{year}}) — scrolled to below.`;
  document.getElementById('fact-bar').style.display = 'flex';
}})();
</script>
</body>
</html>"""
