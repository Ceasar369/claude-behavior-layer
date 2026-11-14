#!/usr/bin/env python3
"""teams-page.py — an advisor's Teams tab: its plan of teams, drawn from
that advisor's own teams.json, which tools/teams.py keeps.

Any advisor may keep one: my general advisor, or a list advisor. Each tab
reads its own advisor's file alone. A session that is no advisor shows no
Teams tab, whatever its folder holds.

The tab is the locked prototype teams-tab g5/v1, in four sections:

  1 the plan of teams, left to right: a card per team, an arrow from each
    team it waits on. A click on a card opens it in 2.
  2 one team opened: its seat, what it waits on, the shared places it owns,
    and its launch list as a checklist, on the page's own background.
  3 each running team's plan, read only, from its own stages.json. Its
    assistant plans it with me, never this tab.
  4 each team's launch row: its account, model, effort and self-drive, in
    the launch page's pills, then the drive my advisor recommends.

A team runs while a session holds its seat. Its row then takes no press.
A choice left unset shows the launch page's default: the order's next
account, and the model and effort set on System.

A pill press calls teams.py set, as I could myself. The tab never writes
teams.json.

1100 imports this file for tab: the tab shows while an advisor holds
teams.json, last among its tabs, and never waits on me. On the contract, lib/live.py's, it draws
through drawn, files and LIVE, and takes a press through pressed.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import launch  # noqa: E402
import live  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

TEAMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teams.py")
teams = page.tool("teams")
launcher = page.tool("launch-page")
advisor = page.tool("advisor-page")

DRIVES = {"keep": "You keep the team", "plan": "Its assistant drives its whole plan",
          "topic": "It drives on one topic"}


def kept(nn: str) -> bool:
    """Whether session NN is an advisor holding its own plan of teams."""
    return advisor.seat(nn) and os.path.isfile(teams.path(nn))


def world(nn: str) -> dict:
    mine = registry.entries().get(nn) or {}
    plan = teams.load(nn) if kept(nn) else {"teams": [], "shared": []}
    return {"nn": nn, "plan": plan, "held": launch.live(), "session": mine.get("session_id", "")}


def state(t: dict, held: dict) -> str:
    """running while a session holds its seat; ready once its list is
    green; waiting while a line is red; otherwise it waits on nothing."""
    if t["seat"] in held:
        return "running"
    if teams.ready(t):
        return "ready"
    return "waiting" if t.get("launch") else "free"


WORD = {"running": ("running", "green"), "ready": ("every line green", "green"),
        "waiting": ("waiting", "red"), "free": ("waits on nothing", "grey")}


# ---- 1. the plan of teams, left to right ---------------------------------------

COL, ROW, W, H = 300, 120, 230, 86


def placed(ts: list) -> dict:
    """Each seat's column, its longest chain of waits, and its row there."""
    seats = {t["seat"]: t for t in ts}
    depth: dict = {}

    def deep(s: str, seen: tuple = ()) -> int:
        if s in depth:
            return depth[s]
        waits = [w for w in seats[s].get("waits", []) if w in seats and w not in seen]
        depth[s] = 1 + max((deep(w, seen + (s,)) for w in waits), default=-1)
        return depth[s]

    for s in seats:
        deep(s)
    rows: dict = {}
    out = {}
    for t in ts:
        c = depth[t["seat"]]
        out[t["seat"]] = (c, rows.get(c, 0))
        rows[c] = rows.get(c, 0) + 1
    return out


def chart(ts: list, held: dict) -> str:
    e = page.esc
    at = placed(ts)
    cols = max((c for c, _ in at.values()), default=0) + 1
    rows = max((r for _, r in at.values()), default=0) + 1
    width, height = COL * (cols - 1) + W + 2, ROW * (rows - 1) + H + 2
    arrows = ""
    for t in ts:
        for w in t.get("waits", []):
            if w not in at:
                continue
            (c1, r1), (c2, r2) = at[w], at[t["seat"]]
            x1, y1, x2, y2 = c1 * COL + W, r1 * ROW + H / 2, c2 * COL - 2, r2 * ROW + H / 2
            mx = (x1 + x2) / 2
            arrows += (f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}" fill="none" '
                       'stroke="var(--dim)" stroke-width="1.5" marker-end="url(#tip)"/>')
    cards = ""
    for i, t in enumerate(ts):
        c, r = at[t["seat"]]
        word, colour = WORD[state(t, held)]
        left = [ln for ln in t.get("launch", []) if ln["state"] != "out"]
        green = sum(ln["state"] == "green" for ln in left)
        count = f"launch list: {green} of {len(left)} green" if left else "no launch list"
        cards += (f'<button type="button" class="tcard{" on" if i == 0 else ""}" data-seat="{e(t["seat"])}" '
                  f'style="left:{c * COL}px;top:{r * ROW}px;width:{W}px;height:{H}px;--c:var(--{colour})">'
                  f'<span class="ct"><span class="chip">{e(t["seat"])}</span><b>{e(t["name"])}</b></span>'
                  f'<span class="tst">{e(word)}</span><span class="dim">{e(count)}</span></button>')
    return (f'<div class="plan" style="width:{width}px;height:{height}px">'
            f'<svg width="{width}" height="{height}" class="arrows" aria-hidden="true"><defs>'
            '<marker id="tip" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/></marker></defs>'
            f'{arrows}</svg>{cards}</div>')


