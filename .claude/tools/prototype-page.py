#!/usr/bin/env python3
"""prototype-page.py — the page 4-prototype draws, on the prototypes app, 1400.

It shows the prototypes, so I can see them and go from one to the next,
and it picks: a Pick bar under every frame, a Pick page of rows, a
feedback box, and Send. Send types what I picked, and whatever I wrote,
into the session's own pane, exactly as I would type it myself. Nothing
here decides whether that locks a variation in or opens a new generation —
the session reads the line like any other I type in chat.

A prototype moves in generations. A generation is one round of my
instructions, one file, g<N>.json. It may hold variations from several
sources: each variation names the one it grew from, as 1/v3, or none.

A variation may name its looks: a number, a title, and for a look that
competes, a group. Looks in one group compete, and I pick one. A look with
no group is only shown. A variation naming none is picked whole.

The rail leads with Pick, always there, above every variation. Its page is
one block per generation, newest first: a row for the variations, then a
row per group of looks, each named by its variation. One pick per row.
The variation in view sits beside the rows, half and half. Only a click
changes a pick or that variation. Below Pick, the rail lists every variation by id, newest generation first,
a thin line between two generations. Main opens on all of them, live and
small, a row per generation. A variation I click fills main. Opened alone,
it takes a tab.

The top rail holds the family and the session on the left, the subject
and the variation in view in the middle, with the one it grew from, and
the page's two tools together on the right, one width: View all, then
Open alone. Nothing moves when the view does.

It draws; it never serves. The prototypes app, code/prototypes/, serves
it at /, beside every variation, so both share 1400. 1100 frames it with
the subject and the session in its query, and the app passes both here.

None named, or one no subject name could be, draws the library: every
winner under Locked, then every subject no hub frames under Saved,
grouped by its session. Each is one card, a click opening its subject.
Opened with no session, a subject only shows: no pick, no feedback, no
Send, and a way back to the library.

A card shows a still picture, never a live frame: a live frame is a
whole app, and the library holds every prototype. Chrome draws each
picture once, headless, in the background, at low priority, one at a
time. It draws the variation standing for the prototype, as its file
stands, so an edit to that file draws it again.

  prototype-page.py render --subject sign-in-form --session 05
  prototype-page.py heard --subject sign-in-form --session 05
  prototype-page.py render                         the library
  prototype-page.py shoot                          draws the pictures missing

heard prints the page's key, and the files whose writes can move it, so
the app holds the page's watch until one moves it, as 1100 does.

The shell is shared. See .claude/lib/page.py.
It keeps the page rules atop .claude/lib/page.py.
"""

import argparse
import base64
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
from prototypes import APP, PORT, ROUTES, SUBJECT, TAKEN, generations, looks, shelf, subject_file  # noqa: E402


def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def source(v: dict) -> str:
    """The variation one grew from, as the page names it: 1/v3 reads G1 · v3."""
    g, _, n = (v.get("from") or "").partition("/")
    return f"G{page.esc(g)} · {page.esc(n)}" if g and n else ""


# Pick's mark in the rail: a check.
CHECK = ('<svg viewBox="0 0 14 14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 7.5l3 3 6-7"/></svg>')

# View all's mark: four lines, as Open alone carries its arrow.
LIST = ('<svg viewBox="0 0 14 14" aria-hidden="true" fill="currentColor">'
        + "".join(f'<rect x="1" y="{y}" width="12" height="1.6" rx=".8"/>' for y in (1.5, 4.8, 8.1, 11.4))
        + "</svg>")


