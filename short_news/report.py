"""
Short News — Report Generator
================================
Renders "Quick Read" — a bite-sized news digest where every story is
condensed to ~60 words (Inshorts-style) so the whole story is understood
in a few seconds, with per-story and per-category reading-time badges.

Theme: "Quick Read" — warm coral-to-gold gradient, bold rounded flashcards,
Poppins display font, a swipeable one-card-at-a-time "Deck Mode" alongside
the default scrollable grid. Distinct from every other agent's theme in
this hub (none of the other 10 use a bright warm gradient + flashcard deck).
"""

from __future__ import annotations

import json

CSS = """
:root {
  --bg1: #ff6b6b;
  --bg2: #feca57;
  --ink: #1f2430;
  --ink-soft: #6b7280;
  --card: #ffffff;
  --accent: #ff5e57;
  --line: #f1e3d3;
  --shadow: 0 10px 26px rgba(31,36,48,0.12);
  --radius: 16px;
  font-family: 'Poppins', 'Inter', sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%) fixed;
  color: var(--ink);
  font-family: 'Poppins', 'Inter', sans-serif;
  padding-bottom: 60px;
  min-height: 100vh;
}
a { color: inherit; }

.skip-link {
  position: absolute; left: -999px; top: 0; background: var(--accent); color: #fff;
  padding: 10px 16px; z-index: 2000; border-radius: 0 0 8px 0; font-size: 0.85rem;
}
.skip-link:focus { left: 0; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; }

header.hero {
  padding: 30px 24px 22px;
  text-align: center;
}
.bolt { font-size: 2.4rem; display: inline-block; margin-bottom: 4px; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.15)); }
header.hero h1 { margin: 0; font-size: 2.1rem; font-weight: 800; color: #fff; text-shadow: 0 2px 10px rgba(0,0,0,0.15); }
header.hero p.sub { margin: 8px 0 0; color: rgba(255,255,255,0.92); font-size: 1rem; font-weight: 500; }
header.hero p.meta { margin: 8px 0 0; color: rgba(255,255,255,0.8); font-size: 0.78rem; }

.wrap { max-width: 1160px; margin: 0 auto; padding: 0 20px; }

.stats-strip {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px;
  margin: 10px auto 18px;
}
.stat-card {
  background: var(--card); border-radius: var(--radius); padding: 14px 16px;
  box-shadow: var(--shadow); text-align: center;
}
.stat-card .num { font-size: 1.6rem; font-weight: 800; color: var(--accent); display: block; }
.stat-card .lbl { font-size: 0.76rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.5px; }

.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 18px 0 10px; }
#search {
  flex: 1; min-width: 220px; padding: 12px 16px; border: none; border-radius: 999px;
  background: var(--card); font-family: inherit; font-size: 0.95rem; color: var(--ink); box-shadow: var(--shadow);
}
.chip {
  padding: 8px 16px; border: none; border-radius: 999px; background: rgba(255,255,255,0.65);
  color: var(--ink); font-size: 0.82rem; cursor: pointer; font-family: inherit; font-weight: 600;
  transition: background 0.15s, color 0.15s, transform 0.1s;
}
.chip.active, .chip:hover { background: var(--ink); color: #fff; transform: translateY(-1px); }

.mode-toggle { display: flex; gap: 8px; }
.mode-btn {
  padding: 8px 16px; border: none; border-radius: 999px; background: rgba(255,255,255,0.65);
  color: var(--ink); font-size: 0.82rem; cursor: pointer; font-family: inherit; font-weight: 700;
}
.mode-btn.active { background: #fff; color: var(--accent); box-shadow: var(--shadow); }

#count-line { font-size: 0.82rem; color: rgba(255,255,255,0.9); margin: 0 0 12px; font-weight: 600; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.story-card {
  background: var(--card); border-radius: var(--radius); padding: 18px 20px;
  box-shadow: var(--shadow); position: relative; transition: transform 0.15s;
}
.story-card:hover { transform: translateY(-3px); }
.cat-badge {
  display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; font-weight: 700;
  padding: 3px 10px; border-radius: 999px; color: #fff; margin-bottom: 8px;
}
.story-card h3 { margin: 0 0 8px; font-size: 1.05rem; line-height: 1.35; font-weight: 700; }
.story-card .summary { font-size: 0.88rem; color: var(--ink-soft); line-height: 1.55; margin: 0 0 12px; }
.story-meta { display: flex; justify-content: space-between; align-items: center; font-size: 0.74rem; color: var(--ink-soft); flex-wrap: wrap; gap: 6px; }
.read-time { font-weight: 700; color: var(--accent); }
.story-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.read-more {
  font-size: 0.8rem; font-weight: 700; color: var(--accent); text-decoration: none;
}
.bookmark-btn {
  background: none; border: none; font-size: 1.1rem; cursor: pointer; color: var(--ink-soft);
}
.bookmark-btn.active { color: #f59e0b; }

/* ── Deck (swipe) mode ── */
#deck-view { display: none; max-width: 520px; margin: 0 auto; }
#deck-view.show { display: block; }
.grid.deck-hidden { display: none; }
.deck-progress { text-align: center; color: #fff; font-weight: 700; margin-bottom: 10px; font-size: 0.85rem; }
.deck-card { min-height: 280px; display: flex; flex-direction: column; justify-content: space-between; }
.deck-nav { display: flex; justify-content: space-between; margin-top: 16px; }
.deck-nav button {
  background: #fff; border: none; border-radius: 999px; padding: 10px 20px; font-weight: 700;
  color: var(--accent); cursor: pointer; font-family: inherit; box-shadow: var(--shadow);
}
.deck-nav button:disabled { opacity: 0.4; cursor: not-allowed; }

.category-summary { font-size: 0.78rem; color: rgba(255,255,255,0.9); margin: -6px 0 14px; font-weight: 600; }

footer { text-align: center; margin-top: 40px; padding: 18px; color: rgba(255,255,255,0.85); font-size: 0.78rem; }
@media (max-width: 560px) { header.hero h1 { font-size: 1.6rem; } }
"""


