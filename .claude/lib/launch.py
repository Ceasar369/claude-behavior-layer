#!/usr/bin/env python3
"""launch.py — opening a launched pane, and starting what runs in it.

The launch page and tools/launch.py both come here, so a row placed on the
page and one passed as flags open the same way.

A row is one pane. Its kind is a session, or a browser.

  session   n, name, message, account, model, effort, drive, and clone
  browser   site, and name. A bare port is a page on this machine.

A browser pane is named NN-browser-K: the launching session's number, then
the next K not already open. One of this layer's own pages, on 1000 to
1999 with the shift taken off, names itself by its title, so it is never
renamed.

Where each row lands is decided here once, by fill and settle: the launch
page draws by them, and tools/schedule.py fires by them.

Both take a place. `at` is one side of a pane: {"anchor": "p:<pane id>" or
"r:<uid>", "side": "right", "left", "down" or "up"}. A row with no `at`
fills a new tab or window. Its `win` is "L:<window id>" for a new tab in a
live window. Anything else is a new window, opened once, by its first row.

A launch page's file, launch.json, is read and written here too, one
writer at a time on this Mac: LOCK. So is the page's launch itself, go():
its moves, its panes, its log. A press on the page starts it as a program
of its own, tools/launch.py page NN, through begin(), so it never dies
with 1100. One launch of a page runs at a time: claim() holds its lock
for as long as that program runs, and a fresh 1100 leaves a page alone
while it is held. tools/schedule.py's fire runs the same go() in its own
program: run().

Imported, never run.
"""

import fcntl
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback

import accounts
import hear
import iterm
import panes
import plans
import ports
import registry

# Every launched session holds this file in its folder: the model and
# effort its launch named, {"model": ..., "effort": ...}, or {} when it
# named neither. Its launch writes it once the session claims its number.
# A take-over carries it into the seat, so a successor's replaces its
# seat's. lib/handover.py hands a successor what its seat was named.
NAMED = "named.json"


def default() -> dict:
    """What a session row I left unset starts at: the model and effort set
    on System. A launch page row takes it once, on its first save,
    tools/launch-page.py's made(); a launch from flags, as its pane opens.
    Its account is the order's next, taken then too: accounts.py."""
    return {"model": accounts.model(), "effort": accounts.effort()}


def named_of(number: str) -> dict | None:
    """The model and effort session NUMBER's launch named, or None when its
    folder holds no NAMED file: it launched before launches kept one."""
    try:
        with open(os.path.join(registry.folder(number), NAMED)) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return None
    got = got if isinstance(got, dict) else {}
    return {k: got[k] for k in ("model", "effort") if isinstance(got.get(k), str) and got[k]}

# A claim's rename lands within seconds. One not landed after this many was
# lost on the way, and is typed again.
RENAME = 10

# Seconds after typing that a row's shell has had to start Claude, and how
# many more times its boot line is typed when it has not. Eight rows of one
# launch each started Claude within 3 seconds of their shell.
STARTED = 10
RETYPES = 2

# A page's steps, so a failed row explains itself. The file sits beside its
# launch.json, and tools/launch-page.py deletes both once no row is left. A
# row carries its file's path as "log". A row with none, as a one-pane launch
# from tools/launch.py, logs nothing: that launch prints its own failure.
LOG = "launch-log.jsonl"

# The row each pane's refused writes belong to, while its launch runs.
WATCHED: dict = {}


def note(row: dict, pane: str, step: str, answer="") -> None:
    """Write one step to the row's log. A log that cannot be written never
    stops a launch."""
    if not row.get("log"):
        return
    try:
        with open(row["log"], "a") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "n": row.get("n", ""),
                                "pane": pane, "step": step, "answer": answer}) + "\n")
    except OSError:
        pass


def refused(pane: str, why: str) -> None:
    """A write iTerm refused, in the log of the row its pane belongs to."""
    if pane in WATCHED:
        note(WATCHED[pane], pane, "iTerm refused a write", why)


panes.MISSED[0] = refused


def browser(row: dict) -> bool:
    return row.get("kind") == "browser"


def chrome(row: dict) -> bool:
    """Whether a session row's message opens with /drive-chrome. Such a
    session runs only on the account driving my Chrome, accounts.CHROME:
    any other has no way to click it."""
    words = str(row.get("message", "")).split()
    return not browser(row) and bool(words) and words[0] == "/drive-chrome"


def browser_number(nn: str, name: str) -> int:
    """K, when a pane's name is NN-browser-K. Otherwise 0."""
    m = re.fullmatch(rf"{nn}-browser-(\d+)", name or "")
    return int(m.group(1)) if m else 0


def browsers_named(nn: str, tree=None) -> list:
    """Every K already open as a pane named NN-browser-K. `tree` is iTerm's
    layout, for a caller already holding it."""
    found = set()

    def walk(n):
        if "split" in n:
            for c in n["children"]:
                walk(c)
        elif k := browser_number(nn, n.get("name")):
            found.add(k)

    for w in iterm.tree() if tree is None else tree:
        for t in w["tabs"]:
            walk(t["root"])
    return sorted(found)


def own_page(row: dict) -> bool:
    """Whether a browser row shows one of this layer's own pages: a port
    of layer 1, the shift taken off."""
    return 1000 <= ports.plain(ports.of(address(row))) <= 1999


