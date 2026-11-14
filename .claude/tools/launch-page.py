#!/usr/bin/env python3
"""launch-page.py — the page that starts sessions, drawn by 1100 at /p/launch/NN.

A session asked to start others writes their rows to
.claude/state/sessions/NN/launch.json. 1100 hears the file, and shows the
page in the session's hub, a white dot on its number from its session's turn ending, until the rows are gone. A row is one pane. A session row carries a number, name, first message,
account, model and effort, and whether it self-drives: on, its first
message is handed to /self-drive. One cloning a session shows "clone of NN". A browser row carries a site, and shows it: a
port on this machine, or any address. The session writes what I named, and the page fills the rest.
An account, a model or an effort left unnamed takes System's once, when
its row is first saved: the order's next account, and the model and
effort set on 1100/system. From then on, only my press on a pill changes
it. Every group shows its pill picked, a family named, sonnet, its newest
model's. I place each row, and press Launch.

A stage I hand my assistant has its page scheduled: one key more in the
file, after, names the stage whose close fires it. Its button then reads
Schedule, and a press launches nothing. I change any row until
tools/schedule.py fires it, as my press would.

A session that gathers sessions for me sets its page alone: one key
more in the file, "alone": true. Its rows then launch as my own page's
do, naming no session as the one that launched them.

The app door writes its rows on my own page, each carrying by: app.
Its Launch names those rows alone, as only: they launch, and every other
row stays as it is until my own press. A page planning pane moves
refuses it, since those moves wait for my press.

My own page is /p/launch/00, and it is always there. No session is behind
it: band 00 is mine, and no session takes it. Its rows live in
sessions/00/, made with its first row and gone with its last. With none,
one blank session row waits, saved once I change it. It takes the lowest
free side number, 01 first, and lands where lib/launch.py places a row
with no starter.

The map is iTerm's real layout, read through lib/iterm.py. A row lands on
one side of a pane, or of a row before it, or fills a new tab or window.
The map is a section like any other, and scrolls with the page. On my
phone held sideways, it fills the first screen, and the picked row's
lands line and arrows sit beside it; in half my phone, they sit under it,
and the map takes the whole width. The rows follow, without arrows of
their own.

The file's order is launch order. The map can arrange existing and new
panes together; existing panes move only after my Launch press. The cards
never move: each keeps its place, pos, from the moment it arrived.

Launch first holds every row's number, so a launch beside it never takes
one, then opens every pane in launch order, through lib/launch.py, as
tools/launch.py does for a skill. Each session gets its first message once
it has claimed its number. A row leaves the file once its pane is live. The file goes once no row is left, so it
never holds up /9-session-stop, and the page leaves its hub. A row that
fails keeps its pane and its place, and Launch again types there. Each step
goes to a launch log beside the file, and the log goes with the file.

1100 imports this file for its LIVE, lib/live.py's: drawn(), files()
and its take, take_for()'s. A launch runs
as a program of its own, tools/launch.py page NN, so it keeps running
while 1100 restarts. A fresh 1100 leaves a launch whose program runs
alone, and hands one whose program died to a new one: resume. Nothing
here runs a server.
"""

import json
import os
import re
import sys
import traceback

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import live  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import reader  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
# The page's file, and its launch, are lib/launch.py's: a launch runs as a
# program of its own, and a fire and the app door read the same file.
from launch import (AFTER, ALONE, FILE, KEYS, LAYOUTS, LOCK, MINE, MOVES, Locked, Unreadable,  # noqa: E402,F401
                    alone, follow, go, launcher, layout_matches, layout_spec, layouts, load,
                    logfile, made, mark, move_problems, moves, opening, path, put, read, save, scheduled,
                    shape_problems, standing, system, typed, unboot, whole)

# The row my own page waits with while it has none. A browser row on it is
# named 00-browser-K: a stand-in, never ruled.
BLANK = {"uid": 1, "name": "", "message": ""}

