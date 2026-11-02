#!/usr/bin/env python3
"""early-compaction.py — an automatic compaction that comes early is blocked.

A PreCompact hook, matcher auto, with no skill behind it. Automatic
compaction is off in settings.json, so a session hands over instead of
compacting. Claude Code may still compact on its own: one idle near an
hour was compacted at 50%, "before the prompt cache expired". Under
EARLY of its window, an automatic compaction is that kind, and this
blocks it: the conversation goes on whole. Near a full window it runs,
since nothing else frees the space. /compact, typed, is never touched.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import context  # noqa: E402

# Percent of its window under which an automatic compaction is early.
# Claude Code's own comes near 97%, as the auto-compact window sits.
EARLY = 90


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("trigger") != "auto":
        sys.exit(0)
    got = context.last(event.get("transcript_path") or "")
    pct = context.share(*got) if got else 0
    if pct >= EARLY:
        sys.exit(0)
    print(json.dumps({"decision": "block",
                      "reason": f"Compaction at {pct}% is early. This session is handed over instead."}))


if __name__ == "__main__":
    main()
