#!/usr/bin/env python3
"""agenda.py — the one door to my agenda's folder, .claude/state/agenda/.

A session writes it only on my word, and only through here. lib/agenda.py
holds its rules: an item's file, its topics, its note's shape, its column,
and the refusals.

  agenda.py list [ITEM ...]         every item, or those named: its column, phase, topics, waits and note
  agenda.py titles                  every item's title and file name, and nothing more
  agenda.py topics                  the topics, in order, each with the items under it
  agenda.py where ITEM              what ITEM waits on, what waits on it, whether it is ready, its phase, topics and Mine
  agenda.py add NAME --topics TOPIC ... [--phase PHASE] --note TEXT [--after ITEM ...]
                                    a new item I dictate, in its phase when the agenda has phases
  agenda.py under ITEM TOPIC ...    ITEM's topics, replaced
  agenda.py phase ITEM PHASE        ITEM moves to PHASE, refused while a wait joins it to another
  agenda.py link ITEM PARENT        ITEM now waits on PARENT too
  agenda.py unlink ITEM PARENT      ITEM no longer waits on PARENT
  agenda.py rename ITEM NAME        every item waiting on it follows
  agenda.py note ITEM               its note, replaced by the text on stdin, in the README's shape
  agenda.py down ITEM               dealt with: it comes down, and what waited on it moves up
  agenda.py check                   what a hand edit broke, or that nothing is

An ITEM is its file name or its name. A TOPIC is one of the topics, as "Web
app" or "web-app". A write prints what it did, then each item a new link
pushed to another column. A refusal prints its sentence and exits 1.
--dir points every verb at another folder, for tests.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import agenda  # noqa: E402


def listing(folder: str, names: list = ()) -> list:
    """Every item, or only those named, each with its note."""
    items, broken = agenda.read(folder)
    shown_only = {agenda.find(items, n) for n in names}
    out = [] if items else ["The agenda holds no item."]
    cols = agenda.columns(items)
    for i in sorted(items, key=lambda i: (cols[i], i)):
        if shown_only and i not in shown_only:
            continue
        it = items[i]
        waits = ("waits on " + ", ".join(items[p]["title"] if p in items else f"{p} (no item)" for p in it["after"])
                 if it["after"] else "waits on nothing")
        out.append(f"{it['title']} ({i}) · column {cols[i]}" + (f" · phase {it['phase']}" if it["phase"] else "")
                   + f" · under {', '.join(it['topics']) or 'no topic'} · {waits}")
        out += [f"    {line}" for line in it["note"].splitlines()]
    out += [f"Could not read: {name}" for name in broken]
    return out


def titles(folder: str) -> list:
    """Every item's title and file name, one a line, by title."""
    items, broken = agenda.read(folder)
    out = [f"{it['title']} ({i})" for i, it in sorted(items.items(), key=lambda p: p[1]["title"].lower())]
    return (out or ["The agenda holds no item."]) + [f"Could not read: {name}" for name in broken]


def topics(folder: str) -> list:
    """The topics, in order, each with the items under it, by column, then
    by title."""
    items, broken = agenda.read(folder)
    cols, out = agenda.columns(items), []
    for name in agenda.NAMES:
        under = sorted((i for i, it in items.items() if name in agenda.placed(it)),
                       key=lambda i: (cols[i], items[i]["title"].lower()))
        out.append(f"{name}: " + (f"{len(under)} item" + ("" if len(under) == 1 else "s") if under else "no item"))
        out += [f"    column {cols[i]} · {items[i]['title']} ({i})" for i in under]
    return out + [f"Could not read: {name}" for name in broken]


def where(folder: str, name: str) -> list:
    items, _ = agenda.read(folder)
    i = agenda.find(items, name)
    it, cols = items[i], agenda.columns(items)
    waiting = [o["title"] for o in items.values() if i in o["after"]]
    state = ("ready: it waits on nothing." if not it["after"] else
             "waiting on " + ", ".join(items[p]["title"] if p in items else p for p in it["after"]) + ".")
    mine = [f"Mine: {text}" for name, text in agenda.note_lines(it["note"]) if name == "Mine"]
    return [f"{it['title']} ({i}), column {cols[i]}" + (f", phase {it['phase']}" if it["phase"] else "")
            + f", under {', '.join(it['topics']) or 'no topic'}: {state}",
            *mine, "Waiting on it: " + (", ".join(waiting) if waiting else "nothing") + "."]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=agenda.FOLDER)
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("list").add_argument("items", nargs="*")
    sub.add_parser("titles")
    sub.add_parser("topics")
    sub.add_parser("where").add_argument("item")
    a = sub.add_parser("add")
    a.add_argument("name")
    a.add_argument("--topics", nargs="*", default=[])
    a.add_argument("--after", nargs="*", default=[])
    a.add_argument("--note", default="")
    a.add_argument("--phase", default="")
    u = sub.add_parser("under")
    u.add_argument("item")
    u.add_argument("topics", nargs="*")
    ph = sub.add_parser("phase")
    ph.add_argument("item")
    ph.add_argument("phase")
    for verb in ("link", "unlink"):
        v = sub.add_parser(verb)
        v.add_argument("item")
        v.add_argument("parent")
    r = sub.add_parser("rename")
    r.add_argument("item")
    r.add_argument("name")
    sub.add_parser("note").add_argument("item")
    sub.add_parser("down").add_argument("item")
    sub.add_parser("check")
    args = ap.parse_args()
    folder = args.dir

    try:
        if args.verb == "list":
            out = listing(folder, args.items)
        elif args.verb == "titles":
            out = titles(folder)
        elif args.verb == "topics":
            out = topics(folder)
        elif args.verb == "where":
            out = where(folder, args.item)
        elif args.verb == "add":
            out = agenda.add(folder, args.name, args.topics, args.after, args.note, args.phase)
        elif args.verb == "under":
            out = agenda.set_topics(folder, args.item, args.topics)
        elif args.verb == "phase":
            out = agenda.set_phase(folder, args.item, args.phase)
        elif args.verb == "link":
            out = agenda.link(folder, args.item, args.parent)
        elif args.verb == "unlink":
            out = agenda.unlink(folder, args.item, args.parent)
        elif args.verb == "rename":
            out = agenda.rename(folder, args.item, args.name)
        elif args.verb == "note":
            out = agenda.set_note(folder, args.item, sys.stdin.read())
        elif args.verb == "down":
            out = agenda.down(folder, args.item)
        elif args.verb == "check":
            found = agenda.problems(folder)
            print("\n".join(found) if found else "The agenda checks: nothing is broken.")
            sys.exit(1 if found else 0)
    except agenda.Refused as e:
        print(f"Refused. {e}", file=sys.stderr)
        sys.exit(1)
    print("\n".join(out))


if __name__ == "__main__":
    main()