def browser_name(nn: str, taken=(), opened=None) -> str:
    """The next NN-browser-K, past every one open and every one in `taken`.
    `opened` is browsers_named's, for a caller already holding it."""
    used = set(browsers_named(nn) if opened is None else opened) | set(taken)
    k = next(k for k in range(1, 1000) if k not in used)
    return f"{nn}-browser-{k}"


def address(row: dict) -> str:
    """A browser row's site, as an address. A bare port is a page on this machine."""
    site = str(row.get("site", "")).strip()
    if site.isdigit():
        return f"http://localhost:{site}"
    return site if "://" in site else f"http://{site}"


def live() -> set:
    running = registry.claude_records()
    return {k for k, v in registry.entries().items() if registry.pid_of(v, running)}


def teams(held: dict) -> set:
    """Every ten an assistant leads, by its digit: "1" while 10 holds a plan."""
    return {n[0] for n in held if n[1] == "0" and plans.plan(n).get("stages")}


def team_work(seat: str, name: str) -> bool:
    """Whether a launch named `name` is assistant `seat`'s team work: one of
    its plan's missions, under the mission's name, or a mission's helper,
    named as helper-session names it, "C1 helper frontend"."""
    words = registry.kebab(name)
    missions = [m for s in plans.plan(seat).get("stages", []) for m in s.get("missions", [])]
    return bool(words) and any(words == registry.kebab(m.get("name", ""))
                               or words.startswith(f"{registry.kebab(m.get('id', ''))}-helper")
                               for m in missions)


def free(taken=(), by: str = "", name: str = "") -> list:
    """The numbers a launch by session `by`, named `name`, may take, in the
    order it tries them.

    Only missions and helpers take a team's ten, past its seat: assistant
    10's missions and their helpers take 11 to 19, launched by 10 or a
    session in its ten. Every other launch is a side session's, whoever
    launches it: 02 to 09, then on past 09, around every assistant's ten.
    knowledge/0010-playbook/0019-targeted/the-map/running-locally.md rules it.
    01 is the advisor's seat: none is given it unless it names it, as
    my-advisor does.

    A number is free when no live session holds it, its folder holds no
    work, and no other launch holds it. A session that died without stopping
    leaves its work there, and claiming its number would sweep it.
    """
    held, taken, running = registry.entries(), set(taken), registry.claude_records()
    led = teams(held)
    ten = str(by)[:1] if re.fullmatch(r"\d{2}", str(by)) else ""
    pool = ([f"{ten}{i}" for i in range(1, 10)] if ten in led and team_work(f"{ten}0", name) else
            [n for n in (f"{i:02d}" for i in range(2, 100)) if n[0] not in led])
    return [n for n in pool if n not in taken and registry.free(n, held, running)]


def seat() -> str:
    """The seat a new assistant takes: the zero of the lowest ten no session
    holds. Side sessions on 10 to 12 make it 20. Empty when no ten is free."""
    held, running = registry.entries(), registry.claude_records()
    return next((f"{d}0" for d in range(1, 10)
                 if all(registry.free(f"{d}{i}", held, running) for i in range(10))), "")


def problems(rows: list) -> list:
    """What stops a launch, one line per row at fault."""
    held = live()
    seen, out = set(), []
    for i, r in enumerate(rows, 1):
        if browser(r):
            site = str(r.get("site", "")).strip()
            if not site or " " in site or (site.isdigit() and not 1 <= int(site) <= 65535):
                out.append(f"Row {i}: a site is a port, or an address.")
            continue
        n = str(r.get("n", ""))
        if not (n.isdigit() and len(n) == 2 and 1 <= int(n) <= 99):
            out.append(f"Row {i}: a number is 01 to 99.")
        elif n in held:
            out.append(f"Row {i}: {n} is held by a live session.")
        elif registry.files(n):
            out.append(f"Row {i}: {n}'s folder holds a stopped session's work.")
        elif n in seen:
            out.append(f"Row {i}: {n} is on another row too.")
        elif r.get("clone") and not cloned(str(r["clone"])):
            out.append(f"Row {i}: {refuse_clone(str(r['clone']))}")
        elif chrome(r) and r.get("account") and str(r["account"]) != accounts.CHROME:
            out.append(f"Row {i}: /drive-chrome runs only on account {accounts.CHROME}, the one "
                       f"driving Chrome. Account {r['account']} cannot click it.")
        # An account left unnamed is taken at launch, so a stand-in checks the rest.
        elif not line({**r, "account": r.get("account") or accounts.FALLBACK}):
            out.append(f"Row {i}: its account, model or effort is refused.")
        seen.add(n)
    return out


def line(row: dict) -> str:
    """A session row's boot line. A model or an effort it leaves unset is
    the one set on System now. A row with a clone starts forked from that
    session's conversation. Empty when its clone has nothing to fork."""
    now = default()
    fork = ""
    if row.get("clone"):
        fork = cloned(str(row["clone"])).get("session_id", "")
        if not fork:
            return ""
    return panes.boot_line(row.get("name", ""), row.get("account", ""), row.get("model") or now["model"],
                           row.get("effort") or now["effort"], row.get("n", ""), fork)


