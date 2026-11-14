#!/usr/bin/env python3
"""Replay my real transcripts through the reader 1100 draws them with.

On 9 November every transcript holding a task notice failed to draw, 170
times: a line of a kind no test had read. Here the newest transcripts of
this project, forty unless a number is given, are each read as a
Transcript tab and home read one: its thread, its last words, whether its
turn ended, its turns. One that raises, or logs an error, fails, named by
its file. Nothing is written, and none of their words is printed.

  transcripts-replay-test.py [how many]
"""

import contextlib
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import registry  # noqa: E402
import transcripts  # noqa: E402

MANY = int(sys.argv[1]) if len(sys.argv) > 1 else 40
found = sorted((path for base in registry.LIVE
                for path in glob.glob(os.path.expanduser(f"{base}/projects/{transcripts.SLUG}/*.jsonl"))),
               key=os.path.getmtime)[-MANY:]
failed = []
for path in found:
    logged = io.StringIO()
    try:
        with contextlib.redirect_stderr(logged):
            transcripts.thread(path)
            transcripts.last_said(path)
            transcripts.ended(path)
            transcripts.turns(path, "00")
    except Exception as e:
        failed.append((path, f"{type(e).__name__}: {e}"))
        continue
    if "Traceback" in logged.getvalue():
        failed.append((path, [line for line in logged.getvalue().splitlines() if line.strip()][-1]))
print(f"{len(found)} real transcripts read, {len(found) - len(failed)} whole." if found
      else "No real transcript was found to read.")
for path, why in failed:
    print(f"  {os.path.basename(path)} failed: {why[:160]}")
sys.exit(1 if failed or not found else 0)