def _story_card(a: dict, idx: int) -> str:
    return f'''
<div class="story-card" data-idx="{idx}" data-title="{a['title'].lower()}" data-summary="{a['summary'].lower()}"
     data-category="{a['category_key']}" data-link="{a['link']}">
  <span class="cat-badge" style="background:{a['category_color']}">{a['category_icon']} {a['category_label']}</span>
  <h3>{a['title']}</h3>
  <p class="summary">{a['summary']}</p>
  <div class="story-meta">
    <span>{a['source']} &middot; {a['published']}</span>
    <span class="read-time">⏱ {a['read_time']}</span>
  </div>
  <div class="story-actions">
    <a class="read-more" href="{a['link']}" target="_blank" rel="noopener">Read full story →</a>
    <button class="bookmark-btn" onclick="toggleBookmark('{a['link']}', this)" title="Bookmark" aria-label="Bookmark this story">☆</button>
  </div>
</div>'''


def build_html(payload: dict) -> str:
    categories = payload["categories"]
    stats = payload["stats"]

    all_articles = []
    for c in categories:
        all_articles.extend(c["articles"])

    cards_html = "\n".join(_story_card(a, i) for i, a in enumerate(all_articles))

    category_chips = "".join(
        f'<button class="chip" data-filter="{c["key"]}" onclick="setFilter(\'{c["key"]}\', this)">'
        f'{c["icon"]} {c["label"]} ({len(c["articles"])})</button>'
        for c in categories
    )

    category_summary_html = "".join(
        f'<div class="category-summary" data-cat-summary="{c["key"]}" style="display:none">'
        f'{c["icon"]} {c["label"]}: {len(c["articles"])} stories &middot; read them all in '
        f'~{round(c["total_read_seconds"] / 60, 1)} min</div>'
        for c in categories
    )

    articles_json = json.dumps(all_articles, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Short News — Quick Read</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<a class="skip-link" href="#main-content">Skip to main content</a>

<header class="hero">
  <div class="bolt">⚡</div>
  <h1>Short News — Quick Read</h1>
  <p class="sub">Every story in 60 words or less — the full picture, in seconds.</p>
  <p class="meta">Updated {payload['generated_at']} &middot; {stats['total_articles']} stories &middot; read everything in ~{stats['total_read_minutes']} min</p>
</header>

<main id="main-content" class="wrap">

  <div class="stats-strip">
    <div class="stat-card"><span class="num">{stats['total_articles']}</span><span class="lbl">Stories</span></div>
    <div class="stat-card"><span class="num">{stats['total_categories']}</span><span class="lbl">Categories</span></div>
    <div class="stat-card"><span class="num">{stats['total_read_minutes']}</span><span class="lbl">Minutes — Everything</span></div>
  </div>

  <div class="toolbar">
    <label for="search" class="visually-hidden">Search stories</label>
    <input id="search" type="text" placeholder="Search today's stories…" oninput="filterStories()">
    <a href="../" class="chip" style="text-decoration:none" title="Back to India Agents Hub">🏠 Home</a>
    <div class="mode-toggle">
      <button class="mode-btn active" id="grid-mode-btn" onclick="setMode('grid')">▦ Grid</button>
      <button class="mode-btn" id="deck-mode-btn" onclick="setMode('deck')">🂠 Deck</button>
    </div>
  </div>

  <div class="toolbar">
    <button class="chip active" data-filter="all" onclick="setFilter('all', this)">All</button>
    {category_chips}
  </div>

  {category_summary_html}

  <p id="count-line" role="status" aria-live="polite"></p>

  <div class="grid" id="grid">
    {cards_html}
  </div>

  <div id="deck-view" role="region" aria-label="Swipe through stories one at a time">
    <div class="deck-progress" id="deck-progress" role="status" aria-live="polite"></div>
    <div class="grid" style="grid-template-columns:1fr">
      <div class="story-card deck-card" id="deck-card"></div>
    </div>
    <div class="deck-nav">
      <button id="deck-prev" onclick="deckMove(-1)">← Prev</button>
      <button id="deck-next" onclick="deckMove(1)">Next →</button>
    </div>
  </div>

</main>

<footer role="contentinfo">Short News — Quick Read &middot; Crisp, extractive summaries (no AI) from free public RSS feeds &middot; Generated {payload['generated_at']}</footer>

<script>
const ARTICLES = {articles_json};
let currentFilter = 'all';
let deckIdx = 0;
let deckList = ARTICLES;

function cardEls() {{ return document.querySelectorAll('.story-card[data-idx]'); }}

function getBookmarks() {{
  try {{ return JSON.parse(localStorage.getItem('short_news_bookmarks') || '[]'); }} catch(e) {{ return []; }}
}}
function toggleBookmark(link, btn) {{
  let marks = getBookmarks();
  if (marks.includes(link)) {{
    marks = marks.filter(l => l !== link);
    btn.classList.remove('active'); btn.textContent = '☆';
  }} else {{
    marks.push(link);
    btn.classList.add('active'); btn.textContent = '★';
  }}
  localStorage.setItem('short_news_bookmarks', JSON.stringify(marks));
}}
(function initBookmarks() {{
  const marks = getBookmarks();
  document.querySelectorAll('.bookmark-btn').forEach(btn => {{
    const card = btn.closest('.story-card');
    if (card && marks.includes(card.dataset.link)) {{ btn.classList.add('active'); btn.textContent = '★'; }}
  }});
}})();

function setFilter(f, btn) {{
  currentFilter = f;
  document.querySelectorAll('.chip[data-filter]').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('[data-cat-summary]').forEach(el => {{
    el.style.display = (f !== 'all' && el.dataset.catSummary === f) ? 'block' : 'none';
  }});
  filterStories();
}}

function filterStories() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  let shown = 0;
  cardEls().forEach(card => {{
    const matchesText = card.dataset.title.includes(q) || card.dataset.summary.includes(q);
    const matchesCat = currentFilter === 'all' || card.dataset.category === currentFilter;
    const pass = matchesText && matchesCat;
    card.style.display = pass ? '' : 'none';
    if (pass) shown++;
  }});
  document.getElementById('count-line').textContent = `Showing ${{shown}} of {stats['total_articles']} stories`;
  deckList = ARTICLES.filter(a => {{
    const matchesText = a.title.toLowerCase().includes(q) || a.summary.toLowerCase().includes(q);
    const matchesCat = currentFilter === 'all' || a.category_key === currentFilter;
    return matchesText && matchesCat;
  }});
  deckIdx = 0;
  renderDeck();
}}

