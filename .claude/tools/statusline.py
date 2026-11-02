#!/usr/bin/env python3
"""statusline.py — the status line, keeping each account's limits on disk.

Claude Code runs the status line after each message, handing it a payload
on stdin. Its rate_limits hold the account's two windows, five_hour and
seven_day, each with used_percentage and resets_at, in epoch seconds. They
are absent until the session's first answer, and again just after a
resume.

This keeps them on disk, through lib/finish.py, so a capped session's
reset can be read from outside it. The account is the one the session
runs under. Then it hands the payload on to statusline-draw.py beside it,
and prints the two lines that draws.

The project's .claude/settings.json runs it, through $CLAUDE_PROJECT_DIR,
the folder the session started in. The command runs in the session's
current folder, which a cd moves, so a path from there would break.

  statusline.py         the limits go where lib/finish.py keeps them
  statusline.py DIR     into DIR instead, for a test

What it prints is kept too, in the session's own folder, so its
transcript page draws the same two lines whole, however narrow its pane.

It never fails and never blanks the line: limits that cannot be kept are
skipped, and the line still shows. lib/finish.py is imported only to keep
them, so a library another session is mid-way through editing skips the
limits, never the line.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

DRAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "statusline-draw.py")


def main() -> None:
    raw = sys.stdin.read()
    try:
        import finish
        import registry
        finish.keep(registry.account(), json.loads(raw).get("rate_limits"), *sys.argv[1:2])
    except Exception:
        pass
    shown = subprocess.run([sys.executable, DRAW], input=raw, capture_output=True, text=True)
    sys.stdout.write(shown.stdout)
    try:
        keep(json.loads(raw).get("session_id", ""), shown.stdout)
    except Exception:
        pass


def keep(session_id: str, lines: str) -> None:
    """The two lines, kept in the numbered session's folder for its page.
    Written whole, then moved in, so a page never reads half."""
    import registry
    number = registry.number_of(session_id)
    if not number or not lines.strip():
        return
    registry.write_whole(os.path.join(registry.folder(number), registry.STATUSLINE), lines)


if __name__ == "__main__":
    main()
