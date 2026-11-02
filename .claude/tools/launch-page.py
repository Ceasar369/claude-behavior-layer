#!/usr/bin/env python3
"""launch-page.py — the page that starts sessions, drawn by 1100 at /p/launch/NN.

A session asked to start others writes their rows to
.claude/state/sessions/NN/launch.json. 1100 hears the file, and shows the
page in the session's hub, a white dot on its number from its session's turn ending, until the rows are gone. A row is one pane. A session row carries a number, name, first message,
account, model and effort, and whether it self-drives: on, its first
message is handed to /self-drive. A browser row carries a site, and shows it: a
port on this machine, or any address. The session writes what I named, and the page fills the rest.
An account, a model or an effort left unset stays unset in the file, and
is read from 1100/system as its pane opens. The pill of the one it will
read shows picked. I place each row, and press Launch.

A stage I hand my assistant has its page scheduled: one key more in the
file, after, names the stage whose close fires it. Its button then reads
Schedule, and a press launches nothing. I change any row until
tools/schedule.py fires it, as my press would.

A session that gathers sessions for me sets its page alone: one key
more in the file, "alone": true. Its rows then launch as my own page's
do, naming no session as the one that launched them.

My own page is /p/launch/00, and it is always there. No session is behind
it: band 00 is mine, and no session takes it. Its rows live in
sessions/00/, made with its first row and gone with its last. With none,
one blank session row waits, saved once I change it. It takes the lowest
free side number, 01 first, and lands where lib/launch.py places a row
with no starter.

The map is iTerm's real layout, read through lib/iterm.py. A row lands on
one side of a pane, or of a row before it, or fills a new tab or window.
The map is a section like any other, and scrolls with the page. On my
phone held sideways, it fills the first screen, and the picked row's
lands line and arrows sit beside it; in half my phone, they sit under it,
and the map takes the whole width. The rows follow, without arrows of
their own.

The file's order is launch order. The map can arrange existing and new
panes together; existing panes move only after my Launch press. The cards
never move: each keeps its place, pos, from the moment it arrived.

Launch first holds every row's number, so a launch beside it never takes
one, then opens every pane in launch order, through lib/launch.py, as
tools/launch.py does for a skill. Each session gets its first message once
it has claimed its number. A row leaves the file once its pane is live. The file goes once no row is left, so it
never holds up /9-session-stop, and the page leaves its hub.

1100 imports this file, and serves render_for and take_for. A launch runs
inside 1100, so it dies with it: unboot fails what a fresh 1100 finds
still booting. Nothing here runs a server.
"""

import hashlib
import json
import os
import sys
import threading
import traceback

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

FILE = "launch.json"
LOCK = threading.Lock()
MOVES = "moves"
LAYOUTS = "layouts"

# The key that schedules a page: the stage whose close fires it.
AFTER = "after"
# The key that launches a page's rows as my own page's: naming no session.
ALONE = "alone"

# My own page's number, and the row it waits with while it has none. A
# browser row on it is named 00-browser-K: a stand-in, never ruled.
MINE = "00"
BLANK = {"uid": 1, "name": "", "message": ""}

# (value, label, shade). One hue per group. A chosen pill is filled with
# its own shade. One account pill per account on this Mac: lib/accounts.py.
ACCOUNTS = [(a, f"claude-{a}", "#a8741c") for a in accounts.KNOWN]
# Each model family's shade, in the order its pill stands. A family
# Claude Code adds stands after them. Stand-in: its shade.
SHADES = {"opus": "#a66bff", "sonnet": "#9273ee", "fable": "#d65cff", "haiku": "#5a4a8c"}
NEW = "#7b5bd0"
EFFORTS = [("low", "low", "#1d5c55"), ("medium", "medium", "#1f857a"),
           ("high", "high", "#1db3a1"), ("xhigh", "xhigh", "#18d9c3"), ("max", "max", "#35ffe8")]


def offered() -> list:
    """The model pills: each family's newest model, as Claude Code's catalog
    holds it now, lib/models.py's. A new model replaces its family's."""
    rank = lambda fm: list(SHADES).index(fm[0]) if fm[0] in SHADES else len(SHADES)
    return [(m, models.name(m), SHADES.get(f, NEW)) for f, m in sorted(models.families(), key=rank)]


def pills(key: str, options: list, on: str, off: str = "") -> str:
    """One group of these pills, drawn on the server for a page that borrows
    them, as the handover page does: `on` picked, `off` disabling each.
    This page draws its own in its script."""
    return (f'<span class="pills" data-k="{key}">' + "".join(
        f'<button type="button" data-v="{page.esc(v)}" class="{"on" if v == on else ""}" '
        f'style="--g:{shade}"{off}>{page.esc(label)}</button>' for v, label, shade in options) + "</span>")

# The layout each page was drawn from, its starter pane and its open
# browsers, by session: a save places its rows against what I saw.
KEPT: dict = {}

# What a row may carry. Anything else in the file is dropped on save.
KEYS = ("uid", "kind", "n", "name", "message", "account", "model", "effort", "drive", "site",
        "win", "tab", "at", "pos", "status")


# ---- the file ---------------------------------------------------------------

def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), FILE)


def read(nn: str) -> list:
    """Every row, as the file holds it. Reading never writes, so 1100's model reads here."""
    try:
        with open(path(nn)) as f:
            return [r for r in json.load(f).get("rows", []) if isinstance(r, dict)]
    except (OSError, ValueError, AttributeError):
        return []


def moves(nn: str) -> list:
    """The moves waiting for this page's launch."""
    try:
        with open(path(nn)) as f:
            got = json.load(f).get(MOVES, [])
        return got if isinstance(got, list) else []
    except (OSError, ValueError, AttributeError):
        return []


def layouts(nn: str) -> list:
    """The preview's target shapes for the tabs with planned moves."""
    try:
        with open(path(nn)) as f:
            got = json.load(f).get(LAYOUTS, [])
        return got if isinstance(got, list) else []
    except (OSError, ValueError, AttributeError):
        return []


def scheduled(nn: str) -> str:
    """The stage whose close fires this page, or "" when my press launches it."""
    try:
        with open(path(nn)) as f:
            got = json.load(f).get(AFTER, "")
    except (OSError, ValueError, AttributeError):
        return ""
    return got if isinstance(got, str) else ""


def alone(nn: str) -> bool:
    """Whether this page's rows launch naming no session, as my own page's do."""
    try:
        with open(path(nn)) as f:
            return json.load(f).get(ALONE) is True
    except (OSError, ValueError, AttributeError):
        return False


def load(nn: str) -> list:
    """Every row, each with a uid. A row the session just wrote gets one here."""
    rows = read(nn)
    if not rows:
        return []
    top = max([r["uid"] for r in rows if isinstance(r.get("uid"), int)], default=0)
    fresh = False
    for r in rows:
        if not isinstance(r.get("uid"), int):
            top += 1
            r["uid"], fresh = top, True
    if fresh:
        save(nn, rows)
    return rows


def save(nn: str, rows: list, planned=None, shapes=None) -> None:
    """Write the rows. No row left means no file. My own page's folder
    holds nothing else, so it comes with the file and goes with it. A
    scheduled page stays scheduled, and a page alone stays alone."""
    if not rows:
        try:
            os.remove(path(nn))
            if nn == MINE:
                os.rmdir(registry.folder(nn))
        except OSError:
            pass
        return
    if nn == MINE:
        os.makedirs(registry.folder(nn), exist_ok=True)
    after, single = scheduled(nn), alone(nn)
    planned = moves(nn) if planned is None else planned
    shapes = layouts(nn) if shapes is None else shapes
    with open(path(nn), "w") as f:
        json.dump({**({AFTER: after} if after else {}), **({ALONE: True} if single else {}),
                   **({MOVES: planned} if planned else {}),
                   **({LAYOUTS: shapes} if shapes else {}),
                   "rows": [{k: r[k] for k in KEYS if k in r} for r in rows]}, f, indent=2)
        f.write("\n")


