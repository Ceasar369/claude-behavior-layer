#!/usr/bin/env python3
"""registry.py — the session registry.

A session is one folder, .claude/state/sessions/NN/. Its record sits inside
it as record.json, beside the work the session writes there. A terminal is
invisible until it claims a number, and /0-session-start is the only door.

A record holds what cannot be read from outside the process: the number,
the account, and where the transcript sits. A launched session's also
names the session that launched it, as `by`. It makes no team. What a
session is doing is never stored here — Claude Code publishes that
itself, live.

Its pane is read live too, by panes.pane. The record keeps the last pane
the session sat in, and panes.pane keeps it current, because once the
process ends, only that pane tells closed from gone.

Whether a record's session is still running is a pid question, and
ports.py answers it.

Imported, never run.
"""

import glob
import json
import os
import re
import shutil
import time

import accounts
import ports

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, ".claude", "state", "sessions")
RECORD = "record.json"
WAVES = "waves"
# The prototype subject a session holds, one line. lib/prototypes.py keeps it.
PROTOTYPE = "prototype"
# Each prototype subject whose winner a session builds, one line each. lib/prototypes.py keeps it.
BUILDING = "building"
# What the session's status line last printed. tools/statusline.py keeps it.
STATUSLINE = "statusline"

# A launch holds the number it picked, so no second launch picks it too.
# The marker sits in the number's folder until the claim empties it, and
# holds only while a claim may still come.
RESERVED = "reserved"
CLAIM = 90  # seconds a launched session has to claim its number

# A clarify wave. Kept for the session's life, and never its work.
WAVE = re.compile(r"wave-\d+\.md")

# A session's name is its number, then at most three words.
WORDS = 3

# CLAUDE_CONFIG_DIR picks the account, and a running session cannot change
# it. Nothing outside the process can read it, so it is recorded at claim
# time or nowhere. Each account is its folder, in this Mac's list:
# lib/accounts.py. The desktop app names no folder: its chats sit in
# Claude Code's own, whichever login it signed in with. It hands every
# process it starts that login's uuid instead, as CLAUDE_CODE_ACCOUNT_UUID.
ACCOUNTS = {accounts.ACCOUNTS[a]["folder"]: a for a in accounts.KNOWN}


def account() -> str:
    """The account this process runs under: its folder's. With none named,
    the desktop app's login, when the list holds it, else Claude Code's own
    folder's. "?" for a folder the list lacks."""
    d = os.environ.get("CLAUDE_CONFIG_DIR", "")
    if d:
        return ACCOUNTS.get(os.path.abspath(os.path.expanduser(d)), "?")
    login = os.environ.get("CLAUDE_CODE_ACCOUNT_UUID", "")
    signed = accounts.logins().get(login) if login else None
    return signed[0] if signed else ACCOUNTS.get(accounts.DEFAULT, "?")


def kebab(text: str) -> str:
    """The words a session's name carries: lowercase, dashed, three at most."""
    parts = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(parts[:WORDS])


def folder(number: str) -> str:
    """One session's own folder. The path only, made or not."""
    return os.path.join(WORK, f"{int(number):02d}")


def entries() -> dict:
    """Every record on disk, by number, each on its session's current id.

    A record keeps the id its session claimed with. Sent to the background,
    the session runs on under a new id, so every record follows its chain.
    Of the ids in it, the newest Claude Code still runs wins, with its
    transcript. A session resumed under an older id runs that one again.
    None running, the chain's end wins.
    """
    found = {}
    if not os.path.isdir(WORK):
        return found
    for name in sorted(os.listdir(WORK)):
        if not re.fullmatch(r"\d{2}", name):
            continue
        try:
            with open(os.path.join(WORK, name, RECORD)) as f:
                found[name] = json.load(f)
        except Exception:
            continue
    live = None
    for number, record in found.items():
        links = chain(record)
        if len(links) > 1:
            live = claude_records() if live is None else live
            sid, path = next((c for c in reversed(links) if c[0] in live), links[-1])
            found[number] = {**record, "session_id": sid, "transcript": path}
    return found