def cloned(nn: str) -> dict:
    """What a row cloning session NN forks from, its record's session_id,
    account and transcript. {} when NN has no record, or no session_id."""
    if not str(nn).isdigit():
        return {}
    try:
        with open(os.path.join(registry.folder(nn), registry.RECORD)) as f:
            rec = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(rec, dict) or not rec.get("session_id"):
        return {}
    return {k: str(rec.get(k) or "") for k in ("session_id", "account", "transcript")}


def refuse_clone(nn: str) -> str:
    """The one sentence a clone nothing can fork from is refused with."""
    return f"Session {nn} has no conversation to clone."


def carry(target: dict, acct: str, folders: dict | None = None) -> str:
    """Copy a clone's transcript into account ACCT's own projects folder,
    under the same name, so --resume finds it there. The original is never
    moved or changed. The same account copies nothing. `folders` is each
    account's config folder, lib/accounts.py's by default. The path the
    fork reads, or "" when there is no transcript to carry."""
    src = target.get("transcript", "")
    folders = folders or {a: v["folder"] for a, v in accounts.ACCOUNTS.items()}
    if not (src and os.path.isfile(src)):
        return ""
    if str(acct) == str(target.get("account")) or str(acct) not in folders:
        return src
    dest = os.path.join(folders[str(acct)], "projects", os.path.basename(os.path.dirname(src)),
                        os.path.basename(src))
    if os.path.abspath(dest) == os.path.abspath(src):
        return src
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    shutil.copyfile(src, part)
    os.replace(part, dest)
    return dest


def leaves(n: dict) -> list:
    """A tab's pane ids, in the order the page reads them."""
    return [p for c in n["children"] for p in leaves(c)] if "split" in n else [n["pane"]]


def home(tree: list, starter: str) -> tuple:
    """Where a row with no place lands, as (window, tab): the starter's tab,
    else the first live tab, else a new window."""
    tabs = [(f"L:{w['window']}", f"L:{t['tab']}", leaves(t["root"])) for w in tree for t in w["tabs"]]
    return next(((w, t) for w, t, ps in tabs if starter in ps),
                next(((w, t) for w, t, _ in tabs), ("N1", "N1")))


def fill(rows: list, free, place: tuple, opened, nn: str) -> None:
    """What a row left unset takes: its place, `place`; the lowest number
    `free` gives its name; a browser's next name, past those `opened`; a
    card's pos, past every other. It never sets an account, model or
    effort: default() says when each is given.

    A number a session wrote as a JSON number, 91, becomes "91", as every
    record is keyed. Left a number, its claim was never seen."""
    for r in rows:
        if not browser(r) and type(r.get("n")) is int:
            r["n"] = f"{r['n']:02d}"
    taken = {r.get("n") for r in rows if not browser(r) and r.get("n")}
    ks = {browser_number(nn, r.get("name")) for r in rows if browser(r)}
    top = max([r["pos"] for r in rows if isinstance(r.get("pos"), int)], default=-1)
    for r in rows:
        if not isinstance(r.get("pos"), int):
            top += 1
            r["pos"] = top
        if not r.get("win"):
            r["win"], r["tab"] = place
        r.setdefault("at", None)
        if browser(r):
            if not r.get("name"):
                r["name"] = browser_name(nn, ks, opened)
                ks.add(browser_number(nn, r["name"]))
            continue
        if not r.get("n"):
            r["n"] = next((n for n in free(r.get("name", "")) if n not in taken), "")
            taken.add(r["n"])


def settle(rows: list, tree: list, starter: str) -> None:
    """Give each row, in launch order, a place standing in `tree`, the layout
    as iTerm gives it.

    A window is "L:<id>", a tab too, and an anchor "p:<pane id>" or a row
    before it, "r:<uid>". A new window or tab, "N1", stands until it opens,
    and a new window holds only new tabs. A window or tab gone lands in the
    starter's tab. An anchor gone, or a side iTerm has not, takes the
    default: below the last row before it in that tab, else below the
    starter, else below the tab's last pane. The first row in an empty
    tab fills it.
    """
    live = {f"L:{w['window']}": {f"L:{t['tab']}": leaves(t["root"]) for t in w["tabs"]} for w in tree}
    place = home(tree, starter)
    new = lambda k: str(k or "").startswith("N")
    for i, r in enumerate(rows):
        win, tab = str(r.get("win") or ""), str(r.get("tab") or "")
        tabs = list(live.get(win, {})) + [s.get("tab") for s in rows if s.get("win") == win and new(s.get("tab"))]
        if not (win in live or new(win)) or tab not in tabs:
            win, tab = place
        r["win"], r["tab"] = win, tab
        here = live.get(win, {}).get(tab, [])
        before = [s for s in rows[:i] if s["win"] == win and s["tab"] == tab]
        ids = [f"p:{p}" for p in here] + [f"r:{s['uid']}" for s in before]
        at = r.get("at") if isinstance(r.get("at"), dict) else {}
        if not ids:
            r["at"] = None
        elif at.get("anchor") not in ids or at.get("side") not in iterm.SIDES:
            r["at"] = {"anchor": f"r:{before[-1]['uid']}" if before
                       else f"p:{starter}" if starter in here else f"p:{here[-1]}", "side": "down"}


def place(row: dict, made: dict, windows: dict) -> str:
    """Open one row's pane where it was placed. Its id, or empty.

    `made` maps each earlier row's uid to its pane, so a row can land beside
    one opened moments before. `windows` maps each new window to its id.
    """
    pane = opened(row, made, windows)
    note(row, pane, "pane opened", True if pane else iterm.why() or False)
    return pane


