#!/usr/bin/env python3
"""handover.py — a seat handed to a fresh session, in two halves, and the
press that types both into a seat's pane from outside it.

handover-prepare saves this session's conversation into its handovers/,
and the successor's settings into resume.json. handover-resume launches
the successor, from any session: it takes the seat, reads every copy,
oldest first, and goes on. session-handover runs the two back to back.

Both hooks read the same words, the same files and the same message here,
so the two halves never drift.

The press types /handover-prepare into a seat's pane. Once that hook says
it saved, it types /handover-resume NN with the successor's settings, and
waits for the successor to take the seat. Both are hooks, so no model
turn runs. Nothing is typed into a session working, nor at a dialog,
whose Return would approve its first option. Each step goes into the
seat's handover.json, which the Handover page draws. 1100 runs the press
when I press Hand over. A driver runs it through hand(), and handover.json
names it, so the successor knows its driver.

Every successor launches on the same settings, whichever way it comes:
my words at handover, then resume.json, then the model and effort its
seat's launch named, lib/launch.py's NAMED: carried(). What none names
takes the order's next account, and the model and effort set on System,
as any launch does. A model or an effort of system takes System's,
whatever the seat was named.

A driven seat's successor reads its copies, waits again only on what its
seat took, and ends its turn: its driver's next words are what it does
next. Any other successor goes on as its seat's role says: message().

Imported, never run.
"""

import json
import os
import re
import time

import accounts
import context
import hear
import launch
import page
import panes
import plans
import ports
import registry
import successor
import wake

HANDOVERS = "handovers"
RESUME = "resume.json"
ACCOUNTS = sorted(set(registry.ACCOUNTS.values()))
# A model or an effort that takes System's, whatever the seat was named.
SYSTEM = "system"
# An account picked as the order's next, over one resume.json keeps.
NEXT = "next"

FILE = "handover.json"
PREPARE = "/handover-prepare"
# Claude Code records a prompt a hook blocked with these words, then the hook's sentence.
BLOCKED = "operation blocked by hook:"
# The states that take a line as a fresh prompt.
SAFE = ("idle", "shell")
# Seconds each step may take: the copy, the launch, which waits out a
# claim, and the successor's first turn, which takes the seat.
SAVING = 120
LAUNCHING = registry.CLAIM + 60
SEATING = 300
# Stand-in: how long Handed over shows before the page goes.
CLEARS = 2.5
# A press's steps, in order. One that fails says why instead.
STEPS = ("saving", "launching", "done")


def settings(words: list) -> tuple:
    """The settings my words name, and the words they leave over.

    account A, model M and effort E, in any order. A bare effort word is
    its effort, so "account 3 max" names both. A model or an effort of
    system takes System's.
    """
    got, odd, i = {}, [], 0
    while i < len(words):
        w = words[i].lower()
        then = words[i + 1] if i + 1 < len(words) else ""
        if w == "account" and then in ACCOUNTS:
            got["account"], i = then, i + 2
        elif w == "model" and then:
            got["model"], i = SYSTEM if then.lower() == SYSTEM else then, i + 2
        elif w == "effort" and then.lower() in (*panes.EFFORTS, SYSTEM):
            got["effort"], i = then.lower(), i + 2
        elif w in panes.EFFORTS:
            got["effort"], i = w, i + 1
        else:
            odd.append(words[i])
            i += 1
    return got, odd


def copies(nn: str) -> list:
    """Session NN's saved conversations, oldest first: 1.md, 2.md."""
    try:
        names = os.listdir(os.path.join(registry.folder(nn), HANDOVERS))
    except OSError:
        return []
    return sorted((n for n in names if re.fullmatch(r"\d+\.md", n)), key=lambda n: int(n[:-3]))


def saved(nn: str) -> dict:
    """The settings resume.json keeps for session NN's successor, or none."""
    try:
        with open(os.path.join(registry.folder(nn), RESUME)) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return got if isinstance(got, dict) else {}


