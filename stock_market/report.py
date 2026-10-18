"""
Stock Market — HTML Dashboard Generator
==========================================
Trading-terminal aesthetic: black background, monospace green/amber text,
scrolling ticker tape — deliberately distinct from the other agents'
soft "news app" dashboards.
"""

from __future__ import annotations


def _fmt_num(n):
    if n is None:
        return "—"
    return f"{n:,.2f}"


def _arrow(change: float) -> str:
    return "▲" if change >= 0 else "▼"


def _cls(change: float) -> str:
    return "up" if change >= 0 else "down"


def _ticker_item(idx: dict) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f'<span class="tick-item">{idx["name"]} N/A</span>'
    cls = _cls(q["change"])
    return (f'<span class="tick-item {cls}">{idx["name"]} '
            f'{_fmt_num(q["price"])} {_arrow(q["change"])}{q["change_pct"]:+.2f}%</span>')


def _index_card(idx: dict) -> str:
    q = idx.get("quote", {})
    if "error" in q:
        return f"""
      <div class="idx-panel err">
        <div class="idx-head">[{idx['exchange']}] {idx['name']}</div>
        <div class="idx-na">-- NO DATA --</div>
      </div>"""
    cls = _cls(q["change"])
    return f"""
      <div class="idx-panel {cls}">
        <div class="idx-head">[{idx['exchange']}] {idx['name']}</div>
        <div class="idx-price">{_fmt_num(q['price'])}</div>
        <div class="idx-chg">{_arrow(q['change'])} {_fmt_num(abs(q['change']))}  ({q['change_pct']:+.2f}%)</div>
        <div class="idx-range">HI {_fmt_num(q['day_high'])}  LO {_fmt_num(q['day_low'])}</div>
      </div>"""


def _stock_row(s: dict, rank: int) -> str:
    q = s.get("quote", {})
    if "error" in q:
        return ""
    cls = _cls(q["change"])
    return f"""
    <tr class="stock-row {cls}" data-name="{s['name'].lower()}" data-pct="{q['change_pct']}">
      <td class="num muted">{rank:02d}</td>
      <td class="sym">{s['symbol'].replace('.NS','')}</td>
      <td>{s['name']}</td>
      <td class="muted">{s['sector']}</td>
      <td class="num">{_fmt_num(q['price'])}</td>
      <td class="num {cls}">{_arrow(q['change'])} {q['change_pct']:+.2f}%</td>
    </tr>"""


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    indices      = payload.get("indices", [])
    stocks       = payload.get("stocks", [])

    ticker_items = " &nbsp;•&nbsp; ".join(_ticker_item(i) for i in indices)
    index_cards  = "\n".join(_index_card(i) for i in indices)
    stock_rows   = "\n".join(_stock_row(s, i + 1) for i, s in enumerate(stocks))

    valid_stocks = [s for s in stocks if "error" not in s.get("quote", {})]
    gainers = sum(1 for s in valid_stocks if s["quote"]["change"] >= 0)
    losers  = len(valid_stocks) - gainers

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
  .stats {{ display:flex; gap:14px; flex-wrap:wrap; font-size:.72rem; color:var(--muted); }}
  .stats b {{ color:var(--fg); }}
  #theme-btn {{
    background:var(--panel); border:1px solid var(--grid); color:var(--fg);
    padding:6px 12px; cursor:pointer; font-family:inherit; font-size:.72rem; border-radius:var(--radius);
  }}

  main {{ max-width:1200px; margin:0 auto; padding:22px 24px 40px; }}
  .indices-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:26px; }}
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
  table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--grid); }}
  th, td {{ padding:8px 12px; text-align:left; font-size:.76rem; border-bottom:1px solid var(--grid); }}
  th {{ color:var(--muted); font-size:.64rem; text-transform:uppercase; letter-spacing:.06em; background:var(--panel-h); font-weight:500; }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.sym {{ font-weight:700; }}
  td.muted {{ color:var(--muted); }}
  tr.stock-row:hover {{ background:var(--panel-h); }}
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

  <div class="section-head">TOP MOVERS — CURATED NSE LARGE-CAP <span>30 symbols</span></div>
  <div class="toolbar">
    <span class="prompt">&gt;</span>
    <input id="search" type="text" placeholder="grep company / sector…" oninput="filterStocks()"/>
    <button class="sort-btn active" id="sort-gainers" onclick="sortStocks('gainers')">SORT: GAINERS</button>
    <button class="sort-btn" id="sort-losers" onclick="sortStocks('losers')">SORT: LOSERS</button>
  </div>
  <table>
    <thead>
      <tr><th>#</th><th>SYM</th><th>NAME</th><th>SECTOR</th><th class="num">PRICE ₹</th><th class="num">CHG%</th></tr>
    </thead>
    <tbody id="stock-tbody">
      {stock_rows}
    </tbody>
  </table>

  <div class="disclaimer">
    // DATA: Yahoo Finance free public quote endpoint, delayed ~15min. Informational use only — not investment advice.
  </div>
</main>
<footer>:: free public market data feed :: no key required ::</footer>
<script>
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
    document.querySelectorAll('#stock-tbody tr').forEach(row => {{
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
  }}
  function sortStocks(mode) {{
    document.getElementById('sort-gainers').classList.toggle('active', mode === 'gainers');
    document.getElementById('sort-losers').classList.toggle('active', mode === 'losers');
    const tbody = document.getElementById('stock-tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.sort((a, b) => {{
      const pa = parseFloat(a.dataset.pct), pb = parseFloat(b.dataset.pct);
      return mode === 'gainers' ? pb - pa : pa - pb;
    }});
    rows.forEach(r => tbody.appendChild(r));
  }}
  sortStocks('gainers');
</script>
</body>
</html>"""
