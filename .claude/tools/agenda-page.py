#!/usr/bin/env python3
"""agenda-page.py — my agenda, drawn on 1100/agenda.

Its folder, .claude/state/agenda/, holds one file per item, each naming
its topics. This page draws them as one chart, read from left
to right: the topics' rectangles down the first column, in their
order, then the items waiting on nothing, each linked to the rectangle of
every topic it sits under, then what waits on them, each one column past
the furthest item it waits on. An item under two topics is one item, a line in
from each rectangle. An item waiting on other items has no line from a
rectangle.
An agenda split into phases draws one such chart per phase, each with its
own rectangles, under its heading, as "Phase 1: Launch", the next
phase's below it.
No line joins two of them.
It opens left to right at every width, a phone's too. Flipped, it reads
from top to bottom, the rectangles side by side, and each device keeps the
way I last flipped it to.

The page wears the top rail every page does, on top whichever way the
chart flows. Its middle counts every item, then Mine, its number red, each
a button opening its list at the right, where a note opens. Then the
orders, how many columns of items there are, and a chip for each, and All.
A chip shows that order's items alone, their names and marks with them;
every line stays, and the chart never moves. Its tools sit together at
its right: a search, the zoom tools every chart wears, and the flip. The
search finds titles and notes as I type, and its hits fill the same list,
a title's before a note's. A list opens straight on its rows, with no
head. A row's click opens its item's note, as a click on the chart does.
Each row, and each item a note lists, wears its item's colour. Narrower than
1060, the counts lead the first line, and the search and the zoom tools end
it while they fit; what does not fit takes the next line. The orders take a
row of their own.

The chart is placed by the page itself, in the browser: each column's
order crosses as few lines as it can find, and each item sits between the
items it hangs on. The rectangles keep
their order, and a line from one to an item weighs a thousand crossings in
the search, so the items out of a rectangle stay beside it. The rectangles
stand the same distance apart, whatever their items. Lines bend only between
columns, so none crosses a name. The browser keeps the order it found
with the agenda's shape, so the same shape opens at once. Each topic wears
its own colour, lib/agenda.py's. An item waiting on nothing takes the
even mix of its topics' colours; any other the mix of what it waits on,
darker a column further out.

A click on an item opens its note, at the right, or over the chart on a
phone. An item whose note carries a Mine line wears a small red mark at its top right.
The note holds
Start: pressed, a session opens on its item, through tools/launch.py, its
first message the item, in my words.

A write into the folder is heard, and the page draws itself again in
place: its counts move, and its way, its size, its spot, its chip and an
open note or list stay. 1100 serves it at /agenda. FOLDER is the folder
it draws: a test points it at a copy.

The dashboard's server serves it. Imported, never run.
"""

import json
import os
import subprocess
import sys
import threading

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import agenda  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import live  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

HERE =os.path.dirname(os.path.abspath(__file__))
FOLDER = agenda.FOLDER
LAUNCH = os.path.join(HERE, "launch.py")

STYLE = "<style>\n" + page.shared("agenda.css") + "</style>\n"

# The order chips wear the launch page's pills. The page's own sizes come
# after.
PILLS = page.rules(page.tool("launch-page").CSS, ".pills")

BODY = ('<div class="ag" id="ag"><div class="sc" id="sc"></div>'
        '<aside class="note" id="note" hidden></aside><p class="bad" id="bad" hidden></p></div>')

# Lucide's arrow-up-down and arrow-left-right: what a press of the flip
# button turns the chart to.
FLIP_V = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21 16-4 4-4-4"/>'
          '<path d="M17 20V4"/><path d="m3 8 4-4 4 4"/><path d="M7 4v16"/></svg>')
FLIP_H = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3 4 7l4 4"/>'
          '<path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>')

# The top rail's tools, together at its right: the search, then the zoom
# tools every chart wears and the flip, which never part. Its middle holds
# the counts, drawn by the page.
TOOLS = (f'<label class="find">{page.icon("search", 14)}<input id="q" spellcheck="false" autocomplete="off" '
         'aria-label="Find an item by its title or its note" placeholder="Find: a title, a note"></label>'
         '<span class="tl">' + page.ZOOM_TOOLS
         + '<button type="button" class="flip" id="flip" aria-label="Flip"></button></span>')


