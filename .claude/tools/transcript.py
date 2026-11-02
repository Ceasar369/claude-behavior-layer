#!/usr/bin/env python3
"""transcript.py — another session's transcript, copied as something I can read.

A transcript is mostly tool traffic. The copy keeps only what was said: my
turns, the session's turns, and one line for each skill it ran and each
file it wrote. Every turn is numbered, so I can point at one. It sits in
the reading session's folder, where 1100 shows it.

A live session is found by its record. An ended one by its title, which
opens with its number. The newest such transcript is the one meant, because
a number is handed out again once its session ends.

  transcript.py copy 11 --into 01            session 11's transcript, into session 01's folder
  transcript.py new 11 [--since T]           its turns after bookmark T, printed
  transcript.py wait 11 --since T            the same, once it has finished
  transcript.py wait 11 12 --since T11 T12   the same for several, once any one has
  transcript.py wait --awake                 the one wait: all this seat follows and drives

copy prints the copy's path, the session's title, its turns and their span,
its size, then every file in the copied session's folder, one per line. A copy made
again replaces the last one, so it catches up with a session still running.

new is how an assistant catches up. It prints only the turns that ended
after T, numbered as the copy numbers them, then a last line: the bookmark
to keep for next time, the newest turn's time to the second. No --since
prints every turn, once. A turn of mine opening "Session NN reports:" is a
helper's report typed into its parent's pane, so it reads as that
session's report, never as mine.

wait runs in the background, its session's turn over, as session-control
runs it. Claude Code starts that session's next turn the moment the wait ends.
A drive's wait adds --awake: the Mac stays awake on power until it ends.

It wakes when a session's transcript or its Claude Code status file is
written, or its process ends, never polled. It returns once one session's
finish is new since its bookmark, as lib/finish.py reads it, or once a
cap's reset or an error's one more try falls due. A driven session still
idle lib/wake.py's IDLE after its last turn ends it too, once: an idle
stretch never wakes it twice. A followed one never does. At its limit,
lib/wake.py's, it returns with no finish. Several
sessions take one bookmark each, in their order, so none waits on another.

Its words open with one line naming each session that woke it: by its
finish, or idle. Then each session's block: its turns after its bookmark,
its next bookmark, and its state as finish says it, the timeout said
beside it. An idle one says since when, and for how long: idle since
19:25, 12 minutes. One still working prints no turn, and keeps its
bookmark. A finish stamped after the session's last turn moves its
bookmark there, so one finish never wakes it twice.

Each arming and each end puts one line in the waiting session's
wakes.log: the bookmarks it was armed with, then what woke it and every
session's state. A stop, at the Bash tool's limit or by TaskStop, is
logged too. A wait never names its own seat.

wait naming no session is the one wait a seat runs, as the follow skill
and session-control arm it: every session it follows, lib/follow.py's
records, and every one it drives, lib/successor.py's, each on the
bookmark its record keeps. A take or a release while it runs joins or
leaves it, heard. One runs per seat: it holds its seat's wakes.log, and a
second is refused at once. Each block's head says what the seat does with
that session. A session stopped, or another on its number, wakes it, and
the wait releases it. A gone one wakes it once, after GRACE. Each next
bookmark is kept as read, and moves once the same session arms it again.
Its last line: "Wait again.", or "Following and driving nothing."
"""

import argparse
import fcntl
import os
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import finish  # noqa: E402
import follow  # noqa: E402
import hear  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402
import wake  # noqa: E402
from transcripts import ROOT, STAMP, copy, drawn, find, turns  # noqa: E402


def fresh(title: str, said: list, since: str, then: str = "") -> None:
    """The turns that ended after `since`, then the next bookmark: `then`,
    or else the newest turn's."""
    start = next((i for i, t in enumerate(said) if t[3] > since), len(said))
    # A bookmark compares as text: both are this Mac's clock, to the second.
    print(f"# {title} · {len(said) - start} of {len(said)} turns since "
          f"{since or 'the start'}\n")
    if said[start:]:
        print("\n\n".join(drawn(said[start:], start + 1)) + "\n")
    print(f"Bookmark: {then or (said[-1][3] if said else since)}")