def key(nn: str) -> str:
    """What the page reloads on: any change to a row, a session's edit
    included, or a new 1100, which may draw a new page. A page drawn before
    an edit would save its old copy over it. So does what picks what it
    shows: System's model, effort and account order, its pills; whether it
    is scheduled, its button; each number held, a row's free number; and
    each pane open, its map."""
    with LOCK:
        rows = load(nn)
    held = sorted(n for n in registry.listing(registry.WORK) if n.isdigit())
    world = [os.getpid(), rows, moves(nn), layouts(nn), launch.default(), accounts.read(), scheduled(nn), held,
             sorted(panes.ids(panes.FRESH) or [])]
    return hashlib.sha1(json.dumps(world, sort_keys=True, default=str).encode()).hexdigest()[:12]


def unboot(nn: str) -> None:
    """A launch dies with the 1100 that ran it. A row it left booting would
    lock the page, so a fresh 1100 fails it instead."""
    with LOCK:
        rows = load(nn)
        if not any(r.get("status") == "booting" for r in rows):
            return
        for r in rows:
            if r.get("status") == "booting":
                r["status"] = "failed: its launch was cut short. Launch again."
        save(nn, rows)


def launcher(nn: str) -> str:
    """The session this page's rows name as the one that launched them: its
    own, unless its page is alone. My own page names none."""
    return "" if nn == MINE or alone(nn) else nn


def free(nn: str, rows: list):
    """The numbers each of session NN's rows may take, by its name, as its
    launcher's own launch would."""
    taken = [r.get("n") for r in rows if not launch.browser(r)]
    return lambda name: launch.free(taken, by=launcher(nn), name=name)


def placed(nn: str, rows: list, fresh: bool = False) -> None:
    """Fill and settle session NN's rows by lib/launch.py's one rule, against
    the layout its page was drawn from. A launch asks iTerm afresh, and so
    does a save no drawn page answers for, as after a restart."""
    if fresh or nn not in KEPT:
        rec = registry.entries().get(nn) or {}
        wins = iterm.tree()
        KEPT[nn] = (wins, panes.pane(rec) if rec else "", launch.browsers_named(nn, wins))
    wins, starter, opened = KEPT[nn]
    launch.fill(rows, free(nn, rows), launch.home(wins, starter), opened, nn)
    launch.settle(rows, wins, starter)


def saved(nn: str) -> str:
    """The rows as a save left them, for the page to draw."""
    with LOCK:
        return json.dumps(load(nn))


# ---- launching --------------------------------------------------------------

def mark(nn: str, uid: int, status) -> None:
    """Set one row's status, or remove the row once its session is live."""
    with LOCK:
        rows = load(nn)
        if status is None:
            rows = [r for r in rows if r["uid"] != uid]
        else:
            for r in rows:
                if r["uid"] == uid:
                    r["status"] = status
        save(nn, rows)


def follow(nn: str, row: dict, pane: str, by: str) -> None:
    """A session row leaves the file once its session is live. Its record
    names `by`, the page's launcher, as the one that launched it."""
    if launch.arrive(row, pane, by):
        mark(nn, row["uid"], None)
        return
    registry.release(row["n"])
    mark(nn, row["uid"], f"failed: {row['n']} never claimed its number.")


def move_problems(planned: list, rows: list, wins: list) -> list:
    """Refuse moves whose panes or destinations no longer share their tab."""
    tabs = {(f"L:{w['window']}", f"L:{t['tab']}"): set(launch.leaves(t["root"]))
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
    tabs = {(f"L:{w['window']}", f"L:{t['tab']}"): set(launch.leaves(t["root"]))
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
               else set(launch.leaves(tabs[t["tab_id"]])) == set(ids(t["root"]))) for t in spec["tabs"])


def go(nn: str) -> None:
    """Open every booting row's pane, in row order, and start what runs in it.
    The launcher is read first: the file goes with its last row."""
    with LOCK:
        rows = [dict(r) for r in load(nn) if r.get("status") == "booting"]
        by, planned, shapes = launcher(nn), moves(nn), layouts(nn)
    if planned:
        live = iterm.tree()
        if move_problems(planned, rows, live) or shape_problems(planned, shapes, rows, live):
            for r in rows:
                if not launch.browser(r):
                    registry.release(r["n"])
                mark(nn, r["uid"], "failed: arrangement changed before launch.")
            return
    made, windows, waits, opened = {}, {}, [], []
    def start_one(r, pane):
        if launch.browser(r):
            mark(nn, r["uid"], None)
            threading.Thread(target=launch.start, args=(r, pane)).start()
        else:
            launch.start(r, pane)
            t = threading.Thread(target=follow, args=(nn, r, pane, by))
            t.start()
            waits.append(t)
    for r in rows:
        pane = launch.place(r, made, windows)
        if not pane:
            if not launch.browser(r):
                registry.release(r["n"])
            mark(nn, r["uid"], "failed: the pane did not open.")
            continue
        made[str(r["uid"])] = pane
        if planned:
            opened.append((r, pane))
        else:
            start_one(r, pane)
    if not planned:
        for t in waits:
            t.join()
        return
    # No existing pane moves until every new pane is open. A failure closes
    # only these unstarted panes; existing sessions are never closed.
    if planned and len(opened) == len(rows):
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
                if not launch.browser(r):
                    registry.release(r["n"])
                note = (refused[:1].lower() + refused[1:-1] if refused
                        else "arrangement stopped; existing panes may have moved" if safe
                        else "arrangement changed before launch")
                if not closed:
                    note += "; an unstarted pane could not be closed"
                mark(nn, r["uid"], "failed: " + note + ".")
            return
        with LOCK:
            save(nn, load(nn), [], [])
    elif planned:
        # Some pane failed to open. Do not change any existing session.
        for r, pane in opened:
            closed = iterm.close(pane)
            if not launch.browser(r):
                registry.release(r["n"])
            mark(nn, r["uid"], "failed: arrangement was not applied"
                 + ("; an unstarted pane could not be closed" if not closed else "") + ".")
        return
    for r, pane in opened:
        start_one(r, pane)
    for t in waits:
        t.join()


def take_for(nn: str, banner: list):
    def take(form: dict) -> None:
        get = lambda k: (form.get(k) or [""])[0]
        try:
            sent = json.loads(get("rows") or "[]")
            planned = json.loads(get(MOVES)) if get(MOVES) else moves(nn)
            shapes = json.loads(get(LAYOUTS)) if get(LAYOUTS) else layouts(nn)
        except ValueError:
            return
        if not isinstance(planned, list) or not isinstance(shapes, list):
            return
        with LOCK:
            if any(r.get("status") == "booting" for r in load(nn)):
                return
            rows = [{k: r[k] for k in KEYS if k in r} for r in sent if isinstance(r, dict)]
            # A row the session wrote after the page drew is one the page never
            # saw. It is kept, never overwritten.
            seen = set(json.loads(get("seen") or "[]"))
            rows += [r for r in load(nn) if r["uid"] not in seen]
            # A scheduled page launches only when its fire takes the key out.
            launching = get("act") == "launch" and not scheduled(nn)
            # A refused launch's sentence stays until the next launch tries.
            if launching:
                banner[0] = ""
            placed(nn, rows, launching)
            if launching:
                for r in rows:
                    r.pop("status", None)
                wrong = (launch.problems(rows) + move_problems(planned, rows, KEPT[nn][0])
                         + shape_problems(planned, shapes, rows, KEPT[nn][0]))
                # Each number is held before anything opens, so a launch
                # beside this one picks another. One held elsewhere stops all.
                held = []
                if not wrong:
                    for r in rows:
                        if launch.browser(r):
                            continue
                        if not registry.reserve(r["n"]):
                            wrong = [f"{r['n']} is held by another launch."]
                            break
                        held.append(r["n"])
                if wrong:
                    for n in held:
                        registry.release(n)
                    banner[0] = "Nothing launched. " + " ".join(wrong)
                    launching = False
                else:
                    for r in rows:
                        r["status"] = "booting"
            save(nn, rows, planned, shapes)
        if launching:
            threading.Thread(target=go, args=(nn,)).start()
    return take


