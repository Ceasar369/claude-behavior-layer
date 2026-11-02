#!/usr/bin/env python3
"""launch.py — opening a launched pane, and starting what runs in it.

The launch page and tools/launch.py both come here, so a row placed on the
page and one passed as flags open the same way.

A row is one pane. Its kind is a session, or a browser.

  session   n, name, message, account, model, effort, and drive
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

Imported, never run.
"""

import glob
import json
import os
import re
import time

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
    """What a session row I left unset starts at, read as its pane opens:
    the model and effort set on System. Its account is the order's
    next, taken then too: accounts.py."""
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


def browser(row: dict) -> bool:
    return row.get("kind") == "browser"


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
        # An account left unnamed is taken at launch, so a stand-in checks the rest.
        elif not line({**r, "account": r.get("account") or accounts.FALLBACK}):
            out.append(f"Row {i}: its account, model or effort is refused.")
        seen.add(n)
    return out


def line(row: dict) -> str:
    """A session row's boot line. A model or an effort it leaves unset is
    the one set on System now."""
    now = default()
    return panes.boot_line(row.get("name", ""), row.get("account", ""), row.get("model") or now["model"],
                           row.get("effort") or now["effort"], row.get("n", ""))


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
    card's pos, past every other. An unnamed account, model and effort stay
    unset: each is read as the row's pane opens."""
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
    its pane is open, so a launch that never opens takes none. Its line
    reads an unnamed model and effort here too.
    """
    if browser(row):
        if row.get("name") and not own_page(row):
            iterm.name(pane, row["name"], wait=True)
        return
    if not row.get("account"):
        row["account"] = accounts.take()
    panes.settle(pane)
    panes.say(pane, line(row))


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
    lost on the way is typed again, onto a cleared prompt. False means it
    never claimed, and nothing was typed.

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
    while not rec and time.time() < end:
        was = standing()
        hear.until(lambda: bool(claimed()) or standing() != was,
                   files=[p for p, _ in was], seconds=end - time.time())
        rec = claimed()
    if not rec:
        return False
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
        panes.say(pane, f"/rename {rec.get('title')}")
        hear.until(named, files=registry.watched(()), seconds=max(0.0, end - time.time()))
    # The rename is typed, then lands. A second lets it land.
    time.sleep(1)
    message = " ".join(str(row.get("message", "")).split())
    if row.get("drive") is True:
        message = f"/self-drive {message}".strip()
    if message:
        panes.say(pane, message)
    return True
