"""
Current Affairs — History HTML Report Generator
================================================
Builds a self-contained HTML page showing the important-news digest
for a single archived day.

Features
--------
• Same dark/light design system as the main dashboard
• Date navigation bar (← Previous day | date selector | Next day →)
• "Back to Today" link
• Category tabs with article cards
• Summary strip: date, article count, archived-at timestamp
"""

from __future__ import annotations


# ── Category metadata used for history display ───────────────────────────────
_CAT_META: dict[str, dict] = {
    "national"     : {"label": "National Affairs",       "icon": "🇮🇳", "color": "#f97316"},
    "international": {"label": "International Affairs",   "icon": "🌍", "color": "#6366f1"},
    "economy"      : {"label": "Economy & Finance",       "icon": "💹", "color": "#10b981"},
    "science_tech" : {"label": "Science & Technology",    "icon": "🔬", "color": "#3b82f6"},
    "environment"  : {"label": "Environment & Ecology",   "icon": "🌿", "color": "#22c55e"},
    "polity"       : {"label": "Governance & Polity",     "icon": "⚖️", "color": "#a855f7"},
    "defence"      : {"label": "Defence & Security",      "icon": "🛡️", "color": "#ef4444"},
    "sports"       : {"label": "Sports",                  "icon": "🏅", "color": "#f59e0b"},
    "awards"       : {"label": "Awards & Honours",        "icon": "🏆", "color": "#ec4899"},
    "art_culture"  : {"label": "Art & Culture",           "icon": "🎭", "color": "#06b6d4"},
}

_ORDERED_KEYS = list(_CAT_META.keys())


