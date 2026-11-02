#!/usr/bin/env python3
"""successor.py — who hands each seat over, and when.

Whoever drives a seat hands it over. A driver nobody drives hands itself
over, and so does a seat that follows one: driving(). Every other seat
keeps its Handover page, and I press it there.

A driver is a seat that took a drive, written down at the take, or an
assistant whose drive is on. A wait proves nothing: a session may wait
on another only to read it. session-control's first step takes each
session through tools/successor.py's take: FILE, in the driver's own
folder, names it, with the topic of a partial drive, "" for a full one.
A partial drive answers on its topic alone, and closes the session only
when its topic names the close and I said yes. One driver per session: a
take of a session another seat drives is refused. Its Save lets go, or
its Close: release. drivers() answers who drives whom now, never another
session on a reused number. An assistant's drive holds what it names
even before its sessions are taken: driven().

A driver or a follower asks due() once each finish is handled, before it
arms its wait again, through tools/successor.py: for each session it
drives, then for itself. Each reads its context against the handover
threshold set on 1100/system, the same % and threshold the Handover page
reads. A driven session past it, its turn over, is handed over by its
driver, through lib/handover.py's hand(). A driver or a follower nobody
drives, past it, hands itself over through session-handover.

A session working one long turn reaches no finish. Past the wrap-up
threshold, hooks/wrap-up.py tells it, after each tool call, to finish its
step and end its turn. Its driver then hands it over. A driver or a
follower told so hands itself over once its step ends, never mid-turn.

An assistant's successor drives on with the drive its seat last took:
line(). Any other driver's successor arms the one wait again, on what
its seat took and follows, each on the bookmark its record keeps. A take
from before records kept one takes its bookmark from the seat's last
armed wait: waited(), from its wakes.log.

The drive is lib/drive.py's file, read through its reader.

Imported, never run.
"""

import os
import re
import time

import context
import drive
import follow
import plans
import registry
import transcripts
import wake

# What a seat drives, in its own folder: each session by number, the topic
# of a partial drive or "" for a full one, when it was taken, and what
# lib/follow.py keeps for a follow too: its identity and its bookmark.
#   {"22": {"topic": "the awaiting wording", "taken": "2026-10-12T14:31:02",
#           "title": "22-copy-fix", "session": "<id>", "bookmark": "2026-10-12T14:30:40"}}
FILE = "driving.json"

# The one wait a seat runs, on every session it drives and follows, each
# on the bookmark its record keeps: tools/transcript.py's.
WAIT = "python3 .claude/tools/transcript.py wait --awake"

# One session in a wakes.log line that armed a wait, and its bookmark.
ARMED = re.compile(r"\b(\d{2}) since (the start|\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)")


def line(nn: str) -> str:
    """The line seat NN's successor drives on with, /1-assistant drive C1,
    while its drive is on. Empty when it drives nothing."""
    d = drive.read(nn)
    return f"{drive.DRIVE} {' '.join(drive.words(d))}" if drive.driving(d) and drive.words(d) else ""


def due(nn: str) -> tuple:
    """Seat NN's context and System's threshold, in whole percent, and
    whether it is handed over: (74, 70, True). A seat whose context reads
    nothing never is."""
    pct = context.percent(registry.entries().get(nn) or {}, registry.claude_records())
    limit = context.threshold()
    return pct, limit, pct is not None and pct >= limit


def path(mm: str) -> str:
    """Seat MM's drives."""
    return os.path.join(registry.folder(mm), FILE)


def taken(mm: str) -> dict:
    """What seat MM took to drive: {"22": {"topic": "", "taken": T, ...}},
    or {} when it took nothing. Each entry also keeps lib/follow.py's
    identity and bookmark, once taken since they were kept."""
    return {n: {**r, "topic": str(r.get("topic", "")), "taken": str(r.get("taken", ""))}
            for n, r in follow.records(path(mm)).items()}


