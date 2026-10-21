"""
Abbreviations — Report Generator
===================================
Renders "The Lexicon" — a searchable dictionary-style dashboard of general
abbreviations spanning government, defence, finance, technology, science,
education, international bodies, law, sport and everyday usage.

Theme: Dictionary / Index-Card Lexicon — ivory paper background, deep
plum/burgundy ink, serif body text with a monospace treatment for each
abbreviation's short code (like a print dictionary headword), gold rule
lines. Distinct from every other agent's theme in this hub (monochrome
newsprint, maroon departure-board, amber weather, navy+saffron parchment,
dark glass stocks, blue/purple AQI, green/teal atlas, asphalt highways).
"""

from __future__ import annotations

import json

CSS = """
:root {
  --bg: #faf7f2;
  --bg2: #f1ead9;
  --ink: #2b1d22;
  --ink-soft: #6b5a5f;
  --accent: #6e1f3a;
  --accent2: #b8872f;
  --line: #ddd0c0;
  --card: #ffffff;
  --shadow: 0 8px 20px rgba(43,29,34,0.08);
  --radius: 10px;
  font-family: 'Source Serif 4', 'Georgia', serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: linear-gradient(170deg, var(--bg), var(--bg2));
  color: var(--ink);
  font-family: 'Source Serif 4', 'Georgia', serif;
  padding-bottom: 60px;
}
a { color: inherit; }
.mono { font-family: 'JetBrains Mono', 'Courier New', monospace; }

header.hero {
  padding: 36px 24px 26px;
  text-align: center;
  border-bottom: 3px double var(--accent);
  background: rgba(255,255,255,0.5);
}
.book-icon { font-size: 2.5rem; display: inline-block; margin-bottom: 6px; }
header.hero h1 { margin: 0; font-size: 2.3rem; letter-spacing: 0.5px; color: var(--accent); font-weight: 700; }
header.hero p.sub { margin: 8px 0 0; color: var(--ink-soft); font-size: 1.02rem; font-style: italic; }
header.hero p.meta { margin: 10px 0 0; color: var(--ink-soft); font-size: 0.8rem; letter-spacing: 0.4px; }

.wrap { max-width: 1160px; margin: 0 auto; padding: 0 20px; }

.skip-link {
  position: absolute; left: -999px; top: 0; background: var(--accent); color: #fff;
  padding: 10px 16px; z-index: 2000; border-radius: 0 0 8px 0; font-size: 0.85rem;
}
.skip-link:focus { left: 0; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; }

.featured-banner {
  margin: 26px 0 0; background: var(--card); border: 1px solid var(--accent2);
  border-left: 5px solid var(--accent); border-radius: var(--radius); padding: 16px 20px;
  box-shadow: var(--shadow); display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}
.featured-banner .fb-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.8px; color: var(--accent2); font-weight: 700; }
.featured-banner .fb-abbr { font-size: 1.3rem; font-weight: 700; color: var(--accent); }
.featured-banner .fb-full { color: var(--ink); }
.featured-banner .fb-desc { color: var(--ink-soft); font-size: 0.88rem; flex-basis: 100%; }

.stats-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin: 20px auto 10px; }
.stat-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); text-align: center; }
.stat-card .num { font-size: 1.6rem; font-weight: 700; color: var(--accent); display: block; }
.stat-card .lbl { font-size: 0.76rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.5px; }

.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 22px 0 10px; }
#search { flex: 1; min-width: 220px; padding: 11px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--card); font-family: inherit; font-size: 0.95rem; color: var(--ink); }
.chip { padding: 7px 14px; border: 1px solid var(--accent); border-radius: 20px; background: transparent; color: var(--accent); font-size: 0.8rem; cursor: pointer; font-family: inherit; transition: background 0.15s, color 0.15s; }
.chip.active, .chip:hover { background: var(--accent); color: #fff; }

.az-nav { display: flex; flex-wrap: wrap; gap: 4px; margin: 4px 0 16px; }
.az-btn { width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--line); border-radius: 50%; background: var(--card); color: var(--ink-soft); font-size: 0.74rem; cursor: pointer; font-family: inherit; }
.az-btn.has-entries { color: var(--accent); border-color: var(--accent2); }
.az-btn.has-entries:hover { background: var(--accent); color: #fff; }
.az-btn:disabled { opacity: 0.3; cursor: default; }

#count-line { font-size: 0.82rem; color: var(--ink-soft); margin: 0 0 10px; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.entry-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); cursor: pointer; transition: transform 0.15s, border-color 0.15s; }
.entry-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.entry-card .abbr-code { font-size: 1.15rem; font-weight: 700; color: var(--accent); }
.entry-card .cat-badge { display: inline-block; font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.4px; font-weight: 600; color: var(--accent2); background: #faf2df; border-radius: 10px; padding: 2px 8px; margin-left: 8px; vertical-align: middle; }
.entry-card .full-form { margin: 6px 0 0; font-size: 0.92rem; color: var(--ink); }
.entry-card .desc { display: none; margin-top: 8px; font-size: 0.85rem; color: var(--ink-soft); line-height: 1.5; border-top: 1px dashed var(--line); padding-top: 8px; }
.entry-card.expanded .desc { display: block; }
.entry-card .toggle-hint { margin-top: 6px; font-size: 0.72rem; color: var(--accent2); }

.section-title2 { color: var(--accent); font-size: 1.3rem; border-bottom: 2px solid var(--line); padding-bottom: 8px; margin: 34px 0 16px; }

.quiz-box { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
.quiz-q { font-size: 0.98rem; font-weight: 600; margin-bottom: 12px; }
.quiz-opts { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.quiz-opt { text-align: left; padding: 10px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--bg); cursor: pointer; font-family: inherit; font-size: 0.88rem; color: var(--ink); }
.quiz-opt:hover { border-color: var(--accent); }
.quiz-opt.correct { background: #e8f3e3; border-color: #2f7d32; }
.quiz-opt.wrong { background: #f8e3e3; border-color: #a23b3b; }
.quiz-progress { font-size: 0.78rem; color: var(--ink-soft); margin-bottom: 6px; }
.quiz-next-btn { display: none; background: var(--accent); color: #fff; border: none; border-radius: 8px; padding: 10px 18px; font-size: 0.88rem; cursor: pointer; font-family: inherit; font-weight: 600; }
.quiz-next-btn.show { display: inline-block; }

footer { text-align: center; margin-top: 40px; padding: 18px; color: var(--ink-soft); font-size: 0.78rem; }
@media (max-width: 560px) { header.hero h1 { font-size: 1.7rem; } }
"""


