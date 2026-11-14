#!/usr/bin/env python3
"""system-page.py — System, 1100's page at /system.

Each account's usage and own default, each outsource engine's card, the
account order, the default effort and model, both thresholds, the rail's
size, band 00, the other ports, the app views open right now, and last the
memory guard's findings.

drawn() draws it on the contract, lib/live.py's: it loads once, and only
what moved is put in place. Its own script is .claude/pages/scripts/system.js.
sessions-dashboard.py answers every name another file calls here, and
routes /system.

Imported, never run.
"""

import datetime
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import context  # noqa: E402
import engines  # noqa: E402
import finish  # noqa: E402
import live  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import reader  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = serve.PORT
# Every view: the launch page's pills, the handover page's thresholds.
views = page.tool("dashboard-views")

# Band 00 is the project's own, as .claude/project.json names it: one
# group per layer, port by port.
BAND = project.BAND
PORTS = [p for _, group in BAND for p, _ in group]

# Shown first in band 00, never started with it. A database that listens
# can still refuse every query, so its dot asks the database itself. A
# project naming none shows no dot.
DATABASE = ("Database", [(ports.POSTGRES, project.DATABASE["name"])]) if project.DATABASE else None


# ---- the system -----------------------------------------------------------------

def band_state() -> dict:
    # Serial checks at a quarter second each would make the page crawl.
    # They are independent, so they run at once.
    if not PORTS:
        return {}
    with ThreadPoolExecutor(max_workers=len(PORTS)) as pool:
        return dict(zip(PORTS, pool.map(ports.answering, PORTS)))


