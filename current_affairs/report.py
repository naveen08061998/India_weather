"""
Current Affairs — HTML Dashboard Generator
============================================
Builds a self-contained, mobile-friendly HTML dashboard
for competitive exam aspirants from the fetched news payload.

Features:
  • Category tabs (National, Economy, Science, etc.)
  • Article cards with title, summary, source badge, date & read-more link
  • Search bar to filter articles by keyword
  • Auto-refresh countdown (every 30 minutes)
  • Dark/light mode toggle
  • Fully offline-capable once loaded (no CDN dependencies)
"""

from __future__ import annotations


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    categories   = payload.get("categories", {})
    total        = payload.get("total_articles", 0)

    tabs_html    = _build_tabs(categories)
    panels_html  = _build_panels(categories)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Current Affairs Daily — {date_label}</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --card: #263246;
    --accent: #6366f1; --text: #e2e8f0; --muted: #94a3b8;
    --border: #334155; --radius: 10px; --shadow: 0 4px 20px rgba(0,0,0,.4);
  }}
  body.light {{
    --bg: #f1f5f9; --surface: #ffffff; --card: #f8fafc;
    --text: #1e293b; --muted: #64748b; --border: #e2e8f0;
    --shadow: 0 4px 20px rgba(0,0,0,.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text);
    min-height: 100vh; transition: background .3s, color .3s;
  }}

  /* ── Header ── */
  header {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 16px 24px; display: flex; align-items: center;
    justify-content: space-between; gap: 12px; flex-wrap: wrap;
    position: sticky; top: 0; z-index: 100;
    box-shadow: var(--shadow);
  }}
  .brand {{ display: flex; align-items: center; gap: 10px; }}
  .brand h1 {{ font-size: 1.25rem; font-weight: 700; }}
  .brand span {{ font-size: .8rem; color: var(--muted); }}
  .header-right {{ display: flex; align-items: center; gap: 10px; }}
  .badge {{
    background: var(--accent); color: #fff; border-radius: 999px;
    padding: 2px 10px; font-size: .75rem; font-weight: 600;
  }}
  #search {{
    padding: 6px 12px; border-radius: 8px;
    border: 1px solid var(--border); background: var(--bg);
    color: var(--text); font-size: .875rem; width: 200px;
    outline: none; transition: border .2s;
  }}
  #search:focus {{ border-color: var(--accent); }}
  #theme-btn {{
    background: none; border: 1px solid var(--border); border-radius: 8px;
    color: var(--text); padding: 6px 10px; cursor: pointer; font-size: .85rem;
  }}

  /* ── Subheader ── */
  .subheader {{
    background: var(--surface); padding: 8px 24px;
    display: flex; align-items: center; gap: 16px;
    font-size: .78rem; color: var(--muted); flex-wrap: wrap;
  }}
  #countdown {{ color: var(--accent); font-weight: 600; }}

  /* ── Tabs ── */
  .tabs-wrapper {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 0 16px; overflow-x: auto; white-space: nowrap;
    position: sticky; top: 57px; z-index: 90;
  }}
  .tabs {{ display: inline-flex; gap: 2px; padding: 6px 0; }}
  .tab-btn {{
    background: none; border: none; color: var(--muted);
    padding: 8px 14px; border-radius: 8px; cursor: pointer;
    font-size: .82rem; font-weight: 500; white-space: nowrap;
    transition: background .15s, color .15s;
  }}
  .tab-btn:hover {{ background: var(--card); color: var(--text); }}
  .tab-btn.active {{ background: var(--accent); color: #fff; }}
  .tab-separator {{
    display: inline-flex; align-items: center; padding: 0 10px;
    color: var(--muted); font-size: .72rem; font-weight: 600;
    letter-spacing: .05em; white-space: nowrap; user-select: none;
  }}
  .tab-btn.state-tab.active {{ background: #0d9488; }}

  /* ── Main layout ── */
  main {{ padding: 24px; max-width: 1200px; margin: 0 auto; }}

  /* ── Panel ── */
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  .panel-header {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 16px; padding-bottom: 12px;
    border-bottom: 2px solid var(--border);
  }}
  .panel-icon {{ font-size: 1.6rem; }}
  .panel-title {{ font-size: 1.1rem; font-weight: 700; }}
  .panel-desc {{ font-size: .8rem; color: var(--muted); margin-top: 2px; }}

  /* ── Cards grid ── */
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px;
    display: flex; flex-direction: column; gap: 8px;
    transition: transform .15s, box-shadow .15s;
    cursor: pointer; text-decoration: none; color: inherit;
  }}
  .card:hover {{
    transform: translateY(-2px); box-shadow: var(--shadow);
  }}
  .card-meta {{
    display: flex; align-items: center; justify-content: space-between;
    font-size: .72rem; color: var(--muted);
  }}
  .source-badge {{
    padding: 2px 8px; border-radius: 999px; font-size: .68rem;
    font-weight: 600; color: #fff;
  }}
  .card-title {{
    font-size: .95rem; font-weight: 600; line-height: 1.4;
  }}
  .card-summary {{ font-size: .82rem; color: var(--muted); line-height: 1.5; }}
  .read-more {{
    display: inline-block; margin-top: 4px; font-size: .78rem;
    color: var(--accent); font-weight: 500;
  }}
  .card:hover .read-more {{ text-decoration: underline; }}
  .no-articles {{
    color: var(--muted); font-size: .9rem; padding: 32px;
    text-align: center; grid-column: 1/-1;
  }}

  /* ── Footer ── */
  footer {{
    text-align: center; padding: 24px;
    font-size: .75rem; color: var(--muted);
    border-top: 1px solid var(--border);
  }}

  /* ── Responsive ── */
  @media (max-width: 600px) {{
    header {{ padding: 12px 16px; }}
    main {{ padding: 16px; }}
    #search {{ width: 140px; }}
    .cards {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div class="brand">
    <div>
      <h1>📰 Current Affairs Daily</h1>
      <span>For UPSC · SSC · Banking · State PSC · Railways</span>
    </div>
  </div>
  <div class="header-right">
    <span class="badge">{total} Articles</span>
    <input type="text" id="search" placeholder="Search news…" oninput="filterCards(this.value)"/>
    <button id="theme-btn" onclick="toggleTheme()">☀ Light</button>
  </div>
</header>

<div class="subheader">
  <span>📅 {date_label}</span>
  <span>🕐 Fetched: {generated_at}</span>
  <span id="countdown-wrap">⏳ <span id="countdown">—</span></span>
</div>

<div class="tabs-wrapper">
  <div class="tabs" id="tabs">
    {tabs_html}
  </div>
</div>

<main id="main">
  {panels_html}
</main>

<footer>
  Current Affairs Daily — Built for competitive exam aspirants &nbsp;|&nbsp;
  Sources: PIB · DD News · The Hindu · Indian Express · Business Standard
</footer>

<script>
// ── Tab switching ──────────────────────────────────────────────────────────
function switchTab(key) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-key="${{key}}"]`).classList.add('active');
  document.getElementById('panel-' + key).classList.add('active');
  currentTab = key;
  filterCards(document.getElementById('search').value);
}}

let currentTab = document.querySelector('.tab-btn')?.dataset.key || '';

// ── Search / filter ────────────────────────────────────────────────────────
function filterCards(query) {{
  const q = query.toLowerCase().trim();
  const panel = document.getElementById('panel-' + currentTab);
  if (!panel) return;
  panel.querySelectorAll('.card').forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.style.display = (!q || text.includes(q)) ? '' : 'none';
  }});
}}

// ── Theme toggle ───────────────────────────────────────────────────────────
function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent = isLight ? '🌙 Dark' : '☀ Light';
  localStorage.setItem('ca_theme', isLight ? 'light' : 'dark');
}}
if (localStorage.getItem('ca_theme') === 'light') toggleTheme();

// ── Countdown / staleness indicator ───────────────────────────────────────
const GENERATED_AT = "{generated_at}";   // e.g. "2026-07-27 10:34 IST"

// Detect mode: 'flask' (localhost/private IP), 'static' (file:// or static host)
// We probe /api/status once; if it responds we're on the Flask server.
let _mode = 'detecting';   // 'flask' | 'static'
(function detectMode() {{
  if (window.location.protocol === 'file:') {{ _mode = 'static'; return; }}
  fetch('/api/status', {{ signal: AbortSignal.timeout(2000) }})
    .then(r => {{ _mode = r.ok ? 'flask' : 'static'; }})
    .catch(() => {{ _mode = 'static'; }});
}})();

function parseIST(str) {{
  // "YYYY-MM-DD HH:MM IST" → Date (treat as UTC+5:30)
  const m = str.match(/(\\d{{4}})-(\\d{{2}})-(\\d{{2}}) (\\d{{2}}):(\\d{{2}})/);
  if (!m) return null;
  return new Date(Date.UTC(+m[1], +m[2]-1, +m[3], +m[4]-5, +m[5]-30));
}}

let _refreshTriggered = false;

function updateCountdown() {{
  if (_mode === 'detecting') return;  // wait for probe to finish

  const genDate = parseIST(GENERATED_AT);
  if (!genDate) return;
  const ageMs  = Date.now() - genDate.getTime();
  const ageMin = Math.floor(ageMs / 60000);
  const el     = document.getElementById('countdown');

  if (_mode === 'static') {{
    // Static host (GitHub Pages, file://) — just show data age
    if (ageMin < 60) {{
      el.textContent = `Data is ${{ageMin}}m old`;
      el.style.color = ageMin > 30 ? '#f59e0b' : '';
    }} else {{
      const h = Math.floor(ageMin / 60), mm = ageMin % 60;
      el.textContent = `Data is ${{h}}h ${{mm}}m old`;
      el.style.color = '#ef4444';
    }}
  }} else {{
    // Served via Flask — countdown to next refresh
    const refreshMs = 30 * 60 * 1000;
    const left = Math.max(0, refreshMs - ageMs);
    const mm = String(Math.floor(left / 60000)).padStart(2, '0');
    const ss = String(Math.floor((left % 60000) / 1000)).padStart(2, '0');
    el.textContent = mm + ':' + ss;
    if (left === 0 && !_refreshTriggered) {{
      _refreshTriggered = true;
      el.textContent = 'Refreshing…';
      fetch('/api/refresh', {{ method: 'POST' }}).catch(() => {{}});
      // Poll /api/status every 3 s; reload only when the refresh has finished
      const _poll = setInterval(() => {{
        fetch('/api/status')
          .then(r => r.json())
          .then(s => {{ if (!s.running) {{ clearInterval(_poll); location.reload(); }} }})
          .catch(() => {{}});
      }}, 3000);
    }}
  }}
}}

setInterval(updateCountdown, 5000);
updateCountdown();

// ── Init first tab ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {{
  const first = document.querySelector('.tab-btn');
  if (first) switchTab(first.dataset.key);
}});
</script>
</body>
</html>"""


# ── HTML builders ──────────────────────────────────────────────────────────

def _build_tabs(categories: dict) -> str:
    from current_affairs.categories import CATEGORIES, STATE_CATEGORIES
    parts = []
    # ── National topic tabs ────────────────────────────────────────────────
    for cat in CATEGORIES:
        key = cat["key"]
        if key not in categories:
            continue
        icon  = cat["icon"]
        label = cat["label"]
        parts.append(
            f'<button class="tab-btn" data-key="{key}" '
            f'onclick="switchTab(\'{key}\')">{icon} {label}</button>'
        )
    # ── Separator ──────────────────────────────────────────────────────────
    if any(c["key"] in categories for c in STATE_CATEGORIES):
        parts.append('<span class="tab-separator">┃ STATE NEWS</span>')
    # ── State tabs ─────────────────────────────────────────────────────────
    for cat in STATE_CATEGORIES:
        key = cat["key"]
        if key not in categories:
            continue
        icon  = cat["icon"]
        label = cat["label"]
        parts.append(
            f'<button class="tab-btn state-tab" data-key="{key}" '
            f'onclick="switchTab(\'{key}\')">{icon} {label}</button>'
        )
    return "\n    ".join(parts)


def _build_panels(categories: dict) -> str:
    from current_affairs.categories import ALL_CATEGORIES
    parts = []
    for cat in ALL_CATEGORIES:
        key = cat["key"]
        if key not in categories:
            continue
        data        = categories[key]
        icon        = cat["icon"]
        label       = cat["label"]
        description = cat.get("description", "")
        color       = cat["color"]
        articles    = data.get("articles", [])

        cards_html = _build_cards(articles, color) if articles else (
            '<p class="no-articles">No articles fetched for this category. '
            'Feeds may be temporarily unavailable.</p>'
        )

        parts.append(f"""
  <div class="panel" id="panel-{key}">
    <div class="panel-header">
      <span class="panel-icon">{icon}</span>
      <div>
        <div class="panel-title">{label}</div>
        <div class="panel-desc">{description}</div>
      </div>
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

        parts.append(f"""      <a class="card" href="{link}" rel="noopener noreferrer">
        <div class="card-meta">
          <span class="source-badge" style="background:{color}">{source}</span>
          <span>{pub}</span>
        </div>
        <div class="card-title">{title}</div>
        <div class="card-summary">{summary}</div>
        <span class="read-more">Read more →</span>
      </a>""")
    return "\n".join(parts)


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
