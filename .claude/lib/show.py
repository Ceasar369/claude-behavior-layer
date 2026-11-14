#!/usr/bin/env python3
"""show.py — the orders telling each open app home what to show.

An app home is 1100 opened as /?app, view 1, or /?app=2, view 2, up to 99:
one per app chat. 1100 counts the homes asking for each view right now,
homes(), so a chat hears when another panel already holds its view. A tool, as the app door, calls show(target, view=N).
Each view has its own order file, which 1100 hears: order.json for view
1, order-N.json past it. A home asks /show?view=N, and acts once its
order is newer than the last it acted on, or than its own load. So one
chat's order never moves another chat's view.

An order that stays switches no page: it only fills or borders a spot in
its page, where that page stands. It names no view. It is one file,
stay.json, every view reads: a box belongs to its session. Both the
caller and 1100 read this module, so each order is a file both know.

A target is a rail tool, a session's number, or a number and one of its
tab kinds: "agenda", "05", "05:clarify". A place, when given, opens one
item inside that page.

Imported, never run.
"""

import glob
import json
import os
import re
import time

import launch
import page
import registry

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOLDER = os.path.join(ROOT, ".claude", "state", "show")
ORDER = os.path.join(FOLDER, "order.json")
# The rail's tools, as home's TOOLS names them.
TOOLS = ("skills", "system", "agenda", "launch", "prototypes", "files", "library")
# A session's tab kinds, and its team tab.
KINDS = (*page.TAB_KINDS, "assistant")
TARGET = re.compile(r"(\d{2})(?::([a-z]+))?")
# A view's number, 1 to 99: each one app chat's own home.
VIEW = re.compile(r"[1-9]\d?")
NO_VIEW = "Name your view, like 1: the number in the address you opened. ?app is 1, ?app=2 is 2."
# The app homes asking for their view's order right now, by (view, home):
# when each last asked. Only 1100's own process holds it, in memory, so a
# closed panel leaves no mark: it stops asking, and is gone OPEN seconds on.
HOMES = {}
# 1100 reads a held home's order again every few seconds, serve.run's recheck.
OPEN = 8


def viewed(view) -> str:
    """A view's number as its files name it, or "" when it is none."""
    view = str(view).strip()
    return view if VIEW.fullmatch(view) else ""


def asked(view, home: str) -> None:
    """One app home, by the name it gave itself at load, asks for its
    view's order: 1100 says so each time it reads that home's key."""
    if viewed(view) and home:
        HOMES[(viewed(view), home)] = time.time()


def homes() -> dict:
    """How many app homes hold each view right now: {"2": 2}."""
    now, out = time.time(), {}
    for (view, home), at in list(HOMES.items()):
        if now - at > OPEN:
            HOMES.pop((view, home), None)
        else:
            out[view] = out.get(view, 0) + 1
    return out


def already(view, count: int) -> str:
    """What a chat is told once more than one panel holds its view."""
    return f"View {view} is already open." if count > 1 else ""


def path(view: str) -> str:
    """One view's order file, beside ORDER, which is view 1's."""
    return ORDER if view == "1" else os.path.join(os.path.dirname(ORDER), f"order-{view}.json")


def stays() -> str:
    """The order that stays, which every view reads."""
    return os.path.join(os.path.dirname(ORDER), "stay.json")


def _order(file: str) -> dict:
    try:
        with open(file) as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {}
    except (OSError, ValueError):
        return {}


def _at(order: dict) -> int:
    try:
        return int(order.get("at", 0) or 0)
    except (TypeError, ValueError):
        return 0


def read(view="1") -> dict:
    """The last order one view acts on: its own, or the one that stays,
    whichever is newer. An empty one before any, or for no view."""
    view = viewed(view)
    return max(_order(path(view)), _order(stays()), key=_at) if view else {}


def key(view="1") -> str:
    """One view's last order's stamp, as a page's key: it moves with each order."""
    return str(_at(read(view)))


def last() -> int:
    """The newest stamp of any order, every view's and the one that stays."""
    folder = os.path.dirname(ORDER)
    return max((_at(_order(f)) for f in (ORDER, stays(), *glob.glob(os.path.join(folder, "order-*.json")))),
               default=0)


def refused(target: str) -> str:
    """Why a target cannot be shown, or "" when it can."""
    if target in TOOLS:
        return ""
    m = TARGET.fullmatch(target)
    if not m:
        return (f"{target!r} is no page: name a tool ({', '.join(TOOLS)}), "
                "a session's number, or a number and a tab, as 05:clarify.")
    nn, kind = m.groups()
    if kind and kind not in KINDS:
        return f"{kind!r} is no tab: a tab is one of {', '.join(KINDS)}."
    if nn not in launch.live():
        return f"Session {nn} is not running."
    return ""


def show(target: str, place: str = "", draft: str = "", mark: str = "", stay: bool = False, view="") -> str:
    """Order the home of `view` to show `target`, and inside it `place`, the
    end of the page's address naming one item: "#api-key", "?run=…",
    "/name". The caller makes it. A draft, on a session's transcript tab,
    fills its box, unsent. A mark, a CSS selector inside the page, is the
    spot the app chat just changed: frame.js borders it for a moment. With
    `stay`, no home moves and no view is named: the draft and the mark
    wait in that page, in every view, seen whenever I open it. One
    sentence: what it shows, or why it cannot. Each order's stamp, in
    milliseconds, is past every other's."""
    target = str(target).strip().lower()
    view = viewed(view)
    if not stay and not view:
        return NO_VIEW
    if why := refused(target):
        return why
    at = max(int(time.time() * 1000), last() + 1)
    order = {"target": target, "place": place, "at": at, **({"draft": draft} if draft else {}),
             **({"mark": mark} if mark else {}), **({"stay": True} if stay else {})}
    registry.write_whole(stays() if stay else path(view), json.dumps(order) + "\n")
    return f"1100 shows {target}." if stay else f"1100 shows {target}, in view {view}."
