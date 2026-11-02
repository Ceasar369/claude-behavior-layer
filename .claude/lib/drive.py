#!/usr/bin/env python3
"""drive.py — what my assistant drives, kept on disk, and what its page shows of it.

I hand my assistant a session, a stage or my whole plan to drive. What it
drives, and whether that drive runs, is paused or has ended, is one file
in its own folder, drive.json.

    {"drive": "plan", "state": "running", "taken": "2026-10-02T15:41:00",
     "closed": {"A": "2026-10-02T13:53:07", "B": "2026-10-02T16:20:11"}}

`drive` holds the words each take handed it, in order, as its drive line
takes them: plan, a stage's letter, or mission ids. The plan holds every
other, so taking it replaces them. `taken` is when the drive was taken,
or when the plan joined it. `closed` holds each stage closed, with when.
In a plan run in order, a stage already done when the plan was taken is
one I closed, before `taken`. Its time is when its last session stopped,
read once at the take, from each mission's kept transcript. "" when no
kept transcript says.

An open plan's stage closes on my word alone, driven or not. Closed while
nothing drives the plan, the file holds no drive: `drive` and `state`
read "", and `closed` alone counts. A later take keeps it.

A take keeps a paused drive paused, so a successor taking its seat's
drive again never undoes my pause. An ended drive taken again starts
afresh, its closed stages kept.

Each driven session's work is kept before its stop, in the assistant's
reports/<id>/: its folder without its screenshots, and its transcript. Each mission has its own
folder, so a number used again never overwrites one. Each closed stage's
summary is kept in summaries/<letter>.md, the words said in chat.

The team bar carries the plan's two buttons: Drive the whole plan, green
and checked once the plan is driven, then play/pause, pause while the
drive runs, play while it is paused, greyed while nothing is driven. A
press types the line I could type myself. While a drive is on, each stage
row shows its three moments, kick off, work and close: ✓ done, ● now, – later,
and ‖ in place of ● while paused.

Imported, never run.
"""

import json
import os
import shutil
import time

import page
import registry
import transcripts

FILE = "drive.json"
REPORTS = "reports"
SUMMARIES = "summaries"
PLAN = "plan"
STATES = ("running", "paused", "ended")

# What a press of the plan's button types, as I would type it myself. 1100
# types RESUME too, into a driving assistant capped on its own account.
PAUSE = "Pause the drive."
RESUME = "Resume the drive."

# The command that hands an assistant what it drives, before the drive's words.
DRIVE = "/1-assistant drive"

# The registry's own files in a session's folder. They describe the seat,
# never the work, so they stay behind when the work is kept.
SEAT = (registry.RECORD, registry.RESERVED)

# A screenshot stays behind too. The report's words carry what it showed.
SHOTS = (".png", ".jpg", ".jpeg")


# ---- the file -------------------------------------------------------------------

def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), FILE)


def read(nn: str) -> dict:
    """Assistant NN's drive, or {} when it never took one."""
    try:
        with open(path(nn)) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(got, dict) or got.get("state") not in (*STATES, "") or not isinstance(got.get("drive"), str):
        return {}
    return {"drive": " ".join(got["drive"].split()), "state": got["state"], "taken": str(got.get("taken", "")),
            "closed": {str(k): str(v) for k, v in (got.get("closed") or {}).items()}}


def state(nn: str) -> str:
    """running, paused or ended, or "" when assistant NN drives nothing."""
    return read(nn).get("state", "")


def driving(d: dict) -> bool:
    """Whether a drive is on: running, or paused until I resume it."""
    return d.get("state") in ("running", "paused")


def words(d: dict) -> list:
    """What a drive holds: plan, stage letters, mission ids."""
    return d.get("drive", "").split()


def write(nn: str, d: dict) -> dict:
    """The drive, written whole at once, so a reader never sees half."""
    registry.write_whole(path(nn), json.dumps(d, indent=1) + "\n")
    return d


def take(nn: str, keys: list, done=None) -> dict:
    """Assistant NN takes the drive of each key: "plan", a stage's letter,
    or a mission's id. `done` is each stage already done at a take of the
    plan, closed by me before the drive, with when its last session
    stopped. A stage already closed keeps its time."""
    d = read(nn)
    was = words(d) if driving(d) else []
    held = list(was)
    for k in keys:
        if k == PLAN:
            held = [PLAN]
        elif PLAN not in held and k not in held:
            held.append(k)
    fresh = not driving(d) or (PLAN in held and PLAN not in was)
    d = {"drive": " ".join(held), "state": d["state"] if driving(d) else "running",
         "taken": time.strftime(transcripts.STAMP) if fresh else d["taken"],
         "closed": d.get("closed", {})}
    if PLAN in held:
        for at, when in (done or {}).items():
            d["closed"].setdefault(at, when)
    return write(nn, d)