def _entry_card(e: dict, idx: int) -> str:
    return f'''
<div class="entry-card" data-idx="{idx}" data-abbr="{e['abbr'].lower()}" data-full="{e['full'].lower()}"
     data-desc="{e['desc'].lower()}" data-category="{e['category']}" onclick="toggleEntry(this)"
     role="button" tabindex="0" aria-expanded="false">
  <span class="abbr-code mono">{e['abbr']}</span><span class="cat-badge">{e['category']}</span>
  <p class="full-form">{e['full']}</p>
  <p class="desc">{e['desc']}</p>
  <div class="toggle-hint">Tap for meaning ▾</div>
</div>'''


def build_html(payload: dict) -> str:
    entries = payload["entries"]
    categories = payload["categories"]
    category_counts = payload["category_counts"]
    az_index = payload["az_index"]
    featured = payload["featured"]
    stats = payload["stats"]

    cards_html = "\n".join(_entry_card(e, i) for i, e in enumerate(entries))

    category_chips = "".join(
        f'<button class="chip" data-filter="{c}" onclick="setFilter(\'{c}\', this)">{c} ({category_counts.get(c, 0)})</button>'
        for c in categories
    )

    az_html = "".join(
        f'<button class="az-btn {"has-entries" if letter in az_index else ""}" '
        f'{"disabled" if letter not in az_index else ""} onclick="jumpToLetter(\'{letter}\')">{letter}</button>'
        for letter in [chr(c) for c in range(65, 91)]
    )

    entries_json = json.dumps(entries, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Lexicon — General Abbreviations Reference</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<a class="skip-link" href="#main-content">Skip to main content</a>

<header class="hero">
  <div class="book-icon">📖</div>
  <h1>The Lexicon</h1>
  <p class="sub">A general reference of common abbreviations — government, finance, tech, science, law, sport and everyday life.</p>
  <p class="meta">Compiled {payload['date']} &middot; {stats['total']} abbreviations across {stats['total_categories']} categories</p>
</header>

<main id="main-content" class="wrap">

  <div class="featured-banner" role="status" aria-live="polite">
    <span class="fb-label">Abbreviation of the Day</span>
    <span class="fb-abbr mono">{featured['abbr']}</span>
    <span class="fb-full">— {featured['full']}</span>
    <span class="fb-desc">{featured['desc']}</span>
  </div>

  <div class="stats-strip">
    <div class="stat-card"><span class="num">{stats['total']}</span><span class="lbl">Abbreviations</span></div>
    <div class="stat-card"><span class="num">{stats['total_categories']}</span><span class="lbl">Categories</span></div>
  </div>

  <div class="toolbar">
    <label for="search" class="visually-hidden">Search an abbreviation, full form or description</label>
    <input id="search" type="text" placeholder="Search e.g. GDP, Supreme Court, machine learning…" oninput="filterEntries()">
    <button class="chip active" data-filter="all" onclick="setFilter('all', this)">All</button>
    {category_chips}
  </div>

  <div class="az-nav" role="navigation" aria-label="Jump to letter">
    {az_html}
  </div>

  <p id="count-line" role="status" aria-live="polite"></p>

  <div class="grid" id="grid">
    {cards_html}
  </div>

  <h2 class="section-title2">Abbreviation Trivia Quiz</h2>
  <div class="quiz-box" id="quiz-box"></div>

</main>

<footer role="contentinfo">The Lexicon &middot; Curated general-reference abbreviations &middot; Generated {payload['generated_at']}</footer>

<script>
const ENTRIES = {entries_json};
let currentFilter = 'all';

function cardEls() {{ return document.querySelectorAll('.entry-card'); }}

function toggleEntry(card) {{
  const expanded = card.classList.toggle('expanded');
  card.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  card.querySelector('.toggle-hint').textContent = expanded ? 'Tap to collapse ▴' : 'Tap for meaning ▾';
}}
cardEls().forEach(c => c.addEventListener('keydown', e => {{
  if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggleEntry(c); }}
}}));