# ---- the page ---------------------------------------------------------------

CSS = """<style>
  /* The shared shell draws a top rail and a left one. This page keeps only
     the top, in one column that never grows past the glass, so a narrow
     pane wraps the rows instead of cutting them. */
  body:has(> header.top) { grid-template-columns:minmax(0, 1fr); }
  body:has(> header.top) > main, header.top { min-width:0; grid-column:1 / -1; }
  /* The page's tools sit together, one width: the two adds, then Launch. */
  header.top .acts button { white-space:nowrap; }
  header.top .acts button.minor { font-weight:600; background:var(--bg); color:var(--text);
    border:1px solid var(--line); }
  header.top .acts button.minor:hover:enabled { border-color:var(--text); }
  @media (max-width:520px) { header.top .acts button { padding:5px 7px; } }
  /* With no row, the page says so, in one line across the whole screen. */
  body.none .preview, body.none main > h2 { display:none; }
  body.none #rows { height:100%; }
  .banner { background:var(--panel); border:1px solid var(--red); color:var(--red); border-radius:5px;
    padding:6px 9px; margin-bottom:8px; }
  /* The map is a section like any other. It scrolls with the page. */
  .preview { padding-bottom:8px; }
  .mhead { display:flex; align-items:center; gap:10px; margin-bottom:5px; flex-wrap:wrap; }
  .mhead .who { font-weight:700; color:var(--blue); }
  .strip { display:flex; gap:4px; }
  .strip span { font-size:10px; padding:1px 7px; border-radius:3px; color:var(--dim);
    border:1px solid var(--line); text-transform:uppercase; letter-spacing:.06em; }
  .strip span.on { color:var(--text); border-color:var(--blue); }
  /* One tab, drawn to the shape of the real one. Its height is fixed and
     its width follows the tab's own proportions, as iTerm reports them. A
     pane too narrow for it shrinks it whole, its shape kept. */
  .tabmap { display:flex; width:calc(var(--h) * var(--ar)); max-width:100%; aspect-ratio:var(--ar);
    background:var(--line); border:1px solid var(--line); border-radius:4px; overflow:hidden; }
  .split { display:flex; gap:2px; min-width:0; min-height:0; }
  .split.cols { flex-direction:row; } .split.rows { flex-direction:column; }
  .pane { flex:1; min-width:0; min-height:0; overflow:hidden;
    border-left:3px solid var(--c); padding:4px 6px; background:var(--panel); }
  .pane .pl { font-weight:700; font-size:12px; overflow-wrap:anywhere; line-height:1.25; }
  .pane .pm { color:var(--dim); font-size:10px; overflow-wrap:anywhere; }
  .pane.ghost { outline:1px dashed var(--blue); outline-offset:-1px; border-left-color:var(--blue);
    background:color-mix(in srgb, var(--blue) 10%, var(--panel)); cursor:grab; opacity:.7; touch-action:none; }
  .pane.ghost .pl, .pane.ghost .pm { overflow:hidden; text-overflow:clip; white-space:nowrap;
    overflow-wrap:normal; }
  .pane.ghost .pl { font-size:14px; }
  .pane.ghost.active { outline:2px solid var(--blue); outline-offset:-2px; opacity:1;
    background:color-mix(in srgb, var(--blue) 24%, var(--panel)); }
  .pane.live { cursor:grab; touch-action:none; }
  .pane.drop { position:relative; }
  .pane.drop::after { content:''; position:absolute; background:color-mix(in srgb, var(--blue) 40%, transparent);
    border:2px solid var(--blue); box-sizing:border-box; pointer-events:none; }
  .pane.drop.left::after { inset:0 50% 0 0; } .pane.drop.right::after { inset:0 0 0 50%; }
  .pane.drop.up::after { inset:0 0 50% 0; } .pane.drop.down::after { inset:50% 0 0 0; }

  .row { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--blue);
    border-radius:5px; padding:6px 8px; margin-bottom:5px; cursor:pointer; }
  .row.active { box-shadow:0 0 0 2px var(--blue); }
  .row.busy { border-left-color:var(--grey); cursor:default; opacity:.7; }
  .row.failed { border-left-color:var(--red); }
  .line { display:flex; gap:5px 14px; align-items:center; flex-wrap:wrap; margin-bottom:4px; }
  /* A label and its pills wrap as one, never apart. Pills too many for the
     row, as a window's tabs, wrap inside their group, its label first. */
  .grp { display:inline-flex; gap:3px; align-items:center; white-space:nowrap; max-width:100%; }
  .grp > .pills { flex-wrap:wrap; min-width:0; }
  .grp .lbl { margin-right:3px; }
  /* Every control in a row is one height. */
  .row input[type=text], .pills button, .pad button, .x { box-sizing:border-box; height:22px;
    font:inherit; font-size:11px; line-height:1; border-radius:4px; }
  .row input[type=text], .row textarea { padding:0 7px; background:var(--bg); color:var(--text);
    border:1px solid var(--line); }
  .row input:focus, .row textarea:focus { outline:none; border-color:var(--blue); }
  .num { width:3.2em; text-align:center; font-weight:700; }
  .site { width:16em; font-weight:700; }
  .words { width:14em; font-weight:700; }
  .row textarea { display:block; width:100%; height:2.9em; padding:3px 7px; font:inherit;
    font-size:12px; border-radius:4px; resize:vertical; }
  .lbl { color:var(--dim); font-size:10px; text-transform:uppercase; letter-spacing:.06em; }
  .lbl.acct { color:#ff9500; } .lbl.model { color:#d65cff; } .lbl.effort { color:#35ffe8; }
  .lbl.drive { color:#ff6b8b; }
  .lbl.place { color:var(--blue); }
  .lands { flex:1; min-width:0; color:var(--blue); font-size:12px; font-weight:700;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .state { color:var(--red); font-size:12px; font-weight:700; }
  .row.busy .state { color:var(--dim); }
  .pills { display:inline-flex; gap:3px; align-items:center; }
  .pills button { padding:0 8px; cursor:pointer; background:var(--bg); color:var(--g); font-weight:600;
    border:1px solid color-mix(in srgb, var(--g) 45%, var(--line)); }
  .pills button:hover { border-color:var(--g); }
  .pills button.on { background:var(--g); color:#0f1115; border-color:var(--g); font-weight:800; }
  .pills button.new { border-style:dashed; }
  .pills button:disabled, .pad button:disabled { opacity:.3; cursor:not-allowed; }
  .pad { display:inline-flex; gap:3px; }
  .pad button { width:22px; padding:0; cursor:pointer; font-size:12px;
    background:var(--bg); color:var(--blue); border:1px solid var(--blue); font-weight:700; }
  .pad button:hover:enabled { background:var(--blue); color:var(--bg); }
  .x { width:22px; padding:0; cursor:pointer; font-size:14px; background:var(--bg); color:var(--dim);
    border:1px solid var(--line); }
  .x:hover:enabled { color:var(--red); border-color:var(--red); }
</style>"""