# A small preview is the page drawn at 1280 by 800, then shrunk to a quarter.
# A real route frames small or full; a variation whose file is gone draws
# as a reconstructed stub instead, in both the same way.
STYLE = """<style>
  #items:has(> .item.v.on) { padding:0; display:flex; flex-direction:column; }
  #items .item.v { position:relative; }
  #items .item.v.on { flex:1; display:flex; flex-direction:column; min-height:0; }
  #items .item.v iframe { flex:1; width:100%; border:0; background:#fff; }
  #items .item.v .stub { flex:1; display:flex; align-items:center; justify-content:center;
    padding:0 18px; color:var(--dim); text-align:center; background:var(--bg); }
  #items .thumbs { display:flex; flex-wrap:wrap; gap:14px; }
  #items .card { width:320px; border:1px solid var(--line); border-radius:6px; overflow:hidden; }
  #items .thumb { position:relative; height:200px; overflow:hidden; cursor:pointer; background:#fff; }
  #items .thumb:hover { outline:2px solid var(--text); outline-offset:-2px; }
  #items .thumb iframe { width:1280px; height:800px; border:0; transform:scale(.25);
    transform-origin:0 0; pointer-events:none; }
  #items .thumb .stub { height:100%; font-size:12px; line-height:1.5; padding:0 14px; }
  #items .thumb .chip { position:absolute; top:6px; left:6px; }
  #items .thumb .chip.src { left:auto; right:6px; }
  /* My pick: a bar below every frame it appears on, thumb or full, green once on. */
  #items .card .pick, #items .item.v .pick { flex:none; display:flex; align-items:center;
    justify-content:center; gap:6px; padding:9px; cursor:pointer; font-size:12px; font-weight:700;
    color:var(--dim); border-top:1px solid var(--line); background:var(--panel); }
  #items .card .pick:hover, #items .item.v .pick:hover { color:var(--text); }
  #items .card.picked, #items .item.v.picked { outline:2px solid var(--green); outline-offset:-2px; }
  #items .card.picked .pick, #items .item.v.picked .pick { color:var(--green); border-top-color:var(--green);
    background:color-mix(in srgb, var(--green) 14%, var(--panel)); }
  /* View all is grey, edged white. Open alone is white. Send is outlined. */
  body:has(> header.top.prototype) > main { padding:0; display:flex; flex-direction:column; }
  header.top.prototype .mid .now { margin-left:10px; color:var(--text); }
  header.top.prototype .mid .now .src { color:var(--dim); font-weight:400; }
  header.top.prototype button { display:inline-flex; align-items:center; justify-content:center; gap:8px; }
  header.top.prototype button.all { background:var(--grey); color:#fff; border:2px solid #fff; }
  header.top.prototype button.all:hover:not(:disabled) { background:color-mix(in srgb, #fff 18%, var(--grey)); }
  header.top.prototype button.all svg { width:14px; height:14px; flex:none; }
  header.top.prototype button:disabled:not(#send) { background:var(--grey); color:var(--text);
    border-color:var(--grey); opacity:.5; cursor:default; }
  header.top.prototype button#send { margin-left:8px; }
  header.top.prototype button#send[hidden] { display:none; }
  header.top.prototype button#back { margin-right:8px; }
  nav.nums .lbl { width:26px; margin:0 0 4px; text-align:center; color:var(--dim);
    font-size:10px; font-weight:700; }
  nav.nums .tab.pk { cursor:pointer; padding:5px 0 3px; background:var(--green); color:var(--bg); }
  nav.nums .tab.pk svg { width:14px; height:14px; }
  /* The Pick page: the rows on the left, the variation in view beside them,
     half and half at any width, so a look's number is read where it is drawn. A .ch is one choice, a row
     of options, one of them on. */
  #items:has(> .item.pk.on) { padding:0; display:flex; flex-direction:column; flex:1 1 0; min-height:0; overflow:hidden; }
  #items .item.pk.on { flex:1; display:flex; min-height:0; }
  #items .item.pk .rows { flex:none; width:50%; box-sizing:border-box; overflow-y:auto; padding:14px 24px 20px; }
  #items .item.pk .view { flex:none; width:50%; box-sizing:border-box; display:flex; flex-direction:column;
    border-left:1px solid var(--line); }
  #items .item.pk .view .cap { flex:none; padding:7px 14px; font-size:12px; font-weight:700;
    color:var(--dim); background:var(--panel); border-bottom:1px solid var(--line); }
  #items .item.pk .view iframe { flex:1; width:100%; border:0; background:#fff; }
  #items .item.pk .view .stub { flex:1; display:flex; align-items:center; justify-content:center;
    padding:0 24px; color:var(--dim); text-align:center; }
  #items .item.pk .view [hidden] { display:none; }
  #items .item.pk .gen { margin:0 0 26px; }
  #items .item.pk .ch { margin:0 0 16px; }
  #items .item.pk .ch.off { opacity:.5; }
  #items .item.pk .rl { margin:0 0 6px; font-size:12px; font-weight:700; color:var(--dim);
    letter-spacing:.04em; text-transform:uppercase; }
  #items .item.pk .rl .hint { margin-left:8px; font-weight:400; text-transform:none; letter-spacing:0; }
  #items .item.pk .opts { display:flex; flex-wrap:wrap; gap:10px; }
  #items .item.pk .opt { flex:1 1 170px; min-height:64px; padding:10px 14px;
    display:flex; flex-direction:column; align-items:flex-start; justify-content:center; gap:3px;
    font:inherit; text-align:left; color:var(--text); background:var(--panel); cursor:pointer;
    border:1px solid var(--line); border-radius:6px; }
  #items .item.pk .opt b { font-size:16px; }
  #items .item.pk .opt .d { color:var(--dim); font-size:12px; line-height:1.4; overflow:hidden;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
  #items .item.pk .opt.on { outline:2px solid var(--green); outline-offset:-2px;
    background:color-mix(in srgb, var(--green) 14%, var(--panel)); }
  #items .item.pk .opt.on b { color:var(--green); }
  #items .item.pk .shown { margin:0; color:var(--dim); font-size:13px; line-height:1.5; }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    header.top.prototype button { min-height:44px; }
    header.top.prototype ~ nav.nums .tab { width:44px; padding:0; line-height:44px; }
    #items .card .pick, #items .item.v .pick { min-height:44px; }
  }
</style>
"""

