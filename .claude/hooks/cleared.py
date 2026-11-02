#!/usr/bin/env python3
"""cleared.py — a numbered session keeps its number through /clear.

A SessionStart hook, matcher clear, with no skill behind it. /clear starts
a new conversation in the same process, under a new id and a new
transcript, and the session's record still names the old pair: 1100 would
read it gone, and its page could type nothing. Its record moves to the
new pair, so its number, its tab and its page stay.

The process is the link. Claude Code's own record of it, found by its pid
up this hook's parents, carries the session's name, and the name opens
with its number.

It prints nothing: what a SessionStart hook prints reaches the session.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import registry  # noqa: E402


def claude() -> tuple:
    """The number and pid of the Claude Code process above this hook."""
    pid = os.getppid()
    for _ in range(4):
        for base in registry.LIVE:
            try:
                with open(os.path.expanduser(f"{base}/sessions/{pid}.json")) as f:
                    name = json.load(f).get("name") or ""
            except (OSError, ValueError):
                continue
            return (name[:2] if re.match(r"\d{2}-", name) else ""), pid
        try:
            pid = int(subprocess.run(["/bin/ps", "-o", "ppid=", "-p", str(pid)],
                                     capture_output=True, text=True, timeout=5).stdout.strip() or 0)
        except (OSError, ValueError, subprocess.SubprocessError):
            return "", 0
        if pid <= 1:
            break
    return "", 0


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("source") != "clear" or not event.get("session_id"):
        return
    number, pid = claude()
    path = os.path.join(registry.folder(number), registry.RECORD) if number else ""
    try:
        with open(path) as f:
            record = json.load(f)
    except (OSError, ValueError):
        return
    record.update(session_id=event["session_id"], transcript=event.get("transcript_path", ""), pid=pid)
    registry.write(record)


if __name__ == "__main__":
    main()
