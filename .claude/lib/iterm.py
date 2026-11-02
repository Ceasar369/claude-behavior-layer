#!/usr/bin/env python3
"""iterm.py — iTerm's real layout, and panes opened on any side.

AppleScript is lib/panes.py's, and it still types into every pane. This is
for what AppleScript cannot do. tools/iterm.py lists each verb.

Each goes through iTerm's Python API. A pane opened with a url is a browser
pane, showing that address, in place of a shell.

The API needs the iterm2 package, which the system python does not carry,
so a venv under .claude/state/iterm/ holds it. It is made on first use.

Imported, never run.
"""

import json
import os
import subprocess
import sys

import panes

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENV = os.path.join(ROOT, ".claude", "state", "iterm", "venv")
PYTHON = os.path.join(VENV, "bin", "python")
TOOL = os.path.join(ROOT, ".claude", "tools", "iterm.py")

SIDES = ("right", "left", "down", "up")


def ready() -> bool:
    """Make the venv, once. False means it could not be made."""
    if os.path.isfile(PYTHON):
        return True
    try:
        subprocess.run([sys.executable, "-m", "venv", VENV], check=True,
                       capture_output=True, timeout=120)
        subprocess.run([PYTHON, "-m", "pip", "install", "-q", "iterm2"], check=True,
                       capture_output=True, timeout=300)
    except Exception:
        return False
    return os.path.isfile(PYTHON)


# Why the last call came back empty, in the tool's own words. Empty after
# a call that answered.
FAILED = [""]


def call(*args: str) -> str:
    """One run of the tool. Empty means nothing came back, and why() says why."""
    if not ready():
        FAILED[0] = "its Python venv could not be made"
        return ""
    try:
        # Its cookie request can bring iTerm up: panes.clean says why.
        r = subprocess.run([PYTHON, TOOL, *args], env=panes.clean(),
                           capture_output=True, text=True, timeout=30)
    except Exception as e:
        FAILED[0] = str(e) or type(e).__name__
        return ""
    out, lines = r.stdout.strip(), r.stderr.strip().splitlines()
    FAILED[0] = ("" if r.returncode == 0 and out else lines[-1] if lines
                 else f"it exited {r.returncode}" if r.returncode else "it answered nothing")
    return out if r.returncode == 0 else ""


def why() -> str:
    """Why the last call came back empty, or empty when it answered."""
    return FAILED[0]


def tree() -> list:
    """Every window, each tab's split tree. Empty when iTerm did not answer."""
    try:
        return json.loads(call("tree") or "[]")
    except ValueError:
        return []


def opened(out: str) -> tuple:
    """The new pane's id and its window's id, or two empty strings."""
    parts = out.split()
    return (parts[0], parts[1] if len(parts) > 1 else "") if parts else ("", "")


def split(pane: str, side: str, url: str = "") -> tuple:
    if side not in SIDES:
        return "", ""
    return opened(call("split", "--pane", pane, "--side", side, "--url", url))


def apply_layout(spec: dict) -> bool:
    """Apply an arrangement of existing panes, without closing sessions.
    False, nothing moved, on an iTerm2 older than its Python API 1.14:
    why() says so, in one line."""
    return bool(call("layout", "--spec", json.dumps(spec)))


def tab(window: str, url: str = "") -> tuple:
    return opened(call("tab", "--window", window, "--url", url))


def window(url: str = "") -> tuple:
    return opened(call("window", "--url", url))


def close(pane: str) -> bool:
    """Close one pane. A browser pane has no shell to type exit into."""
    return bool(call("close", "--pane", pane))


def name(pane: str, name: str, wait: bool = False) -> bool:
    """Name one pane. A browser pane keeps it until its page sets a new title.

    `wait` is for a pane just opened: its page's first title lands first.
    """
    return bool(call("name", "--pane", pane, "--as", name, *(["--wait"] if wait else [])))


def find(url: str) -> str:
    """The browser pane already showing an address, or empty."""
    return call("find", "--url", url)


def browsers() -> list:
    """Every browser pane open now: its id, the name it was given, the address it opened on."""
    try:
        return json.loads(call("browsers") or "[]")
    except ValueError:
        return []


def screen(pane: str) -> list:
    """A pane's screen, top to bottom: each line as [text, colour, faint]
    runs, its colour "r,g,b", or "" when the pane's own, and faint 1 when
    dimmed. Empty when iTerm did not answer."""
    try:
        return json.loads(call("screen", "--pane", pane) or "[]")
    except ValueError:
        return []


def window_of(pane: str) -> str:
    """The id of the window holding a pane, or empty."""
    def holds(n):
        return any(holds(c) for c in n["children"]) if "split" in n else n["pane"] == pane
    return next((w["window"] for w in tree() for t in w["tabs"] if holds(t["root"])), "")
