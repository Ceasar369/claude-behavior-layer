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
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import registry  # noqa: E402
import transcripts  # noqa: E402

# A move that asks me something. A Wait asks nothing.
ASKS = re.compile(r"^(Ruling|Answer|Action)\b")
# The items a move names: "item 10", "items 7 and 8", "items 1 to 4".
NAMED = re.compile(r"\bitems?\s+(\d+(?:\s*(?:,|and|to|–|-)\s*\d+)*)", re.I)


def asked(move: str) -> list:
    """The item numbers a move names, in order. "1 to 4" is four."""
    out = []
    for group in NAMED.findall(move):
        last, span = None, False
        for tok in re.findall(r"\d+|to|–|-", group):
            if not tok.isdigit():
                span = True
                continue
            n = int(tok)
            out += range(last + 1, n + 1) if span and last is not None else [n]
            last, span = n, False
    return sorted(set(out))


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


def shown(n: int, words: str) -> bool:
    return bool(re.search(rf"(?mi)^[\s>*#-]*(?:item\s+)?{n}\s*·", words))


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
    unshown = [n for n in asked(move) if not shown(n, words)]
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
