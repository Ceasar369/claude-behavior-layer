#!/usr/bin/env python3
"""follow.py — one seat following others, live.

A follower takes a session to follow, then arms its one wait,
tools/transcript.py wait with no session named, in the background, and
ends its turn. The wait returns once a session it follows or drives has
answered, and Claude Code wakes the follower, which answers in its own
role, never typing into it, and arms the same wait again.

  follow.py take 01 10 --for "T" --ends "E"   01 follows 10, for T, until E
  follow.py release 01 10                     01 stops following 10
  follow.py 10                                this seat follows 10, then waits

take writes the follow into the follower's folder, lib/follow.py's FILE,
and says one line. The running wait hears it, so a press never stops it.
A follow taken again takes the new words and keeps its place. A session
the seat drives is refused: the drive already wakes it on every turn.
So is the seat itself, and a number no session holds.

release lets a follow go: its end held, or my stop line came. The wait
hears that too. A session stopped, or another on its number, is released
by the wait itself.

A bare number is the follow of a session whose skill named no task: it
takes the follow, if not taken, then becomes the one wait.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import follow  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))


def seat(n: str) -> str:
    if not re.fullmatch(r"\d{1,2}", n):
        sys.exit(f"{n}: a seat's number, like 31.")
    return f"{int(n):02d}"


def refused(mm: str, nn: str) -> str:
    """Why seat MM cannot follow NN, or ""."""
    held = registry.entries()
    if nn == mm:
        return f"Refused {nn}: it is this seat."
    if nn not in held:
        return f"Refused {nn}: no session holds it."
    if successor.drivers(held).get(nn) == mm:
        return f"Refused {nn}: you drive it, and the drive already wakes you on its every turn."
    return ""


def main() -> None:
    if len(sys.argv) == 2 and re.fullmatch(r"\d{1,2}", sys.argv[1]):
        nn = seat(sys.argv[1])
        mm = registry.number_of(os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
        if not mm:
            sys.exit("This session holds no number.")
        if nn not in follow.following(mm):
            if why := refused(mm, nn):
                sys.exit(why)
            follow.take(mm, nn, "", "")
        os.execv(sys.executable, [sys.executable, os.path.join(TOOLS, "transcript.py"), "wait", "--awake"])

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    t = sub.add_parser("take")
    t.add_argument("number")
    t.add_argument("follows")
    t.add_argument("--for", dest="why", required=True)
    t.add_argument("--ends", required=True)
    r = sub.add_parser("release")
    r.add_argument("number")
    r.add_argument("follows", nargs="+")
    args = ap.parse_args()
    mm = seat(args.number)

    if args.verb == "release":
        them = [seat(n) for n in args.follows]
        follow.release(mm, them)
        for nn in them:
            print(f"Released {nn}.")
        return

    nn = seat(args.follows)
    if why := refused(mm, nn):
        sys.exit(why)
    again = nn in follow.following(mm)
    got = follow.take(mm, nn, args.why, args.ends)
    print(f"{'Following' if not again else 'Still following'} {nn}, {got['title']}: for {got['for']}. "
          f"It ends when {got['ends']}.")


if __name__ == "__main__":
    main()