function setFilter(f, btn) {{
  currentFilter = f;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  filterEntries();
}}

function filterEntries() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  let shown = 0;
  cardEls().forEach(card => {{
    const matchesText = card.dataset.abbr.includes(q) || card.dataset.full.includes(q) || card.dataset.desc.includes(q);
    const matchesCat = currentFilter === 'all' || card.dataset.category === currentFilter;
    const pass = matchesText && matchesCat;
    card.style.display = pass ? '' : 'none';
    if (pass) shown++;
  }});
  document.getElementById('count-line').textContent = `Showing ${{shown}} of {stats['total']}`;
}}

function jumpToLetter(letter) {{
  document.getElementById('search').value = '';
  setFilter('all', document.querySelector('.chip[data-filter="all"]'));
  const target = Array.from(cardEls()).find(c => c.dataset.abbr[0].toUpperCase() === letter);
  if (target) target.scrollIntoView({{behavior: 'smooth', block: 'center'}});
}}

// ── Trivia quiz (generated from the real embedded ENTRIES data) ──
function shuffle(arr) {{
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }}
  return a;
}}
function pickQuiz(n) {{
  const pool = shuffle(ENTRIES).slice(0, n);
  return pool.map(e => {{
    const wrong = shuffle(ENTRIES.filter(x => x.abbr !== e.abbr)).slice(0, 3).map(x => x.full);
    return {{ q: `What does "${{e.abbr}}" stand for?`, options: shuffle([e.full, ...wrong]), answer: e.full }};
  }});
}}
const QUIZ_QUESTIONS = pickQuiz(6);
let quizIdx = 0;
let quizScore = 0;
function renderQuiz() {{
  const box = document.getElementById('quiz-box');
  if (quizIdx >= QUIZ_QUESTIONS.length) {{
    box.innerHTML = `<div class="quiz-q">Quiz complete! You scored ${{quizScore}} / ${{QUIZ_QUESTIONS.length}}.</div>
      <button class="quiz-next-btn show" onclick="quizIdx=0;quizScore=0;renderQuiz()">Try Again</button>`;
    return;
  }}
  const cur = QUIZ_QUESTIONS[quizIdx];
  box.innerHTML = `
    <div class="quiz-progress">Question ${{quizIdx + 1}} of ${{QUIZ_QUESTIONS.length}} &middot; Score: ${{quizScore}}</div>
    <div class="quiz-q">${{cur.q}}</div>
    <div class="quiz-opts">${{cur.options.map((o, i) => `<button class="quiz-opt" onclick="answerQuiz(this, ${{i}})">${{o}}</button>`).join('')}}</div>
    <button class="quiz-next-btn" id="quiz-next" onclick="quizIdx++;renderQuiz()">Next →</button>
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

filterEntries();
</script>

</body>
</html>'''