def processes(pids) -> dict:
    """Each running pid's process name, in one ps call."""
    wanted = sorted({str(p) for p in pids if p > 0})
    if not wanted:
        return {}
    r = subprocess.run(["/bin/ps", "-o", "pid=,ucomm=", "-p", ",".join(wanted)],
                       capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        pid, _, name = line.strip().partition(" ")
        if pid.isdigit():
            out[int(pid)] = name.strip()
    return out


def outside() -> tuple:
    """What System shows of the world outside: band 00's state, the
    database first, and every port listening outside band 00 and 1100, as
    (port, process)."""
    found = {p: pid for p, pid in ports.listeners().items()
             if p not in PORTS and p not in (PORT, ports.POSTGRES)}
    names = processes(found.values())
    return ({**band_state(), **({ports.POSTGRES: ports.database()} if DATABASE else {})},
            [(p, names.get(found[p], "?")) for p in sorted(found)])


def seen() -> tuple:
    """outside(), read now, as the app door asks it."""
    return outside()


def other(titles: dict, listening: list) -> list:
    """Each other port listening, as (port, process, session).

    The session is the one the port scheme names: its name while it is
    registered, "no session NN" once it is not. A port outside the scheme
    names none.
    """
    out = []
    for p, proc in listening:
        nn = f"{p % 100:02d}"
        out.append((p, proc, (titles.get(nn) or f"no session {nn}") if ports.in_scheme(p) else ""))
    return out


SYSTEM_STYLE = "<style>\n" + page.shared("system.css") + "</style>\n"


def order_part(d: dict) -> str:
    """The order launched sessions take accounts in, the next turn outlined,
    and a box to set a new one."""
    order, at = d["order"], d["next"]
    nxt = ' class="turn next" title="The next launch takes it"'
    turns = ("".join(f'<span{nxt if i == at else " class=turn"}>{page.esc(a)}</span>' for i, a in enumerate(order))
             if order else f'<span class="dim">None set. Every launch takes account {accounts.FALLBACK}.</span>')
    return (f'<div class="lbl">Default account order</div><div class="order">{turns}</div>'
            f'<form class="set" id="set"><input id="order" value="{page.esc(" ".join(order))}" spellcheck="false"'
            ' autocomplete="off" placeholder="1" aria-label="A new account order">'
            '<button class="btn go">Save</button></form>'
            '<p class="hint">A session launched with no account named takes the outlined one, and the next '
            'launch the one after. The order repeats. A named account always wins, and takes no turn.</p>')


def clock(epoch: int) -> str:
    """An instant on this Mac's clock: 14:20 today, Mon 18:00 on another day."""
    t = time.localtime(epoch)
    return time.strftime("%H:%M" if t[:3] == time.localtime()[:3] else "%a %H:%M", t)


def resets(reset: int) -> str:
    """A window's reset, as its epoch alone: system.js says it on the
    clock, resets 14:20, or reset Mon 18:00 once it passed."""
    return f'<span data-reset="{reset}"></span>'


def at(epoch: int, before: str = "") -> str:
    """An instant, as its epoch alone, `before` it: system.js says both, as
    one run of words."""
    return f'<span data-at="{epoch}" data-before="{before}"></span>'


# Each account's plan, as I hold it.
PLANS = {a: accounts.ACCOUNTS[a]["plan"] for a in accounts.KNOWN}

# A window as the status line names it.
WINDOWS = {"five": "five_hour", "week": "seven_day"}


def usage(held: dict, zeroed: bool = True) -> dict:
    """Each account's two windows now, the sessions running on it, and when
    its numbers were last read: {"3": {"five": (36.0, 1791570000), "week":
    (17.0, 1791990000), "on": ["12", "20"], "read": 1791566640}}. A window
    whose reset has passed reads 0, beside the reset it passed: with
    `zeroed` false, only one with no reset, and the page says the rest. Read
    is the kept file's time, to the minute, and 0 when none was ever kept.
    The shared usage reader answers first, when this Mac has one."""
    live = registry.claude_records()
    now = time.time()
    out = {}
    for a in accounts.KNOWN:
        on = [nn for nn, r in held.items() if r.get("account") == a and registry.pid_of(r, live)]
        mine = accounts.shared_account(a)
        if mine:
            out[a] = {"read": int(mine.get("read") or 0), "on": on, "shared": True,
                      **{k: (float((mine.get(k) or {}).get("pct") or 0), int((mine.get(k) or {}).get("reset") or 0))
                         for k in WINDOWS}}
            continue
        got = finish.limits(a)
        try:
            read = int(os.path.getmtime(os.path.join(finish.STATE, f"limits-{a}.json")))
        except OSError:
            read = 0
        out[a] = {"read": read, "on": on}
        for k, name in WINDOWS.items():
            w = got.get(name) if isinstance(got.get(name), dict) else {}
            reset = int(w.get("resets_at") or 0)
            out[a][k] = (float(w.get("used_percentage") or 0) if reset > (now if zeroed else 0) else 0.0, reset)
    return out


def own_part(a: str, mine: dict) -> str:
    """Account A's own default, at the foot of its card: the model a session
    I start myself on it takes, in the launch page's pills, then the effort
    kept for that model, one click to set each. With no model saved, Claude
    Code picks, and no effort can be kept yet."""
    if not mine["saved"]:
        said = '<div class="dim">None saved. Claude Code picks its own.</div>'
    elif mine["model"] not in [v for v, _, _ in views.launcher.offered()]:
        said = f'<div class="dim">Saved: {page.esc(models.name(mine["model"]))}</div>'
    else:
        said = ""
    off = ' disabled title="Pick a model first: Claude Code keeps an effort per model"'
    kept = [e for e in views.launcher.EFFORTS if e[0] in accounts.SAVED]
    efforts = (views.launcher.pills("effort", kept, mine["effort"], "" if mine["model"] else off)
               + views.launcher.pills("effort", [e for e in views.launcher.EFFORTS if e not in kept], "",
                                      ' disabled title="Claude Code keeps max for one session only"'))
    return (f'<div class="own" data-a="{a}"><div class="lbl">Started by hand</div>'
            f'<div class="order">{model_pills(mine["model"])}</div>{said}<div class="order">{efforts}</div></div>')


def epoch(iso) -> int:
    """An ISO instant Claude Code keeps, as an epoch, or 0."""
    try:
        return int(datetime.datetime.fromisoformat(str(iso)).timestamp())
    except (ValueError, OverflowError):
        return 0


def facts(a: str) -> dict:
    """What Claude Code last fetched about account A, from its .claude.json:
    its Fable week, its held reset, its extra usage, where its week went,
    its plan tier and when it fetched them. {} when it holds none. Its
    email and ids are never read out."""
    got = accounts.login(a)
    snap = got.get("cachedUsageUtilization") or {}
    u = snap.get("utilization") if isinstance(snap.get("utilization"), dict) else {}
    if not u:
        return {}
    fable = next((x for x in u.get("limits") or [] if x.get("kind") == "weekly_scoped"
                  and ((x.get("scope") or {}).get("model") or {}).get("display_name") == "Fable"), None)
    held = got.get("unusedLimitResetStatusCache") or {}
    extra = u.get("extra_usage") or {}
    week = (u.get("seven_day_breakdown") or {}).get("rows") or []
    tier = re.search(r"(\d+x)$", str((got.get("oauthAccount") or {}).get("organizationRateLimitTier") or ""))
    level = (fable or {}).get("severity") or ""
    mine = (accounts.shared_account(a) or {}).get("fable")     # the shared reader's Fable window, when it has one
    return {"fable": (float(mine.get("pct") or 0), int(mine.get("reset") or 0), level) if isinstance(mine, dict)
            else (float(fable.get("percent") or 0), epoch(fable.get("resets_at")), level) if fable else None,
            "held": (bool(held.get("holdsUnusedReset")), int((held.get("checkedAt") or 0) / 1000)) if held else None,
            "extra": extra, "week": [(r.get("display_name", ""), r.get("percent") or 0) for r in week],
            "tier": f"Max {tier.group(1)}" if tier else "", "fetched": int((snap.get("fetchedAtMs") or 0) / 1000)}


def money(minor, places) -> str:
    """An amount Claude Code keeps in minor units, as 51.30."""
    return f"{(minor or 0) / 10 ** (places or 0):.{places or 0}f}"


def facts_part(a: str, f: dict) -> str:
    """Account A's facts under its windows: the Fable week as a third bar,
    then one line each for its plan tier, its held reset, its extra usage
    and where its week went, then when Claude Code fetched them."""
    if not f:
        return '<p class="dim seen">Claude Code has fetched nothing more about this account yet.</p>'
    out = ""
    if f["fable"]:
        pct, reset, level = f["fable"]
        word = "Fable week" + (" · critical" if level == "critical" else "")
        tip = f"claude-{a}'s Fable week: {pct:.0f}% used"
        when = f'{resets(reset)}<span data-t="{reset}"></span>' if reset else ""
        out += (f'<div class="win" title="{page.esc(tip)}"><div class="wl"><span>{page.esc(word)} <b>{pct:.0f}%</b>'
                f'</span><span class="dim">{when}</span></div>'
                f'<div class="meter"><i style="width:{min(pct, 100):.0f}%"></i></div></div>')
    lines = []
    if f["tier"]:
        lines.append(page.esc(f"Plan tier: {f['tier']}"))
    if f["held"]:
        holds, checked = f["held"]
        lines.append(("Held reset: one, unused" if holds else "Held reset: none")
                     + (" · " + at(checked, "checked ") if checked else ""))
    e = f["extra"]
    if e:
        cur, places = e.get("currency") or "", e.get("decimal_places") or 0
        why = str(e.get("disabled_reason") or "").replace("_", " ")
        lines.append(page.esc("Extra usage: " + (f"on · {money(e.get('used_credits'), places)} of "
                                                 f"{money(e.get('monthly_limit'), places)} {cur} used"
                                                 if e.get("is_enabled") else "off" + (f" · {why}" if why else ""))))
    went = [f"{name} {pct}%" for name, pct in f["week"] if pct]
    if went:
        lines.append(page.esc("This week went to: " + ", ".join(went)))
    out += "".join(f'<div class="dim seen">{x}</div>' for x in lines)
    if f["fetched"]:
        out += f'<div class="dim seen">{at(f["fetched"], "Fetched by Claude Code ")}<span data-t="{f["fetched"]}"></span></div>'
    return out


def usage_part(use: dict, titles: dict, own: dict) -> str:
    """One card per account: its 5-hour and 7-day windows as bars, each
    with its percent and its reset, then when they were last read, then
    its own default. Its title names its plan. Each session's number opens
    it, as the rail does. A window wears its reset, and system.js reads it
    0 once that passed."""
    def bar(a: str, word: str, w) -> str:
        pct, reset = w
        tip = f"claude-{a}'s {word} window: {pct:.0f}% used"
        passing = f' data-window="{reset}"' if reset else ""
        return (f'<div class="win" title="{page.esc(tip)}"{passing}><div class="wl"><span>{word} <b>{pct:.0f}%</b>'
                '</span><span class="dim">'
                + (f'{resets(reset)}<span data-t="{reset}"></span>'
                   if reset else '') + '</span></div>'
                f'<div class="meter"><i style="width:{min(pct, 100):.0f}%"></i></div></div>')
    cards = []
    for a, u in use.items():
        on = u["on"]
        plan = PLANS.get(a, "")
        running = (("session " if len(on) == 1 else "sessions ") + ", ".join(
            f'<button type="button" class="sn" data-nn="{nn}" title="{page.esc(titles.get(nn, nn))}">{nn}</button>'
            for nn in on) if on else "no session running")
        head = (f'<div class="hd"><span class="lbl">claude-{a}{" · " + plan if plan else ""}</span>'
                f'<span class="dim">{running}</span></div>')
        if not u["read"]:
            inner = '<p class="dim seen">No reading yet. It comes with this account\'s first answer.</p>'
        elif not u.get("shared") and unreadable(os.path.join(finish.STATE, f"limits-{a}.json")):
            inner = (f'<p class="dim seen">This account\'s reading is unreadable: '
                     f'.claude/state/finish/limits-{a}.json</p>')
        else:
            inner = (bar(a, "5-hour", u["five"]) + bar(a, "7-day", u["week"])
                     + f'<div class="dim seen">{at(u["read"], "Last read ")}<span data-t="{u["read"]}"></span></div>')
        cards.append(f'<div class="grp">{head}{inner}{facts_part(a, facts(a))}{own_part(a, own[a])}</div>')
    return (f'<div class="lbl">Usage</div><div class="use">{"".join(cards)}</div>'
            '<p class="hint">Each card\'s pills: a session you start yourself on that account, in any project, '
            'starts there. /model in any of its sessions moves them too. Its effort is the one kept for its '
            'model. Max lasts one session, so it can\'t be saved.</p>')


# An engine's effort pills wear the launch page's shades. Codex's ultra
# goes past max.
SHADES = {v: shade for v, _, shade in views.launcher.EFFORTS} | {"ultra": "#9cfff3"}
MODEL_SHADE = "#4b6bd6"


def engines_seen() -> dict:
    """What the outsource card shows: each engine's settings, models,
    plan and window, and the sessions running it now. A project without
    outsource shows none, and so does a file missing an engine or its
    model."""
    try:
        sets = {e: engines.config()["engines"][e] for e in engines.NAMES}
    except (OSError, ValueError, KeyError, TypeError):
        return {}
    if not all(isinstance(s, dict) and isinstance(s.get("model"), str) for s in sets.values()):
        return {}
    on = engines.running()
    return {e: {"set": sets[e], "models": engines.models(e), "on": on[e],
                "use": engines.codex_use()} for e in engines.NAMES}


def engines_part(seen: dict, titles: dict) -> str:
    """One card per outsource engine, as an account's: its plan and window,
    the sessions running it, then the model and effort every outsource run
    on it takes, one click to set each. No script: system.js sends each
    pill. An outsource file that cannot be read says so."""
    if not seen and unreadable(engines.CONFIG):
        return ('<div class="lbl">Outsource</div><p class="hint">The outsource settings are unreadable: '
                f'{page.esc(os.path.relpath(engines.CONFIG, serve.ROOT))}</p>')
    if not seen:
        return ""
    cards = []
    for e, s in seen.items():
        use, on, mine = s["use"], s["on"], s["set"]
        plan = use.get("plan", "")
        running = (("session " if len(on) == 1 else "sessions ") + ", ".join(
            f'<button type="button" class="sn" data-nn="{nn}" title="{page.esc(titles.get(nn, nn))}">{nn}</button>'
            for nn in on) if on else "no session running")
        head = (f'<div class="hd"><span class="lbl">{engines.NAMES[e]}{" · " + page.esc(plan) if plan else ""}</span>'
                f'<span class="dim">{running}</span></div>')
        if not use:
            inner = f'<p class="dim seen">No reading yet. It comes with {engines.NAMES[e]}\'s first run.</p>'
        else:
            pct, reset = use["pct"], use["reset"]
            inner = (f'<div class="win"><div class="wl"><span>{use["days"]}-day <b>{pct:.0f}%</b></span>'
                     f'<span class="dim">{resets(reset)}'
                     f'<span data-t="{reset}"></span></span></div>'
                     f'<div class="meter"><i style="width:{min(pct, 100):.0f}%"></i></div></div>')
        if use:
            inner += (f'<div class="dim seen">{at(use["read"], "Last read ")}'
                      f'<span data-t="{use["read"]}"></span></div>')
        offered = s["models"]
        names = list(offered) if mine["model"] in offered else [mine["model"], *offered]
        efforts = offered.get(mine["model"], ([mine.get("effort")] if mine.get("effort") else [], ""))[0]
        pills = views.launcher.pills("model", [(m, m, MODEL_SHADE) for m in names], mine["model"])
        pills_e = (views.launcher.pills("effort", [(x, x, SHADES.get(x, MODEL_SHADE)) for x in efforts],
                                        mine.get("effort") or "")
                   if efforts else '<span class="dim">This model takes no effort.</span>')
        cards.append(f'<div class="grp">{head}{inner}<div class="eng" data-e="{e}">'
                     f'<div class="lbl">Every outsource run</div><div class="order">{pills}</div>'
                     f'<div class="order">{pills_e}</div></div></div>')
    return (f'<div class="lbl">Outsource</div><div class="use">{"".join(cards)}</div>'
            '<p class="hint">Each card\'s pills: the model and effort every outsource run on that engine takes. '
            'A brief names its engine alone.</p>')


def effort_part(level: str) -> str:
    """The effort every launch starts at, whatever its account, one click to set it."""
    return (f'<div class="lbl">Default effort</div><div class="order" id="effort">'
            f'{views.launcher.pills("effort", views.launcher.EFFORTS, level)}</div>'
            '<p class="hint">A session launched with no effort named starts at the filled one, '
            'whatever its account. A named effort always wins.</p>')


def model_pills(name: str) -> str:
    """The launch page's model pills, model `name` filled. Each sets its
    family, so a default moves with each new one."""
    offered = views.launcher.offered()
    family = lambda v: models.family(v) or v
    return views.launcher.pills("model", [(family(v), label, shade) for v, label, shade in offered],
                                next((family(v) for v, _, _ in offered if v == name), ""))


def model_part(name: str) -> str:
    """The model every launch starts at, whatever its account, one click to
    set it."""
    return (f'<div class="lbl">Default model</div><div class="order" id="model">{model_pills(name)}</div>'
            '<p class="hint">A session launched with no model named starts at the filled one, '
            'whatever its account. A named model always wins. A new model replaces its family\'s '
            'once Claude Code knows it.</p>')


# The guard's findings, as memory-guard.py writes them: only when one opens,
# changes or closes, never on a clock. 1100 hears the file, so the system
# page draws again only then, and asks nothing on its own. No file is calm.
FINDINGS = os.path.join(serve.ROOT, ".claude", "state", "memory-guard", "findings.json")
# A button runs the guard's own act, on the Python launchd runs it on.
GUARD = ["/usr/bin/python3", os.path.join(HERE, "memory-guard.py")]

# Each level's dot, and the word a screen reader says for it. Stand-in, G3
# v1's.
LEVELS = {"warn": ("gold", "Warning"), "stop": ("red", "Stopped"), "hold": ("gold", "Frozen"),
          "slow": ("blue", "Slow"), "thawed": ("green", "Went on")}

# Rail size: the rail's own zoom, on this device, apart from the page's.
# Its −, + and percent wear a chart's zoom tools; system.js keeps its pick
# as rail-zoom, which home hears change, so the rail grows at once.
RAIL_PART = """<div class="lbl">Rail size</div>
<div class="set"><span class="zt" id="rail"><span class="group">
<button type="button" data-z="-1" title="Shrink the rail" aria-label="Shrink the rail" onmousedown="event.preventDefault()">−</button>
<button type="button" data-z="1" title="Grow the rail" aria-label="Grow the rail" onmousedown="event.preventDefault()">+</button>
</span><span class="pct"></span></span></div>
<p class="hint">The left rail alone, on this device. The zoom buttons under Library zoom the page.</p>
"""


def findings():
    """The guard's open findings, in the order they opened: [] when calm,
    or before it wrote any. None when its file cannot be read."""
    try:
        with open(FINDINGS) as f:
            got = json.load(f)
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None
    found = got.get("findings") if isinstance(got, dict) else None
    return found if isinstance(found, list) else None


def row(f: dict) -> str:
    """One finding: a dot, its one line, its buttons, a Tell's note on
    hover. End's carry its question, shown in their place once End is
    pressed. End wears the shell's red fill, .btn.gone. A memory
    warning's idle sessions follow, one line each."""
    colour, word = LEVELS.get(f["level"], ("grey", f["level"]))
    acts, ask = [], ""
    for b in f["buttons"]:
        verb = b["verb"]
        acts.append(f'<button type="button" class="btn{" go" if verb == "tell" else " gone" if verb == "end" else ""}"'
                    f' data-verb="{page.esc(verb)}"' + (f' title="{page.esc(b["note"])}"' if b.get("note") else "")
                    + f'>{page.esc(b["label"])}</button>')
        if verb == "end":
            again = b["again"]
            ask = (f'<span class="q" hidden>{page.esc(again["question"])}</span><span class="bs" hidden>'
                   f'<button type="button" class="btn gone" data-verb="end" data-sure>{page.esc(again["yes"])}</button>'
                   f'<button type="button" class="btn" data-back>{page.esc(again["no"])}</button></span>')
    return (f'<div class="row" id="f-{page.esc(f["id"])}" data-id="{page.esc(f["id"])}"><span class="t">'
            f'<span class="dot" role="img" aria-label="{page.esc(word)}" style="--c:var(--{colour})"></span>'
            f'{page.esc(f["line"])}</span><span class="bs">{"".join(acts)}</span>{ask}</div>'
            + "".join(f'<div class="idle">{page.esc(s["number"])} · {s["gb"]:.1f} GB · idle {s["idle"]} min</div>'
                      for s in f.get("sessions", [])))


def memory_parts(found) -> tuple:
    """The bars under the head, and the section last on the page. Calm is
    one line, and no bar. A file the guard left unreadable is said, never
    drawn as calm. No script: system.js takes each button."""
    try:
        bars = "".join(f'<button type="button" class="mbar" data-to="f-{page.esc(f["id"])}" style="--c:var(--'
                       f'{LEVELS.get(f["level"], ("grey",))[0]})"><span>{page.esc(f["title"])}</span>'
                       '<span class="dim">Show below</span></button>' for f in found)
        rows = "".join(row(f) for f in found) or '<p class="calm">Nothing is wrong.</p>'
    except (KeyError, TypeError, AttributeError, ValueError):
        bars, rows = "", ('<p class="calm">The guard\'s findings cannot be read: '
                          '.claude/state/memory-guard/findings.json</p>')
    return ((f'<div class="bars">{bars}</div>' if bars else ""),
            f'<div class="lbl">Memory</div><div class="mem" id="mem">{rows}</div>')


def act(fid: str, verb: str, read=None):
    """A finding's button, pressed: the guard acts on that finding's own
    program alone, and its one line, what it did, is the press's answer,
    as a success: serve.Said. It runs off 1100's queue, serve.Typing's, so
    no page waits on it. A finding already closed, a button it never
    offered, or a guard that failed or said nothing is refused. iTerm2
    takes up to a minute to turn its logging off, so that one runs beside,
    and the findings file says how it went. `read` reads the findings,
    findings() unless given."""
    try:
        f = next((f for f in (read or findings)() if f["id"] == fid), None)
        offered = f is not None and any(b["verb"] == verb for b in f["buttons"])
    except (KeyError, TypeError):
        return "The guard's findings cannot be read. Nothing was done."
    if f is None:
        return "This finding is already closed. Nothing was done."
    if not offered:
        return "This finding offers no such button. Nothing was done."
    asked = [*GUARD, "act", fid, verb]
    if verb == "logging-off":
        threading.Thread(target=subprocess.run, args=(asked,), kwargs={"capture_output": True}, daemon=True).start()
        return serve.Said("Asked iTerm2 to turn its logging off. It can take a minute.")

    def guarded() -> str:
        try:
            r = subprocess.run(asked, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            return "The guard did not answer in 20 seconds."
        line = r.stdout.strip().splitlines()[-1:]
        if r.returncode == 0 and line:
            return serve.Said(line[0])
        return (r.stderr.strip().splitlines() or line or ["The guard said nothing."])[-1]
    return serve.Typing(guarded)


def whole() -> str:
    """Each account's usage and own default, then each outsource engine's
    card, lib/engines.py's, then the account order with
    the default effort beside it, the default model, both thresholds side
    by side, the rail's size, then band 00, the database first, then every other port this
    project's scheme could own, every other app's folded into one line, then
    the app views open right now, and last the memory guard's findings. While one is open, its bar sits under
    the head.

    It opens with its watch, carries no script but system.js, reads its
    ports from OUTSIDE, saves nothing, and draws nothing that ticks."""
    held = registry.entries()
    titles = {nn: r.get("title", nn) for nn, r in held.items()}
    state, listening = looked()
    others = other(titles, listening)
    d = accounts.read()
    level = accounts.effort()
    chosen = accounts.model()
    use = usage(held, zeroed=False)
    own = {a: accounts.own(a) for a in accounts.KNOWN}
    eng = engines_seen()
    groups = "".join(
        f'<div class="grp"><div class="lbl">{page.esc(label)}</div>'
        + "".join(f'<a class="port" href="http://localhost:{p}" data-port="{p}" target="_blank" '
                  f'title="{"up" if state[p] else "down"}">'
                  f'<span class="dot" style="--c:var(--{"green" if state[p] else "grey"})"></span><b>{p}</b>'
                  f'<span class="nm">{page.esc(name)}</span>{"" if state[p] else "<span class=dim>down</span>"}</a>'
                  for p, name in group) + '</div>' for label, group in [*([DATABASE] if DATABASE else []), *BAND])
    # This project's ports first: those its port scheme could own. Every
    # other port folds into one line.
    mine = [o for o in others if ports.in_scheme(o[0])]
    rest = [o for o in others if not ports.in_scheme(o[0])]
    rows = lambda found: "".join(
        f'<div class="op"><a class="c" href="http://localhost:{p}" data-port="{p}" target="_blank"><b>{p}</b></a>'
        f'<span class="c dim">{page.esc(proc)}</span>'
        + (f'<span class="c">{page.esc(who)}</span>' if who[:2] in held and who.startswith(who[:2] + "-")
           else f'<span class="c dim">{page.esc(who) or "–"}</span>') + '</div>'
        for p, proc, who in found)
    folded = (f'<details class="rest" id="rest"><summary class="dim">{page.count(len(rest), "more port")}, '
              f'not this project\'s</summary><div class="ops">{rows(rest)}</div></details>' if rest else "")
    up = sum(1 for v in state.values() if v)
    found = findings()
    bars, guard = memory_parts(found)
    rail = page.head("system", "", "", f'<span class="dim">band 00 · {up} of {len(state)} up · '
                                       f'{len(mine)} other</span>')
    # The pickers wear the launch page's pills. System's own sizes come after.
    parts = (page.rules(views.launcher.CSS, ".pills") + SYSTEM_STYLE + bars + usage_part(use, titles, own)
             + engines_part(eng, titles)
             + f'<div class="pair"><div>{order_part(d)}</div><div>{effort_part(level)}</div></div>'
             + model_part(chosen)
             + SCRIPT.sub("", views.handover.system_part()) + RAIL_PART
             + f'<div class="lbl">Band 00</div><div class="band">{groups}</div>'
             f'<div class="lbl">Other ports · {len(mine)}</div><div class="ops">{rows(mine)}</div>{folded}'
             + views_part(opened()) + guard)
    data = json.dumps({"known": "".join(accounts.KNOWN), "zooms": page.ZOOMS}).replace("</", "<\\/")
    body = (live.watch() + parts + f'<script type="application/json" id="system">{data}</script>\n'
            f'<script src="{live.src("system.js")}"></script>\n')
    return page.render("00-system", [("", body)], rail, refresh=0)


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws every part, whole(), and a change lands part by part:
# lib/live.py. Each instant goes as its epoch, and the page's own script,
# .claude/pages/scripts/system.js, says it on this Mac's clock, ticks how far it is,
# and reads a window 0 once its reset passed. It sends each press, and
# keeps the rail's size. Nothing reloads: a save lands, its file is heard,
# and the part it moves is put in place.

# Each script a borrowed part carries: system.js does its work.
SCRIPT = re.compile(r"<script>.*?</script>\n?", re.S)

# outside(), band 00 and the other ports, read on a thread of its own, so
# no draw starts lsof, ps or pg_isready: lib/reader.py's Reader.
# sessions-dashboard.py serve starts each page tool's READERS.
OUTSIDE = reader.Reader(outside)
READERS = [OUTSIDE]


def looked() -> tuple:
    """outside(), as OUTSIDE last read it. With no reader running, as in a
    tool run alone or a made-up folder, nothing is read: every port reads
    down, and no other port shows."""
    if not OUTSIDE.started:
        return {**{p: False for p in PORTS}, **({ports.POSTGRES: False} if DATABASE else {})}, []
    return OUTSIDE.last()


def opened() -> tuple:
    """Each app view open right now and its panels, as lib/show.py's homes()
    counts them, lowest view first: ((1, 1), (2, 2)). No file carries it, so
    it is a look: System draws again as a panel opens or closes."""
    return tuple(sorted((int(view), n) for view, n in show.homes().items()))


def views_part(found: tuple) -> str:
    """The app views open right now, one row each, in the other ports' look.
    A view more than one panel holds reads amber: its chats move each other.
    Each row names its view, so system.js marks the one this page sits in."""
    rows = "".join(
        f'<div class="op" data-view="{view}"><span class="c"><b>View {view}</b></span>'
        + (f'<span class="c dim">1 panel</span>' if n == 1
           else f'<span class="c" style="color:#a8741c">{n} panels</span>') + '</div>'
        for view, n in found) or '<div class="op"><span class="c dim">No app view is open.</span></div>'
    return f'<div class="lbl">App views · {len(found)}</div><div class="ops" id="views">{rows}</div>'


def unreadable(path: str) -> bool:
    """Whether a file is there, and holds no JSON object."""
    try:
        with open(path) as f:
            return not isinstance(json.load(f), dict)
    except FileNotFoundError:
        return False
    except (OSError, ValueError):
        return True


def drawn() -> str:
    """System on the contract: whole()."""
    return whole()


def files() -> list:
    """Every file and folder whose write can move System: each session's
    record and Claude Code's, registry.watched()'s, the account order, effort and model, the thresholds, each
    account's windows and settings, the outsource settings, models and
    readings, the guard's findings, and
    the models offered. What no file carries, the ports, is its look."""
    out = registry.watched(list(registry.entries()))
    out += [accounts.FILE, accounts.EFFORT, accounts.MODEL, context.FILE, finish.STATE,
            *(os.path.join(finish.STATE, f"limits-{a}.json") for a in accounts.KNOWN),
            *(accounts.settings_file(a) for a in accounts.KNOWN),
            *(accounts.login_file(a) for a in accounts.KNOWN), models.FILE]
    out += [engines.CONFIG, os.path.join(engines.CODEX, "models_cache.json")]
    out += glob.glob(os.path.join(engines.SESSIONS, "*", "outsource", "*", "runs", ".lock"))
    codex = sorted(glob.glob(os.path.join(engines.CODEX, "sessions", "*", "*", "*", "*.jsonl")), key=mtime)
    out += codex[::-1][:5]
    return out + [os.path.dirname(FINDINGS), FINDINGS]


def mtime(path: str) -> float:
    """When a file was last written, or 0 once it is gone."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0


# What a press System takes none of answers.
NO_SUCH = "This page takes no such press. Nothing was done."


def pressed(form: dict):
    """A press posted to /system on the contract: a finding's button, act().
    Every setting posts to /, sessions-dashboard.py's take(), as before."""
    if "act" not in form:
        return NO_SUCH
    return act((form.get("finding") or [""])[0], form["act"][0])


# The page's contract, lib/live.py's: its address, its draw, its files, the
# ports no file carries, and its take.
LIVE = live.Page("/system", drawn, files=files, looks=(looked, opened), take=pressed)