def pause(nn: str) -> dict:
    d = read(nn)
    return write(nn, {**d, "state": "paused"}) if d.get("state") == "running" else d


def resume(nn: str) -> dict:
    d = read(nn)
    return write(nn, {**d, "state": "running"}) if d.get("state") == "paused" else d


def close(nn: str, at: str, said: str) -> str:
    """Stage AT's summary, the words said in chat, kept as summaries/AT.md.
    Then the stage is marked closed, with no drive when none was taken.
    Returns the summary's path."""
    out = summary(nn, at)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(said.strip("\n") + "\n")
    d = read(nn) or {"drive": "", "state": "", "taken": "", "closed": {}}
    d["closed"][at] = time.strftime(transcripts.STAMP)
    write(nn, d)
    return out


def end(nn: str) -> dict:
    return write(nn, {**read(nn), "state": "ended"})


# ---- each mission's work, and each stage's summary ---------------------------------

def report(nn: str, k: str) -> str:
    """Where mission K's work is kept, in assistant NN's folder."""
    return os.path.join(registry.folder(nn), REPORTS, k)


def summary(nn: str, at: str) -> str:
    """Where stage AT's summary is kept, in assistant NN's folder."""
    return os.path.join(registry.folder(nn), SUMMARIES, f"{at}.md")


def stopped(nn: str, k: str, number: str) -> str:
    """When mission K's session NUMBER stopped, written as a bookmark is.

    Its kept transcript, in reports/K/, names the session's own on its
    third line. That one's last record is its stop. "" when either is gone.
    """
    try:
        with open(os.path.join(report(nn, k), f"transcript-{number}.md")) as f:
            head = [f.readline() for _ in range(3)]
    except OSError:
        return ""
    own = head[2].strip().removeprefix("Transcript: ") if head[2].startswith("Transcript: ") else ""
    return max((transcripts.stamp(d) for d in registry.tail(own) if d.get("timestamp")), default="")


def keep(nn: str, k: str, number: str) -> list:
    """Session NUMBER's work, kept for mission K in assistant NN's
    reports/K/: every file of its folder but its screenshots, then its
    transcript, as transcripts.copy writes one. Returns every path kept.

    Kept again, a file replaces the one it kept before, so a mission
    kept twice catches up.
    """
    src, dst = registry.folder(number), report(nn, k)
    kept = []
    for base, _, names in os.walk(src):
        for n in sorted(names):
            if (base == src and n in SEAT) or n.lower().endswith(SHOTS):
                continue
            to = os.path.join(dst, os.path.relpath(os.path.join(base, n), src))
            os.makedirs(os.path.dirname(to), exist_ok=True)
            shutil.copy2(os.path.join(base, n), to)
            kept.append(to)
    out = os.path.join(dst, f"transcript-{number}.md")
    if transcripts.copy(number, out):
        kept.append(out)
    return kept


# ---- what the assistant page shows ---------------------------------------------------

def line(nn: str, act: str) -> str:
    """The line a press of a plan button types into assistant NN.

    Drive the whole plan types /1-assistant drive plan. A command typed into a
    working session waits until its turn ends, while plain words land at
    its next step, so an assistant at work takes "Drive the plan." Pause
    and Resume type their own words, which land either way.
    """
    if act == "pause":
        return PAUSE
    if act == "resume":
        return RESUME
    return handed(nn, PLAN) if act == PLAN else ""


def busy(nn: str) -> bool:
    """Whether assistant NN works now. A command typed into a working
    session waits until its turn ends, while plain words land at its next
    step."""
    mine = registry.entries().get(nn) or {}
    return (registry.claude_records().get(mine.get("session_id")) or {}).get("status") == "busy"


def handed(nn: str, key: str) -> str:
    """The line that hands assistant NN the plan, a stage or a mission:
    /1-assistant drive A2, or "Drive A2." while it works."""
    return f"Drive {'the plan' if key == PLAN else key}." if busy(nn) else f"{DRIVE} {key}"


