#!/usr/bin/env python3
"""ports.py — the command line over lib/ports.py.

  ports.py stop PORT [PORT ...]    stop this session's own servers
  ports.py free                    the lowest shift no project on this Mac holds

free reads every project two folders under my home, ~/*/*/.claude/, its
project.json's fixed shift, else its state file's, and prints the lowest
of 0, 10000 … 50000 none holds. A new project writes it into its own
project.json, so no two projects share ports.

A port of this session's band stops with everything serving it:
lib/ports.py's serving().

A port that is not the session's own, as lib/ports.py's own() reads it, is
refused, and nothing stops. The number is the registry's, by
CLAUDE_CODE_SESSION_ID.
Another session's Claude Code, and this one's, are never stopped.

hooks/guard.py points a refused kill here. lib/ports.py does the work,
and /9-session-stop sweeps a whole band with it.
"""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import ports  # noqa: E402
import project  # noqa: E402
import registry  # noqa: E402


def held() -> dict:
    """Each project's shift on this Mac, by its folder: ~/*/*/.claude/."""
    found = {}
    for claude in glob.glob(os.path.join(os.path.expanduser("~"), "*", "*", ".claude")):
        root = os.path.dirname(claude)
        if os.path.isfile(os.path.join(claude, "project.json")) or os.path.isfile(os.path.join(root, project.SHIFT_FILE)):
            found[root] = project.shift(root)
    return found


def free() -> int:
    taken = held()
    for root, by in sorted(taken.items(), key=lambda x: x[1]):
        print(f"{by:>6}  {root}")
    left = [s for s in range(0, 50001, 10000) if s not in taken.values()]
    if not left:
        print("Every shift from 0 to 50000 is held. Nothing is free.")
        return 1
    print(f"Free: {left[0]}")
    return 0


def stop(asked: list) -> int:
    number = registry.number_of(os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
    if not number:
        print("This session holds no number, so no port is its own. Nothing stopped.")
        return 1
    theirs = [p for p in asked if not ports.own(p, number)]
    if theirs:
        print(f"Refused: {', '.join(map(str, theirs))} is outside band {number}. "
              "Nothing stopped.")
        return 1
    table = ports.processes()
    keep = ports.spared(table)
    failed = False
    for port in asked:
        pids = ports.serving(port, table) - keep
        if not pids:
            print(f"{port} had nothing running.")
            continue
        left = ports.halt(pids)
        if left or ports.answering(port):
            failed = True
            print(f"{port} did not stop: {', '.join(map(str, left)) or 'its port still answers'}.")
        else:
            print(f"{port} successfully stopped: {len(pids)} "
                  f"process{'' if len(pids) == 1 else 'es'}.")
    return 1 if failed else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    p = sub.add_parser("stop")
    p.add_argument("ports", nargs="+", type=int)
    sub.add_parser("free")
    args = ap.parse_args()
    sys.exit(free() if args.verb == "free" else stop(args.ports))


if __name__ == "__main__":
    main()
