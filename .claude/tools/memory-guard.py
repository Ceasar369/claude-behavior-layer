#!/usr/bin/env python3
"""memory-guard.py — holds the program eating memory before the Mac runs out, and tells 1100.

Twenty times a second it reads free memory: the kernel's own percent,
`kern.memorystatus_level`, times the Mac's memory. Once a second, four
times while memory is short, it measures every program: its size, its
parent, its start, its CPU. One scan serves the guard and the watcher.

It acts only on a program tree still rising when memory runs short, and
only if the trees it picks explain at least half of the fall. A tree that
grew and stopped, a fresh test run, a relaunched app, session 12's
webpack server: none is picked. Short of memory with no one explaining
it, it only says so.

What it does to a runaway, in order:

  1. Freezes it at once, SIGSTOP, parents first, then looks again for
     anything it started meanwhile. A frozen program loses nothing.
  2. Within a second: ends it, SIGKILL, only if under 1 GB is left, or the
     tree is a flood of 30 programs or more at that moment.
  3. Otherwise holds it frozen up to a minute. At the minute it thaws it
     if free memory is back over 2 GB, and ends it if not.

Never a Claude session, iTerm2, Postgres or Docker. Band 00, known by the
text the project's file names under band and match, is frozen and asked:
it is ended only when I press End, and with no answer at the minute it
thaws. A project naming no band 00 has none here. In Chrome and my other apps,
only the one program that grew. A session's Playwright browser is ended
alone, never its MCP server. Every signal checks the program's start time
first, so a pid handed to another program is never hit.

When my own sessions fill the memory, the finding lists the sessions by
memory held, each with the minutes since it last worked. Under 0.8 GB
free, the guard ends the Playwright browser unused longest, 10 minutes or
more, then the next, and says which.

The session that started a stopped program has its next command refused
once, with a note, by hooks/guard.py: what was stopped and why. The same
program in the same folder, or on the same port, stays refused for
hooks/guard.py's REFUSED_FOR, or until `memory-guard.py clear NNNN`. The guard types nothing, anywhere.

The watcher sits beside it, on the same scan: iTerm2's debug logging left
on 10 minutes, a test run holding the cores, a program outside every
session using half a core for two minutes. It acts on nothing alone.

Everything shows on 1100/system, from one file, findings.json. A finding
is written only when it opens, changes or closes, never on a clock. Each
finding carries the buttons that act on its own program, through

  memory-guard.py act ID VERB     tell freeze thaw end lower dismiss logging-off

Never a sound, a spoken line, a notification or a window.

  memory-guard.py watch [--below GB] [--dry] [--state DIR]   run forever, as launchd does
  memory-guard.py now                  free memory and the biggest trees, once
  memory-guard.py act ID VERB          one button's act, on its finding's own program
  memory-guard.py incidents            the notes still open
  memory-guard.py clear NAME           an incident fixed: lifts its refusal
  memory-guard.py thaw                 thaws everything the guard holds frozen
  memory-guard.py install [--dry]      hand it to launchd, and start it

--dry names what it would do and signals nothing. It writes no state unless
--state names a folder, so a dry guard never touches the live one's. A dry
install prints the plist it would write, and hands launchd nothing.

The plist names this file, so it is the guard of the project at hand. Its
label is the same in every project: an install replaces the guard any
project installed before it, so one guard watches the one project running.

State is .claude/state/memory-guard/: findings.json, frozen.json, open/,
incidents/, and blackbox.jsonl, the last ten minutes, one line a second.
Its log is ~/Library/Logs/memory-guard.log. launchd runs it, outside iTerm2,
so macOS never counts it in iTerm2's group, and starts it again when it
dies or the Mac boots.

It runs on macOS's own /usr/bin/python3, 3.9, so it never moves with
Homebrew. Nothing here may need a newer Python.
"""

from __future__ import annotations

import argparse
import collections
import ctypes
import glob
import json
import os
import plistlib
import re
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import incident  # noqa: E402
import project  # noqa: E402

GIB = 2**30
BELOW = 2.0          # GB free: the line
ARM_LINE, ARM_FALL = 5.0, 0.5    # armed under 5 GB and down 0.5 in 2 s
ARM_ABS = 2.5        # armed under this, whatever it did
SUS_LINE, SUS_FALL = 3.5, 1.2    # danger under 3.5 GB, down 1.2 in 3 s and still falling
RISE3, RISE1 = 0.5, 0.2          # rising now: this much in 3 s, and in the last second
SLOW20, SLOW3, SLOW1 = 0.4, 0.05, 0.01   # rising slowly: this much in 20 s, in the last 3 s, and in the last second
SHARE = 0.5          # the picks explain at least this part of the fall
END_UNDER = 1.0      # GB free: end at once
FLOOD = 30           # programs in a tree: end at once
HOLD = 60            # seconds a hold lasts
CEILING = 600        # seconds a freeze of mine lasts
THAW_OVER = 2.0      # GB free: thaw at the minute
LOW, LOW_LEAVES = 4.0, 5.0       # GB free: the sessions are listed, and the list closes
LAST_RESORT = 0.8    # GB free: an idle browser is ended
IDLE_MIN = 10        # minutes a session sat unused before its browser may be ended
PAUSE = 5            # seconds after an act before the next can come
TICK = 0.05          # seconds between two reads of free memory
SCAN, SCAN_ARMED = 1.0, 0.25
BURST_TOTAL = 800    # percent of one core, the whole Mac, for 10 s
BURST_TREE = 150     # percent of one core, one tree, for 60 s
HOT_TREE, HOT_SECS = 50, 120     # a program outside every session
LOGGING_MIN = 600    # seconds iTerm2's debug logging stays on before I am told
LOGGING_EVERY = 120  # seconds between two reads of iTerm2's menu

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, ".claude", "state", "memory-guard")
SESSIONS = os.path.join(ROOT, ".claude", "state", "sessions")
VENV = os.path.join(ROOT, ".claude", "state", "iterm", "venv", "bin", "python")
LABEL = "com.behaviour-layer.memory-guard"
PLIST = os.path.expanduser(f"~/Library/LaunchAgents/{LABEL}.plist")
LOG = os.path.expanduser("~/Library/Logs/memory-guard.log")
PYTHON = "/usr/bin/python3"
LIVE = accounts.FOLDERS

# Kept by name, as the kernel names it, lowercased. iTerm2's pane servers
# carry their version. Claude Code is named by its version number, so it
# is known by where it lives instead, and a pane's shell by its login.
KEPT = {"iterm2", "login", "launchd"}
# macOS's own programs live here: loginwindow, Dock, Finder. A shell or a
# Python in /bin or /usr/bin is never kept for where it lives.
SYSTEM = ("/System/", "/usr/libexec/", "/usr/sbin/")
APPLE = SYSTEM + ("/bin/", "/usr/bin/", "/sbin/")
SHELLS = {"sh", "zsh", "bash", "dash", "fish"}
NEVER = re.compile(r"\bpostgres\b|\bDocker\b|com\.docker|vpnkit|vmnetd")   # not even frozen
BAND = project.MATCH    # in band 00's command lines; empty when the project names none
BROWSER = re.compile(r"ms-playwright|chrome-headless|headless_shell|remote-debugging-pipe", re.I)

libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
libc.mach_host_self.restype = ctypes.c_uint32


class BsdInfo(ctypes.Structure):
    _fields_ = [("flags", ctypes.c_uint32), ("status", ctypes.c_uint32), ("xstatus", ctypes.c_uint32),
                ("pid", ctypes.c_uint32), ("ppid", ctypes.c_uint32), ("uid", ctypes.c_uint32),
                ("gid", ctypes.c_uint32), ("ruid", ctypes.c_uint32), ("rgid", ctypes.c_uint32),
                ("svuid", ctypes.c_uint32), ("svgid", ctypes.c_uint32), ("rfu", ctypes.c_uint32),
                ("comm", ctypes.c_char * 16), ("name", ctypes.c_char * 32), ("nfiles", ctypes.c_uint32),
                ("pgid", ctypes.c_uint32), ("pjobc", ctypes.c_uint32), ("tdev", ctypes.c_uint32),
                ("tpgid", ctypes.c_uint32), ("nice", ctypes.c_int32), ("start_sec", ctypes.c_uint64),
                ("start_usec", ctypes.c_uint64)]


class Usage(ctypes.Structure):
    _fields_ = [("uuid", ctypes.c_uint8 * 16), ("user", ctypes.c_uint64), ("system", ctypes.c_uint64),
                ("idle", ctypes.c_uint64), ("interrupt", ctypes.c_uint64), ("pageins", ctypes.c_uint64),
                ("wired", ctypes.c_uint64), ("resident", ctypes.c_uint64), ("footprint", ctypes.c_uint64),
                ("start", ctypes.c_uint64), ("exit", ctypes.c_uint64)]


class TimeBase(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]


def sysctl(name: str) -> int:
    v, n = ctypes.c_uint64(0), ctypes.c_size_t(8)
    libc.sysctlbyname(name.encode(), ctypes.byref(v), ctypes.byref(n), None, 0)
    return v.value


TOTAL = sysctl("hw.memsize")
NCPU = sysctl("hw.ncpu") or 1
_base = TimeBase()
libc.mach_timebase_info(ctypes.byref(_base))


def free() -> int:
    """Free memory in bytes, as the kernel counts it before it starts killing."""
    return sysctl("kern.memorystatus_level") * TOTAL // 100


def swap() -> int:
    """Swap in use, in bytes: a second signal beside the free level, which steps by 1% of
    the Mac's memory, and moved 0.16 GB while a replay took 2.3 GB."""
    buf, n = ctypes.create_string_buffer(32), ctypes.c_size_t(32)
    if libc.sysctlbyname(b"vm.swapusage", buf, ctypes.byref(n), None, 0) != 0:
        return 0
    return int.from_bytes(buf.raw[16:24], "little")