def build_history_html(snapshot: dict, available_dates: list[str],
                       static_mode: bool = False) -> str:
    """
    Build the HTML for a single archived day's digest.

    Parameters
    ----------
    snapshot        : dict returned by history_agent.load_snapshot()
    available_dates : all archived date keys, newest-first
    static_mode     : when True all links use relative .html paths
                      (for GitHub Pages); when False uses Flask /history/ routes
    """
    date_label  = snapshot.get("date", "")
    date_key    = snapshot.get("date_key", "")
    archived_at = snapshot.get("archived_at", "")
    total       = snapshot.get("total_articles", 0)
    categories  = snapshot.get("categories", {})

    tabs_html   = _build_tabs(categories)
    panels_html = _build_panels(categories)
    dates_opts  = _build_date_options(available_dates, date_key, static_mode)

    # Prev / Next navigation — relative paths in static mode, absolute in Flask
    idx      = available_dates.index(date_key) if date_key in available_dates else -1
    prev_key = available_dates[idx + 1] if 0 <= idx < len(available_dates) - 1 else None
    next_key = available_dates[idx - 1] if idx > 0 else None

    def _date_href(dk: str) -> str:
        return f"./{dk}.html" if static_mode else f"/history/{dk}"

    live_href = "../" if static_mode else "/"

    prev_btn = (
        f'<a class="nav-btn" href="{_date_href(prev_key)}">&#8592; {prev_key}</a>'
        if prev_key else
        '<span class="nav-btn disabled">&#8592; No earlier</span>'
    )
    next_btn = (
        f'<a class="nav-btn" href="{_date_href(next_key)}">{next_key} &#8594;</a>'
        if next_key else
        '<span class="nav-btn disabled">Latest &#8594;</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>History: {date_label} — Current Affairs Daily</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg: #070c1b; --surface: #0d1528; --card: #111e35; --card-h: #172543;
    --accent: #818cf8; --accent2: #f97316; --accent3: #22c55e;
    --accent-glow: rgba(129,140,248,.18);
    --text: #e8edf5; --muted: #7b8899; --border: #1a2a45;
    --radius: 14px; --shadow: 0 8px 32px rgba(0,0,0,.5);
    --hist: #f59e0b;
  }}
  body.light {{
    --bg: #eef2ff; --surface: #ffffff; --card: #ffffff; --card-h: #f4f6ff;
    --accent: #4f46e5; --accent-glow: rgba(79,70,229,.1);
    --text: #0f172a; --muted: #64748b; --border: #dde3f0;
    --shadow: 0 4px 20px rgba(0,0,0,.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text);
    min-height: 100vh; transition: background .3s, color .3s;
  }}
  .tricolor {{
    height: 4px; position: sticky; top: 0; z-index: 200;
    background: linear-gradient(90deg,
      #f97316 0% 33.3%, #e2e8f0 33.3% 66.6%, #22c55e 66.6% 100%);
  }}

  /* ── Header ── */
  header {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 12px 24px; display: flex; align-items: center;
    justify-content: space-between; gap: 12px; flex-wrap: wrap;
    position: sticky; top: 4px; z-index: 100;
    box-shadow: var(--shadow);
  }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .brand-icon {{
    width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; box-shadow: 0 4px 12px rgba(245,158,11,.35);
  }}
  .brand-text h1 {{ font-size: 1.1rem; font-weight: 800; letter-spacing: -.025em; }}
  .brand-text p  {{ font-size: .7rem; color: var(--muted); margin-top: 1px; }}
  .header-right {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .stat-chip {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 999px; padding: 4px 12px;
    font-size: .74rem; color: var(--muted);
    display: inline-flex; align-items: center; gap: 5px;
  }}
  .stat-chip b {{ color: var(--text); font-weight: 600; }}
  #theme-btn {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); padding: 7px 12px; cursor: pointer; font-size: .8rem;
    transition: background .2s; white-space: nowrap; font-family: inherit;
  }}
  #theme-btn:hover {{ background: var(--card-h); }}

  /* ── Date navigation bar ── */
  .date-nav {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 10px 24px; display: flex; align-items: center;
    gap: 12px; flex-wrap: wrap;
    position: sticky; top: 66px; z-index: 95;
  }}
  .nav-btn {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 5px 14px; font-size: .78rem;
    color: var(--text); text-decoration: none; font-weight: 500;
    transition: background .15s, transform .1s;
    white-space: nowrap; font-family: inherit;
  }}
  .nav-btn:hover {{ background: var(--card-h); transform: translateY(-1px); }}
  .nav-btn.disabled {{ color: var(--muted); cursor: default; opacity: .5; }}
  .nav-btn.today {{
    background: var(--accent); color: #fff;
    box-shadow: 0 2px 10px var(--accent-glow);
    border-color: transparent;
  }}
  .date-select-wrap {{ display: flex; align-items: center; gap: 6px; }}
  .date-select-wrap label {{ font-size: .75rem; color: var(--muted); }}
  #date-jump {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 5px 10px; font-size: .78rem;
    color: var(--text); outline: none; font-family: inherit;
    cursor: pointer;
  }}
  #date-jump:focus {{ border-color: var(--accent); }}
  .hist-badge {{
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    color: #fff; border-radius: 999px; padding: 3px 12px;
    font-size: .7rem; font-weight: 700; letter-spacing: .04em;
    margin-left: auto; flex-shrink: 0;
  }}

  /* ── Tabs ── */
  .tabs-wrapper {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 0 20px; overflow-x: auto; white-space: nowrap;
    position: sticky; top: 113px; z-index: 90;
    scrollbar-width: none;
  }}
  .tabs-wrapper::-webkit-scrollbar {{ display: none; }}
  .tabs {{ display: inline-flex; gap: 4px; padding: 8px 0; }}
  .tab-btn {{
    background: none; border: none; color: var(--muted);
    padding: 6px 14px; border-radius: 999px; cursor: pointer;
    font-size: .78rem; font-weight: 500; white-space: nowrap;
    transition: background .15s, color .15s, transform .1s;
    display: inline-flex; align-items: center; gap: 5px;
    font-family: inherit;
  }}
  .tab-btn:hover {{ background: var(--card); color: var(--text); transform: translateY(-1px); }}
  .tab-btn.active {{ background: var(--accent); color: #fff; box-shadow: 0 2px 14px var(--accent-glow); }}
  .tab-count {{
    background: rgba(255,255,255,.25); border-radius: 999px;
    padding: 1px 6px; font-size: .66rem; font-weight: 700;
  }}
  .tab-btn:not(.active) .tab-count {{ background: var(--border); color: var(--muted); }}

  /* ── Main ── */
  main {{ padding: 24px; max-width: 1280px; margin: 0 auto; }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; animation: panelIn .22s ease; }}
  @keyframes panelIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}

  .panel-header {{
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 20px; padding: 16px 20px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius);
  }}
  .panel-icon {{
    font-size: 1.8rem; width: 52px; height: 52px; border-radius: 12px;
    background: var(--card); display: flex; align-items: center;
    justify-content: center; flex-shrink: 0;
  }}
  .panel-title {{ font-size: 1.05rem; font-weight: 700; }}
  .panel-desc  {{ font-size: .76rem; color: var(--muted); margin-top: 3px; line-height: 1.4; }}
  .panel-count {{
    margin-left: auto; background: var(--card); border: 1px solid var(--border);
    border-radius: 999px; padding: 4px 14px;
    font-size: .76rem; color: var(--muted); white-space: nowrap; flex-shrink: 0;
  }}
  .panel-count b {{ color: var(--text); }}

  /* ── Cards ── */
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 16px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-left: 4px solid var(--cc, #818cf8);
    border-radius: var(--radius); padding: 16px 18px;
    display: flex; flex-direction: column; gap: 10px;
    text-decoration: none; color: inherit;
    transition: transform .2s, box-shadow .2s;
    animation: cardIn .3s ease both;
  }}
  .card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 36px rgba(0,0,0,.35); }}
  @keyframes cardIn {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; }} }}
  .card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .source-badge {{
    padding: 3px 10px; border-radius: 999px;
    font-size: .66rem; font-weight: 700; color: #fff; flex-shrink: 0;
  }}
  .card-date   {{ font-size: .68rem; color: var(--muted); text-align: right; line-height: 1.3; }}
  .card-title  {{ font-size: .93rem; font-weight: 650; line-height: 1.45; }}
  .card-summary {{
    font-size: .79rem; color: var(--muted); line-height: 1.55;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  }}
  .card-footer {{ display: flex; justify-content: flex-end; margin-top: auto; padding-top: 4px; }}
  .read-more {{
    font-size: .74rem; color: var(--accent); font-weight: 600;
    display: inline-flex; align-items: center; gap: 3px; transition: gap .15s;
  }}
  .card:hover .read-more {{ gap: 7px; }}
  .no-articles {{
    grid-column: 1/-1; text-align: center; padding: 56px 24px;
    color: var(--muted); font-size: .9rem;
  }}

  /* ── Empty state ── */
  .empty-history {{
    text-align: center; padding: 80px 24px; color: var(--muted);
  }}
  .empty-history .big {{ font-size: 3rem; opacity: .4; margin-bottom: 12px; }}

  /* ── Footer ── */
  footer {{
    text-align: center; padding: 28px 24px;
    font-size: .74rem; color: var(--muted);
    border-top: 1px solid var(--border); margin-top: 16px; line-height: 1.8;
  }}

  /* ── Responsive ── */
  @media (max-width: 768px) {{
    .header-right .stat-chip {{ display: none; }}
    main {{ padding: 14px; }}
    .cards {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="tricolor"></div>

<header>
  <div class="brand">
    <div class="brand-icon">📚</div>
    <div class="brand-text">
      <h1>Current Affairs History</h1>
      <p>Daily digest archive for competitive exam aspirants</p>
    </div>
  </div>
  <div class="header-right">
    <div class="stat-chip">📅 <b>{date_label}</b></div>
    <div class="stat-chip">🗞️ <b>{total}</b> important articles</div>
    <div class="stat-chip">🗄️ Archived: <b>{archived_at}</b></div>
    <button id="theme-btn" onclick="toggleTheme()">☀ Light</button>
  </div>
</header>

<nav class="date-nav">
  {prev_btn}
  <div class="date-select-wrap">
    <label for="date-jump">Jump to:</label>
    <select id="date-jump" onchange="if(this.value) location.href=this.value">
      <option value="">— select date —</option>
      {dates_opts}
    </select>
  </div>
  {next_btn}
  <a class="nav-btn today" href="{live_href}">🏠 Live Report</a>
  <span class="hist-badge">📚 ARCHIVE</span>
</nav>

<div class="tabs-wrapper">
  <div class="tabs" id="tabs">
    {tabs_html}
  </div>
</div>

<main id="main">
  {panels_html}
</main>

<footer>
  Current Affairs History Archive &mdash; Important news digest for {date_label}<br/>
  <span style="opacity:.65">Top stories from: National &middot; Economy &middot; Science &middot; Environment &middot; Polity &middot; Defence &middot; Sports &middot; Awards &middot; Culture</span>
</footer>

<script>
// ── Tab switching ─────────────────────────────────────────────────────────
function switchTab(key) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const btn = document.querySelector(`[data-key="${{key}}"]`);
  const panel = document.getElementById('panel-' + key);
  if (btn)   btn.classList.add('active');
  if (panel) panel.classList.add('active');
}}

// Activate first tab on load
document.addEventListener('DOMContentLoaded', () => {{
  const first = document.querySelector('.tab-btn');
  if (first) switchTab(first.dataset.key);
}});

// ── Theme toggle ─────────────────────────────────────────────────────────
function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent = isLight ? '🌙 Dark' : '☀ Light';
  localStorage.setItem('ca_theme', isLight ? 'light' : 'dark');
}}
if (localStorage.getItem('ca_theme') === 'light') toggleTheme();
</script>