def opened(row: dict, made: dict, windows: dict) -> str:
    """place's work, on iTerm."""
    web = address(row) if browser(row) else ""
    at, win = row.get("at"), str(row.get("win", ""))
    if at:
        a = str(at.get("anchor", ""))
        target = a[2:] if a.startswith("p:") else made.get(a[2:], "")
        if not target:
            return ""
        pane = iterm.split(target, at.get("side", ""), web)[0]
        if not pane:
            # A split that fails once often opens a second later.
            time.sleep(1)
            pane = iterm.split(target, at.get("side", ""), web)[0]
        return pane
    if win.startswith("L:"):
        return iterm.tab(win[2:], web)[0]
    if win in windows:
        return iterm.tab(windows[win], web)[0]
    pane, windows[win] = iterm.window(web)
    return pane


def start(row: dict, pane: str) -> None:
    """Start what runs in a new pane. A session has its boot line typed.

    A browser pane is named, once its page has loaded. One of this layer's
    own pages already names itself, so it is left alone.

    A session with no account named takes the order's next turn here, once
    its pane is open, so a launch that never opens takes none. One opening
    /drive-chrome takes Chrome's account instead, and no turn. Its line
    reads an unnamed model and effort here too.

    A clone's transcript is carried into its account's folder first: carry().
    """
    if browser(row):
        if row.get("name") and not own_page(row):
            iterm.name(pane, row["name"], wait=True)
        return
    if not row.get("account"):
        row["account"] = accounts.CHROME if chrome(row) else accounts.take()
    if row.get("clone"):
        note(row, pane, "transcript carried", carry(cloned(str(row["clone"])), row["account"]))
    WATCHED[pane] = row
    panes.settle(pane)
    note(row, pane, "boot line typed", panes.say(pane, line(row)))


def reusable(row: dict) -> bool:
    """Whether a failed row's pane stands open with only its shell running,
    so Launch again types there. A pane running anything else is left alone."""
    pane = row.get("pane")
    return bool(pane) and pane in (panes.terminals() or {}) and panes.programs(pane) == []


def kept(row: dict, pane: str, made: dict) -> dict:
    """What a failed row keeps for Launch again: its pane and the live tab
    holding it, and its neighbour as a pane, since that neighbour's row
    leaves the file once its session is live. `made` is launch.place's."""
    keep = {"pane": pane}
    at = row.get("at")
    if isinstance(at, dict) and str(at.get("anchor", "")).startswith("r:") and made.get(at["anchor"][2:]):
        keep["at"] = {**at, "anchor": f"p:{made[at['anchor'][2:]]}"}
    for w in iterm.tree():
        for t in w["tabs"]:
            if pane in leaves(t["root"]):
                keep.update(win=f"L:{w['window']}", tab=f"L:{t['tab']}")
    return keep


def renamed(session_id: str, title: str) -> bool:
    """Whether Claude Code's own record already carries the new title. Each
    listed account's sessions folder is read: registry.LIVE."""
    for base in registry.LIVE:
        for f in glob.glob(os.path.join(base, "sessions", "*.json")):
            try:
                with open(f) as fh:
                    d = json.load(fh)
            except (OSError, ValueError):
                continue
            if d.get("sessionId") == session_id and d.get("name") == title:
                return True
    return False


