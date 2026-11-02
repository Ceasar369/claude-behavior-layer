#!/usr/bin/env python3
"""successor.py — what a driver drives, what it hands over now, and the handover itself.

  successor.py take 30 31 32               30 takes 31 and 32, a full drive
  successor.py take 30 22 --topic "T"      30 takes 22, a partial drive on topic T
  successor.py release 30 22               30 lets 22 go
  successor.py due 30 31 32                each session 30 drives, then 30 itself
  successor.py hand 31 --by 30             hand seat 31 over, for its driver 30

take writes the drive down, in the driver's folder: lib/successor.py's
FILE. 1100's wheel and the Handover page read only that, never a wait.
A session another seat drives is refused: one driver per session. take
says one line for each session, and fails on a refusal, writing nothing.
A drive replaces the seat's follow of that session, and says so. The
seat's one wait hears a take, so a session joining never stops it.
release lets each go, once a partial drive's topic is saved, once a
drive closes its session, or on my stop line.

A driver or a follower asks due once each finish is handled, before it
arms its wait again: its own number, then each session it drives. It reads each one's
context against the threshold set on System, as lib/successor.py's due()
does, and says one line for each, its own last:

  Hand over 31: 64%, past 60%.
  Wait for 32: 66%, past 60%, still working.
  Drive on 33: 41%, under 60%.
  Hand over: 74%, past 70%.
  Drive on: 41%, under 70%.
  Driven by 10: it hands you over.

Hand over 31 means: run hand 31 now, in the background, and answer 31's
finish meanwhile. Wait for means: nothing is typed now. A session still
working is turned to its driver by its wrap-up. One capped, erring, held
by a dialog or gone is session-control Step 2's. Hand over, for itself,
means: run session-handover now, and arm no wait. Driven by means: its
own driver hands it over, never itself.

hand types /handover-prepare, then /handover-resume, into the seat's
pane, as the Handover page's press does, picking nothing: the successor
launches on what lib/handover.py's carried() keeps, else the order's
next account, and the model and effort set on System. It says one line,
with "successfully" once the successor holds the seat.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import finish  # noqa: E402
import follow  # noqa: E402
import handover  # noqa: E402
import successor  # noqa: E402


def seat(n: str) -> str:
    if not re.fullmatch(r"\d{1,2}", n):
        sys.exit(f"{n}: a seat's number, like 31.")
    return f"{int(n):02d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    d = sub.add_parser("due")
    d.add_argument("number")
    d.add_argument("drives", nargs="*")
    h = sub.add_parser("hand")
    h.add_argument("number")
    h.add_argument("--by", required=True)
    t = sub.add_parser("take")
    t.add_argument("number")
    t.add_argument("drives", nargs="+")
    t.add_argument("--topic", default="")
    r = sub.add_parser("release")
    r.add_argument("number")
    r.add_argument("drives", nargs="+")
    args = ap.parse_args()

    if args.verb == "take":
        me, them = seat(args.number), [seat(n) for n in args.drives]
        if me in them:
            sys.exit(f"Refused {me}: it is this seat. Nothing taken.")
        followed = follow.following(me)
        if refused := successor.take(me, them, args.topic):
            for nn, by in refused:
                print(f"Refused {nn}: session {by} drives it. Nothing taken.")
            sys.exit(1)
        what = f"a partial drive on {' '.join(args.topic.split())}" if args.topic.strip() else "a full drive"
        for nn in them:
            print(f"Taken {nn}: {what}." + (" Its follow ends: the drive wakes you on its every turn."
                                            if nn in followed else ""))
        return

    if args.verb == "release":
        me, them = seat(args.number), [seat(n) for n in args.drives]
        successor.release(me, them)
        for nn in them:
            print(f"Released {nn}.")
        return

    if args.verb == "hand":
        said = handover.hand(seat(args.number), seat(args.by))
        print(said)
        sys.exit(0 if "successfully" in said else 1)

    me = seat(args.number)
    for nn in map(seat, args.drives):
        pct, limit, go = successor.due(nn)
        f = finish.read(nn)
        if pct is None:
            print(f"Drive on {nn}: no context read.")
        elif not go:
            print(f"Drive on {nn}: {pct}%, under {limit}%.")
        elif f["kind"] in ("working", "blocked", "capped", "error", "gone", "stopped"):
            print(f"Wait for {nn}: {pct}%, past {limit}%, {'still working' if f['kind'] == 'working' else finish.word(f)}.")
        else:
            print(f"Hand over {nn}: {pct}%, past {limit}%.")
    if by := successor.driven(me):
        print(f"Driven by {by}: it hands you over.")
        return
    pct, limit, go = successor.due(me)
    if pct is None:
        print("Drive on: no context read.")
    elif go:
        print(f"Hand over: {pct}%, past {limit}%.")
    else:
        print(f"Drive on: {pct}%, under {limit}%.")


if __name__ == "__main__":
    main()
