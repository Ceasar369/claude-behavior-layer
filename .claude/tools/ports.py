#!/usr/bin/env python3
"""ports.py — the command line over lib/ports.py.

  ports.py stop PORT [PORT ...]    stop this session's own servers

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
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import ports  # noqa: E402
import registry  # noqa: E402

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
    args = ap.parse_args()
    sys.exit(stop(args.ports))


if __name__ == "__main__":
    main()