def cpu_ticks() -> tuple:
    """User, system, idle and nice ticks of every core together, running since boot."""
    buf, n = (ctypes.c_uint32 * 4)(), ctypes.c_uint32(4)
    libc.host_statistics(libc.mach_host_self(), 3, buf, ctypes.byref(n))
    return tuple(buf)


_paths: dict = {}


def table() -> dict:
    """Every program now: {pid: (ppid, uid, name, bytes, path, start, pgid, cpu)}.
    Bytes is its footprint, as Activity Monitor's Memory column shows it, and 0 for
    another user's. Path is its program file's. Start is in microseconds, and with
    the pid it names the program. Cpu is the nanoseconds it has used."""
    room = 8192
    while True:
        pids = (ctypes.c_int * room)()
        n = libc.proc_listallpids(pids, ctypes.sizeof(pids))
        if n < room:
            break
        room *= 2
    out = {}
    info, use, path = BsdInfo(), Usage(), ctypes.create_string_buffer(4096)
    for pid in pids[:max(n, 0)]:
        if libc.proc_pidinfo(pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info)) != ctypes.sizeof(info):
            continue
        if libc.proc_pid_rusage(pid, 0, ctypes.byref(use)) == 0:
            size, cpu = use.footprint, (use.user + use.system) * _base.numer // _base.denom
        else:
            size = cpu = 0
        start = info.start_sec * 1_000_000 + info.start_usec
        where = _paths.get((pid, start))
        if where is None:
            where = path.value.decode(errors="replace") if libc.proc_pidpath(pid, path, 4096) > 0 else ""
            _paths[(pid, start)] = where
        out[pid] = (info.ppid, info.uid, (info.name or info.comm).decode(errors="replace"), size, where,
                    start, info.pgid, cpu)
    if len(_paths) > 2 * len(out) + 1000:
        alive = {(p, row[5]) for p, row in out.items()}
        for k in [k for k in _paths if k not in alive]:
            del _paths[k]
    return out


def started(pid: int) -> int:
    """A program's start time in microseconds, or 0 once it is gone."""
    info = BsdInfo()
    if libc.proc_pidinfo(pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info)) != ctypes.sizeof(info):
        return 0
    return info.start_sec * 1_000_000 + info.start_usec


def send(pid: int, sig: int, start: int) -> bool:
    """Signals a program only while its start time is still the one given.
    Every signal this guard sends goes through here."""
    if not start or started(pid) != start:
        return False
    try:
        os.kill(pid, sig)
        return True
    except OSError:
        return False


def claude(row: tuple) -> bool:
    """A Claude Code session, or the Claude app."""
    return "/claude/versions/" in row[4] or os.path.basename(row[4]).lower() == "claude"


def kept(t: dict, own: int) -> set:
    """Every program never ended, and every program above one. Own is the
    guard's pid."""
    me = os.getuid()
    seeds = [p for p, row in t.items()
             if p <= 1 or p == own or row[1] != me or row[4].startswith(SYSTEM) or claude(row)
             or row[2].lower() in KEPT or row[2].startswith("iTermServer")
             or (row[0] in t and t[row[0]][2] == "login")]
    out = set()
    for p in seeds:
        while p in t and p not in out:
            out.add(p)
            p = t[p][0]
    return out


def trees(t: dict, own: int = 0) -> dict:
    """Every program tree: {root: {"pids", "bytes", "kept", "owner"}}. A kept
    program is a tree of its own. Owner is the Claude Code session above a
    tree, 0 when none is. Own is the guard's pid, when the guard asks."""
    keep = kept(t, own)
    root = {}

    def top(p: int) -> int:
        path = []
        while p not in root:
            path.append(p)
            up = t[p][0]
            if p in keep or up <= 1 or up not in t or up in keep:
                root[p] = p
                break
            p = up
        for q in path:
            root[q] = root[p]
        return root[p]

    out = {}
    for p in t:
        r = top(p)
        tr = out.setdefault(r, {"pids": [], "bytes": 0, "kept": r in keep, "owner": 0})
        tr["pids"].append(p)
        tr["bytes"] += t[p][3]
    for r, tr in out.items():
        up = r if tr["kept"] else t[r][0]
        while up in t and up > 1 and not claude(t[up]):
            up = t[up][0]
        tr["owner"] = up if up in t and claude(t[up]) else 0
    return out


def below(t: dict, roots: list) -> list:
    """Every (pid, start) at or under the given pids, parents first."""
    kids = {}
    for p, row in t.items():
        kids.setdefault(row[0], []).append(p)
    out, todo, seen = [], [r for r in roots if r in t], set()
    while todo:
        p = todo.pop(0)
        if p not in seen:
            seen.add(p)
            out.append((p, t[p][5]))
            todo += kids.get(p, [])
    return out


_buf = None


def environment(pid: int) -> tuple:
    """(argv, env) of a program, or ([], {}) once it is gone, and for macOS's own."""
    global _buf
    if _buf is None:
        _buf = ctypes.create_string_buffer(sysctl("kern.argmax"))
    room = ctypes.c_size_t(len(_buf))
    mib = (ctypes.c_int * 3)(1, 49, pid)  # CTL_KERN, KERN_PROCARGS2
    if libc.sysctl(mib, 3, _buf, ctypes.byref(room), None, 0) != 0:
        return [], {}
    raw = _buf.raw[:room.value]
    if len(raw) < 5:
        return [], {}
    argc = int.from_bytes(raw[:4], "little")
    rest = raw[4:].split(b"\0")
    # The path, then the padding after it, then exactly argc words, then the
    # environment. A program that renamed itself, as npm does, leaves the rest empty.
    i = 1
    while i < len(rest) and not rest[i]:
        i += 1
    argv = [x.decode(errors="replace") for x in rest[i:i + argc]]
    env = {}
    for x in rest[i + argc:]:
        k, eq, v = x.decode(errors="replace").partition("=")
        if eq:
            env[k] = v
    return argv, env


def args(pid: int) -> str:
    """A program's command line, or "" once it is gone."""
    return " ".join(" ".join(environment(pid)[0]).split())


def name(root: int, tr: dict, t: dict) -> str:
    """What a tree runs, past a shell that only ran one program: npm run
    dev, never the bash a session's Bash tool wrapped it in. A Bash tool's
    shell running more than one names the command it was given."""
    p = root
    while not tr["kept"] and t[p][2] in SHELLS:
        kids = [q for q in tr["pids"] if t[q][0] == p]
        if len(kids) != 1:
            break
        p = kids[0]
    line, path = args(p) or t[p][2], t[p][4]
    asked = re.search(r" eval '(.*)' < /dev/null", line, re.S)
    if asked:
        return " ".join(asked.group(1).replace("'\"'\"'", "'").replace("'\\''", "'").split())[:120]
    first, rest = (path, line[len(path):]) if path and line.startswith(path) else line.partition(" ")[::2]
    return (os.path.basename(first) + " " + rest.strip()).strip()[:120]


def reading(n: int = 8) -> dict:
    """Free memory and the n biggest program trees now, as the guard sees
    them, for `now`."""
    t = table()
    all_ = trees(t)
    top = sorted(all_.items(), key=lambda kv: -kv[1]["bytes"])[:n]
    return {"free": free(), "total": TOTAL,
            "trees": [{"root": r, "name": name(r, tr, t), "count": len(tr["pids"]), "bytes": tr["bytes"],
                       "kept": tr["kept"], "owner": tr["owner"]} for r, tr in top]}


# ---------- words ----------

def gb(n: float) -> str:
    return f"{n / GIB:.1f} GB"


def clock(when: float = 0.0) -> str:
    return time.strftime("%H:%M", time.localtime(when or time.time()))


def secs(n: float) -> str:
    n = max(1, int(round(n)))
    return f"{n} second" + ("" if n == 1 else "s")


def say(line: str) -> None:
    """One line of the log."""
    print(time.strftime("%Y-%m-%d %H:%M:%S ") + line, flush=True)


ROLES = [(re.compile(r"playwright|chrome-headless|headless_shell|remote-debugging-pipe", re.I), "browser"),
         (re.compile(r"\btests?\b|vitest|jest|--test\b", re.I), "test run"),
         (re.compile(r"typecheck|\btsc\b", re.I), "type check"),
         (re.compile(r"\bbuild\b|\blint\b|webpack|turbo|esbuild", re.I), "build"),
         (re.compile(r"\bdev\b|\bserve\b|\bstart\b|http\.server|uvicorn|next", re.I), "dev server")]


def role(what: str) -> str:
    """The words for a program: a test run, a dev server. Its command's first two words when none fits."""
    if BAND and BAND in what:
        return "band 00"
    for rx, word in ROLES:
        if rx.search(what):
            return word
    words = [os.path.basename(w) if "/" in w else w for w in what.split(" ")[:2]]
    return " ".join(words).strip() or "program"


def whose(number: str, what: str) -> tuple:
    """("session 72's dev server", "72's dev server")."""
    r = role(what)
    if r == "band 00":
        return "band 00", "band 00"
    return (f"session {number}'s {r}", f"{number}'s {r}") if number else (f"the {r}", f"the {r}")


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def button(verb: str, label: str, stops: str, **more) -> dict:
    return dict({"verb": verb, "label": label, "stops": stops}, **more)


DISMISS = button("dismiss", "Dismiss", "Nothing. It touches no program.")


# ---------- state ----------

