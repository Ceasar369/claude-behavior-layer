#!/usr/bin/env python3
"""walk-shots-page.py — a session's Screenshots tab: every screenshot its walk keeps, in order.

A walker saves each check's screenshots beside the page's text, in its
own folder: walk/<area>/<section>/<journey>/<number>.png, the number its
checklist's # column, like 14. A check saved more than once ends each
save -1, -2, and on. Its time is the file's own. The tab shows the
session's own walk/ alone. A walker clears its walk/ before it walks a
journey, so the tab holds that journey alone.

The rail names each journey by its file's title, then holds one box per
screenshot, one under the other, in walked order, by time, each reading
its file's name: 19, or 40-1, 40-2. It is as wide as the widest name a
walk makes, 190-21. The box in view wears an outline. A screenshot the
lead's case names under its Issues, the case written after it, wears red,
the page's only colour. Back, Play, Next and Speed walk them; left and
right step, space plays. The screenshot fills the width beside the rail,
its shape kept, and a taller one scrolls down, from its top on each new
one. On my phone held upright, it takes three quarters of the glass under
the top rail, and the journeys the rest, each scrolling on its own. Its
name and place show in the top rail.

The lead's cases are .claude/state/walk-case/<walker>-….md, outside every
session's folder. The lead is walk.json's "main".

1100 imports this file for answer, tab and heard: the tab shows once a
session holds a screenshot, and never waits on me. On the contract,
lib/live.py's, it draws through drawn, files and LIVE.

Each screenshot is {j, journey, name, time, at, file, rep}: j its folder
under walk/, journey that journey's title, name the file's without .png,
file an absolute path.
"""

import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

WALK = "walk"
CASES = os.path.join(registry.ROOT, ".claude", "state", "walk-case")
SHOT = re.compile(r"\d+[A-Z]*(?:-[\w-]+)?\.png")
# A screenshot a case names, its path under the walker's walk/ folder.
NAMED = re.compile(r"[\w-]+/[\w-]+/[\w-]+/\d+[A-Z]*(?:-[\w-]+)?\.png")
SPEEDS = [1, 1.5, 2, 3]
BASE = 1500


# ---- what the walk left -----------------------------------------------------------