SCRIPT = """<script>
const now = document.getElementById('now');
/* GROUPS names each variation's competing groups, as 1/v1: ['A', 'B'].
   pick is the variation I chose, lk the look I chose in each group, as
   '1/v1|A': '1'. A group left out is open. */
let cur = 'all', pick = '', lk = {};
/* Whether the session works now. Its word rides at the end of the watch's
   key, after its last '|'. A move of that word alone greys or frees Send in
   place, so the box keeps what I typed. A Send already sent stays as it
   is. Any other move draws the page again. */
const WORKING = 'Working. Send opens once its turn ends.';
let busy = BUSY;
/* WebKit applies the page's zoom again inside a framed variation. Neutralize
   it on each frame, then zoom a full variation itself. Thumbnails keep their
   1280 by 800 layout and scale with the surrounding page. */
function zoomFrames() {
  const z = parseFloat(document.documentElement.style.zoom) || 1;
  document.querySelectorAll('#items iframe').forEach(f => {
    f.style.zoom = z === 1 ? '' : String(1 / z);
    if (f.closest('.thumb')) f.style.transform = `scale(${z / 4})`;
    else {
      try {
        const root = f.contentDocument && f.contentDocument.documentElement;
        if (root) root.style.zoom = z === 1 ? '' : String(z);
      } catch (e) {}
    }
  });
}
document.querySelectorAll('#items iframe').forEach(f => f.addEventListener('load', zoomFrames));
addEventListener('ws-zoom', zoomFrames);
zoomFrames();
window.told = now => {
  const w = document.getElementById('watch'), files = k => k.slice(0, k.lastIndexOf('|'));
  if (files(now) !== files(w.dataset.key)) return location.reload();
  w.dataset.key = now;
  busy = now.endsWith('|working');
  if (!document.getElementById('send').classList.contains('sent')) sync();
};

function show(k) {
  cur = k;
  tab(k);
  const f = document.getElementById('f-' + k);
  if (f && !f.src) f.src = f.dataset.src;
  const item = document.getElementById('t-' + k), from = item.dataset.from;
  const bare = k === 'all' || k === 'pick';
  now.innerHTML = bare ? '' : 'G' + k.replace('/', ' · ')
    + `<span class="src">${from ? '  ←  ' + from : '  ·  fresh'}</span>`;
  document.getElementById('all').disabled = k === 'all';
  document.getElementById('alone').disabled = bare;
  if (k === 'pick') focusVar(pick || FIRST);
}

/* The frame beside the rows shows one variation, drawn live: the one I last
   clicked a row of. Nothing changes it on hover. A variation whose file is
   gone shows its direction instead. */
function focusVar(k) {
  if (!(k in ROUTES)) return;
  const f = document.getElementById('pf'), st = document.getElementById('ps');
  document.getElementById('pc').textContent = 'G' + k.replace('/', ' · ');
  f.hidden = !ROUTES[k];
  st.hidden = !!ROUTES[k];
  if (ROUTES[k] && f.dataset.k !== k) { f.dataset.k = k; f.src = ROUTES[k]; }
  if (!ROUTES[k]) st.textContent = 'Reconstructed from the record — the file is gone. ' + DIRECTIONS[k];
}


function alone() {
  const f = document.getElementById('f-' + cur);
  if (f) window.open(f.dataset.src, '_blank');
}

/* Every place a pick shows draws from pick and lk, so a pick made on a
   bar, or in a row, shows on both. */
function paint() {
  document.querySelectorAll('.card, .item.v').forEach(el => el.classList.toggle('picked', el.dataset.k === pick));
  document.querySelectorAll('.opt.vo').forEach(el => el.classList.toggle('on', el.dataset.k === pick));
  document.querySelectorAll('.opt.lo').forEach(el =>
    el.classList.toggle('on', lk[el.dataset.k + '|' + el.dataset.g] === el.dataset.n));
  document.querySelectorAll('.ch.gr').forEach(el => el.classList.toggle('off', !!pick && el.dataset.k !== pick));
  sync();
}

/* My pick: one variation at a time, on a bar or in a row. Never show()'s
   own navigation — the bar stops that click reaching it. */
function selectCard(k, ev) {
  ev.stopPropagation();
  pickVar(k);
}

function pickVar(k) {
  pick = pick === k ? '' : k;
  focusVar(k);
  paint();
}

/* A look picked chooses its variation too: the look is one of its own. */
function pickLook(k, g, n) {
  const id = k + '|' + g;
  lk[id] = lk[id] === n ? '' : n;
  if (lk[id]) pick = k;
  focusVar(k);
  paint();
}

/* The groups of the variation I chose that hold no pick yet. */
function unpicked() {
  return (GROUPS[pick] || []).filter(g => !lk[pick + '|' + g]);
}

function fit() {
  const t = document.getElementById('fb'), b = document.getElementById('pbar');
  const open = document.activeElement === t || !!t.value.trim();
  b.classList.toggle('open', open);
  t.style.height = 'auto';
  t.style.height = (open ? Math.max(t.scrollHeight + 4, 84) : 40) + 'px';
}

/* The button names what Send types: a pick with every group picked, a pick
   with groups still open, or my words alone. While the session works, it
   is greyed. */
function sync() {
  const t = document.getElementById('fb'), send = document.getElementById('send');
  const note = t.value.trim(), left = unpicked().length;
  const word = left ? left + ' open' : 'lock in';
  send.disabled = busy || (!pick && !note);
  if (busy) send.title = WORKING;
  else if (send.title === WORKING) send.title = '';
  send.textContent = pick && note ? (left ? 'Send · ' + word + ', with feedback' : 'Send · with feedback')
    : pick ? 'Send · ' + word : note ? 'Send · feedback only' : 'Send';
}

/* The looks I picked, one pair a group of the variation I chose: 'A:1,B:'.
   A group with no number is open. */
function chosen() {
  return (GROUPS[pick] || []).map(g => g + ':' + (lk[pick + '|' + g] || '')).join(',');
}

/* Nothing here decides whether Send locks a variation in or opens a new
   generation. It only types the line; the session reads it like any other.
   The post keeps the address's query, which names the session. */
async function send() {
  const b = document.getElementById('send');
  b.classList.add('busy');
  b.disabled = true;
  const why = await typePost({act: 'send', pick, looks: chosen(), feedback: document.getElementById('fb').value},
    location.pathname + location.search);
  b.classList.remove('busy');
  if (why === '') { b.classList.add('sent'); b.textContent = 'Sent'; return; }
  b.classList.add('gone');
  b.title = why || UNANSWERED;
  b.textContent = 'Try again';
  b.disabled = false;
  refusal(b.title);
}

document.getElementById('fb').addEventListener('input', () => { fit(); sync(); });
document.getElementById('fb').addEventListener('focus', fit);
document.getElementById('fb').addEventListener('blur', fit);
document.getElementById('send').onclick = send;
sync();
fit();

const want = decodeURIComponent(location.hash.slice(1));
show(document.getElementById('t-' + want) ? want : 'all');
</script>
"""


