#!/usr/bin/env python3
"""wake.py — a session waiting on others in the background, and its wake.

A driving session runs its wait, tools/transcript.py's, as a background
command, then ends its turn. Claude Code starts its next turn the moment that
command ends, so a finish wakes it, and between finishes my words reach
it at once. A session it drives is named by the number the wait was armed
with, never by a path the wait watches.

Each time the wait is armed, and each time it ends, one line goes into
the waiting session's own folder, wakes.log, flushed at once.

A page reads such a session green, as working, while its turn has ended
on work still running and its last move asks me nothing. A wait is that
work, and so is an agent, a command or a browser script it sent to the
background. A server never is. What still runs is read from its
transcript.

Imported, never run.
"""

import contextlib
import datetime
import os
import re
import threading
import time

import ports
import registry
import transcripts

# The wait ends itself after 50 minutes, so its session wakes before
# Claude Code's one-hour cache expires. Each wake keeps that cache, and
# Claude Code never compacts the session while it idles. The Bash tool's
# own timeout, 7200000 ms, never cuts it short.
LIMIT = 50 * 60

# A driven session still idle this long after its last turn ends the
# wait, once per idle stretch: a session a driver holds never sits idle
# unseen, nor wakes it again and again. A followed one never does.
IDLE = 5 * 60

LOG = "wakes.log"

# Each shell the Bash tool starts opens by sourcing its session's shell
# snapshot, which tells it from the session's other children: its MCP
# servers, its caffeinate.
TOOL = "/shell-snapshots/snapshot-"

# A move asking me something: a ruling, an action or an answer. Any other
# move asks me nothing, a progress note with no move line too.
ASKS = re.compile(r"^(?:ruling|action|answer)\b", re.I)


def log(number: str, line: str) -> None:
    """One line into session NN's wakes.log, on this Mac's clock, flushed at once."""
    with open(os.path.join(registry.folder(number), LOG), "a") as f:
        f.write(f"{time.strftime(transcripts.STAMP)} {line}\n")
        f.flush()


# One draw asks for the process table once per session it shows. Inside
# once(), this thread asks ps the first time, and every table() after
# reads that same list.
_held = threading.local()


@contextlib.contextmanager
def once():
    """Every table() inside, on this thread, reads one ps call's list."""
    outer = getattr(_held, "on", False)
    _held.on = True
    try:
        yield
    finally:
        if not outer:
            _held.on, _held.procs = False, None


def table() -> list:
    """Every process now, as (pid, parent, command): ports.table()'s one ps
    call, or none inside once() after its first."""
    if getattr(_held, "on", False):
        if getattr(_held, "procs", None) is None:
            _held.procs = _ps()
        return _held.procs
    return _ps()


def _ps() -> list:
    return [(pid, parent, command) for pid, (parent, command) in ports.table().items()]


def started(rec) -> datetime.datetime:
    """When a live session's process started, from Claude Code's record."""
    return datetime.datetime.fromtimestamp(rec.get("startedAt", 0) / 1000, datetime.timezone.utc)


def over(rec, mine: dict) -> bool:
    """Whether a live session's turn is over. Claude Code reads it busy
    while an agent it sent to the background runs, its turn over or not,
    so a busy one asks its transcript: transcripts.ended's."""
    status = (rec or {}).get("status")
    return status in ("idle", "shell") or (status == "busy" and transcripts.ended(mine.get("transcript", "")))


def waiting(rec, mine: dict) -> bool:
    """Whether a session's turn ended on work still running, asking me nothing.

    `rec` is Claude Code's record for it, `mine` its record in the
    registry. Its turn is over, its last move is no Ruling, Action or
    Answer, and its process still runs work it sent to the background:
    Thread.running's.
    """
    if not rec or not over(rec, mine):
        return False
    path = mine.get("transcript", "")
    if ASKS.match(transcripts.last_said(path)[2]):
        return False
    return bool(transcripts.thread(path).running(started(rec)))
