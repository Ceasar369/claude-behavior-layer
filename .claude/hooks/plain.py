#!/usr/bin/env python3
"""plain.py — a turn showing me a file's line number, or a bare item number, is held once.

A Stop hook, on every turn's end, with no skill behind it. Anything
technical reaches me in plain words, and each number a turn names is
restated there, as .claude/rules/talking.md rules.

    held:   "Release only works after Submit, milestones-rules.ts:1181."
    held:   "Items 61 and 62 wait."
    passes: "item 55, Release needs no review step"

A path with a line number passes under Done, on a sources line, and
inside a fence or a copy block: those are pictures, records and lines to
paste. An item number passes when the turn lays it out, "55 · its
title", or when its own words follow it: a comma, a "·", a colon or a
bracket. A range passes only when every item in it is laid out. A turn
held once ends the second time, so it never loops.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import items  # noqa: E402

# A file, its line, and maybe a range: "milestones-rules.ts:1181", "page.py:12-30".
LINED = re.compile(r"\b[\w./-]+\.(?:py|ts|tsx|js|jsx|md|json|swift|sh|css|html|sql|yml|yaml|txt):\d+(?:-\d+)?\b")
FENCE = re.compile(r"^\s*```")
LABEL = re.compile(r"^\s*\*\*[^*]+\*\*\s*$")


def plain_lines(text: str) -> list:
    """The lines a reader meets as prose: no fence, no copy block, no Done, no sources."""
    out, fenced, copy, done = [], False, False, False
    for line in text.split("\n"):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if "START COPY" in line or "END COPY" in line:
            copy = "START COPY" in line
            continue
        if LABEL.match(line):
            done = line.strip().strip("*").strip().lower() == "done"
            continue
        if fenced or copy or done or re.match(r"^\s*(\*\*)?sources\b", line, re.I):
            continue
        out.append(line)
    return out


def faults(text: str) -> tuple:
    lines = plain_lines(text)
    paths = [m.group(0) for line in lines for m in LINED.finditer(line)]
    bare = []
    for line in lines:
        for m in items.NAMED.finditer(line):
            after = line[m.end():m.end() + 3].lstrip()
            if after[:1] in (",", "·", ":", "(", "—", "–"):
                continue
            nums = items.numbers(m.group(1))
            if all(items.laid_out(n, text) for n in nums):
                continue
            bare.append(f"item{'s' if len(nums) > 1 else ''} {m.group(1)}")
    return paths, bare


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("stop_hook_active"):
        sys.exit(0)
    paths, bare = faults(event.get("last_assistant_message") or "")
    told = []
    if paths:
        told.append(f"Your turn shows me {', '.join(sorted(set(paths)))}. Say each in plain words instead; "
                    "a path with its line goes under Done or on a sources line only.")
    if bare:
        told.append(f"Your turn names {'; '.join(dict.fromkeys(bare))} with no title. Give each item its title "
                    "once, like \"item 55, Release needs no review step\".")
    if told:
        print(json.dumps({"decision": "block", "reason": " ".join(told) + " Then end your turn."}))


if __name__ == "__main__":
    main()