def arrive(row: dict, pane: str, by: str = "") -> bool:
    """Wait for the session to claim its number, then hand it its message.

    Once it claims, its record takes `by`: the session that launched it.
    Each launch records who launched it. It makes no team. Its folder
    takes its NAMED file then, before anything is typed.

    Claiming types /rename into its own pane, once. A message typed before
    that rename lands joins onto it, so the rename is waited for first. One
    lost on the way is typed again, onto a cleared prompt.

    A boot line can be lost too, so STARTED seconds after it is typed, the
    pane is read. No Claude there, the line is typed again: RETYPES. Claude
    there, the session has the rest of CLAIM to claim.

    False means the row failed, and row["why"] says why.

    Both waits are heard. A claim counts once its record stands and Claude
    Code's own records show it running, so the claim wait hears both, and
    reads Claude Code's fresh: one a second old can miss a session that
    just started, and nothing else would ask again. A claim empties the
    number's folder by deleting and making it again, so each time a watched
    path comes or goes, the watch is set anew on what stands.
    """
    end = time.time() + registry.CLAIM
    own = registry.folder(row["n"])

    def claimed() -> dict:
        rec = registry.entries().get(row["n"]) or {}
        pid = registry.pid_of(rec, registry.claude_records(fresh=True)) if rec else 0
        return rec if pid and panes.pane(rec, pid) == pane else {}

    def standing() -> list:
        paths = [own, os.path.join(own, registry.RECORD)] + registry.watched(())
        return [(p, os.stat(p).st_ino if os.path.exists(p) else 0) for p in paths]

    rec = claimed()
    check, typed = time.time() + STARTED, 0
    while not rec and time.time() < end:
        was = standing()
        hear.until(lambda: bool(claimed()) or standing() != was,
                   files=[p for p, _ in was], seconds=min(end, check) - time.time())
        rec = claimed()
        if rec or time.time() < check:
            continue
        running = panes.programs(pane)
        note(row, pane, "programs in its pane", running)
        if running is None:
            check = time.time() + 1
        elif any(c.split()[0].rsplit("/", 1)[-1] == "claude" for c in running):
            check = end
        elif typed < RETYPES:
            typed += 1
            panes.settle(pane)
            note(row, pane, "boot line typed again", panes.say(pane, line(row)))
            check = time.time() + STARTED
        else:
            row["why"] = "Claude never started in its pane."
            note(row, pane, "failed", row["why"])
            return False
    if not rec:
        row["why"] = f"{row['n']} never claimed its number."
        note(row, pane, "failed", row["why"])
        return False
    note(row, pane, "claimed", rec.get("session_id", ""))
    if by and by != row["n"]:
        with open(os.path.join(registry.folder(row["n"]), registry.RECORD)) as f:
            registry.write({**json.load(f), "by": by})
    with open(os.path.join(registry.folder(row["n"]), NAMED), "w") as f:
        json.dump({k: row[k] for k in ("model", "effort") if row.get(k)}, f)
        f.write("\n")
    named = lambda: renamed(rec.get("session_id"), rec.get("title"))
    if not hear.until(named, files=registry.watched(()),
                      seconds=min(RENAME, max(0.0, end - time.time()))):
        # Nothing checks the claim's rename. A rename typed and never sent
        # would join this one, so the prompt is emptied first.
        panes.settle(pane)
        note(row, pane, "rename typed again", panes.say(pane, f"/rename {rec.get('title')}"))
        hear.until(named, files=registry.watched(()), seconds=max(0.0, end - time.time()))
    # The rename is typed, then lands. A second lets it land.
    time.sleep(1)
    message = " ".join(str(row.get("message", "")).split())
    if row.get("drive") is True:
        message = f"/self-drive {message}".strip()
    if message:
        typed = panes.say(pane, message)
        note(row, pane, "first message typed", typed)
        if not typed:
            row["why"] = f"{row['n']} started, but its first message did not reach it."
            return False
    return True


# ---- a launch page's file ---------------------------------------------------------

FILE = "launch.json"


class Locked:
    """One writer at a time on every launch page's file: one thread in this
    process, and one process on this Mac, by a lock on the sessions folder
    itself, as lib/follow.py's editing() takes a seat's. 1100, a launch, a
    scheduled fire and the app door each run in a process of their own,
    and each marks rows."""

    def __init__(self):
        self.one, self.fd = threading.Lock(), -1

    def __enter__(self):
        self.one.acquire()
        try:
            self.fd = os.open(registry.WORK, os.O_RDONLY)
            fcntl.flock(self.fd, fcntl.LOCK_EX)
        except OSError:
            # No sessions folder stands yet, so no other process writes one.
            pass

    def __exit__(self, *left):
        if self.fd >= 0:
            os.close(self.fd)
        self.fd = -1
        self.one.release()


LOCK = Locked()
MOVES = "moves"
LAYOUTS = "layouts"

# The key that schedules a page: the stage whose close fires it.
AFTER = "after"
# The key that launches a page's rows as my own page's: naming no session.
ALONE = "alone"

# My own page's number. No session is behind it.
MINE = "00"

# What a row may carry. Anything else in the file is dropped on save.
KEYS = ("uid", "kind", "n", "name", "message", "account", "model", "effort", "drive", "clone", "site",
        "win", "tab", "at", "pos", "status", "pane", "by")


def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), FILE)


def logfile(nn: str) -> str:
    """This page's launch log, beside its file: LOG."""
    return os.path.join(os.path.dirname(path(nn)), LOG)


class Unreadable(ValueError):
    """A launch page's file that stands and cannot be read."""


def whole(nn: str) -> dict:
    """The page's whole file, {} with none. One caught half-written, as a
    session's own write leaves it for a moment, is read again, for a fifth
    of a second. One that never reads raises Unreadable."""
    for _ in range(10):
        try:
            with open(path(nn)) as f:
                got = json.load(f)
            if isinstance(got, dict):
                return got
        except OSError:
            return {}
        except ValueError:
            pass
        time.sleep(0.02)
    raise Unreadable(f"{path(nn)} cannot be read")


def standing(nn: str) -> dict:
    """whole(nn), or {} for a file that cannot be read: what a reader shows."""
    try:
        return whole(nn)
    except Unreadable:
        return {}


def read(nn: str) -> list:
    """Every row, as the file holds it. Reading never writes, so 1100's model reads here."""
    rows = standing(nn).get("rows", [])
    return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []


def moves(nn: str) -> list:
    """The moves waiting for this page's launch."""
    got = standing(nn).get(MOVES, [])
    return got if isinstance(got, list) else []


def layouts(nn: str) -> list:
    """The preview's target shapes for the tabs with planned moves."""
    got = standing(nn).get(LAYOUTS, [])
    return got if isinstance(got, list) else []


def scheduled(nn: str) -> str:
    """The stage whose close fires this page, or "" when my press launches it."""
    got = standing(nn).get(AFTER, "")
    return got if isinstance(got, str) else ""


def alone(nn: str) -> bool:
    """Whether this page's rows launch naming no session, as my own page's do."""
    return standing(nn).get(ALONE) is True