# (value, label, shade). One hue per group. A chosen pill is filled with
# its own shade. One account pill per account on this Mac: lib/accounts.py.
ACCOUNTS = [(a, f"claude-{a}", "#a8741c") for a in accounts.KNOWN]
# Each model family's shade, in the order its pill stands. A family
# Claude Code adds stands after them. Stand-in: its shade.
SHADES = {"opus": "#a66bff", "sonnet": "#9273ee", "fable": "#d65cff", "haiku": "#5a4a8c"}
NEW = "#7b5bd0"
EFFORTS = [("low", "low", "#1d5c55"), ("medium", "medium", "#1f857a"),
           ("high", "high", "#1db3a1"), ("xhigh", "xhigh", "#18d9c3"), ("max", "max", "#35ffe8")]


def offered() -> list:
    """The model pills: each family's newest model, as Claude Code's catalog
    holds it now, lib/models.py's. A new model replaces its family's."""
    rank = lambda fm: list(SHADES).index(fm[0]) if fm[0] in SHADES else len(SHADES)
    return [(m, models.name(m), SHADES.get(f, NEW)) for f, m in sorted(models.families(), key=rank)]


def pills(key: str, options: list, on: str, off: str = "") -> str:
    """One group of these pills, drawn on the server for a page that borrows
    them, as the handover page does: `on` picked, `off` disabling each.
    This page draws its own in rows_part()."""
    return (f'<span class="pills" data-k="{key}">' + "".join(
        f'<button type="button" data-v="{page.esc(v)}" class="{"on" if v == on else ""}" '
        f'style="--g:{shade}"{off}>{page.esc(label)}</button>' for v, label, shade in options) + "</span>")

# The layout each page was drawn from, its starter pane and its open
# browsers, by session: a save places its rows against what I saw.
KEPT: dict = {}


# ---- the file: lib/launch.py's --------------------------------------------------

def resume(nn: str) -> None:
    """A fresh 1100 meets a launch left booting. While its program runs, it
    is left alone: 1100 stopping never stopped it. With none running it, as
    when that program was killed, a new one picks it up: lib/launch.py's
    picked_up."""
    if not any(r.get("status") == "booting" for r in read(nn)):
        return
    fd = launch.claim(nn)
    if fd < 0:
        return
    try:
        launch.begin(nn, fd, resume=True)
    except Exception:
        traceback.print_exc()
        unboot(nn)


def free(nn: str, rows: list):
    """The numbers each of session NN's rows may take, by its name, as its
    launcher's own launch would."""
    taken = [r.get("n") for r in rows if not launch.browser(r)]
    return lambda name: launch.free(taken, by=launcher(nn), name=name)


def placed(nn: str, rows: list, fresh: bool = False) -> None:
    """Fill and settle session NN's rows by lib/launch.py's one rule, against
    the layout its page was drawn from. A launch asks iTerm afresh, and so
    does a save no drawn page answers for, as after a restart."""
    if fresh or nn not in KEPT:
        rec = registry.entries().get(nn) or {}
        wins = iterm.tree()
        KEPT[nn] = (wins, panes.pane(rec) if rec else "", launch.browsers_named(nn, wins))
    wins, starter, opened = KEPT[nn]
    launch.fill(rows, free(nn, rows), launch.home(wins, starter), opened, nn)
    launch.settle(rows, wins, starter)


# ---- launching: its run is lib/launch.py's ------------------------------------

def faults(rows: list, going: list) -> list:
    """What stops the launching rows, lib/launch.py's lines, each naming its
    row by its place on the whole page. A line naming no row stops it too."""
    at = {i for i, r in enumerate(rows, 1) if any(r is g for g in going)}
    return [w for w in launch.problems(rows) if not (m := re.match(r"Row (\d+):", w)) or int(m[1]) in at]


