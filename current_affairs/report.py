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

  /* ── India tricolor accent bar ── */
  .tricolor {{
    height: 4px; position: sticky; top: 0; z-index: 200;
    background: linear-gradient(90deg,
      #f97316 0% 33.3%, #e2e8f0 33.3% 66.6%, #22c55e 66.6% 100%);
  }}
  body.light .tricolor {{
    background: linear-gradient(90deg,
      #f97316 0% 33.3%, #94a3b8 33.3% 66.6%, #22c55e 66.6% 100%);
  }}

  /* ── Header ── */
  header {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 12px 24px; display: flex; align-items: center;
    justify-content: space-between; gap: 12px; flex-wrap: wrap;
    position: sticky; top: 4px; z-index: 100;
    box-shadow: var(--shadow);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .brand-icon {{
    width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; box-shadow: 0 4px 12px rgba(249,115,22,.35);
  }}
  .brand-text h1 {{
    font-size: 1.1rem; font-weight: 800; letter-spacing: -.025em;
  }}
  .brand-text p {{ font-size: .7rem; color: var(--muted); margin-top: 1px; }}

  .header-stats {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .stat-chip {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 999px; padding: 4px 12px;
    font-size: .74rem; color: var(--muted);
    display: inline-flex; align-items: center; gap: 5px;
  }}
  .stat-chip b {{ color: var(--text); font-weight: 600; }}
  #countdown {{ color: var(--accent); font-weight: 700; }}

  .header-right {{ display: flex; align-items: center; gap: 8px; }}
  .search-wrap {{ position: relative; display: flex; align-items: center; }}
  .search-wrap svg {{
    position: absolute; left: 10px; width: 14px; height: 14px;
    color: var(--muted); pointer-events: none; flex-shrink: 0;
  }}
  #search {{
    padding: 7px 12px 7px 32px; border-radius: 10px;
    border: 1px solid var(--border); background: var(--bg);
    color: var(--text); font-size: .8rem; width: 190px; outline: none;
    transition: border .2s, box-shadow .2s; font-family: inherit;
  }}
  #search:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }}
  #theme-btn {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); padding: 7px 12px; cursor: pointer; font-size: .8rem;
    transition: background .2s; white-space: nowrap; font-family: inherit;
  }}
  #theme-btn:hover {{ background: var(--card-h); }}

  /* ── Tabs ── */
  .tabs-wrapper {{
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 0 20px; overflow-x: auto; white-space: nowrap;
    position: sticky; top: 66px; z-index: 90;
    scrollbar-width: none;
  }}
  .tabs-wrapper::-webkit-scrollbar {{ display: none; }}
  .tabs {{ display: inline-flex; gap: 4px; padding: 8px 0; }}
  .tab-btn {{
    background: none; border: none; color: var(--muted);
    padding: 6px 14px; border-radius: 999px; cursor: pointer;
    font-size: .78rem; font-weight: 500; white-space: nowrap;
    transition: background .15s, color .15s, transform .1s, box-shadow .15s;
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
  .tab-separator {{
    display: inline-flex; align-items: center; padding: 0 12px;
    color: var(--muted); font-size: .65rem; font-weight: 800;
    letter-spacing: .1em; text-transform: uppercase; user-select: none;
  }}
  .tab-btn.state-tab.active {{ background: #0d9488; box-shadow: 0 2px 14px rgba(13,148,136,.35); }}

  /* ── Main ── */
  main {{ padding: 24px; max-width: 1280px; margin: 0 auto; }}

  /* ── Panel ── */
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
  .panel-desc {{ font-size: .76rem; color: var(--muted); margin-top: 3px; line-height: 1.4; }}
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
  .card:nth-child(2)  {{ animation-delay: .04s; }}
  .card:nth-child(3)  {{ animation-delay: .07s; }}
  .card:nth-child(4)  {{ animation-delay: .10s; }}
  .card:nth-child(5)  {{ animation-delay: .13s; }}
  .card:nth-child(6)  {{ animation-delay: .16s; }}
  .card:nth-child(n+7) {{ animation-delay: .19s; }}
  @keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: none; }}
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0,0,0,.35), 0 0 0 1px var(--cc, #818cf8);
  }}
  .card-top {{
    display: flex; align-items: center;
    justify-content: space-between; gap: 8px;
  }}
  .source-badge {{
    padding: 3px 10px; border-radius: 999px;
    font-size: .66rem; font-weight: 700; color: #fff;
    letter-spacing: .02em; flex-shrink: 0;
  }}
  .card-date {{ font-size: .68rem; color: var(--muted); text-align: right; line-height: 1.3; }}
  .card-title {{ font-size: .93rem; font-weight: 650; line-height: 1.45; }}
  .card-summary {{
    font-size: .79rem; color: var(--muted); line-height: 1.55;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .card-footer {{
    display: flex; justify-content: flex-end; margin-top: auto; padding-top: 4px;
  }}
  .read-more {{
    font-size: .74rem; color: var(--accent); font-weight: 600;
    display: inline-flex; align-items: center; gap: 3px;
    transition: gap .15s;
  }}
  .card:hover .read-more {{ gap: 7px; }}
  .no-articles {{
    grid-column: 1/-1; text-align: center; padding: 56px 24px;
    color: var(--muted); font-size: .9rem;
  }}
  .no-articles-icon {{ font-size: 2.5rem; margin-bottom: 10px; opacity: .4; }}

  /* ── Footer ── */
  footer {{
    text-align: center; padding: 28px 24px;
    font-size: .74rem; color: var(--muted);
    border-top: 1px solid var(--border); margin-top: 16px;
    line-height: 1.8;
  }}

  /* ── Responsive ── */
  @media (max-width: 768px) {{
    .header-stats {{ display: none; }}
    main {{ padding: 14px; }}
    .cards {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 500px) {{
    header {{ padding: 10px 14px; }}
    .brand-text p {{ display: none; }}
    #search {{ width: 130px; }}
    .panel-count {{ display: none; }}
  }}
</style>
</head>
<body>

<div class="tricolor"></div>

<header>
  <div class="brand">
    <div class="brand-icon">📰</div>
    <div class="brand-text">
      <h1>Current Affairs Daily</h1>
      <p>UPSC &middot; SSC &middot; Banking &middot; State PSC &middot; Railways</p>
    </div>
  </div>
  <div class="header-stats">
    <div class="stat-chip">📅 <b>{date_label}</b></div>
    <div class="stat-chip">🗞️ <b>{total}</b> articles</div>
    <div class="stat-chip">🕐 Fetched: <b>{generated_at}</b></div>
    <div class="stat-chip">⏱ <span id="countdown">—</span></div>
  </div>
  <div class="header-right">
    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" id="search" placeholder="Search articles…"
             oninput="filterCards(this.value)" autocomplete="off"/>
    </div>
    <button id="theme-btn" onclick="toggleTheme()">☀ Light</button>
    <a href="./history/" style="
      background:var(--card);border:1px solid var(--border);border-radius:10px;
      color:var(--text);padding:7px 12px;font-size:.8rem;text-decoration:none;
      transition:background .2s;white-space:nowrap;font-family:inherit;"
      onmouseover="this.style.background='var(--card-h)'"
      onmouseout="this.style.background='var(--card)'">📚 History</a>
  </div>
</header>

<div class="tabs-wrapper">
  <div class="tabs" id="tabs">
    {tabs_html}
  </div>
</div>

<main id="main">
  {panels_html}
</main>

<footer>
  Current Affairs Daily &mdash; Built for competitive exam aspirants<br/>
  <span style="opacity:.65">Sources: PIB &middot; NDTV &middot; Economic Times &middot; LiveMint &middot; DD News</span><br/>
  <span style="opacity:.65">Built by naveen08061998</span>
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
    // Static host (GitHub Pages, file://) — show data age and schedule a
    // single auto-reload timed to the next GitHub Actions deployment.
    // Workflow cron: every 2 hours  →  CYCLE_MIN = 120.
    const CYCLE_MIN    = 120;
    const CI_BUFFER    = 8;    // minutes for CI run + CDN propagation
    const RELOAD_COOL  = 15;   // minimum minutes between reload attempts
    const minsLeft     = CYCLE_MIN - ageMin;

    // ── Display ────────────────────────────────────────────────────────
    if (ageMin < 60) {{
      el.textContent = `Data is ${{ageMin}}m old`;
      el.style.color = ageMin > 30 ? '#f59e0b' : '';
    }} else if (minsLeft > 0) {{
      const h = Math.floor(ageMin / 60), mm = ageMin % 60;
      el.textContent = `Data is ${{h}}h ${{mm}}m old — refresh in ${{minsLeft}}m`;
      el.style.color = '#f59e0b';
    }} else {{
      const h = Math.floor(ageMin / 60), mm = ageMin % 60;
      el.textContent = `Data is ${{h}}h ${{mm}}m old`;
      el.style.color = '#ef4444';
    }}

    // ── Schedule reload (only once per page load) ───────────────────────
    if (!_refreshTriggered) {{
      _refreshTriggered = true;

      if (minsLeft > 0) {{
        // Data is not yet stale — reload exactly when the next deploy lands
        setTimeout(() => location.reload(), (minsLeft + CI_BUFFER) * 60 * 1000);
      }} else {{
        // Data is already past the cycle boundary.
        // Use sessionStorage to prevent a rapid reload loop:
        // if we reloaded within the last RELOAD_COOL minutes and data is
        // still stale (CDN cached old HTML), wait out the remainder first.
        let lastReload = 0;
        try {{ lastReload = parseInt(sessionStorage.getItem('ca_last_reload') || '0'); }} catch(_) {{}}
        const msSinceReload = Date.now() - lastReload;
        const coolMs = RELOAD_COOL * 60 * 1000;
        const waitMs = msSinceReload < coolMs ? coolMs - msSinceReload : 0;

        setTimeout(() => {{
          try {{ sessionStorage.setItem('ca_last_reload', String(Date.now())); }} catch(_) {{}}
          location.reload();
        }}, waitMs);

        // Update display to show when the next reload attempt is
        if (waitMs > 0) {{
          const minsWait = Math.ceil(waitMs / 60000);
          el.textContent = `Stale data — retrying in ${{minsWait}}m`;
          el.style.color = '#f59e0b';
        }} else {{
          el.textContent = 'Checking for latest data…';
          el.style.color = '#22c55e';
        }}
      }}
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
      // Wait 4s before first poll so the background thread has time to
      // acquire the lock and set running=True before we check.
      setTimeout(() => {{
        const _poll = setInterval(() => {{
          fetch('/api/status')
            .then(r => r.json())
            .then(s => {{ if (!s.running) {{ clearInterval(_poll); location.reload(); }} }})
            .catch(() => {{}});
        }}, 3000);
      }}, 4000);
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
        count = len(categories[key].get("articles", []))
        parts.append(
            f'<button class="tab-btn" data-key="{key}" '
            f'onclick="switchTab(\'{key}\')">{icon} {label}'
            f'<span class="tab-count">{count}</span></button>'
        )
    # ── Separator ──────────────────────────────────────────────────────────
    if any(c["key"] in categories for c in STATE_CATEGORIES):
        parts.append('<span class="tab-separator">┃ States</span>')
    # ── State tabs ─────────────────────────────────────────────────────────
    for cat in STATE_CATEGORIES:
        key = cat["key"]
        if key not in categories:
            continue
        icon  = cat["icon"]
        label = cat["label"]
        count = len(categories[key].get("articles", []))
        parts.append(
            f'<button class="tab-btn state-tab" data-key="{key}" '
            f'onclick="switchTab(\'{key}\')">{icon} {label}'
            f'<span class="tab-count">{count}</span></button>'
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
            '<div class="no-articles">'
            '<div class="no-articles-icon">📰</div>'
            'No articles fetched for this category. Feeds may be temporarily unavailable.</div>'
        )

        count = len(articles)
        parts.append(f"""
  <div class="panel" id="panel-{key}">
    <div class="panel-header">
      <div class="panel-icon">{icon}</div>
      <div>
        <div class="panel-title">{label}</div>
        <div class="panel-desc">{description}</div>
      </div>
      <div class="panel-count"><b>{count}</b> articles</div>
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

        parts.append(f"""      <a class="card" href="{link}" target="_blank" rel="noopener noreferrer" style="--cc:{color}">
        <div class="card-top">
          <span class="source-badge" style="background:{color}">{source}</span>
          <span class="card-date">{pub}</span>
        </div>
        <div class="card-title">{title}</div>
        <div class="card-summary">{summary}</div>
        <div class="card-footer"><span class="read-more">Read more &#8594;</span></div>
      </a>""")
    return "\n".join(parts)


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