def numbered(rows: list) -> list:
    """Each row a uid, past the highest one held, in file order: the rows the
    session wrote with none. Returns those it gave one."""
    top = max([r["uid"] for r in rows if isinstance(r.get("uid"), int)], default=0)
    fresh = []
    for r in rows:
        if not isinstance(r.get("uid"), int):
            top += 1
            r["uid"] = top
            fresh.append(r)
    return fresh


def load(nn: str) -> list:
    """Every row, each with a uid. A row the session just wrote gets one
    here, and System's account, model and effort for any it left unnamed."""
    rows = read(nn)
    if not rows:
        return []
    fresh = numbered(rows)
    if fresh:
        made(fresh)
        save(nn, rows)
    return rows


def system(row: dict, key: str) -> str:
    """What System gives a session row's account, model or effort: the
    order's next account, its turn taken now, or Chrome's for a row opening
    /drive-chrome, with no turn; the model and effort set on 1100/system."""
    if key == "account":
        return accounts.CHROME if chrome(row) else accounts.take()
    return default()[key]


def made(rows: list) -> None:
    """Give each session row System's account, model and effort, for each
    it holds none of. Given once, as the row is first saved, so no row ever
    follows System, or the order, after: only a press on its pill changes it."""
    for r in rows:
        if not browser(r):
            for k in ("account", "model", "effort"):
                if not r.get(k):
                    r[k] = system(r, k)


def save(nn: str, rows: list, planned=None, shapes=None) -> None:
    """Write the rows, whole at once, so no reader meets half a file. No
    row left means no file and no launch log. My own page's folder holds
    nothing else, so it comes with the file and goes with it. A scheduled
    page stays scheduled, and a page alone stays alone. A file that stands
    and cannot be read is never written over, nor removed: Unreadable."""
    whole(nn)
    if not rows:
        for gone in (logfile(nn), path(nn)):
            try:
                os.remove(gone)
            except OSError:
                pass
        if nn == MINE:
            try:
                os.rmdir(registry.folder(nn))
            except OSError:
                pass
        return
    if nn == MINE:
        os.makedirs(registry.folder(nn), exist_ok=True)
    after, single = scheduled(nn), alone(nn)
    planned = moves(nn) if planned is None else planned
    shapes = layouts(nn) if shapes is None else shapes
    put(nn, {**({AFTER: after} if after else {}), **({ALONE: True} if single else {}),
             **({MOVES: planned} if planned else {}), **({LAYOUTS: shapes} if shapes else {}),
             "rows": [{k: r[k] for k in KEYS if k in r} for r in rows]})


def put(nn: str, d: dict) -> None:
    """The page's whole file, swapped in at once, so no reader meets half
    of it, and keeping its birth: registry.rewrite."""
    registry.rewrite(path(nn), json.dumps(d, indent=2) + "\n")


def launcher(nn: str) -> str:
    """The session this page's rows name as the one that launched them: its
    own, unless its page is alone. My own page names none."""
    return "" if nn == MINE or alone(nn) else nn


def mark(nn: str, uid: int, status, keep: dict | None = None) -> None:
    """Set one row's status and what it keeps, or remove the row once its
    session is live."""
    with LOCK:
        rows = load(nn)
        if status is None:
            rows = [r for r in rows if r["uid"] != uid]
        else:
            for r in rows:
                if r["uid"] == uid:
                    r.update(keep or {}, status=status)
        save(nn, rows)


def unboot(nn: str, why: str = "its launch was cut short", spared=()) -> None:
    """A row left booting with nothing running it would lock the page, so it
    fails instead, unless its uid is spared. A launch stopped by an error
    calls this, and so does one picked up after its program died."""
    with LOCK:
        rows = load(nn)
        cut = lambda r: r.get("status") == "booting" and r["uid"] not in spared
        if not any(cut(r) for r in rows):
            return
        for r in rows:
            if cut(r) and r.get("n"):
                registry.release(r["n"])
                note({**r, "log": logfile(nn)}, r.get("pane", ""), "failed", why)
        save(nn, [dict(r, status=f"failed: {why}. Launch again.") if cut(r) else r for r in rows])


def typed(nn: str) -> set:
    """The numbers whose first message this page's launch log shows typed."""
    try:
        with open(logfile(nn)) as f:
            steps = [json.loads(s) for s in f if s.strip()]
    except (OSError, ValueError):
        return set()
    return {s.get("n") for s in steps if s.get("step") == "first message typed" and s.get("answer") is True}


# ---- a launch page's launch ---------------------------------------------------------

def follow(nn: str, row: dict, pane: str, by: str, made: dict) -> None:
    """A session row leaves the file once its session is live. Its record
    names `by`, the page's launcher, as the one that launched it. A row that
    fails keeps its pane and its place for Launch again: kept."""
    try:
        if arrive(row, pane, by):
            mark(nn, row["uid"], None)
            return
        why = row["why"]
    except Exception as e:
        traceback.print_exc()
        why = f"{type(e).__name__}: {e}."
        note(row, pane, "failed", why)
    finally:
        WATCHED.pop(pane, None)
    registry.release(row["n"])
    mark(nn, row["uid"], f"failed: {why}", kept(row, pane, made))


