#!/usr/bin/env python3
"""prototype-save.py — the hook behind /prototype-save.

    /prototype-save      this session lets go of its prototype, for later

The subject stays whole, every generation and variation. Only this
session's hold goes, through the release in lib/prototypes.py, so its hub
drops the tab, and 1400's library lists it under Saved, under this
session's number and title. /prototype-continue takes it back, from any
session. Loose words are never read.

A winner is never saved. It already left the hub for 1400's Locked list,
and its hold marks who builds it.
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402

TRIGGER = "/prototype-save"


def main() -> None:
    args = hook.words(TRIGGER)
    number = registry.number_of(args.event.get("session_id") or "")
    subject = prototypes.subject_of(number) if number else ""
    if not subject:
        hook.done("This session holds no prototype. Nothing was saved.")
    if pick := prototypes.winner(subject):
        hook.done(f"{subject} is locked in, as {pick}. It already shows on 1400's Locked list. "
                  "Nothing was saved.")
    prototypes.stamp(number, subject)
    prototypes.release(number)
    hook.done(f"Prototype {subject} successfully saved. 1400 lists it under Saved, as session {number}'s.")


if __name__ == "__main__":
    main()
