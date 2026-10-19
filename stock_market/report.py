"""
Stock Market — HTML Dashboard Generator
==========================================
Trading-terminal aesthetic: black background, monospace green/amber text,
scrolling ticker tape — deliberately distinct from the other agents'
soft "news app" dashboards.

Features: market-open/closed badge, FX & commodities ticker, intraday
index mini-charts, sector heatmap, per-stock expandable detail (day-range
bar, 52-week range, historical trend sparkline), a watchlist (localStorage),
a 2-stock compare modal, a market newswire, and an illustrative portfolio
simulator.
"""

from __future__ import annotations

import json


def _fmt_num(n):
    if n is None:
        return "—"
    return f"{n:,.2f}"


def _arrow(change: float) -> str:
    return "▲" if change >= 0 else "▼"


def _cls(change: float) -> str:
    return "up" if change >= 0 else "down"


def _sparkline_svg(points: list, width: int = 140, height: int = 32) -> str:
    """Tiny inline SVG trend line from [[date, price], ...] points (oldest-first)."""
    if len(points) < 2:
        return '<div class="trend-empty">Building trend… check back after a few daily refreshes.</div>'
    values = [p[1] for p in points]
    lo, hi = min(values), max(values)
    span = max(hi - lo, 1e-6)
    n = len(values)
    coords = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * (width - 4) + 2
        y = height - 2 - ((v - lo) / span) * (height - 4)
        coords.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(coords)
    stroke = "var(--up)" if values[-1] >= values[0] else "var(--down)"
    return f"""
    <svg class="sparkline" viewBox="0 0 {width} {height}" preserveAspectRatio="none" aria-hidden="true">
      <polyline points="{polyline}" fill="none" stroke="{stroke}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""


def _intraday_svg(prices: list, color_var: str, width: int = 160, height: int = 40) -> str:
    if len(prices) < 2:
        return ""
    lo, hi = min(prices), max(prices)
    span = max(hi - lo, 1e-6)
    n = len(prices)
    coords = []
    for i, v in enumerate(prices):
        x = (i / (n - 1)) * (width - 2) + 1
        y = height - 1 - ((v - lo) / span) * (height - 2)
        coords.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(coords)
    return f"""
    <svg class="intraday-chart" viewBox="0 0 {width} {height}" preserveAspectRatio="none" aria-hidden="true">
      <polyline points="{polyline}" fill="none" stroke="{color_var}" stroke-width="1.6"/>
    </svg>"""


def _day_range_bar(q: dict) -> str:
    lo, hi, price = q.get("day_low"), q.get("day_high"), q.get("price")
    if lo is None or hi is None or price is None or hi <= lo:
        return ""
    pct = max(0, min((price - lo) / (hi - lo) * 100, 100))
    return f"""
    <div class="range-row">
      <span class="range-label">{_fmt_num(lo)}</span>
      <div class="range-bar"><div class="range-dot" style="left:{pct:.1f}%"></div></div>
      <span class="range-label">{_fmt_num(hi)}</span>
    </div>"""


def _week52_info(q: dict) -> str:
    yh, yl, price = q.get("year_high"), q.get("year_low"), q.get("price")
    if yh is None or yl is None or price is None:
        return ""
    from_high = (price - yh) / yh * 100 if yh else 0
    return (f'<div class="week52">52w Range: {_fmt_num(yl)} – {_fmt_num(yh)} '
            f'&nbsp;|&nbsp; {from_high:+.1f}% from 52w high</div>')


def _ticker_item(idx: dict) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f'<span class="tick-item">{idx["name"]} N/A</span>'
    cls = _cls(q["change"])
    return (f'<span class="tick-item {cls}">{idx["name"]} '
            f'{_fmt_num(q["price"])} {_arrow(q["change"])}{q["change_pct"]:+.2f}%</span>')


def _index_card(idx: dict, intraday: dict) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f"""
      <div class="idx-panel err">
        <div class="idx-head">[{idx['exchange']}] {idx['name']}</div>
        <div class="idx-na">-- NO DATA --</div>
      </div>"""
    cls = _cls(q["change"])
    chart = _intraday_svg(intraday.get(idx["symbol"], []), f"var(--{cls})")
    return f"""
      <div class="idx-panel {cls}">
        <div class="idx-head">[{idx['exchange']}] {idx['name']}</div>
        <div class="idx-price">{_fmt_num(q['price'])}</div>
        <div class="idx-chg">{_arrow(q['change'])} {_fmt_num(abs(q['change']))}  ({q['change_pct']:+.2f}%)</div>
        <div class="idx-range">HI {_fmt_num(q['day_high'])}  LO {_fmt_num(q['day_low'])}</div>
        {chart}
      </div>"""


def _commodity_card(c: dict) -> str:
    q = c.get("quote", {})
    if "error" in q:
        return f'<div class="idx-panel err"><div class="idx-head">{c["name"]}</div><div class="idx-na">-- NO DATA --</div></div>'
    cls = _cls(q["change"])
    return f"""
      <div class="idx-panel {cls} commodity">
        <div class="idx-head">{c['name']}</div>
        <div class="idx-price">{_fmt_num(q['price'])}{c.get('unit', '')}</div>
        <div class="idx-chg">{_arrow(q['change'])} {q['change_pct']:+.2f}%</div>
      </div>"""


def _heatmap_cell(h: dict) -> str:
    pct = h["avg_change_pct"]
    cls = "up" if pct >= 0 else "down"
    intensity = min(abs(pct) / 3, 1)
    return f"""
    <div class="heat-cell {cls}" style="opacity:{.35 + intensity * .65:.2f}">
      <div class="heat-sector">{h['sector']}</div>
      <div class="heat-pct">{pct:+.2f}%</div>
      <div class="heat-count">{h['count']} stock{'s' if h['count'] != 1 else ''}</div>
    </div>"""


def _news_item(a: dict) -> str:
    return f"""
    <a class="news-row" href="{a['link']}" target="_blank" rel="noopener noreferrer">
      <span class="news-title">{a['title']}</span>
      <span class="news-meta">{a['source']} &middot; {a['published']}</span>
    </a>"""


def _stock_row(s: dict, rank: int, trend_points: list) -> str:
    q = s.get("quote", {})
    if "error" in q:
        return ""
    cls = _cls(q["change"])
    safe_id = s["symbol"].replace(".", "-")
    return f"""
    <tr class="stock-row {cls}" data-name="{s['name'].lower()}" data-pct="{q['change_pct']}" data-detail="detail-{safe_id}">
      <td class="num muted">{rank:02d}</td>
      <td class="sym">{s['symbol'].replace('.NS','')}</td>
      <td>{s['name']}</td>
      <td class="muted">{s['sector']}</td>
      <td class="num">{_fmt_num(q['price'])}</td>
      <td class="num {cls}">{_arrow(q['change'])} {q['change_pct']:+.2f}%</td>
      <td class="num">
        <button class="star-btn" data-sym="{s['symbol']}" onclick="toggleWatch(this)" aria-label="Toggle watchlist">☆</button>
        <button class="expand-btn" aria-expanded="false" onclick="toggleRow(this, '{safe_id}')">+</button>
      </td>
    </tr>
    <tr class="detail-row" id="detail-{safe_id}" hidden>
      <td colspan="7">
        {_day_range_bar(q)}
        {_week52_info(q)}
        <div class="trend-wrap">{_sparkline_svg(trend_points)}</div>
      </td>
    </tr>"""


def _stock_data_js(stocks: list) -> str:
    rows = []
    for s in stocks:
        q = s.get("quote", {})
        if "error" in q:
            continue
        rows.append({
            "symbol": s["symbol"], "name": s["name"], "sector": s["sector"],
            "price": q["price"], "change_pct": q["change_pct"],
            "day_low": q.get("day_low"), "day_high": q.get("day_high"),
            "year_low": q.get("year_low"), "year_high": q.get("year_high"),
        })
    return json.dumps(rows, ensure_ascii=False)


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    indices      = payload.get("indices", [])
    stocks       = payload.get("stocks", [])
    commodities  = payload.get("commodities", [])
    intraday     = payload.get("intraday", {})
    trends       = payload.get("trends", {})
    market_status = payload.get("market_status", {})
    sector_heatmap = payload.get("sector_heatmap", [])
    news         = payload.get("news", [])

    ticker_items = " &nbsp;•&nbsp; ".join(_ticker_item(i) for i in indices)
    index_cards  = "\n".join(_index_card(i, intraday) for i in indices)
    commodity_cards = "\n".join(_commodity_card(c) for c in commodities)
    stock_rows   = "\n".join(_stock_row(s, i + 1, trends.get(s["symbol"], [])) for i, s in enumerate(stocks))
    heatmap_cells = "\n".join(_heatmap_cell(h) for h in sector_heatmap)
    news_rows = "\n".join(_news_item(a) for a in news) or '<p class="news-empty">No market headlines matched right now.</p>'

    valid_stocks = [s for s in stocks if "error" not in s.get("quote", {})]
    gainers = sum(1 for s in valid_stocks if s["quote"]["change"] >= 0)
    losers  = len(valid_stocks) - gainers

    status_html = (
        '<span class="market-open">● MARKET OPEN</span>' if market_status.get("is_open")
        else '<span class="market-closed">● MARKET CLOSED</span>'
    )

    stock_data_js = _stock_data_js(stocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>MKT// Indian Stock Terminal — {date_label}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:#060706; --panel:#0c0f0c; --panel-h:#121712; --grid:#1d2a1d;
    --fg:#39ff7a; --fg-dim:#1f8c48; --up:#39ff7a; --down:#ff3b4e; --muted:#5f7a63;
    --radius:4px; --glow:0 0 8px rgba(57,255,122,.25);
  }}
  body.amber {{
    --fg:#ffb000; --fg-dim:#a66d00; --up:#ffb000; --down:#ff3b4e; --muted:#8a6a2f;
    --grid:#2a2013; --panel:#0f0b05; --panel-h:#161006;
    --glow:0 0 8px rgba(255,176,0,.25);
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'IBM Plex Mono', 'Consolas', monospace;
    background:
      repeating-linear-gradient(0deg, rgba(255,255,255,.015) 0px, rgba(255,255,255,.015) 1px, transparent 1px, transparent 3px),
      var(--bg);
    color:var(--fg); min-height:100vh;
  }}
  .ticker-bar {{
    background:#000; border-bottom:1px solid var(--grid); overflow:hidden;
    white-space:nowrap; padding:6px 0; position:sticky; top:0; z-index:200;
  }}
  .ticker-track {{ display:inline-block; animation:scroll-left 28s linear infinite; }}
  .ticker-track span {{ font-size:.78rem; }}
  @keyframes scroll-left {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
  .tick-item.up {{ color:var(--up); }}
  .tick-item.down {{ color:var(--down); }}

  header {{
    border-bottom:1px solid var(--grid); padding:16px 24px;
    display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;
  }}
  .brand {{ display:flex; align-items:baseline; gap:10px; }}
  .brand h1 {{ font-size:1.1rem; font-weight:700; letter-spacing:.06em; text-shadow:var(--glow); }}
  .brand .blink {{ animation:blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity:0; }} }}
  .brand p {{ font-size:.7rem; color:var(--muted); }}
  .stats {{ display:flex; gap:14px; flex-wrap:wrap; font-size:.72rem; color:var(--muted); align-items:center; }}
  .stats b {{ color:var(--fg); }}
  .market-open {{ color:var(--up); font-weight:700; }}
  .market-closed {{ color:var(--down); font-weight:700; }}
  #theme-btn {{
    background:var(--panel); border:1px solid var(--grid); color:var(--fg);
    padding:6px 12px; cursor:pointer; font-family:inherit; font-size:.72rem; border-radius:var(--radius);
  }}

  main {{ max-width:1200px; margin:0 auto; padding:22px 24px 40px; }}
  .indices-grid, .commodities-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:26px; }}
  .idx-panel {{
    background:var(--panel); border:1px solid var(--grid); border-radius:var(--radius); padding:14px 16px;
  }}
  .idx-panel.up {{ box-shadow:inset 3px 0 0 var(--up); }}
  .idx-panel.down {{ box-shadow:inset 3px 0 0 var(--down); }}
  .idx-head {{ font-size:.68rem; color:var(--muted); letter-spacing:.05em; }}
  .idx-price {{ font-size:1.7rem; font-weight:700; margin:6px 0 2px; text-shadow:var(--glow); }}
  .idx-chg.up, .idx-chg {{ font-size:.8rem; }}
  .up {{ color:var(--up); }} .down {{ color:var(--down); }}
  .idx-range {{ font-size:.68rem; color:var(--muted); margin-top:6px; }}
  .idx-na {{ color:var(--down); font-size:.78rem; margin-top:8px; }}
  .intraday-chart {{ width:100%; height:40px; margin-top:8px; display:block; }}

  .section-head {{
    font-size:.82rem; letter-spacing:.08em; color:var(--fg); border-bottom:1px dashed var(--grid);
    padding-bottom:8px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;
  }}
  .section-head span {{ color:var(--muted); font-size:.68rem; letter-spacing:0; }}
  .toolbar {{ display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap; align-items:center; }}
  .prompt {{ color:var(--fg-dim); }}
  #search {{
    flex:1; min-width:200px; padding:7px 10px; border-radius:var(--radius); border:1px solid var(--grid);
    background:#000; color:var(--fg); font-family:inherit; font-size:.78rem; outline:none;
  }}
  .sort-btn {{
    background:var(--panel); border:1px solid var(--grid); border-radius:var(--radius);
    color:var(--fg); padding:7px 12px; cursor:pointer; font-size:.7rem; font-family:inherit; letter-spacing:.04em;
  }}
  .sort-btn.active {{ background:var(--fg); color:#000; }}
  table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--grid); margin-bottom:26px; }}
  th, td {{ padding:8px 12px; text-align:left; font-size:.76rem; border-bottom:1px solid var(--grid); }}
  th {{ color:var(--muted); font-size:.64rem; text-transform:uppercase; letter-spacing:.06em; background:var(--panel-h); font-weight:500; }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.sym {{ font-weight:700; }}
  td.muted {{ color:var(--muted); }}
  tr.stock-row:hover {{ background:var(--panel-h); }}
  .star-btn, .expand-btn {{
    background:none; border:1px solid var(--grid); color:var(--muted); border-radius:3px;
    width:22px; height:22px; cursor:pointer; font-family:inherit; font-size:.72rem; line-height:1;
  }}
  .star-btn.active {{ color:#ffd84d; border-color:#ffd84d; }}
  tr.detail-row td {{ background:var(--panel-h); padding:12px 16px; }}
  .range-row {{ display:flex; align-items:center; gap:8px; margin-bottom:8px; }}
  .range-label {{ font-size:.68rem; color:var(--muted); }}
  .range-bar {{ flex:1; height:4px; background:var(--grid); border-radius:2px; position:relative; }}
  .range-dot {{ position:absolute; top:-3px; width:10px; height:10px; border-radius:50%; background:var(--fg); transform:translateX(-50%); }}
  .week52 {{ font-size:.68rem; color:var(--muted); margin-bottom:8px; }}
  .sparkline {{ width:140px; height:32px; display:block; }}
  .trend-empty {{ font-size:.66rem; color:var(--muted); font-style:italic; }}

  .heatmap-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:8px; margin-bottom:26px; }}
  .heat-cell {{ border-radius:var(--radius); padding:10px; text-align:center; }}
  .heat-cell.up {{ background:var(--up); color:#000; }}
  .heat-cell.down {{ background:var(--down); color:#000; }}
  .heat-sector {{ font-size:.66rem; font-weight:700; }}
  .heat-pct {{ font-size:.9rem; font-weight:700; margin:2px 0; }}
  .heat-count {{ font-size:.6rem; opacity:.8; }}

  .news-row {{
    display:flex; justify-content:space-between; gap:12px; padding:9px 12px; border-bottom:1px solid var(--grid);
    text-decoration:none; color:var(--fg); font-size:.76rem;
  }}
  .news-row:hover {{ background:var(--panel-h); }}
  .news-title {{ flex:1; }}
  .news-meta {{ color:var(--muted); font-size:.66rem; white-space:nowrap; }}
  .news-list {{ background:var(--panel); border:1px solid var(--grid); border-radius:var(--radius); margin-bottom:26px; }}
  .news-empty {{ padding:14px; color:var(--muted); font-size:.76rem; }}

  .sim-box {{ background:var(--panel); border:1px solid var(--grid); border-radius:var(--radius); padding:16px; margin-bottom:26px; }}
  .sim-result {{ font-size:1rem; margin-top:10px; }}
  .sim-note {{ font-size:.66rem; color:var(--muted); margin-top:6px; }}

  .modal-overlay {{
    display:none; position:fixed; inset:0; background:rgba(0,0,0,.75); z-index:1000;
    align-items:center; justify-content:center; padding:20px;
  }}
  .modal-overlay.show {{ display:flex; }}
  .compare-modal {{
    background:var(--bg); border:1px solid var(--grid); border-radius:var(--radius);
    padding:22px; max-width:600px; width:100%; max-height:85vh; overflow:auto;
  }}
  .compare-selects {{ display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap; }}
  .compare-selects select {{
    flex:1; min-width:150px; padding:8px; border-radius:var(--radius); border:1px solid var(--grid);
    background:var(--panel); color:var(--fg); font-family:inherit;
  }}
  .close-modal {{
    margin-top:14px; background:var(--panel); border:1px solid var(--grid); border-radius:var(--radius);
    color:var(--fg); padding:7px 16px; cursor:pointer; font-family:inherit; font-size:.76rem;
  }}

  footer {{ text-align:center; color:var(--muted); font-size:.68rem; padding:28px; }}
  .disclaimer {{
    border:1px dashed var(--grid); border-radius:var(--radius); padding:12px 16px;
    font-size:.7rem; color:var(--muted); margin-top:20px;
  }}
</style>
</head>
<body>
<div class="ticker-bar"><div class="ticker-track">{ticker_items} &nbsp;•&nbsp; {ticker_items}</div></div>
<header>
  <div class="brand">
    <h1>MKT<span class="blink">_</span>// INDIAN MARKET TERMINAL</h1>
    <p>{date_label}</p>
  </div>
  <div class="stats">
    {status_html}
    <span>SYNC <b id="generated-at">{generated_at}</b></span>
    <span>UP <b>{gainers}</b></span>
    <span>DOWN <b>{losers}</b></span>
  </div>
  <button id="theme-btn" onclick="toggleTheme()">MODE: GREEN</button>
</header>
<main>
  <div class="indices-grid">
    {index_cards}
  </div>

  <div class="section-head">FX &amp; COMMODITIES</div>
  <div class="commodities-grid">
    {commodity_cards}
  </div>

  <div class="section-head">SECTOR HEATMAP <span>avg % change, curated stocks</span></div>
  <div class="heatmap-grid">
    {heatmap_cells}
  </div>

  <div class="section-head">TOP MOVERS — CURATED NSE LARGE-CAP <span>30 symbols</span></div>
  <div class="toolbar">
    <span class="prompt">&gt;</span>
    <input id="search" type="text" placeholder="grep company / sector…" oninput="filterStocks()"/>
    <button class="sort-btn active" id="sort-gainers" onclick="sortStocks('gainers')">SORT: GAINERS</button>
    <button class="sort-btn" id="sort-losers" onclick="sortStocks('losers')">SORT: LOSERS</button>
    <button class="sort-btn" id="watch-filter-btn" onclick="toggleWatchFilter()">☆ WATCHLIST</button>
    <button class="sort-btn" onclick="openCompare()">COMPARE</button>
  </div>
  <table>
    <thead>
      <tr><th>#</th><th>SYM</th><th>NAME</th><th>SECTOR</th><th class="num">PRICE ₹</th><th class="num">CHG%</th><th class="num">​</th></tr>
    </thead>
    <tbody id="stock-tbody">
      {stock_rows}
    </tbody>
  </table>

  <div class="section-head">NEWSWIRE <span>market-related headlines, keyword-filtered</span></div>
  <div class="news-list">
    {news_rows}
  </div>

  <div class="section-head">PORTFOLIO SIMULATOR <span>illustrative only</span></div>
  <div class="sim-box">
    <button class="sort-btn" onclick="runSimulator()">▶ SIMULATE ₹1,00,000 ACROSS TODAY'S TOP 5 GAINERS</button>
    <div class="sim-result" id="sim-result"></div>
    <div class="sim-note">// Hypothetical equal-weight split, using today's intraday % change only. Not investment advice.</div>
  </div>

  <div class="disclaimer">
    // DATA: Yahoo Finance free public quote endpoint, delayed ~15min. Market status is a simple weekday/time check
    (not a holiday calendar). Informational use only — not investment advice.
  </div>
</main>
<footer>:: free public market data feed :: no key required ::</footer>

<div class="modal-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title">
  <div class="compare-modal">
    <h3 id="compare-title">COMPARE STOCKS</h3>
    <div class="compare-selects">
      <select id="compare-a"></select>
      <select id="compare-b"></select>
    </div>
    <table id="compare-table"></table>
    <button class="close-modal" onclick="closeCompare()">CLOSE</button>
  </div>
</div>

<script>
  const STOCK_DATA = {stock_data_js};

  function toggleTheme() {{
    document.body.classList.toggle('amber');
    const btn = document.getElementById('theme-btn');
    btn.textContent = document.body.classList.contains('amber') ? 'MODE: AMBER' : 'MODE: GREEN';
    localStorage.setItem('stock_theme', document.body.classList.contains('amber') ? 'amber' : 'green');
  }}
  if (localStorage.getItem('stock_theme') === 'amber') {{
    document.body.classList.add('amber');
    document.getElementById('theme-btn').textContent = 'MODE: AMBER';
  }}

  function filterStocks() {{
    const q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('#stock-tbody tr.stock-row').forEach(row => {{
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
  }}

  function sortStocks(mode) {{
    document.getElementById('sort-gainers').classList.toggle('active', mode === 'gainers');
    document.getElementById('sort-losers').classList.toggle('active', mode === 'losers');
    const tbody = document.getElementById('stock-tbody');
    const rows = Array.from(tbody.querySelectorAll('tr.stock-row'));
    rows.sort((a, b) => {{
      const pa = parseFloat(a.dataset.pct), pb = parseFloat(b.dataset.pct);
      return mode === 'gainers' ? pb - pa : pa - pb;
    }});
    rows.forEach(r => {{
      tbody.appendChild(r);
      const detail = document.getElementById(r.dataset.detail);
      if (detail) tbody.appendChild(detail);
    }});
  }}
  sortStocks('gainers');

  function toggleRow(btn, id) {{
    const row = document.getElementById('detail-' + id);
    const expanded = !row.hidden;
    row.hidden = expanded;
    btn.setAttribute('aria-expanded', String(!expanded));
    btn.textContent = expanded ? '+' : '−';
  }}

  // ── Watchlist (localStorage) ─────────────────────────────────────────────
  function _getWatchlist() {{
    try {{ return JSON.parse(localStorage.getItem('stock_watchlist') || '[]'); }} catch {{ return []; }}
  }}
  function toggleWatch(btn) {{
    const sym = btn.dataset.sym;
    let list = _getWatchlist();
    if (list.includes(sym)) {{ list = list.filter(s => s !== sym); btn.classList.remove('active'); btn.textContent = '☆'; }}
    else {{ list.push(sym); btn.classList.add('active'); btn.textContent = '★'; }}
    localStorage.setItem('stock_watchlist', JSON.stringify(list));
  }}
  (function initWatchStars() {{
    const list = _getWatchlist();
    document.querySelectorAll('.star-btn').forEach(btn => {{
      if (list.includes(btn.dataset.sym)) {{ btn.classList.add('active'); btn.textContent = '★'; }}
    }});
  }})();
  let _watchFilterOn = false;
  function toggleWatchFilter() {{
    _watchFilterOn = !_watchFilterOn;
    document.getElementById('watch-filter-btn').classList.toggle('active', _watchFilterOn);
    const list = _getWatchlist();
    document.querySelectorAll('#stock-tbody tr.stock-row').forEach(row => {{
      const sym = row.querySelector('.star-btn').dataset.sym;
      row.style.display = (!_watchFilterOn || list.includes(sym)) ? '' : 'none';
    }});
  }}

  // ── Compare modal ────────────────────────────────────────────────────────
  function openCompare() {{
    const a = document.getElementById('compare-a'), b = document.getElementById('compare-b');
    if (!a.options.length) {{
      STOCK_DATA.forEach((s, i) => {{ a.add(new Option(s.name, i)); b.add(new Option(s.name, i)); }});
      b.selectedIndex = Math.min(1, STOCK_DATA.length - 1);
      a.onchange = b.onchange = renderCompare;
    }}
    document.getElementById('compare-overlay').classList.add('show');
    renderCompare();
  }}
  function closeCompare() {{ document.getElementById('compare-overlay').classList.remove('show'); }}
  function renderCompare() {{
    const a = STOCK_DATA[document.getElementById('compare-a').value || 0];
    const b = STOCK_DATA[document.getElementById('compare-b').value || 1];
    if (!a || !b) return;
    const rows = [
      ['Price (₹)', a.price, b.price], ['Change %', a.change_pct, b.change_pct],
      ['Sector', a.sector, b.sector], ['Day Low/High', `${{a.day_low}} / ${{a.day_high}}`, `${{b.day_low}} / ${{b.day_high}}`],
      ['52w Low/High', `${{a.year_low}} / ${{a.year_high}}`, `${{b.year_low}} / ${{b.year_high}}`],
    ];
    document.getElementById('compare-table').innerHTML =
      `<tr><th>${{a.symbol.replace('.NS','')}}</th><th>Metric</th><th>${{b.symbol.replace('.NS','')}}</th></tr>` +
      rows.map(([label, av, bv]) => `<tr><td>${{av}}</td><td>${{label}}</td><td>${{bv}}</td></tr>`).join('');
  }}

  // ── Portfolio simulator (illustrative, client-side only) ────────────────
  function runSimulator() {{
    const top5 = [...STOCK_DATA].sort((a, b) => b.change_pct - a.change_pct).slice(0, 5);
    const perStock = 100000 / 5;
    let total = 0;
    const lines = top5.map(s => {{
      const value = perStock * (1 + s.change_pct / 100);
      total += value;
      return `${{s.symbol.replace('.NS','')}}: ₹${{perStock.toFixed(0)}} → ₹${{value.toFixed(0)}} (${{s.change_pct > 0 ? '+' : ''}}${{s.change_pct.toFixed(2)}}%)`;
    }});
    const gain = total - 100000;
    document.getElementById('sim-result').innerHTML =
      lines.join('<br>') +
      `<br><br><b class="${{gain >= 0 ? 'up' : 'down'}}">TOTAL: ₹${{total.toFixed(0)}} (${{gain >= 0 ? '+' : ''}}₹${{gain.toFixed(0)}})</b>`;
  }}
</script>
</body>
</html>"""