def idle_at(mark: str, start: float = 0) -> float:
    """When a driven session sitting idle wakes its driver: IDLE after its
    last turn, its bookmark. The named wait keeps no record of that wake,
    so it counts it once only by `start`: 0 when it came before the wait
    began. The one wait passes no start: its record keeps the wake."""
    if not mark:
        return 0
    at = time.mktime(time.strptime(mark, STAMP)) + wake.IDLE
    return at if at > start else 0


def idled(ats: dict, got: dict, now: float) -> list:
    """Each session whose idle wake falls due now, still idle."""
    return [n for n, at in ats.items() if at and now >= at and got[n]["kind"] == "idle"]


def wait(numbers: list, marks: dict, limit: int) -> tuple:
    """Each session's finish, once one is new since its bookmark, or once a
    cap's reset or an error's one more try falls due, or at `limit`
    seconds. Also whether no finish ended it, and each session whose idle
    wake fell due, idle_at()'s, which ends it too."""
    got = {}

    def heard() -> bool:
        # Every session is read each time, so every state printed is current.
        for n in numbers:
            got[n] = finish.read(n, marks[n])
        return any(finish.new(got[n], marks[n]) for n in numbers)

    held, live = registry.entries(), registry.claude_records()
    files, pids = [], []
    for n in numbers:
        rec = held.get(n) or {}
        pid = (live.get(rec.get("session_id")) or {}).get("pid")
        files += [rec.get("transcript", "")] + [
            os.path.expanduser(f"{base}/sessions/{pid}.json") for base in registry.LIVE if pid]
        pids += [pid] if pid else []
    heard()
    start = time.time()
    idle_by = {n: idle_at(marks[n], start) for n in numbers}
    while True:
        # An idle session that went back to work, through what its driver
        # typed, ends nothing: the wait runs on to its limit.
        ends = [finish.due(f) for f in got.values() if finish.due(f)] + [start + limit] + [
            at for n, at in idle_by.items() if at > time.time() and got[n]["kind"] == "idle"]
        if hear.until(heard, files, pids, max(0.0, min(ends) - time.time())):
            return got, False, []
        now = time.time()
        idle = idled(idle_by, got, now)
        if idle or now >= start + limit:
            return got, True, idle


def state(f: dict, mark: str) -> str:
    """A finish as finish words it. An idle session adds since when, its
    bookmark, and for how long: idle since 19:25, 12 minutes."""
    if f["kind"] != "idle" or not mark:
        return finish.word(f)
    sat = int(time.time() - time.mktime(time.strptime(mark, STAMP))) // 60
    return f"idle since {mark[11:16]}, {sat} minute{'' if sat == 1 else 's'}"


def block(n: str, f: dict, mark: str, late: str) -> None:
    """One session's block: its turns since its bookmark, its next bookmark, its state."""
    path, title = find(n)
    if f["kind"] == "working":
        print(f"# {title or n} · still working\n\nBookmark: {mark}")
    else:
        said = turns(path, n) if path else []
        fresh(title or n, said, mark, max([mark] + [t[3] for t in said[-1:]] + [f["at"] or ""]))
    print(f"State: {state(f, mark)}{late}\n")


# ---- the one wait: everything a seat follows and drives ----------------------

# A seat changing hands reads gone a moment: its successor's claim ends its
# process, then writes the new record. Gone this long, it is told.
GRACE = 30

# Seconds a stopped session's number is given for a new claim's record to
# land, so another session on it is told as such.
CLAIMING = 3


def seat(me: str) -> dict:
    """Every session seat ME follows or drives, by number: (its records
    file, its entry). A drive replaces its follow, so it wins a tie."""
    found = {n: (follow.path(me), r) for n, r in follow.records(follow.path(me)).items()}
    found.update({n: (successor.path(me), r) for n, r in successor.taken(me).items()})
    found.pop(me, None)
    return found