def keep(nn: str, named: dict) -> None:
    """Write the settings named into resume.json. A setting not named stays."""
    merged = {**saved(nn), **named}
    with open(os.path.join(registry.folder(nn), RESUME), "w") as f:
        json.dump(merged, f)
        f.write("\n")


def named(nn: str) -> dict:
    """The model and effort seat NN's launch named: lib/launch.py's NAMED.

    Stand-in: a seat launched before launches kept that file names its own
    claude line's model and effort, as a driver's handover once kept them.
    """
    got = launch.named_of(nn)
    if got is not None:
        return got
    mine = registry.entries().get(nn) or {}
    rec = registry.claude_records().get(mine.get("session_id")) or {}
    return own(int(rec.get("pid") or 0))


def carried(nn: str, words: dict | None = None) -> dict:
    """What seat NN's successor launches on, before the order and System: my
    words, then resume.json, then what its seat was named. A setting left
    out takes the order's next account, or the model and effort set on
    System, as any launch does. SYSTEM leaves one out."""
    got = {**named(nn), **saved(nn), **(words or {})}
    return {k: got[k] for k in ("account", "model", "effort") if got.get(k) and got[k] != SYSTEM}


def message(nn: str) -> str:
    """The successor's first message: take the seat, read every copy, go on.

    A seat a driver hands over ends its turn once it waits again on what
    it drove or followed, if anything: its driver's next words are its next
    work. An assistant's drive line, or any other seat's one wait on what it
    took and follows, is taken up first. A wait on a session it never took
    nor followed was only to read it, and is not armed again.
    Otherwise an assistant's successor takes the plan, and any other lays
    out its next steps, then works on them.
    """
    press = progress(nn)
    by = press.get("by", "") if press.get("step") == "launching" else ""
    drives = successor.line(nn)
    arm = (f"Then arm your wait again, as `session-control` Step 1 says: `{successor.WAIT}`. "
           if not drives and successor.watching(nn) else "")
    if by:
        go = (f"Then run `{drives}`. " if drives else "") + (
            f"{arm}Then end your turn. Session {by} drives you: its next words are what you do next.")
    else:
        then = drives or ("/assistant-successor" if os.path.exists(
            os.path.join(registry.folder(nn), plans.PLAN)) else "/session-successor")
        go = f"{arm}Then run `{then}`."
    return (f"First, run the skill `0-session-start` with exactly `{nn} keep`. "
            f"It ends session {nn}, closes its pane, and gives you its number, name and folder. "
            f"Then read every file in `.claude/state/sessions/{nn}/{HANDOVERS}/`, whole, oldest first. "
            f"It is my conversation with session {nn}, and you now hold its seat. {go}")


# ---- the press ----------------------------------------------------------------

def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), FILE)


def failure(copy: str, then: str) -> str:
    """A step failing after the save: the copy first, then what failed."""
    return (f"Saved as {copy}. " if copy else "Saved. ") + then


def progress(nn: str) -> dict:
    """The press running on seat NN, or the last one, which failed. Nothing when none."""
    try:
        with open(path(nn)) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(got, dict):
        return {}
    if got.get("step") in STEPS and not ports.alive(got.get("pid", 0)):
        if got["step"] == "done":
            return {}
        cut = (f"press was cut short when {'session ' + got['by'] if got.get('by') else '1100'} "
               f"stopped. Hand over again.")
        return {"step": "failed", "said": failure(got.get("copy", ""), "Then its " + cut)
                if got["step"] == "launching" else "Its " + cut}
    return got


def note(nn: str, **press) -> None:
    """Write the press's step, and the process running it. A new file each
    time, so the folder's watch hears it."""
    registry.write_whole(path(nn), json.dumps({**press, "pid": os.getpid()}) + "\n")


def size(transcript: str) -> int:
    try:
        return os.path.getsize(transcript)
    except OSError:
        return 0


def status(session_id: str) -> str:
    return (registry.claude_records().get(session_id) or {}).get("status", "")


