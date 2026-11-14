#!/usr/bin/env python3
"""prototype-page.py — the page 4-prototype draws, beside the prototypes app, 1400.

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
it takes a tab. A new generation, arriving while the page is open, fills
main with its first variation and opens a new round: no pick, Send open
again. Send that landed empties the feedback box.

The top rail holds the family and the session on the left, the subject
and the variation in view in the middle, with the one it grew from, and
the page's two tools together on the right, one width: View all, then
Open alone. Nothing moves when the view does.

1100 draws it at /proto/, the subject and the session in its query, and
passes every variation under /proto/ through to the prototypes app,
code/prototypes/, on 1400.

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

  prototype-page.py shoot          draws the pictures missing

On the contract, lib/live.py's, 1100 draws the page itself, through
drawn, files, taken and LIVE, and 1400 serves the variations alone.

The shell is shared. See .claude/lib/page.py.
It keeps the page rules atop .claude/lib/page.py.
"""

import argparse
import base64
import fcntl
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import reader  # noqa: E402
import registry  # noqa: E402
from prototypes import APP, BASE, PORT, ROUTES, SUBJECT, TAKEN, generations, looks, shelf, subject_file  # noqa: E402


def at(route: str) -> str:
    """A variation's route as the browser asks for it: under BASE. A
    generation's file names it from the app's root, /checkout-page/g3/v1."""
    return BASE.rstrip("/") + route


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
STYLE = "<style>\n" + page.shared("prototype.css") + "</style>\n"


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
    if pick and not m:
        return "That pick names no variation. Nothing was typed."
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
        src = page.esc(at(v["route"]))
        return f'<iframe id="f-{k}" data-src="{src}"></iframe>' if full \
            else f'<iframe src="{src}" loading="lazy" tabindex="-1"></iframe>'
    return f'<div class="stub">Reconstructed from the record — the file is gone.<br>{page.esc(v.get("direction", ""))}</div>'


def block(g: dict) -> str:
    """One generation on the Pick page: a row for its variations, then a row
    per group of looks, each named by its variation. A look with no group
    only shows, on a line of its own. One pick per row. A button carries no
    handler of its own: the page's script hears it."""
    n = g["generation"]
    opts, rest = [], []
    for v in g["variations"]:
        vid, k = page.esc(v["id"]), f"{n}/{page.esc(v['id'])}"
        came = f"← {source(v)} · " if source(v) else ""
        opts.append(f'<button class="opt vo" data-k="{k}">'
                    f'<b>{vid}</b><span class="d">{came}{page.esc(v.get("direction", ""))}</span></button>')
        groups, shown = looks(v)
        for name, found in groups.items():
            gid = page.esc(name)
            chosen = "".join(
                f'<button class="opt lo" data-k="{k}" data-g="{gid}" data-n="{page.esc(l["n"])}">'
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
    """Everything the library draws. Each entry carries its picture's path,
    once drawn, and whether one waits to be drawn."""
    locked, saved = shelf()
    for e in locked + saved:
        path = picture(e)
        e["picture"] = path if path and os.path.exists(path) else ""
        e["waits"] = bool(path) and not e["picture"] and not os.path.exists(path + NONE)
    return {"locked": locked, "saved": saved}


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
                            "--virtual-time-budget=6000", f"--screenshot={raw}", f"http://localhost:{PORT}{at(route)}"],
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


def heard() -> list:
    """Every file and folder whose write can move the library: the app's
    folder, its pictures, the sessions folder, every subject's folder,
    every session's hold, and where sessions start and stop."""
    held = [n for n in registry.listing(registry.WORK) if re.fullmatch(r"\d{2}", n)]
    homes = [os.path.join(APP, s) for s in registry.listing(APP) if generations(os.path.join(APP, s))]
    return ([APP, SHOTS, registry.WORK] + homes + [subject_file(n) for n in held]
            + [os.path.expanduser(f"{base}/sessions") for base in registry.LIVE])


SHELF_STYLE = "<style>\n" + page.shared("prototype-shelf.css") + "</style>\n"


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
    return (f'<a class="card" href="{BASE}?{urllib.parse.urlencode({"subject": e["subject"]})}">'
            f'<div class="thumb">{shown}<span class="chip g" style="--c:var(--grey)">{page.esc(e["shown"])}</span></div>'
            f'<div class="cap"><b>{page.esc(e["subject"])}</b><span>{page.esc(line)}</span></div></a>')


def draw_shelf(d: dict) -> str:
    """The library, from library()'s dict. Every winner under Locked, each
    card naming its session. Every subject saved under Saved, grouped by
    its session, a session unknown last."""
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
            + '</section></div>\n' + page.TABS)
    top = page.head("prototype", "band 00", "Prototypes")
    return page.render("00-prototypes", [("", body)], top, refresh=0)


