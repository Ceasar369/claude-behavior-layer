#!/usr/bin/env python3
"""prototype-hold.py — a session holds a prototype subject the moment it writes a generation.

A PostToolUse hook, with no skill behind it. A write is the trigger, so
nothing is typed and no turn is spent.

    code/prototypes/proposal-header/g2.json    the writing session holds proposal-header

1100 hears the session's folder, counts the prototype as waiting on me,
and frames it from the one prototypes app on 1400. Every other page 1100
draws from files it hears itself, so no other write needs a hook.
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402

PATTERN = rf"/code/prototypes/({prototypes.SUBJECT.pattern})/g\d+\.json$"


def main() -> None:
    found, event = hook.written(PATTERN)
    number = registry.number_of(event.get("session_id", ""))
    if number and found.group(1) not in prototypes.TAKEN:
        prototypes.hold(number, found.group(1))


if __name__ == "__main__":
    main()
