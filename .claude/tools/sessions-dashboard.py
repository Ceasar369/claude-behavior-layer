#!/usr/bin/env python3
"""sessions-dashboard.py — 1100, the one page server.

One page, open all day. Band 00 belongs to no session, and 1100 is the
behaviour layer's own front door: every page is drawn here. A session may
serve its own copy on 11NN to try new code: session 08 tries 1100 on 1108.

Home is the workstation: what waits on me, and the team it belongs to.
workstation.py draws it. The pages it opens for a session are 1100's own:

  /p/clarify/NN     a wave, clarify-page.py's render and take, and /p/clarify/NN/key
  /p/assistant/NN   a plan, assistant-page.py's
  /p/launch/NN      a launch, launch-page.py's, and /p/launch/NN/key
  /p/handover/NN    a handover, handover-page.py's
  /p/jury/NN        a jury's plan, then its results, jury-page.py's, and /p/jury/NN/key
  /p/walk/NN        a walk's checklist, walk-list-page.py's, and /p/walk/NN/key
  /p/shots/NN       a walk's screenshots, walk-shots-page.py's, and each one
  /p/transcript/NN  a session's whole transcript, transcript-page.py's,
                    and the parts it asks for as I read it; the advisor's
                    wears its panel, advisor-page.py's

A prototype is framed from the prototypes app on 1400. Each page's posts
come back to its own address, and its own take answers them. DRAWN names
how each /p/ page draws, keys and takes. An address named nowhere here
answers not found, and a post there takes nothing.

The rail opens five more pages, each at its own address. This file
draws two of them.

  /p/launch/00  my own launch page, behind Launch. launch-page.py draws it.
  /agenda  my agenda, as one chart, and its JSON at /agenda/data, for
           drawing it again in place. agenda-page.py draws it, takes
           Start, and names its folder for 1100 to hear.
  /system  usage, the outsource engines, defaults, thresholds, the rail's
           size, band 00, other ports and the memory guard: system_page()
           draws it.
  /files   every session's folder as a tree, and the file I pick:
           files_page() draws it.
  /skills  every skill, by family. skills-page.py draws it.

/apple-touch-icon.png is 1100's icon on my iPhone's home screen, and
/manifest.webmanifest names it there as an app of its own, by the
project's name. /sw.js is its service worker, which shows the buzz:
lib/push.py's, posted to /push once I allow it, and sent once a session
is done, from the colour watch below.

/project names the project this 1100 serves, by name and folder. One
project runs at a time: while another project's 1100 answers, band, stop
and restart refuse, naming it. lib/project.py holds both halves.

1100 also types drive.RESUME into a driving assistant capped on its own
account, once the cap resets: lib/finish.py's watch, on a thread of its
own for as long as 1100 runs. On another, a session whose number turns
from green to red buzzes my phone, and an assistant is handed its
mission's sessions waiting on me, as assistant-page.py's auto-send rules:
lib/page.py's colour watch, reddened. On another, it asks every account
for its two windows: lib/finish.py's asking. On another, it reads iTerm's
pane list while pages ask for it, so no draw ever waits on iTerm:
lib/panes.py's freshen. On another, System's ports and database while
System shows: freshen() here.

Nothing is stored here. Every request reads what it shows.

The shell, the colours and the server are shared. See .claude/lib/.
It keeps the page rules atop .claude/lib/page.py.

  sessions-dashboard.py serve  [--port 1100]
  sessions-dashboard.py band
  sessions-dashboard.py status
  sessions-dashboard.py stop      band 00 and 1100, never a session's
  sessions-dashboard.py check     the code on disk draws, and its scripts parse, or it raises
  sessions-dashboard.py restart   1100 alone, on the code on disk
"""

import argparse
import base64
import codecs
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import context  # noqa: E402
import door  # noqa: E402
import engines  # noqa: E402
import finish  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import push  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import wake  # noqa: E402

SKILL = "sessions-dashboard"
PORT = serve.PORT
HERE = os.path.dirname(os.path.abspath(__file__))

# Home, and every view, through it.
workstation = page.tool("workstation")
views = workstation.views
jury = views.jury
skills = page.tool("skills-page")
agenda = page.tool("agenda-page")
transcript = page.tool("transcript-page")

# Band 00 is the project's own, as .claude/project.json names it: one
# group per layer, port by port, and the one command that starts every
# one. The command goes through a login shell, so it finds what my shell
# finds, which a hook's own PATH does not carry. A project naming none
# runs 1100 alone.
DEV = ["/bin/zsh", "-lc", project.COMMAND] if project.COMMAND else None
BAND = project.BAND
PORTS = [p for _, group in BAND for p, _ in group]

# Shown first in band 00, never started with it. A database that listens
# can still refuse every query, so its dot asks the database itself. A
# project naming none shows no dot.
DATABASE = ("Database", [(ports.POSTGRES, project.DATABASE["name"])]) if project.DATABASE else None


# ---- the system -----------------------------------------------------------------

def band_state() -> dict:
    # Serial checks at a quarter second each would make the page crawl.
    # They are independent, so they run at once.
    if not PORTS:
        return {}
    with ThreadPoolExecutor(max_workers=len(PORTS)) as pool:
        return dict(zip(PORTS, pool.map(ports.answering, PORTS)))