def missing(d: dict) -> bool:
    """Whether Chrome is here, and library `d` waits on a picture."""
    return os.path.exists(CHROME) and any(e["waits"] for e in d["locked"] + d["saved"])


def shot() -> subprocess.Popen:
    """The job drawing every picture missing, shoot(), started detached."""
    return subprocess.Popen([sys.executable, os.path.abspath(__file__), "shoot"], stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws the page itself, at BASE, beside every variation 1400 still
# serves: lib/live.py. Each change lands part by part, and the feedback box
# keeps my words. The page's own script, .claude/pages/scripts/prototype.js, moves
# about the page, picks and sends. Its data goes as JSON beside it. The
# library's draw starts no program: it says the pictures are wanted, and
# 1100's reader, PICTURES, starts the job. A picture still missing reads
# "Drawing its picture…" until one is drawn.

# What the page tells a press it takes none of.
NO_SUCH = "This page takes no such press. Nothing was typed."
# The picture job this process started last.
JOB: list = [None]


def shooting() -> None:
    """Start the picture job, once a library draw wants it, a picture is
    missing, the app answers, and the job started last has ended."""
    if PICTURES.wanted() and not (JOB[0] and JOB[0].poll() is None) and missing(library()) and ports.answering(PORT):
        JOB[0] = shot()


PICTURES = reader.Reader(shooting)
# What 1100 reads off the draws for this page: lib/reader.py.
READERS = [PICTURES]


def asked(query: str) -> tuple:
    """The subject and the session an address names, as main() reads them:
    a name no subject could take is none, and a session no number, 00."""
    q = urllib.parse.parse_qs(query)
    subject, session = (q.get("subject") or [""])[0], (q.get("session") or [""])[0]
    return (subject if SUBJECT.fullmatch(subject) and subject not in TAKEN else "",
            session if re.fullmatch(r"\d{2}", session) else "00")


def readable(nn: str, subject: str) -> dict:
    """Everything a subject's page draws for session NN, its generations
    read one by one: a file cut short, or not a generation, stands as its
    number alone, unreadable. `live` is the session's word, page.word's."""
    gens = []
    for n, p in generations(os.path.join(APP, subject)):
        try:
            g = load(p)
            if not isinstance(g, dict) or not isinstance(g.get("variations"), list) \
                    or not all(isinstance(v, dict) and v.get("id") for v in g["variations"]):
                raise ValueError(p)
            gens.append({**g, "generation": g.get("generation", n)})
        except (OSError, ValueError):
            gens.append({"generation": n, "variations": [], "unreadable": True})
    return {"nn": nn, "tag": plans.tag(nn) if nn != "00" else "band 00", "subject": subject,
            "generations": gens, "live": page.word(now(nn))}


def now(nn: str):
    """Claude Code's record of session NN as its file reads now, or None
    once its process is gone. registry.claude_records() keeps its answer a
    second, so a draw on a status write could read the status before it:
    which record runs is read from there, its status from its own file."""
    sid = (registry.entries().get(nn) or {}).get("session_id")
    rec = registry.claude_records().get(sid)
    if not rec:
        return None
    for base in registry.LIVE:
        try:
            with open(os.path.join(os.path.expanduser(base), "sessions", f"{rec['pid']}.json")) as f:
                got = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(got, dict) and got.get("sessionId") == sid:
            return got
    return rec


def drawn_page(d: dict) -> str:
    """A subject's page, from readable()'s dict, opened by live.watch(),
    every handler the page's script's. Opened with no session, it only
    shows: Send and the feedback box stay hidden, nothing picks, and a
    button leads back to the library."""
    nn, subject = d["nn"], page.esc(d["subject"])
    gens = [g for g in d["generations"] if g["variations"]]
    shows = nn == "00"
    watch = live.watch((registry.entries().get(nn) or {}).get("session_id", "") if not shows else "")
    off = "" if gens else " disabled"
    back = '<button class="all" id="back">All prototypes</button>' if shows else ""
    top = page.head("prototype", d.get("tag", ""), f'{subject}<span class="now" id="now"></span>',
                    f'{back}<span class="group"><button class="all" id="all"{off}>View all{LIST}</button>'
                    f'<button id="alone"{off}>Open alone ↗</button></span>'
                    f'<button id="send"{" hidden" if shows else off}>Send</button>')
    scripts = page.TABS + f'<script src="{live.src("prototype.js")}"></script>\n'
    if not gens:
        lost = "".join(f'<p class="note">G{page.esc(g["generation"])} is unreadable.</p>' for g in d["generations"])
        return page.render(f"{nn}-prototype", [("", watch + STYLE + page.blank("No generation yet") + lost
                                                 + "\n" + scripts)], top, refresh=0)
    rail = [] if shows else ['<div class="tab pk" data-k="pick" title="Pick">' + CHECK + '</div>']
    rows, items, groups, routes, said = [], [], {}, {}, {}
    for g in reversed(d["generations"]):
        n = page.esc(g["generation"])
        rail.append('<div class="gap"></div>')
        rail.append(f'<div class="lbl">G{n}</div>')
        if g.get("unreadable"):
            rows.append(f'<div class="stage"><h3 class="sub">G{n}</h3>'
                        f'<p class="note">This generation\'s file is unreadable.</p></div>')
            continue
        thumbs = []
        for v in g["variations"]:
            k = f"{n}/{page.esc(v['id'])}"
            pick = "" if shows else '<div class="pick">Pick</div>'
            rail.append(f'<div class="tab g" data-k="{k}" style="--c:var(--grey)">{page.esc(v["id"])}</div>')
            came = source(v)
            if looks(v)[0]:
                groups[f"{g['generation']}/{v['id']}"] = list(looks(v)[0])
            routes[f"{g['generation']}/{v['id']}"] = at(v["route"]) if v.get("real", True) and v.get("route") else ""
            said[f"{g['generation']}/{v['id']}"] = v.get("direction", "")
            tag = f'<span class="chip g src" style="--c:var(--grey)">← {came}</span>' if came else ""
            thumbs.append(f'<div class="card" data-k="{k}">'
                          f'<div class="thumb">{frame(v, k, False)}'
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
    data = json.dumps({"GROUPS": groups, "ROUTES": routes, "DIRECTIONS": said, "BASE": BASE,
                       "FIRST": f"{gens[-1]['generation']}/{gens[-1]['variations'][0]['id']}",
                       "BUSY": d.get("live") == "working"}).replace("</", "<\\/")
    body = (watch + STYLE + f'<div id="items">{"".join(items)}</div>\n' + bar
            + f'<script type="application/json" id="proto">{data}</script>\n' + scripts)
    return page.render(f"{nn}-prototype", [("", body)], top + f'<nav class="nums" id="index">{"".join(rail)}</nav>\n',
                       refresh=0)


def drawn_shelf() -> str:
    """The library, as draw_shelf() draws it, opened by live.watch(). It
    starts no program: it says its pictures are wanted."""
    PICTURES.want()
    body = draw_shelf(library())
    return body.replace(page.TABS, live.watch() + page.TABS, 1)


def drawn(query: str) -> str:
    """The page an address under BASE names: a subject's, or the library."""
    subject, nn = asked(query)
    return drawn_page(readable(nn, subject)) if subject else drawn_shelf()


def files(query: str) -> list:
    """Every file and folder whose write can move the page. A subject's
    page: its folder and each file in it, what registry.watched names for
    the session, and each session's record and plan, which name the tag.
    The library: what heard() names, each subject's files, and the route
    file each picture is named for."""
    subject, nn = asked(query)
    if subject:
        home = os.path.join(APP, subject)
        out = [APP, home] + [os.path.join(home, f) for f in registry.listing(home)] + registry.watched([nn])
        for n in registry.entries():
            own = registry.folder(n)
            out += [os.path.join(own, registry.RECORD), os.path.join(own, plans.PLAN)]
        return list(dict.fromkeys(out))
    out = heard()
    for home in out[3:]:
        if home.startswith(APP + os.sep):
            out += [os.path.join(home, f) for f in registry.listing(home)]
    locked, saved = shelf()
    for e in locked + saved:
        g, _, v = e["shown"].partition("/")
        out.append(os.path.join(ROUTES, e["subject"], g, f"{v}.tsx"))
    return list(dict.fromkeys(out))


def taken(form: dict) -> str:
    """Send, pressed on the contract: take(), for the session the press
    names in its `session` field, since lib/live.py hands a press no
    query. A press naming any other act is refused. The app door's names none."""
    if (form.get("act") or ["send"])[0] != "send":
        return NO_SUCH
    return take(asked(urllib.parse.urlencode({"session": (form.get("session") or [""])[0]}))[1], form)


# The page's contract, lib/live.py's: its address, BASE alone, its query
# naming the subject and the session; its draw, its files, its take.
LIVE = live.Page(re.escape(BASE), drawn, files=files, take=taken, query=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["shoot"])
    ap.parse_args()
    shoot()


if __name__ == "__main__":
    main()