# The launch page's own. The handover page borrows CSS, never these.
PHONE = """<style>
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     A box's text is 16px, WebKit's standard size: smaller, a tap into it
     zooms the page. */
  @media (hover:none) and (pointer:coarse) {
    .row input[type=text], .row textarea { font-size:16px; touch-action:manipulation; }
  }
  /* My phone, upright: every box, pill and button takes a fingertip, 44
     by 44 at least, as held sideways, and each line wraps to fit. A row
     keeps its own arrows, 44 pixels each. */
  @media (hover:none) and (pointer:coarse) and (orientation:portrait) {
    header.top .acts button { min-height:44px; }
    .grp, .pills, .pad { gap:4px; }
    .row input[type=text], .pills button, .pad button, .x { height:44px; min-width:44px;
      touch-action:manipulation; }
    .pills button { padding:0 10px; font-size:12px; }
    .pad button { width:44px; font-size:17px; }
    .x { font-size:17px; }
    .words { width:154px; }
    .site { width:176px; }
  }
  /* My phone, held sideways. The map fills the first screen. Beside it sit
     the picked row's lands line and its four arrows, 44 pixels each. The
     rows follow, without arrows of their own. Every box, pill and button
     takes a fingertip: 44 by 44 at least, Apple's least touch size. */
  @media (hover:none) and (pointer:coarse) and (orientation:landscape) {
    header.top .acts button { min-height:44px; }
    .grp, .pills { gap:4px; }
    .row input[type=text], .pills button, .x { height:44px; min-width:44px; touch-action:manipulation; }
    .pills button { padding:0 10px; font-size:12px; }
    .x { font-size:17px; }
    #map { display:flex; flex-wrap:wrap; align-items:flex-start; gap:0 14px; }
    #map > .mhead, #map > .note { flex:0 0 100%; }
    #map > .tabmap { flex:none; max-width:calc(100% - 176px); }
    #map > .side { flex:1 1 162px; min-width:162px; display:flex; flex-direction:column; gap:6px; }
    .side .spot { color:var(--blue); font-size:13px; font-weight:700; line-height:1.35; overflow-wrap:anywhere; }
    .pad.big { display:grid; grid-template-columns:repeat(3, 44px); grid-template-rows:repeat(3, 44px); gap:4px;
      grid-template-areas:". up ." "left . right" ". down ."; margin-top:6px; }
    .pad.big button { width:44px; height:44px; font-size:20px; border-radius:8px; touch-action:manipulation; }
    .pad.big [data-d=up] { grid-area:up; }
    .pad.big [data-d=left] { grid-area:left; }
    .pad.big [data-d=right] { grid-area:right; }
    .pad.big [data-d=down] { grid-area:down; }
    .row .grp.move { display:none; }
  }
  /* Half my phone held sideways: the map takes the whole width, and the
     lands line and the four arrows, in one row, sit under it. */
  @media (hover:none) and (pointer:coarse) and (orientation:landscape) and (max-width:600px) {
    #map > .tabmap { max-width:100%; }
    #map > .side { flex:1 1 100%; flex-direction:row; flex-wrap:wrap; align-items:center; gap:4px 10px;
      margin-top:8px; }
    .pad.big { grid-template-columns:repeat(4, 44px); grid-template-rows:44px; grid-template-areas:"left up down right";
      margin-top:0; }
  }
</style>"""