# Claude Code writes this line at the head of its own record, never inside
# a message, so it opens a line of the transcript.
LINK = b'\n{"type":"continued-in"'


def continued_in(path: str) -> str:
    """The id a transcript's session went on under, or "" when it did not."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - TAIL))
            data = f.read()
    except OSError:
        return ""
    at = data.rfind(LINK)
    if at < 0:
        return ""
    end = data.find(b"\n", at + 1)
    try:
        d = json.loads(data[at + 1:end if end > 0 else None])
    except ValueError:
        return ""
    return d.get("continuedInSessionId") or ""


def chain(record: dict) -> list:
    """Every (id, transcript) a record's session has run under, oldest first.

    Each transcript sits beside the one it continued from.
    """
    sid, path = record.get("session_id", ""), record.get("transcript", "")
    links = [(sid, path)]
    while path:
        nxt = continued_in(path)
        if not nxt or any(nxt == s for s, _ in links):
            break
        path = os.path.join(os.path.dirname(path), f"{nxt}.jsonl")
        links.append((nxt, path))
    return links


def files(number: str) -> list:
    """Every work file in one session's folder, deepest last.

    The record is not work, nor a launch's marker, nor the prototype subject
    it holds or builds, nor what its status line last printed, nor what its
    launch named: lib/launch.py's NAMED, imported here, since launch
    imports this module. Nor is a wave: it is
    the session's own conversation with me,
    kept for its life and gone with it. Waves live in waves/. One written
    loose in the folder, the older place, is a wave too.
    """
    import launch
    root = folder(number)
    waves = os.path.join(root, WAVES)
    kept = (RECORD, RESERVED, PROTOTYPE, BUILDING, STATUSLINE, launch.NAMED)
    found = []
    for base, _, names in os.walk(root):
        found += [os.path.join(base, n) for n in sorted(names)
                  if base != waves
                  and not (base == root and (n in kept or WAVE.fullmatch(n)))]
    return found


def reserve(number: str) -> bool:
    """Hold a number for one launch. False when another launch holds it.

    O_EXCL makes the marker, so two launches never both hold a fresh one.
    A marker past the claim window is taken over.
    """
    os.makedirs(folder(number), exist_ok=True)
    path = os.path.join(folder(number), RESERVED)
    try:
        os.close(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        if reserved(number):
            return False
        os.utime(path)
    return True


def reserved(number: str) -> bool:
    """Whether a launch holds this number now."""
    try:
        return time.time() - os.path.getmtime(os.path.join(folder(number), RESERVED)) < CLAIM
    except OSError:
        return False


def release(number: str) -> None:
    """Drop a failed launch's hold, and its folder when nothing else is there."""
    try:
        os.remove(os.path.join(folder(number), RESERVED))
        os.rmdir(folder(number))
    except OSError:
        pass


def clear(number: str) -> int:
    """Empty one session's folder and leave it standing. Returns the count.

    Claiming a number is the moment it changes hands, so this runs there,
    before the new record is written. A session that died without stopping
    leaves its work behind, and this keeps that work off a stranger.
    """
    was = len(files(number))
    shutil.rmtree(folder(number), ignore_errors=True)
    os.makedirs(folder(number), exist_ok=True)
    return was


def remove(number: str) -> None:
    """Delete one session's folder whole, record and work. A session ends here."""
    shutil.rmtree(folder(number), ignore_errors=True)


def move(old: str, new: str) -> None:
    """Move one session's folder under its new number. The old folder goes.

    A folder with no record has no owner, and nothing shows it or sweeps
    it, so a session changing numbers takes all of its folder along. The
    old record goes with the old folder: the claim writes the new one.
    """
    src, dst = folder(old), folder(new)
    os.makedirs(dst, exist_ok=True)
    for name in listing(src):
        if name != RECORD:
            merge(os.path.join(src, name), os.path.join(dst, name))
    shutil.rmtree(src, ignore_errors=True)


