#!/usr/bin/env python3
"""follow.py — what a seat follows, and how its follows and drives keep their place.

A seat follows a session to answer each of its turns in its own role,
never typing into it: the follow skill. Each follow sits in the seat's own
folder, FILE, beside lib/successor.py's driving.json:

  {"10": {"for": "approve checks 16 to 24", "ends": "10 sends 11 its next journey",
          "taken": "2026-10-29T17:02:11", "title": "10-proposals-lead",
          "session": "<its session id>", "bookmark": "2026-10-29T17:01:40"}}

The seat's folder holds it, so a handover of the seat keeps it, and a new
claim of the number sweeps it. following() is what the advisor's panel
reads for Following.

A record names a session by number, and numbers are reused. same() tells
the session a record took from another on the same number: by its session
id, followed through the seat's handover copies. A successor takes its
seat by keep, and reads copies of its predecessor's conversation, each
naming the transcript it came from. A new claim sweeps the folder, copies
and all.

A bookmark is the newest turn already read. The one wait, tools/transcript.py
wait with no session named, keeps each next bookmark as read by its own
session as it returns: read(). Its next arming by that same session proves
those turns were answered, and only then does the bookmark move: armed().
A successor arming it drops what its predecessor read, and reads it again.

Imported, never run.
"""

import contextlib
import fcntl
import json
import os
import re
import time

import registry
import transcripts

FILE = "following.json"

# The head of a handover copy names the transcript it was copied from:
# transcripts.copy()'s.
COPIED = re.compile(r"^Transcript: .*/([0-9a-f-]{36})\.jsonl$", re.M)


def path(mm: str) -> str:
    """Seat MM's follows."""
    return os.path.join(registry.folder(mm), FILE)


def records(p: str) -> dict:
    """A records file's entries by number, or {} when it holds none."""
    try:
        with open(p) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(got, dict):
        return {}
    return {n: r for n, r in got.items() if re.fullmatch(r"\d{2}", n) and isinstance(r, dict)}


def put(p: str, d: dict) -> None:
    """A records file written whole at once, so a reader never sees half.
    None left → the file goes."""
    if d:
        registry.write_whole(p, json.dumps(d, indent=1) + "\n")
        return
    try:
        os.remove(p)
    except OSError:
        pass


@contextlib.contextmanager
def editing(mm: str):
    """Seat MM's records, edited by one writer at a time: a press taking a
    session while the wait keeps what it read never loses either."""
    os.makedirs(registry.folder(mm), exist_ok=True)
    fd = os.open(registry.folder(mm), os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def update(mm: str, p: str, change) -> dict:
    """change(entries) on the records file p of seat MM, under its lock.
    Returns the entries as written."""
    with editing(mm):
        d = records(p)
        change(d)
        put(p, d)
    return d


def copied(nn: str) -> set:
    """Every session whose conversation seat NN's handover copies hold, by id."""
    import handover  # handover imports successor, which imports this
    folder = os.path.join(registry.folder(nn), handover.HANDOVERS)
    found = set()
    for name in registry.listing(folder):
        try:
            with open(os.path.join(folder, name)) as f:
                head = f.read(2048)
        except OSError:
            continue
        if got := COPIED.search(head):
            found.add(got.group(1))
    return found


def same(kept: dict, rec: dict | None, nn: str) -> bool:
    """Whether the session holding NN now, `rec`, is the one a record took:
    that session, or its handover's successor. A record keeping no session
    id holds whoever holds the number."""
    if not rec:
        return False
    sid = kept.get("session", "")
    if not sid or rec.get("session_id") == sid:
        return True
    try:
        with open(os.path.join(registry.folder(nn), registry.RECORD)) as f:
            raw = json.load(f)
    except (OSError, ValueError):
        raw = {}
    return any(s == sid for s, _ in registry.chain(raw)) or sid in copied(nn)


def mark(nn: str, back: int = 0) -> str:
    """Session NN's bookmark `back` turns before its newest: 0 reads only
    what comes next, 1 its newest turn too. "" reads from its first turn."""
    rec = registry.entries().get(nn) or {}
    said = transcripts.turns(rec["transcript"], nn) if os.path.isfile(rec.get("transcript", "")) else []
    return said[-1 - back][3] if len(said) > back else ""


def identity(nn: str) -> dict:
    """What a record keeps of session NN, so a reused number never passes for it."""
    rec = registry.entries().get(nn) or {}
    return {"title": rec.get("title", nn), "session": rec.get("session_id", "")}


def following(mm: str, held: dict | None = None) -> dict:
    """What seat MM follows now, by number: each entry whose session still
    holds its number. A session stopped, or another on its number, drops out."""
    held = registry.entries() if held is None else held
    return {n: r for n, r in records(path(mm)).items() if n != mm and same(r, held.get(n), n)}


def take(mm: str, nn: str, why: str, ends: str) -> dict:
    """Seat MM follows NN, for `why`, until `ends`. A follow taken again
    keeps its bookmark, and takes the new words. A new one reads only
    the turns after NN's newest. Returns the entry."""
    why, ends = " ".join(why.split()), " ".join(ends.split())
    rec = registry.entries().get(nn) or {}
    old = records(path(mm)).get(nn)
    keep = old if old and same(old, rec, nn) else None
    entry = {"for": why, "ends": ends, "taken": time.strftime(transcripts.STAMP), **identity(nn),
             "bookmark": keep.get("bookmark", "") if keep else mark(nn)}
    update(mm, path(mm), lambda d: d.update({nn: entry}))
    return entry


def release(mm: str, numbers: list) -> None:
    """Seat MM stops following each session."""
    update(mm, path(mm), lambda d: [d.pop(n, None) for n in numbers])


def read(mm: str, p: str, marks: dict, sid: str) -> None:
    """The one wait returned: each session's next bookmark, kept as read by
    session `sid`, never yet moved."""
    def change(d):
        for n, to in marks.items():
            if n in d:
                d[n]["read"] = {"to": to, "by": sid}
    update(mm, p, change)


def armed(mm: str, p: str, sid: str) -> None:
    """The one wait arms again: what session `sid` read moves its bookmark,
    since it answered it. What another session read, a predecessor's, is
    dropped, so its successor reads those turns again."""
    def change(d):
        for r in d.values():
            got = r.pop("read", None)
            if isinstance(got, dict) and got.get("by") == sid and got.get("to"):
                r["bookmark"] = got["to"]
    if any("read" in r for r in records(p).values()):
        update(mm, p, change)