def move_problems(planned: list, rows: list, wins: list) -> list:
    """Refuse moves whose panes or destinations no longer share their tab."""
    tabs = {(f"L:{w['window']}", f"L:{t['tab']}"): set(leaves(t["root"]))
            for w in wins for t in w["tabs"]}
    for m in planned:
        if not isinstance(m, dict) or m.get("side") not in iterm.SIDES:
            return ["A planned move is invalid. Undo it and arrange again."]
        place = (m.get("win"), m.get("tab"))
        ids = {f"p:{p}" for p in tabs.get(place, set())}
        ids.update(f"r:{r['uid']}" for r in rows if (r.get("win"), r.get("tab")) == place)
        if m.get("source") not in ids or m.get("anchor") not in ids or m["source"] == m["anchor"]:
            return ["A planned pane moved or disappeared. Undo the moves and arrange again."]
    return []


def shape_problems(planned: list, shapes: list, rows: list, wins: list) -> list:
    """Require each affected tab's complete, unambiguous target shape."""
    wanted = {(m.get("win"), m.get("tab")) for m in planned if isinstance(m, dict)}
    tabs = {(f"L:{w['window']}", f"L:{t['tab']}"): set(leaves(t["root"]))
            for w in wins for t in w["tabs"]}
    seen_tabs = set()
    try:
        for shape in shapes:
            place = (shape["win"], shape["tab"])
            if place not in tabs or place in seen_tabs:
                raise ValueError()
            seen_tabs.add(place)
            refs = []
            def visit(n, parent=None):
                if set(n) == {"ref"} and isinstance(n["ref"], str):
                    refs.append(n["ref"])
                    return
                if (set(n) != {"split", "children"} or n["split"] not in ("columns", "rows")
                        or n["split"] == parent or not isinstance(n["children"], list)
                        or len(n["children"]) < 2):
                    raise ValueError()
                for child in n["children"]:
                    visit(child, n["split"])
            visit(shape["root"])
            expected = {f"p:{p}" for p in tabs[place]}
            expected.update(f"r:{r['uid']}" for r in rows if (r.get("win"), r.get("tab")) == place)
            if len(refs) != len(set(refs)) or set(refs) != expected:
                raise ValueError()
        if seen_tabs != wanted:
            raise ValueError()
    except (TypeError, KeyError, ValueError, RecursionError):
        return ["The planned layout changed. Undo the moves and arrange again."]
    return []


def layout_spec(shapes: list, made: dict) -> dict:
    """Replace preview row references with the panes that were opened."""
    def convert(n):
        if "ref" in n:
            ref = n["ref"]
            pane = ref[2:] if ref.startswith("p:") else made[ref[2:]]
            return {"session_id": pane}
        return {"vertical": n["split"] == "columns", "children": [convert(c) for c in n["children"]]}
    return {"tabs": [{"tab_id": s["tab"][2:], "root": convert(s["root"])} for s in shapes]}


def layout_matches(spec: dict, wins: list, exact: bool = False) -> bool:
    """Check that no unexpected pane would be affected; optionally check shape."""
    tabs = {t["tab"]: t["root"] for w in wins for t in w["tabs"]}
    def ids(n):
        return [n["session_id"]] if "session_id" in n else [v for c in n["children"] for v in ids(c)]
    def actual(n):
        if "split" not in n:
            return {"session_id": n["pane"]}
        return {"vertical": n["split"] == "columns", "children": [actual(c) for c in n["children"]]}
    return all(t["tab_id"] in tabs and (actual(tabs[t["tab_id"]]) == t["root"] if exact
               else set(leaves(tabs[t["tab_id"]])) == set(ids(t["root"]))) for t in spec["tabs"])


def go(nn: str) -> None:
    """Open every booting row's pane, in row order, and start what runs in
    it. An error ends only its row. A row still booting once nothing runs
    it fails: unboot."""
    waits: list = []
    try:
        opening(nn, waits)
    except Exception:
        traceback.print_exc()
    for t in waits:
        t.join()
    unboot(nn, "its launch stopped on an error")