PICK = re.compile(r"(\d+)/(v\d+)")
# One group's pick: its name, then the look's number. No number, the group is open.
GROUP = re.compile(r"([A-Za-z0-9]+):(\d+(?:\.\d+)?)?")
# Typing is safe only while the session sits idle at its prompt: idle, or
# shell, idle with a background shell still running. Busy, or at a dialog,
# is the app's own: page.typable says why, in its own sentence.
OK = ("idle", "shell")


def take(nn: str, form: dict) -> str:
    """Send, pressed: my pick and my feedback, typed into the session's
    own pane, as I would type them myself. The one refusal sentence, or ""
    once it typed.

    A variation with groups reads `g1/v1 · A: look 1 · B: open`: each group
    with its look, or open. A note follows, after a dash."""
    get = lambda k: (form.get(k) or [""])[0]
    pick, note = get("pick").strip(), get("feedback").strip()
    m = PICK.fullmatch(pick) if pick else None
    if not m and not note:
        return ""
    line = f"g{m.group(1)}/{m.group(2)}" if m else ""
    if m and get("looks").strip():
        for part in get("looks").strip().split(","):
            g = GROUP.fullmatch(part)
            if not g:
                return "That pick names a group no variation holds. Nothing was typed."
            line += f" · {g.group(1)}: " + (f"look {g.group(2)}" if g.group(2) else "open")
    line = f"{line} — {note}" if line and note else (note or line)
    why, _, pane = page.typable(nn, OK)
    if why:
        return why
    if not panes.say(pane, line):
        return page.gone(nn)
    return ""


