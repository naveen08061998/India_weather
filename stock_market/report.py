"""
Stock Market — HTML Dashboard Generator
==========================================
Premium dark dashboard aesthetic: glassmorphic cards, indigo/gold gradient
accents, gradient-filled area charts — deliberately distinct from the
other agents' dashboards (and from this file's earlier terminal look).

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


def _sparkline_svg(points: list, width: int = 140, height: int = 36, grad_id: str = "sg") -> str:
    """Tiny inline SVG trend line (with a soft gradient fill) from [[date, price], ...] points."""
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
        coords.append((x, y))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"2,{height - 2} " + polyline + f" {width - 2:.1f},{height - 2}"
    stroke = "var(--up)" if values[-1] >= values[0] else "var(--down)"
    return f"""
    <svg class="sparkline" viewBox="0 0 {width} {height}" preserveAspectRatio="none" aria-hidden="true">
      <defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{stroke}" stop-opacity=".35"/>
        <stop offset="100%" stop-color="{stroke}" stop-opacity="0"/>
      </linearGradient></defs>
      <polygon points="{area}" fill="url(#{grad_id})"/>
      <polyline points="{polyline}" fill="none" stroke="{stroke}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""


def _intraday_svg(prices: list, color_var: str, grad_id: str, width: int = 170, height: int = 48) -> str:
    if len(prices) < 2:
        return ""
    lo, hi = min(prices), max(prices)
    span = max(hi - lo, 1e-6)
    n = len(prices)
    coords = []
    for i, v in enumerate(prices):
        x = (i / (n - 1)) * (width - 2) + 1
        y = height - 1 - ((v - lo) / span) * (height - 2)
        coords.append((x, y))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"1,{height - 1} " + polyline + f" {width - 1:.1f},{height - 1}"
    return f"""
    <svg class="intraday-chart" viewBox="0 0 {width} {height}" preserveAspectRatio="none" aria-hidden="true">
      <defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{color_var}" stop-opacity=".4"/>
        <stop offset="100%" stop-color="{color_var}" stop-opacity="0"/>
      </linearGradient></defs>
      <polygon points="{area}" fill="url(#{grad_id})"/>
      <polyline points="{polyline}" fill="none" stroke="{color_var}" stroke-width="2"/>
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
            f'&nbsp;&middot;&nbsp; {from_high:+.1f}% from 52w high</div>')


def _ticker_item(idx: dict) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f'<span class="tick-item">{idx["name"]} N/A</span>'
    cls = _cls(q["change"])
    return (f'<span class="tick-item {cls}">{idx["name"]} '
            f'{_fmt_num(q["price"])} {_arrow(q["change"])}{q["change_pct"]:+.2f}%</span>')


def _index_card(idx: dict, intraday: dict, i: int) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f"""
      <div class="glass-card idx-panel err">
        <div class="idx-head">{idx['exchange']} &middot; {idx['name']}</div>
        <div class="idx-na">No data available</div>
      </div>"""
    cls = _cls(q["change"])
    chart = _intraday_svg(intraday.get(idx["symbol"], []), f"var(--{cls})", f"idx-grad-{i}")
    return f"""
      <div class="glass-card idx-panel {cls}">
        <div class="idx-head">{idx['exchange']} &middot; {idx['name']}</div>
        <div class="idx-price">{_fmt_num(q['price'])}</div>
        <div class="idx-chg">{_arrow(q['change'])} {_fmt_num(abs(q['change']))} &nbsp;({q['change_pct']:+.2f}%)</div>
        <div class="idx-range">Day: {_fmt_num(q['day_low'])} – {_fmt_num(q['day_high'])}</div>
        {chart}
      </div>"""


def _commodity_card(c: dict) -> str:
    q = c.get("quote", {})
    if "error" in q:
        return f'<div class="glass-card idx-panel err commodity"><div class="idx-head">{c["name"]}</div><div class="idx-na">No data</div></div>'
    cls = _cls(q["change"])
    return f"""
      <div class="glass-card idx-panel {cls} commodity">
        <div class="idx-head">{c['name']}</div>
        <div class="idx-price">{_fmt_num(q['price'])}{c.get('unit', '')}</div>
        <div class="idx-chg">{_arrow(q['change'])} {q['change_pct']:+.2f}%</div>
      </div>"""


def _heatmap_cell(h: dict) -> str:
    pct = h["avg_change_pct"]
    cls = "up" if pct >= 0 else "down"
    intensity = min(abs(pct) / 3, 1)
    return f"""
    <div class="glass-card heat-cell {cls}" style="--heat-a:{.18 + intensity * .5:.2f}">
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
      <td class="num">₹{_fmt_num(q['price'])}</td>
      <td class="num"><span class="pct-pill {cls}">{_arrow(q['change'])} {q['change_pct']:+.2f}%</span></td>
      <td class="num">
        <button class="star-btn" data-sym="{s['symbol']}" onclick="toggleWatch(this)" aria-label="Toggle watchlist">☆</button>
        <button class="expand-btn" aria-expanded="false" onclick="toggleRow(this, '{safe_id}')">⌄</button>
      </td>
    </tr>
    <tr class="detail-row" id="detail-{safe_id}" hidden>
      <td colspan="7">
        {_day_range_bar(q)}
        {_week52_info(q)}
        <div class="trend-wrap">{_sparkline_svg(trend_points, grad_id=f"sg-{safe_id}")}</div>
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