SCRIPT = r"""<script>
const D = %(data)s;
const LAYOUT = D.layout, STARTER = D.starter;
const ACCOUNTS = D.accounts, MODELS = D.models, EFFORTS = D.efforts;
let ROWS = D.rows;
let PLANNED = D.moves || [];
const SEEN = new Set(ROWS.map(r => r.uid));
const BUSY = ROWS.some(r => r.status === 'booting');
const H = 380;
/* My phone, held sideways: the map fills the first screen, and the picked
   row's lands line and arrows sit beside it. */
const SIDEWAYS = matchMedia('(hover:none) and (pointer:coarse) and (orientation:landscape)');
const PLACE = '#60a5fa', DRIVE = '#ff6b8b';
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
const copy = x => JSON.parse(JSON.stringify(x));

/* ---- the live layout ---------------------------------------------------- */

/* A live window or tab is keyed L:<its iTerm id>. One a row opens is N1, N2… */
const leaves = n => !n ? [] : n.split ? n.children.flatMap(leaves) : [n];
const idOf = n => n.ghost != null ? 'r:' + n.ghost : 'p:' + n.pane;
const liveWin = k => LAYOUT.find(w => 'L:' + w.window === k);
const liveTab = (win, k) => { const w = liveWin(win); return w && w.tabs.find(t => 'L:' + t.tab === k); };

let HOME = LAYOUT.length ? {win: 'L:' + LAYOUT[0].window, tab: 'L:' + LAYOUT[0].tabs[0].tab, pane: ''}
  : {win: 'N1', tab: 'N1', pane: ''};
LAYOUT.forEach(w => w.tabs.forEach(t => leaves(t.root).forEach(p => {
  if (p.pane === STARTER) HOME = {win: 'L:' + w.window, tab: 'L:' + t.tab, pane: p.pane};
})));

/* A node's size, in iTerm's own pixels. A column split adds widths, a row split heights. */
function size(n) {
  if (!n.split) return [n.w, n.h];
  const s = n.children.map(size);
  return n.split === 'columns' ? [s.reduce((a, c) => a + c[0], 0), Math.max(...s.map(c => c[1]))]
    : [Math.max(...s.map(c => c[0])), s.reduce((a, c) => a + c[1], 0)];
}
const FULL = liveTab(HOME.win, HOME.tab) ? size(liveTab(HOME.win, HOME.tab).root) : [1600, 900];

/* ---- rows --------------------------------------------------------------- */

/* The session wrote what I named. 1100 numbers and places every row, by
   lib/launch.py's one rule, each time the rows are saved. An account, a
   model or an effort left unset stays unset until launch. */
const web = r => r.kind === 'browser';
/* ROWS is launch order, which moving a row changes. The cards stand in pos
   order instead, so a card never moves. A new row takes the next pos. */
const shown = () => ROWS.map((r, i) => i).sort((a, b) => ROWS[a].pos - ROWS[b].pos);
const tag = r => web(r) ? 'web ' + (r.site || '?') : r.n;
let active = shown().find(i => ROWS[i].status !== 'booting') ?? 0;

const num = k => Number(k.slice(1));
const news = keys => [...new Set(keys.filter(k => k && k[0] === 'N'))].sort((a, b) => num(a) - num(b));
const next = keys => 'N' + (Math.max(0, ...keys.filter(k => k && k[0] === 'N').map(num)) + 1);

function windows() { return LAYOUT.map(w => 'L:' + w.window).concat(news(ROWS.map(r => r.win))); }
function tabsOf(win) {
  const w = liveWin(win);
  const live = w ? w.tabs.map(t => 'L:' + t.tab) : [];
  return live.concat(news(ROWS.filter(r => r.win === win).map(r => r.tab)));
}
function winLabel(k) {
  const w = liveWin(k);
  return w ? 'window ' + (LAYOUT.indexOf(w) + 1)
    : 'window ' + (LAYOUT.length + news(ROWS.map(r => r.win)).indexOf(k) + 1) + ' · new';
}
function tabLabel(win, k) {
  const w = liveWin(win), t = liveTab(win, k);
  if (t) return 'tab ' + (w.tabs.indexOf(t) + 1);
  return 'tab ' + ((w ? w.tabs.length : 0) + news(ROWS.filter(r => r.win === win).map(r => r.tab)).indexOf(k) + 1) + ' · new';
}

/* ---- where a row lands -------------------------------------------------- */

/* A node refitted to a new box. Its inner split keeps its proportions. */
function fit(n, w, h) {
  if (!n.split) return {...n, w, h};
  const [ow, oh] = size(n), k = n.children.length;
  return {...n, children: n.children.map(c => {
    const [cw, ch] = size(c);
    return n.split === 'columns' ? fit(c, ow ? cw * w / ow : w / k, h) : fit(c, w, oh ? ch * h / oh : h / k);
  })};
}

/* A row lands as iTerm places it. Beside its anchor, inside the anchor's own
   split when that split runs the same way, and then every pane of that split
   takes an equal share. Otherwise the anchor splits in two, halves each. */
function insert(tree, r, i) {
  const ghost = (w, h) => ({ghost: r.uid, idx: i, w, h});
  if (!tree) return ghost(FULL[0], FULL[1]);
  if (!r.at) return tree;
  const across = r.at.side === 'left' || r.at.side === 'right';
  const kind = across ? 'columns' : 'rows';
  const first = r.at.side === 'left' || r.at.side === 'up';
  const walk = n => {
    if (n.split) {
      const hit = n.split === kind ? n.children.findIndex(c => !c.split && idOf(c) === r.at.anchor) : -1;
      if (hit < 0) return {...n, children: n.children.map(walk)};
      const kids = n.children.slice();
      kids.splice(first ? hit : hit + 1, 0, ghost(0, 0));
      const [w, h] = size(n), k = kids.length;
      return {...n, children: kids.map(c => across ? fit(c, w / k, h) : fit(c, w, h / k))};
    }
    if (idOf(n) !== r.at.anchor) return n;
    const half = across ? [n.w / 2, n.h] : [n.w, n.h / 2];
    const a = {...n, w: half[0], h: half[1]}, g = ghost(half[0], half[1]);
    return {split: kind, children: first ? [g, a] : [a, g]};
  };
  return walk(tree);
}

/* The tab as it will stand once every row before `upto` has launched. */
function treeFor(win, tab, upto) {
  const t = liveTab(win, tab);
  let tree = t ? copy(t.root) : null;
  if (BUSY) return tree;
  ROWS.slice(0, upto).forEach((r, i) => { if (r.win === win && r.tab === tab) tree = insert(tree, r, i); });
  if (upto === ROWS.length) PLANNED.filter(m => m.win === win && m.tab === tab).forEach(m => { tree = moved(tree, m); });
  return tree;
}

/* Remove one leaf, closing its empty split and fitting the remaining panes. */
function without(n, id) {
  if (!n) return [null, null];
  if (!n.split) return idOf(n) === id ? [null, n] : [n, null];
  const [w, h] = size(n); let found = null;
  const kids = n.children.map(c => {
    const [rest, hit] = without(c, id);
    if (hit) found = hit;
    return rest;
  }).filter(Boolean);
  if (!found) return [n, null];
  if (!kids.length) return [null, found];
  const flat = kids.flatMap(c => c.split === n.split ? c.children : [c]);
  const rest = flat.length === 1 ? flat[0] : {...n, children:flat};
  return [fit(rest, w, h), found];
}

/* Replay a planned move on the preview; the real move waits for Launch. */
function moved(tree, m) {
  const [rest, leaf] = without(tree, m.source);
  if (!rest || !leaf || !leaves(rest).some(n => idOf(n) === m.anchor)) return tree;
  const marker = '__planned_move__';
  const next = insert(rest, {uid:marker, at:{anchor:m.anchor, side:m.side}}, -1);
  const put = n => n.split ? {...n, children:n.children.map(put)}
    : n.ghost === marker ? fit(leaf, n.w, n.h) : n;
  return put(next);
}

function nameOf(id) {
  if (id[0] === 'r') { const r = ROWS.find(r => 'r:' + r.uid === id); return r ? tag(r) : '?'; }
  const p = LAYOUT.flatMap(w => w.tabs.flatMap(t => leaves(t.root))).find(p => 'p:' + p.pane === id);
  return p ? (p.number || p.label) : '?';
}

const SIDE = {right: 'right of', left: 'left of', down: 'below', up: 'above'};
const OPPOSITE = {right: 'left', left: 'right', down: 'up', up: 'down'};

/* Right of 07 and left of 08 are one place when they are neighbours. Such a
   place reads as between them, the left or upper one first. */
function where(i) {
  const r = ROWS[i];
  const head = winLabel(r.win) + ' · ' + tabLabel(r.win, r.tab) + ' · ';
  if (PLANNED.some(m => m.win === r.win && m.tab === r.tab)) return head + 'as shown in the preview';
  if (!r.at) return head + 'fills the tab';
  const spot = BUSY ? null : spots(i).find(s => s.ways.some(o => o.anchor === r.at.anchor && o.side === r.at.side));
  const pair = spot && spot.ways.find(o => o.side === OPPOSITE[r.at.side] && o.anchor !== r.at.anchor);
  if (!pair) return head + SIDE[r.at.side] + ' ' + nameOf(r.at.anchor);
  const [a, b] = r.at.side === 'right' || r.at.side === 'down' ? [r.at.anchor, pair.anchor] : [pair.anchor, r.at.anchor];
  return head + 'between ' + nameOf(a) + ' and ' + nameOf(b);
}

/* ---- the arrows --------------------------------------------------------- */

function rects(n, x, y, w, h, out) {
  if (!n.split) { out[idOf(n)] = {x, y, w, h}; return out; }
  const axis = n.split === 'columns' ? 0 : 1;
  const total = n.children.reduce((a, c) => a + size(c)[axis], 0);
  let at = axis ? y : x;
  n.children.forEach(c => {
    const part = (axis ? h : w) * size(c)[axis] / total;
    axis ? rects(c, x, at, w, part, out) : rects(c, at, y, part, h, out);
    at += part;
  });
  return out;
}

/* A tab's shape, sizes aside. Two spots giving one shape are one place. */
const shape = n => n.split ? n.split[0] + '(' + n.children.map(shape).join(',') + ')' : idOf(n);

/* Every distinct place a row can land, with every way of saying it. Each one
   sits where the row itself would be drawn, so an arrow measures what I see. */
function spots(i) {
  const r = ROWS[i];
  const tree = treeFor(r.win, r.tab, i);
  if (!tree) return [];
  const places = new Map();
  leaves(tree).map(idOf).forEach(anchor => Object.keys(SIDE).forEach(side => {
    const t = insert(tree, {...r, at: {anchor, side}}, i), key = shape(t);
    if (places.has(key)) { places.get(key).ways.push({anchor, side}); return; }
    const [w, h] = size(t), g = rects(t, 0, 0, w, h, {})['r:' + r.uid];
    places.set(key, {anchor, side, cx: g.x + g.w / 2, cy: g.y + g.h / 2, ways: [{anchor, side}]});
  }));
  return [...places.values()];
}

/* The moving row launches last. A row anchored to it takes its old place. */
function moveLast() {
  const r = ROWS[active];
  if (active !== ROWS.length - 1) {
    const id = 'r:' + r.uid, kids = ROWS.filter(s => s !== r && s.at && s.at.anchor === id);
    if (kids.length) {
      kids.slice(1).forEach(s => { s.at = {anchor: 'r:' + kids[0].uid, side: s.at.side}; });
      kids[0].at = r.at ? {...r.at} : null;
    }
    ROWS.splice(active, 1);
    ROWS.push(r);
    active = ROWS.length - 1;
  }
}

/* An arrow moves the row to the nearest place that way, measured where the
   row would be drawn. Drifting sideways costs four times going straight. */
function move(dir) {
  const r = ROWS[active];
  if (BUSY || !r || !r.at) return;
  if (PLANNED.some(m => m.win === r.win && m.tab === r.tab)) return plannedArrow(dir);
  moveLast();
  const all = spots(active);
  const here = all.find(s => s.ways.some(o => o.anchor === r.at.anchor && o.side === r.at.side));
  if (!here) { changed(); return; }
  const [dx, dy] = {right: [1, 0], left: [-1, 0], down: [0, 1], up: [0, -1]}[dir];
  let best = null, score = Infinity;
  for (const s of all) {
    const along = (s.cx - here.cx) * dx + (s.cy - here.cy) * dy;
    if (s === here || along <= 0.5) continue;
    const sc = along + 4 * (Math.abs((s.cx - here.cx) * dy) + Math.abs((s.cy - here.cy) * dx));
    if (sc < score) { score = sc; best = s; }
  }
  if (best) r.at = {anchor: best.anchor, side: best.side};
  changed();
}

function plannedArrow(dir) {
  const r = ROWS[active], source = 'r:' + r.uid, tree = treeFor(r.win, r.tab, ROWS.length);
  const [w, h] = size(tree), current = rects(tree, 0, 0, w, h, {})[source];
  const [base] = without(tree, source);
  if (!current || !base) return;
  const x = current.x + current.w / 2, y = current.y + current.h / 2;
  const [dx, dy] = {right:[1,0], left:[-1,0], down:[0,1], up:[0,-1]}[dir];
  let best = null, score = Infinity;
  for (const n of leaves(base)) for (const side of Object.keys(SIDE)) {
    const candidate = {win:r.win, tab:r.tab, source, anchor:idOf(n), side};
    const t = moved(tree, candidate), [tw, th] = size(t), p = rects(t, 0, 0, tw, th, {})[source];
    const px = p.x + p.w / 2 - x, py = p.y + p.h / 2 - y;
    const along = px * dx + py * dy;
    const sc = along + 4 * Math.abs(px * dy + py * dx);
    if (along > 0.5 && sc < score) { best = candidate; score = sc; }
  }
  if (best) { PLANNED.push(best); changed(); }
}

/* Drag within this tab. Removing the row first lets every remaining pane
   offer its four sides. A cancelled drag restores the original launch order. */
let drag = null, suppressClick = false;
function capture(e) {
  // The map survives redraws; capture before its touched child is removed.
  try { document.getElementById('map').setPointerCapture(e.pointerId); } catch (err) {}
}
function dragStart(e, i) {
  if (BUSY || e.button !== 0 || drag) return;
  const r = ROWS[i];
  drag = {id:e.pointerId, x:e.clientX, y:e.clientY, i, source:'r:' + r.uid,
    planned:PLANNED.some(m => m.win === r.win && m.tab === r.tab), rows:copy(ROWS), active, moving:false, target:null};
  capture(e);
}
function dragLive(e, source) {
  if (BUSY || e.button !== 0 || drag || !ROWS[active]) return;
  drag = {id:e.pointerId, x:e.clientX, y:e.clientY, source, planned:true,
    rows:copy(ROWS), active, moving:false, target:null};
  capture(e);
}
function dragMove(e) {
  if (!drag || e.pointerId !== drag.id) return;
  if (!drag.moving) {
    if (Math.hypot(e.clientX - drag.x, e.clientY - drag.y) < 6) return;
    drag.moving = true;
    if (drag.i != null) active = drag.i;
    if (!drag.planned) moveLast();
    drawMap();
  }
  e.preventDefault();
  document.querySelectorAll('#map .pane.drop').forEach(el => el.classList.remove('drop', 'left', 'right', 'up', 'down'));
  const el = document.elementFromPoint(e.clientX, e.clientY)?.closest('#map .pane[data-anchor]');
  drag.target = null;
  if (!el) return;
  const box = el.getBoundingClientRect(), x = (e.clientX - box.left) / box.width, y = (e.clientY - box.top) / box.height;
  const side = [['left', x], ['right', 1 - x], ['up', y], ['down', 1 - y]].sort((a, b) => a[1] - b[1])[0][0];
  el.classList.add('drop', side);
  drag.target = {anchor: el.dataset.anchor, side};
}
function dragEnd(e) {
  if (!drag || e.pointerId !== drag.id) return;
  const d = drag;
  drag = null;
  if (!d.moving) {
    if (e.type === 'pointerup' && d.i != null) pick(d.i);
    return;
  }
  suppressClick = true;
  setTimeout(() => { suppressClick = false; }, 0);
  if (e.type === 'pointercancel' || !d.target) {
    ROWS = d.rows; active = d.active; draw(); return;
  }
  if (d.planned) PLANNED.push({win:ROWS[active].win, tab:ROWS[active].tab,
    source:d.source, anchor:d.target.anchor, side:d.target.side});
  else ROWS[active].at = d.target;
  changed();
}
window.addEventListener('pointermove', dragMove, {passive: false});
window.addEventListener('pointerup', dragEnd);
window.addEventListener('pointercancel', dragEnd);
document.getElementById('map').addEventListener('lostpointercapture', e => {
  if (e.target.id === 'map') dragEnd({pointerId:e.pointerId, type:'pointercancel'});
});
// A new primary press also releases a gesture whose end never arrived.
window.addEventListener('pointerdown', e => {
  if (!drag || !e.isPrimary || e.button !== 0) return;
  dragEnd({pointerId:drag.id, type:'pointercancel'});
  e.preventDefault();
  e.stopImmediatePropagation();
}, true);

document.addEventListener('keydown', e => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
  const dir = {ArrowRight: 'right', ArrowLeft: 'left', ArrowDown: 'down', ArrowUp: 'up'}[e.key];
  if (dir) { e.preventDefault(); move(dir); }
});

/* ---- saving ------------------------------------------------------------- */

/* Every change is saved, so a reload keeps it. The page reloads whenever a
   row in its file changes, and never on its own save: page.py's post(). A
   save sends every row, and each row the page has seen. */
let timer = null, seq = 0, dirty = false, writing = Promise.resolve();
function plannedLayouts() {
  const places = new Map(PLANNED.map(m => [m.win + '\n' + m.tab, {win:m.win, tab:m.tab}]));
  const shape = n => !n ? null : n.split ? {split:n.split, children:n.children.map(shape)} : {ref:idOf(n)};
  return [...places.values()].map(p => ({...p, root:shape(treeFor(p.win, p.tab, ROWS.length))}));
}
const form = act => ({act, rows: JSON.stringify(ROWS), moves:JSON.stringify(PLANNED),
  layouts:JSON.stringify(plannedLayouts()), seen: JSON.stringify([...SEEN])});
function pending() {
  dirty = true;
  const watch = document.getElementById('watch');
  if (watch) watch.dataset.busy = '';
}
function save() {
  ++seq; pending(); clearTimeout(timer);
  timer = setTimeout(() => persist(false), 300);
}
/* A change of place saves at once, and the page draws the rows as 1100
   placed them. The picked row stays picked. Only the last change draws. */
async function persist(redraw) {
  const me = seq, uid = ROWS[active] && ROWS[active].uid, sent = form('save');
  clearTimeout(timer);
  writing = writing.catch(() => false).then(() => post(sent));
  const landed = await writing;
  if (me !== seq) { pending(); return false; }
  const error = document.getElementById('save-error');
  if (!landed) { pending(); error.hidden = false; return false; }
  dirty = false; error.hidden = true;
  const watch = document.getElementById('watch');
  if (watch) delete watch.dataset.busy;
  if (!redraw) return true;
  let rows = null;
  try { rows = await (await fetch(location.pathname + '/rows', {cache: 'no-store'})).json(); } catch (e) {}
  if (me !== seq || dirty || !Array.isArray(rows)) return true;
  ROWS = rows;
  ROWS.forEach(r => SEEN.add(r.uid));
  active = Math.max(0, ROWS.findIndex(r => r.uid === uid));
  draw();
  return true;
}
function changed() {
  ++seq; pending(); draw();
  return persist(true);
}

/* A scheduled page launches nothing: its fire does, once its stage closes. */
async function launch() {
  if (BUSY || !ROWS.length || D.after) return;
  clearTimeout(timer);
  if (dirty && !await persist(false)) return;
  if (!await post(form('launch'))) {
    document.getElementById('launch-error').hidden = false;
    document.getElementById('launch').disabled = true;
    return;
  }
  location.reload();
}

/* ---- drawing ------------------------------------------------------------ */

function node(n, grow) {
  if (n.split) {
    const axis = n.split === 'columns' ? 0 : 1;
    return `<div class="split ${axis ? 'rows' : 'cols'}" style="flex:${grow} 1 0">`
      + n.children.map(c => node(c, size(c)[axis])).join('') + '</div>';
  }
  if (n.ghost != null) {
    const r = ROWS[n.idx];
    return `<div class="pane ghost${n.idx === active ? ' active' : ''}" data-anchor="${esc(idOf(n))}" style="flex:${grow} 1 0"
      onpointerdown="dragStart(event, ${n.idx})" onclick="if (!suppressClick) pick(${n.idx})" title="${esc(tag(r))} ${esc(r.name)}"><div class="pl">${esc(tag(r))}</div>
      <div class="pm">${esc(web(r) ? (r.name || 'browser') : r.name)}</div></div>`;
  }
  const me = n.pane === STARTER;
  return `<div class="pane live" data-anchor="${esc(idOf(n))}" onpointerdown="dragLive(event, this.dataset.anchor)" style="flex:${grow} 1 0; --c:var(--${me ? 'green' : n.number ? 'grey' : 'line'})">
    <div class="pl">${esc(n.number)} ${esc(n.label)}</div>
    <div class="pm">${me ? 'starter' : ''}</div></div>`;
}

function drawMap() {
  const r = ROWS[active];
  const el = document.getElementById('map');
  const win = r ? r.win : HOME.win, tab = r ? r.tab : HOME.tab;
  let tree = treeFor(win, tab, drag && drag.moving && !drag.planned ? ROWS.length - 1 : ROWS.length);
  if (tree && drag && drag.moving && drag.planned) tree = without(tree, drag.source)[0];
  if (!tree) { el.innerHTML = drag && drag.moving ? '<div class="note">No other pane in this tab.</div>'
    : '<div class="note">iTerm did not answer. The layout is missing.</div>'; return; }
  const [w, h] = size(tree);
  const sideways = SIDEWAYS.matches;
  const strip = tabsOf(win).map(t => `<span class="${t === tab ? 'on' : ''}">${esc(tabLabel(win, t))}</span>`).join('');
  const who = BUSY ? 'launching · new panes appear as they open'
    : r ? `row ${shown().indexOf(active) + 1} · ${esc(tag(r))} ${esc(web(r) ? (r.name || 'browser') : r.name)}` : 'no row';
  el.innerHTML = `<div class="mhead"><span class="who">${who}</span>
      <span class="lbl">${esc(winLabel(win))}</span><span class="strip">${strip}</span>
      <span class="lbl">${BUSY ? '' : `drag any pane · moves apply on Launch`}</span>
      ${PLANNED.length && !BUSY ? `<button type="button" onclick="undoMove()">Undo move</button>` : ''}</div>
    <div class="tabmap" style="--h:${H}px; --ar:${w / h}">${node(tree, 1)}</div>${sideways ? bigPad(r) : ''}`;
  if (!sideways) return;
  /* The map stands as tall as the first screen has room for, under its head. */
  const main = document.querySelector('main'), map = el.querySelector('.tabmap');
  const top = map.getBoundingClientRect().top - main.getBoundingClientRect().top + main.scrollTop;
  map.style.setProperty('--h', Math.max(160, main.clientHeight - top - 8) + 'px');
}

/* The picked row's lands line and its four arrows, made for a finger. */
function bigPad(r) {
  const still = BUSY || !r || !r.at ? ' disabled' : '';
  return `<div class="side"><span class="lbl place">lands</span>
    <div class="spot">${r && !BUSY ? esc(where(active)) : ''}</div><div class="pad big">`
    + [['up', '↑'], ['left', '←'], ['right', '→'], ['down', '↓']].map(([d, a]) =>
      `<button data-d="${d}"${still} onclick="move('${d}')">${a}</button>`).join('') + '</div></div>';
}

/* A group left unset shows `now` picked: the one 1100/system gives at
   launch. Picking `now` leaves the row unset, so it still reads it then. */
function pills(i, key, options, now, tip) {
  const set = ROWS[i][key];
  return options.map(([v, label, shade]) =>
    `<button class="${(set || now) === v ? 'on' : ''}" style="--g:${shade}"${BUSY ? ' disabled' : ''}${v === now ? ` title="${tip}"` : ''}
      onclick="event.stopPropagation(); ROWS[${i}].${key}='${v === now ? '' : v}'; changed()">${esc(label)}</button>`).join('');
}

/* An account left unnamed takes the order's next turn, set on 1100/system,
   at launch, in launch order. A model or an effort takes the one set there. */
function turn(i) {
  const k = ROWS.slice(0, i).filter(r => !web(r) && !r.account).length, o = D.order.order;
  return o.length ? o[(D.order.next + k) %% o.length] : D.fallback;
}
function accountPills(i) {
  return pills(i, 'account', ACCOUNTS, turn(i), 'The next account in the order set on 1100/system, taken at launch');
}
function systemPills(i, key, options) {
  return pills(i, key, options, D.system[key], `The ${key} set on 1100/system, read at launch`);
}

/* Off unless I turn it on. */
function drivePill(i) {
  return `<button class="${ROWS[i].drive ? 'on' : ''}" style="--g:${DRIVE}"${BUSY ? ' disabled' : ''}
      title="It takes the work to its end, then stops itself"
      onclick="event.stopPropagation(); ROWS[${i}].drive=!ROWS[${i}].drive; changed()">self-drive</button>`;
}

function placePills(i) {
  const r = ROWS[i], off = BUSY ? ' disabled' : '';
  const wins = windows().map(k => `<button class="${r.win === k ? 'on' : ''}" style="--g:${PLACE}"${off}
      onclick="event.stopPropagation(); setWin(${i}, '${k}')">${esc(winLabel(k))}</button>`).join('')
    + `<button class="new" style="--g:${PLACE}"${off} onclick="event.stopPropagation(); setWin(${i}, null)">+ new window</button>`;
  const tabs = tabsOf(r.win).map(k => `<button class="${r.tab === k ? 'on' : ''}" style="--g:${PLACE}"${off}
      onclick="event.stopPropagation(); setTab(${i}, '${k}')">${esc(tabLabel(r.win, k))}</button>`).join('')
    + `<button class="new" style="--g:${PLACE}"${off} onclick="event.stopPropagation(); setTab(${i}, null)">+ new tab</button>`;
  const still = BUSY || i !== active || !r.at ? ' disabled' : '';
  const pad = [['left', '←'], ['up', '↑'], ['down', '↓'], ['right', '→']].map(([d, a]) =>
    `<button${still} onclick="event.stopPropagation(); move('${d}')">${a}</button>`).join('');
  return `<span class="grp"><span class="lbl place">window</span><span class="pills">${wins}</span></span>
    <span class="grp"><span class="lbl place">tab</span><span class="pills">${tabs}</span></span>
    <span class="grp move"><span class="lbl place">move</span><span class="pad">${pad}</span></span>`;
}

function drawRows() {
  const off = BUSY ? ' disabled' : '';
  document.getElementById('rows').innerHTML = ROWS.length ? shown().map(i => {
    const r = ROWS[i];
    const failed = String(r.status || '').startsWith('failed');
    const cls = r.status === 'booting' ? ' busy' : failed ? ' failed' : '';
    const state = r.status === 'booting' ? 'booting…' : failed ? r.status : '';
    const head = `<div class="row${i === active && !BUSY ? ' active' : ''}${cls}" onclick="pick(${i})">`;
    const tail = `<span class="lbl">lands</span><span class="lands">${esc(where(i))}</span>
      <span class="state">${esc(state)}</span>
      <button class="x"${off} title="remove this row" onclick="event.stopPropagation(); drop(${i})">×</button>`;
    if (web(r)) return `
  ${head}
    <div class="line">
      <span class="grp"><span class="lbl place">browser site</span>
      <input class="site" type="text" value="${esc(r.site)}"${off} onclick="event.stopPropagation()"
        placeholder="7204, or any address" oninput="ROWS[${i}].site=this.value; relabel(); save()"></span>
      <input class="words" type="text" value="${esc(r.name)}"${off} onclick="event.stopPropagation()"
        oninput="ROWS[${i}].name=this.value; relabel(); save()">
      ${tail}
    </div>
    <div class="line" style="margin:4px 0 0">${placePills(i)}</div>
  </div>`;
    return `
  ${head}
    <div class="line">
      <input class="num" type="text" value="${esc(r.n)}"${off} onclick="event.stopPropagation()"
        oninput="ROWS[${i}].n=this.value; relabel(); save()">
      <input class="words" type="text" value="${esc(r.name)}"${off} onclick="event.stopPropagation()"
        oninput="ROWS[${i}].name=this.value; relabel(); save()">
      ${tail}
    </div>
    <textarea${off} onclick="event.stopPropagation()" oninput="ROWS[${i}].message=this.value; save()"
      placeholder="The first message it receives.">${esc(r.message)}</textarea>
    <div class="line" style="margin:4px 0 0">
      <span class="grp"><span class="lbl acct">account</span><span class="pills">${accountPills(i)}</span></span>
      <span class="grp"><span class="lbl model">model</span><span class="pills">${systemPills(i, 'model', MODELS)}</span></span>
      <span class="grp"><span class="lbl effort">effort</span><span class="pills">${systemPills(i, 'effort', EFFORTS)}</span></span>
      <span class="grp"><span class="lbl drive">drive</span><span class="pills">${drivePill(i)}</span></span>
    </div>
    <div class="line" style="margin:4px 0 0">${placePills(i)}</div>
  </div>`;
  }).join('') : '<div class="empty"><p>No row waits</p></div>';
  document.body.classList.toggle('none', !ROWS.length);
  const go = document.getElementById('launch');
  // A scheduled page's press launches nothing, so its button never looks pressable.
  go.disabled = BUSY || !ROWS.length || !!D.after;
  const count = (k, word) => k ? `${k} ${word}${k === 1 ? '' : 's'}` : '';
  const sessions = ROWS.filter(r => !web(r)).length, browsers = ROWS.length - sessions;
  go.textContent = BUSY ? 'Launching…' : `${D.after ? 'Schedule' : 'Launch'} · ${ROWS.length}`;
  go.title = D.after ? `Launches once stage ${D.after} closes`
    : [count(sessions, 'session'), count(browsers, 'browser')].filter(Boolean).join(', ');
  document.getElementById('add').disabled = BUSY;
  document.getElementById('addweb').disabled = BUSY;
}

function draw() { drawMap(); drawRows(); }

/* Typing a number or a name redraws the map and every "lands" line, never
   the box being typed in. */
function relabel() {
  drawMap();
  const order = shown();
  document.querySelectorAll('.row .lands').forEach((el, k) => el.textContent = where(order[k]));
}
function pick(i) { if (!BUSY && i !== active) { active = i; draw(); } }
function undoMove() { if (!BUSY && PLANNED.length) { PLANNED.pop(); changed(); } }

function forgetRow(r) {
  const id = 'r:' + r.uid;
  PLANNED = PLANNED.filter(m => m.source !== id && m.anchor !== id);
}

/* A new window opens with its own first tab. A new tab starts empty. */
function setWin(i, k) {
  const r = ROWS[i];
  if (k === r.win) return;
  forgetRow(r);
  active = i;
  if (k === null) { r.win = next(ROWS.map(s => s.win)); r.tab = 'N1'; }
  else if (k !== r.win) { r.win = k; r.tab = tabsOf(k)[0]; }
  r.at = null;
  changed();
}

function setTab(i, k) {
  const r = ROWS[i];
  if (k === r.tab) return;
  forgetRow(r);
  active = i;
  r.tab = k === null ? next(ROWS.filter(s => s.win === r.win).map(s => s.tab)) : k;
  r.at = null;
  changed();
}

function drop(i) {
  forgetRow(ROWS[i]);
  ROWS.splice(i, 1);
  active = Math.max(0, Math.min(active, ROWS.length - 1));
  changed();
}

function add(browser) {
  if (BUSY) return;
  const last = ROWS[ROWS.length - 1];
  const uid = Date.now();
  SEEN.add(uid);
  const place = {win: last ? last.win : HOME.win, tab: last ? last.tab : HOME.tab, at: null};
  ROWS.push(browser ? {uid, kind: 'browser', site: '', ...place} : {uid, name: '', message: '', ...place});
  active = ROWS.length - 1;
  changed();
}

draw();
/* Turning my phone draws the page anew. A screen changing size measures the map again. */
SIDEWAYS.addEventListener('change', draw);
addEventListener('resize', () => { if (SIDEWAYS.matches) drawMap(); });
</script>"""