def take_for(nn: str, banner: list, run=None):
    """The page's press, answered "" once saved, or launched, or its one
    refusal: rows it cannot read, a file it cannot read, a launch booting,
    or a launch refused, whose words the banner also shows. A Launch naming
    rows as only launches those alone; every other row stays as it is.

    A launch holds the page's lock from before its rows are marked booting,
    then `run` takes it over with the launch: by default lib/launch.py's
    begin(), a program of its own. A fire passes run(), in its own program."""
    def take(form: dict) -> str:
        get = lambda k: (form.get(k) or [""])[0]
        unread = "The page's rows could not be read, so nothing was saved."
        try:
            sent = json.loads(get("rows") or "[]")
            planned = json.loads(get(MOVES)) if get(MOVES) else moves(nn)
            shapes = json.loads(get(LAYOUTS)) if get(LAYOUTS) else layouts(nn)
            only = json.loads(get("only")) if get("only") else None
        except ValueError:
            return unread
        if not isinstance(planned, list) or not isinstance(shapes, list) or not isinstance(only, (list, type(None))):
            return unread
        # A launch whose program died leaves rows booting: a new one picks it up.
        if any(r.get("status") == "booting" for r in read(nn)) and not launch.running(nn):
            resume(nn)
            return "A launch is booting on this page, so nothing was saved."
        fd = -1
        with LOCK:
            try:
                whole(nn)
            except Unreadable:
                return "This page's file cannot be read, so nothing was saved."
            if any(r.get("status") == "booting" for r in load(nn)):
                return "A launch is booting on this page, so nothing was saved."
            rows = [{k: r[k] for k in KEYS if k in r} for r in sent if isinstance(r, dict)]
            # A row the session wrote after the page drew is one the page never
            # saw. It is kept, never overwritten.
            seen = set(json.loads(get("seen") or "[]"))
            on_file = load(nn)
            rows += [r for r in on_file if r["uid"] not in seen]
            # A page never clears a pill. A row sent without an account, model
            # or effort its file holds never saw it, as one saved while I typed.
            held = {r["uid"]: r for r in on_file}
            for r in rows:
                for k in ("account", "model", "effort"):
                    if not r.get(k) and held.get(r.get("uid"), {}).get(k):
                        r[k] = held[r["uid"]][k]
            made(rows)
            # A scheduled page launches only when its fire takes the key out.
            launching = get("act") == "launch" and not scheduled(nn)
            wrong = []
            # A refused launch's sentence stays until the next launch tries.
            if launching:
                banner[0] = ""
            placed(nn, rows, launching)
            if launching:
                going = [r for r in rows if only is None or r["uid"] in only]
                for r in going:
                    r.pop("status", None)
                if only is not None and planned:
                    wrong = ["This page plans pane moves, which wait for its own Launch."]
                elif not going:
                    wrong = ["No row it names is on this page."]
                else:
                    wrong = (faults(rows, going) + move_problems(planned, going, KEPT[nn][0])
                             + shape_problems(planned, shapes, going, KEPT[nn][0]))
                # Each number is held before anything opens, so a launch
                # beside this one picks another. One held elsewhere stops all.
                held = []
                if not wrong:
                    fd = launch.claim(nn)
                    if fd < 0:
                        wrong = ["This page's last launch is still ending. Launch again in a moment."]
                if not wrong:
                    for r in going:
                        if launch.browser(r):
                            continue
                        if not registry.reserve(r["n"]):
                            wrong = [f"{r['n']} is held by another launch."]
                            break
                        held.append(r["n"])
                if wrong:
                    for n in held:
                        registry.release(n)
                    if fd >= 0:
                        os.close(fd)
                    banner[0] = "Nothing launched. " + " ".join(wrong)
                    launching = False
                else:
                    for r in going:
                        r["status"] = "booting"
            save(nn, rows, planned, shapes)
        if launching:
            try:
                (run or launch.begin)(nn, fd)
            except Exception:
                traceback.print_exc()
                unboot(nn, "its launch could not start")
        return banner[0] if wrong else ""
    return take


# ---- the page ---------------------------------------------------------------

CSS = "<style>\n" + page.shared("launch.css") + "</style>"

# The launch page's own. The handover page borrows CSS, never this.
PHONE = "<style>\n" + page.shared("launch-phone.css") + "</style>"


def arrange() -> tuple:
    """iTerm's windows and split trees, each pane named by its session, and
    every running session's number by its pane, as lib/panes.py's numbers()
    answers."""
    records, numbers = registry.entries(), panes.numbers(panes.FRESH)
    held = {at: (k, records.get(k) or {}) for at, k in numbers.items()}

    def mark(n):
        if "split" in n:
            for c in n["children"]:
                mark(c)
            return
        number, rec = held.get(n["pane"], ("", {}))
        label = rec.get("title", "") if number else n.get("name", "")
        if number and label.startswith(number + "-"):
            label = label[len(number) + 1:]
        n.update(number=number, label=label.strip())

    wins = iterm.tree()
    for w in wins:
        for t in w["tabs"]:
            mark(t["root"])
    return wins, numbers


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws every row itself, so a change lands part by part:
# lib/live.py. The page's own script, .claude/pages/scripts/launch.js, draws what
# needs the browser's measure: the map, each row's lands line, the row I
# picked. It saves each change and sends each press.

