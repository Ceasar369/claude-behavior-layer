#!/usr/bin/env python3
"""wrap-up.py — a working session told to wrap up its turn, past System's
wrap-up threshold.

A PostToolUse and PostToolUseFailure hook, on every tool, with no skill
behind it. A session working one long turn never finishes, so nothing can
hand it over. After each of its tool calls, this reads its context. Past
the wrap-up threshold, its words ride beside that tool's result, and the
session reads them before its next step. Nothing interrupts it, and no
turn is spent.

Who hands it over decides what it is told, as lib/successor.py rules:

  driven       end your turn: session 30 drives you, and hands you over.
  a driver, or a follower
               hand yourself over once your step ends, never mid-turn.
  any other    end your turn: I hand you over from your Handover page.

A subagent's tool call is passed over: its session's context moves only
once the subagent answers.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import context  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("agent_id"):
        sys.exit(0)
    got = context.last(event.get("transcript_path") or "")
    pct, limit = (context.share(*got) if got else 0), context.wrapup()
    if pct < limit:
        sys.exit(0)
    held = registry.entries()
    nn = registry.number_of(event.get("session_id") or "", held)
    if not nn:
        sys.exit(0)
    past = f"Your context is at {pct}%, past {limit}%. Finish the step you are on, then "
    if by := successor.driven(nn, held):
        words = past + f"end your turn, and say why. Session {by} drives you, and hands you over."
    elif successor.driving(nn, held):
        words = past + "hand yourself over, as `session-control` says. Never mid-turn."
    else:
        words = past + "end your turn, and say why. I hand you over from your Handover page."
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": event.get("hook_event_name") or "PostToolUse",
        "additionalContext": words}}))


if __name__ == "__main__":
    main()