def processes(pids) -> dict:
    """Each running pid's process name, in one ps call."""
    wanted = sorted({str(p) for p in pids if p > 0})
    if not wanted:
        return {}
    r = subprocess.run(["/bin/ps", "-o", "pid=,ucomm=", "-p", ",".join(wanted)],
                       capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        pid, _, name = line.strip().partition(" ")
        if pid.isdigit():
            out[int(pid)] = name.strip()
    return out


def outside() -> tuple:
    """What System shows of the world outside: band 00's state, the
    database first, and every port listening outside band 00 and 1100, as
    (port, process)."""
    found = {p: pid for p, pid in ports.listeners().items()
             if p not in PORTS and p not in (PORT, ports.POSTGRES)}
    names = processes(found.values())
    return ({**band_state(), **({ports.POSTGRES: ports.database()} if DATABASE else {})},
            [(p, names.get(found[p], "?")) for p in sorted(found)])


# outside() as last read, and when System last asked for it. 1100 reads it
# on a thread of its own every few seconds while System was asked in the
# last minute, so no draw waits on lsof or the database: lib/panes.py's
# freshen, for ports. A tool run alone reads it itself.
SEEN = {"got": None, "asked": 0.0, "fresh": False}


def seen() -> tuple:
    """outside(), as the refresher last read it, or read now while none runs."""
    SEEN["asked"] = time.time()
    if not SEEN["fresh"] or SEEN["got"] is None:
        SEEN["got"] = outside()
    return SEEN["got"]


def freshen(every: float = panes.FRESH) -> None:
    """The refresher, on a thread of its own for as long as 1100 runs."""
    SEEN["fresh"] = True
    while True:
        if time.time() - SEEN["asked"] < 60:
            try:
                SEEN["got"] = outside()
            except Exception:
                pass
        time.sleep(every)


def other(titles: dict, listening: list) -> list:
    """Each other port listening, as (port, process, session).

    The session is the one the port scheme names: its name while it is
    registered, "no session NN" once it is not. A port outside the scheme
    names none.
    """
    out = []
    for p, proc in listening:
        nn = f"{p % 100:02d}"
        out.append((p, proc, (titles.get(nn) or f"no session {nn}") if ports.in_scheme(p) else ""))
    return out


SYSTEM_STYLE = """<style>
  body > main { padding:12px; }
  .lbl { font:700 10px/1.4 ui-monospace,Menlo,monospace; letter-spacing:.08em; text-transform:uppercase; color:var(--dim); }
  .band { display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 190px), 1fr)); gap:8px; margin:6px 0 16px; }
  .grp { min-width:0; padding:7px 10px; background:var(--panel); border:1px solid var(--line); border-radius:6px; }
  .port { display:flex; align-items:center; gap:7px; min-width:0; margin-top:3px; color:var(--text); text-decoration:none; }
  .port:hover { color:var(--blue); }
  .port .nm, .op .c { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .port .nm { flex:1; }
  .dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--c); }
  .ops { display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 330px), 1fr)); column-gap:24px; margin:6px 0 16px; }
  .op { display:grid; grid-template-columns:6ch 17ch minmax(0,1fr); gap:8px; align-items:center; min-width:0;
    padding:3px 4px; border-bottom:1px solid var(--line); }
  .op a { color:var(--text); text-decoration:none; }
  .op a:hover { color:var(--blue); }
  /* Every other app's port, folded into one line, its arrow as Files' folders wear. */
  .rest { margin:-10px 0 16px; }
  .rest summary { list-style:none; cursor:pointer; padding:3px 4px; }
  .rest summary::-webkit-details-marker { display:none; }
  .rest summary::before { content:"▸ "; }
  .rest[open] summary::before { content:"▾ "; }
  .rest .ops { margin-top:2px; }
  /* The account order: each turn, the next one outlined, then a box to set a new one. */
  .order { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:6px 0 8px; }
  .turn { display:inline-flex; align-items:center; justify-content:center; min-width:30px; height:26px; padding:0 8px;
    font-weight:700; background:var(--panel); border:1px solid var(--line); border-radius:5px; }
  .turn.next { border-color:var(--text); box-shadow:inset 0 -2px 0 var(--text); }
  /* The launch page's pills, a row of them wrapping as the order does. */
  .order .pills { flex-wrap:wrap; }
  .set { display:flex; gap:6px; align-items:center; max-width:520px; }
  .set input { flex:1; min-width:0; height:27px; padding:0 10px; font:inherit; border-radius:4px;
    background:var(--bg); color:var(--text); border:1px solid var(--line); }
  .set input:focus { outline:none; border-color:var(--blue); }
  .set input.bad { border-color:var(--red); }
  .hint { max-width:520px; margin:6px 0 16px; color:var(--dim); }
  /* Two parts side by side. */
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:0 40px; }
  .pair > div { min-width:0; }
  .pair .set, .pair .hint { max-width:none; }
  @media (max-width:700px) { .pair { grid-template-columns:1fr; } }
  /* Each account's two windows, as bars: its percent and its reset. */
  .use { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 16px; }
  .use > .grp { flex:1 1 0; min-width:240px; }
  .use .hd { display:flex; justify-content:space-between; gap:8px; }
  .use .sn { font:inherit; color:var(--text); background:none; border:0; padding:0 2px; cursor:pointer; }
  .use .sn:hover { color:var(--blue); }
  .win { margin-top:8px; }
  .win .wl { display:flex; flex-wrap:wrap; justify-content:space-between; gap:0 8px; }
  .meter { position:relative; height:8px; margin-top:4px; background:var(--line); border-radius:4px; }
  .meter i { display:block; height:100%; background:var(--blue); border-radius:4px; }
  .use .seen { margin-top:8px; }
  /* Each account's own default, at the foot of its card. Max, which no
     settings.json keeps, is greyed. An outsource engine's wears it too. */
  .own, .eng { margin-top:10px; padding-top:8px; border-top:1px solid var(--line); }
  .own .order, .eng .order { margin:4px 0 0; gap:5px; }
  .use + .hint { margin-top:-8px; }
  /* The memory guard's findings, last: one line each, its buttons after
     it. Stand-in, G3 v1's: every size and colour, bar End's red fill. */
  .mem { margin:6px 0 16px; font-size:12px; }
  .mem .calm { margin:0; padding:4px 0; }
  .mem .row { display:flex; flex-wrap:wrap; align-items:center; gap:6px 12px; padding:4px 0; }
  .mem .t, .mem .q { flex:1 1 320px; min-width:0; }
  .mem .t .dot { margin-right:8px; vertical-align:1px; }
  .mem .bs { display:flex; flex-wrap:wrap; gap:6px; max-width:100%; }
  .mem .btn { height:22px; padding:0 7px; font-size:11px; }
  .mem .said { flex-basis:100%; color:var(--dim); }
  .mem .idle { padding:2px 0 2px 15px; }
  .mem .row [hidden] { display:none; }
  /* While a finding is open, its bar sits under the head, edge to edge. */
  .bars { margin:-12px -12px 12px; }
  .mbar { display:flex; align-items:center; justify-content:space-between; gap:12px; width:100%; height:32px;
    padding:0 12px; font:inherit; font-size:12px; color:var(--text); text-align:left; cursor:pointer;
    background:var(--panel); border:0; border-left:3px solid var(--c); }
  .mbar .dim { flex:none; white-space:nowrap; }
  @media (max-width:520px) { body > main { padding:8px; } .bars { margin:-8px -8px 10px; } }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. A
     field's text is 16px, WebKit's standard size: smaller, a tap into it
     zooms the page. */
  @media (hover:none) and (pointer:coarse) {
    .set input { height:44px; font-size:16px; }
    .set .btn, .pills button { min-width:44px; height:44px; }
    .port { min-height:44px; }
    .op a { display:flex; align-items:center; min-height:44px; }
    .rest summary { display:flex; align-items:center; min-height:44px; }
    .use .sn { min-width:44px; min-height:44px; }
    .mem .btn { min-width:44px; height:auto; min-height:44px; }
    .mbar { height:auto; min-height:44px; }
  }
</style>
"""

# Saving reloads the page. A reload while I type keeps my words: DRAFTS.
ORDER_SCRIPT = """<script>
(() => {
  const box = document.getElementById('order'), ok = v => /^[\\s,%s]*$/.test(v);
  box.addEventListener('input', () => box.classList.toggle('bad', !ok(box.value)));
  document.getElementById('set').onsubmit = async e => {
    e.preventDefault();
    if (!ok(box.value)) return;
    await fetch('/', {method: 'POST', redirect: 'manual', body: new URLSearchParams({order: box.value})});
    location.reload();
  };
  // A pill's group names what it sets, effort or model.
  document.querySelectorAll('#effort button, #model button, #grok button').forEach(b => b.onclick = async () => {
    const body = {[b.parentNode.dataset.k]: b.dataset.v};
    await fetch('/', {method: 'POST', redirect: 'manual', body: new URLSearchParams(body)});
    location.reload();
  });
  document.querySelectorAll('.own button:enabled').forEach(b => b.onclick = async () => {
    const body = {own: b.closest('.own').dataset.a, ['own_' + b.parentNode.dataset.k]: b.dataset.v};
    await fetch('/', {method: 'POST', redirect: 'manual', body: new URLSearchParams(body)});
    location.reload();
  });
})();
</script>
"""


def order_part(d: dict) -> str:
    """The order launched sessions take accounts in, the next turn outlined,
    and a box to set a new one."""
    order, at = d["order"], d["next"]
    nxt = ' class="turn next" title="The next launch takes it"'
    turns = ("".join(f'<span{nxt if i == at else " class=turn"}>{page.esc(a)}</span>' for i, a in enumerate(order))
             if order else f'<span class="dim">None set. Every launch takes account {accounts.FALLBACK}.</span>')
    return (f'<div class="lbl">Default account order</div><div class="order">{turns}</div>'
            f'<form class="set" id="set"><input id="order" value="{page.esc(" ".join(order))}" spellcheck="false"'
            ' autocomplete="off" placeholder="1" aria-label="A new account order">'
            '<button class="btn go">Save</button></form>'
            '<p class="hint">A session launched with no account named takes the outlined one, and the next '
            'launch the one after. The order repeats. A named account always wins, and takes no turn.</p>')


# How far each reset is from now, ticking on its own, so the page never
# reloads for the minutes alone. A reset passing moves the page's key. It
# serves the account cards and the outsource cards both, after them.
USAGE_SCRIPT = """<script>
(() => {
  const far = s => {
    const m = Math.round(Math.abs(s) / 60), h = Math.round(m / 60), d = Math.round(h / 24);
    return m < 60 ? `${m} minute${m === 1 ? '' : 's'}` : h < 48 ? `${h} hour${h === 1 ? '' : 's'}` : `${d} days`;
  };
  const tick = () => document.querySelectorAll('.use [data-t]').forEach(e => {
    const s = +e.dataset.t - Date.now() / 1000;
    e.textContent = Math.abs(s) < 60 ? (s > 0 ? ', in under a minute' : ', just now')
                  : s > 0 ? `, in ${far(s)}` : `, ${far(s)} ago`;
  });
  tick();
  setInterval(tick, 30000);
  // A session's number opens it as the rail does: home opens its hub.
  document.querySelectorAll('.use .sn').forEach(b => b.onclick = () => {
    if (parent !== window) parent.postMessage({ws: 1, open: 'session', nn: b.dataset.nn}, '*');
    else location.href = '/#' + b.dataset.nn;
  });
})();
</script>
"""


def clock(epoch: int) -> str:
    """An instant on this Mac's clock: 14:20 today, Mon 18:00 on another day."""
    t = time.localtime(epoch)
    return time.strftime("%H:%M" if t[:3] == time.localtime()[:3] else "%a %H:%M", t)


# Each account's plan, as I hold it.
PLANS = {a: accounts.ACCOUNTS[a]["plan"] for a in accounts.KNOWN}

# A window as the status line names it.
WINDOWS = {"five": "five_hour", "week": "seven_day"}


def usage(held: dict) -> dict:
    """Each account's two windows now, the sessions running on it, and when
    its numbers were last read: {"3": {"five": (36.0, 1791570000), "week":
    (17.0, 1791990000), "on": ["12", "20"], "read": 1791566640}}. A window
    whose reset has passed reads 0, beside the reset it passed. Read is the
    kept file's time, to the minute, and 0 when none was ever kept."""
    live = registry.claude_records()
    now = time.time()
    out = {}
    for a in accounts.KNOWN:
        got = finish.limits(a)
        try:
            read = int(os.path.getmtime(os.path.join(finish.STATE, f"limits-{a}.json")))
        except OSError:
            read = 0
        out[a] = {"read": read,
                  "on": [nn for nn, r in held.items() if r.get("account") == a and registry.pid_of(r, live)]}
        for k, name in WINDOWS.items():
            w = got.get(name) if isinstance(got.get(name), dict) else {}
            reset = int(w.get("resets_at") or 0)
            out[a][k] = (float(w.get("used_percentage") or 0) if reset > now else 0.0, reset)
    return out


def own_part(a: str, mine: dict) -> str:
    """Account A's own default, at the foot of its card: the model a session
    I start myself on it takes, in the launch page's pills, then the effort
    kept for that model, one click to set each. With no model saved, Claude
    Code picks, and no effort can be kept yet."""
    if not mine["saved"]:
        said = '<div class="dim">None saved. Claude Code picks its own.</div>'
    elif mine["model"] not in [v for v, _, _ in views.launcher.offered()]:
        said = f'<div class="dim">Saved: {page.esc(models.name(mine["model"]))}</div>'
    else:
        said = ""
    off = ' disabled title="Pick a model first: Claude Code keeps an effort per model"'
    kept = [e for e in views.launcher.EFFORTS if e[0] in accounts.SAVED]
    efforts = (views.launcher.pills("effort", kept, mine["effort"], "" if mine["model"] else off)
               + views.launcher.pills("effort", [e for e in views.launcher.EFFORTS if e not in kept], "",
                                      ' disabled title="Claude Code keeps max for one session only"'))
    return (f'<div class="own" data-a="{a}"><div class="lbl">Started by hand</div>'
            f'<div class="order">{model_pills(mine["model"])}</div>{said}<div class="order">{efforts}</div></div>')


def usage_part(use: dict, titles: dict, own: dict) -> str:
    """One card per account: its 5-hour and 7-day windows as bars, each
    with its percent and its reset, then when they were last read, then
    its own default. Its title names its plan. Each session's number opens
    it, as the rail does."""
    def bar(a: str, word: str, w) -> str:
        pct, reset = w
        tip = f"claude-{a}'s {word} window: {pct:.0f}% used"
        return (f'<div class="win" title="{page.esc(tip)}"><div class="wl"><span>{word} <b>{pct:.0f}%</b>'
                '</span><span class="dim">'
                + (f'{"resets" if reset > time.time() else "reset"} {clock(reset)}<span data-t="{reset}"></span>'
                   if reset else '') + '</span></div>'
                f'<div class="meter"><i style="width:{min(pct, 100):.0f}%"></i></div></div>')
    cards = []
    for a, u in use.items():
        on = u["on"]
        plan = PLANS.get(a, "")
        running = (("session " if len(on) == 1 else "sessions ") + ", ".join(
            f'<button type="button" class="sn" data-nn="{nn}" title="{page.esc(titles.get(nn, nn))}">{nn}</button>'
            for nn in on) if on else "no session running")
        head = (f'<div class="hd"><span class="lbl">claude-{a}{" · " + plan if plan else ""}</span>'
                f'<span class="dim">{running}</span></div>')
        if not u["read"]:
            inner = '<p class="dim seen">No reading yet. It comes with this account\'s first answer.</p>'
        else:
            inner = (bar(a, "5-hour", u["five"]) + bar(a, "7-day", u["week"])
                     + f'<div class="dim seen">Last read {clock(u["read"])}<span data-t="{u["read"]}"></span></div>')
        cards.append(f'<div class="grp">{head}{inner}{own_part(a, own[a])}</div>')
    return (f'<div class="lbl">Usage</div><div class="use">{"".join(cards)}</div>'
            '<p class="hint">Each card\'s pills: a session you start yourself on that account, in any project, '
            'starts there. /model in any of its sessions moves them too. Its effort is the one kept for its '
            'model. Max lasts one session, so it can\'t be saved.</p>')


# Each engine's pills post its engine and what they set, then draw again.
ENGINE_SCRIPT = """<script>
document.querySelectorAll('.eng button:enabled').forEach(b => b.onclick = async () => {
  const body = {engine: b.closest('.eng').dataset.e, ['engine_' + b.parentNode.dataset.k]: b.dataset.v};
  await fetch('/', {method: 'POST', redirect: 'manual', body: new URLSearchParams(body)});
  location.reload();
});
</script>
"""

# An engine's effort pills wear the launch page's shades. Codex's ultra
# goes past max.
SHADES = {v: shade for v, _, shade in views.launcher.EFFORTS} | {"ultra": "#9cfff3"}
MODEL_SHADE = "#4b6bd6"


def engines_seen() -> dict:
    """What the two outsource cards show: each engine's settings, models,
    plan and window, and the sessions running it now. A project without
    outsource shows none, and so does a file missing an engine or its
    model."""
    try:
        sets = {e: engines.config()["engines"][e] for e in engines.NAMES}
    except (OSError, ValueError, KeyError, TypeError):
        return {}
    if not all(isinstance(s, dict) and isinstance(s.get("model"), str) for s in sets.values()):
        return {}
    on = engines.running()
    return {e: {"set": sets[e], "models": engines.models(e), "on": on[e],
                "use": engines.codex_use() if e == "codex" else engines.grok_use()} for e in engines.NAMES}


def engines_part(seen: dict, titles: dict) -> str:
    """One card per outsource engine, as an account's: its plan and window,
    the sessions running it, then the model and effort every outsource run
    on it takes, one click to set each."""
    if not seen:
        return ""
    cards = []
    for e, s in seen.items():
        use, on, mine = s["use"], s["on"], s["set"]
        plan = use.get("plan", "")
        running = (("session " if len(on) == 1 else "sessions ") + ", ".join(
            f'<button type="button" class="sn" data-nn="{nn}" title="{page.esc(titles.get(nn, nn))}">{nn}</button>'
            for nn in on) if on else "no session running")
        head = (f'<div class="hd"><span class="lbl">{engines.NAMES[e]}{" · " + page.esc(plan) if plan else ""}</span>'
                f'<span class="dim">{running}</span></div>')
        if not use:
            inner = f'<p class="dim seen">No reading yet. It comes with {engines.NAMES[e]}\'s first run.</p>'
        elif "pct" in use:
            pct, reset = use["pct"], use["reset"]
            word = f'{use["days"]}-day' if e == "codex" else "Week"
            inner = (f'<div class="win"><div class="wl"><span>{word} <b>{pct:.0f}%</b></span>'
                     f'<span class="dim">{"resets" if reset > time.time() else "reset"} {clock(reset)}'
                     f'<span data-t="{reset}"></span></span></div>'
                     f'<div class="meter"><i style="width:{min(pct, 100):.0f}%"></i></div></div>')
        else:
            reset = use["reset"]
            inner = (f'<div class="win"><div class="wl"><span>Week</span><span class="dim">'
                     f'{"resets" if reset > time.time() else "reset"} {clock(reset)}<span data-t="{reset}"></span>'
                     '</span></div><p class="dim">This plan reports no percent.</p></div>')
        if use:
            inner += f'<div class="dim seen">Last read {clock(use["read"])}<span data-t="{use["read"]}"></span></div>'
        offered = s["models"]
        names = list(offered) if mine["model"] in offered else [mine["model"], *offered]
        efforts = offered.get(mine["model"], ([mine.get("effort")] if mine.get("effort") else [], ""))[0]
        pills = views.launcher.pills("model", [(m, m, MODEL_SHADE) for m in names], mine["model"])
        pills_e = (views.launcher.pills("effort", [(x, x, SHADES.get(x, MODEL_SHADE)) for x in efforts],
                                        mine.get("effort") or "")
                   if efforts else '<span class="dim">This model takes no effort.</span>')
        cards.append(f'<div class="grp">{head}{inner}<div class="eng" data-e="{e}">'
                     f'<div class="lbl">Every outsource run</div><div class="order">{pills}</div>'
                     f'<div class="order">{pills_e}</div></div></div>')
    return (f'<div class="lbl">Outsource</div><div class="use">{"".join(cards)}</div>'
            '<p class="hint">Each card\'s pills: the model and effort every outsource run on that engine takes. '
            'A brief names its engine alone, Codex unless I name Grok.</p>' + ENGINE_SCRIPT)


def effort_part(level: str) -> str:
    """The effort every launch starts at, whatever its account, one click to set it."""
    return (f'<div class="lbl">Default effort</div><div class="order" id="effort">'
            f'{views.launcher.pills("effort", views.launcher.EFFORTS, level)}</div>'
            '<p class="hint">A session launched with no effort named starts at the filled one, '
            'whatever its account. A named effort always wins.</p>')


def model_pills(name: str) -> str:
    """The launch page's model pills, model `name` filled. Each sets its
    family, so a default moves with each new one."""
    offered = views.launcher.offered()
    family = lambda v: models.family(v) or v
    return views.launcher.pills("model", [(family(v), label, shade) for v, label, shade in offered],
                                next((family(v) for v, _, _ in offered if v == name), ""))


def model_part(name: str) -> str:
    """The model every launch starts at, whatever its account, one click to
    set it."""
    return (f'<div class="lbl">Default model</div><div class="order" id="model">{model_pills(name)}</div>'
            '<p class="hint">A session launched with no model named starts at the filled one, '
            'whatever its account. A named model always wins. A new model replaces its family\'s '
            'once Claude Code knows it.</p>')


def grok_part() -> str:
    """Grok's door, lib/door.py's: open, or shut for every bot at once."""
    state = "shut" if door.shut() else "open"
    pills = views.launcher.pills("grok", [("open", "open", "#1f857a"), ("shut", "shut", "#a8741c")], state)
    return (f'<div class="lbl">Grok\'s door</div><div class="order" id="grok">{pills}</div>'
            '<p class="hint">Shut, every Grok bot is refused at once, whatever its key. '
            'Each act a bot takes is logged: grok-door.py log.</p>')


# The guard's findings, as memory-guard.py writes them: only when one opens,
# changes or closes, never on a clock. 1100 hears the file, so the system
# page draws again only then, and asks nothing on its own. No file is calm.
FINDINGS = os.path.join(serve.ROOT, ".claude", "state", "memory-guard", "findings.json")
# A button runs the guard's own act, on the Python launchd runs it on.
GUARD = ["/usr/bin/python3", os.path.join(HERE, "memory-guard.py")]

# Each level's dot, and the word a screen reader says for it. Stand-in, G3
# v1's.
LEVELS = {"warn": ("gold", "Warning"), "stop": ("red", "Stopped"), "hold": ("gold", "Frozen"),
          "slow": ("blue", "Slow"), "thawed": ("green", "Went on")}

# A finding's button acts through the guard, on that finding alone, and
# the guard's answer shows under its line. End asks once more first: its
# buttons give way to its question, which a reload keeps open. A bar under
# the head takes me down to its finding. Nothing here asks on its own.
MEMORY_SCRIPT = """<script>
(() => {
  document.querySelectorAll('.mbar').forEach(b => b.onclick = () => {
    const to = document.getElementById(b.dataset.to);
    if (to) to.scrollIntoView();
  });
  const K = 'system-asking', flip = row => row.querySelectorAll(':scope > .bs, :scope > .q').forEach(e => e.hidden = !e.hidden);
  const was = (performance.getEntriesByType('navigation')[0] || {}).type === 'reload' && sessionStorage.getItem(K);
  const open = was && document.querySelector(`#mem .row[data-id="${CSS.escape(was)}"]`);
  if (open) flip(open); else sessionStorage.removeItem(K);
  document.getElementById('mem').addEventListener('click', async e => {
    const b = e.target.closest('button'), row = b && b.closest('.row');
    if (!row) return;
    if (b.dataset.verb === 'end' && !('sure' in b.dataset)) { sessionStorage.setItem(K, row.dataset.id); return flip(row); }
    if ('back' in b.dataset) { sessionStorage.removeItem(K); return flip(row); }
    const all = row.querySelectorAll('button'), sure = 'sure' in b.dataset;
    row.querySelectorAll('.said').forEach(s => s.remove());
    all.forEach(x => x.disabled = true);
    let why;
    try {
      const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual',
                            body: new URLSearchParams({act: b.dataset.verb, finding: row.dataset.id})});
      why = r.status === 409 ? await r.text() : '';
    } catch (err) { why = '1100 did not answer.'; }
    all.forEach(x => x.disabled = false);
    if (sure) { sessionStorage.removeItem(K); flip(row); }
    if (why) {
      row.insertAdjacentHTML('beforeend', '<span class="said"></span>');
      row.lastChild.textContent = why;
    }
  });
})();
</script>
"""


# The page draws again whenever what it shows moves: an account's usage
# does, every minute or so, and never within three seconds of my typing. A
# box I typed into keeps my words through it, unsaved, and the cursor too,
# so the bars never stop moving while a box holds a draft.
DRAFTS_SCRIPT = """<script>
(() => {
  const K = 'system-drafts', kept = () => JSON.parse(sessionStorage.getItem(K) || '{}');
  const again = (performance.getEntriesByType('navigation')[0] || {}).type === 'reload';
  const was = again ? kept() : {}, at = again && sessionStorage.getItem(K + '-at');
  if (!again) sessionStorage.removeItem(K);
  document.querySelectorAll('form.set input[id]').forEach(box => {
    if (box.id in was && was[box.id] !== box.value) {
      box.value = was[box.id];
      box.dispatchEvent(new Event('input'));
    }
    box.addEventListener('input', () => sessionStorage.setItem(K, JSON.stringify({...kept(), [box.id]: box.value})));
    // A save keeps nothing: the saved value draws in its box.
    box.form.addEventListener('submit', () => {
      const d = kept();
      delete d[box.id];
      sessionStorage.setItem(K, JSON.stringify(d));
    });
  });
  const back = at && document.getElementById(at);
  if (back) { back.focus(); back.setSelectionRange(back.value.length, back.value.length); }
  addEventListener('beforeunload', () => sessionStorage.setItem(K + '-at', (document.activeElement || {}).id || ''));
})();
</script>
"""

# A reload keeps my place, so the memory section, last on the page, stays
# in view, and the other apps' ports stay open once I open them. Each
# port's link opens at the address System itself was opened at, as home's
# links do.
PLACE_SCRIPT = """<script>
(() => {
  const main = document.querySelector('main'), K = 'system-place', R = 'system-rest';
  const again = (performance.getEntriesByType('navigation')[0] || {}).type === 'reload';
  const rest = document.getElementById('rest');
  if (rest) {
    rest.open = again && sessionStorage.getItem(R) === '1';
    rest.addEventListener('toggle', () => sessionStorage.setItem(R, rest.open ? '1' : ''));
  }
  if (again) main.scrollTop = +sessionStorage.getItem(K) || 0;
  addEventListener('beforeunload', () => sessionStorage.setItem(K, main.scrollTop));
  document.querySelectorAll('a[data-port]').forEach(a => {
    a.href = `${location.protocol}//${location.hostname}:${a.dataset.port}/`;
  });
})();
</script>
"""

# Rail size: the rail's own zoom, on this device, apart from the page's.
# Its −, + and percent wear a chart's zoom tools. It keeps its pick as
# rail-zoom, which home hears change, so the rail grows at once.
RAIL_PART = """<div class="lbl">Rail size</div>
<div class="set"><span class="zt" id="rail"><span class="group">
<button type="button" data-z="-1" title="Shrink the rail" aria-label="Shrink the rail" onmousedown="event.preventDefault()">−</button>
<button type="button" data-z="1" title="Grow the rail" aria-label="Grow the rail" onmousedown="event.preventDefault()">+</button>
</span><span class="pct"></span></span></div>
<p class="hint">The left rail alone, on this device. The zoom buttons under Files zoom the page.</p>
<script>
(() => {
  const ZOOMS = %ZOOMS%, tools = document.getElementById('rail'), pct = tools.querySelector('.pct');
  const now = () => ZOOMS.includes(+localStorage.getItem('rail-zoom')) ? +localStorage.getItem('rail-zoom') : 1;
  const paint = () => {
    const z = now();
    pct.textContent = Math.round(z * 100) + '%';
    tools.querySelector('[data-z="-1"]').disabled = z === ZOOMS[0];
    tools.querySelector('[data-z="1"]').disabled = z === ZOOMS[ZOOMS.length - 1];
  };
  tools.addEventListener('click', e => {
    const b = e.target.closest('[data-z]');
    if (!b) return;
    localStorage.setItem('rail-zoom', ZOOMS[Math.max(0, Math.min(ZOOMS.length - 1, ZOOMS.indexOf(now()) + +b.dataset.z))]);
    paint();
  });
  addEventListener('storage', e => { if (e.key === 'rail-zoom') paint(); });
  paint();
})();
</script>
""".replace("%ZOOMS%", json.dumps(page.ZOOMS))


def findings():
    """The guard's open findings, in the order they opened: [] when calm,
    or before it wrote any. None when its file cannot be read."""
    try:
        with open(FINDINGS) as f:
            got = json.load(f)
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None
    found = got.get("findings") if isinstance(got, dict) else None
    return found if isinstance(found, list) else None


def row(f: dict) -> str:
    """One finding: a dot, its one line, its buttons, a Tell's note on
    hover. End's carry its question, shown in their place once End is
    pressed. End wears the shell's red fill, .btn.gone. A memory
    warning's idle sessions follow, one line each."""
    colour, word = LEVELS.get(f["level"], ("grey", f["level"]))
    acts, ask = [], ""
    for b in f["buttons"]:
        verb = b["verb"]
        acts.append(f'<button type="button" class="btn{" go" if verb == "tell" else " gone" if verb == "end" else ""}"'
                    f' data-verb="{page.esc(verb)}"' + (f' title="{page.esc(b["note"])}"' if b.get("note") else "")
                    + f'>{page.esc(b["label"])}</button>')
        if verb == "end":
            again = b["again"]
            ask = (f'<span class="q" hidden>{page.esc(again["question"])}</span><span class="bs" hidden>'
                   f'<button type="button" class="btn gone" data-verb="end" data-sure>{page.esc(again["yes"])}</button>'
                   f'<button type="button" class="btn" data-back>{page.esc(again["no"])}</button></span>')
    return (f'<div class="row" id="f-{page.esc(f["id"])}" data-id="{page.esc(f["id"])}"><span class="t">'
            f'<span class="dot" role="img" aria-label="{page.esc(word)}" style="--c:var(--{colour})"></span>'
            f'{page.esc(f["line"])}</span><span class="bs">{"".join(acts)}</span>{ask}</div>'
            + "".join(f'<div class="idle">{page.esc(s["number"])} · {s["gb"]:.1f} GB · idle {s["idle"]} min</div>'
                      for s in f.get("sessions", [])))


def memory_parts(found) -> tuple:
    """The bars under the head, and the section last on the page. Calm is
    one line, and no bar. A file the guard left unreadable is said, never
    drawn as calm."""
    try:
        bars = "".join(f'<button type="button" class="mbar" data-to="f-{page.esc(f["id"])}" style="--c:var(--'
                       f'{LEVELS.get(f["level"], ("grey",))[0]})"><span>{page.esc(f["title"])}</span>'
                       '<span class="dim">Show below</span></button>' for f in found)
        rows = "".join(row(f) for f in found) or '<p class="calm">Nothing is wrong.</p>'
    except (KeyError, TypeError, AttributeError, ValueError):
        bars, rows = "", ('<p class="calm">The guard\'s findings cannot be read: '
                          '.claude/state/memory-guard/findings.json</p>')
    return ((f'<div class="bars">{bars}</div>' if bars else ""),
            f'<div class="lbl">Memory</div><div class="mem" id="mem">{rows}</div>' + (MEMORY_SCRIPT if bars else ""))


def act(fid: str, verb: str):
    """A finding's button, pressed: the guard acts on that finding's own
    program alone, and its one line, what it did, is the press's answer.
    It runs off 1100's queue, serve.Typing's, so no page waits on it. A
    finding already closed, or a button it never offered, is said, and
    nothing acts. iTerm2 takes up to a minute to turn its logging off, so
    that one runs beside, and the findings file says how it went."""
    try:
        f = next((f for f in findings() if f["id"] == fid), None)
        offered = f is not None and any(b["verb"] == verb for b in f["buttons"])
    except (KeyError, TypeError):
        return "The guard's findings cannot be read. Nothing was done."
    if f is None:
        return "This finding is already closed. Nothing was done."
    if not offered:
        return "This finding offers no such button. Nothing was done."
    asked = [*GUARD, "act", fid, verb]
    if verb == "logging-off":
        threading.Thread(target=subprocess.run, args=(asked,), kwargs={"capture_output": True}, daemon=True).start()
        return "Asked iTerm2 to turn its logging off. It can take a minute."

    def guarded() -> str:
        try:
            r = subprocess.run(asked, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            return "The guard did not answer in 20 seconds."
        return ((r.stdout.strip() or r.stderr.strip()).splitlines() or ["The guard said nothing."])[-1]
    return serve.Typing(guarded)


def system_page() -> str:
    """Each account's usage and own default, then each outsource engine's
    card, lib/engines.py's, then the account order with
    the default effort beside it, the default model with Grok's door
    beside it, both thresholds side
    by side, the rail's size, then band 00, the database first, then every other port this
    project's scheme could own, every other app's folded into one line, and
    last the memory guard's findings. While one is open, its bar sits under
    the head."""
    held = registry.entries()
    titles = {nn: r.get("title", nn) for nn, r in held.items()}
    state, listening = seen()
    others = other(titles, listening)
    d = accounts.read()
    level = accounts.effort()
    chosen = accounts.model()
    use = usage(held)
    own = {a: accounts.own(a) for a in accounts.KNOWN}
    eng = engines_seen()
    groups = "".join(
        f'<div class="grp"><div class="lbl">{page.esc(label)}</div>'
        + "".join(f'<a class="port" href="http://localhost:{p}" data-port="{p}" target="_blank" '
                  f'title="{"up" if state[p] else "down"}">'
                  f'<span class="dot" style="--c:var(--{"green" if state[p] else "grey"})"></span><b>{p}</b>'
                  f'<span class="nm">{page.esc(name)}</span>{"" if state[p] else "<span class=dim>down</span>"}</a>'
                  for p, name in group) + '</div>' for label, group in [*([DATABASE] if DATABASE else []), *BAND])
    # This project's ports first: those its port scheme could own. Every
    # other port folds into one line.
    mine = [o for o in others if ports.in_scheme(o[0])]
    rest = [o for o in others if not ports.in_scheme(o[0])]
    rows = lambda found: "".join(
        f'<div class="op"><a class="c" href="http://localhost:{p}" data-port="{p}" target="_blank"><b>{p}</b></a>'
        f'<span class="c dim">{page.esc(proc)}</span>'
        + (f'<span class="c">{page.esc(who)}</span>' if who[:2] in held and who.startswith(who[:2] + "-")
           else f'<span class="c dim">{page.esc(who) or "–"}</span>') + '</div>'
        for p, proc, who in found)
    folded = (f'<details class="rest" id="rest"><summary class="dim">{page.count(len(rest), "more port")}, '
              f'not this project\'s</summary><div class="ops">{rows(rest)}</div></details>' if rest else "")
    up = sum(1 for v in state.values() if v)
    found = findings()
    bars, guard = memory_parts(found)
    # Last read shows to the minute, so a reading kept again within it moves
    # nothing. Another app's port moving moves nothing either: only how
    # many there are.
    shown = {a: {**u, "read": u["read"] // 60} for a, u in use.items()}
    key = hashlib.sha1(json.dumps([sorted(state.items()), mine, len(rest), d, level, chosen, context.held(), shown,
                                   own, found, eng, door.shut()]).encode()).hexdigest()[:12]
    # The pickers wear the launch page's pills. System's own sizes come after.
    body = (page.rules(views.launcher.CSS, ".pills") + SYSTEM_STYLE + bars + usage_part(use, titles, own)
            + engines_part(eng, titles) + USAGE_SCRIPT
            + f'<div class="pair"><div>{order_part(d)}</div><div>{effort_part(level)}</div></div>'
            + f'<div class="pair"><div>{model_part(chosen)}</div><div>{grok_part()}</div></div>'
            + views.handover.system_part() + RAIL_PART
            + f'<div class="lbl">Band 00</div><div class="band">{groups}</div>'
            f'<div class="lbl">Other ports · {len(mine)}</div><div class="ops">{rows(mine)}</div>{folded}'
            + guard + ORDER_SCRIPT % "".join(accounts.KNOWN) + DRAFTS_SCRIPT + PLACE_SCRIPT + page.watch(key))
    return page.render("00-system", [("", body)],
                       page.head("system", "", "", f'<span class="dim">band 00 · {up} of {len(state)} up · '
                                                  f'{len(mine)} other</span>'), refresh=0)


# ---- the files ----------------------------------------------------------------------

# A file larger than this opens cut, with a line saying so. A wave is 10 KB.
SHOWN = 400_000

# A picture or a clip opens as itself, inside the /text answer the view
# drops in whole. A clip, or a picture past BIG, plays from its own
# address, /raw/NN/REL, sent in pieces off 1100's queue, so no page waits.
BIG = 5_000_000
MEDIA = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
         ".webm": "video/webm", ".mp4": "video/mp4", ".mov": "video/quicktime"}


def size(n: int) -> str:
    return f"{n} B" if n < 1024 else f"{n / 1024:.1f} KB" if n < 1048576 else f"{n / 1048576:.1f} MB"


# One icon per kind of file, keyed by extension. A long name is cut before
# its extension shows, so the icon is what says a row is a picture.
ICONS = {
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/>'
             '<path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "video": '<rect x="2" y="5" width="14" height="14" rx="2"/><path d="m22 8-6 4 6 4z"/>',
    "text": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>'
            '<path d="M14 3v6h6"/><path d="M8 13h8M8 17h6"/>',
    "data": '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1"/>'
            '<path d="M16 21h1a2 2 0 0 0 2-2v-5a2 2 0 0 1 2-2 2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"/>',
    "log": '<path d="m4 17 6-6-6-6"/><path d="M12 19h8"/>',
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    "file": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>',
}
KIND = {".md": "text", ".txt": "text", ".json": "data", ".yml": "data", ".yaml": "data",
        ".log": "log", ".py": "code", ".ts": "code", ".tsx": "code", ".js": "code",
        ".sh": "code", ".css": "code", ".html": "code"}


def icon(name: str) -> str:
    """The icon for one file. A picture or a clip is media, and wears blue."""
    ext = os.path.splitext(name)[1].lower()
    kind = MEDIA.get(ext, "").split("/")[0] or KIND.get(ext, "file")
    media = " media" if ext in MEDIA else ""
    return (f'<svg class="kind{media}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{ICONS[kind]}</svg>')


def count(root: str) -> int:
    """How many files sit anywhere under one folder, hidden ones aside."""
    files = 0
    for _, dirs, names in os.walk(root, followlinks=True):
        dirs[:] = [n for n in dirs if not n.startswith(".")]
        files += sum(1 for n in names if not n.startswith("."))
    return files


def level(number: str, root: str, d: str) -> str:
    """The files and folders right under one folder, as tree rows. Pictures
    first, then other files, then folders, each by name. A folder comes
    closed, counting the files under it, and its rows load once it opens.
    """
    try:
        names = [n for n in os.listdir(d) if not n.startswith(".")]
    except OSError:
        return ""
    full = sorted((os.path.join(d, n) for n in names), key=lambda p: (
        os.path.isdir(p),
        not MEDIA.get(os.path.splitext(p)[1].lower(), "").startswith("image/"),
        [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(p))]))
    depth = 1 if d == root else os.path.relpath(d, root).count(os.sep) + 2
    pad = f' style="padding-left:{6 + depth * 14}px"'
    rows = []
    for p in full:
        rel = os.path.relpath(p, root)
        try:
            st = os.stat(p)
        except OSError:
            continue
        if os.path.isdir(p):
            rows.append(f'<details data-k="{page.esc(number)}/{page.esc(rel)}"><summary class="frow"{pad}>'
                        f'<span class="nm">{page.esc(os.path.basename(p))}/</span>'
                        f'<span class="fs">{count(p)}</span></summary></details>')
        else:
            rows.append(f'<a class="frow file" data-f="{page.esc(number)}/{page.esc(rel)}"{pad}'
                        f' href="?f={page.esc(urllib.parse.quote(f"{number}/{rel}"))}"'
                        f' title=".claude/state/sessions/{page.esc(number)}/{page.esc(rel)}">'
                        f'{icon(p)}<span class="nm">{page.esc(os.path.basename(p))}</span>'
                        f'<span class="fs">{size(st.st_size)} · <span data-since="{int(st.st_mtime)}"></span></span></a>')
    return "".join(rows)


def tree(nn: str, rel: str) -> str:
    """One folder's rows, asked the first time it opens. Nothing outside a
    session's own folder is ever listed, whatever the address says."""
    root = os.path.realpath(registry.folder(nn))
    want = os.path.realpath(os.path.join(root, rel)) if rel else root
    if not ((want == root or want.startswith(root + os.sep)) and os.path.isdir(want)):
        return ""
    return level(nn, root, want)


FILES_STYLE = """<style>
  body > main { padding:0; overflow:hidden; }
  .files { height:100%; display:grid; grid-template-columns:300px minmax(0,1fr); grid-template-rows:minmax(0,1fr); }
  .tree { min-width:0; min-height:0; display:flex; flex-direction:column; border-right:1px solid var(--line); }
  .view { min-width:0; min-height:0; display:flex; flex-direction:column; }
  .fhd { flex:none; display:flex; align-items:center; gap:10px; min-height:40px; padding:6px 10px;
    background:var(--panel); border-bottom:1px solid var(--line); }
  .fhd .p { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:700; }
  .fhd .dim { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .fhd #again { flex:none; margin-left:auto; }
  .fhd #copy { flex:none; }
  .fhd #copy-status { color:var(--dim); font-size:11px; }
  .scroll { flex:1; min-height:0; overflow-y:auto; }
  .ftb { padding:8px 6px 16px; }
  .team { margin:14px 0; }
  .team:first-child { margin-top:0; }
  .tl { margin:0 0 4px; padding:0 6px; font:700 10px/1.4 ui-monospace,Menlo,monospace; letter-spacing:.08em;
    text-transform:uppercase; color:var(--dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  details { margin:0; }
  summary { list-style:none; }
  summary::-webkit-details-marker { display:none; }
  .frow { display:flex; align-items:center; gap:6px; width:100%; min-width:0; padding:2px 6px; font-size:12px;
    color:var(--text); text-decoration:none; border-radius:4px; cursor:pointer; }
  summary.frow::before { content:"▸"; color:var(--dim); flex:none; }
  details[open] > summary.frow::before { content:"▾"; }
  .tree .kind { flex:none; width:12px; height:12px; color:var(--dim); }
  .tree .kind.media { color:var(--blue); }
  .frow:hover { background:var(--hover); }
  .frow:focus-visible { outline:2px solid var(--blue); outline-offset:-2px; }
  .frow.on { background:var(--raised); box-shadow:inset 2px 0 0 var(--text); }
  .nm { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .fs { flex:none; font-size:11px; color:var(--dim); white-space:nowrap; }
  pre.txt { margin:0; padding:12px 14px 24px; font:12px/1.55 ui-monospace,Menlo,monospace; white-space:pre-wrap;
    overflow-wrap:anywhere; tab-size:2; }
  .cut { padding:0 14px 14px; color:var(--dim); }
  div.media { padding:12px; }
  .media img, .media video { max-width:100%; }
  .files[data-picked="0"] .view .fhd, .files[data-picked="0"] #fview, .files[data-picked="1"] .view .empty { display:none; }
  /* Narrow, one side at a time: the tree, then the file. */
  @media (max-width: 820px) {
    .files { grid-template-columns:minmax(0,1fr); }
    .tree { border-right:0; }
    .files[data-picked="1"] > .tree, .files[data-picked="0"] > .view { display:none; }
  }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    .frow { min-height:44px; }
    .fhd #again, .fhd #copy { min-width:44px; height:44px; }
  }
</style>
"""

# A folder stays as I left it across reloads, and the picked file rides in
# the address's query, so a reload keeps both. A folder's rows load the
# first time it opens, so the page carries only what I opened. How long ago
# ticks on its own. The tree never draws again on its own, whatever the
# sessions write: Refresh draws it again. Inside home its frame stays when
# I leave it, so shown again, it is drawn again. The picked file is told:
# a session rewriting it draws it again in place, where I scrolled. Each
# file is a link, so the keyboard reaches it, and Cmd opens it on its own.
FILES_SCRIPT = """<script>
(() => {
  const K = 'files-open', opened = () => JSON.parse(localStorage.getItem(K) || '{}');
  const box = document.querySelector('.files'), view = document.getElementById('fview');
  const tree = document.querySelector('.tree .scroll');
  const ago = t => { const d = Math.max(0, Math.floor(Date.now() / 1000 - t));
    return d < 60 ? d + 's' : d < 3600 ? Math.floor(d / 60) + 'm' : Math.floor(d / 3600) + 'h'; };
  const tick = () => document.querySelectorAll('[data-since]').forEach(e => e.textContent = ago(+e.dataset.since));
  // A folder's rows, asked once. Each folder inside opens as I left it.
  let busy = 0, settle;
  const settled = new Promise(r => settle = r);
  function fill(d) {
    if (d.filled) return d.filled;
    busy++;
    const [nn, ...rel] = d.dataset.k.split('/');
    return d.filled = (async () => {
      try {
        const r = await fetch('/tree/' + nn + '/' + rel.map(encodeURIComponent).join('/'));
        d.insertAdjacentHTML('beforeend', await r.text());
        tick();
        restore(d);
      } catch (e) {}
      if (!--busy) settle();
    })();
  }
  function restore(root) {
    const s = opened();
    root.querySelectorAll('details[data-k]').forEach(d => {
      if (d.restored) return;
      d.restored = true;
      if (s[d.dataset.k]) { d.open = true; fill(d); }
    });
  }
  tree.addEventListener('toggle', e => {
    const d = e.target;
    if (!(d instanceof HTMLDetailsElement) || !d.dataset.k) return;
    const s = opened();
    s[d.dataset.k] = d.open;
    localStorage.setItem(K, JSON.stringify(s));
    if (d.open) fill(d);
  }, true);
  // The watch's key is the picked file's, so a rewrite tells the page.
  const watch = document.getElementById('watch'), text = f => '/text/' + f.split('/').map(encodeURIComponent).join('/');
  const copyButton = document.getElementById('copy'), copyStatus = document.getElementById('copy-status');
  let shown = '', selection = 0;
  function show(html) {
    view.innerHTML = html;
    const got = view.querySelector('.picked');
    document.getElementById('fpath').textContent = got ? got.dataset.path + ' · ' + got.dataset.size : shown;
    if (watch) watch.dataset.key = got ? got.dataset.mark : 'none';
  }
  async function pick(f) {
    const picked = ++selection;
    shown = f;
    box.dataset.picked = f ? '1' : '0';
    copyButton.disabled = true;
    copyStatus.textContent = '';
    view.textContent = f ? 'Loading…' : '';
    document.getElementById('fpath').textContent = f;
    history.replaceState(null, '', f ? '?f=' + encodeURIComponent(f) : location.pathname);
    const parts = f ? f.split('/') : [];
    for (let i = 1; i < parts.length; i++) {
      const d = tree.querySelector(`details[data-k="${CSS.escape(parts.slice(0, i).join('/'))}"]`);
      if (!d) break;
      d.open = true;
      await fill(d);
      if (picked !== selection) return;
    }
    document.querySelectorAll('.frow.file').forEach(a => a.classList.toggle('on', a.dataset.f === f));
    if (f) {
      try {
        const response = await fetch(text(f));
        if (!response.ok) throw new Error('file');
        const html = await response.text();
        if (picked !== selection) return;
        show(html);
        copyButton.disabled = !view.querySelector('.picked');
        view.scrollTop = +sessionStorage.getItem('files-view') || 0;
        sessionStorage.removeItem('files-view');
      } catch (e) { if (picked === selection) view.textContent = 'Could not open this file.'; }
    } else if (watch) watch.dataset.key = 'none';
    // Home watches the page by its address, which now names another file.
    try { if (parent !== window && parent.watchFor) parent.watchFor(window); } catch (e) {}
  }
  window.told = async () => {
    const f = shown, picked = selection, top = view.scrollTop;
    if (!f) return;
    try {
      const html = await (await fetch(text(f))).text();
      if (picked === selection) { show(html); copyButton.disabled = !view.querySelector('.picked'); view.scrollTop = top; }
    } catch (e) {}
  };
  // Copy the complete file, never the shortened preview. Clipboard writes
  // start in the click itself, including on browsers requiring that gesture.
  copyButton.onclick = async () => {
    const f = shown, info = view.querySelector('.picked');
    if (!f || !info) return;
    const kind = info.dataset.copy;
    const url = '/raw/' + f.split('/').map(encodeURIComponent).join('/');
    copyStatus.textContent = 'Copying…';
    try {
      if (!navigator.clipboard || !window.ClipboardItem) throw new Error('Clipboard unavailable.');
      let type = kind === 'text' ? 'text/plain' : kind === 'image' ? 'image/png' : 'application/octet-stream';
      if (kind === 'file' && (!ClipboardItem.supports || !ClipboardItem.supports(type)))
        throw new Error('This browser cannot copy this file type.');
      const data = fetch(url).then(r => {
        if (!r.ok) throw new Error('File unavailable.');
        return r.blob();
      }).then(async blob => {
        if (kind === 'text') return new Blob([new TextDecoder('utf-8', {fatal:true}).decode(await blob.arrayBuffer())], {type});
        if (kind === 'file') return new Blob([blob], {type: 'application/octet-stream'});
        const image = new Image(), src = URL.createObjectURL(blob);
        try {
          image.src = src;
          await image.decode();
          const canvas = document.createElement('canvas');
          canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
          canvas.getContext('2d').drawImage(image, 0, 0);
          return await new Promise((resolve, reject) => canvas.toBlob(b => b ? resolve(b) : reject(new Error('Image unavailable.')), 'image/png'));
        } finally { URL.revokeObjectURL(src); }
      });
      await navigator.clipboard.write([new ClipboardItem({[type]: data})]);
      if (f === shown) copyStatus.textContent = kind === 'file' ? 'Copied; the destination must support this format.' : 'Copied';
    } catch (e) { if (f === shown) copyStatus.textContent = e.message || 'Could not copy this file.'; }
  };
  tree.addEventListener('click', e => {
    const a = e.target.closest('.frow.file');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    pick(a.dataset.f);
  });
  document.getElementById('shut').onclick = () => pick('');
  addEventListener('keydown', e => { if (e.key === 'Escape') pick(''); });
  addEventListener('beforeunload', () => {
    sessionStorage.setItem('files-scroll', tree.scrollTop);
    sessionStorage.setItem('files-view', view.scrollTop);
  });
  restore(tree);
  if (!busy) settle();
  // The tree scrolls back once every folder I left open has its rows.
  settled.then(() => { tree.scrollTop = +sessionStorage.getItem('files-scroll') || 0; });
  tick();
  setInterval(tick, 5000);
  pick(new URLSearchParams(location.search).get('f') || decodeURIComponent(location.hash.slice(1)));
  document.getElementById('again').onclick = () => location.reload();
  let away = false;
  new IntersectionObserver(([e]) => {
    if (e.isIntersecting && away) location.reload();
    away = !e.isIntersecting;
  }).observe(box);
})();
</script>
"""


def files_page(query: str = "") -> str:
    """Every session's folder, lowest number first. A team's sit together,
    under its head's, and only a team wears a header: an assistant with a
    plan, and its sessions, as its hub has a team tab. Its key is the
    picked file's, as its query names it."""
    held, live, open_ids = registry.entries(), registry.claude_records(), workstation.panes.ids(workstation.panes.FRESH)
    owned = workstation.plans.owners(held)
    states = {nn: page.shown(nn, r, live.get(r.get("session_id")), open_ids)[:4] for nn, r in held.items()}
    out = []
    for head, members in workstation.teams_of(held, owned):
        folders = []
        for nn in [head] + members:
            files = count(os.path.realpath(registry.folder(nn)))
            name, word, colour, look = states[nn]
            folders.append(f'<details data-k="{nn}"><summary class="frow" title="{page.esc(word)}">'
                           f'<span class="chip{" g" if colour == "grey" else ""}{" dashed" if look else ""}" '
                           f'style="--c:var(--{colour})">'
                           f'{page.esc(workstation.plans.tag(nn, owned))}</span><span class="nm">sessions/{nn}/ · '
                           f'{page.esc(name)}</span>'
                           f'<span class="fs">{files}</span></summary></details>')
        if workstation.plans.plan(head).get("stages"):
            out.append(f'<div class="team"><div class="tl">Team {head} · '
                       f'{page.esc(states[head][0])}</div>{"".join(folders)}</div>')
        else:
            out += folders
    body = (FILES_STYLE + '<div class="files" data-picked="0"><div class="tree">'
            f'<div class="fhd">{page.family("files")}<span class="dim">· {len(held)} session folders</span>'
            '<button class="btn" id="again" title="Draw the page again, as it stands now">Refresh</button></div>'
            f'<div class="scroll"><div class="ftb">{"".join(out)}</div></div></div>'
            f'<div class="view"><div class="fhd"><span class="p" id="fpath"></span>'
            '<span id="copy-status" role="status"></span><button class="btn" id="copy" disabled>Copy</button>'
            f'<button class="close" id="shut" aria-label="Close the file" title="Show no file">{page.icon("close", 15)}</button></div>'
            f'<div class="scroll" id="fview"></div>{page.blank("Pick a file")}</div></div>'
            + page.watch(files_key(query)) + FILES_SCRIPT)
    return page.render("00-files", [("", body)], refresh=0)


def inside(nn: str, rel: str) -> str:
    """The file REL names inside session NN's own folder, as its real path,
    or "" when it is no file there. Nothing outside a session's own folder
    is ever read or sent, whatever the address says."""
    root = os.path.realpath(registry.folder(nn))
    want = os.path.realpath(os.path.join(root, rel))
    return want if want.startswith(root + os.sep) and os.path.isfile(want) else ""


def raw(path: str):
    """The file /raw/NN/REL names, for serve.run to send in pieces, or None."""
    m = re.fullmatch(r"/raw/(\d{2})/(.+)", path)
    return (inside(m.group(1), urllib.parse.unquote(m.group(2))) or None) if m else None


def mark(path: str) -> str:
    """A picked file's key: its size and time, so a session rewriting it
    moves it."""
    try:
        st = os.stat(path)
    except OSError:
        return "none"
    return f"{st.st_size}-{st.st_mtime_ns}"


# Each file a Files page shows, and when its watch last asked: 1100 hears
# it while a page asks about it, as it hears a transcript.
SHOWING: dict = {}


def files_key(query: str) -> str:
    """The Files page's key: the file its query picks, f=NN/REL, else none.
    The tree never moves it: Refresh draws it again."""
    m = re.fullmatch(r"(\d{2})/(.+)", (urllib.parse.parse_qs(query).get("f") or [""])[0])
    path = inside(m.group(1), m.group(2)) if m else ""
    if not path:
        return "none"
    SHOWING[path] = time.time()
    return mark(path)


def showing() -> list:
    """Every file a Files page asked about in the last minute."""
    now = time.time()
    return [p for p, at in list(SHOWING.items()) if now - at < 60]


def text(nn: str, rel: str) -> str:
    """One picked file, as the right side shows it: its path, size and key,
    then its text, or itself when it is a picture or a clip."""
    want = inside(nn, rel)
    if not want:
        return '<p class="cut">This file is gone.</p>'
    root = os.path.realpath(registry.folder(nn))
    kind = MEDIA.get(os.path.splitext(want)[1].lower())
    with open(want, "rb") as f:
        sample = f.read(8192)
    try:
        codecs.getincrementaldecoder("utf-8")().decode(sample, final=False)
        copy_kind = "text" if b"\0" not in sample else "file"
    except UnicodeDecodeError:
        copy_kind = "file"
    if kind and kind.startswith("image/"):
        copy_kind = "image" if kind in ("image/png", "image/jpeg") else "file"
    elif kind and kind.startswith("video/"):
        copy_kind = "file"
    head = (f'<div class="picked" data-path=".claude/state/sessions/{nn}/{page.esc(os.path.relpath(want, root))}" '
            f'data-size="{size(os.path.getsize(want))}" data-mark="{mark(want)}" data-copy="{copy_kind}"></div>')
    if kind:
        if kind.startswith("video/") or os.path.getsize(want) > BIG:
            src = f"/raw/{nn}/{urllib.parse.quote(os.path.relpath(want, root))}"
        else:
            with open(want, "rb") as f:
                src = f"data:{kind};base64,{base64.b64encode(f.read()).decode()}"
        return head + (f'<div class="media"><video src="{src}" controls preload="metadata"></video></div>'
                       if kind.startswith("video/") else f'<div class="media"><img src="{src}" alt=""></div>')
    # The cut counts bytes, as SHOWN does: a letter taking two bytes still
    # says where the file was cut.
    with open(want, "rb") as f:
        raw = f.read(SHOWN + 1)
    return (head + f'<pre class="txt">{page.esc(raw[:SHOWN].decode("utf-8", "replace"))}</pre>'
            + (f'<p class="cut">Cut at {size(SHOWN)}.</p>' if len(raw) > SHOWN else ""))


# Each launch page's banner: the one sentence a refused launch leaves, kept
# until the next launch tries, or its rows are gone.
BANNERS: dict = {}


def banner_of(nn: str) -> list:
    if not views.launcher.read(nn):
        BANNERS.pop(nn, None)
    return BANNERS.setdefault(nn, [""])


# Every page 1100 draws at /p/KIND/NN, by kind: how it draws, its key when
# a cheap one exists, and how it takes a press. A session's tab kinds are
# page.TAB_KINDS'; the team tab's is the assistant's. A kind with no line
# here answers not found, never another kind's page. A transcript and a
# walk's screenshots answer parts of their own, at their own addresses.
DRAWN = {
    "clarify": (views.clarify.render, views.clarify.key, views.clarify.take),
    "assistant": (views.assistant.render, None, views.assistant.take),
    "launch": (lambda nn: views.launcher.render_for(nn, banner_of(nn))(), views.launcher.key,
               lambda nn, form: views.launcher.take_for(nn, banner_of(nn))(form) or ""),
    "handover": (views.handover.render, None, views.handover.take),
    "jury": (jury.render, jury.key, jury.take),
    "walk": (views.walk_list.render, views.walk_list.key, None),
}
# A page 1100 draws for one session, and its key, and the launch page's rows.
PAGE = re.compile(serve.address(f"({'|'.join(DRAWN)})", r"(\d{2})") + "(/key|/rows)?")
# A session's transcript, and each part it asks for: transcript-page.py's answer().
TRANSCRIPT = re.compile(serve.address("transcript", r"(\d{2})") + r"(/[\w/-]+)?")
# A session's screenshots, and each one: walk-shots-page.py's answer().
SHOTS = re.compile(serve.address("shots", r"(\d{2})") + r"(/pic/\d+)?")
# What an address nothing lives at answers, and a press there.
NOT_FOUND = (b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404)
# The type data goes as: home's model, the agenda's, a launch page's rows.
JSON = "application/json"
NO_PRESS = "Nothing at this address takes a press."


def draw_page(kind: str, nn: str, part: str = ""):
    render, key, _ = DRAWN[kind]
    if part == "/rows" and kind == "launch":
        return views.launcher.saved(nn).encode(), JSON
    return key(nn) if part == "/key" and key else render(nn)


def keyof(path: str):
    """A page's key without drawing it, from that page's own key(), or None
    when only a draw tells, as when its key() fails: the draw then shows
    why, contained()."""
    try:
        if path.partition("?")[0] == "/files":
            return files_key(path.partition("?")[2])
        if t := TRANSCRIPT.fullmatch(path.partition("?")[0]):
            return transcript.key(t.group(1))
        if (s := SHOTS.fullmatch(path.partition("?")[0])) and not s.group(2):
            return views.shots.key(s.group(1))
        m = PAGE.fullmatch(path.partition("?")[0])
        key = m and DRAWN[m.group(1)][1]
        return key(m.group(2)) if key else None
    except Exception:
        logged(f"key {path}")
        return None


def take(form: dict, path: str = "/") -> str:
    """A post from a page 1100 draws, answered by that page's own take, or a
    control on the system page, which posts to /. A pane gone is said, and
    so is what the guard did. A post anywhere else takes nothing."""
    if t := TRANSCRIPT.fullmatch(path):
        return transcript.take(t.group(1), form)
    if path == "/push":
        return push.keep(form)
    if m := PAGE.fullmatch(path):
        took = DRAWN[m.group(1)][2]
        return took(m.group(2), form) if took else ""
    if path == "/agenda":
        return agenda.take(form)
    if path != "/":
        return NO_PRESS
    if "act" in form:
        return act(form.get("finding", [""])[0], form["act"][0])
    if "order" in form:
        order = accounts.parse(form["order"][0])
        if order is not None:
            accounts.save(order)
    if "effort" in form:
        accounts.save_effort(form["effort"][0])
    if "model" in form:
        accounts.save_model(form["model"][0])
    if "own" in form:
        accounts.save_own(form["own"][0], form.get("own_model", [""])[0], form.get("own_effort", [""])[0])
    if "engine" in form and form["engine"][0] in engines_seen():
        engines.save(form["engine"][0], form.get("engine_model", [""])[0], form.get("engine_effort", [""])[0])
    if "threshold" in form:
        context.save("threshold", form["threshold"][0])
    if "wrapup" in form:
        context.save("wrapup", form["wrapup"][0])
    if "grok" in form:
        door.switch(form["grok"][0] == "open")
    return ""


# ---- my iPhone's icon -----------------------------------------------------------------------

# 1100 on my iPhone's home screen: my primary orange, --primary in
# code/tokens/tokens.css, filling the square, and the white rocket Launch
# wears, centred. With no icon tag, iOS asks the site's root for it.
# librsvg draws it.
TOUCH = ('<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">'
         '<rect width="180" height="180" fill="#f26b1f"/><g transform="translate(36 36) scale(4.5)" fill="none" '
         'stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{}</g></svg>')


def touch_icon() -> bytes:
    """The icon, 180 by 180, as a PNG."""
    return subprocess.run(["/opt/homebrew/bin/rsvg-convert"], input=TOUCH.format(page.PATHS["launch"]).encode(),
                          capture_output=True, check=True).stdout


# 1100 as an app of its own on my phone: its name, its icon, and no Safari
# around it. A phone's buzz needs one.
MANIFEST = json.dumps({"name": project.NAME, "short_name": project.NAME, "id": "/", "start_url": "/",
                       "scope": "/", "display": "standalone", "background_color": "#0f1115",
                       "theme_color": "#0f1115",
                       "icons": [{"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}]})


def opened(nn: str) -> str:
    """Home's address that opens session NN's transcript, in its hub."""
    held = registry.entries()
    return "/#{}/transcript:{}".format(next((h for h, members in workstation.teams_of(held, plans.owners(held))
                                            if nn == h or nn in members), nn), nn)


# ---- the server -------------------------------------------------------------------------

def one_list(fn):
    """`fn`, asking the Mac for its process table once per draw, however
    many sessions it shows: wake.once()."""
    def run(*args):
        with wake.once():
            return fn(*args)
    return run


# Each failure already in 1100's log, so a page failing on every beat is
# logged once.
LOGGED: set = set()


def logged(name: str) -> None:
    """The error being handled, into 1100's log, once per name."""
    if name not in LOGGED:
        LOGGED.add(name)
        traceback.print_exc()


def contained(fn):
    """`fn`, its error kept to the page that raised it. That page shows the
    error's last line and wears a key made from it, so every other page
    asked about in the same /heard goes on being told. Home's /model
    failing, home keeps the model it holds."""
    def run(*args):
        try:
            return fn(*args)
        except Exception as e:
            line = f"{type(e).__name__}: {e}"
            key = hashlib.sha1(f"{args}{line}".encode()).hexdigest()[:12]
            logged(key)
            return page.render("00-failed", [("", '<p class="note">This page failed to draw. 1100\'s log '
                                             f'holds the whole error.</p><pre class="doc">{page.esc(line)}</pre>'
                                             + page.watch(key))], refresh=0)
    return run


def route(path: str):
    """Home is /. Every other address is named here, and one named nowhere
    answers not found."""
    bare, _, query = path.partition("?")
    bare = bare.split("#")[0]
    if bare == "/":
        return None
    # Data goes as data, never as a page: a name in it can never draw.
    if bare == "/model":
        return json.dumps(workstation.model()).encode(), JSON
    if m := PAGE.fullmatch(bare):
        return draw_page(m.group(1), m.group(2), m.group(3) or "")
    if m := TRANSCRIPT.fullmatch(bare):
        got = transcript.answer(m.group(1), m.group(2) or "", query)
        return NOT_FOUND if got is None else got
    if m := SHOTS.fullmatch(bare):
        got = views.shots.answer(m.group(1), m.group(2) or "")
        return NOT_FOUND if got is None else got
    if bare == "/system":
        return system_page()
    if bare == "/files":
        return files_page(query)
    if m := re.fullmatch(r"/tree/(\d{2})/?(.*)", bare):
        return tree(m.group(1), urllib.parse.unquote(m.group(2)))
    if m := re.fullmatch(r"/text/(\d{2})/(.+)", bare):
        return text(m.group(1), urllib.parse.unquote(m.group(2)))
    if bare == "/skills":
        return skills.render()
    if bare == "/agenda":
        return agenda.render()
    if bare == "/agenda/data":
        return agenda.answer().encode(), JSON
    if bare == "/apple-touch-icon.png":
        return touch_icon(), "image/png"
    if bare == "/manifest.webmanifest":
        return MANIFEST.encode(), "application/manifest+json"
    if bare == project.ASKED:
        return project.identity().encode(), "application/json"
    if bare == "/sw.js":
        return push.WORKER.encode(), "text/javascript; charset=utf-8"
    return NOT_FOUND


def read_pid(path: str) -> int:
    """The pid a pidfile holds, or 0 when there is nothing to read."""
    try:
        with open(path) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def start_band() -> str:
    """Bring up every band-00 server that is not already answering.

    Nothing is waited for. A dev server takes far longer to bind than a
    prompt should block, and the system page turns each port green on its
    own, which is what it is for.

    The command is left detached, so it outlives the hook that started it,
    and its pid is recorded. A live launcher is the reason not to start a second
    one: a port that never binds, because its package is not written yet,
    would otherwise relaunch the whole band on every call.

    A project naming no band 00 starts none.
    """
    if not DEV or not PORTS:
        return "This project names no band 00, so 1100 runs alone."
    pidfile = serve.pidfile("band-00")
    if ports.alive(read_pid(pidfile)):
        return "Band 00 is already running."
    down = sorted(p for p, up in band_state().items() if not up)
    if not down:
        return "Band 00 was already up."
    log = serve.logfile("band-00")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "ab") as f:
        started = subprocess.Popen(DEV, cwd=serve.ROOT, stdout=f, stderr=f,
                                   start_new_session=True)
    with open(pidfile, "w") as f:
        f.write(str(started.pid))
    return f"Band 00 starting, {len(down)} to come up."


def stop_everything() -> str:
    """Take down band 00 and this page, and wait until they are gone.

    Every session's own servers stay up: each session stops its own. This
    page goes last, so it is watching until the end.
    """
    running = ports.held("00")
    running.pop(PORT, 0)
    killed = ports.stop(running)
    # The command that started the band outlives the servers under it. Left
    # alive, it would tell the next start that band 00 is still running.
    band = read_pid(serve.pidfile("band-00"))
    serve.stop("band-00", 0)
    page = serve.holder(PORT)
    if serve.stop(SKILL, PORT):
        killed.append(str(PORT))
    ports.gone([p for p in (*running.values(), band, page) if p], 10)
    if not killed:
        return "Nothing was running."
    return f"{len(killed)} successfully stopped: {', '.join(sorted(killed))}."


# A page's own scripts: each script tag but a JSON one.
SCRIPTS = re.compile(r"<script(?![^>]*application/json)[^>]*>(.*?)</script>", re.S)
# Node compiles each script file it is handed, as node --check would, and
# prints each one failing: its file, its line, and why.
PARSE = r"""
const fs = require('fs'), vm = require('vm');
for (const f of process.argv.slice(1)) {
  try { new vm.Script('(function(){' + fs.readFileSync(f, 'utf8') + '\n})', {filename: f}); }
  catch (e) { console.log(f + '\t' + ((String(e.stack).split('\n')[0].match(/:(\d+)$/) || [])[1] || '?') + '\t' + e.message); }
}
"""


def node() -> str:
    """Node, as this Mac holds it: on the PATH, else nvm's newest. "" with none."""
    found = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/node")))
    return shutil.which("node") or (found[-1] if found else "")


def parsed(drawn: dict) -> None:
    """Every script each drawn page carries, compiled by Node, so a slip
    inside a Python string never blanks a page. One failing raises, naming
    its page, its script and its line. A Mac with no Node checks nothing."""
    runner = node()
    if not runner:
        return
    with tempfile.TemporaryDirectory() as tmp:
        files = {}
        for path, html in drawn.items():
            for i, src in enumerate(SCRIPTS.findall(html)):
                f = os.path.join(tmp, f"{len(files)}.js")
                with open(f, "w") as out:
                    out.write(src)
                files[f] = f"{path} script {i + 1}"
        r = subprocess.run([runner, "-e", PARSE, *files], capture_output=True, text=True, timeout=60)
    bad = [line.split("\t") for line in r.stdout.splitlines() if line.count("\t") == 2]
    if bad:
        f, line, why = bad[0]
        raise SyntaxError(f"{files.get(f, f)}, line {line}: {why}"
                          + (f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""))


def check() -> None:
    """Draw home once, as a fresh 1100 would, then one page of each kind
    home shows now, my own launch page, and every rail page 1100 draws,
    and parse every script they carry. Raises when the code on disk cannot."""
    first = {}
    for p in workstation.model()["pages"].values():
        if not p["port"]:
            first.setdefault(p["kind"], p["path"])
    drawn = {"/": workstation.home()}
    for path in [*first.values(), serve.address("launch", "00"), "/system", "/files", "/skills", "/agenda"]:
        got = route(path)
        if isinstance(got, serve.Typing):
            got = got.outside()
        if isinstance(got, str):
            drawn[path] = got
    parsed(drawn)


def restart() -> str:
    """1100 alone, stopped and started on the code on disk. Band 00 and
    every session's servers stay up.

    The new code draws in a child first, and its pages' scripts parse.
    When it cannot, the running 1100 is never touched, so a broken edit
    never leaves me with no page.
    """
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "check"],
                       capture_output=True, text=True)
    if r.returncode:
        last = (r.stderr.strip().splitlines() or ["it printed nothing"])[-1]
        return f"1100 kept its old code. The new code fails to draw: {last}"
    pid = serve.holder(PORT)
    serve.stop(SKILL, PORT)
    if pid:
        ports.gone([pid], 5)
    if ports.answering(PORT):
        return "1100 did not stop, so nothing changed."
    problem = serve.start(SKILL, PORT, os.path.abspath(__file__))
    return problem or "1100 successfully restarted on the new code."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["serve", "status", "stop", "band", "check", "restart"])
    ap.add_argument("--port", type=int, default=PORT)
    args = ap.parse_args()

    # One project at a time: another project's 1100 and band are never
    # stopped, started over or joined from here.
    refused = project.refusal(PORT) if args.verb in ("band", "stop", "restart") else ""
    if refused:
        print(refused)
    elif args.verb == "check":
        check()
        print("1100's code draws.")
    elif args.verb == "restart":
        print(restart())
    elif args.verb == "serve":
        # A copy tried on a session's own port keeps its pid in that
        # session's server folder, which its stop deletes.
        skill = SKILL if args.port == PORT else f"{SKILL}-{args.port % 100:02d}"
        # A launch runs inside 1100, so it died with the last one, and a
        # row it left booting is failed. My own launch page's rows are
        # 00's, and 00 is no session. A copy on a session's port ran no
        # launch, so it fails none. A driving assistant capped on its own
        # account goes on at the reset, a session done buzzes my phone, a
        # mission's session waiting on me is handed to its assistant, every
        # account is asked for its windows, so is Grok for its own, and
        # band 00's log is kept short. Only 1100 does any.
        if args.port == PORT:
            for nn in [*registry.entries(), "00"]:
                views.launcher.unboot(nn)
            threading.Thread(target=finish.watch, daemon=True).start()
            threading.Thread(target=finish.asking, daemon=True).start()
            threading.Thread(target=engines.asking, daemon=True).start()
            threading.Thread(target=page.reddened, args=([push.buzz(opened), views.assistant.sent],),
                             daemon=True).start()
            threading.Thread(target=serve.keep_short, args=("band-00",), daemon=True).start()
        # iTerm's pane list is read on a thread of its own, so no draw ever
        # waits on iTerm: lib/panes.py's refresher. So are System's ports and
        # database, freshen()'s. A copy runs both too.
        threading.Thread(target=panes.freshen, daemon=True).start()
        threading.Thread(target=freshen, daemon=True).start()
        # A port going up or down is no file: the recheck catches it. A
        # transcript, and the file Files shows, are heard only while a page
        # asks about them. The agenda's
        # folder is heard always, and so are each account's usage and
        # settings.json, and the guard's findings.
        serve.run(skill, args.port, contained(one_list(workstation.home)), take=take,
                  route=contained(one_list(route)), keyof=keyof, raw=raw,
                  hears=lambda: views.heard() + [accounts.FILE, accounts.EFFORT, accounts.MODEL, context.FILE, finish.STATE,
                                                 FINDINGS]
                  + [accounts.settings_file(a) for a in accounts.KNOWN]
                  + transcript.heard() + agenda.heard() + showing())
    elif args.verb == "band":
        print(start_band())
    elif args.verb == "stop":
        print(stop_everything())
    else:
        print(f"http://127.0.0.1:{args.port} — "
              + ("up" if ports.answering(args.port) else "down"))


if __name__ == "__main__":
    main()