def controls(nn: str, d: dict) -> str:
    """The plan's two buttons, in the team bar: Drive the whole plan, green
    and checked once the plan is driven, then play/pause, pause while the
    drive runs, play while it is paused, greyed while nothing is driven. A
    press types its line."""
    planned = driving(d) and PLAN in words(d)
    act = {"running": "pause", "paused": "resume"}.get(d.get("state", ""), "")

    def tip(a: str) -> str:
        return page.esc(f'Types "{line(nn, a)}" into your assistant\'s chat')

    return (f'<button class="btn ask{" taken" if planned else ""}" title="{tip(PLAN)}" '
            f'onclick="pressType(this,\'\', true, \'\', \'{PLAN}\')">'
            f'{page.icon("check" if planned else "drive", 11)}Drive the whole plan</button>'
            + (f'<button class="btn ask sq" title="{tip(act)}" onclick="pressType(this,\'\', true, \'\', \'{act}\')">'
               f'{page.icon("play" if act == "resume" else "pause", 11)}</button>' if act
               else f'<button class="btn ask sq" title="Nothing is driven" disabled>{page.icon("pause", 11)}</button>'))


# Each moment's skills, shown on hover.
SKILLS = {
    "kick": "assistant-mission writes its missions · assistant-page.py queue · launch, from its launch page",
    "work": "session-control drives each session · assistant-check checks each finish",
    "close": "session-control keeps each transcript, then stops each session · a short summary in chat",
}


def hour(when) -> str:
    """A time on this Mac's clock, as a row and a finish show it: 14:05 today,
    Mon 18:00 on another day. `when` is a stamp, or epoch seconds."""
    if isinstance(when, str):
        try:
            at = time.strptime(when, transcripts.STAMP)
        except ValueError:
            return ""
    else:
        at = time.localtime(when)
    return time.strftime("%H:%M" if at[:3] == time.localtime()[:3] else "%a %H:%M", at)


def moments(d: dict, at: str, missions: list, done: bool, launch: bool) -> str:
    """Stage AT's three moments, while a drive runs: kick off, work, close.

    Shown whatever the drive holds, a session, a stage or the whole plan,
    as long as one is running or paused.

    A stage is kicked off once one of its sessions claimed, at its first
    queue stamp. Its work is done once every mission stopped: `done`. It is
    closed once the drive closed it, or I did before the drive. `launch`
    marks the row holding Launch page: the first stage not kicked off.
    """
    if not driving(d):
        return ""
    kicked = any(m.get("session") for m in missions)
    kick = min((m["queued"] for m in missions if m.get("queued")), default="") if kicked else ""
    closed = d["closed"].get(at)
    paused = d["state"] == "paused"
    work = (("ok", "✓", "") if done else ("nx", "‖" if paused else "●", "paused" if paused else "")
            if kicked else ("no", "–", ""))

    def mo(cls: str, mark: str, word: str, tip: str, when: str = "") -> str:
        return (f'<span class="mo {cls}" title="{page.esc(tip)}"><b>{mark}</b>{word}'
                + (f'<span class="t">{page.esc(when)}</span>' if when else "") + "</span>")

    arrow = '<span class="ar">→</span>'
    return ('<div class="mom">'
            + mo("ok" if kicked else "no", "✓" if kicked else "–", "Kick off", SKILLS["kick"], hour(kick))
            + (f'<button type="button" class="btn lp" title="The launch page Stage {at} will use" '
               f'onclick="launchPage(\'{at}\')">{page.icon("launch", 11)}Launch page</button>' if launch else "")
            + arrow + mo(*work[:2], "Work", SKILLS["work"], work[2])
            + arrow + mo("ok" if closed is not None else "no", "✓" if closed is not None else "–", "Close",
                         SKILLS["close"], hour(closed or ""))
            + "</div>")


# The whole plan's head, and each stage row's moments. Launch page asks
# 1100's hub to open the assistant's launch page, or opens it in place when
# the page stands alone.
STYLE = """<style>
  #items .phead { display:flex; align-items:center; flex-wrap:wrap; gap:8px 12px; margin:0 0 14px; }
  #items .phead h1.q { margin:0; }
  #items .mom { display:flex; flex-wrap:wrap; align-items:center; gap:4px 10px; margin:0 0 8px; font-size:12px; }
  #items .mom .mo { display:inline-flex; align-items:center; gap:6px; color:var(--text); cursor:help; }
  #items .mom .mo b { width:1.1em; text-align:center; }
  #items .mom .mo.ok b { color:var(--green); }
  #items .mom .mo.nx b { color:var(--blue); }
  #items .mom .mo.no { color:var(--dim); }
  #items .mom .mo.no b { color:var(--grey); }
  #items .mom .t { color:var(--dim); }
  #items .mom .ar { color:var(--grey); }
  #items .mom .btn.lp { height:22px; padding:0 8px; font-size:11px; }
</style>
<script>
function launchPage(at) {
  if (parent === window) location.href = location.pathname.replace('/assistant/', '/launch/');
  else parent.postMessage({ws: 1, open: 'launch', stage: at}, '*');
}
</script>
"""
