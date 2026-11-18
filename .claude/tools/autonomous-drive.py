#!/usr/bin/env python3
"""autonomous-drive.py — a drive prepared whole, so nothing waits on my press.

  autonomous-drive.py check 05          every line the drive needs, each holding or naming its fix
  autonomous-drive.py start 05          the check, then the drive marked running, once every line holds
  autonomous-drive.py account 05        the account an extra session takes
  autonomous-drive.py row 05 50         team 50's row, alone on 05's launch page, for schedule.py fire
  autonomous-drive.py resume 05         "Resume the drive." past a pause point before a team
  autonomous-drive.py take 50 05        team 50 takes the plan 05 wrote for it, once 50 is claimed
  autonomous-drive.py end 05            the drive marked ended

A drive's driver holds its plan in its own folder. Over one session or
one team, that is its stages.json: one session is a plan of one mission.
Over several teams, it is its teams.json, as tools/teams.py keeps it. A
team already launched holds its plan in its own folder. A team not
launched yet has its plan written in the driver's autonomous-drive/<seat>/:
stages.json and missions/, as the driver's own would be. At launch, take
moves it into the team's folder, so the plan has one writer at a time.

Each mission not yet launched names the account, model and effort its
launch row takes, in its stages.json entry. Each team does too, in
teams.json, as teams.py set keeps them. One folder holds one launch
page, so a stage's page is written from its missions as it goes out.

The check reads, and never writes:

  plans      each plan stands, runs in order, and holds a finish list
  missions   each mission is written whole, beside its objectives file
  run        every objective, finish line and launch-list line is a Run line
  needs me   no mission thinks, prototypes, discovers or walks with me
  launches   every launch named its account, model and effort, none on an
             account pinned to another family
  waves      no wave of the driver's, nor of a launched team's, is open
  usage      shown, never failing: each account the drive uses, with only
             the windows that apply, each its percent used and its reset

A window an account never reported shows as unread. A model's own window
shows only when the drive runs that model and the account reports it.

The check also lists each pause point. One before a team, `"pause": true`
in teams.json, is held here: row pauses the drive there, in its own
drive.json, launches nothing until resume, and exits lib/drive.py's
PAUSED. A plan's own pause points are tools/drive.py's.

An extra session goes on System's default account, the order's next
turn, read without taking it. Capped, it goes on the account with the
most left: the lowest of its windows' highest percent used.

knowledge/0010-playbook/0011-assisting/assisting-protocols/autonomous-driving-protocols/
rules it.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import drive  # noqa: E402
import finish  # noqa: E402
import models  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import waves  # noqa: E402

HOME = "autonomous-drive"
RECORD = "drive.json"
TEAMS = "teams.json"
WINDOWS = ("five_hour", "seven_day")
CHOICES = ("account", "model", "effort")
# A mission naming one of these needs me while it runs.
NEEDS_ME = re.compile(r"/3-thinker|/4-prototype|/7-walk|protocol-my-walk")
RUN = re.compile(r"Run: `[^`]+`")


def rel(p: str) -> str:
    return os.path.relpath(p, registry.ROOT)


def home(nn: str) -> str:
    return os.path.join(registry.folder(nn), HOME)


def load(p: str) -> dict:
    try:
        with open(p) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return got if isinstance(got, dict) else {}


def driver(nn: str) -> str:
    """The seat whose drive launched team NN, as take recorded it. None gives ""."""
    return str(load(os.path.join(home(nn), RECORD)).get("by", ""))


def plans_of(nn: str) -> list:
    """Each plan the drive runs, as (whose, its stages.json path, its plan):
    the driver's own, then each team's of its teams.json."""
    out = []
    own = os.path.join(registry.folder(nn), plans.PLAN)
    if os.path.isfile(own):
        out.append((f"Session {nn}'s plan", own, load(own)))
    for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []):
        launched = os.path.join(registry.folder(t["seat"]), plans.PLAN)
        p = launched if os.path.isfile(launched) else os.path.join(home(nn), t["seat"], plans.PLAN)
        out.append((f"Team {t['seat']}'s plan", p, load(p)))
    return out


def missions(p: dict) -> list:
    return [m for s in p.get("stages", []) for m in s.get("missions", [])]


def objectives(m: dict) -> str:
    """Mission M's objectives file: missions/<id>-objectives.md, beside its file."""
    return os.path.join(registry.ROOT, os.path.dirname(m.get("file", "")), f"{m['id']}-objectives.md")


