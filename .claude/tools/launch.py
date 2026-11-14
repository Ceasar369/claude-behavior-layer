#!/usr/bin/env python3
"""launch.py — start a session, or open a browser pane, from flags alone.

The launch page is for me. This is for a skill: every value the page
offers is a flag here, self-drive as a message opening with /self-drive,
so a skill starts exactly what it needs.

  launch.py session [--name "demo skeleton"] [--message "..."] [--number 08]
                    [--account 1] [--model claude-opus-5-5] [--effort max]
                    [--clone 01] [--from 07] [--where down]
  launch.py browser --site 7204 [--from 07] [--where down]
  launch.py seat                                the seat a new assistant takes
  launch.py page NN [--resume]                  session NN's launch page's launch

`page` runs the launch my press on session NN's launch page started, as a
program of its own: lib/launch.py's run(). The press marks the rows and
hands it the page's lock, --held. `--resume` picks up a launch whose
program died. Ended by a signal, it fails the rows still booting, so the
page is never left locked.

--from is a session number or a pane id. Left out, it is the caller's own
pane. --where is right, left, down or up of it, tab for a new tab in its
window, or window for a new window. Down is the default.

A session left unset takes what the page would: the lowest free number its
name may take, then, as its pane opens, the next account in the order set
on 1100/system, and the model and effort set there. Its folder keeps the
model and effort its flags named: lib/launch.py's NAMED. A number is
picked as lib/launch.py's free() picks it, and held until its session
claims it.

It prints the new pane's id. A session then waits until it has claimed its
number and received its message, and prints its number. Its record names
the caller as the session that launched it. Anything that
stops it is said on stderr, and it exits 1.

--clone is a session's number. The new session starts from that one's
conversation, forked, on its own account, model and effort:
lib/launch.py's line().

--site is a port on this machine, or any address.

A browser pane already showing the same site is kept, and its id printed.
A page never opens twice.
"""

import argparse
import os
import re
import signal
import sys
import threading

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import iterm  # noqa: E402
import launch  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402

WHERE = ("right", "left", "down", "up", "tab", "window")


def fail(why: str, held: str = "") -> None:
    """Say why and exit 1, dropping the number this launch held."""
    if held:
        registry.release(held)
    print(why, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="kind", required=True)
    s = sub.add_parser("session")
    s.add_argument("--name", default="")
    s.add_argument("--message", default="")
    s.add_argument("--number", default="")
    s.add_argument("--account", default="")
    s.add_argument("--model", default="")
    s.add_argument("--effort", default="")
    s.add_argument("--clone", default="")
    b = sub.add_parser("browser")
    b.add_argument("--site", required=True)
    b.add_argument("--name", default="")
    for p in (s, b):
        p.add_argument("--from", dest="frm", default="")
        p.add_argument("--where", choices=WHERE, default="down")
    sub.add_parser("seat")
    g = sub.add_parser("page")
    g.add_argument("nn")
    g.add_argument("--held", type=int, default=-1)
    g.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    if args.kind == "page":
        if not re.fullmatch(r"\d{2}", args.nn):
            fail("page takes a session number, like 07.")

        # A signal can land while this thread holds the page's file lock, so
        # another thread fails the rows still booting.
        def cut(*_):
            threading.Thread(target=lambda: (launch.unboot(args.nn), os._exit(1)), daemon=True).start()

        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(sig, cut)
        launch.run(args.nn, args.held, args.resume)
        return

    if args.kind == "seat":
        got = launch.seat()
        if not got:
            fail("No ten is free for an assistant.")
        print(got)
        return

    anchor = panes.anchor(args.frm)
    if not anchor:
        fail(f"No pane answers to {args.frm or 'this caller'}.")
    row, held = {"kind": args.kind}, ""
    sat = panes.numbers()
    caller = sat.get(panes.me(), "")
    if args.kind == "browser":
        row["site"] = args.site
        mine = sat.get(anchor, "")
        row["name"] = args.name or (launch.browser_name(mine) if mine else "")
    else:
        # A number picked is held at once, so a launch beside this one picks another.
        n = args.number or next((c for c in launch.free(by=caller, name=args.name)
                                 if registry.reserve(c)), "")
        if not n:
            fail("No number is free for this launch.")
        held = "" if args.number else n
        row.update(n=f"{int(n):02d}" if str(n).isdigit() else n, name=args.name,
                   message=args.message, account=args.account,
                   model=args.model, effort=args.effort)
        if args.clone:
            row["clone"] = f"{int(args.clone):02d}" if args.clone.isdigit() else args.clone
    if args.where == "window":
        row["win"] = "new"
    elif args.where == "tab":
        row["win"] = "L:" + iterm.window_of(anchor)
    else:
        row["at"] = {"anchor": "p:" + anchor, "side": args.where}

    wrong = launch.problems([row])
    if wrong:
        fail(" ".join(w.replace("Row 1: ", "") for w in wrong), held)
    if args.kind == "session" and not held:
        if not registry.reserve(row["n"]):
            fail(f"{row['n']} is held by another launch.")
        held = row["n"]
    if launch.browser(row):
        shown = iterm.find(launch.address(row))
        if shown:
            print(shown)
            return
    pane = launch.place(row, {}, {})
    if not pane:
        fail("The pane did not open." + (f" iTerm said: {iterm.why()}." if iterm.why() else ""), held)
    print(pane, flush=True)
    launch.start(row, pane)
    if launch.browser(row):
        return
    if not launch.arrive(row, pane, caller):
        fail(row["why"], held)
    print(row["n"])


if __name__ == "__main__":
    main()