def frame(v: dict, k: str, full: bool) -> str:
    """One variation's picture: its real route, small or full, or a
    reconstructed stub when its file is already gone."""
    if v.get("real", True) and v.get("route"):
        src = page.esc(v["route"])
        return f'<iframe id="f-{k}" data-src="{src}"></iframe>' if full \
            else f'<iframe src="{src}" loading="lazy" tabindex="-1"></iframe>'
    return f'<div class="stub">Reconstructed from the record — the file is gone.<br>{page.esc(v.get("direction", ""))}</div>'


def block(g: dict) -> str:
    """One generation on the Pick page: a row for its variations, then a row
    per group of looks, each named by its variation. A look with no group
    only shows, on a line of its own. One pick per row."""
    n = g["generation"]
    opts, rest = [], []
    for v in g["variations"]:
        vid, k = page.esc(v["id"]), f"{n}/{page.esc(v['id'])}"
        came = f"← {source(v)} · " if source(v) else ""
        opts.append(f'<button class="opt vo" data-k="{k}" onclick="pickVar(this.dataset.k)">'
                    f'<b>{vid}</b><span class="d">{came}{page.esc(v.get("direction", ""))}</span></button>')
        groups, shown = looks(v)
        for name, found in groups.items():
            gid = page.esc(name)
            chosen = "".join(
                f'<button class="opt lo" data-k="{k}" data-g="{gid}" data-n="{page.esc(l["n"])}" '
                f'onclick="pickLook(this.dataset.k, this.dataset.g, this.dataset.n)">'
                f'<b>look {page.esc(l["n"])}</b><span class="d">{page.esc(l.get("title", ""))}</span></button>'
                for l in found)
            rest.append(f'<div class="ch gr" data-k="{k}"><div class="rl">{vid} · group {gid}'
                        f'<span class="hint">pick one</span></div><div class="opts">{chosen}</div></div>')
        if shown:
            line = "<br>".join(f'look {page.esc(l["n"])} · {page.esc(l.get("title", ""))}' for l in shown)
            rest.append(f'<div class="ch"><div class="rl">{vid} · shown'
                        f'<span class="hint">never picked</span></div><p class="shown">{line}</p></div>')
    return (f'<div class="gen"><h3 class="sub">G{n}</h3>'
            f'<div class="ch"><div class="rl">Variations<span class="hint">pick one</span></div>'
            f'<div class="opts">{"".join(opts)}</div></div>{"".join(rest)}</div>')


def world(nn: str, subject: str) -> dict:
    """Everything the page draws for session NN, in the fixture file's own
    shape. `live` is the session's word, page.word's.
    `key` drives the watch: the generations, then the word after its last
    "|"; a fixture carries none."""
    found = generations(os.path.join(APP, subject))
    rec = registry.claude_records().get((registry.entries().get(nn) or {}).get("session_id"))
    live = page.word(rec)
    return {"nn": nn, "tag": plans.tag(nn) if nn != "00" else "band 00", "subject": subject,
            "generations": [load(p) for _, p in found], "live": live,
            "key": subject + ":" + ":".join(f"{n}@{os.path.getmtime(p)}" for n, p in found) + "|" + live}


# The library's pictures, and Chrome's own profile for drawing them.
SHOTS = os.path.join(registry.ROOT, ".claude", "state", "prototype-page")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# A picture is the route drawn at 1280 by 800, then shrunk to this width:
# a card's 320 on a screen of twice the density.
WIDTH = 640
# Marks a variation Chrome could not draw, so it is never tried again.
NONE = ".none"


def picture(e: dict) -> str:
    """Where the picture of a library entry's variation goes, named for its
    file as it stands. Nothing when the variation has no route or file."""
    g, _, v = e["shown"].partition("/")
    try:
        at = int(os.path.getmtime(os.path.join(ROUTES, e["subject"], g, f"{v}.tsx")))
    except OSError:
        return ""
    return os.path.join(SHOTS, f"{e['subject']}--{g}-{v}--{at}.jpg") if e["route"] else ""


