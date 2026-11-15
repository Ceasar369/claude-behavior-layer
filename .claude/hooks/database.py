#!/usr/bin/env python3
"""database.py — every session starts knowing whether the database answers.

A SessionStart hook, matcher startup|resume, with no skill behind it.
Every backend reads the one database .claude/project.json names. Down,
every login and every screen with data fails, and nothing on screen says
why. A project naming no database hears nothing.

One cause is known, and healed here. Postgres writes its pid into
postmaster.pid as it starts. The Mac restarts with Postgres still up, so
the file stays. After the restart another program holds that pid, and
Postgres reads the file as itself still running: it refuses to start,
every 10 seconds, forever. With no postgres running, and another program
holding the pid the file names, the file is a leftover. It goes, and
launchd starts Postgres again. Only a Postgres Homebrew installed is
healed: its data folder, its log and its service are read from the
project's "pg_isready" path, <prefix>/opt/<formula>/bin/pg_isready.

Up, it prints nothing. Healed, or down for another cause, it tells the
session, which says so in its first reply.
"""

import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import ports  # noqa: E402

# Homebrew's own places for one formula, from the pg_isready the project names.
BREW = re.fullmatch(r"(.+)/opt/([^/]+)/bin/pg_isready", ports.PG_ISREADY)
DATA, LOG, SERVICE = ((f"{BREW[1]}/var/{BREW[2]}", f"{BREW[1]}/var/log/{BREW[2]}.log", f"homebrew.mxcl.{BREW[2]}")
                      if BREW else ("", "", ""))


def running() -> bool:
    """Whether any postgres process runs, starting or serving."""
    try:
        return subprocess.run(["/usr/bin/pgrep", "-x", "postgres"],
                              capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return True


def held(path: str) -> bool:
    """Whether a live process holds the pid on the file's first line. With
    no postgres running, that process is another program."""
    try:
        with open(path) as f:
            pid = int(f.readline().strip())
    except (OSError, ValueError):
        return False
    return ports.alive(pid)


def heal() -> bool:
    """Delete a leftover postmaster.pid, start Postgres, and wait for it.

    Only in the one known case: no postgres runs, and another program holds
    the pid the file names. A live one's file is never touched.
    """
    pid = os.path.join(DATA, "postmaster.pid")
    if not DATA or not os.path.exists(pid) or running() or not held(pid):
        return False
    os.remove(pid)
    subprocess.run(["/bin/launchctl", "kickstart", f"gui/{os.getuid()}/{SERVICE}"],
                   capture_output=True, timeout=10)
    for _ in range(15):
        if ports.database():
            return True
        time.sleep(1)
    return False


def tell(text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        },
    }))


def main() -> None:
    sys.stdin.read()
    if not ports.POSTGRES or ports.database():
        return
    if heal():
        tell("The database was down as this session started. A file left from "
             "before the Mac's last restart blocked Postgres. It was deleted, "
             "and Postgres answers again. Say so in one line in your first reply.")
        return
    tell(f"The database does not answer on port {ports.POSTGRES}. Every backend's logins and "
         "data fail until it does. " + (f"Read the last lines of {LOG} for the cause. " if LOG else "")
         + "In your first reply, say the database is down, and why, in plain words.")


if __name__ == "__main__":
    main()
