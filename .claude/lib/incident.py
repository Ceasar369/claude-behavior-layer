#!/usr/bin/env python3
"""incident.py — the note the memory guard leaves a session whose program it stopped.

tools/memory-guard.py opens one note per incident, in its folder's open/:
what it stopped, where, on which ports, and for each session its line and
when it was told. hooks/guard.py tells each session its line at its next
command, once, then refuses a restart. Both take the note's shape, its
lock, its read and its write from here, so the two never drift.

The lock is the guard's whole folder's. The guard's loop, its act verb and
the hook each take it, so two calls at once tell a session once.

It stays on Python 3.9. memory-guard.py imports it, and launchd runs that
on macOS's own /usr/bin/python3, 3.9, which never moves with Homebrew.

Imported, never run.
"""

import contextlib
import fcntl
import json
import os
import time


def note(key: str, targets: list, command: str = "", cwd: str = "", ports: list = (),
         restart: bool = False) -> dict:
    """Incident KEY's note: each target session's line, not told yet. `restart`
    also refuses the same program in the same folder, or on the same port."""
    return {"incident": key, "at": round(time.time(), 2), "restart": restart, "command": command, "cwd": cwd,
            "ports": list(ports), "for": [dict(t, told=None) for t in targets]}


@contextlib.contextmanager
def lock(folder: str):
    """The guard's folder, held by one writer at a time."""
    with open(os.path.join(folder, "lock"), "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def read(path: str, default=None):
    """One file of the guard's folder, or `default` when it is gone or torn."""
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write(path: str, data) -> None:
    """One file of the guard's folder, whole: a reader never meets half of it."""
    with open(path + ".tmp", "w") as f:
        json.dump(data, f)
    os.replace(path + ".tmp", path)
