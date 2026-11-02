#!/usr/bin/env python3
"""prototype-continue.py — the hook behind /prototype-continue.

    /prototype-continue                  names every saved prototype, to pick one
    /prototype-continue member-pages     this session takes that prototype, wherever it is

It takes a subject's exact kebab name, or no word. A name matching no
subject says so, and moves nothing.

A saved subject moves at once. One another session holds moves only while
that session's turn is over: a turn still running may be writing the next
generation, and a take then splits it. Moved, it leaves the other
session's hub for this one's, and its stamp names this session, through
the hold in lib/prototypes.py. This session's own earlier subject, not
locked in, is saved by the move.

A winner never moves. It waits for its build.
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
from prototypes import APP, SUBJECT, TAKEN  # noqa: E402

TRIGGER = "/prototype-continue"
# Claude Code's statuses for a turn still running: working, or a dialog
# open in its middle.
RUNNING = ("busy", "waiting")


def who(e: dict) -> str:
    return f"session {e['number']} · {e['title']}" if e["number"] else "session unknown"


def main() -> None:
    args = hook.words(TRIGGER)
    number = registry.number_of(args.event.get("session_id") or "")
    if not number:
        hook.done("This session has no number yet. Nothing moved.")

    if not args:
        _, saved = prototypes.shelf()
        if not saved:
            hook.done("No prototype is saved. Nothing moved.")
        hook.done("Saved: " + "; ".join(f"{e['subject']}, {who(e)}" for e in saved)
                  + ". Nothing moved.\nName one: /prototype-continue " + saved[0]["subject"])

    subject = " ".join(args)
    if not SUBJECT.fullmatch(subject) or subject in TAKEN \
            or not prototypes.generations(os.path.join(APP, subject)):
        hook.done(f"{subject} names no prototype. Nothing moved.")
    if pick := prototypes.winner(subject):
        hook.done(f"{subject} is locked in, as {pick}. A winner waits for its build. Nothing moved.")
    mine = prototypes.subject_of(number)
    if mine == subject:
        hook.done(f"This session already holds {subject}. Nothing moved.")

    held, live = registry.entries(), registry.claude_records(fresh=True)
    others = [nn for nn in prototypes.holders(subject) if nn != number]
    for nn in others:
        rec = live.get((held.get(nn) or {}).get("session_id"))
        if rec and rec.get("status") in RUNNING:
            hook.done(f"Session {nn} is mid-turn, and holds {subject}. Nothing moved. "
                      "Ask again once its turn ends.")
    prototypes.hold(number, subject)
    said = (f"Prototype {subject} successfully taken, "
            + (f"from session {', '.join(others)}." if others else "from 1400's Saved list."))
    if mine and not prototypes.winner(mine):
        said += f" {mine} is saved."
    hook.done(said)


if __name__ == "__main__":
    main()