def standing(n: str, kept: dict, held: dict, mark: str) -> dict:
    """Session N's finish as the one wait reads it: finish's, stopped once
    its record went, or reused once another session holds its number."""
    rec = held.get(n)
    if not rec:
        return finish.found("stopped")
    if not follow.same(kept, rec, n):
        return {**finish.found("reused"), "title": rec.get("title", n)}
    return finish.read(n, mark)


def seat_wait(me: str, limit: int) -> tuple:
    """The one wait, as wait() waits, on every session seat ME follows and
    drives, each on its record's bookmark. A take or a release while it
    runs is heard, and joins or leaves it. A session stopped or reused
    wakes it, and a gone one too, once gone GRACE seconds and never told
    before. A driven session sitting idle wakes it once, idle_at()'s, at
    once when that came while no wait ran: its record's idled names the
    bookmark it already woke on. A followed one never does: its follower
    has nothing to send it. Returns (its sessions, their bookmarks, their
    finishes, those that woke it, whether no finish ended it, the idle)."""
    old = dict(successor.waited(me))
    start, gone, logged = time.time(), {}, False
    while True:
        on = seat(me)
        if not on:
            return {}, {}, {}, [], False, []
        marks = {n: r.get("bookmark", old.get(n, "")) for n, (_, r) in on.items()}
        idle_by = {n: 0 if file.endswith(follow.FILE) or r.get("idled") == marks[n] else idle_at(marks[n])
                   for n, (file, r) in on.items()}
        if not logged:
            wake.log(me, "armed · seat · " + " · ".join(f"{n} since {marks[n] or 'the start'}" for n in on)
                     + f" · limit {limit} s")
            logged = True
        got, moved, woke = {}, [], []

        def heard() -> bool:
            moved.clear()
            if seat(me) != on:
                moved.append(me)
                return True
            held, now = registry.entries(), time.time()
            for n, (_, r) in on.items():
                got[n] = standing(n, r, held, marks[n])
                if got[n]["kind"] != "gone":
                    gone.pop(n, None)
                elif n not in gone:
                    gone[n] = now
                    moved.append(n)
            if moved:
                return True
            sid = lambda n: (held.get(n) or {}).get("session_id")
            woke[:] = [n for n, (_, r) in on.items()
                       if got[n]["kind"] in ("stopped", "reused")
                       or got[n]["kind"] == "gone" and r.get("gone") != sid(n) and now - gone[n] >= GRACE
                       or got[n]["kind"] != "gone" and finish.new(got[n], marks[n])]
            return bool(woke)

        held, live = registry.entries(), registry.claude_records()
        files, pids = [registry.folder(me)], []
        for n in on:
            rec = held.get(n) or {}
            pid = (live.get(rec.get("session_id")) or {}).get("pid")
            files += [rec.get("transcript", ""), registry.folder(n)] + [
                os.path.expanduser(f"{base}/sessions/{pid}.json") for base in registry.LIVE if pid]
            pids += [pid] if pid else []
        if heard():
            if moved:
                continue
            return on, marks, got, woke, False, []
        while True:
            # An idle wake already due, its stretch never woken on, ends it
            # at once: it came while no wait ran.
            now = time.time()
            idle = idled(idle_by, got, now)
            if idle or now >= start + limit:
                return on, marks, got, woke, True, idle
            # A gone session's grace ends once. Told before, it sets no
            # deadline, and no deadline set is ever past.
            ends = [finish.due(f) for f in got.values() if finish.due(f)] + [start + limit] + [
                at + GRACE for at in gone.values() if at + GRACE > now] + [
                at for n, at in idle_by.items() if at > now and got[n]["kind"] == "idle"]
            if hear.until(heard, files, pids, max(0.0, min(ends) - time.time())):
                if moved:
                    break
                return on, marks, got, woke, False, []