def text(p: str) -> str:
    try:
        with open(p) as f:
            return f.read()
    except OSError:
        return ""


# ---- each line of the check -------------------------------------------------------

def check_plans(nn: str) -> list:
    held = plans_of(nn)
    if not held:
        return [f"Session {nn} holds no plan: write its stages.json, or its teams.json for several teams."]
    out = []
    for whose, path, p in held:
        if not missions(p):
            out.append(f"{whose} is not written: {rel(path)} holds no mission.")
            continue
        if plans.opened(p):
            out.append(f"{whose} is open: its stages close on my word alone. Run it in order.")
        if not p.get("finish"):
            out.append(f"{whose} holds no finish list: keep it through `drive.py finish`.")
    for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []):
        if t.get("waits") and not t.get("launch"):
            out.append(f"Team {t['seat']} waits on teams {', '.join(t['waits'])}, with no launch list: "
                       f"keep one through `teams.py wait`.")
    return out


def check_missions(nn: str) -> list:
    out = []
    for whose, _, p in plans_of(nn):
        for m in missions(p):
            if m.get("session"):
                continue
            body = text(os.path.join(registry.ROOT, m.get("file", "")))
            if not body:
                out.append(f"{whose}: {m['id']}'s mission is not written: {m.get('file') or 'no file named'}.")
            elif body.splitlines()[0].rstrip().endswith("· notes"):
                out.append(f"{whose}: {m['id']}'s mission is still notes: write it whole, through `assistant-mission`.")
            if not os.path.isfile(objectives(m)):
                out.append(f"{whose}: {m['id']} has no objectives file: {rel(objectives(m))}.")
    return out


def check_run(nn: str) -> list:
    out = []
    for whose, _, p in plans_of(nn):
        for m in missions(p):
            if m.get("session") or not os.path.isfile(objectives(m)):
                continue
            lines = text(objectives(m)).splitlines()
            for i, line in enumerate(lines):
                if not re.match(r"\s*- \[[ x]\] ", line):
                    continue
                proof = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
                if proof.startswith("Yours:"):
                    out.append(f"{whose}: {m['id']}'s objective on line {i + 1} is a Yours line: prove it "
                               f"before the drive, or keep {m['id']} in a regular drive.")
                elif not RUN.match(proof):
                    out.append(f"{whose}: {m['id']}'s objective on line {i + 1} has no Run line.")
        for k, l in enumerate(p.get("finish", []), 1):
            if l.get("state") == "red" and not RUN.search(l.get("line", "")):
                out.append(f"{whose}: finish line {k} has no Run command: {l.get('line', '')}")
    for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []):
        for k, l in enumerate(t.get("launch", []), 1):
            if l.get("state") == "red" and not RUN.search(l.get("line", "")):
                out.append(f"Team {t['seat']}: launch-list line {k} has no Run command: {l.get('line', '')}")
    return out


def check_needs_me(nn: str) -> list:
    out = []
    for whose, _, p in plans_of(nn):
        for m in missions(p):
            if m.get("session"):
                continue
            hit = NEEDS_ME.search(text(os.path.join(registry.ROOT, m.get("file", ""))))
            if hit or "discovery" in m.get("name", "").lower():
                out.append(f"{whose}: {m['id']} needs me while it runs ({hit.group(0) if hit else 'discovery'}): "
                           f"keep it in a regular drive.")
    return out


