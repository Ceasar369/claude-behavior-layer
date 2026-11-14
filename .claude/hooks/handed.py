#!/usr/bin/env python3
"""handed.py — a turn handing me words for a session its seat drives is held once.

A Stop hook, on every turn's end, with no skill behind it. A seat drives
the sessions it took, lib/successor.py's taken(). Their words are typed
by the seat, never handed to me, as .claude/rules/talking.md rules under
Your move.

    held:   "Send to session 05." above a copy block, the seat driving 05.
    held:   "Action: paste the message above into session 05's pane."
    held:   a copy block, and session 05 named anywhere in the turn,
            under any move: a Ruling, an Answer.
    passes: "Action: type `/9-session-stop` in session 05." A stop is mine.
    passes: any of these, for a session the seat does not drive.

A turn held once ends the second time, so it never loops.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import registry  # noqa: E402
import successor  # noqa: E402

# The hand-off shape: "Send to session 05."
SHAPE = re.compile(r"\bSend to session (\d{2})\b")
# A move giving my hands a send: "Action: on 1100, send session 05 the fixes."
MOVE = re.compile(r"^\W*Action:([^\n]*)$", re.M | re.I)
SEND = re.compile(r"\b(?:send|paste|type)\b", re.I)
SESSION = re.compile(r"\bsession (\d{2})\b", re.I)
# A stop is mine to give, unless my drive already gave it.
STOP = re.compile(r"9-session-stop|reaper|\bstop\b", re.I)
# The marker opening a copy block, as talking.md lays one out.
COPY = "START COPY"


def handed(said: str) -> set:
    """The sessions whose words a turn hands me to send."""
    found = set(SHAPE.findall(said))
    if COPY in said:
        found |= set(SESSION.findall(said))
    for line in MOVE.findall(said):
        if SEND.search(line) and not STOP.search(line):
            found |= set(SESSION.findall(line))
    return found


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("stop_hook_active"):
        sys.exit(0)
    me = registry.number_of(event.get("session_id") or "", registry.entries())
    if not me:
        sys.exit(0)
    them = sorted(handed(event.get("last_assistant_message") or "") & set(successor.taken(me)))
    if not them:
        sys.exit(0)
    names = " and ".join(them)
    print(json.dumps({"decision": "block", "reason":
        f"You drive session{'s' if len(them) > 1 else ''} {names}. Type its words yourself, with "
        f"`python3 .claude/tools/panes.py say --to NN --line \"…\"`, and show them under Done. "
        "Drop the hand-off and its copy block. Then end your turn."}))


if __name__ == "__main__":
    main()
