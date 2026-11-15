#!/usr/bin/env python3
"""own-hooks.py — runs the hooks a project names for itself.

A hook of every event the layer answers: SessionStart, UserPromptSubmit,
PreToolUse on a Skill call, PostToolUse on a Write or an Edit, and Stop.
It has no skill behind it. One more event is the layer's own: AfterShip,
which hooks/8-ship.py sends after each commit, with the commit and its
paths.

.claude/settings.json is the layer's, the same in every project, so an
update never clashes there. A project's own hooks sit in its
.claude/project.json instead, under "hooks", by event:

    "hooks": {"UserPromptSubmit": [{"file": ".claude/hooks/my-skill.py", "timeout": 60}],
              "PreToolUse": [{"file": ".claude/hooks/my-skill.py", "timeout": 60}]}

Each one is run in the file's order, as Claude Code would run it: python3,
the file, the event on stdin. "matcher", a pattern, holds a hook to the
tools, or the session starts, it matches whole. "timeout" is in seconds,
60 with none. The first hook that answers, or fails, ends the run: its
output and its exit code become this hook's. A project naming none costs
one read of its file.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import project  # noqa: E402


def main() -> None:
    if not project.HOOKS:
        return
    raw = sys.stdin.read()
    try:
        event = json.loads(raw)
    except ValueError:
        return
    asked = event.get("tool_name") or event.get("source") or ""
    for own in project.HOOKS.get(event.get("hook_event_name"), []):
        matcher = own.get("matcher")
        if isinstance(matcher, str) and matcher and not re.fullmatch(matcher, asked):
            continue
        limit = own["timeout"] if type(own.get("timeout")) is int else 60
        try:
            r = subprocess.run([sys.executable, os.path.join(project.ROOT, own["file"])],
                               input=raw, capture_output=True, text=True, timeout=limit)
        except subprocess.TimeoutExpired:
            print(f"{own['file']} ran past {limit} seconds, and was stopped.", file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print(f"{own['file']} did not run: {e}", file=sys.stderr)
            sys.exit(1)
        if r.stdout.strip() or r.returncode:
            sys.stdout.write(r.stdout)
            sys.stderr.write(r.stderr)
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