class Store:
    """The guard's folder. One writer at a time: the guard's own loop and the act verb share a lock."""

    def __init__(self, folder: str):
        self.dir = folder
        for sub in ("", "open", "incidents"):
            os.makedirs(os.path.join(folder, sub), exist_ok=True)

    def path(self, *parts: str) -> str:
        return os.path.join(self.dir, *parts)

    def lock(self):
        return incident.lock(self.dir)

    def read(self, name: str, default):
        return incident.read(self.path(name), default)

    def write(self, name: str, data) -> None:
        incident.write(self.path(name), data)

    def text(self, name: str, text: str) -> None:
        with open(self.path(name), "w") as f:
            f.write(text)

    def findings(self) -> list:
        return self.read("findings.json", {}).get("findings", [])

    def put_findings(self, items: list) -> None:
        self.write("findings.json", {"at": round(time.time(), 2), "findings": items})

    def frozen(self) -> list:
        return self.read("frozen.json", [])

    def incident(self) -> str:
        """The next incident number: past every file, hold and finding that holds one."""
        top = [int(os.path.basename(f)[:4]) for f in glob.glob(self.path("incidents", "????.md"))]
        top += [int(x["id"][5:]) for x in self.frozen() + self.findings() if re.fullmatch(r"stop-\d{4}", x["id"])]
        return f"{max(top or [0]) + 1:04d}"

    def append(self, name: str, line: str) -> None:
        with open(self.path(name), "a") as f:
            f.write(line + "\n")

    def move(self, name: str, to: str) -> None:
        if os.path.exists(self.path(name)):
            os.replace(self.path(name), self.path(to))


class Memory(Store):
    """The same, kept in memory: a dry guard with no folder of its own writes nothing."""

    def __init__(self):
        self.dir = ""
        self.files = {}
        self.mutex = threading.Lock()
        self.count = 0

    def path(self, *parts: str) -> str:
        return os.path.join("/dev/null", *parts)

    def lock(self):
        return self.mutex

    def read(self, name: str, default):
        return json.loads(json.dumps(self.files.get(name, default)))

    def write(self, name: str, data) -> None:
        self.files[name] = json.loads(json.dumps(data))

    def text(self, name: str, text: str) -> None:
        self.files[name] = text

    def incident(self) -> str:
        self.count += 1
        return f"{self.count:04d}"

    def append(self, name: str, line: str) -> None:
        pass

    def move(self, name: str, to: str) -> None:
        pass


def refusal(state: Store, key: str, targets: list, command: str = "", cwd: str = "", ports: list = (),
            restart: bool = False) -> None:
    """Opens the one file hooks/guard.py reads for an incident: each target session's note, told once.
    `restart` also refuses the same program in the same folder, or on the same port."""
    state.write(os.path.join("open", key + ".json"), incident.note(key, targets, command, cwd, ports, restart))


def sessions_now(t: dict = None) -> dict:
    """{claude pid: {"number", "id", "idle"}} for every session running now. Idle is the minutes
    since it last worked, and 0 while Claude Code says it is busy."""
    ids = {}
    for f in glob.glob(os.path.join(SESSIONS, "*", "record.json")):
        try:
            with open(f) as fh:
                d = json.load(fh)
            ids[d["session_id"]] = d.get("number") or os.path.basename(os.path.dirname(f))
        except (OSError, ValueError, KeyError):
            pass
    out, now = {}, time.time()
    for base in LIVE:
        for f in glob.glob(os.path.expanduser(f"{base}/sessions/*.json")):
            try:
                with open(f) as fh:
                    d = json.load(fh)
                pid, sid = int(d["pid"]), d["sessionId"]
            except (OSError, ValueError, KeyError):
                continue
            if t is not None and (pid not in t or not claude(t[pid])):
                continue
            since = (d.get("statusUpdatedAt") or d.get("updatedAt") or 0) / 1000
            out[pid] = {"number": ids.get(sid, ""), "id": sid,
                        "idle": 0 if d.get("status") == "busy" else max(0.0, (now - since) / 60)}
    return out


# ---------- the guard ----------