def role(file: str, r: dict) -> str:
    """What the seat does with one session, as its block's head says it."""
    if file.endswith(follow.FILE):
        return (f"you follow it for: {r.get('for') or 'no task named'}. "
                f"It ends when: {r.get('ends') or 'it stops, or I stop it'}")
    return f"you drive it on: {r['topic']}" if r.get("topic") else "you drive it fully"


def seat_block(n: str, file: str, r: dict, f: dict, mark: str, late: str, first: bool) -> str:
    """One session's block in the one wait: its head, its turns since its
    bookmark, its state. A gone one is told whole the `first` time.
    Returns its next bookmark, or "" when it keeps it."""
    # A record keeps the title it took: the number may hold another now.
    head = f"# {r.get('title') or n} · {role(file, r)}"
    if f["kind"] == "reused":
        print(f"{head}\n\nState: another session holds {n} now, {f['title']}. The wait released it.\n")
        return ""
    if f["kind"] == "stopped":
        print(f"{head}\n\nState: stopped. The wait released it.\n")
        return ""
    if f["kind"] == "working":
        print(f"{head}\n\nState: working\n")
        return ""
    path = (registry.entries().get(n) or {}).get("transcript", "")
    said = turns(path, n) if os.path.isfile(path) else []
    start = next((i for i, t in enumerate(said) if t[3] > mark), len(said))
    print(head + "\n")
    if said[start:]:
        print("\n\n".join(drawn(said[start:], start + 1)) + "\n")
    if f["kind"] == "gone":
        print("State: gone. " + ("Its process ended with no stop. It stays yours until it is "
                                 "resumed, handed over or reaped.\n" if first else "As told before.\n"))
    else:
        print(f"State: {state(f, mark)}{late}\n")
    then = max([mark] + [t[3] for t in said[-1:]] + [f["at"] or ""])
    return then if then != mark else ""