def merge(src: str, dst: str) -> None:
    """Move one path onto another. Two folders merge. Anything else replaces.

    Only a take-over meets a name already there: the folder it takes keeps
    its work, and the taker's own work joins it.
    """
    if os.path.isdir(src) and os.path.isdir(dst):
        for name in listing(src):
            merge(os.path.join(src, name), os.path.join(dst, name))
    else:
        os.replace(src, dst)


# Claude Code keeps one file per running session, carrying its id and its
# pid now, in its account's sessions folder. Every account's is read. Two
# that lead to the same files, as a link can make them, are read once.
LIVE = accounts.FOLDERS

# claude_records' last answer, and when it was read. A page draws every
# session, and every watched page draws each tick: all of them within one
# second read one process table.
PUBLISHED: list = [0.0, None]
A_SECOND = 1.0


def watched(numbers) -> list:
    """What a page hears for these sessions, so a change tells it at once.

    The sessions folder, where a number is claimed. Each session's folder,
    its record, its waves and its newest wave. Claude Code's own records,
    where a state moves. A write to any of them can move a page.
    """
    out = [WORK]
    for n in numbers:
        own = folder(n)
        waves = os.path.join(own, WAVES)
        found = [(int(m.group(1)), os.path.join(waves, x)) for x in listing(waves)
                 if (m := re.fullmatch(r"wave-(\d+)\.md", x))]
        out += [own, os.path.join(own, RECORD), waves] + ([max(found)[1]] if found else [])
    # Every account's folder leads to the same files: each is heard once.
    seen = set()
    for base in LIVE:
        live = os.path.expanduser(f"{base}/sessions")
        for p in [live] + glob.glob(os.path.join(live, "*.json")):
            real = os.path.realpath(p)
            if real not in seen:
                seen.add(real)
                out.append(real)
    return out


def listing(path: str) -> list:
    """A folder's names, or none when it is missing."""
    try:
        return os.listdir(path)
    except OSError:
        return []


def claude_records(fresh: bool = False) -> dict:
    """Claude Code's own record of every running session, by session id.

    A restart gives a session a new pid, and its file follows. A crash can
    leave a file behind: its pid is dead, or handed to another process that
    started at another time than the file says. Either way it is skipped.

    The answer is kept for a second: one process-table read serves every
    draw of that second, however many sessions and pages ask. A press that
    types into a pane asks `fresh`, page.typable's, so a dialog that just
    opened is never typed into.
    """
    if not fresh and PUBLISHED[1] is not None and time.time() - PUBLISHED[0] < A_SECOND:
        return PUBLISHED[1]
    paths = {}
    for base in LIVE:
        for f in glob.glob(os.path.expanduser(f"{base}/sessions/*.json")):
            paths.setdefault(os.path.realpath(f), f)
    found = []
    for f in paths:
        try:
            with open(f) as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        if d.get("sessionId") and d.get("pid"):
            found.append(d)
    running = ports.started(d["pid"] for d in found)
    best = {}
    for d in found:
        began = running.get(int(d["pid"]))
        if began is None:
            continue
        if d.get("procStart") and " ".join(d["procStart"].split()) != began:
            continue
        if d.get("updatedAt", 0) >= best.get(d["sessionId"], {}).get("updatedAt", -1):
            best[d["sessionId"]] = d
    PUBLISHED[:] = [time.time(), best]
    return best


# A transcript passes a megabyte in a long session, so only its tail is read.
TAIL = 200_000

# Each tail read, kept while its transcript's size and time hold. A page
# reads every session's tail on every draw, and a transcript only grows.
TAILS: dict = {}

# An iTerm pane id. launch.py prints one for every browser it opens or keeps.
PANE = re.compile(r"[0-9A-F]{8}-(?:[0-9A-F]{4}-){3}[0-9A-F]{12}")


