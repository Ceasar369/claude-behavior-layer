#!/usr/bin/env python3
"""guard.py — refuses a shell command that reaches what other sessions hold.

A PreToolUse hook, matcher Bash|Monitor, with no skill behind it. Every
session shares one Mac, one folder and band 00, so one wrong command
reaches all of them. Three kinds are refused, each refusal naming the way
that works. The session reads it as the call's answer.

  A stop by name: pkill, killall, fuser -k, or a kill fed by pgrep or by a
  ps listing every process through a filter. A ps asking after one pid is
  no search. A name matches every band's servers. macOS pkill also reads
  an option placed after its pattern as one more pattern.
  A stop aimed past this session: pid 0 or a group, a pid of another
  session, 1100, 1400 or band 00, or a port outside this session's band.
  A git command that erases or moves the shared folder: reset, checkout,
  switch, restore, stash, clean, rebase, merge and pull. Reading git runs,
  and so do restore --staged, stash list and show, and clean -n. A copy
  outside this project runs freely, its git dir and work tree both outside.

It reads what is typed through lib/shell.py, down into $(...), backticks,
bash -c, eval and a heredoc a shell reads. A pid or a port hidden in a
variable passes unseen, and so does a script that kills.

One more refusal, with no kill in it. When the memory guard stops a
session's program, tools/memory-guard.py leaves a note for that session
in state/memory-guard/open/, one file for the incident. The session's
next command of any kind is refused once, with the note: what was stopped
and why. Then the same program in the same folder, or any command that
starts something on the same port, is refused for 30 minutes, or until
`memory-guard.py clear NNNN`. A plain read of the port, a curl, passes. A
loop the session started before the stop restarts the program with no
call at all, and this hook never hears it: the note says to stop it.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import incident  # noqa: E402
from shell import Reader  # noqa: E402

NAMED = {"pkill", "killall"}
FILTERS = {"grep", "egrep", "fgrep", "rg", "awk", "sed"}
REWRITES = {"reset", "checkout", "switch", "restore", "stash", "clean", "rebase",
            "merge", "pull"}
TOOL = "python3 .claude/tools/ports.py stop PORT"

# What the memory guard leaves for a session whose program it stopped.
OPEN = os.path.join(hook.ROOT, ".claude", "state", "memory-guard", "open")
REFUSED_FOR = 1800
# A command that only looks at a port, or stops what is on it, starts nothing.
LOOKS = {"curl", "wget", "lsof", "nc", "netstat", "ps", "pgrep", "grep", "egrep", "rg", "cat", "echo", "printf",
         "ls", "head", "tail", "wc", "sleep", "true", "test", "[", "open", "stat", "find", "jq", "kill", "tee"}

BY_NAME = ("Refused: it stops programs by name, and a name reaches every session's. "
           f"Stop a pid you checked, or your own port: {TOOL}.")
NO_PORT = ("Refused: this lsof feeds a kill without naming one port. "
           f"Stop a pid you checked, or your own port: {TOOL}.")
GIT = ("Refused: git {} rewrites the folder every session shares. Edit the files "
       "back by hand, and unstage with git restore --staged. Reading git still "
       "runs, and a copy under /tmp runs freely.")


def kill_targets(args: list):
    """What a kill aims at, or None when it stops nothing: signal 0 only
    asks whether a pid lives, and -l only lists the signals."""
    sig, targets, ended, i = None, [], False, 0
    while i < len(args):
        a = args[i]
        if not ended and a == "--":
            ended = True
        elif not ended and sig is None and a.startswith("-") and len(a) > 1:
            if a.startswith("-l") or a == "-L":
                return None
            if a in ("-s", "-n"):
                sig = args[i + 1] if i + 1 < len(args) else ""
                i += 1
            else:
                sig = a[1:]
        else:
            targets.append(a)
        i += 1
    if sig is not None and sig.upper().removeprefix("SIG") == "0":
        return None
    return targets


def lsof_ports(args: list) -> tuple:
    """Whether an lsof prints bare pids, and the ports it names. None
    stands for naming no one port: no -i, every port, or a host. A port
    held in a variable is unseen, and adds nothing."""
    terse, specs, i = False, [], 0
    while i < len(args):
        a = args[i]
        if a.startswith("-") and len(a) > 1 and not a.startswith("--"):
            body = a[1:]
            for j, c in enumerate(body):
                if c == "t":
                    terse = True
                if c == "i":
                    rest = body[j + 1:]
                    if not rest and i + 1 < len(args) and not args[i + 1].startswith("-"):
                        i += 1
                        rest = args[i]
                    specs.append(rest)
                    break
                if c in "scdpuagFk":
                    if not body[j + 1:]:
                        i += 1
                    break
        i += 1
    if not specs:
        return terse, None
    found = []
    for s in specs:
        if re.search(r":[^:]*(\$|\x00)", s):
            continue
        m = re.search(r":(\d+)(?:-(\d+))?$", s)
        if not m or (m.group(2) and m.group(2) != m.group(1)):
            return terse, None
        found.append(int(m.group(1)))
    return terse, found


def git(words: list, assigns: dict, cwd, path) -> str:
    """The refusal for a git command that rewrites this project, or "".

    `path` turns a folder the command names into one, or None when the
    text cannot say. An unknown folder counts as this project. The git dir
    and the work tree are judged apart, and a half left unnamed is the
    folder the command runs in.
    """
    named, i = {}, 1
    while i < len(words) and words[i].startswith("-"):
        w = words[i]
        if w in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path",
                 "--config-env", "--super-prefix") and i + 1 < len(words):
            if w == "-C":
                cwd = path(words[i + 1], cwd)
            elif w in ("--git-dir", "--work-tree"):
                named[w] = words[i + 1]
            i += 2
        else:
            if w.startswith(("--git-dir=", "--work-tree=")):
                flag, _, value = w.partition("=")
                named[flag] = value
            i += 1
    gitdir = named.get("--git-dir") or assigns.get("GIT_DIR")
    worktree = named.get("--work-tree") or assigns.get("GIT_WORK_TREE")
    if i >= len(words):
        return ""
    sub, rest = words[i], words[i + 1:]
    if sub not in REWRITES:
        return ""
    where = [path(p, cwd or hook.ROOT) if p else cwd for p in (gitdir, worktree)]
    if all(p is not None and not inside(p) for p in where):
        return ""
    if sub == "restore" and any(w in ("--staged", "-S") for w in rest) \
            and not any(w in ("--worktree", "-W") for w in rest):
        return ""
    if sub == "stash" and rest[:1] and rest[0] in ("list", "show"):
        return ""
    if sub == "clean" and any(w in ("-n", "--dry-run") or re.fullmatch(r"-[a-z]*n[a-z]*", w)
                              for w in rest):
        return ""
    return GIT.format(sub)


def inside(path: str) -> bool:
    root = os.path.realpath(hook.ROOT)
    real = os.path.realpath(path)
    return real == root or real.startswith(root + os.sep)


def held(me: int, number) -> dict:
    """Every pid this session may not stop, with whose it is.

    Another session's Claude Code, what it runs, and the panes above it.
    Every server on a port that is not this session's own, with what
    launched it and what it runs: band 00, another band, or the shared
    stack outside the scheme. This session's own Claude Code, and
    everything under it, is always its own.
    """
    import ports
    import registry
    import serve
    parent = {pid: pp for pid, (pp, _) in ports.table().items()}
    kids = {}
    for pid, pp in parent.items():
        kids.setdefault(pp, []).append(pid)
    out = {}

    def mark(pid: int, label: str) -> None:
        up = pid
        while up > 1 and up != me and up in parent:
            out.setdefault(up, label)
            up = parent[up]
        todo = list(kids.get(pid, []))
        while todo:
            p = todo.pop()
            out.setdefault(p, label)
            todo += kids.get(p, [])

    entries = registry.entries()
    for sid, d in registry.claude_records().items():
        pid = int(d.get("pid") or 0)
        if pid and pid != me:
            nn = registry.number_of(sid, entries)
            mark(pid, f"session {nn}" if nn else "another session")
    for port, pid in ports.listeners().items():
        s = str(ports.plain(port))
        if ports.own(port, number):
            continue
        if s in ("1100", "1400"):
            mark(pid, s)
        elif ports.in_scheme(port) and s[2:] == "00":
            mark(pid, "band 00")
        elif ports.own(port, s[2:]):
            mark(pid, f"session {s[2:]}'s port {port}")
        else:
            mark(pid, f"port {port}, outside your band")
    try:
        with open(serve.pidfile("band-00")) as f:
            band = int(f.read().strip() or 0)
    except (OSError, ValueError):
        band = 0
    if band:
        mark(band, "band 00")
    mine, todo = {me}, [me]
    while todo:
        p = todo.pop()
        for k in kids.get(p, []):
            mine.add(k)
            todo.append(k)
    return {p: label for p, label in out.items() if p not in mine}


def judge(command: str, cwd: str, session_id: str, me: int) -> str:
    """The refusal for one typed command, or "" when it runs."""
    reader = Reader()
    reader.read(command, cwd)
    # A search, or an lsof, reaches only a later kill that takes pids it
    # cannot see: a variable, a substitution, or xargs. Literal pids are
    # checked below, and a search after a kill is a look, nothing more.
    kills, lsofs, looked, named = [], [], [], False
    pgrep = ps = filters = False
    for words, assigns, where, inner in reader.found:
        name = os.path.basename(words[0])
        if name in NAMED:
            return BY_NAME
        if name == "fuser" and any(re.fullmatch(r"-[a-z]*k[a-z]*", w) for w in words[1:]):
            return BY_NAME
        pgrep |= name == "pgrep"
        ps |= name == "ps" and not any(w.startswith(("-p", "-q")) for w in words[1:])
        filters |= name in FILTERS
        if name == "lsof":
            looked.append(words[1:])
        if name == "kill":
            aimed = kill_targets(words[1:])
            if aimed is not None:
                kills.append(aimed)
                if not aimed or any(not re.fullmatch(r"\d+|%\S*|\$!", t) for t in aimed):
                    named |= pgrep or (ps and filters)
                    lsofs, looked = lsofs + looked, []
        if name == "git":
            refused = git(words, assigns, where,
                          lambda w, c, inner=inner: reader.path(w, c, inner))
            if refused:
                return refused
    if named:
        return BY_NAME
    if not kills:
        return ""
    pids = []
    for aimed in kills:
        for t in aimed:
            if re.fullmatch(r"-?\d+", t):
                if int(t) <= 0:
                    return (f"Refused: {t} stops a whole group of processes, or every "
                            "one. Stop one pid you checked.")
                pids.append(int(t))
    import ports
    import registry
    number = registry.number_of(session_id)
    ports_named = []
    for args in lsofs:
        terse, found = lsof_ports(args)
        if not terse:
            continue
        if found is None:
            return NO_PORT
        ports_named += found
    for port in ports_named:
        if not ports.own(port, number):
            mine = f"your band, {number}" if number else "any band, because this session holds no number"
            return (f"Refused: port {port} is outside {mine}. Stop only your own ports: "
                    f"{TOOL}.")
    if pids:
        guarded = held(me, number)
        for pid in pids:
            if pid in guarded:
                return f"Refused: pid {pid} belongs to {guarded[pid]}. Stop only your own."
    return ""


def starts(command: str, cwd: str, note: dict) -> bool:
    """Whether a command starts the stopped program again in its folder, or starts anything on its port.
    A read of the port, a curl, and a stop of it start nothing. A folder the text cannot say counts as the same."""
    here = " ".join(command.split())
    folder = note.get("cwd") or ""
    what = " ".join((note.get("command") or "").split())
    same = not folder or cwd == folder or folder in command
    if len(what) >= 8 and what in here and same:
        return True
    reader = Reader()
    try:
        reader.read(command, cwd)
    except Exception:
        return False
    for words, assigns, where, inner in reader.found:
        first = os.path.basename(words[0])
        if first in LOOKS or any(w.endswith("memory-guard.py") for w in words[:3]) \
                or (first.startswith("python") and any(w.endswith("ports.py") for w in words[:3]) and "stop" in words[:5]):
            continue
        text = " ".join(words + ["%s=%s" % kv for kv in assigns.items()])
        if any(re.search(r"(?<![\d.])%d(?!\d)" % p, text) for p in note.get("ports") or []):
            return True
        if len(what) >= 8 and what in " ".join(words) and (where is None or os.path.realpath(where) == os.path.realpath(folder or where)):
            return True
    return False


def stopped(session: str, command: str, cwd: str) -> str:
    """The refusal for a session whose program the memory guard stopped, or "" when it has none open."""
    try:
        names = [n for n in os.listdir(OPEN) if n.endswith(".json")]
    except OSError:
        return ""
    for n in sorted(names):
        path = os.path.join(OPEN, n)
        try:
            with incident.lock(os.path.dirname(OPEN)):       # two calls at once tell the session once
                note = incident.read(path)
                if note is None:
                    continue
                mine = next((x for x in note["for"] if x["session"] == session), None)
                if mine is None:
                    continue
                if mine["told"] is None:
                    mine["told"] = round(time.time(), 2)
                    incident.write(path, note)
                    return mine["text"]
        except (OSError, KeyError):
            continue
        if note["restart"] and time.time() - note["at"] < REFUSED_FOR and starts(command, cwd, note):
            return ("Refused: the memory guard stopped this program at %s (incident %s). Do not start it again, and stop any "
                    "loop of yours that restarts it. The refusal lifts when the incident is cleared, or at %s. Tell "
                    "me, then go on with your own work."
                    % (time.strftime("%H:%M", time.localtime(note["at"])), note["incident"],
                       time.strftime("%H:%M", time.localtime(note["at"] + REFUSED_FOR))))
    return ""


def fallback(command: str) -> str:
    """The same refusals by plain search, for a text the reader cannot take."""
    text = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n.*?\n\s*\1\s*(\n|$)", "\n", command, flags=re.S)
    if re.search(r"(^|[\s;&|(`/])(pkill|killall)\b", text):
        return BY_NAME
    if re.search(r"\bkill\b", text) and re.search(r"\bpgrep\b", text):
        return BY_NAME
    m = re.search(r"\bgit\s+(?:-\S+\s+)*(reset|checkout|switch|rebase|merge|pull|clean|stash(?!\s+(?:list|show))|restore(?!.*--staged))\b", text)
    if m and not re.search(r"(cd|-C)\s+['\"]?/(private/)?tmp/", text):
        return GIT.format(m.group(1))
    return ""


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    command = (event.get("tool_input") or {}).get("command") or ""
    hook.answering = "PreToolUse"
    cwd = event.get("cwd") or os.getcwd()
    try:
        note = stopped(event.get("session_id") or "", command, cwd)
    except Exception:
        note = ""
    if note:
        hook.done(note)
    if not re.search(r"kill|git|fuser", command):
        sys.exit(0)
    me = int(os.environ.get("CLAUDE_PID") or 0)
    try:
        refused = judge(command, cwd, event.get("session_id") or "", me)
    except Exception:
        refused = fallback(command)
    if refused:
        hook.done(refused)
    sys.exit(0)


if __name__ == "__main__":
    main()