# ---- 2. one team opened ---------------------------------------------------------

def opened(nn: str, t: dict, owns: list, first: bool) -> str:
    e = page.esc
    waits = ", ".join(f"team {w}" for w in t.get("waits", [])) or "nothing"
    facts = (f'<div class="facts"><div><span class="lbl">seat</span>{e(t["seat"])}</div>'
             f'<div><span class="lbl">waits on</span>{e(waits)}</div>'
             f'<div><span class="lbl">owns</span>{e(", ".join(owns) or "no shared place")}</div></div>')
    lines = t.get("launch", [])
    if lines:
        body = "".join(f'<tr><td class="ob-mark"><span class="mark" style="--c:var(--{dict(green="green", red="red").get(ln["state"], "grey")})">'
                       f'{e(ln["state"])}</span></td><td class="ob-what">{e(ln["line"])}</td>'
                       f'<td class="dim">{e(ln.get("said") or "not yet proven")}</td></tr>' for ln in lines)
        listed = (f'<div class="ob"><div class="ob-block"><h3 class="ob-h">Launch list '
                  f'<span class="ob-path dim">.claude/state/sessions/{nn}/{teams.PLAN}</span></h3>'
                  '<table><thead><tr><th class="ob-mark">State</th><th>Line</th><th>Proof</th></tr></thead>'
                  f'<tbody>{body}</tbody></table></div></div>')
    else:
        listed = f'<div class="note">Team {e(t["seat"])} has no launch list.</div>'
    return (f'<div class="opened{" on" if first else ""}" id="team-{e(t["seat"])}">'
            f'<h2 class="sec">2 · Team {e(t["seat"])}, {e(t["name"])}</h2>{facts}{listed}</div>')


# ---- 3. each running team's plan, read only ---------------------------------------

def plan_of(t: dict, held: dict) -> str:
    e = page.esc
    seat = t["seat"]
    stages = plans.plan(seat).get("stages", [])
    if not stages:
        return f'<div class="note">Team {e(seat)} has no plan yet.</div>'
    out = f'<div class="tplan"><div class="ob-path dim">.claude/state/sessions/{e(seat)}/{plans.PLAN}</div>'
    for s in stages:
        cards, marks = "", []
        for m in s.get("missions", []):
            n = m.get("session", "")
            st = "running" if n and n in held else "done" if n else "not started"
            marks.append(st)
            colour = "green" if st == "running" else "grey"
            chip = f"{n}-{m['id']}" if n else m["id"]
            cards += (f'<div class="card{" done" if st == "done" else ""}" style="--c:var(--{colour})">'
                      f'<div class="hd"><span class="chip{"" if n else " g dashed"}" style="--c:var(--{colour})">'
                      f'{e(chip)}</span><span class="st">{e(st)}</span></div>'
                      f'<div class="nm">{e(m.get("name", ""))}</div></div>')
        mk = ("ok", "✓") if marks and all(x == "done" for x in marks) else ("on", "▸") if "running" in marks else ("", "·")
        out += (f'<div class="stage"><h3 class="sub"><span class="mk {mk[0]}">{mk[1]}</span>'
                f'Team {e(seat)} · {e(s.get("name", ""))}</h3><div class="cards">{cards}</div></div>')
    return out + "</div>"


# ---- 4. each team's launch row, its drive under its pills -------------------------

def pills(seat: str, key: str, options: list, on: str, off: str) -> str:
    return '<span class="pills">' + "".join(
        f'<button type="button" class="{"on" if on == v else ""}" style="--g:{shade}"{off} '
        f'data-seat="{page.esc(seat)}" data-k="{key}" data-v="{page.esc(v)}">{page.esc(label)}</button>'
        for v, label, shade in options) + "</span>"