def read(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def sources(nn: str) -> list:
    """The walk session NN's tab draws, as [(walker, its walk folder, its
    main)], or [] with none."""
    mine = registry.folder(nn)
    if not os.path.isdir(os.path.join(mine, WALK)):
        return []
    return [(nn, os.path.join(mine, WALK), read(os.path.join(mine, "walk.json")).get("main", ""))]


def reported(walker: str) -> dict:
    """Each screenshot the cases about this walker name under Issues, with
    the newest such case's time: a case older than a screenshot judged an
    earlier pass, and dots nothing."""
    out = {}
    for name in registry.listing(CASES):
        if not (name.startswith(f"{walker}-") and name.endswith(".md")):
            continue
        path = os.path.join(CASES, name)
        try:
            at = os.path.getmtime(path)
            with open(path) as f:
                text = f.read()
        except OSError:
            continue
        for part in re.split(r"(?m)^## ", text):
            if part.startswith("Issues"):
                for shot in NAMED.findall(part):
                    out[shot] = max(at, out.get(shot, 0))
    return out


def title(area: str, section: str, journey: str) -> str:
    """A journey's title, its file's first line, walks/<area>/<section>/<journey>.md.
    No such file, its folder's name."""
    try:
        with open(os.path.join(registry.ROOT, "walks", area, section, journey + ".md")) as f:
            first = f.readline()
    except OSError:
        first = ""
    return first[2:].strip() if first.startswith("# ") else journey.replace("-", " ").capitalize()


def shots(nn: str) -> list:
    """Every screenshot session NN's tab draws, journey by journey, each
    journey's in walked order, journeys by their first screenshot."""
    out = []
    for walker, base, main in sources(nn):
        dots = reported(walker) if main else {}
        for here in glob.glob(os.path.join(base, "*", "*", "*", "")):
            j = os.path.relpath(here, base)
            journey, got = title(*j.split(os.sep)), []
            for name in registry.listing(here):
                if SHOT.fullmatch(name):
                    file = os.path.join(here, name)
                    try:
                        at = os.path.getmtime(file)
                    except OSError:
                        continue
                    got.append({"j": j, "journey": journey, "name": name[:-4],
                                "time": time.strftime("%H:%M:%S", time.localtime(at)),
                                "at": at, "file": file,
                                "rep": dots.get(os.path.relpath(file, base), 0) > at})
            got.sort(key=lambda s: (s["at"], s["file"]))
            if got:
                out.append(got)
    out.sort(key=lambda g: g[0]["at"])
    return [s for g in out for s in g]


def world(nn: str) -> dict:
    """Everything the tab draws for session NN: its tag and its screenshots."""
    return {"nn": nn, "tag": plans.tag(nn, plans.owners(registry.entries())), "shots": shots(nn)}


# ---- the page -----------------------------------------------------------------------

# The prototype's own rules, after the shell's: screenshots-tab g5/v1.
CSS = "<style>\n" + page.shared("walk-shots.css") + "</style>"

def picture(d: dict, k: str):
    """Screenshot K of the tab, as its bytes and their type."""
    s = d["shots"]
    if not k.isdigit() or int(k) >= len(s):
        return b"", "text/plain; charset=utf-8"
    try:
        with open(s[int(k)]["file"], "rb") as f:
            return f.read(), "image/png"
    except OSError:
        return b"", "text/plain; charset=utf-8"


def answer(nn: str, rest: str):
    """One screenshot of the tab: /pic/K."""
    if m := re.fullmatch(r"/pic/(\d+)", rest):
        return picture(world(nn), m.group(1))
    return None


def tab(nn: str):
    """Session NN's tab, as (its line, the file it began with), or None
    with no screenshot. Its line is the newest journey and the count."""
    s = shots(nn)
    if not s:
        return None
    first = min(s, key=lambda x: os.path.getmtime(x["file"]) if os.path.exists(x["file"]) else 0)
    return f"{s[-1]['journey']} · {len(s)}", first["file"]


def heard() -> list:
    """What 1100 hears for every session's tab: each walk folder, down to
    its journeys, and the cases folder once a walk names its main."""
    out, mains = [], False
    for nn in registry.listing(registry.WORK):
        if not re.fullmatch(r"\d{2}", nn):
            continue
        for _, base, main in sources(nn):
            out.append(base)
            for section in registry.listing(base):
                out.append(os.path.join(base, section))
                out += [os.path.join(base, section, j) for j in registry.listing(os.path.join(base, section))]
            mains = mains or bool(main)
    return out + [CASES] if mains else out


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws the rail itself, so a new screenshot lands part by part:
# lib/live.py. The screenshots go as
# data beside it, and the page's own script, .claude/pages/scripts/walk-shots.js,
# walks them. Each screenshot's bytes still ride on answer()'s /pic/K.

def drawn(nn: str) -> str:
    """Session NN's Screenshots tab, on the contract."""
    d, e = world(nn), page.esc
    s = d["shots"]
    watch = live.watch((registry.entries().get(nn) or {}).get("session_id", ""))
    # The same script with no screenshot at all, so the first one arriving reloads nothing.
    script = f'<script src="{live.src("walk-shots.js")}"></script>\n'
    if not s:
        top = page.head("shots", d["tag"], "0 of 0")
        return page.render(f"{nn}-shots", [("", watch + page.blank("No screenshot yet") + script)],
                           top + "<aside></aside>\n", refresh=0)
    acts = ('<span class="group"><button class="btn" id="back">Back</button>'
            '<button class="btn" id="play">Play</button>'
            '<button class="btn" id="next">Next</button>'
            '<button class="btn" id="speed" title="Speed">1×</button></span>')
    top = page.head("shots", d["tag"], '<span id="mid"></span>', acts)
    rail = ""
    for i, x in enumerate(s):
        if not i or s[i - 1]["j"] != x["j"]:
            rail += f'<h2 class="ws-j">{e(x["journey"])}</h2>'
        rail += (f'<div class="tab ws-row" data-i="{i}"' + (' style="--c:var(--red)"' if x["rep"] else "")
                 + f'>{e(x["name"])}</div>')
    data = json.dumps({"shots": [{k: x[k] for k in ("j", "journey", "name", "time")} for x in s],
                       "speeds": SPEEDS, "base": BASE, "pic": serve.address("shots", nn) + "/pic"}).replace("</", "<\\/")
    body = (watch + CSS + '<div class="ws-view" id="view"><img class="ws-shot" id="shot" alt=""></div>'
            + f'<script type="application/json" id="shots">{data}</script>\n' + script)
    return page.render(f"{nn}-shots", [("", body)], top + f'<aside id="rail">{rail}</aside>\n', refresh=0)


def files(nn: str) -> list:
    """Every file and folder whose write can move session NN's tab: its
    folder, where walk/ and walk.json come later, walk.json itself, walk/
    down to each journey's folder, the journeys' own files in walks/, which
    title them, the cases folder, and each session's record and plan,
    which name the tag."""
    mine = registry.folder(nn)
    out = [registry.WORK, mine, os.path.join(mine, "walk.json"), CASES]
    for _, base, _ in sources(nn):
        out.append(base)
        for area in registry.listing(base):
            out.append(os.path.join(base, area))
            for section in registry.listing(os.path.join(base, area)):
                out += [os.path.join(base, area, section), os.path.join(registry.ROOT, "walks", area, section)]
                out += [os.path.join(base, area, section, j) for j in registry.listing(os.path.join(base, area, section))]
    for n in registry.entries():
        own = registry.folder(n)
        out += [os.path.join(own, registry.RECORD), os.path.join(own, plans.PLAN)]
    return list(dict.fromkeys(out))


# The tab's contract, lib/live.py's: its address, its draw, its files. It
# takes no press. /pic/K is no Page: each screenshot's bytes would be kept
# in the table's memory, so it rides on answer().
LIVE = live.Page(serve.address("shots", r"(\d{2})"), drawn, files=files)
