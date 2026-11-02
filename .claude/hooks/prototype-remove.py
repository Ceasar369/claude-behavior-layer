#!/usr/bin/env python3
"""prototype-remove.py — the hook behind /prototype-remove.

    /prototype-remove                   this session's own prototype
    /prototype-remove proposal-header   the subject with that exact name

A subject goes whole, its generations and its routes, through the remove
in lib/prototypes.py, the only one. It takes a subject's exact kebab name,
or no word. A name matching no subject says so, and removes nothing. Loose
words are never read.

Every session's hold on the subject goes with it, through that same remove,
so none waits on 1100 for a prototype that is gone, and each one's next
subject starts clean. The reply says so only for this session's own.

A winner stays until the session building it removes it, once its real
version is live, or the last one building it stops, through
prototypes.built. The session that made it never removes it. The
builder's mission names the winner's file under "Read first", as
assistant-mission rules, or prototype.py build marked it as building. Any
other remove of it, mine too, says so and removes nothing.
"""

import glob
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
from prototypes import APP, ROUTES, SUBJECT, TAKEN  # noqa: E402

TRIGGER = "/prototype-remove"


def many(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def main() -> None:
    args = hook.words(TRIGGER)
    number = registry.number_of(args.event.get("session_id") or "")
    mine = prototypes.subject_of(number) if number else ""

    subject = " ".join(args) if args else mine
    if not subject:
        hook.done("This session has no prototype. Nothing was removed.")

    home, routes = os.path.join(APP, subject), os.path.join(ROUTES, subject)
    if not SUBJECT.fullmatch(subject) or subject in TAKEN \
            or not (os.path.isdir(home) or os.path.isdir(routes)):
        hook.done(f"{subject} names no subject. Nothing was removed.")

    pick = prototypes.winner(subject)
    if pick and not prototypes.builds(number, subject):
        hook.done(f"{subject} keeps its winner, {pick}, until the session "
                  "building it removes it. Nothing was removed.")

    generations = len(glob.glob(os.path.join(home, "g*.json")))
    variations = len(glob.glob(os.path.join(routes, "**", "*.tsx"), recursive=True))
    prototypes.remove(subject)
    said = (f"Prototype {subject} successfully removed: "
            f"{many(generations, 'generation')} and {many(variations, 'variation')}.")
    if subject == mine:
        said += " It no longer waits on 1100."
    hook.done(said)


if __name__ == "__main__":
    main()