def family(model: str) -> str:
    return models.family(model) or model


def pin_clash(account: str, model: str) -> bool:
    """Whether ACCOUNT is pinned to a family other than MODEL's: its sessions would run another model."""
    pinned = accounts.pinned(account)
    return bool(pinned) and family(pinned) != family(model)


def launches(nn: str) -> list:
    """Each launch the drive makes, as (what, its choices)."""
    out = []
    for whose, _, p in plans_of(nn):
        out += [(f"{whose}: {m['id']}", m) for m in missions(p) if not m.get("session")]
    for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []):
        if not os.path.isfile(os.path.join(registry.folder(t["seat"]), registry.RECORD)):
            out.append((f"Team {t['seat']}'s row", t))
    return out


def check_launches(nn: str) -> list:
    out = []
    for what, c in launches(nn):
        left = [k for k in CHOICES if not c.get(k)]
        if left:
            out.append(f"{what} names no {' and no '.join(left)}.")
        elif str(c["account"]) not in accounts.KNOWN:
            out.append(f"{what} names account {c['account']}, which this Mac does not hold.")
        elif pin_clash(str(c["account"]), c["model"]):
            out.append(f"{what} runs {c['model']} on account {c['account']}, pinned to "
                       f"{family(accounts.pinned(str(c['account'])))}.")
    return out


def check_waves(nn: str) -> list:
    seats = [nn] + [t["seat"] for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", [])
                    if os.path.isdir(registry.folder(t["seat"]))]
    out = []
    for s in seats:
        k, _, _ = waves.open_wave(s)
        if k:
            out.append(f"Session {s}'s wave {k} is open: send it, or close it.")
    return out


# ---- usage ----------------------------------------------------------------------

def capped(w: dict, now: float) -> bool:
    return isinstance(w, dict) and w.get("used_percentage", 0) >= 100 and w.get("resets_at", 0) > now


def windows(account: str, families: set) -> list:
    """The windows that apply to ACCOUNT, as (name, window or None): five-hour,
    seven-day, then each model's own it reports for a family the drive runs."""
    got = finish.limits(account)
    own = sorted(k for k in got if k not in WINDOWS and any(f and f in k for f in families))
    return [(k, got.get(k) if isinstance(got.get(k), dict) and "used_percentage" in got.get(k, {}) else None)
            for k in (*WINDOWS, *own)]


def used(account: str, families: set) -> float:
    """ACCOUNT's highest percent used among its windows read. 100 when capped, or none read."""
    now = time.time()
    read = [w for _, w in windows(account, families) if w]
    if not read or any(capped(w, now) for w in read):
        return 100.0
    return max(float(w["used_percentage"]) for w in read)


def default_account() -> str:
    """The account System's order gives the next launch, read without taking its turn."""
    d = accounts.read()
    return d["order"][d["next"]] if d["order"] else accounts.FALLBACK


def extra_account(model: str = "") -> str:
    """The account an extra session takes: the default, unless capped, else the most left."""
    model = model or accounts.model()
    fams = {family(model)}
    now = time.time()
    first = default_account()
    if not any(capped(w, now) for _, w in windows(first, fams) if w) and not pin_clash(first, model):
        return first
    free = [a for a in accounts.KNOWN if not pin_clash(a, model)]
    return min(free or accounts.KNOWN, key=lambda a: (used(a, fams), a))


