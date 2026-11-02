#!/usr/bin/env python3
"""checklists.py — reads one walk checklist: a section's 0-checklist.md, or
its looks/looks-checklist.md.

One reader for every tool that reads one. .claude/tools/walk-checklists.py
rebuilds them from it, and .claude/tools/walk-list-page.py draws a walk's
list from it, so a change to the checklist's shape lands here alone.

Imported, never run.
"""

import re

JOURNEY = re.compile(r"^## \[\[([^|\]]+)\|([^\]]+)\]\]\s*$")
ROW = re.compile(r"^\|\s*(?:(\d+[A-Z]*)\s*\|\s*)?(.+?)\s*\|\s*(.*?)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*$")


def read(path: str) -> tuple:
    """The lines before the first journey, then each journey: {link, name,
    rows}, each row (#, check, what, you, tester) in order. A row with no #
    column holds "" there. Header and rule rows are skipped."""
    head, journeys = [], []
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines():
            m = JOURNEY.match(line)
            if m:
                journeys.append({"link": m.group(1), "name": m.group(2), "rows": []})
            elif not journeys:
                head.append(line)
            elif (r := ROW.match(line)) and r.group(2) not in ("#", "Step", "Check", "---") \
                    and not r.group(2).startswith("-"):
                journeys[-1]["rows"].append((r.group(1) or "",) + r.group(2, 3, 4, 5))
    return head, journeys