def mine(note: str) -> str:
    """The note's Mine line, its words alone, or "" when it carries none."""
    return next((text for name, text in agenda.note_lines(note) if name == "Mine"), "")


def world() -> dict:
    """What the folder holds, as the page draws it: the topics and the
    phases, then each item with its Mine line. It never raises: a folder
    that cannot be read draws as the empty start, so 1100 always draws."""
    try:
        d = agenda.world(FOLDER)
    except Exception:
        d = {"items": [], "broken": []}
    for it in d["items"]:
        it["mine"] = mine(it["note"])
    return {"topics": [{"name": name, "colour": colour} for name, colour in agenda.TOPICS],
            "phases": list(agenda.PHASES), "headings": agenda.HEADINGS, **d, "live": True}


def start(item: str) -> str:
    """A session opens on the item, through tools/launch.py, right of window
    1's last pane, its first message the item, handed over in my words. The
    answer waits for the pane alone: the session claims its number on its
    own.

    The press is mine, so no session launched it. A server started from a
    session's shell carries that session's process and pane in its
    environment, and launch.py would name it the caller: both are left out."""
    items, _ = agenda.read(FOLDER)
    try:
        i = agenda.find(items, item)
    except agenda.Refused as e:
        return str(e)
    tabs = [launch.leaves(t["root"]) for w in iterm.tree() for t in w["tabs"]]
    if not tabs:
        return "iTerm did not answer, so no session started."
    mine = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PID", "ITERM_SESSION_ID")}
    where = os.path.relpath(os.path.join(FOLDER, f"{i}.md"), registry.ROOT)
    run = subprocess.Popen([sys.executable, LAUNCH, "session", "--name", items[i]["title"],
                            "--message", f"There's this agenda item I'd like to look at: {items[i]['title']}, in {where}.",
                            "--from", tabs[0][-1], "--where", "right"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, start_new_session=True, env=mine)
    if not run.stdout.readline():
        return run.communicate()[1].strip() or "The session did not start."
    threading.Thread(target=run.communicate, daemon=True).start()
    return ""


def take(form: dict):
    """Start pressed on an item's note. A refusal comes back as its sentence,
    and the page shows it. The start waits on iTerm and the new pane, so it
    runs off 1100's draw queue: serve.Typing."""
    if "start" not in form:
        return ""
    item = (form.get("start") or [""])[0]
    return serve.Typing(lambda: start(item))


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws the frame and hands the agenda over as data. The page's own
# script, .claude/pages/scripts/agenda.js, draws the chart from it, and draws it
# again in place each time 1100 puts new data in place: lib/live.py.

# The flip's two pictures and the close button's, as the page's script reads them.
ICONS = json.dumps({"flipV": FLIP_V, "flipH": FLIP_H, "close": page.icon("close", 15)}).replace("</", "<\\/")
# The search keeps no words past a reload.
FIND = TOOLS.replace('<input id="q"', '<input id="q" data-draft="no"', 1)


def drawn() -> str:
    """The agenda page: its frame, and what the folder holds as data."""
    data = json.dumps(world(), ensure_ascii=False).replace("</", "<\\/")
    body = (live.watch() + PILLS + STYLE + BODY + f'<script type="application/json" id="data">{data}</script>'
            + f'<script type="application/json" id="icons">{ICONS}</script>'
            + page.ZOOM + f'<script src="{live.src("agenda.js")}"></script>\n')
    return page.render("00-agenda", [("", body)], page.head("agenda", "", "", FIND), refresh=0)


def files() -> list:
    """The folder, and each item in it: a write into any moves the page. An
    item added later is heard by the folder."""
    try:
        names = sorted(n for n in os.listdir(FOLDER) if n.endswith(".md"))
    except OSError:
        names = []
    return [FOLDER, *(os.path.join(FOLDER, n) for n in names)]


def pressed(form: dict):
    """A press on the contract: Start, as take() answers it. Any other is
    refused in a sentence."""
    if "start" not in form:
        return "This page takes no such press. Nothing was started."
    return take(form)


# The page's contract, lib/live.py's: its address, its draw, its files, its take.
LIVE = live.Page(r"/agenda", drawn, files=files, take=pressed)