class Guard:
    def __init__(self, below_gb: float, dry: bool, state: Store):
        self.line = int(below_gb * GIB)
        self.dry = dry
        self.st = state
        self.own = os.getpid()
        self.mode = "calm"
        self.armed_until = 0.0
        self.frees = collections.deque()       # (t, free) every tick, 25 s
        self.swaps = collections.deque()       # (t, swap) every second, 12 s
        self.rings = {}                        # tid -> deque[(t, bytes)], 40 s
        self.cpu = {}                          # tid -> deque[(t, ns used since the last scan)], 130 s
        self.prev_cpu = {}                     # (pid, start) -> ns
        self.prev_at = 0.0
        self.lineage = {}                      # (pid, start) -> tid
        self.groups = {}                       # process group -> tid, for a program whose parent died unseen
        self.meta = {}                         # tid -> born, root, owner, what, class, rose_since
        self.progs = {}                        # pid -> deque[(t, bytes)] for programs of 20 MB or more, 25 s
        self.last = None                       # the last scan
        self.last_scan = 0.0
        self.scans = 0
        self.calm_until = 0.0
        self.told = 0.0
        self.low_seen = self.low_at = 0.0
        self.resorted = 0.0
        self.known = {}                        # finding id -> finding, as last seen on disk
        self.opened = set()                    # the ids this guard wrote
        self.dismissed = set()                 # the ids I took off the list while their cause lasts
        self.holds = []                        # frozen.json, as last read
        self.looked = 0.0
        self.box = collections.deque()         # (t, row) the last 130 s, for an incident
        self.box_began = time.time()
        self.cpu_total = collections.deque()   # (t, percent of one core) the last 12 s
        self.ticks = None
        self.beat_at = 0.0
        self.faulted = 0.0
        self.cause = {}                        # finding id -> the tree it names, for the watcher's findings
        self.done = {}                         # tree -> when it may be picked again
        self.ended = set()                     # browsers ended under 0.8 GB
        self.logging = {"on_since": 0.0, "checked": 0.0, "state": None, "thread": None, "told": False, "fails": 0}
        self.scan_ms = []

    # ----- reads -----------------------------------------------------------------
    def ago(self, now: float, back: float) -> int:
        """Free memory as read `back` seconds ago, or the oldest read held."""
        for t, v in self.frees:
            if t >= now - back:
                return v
        return self.frees[-1][1] if self.frees else 0

    @staticmethod
    def median(xs: list) -> float:
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else 0.0

    def value_at(self, ring, when: float) -> float:
        """A tree's size at `when`: the median of its last three reads at or before it, 0 before it began."""
        xs = [b for t, b in ring if t <= when]
        return self.median(xs[-3:]) if xs else 0.0

    def rise(self, tid, now: float, back: float) -> float:
        """How much a tree grew over the last `back` seconds. A tree that was there before this guard first looked
        has an unknown past, taken as its first reading: it never counts as risen from nothing."""
        ring = self.rings.get(tid)
        if not ring:
            return 0.0
        then = self.value_at(ring, now - back)
        if not then and self.meta[tid].get("old"):
            then = self.median([b for _, b in list(ring)[:3]])
        return self.value_at(ring, now) - then

    def sig(self, pid: int, sig: int, start: int) -> bool:
        """A signal to one program, unless dry. Only through send(): its start time is checked."""
        return started(pid) == start if self.dry else send(pid, sig, start)

    # ----- the scan ----------------------------------------------------------------
    def scan(self, now: float) -> None:
        began = time.perf_counter()
        t = table()
        cur = trees(t, self.own)
        pids_, bytes_ = {}, {}
        for r, tr in cur.items():
            if tr["kept"]:
                tid = ("k", r, t[r][5])
                pids_[tid], bytes_[tid] = tr["pids"], tr["bytes"]
                self.meta.setdefault(tid, {"born": now, "cls": "D", "claude": 0, "session": None, "what": None,
                                           "rose_since": None, "root": r, "rstart": t[r][5], "kept": True})
                continue
            kids = {}
            for p in tr["pids"]:
                kids.setdefault(t[p][0], []).append(p)
            todo = [r]
            while todo:
                p = todo.pop(0)
                todo += [k for k in kids.get(p, []) if k != p]
                row = t[p]
                key = (p, row[5])
                tid = self.lineage.get(key)
                orphan = row[0] <= 1 or row[0] not in t
                if tid is None:
                    up = (row[0], t[row[0]][5]) if not orphan else None
                    if up in self.lineage:
                        tid = self.lineage[up]
                    elif orphan and row[6] > 1 and row[6] != p and row[6] not in t:
                        # A parent that died unseen: its group still holds its children together,
                        # while the group's leader is gone.
                        tid = self.groups.get(row[6])
                    if tid is None:
                        tid = key
                    self.lineage[key] = tid
                if row[6] == p:
                    self.groups.setdefault(p, tid)
                elif orphan and row[6] > 1 and row[6] not in t:
                    self.groups.setdefault(row[6], tid)
                pids_.setdefault(tid, []).append(p)
                bytes_[tid] = bytes_.get(tid, 0) + row[3]
                if tid not in self.meta:
                    self.meta[tid] = {"born": now, "cls": None, "claude": tr["owner"] or self.via_group(t, row[6]),
                                      "session": None, "what": None, "rose_since": None, "root": p, "rstart": row[5],
                                      "kept": False, "tried": 0}
        for tid, ps in pids_.items():                    # a tree's root is its oldest program still living
            m = self.meta[tid]
            if m["root"] not in t or t[m["root"]][5] != m["rstart"]:
                m["root"] = min(ps, key=lambda p: t[p][5])
                m["rstart"] = t[m["root"]][5]
            if "old" not in m:                           # older than this guard's first look at it, by more than a scan
                m["old"] = now * 1e6 - min(t[p][5] for p in ps) > 3e6
        # CPU each tree used since the last scan, from each program's own running total
        for tid, ps in pids_.items():
            ns = 0
            for p in ps:
                row = t[p]
                before = self.prev_cpu.get((p, row[5]))
                if before is None:
                    if self.prev_at and row[5] >= (self.prev_at - 1.0) * 1_000_000:
                        ns += row[7]               # a program new since the last scan: all it used is since then
                elif row[7] > before:
                    ns += row[7] - before
            if ns:
                self.cpu.setdefault(tid, collections.deque()).append((now, ns))
        self.prev_cpu = {(p, row[5]): row[7] for p, row in t.items()}
        self.prev_at = now
        for tid in list(self.cpu):
            ring = self.cpu[tid]
            while ring and ring[0][0] < now - 130:
                ring.popleft()
            if not ring:
                del self.cpu[tid]
        for tid, b in bytes_.items():
            m = self.meta[tid]
            if m["kept"]:
                continue
            ring = self.rings.setdefault(tid, collections.deque())
            ring.append((now, b))
            while ring and ring[0][0] < now - 40:
                ring.popleft()
            if len(ring) >= 2:
                if ring[-1][1] > ring[-2][1] + 5 * 2**20:
                    m["last_grow"] = now
                    if m["rose_since"] is None:
                        m["rose_since"] = ring[-2][0]
                elif m["rose_since"] is not None and now - m.get("last_grow", now) > 1.0:
                    m["rose_since"] = None
        for tid in [tid for tid in self.meta if tid not in bytes_]:
            if now - self.meta[tid].get("seen", self.meta[tid]["born"]) > 40:
                for d in (self.meta, self.rings, self.cpu):
                    d.pop(tid, None)
        for tid in bytes_:
            self.meta[tid]["seen"] = now
        seen = set()
        for tid, ps in pids_.items():
            if not self.meta[tid]["kept"]:
                for p in ps:
                    if t[p][3] >= 20 * 2**20:
                        pr = self.progs.setdefault(p, collections.deque())
                        pr.append((now, t[p][3]))
                        while pr and pr[0][0] < now - 25:
                            pr.popleft()
                        seen.add(p)
        for p in [p for p in self.progs if p not in seen]:
            del self.progs[p]
        self.last = {"t": now, "table": t, "cur": cur, "pids": pids_, "bytes": bytes_}
        self.last_scan = now
        self.scans += 1
        self.scan_ms.append((time.perf_counter() - began) * 1000)
        del self.scan_ms[:-120]
        if self.scans % 60 == 0:
            alive = {(p, row[5]) for p, row in t.items()}
            self.lineage = {k: v for k, v in self.lineage.items() if k in alive}
            groups = {row[6] for row in t.values()}
            self.groups = {g: v for g, v in self.groups.items() if g in groups}

    @staticmethod
    def via_group(t: dict, pgid: int) -> int:
        """The Claude Code session above a program's process group leader, when the leader still lives."""
        up = pgid
        while up in t and up > 1:
            if claude(t[up]):
                return up
            up = t[up][0]
        return 0

    # ----- who and what --------------------------------------------------------------
    def classify(self, tid) -> dict:
        """A tree's class: A a session's, B band 00, C an app of mine, N never touched, D kept.
        Also what it runs, and its session's id when its environment says. Cached on the tree."""
        m = self.meta[tid]
        if m["cls"]:
            return m
        t, ps = self.last["table"], self.last["pids"].get(tid, [])
        if not ps:
            return m
        m["what"] = m["what"] or name(m["root"], {"pids": ps, "kept": False}, t)
        for p in sorted(ps, key=lambda p: t[p][5]):
            if t[p][4].startswith(APPLE) or m["tried"] >= 3:
                continue
            m["tried"] += 1
            argv, env = environment(p)
            if env.get("CLAUDE_CODE_SESSION_ID"):
                m["session"], m["pwd"], m["argv"] = env["CLAUDE_CODE_SESSION_ID"], env.get("PWD", ""), argv
                break
        text = " ".join([m["what"]] + [t[p][2] for p in ps[:40]])
        m["cls"] = "N" if NEVER.search(text) else "B" if BAND and BAND in m["what"] else "A" if m["session"] or m["claude"] else "C"
        return m

    def whose_session(self, m: dict) -> tuple:
        """(session id, number) of a tree's owner, "" when unknown."""
        for pid, d in sessions_now(self.last["table"] if self.last else None).items():
            if (m.get("session") and d["id"] == m["session"]) or (m.get("claude") and pid == m["claude"]):
                return d["id"], d["number"]
        return m.get("session") or "", ""

    # ----- the loop -------------------------------------------------------------------
    def run(self) -> None:
        say(f"watching{' dry, signalling nothing' if self.dry else ''}: holds the tree rising when free memory "
            f"is under {gb(self.line)}. Free now {gb(free())}.")
        signal.signal(signal.SIGTERM, lambda *_: self.bye())
        libc.pthread_set_qos_class_self_np(0x21, 0)    # user-interactive: its short bursts of work run on the fast cores, not the slow ones
        self.recover()
        errored = 0.0
        while True:
            tick = time.time()
            try:
                self.step(tick)
            except Exception:
                if tick - errored > 10:
                    import traceback
                    say("ERROR " + traceback.format_exc().replace("\n", " | "))
                    errored = tick
            time.sleep(max(0.0, TICK - (time.time() - tick)))

    def ready(self) -> None:
        """While armed, the biggest trees are classified before danger comes, so the first freeze waits on nothing."""
        todo = [tid for tid, b in sorted(self.last["bytes"].items(), key=lambda kv: -kv[1])
                if b >= 50 * 2**20 and not self.meta[tid]["cls"]]
        for tid in todo[:3]:
            self.classify(tid)

    def safely(self, part, *a) -> None:
        """The black box and the watcher never stop the guard from acting: a fault in either is logged, once in ten seconds."""
        try:
            part(*a)
        except Exception:
            if time.time() - self.faulted > 10:
                import traceback
                say(f"ERROR in {part.__name__}: " + traceback.format_exc().replace("\n", " | "))
                self.faulted = time.time()

    def bye(self) -> None:
        """Stopped by launchd: nothing stays frozen."""
        for h in self.st.frozen():
            self.thaw(h, "the guard stopped")
        sys.exit(0)

    def step(self, now: float) -> None:
        left = free()
        self.frees.append((now, left))
        while self.frees and self.frees[0][0] < now - 25:
            self.frees.popleft()
        if now - self.looked >= 0.25:
            self.looked = now
            self.known = {f["id"]: f for f in self.st.findings()}
            self.holds = self.st.frozen()
            for fid in self.opened - set(self.known):      # taken off the list, by a button
                self.dismissed.add(fid)
                self.opened.discard(fid)
            for f in list(self.known.values()):             # "went on" is news for ten minutes
                if f["level"] == "thawed" and time.time() - f["at"] > CEILING:
                    self.close(f["id"])
        armed = left < ARM_ABS * GIB
        if not armed and left < ARM_LINE * GIB:
            armed = self.ago(now, 2.0) - left >= ARM_FALL * GIB
        if not armed and len(self.swaps) > 1 and self.swaps[-1][1] - min(v for _, v in self.swaps) >= 0.5 * GIB:
            armed = True
        if armed:
            if self.mode == "calm":
                say(f"armed at {gb(left)} free")
            self.mode, self.armed_until = "armed", now + 5
        elif self.mode == "armed" and now > self.armed_until:
            self.mode = "calm"
        if now - self.last_scan >= (SCAN_ARMED if self.mode == "armed" else SCAN):
            self.scan(now)
            if self.mode == "armed":
                self.ready()
            if now - self.beat_at >= 1.0:
                self.beat_at = now
                self.safely(self.beat, now, left)
                self.safely(self.watcher, now)
        if self.last is None:
            return
        self.tend(now, left)
        if now < self.calm_until:
            return
        if left < self.line:
            self.danger(now, left, "line")
        elif left < SUS_LINE * GIB and self.ago(now, 3.0) - left >= SUS_FALL * GIB and left < self.ago(now, 1.0):
            self.danger(now, left, "sustained fall")
        else:
            self.low(now, left)

    # ----- danger ----------------------------------------------------------------------
    def suspects(self, now: float, back: float, rise_min: float, rise_now: float, now_back: float, rise_last: float = 0.0) -> list:
        """(rise, tree), biggest first: trees up `rise_min` over `back` seconds, `rise_now` over the last `now_back`,
        and `rise_last` over the last second."""
        held = {tuple(h["tid"]) for h in self.holds if h["tid"]}
        out = []
        for tid in self.last["pids"]:
            if self.meta[tid]["kept"] or tid in held or self.done.get(tid, 0) > now:
                continue
            r = self.rise(tid, now, back)
            if r >= rise_min and self.rise(tid, now, now_back) >= rise_now and self.rise(tid, now, 1.0) >= rise_last:
                out.append((r, tid))
        return sorted(out, key=lambda x: -x[0])

    def danger(self, now: float, left: int, why: str) -> None:
        if now - self.last_scan > (0.6 if self.mode == "armed" else 1.2):
            self.scan(now)
        fall3, fall20 = self.ago(now, 3.0) - left, self.ago(now, 20.0) - left
        picks, window = [], 3
        for back, rise_min, rise_now, now_back, rise_last, fall in ((3.0, RISE3 * GIB, RISE1 * GIB, 1.0, 0.0, fall3),
                                                                    (20.0, SLOW20 * GIB, SLOW3 * GIB, 3.0, SLOW1 * GIB, fall20)):
            picks, share = [], 0.0
            if fall > 0:
                for r, tid in self.suspects(now, back, rise_min, rise_now, now_back, rise_last):
                    picks.append((r, tid))
                    share += r
                    if share >= SHARE * fall:
                        break
            if picks and share >= SHARE * fall:
                window = int(back)
                break
            picks = []
        say(f"danger ({why}) at {gb(left)}: {len(picks)} picked")
        if not picks:
            if now >= self.told:
                self.told = now + 60
                say(f"free {gb(left)}, down {gb(max(fall3, 0))} in 3 s: no program explains it. Nothing stopped.")
            self.calm_until = now + PAUSE
            self.low(now, left, force=True)
            return
        for r, tid in picks:
            self.stop(now, left, tid, r, window, why)
        self.calm_until = time.time() + PAUSE

    def stop(self, now: float, left: int, tid, rose: float, window: int, why: str) -> None:
        t0 = time.time()
        m = self.classify(tid)
        self.done[tid] = now + 30
        t, ps = self.last["table"], list(self.last["pids"][tid])
        what = m["what"] or "?"
        if m["cls"] == "N":
            say(f"{what} is rising and is never touched: only said")
            self.low(now, left, force=True, extra=f"{what.split(' ')[0]} grew {gb(rose)}. The guard never touches it.")
            return
        unit = ps
        if m["cls"] == "C":
            riser = self.riser(ps, m, now, window)
            if riser is None:
                say(f"{what} is an app of mine, and no one program of it rose alone: nothing stopped")
                self.low(now, left, force=True)
                return
            unit = [riser]
        frozen = self.freeze(unit, t)
        t_first = time.time()
        sid, number = self.whose_session(m)
        ring = self.rings[tid]
        grew = max(0.0, self.value_at(ring, now) - self.value_at(ring, (m["rose_since"] or now - window) - 0.5))
        over = (now - m["rose_since"]) if m["rose_since"] else window
        h = {"id": "stop-" + self.st.incident(), "tid": list(tid), "items": frozen, "since": time.time(), "until": time.time() + HOLD,
             "cls": m["cls"], "who": "guard", "what": what, "number": number, "session": sid,
             "bytes": sum(t[p][3] for p in unit if p in t), "n": len(frozen), "grew": grew, "over": over, "free": left,
             "cwd": "", "ports": [], "why": why, "detail": {"names": {}, "five": []}}
        h["incident"] = h["id"][5:]
        self.persist(h)                      # on disk before anything else can fail: a frozen program is never forgotten
        try:
            ports = threading.Thread(target=self.listen, args=(frozen,), daemon=True)
            ports.start()
            for _ in range(3):
                seen = {p for p, _ in frozen}
                fresh = table()
                extra = [p for p, row in fresh.items() if p not in seen and row[0] in seen]
                if not extra:
                    break
                frozen += self.freeze(extra, fresh)
            flood = m["cls"] == "A" and len(frozen) >= FLOOD
            h.update(items=frozen, n=len(frozen), cwd=m.get("pwd") or self.pwd_of(ps, t), detail=self.detail(frozen, t))
            self.persist(h)
            say(f"froze {len(frozen)} programs of {what} (class {m['cls']}) {1000 * (t_first - t0):.0f} ms after the call, "
                f"all {1000 * (time.time() - t0):.0f} ms; free {gb(left)}, flood {flood}")
            end = m["cls"] in ("A", "C") and (left < END_UNDER * GIB or flood or free() < END_UNDER * GIB)
            if end:
                ports.join(0.5)
                h["ports"] = getattr(ports, "found", [])
                self.persist(h)
                self.end(h, "under 1 GB left" if left < END_UNDER * GIB else "a flood")
            else:
                say(f"holding {h['id']} frozen up to a minute")
                self.open_for(h, "hold")
                threading.Thread(target=self.save_ports, args=(h, ports), daemon=True).start()
        except Exception:
            if self.claim(h["id"]):                 # nothing stays frozen on a fault
                for p, s_ in h["items"] + frozen:
                    self.sig(p, signal.SIGCONT, s_)
            raise

    def persist(self, h: dict) -> None:
        with self.st.lock():
            self.st.write("frozen.json", [x for x in self.st.frozen() if x["id"] != h["id"]] + [h])

    def save_ports(self, h: dict, th) -> None:
        """The ports a held program listens on, kept with its hold once lsof answers."""
        th.join(5)
        found = getattr(th, "found", [])
        if found:
            with self.st.lock():
                rows = self.st.frozen()
                for r in rows:
                    if r["id"] == h["id"]:
                        r["ports"] = found
                self.st.write("frozen.json", rows)

    def riser(self, ps: list, m: dict, now: float, window: int = 3):
        """The one program of an app that rose over the window the pick was made on, never the app's main program."""
        best, who, seen = 0.0, None, 0
        for p in ps:
            pr = self.progs.get(p)
            if pr and len(pr) >= 2:
                seen += 1
                r = pr[-1][1] - min(b for t, b in pr if t >= now - window)
                if r > best:
                    best, who = r, p
        say(f"riser of {m.get('what')}: {seen} programs read, the most grown {gb(best)}" + (" (the main program)" if who == m.get("root") else ""))
        return None if who is None or who == m.get("root") or best < (0.2 if window <= 3 else 0.3) * GIB else who

    def freeze(self, pids: list, t: dict) -> list:
        """SIGSTOP, parents before children. Returns [[pid, start]] frozen."""
        return [[p, t[p][5]] for p in sorted((p for p in pids if p in t), key=lambda p: self.depth(p, t))
                if self.sig(p, signal.SIGSTOP, t[p][5])]

    @staticmethod
    def depth(p: int, t: dict) -> int:
        d = 0
        while p in t and d < 64 and t[p][0] > 1:
            p, d = t[p][0], d + 1
        return d

    @staticmethod
    def pwd_of(ps: list, t: dict) -> str:
        """The folder a tree was started in, from the first program of it that is not Apple's."""
        for p in sorted(ps, key=lambda p: t[p][5])[:6]:
            if not t[p][4].startswith(APPLE):
                pwd = environment(p)[1].get("PWD")
                if pwd:
                    return pwd
        return ""

    @staticmethod
    def detail(items: list, t: dict) -> dict:
        """What the incident file says of the programs, read while they are frozen and alive."""
        live = [p for p, _ in items if p in t]
        names = collections.Counter(t[p][2] for p in live)
        big = sorted(live, key=lambda p: -t[p][3])[:5]
        return {"names": dict(names.most_common(6)), "five": [[round(t[p][3] / 2**20), args(p)[:110]] for p in big]}

    @staticmethod
    def listen(items: list) -> None:
        """The ports the frozen programs listen on, through lsof, off the hot path. Left on the thread."""
        th = threading.current_thread()
        th.found = []
        pids = [str(p) for p, _ in items[:30]]
        if pids:
            try:
                r = subprocess.run(["/usr/sbin/lsof", "-nP", "-a", "-p", ",".join(pids), "-iTCP", "-sTCP:LISTEN", "-Fn"],
                                   capture_output=True, text=True, timeout=4)
                th.found = sorted({int(x.rsplit(":", 1)[1]) for x in r.stdout.split() if x.startswith("n") and ":" in x})
            except Exception:
                pass

    # ----- holds, ends, thaws --------------------------------------------------------------
    def claim(self, hid: str):
        """Takes a hold off frozen.json, once: whoever gets it decides it. None when a button took it first."""
        with self.st.lock():
            rows = self.st.frozen()
            h = next((r for r in rows if r["id"] == hid), None)
            if h:
                self.st.write("frozen.json", [r for r in rows if r["id"] != hid])
                self.holds = [x for x in self.holds if x["id"] != hid]
            return h

    def tend(self, now: float, left: int) -> None:
        for h in self.holds:
            if not any(started(p) == s for p, s in h["items"]):
                if self.claim(h["id"]):
                    self.close(h["id"])             # it ended by itself
            elif time.time() >= h["until"]:
                if h["who"] == "you":
                    self.thaw(h, "ten minutes passed")
                elif h["cls"] == "B":
                    self.thaw(h, "no answer came")
                elif left >= THAW_OVER * GIB:
                    self.thaw(h, f"free memory is back over 2 GB ({gb(left)})")
                else:
                    self.end(h, "a minute held, still under 2 GB")
        if left < LAST_RESORT * GIB:
            self.last_resort(now, left)

    def end(self, h: dict, reason: str) -> None:
        """SIGKILL what is frozen, whole. Never a program whose start time changed."""
        if not self.claim(h["id"]):
            return
        n = sum(1 for p, s in h["items"] if self.sig(p, signal.SIGKILL, s))
        alive = 0 if self.dry else sum(1 for p, s in h["items"] if started(p) == s)
        say(f"ended {n} programs of {h['what']} ({reason}); alive after: {alive}")
        self.open_for(h, "stop", reason)

    def thaw(self, h: dict, reason: str) -> None:
        if not self.claim(h["id"]):
            return
        n = sum(1 for p, s in h["items"] if self.sig(p, signal.SIGCONT, s))
        say(f"thawed {n} programs of {h['what']} ({reason})")
        self.open_for(h, "thawed", reason)

    def recover(self) -> None:
        """A guard that starts thaws, or ends, whatever an earlier one left frozen."""
        left = free()
        for h in self.st.frozen():
            items = [[p, s] for p, s in h["items"] if started(p) == s]
            if items:
                end = h["cls"] in ("A", "C") and h["who"] == "guard" and left < THAW_OVER * GIB
                say(f"recovered {h['what']}: " + ("ended" if end else "thawed") + f" {len(items)} programs a stopped guard left frozen")
                for p, s in items:
                    self.sig(p, signal.SIGKILL if end else signal.SIGCONT, s)
            self.close(h["id"])
        self.st.write("frozen.json", [])

    def last_resort(self, now: float, left: int) -> None:
        """Under 0.8 GB: the Playwright browser its session left unused longest, 10 minutes or more, is ended. Then the next."""
        if now - self.resorted < 1.0:
            return
        t = self.last["table"]
        who = sessions_now(t)
        held = {tuple(h["tid"]) for h in self.holds if h["tid"]}
        pick = None
        for tid, ps in self.last["pids"].items():
            m = self.meta[tid]
            if m["kept"] or tid in held or tid in self.ended:
                continue
            mine = [p for p in ps if BROWSER.search(t[p][4] + " " + t[p][2])]
            if not mine or self.classify(tid)["cls"] != "A":
                continue
            d = next((d for pid, d in who.items() if pid == m["claude"] or d["id"] == m["session"]), None)
            if d and d["idle"] >= IDLE_MIN and (pick is None or d["idle"] > pick[0]):
                pick = (d["idle"], [p for p in mine if t[p][0] not in mine], d, tid)
        if not pick:
            return
        self.resorted = now
        mins, tops, d, tid = pick
        self.ended.add(tid)
        items = [[p, s] for p, s in below(t, tops)]
        for p, s in items:
            self.sig(p, signal.SIGSTOP, s)
        n = sum(1 for p, s in items if self.sig(p, signal.SIGKILL, s))
        say(f"under 0.8 GB at {gb(left)}: ended the Playwright browser of session {d['number']}, unused {mins:.0f} minutes, {n} programs")
        self.open_for({"id": "stop-" + self.st.incident(), "tid": list(tid), "items": items, "since": time.time(), "cls": "A", "who": "guard",
                       "what": "browser", "number": d["number"], "session": d["id"], "n": n, "incident": "", "grew": 0, "over": 0, "free": left,
                       "cwd": "", "ports": [], "idle": mins}, "stop", "idle")

    # ----- findings --------------------------------------------------------------------
    def open_for(self, h: dict, level: str, reason: str = "") -> None:
        """The finding for one held program, at its level: hold, stop or thawed."""
        number = h.get("number", "")
        words, short = whose(number, h["what"])
        at = h["since"] if level == "hold" else time.time()
        clk = clock(at)
        grew = f" It grew {gb(h['grew'])} in {secs(h['over'])}." if h.get("grew", 0) >= 0.05 * GIB else ""
        incident = h.get("incident", "")
        if h["what"] == "browser":
            line = f"{clk} · Ended session {number}'s browser, idle {h['idle']:.0f} minutes. {gb(h['free'])} was left."
            title, words, short = f"Memory guard: ended an idle browser in session {number}", f"session {number}'s browser", f"{number}'s browser"
        elif level == "hold":
            line = f"{clk} · Froze {words}.{grew}"
            title = f"Memory guard: froze a {role(h['what'])}" + (f" in session {number}" if number else "")
        elif level == "stop":
            line = f"{clk} · Ended {words}.{grew}"
            title = "Memory guard: stopped" + (f" in session {number}" if number else "")
        else:
            line = f"{clk} · {cap(words)} went on. " + ("No answer came." if "no answer" in reason else "Memory came back.")
            title = f"Memory guard: {role(h['what'])} went on"
        buttons = []
        if level == "hold":
            buttons = [button("thaw", f"Thaw {short}", f"Only {words}: its {h['n']} programs."),
                       button("end", f"End {short}", f"Only {words}: its {h['n']} programs, {gb(h.get('bytes', 0))}.",
                              again={"question": f"End {words}? It ends {h['n']} programs and gives back {gb(h.get('bytes', 0))}. "
                                                 f"{'Session ' + number if number else 'It'} loses this run.", "yes": "End it", "no": "Keep it frozen"})]
        tell = [{"id": h["session"], "number": number, "text": self.note(h, level, incident)}] if h.get("session") else []
        if tell and level != "thawed":
            buttons.append(button("tell", f"Tell {number or 'it'}", f"Only session {number}'s next command, once. No program.",
                                  note=tell[0]["text"]))
        buttons.append(DISMISS)
        self.put({"id": h["id"], "kind": "hold" if level == "hold" else "stop", "level": level, "at": round(at, 2), "clock": clk,
                  "title": title, "line": line, "short": short, "session": number or None, "buttons": buttons,
                  "roots": [list(i) for i in h["items"]], "incident": incident, "tell": tell})
        if level == "stop" and incident and h["what"] != "browser":
            self.write_incident(h, reason)
            if tell:
                refusal(self.st, incident, [{"session": x["id"], "number": x["number"], "text": x["text"]} for x in tell],
                        h["what"], h["cwd"], h["ports"], restart=True)

    @staticmethod
    def note(h: dict, level: str, incident: str) -> str:
        """What the session reads at its next command, once. What was stopped and why. Never its task."""
        where = f" in `{h['cwd']}`" if h.get("cwd") else ""
        port = f" (port {h['ports'][0]})" if h.get("ports") else ""
        facts = f"it grew {gb(h['grew'])} in {secs(h['over'])} and the Mac had {gb(h['free'])} free" if h.get("grew", 0) >= 0.05 * GIB \
            else f"the Mac had {gb(h['free'])} free"
        when = clock(h["since"])
        if level == "hold":
            return (f"Memory guard froze your `{h['what'][:70]}`{where}{port} at {when}: {facts}. It waits for a decision, "
                    f"up to a minute. Your work and context are intact. Wait for it. Tell me in your next message, "
                    f"then go on with your own work.")
        return (f"Memory guard stopped your `{h['what'][:70]}`{where}{port} at {when}: {facts}. Your work and context are intact. "
                f"Do not start it again, and stop any loop of yours that restarts it. Tell me in your next message, "
                f"then go on with your own work. Incident {incident}: .claude/state/memory-guard/incidents/{incident}.md")

    def put(self, f: dict) -> None:
        """Writes one finding: opened, or changed. Nothing is written when it reads the same."""
        with self.st.lock():
            items = self.st.findings()
            old = next((i for i in items if i["id"] == f["id"]), None)
            if old and {k: v for k, v in old.items() if k != "at"} == {k: v for k, v in f.items() if k != "at"}:
                return
            if old and old["level"] == f["level"]:
                f["at"] = old["at"]
            self.st.put_findings([i for i in items if i["id"] != f["id"]] + [f])
        self.known[f["id"]] = f
        self.opened.add(f["id"])
        say("finding " + f["id"] + ": " + f["line"])

    def close(self, fid: str) -> None:
        self.opened.discard(fid)
        self.known.pop(fid, None)
        with self.st.lock():
            items = self.st.findings()
            rest = [i for i in items if i["id"] != fid]
            if len(rest) != len(items):
                self.st.put_findings(rest)
                say("closed " + fid)

    def write_incident(self, h: dict, status: str) -> None:
        """The facts of one stop, for the session that fixes the cause."""
        box = [r for tt, r in self.box if tt >= h["since"] - 90]
        d = h.get("detail") or {"names": {}, "five": []}
        self.st.text(os.path.join("incidents", h["id"][5:] + ".md"), "\n".join([
            f"# Incident {h['id'][5:]}", "",
            f"- Time: {time.strftime('%H:%M:%S', time.localtime(h['since']))}. Status: ended, {status}.",
            f"- Free memory: {gb(h['free'])} when it fired. The program grew {gb(h.get('grew', 0))} in {secs(h.get('over', 0))}.",
            f"- Command: `{h['what']}`. Folder: `{h['cwd'] or '?'}`.",
            f"- Owner: session {h['number'] or 'unknown'} (id {h['session'] or 'unknown'}).",
            f"- Programs: {h['n']}, by name {d['names']}. Class {h['cls']}. Ports it listened on: {h['ports']}.",
            "- Five biggest: " + "; ".join(f"{mb} MB {cmd}" for mb, cmd in d["five"]),
            f"- Black box, the 90 s before ({len(box)} rows): " + json.dumps(box[-90:], separators=(",", ":"))[:2500],
            "- Told: finding on 1100/system, and the session's next command refused once by hooks/guard.py.", ""]))

    def low(self, now: float, left: int, force: bool = False, extra: str = "") -> None:
        """The memory-low finding: who holds the memory, and who sat idle. Opens under 4 GB and falling, closes over 5 GB."""
        if left >= LOW_LEAVES * GIB:
            if now - self.low_seen >= 30:
                self.dismissed.discard("low")
                if "low" in self.known:
                    self.close("low")
            return
        self.low_seen = now
        if "low" in self.dismissed or (now - self.low_at < 10 and "low" in self.known and not extra):
            return
        if "low" not in self.known and not force and not (left < LOW * GIB and left < self.ago(now, 4.0) - 0.1 * GIB):
            return
        self.low_at = now
        t, cur = self.last["table"], self.last["cur"]
        rows = [{"number": d["number"] or "?", "gb": round(((t[pid][3] if pid in t else 0) + sum(
                    tr["bytes"] for tr in cur.values() if not tr["kept"] and tr["owner"] == pid)) / GIB, 1),
                 "idle": int(d["idle"]), "id": d["id"], "pid": pid} for pid, d in sessions_now(t).items()]
        top = sorted(rows, key=lambda r: -r["gb"])[:4]
        idle = [r for r in top if r["idle"] >= IDLE_MIN]
        roots = self.idle_browsers(t, idle)
        line = f"{clock()} · Memory is low. {gb(left)} left" + (" and falling." if self.ago(now, 20.0) - left >= 0.3 * GIB else ".")
        tell = [{"id": r["id"], "number": r["number"], "text": (
            f"Memory guard: memory is running low ({gb(left)} left) and your session sat idle {r['idle']} minutes, holding "
            f"{r['gb']:.1f} GB. Tell me in your next message, then go on with your own work.")} for r in idle]
        buttons = []
        if tell:
            buttons.append(button("tell", "Tell " + ", ".join(r["number"] for r in idle),
                                  "Only the next command of sessions " + ", ".join(r["number"] for r in idle) + ", once each. No program.",
                                  note=tell[0]["text"]))
        if roots:
            who = ", ".join(r["number"] for r in idle)
            buttons.append(button("end", f"End {len(roots)} browsers", f"Only the {len(roots)} browsers of sessions {who}. The sessions stay open.",
                                  again={"question": f"End the {len(roots)} browsers of sessions {who}? The sessions stay open.",
                                         "yes": "End them", "no": "Keep them"}))
        buttons.append(DISMISS)
        self.put({"id": "low", "kind": "low", "level": "warn", "at": round(now, 2), "clock": clock(),
                  "title": "Memory guard: memory is running low", "line": line + (" " + extra if extra else ""),
                  "short": f"{len(roots)} browsers" if roots else "sessions", "session": None,
                  "sessions": [{"number": r["number"], "gb": r["gb"], "idle": r["idle"]} for r in top], "buttons": buttons,
                  "roots": roots, "incident": None, "tell": tell})

    @staticmethod
    def idle_browsers(t: dict, idle: list) -> list:
        """The Playwright browsers of the idle sessions listed: the top program of each, which holds the rest."""
        mine = {p for p, row in t.items() if BROWSER.search(row[4])}
        roots = []
        for p in mine:
            if t[p][0] not in mine:
                up = t[p][0]
                while up in t and up > 1 and not any(up == r["pid"] for r in idle):
                    up = t[up][0]
                if any(up == r["pid"] for r in idle):
                    roots.append([p, t[p][5]])
        return roots

    # ----- the watcher ----------------------------------------------------------------
    def mean(self, tid, now: float, back: float) -> float:
        """Percent of one core a tree used over the last `back` seconds, and 0 for a tree younger than that."""
        ring, m = self.cpu.get(tid), self.meta.get(tid)
        if not ring or not m:
            return 0.0
        if now - m["born"] < back - 1:                 # a tree younger than the window has not held it
            return 0.0
        used = 0
        for at, ns in reversed(ring):
            if at < now - back:
                break
            used += ns
        return 100.0 * used / 1e9 / back

    def watcher(self, now: float) -> None:
        ticks = cpu_ticks()
        if self.ticks:
            d = [a - b for a, b in zip(ticks, self.ticks)]
            if sum(d) > 0:
                self.cpu_total.append((now, 100.0 * NCPU * (d[0] + d[1] + d[3]) / sum(d)))
        self.ticks = ticks
        while self.cpu_total and self.cpu_total[0][0] < now - 12:
            self.cpu_total.popleft()
        recent = [c for t, c in self.cpu_total if t >= now - 10]
        wide = len(recent) >= 8 and sum(recent) / len(recent) >= min(BURST_TOTAL, 0.8 * NCPU * 100)
        for tid, ring in self.cpu.items():
            if not ring or ring[-1][0] != now or tid not in self.last["pids"]:
                continue
            m, c10 = self.meta[tid], self.mean(tid, now, 10)
            if c10 < 50:
                continue
            if m["kept"]:
                self.hot(tid, m, now)
            elif ("burst-%s-%s" % tid) not in self.known and ("burst-%s-%s" % tid) not in self.dismissed \
                    and ((wide and c10 >= 300) or (self.mean(tid, now, 60) >= BURST_TREE and c10 >= 100)):
                self.burst(tid, now, "burst-%s-%s" % tid, c10)
        for fid, tid in list(self.cause.items()):      # a finding ends with its cause
            if tid not in self.last["pids"] or self.mean(tid, now, 5) < 30:
                self.dismissed.discard(fid)
                del self.cause[fid]
                if fid in self.known:
                    self.close(fid)
        self.iterm(now)

    def burst(self, tid, now: float, fid: str, cpu: float) -> None:
        m = self.classify(tid)
        if m["cls"] in ("N", "B"):
            return
        sid, number = self.whose_session(m)
        words, short = whose(number, m["what"] or "")
        cores = max(1, int(round(cpu / 100)))
        n = len(self.last["pids"][tid])
        t = self.last["table"]
        note = (f"Memory guard: your `{(m['what'] or '')[:70]}` used {cores} core{'s' if cores > 1 else ''} and slows every session. Run tests, builds and "
                f"type checks under `taskpolicy -b nice -n 19`. Tell me in your next message, then go on with your own work.")
        buttons = []
        if sid:
            buttons.append(button("tell", f"Tell {number or 'it'}", f"Only session {number}'s next command, once. No program.", note=note))
        buttons += [button("freeze", f"Freeze {short}", f"Only {words}: its {n} programs."),
                    button("lower", f"Lower {short}", f"Only {words}: its {n} programs. They go on, behind other work."),
                    button("end", f"End {short}", f"Only {words}: its {n} programs.",
                           again={"question": f"End {words}? It ends {n} programs. {'Session ' + number if number else 'It'} loses this run.", "yes": "End it", "no": "Keep it"}),
                    DISMISS]
        self.put({"id": fid, "kind": "burst", "level": "slow", "at": round(now, 2), "clock": clock(),
                  "title": f"{cap(words)} is slowing the Mac", "line": f"{clock()} · {cap(words)} uses {cores} core{'s' if cores > 1 else ''}. Every session waits.",
                  "short": short, "session": number or None, "buttons": buttons,
                  "roots": [[m["root"], t[m["root"]][5]]] if m["root"] in t else [], "incident": None,
                  "tell": [{"id": sid, "number": number, "text": note}] if sid else []})
        self.cause[fid] = tid

    def hot(self, tid, m: dict, now: float) -> None:
        """A program outside every session over half a core for two minutes, and iTerm2 over 60% for one."""
        t = self.last["table"]
        root = m["root"]
        if root not in t or claude(t[root]) or t[root][1] != os.getuid():
            return
        iterm = t[root][2] == "iTerm2"
        fid = f"hot-{root}"
        c = self.mean(tid, now, 60 if iterm else HOT_SECS)
        if fid in self.known or fid in self.dismissed or (iterm and self.logging["state"] is True) \
                or c < (60 if iterm else HOT_TREE) or self.mean(tid, now, 10) < 30:
            return
        who = "iTerm2" if iterm else ("macOS's " + t[root][2] if t[root][4].startswith(SYSTEM) else t[root][2])
        self.put({"id": fid, "kind": "hot", "level": "slow", "at": round(now, 2), "clock": clock(), "title": f"{who} is slow",
                  "line": f"{clock()} · {who} has used {int(c)}% of a core for {'a minute' if iterm else '2 minutes'}."
                          + (" It slows every pane." if iterm else ""),
                  "short": who, "session": None, "buttons": [DISMISS], "roots": [], "incident": None, "tell": []})
        self.cause[fid] = tid

    def iterm(self, now: float) -> None:
        """Reads iTerm2's debug logging switch every two minutes, off the hot path. On for 10 minutes: one finding."""
        lg = self.logging
        if lg["thread"] is not None and not lg["thread"].is_alive():
            lg["thread"] = None
        if now - lg["checked"] >= LOGGING_EVERY * 2 ** min(lg["fails"], 4) and lg["thread"] is None and os.path.exists(VENV) \
                and any(row[2] == "iTerm2" for row in self.last["table"].values()):
            lg["checked"] = now
            lg["thread"] = threading.Thread(target=self.read_logging, daemon=True)
            lg["thread"].start()
        if lg["state"] is True:
            lg["on_since"] = lg["on_since"] or now
            if now - lg["on_since"] >= LOGGING_MIN and "iterm" not in self.known and "iterm" not in self.dismissed and not lg["told"]:
                lg["told"] = True
                self.put({"id": "iterm", "kind": "iterm", "level": "slow", "at": round(now, 2), "clock": clock(), "title": "iTerm2 is slow",
                          "line": f"{clock()} · iTerm2 debug logging is on. It slows every pane.", "short": "logging", "session": None,
                          "buttons": [button("logging-off", "Turn off logging", "Only iTerm2's Toggle Debug Logging switch. No program and no session."),
                                      DISMISS], "roots": [], "incident": None, "tell": []})
        elif lg["state"] is False:
            lg["on_since"], lg["told"] = 0.0, False
            self.dismissed.discard("iterm")
            if "iterm" in self.known:
                self.close("iterm")

    def read_logging(self) -> None:
        """One read of iTerm2's switch. A read that fails is tried again after twice as long, up to 32 minutes."""
        state = logging_state()
        if state != self.logging["state"]:
            say("iTerm2 debug logging: " + {True: "on", False: "off", None: "unreadable"}[state])
        self.logging["fails"] = 0 if state is not None else self.logging["fails"] + 1
        self.logging["state"] = state

    # ----- the black box ----------------------------------------------------------------
    def beat(self, now: float, left: int) -> None:
        """One line a second: free memory, swap, the five biggest trees. The last ten minutes survive a crash."""
        self.swaps.append((now, swap()))
        while self.swaps and self.swaps[0][0] < now - 12:
            self.swaps.popleft()
        names = []
        for tid, b in sorted(self.last["bytes"].items(), key=lambda kv: -kv[1])[:5]:
            m = self.meta[tid]
            if m["what"] is None:
                t = self.last["table"]
                m["what"] = t[m["root"]][2] if m["kept"] and m["root"] in t else name(m["root"], {"pids": self.last["pids"][tid], "kept": False}, t)
            names.append([m["what"][:30], round(b / 2**20)])
        row = {"t": round(now, 1), "free": round(left / 2**20), "swap": round(self.swaps[-1][1] / 2**20), "mode": self.mode,
               "cpu": round(self.cpu_total[-1][1]) if self.cpu_total else 0, "top": names}
        self.box.append((now, row))
        while self.box and self.box[0][0] < now - 130:
            self.box.popleft()
        if self.st.dir:
            if now - self.box_began >= 600:
                self.st.move("blackbox.jsonl", "blackbox.prev.jsonl")
                self.box_began = now
            self.st.append("blackbox.jsonl", json.dumps(row, separators=(",", ":")))