def opening(nn: str, waits: list) -> None:
    """go's work. Each session's wait, on a thread of its own, joins `waits`.
    The launcher is read first: the file goes with its last row."""
    with LOCK:
        rows = [dict(r, log=logfile(nn)) for r in load(nn) if r.get("status") == "booting"]
        by, planned, shapes = launcher(nn), moves(nn), layouts(nn)
    if planned:
        now = iterm.tree()
        if move_problems(planned, rows, now) or shape_problems(planned, shapes, rows, now):
            for r in rows:
                if not browser(r):
                    registry.release(r["n"])
                mark(nn, r["uid"], "failed: arrangement changed before launch.")
            return
    made, windows, opened = {}, {}, []
    def stopped(r, e):
        traceback.print_exc()
        if not browser(r):
            registry.release(r["n"])
        note(r, r.get("pane", ""), "failed", f"{type(e).__name__}: {e}")
        mark(nn, r["uid"], f"failed: {type(e).__name__}: {e}.")
    def start_one(r, pane):
        try:
            if browser(r):
                mark(nn, r["uid"], None)
                threading.Thread(target=start, args=(r, pane)).start()
            else:
                start(r, pane)
                # Its pane and account are saved, so a launch picked up resumes it.
                mark(nn, r["uid"], "booting", {"pane": pane, "account": r["account"]})
                t = threading.Thread(target=follow, args=(nn, r, pane, by, made))
                t.start()
                waits.append(t)
        except Exception as e:
            stopped(r, e)
    for r in rows:
        try:
            # A planned layout counts every open pane as its own, so only a
            # plain launch reuses a failed row's pane.
            if not planned and reusable(r):
                pane = r["pane"]
                note(r, pane, "pane reused", True)
            else:
                pane = place(r, made, windows)
        except Exception as e:
            stopped(r, e)
            continue
        if not pane:
            if not browser(r):
                registry.release(r["n"])
            mark(nn, r["uid"], "failed: the pane did not open.")
            continue
        made[str(r["uid"])] = pane
        if planned:
            opened.append((r, pane))
        else:
            start_one(r, pane)
    if not planned:
        return
    # No existing pane moves until every new pane is open. A failure closes
    # only these unstarted panes; existing sessions are never closed.
    if len(opened) == len(rows):
        safe = verified = False
        refused = ""
        try:
            spec = layout_spec(shapes, made)
            safe = layout_matches(spec, iterm.tree())
            applied = safe and iterm.apply_layout(spec)
            # Too old an iTerm2 refuses the move in one line, ending
            # "Nothing moved.": the rows read it in place of their own.
            if safe and not applied and iterm.why().endswith("Nothing moved."):
                refused = iterm.why()
            verified = applied and layout_matches(spec, iterm.tree(), exact=True)
        except Exception:
            traceback.print_exc()
        if not verified:
            for r, pane in opened:
                closed = iterm.close(pane)
                if not browser(r):
                    registry.release(r["n"])
                note_ = (refused[:1].lower() + refused[1:-1] if refused
                         else "arrangement stopped; existing panes may have moved" if safe
                         else "arrangement changed before launch")
                if not closed:
                    note_ += "; an unstarted pane could not be closed"
                mark(nn, r["uid"], "failed: " + note_ + ".")
            return
        with LOCK:
            save(nn, load(nn), [], [])
    else:
        # Some pane failed to open. Do not change any existing session.
        for r, pane in opened:
            closed = iterm.close(pane)
            if not browser(r):
                registry.release(r["n"])
            mark(nn, r["uid"], "failed: arrangement was not applied"
                 + ("; an unstarted pane could not be closed" if not closed else "") + ".")
        return
    for r, pane in opened:
        start_one(r, pane)


def picked_up(nn: str) -> None:
    """A launch whose program died, picked up by a new one. A session row
    whose message the log shows typed is live, and leaves the file. One
    whose pane stands goes on from its claim: arrive, then its first
    message. Every other row booting fails: unboot."""
    with LOCK:
        rows = [dict(r, log=logfile(nn)) for r in load(nn) if r.get("status") == "booting"]
    if not rows:
        return
    done, open_ = typed(nn), panes.terminals() or {}
    spared, waits = set(), []
    for r in rows:
        if browser(r) or not r.get("pane"):
            continue
        if r.get("n") in done:
            mark(nn, r["uid"], None)
        elif r["pane"] in open_:
            note(r, r["pane"], "resumed by a new launch", True)
            WATCHED[r["pane"]] = r
            t = threading.Thread(target=follow, args=(nn, r, r["pane"], launcher(nn), {}))
            t.start()
            waits.append(t)
        else:
            continue
        spared.add(r["uid"])
    unboot(nn, spared=spared)
    for t in waits:
        t.join()


# ---- one launch of a page at a time, as a program of its own ----------------------

# The program a press starts: tools/launch.py page NN.
PROGRAM = [sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "tools", "launch.py"), "page"]


def held_at(nn: str) -> str:
    """The file whose lock a launch of session NN's page holds while it
    runs, in this module's own state folder, beside the sessions folder."""
    return os.path.join(os.path.dirname(registry.WORK), "launches", f"{nn}.lock")


def claim(nn: str) -> int:
    """The lock of session NN's page's launch, taken: its descriptor, or -1
    while another launch of the page holds it. Held until it is closed, or
    its process ends, however it ends."""
    os.makedirs(os.path.dirname(held_at(nn)), exist_ok=True)
    fd = os.open(held_at(nn), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return -1
    return fd


def running(nn: str) -> bool:
    """Whether a launch of session NN's page runs now, in any process."""
    fd = claim(nn)
    if fd < 0:
        return True
    os.close(fd)
    return False


def run(nn: str, fd: int = -1, resume: bool = False) -> None:
    """Session NN's page's launch, in this process, holding its lock: `fd`,
    handed over by the press that marked its rows, or taken now. While
    another launch holds it, nothing runs. `resume` picks up a launch whose
    program died."""
    if fd < 0:
        fd = claim(nn)
        if fd < 0:
            return
    try:
        (picked_up if resume else go)(nn)
    finally:
        os.close(fd)


def begin(nn: str, fd: int, resume: bool = False) -> None:
    """Session NN's page's launch, started as its own program, PROGRAM,
    which takes over the lock `fd`: this process lets go of it. The program
    runs on in a session of its own, so 1100 stopping never stops it. What
    it prints goes to a log beside its lock."""
    try:
        with open(os.path.join(os.path.dirname(held_at(nn)), f"{nn}.log"), "ab") as log:
            subprocess.Popen([*PROGRAM, nn, "--held", str(fd)] + (["--resume"] if resume else []),
                             stdin=subprocess.DEVNULL, stdout=log, stderr=log, pass_fds=(fd,),
                             start_new_session=True, cwd=registry.ROOT)
    finally:
        os.close(fd)