def library() -> dict:
    """Everything the library draws, in the fixture file's own shape. Each
    entry carries its picture's path, once drawn, and whether one waits
    to be drawn. `key` drives the watch: the shelf itself."""
    locked, saved = shelf()
    for e in locked + saved:
        path = picture(e)
        e["picture"] = path if path and os.path.exists(path) else ""
        e["waits"] = bool(path) and not e["picture"] and not os.path.exists(path + NONE)
    return {"locked": locked, "saved": saved,
            "key": hashlib.sha1(json.dumps([locked, saved]).encode()).hexdigest()[:12]}


def shoot() -> None:
    """Draw every picture missing, one at a time, until none is, then drop
    each picture no entry names. One job runs at once; a second leaves.
    Nothing is drawn while the app is down, so no picture is of an error."""
    os.makedirs(SHOTS, exist_ok=True)
    with open(os.path.join(SHOTS, "shooting"), "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
        while ports.answering(PORT):
            d = library()
            todo = [e for e in d["locked"] + d["saved"] if e["waits"]]
            if not todo:
                break
            for e in todo:
                draw_picture(e["route"], picture(e))
        locked, saved = shelf()
        named = {os.path.basename(p) for e in locked + saved if (p := picture(e))}
        for name in registry.listing(SHOTS):
            if name.endswith((".jpg", NONE)) and name.removesuffix(NONE) not in named:
                os.remove(os.path.join(SHOTS, name))


def draw_picture(route: str, path: str) -> None:
    """One route drawn by Chrome, headless, at background priority, then
    shrunk to a JPEG. Chrome gets two tries, since its first start can
    outlast the wait. A route it cannot draw leaves its mark instead."""
    raw = path + ".png"
    for _ in range(2):
        try:
            subprocess.run(["taskpolicy", "-b", CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--no-first-run", "--no-default-browser-check",
                            f"--user-data-dir={os.path.join(SHOTS, 'chrome')}", "--window-size=1280,800",
                            "--virtual-time-budget=6000", f"--screenshot={raw}", f"http://localhost:{PORT}{route}"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False)
        except subprocess.TimeoutExpired:
            pass
        if os.path.exists(raw):
            break
    shrunk = os.path.exists(raw) and subprocess.run(
        ["sips", "-Z", str(WIDTH), "-s", "format", "jpeg", "-s", "formatOptions", "60", raw, "--out", path + ".part"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0
    if shrunk:
        os.replace(path + ".part", path)
    else:
        open(path + NONE, "w").close()
    for left in (raw, path + ".part"):
        if os.path.exists(left):
            os.remove(left)


def heard(nn: str, subject: str) -> dict:
    """The page's key, and every file and folder whose write can move it.
    A subject's page hears its folder, and what registry.watched names for
    the session. The library hears the app's folder, every subject's, its
    pictures, every session's hold, and where sessions start and stop. The
    prototypes app holds its /heard on them."""
    if not subject:
        held = [n for n in registry.listing(registry.WORK) if re.fullmatch(r"\d{2}", n)]
        homes = [os.path.join(APP, s) for s in registry.listing(APP) if generations(os.path.join(APP, s))]
        return {"key": library()["key"],
                "hears": [APP, SHOTS, registry.WORK] + homes + [subject_file(n) for n in held]
                + [os.path.expanduser(f"{base}/sessions") for base in registry.LIVE]}
    d = world(nn, subject)
    return {"key": d["key"], "hears": [os.path.join(APP, d["subject"])] + registry.watched([nn])}


SHELF_STYLE = """<style>
  #items .shelf h2.sec { font-size:26px; line-height:1.25; letter-spacing:0; text-transform:none;
    color:var(--text); margin:36px 0 16px; padding-top:22px; }
  #items .shelf h2.sec:first-child { margin-top:0; padding-top:0; border-top:0; }
  #items .shelf .team { margin:0 0 22px; }
  #items .shelf .tl { margin:0 0 8px; font:700 10px/1.4 ui-monospace,Menlo,monospace;
    letter-spacing:.08em; text-transform:uppercase; color:var(--dim); }
  #items .shelf a.card { display:block; color:var(--text); text-decoration:none; }
  #items .shelf a.card:hover { outline:2px solid var(--text); outline-offset:-2px; }
  #items .shelf .thumb { cursor:pointer; }
  #items .shelf .thumb img { display:block; width:100%; height:100%; object-fit:cover; object-position:top left; }
  #items .shelf .thumb .stub { display:flex; align-items:center; justify-content:center;
    color:var(--dim); text-align:center; background:var(--bg); }
  #items .shelf .cap { padding:8px 10px; border-top:1px solid var(--line); background:var(--panel); }
  #items .shelf .cap b, #items .shelf .cap span { display:block; overflow:hidden; text-overflow:ellipsis;
    white-space:nowrap; }
  #items .shelf .cap b { font-size:13px; }
  #items .shelf .cap span { margin-top:2px; font-size:11px; color:var(--dim); }
  #items .shelf p.none { color:var(--dim); font-size:13px; }
</style>
"""


def who(e: dict) -> str:
    """A subject's session, as a card names it: 10 · 10-sign-in-team."""
    return f"{e['number']} · {e['title']}" if e["number"] else "Session unknown"


def card(e: dict, line: str) -> str:
    """One prototype: its picture, its variation's id over it, its name, and
    one line under it. The picture rides inside the page, so the page
    asks for nothing more."""
    if e.get("picture"):
        with open(e["picture"], "rb") as f:
            shown = f'<img alt="" src="data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}">'
    else:
        shown = f'<div class="stub">{"Drawing its picture…" if e.get("waits") else "No picture"}</div>'
    return (f'<a class="card" href="/?{urllib.parse.urlencode({"subject": e["subject"]})}">'
            f'<div class="thumb">{shown}<span class="chip g" style="--c:var(--grey)">{page.esc(e["shown"])}</span></div>'
            f'<div class="cap"><b>{page.esc(e["subject"])}</b><span>{page.esc(line)}</span></div></a>')


def draw_shelf(d: dict) -> str:
    """The library, from library()'s dict or a fixture's. Every winner
    under Locked, each card naming its session. Every subject saved under
    Saved, grouped by its session, a session unknown last."""
    watch = page.watch(d["key"]) if "key" in d else page.TABS
    many = lambda n, word: f"{n} {word}{'' if n == 1 else 's'}"
    locked = "".join(card(e, who(e)) for e in d["locked"])
    groups = {}
    for e in d["saved"]:
        groups.setdefault((e["number"], e["title"]), []).append(e)
    saved = "".join(
        f'<div class="team"><div class="tl">{page.esc(who(es[0]))}</div><div class="thumbs">'
        + "".join(card(e, f"g{e['generation']} · {many(e['variations'], 'variation')}") for e in es)
        + '</div></div>'
        for _, es in sorted(groups.items(), key=lambda kv: not kv[0][0]))
    body = (STYLE + SHELF_STYLE + '<div id="items"><section class="item on shelf">'
            f'<h2 class="sec">Locked · {len(d["locked"])}</h2>'
            + (f'<div class="team"><div class="thumbs">{locked}</div></div>' if locked
               else '<p class="none">No prototype is locked in.</p>')
            + f'<h2 class="sec">Saved · {len(d["saved"])}</h2>'
            + (saved or '<p class="none">No prototype is saved.</p>')
            + '</section></div>\n' + watch)
    top = page.head("prototype", "band 00", "Prototypes")
    return page.render("00-prototypes", [("", body)], top, refresh=0)


def draw(d: dict) -> str:
    """The page, from world()'s dict or a fixture's. Opened with no session,
    it only shows: Send and the feedback box stay hidden, nothing picks,
    and a button leads back to the library."""
    nn, subject, gens = d.get("nn", "00"), page.esc(d["subject"]), d["generations"]
    shows = nn == "00"
    watch = page.watch(d["key"]) if "key" in d else page.TABS
    # With nothing to show, every button stands disabled, in the same places.
    off = "" if gens else " disabled"
    back = '<button class="all" id="back" onclick="location.href=\'/\'">All prototypes</button>' if shows else ""
    top = page.head("prototype", d.get("tag", ""), f'{subject}<span class="now" id="now"></span>',
                    f'{back}<span class="group"><button class="all" id="all" onclick="show(\'all\')"{off}>'
                    f'View all{LIST}</button>'
                    f'<button id="alone" onclick="alone()"{off}>Open alone ↗</button></span>'
                    f'<button id="send"{" hidden" if shows else off}>Send</button>')
    if not gens:
        body = STYLE + page.blank("No generation yet") + "\n" + watch
        return page.render(f"{nn}-prototype", [("", body)], top, refresh=0)

    rail = [] if shows else ['<div class="tab pk" data-k="pick" title="Pick" onclick="show(\'pick\')">' + CHECK + '</div>']
    rows, items, groups, routes, said = [], [], {}, {}, {}
    for g in reversed(gens):
        n = g["generation"]
        rail.append('<div class="gap"></div>')
        rail.append(f'<div class="lbl">G{n}</div>')
        thumbs = []
        for v in g["variations"]:
            k = f"{n}/{page.esc(v['id'])}"
            pick = "" if shows else f'<div class="pick" onclick="selectCard(\'{k}\', event)">Pick</div>'
            rail.append(f'<div class="tab g" data-k="{k}" style="--c:var(--grey)" '
                        f'onclick="show(\'{k}\')">{page.esc(v["id"])}</div>')
            came = source(v)
            if looks(v)[0]:
                groups[f"{n}/{v['id']}"] = list(looks(v)[0])
            routes[f"{n}/{v['id']}"] = v["route"] if v.get("real", True) and v.get("route") else ""
            said[f"{n}/{v['id']}"] = v.get("direction", "")
            tag = f'<span class="chip g src" style="--c:var(--grey)">← {came}</span>' if came else ""
            thumbs.append(f'<div class="card" data-k="{k}">'
                          f'<div class="thumb" onclick="show(\'{k}\')">{frame(v, k, False)}'
                          f'<span class="chip g" style="--c:var(--grey)">{page.esc(v["id"])}</span>{tag}</div>'
                          f'{pick}</div>')
            items.append(f'<section class="item v" id="t-{k}" data-k="{k}" data-from="{came}">'
                         f'{frame(v, k, True)}{pick}</section>')
        rows.append(f'<div class="stage"><h3 class="sub">G{n}</h3>'
                    f'<div class="thumbs">{"".join(thumbs)}</div></div>')
    items.insert(0, f'<section class="item" id="t-all">{"".join(rows)}</section>')
    if not shows:
        items.insert(1, '<section class="item pk" id="t-pick"><div class="rows">'
                     + "".join(block(g) for g in reversed(gens)) + '</div>'
                     '<div class="view"><div class="cap" id="pc"></div><iframe id="pf" hidden></iframe>'
                     '<div class="stub" id="ps" hidden></div></div></section>')
    bar = (f'<div class="bar{" hide" if shows else ""}" id="pbar"><div class="lab">Feedback</div>'
           '<textarea id="fb" placeholder="Optional. Empty sends the pick as-is."></textarea></div>')
    first = f"{gens[-1]['generation']}/{gens[-1]['variations'][0]['id']}"
    data = json.dumps({"GROUPS": groups, "ROUTES": routes, "DIRECTIONS": said, "FIRST": first,
                       "BUSY": d.get("live") == "working"})
    # A name inside the data can never close the script around it.
    known = ("<script>const {GROUPS, ROUTES, DIRECTIONS, FIRST, BUSY} = "
             + data.replace("</", "<\\/") + ";</script>")
    body = (STYLE + f'<div id="items">{"".join(items)}</div>\n' + bar + watch + page.TYPING + known + SCRIPT)
    rail_html = f'<nav class="nums" id="index">{"".join(rail)}</nav>\n'
    return page.render(f"{nn}-prototype", [("", body)], top + rail_html, refresh=0)


def render(nn: str, subject: str) -> str:
    """A subject's page, or the library. A library with a picture missing
    starts the job drawing it, detached, so the page never waits on it."""
    if subject:
        return draw(world(nn, subject))
    d = library()
    if os.path.exists(CHROME) and any(e["waits"] for e in d["locked"] + d["saved"]):
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "shoot"], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return draw_shelf(d)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["render", "heard", "fixture", "take", "shoot"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--subject", default="")
    ap.add_argument("--session", default="00")
    args = ap.parse_args()
    if args.verb == "shoot":
        shoot()
        return
    if args.verb == "fixture":
        if not args.file:
            sys.exit("fixture takes a file.")
        with open(args.file) as f:
            d = json.load(f)
        out = os.path.splitext(args.file)[0] + ".html"
        with open(out, "w") as f:
            f.write(draw_shelf(d) if "locked" in d else draw(d))
        print(out)
        return
    if args.verb == "take":
        session = args.session if re.fullmatch(r"\d{2}", args.session) else "00"
        form = urllib.parse.parse_qs(sys.stdin.read())
        why = take(session, form)
        if why:
            sys.exit(why)
        return
    # The query is anyone's to write. A name no subject could take never
    # reaches a path.
    subject = args.subject if SUBJECT.fullmatch(args.subject) and args.subject not in TAKEN else ""
    session = args.session if re.fullmatch(r"\d{2}", args.session) else "00"
    if args.verb == "heard":
        json.dump(heard(session, subject), sys.stdout)
        return
    sys.stdout.write(render(session, subject))


if __name__ == "__main__":
    main()