LOGGING_SCRIPT = """
import asyncio, sys, iterm2
async def main(c):
    st = await asyncio.wait_for(iterm2.MainMenu.async_get_menu_item_state(c, "Toggle Debug Logging"), 20)
    if len(sys.argv) > 1 and st.checked:
        await iterm2.MainMenu.async_select_menu_item(c, "Toggle Debug Logging")
        await asyncio.sleep(1)
        st = await asyncio.wait_for(iterm2.MainMenu.async_get_menu_item_state(c, "Toggle Debug Logging"), 20)
    print("on" if st.checked else "off")
iterm2.run_until_complete(main, retry=False)
"""


def logging_state(click: bool = False):
    """True while iTerm2's debug logging is on, False off, None when it could not be read. Click turns it off."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    try:
        r = subprocess.run([VENV, "-c", LOGGING_SCRIPT] + (["off"] if click else []), capture_output=True, text=True,
                           timeout=60, env=env)
    except Exception:
        return None
    out = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
    return True if out == "on" else False if out == "off" else None


# ---------- acts ----------

def act(state: Store, fid: str, verb: str) -> str:
    """One button, on its finding's own program: the roots it recorded, each still holding its start time,
    and what is under them."""
    f = next((i for i in state.findings() if i["id"] == fid), None)
    if f is None:
        return f"no finding {fid}"
    if verb not in [b["verb"] for b in f["buttons"]]:
        return f"{fid} offers no {verb}"
    if verb == "logging-off":
        on = logging_state(click=True)
        if on is False:
            with state.lock():
                state.put_findings([i for i in state.findings() if i["id"] != fid])
        return "iTerm2 debug logging is " + {True: "still on", False: "off", None: "unreadable"}[on]
    with state.lock():
        items = state.findings()
        f = next((i for i in items if i["id"] == fid), f)
        rest = [i for i in items if i["id"] != fid]
        if verb == "dismiss":
            state.put_findings(rest)
            return f"dismissed {fid}"
        if verb == "tell":
            key = f["incident"] or fid
            now_open = state.read(os.path.join("open", key + ".json"), None)
            targets = [{"session": w["id"], "number": w["number"], "text": w["text"]} for w in f.get("tell", [])]
            if now_open:
                for x in now_open["for"]:
                    x["told"] = None
                state.write(os.path.join("open", key + ".json"), now_open)
            else:
                refusal(state, key, targets)
            return "told " + ", ".join(w["number"] for w in f.get("tell", [])) + ": the next command is refused once"
        t = table()
        held = next((h for h in state.frozen() if h["id"] == fid), None)
        if held:
            mine = [(p, s) for p, s in held["items"] if p in t and t[p][5] == s]
        else:
            roots = [p for p, s in f.get("roots", []) if p in t and t[p][5] == s]
            mine = below(t, roots)
        if not mine:
            return f"{fid}: its program is gone"
        if verb == "lower":
            n = sum(1 for p, s in mine if started(p) == s and subprocess.run(
                ["/usr/sbin/taskpolicy", "-b", "-p", str(p)], capture_output=True).returncode == 0)
            return f"lowered {n} programs to background priority"
        if verb == "freeze":
            n = sum(1 for p, s in sorted(mine, key=lambda x: Guard.depth(x[0], t)) if send(p, signal.SIGSTOP, s))
            state.write("frozen.json", [h for h in state.frozen() if h["id"] != fid] + [
                {"id": fid, "tid": [], "items": [list(x) for x in mine], "since": time.time(), "until": time.time() + CEILING,
                 "cls": "A", "who": "you", "what": f["short"], "number": f["session"] or "", "session": "", "n": len(mine),
                 "grew": 0, "over": 0, "free": free(), "cwd": "", "ports": []}])
            f["before"] = {k: f[k] for k in ("level", "kind", "line", "title", "buttons")}   # what thaw gives back
            f.update(level="hold", kind="hold", line=f"{clock()} · Froze {f['short']}. It thaws by itself in 10 minutes.",
                     title=f"Memory guard: froze {f['short']}", roots=[list(x) for x in mine])
            f["buttons"] = [button("thaw", f"Thaw {f['short']}", f"Only {f['short']}: its {len(mine)} programs.")] + \
                           [b for b in f["buttons"] if b["verb"] in ("end", "tell", "dismiss")]
            state.put_findings(rest + [f])
            return f"froze {n} programs"
        if verb == "thaw":
            n = sum(1 for p, s in mine if send(p, signal.SIGCONT, s))
            state.write("frozen.json", [h for h in state.frozen() if h["id"] != fid])
            if "before" in f:
                f.update(f.pop("before"))
            else:
                f.update(level="thawed", line=f"{clock()} · {cap(f['short'])} went on.")
                f["buttons"] = [b for b in f["buttons"] if b["verb"] in ("tell", "dismiss")]
            state.put_findings(rest + [f])
            return f"thawed {n} programs"
        if verb == "end":
            live = list(mine)
            for p, s in live:
                send(p, signal.SIGSTOP, s)
            for _ in range(3):
                seen = {p for p, _ in live}
                extra = [(p, row[5]) for p, row in table().items() if p not in seen and row[0] in seen]
                if not extra:
                    break
                for p, s in extra:
                    send(p, signal.SIGSTOP, s)
                live += extra
            n = sum(1 for p, s in live if send(p, signal.SIGKILL, s))
            state.write("frozen.json", [h for h in state.frozen() if h["id"] != fid])
            if f["kind"] == "low":
                f.update(roots=[], buttons=[b for b in f["buttons"] if b["verb"] != "end"])
            else:
                f.update(level="stop", kind="stop", line=f"{clock()} · Ended {f['short']}.")
                f["buttons"] = [b for b in f["buttons"] if b["verb"] in ("tell", "dismiss")]
            state.put_findings(rest + [f])
            return f"ended {n} programs"
    return "nothing done"


def incidents(state: Store) -> list:
    out = []
    for f in sorted(glob.glob(state.path("open", "*.json"))):
        d = incident.read(f)
        if d is None:
            continue
        out.append(f"{d['incident']}  {clock(d['at'])}  " + ", ".join(
            f"session {x['number'] or x['session'][:8]} {'told' if x['told'] else 'not yet told'}" for x in d["for"])
            + ("  refuses a restart" if d["restart"] else "") + f"  {d['command'][:50]}")
    return out


def clear(state: Store, key: str) -> str:
    path = state.path("open", key + ".json")
    if not os.path.exists(path):
        return f"no open note {key}"
    os.remove(path)
    return f"cleared {key}: its refusal is lifted"


def thaw_all(state: Store) -> str:
    n = 0
    with state.lock():
        for h in state.frozen():
            n += sum(1 for p, s in h["items"] if send(p, signal.SIGCONT, s))
        state.write("frozen.json", [])
    return f"thawed {n} programs"


def now() -> None:
    r = reading(12)
    print(f"free {gb(r['free'])} of {gb(r['total'])}")
    for tr in r["trees"]:
        mark = "kept" if tr["kept"] else f"pid {tr['root']}"
        print(f"{tr['bytes'] / 2**20:8.0f} MB  {tr['count']:4d}  {mark:<10}  {tr['name'][:90]}")


def plist() -> bytes:
    """The guard's launchd plist: this file, watching, started again whenever it ends."""
    return plistlib.dumps({"Label": LABEL, "ProgramArguments": [PYTHON, os.path.abspath(__file__), "watch"],
                           "RunAtLoad": True, "KeepAlive": True, "ProcessType": "Interactive", "ThrottleInterval": 2,
                           "StandardOutPath": LOG, "StandardErrorPath": LOG})


