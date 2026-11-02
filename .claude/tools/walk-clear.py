#!/usr/bin/env python3
"""walk-clear.py — keeps a walker's evidence with its lead, then empties its walk/.

  walk-clear.py NN AREA/SECTION/JOURNEY   keep walk/ with the lead, then delete it
  walk-clear.py NN keep                   keep walk/ with the lead alone: a walk's end

A walker runs it before every journey, approved or not, a journey walked
again included. Its whole walk/ is first kept in its lead's folder, the
lead being walk.json's "main". Each walker keeps into a folder of its own,
walkers/<NN>-<MM-DD-HHMM>/, named by its seat and its start: the time it
wrote walk.json, once, as it got ready. So a new walker in the same seat
never mixes into the last one's. Each journey kept replaces that
journey's kept folder whole, so it holds its last pass alone, never an
older save beside it. Then every journey's screenshots and page text go
from walk/, this journey's from a pass before too, and so does every file
its browser wrote in its playwright/: page snapshots and console logs. So
its Screenshots tab holds this pass of this journey alone, and no check is
judged on a file left from the pass before. The playwright/ folder itself
stays: the browser writes into it.

A journey's folder is walk/<area>/<section>/<journey>/: two areas may hold
a section and a journey of one name.

A lead whose folder is gone gets nothing: making it would hold its number.
"""

import glob
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import registry  # noqa: E402

NAME = re.compile(r"[\w-]+")


def clear(folder: str) -> list:
    """Delete every entry of folder, and say each name gone."""
    gone = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        gone.append(name)
    return gone


def keep(nn: str) -> str:
    """Walker NN's walk/ and walk.json, kept in its lead's walkers/<NN>-<start>/,
    each journey replacing its kept folder whole. Returns where, or "" when
    walk.json names no lead whose folder stands."""
    mine = registry.folder(nn)
    card = os.path.join(mine, "walk.json")
    try:
        with open(card) as f:
            lead = str(json.load(f).get("main", ""))
        start = time.strftime("%m-%d-%H%M", time.localtime(os.path.getmtime(card)))
    except (OSError, ValueError, AttributeError):
        return ""
    if not re.fullmatch(r"\d{2}", lead) or not os.path.isdir(registry.folder(lead)):
        return ""
    to = os.path.join(registry.folder(lead), "walkers", f"{int(nn):02d}-{start}")
    os.makedirs(to, exist_ok=True)
    walk = os.path.join(mine, "walk")
    for journey in glob.glob(os.path.join(walk, "*", "*", "*", "")):
        kept = os.path.join(to, "walk", os.path.relpath(journey, walk))
        shutil.rmtree(kept, ignore_errors=True)
        shutil.copytree(journey, kept)
    shutil.copy2(card, to)
    return to


def main():
    nn, what = sys.argv[1:] if len(sys.argv) == 3 else ("", "")
    parts = what.strip("/").split("/")
    if not nn.isdigit() or (what != "keep" and (len(parts) != 3 or not all(NAME.fullmatch(p) for p in parts))):
        sys.exit("walk-clear.py NN AREA/SECTION/JOURNEY, like: walk-clear.py 11 web-app/authentication/sign-up"
                 "\nwalk-clear.py NN keep, at a walk's end")
    to = keep(nn)
    kept = (f"Kept walk/ in {os.path.relpath(to, registry.ROOT)}/." if to else
            "Kept nothing: walk.json names no lead whose folder stands.")
    if what == "keep":
        print(kept)
        return
    mine = registry.folder(nn)
    gone = [f"walk/{g}" for g in clear(os.path.join(mine, "walk"))]
    browser = clear(os.path.join(mine, "playwright"))
    print(f"{kept} Deleted {', '.join(gone) or 'nothing in walk/'}, and {len(browser)} files in playwright/. "
          f"walk/{what.strip('/')}/ starts empty.")


if __name__ == "__main__":
    main()