function setMode(mode) {{
  const grid = document.getElementById('grid');
  const deck = document.getElementById('deck-view');
  document.getElementById('grid-mode-btn').classList.toggle('active', mode === 'grid');
  document.getElementById('deck-mode-btn').classList.toggle('active', mode === 'deck');
  if (mode === 'deck') {{
    grid.classList.add('deck-hidden');
    deck.classList.add('show');
    renderDeck();
  }} else {{
    grid.classList.remove('deck-hidden');
    deck.classList.remove('show');
  }}
}}

function renderDeck() {{
  const card = document.getElementById('deck-card');
  const progress = document.getElementById('deck-progress');
  if (!deckList.length) {{
    card.innerHTML = '<p class="summary">No stories match this search/filter.</p>';
    progress.textContent = '';
    document.getElementById('deck-prev').disabled = true;
    document.getElementById('deck-next').disabled = true;
    return;
  }}
  const a = deckList[deckIdx];
  progress.textContent = `Card ${{deckIdx + 1}} of ${{deckList.length}}`;
  card.innerHTML = `
    <div>
      <span class="cat-badge" style="background:${{a.category_color}}">${{a.category_icon}} ${{a.category_label}}</span>
      <h3>${{a.title}}</h3>
      <p class="summary">${{a.summary}}</p>
    </div>
    <div>
      <div class="story-meta">
        <span>${{a.source}} &middot; ${{a.published}}</span>
        <span class="read-time">⏱ ${{a.read_time}}</span>
      </div>
      <div class="story-actions">
        <a class="read-more" href="${{a.link}}" target="_blank" rel="noopener">Read full story →</a>
        <button class="bookmark-btn ${{getBookmarks().includes(a.link) ? 'active' : ''}}" onclick="toggleBookmark('${{a.link}}', this)" aria-label="Bookmark this story">${{getBookmarks().includes(a.link) ? '★' : '☆'}}</button>
      </div>
    </div>
  `;
  document.getElementById('deck-prev').disabled = deckIdx === 0;
  document.getElementById('deck-next').disabled = deckIdx >= deckList.length - 1;
}}
function deckMove(delta) {{
  deckIdx = Math.max(0, Math.min(deckList.length - 1, deckIdx + delta));
  renderDeck();
}}
document.addEventListener('keydown', e => {{
  if (!document.getElementById('deck-view').classList.contains('show')) return;
  if (e.key === 'ArrowRight') deckMove(1);
  if (e.key === 'ArrowLeft') deckMove(-1);
}});

filterStories();
</script>

</body>
</html>'''