def when(epoch: float) -> str:
    """A reset on this Mac's clock, and how far it is from now."""
    left = max(0, int(epoch - time.time()) // 60)
    far = f"{left // 1440} days" if left >= 2880 else f"{left // 60} hours" if left >= 120 else f"{left} minutes"
    return f"{time.strftime('%b %-d at %H:%M', time.localtime(epoch))}, in {far}"


def usage(nn: str) -> list:
    picked = launches(nn)
    fams = {family(c["model"]) for _, c in picked if c.get("model")} | {family(accounts.model())}
    first = default_account()
    held = sorted({str(c["account"]) for _, c in picked if c.get("account")} | {first})
    out = []
    for a in held:
        if a not in accounts.KNOWN:
            continue
        n = sum(str(c.get("account")) == a for _, c in picked)
        shown = []
        for name, w in windows(a, fams):
            if not w:
                shown.append(f"{name} unread")
                continue
            reset = f", resets {when(w['resets_at'])}" if w.get("resets_at") else ""
            shown.append(f"{name} {w['used_percentage']}% used{reset}")
        tail = " System's default, for extra work." if a == first else ""
        out.append(f"  Account {a}, {n} launch{'es' if n != 1 else ''}: {'; '.join(shown)}.{tail}")
    out.append(f"  Extra work goes on account {extra_account()}.")
    return out


def points(nn: str) -> list:
    """Each pause point the drive holds: after a stage, after a mission, before a team."""
    out = []
    for whose, _, p in plans_of(nn):
        for i, s in enumerate(p.get("stages", [])):
            out += [f"  {whose}: after {m['id']}." for m in s.get("missions", []) if m.get("pause")]
            out += [f"  {whose}: after stage {chr(65 + i)}."] if s.get("pause") else []
    out += [f"  Before team {t['seat']} launches."
            for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []) if t.get("pause")]
    return out or ["  None."]


LINES = (("Every plan written", check_plans), ("Every mission written", check_missions),
         ("Every objective a Run line", check_run), ("No mission needs me", check_needs_me),
         ("Every launch's account, model and effort set", check_launches), ("Every wave sent", check_waves))


def check(nn: str) -> tuple:
    """Each line, holding or with its gaps, then usage. Whether every line holds."""
    out, every = [], True
    for title, run in LINES:
        gaps = run(nn)
        every &= not gaps
        out.append(f"{title}: {'fails' if gaps else 'holds'}.")
        out += [f"  {g}" for g in gaps]
    out += ["Usage:"] + usage(nn) + ["Pause points:"] + points(nn)
    out.append("Ready: every line holds." if every else "Not ready: fix each line that fails, then check again.")
    return out, every


# ---- the drive, its launches and its end ----------------------------------------

def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def write(p: str, d: dict) -> None:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        json.dump(d, f, indent=1)
        f.write("\n")
    os.replace(p + ".tmp", p)