</body>
</html>"""


# ── HTML builders ─────────────────────────────────────────────────────────────

def _build_tabs(categories: dict) -> str:
    parts = []
    for key in _ORDERED_KEYS:
        if key not in categories:
            continue
        meta  = _CAT_META[key]
        count = len(categories[key].get("articles", []))
        parts.append(
            f'<button class="tab-btn" data-key="{key}" '
            f'onclick="switchTab(\'{key}\')">'
            f'{meta["icon"]} {meta["label"]}'
            f'<span class="tab-count">{count}</span></button>'
        )
    return "\n    ".join(parts)


def _build_panels(categories: dict) -> str:
    parts = []
    for key in _ORDERED_KEYS:
        if key not in categories:
            continue
        meta     = _CAT_META[key]
        cat_data = categories[key]
        articles = cat_data.get("articles", [])
        color    = meta["color"]
        count    = len(articles)

        cards_html = _build_cards(articles, color) if articles else (
            '<div class="no-articles">📰 No articles archived for this category.</div>'
        )

        parts.append(f"""
  <div class="panel" id="panel-{key}">
    <div class="panel-header">
      <div class="panel-icon">{meta["icon"]}</div>
      <div>
        <div class="panel-title">{meta["label"]}</div>
        <div class="panel-desc">{cat_data.get("description", "")}</div>
      </div>
      <div class="panel-count"><b>{count}</b> top articles</div>
    </div>
    <div class="cards">
      {cards_html}
    </div>
  </div>""")
    return "\n".join(parts)


def _build_cards(articles: list[dict], color: str) -> str:
    parts = []
    for art in articles:
        title   = _esc(art.get("title", ""))
        summary = _esc(art.get("summary", ""))
        link    = _esc(art.get("link", "#"))
        pub     = _esc(art.get("published", ""))
        source  = _esc(art.get("source", ""))
        parts.append(
            f'      <a class="card" href="{link}" target="_blank" rel="noopener noreferrer"'
            f' style="--cc:{color}">\n'
            f'        <div class="card-top">\n'
            f'          <span class="source-badge" style="background:{color}">{source}</span>\n'
            f'          <span class="card-date">{pub}</span>\n'
            f'        </div>\n'
            f'        <div class="card-title">{title}</div>\n'
            f'        <div class="card-summary">{summary}</div>\n'
            f'        <div class="card-footer"><span class="read-more">Read more &#8594;</span></div>\n'
            f'      </a>'
        )
    return "\n".join(parts)


def _build_date_options(available_dates: list[str], current_key: str,
                        static_mode: bool = False) -> str:
    parts = []
    for d in available_dates:
        href     = f"./{d}.html" if static_mode else f"/history/{d}"
        selected = 'selected' if d == current_key else ''
        parts.append(f'<option value="{href}" {selected}>{d}</option>')
    return "\n      ".join(parts)


def _esc(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
