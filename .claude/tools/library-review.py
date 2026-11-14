#!/usr/bin/env python3
"""library-review.py — whether I reviewed each word and graph of my library.

An item I mark reviewed keeps a copy of its file's text and of its home,
the names of the chapter, subchapter and section it sits under, never
their numbers, which shift whenever a word is added. Its state then reads
from that copy:

  new      never reviewed, or marked not reviewed since
  ok       reviewed, and its text and home still match the copy
  changed  reviewed, and its text or its home differs since

An item is its file, from library/ without .md: `port`, or
`graphs/how-a-url-is-read` for a graph. The record is one file in
.claude/state/library-review/. The library page draws each state; 1100
posts its button here, the app door calls marked() and so does this
command:

  library-review.py set <item> reviewed|not-reviewed

<item> is a number as the rail prints it, like 1.2.5 or 1.2.A, a file as
above, or a name, like Port.
"""

import fcntl
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import registry  # noqa: E402

FOLDER = os.path.join(registry.ROOT, ".claude", "state", "library-review")
RECORD = os.path.join(FOLDER, "reviews.json")
TO = {"reviewed": True, "not-reviewed": False}


def load() -> dict:
    """Each reviewed item, by its file: {text, home, at}."""
    try:
        with open(RECORD, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def item(row: dict) -> str:
    """A rail row's item: its file, from library/ without .md."""
    return f"graphs/{row['slug']}" if row["kind"] == "graph" else row["slug"]


def home(rows: list, row: dict) -> str:
    """The names a row sits under, outermost first, never their numbers."""
    by = {r["n"]: r for r in rows if r["kind"] in ("chapter", "subchapter", "section")}
    names, up = [], row["up"]
    while up in by:
        names.insert(0, by[up]["name"])
        up = by[up]["up"]
    return " › ".join(names)


def text_of(lib, row: dict):
    folder = os.path.join(lib.LIBRARY, lib.GRAPHS) if row["kind"] == "graph" else lib.LIBRARY
    return lib.read(os.path.join(folder, f"{row['slug']}.md"))


def state(kept, text, where: str) -> str:
    """new, ok or changed: an item's copy, or None, against its file now."""
    if not kept:
        return "new"
    return "ok" if kept["text"] == (text or "") and kept["home"] == where else "changed"


def states(rows: list, text) -> dict:
    """Every word's and graph's state, by its item, with the time I
    reviewed it: {item: (state, at)}. text(row) is its file now."""
    record, out = load(), {}
    for r in rows:
        if r["kind"] in ("word", "graph"):
            got = record.get(item(r))
            out[item(r)] = (state(got, text(r), home(rows, r)), got["at"] if got else "")
    return out


def find(rows: list, said: str):
    """The word or graph a number, a file or a name picks, or None."""
    said = said.strip().removeprefix("#").removesuffix(".md").removeprefix("library/")
    kinds = [r for r in rows if r["kind"] in ("word", "graph")]
    for test in (lambda r: r["n"].casefold() == said.casefold(),
                 lambda r: item(r) == said.lower(),
                 lambda r: r["name"].casefold() == said.casefold()):
        if got := next((r for r in kinds if test(r)), None):
            return got
    return None


def kept(change) -> None:
    """Changes the record under a lock, then replaces it whole, so a
    session, the page and the app door never write over each other."""
    os.makedirs(FOLDER, exist_ok=True)
    with open(os.path.join(FOLDER, "lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        record = load()
        change(record)
        spare = RECORD + ".new"
        with open(spare, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(spare, RECORD)


def mark(key: str, text: str, where: str, at: str = "") -> None:
    """Keeps an item reviewed, as `text` under `where`, at `at` or now."""
    kept(lambda r: r.__setitem__(key, {"text": text or "", "home": where,
                                       "at": at or time.strftime("%Y-%m-%d %H:%M")}))


def unmark(key: str) -> None:
    kept(lambda r: r.pop(key, None))


def marked(said: str, to: str) -> tuple:
    """Marks the item `said` names reviewed or not reviewed: (ok, sentence)."""
    if to not in TO:
        return False, f"'{to}' is refused. Say reviewed or not-reviewed."
    lib = page.tool("library-page")
    rows = lib.numbered(lib.tree(lib.read(os.path.join(lib.LIBRARY, lib.MOC)) or ""))
    row = find(rows, said)
    if not row:
        return False, f"The library holds no word or graph {said}."
    key = item(row)
    if TO[to]:
        mark(key, text_of(lib, row), home(rows, row))
    else:
        unmark(key)
    what = "Graph" if row["kind"] == "graph" else "Word"
    return True, f"{what} {row['n']}, {row['name']}, is marked {'reviewed' if TO[to] else 'not reviewed'}."


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] != "set":
        sys.exit("Use: library-review.py set <item> reviewed|not-reviewed")
    ok, said = marked(sys.argv[2], sys.argv[3])
    print(said)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
