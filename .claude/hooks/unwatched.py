#!/usr/bin/env python3
"""unwatched.py — a seat ending its turn with no wait on what it drives or follows is held.

A Stop hook, on every turn's end, with no skill behind it. A seat drives
the sessions it took, lib/successor.py's taken(), and follows those
lib/follow.py records. While one of them still runs, the seat's turn
ends on its one wait, or nothing would wake it when they finish or sit
idle. A turn ending with none of them left unwatched passes. Otherwise it
is held, and the seat told to arm it. A turn held once ends the second
time, so it never loops.

A wait runs when a process running tools/transcript.py wait descends from
the seat's own Claude Code process. One naming no session covers all the
seat drives and follows. One naming sessions covers those alone. A
session gone, its process ended, needs no wait: the one wait already
told it.

A paused drive arms no wait, and neither does a seat handing itself over:
its successor waits instead. Both pass. A seat hands itself over by a
press, or by session-handover, whose copy for its successor is saved in
the same turn.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import drive  # noqa: E402
import handover  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402
import transcripts  # noqa: E402

WAIT = "transcript.py wait"


def waits(pid: int) -> list:
    """What each wait under the Claude Code process `pid` covers: the
    numbers it names, or None for the one wait, which covers all."""
    procs, found = ports.table(), []
    for p, (parent, command) in procs.items():
        if WAIT not in command:
            continue
        seen = set()
        while parent and parent not in seen:
            if parent == pid:
                named = re.findall(r"(?<=\s)(\d{1,2})(?=\s|$)", command.split(WAIT, 1)[1].split(" --", 1)[0])
                found.append({f"{int(n):02d}" for n in named} or None)
                break
            seen.add(parent)
            parent = procs.get(parent, (0, ""))[0]
    return found


def began(transcript: str):
    """When the transcript's last turn began: its last record that starts
    one, transcripts.opener's. The tail is read first, the whole file only
    when the turn began before it. None when no turn is found."""
    if not os.path.isfile(transcript):
        return None
    for records in (registry.tail(transcript), transcripts.records(transcript)):
        found = None
        for d in records:
            if transcripts.opener(d):
                found = d
        if found:
            return transcripts.moment(found)
    return None


def handing_over(me: str, transcript: str) -> bool:
    """Whether seat ME saved its newest copy for a successor this turn."""
    names = handover.copies(me)
    if not names:
        return False
    try:
        saved = os.path.getmtime(os.path.join(registry.folder(me), handover.HANDOVERS, names[-1]))
    except OSError:
        return False
    at = began(transcript)
    return at is not None and saved >= at.timestamp()


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("stop_hook_active"):
        sys.exit(0)
    held = registry.entries()
    me = registry.number_of(event.get("session_id") or "", held)
    if not me or drive.state(me) == "paused" or handover.progress(me).get("step") in handover.STEPS:
        sys.exit(0)
    live = registry.claude_records()
    running = [n for n in successor.watching(me, held) if held[n].get("session_id") in live]
    mine = live.get(held[me].get("session_id")) or {}
    if not running or not mine.get("pid"):
        sys.exit(0)
    covers = waits(int(mine["pid"]))
    if None in covers:
        sys.exit(0)
    running = [n for n in running if not any(n in c for c in covers)]
    if not running or handing_over(me, event.get("transcript_path") or held[me].get("transcript", "")):
        sys.exit(0)
    them = " and ".join(running)
    print(json.dumps({"decision": "block", "reason": (
        f"You drive or follow session{'s' if len(running) > 1 else ''} {them}, and no wait covers "
        f"{'them' if len(running) > 1 else 'it'}. Arm your one wait now, in the background: "
        f"`{successor.WAIT}`. Then end your turn.")}))


if __name__ == "__main__":
    main()