def answer(transcript: str, at: int, seconds: float) -> str:
    """The sentence a hook blocked my line with, read from the transcript past
    byte `at`. Empty when none came in time."""
    got = []

    def blocked() -> bool:
        try:
            with open(transcript, "rb") as f:
                f.seek(at)
                lines = f.read().split(b"\n")
        except OSError:
            return False
        for line in lines:
            if BLOCKED.encode() not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if isinstance(d, dict) and d.get("type") == "system" and isinstance(d.get("content"), str):
                got.append(d["content"].partition(BLOCKED)[2].strip())
                return True
        return False

    hear.until(blocked, files=[transcript], seconds=seconds)
    return got[0] if got else ""


def press(nn: str, mine: dict, pane: str, pick: dict, since: int, by: str = "") -> None:
    """The press, step by step. Each line waits for the hook before it to
    answer, and a step that fails ends the press, saying why. `by` is the
    driver pressing, "" when I press."""
    transcript, sid = mine.get("transcript", ""), mine.get("session_id", "")
    failed = lambda said: note(nn, step="failed", said=said, by=by)
    at = size(transcript)
    if not panes.say(pane, PREPARE, clear=True):
        return failed(page.gone(nn))
    said = answer(transcript, at, SAVING)
    if "successfully" not in said:
        return failed(said or f"{PREPARE} never answered. Nothing more was typed.")
    copy = (re.search(r"handovers/\d+\.md", said) or [""])[0]
    if not hear.until(lambda: status(sid) in SAFE, files=registry.watched(()), seconds=SAVING):
        return failed(failure(copy, f"Then session {nn} stayed busy, so nothing more was typed."))
    # The account picked, else the one saved for this handover, else the
    # order's next. NEXT picks the order's next over a saved one. take()
    # moves the order on, so it runs only when needed.
    acct = pick["account"] if pick["account"] in ACCOUNTS else ""
    if not acct and pick["account"] != NEXT:
        acct = saved(nn).get("account", "")
    acct = acct or accounts.take()
    # A model or an effort goes in the line only when picked. One left out
    # is handover-resume's: carried(), then System's.
    step = {"since": since, "copy": copy, "by": by,
            "typed": f"/handover-resume {nn} account {acct}" + "".join(
                f" {k} {pick[k]}" for k in ("model", "effort") if pick.get(k))}
    note(nn, step="launching", **step)
    at = size(transcript)
    if not panes.say(pane, step["typed"], clear=True):
        return failed(failure(copy, f"Then session {nn}'s pane went, so nothing more was typed."))
    said = answer(transcript, at, LAUNCHING)
    if "successfully" not in said:
        return failed(failure(copy, said or "Then /handover-resume never answered."))
    seat = lambda: (registry.entries().get(nn) or {}).get("session_id")
    if not hear.until(lambda: seat() not in (None, sid), seconds=SEATING,
                      files=[registry.WORK, registry.folder(nn), os.path.join(registry.folder(nn), registry.RECORD)]):
        return failed(failure(copy, f"Then seat {nn}'s successor never took it."))
    note(nn, step="done", **step)
    time.sleep(CLEARS)
    try:
        os.remove(path(nn))
    except OSError:
        pass


def own(pid: int) -> dict:
    """The model and effort a session's own claude line named, when it did."""
    line = next((c for p, _, c in wake.table() if p == pid), "")
    return {k: m.group(1) for k in ("model", "effort") if (m := re.search(rf"--{k}\s+(\S+)", line))}


def hand(nn: str, by: str) -> str:
    """Seat NN handed over by the driver at seat BY, through the press. It
    picks nothing, so its successor launches on carried(), then the order's
    next account and System's model and effort. One line: one with
    "successfully", or why not."""
    why, mine, pane = page.typable(nn, SAFE)
    if why:
        return why
    if progress(nn).get("step") in STEPS:
        return f"A handover of seat {nn} already runs. Nothing was typed."
    pick = {"account": "", "model": "", "effort": ""}
    since = context.crossed(mine.get("transcript", ""), context.threshold())
    note(nn, step="saving", since=since, by=by)
    press(nn, mine, pane, pick, since, by)
    got = progress(nn)
    if got.get("step") == "failed":
        return got.get("said", "The handover failed.")
    return f"Seat {nn} successfully handed over. Its successor holds it now."