def _index_data_js(indices: list) -> str:
    rows = []
    for idx in indices:
        q = idx.get("quote", {})
        if "error" in q:
            continue
        rows.append({
            "symbol": idx["symbol"], "name": idx["name"], "exchange": idx["exchange"],
            "price": q["price"], "change": q["change"], "change_pct": q["change_pct"],
            "day_low": q.get("day_low"), "day_high": q.get("day_high"),
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

    ticker_items = " &nbsp;&bull;&nbsp; ".join(_ticker_item(i) for i in indices)
    index_cards  = "\n".join(_index_card(i, intraday, n) for n, i in enumerate(indices))
    commodity_cards = "\n".join(_commodity_card(c) for c in commodities)
    stock_rows   = "\n".join(_stock_row(s, i + 1, trends.get(s["symbol"], [])) for i, s in enumerate(stocks))
    heatmap_cells = "\n".join(_heatmap_cell(h) for h in sector_heatmap)
    news_rows = "\n".join(_news_item(a) for a in news) or '<p class="news-empty">No market headlines matched right now.</p>'

    valid_stocks = [s for s in stocks if "error" not in s.get("quote", {})]
    gainers = sum(1 for s in valid_stocks if s["quote"]["change"] >= 0)
    losers  = len(valid_stocks) - gainers

    status_html = (
        '<span class="market-open">&#9679; Market Open</span>' if market_status.get("is_open")
        else '<span class="market-closed">&#9679; Market Closed</span>'
    )

    stock_data_js = _stock_data_js(stocks)
    index_data_js = _index_data_js(indices)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Indian Stock Market — {date_label}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:#0a0d16; --bg2:#0f1320; --glass:rgba(255,255,255,.045); --glass-h:rgba(255,255,255,.08);
    --border:rgba(255,255,255,.09); --accent:#f5c451; --accent2:#818cf8;
    --up:#34d399; --down:#f87171; --text:#eef0f7; --muted:#8a8fa3;
    --radius:18px; --shadow:0 12px 40px rgba(0,0,0,.45);
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'Manrope','Segoe UI',system-ui,sans-serif;
    background:
      radial-gradient(900px 500px at 10% -10%, rgba(245,196,81,.08) 0%, transparent 60%),
      radial-gradient(800px 500px at 100% 0%, rgba(129,140,248,.1) 0%, transparent 55%),
      var(--bg);
    color:var(--text); min-height:100vh;
  }}
  .glass-card {{
    background:var(--glass); border:1px solid var(--border); border-radius:var(--radius);
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px); box-shadow:var(--shadow);
    transition:transform .18s, background .18s;
  }}
  .ticker-bar {{
    background:rgba(10,13,22,.85); backdrop-filter:blur(10px); border-bottom:1px solid var(--border);
    overflow:hidden; white-space:nowrap; padding:9px 0; position:sticky; top:0; z-index:200;
  }}
  .ticker-track {{ display:inline-block; animation:scroll-left 30s linear infinite; }}
  .ticker-track span {{ font-size:.82rem; font-weight:600; }}
  @keyframes scroll-left {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
  .tick-item {{ margin:0 6px; }}
  .tick-item.up {{ color:var(--up); }}
  .tick-item.down {{ color:var(--down); }}

  header {{
    border-bottom:1px solid var(--border); padding:18px 26px;
    display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;
  }}
  .brand {{ display:flex; align-items:center; gap:12px; }}
  .brand-icon {{
    width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center;
    font-size:1.3rem; background:linear-gradient(135deg,var(--accent) 0%,#c9881f 100%); box-shadow:var(--shadow);
  }}
  .brand h1 {{ font-size:1.18rem; font-weight:800; letter-spacing:-.01em; }}
  .brand p {{ font-size:.72rem; color:var(--muted); margin-top:1px; }}
  .stats {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
  .stat-chip {{
    background:var(--glass); border:1px solid var(--border); border-radius:999px;
    padding:6px 14px; font-size:.74rem; color:var(--muted);
  }}
  .stat-chip b {{ color:var(--text); font-weight:700; }}
  .market-open {{ color:var(--up); font-weight:700; }}
  .market-closed {{ color:var(--down); font-weight:700; }}

  main {{ max-width:1220px; margin:0 auto; padding:26px; }}
  .indices-grid, .commodities-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; margin-bottom:28px; }}
  .idx-panel {{ padding:18px 20px; position:relative; overflow:hidden; }}
  .idx-panel.up {{ border-top:3px solid var(--up); }}
  .idx-panel.down {{ border-top:3px solid var(--down); }}
  .idx-head {{ font-size:.72rem; color:var(--muted); font-weight:600; letter-spacing:.02em; }}
  .idx-price {{ font-size:1.9rem; font-weight:800; margin:8px 0 4px; }}
  .idx-chg {{ font-size:.85rem; font-weight:600; }}
  .up {{ color:var(--up); }} .down {{ color:var(--down); }}
  .idx-range {{ font-size:.7rem; color:var(--muted); margin-top:6px; }}
  .idx-na {{ color:var(--muted); font-size:.8rem; margin-top:10px; }}
  .intraday-chart {{ width:100%; height:48px; margin-top:10px; display:block; }}

  .section-head {{
    font-size:1rem; font-weight:800; margin:0 0 14px; display:flex; justify-content:space-between; align-items:baseline;
  }}
  .section-head span {{ color:var(--muted); font-weight:500; font-size:.76rem; }}
  .toolbar {{ display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap; align-items:center; }}
  #search {{
    flex:1; min-width:200px; padding:10px 16px; border-radius:999px; border:1px solid var(--border);
    background:var(--glass); color:var(--text); font-family:inherit; font-size:.82rem; outline:none;
  }}
  .sort-btn {{
    background:var(--glass); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:9px 16px; cursor:pointer; font-size:.76rem; font-family:inherit; font-weight:600;
  }}
  .sort-btn.active {{ background:var(--accent); color:#1a1304; border-color:var(--accent); }}

  table {{ width:100%; border-collapse:separate; border-spacing:0 6px; margin-bottom:28px; }}
  th {{ color:var(--muted); font-size:.68rem; text-transform:uppercase; letter-spacing:.05em; text-align:left; padding:0 14px 6px; font-weight:600; }}
  th.num {{ text-align:right; }}
  td {{ padding:12px 14px; font-size:.82rem; background:var(--glass); border-top:1px solid var(--border); border-bottom:1px solid var(--border); }}
  tr.stock-row td:first-child {{ border-left:1px solid var(--border); border-radius:14px 0 0 14px; }}
  tr.stock-row td:last-child {{ border-right:1px solid var(--border); border-radius:0 14px 14px 0; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.sym {{ font-weight:800; }}
  td.muted {{ color:var(--muted); }}
  tr.stock-row:hover td {{ background:var(--glass-h); }}
  .pct-pill {{ padding:3px 10px; border-radius:999px; font-weight:700; font-size:.76rem; }}
  .pct-pill.up {{ background:rgba(52,211,153,.14); }}
  .pct-pill.down {{ background:rgba(248,113,113,.14); }}
  .star-btn, .expand-btn {{
    background:none; border:1px solid var(--border); color:var(--muted); border-radius:8px;
    width:26px; height:26px; cursor:pointer; font-family:inherit; font-size:.8rem; line-height:1;
  }}
  .star-btn.active {{ color:var(--accent); border-color:var(--accent); }}
  tr.detail-row td {{ background:transparent; border:none; padding:6px 20px 16px; }}
  .range-row {{ display:flex; align-items:center; gap:10px; margin-bottom:10px; }}
  .range-label {{ font-size:.72rem; color:var(--muted); }}
  .range-bar {{ flex:1; height:5px; background:var(--border); border-radius:3px; position:relative; }}
  .range-dot {{ position:absolute; top:-3px; width:11px; height:11px; border-radius:50%; background:var(--accent); transform:translateX(-50%); box-shadow:0 0 8px var(--accent); }}
  .week52 {{ font-size:.72rem; color:var(--muted); margin-bottom:10px; }}
  .sparkline {{ width:160px; height:36px; display:block; }}
  .trend-empty {{ font-size:.7rem; color:var(--muted); font-style:italic; }}

  .heatmap-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:10px; margin-bottom:28px; }}
  .heat-cell {{ padding:14px; text-align:center; }}
  .heat-cell.up {{ background:rgba(52,211,153,var(--heat-a)); }}
  .heat-cell.down {{ background:rgba(248,113,113,var(--heat-a)); }}
  .heat-sector {{ font-size:.72rem; font-weight:700; color:var(--muted); }}
  .heat-pct {{ font-size:1.05rem; font-weight:800; margin:4px 0; }}
  .heat-count {{ font-size:.66rem; color:var(--muted); }}

  .news-list {{ display:flex; flex-direction:column; gap:8px; margin-bottom:28px; }}
  .news-row {{
    display:flex; justify-content:space-between; gap:14px; padding:14px 18px;
    text-decoration:none; color:var(--text); font-size:.84rem;
  }}
  .news-row:hover {{ background:var(--glass-h); }}
  .news-title {{ flex:1; font-weight:600; }}
  .news-meta {{ color:var(--muted); font-size:.7rem; white-space:nowrap; }}
  .news-empty {{ padding:16px; color:var(--muted); font-size:.82rem; }}

  .sim-box {{ padding:20px; margin-bottom:28px; }}
  .sim-result {{ font-size:.9rem; margin-top:14px; line-height:1.9; }}
  .sim-note {{ font-size:.7rem; color:var(--muted); margin-top:10px; }}

  .modal-overlay {{
    display:none; position:fixed; inset:0; background:rgba(5,6,12,.72); backdrop-filter:blur(4px); z-index:1000;
    align-items:center; justify-content:center; padding:20px;
  }}
  .modal-overlay.show {{ display:flex; }}
  .compare-modal {{ padding:26px; max-width:620px; width:100%; max-height:85vh; overflow:auto; }}
  .compare-modal h3 {{ margin-bottom:16px; font-size:1.05rem; }}
  .compare-selects {{ display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap; }}
  .compare-selects select {{
    flex:1; min-width:160px; padding:10px; border-radius:12px; border:1px solid var(--border);
    background:var(--bg2); color:var(--text); font-family:inherit;
  }}
  #compare-table {{ width:100%; border-collapse:collapse; }}
  #compare-table th, #compare-table td {{ padding:9px 10px; font-size:.8rem; border-bottom:1px solid var(--border); background:none; }}
  .close-modal {{
    margin-top:16px; background:var(--glass); border:1px solid var(--border); border-radius:999px;
    color:var(--text); padding:8px 18px; cursor:pointer; font-family:inherit; font-size:.8rem; font-weight:600;
  }}

  footer {{ text-align:center; color:var(--muted); font-size:.74rem; padding:30px; }}
  .disclaimer {{ padding:16px 20px; font-size:.76rem; color:var(--muted); margin-top:22px; line-height:1.6; }}
</style>
</head>
<body>
<a href="../" title="Back to India Agents Hub" aria-label="Back to India Agents Hub" style="position:fixed;top:14px;left:14px;z-index:1500;background:rgba(0,0,0,0.55);color:#fff;padding:8px 14px;border-radius:20px;font-family:system-ui,sans-serif;font-size:0.82rem;text-decoration:none;backdrop-filter:blur(4px);box-shadow:0 4px 10px rgba(0,0,0,0.25);">🏠 Home</a>
<div class="ticker-bar"><div class="ticker-track">{ticker_items} &nbsp;&bull;&nbsp; {ticker_items}</div></div>
<header>
  <div class="brand">
    <div class="brand-icon">📈</div>
    <div>
      <h1>Indian Stock Market</h1>
      <p>{date_label}</p>
    </div>
  </div>
  <div class="stats">
    <span class="stat-chip">{status_html}</span>
    <span class="stat-chip">Synced <b id="generated-at">{generated_at}</b></span>
    <span class="stat-chip">🟢 Up <b>{gainers}</b></span>
    <span class="stat-chip">🔴 Down <b>{losers}</b></span>
  </div>
</header>
<main>
  <div class="section-head">Indices <button class="sort-btn" style="margin-left:auto" onclick="openIndexCompare()">📊 Compare Indices</button></div>
  <div class="indices-grid">
    {index_cards}
  </div>

  <div class="section-head">FX &amp; Commodities</div>
  <div class="commodities-grid">
    {commodity_cards}
  </div>

  <div class="section-head">Sector Heatmap <span>avg % change, curated stocks</span></div>
  <div class="heatmap-grid">
    {heatmap_cells}
  </div>

  <div class="section-head">Top Movers <span>30 curated NSE large-caps</span></div>
  <div class="toolbar">
    <input id="search" type="text" placeholder="🔍 Search company or sector…" oninput="filterStocks()"/>
    <button class="sort-btn active" id="sort-gainers" onclick="sortStocks('gainers')">Top Gainers</button>
    <button class="sort-btn" id="sort-losers" onclick="sortStocks('losers')">Top Losers</button>
    <button class="sort-btn" id="watch-filter-btn" onclick="toggleWatchFilter()">☆ Watchlist</button>
    <button class="sort-btn" onclick="openCompare()">⚖️ Compare</button>
  </div>
  <table>
    <thead>
      <tr><th>#</th><th>Symbol</th><th>Name</th><th>Sector</th><th class="num">Price</th><th class="num">Change</th><th class="num"></th></tr>
    </thead>
    <tbody id="stock-tbody">
      {stock_rows}
    </tbody>
  </table>

  <div class="section-head">Newswire <span>market-related headlines, keyword-filtered</span></div>
  <div class="glass-card news-list">
    {news_rows}
  </div>

  <div class="section-head">Portfolio Simulator <span>illustrative only</span></div>
  <div class="glass-card sim-box">
    <button class="sort-btn" onclick="runSimulator()">▶ Simulate ₹1,00,000 across today's top 5 gainers</button>
    <div class="sim-result" id="sim-result"></div>
    <div class="sim-note">Hypothetical equal-weight split, using today's intraday % change only. Not investment advice.</div>
  </div>

  <div class="glass-card disclaimer">
    ⚠️ Data from Yahoo Finance's free public quote endpoint, delayed ~15min. Market status is a simple
    weekday/time check (not a holiday calendar). Informational use only — not investment advice.
  </div>
</main>
<footer>Built with free public market data · No API key required</footer>

<div class="modal-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title">
  <div class="glass-card compare-modal">
    <h3 id="compare-title">⚖️ Compare Stocks</h3>
    <div class="compare-selects">
      <select id="compare-a"></select>
      <select id="compare-b"></select>
    </div>
    <table id="compare-table"></table>
    <button class="close-modal" onclick="closeCompare()">Close</button>
  </div>
</div>

<div class="modal-overlay" id="index-compare-overlay" role="dialog" aria-modal="true" aria-labelledby="index-compare-title">
  <div class="glass-card compare-modal">
    <h3 id="index-compare-title">📊 Compare Indices</h3>
    <div class="compare-selects">
      <select id="index-compare-a"></select>
      <select id="index-compare-b"></select>
    </div>
    <table id="index-compare-table"></table>
    <button class="close-modal" onclick="closeIndexCompare()">Close</button>
  </div>
</div>

<script>
  const STOCK_DATA = {stock_data_js};
  const INDEX_DATA = {index_data_js};

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
    btn.textContent = expanded ? '⌄' : '⌃';
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

  // ── Compare indices modal ────────────────────────────────────────────────
  function openIndexCompare() {{
    const a = document.getElementById('index-compare-a'), b = document.getElementById('index-compare-b');
    if (!a.options.length) {{
      INDEX_DATA.forEach((idx, i) => {{ a.add(new Option(idx.name, i)); b.add(new Option(idx.name, i)); }});
      b.selectedIndex = Math.min(1, INDEX_DATA.length - 1);
      a.onchange = b.onchange = renderIndexCompare;
    }}
    document.getElementById('index-compare-overlay').classList.add('show');
    renderIndexCompare();
  }}
  function closeIndexCompare() {{ document.getElementById('index-compare-overlay').classList.remove('show'); }}
  function renderIndexCompare() {{
    const a = INDEX_DATA[document.getElementById('index-compare-a').value || 0];
    const b = INDEX_DATA[document.getElementById('index-compare-b').value || 1];
    if (!a || !b) return;
    const rows = [
      ['Price', a.price, b.price], ['Change %', a.change_pct, b.change_pct],
      ['Exchange', a.exchange, b.exchange],
      ['Day Low/High', `${{a.day_low}} / ${{a.day_high}}`, `${{b.day_low}} / ${{b.day_high}}`],
    ];
    document.getElementById('index-compare-table').innerHTML =
      `<tr><th>${{a.name}}</th><th>Metric</th><th>${{b.name}}</th></tr>` +
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
