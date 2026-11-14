#!/usr/bin/env python3
"""teams.py — one advisor's plan of teams: which teams run, in what order,
and what each waits on. Advisor 04 below; any advisor keeps its own.

  teams.py show 04                       every team, its launch list, and each shared place
  teams.py team 04 50 "screens team"    a team joins the plan, at seat 50
  teams.py wait 04 50 <<'EOF'            each line team 50 waits on joins its launch list, red
  teams.py green 04 50 2 <<'EOF'         line 2 green, its proof on stdin
  teams.py out 04 50 2 <<'EOF'           line 2 ruled out, my words on stdin
  teams.py share 04 50 "<the place>"     a place two teams share, owned by team 50
  teams.py after 04 50 40 60             team 50 waits on teams 40 and 60; none waits on nothing
  teams.py set 04 50 account=2 model=opus effort=high self=on
                                         team 50's launch choices; an empty value clears one
  teams.py drive 04 50 plan <<'EOF'      the drive recommended for team 50, its reason on stdin:
                                         keep, plan or topic
  teams.py pause 04 50                   a pause point before team 50 launches

The plan is one file in that advisor's own folder, teams.json. Its launch
choices are what team 50's launch page row takes once its list is green. A launch list
holds what one waiting team needs. Each line starts red, turns green on its
proof, and goes out on my word alone, as a finish list's line does. A team
whose every line is green or out, with at least one green, launches next.
A team with no launch list waits on nothing.

knowledge/0010-playbook/0018-advising/advising-protocols/protocol-planning-teams.md
rules it.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import registry  # noqa: E402

PLAN = "teams.json"
CHOICES = ("account", "model", "effort", "self")
DRIVES = ("keep", "plan", "topic")


def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), PLAN)


def load(nn: str) -> dict:
    """Advisor NN's plan of teams, or an empty one."""
    try:
        with open(path(nn)) as f:
            p = json.load(f)
    except (OSError, ValueError):
        p = {}
    p.setdefault("teams", [])
    p.setdefault("shared", [])
    return p


def save(nn: str, p: dict) -> None:
    tmp = path(nn) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(p, f, indent=1)
        f.write("\n")
    os.replace(tmp, path(nn))


def team(p: dict, seat: str) -> dict:
    for t in p["teams"]:
        if t["seat"] == seat:
            return t
    sys.exit(f"No team sits at {seat} in this plan.")


def ready(t: dict) -> bool:
    """Every line of its launch list green or out, at least one green."""
    lines = t.get("launch", [])
    return any(l["state"] == "green" for l in lines) and all(l["state"] != "red" for l in lines)


def shown(p: dict) -> list:
    out = []
    for t in p["teams"]:
        lines = t.get("launch", [])
        left = [l for l in lines if l["state"] != "out"]
        if not lines:
            said = "waits on nothing."
        elif ready(t):
            said = "every line green: its row goes on the launch page."
        else:
            said = f"launch list {sum(l['state'] == 'green' for l in left)} of {len(left)} green."
        out.append(f"Team {t['seat']}, {t['name']}: {said}")
        if t.get("waits"):
            out.append(f"  Waits on teams {', '.join(t['waits'])}.")
        out += [f"  {i}. {l['state']} · {l['line']}" for i, l in enumerate(lines, 1)]
        picked = [f"{k} {t[k]}" for k in CHOICES if t.get(k)]
        if picked:
            out.append(f"  Launches with {', '.join(picked)}.")
        if t.get("drive"):
            out.append(f"  Drive: {t['drive']}. {t.get('why', '')}".rstrip())
        if t.get("pause"):
            out.append("  A pause point before its launch.")
    out += [f"Shared: {s['place']}, owned by team {s['owner']}." for s in p["shared"]]
    return out or ["No plan of teams yet."]


def main() -> None:
    ap = argparse.ArgumentParser(description="One advisor's plan of teams.")
    ap.add_argument("verb", choices=["show", "team", "wait", "green", "out", "share", "after", "set", "drive", "pause"])
    ap.add_argument("nn")
    ap.add_argument("keys", nargs="*")
    args = ap.parse_args()
    nn = f"{int(args.nn):02d}"
    if not os.path.isdir(registry.folder(nn)):
        sys.exit(f"Session {nn} has no folder.")
    p = load(nn)
    if args.verb != "show":
        if not args.keys or not args.keys[0].isdigit() or len(args.keys[0]) != 2:
            sys.exit(f"{args.verb} names a team by its two-digit seat first.")
        seat = args.keys[0]
    if args.verb == "team":
        if len(args.keys) != 2 or not args.keys[1].strip():
            sys.exit('team takes a seat and a name: team NN 50 "screens team".')
        if any(t["seat"] == seat for t in p["teams"]):
            sys.exit(f"Team {seat} is already in this plan.")
        p["teams"].append({"seat": seat, "name": args.keys[1].strip(), "launch": []})
    elif args.verb == "share":
        team(p, seat)
        if len(args.keys) != 2 or not args.keys[1].strip():
            sys.exit('share takes the owning seat and the place: share NN 50 "the pages\' addresses".')
        p["shared"].append({"place": args.keys[1].strip(), "owner": seat})
    elif args.verb == "after":
        t = team(p, seat)
        for s in args.keys[1:]:
            if s == seat:
                sys.exit(f"Team {seat} cannot wait on itself.")
            team(p, s)
        t["waits"] = list(dict.fromkeys(args.keys[1:]))
    elif args.verb == "set":
        t = team(p, seat)
        pairs = [k.partition("=") for k in args.keys[1:]]
        if not pairs or any(not eq or k not in CHOICES for k, eq, _ in pairs):
            sys.exit(f"set takes key=value pairs, each key one of {', '.join(CHOICES)}.")
        for k, _, v in pairs:
            if v.strip():
                t[k] = v.strip()
            else:
                t.pop(k, None)
    elif args.verb == "pause":
        team(p, seat)["pause"] = True
    elif args.verb == "drive":
        t = team(p, seat)
        if len(args.keys) != 2 or args.keys[1] not in DRIVES:
            sys.exit(f"drive takes a seat and one of {', '.join(DRIVES)}.")
        why = sys.stdin.read().strip()
        if not why:
            sys.exit("drive takes its reason on stdin, one line.")
        t.update(drive=args.keys[1], why=why)
    elif args.verb in ("wait", "green", "out"):
        t = team(p, seat)
        lines = t.setdefault("launch", [])
        words = sys.stdin.read().strip()
        if args.verb == "wait":
            if not words:
                sys.exit("wait takes each line on stdin, one per line.")
            lines += [{"line": w.strip(), "state": "red"} for w in words.splitlines() if w.strip()]
        else:
            if len(args.keys) != 2 or not args.keys[1].isdigit() or not 1 <= int(args.keys[1]) <= len(lines):
                sys.exit(f"{args.verb} names one line of team {seat}'s launch list, 1 to {len(lines)}.")
            if not words:
                sys.exit(f"{args.verb} takes {'its proof' if args.verb == 'green' else 'my words'} on stdin.")
            lines[int(args.keys[1]) - 1].update(state=args.verb, said=words)
    if args.verb != "show":
        save(nn, p)
    print("\n".join(shown(p)))


if __name__ == "__main__":
    main()