def tail(path: str) -> list:
    """A transcript's last records, oldest first. Empty when it cannot be read.

    A seek lands mid-line, so the first line is dropped unless the whole
    file fits in the window. The list is shared: read it, never change it.
    """
    if not (path and os.path.isfile(path)):
        return []
    try:
        st = os.stat(path)
        mark = (st.st_size, st.st_mtime_ns)
        if (kept := TAILS.get(path)) and kept[0] == mark:
            return kept[1]
        size = st.st_size
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return []
    found = []
    for line in lines[1:] if size > TAIL else lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            found.append(d)
    TAILS[path] = (mark, found)
    return found


def browsers(path: str) -> list:
    """Every browser pane launch.py opened or kept since my last prompt.

    Claude Code marks a prompt I type with origin kind "human", and each
    one starts the count again. Clarify's Send types one. The pane is the
    id launch.py printed, so a page can ask whether it is still open.
    """
    found, asked = [], set()
    for d in tail(path):
        origin, message = d.get("origin"), d.get("message")
        if isinstance(origin, dict) and origin.get("kind") == "human":
            found, asked = [], set()
            continue
        content = message.get("content") if isinstance(message, dict) else None
        for b in content if isinstance(content, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and "launch.py browser" in str(
                    (b.get("input") or {}).get("command", "")):
                asked.add(b.get("id"))
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in asked:
                found += PANE.findall(json.dumps(b.get("content")))
    return found


def pid_of(record: dict, live: dict | None = None) -> int:
    """A registered session's pid now, or 0 when it is not running.

    The pid saved at claim time goes stale on a restart, so it is never the
    answer while Claude Code publishes anything. Publishing nothing at all
    means its files moved, not that every session ended.
    """
    live = claude_records() if live is None else live
    found = live.get(record.get("session_id", ""))
    if found:
        return int(found["pid"])
    if not live and ports.alive(record.get("pid", 0)):
        return int(record["pid"])
    return 0


def number_of(session_id: str, held: dict | None = None) -> str | None:
    """The number this session already holds, or None."""
    if not session_id:
        return None
    held = entries() if held is None else held
    return next((k for k, v in held.items()
                 if v.get("session_id") == session_id), None)


def free(number: str, held: dict, live: dict | None = None) -> bool:
    """Whether a number is free to hand out, when nobody named one.

    No running session holds it, its folder holds no work, and no launch
    holds it. A record can outlive its session, and so can that session's
    work. Handing its number out would sweep it.
    """
    entry = held.get(number)
    return ((entry is None or not pid_of(entry, live)) and not files(number)
            and not reserved(number))


def write(record: dict) -> None:
    """One record, written whole, so a reader never meets half of it and
    drops the session for that moment."""
    write_whole(os.path.join(folder(record["number"]), RECORD), json.dumps(record, indent=2) + "\n")


def write_whole(path: str, text: str) -> None:
    """One file written whole: a hidden file beside it, named for this
    process, then swapped in. A reader never meets half of it, and two
    writers never share the hidden file. The layer's one way to do it, but
    on Python 3.9: lib/accounts.py, lib/models.py and lib/incident.py keep
    their own."""
    into, name = os.path.split(path)
    os.makedirs(into, exist_ok=True)
    hidden = os.path.join(into, f".{name}.{os.getpid()}.tmp")
    with open(hidden, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(hidden, path)


def repane(number: str, pane: str) -> None:
    """Point one record at the pane its session sits in now.

    Only the pane changes, in the file as it stands, written whole. A
    record already gone stays gone: a stop that deleted its folder is never
    undone here.
    """
    path = os.path.join(folder(number), RECORD)
    hidden = os.path.join(folder(number), f".{RECORD}.{os.getpid()}.tmp")
    try:
        with open(path) as f:
            record = json.load(f)
        if record.get("pane") == pane:
            return
        record["pane"] = pane
        # write_whole's swap, with no folder made: one gone stays gone.
        with open(hidden, "w", encoding="utf-8") as f:
            f.write(json.dumps(record, indent=2) + "\n")
        if os.path.exists(path):
            os.replace(hidden, path)
        else:
            os.remove(hidden)
    except (OSError, ValueError):
        return

