#!/usr/bin/env python3
"""prototype.py — the subject a session holds, and the end of a subject.

Every prototype lives in code/prototypes/, one Vite app, which band 00
serves on 1400 for every session. The app draws the prototype page at /,
for the subject and session its query names, and every variation at its
route, so the page and the variations share one address. With no subject
named, / draws the library. 1100 frames a subject while a running session
holds it, not locked in. Without the app, every verb says so in one
line, and does nothing.

A subject is two folders. code/prototypes/<subject>/ holds one g<N>.json
per generation. code/prototypes/src/routes/<subject>/ holds one
g<N>/v<M>.tsx per variation.

  prototype.py hold 05 proposal-header         session 05 holds that subject, and no other session does
  prototype.py status 05                       1400, 05's subject, its winner while locked, up or down
  prototype.py lock-in proposal-header g2/v3   keeps g2/v3, deletes every other variation
  prototype.py lock-in proposal-header g2/v3 --looks 1,4   the same; a variation with groups keeps one look in each
  prototype.py build 05 proposal-header        session 05 builds that winner, whoever made it: its stop removes it
  prototype.py remove proposal-header          deletes the subject whole, and every session's hold on it
  prototype.py remove rail-teams --winner      the same for a locked winner. Without --winner, it refuses

Writing a generation holds its subject too, through hooks/prototype-hold.py.
The subject held sits in the session's own folder, so its stop deletes it
with the rest. /prototype-save lets a subject go, and /prototype-continue
takes one.
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import ports  # noqa: E402
from prototypes import (APP, LOCKED, NO_APP, PORT, ROUTES, SUBJECT, TAKEN, build, building, hold, looks,  # noqa: E402
                        remove, subject_of, winner)

PICK = re.compile(r"g(\d+)/(v\d+)")
LOOKS = re.compile(r"\d+(?:\.\d+)?(?:,\d+(?:\.\d+)?)*")


def named(subject: str) -> str:
    if not SUBJECT.fullmatch(subject) or subject in TAKEN:
        sys.exit(f"{subject!r} is not a subject name. One to three words, kebab-case.")
    return subject


def keep_looks(winner: dict, v: str, named: str) -> str:
    """Keep one look in each group of the winner, and drop the rest from its
    record. A look with no group stays. A kept look no longer competes, so it
    loses its group. The losing looks, as words, or exits with why."""
    groups, shown = looks(winner)
    numbers = {g: [str(l["n"]) for l in ls] for g, ls in groups.items()}
    if not groups:
        if named:
            sys.exit(f"{v} holds no groups. Lock it in whole, with no --looks.")
        return ""
    if not LOOKS.fullmatch(named):
        sys.exit(f"{v} holds groups {', '.join(groups)}. Name one look in each: --looks 1,4.")
    chosen = {}
    for n in named.split(","):
        home = [g for g, ns in numbers.items() if n in ns]
        if not home:
            sys.exit(f"{v} holds no look {n} in a group. A look with no group is never picked.")
        if home[0] in chosen:
            sys.exit(f"Group {home[0]} takes one look. {chosen[home[0]]} and {n} compete.")
        chosen[home[0]] = n
    for g in groups:
        if g not in chosen:
            sys.exit(f"Group {g} is still open. Name its look, or make the next generation.")
    lost = [str(l["n"]) for ls in groups.values() for l in ls if str(l["n"]) not in chosen.values()]
    kept = [l for l in winner["looks"] if isinstance(l, dict) and l.get("n") not in (None, "")
            and (not l.get("group") or str(l["n"]) in chosen.values())]
    winner["looks"] = [{k: x for k, x in l.items() if k != "group"} for l in kept]
    return ", ".join(lost)


def lock_in(subject: str, pick: str, looks: str = "") -> str:
    """Keep one variation, marked as the winner. Every other variation and
    generation goes. A helper, a file or folder named with a leading "-",
    stays: the winner may import it. A variation with groups of looks keeps
    one look in each: the others leave its record, and the session cuts
    them from its route."""
    m = PICK.fullmatch(pick)
    if not m:
        sys.exit(f"{pick!r} names no variation. Write it as g2/v3.")
    g, v = int(m.group(1)), m.group(2)
    home, routes = os.path.join(APP, subject), os.path.join(ROUTES, subject)
    kept = os.path.join(home, f"g{g}.json")
    try:
        with open(kept) as f:
            gen = json.load(f)
    except OSError:
        sys.exit(f"{subject} holds no generation {g}.")
    winner = [x for x in gen["variations"] if x["id"] == v]
    if not winner:
        sys.exit(f"{subject} g{g} holds no {v}.")
    lost = keep_looks(winner[0], v, looks)
    gone = 0
    for path in glob.glob(os.path.join(home, "g*.json")):
        if path != kept:
            os.remove(path)
            gone += 1
    gen["variations"] = winner
    gen[LOCKED] = True
    with open(kept, "w") as f:
        json.dump(gen, f, indent=2, ensure_ascii=False)
        f.write("\n")
    keep = os.path.join(routes, f"g{g}", f"{v}.tsx")
    dropped = 0
    for path in glob.glob(os.path.join(routes, "**", "*"), recursive=True):
        helper = any(part.startswith("-") for part in os.path.relpath(path, routes).split(os.sep))
        if os.path.isfile(path) and path != keep and not helper:
            os.remove(path)
            dropped += 1
    for d in sorted(glob.glob(os.path.join(routes, "**"), recursive=True), reverse=True):
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    many = lambda n, word: f"{n} other {word}{'' if n == 1 else 's'}"
    cut = ""
    if lost:
        many_lost = "," in lost
        cut = (f" {'Looks' if many_lost else 'Look'} {lost} left its record. "
               f"Cut {'them' if many_lost else 'it'} from its route.")
    return (f"Locked in {subject} g{g}/{v}. {many(dropped, 'variation')} and "
            f"{many(gone, 'generation')} deleted.{cut}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    s = sub.add_parser("hold")
    s.add_argument("nn")
    s.add_argument("subject")
    sub.add_parser("status").add_argument("nn")
    k = sub.add_parser("lock-in")
    k.add_argument("subject")
    k.add_argument("pick")
    k.add_argument("--looks", default="")
    b = sub.add_parser("build")
    b.add_argument("nn")
    b.add_argument("subject")
    r = sub.add_parser("remove")
    r.add_argument("subject")
    r.add_argument("--winner", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(APP):
        sys.exit(NO_APP)
    if args.verb == "hold":
        hold(args.nn, named(args.subject))
        print(f"{PORT} · {args.subject} · " + ("up" if ports.answering(PORT) else "down"))
    elif args.verb == "status":
        # A locked subject says so, and what follows: 1100 frames no tab for it.
        subject = subject_of(args.nn)
        pick = winner(subject) if subject else ""
        print(f"{PORT} · {subject or 'no subject'} · "
              + (f"locked in {pick}, so 1100 shows no Prototype tab · " if pick else "")
              + ("up" if ports.answering(PORT) else "down"))
    elif args.verb == "lock-in":
        print(lock_in(named(args.subject), args.pick, args.looks))
    elif args.verb == "build":
        # Only a winner is built. Whoever made it, the session coding it marks it.
        subject = named(args.subject)
        if not winner(subject):
            sys.exit(f"{subject} holds no winner, so nothing is built. Nothing was marked.")
        build(args.nn, subject)
        if subject not in building(args.nn):
            sys.exit(f"Session {args.nn} has no folder. Nothing was marked.")
        print(f"Session {args.nn} builds {subject}: its stop removes it.")
    else:
        subject = named(args.subject)
        pick = winner(subject)
        if pick and not args.winner:
            sys.exit(f"{subject} keeps its winner, {pick}, until its real version is built. "
                     "Add --winner to remove it anyway. Nothing was removed.")
        print(remove(subject))


if __name__ == "__main__":
    main()
