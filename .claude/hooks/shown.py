#!/usr/bin/env python3
"""shown.py — a turn asking me to rule an item it never shows is held.

A Stop hook, on every turn's end, with no skill behind it.
.claude/rules/talking.md rules that what a move asks shows in its turn,
whole, above it. A move asking me something names its items by number:
"Ruling: agree item 10", "items 7 and 8", "items 1 to 4". Each needs its
heading in the turn's words, as clarify-items lays one out: "10 · its
title". One missing → the turn is held, and the session told to lay it
out. A turn held once ends the second time, so it never loops.

The turn is every word the session said since what started it: my
prompt, or a background task's notice. Its last words come from Claude
Code itself, as last_assistant_message: the transcript may not hold them
yet when this runs. A turn whose start lies past the transcript's tail
passes: what it said early cannot be read.

A ruling with no number passes unchecked. Only the rule covers it.

An item on the session's own wave still open on my page passes: that
wave was laid out whole when it was written, and is named, never shown
again.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import items  # noqa: E402
import registry  # noqa: E402
import transcripts  # noqa: E402
import waves  # noqa: E402


def on_page(session_id: str) -> set:
    """The item numbers of this session's own wave still open on my page."""
    me = registry.number_of(session_id or "", registry.entries())
    if not me:
        return set()
    wave, _, head, listed = waves.newest(me)
    if not wave or head.get("sent") or head.get("closed"):
        return set()
    return {int(it["n"]) for it in listed if str(it.get("n", "")).isdigit()}

# A move that asks me something. A Wait asks nothing.
ASKS = re.compile(r"^(Ruling|Answer|Action)\b")


def said(path: str):
    """Every word the transcript holds of this turn. None when its start is out of reach."""
    words = []
    for d in reversed(registry.tail(path)):
        if d.get("isCompactSummary"):
            return None
        if transcripts.opener(d):
            return "\n".join(reversed(words))
        if d.get("type") == "assistant":
            words.append(transcripts.texts(d.get("message") or {}))
    return None


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("stop_hook_active"):
        sys.exit(0)
    before = said(event.get("transcript_path") or "")
    if before is None:
        sys.exit(0)
    last = event.get("last_assistant_message") or ""
    words = before + "\n" + last
    moves = transcripts.MOVE.findall(last or words)
    move = moves[-1].replace("**", "").strip() if moves else ""
    if not ASKS.match(move):
        sys.exit(0)
    unshown = [n for n in items.asked(move) if not items.laid_out(n, words)]
    if unshown:
        open_now = on_page(event.get("session_id") or "")
        unshown = [n for n in unshown if n not in open_now]
    if not unshown:
        sys.exit(0)
    named = " and ".join(str(n) for n in unshown)
    them = "it" if len(unshown) == 1 else "each"
    print(json.dumps({"decision": "block", "reason": (
        f"Your move asks item{'s' if len(unshown) > 1 else ''} {named}. This turn never shows {them}. "
        f"Lay {them} out whole, above your move, under \"{unshown[0]} · its title\". "
        "Every part it was laid out with, and where I open its picture. "
        "Then end your turn.")}))


if __name__ == "__main__":
    main()