# iTerm's layout and each session's pane, read on a thread of their own, so
# no draw starts a program: lib/reader.py's Reader. sessions-dashboard.py
# serve starts each page tool's READERS. Until it does, the first draw in a
# server, one whose pane refresher runs, starts it.
ARRANGED = reader.Reader(arrange)
READERS = [ARRANGED]


def arranged() -> tuple:
    """(layout, numbers by pane), as last read. A tool run alone reads now."""
    if panes.REFRESHING[0]:
        ARRANGED.start()
    return ARRANGED.last() or ([], {})


# Each launch page's banner on the contract: the one sentence a refused
# launch leaves, kept until the next launch tries, or its rows are gone.
REFUSALS: dict = {}

PLACE = "#60a5fa"
DRIVE = "#ff6b8b"
UNREAD = "This page's file cannot be read. Nothing on it shows, and nothing is written over it."


def refusal(nn: str) -> list:
    if not read(nn):
        REFUSALS.pop(nn, None)
    return REFUSALS.setdefault(nn, [""])


def said(x) -> str:
    """A value as the browser's String() says it, escaped: none says nothing."""
    return page.esc("" if x is None else "true" if x is True else "false" if x is False else str(x))


def news(keys) -> list:
    """The new windows or tabs rows open, N1, N2…, in their order."""
    num = lambda k: int(k[1:]) if k[1:].isdigit() else 0
    return sorted({k for k in keys if isinstance(k, str) and k[:1] == "N"}, key=num)