def layout() -> list:
    """iTerm's windows and split trees, each pane named by its session. A
    draw reads the pane list 1100 keeps: a launch asks iTerm afresh."""
    records = registry.entries()
    held = {at: (k, records.get(k) or {}) for at, k in panes.numbers(panes.FRESH).items()}

    def mark(n):
        if "split" in n:
            for c in n["children"]:
                mark(c)
            return
        number, rec = held.get(n["pane"], ("", {}))
        label = rec.get("title", "") if number else n.get("name", "")
        if number and label.startswith(number + "-"):
            label = label[len(number) + 1:]
        n.update(number=number, label=label.strip())

    wins = iterm.tree()
    for w in wins:
        for t in w["tabs"]:
            mark(t["root"])
    return wins


def render_for(nn: str, banner: list):
    def render():
        """The page. Its key and rows are read on 1100's queue, its key
        first, and iTerm's layout off it, serve.Typing's, so no page waits
        on iTerm."""
        mine = nn == MINE
        rec = registry.entries().get(nn) or {}
        now = key(nn)
        with LOCK:
            rows = load(nn)
        if mine and not rows:
            rows = [dict(BLANK)]
        starter = panes.pane(rec, within=panes.FRESH) if rec else ""
        return serve.Typing(lambda: drawn(nn, banner, rows, starter, now))
    return render