def row(nn: str, seat: str) -> tuple:
    """Team SEAT's row, alone on NN's launch page, its first message the take:
    what to say, and whether a pause point held it instead."""
    import launch  # its iTerm imports cost a second, so only a row loads it
    t = next((t for t in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", []) if t["seat"] == seat), None)
    if not t:
        sys.exit(f"No team sits at {seat} in session {nn}'s plan of teams.")
    if not os.path.isfile(os.path.join(home(nn), seat, plans.PLAN)):
        sys.exit(f"Team {seat}'s plan is not in {rel(os.path.join(home(nn), seat))}/.")
    d = load(os.path.join(home(nn), RECORD))
    if d.get("state") == "paused":
        sys.exit(f"The autonomous drive is paused before team {d.get('at')}: nothing launches until \"Resume the drive.\"")
    if t.get("pause") and seat not in d.get("passed", []):
        write(os.path.join(home(nn), RECORD), {**d, "state": "paused", "at": seat,
                                               "passed": d.get("passed", []) + [seat]})
        done = [f"team {x['seat']}" for x in load(os.path.join(registry.folder(nn), TEAMS)).get("teams", [])
                if load(os.path.join(registry.folder(x["seat"]), "drive.json")).get("state") == "ended"]
        return (f"Pause point reached: before team {seat} launches. Nothing new launches.\n"
                f"Finished: {', '.join(done) or 'no team yet'}. Look at each team's report.md.\n"
                f"Next: tell me so, then wait. \"Resume the drive.\" → `autonomous-drive.py resume {nn}`, "
                "then this row again."), True
    with launch.LOCK:
        if launch.read(nn):
            sys.exit(f"Session {nn}'s launch page holds rows: fire or clear them first.")
        launch.save(nn, [{"n": seat, "name": t["name"], "message": f"/autonomous-drive take {nn}",
                          **{k: str(t[k]) for k in CHOICES}}])
    return f"Team {seat}'s row is on session {nn}'s launch page. Next: `python3 .claude/tools/schedule.py fire {nn}`.", False


def take(seat: str, nn: str) -> list:
    """Team SEAT takes the plan NN wrote for it: its files move into SEAT's
    folder, each path naming the new place, each mission unlaunched."""
    src, dst = os.path.join(home(nn), seat), registry.folder(seat)
    if not os.path.isfile(os.path.join(src, plans.PLAN)):
        sys.exit(f"Session {nn} holds no plan for team {seat}.")
    if not os.path.isfile(os.path.join(dst, registry.RECORD)):
        sys.exit(f"Seat {seat} is not claimed yet.")
    if os.path.exists(os.path.join(dst, plans.PLAN)):
        sys.exit(f"Session {seat} already holds a plan.")
    old, new = rel(src) + "/", rel(dst) + "/"
    for here, _, files in os.walk(src):
        for name in files:
            frm = os.path.join(here, name)
            to = os.path.join(dst, os.path.relpath(frm, src))
            os.makedirs(os.path.dirname(to), exist_ok=True)
            with open(frm) as f:
                body = f.read().replace(old, new)
            if name == plans.PLAN:
                p = json.loads(body)
                for m in missions(p):
                    for k in ("queued", "session", "title"):
                        m.pop(k, None)
                body = json.dumps(p, indent=1) + "\n"
            with open(to, "w") as f:
                f.write(body)
    shutil.rmtree(src)
    write(os.path.join(home(seat), RECORD), {"by": nn, "started": stamp()})
    p = plans.plan(seat)
    return [f"Team {seat} holds its plan: {len(p.get('stages', []))} stages, {len(missions(p))} missions.",
            "Next: run `/1-assistant drive plan`."]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["check", "start", "account", "row", "resume", "take", "end"])
    ap.add_argument("nn")
    ap.add_argument("other", nargs="?", default="")
    args = ap.parse_args()
    nn = f"{int(args.nn):02d}"
    if not os.path.isdir(registry.folder(nn)):
        sys.exit(f"Session {nn} has no folder.")
    if args.verb in ("row", "take") and not re.fullmatch(r"\d{2}", args.other):
        sys.exit(f"{args.verb} names a second two-digit seat.")
    if args.verb in ("check", "start"):
        lines, every = check(nn)
        print("\n".join(lines))
        if not every:
            sys.exit(1)
        if args.verb == "start":
            write(os.path.join(home(nn), RECORD), {"started": stamp(), "state": "running"})
            print(f"The autonomous drive runs, from {rel(home(nn))}/{RECORD}.")
    elif args.verb == "account":
        print(extra_account())
    elif args.verb == "row":
        said, paused = row(nn, args.other)
        print(said)
        if paused:
            sys.exit(drive.PAUSED)
    elif args.verb == "take":
        print("\n".join(take(nn, args.other)))
    elif args.verb == "resume":
        p = os.path.join(home(nn), RECORD)
        d = load(p)
        if d.get("state") != "paused":
            sys.exit(f"Session {nn}'s autonomous drive is not paused.")
        write(p, {**d, "state": "running", "at": ""})
        print(f"Resumed. Next: `python3 .claude/tools/autonomous-drive.py row {nn} {d.get('at')}`, then fire it.")
    elif args.verb == "end":
        try:
            os.remove(os.path.join(home(nn), RECORD))
        except OSError:
            sys.exit(f"Session {nn} runs no autonomous drive.")
        try:
            os.rmdir(home(nn))
        except OSError:
            pass
        print(f"Session {nn}'s autonomous drive ended.")


if __name__ == "__main__":
    main()
