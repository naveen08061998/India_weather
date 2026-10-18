"""
Government Updates — HTML Dashboard Generator
================================================
Official notice-board / letterhead aesthetic: parchment background, navy
header bar, serif headings, stamp-style badges — deliberately distinct
from the other agents' app-like dashboards.

Three sections:
  1. Scheme & Policy Announcements (live news, keyword-filtered)
  2. Exam/Recruitment News (live news, keyword-filtered)
  3. Exam Notification Calendar (static curated reference data)
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

_MONTHS = ["January","February","March","April","May","June","July",
           "August","September","October","November","December"]


def _article_card(a: dict, ref: int) -> str:
    return f"""
    <a class="notice-slip" href="{a['link']}" target="_blank" rel="noopener noreferrer">
      <div class="slip-ref">Ref. {ref:03d}</div>
      <div class="slip-title">{a['title']}</div>
      <div class="slip-summary">{a['summary']}</div>
      <div class="slip-meta"><span class="slip-source">{a['source']}</span> &middot; {a['published']}</div>
    </a>"""


def _exam_card(e: dict, current_month: str) -> str:
    is_now = current_month in e.get("notify_month", "")
    cls = "bulletin highlight" if is_now else "bulletin"
    stamp = '<span class="stamp">Notification<br/>Window</span>' if is_now else ""
    return f"""
    <div class="{cls}" data-name="{e['name'].lower()}" data-category="{e['category'].lower()}">
      {stamp}
      <div class="bulletin-name">{e['name']}</div>
      <div class="bulletin-body">{e['body']} &middot; <span class="bulletin-cat">{e['category']}</span></div>
      <div class="bulletin-dates">Notification: <b>{e['notify_month']}</b> &nbsp;|&nbsp; Exam: <b>{e['exam_month']}</b></div>
      <div class="bulletin-note">{e['note']}</div>
      <a class="bulletin-link" href="{e['site']}" target="_blank" rel="noopener noreferrer">Official website &rarr;</a>
    </div>"""


def build_html(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    date_label   = payload.get("date", "")
    schemes      = payload.get("schemes", [])
    exams_news   = payload.get("exams_news", [])
    exam_calendar = payload.get("exam_calendar", [])

    current_month = _MONTHS[datetime.now(IST).month - 1]

    scheme_cards = "\n".join(_article_card(a, i + 1) for i, a in enumerate(schemes)) or \
        '<p class="empty-note">No scheme-related releases matched in the current feed window.</p>'
    exam_news_cards = "\n".join(_article_card(a, i + 1) for i, a in enumerate(exams_news)) or \
        '<p class="empty-note">No exam-related releases matched in the current feed window.</p>'
    calendar_cards = "\n".join(_exam_card(e, current_month) for e in exam_calendar)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Government Schemes &amp; Exam Tracker — {date_label}</title>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:#f1ead9; --paper:#fbf8f0; --paper-h:#f4eedb;
    --navy:#122a52; --saffron:#d97706; --green:#166534; --maroon:#7f1d1d;
    --text:#241e14; --muted:#6b6250; --border:#d9cdab;
    --radius:3px; --shadow:0 3px 10px rgba(36,30,20,.12);
  }}
  body.ink {{
    --bg:#0d1420; --paper:#121b2c; --paper-h:#182338;
    --navy:#0a1120; --saffron:#f59e0b; --green:#4ade80; --maroon:#f87171;
    --text:#e8e3d4; --muted:#8893a6; --border:#27354d;
    --shadow:0 3px 14px rgba(0,0,0,.4);
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'Noto Sans','Segoe UI',system-ui,sans-serif; color:var(--text); min-height:100vh;
    background:
      repeating-linear-gradient(0deg, rgba(0,0,0,.015) 0px, rgba(0,0,0,.015) 1px, transparent 1px, transparent 28px),
      var(--bg);
  }}
  .tricolor {{ height:5px; background:linear-gradient(90deg,var(--saffron) 0% 33.3%,#e8e3d4 33.3% 66.6%,var(--green) 66.6% 100%); }}
  header {{
    background:var(--navy); color:#f1ead9; padding:20px 28px; border-bottom:3px solid var(--saffron);
    display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;
  }}
  .letterhead {{ display:flex; align-items:center; gap:14px; }}
  .seal {{
    width:48px; height:48px; border-radius:50%; border:2px solid var(--saffron);
    display:flex; align-items:center; justify-content:center; font-size:1.5rem; flex-shrink:0;
  }}
  .letterhead h1 {{ font-family:'Merriweather',serif; font-size:1.15rem; font-weight:700; letter-spacing:.01em; }}
  .letterhead p {{ font-size:.72rem; color:#cbd5e1; letter-spacing:.04em; text-transform:uppercase; margin-top:2px; }}
  .stat-chip {{
    background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.2); border-radius:3px;
    padding:5px 12px; font-size:.72rem; color:#dbe3ee;
  }}
  .stat-chip b {{ color:#fff; }}
  #theme-btn {{
    background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.25); border-radius:3px;
    color:#fff; padding:8px 14px; cursor:pointer; font-size:.76rem; font-family:inherit;
  }}
  main {{ max-width:1100px; margin:0 auto; padding:28px; }}
  .section-title {{
    font-family:'Merriweather',serif; font-size:1.05rem; font-weight:700; margin:30px 0 14px;
    padding-bottom:8px; border-bottom:2px solid var(--navy); display:flex; align-items:baseline; gap:10px;
  }}
  .section-title:first-child {{ margin-top:0; }}
  .section-title span {{ font-family:'Noto Sans',sans-serif; font-weight:500; font-size:.76rem; color:var(--muted); }}

  .article-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; }}
  .notice-slip {{
    background:var(--paper); border:1px solid var(--border); border-left:4px solid var(--maroon);
    border-radius:var(--radius); padding:16px; box-shadow:var(--shadow); text-decoration:none; color:var(--text);
    display:block; transition:transform .15s;
  }}
  .notice-slip:hover {{ transform:translateY(-2px); background:var(--paper-h); }}
  .slip-ref {{ font-size:.64rem; color:var(--maroon); font-weight:700; letter-spacing:.06em; margin-bottom:6px; }}
  .slip-title {{ font-family:'Merriweather',serif; font-weight:700; font-size:.88rem; margin-bottom:6px; line-height:1.4; }}
  .slip-summary {{ font-size:.78rem; color:var(--muted); line-height:1.55; margin-bottom:10px; }}
  .slip-meta {{ font-size:.68rem; color:var(--muted); border-top:1px dashed var(--border); padding-top:8px; }}
  .slip-source {{ color:var(--navy); font-weight:700; }}
  body.ink .slip-source {{ color:var(--saffron); }}
  .empty-note {{ color:var(--muted); font-size:.85rem; padding:12px 0; font-style:italic; }}

  .toolbar {{ display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap; }}
  #search {{
    flex:1; min-width:200px; padding:9px 12px; border-radius:var(--radius); border:1px solid var(--border);
    background:var(--paper); color:var(--text); font-family:inherit; outline:none;
  }}
  .exam-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; }}
  .bulletin {{
    background:var(--paper); border:1px solid var(--border); border-radius:var(--radius);
    padding:16px; box-shadow:var(--shadow); position:relative;
  }}
  .bulletin.highlight {{ border-color:var(--green); box-shadow:0 0 0 1px var(--green); }}
  .stamp {{
    position:absolute; top:10px; right:12px; border:2px solid var(--maroon); color:var(--maroon);
    border-radius:50%; width:58px; height:58px; display:flex; align-items:center; justify-content:center;
    text-align:center; font-size:.58rem; font-weight:700; line-height:1.15; transform:rotate(-12deg);
    text-transform:uppercase; letter-spacing:.02em;
  }}
  .bulletin-name {{ font-family:'Merriweather',serif; font-weight:700; font-size:.9rem; margin-bottom:6px; padding-right:50px; }}
  .bulletin-body {{ font-size:.75rem; color:var(--muted); margin-bottom:8px; }}
  .bulletin-cat {{ color:var(--navy); font-weight:700; }}
  body.ink .bulletin-cat {{ color:var(--saffron); }}
  .bulletin-dates {{ font-size:.76rem; margin-bottom:8px; }}
  .bulletin-note {{ font-size:.74rem; color:var(--muted); line-height:1.5; margin-bottom:10px; }}
  .bulletin-link {{ font-size:.75rem; color:var(--maroon); font-weight:700; text-decoration:none; }}
  .bulletin-link:hover {{ text-decoration:underline; }}
  .disclaimer {{
    background:var(--paper); border:1px dashed var(--border); border-radius:var(--radius);
    padding:14px 18px; font-size:.78rem; color:var(--muted); margin:22px 0; font-style:italic;
  }}
  footer {{ text-align:center; color:var(--muted); font-size:.72rem; padding:24px; }}
</style>
</head>
<body>
<div class="tricolor"></div>
<header>
  <div class="letterhead">
    <div class="seal">🏛️</div>
    <div>
      <h1>Government Schemes &amp; Exam Tracker</h1>
      <p>Public Information Digest &middot; {date_label}</p>
    </div>
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <span class="stat-chip">Issued <b id="generated-at">{generated_at}</b></span>
    <span class="stat-chip">Schemes <b>{len(schemes)}</b></span>
    <span class="stat-chip">Exam News <b>{len(exams_news)}</b></span>
  </div>
  <button id="theme-btn" onclick="toggleTheme()">📄 Paper</button>
</header>
<main>
  <div class="section-title">Scheme &amp; Policy Announcements <span>(live news, keyword-filtered)</span></div>
  <div class="article-grid">
    {scheme_cards}
  </div>

  <div class="section-title">Exam &amp; Recruitment News <span>(live news, keyword-filtered)</span></div>
  <div class="article-grid">
    {exam_news_cards}
  </div>

  <div class="section-title">Exam Notification Calendar <span>(curated reference — verify dates on the official site)</span></div>
  <div class="toolbar">
    <input id="search" type="text" placeholder="Search exam, body or category…" oninput="filterExams()"/>
  </div>
  <div class="exam-grid" id="exam-grid">
    {calendar_cards}
  </div>

  <div class="disclaimer">
    This bulletin is auto-compiled from public news RSS feeds by keyword match — it may occasionally
    miss or mis-tag an article. The Exam Notification Calendar is hand-compiled from publicly known past
    cycles; actual notification/exam dates change every year — always confirm on the linked official
    website before taking any action.
  </div>
</main>
<footer>Compiled from free public news feeds &middot; No API key required</footer>
<script>
  function toggleTheme() {{
    document.body.classList.toggle('ink');
    const btn = document.getElementById('theme-btn');
    btn.textContent = document.body.classList.contains('ink') ? '🌙 Ink' : '📄 Paper';
    localStorage.setItem('gov_theme', document.body.classList.contains('ink') ? 'ink' : 'paper');
  }}
  if (localStorage.getItem('gov_theme') === 'ink') {{
    document.body.classList.add('ink');
    document.getElementById('theme-btn').textContent = '🌙 Ink';
  }}
  function filterExams() {{
    const q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('#exam-grid .bulletin').forEach(card => {{
      const match = card.dataset.name.includes(q) || card.dataset.category.includes(q);
      card.style.display = match ? '' : 'none';
    }});
  }}
</script>
</body>
</html>"""
