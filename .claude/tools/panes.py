#!/usr/bin/env python3
"""panes.py — the command line over lib/panes.py.

A hook imports the library. Anything that cannot import Python calls this.

Every verb prints pane ids, one to a line, or nothing at all. Nothing else
is printed, so a caller reads the whole output as the answer.

say to a session Claude is gone from types nothing: its process ended with
no stop, and the shell left in its pane would run the line as a command.
Nor does say to a session a permission question holds: Return would pick
its first option. A pane iTerm no longer lists is looked for again for a
few seconds: right after a handover, a number still names its old pane
for a moment. Whatever say leaves untyped, it prints nothing, exits 1,
and its one sentence goes to stderr, so no caller takes it for sent.

  panes.py open  [--where down] [--from 07] [--cwd DIR]
  panes.py boot  [--where down] [--from 07] [--words "payments api"]
                 [--acct 1] [--model sonnet] [--effort medium] [--number 04]
  panes.py say   --to 07 --line "/model opus"
  panes.py close --to 07
  panes.py list

Down is the default. It splits the caller's own pane, so the new one
opens below it, in the same tab. A session I launch is placed on the
launch page, or passed as flags to tools/launch.py, never booted here.
"""

import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import panes  # noqa: E402

# The pauses, in seconds, before each look for a pane iTerm does not list.
SETTLE = (0, 1, 1, 2)


def open_pane(to: str) -> str:
    """The pane `to` names, once iTerm lists it, else "". A number's pane is
    found again on each look, so a successor's new pane is found once its
    record names it. iTerm not answering, the pane is taken as named."""
    for pause in SETTLE:
        time.sleep(pause)
        at = panes.anchor(to)
        listed = panes.ids()
        if at and (listed is None or at in listed):
            return at
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)

    for verb in ("open", "boot"):
        p = sub.add_parser(verb)
        p.add_argument("--where", choices=panes.WHERE, default="down")
        p.add_argument("--from", dest="frm", default="")
        if verb == "open":
            p.add_argument("--cwd", default="")
        else:
            p.add_argument("--words", default="")
            p.add_argument("--acct", choices=sorted(panes.CONFIG), default="1")
            p.add_argument("--model", default="")
            p.add_argument("--effort", choices=panes.EFFORTS, default="")
            p.add_argument("--number", default="")

    for verb in ("say", "close"):
        p = sub.add_parser(verb)
        p.add_argument("--to", default="")
        if verb == "say":
            p.add_argument("--line", required=True)
            p.add_argument("--no-enter", dest="enter", action="store_false")

    sub.add_parser("list")
    args = ap.parse_args()

    if args.verb == "open":
        print(panes.open(args.where, args.frm, args.cwd))
    elif args.verb == "boot":
        print(panes.boot(args.where, args.frm, args.words, args.acct,
                         args.model, args.effort, args.number))
    elif args.verb == "say":
        if re.fullmatch(r"\d{1,2}", args.to) and (
                why := page.typable(f"{int(args.to):02d}", ("idle", "shell", "busy"))[0]):
            sys.exit(why)
        where = (f"session {int(args.to):02d}'s pane" if re.fullmatch(r"\d{1,2}", args.to)
                 else f"pane {args.to}" if args.to else "my own pane")
        at = open_pane(args.to)
        if not at:
            sys.exit(f"Nothing was typed: {where} is not open.")
        if not panes.say(at, args.line, enter=args.enter):
            sys.exit(f"iTerm did not take the line for {where}, so it may not have been typed.")
        print(at)
    elif args.verb == "close":
        print(panes.anchor(args.to) if panes.close(panes.anchor(args.to)) else "")
    else:
        found = panes.ids()
        print("\n".join(sorted(found)) if found else "")


if __name__ == "__main__":
    main()
