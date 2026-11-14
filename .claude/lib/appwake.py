#!/usr/bin/env python3
"""appwake.py — the side panel beside my app chat, as 1100's app home posts it.

Nothing here, or anywhere, types into the Claude app.

  panel     PANEL, what 1100's app home posts: whether it holds my
            cursor. Its line stays "": nothing waits to be typed. The
            door's own folder holds it, beside its key and its log.

Imported, never run.
"""

import json
import os
import threading

import door

PANEL = os.path.join(door.STATE, "panel.json")
# 1100's page threads each rewrite PANEL.
LOCK = threading.Lock()


def _put(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def panel() -> dict:
    """{"held": the panel holds my cursor, "line": always "" now}."""
    try:
        with open(PANEL) as f:
            got = json.load(f)
    except (OSError, ValueError):
        got = {}
    got = got if isinstance(got, dict) else {}
    return {"held": bool(got.get("held")), "line": str(got.get("line") or "")}


def _panel(**change) -> None:
    with LOCK:
        now = panel()
        if {**now, **change} != now:
            _put(PANEL, {**now, **change})


def held(on: bool) -> None:
    """The panel holds my cursor, or let it go: 1100's app home says so."""
    _panel(held=bool(on))


def waiting(line: str) -> None:
    """The panel's line, cleared by 1100's Copy."""
    _panel(line=line)
