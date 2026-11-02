#!/usr/bin/env python3
"""prototype-route.py — while a session holds a prototype subject, my
message about it reaches /4-prototype, word for word.

A UserPromptSubmit hook, with no skill behind it. A session picks a skill
from my phrasing, message by message, so a casual "I prefer v2" once ran
no skill, and the family's guards lapsed. The hold routes instead: while
this session holds a subject, every message I type reaches it with one
line more, handing my words to the router unchanged.

    session 05 holds proposal-header · I type "I prefer v2, darker"
        the session invokes 4-prototype with "I prefer v2, darker"

A slash command routes itself, so it hears nothing. Neither does a session
holding no subject, nor one that marked its subject's winner built,
through prototype.py build: my messages are then about the build. Claude Code lets
this hook add a line, never replace my message, so the session still makes
the call.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import prototypes  # noqa: E402
import registry  # noqa: E402


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    prompt = (event.get("prompt") or "").strip()
    if not prompt or prompt.startswith("/"):
        sys.exit(0)
    number = registry.number_of(event.get("session_id") or "")
    subject = prototypes.subject_of(number) if number else ""
    if not subject or subject in prototypes.building(number):
        sys.exit(0)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            f"You hold the prototype {subject}. My message is about it → "
            "invoke the 4-prototype skill now, with my message as its args, "
            "word for word: nothing added, dropped or retold. Build nothing "
            "outside it. My message is about something else → answer it as "
            "usual."),
    }}))


if __name__ == "__main__":
    main()