def rows_part(d: dict) -> str:
    """Every row, in the order the cards stand: pos. What needs the browser's measure stays empty for the
    page's script: each lands line, and the row I picked."""
    rows, wins, busy = d["rows"], d["layout"], d["busy"]
    off = " disabled" if busy else ""
    web = launch.browser
    live_win = lambda k: next((w for w in wins if f"L:{w['window']}" == k), None)
    index = lambda xs, x: xs.index(x) if x in xs else -1

    def tabs_of(win: str) -> list:
        w = live_win(win)
        return ([f"L:{t['tab']}" for t in w["tabs"]] if w else []) + news(r.get("tab") for r in rows if r.get("win") == win)

    def win_label(k: str) -> str:
        w = live_win(k)
        return (f"window {wins.index(w) + 1}" if w
                else f"window {len(wins) + index(news(r.get('win') for r in rows), k) + 1} · new")

    def tab_label(win: str, k: str) -> str:
        w = live_win(win)
        t = next((t for t in w["tabs"] if f"L:{t['tab']}" == k), None) if w else None
        if t:
            return f"tab {w['tabs'].index(t) + 1}"
        return f"tab {(len(w['tabs']) if w else 0) + index(news(r.get('tab') for r in rows if r.get('win') == win), k) + 1} · new"

    def pills(r: dict, key: str, options: list, now: str, tip: str) -> str:
        held = now if r.get(key) in (None, "") else str(r[key])
        on = d["families"][held] if key == "model" and held in d["families"] else held
        return "".join(f'<button class="{"on" if on == v else ""}" style="--g:{shade}"{off}'
                       + (f' title="{tip}"' if v == now else "")
                       + f' data-pill="{key}" data-v="{page.esc(v)}">{page.esc(label)}</button>'
                       for v, label, shade in options)

    def turn(i: int) -> str:
        k = sum(1 for r in rows[:i] if not web(r) and not r.get("account"))
        o = d["order"].get("order") or []
        return o[(d["order"].get("next", 0) + k) % len(o)] if o else d["fallback"]

    def place_pills(r: dict) -> str:
        win = r.get("win")
        ws = "".join(f'<button class="{"on" if win == k else ""}" style="--g:{PLACE}"{off} data-win="{page.esc(k)}">'
                     f'{page.esc(win_label(k))}</button>'
                     for k in [f"L:{w['window']}" for w in wins] + news(s.get("win") for s in rows))
        ws += f'<button class="new" style="--g:{PLACE}"{off} data-win="">+ new window</button>'
        ts = "".join(f'<button class="{"on" if r.get("tab") == k else ""}" style="--g:{PLACE}"{off} data-tab="{page.esc(k)}">'
                     f'{page.esc(tab_label(win, k))}</button>' for k in tabs_of(win))
        ts += f'<button class="new" style="--g:{PLACE}"{off} data-tab="">+ new tab</button>'
        still = " disabled" if busy or not r.get("at") else ""
        pad = "".join(f'<button{still} data-d="{d_}">{a}</button>'
                      for d_, a in (("left", "←"), ("up", "↑"), ("down", "↓"), ("right", "→")))
        return (f'<span class="grp"><span class="lbl place">window</span><span class="pills">{ws}</span></span>'
                f'<span class="grp"><span class="lbl place">tab</span><span class="pills">{ts}</span></span>'
                f'<span class="grp move"><span class="lbl place">move</span><span class="pad">{pad}</span></span>')

    def card(i: int) -> str:
        r, u = rows[i], said(rows[i]["uid"])
        failed = str(r.get("status") or "").startswith("failed")
        cls = " busy" if r.get("status") == "booting" else " failed" if failed else ""
        state = "booting…" if r.get("status") == "booting" else str(r["status"]) if failed else ""
        tail = (f'<span class="lbl">lands</span><span class="lands"></span><span class="state">{page.esc(state)}</span>'
                f'<button class="x"{off} title="remove this row" data-drop="">×</button>')
        box = lambda cls_, f, name: (f'<input class="{cls_}" type="text" id="{name}-{u}" data-f="{f}" '
                                     f'value="{said(r.get(f))}"{off}')
        head = f'<div class="row{cls}" id="row-{u}" data-uid="{u}"><div class="line">'
        if web(r):
            return (head + '<span class="grp"><span class="lbl place">browser site</span>'
                    + box("site", "site", "site") + ' placeholder="7204, or any address"></span>'
                    + box("words", "name", "name") + ">" + tail + "</div>"
                    + f'<div class="line" style="margin:4px 0 0">{place_pills(r)}</div></div>')
        system = d["system"]
        return (head + box("num", "n", "n") + ">" + box("words", "name", "name") + ">" + tail + "</div>"
                + f'<textarea id="msg-{u}" data-f="message"{off} placeholder="The first message it receives.">'
                + said(r.get("message")) + "</textarea>"
                + '<div class="line" style="margin:4px 0 0">'
                + '<span class="grp"><span class="lbl acct">account</span><span class="pills">'
                + pills(r, "account", d["accounts"], turn(i), "The next account in the order set on 1100/system")
                + '</span></span><span class="grp"><span class="lbl model">model</span><span class="pills">'
                + pills(r, "model", d["models"], system["model"], "The model set on 1100/system")
                + '</span></span><span class="grp"><span class="lbl effort">effort</span><span class="pills">'
                + pills(r, "effort", d["efforts"], system["effort"], "The effort set on 1100/system")
                + '</span></span><span class="grp"><span class="lbl drive">drive</span><span class="pills">'
                + f'<button class="{"on" if r.get("drive") else ""}" style="--g:{DRIVE}"{off} '
                  'title="It takes the work to its end, then stops itself" data-pill="drive">self-drive</button>'
                + '</span></span>'
                + (f'<span class="grp"><span class="lbl drive">clone of {page.esc(str(r["clone"]))}</span></span>'
                   if r.get("clone") else "")
                + '</div>'
                + f'<div class="line" style="margin:4px 0 0">{place_pills(r)}</div></div>')

    pos = lambda i: rows[i].get("pos") if isinstance(rows[i].get("pos"), (int, float)) else 0
    order = sorted(range(len(rows)), key=pos)
    return "".join(map(card, order)) if rows else '<div class="empty"><p>No row waits</p></div>'