def seat_main(me: str, sid: str, limit: int) -> None:
    """The one wait, run: one per seat. The seat's wakes.log is held while
    it runs, so a second wait is refused."""
    fd = os.open(os.path.join(registry.folder(me), wake.LOG), os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        print(f"A wait already runs for seat {me}. It hears each take and release: arm nothing.")
        return
    try:
        seat_run(me, sid, limit)
    finally:
        os.close(fd)


def seat_run(me: str, sid: str, limit: int) -> None:
    """The one wait, then what woke it, each session's block, and what to
    do next. What the same session read last moves first."""
    for p in (follow.path(me), successor.path(me)):
        follow.armed(me, p, sid)
    try:
        on, marks, got, woke, late, idle = seat_wait(me, limit)
    except SystemExit:
        wake.log(me, "stopped, before any finish")
        raise
    if not on:
        print("Following and driving nothing.")
        return
    why = (f"on {', '.join(woke)}" if woke else f"on {', '.join(idle)}, idle" if idle
           else "at its limit, no session finished")
    print(f"Woke {why}.\n")
    # A new claim empties the folder before it writes its record, so a
    # reused number first reads stopped, for a moment.
    stopped = [n for n in on if got[n]["kind"] == "stopped"]
    if stopped:
        hear.until(lambda: any(n in registry.entries() for n in stopped),
                   [registry.WORK] + [registry.folder(n) for n in stopped], seconds=CLAIMING)
    held, read, gone = registry.entries(), {}, []
    late = ", at the timeout" if late and not woke and not idle else ""
    for n in on:
        if got[n]["kind"] == "stopped" and n in held:
            got[n] = {**finish.found("reused"), "title": held[n].get("title", n)}
    for n, (file, r) in on.items():
        f, first = got[n], got[n]["kind"] == "gone" and n in woke
        then = seat_block(n, file, r, f, marks[n], late, first)
        if f["kind"] in ("stopped", "reused"):
            (follow.release if file.endswith(follow.FILE) else successor.release)(me, [n])
        elif then:
            read.setdefault(file, {})[n] = then
        if first:
            gone.append((file, n, (held.get(n) or {}).get("session_id", "")))
    for file, marks_read in read.items():
        follow.read(me, file, marks_read, sid)
    for file, n, gone_sid in gone:
        follow.update(me, file, lambda d, n=n, s=gone_sid: d.get(n, {}).update({"gone": s}))
    # Each idle stretch woken on, by its bookmark: it never wakes the seat again.
    for n in idle:
        follow.update(me, on[n][0], lambda d, n=n: d.get(n, {}).update({"idled": marks[n]}))
    print("Wait again." if seat(me) else "Following and driving nothing.")
    sys.stdout.flush()
    wake.log(me, f"woke {why} · " + " · ".join(f"{n} {state(got[n], marks[n])}" for n in on))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["copy", "new", "wait"])
    ap.add_argument("numbers", nargs="*")
    ap.add_argument("--into", default="")
    ap.add_argument("--since", nargs="*", default=[])
    ap.add_argument("--timeout", type=int, default=wake.LIMIT)
    ap.add_argument("--awake", action="store_true")
    args = ap.parse_args()
    numbers = [f"{int(n):02d}" for n in args.numbers]

    if args.verb == "wait":
        sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
        me = registry.number_of(sid)
        if not me:
            sys.exit("The wait runs inside a numbered session, the one it wakes.")
        if me in numbers:
            sys.exit(f"Session {me} is this seat. A wait never names its own seat.")
        # A word in a bookmark's place sorts after every time, so its
        # session's turns would never count. It is refused, never waited on.
        wrong = [t for t in args.since if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d", t)]
        if wrong:
            sys.exit(f"Not a bookmark: {' '.join(wrong)}. A bookmark is a time, like 2026-10-02T17:12:13. "
                     "A session with none goes last, with nothing in its place.")
        # A stop sends TERM. It ends the wait, and the log says so.
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
        # A drive's wait keeps the Mac awake on power till this process ends, however it ends.
        if args.awake:
            subprocess.Popen(["/usr/bin/caffeinate", "-s", "-w", str(os.getpid())],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not numbers:
            seat_main(me, sid, args.timeout)
            return
        marks = dict(zip(numbers, args.since + [""] * len(numbers)))
        wake.log(me, "armed · " + " · ".join(f"{n} since {marks[n] or 'the start'}" for n in numbers)
                 + f" · limit {args.timeout} s")
        try:
            got, late, idle = wait(numbers, marks, args.timeout)
        except SystemExit:
            wake.log(me, "stopped, before any finish")
            raise
        woke = [n for n in numbers if finish.new(got[n], marks[n])]
        why = (f"on {', '.join(woke)}" if woke
               else f"on {', '.join(idle)}, idle" if idle
               else "at its limit, no session finished" if late else "with no session named")
        print(f"Woke {why}.\n")
        for n in numbers:
            block(n, got[n], marks[n], ", at the timeout" if late and not woke and not idle else "")
        sys.stdout.flush()
        wake.log(me, f"woke {why} · " + " · ".join(f"{n} {state(got[n], marks[n])}" for n in numbers))
        return
    if len(numbers) != 1:
        sys.exit(f"{args.verb} takes one session.")
    number = numbers[0]
    since = args.since[0] if args.since else ""

    if args.verb == "new":
        path, title = find(number)
        if not path:
            sys.exit(f"No transcript for session {number}.")
        fresh(title, turns(path, number), since)
        return
    if not args.into:
        sys.exit("copy takes --into, the session folder the copy goes in.")
    out = os.path.join(registry.folder(f"{int(args.into):02d}"), f"transcript-{number}.md")
    head = copy(number, out)
    if not head:
        sys.exit(f"No transcript for session {number}.")

    print(os.path.relpath(out, ROOT))
    print(head[0][2:])
    print(head[3])
    print(f"{os.path.getsize(out) // 1024} KB")
    folder = registry.folder(number)
    if os.path.isdir(folder):
        for base, _, names in os.walk(folder):
            for n in sorted(names):
                print(os.path.relpath(os.path.join(base, n), ROOT))


if __name__ == "__main__":
    main()