def install(dry: bool) -> None:
    if dry:
        sys.stdout.buffer.write(plist())
        return
    os.makedirs(os.path.dirname(PLIST), exist_ok=True)
    with open(PLIST, "wb") as f:
        f.write(plist())
    domain = f"gui/{os.getuid()}"
    subprocess.run(["/bin/launchctl", "bootout", f"{domain}/{LABEL}"], capture_output=True)
    # launchd takes a moment to let go of the old one. The gap with no guard running is the wait, a second or two.
    for _ in range(10):
        r = subprocess.run(["/bin/launchctl", "bootstrap", domain, PLIST], capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(0.5)
    print(r.stderr.strip() or f"{LABEL} handed to launchd. Its log: {LOG}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["watch", "now", "act", "incidents", "clear", "thaw", "install"])
    ap.add_argument("what", nargs="*")
    ap.add_argument("--below", type=float, default=BELOW, help="GB free that starts a hold")
    ap.add_argument("--dry", action="store_true", help="say what it would do, and signal nothing")
    ap.add_argument("--state", default="", help="keep its state in this folder, for a replay")
    a = ap.parse_args()
    state = Memory() if a.verb == "watch" and a.dry and not a.state else Store(a.state or STATE) if a.verb not in ("now", "install") else None
    if a.verb == "watch":
        Guard(a.below, a.dry, state).run()
    elif a.verb == "now":
        now()
    elif a.verb == "install":
        install(a.dry)
    elif a.verb == "act" and len(a.what) == 2:
        print(act(state, a.what[0], a.what[1]))
    elif a.verb == "clear" and a.what:
        print(clear(state, a.what[0]))
    elif a.verb == "incidents":
        print("\n".join(incidents(state)) or "no note is open")
    elif a.verb == "thaw":
        print(thaw_all(state))
    else:
        ap.error("act takes a finding id and a verb")


if __name__ == "__main__":
    main()