def take(mm: str, numbers: list, topic: str = "") -> list:
    """Seat MM takes each session to drive: a full drive, or a partial one
    on `topic`. A session another seat drives is refused, and nothing is
    written. One it already drives keeps its topic, unless a new one is
    named: a successor arming its wait again changes nothing. A new drive
    reads from the session's newest turn, so one asking now is answered at
    once. The drive replaces the seat's follow of it. Returns each
    refusal, as (number, its driver)."""
    held = registry.entries()
    others = {n: by for n, by in driven_all(held).items() if by != mm}
    refused = [(n, others[n]) for n in numbers if n in others]
    if refused:
        return refused
    topic = " ".join(topic.split())

    def change(d):
        for n in numbers:
            kept = d.get(n)
            if kept and follow.same(kept, held.get(n), n):
                if topic:
                    kept["topic"] = topic
                continue
            d[n] = {"topic": topic, "taken": time.strftime(transcripts.STAMP),
                    **follow.identity(n), "bookmark": follow.mark(n, 1)}
    follow.update(mm, path(mm), change)
    follow.release(mm, numbers)
    return []


def release(mm: str, numbers: list) -> None:
    """Seat MM lets each session go: its Save ended a partial drive, its
    Close stopped it, or my stop line ended it."""
    follow.update(mm, path(mm), lambda d: [d.pop(n, None) for n in numbers])


def drivers(held: dict | None = None) -> dict:
    """Each session a seat took to drive, by number, and the driver's seat:
    {"31": "30"}. A session no longer held drops out, and so does another
    session on its number. A handover's successor stays driven.
    `held` is registry.entries()."""
    held = registry.entries() if held is None else held
    return {n: mm for mm in held for n, r in taken(mm).items()
            if n != mm and follow.same(r, held.get(n), n)}


def topics(held: dict | None = None) -> dict:
    """The topic of each session driven partially, by number: {"22": "the
    awaiting wording"}. A full drive has none."""
    held = registry.entries() if held is None else held
    found = drivers(held)
    return {n: r["topic"] for mm in set(found.values()) for n, r in taken(mm).items()
            if found.get(n) == mm and r["topic"]}


def driven(nn: str, held: dict | None = None) -> str:
    """The seat driving session NN, or "" when none does.

    A seat that took it says so. An assistant's drive, while on, takes it
    too: by the whole plan, its stage's letter, or its mission's id.
    `held` is registry.entries().
    """
    held = registry.entries() if held is None else held
    return _seat(nn, drivers(held), plans.owners(held))


def driven_all(held: dict | None = None) -> dict:
    """driven() for every session at once, each driven one by number with
    its driver's seat: {"11": "10"}. 1100 marks each on its rail."""
    held = registry.entries() if held is None else held
    found, owned = drivers(held), plans.owners(held)
    return {nn: seat for nn in held if (seat := _seat(nn, found, owned))}


def _seat(nn: str, found: dict, owned: dict) -> str:
    """driven()'s answer, from drivers() and plans.owners() read once."""
    if seat := found.get(nn):
        return seat
    seat, k = owned.get(nn, ("", ""))
    d = drive.read(seat) if seat else {}
    if not drive.driving(d):
        return ""
    stages = plans.plan(seat).get("stages", [])
    letter = next((chr(65 + i) for i, s in enumerate(stages)
                   if any(m.get("id") == k for m in s.get("missions", []))), "")
    words = drive.words(d)
    return seat if drive.PLAN in words or k in words or letter in words else ""


def driving(nn: str, held: dict | None = None) -> bool:
    """Whether seat NN drives or follows others now: it took one, follows
    one, or its drive is on. Such a seat hands itself over."""
    return bool(watching(nn, held)) or drive.driving(drive.read(nn))


def waited(nn: str, held: dict | None = None) -> list:
    """What seat NN's last wait was armed with, as [(number, bookmark)]:
    each session still held by the session it waited on, and never woken
    on since as stopped or gone. A number claimed after the wait was armed
    holds another session. A session armed from the start has no
    bookmark: ""."""
    try:
        with open(os.path.join(registry.folder(nn), wake.LOG)) as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    at = next((i for i in range(len(lines) - 1, -1, -1) if " armed · " in lines[i]), None)
    if at is None:
        return []
    armed = lines[at].split(" ", 1)[0]
    ended = set(re.findall(r"\b(\d{2}) (?:stopped|gone)\b", "\n".join(lines[at + 1:])))
    held = registry.entries() if held is None else held
    return [(n, "" if b == "the start" else b) for n, b in ARMED.findall(lines[at])
            if n in held and n not in ended and held[n].get("claimed", "") <= armed]


def watching(nn: str, held: dict | None = None) -> list:
    """Every session seat NN drives or follows now, by number: what its one
    wait covers."""
    held = registry.entries() if held is None else held
    found = {n for n, r in taken(nn).items() if n != nn and follow.same(r, held.get(n), n)}
    return sorted(found | set(follow.following(nn, held)))