def drawn(nn: str) -> str:
    """Session NN's launch page, every row drawn, 00 being my own. The rows,
    the layout and what picks each pill go as data beside them, for the
    page's own script. A row the session wrote with no uid shows with the
    one its first save gives it: a draw never writes."""
    mine = nn == MINE
    rec = registry.entries().get(nn) or {}
    try:
        whole(nn)
        unread = False
    except Unreadable:
        unread = True
    rows = [] if unread else read(nn)
    launch.numbered(rows)
    if mine and not rows and not unread:
        rows = [dict(BLANK)]
    wins, numbers = arranged()
    starter = next((p for p, n in numbers.items() if n == nn), rec.get("pane", "")) if rec else ""
    KEPT[nn] = (wins, starter, launch.browsers_named(nn, wins))
    busy = any(r.get("status") == "booting" for r in rows)
    if not busy:
        placed(nn, rows)
    after, banner = scheduled(nn), refusal(nn)
    data = {"layout": wins, "rows": rows, "moves": moves(nn), "starter": starter, "accounts": ACCOUNTS,
            "order": accounts.read(), "fallback": accounts.FALLBACK, "nn": nn, "system": launch.default(),
            "models": offered(), "families": dict(models.families()), "efforts": EFFORTS, "after": after}
    count = lambda k, word: f"{k} {word}{'' if k == 1 else 's'}" if k else ""
    sessions = sum(1 for r in rows if not launch.browser(r))
    tip = (f"Launches once stage {after} closes" if after
           else ", ".join(x for x in (count(sessions, "session"), count(len(rows) - sessions, "browser")) if x))
    body = (live.watch(rec.get("session_id", "")) + CSS + PHONE
            + (f'<div class="banner">{page.esc(UNREAD)}</div>' if unread else "")
            + (f'<div class="banner">{page.esc(banner[0])}</div>' if banner[0] else "")
            + '<div class="banner" id="save-error" hidden>Changes could not be saved. '
              '<button type="button" id="retry">Retry save</button></div>'
            + '<div class="banner" id="launch-error" hidden>Launch could not be confirmed. '
              'Check your sessions before trying again.</div>'
            + '<div class="preview"><h2>Where sessions will land</h2><div id="map"></div></div>'
            + '<h2>Rows</h2><div id="rows">'
            + live.part("The rows", rows_part, {**data, "busy": busy}) + '</div>\n'
            + '<script type="application/json" id="launch-data">' + json.dumps(data).replace("</", "<\\/")
            + '</script>\n'
            + page.TABS + f'<script src="{live.src("launch.js")}"></script>\n')
    # The top rail holds the family and the session that brought me,
    # then the three buttons together. Nothing else. There is no left rail.
    # My own page has no session to name.
    off = " disabled" if busy else ""
    rail = page.head("launch", "" if mine else plans.tag(nn), "",
                     f'<span class="group"><button class="minor" id="add"{off}>+ session</button>'
                     f'<button class="minor" id="addweb"{off}>+ browser</button>'
                     f'<button id="launch"{" disabled" if busy or not rows or after else ""} title="{page.esc(tip)}">'
                     + ("Launching…" if busy else f"{'Schedule' if after else 'Launch'} · {len(rows)}")
                     + "</button></span>")
    return page.render("launch" if mine else f"{nn}-launch", [("", body)], rail, refresh=0)


def files(nn: str) -> list:
    """Every file whose write can move session NN's page: its file, by its
    folder, which may come later; every session's record and Claude Code's
    own, which free a number and name a pane; the account order; and the
    model and effort set on System, with the models offered."""
    out = registry.watched([nn]) + [path(nn)]
    out += [os.path.join(registry.folder(n), registry.RECORD) for n in registry.entries()]
    return out + [accounts.FILE, accounts.MODEL, accounts.EFFORT, models.FILE]


def pressed(nn: str, form: dict) -> str:
    """A press on the page on the contract: a save, or a Launch, as
    take_for()'s take takes it. Any other act is refused. Its own name is
    not take: tools/app-door-test.py reads the first take here as the page's."""
    if (form.get("act") or [""])[0] not in ("save", "launch"):
        return "This page takes no such press. Nothing was saved."
    return take_for(nn, refusal(nn))(form) or ""


# The page's contract, lib/live.py's: its address, its draw, its files, the
# layout no file carries, and its take.
LIVE = live.Page(serve.address("launch", r"(\d{2})"), drawn, files=files, looks=(arranged,), take=pressed)