def drawn(nn: str, banner: list, rows: list, starter: str, now: str) -> str:
    """render_for's page, from what it read on the queue, and iTerm's layout."""
    mine = nn == MINE
    wins = layout()
    KEPT[nn] = (wins, starter, launch.browsers_named(nn, wins))
    if not any(r.get("status") == "booting" for r in rows):
        placed(nn, rows)
    data = {"layout": wins, "rows": rows, "moves": moves(nn), "starter": starter, "accounts": ACCOUNTS,
            "order": accounts.read(), "fallback": accounts.FALLBACK,
            "nn": nn, "system": launch.default(),
            "models": offered(), "efforts": EFFORTS, "after": scheduled(nn)}
    body = (CSS + PHONE
            + (f'<div class="banner">{page.esc(banner[0])}</div>' if banner[0] else "")
            + '<div class="banner" id="save-error" hidden>Changes could not be saved. '
              '<button type="button" onclick="persist(true)">Retry save</button></div>'
            + '<div class="banner" id="launch-error" hidden>Launch could not be confirmed. '
              'Check your sessions before trying again.</div>'
            + '<div class="preview"><h2>Where sessions will land</h2><div id="map"></div></div>'
            + '<h2>Rows</h2><div id="rows"></div>'
            + page.watch(now) + page.POST
            + SCRIPT % {"data": json.dumps(data).replace("</", "<\\/")})
    # The top rail holds the family and the session that brought me,
    # then the three buttons together. Nothing else. There is no left rail.
    # My own page has no session to name.
    rail = page.head("launch", "" if mine else plans.tag(nn), "",
                     '<span class="group"><button class="minor" id="add" onclick="add()">+ session</button>'
                     '<button class="minor" id="addweb" onclick="add(true)">+ browser</button>'
                     '<button id="launch" onclick="launch()"></button></span>')
    return page.render("launch" if mine else f"{nn}-launch", [("", body)], rail, refresh=0)