def row(t: dict, st: str, system: dict, turn: str) -> str:
    e = page.esc
    seat = t["seat"]
    off = " disabled" if st == "running" else ""
    word, colour = WORD[st]
    models_on = [(models.family(m), name, shade) for m, name, shade in launcher.offered()]
    model = t.get("model") or models.family(system["model"])
    drive = ""
    if t.get("drive"):
        drive = (f'<div class="rdrive"><span class="lbl drive">recommended</span>'
                 f'<b>{e(DRIVES.get(t["drive"], t["drive"]))}.</b> <span class="dim">{e(t.get("why", ""))}</span></div>')
    selfie = "on" if t.get("self") == "on" else ""
    return (f'<div class="row{" busy" if off else ""}" style="border-left-color:var(--{colour})">'
            f'<div class="line"><span class="chip" style="--c:var(--{colour})">{e(seat)}</span>'
            f'<b>{e(t["name"])}</b><span class="lands" style="color:var(--{colour})">{e(word)}</span></div>'
            '<div class="line">'
            '<span class="grp"><span class="lbl acct">account</span>'
            + pills(seat, "account", launcher.ACCOUNTS, t.get("account") or turn, off) + '</span>'
            '<span class="grp"><span class="lbl model">model</span>'
            + pills(seat, "model", models_on, model, off) + '</span>'
            '<span class="grp"><span class="lbl effort">effort</span>'
            + pills(seat, "effort", launcher.EFFORTS, t.get("effort") or system["effort"], off) + '</span>'
            '<span class="grp"><span class="lbl drive">drive</span><span class="pills">'
            f'<button type="button" class="{selfie}" style="--g:{launcher.DRIVE}"{off} data-seat="{e(seat)}" '
            f'data-k="self" data-v="{"" if selfie else "on"}">self-drive</button></span></span>'
            f'</div>{drive}</div>')


# ---- the tab ---------------------------------------------------------------------

CSS = ("<style>\n" + page.shared("launch.css") + page.shared("walk-list.css") + page.shared("assistant.css")
       + page.shared("teams.css") + "</style>")


def draw(d: dict, tail: str = "") -> str:
    nn, p, held = d["nn"], d["plan"], d["held"]
    ts = p["teams"]
    if not ts:
        return page.render(f"{nn}-teams", [("", page.blank("No plan of teams yet") + tail)], refresh=0)
    system = launch.default()
    order = accounts.read()
    o = order.get("order") or []
    turn = o[order.get("next", 0) % len(o)] if o else accounts.FALLBACK
    states = {t["seat"]: state(t, held) for t in ts}
    owns = {t["seat"]: [s["place"] for s in p["shared"] if s["owner"] == t["seat"]] for t in ts}
    running = [t for t in ts if states[t["seat"]] == "running"]
    body = ('<div class="tt">'
            '<h2 class="sec">1 · The plan of teams</h2>' + chart(ts, held)
            + "".join(opened(nn, t, owns[t["seat"]], i == 0) for i, t in enumerate(ts))
            + '<h2 class="sec">3 · Each running team\'s plan, read only</h2><div id="items" class="plans">'
            + ("".join(plan_of(t, held) for t in running) or '<div class="note">No team runs yet.</div>')
            + '</div><h2 class="sec">4 · Each team\'s launch row</h2><div id="rows">'
            + "".join(row(t, states[t["seat"]], system, turn) for t in ts) + "</div></div>")
    return page.render(f"{nn}-teams", [("", CSS + body + tail + f'<script src="{live.src("teams.js")}"></script>')],
                       refresh=0)


def tab(nn: str):
    """Session NN's tab, as (its line, its file), or None unless it is an
    advisor holding teams.json."""
    if not kept(nn):
        return None
    n = len(teams.load(nn)["teams"])
    return f"{n} team{'' if n == 1 else 's'}", teams.path(nn)


# ---- the page on the contract --------------------------------------------------

def drawn(nn: str) -> str:
    """Session NN's Teams tab, on the contract."""
    d = world(nn)
    return draw(d, live.watch(d["session"]))


def files(nn: str) -> list:
    """Every file and folder whose write can move session NN's tab: its
    folder, where teams.json comes later, the file itself, each team's
    folder and plan, and every session's record, which says a seat runs."""
    out = [registry.WORK, registry.folder(nn), teams.path(nn)]
    for t in teams.load(nn)["teams"]:
        own = registry.folder(t["seat"])
        out += [own, os.path.join(own, plans.PLAN)]
    for n in registry.entries():
        out.append(os.path.join(registry.folder(n), registry.RECORD))
    return list(dict.fromkeys(out))


def pressed(nn: str, form: dict) -> str:
    """A pill press: one launch choice of one team, through teams.py set,
    as I could type it. A running team's row takes none."""
    get = lambda k: (form.get(k) or [""])[0]
    seat, key, value = get("seat"), get("k"), get("v")
    if get("act") != "set" or key not in teams.CHOICES:
        return "This tab takes no such press. Nothing was set."
    if not kept(nn):
        return f"Session {nn} keeps no plan of teams. Nothing was set."
    t = next((t for t in teams.load(nn)["teams"] if t["seat"] == seat), None)
    if t is None:
        return f"No team sits at {seat} in this plan. Nothing was set."
    if seat in launch.live():
        return f"Team {seat} runs already. Its choices were made at its launch."
    ran = subprocess.run([sys.executable, TEAMS, "set", nn, seat, f"{key}={value}"],
                         capture_output=True, text=True, timeout=20)
    if ran.returncode:
        return (ran.stderr or ran.stdout).strip().splitlines()[-1] if (ran.stderr or ran.stdout).strip() else \
            "teams.py refused it. Nothing was set."
    return ""


# The tab's contract, lib/live.py's: its address, its draw, its files, its take.
LIVE = live.Page(serve.address("teams", r"(\d{2})"), drawn, files=files, take=pressed)
