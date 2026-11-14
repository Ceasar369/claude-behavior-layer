#!/usr/bin/env python3
"""app-door.py — my app chat's door to my sessions.

My app chat is a Claude desktop app chat. The project's desktop extension,
named for it, "<project> sessions", runs this door on my Mac, over a
pipe only the app holds: no tunnel, no port, no key. The door speaks MCP,
the language Claude's connectors speak. It reads my sessions, their clarify waves and explanations, my
agenda, System, my skills, my library, the files git tracks and each
session's own folder. It shows a page on 1100, drafts a reply in a
session's box, unsent, answers a wave item, unsent, and marks a library
item reviewed. It writes and
launches rows on a launch page, ends sessions, and sets System, nothing
else. A session the app chat wants waits as a row on
my own launch page, and it launches only the rows it wrote there. Each press
is one 1100's own page makes. A long list reads in parts, by start and count.

Once my rules change after the chat read them, its next call is refused
until it reads them again. Once the tools change after its tool list, its
next answer says so, once. The switch and the log are lib/door.py's.

  app-door.py stdio          the door as the desktop extension runs it, on its pipe; refused to any other caller
  app-door.py trial [DIR]    the same door on stand-in sessions, its acts kept in DIR, for tools/test-chat.py
  app-door.py extension      the desktop extension, packed for one double-click
  app-door.py keep           1100 kept up, as launchd runs it
  app-door.py install        hand keep to launchd: up at login, back if it dies
  app-door.py open | shut    the door's switch
  app-door.py log [N]        the last N acts, 20 by default

The app chat cannot restart 1100, so keep does: a minute after 1100 stops
answering, it starts it again, as the bare /00-sessions-dashboard would,
without band 00.
"""

import argparse
import contextlib
import hashlib
import http.client
import importlib.util
import json
import mimetypes
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import zipfile
from unittest import mock

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import agenda  # noqa: E402
import context  # noqa: E402
import door  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import transcripts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD = os.path.join(HERE, "sessions-dashboard.py")
REAPER = os.path.join(os.path.dirname(HERE), "hooks", "reaper.py")
# One door per project, each on its own port, so one label per project.
SLUG = re.sub(r"[^a-z0-9]+", "-", project.NAME.lower()).strip("-")
LABEL = "com.behaviour-layer.app-door." + SLUG
PLIST = os.path.expanduser(f"~/Library/LaunchAgents/{LABEL}.plist")
OUT = os.path.join(door.STATE, "door.log")
# launchd's Python: the python3 the shell finds, never its versioned path, so
# an upgrade keeps it. 1100's lib needs 3.10 or newer, which /usr/bin's is not.
BREW = shutil.which("python3")
NN = re.compile(r"\d{2}")


def pressed(path: str, form: dict) -> tuple:
    """A press on 1100, as its own page posts it, 1400's through /proto/.
    (200, the line it answered, often none) once taken, or (409, its
    refusal in one sentence)."""
    # Under the Claude app's 30 seconds, so a slow 1100 is an answer, not a dead call.
    conn = http.client.HTTPConnection("127.0.0.1", serve.PORT, timeout=25)
    # 1100 and 1400 check the Origin a page sends against its Host.
    conn.request("POST", path, urllib.parse.urlencode(form),
                 {"Host": f"127.0.0.1:{serve.PORT}", "Origin": f"http://127.0.0.1:{serve.PORT}",
                  "Content-Type": "application/x-www-form-urlencoded"})
    r = conn.getresponse()
    said = r.read().decode("utf-8", "replace").strip()
    if r.status == 409:
        return 409, said
    # A 303 carries the page it redirects to, never a line of its own.
    return (200, said if r.status == 200 else "") if r.status < 400 else (r.status, said or "1100 refused it.")


def fetched(path: str) -> str:
    """What 1100 answers at `path`, asked for as a browser asks, or "" when
    none came. Short, so the press after it still lands inside the app's 30 seconds."""
    conn = http.client.HTTPConnection("127.0.0.1", serve.PORT, timeout=4)
    conn.request("GET", path, headers={"Host": f"127.0.0.1:{serve.PORT}"})
    r = conn.getresponse()
    said = r.read().decode("utf-8", "replace").strip()
    return said if r.status == 200 else ""


def open_twice(view: str) -> str:
    """"View 2 is already open." once more than one panel holds that view
    right now, as 1100 counts them, or "". 1100 not answering says nothing."""
    try:
        return show.already(view, int(json.loads(fetched("/views") or "{}").get(view, 0)))
    except (OSError, ValueError, AttributeError):
        return ""


# ---- what the app chat reads and does -------------------------------------------------

def home() -> str:
    """Every session, one line each: its number, its name, and whether it
    works or waits on me."""
    lines = []
    for nn, (colour, word, name) in sorted(page.colours().items()):
        state = {"green": "working", "red": "waits on you"}.get(colour, "gone")
        lines.append(f"Session {nn}, {name}: {state}.")
    return "\n".join(lines) or "No session is running."


def last(nn: str, turn: str, start: str, count: str) -> tuple:
    """Session NN. Bare: its state, its move and its last words since my
    turn, as the assistant page reads them, then what its pane shows and
    whether a handover is due. A turn, by the number its page wears, or
    last: that turn whole. Start or count alone: its turns, one line each."""
    path, title = transcripts.find(nn)
    if not path:
        return 409, f"Session {nn} has no transcript."
    tp = page.tool("transcript-page")
    if turn or start or count:
        th = transcripts.thread(path)
        shown = [(t, n) for _, t, n in th.numbered(tp.status(nn) == "idle")]
        if not turn:
            lines = [turn_line(t, n) for t, n in shown]
            return 200, "\n".join([f"Session {nn}'s {page.count(len(lines), 'turn')}, oldest first."]
                                  + paged(lines, start, count, 20))
        want = max((n for _, n in shown), default=0) if turn.lower() == "last" else int(turn) if turn.isdigit() else -1
        got = [turn_text(t, n) for t, n in shown if n == want and want > 0]
        return (200, "\n\n".join(got)) if got else (409, f"Session {nn} has no turn {turn}.")
    said, at, move = transcripts.last_said(path)
    word = tp.state(nn)
    state = {"working": "is working", "idle": "waits on you", "waiting": "waits on you, a dialog open",
             "shell": "waits on you, at its shell", "closed": "has closed its pane"}.get(word, "has ended")
    out = [f"Session {nn}, {title}, {state}."]
    out += [f"Its move: {move}", "", f"Its last words, at {transcripts.clock(at)}:", "", said] if said else [
        "It has said nothing since your last message. Its turns read the rest."]
    return 200, "\n".join(out + paned(nn, tp) + due(nn))


def turn_line(t: dict, n: int) -> str:
    """One turn in a line: its number, who, when, and its first words."""
    first = lambda s: (" ".join(s.split())[:90] + "…") if len(" ".join(s.split())) > 90 else " ".join(s.split())
    if t["who"] == "you":
        who = f"Session {t['from']}'s report" if t.get("from") else "You"
        return ended(f"Turn {n or 'uncounted'}, {who}, {t['at']}: {first(t['text']) or 'a picture'}")
    words = [s["t"] for s in t["steps"] if s["k"] == "text"]
    acts = sum(s["k"] != "text" for s in t["steps"])
    return ended(f"Turn {n or 'uncounted'}, the session, {t['at']}, {page.count(acts, 'step')}: "
                 f"{first(words[-1]) if words else 'no words'}")


def turn_text(t: dict, n: int) -> str:
    """One turn whole, as its page draws it: my words, or the session's
    notes, every skill, file, command, agent and call in order, its reply."""
    if t["who"] == "you":
        who = f"Session {t['from']}'s report" if t.get("from") else "You"
        return "\n".join([f"Turn {n}, {who}, {t['at']}:", t["text"].strip()]
                         + ([f"It answered: {t['out'].strip()}"] if t.get("out") else [])
                         + ([page.count(len(t["pics"]), "picture") + "."] if t.get("pics") else []))
    took = (t["end"] - t["start"]).total_seconds() if t.get("start") and t.get("end") else 0
    out = [f"Turn {n}, the session, {t['at']}" + (f", worked {round(took / 60)} minutes" if took >= 60 else "") + ":"]
    for s in t["steps"]:
        bad = ", failed" if s.get("err") else ""
        if s["k"] == "text":
            out.append(s["t"])
        elif s["k"] == "skill":
            out.append(f"Ran /{s['name']}" + (f" {s['args']}" if s["args"] else "") + ".")
        elif s["k"] == "file":
            out.append(f"{'Wrote' if s['verb'] == 'wrote' else 'Edited'} {s['path']}{bad}.")
        elif s["k"] == "call":
            line = f"{s['tool'].capitalize()}: {s['say']}{bad}."
            if s["tool"] in transcripts.LOUD:
                peek, more = s.get("peek") or ([], 0)
                line += (" Still running." if s.get("out", 0) < 0 or (s.get("bg") and not s.get("done"))
                         else f" It {s['done']}." if s.get("bg") else
                         ("\n" + "\n".join(peek) + (f"\nAnd {more} more lines." if more else "")) if peek else "")
            out.append(line)
        elif s["k"] in ("arrived", "wake"):
            out.append(f"At {s.get('at', '')}, woken: {(s.get('call') or {}).get('say') or s.get('name') or s.get('how', '')}.")
    return "\n".join(out)


def paned(nn: str, tp) -> list:
    """What only the pane shows: a dialog waiting, its words and choices,
    else the reply Claude Code suggests, then its mode and status line."""
    try:
        lines = tp.screen(nn)
    except Exception:
        return []
    out = []
    words, choices, _ = tp.ask(lines)
    if choices:
        out += ["", "A dialog waits: " + " ".join(words)] + [
            f"Choice {c[0]}: {c[1]}" + (f", {c[2]}" if c[2] else "") + "." for c in choices]
    elif hint := tp.hint(lines):
        out += ["", f"Claude Code suggests: {hint}"]
    if mode := tp.mode(lines):
        out.append(f"Its mode: {mode}.")
    try:
        with open(os.path.join(registry.folder(nn), registry.STATUSLINE)) as f:
            meter = " ".join(transcripts.ANSI.sub("", x).strip() for x in f.read().splitlines() if x.strip())
        out += [f"Its status line: {meter}"] if meter else []
    except OSError:
        pass
    return out


def due(nn: str) -> list:
    """Whether its handover is due, or how far a pressed one got."""
    held, running = registry.entries(), registry.claude_records()
    if nn not in held:
        return []
    got = page.tool("handover-page").waiting(nn, held[nn], running, context.threshold())
    return [f"A handover waits: {got[0]}."] if got else []


# ---- a launch page, launch-page.py's ----------------------------------------------------
# A session the app chat wants waits as a row on my own page, for me to
# fine-tune. Each row it writes carries by: app, so its Launch there
# launches only those, and every other row waits for my own press.

MINE = "00"
APP = "app"
# One write at a time: two at once would give two rows the same uid.
WRITING = threading.Lock()


def launch_rows(nn: str) -> tuple:
    """Session NN's launch page, 00 being my own: each row as written, and
    whether a stage's close launches it instead of my press."""
    lp = page.tool("launch-page")
    rows = lp.load(nn)
    if not rows:
        return 409, f"Session {nn}'s launch page holds no row."
    out = [f"Session {nn}'s launch page, {page.count(len(rows), 'row')}."
           + (f" Stage {after}'s close launches it." if (after := lp.scheduled(nn)) else "")]
    for i, r in enumerate(rows, 1):
        what = f"a browser on {r.get('site', '')}" if r.get("kind") == "browser" else (
            f"session {r.get('n', '')}, {r.get('name', '')}")
        pills = ", ".join(x for x in (r.get("account") and f"account {r['account']}", r.get("model"),
                                      r.get("effort"), r.get("drive") and "self-drive",
                                      r.get("by") == APP and "the app chat wrote it") if x)
        out.append(f"Row {i}: {what}" + (f", {pills}" if pills else "") + (f". {r['status']}" if r.get("status") else "")
                   + "." + (f" First message: {r['message']}" if r.get("message") else ""))
    return 200, "\n".join(out)


def launched_rows(nn: str) -> tuple:
    """Launch, pressed on session NN's launch page: its rows as written. On
    my own, only the rows the app chat wrote. The page is drawn first, so
    1100 holds the layout it places them on."""
    lp = page.tool("launch-page")
    rows = lp.load(nn)
    if not rows:
        return 409, f"Session {nn}'s launch page holds no row. Nothing launched."
    only = [r["uid"] for r in rows if r.get("by") == APP] if nn == MINE else None
    if only == []:
        return 409, ("No row on your launch page is one the app chat wrote. Yours wait for your own press. "
                     "Nothing launched.")
    address = serve.address("launch", nn)
    try:
        fetched(address)
    except OSError:
        pass
    status, said = pressed(address, {"act": "launch", "rows": json.dumps(rows),
                                     "seen": json.dumps([r["uid"] for r in rows]),
                                     **({"only": json.dumps(only)} if only else {})})
    if status != 200 or said:
        return 409, said or "1100 refused it."
    if only:
        return 200, (f"Launching the {page.count(len(only), 'row')} the app chat wrote on your launch page."
                     + (" Your other rows stay as they are." if len(only) < len(rows) else ""))
    return 200, (f"Stage {lp.scheduled(nn)}'s close launches session {nn}'s page. Its rows are saved."
                 if lp.scheduled(nn) else f"Launching session {nn}'s page: {page.count(len(rows), 'row')}.")


# A seat number a name was written with, "09 cache" or "session 09 - cache".
# The page shows the number left of the name, so the name never holds it.
SEATED = re.compile(r"(?i)\s*(?:session\s*)?(\d{2})\b[\s:.,_-]*")


def spoken_model(said: str) -> str:
    """A model as I say it, opus, Opus 5.5 or claude-opus-5-5, as the page's
    pill holds it: a family is its newest model."""
    v = re.sub(r"[\s.]+", "-", said.strip().lower())
    if v == "system":
        return v
    latest = dict(models.families())
    known = {m["id"] for m in models.catalog()["models"]}
    return latest.get(v) or next((m for m in (v, f"claude-{v}") if m in known), said)


# A side as I say it, as lib/launch.py's `at` holds it.
SIDES = {"below": "down", "under": "down", "down": "down", "above": "up", "over": "up", "up": "up",
         "left": "left", "right": "right"}
NEW = ("new tab", "new window")


def placed(rows: list, target: dict, near: str, side: str) -> str:
    """Place target as a drag on the map does: beside session NN's pane, or
    a row before it, on one side, or in a new tab or window. Empty once
    placed; else why not, and target stays as it was."""
    side = re.sub(r"\s+", " ", side.strip().lower()) or "below"
    if side not in SIDES and side not in NEW:
        return f"A side is below, above, left, right, new tab or new window, never {side}."
    if side == "new window":
        k = max([int(r["win"][1:]) for r in rows if re.fullmatch(r"N\d+", str(r.get("win") or ""))], default=0)
        target.update(win=f"N{k + 1}", tab="N1", at=None)
        return ""
    tree, near = iterm.tree(), near.strip().lower()
    if not tree:
        return "iTerm did not answer, so nothing was placed."
    if seat := re.fullmatch(r"(?:session\s*)?(\d{1,2})", near):
        nn = f"{int(seat.group(1)):02d}"
        pane = panes.pane_of(nn)
        win, tab = next(((f"L:{w['window']}", f"L:{t['tab']}") for w in tree for t in w["tabs"]
                         if pane and pane in launch.leaves(t["root"])), ("", ""))
        if not win:
            return f"Session {nn} has no pane open, so nothing was placed."
        anchor = f"p:{pane}"
    elif got := re.fullmatch(r"row\s*(\d+)", near):
        k = int(got.group(1)) - 1
        if not 0 <= k < len(rows) or rows[k] is target or rows.index(target) < k:
            return f"A row sits only beside a row above it on the page, never row {k + 1}."
        win, tab, anchor = rows[k].get("win"), rows[k].get("tab"), f"r:{rows[k]['uid']}"
    elif side == "new tab" and not near:
        win, tab, anchor = f"L:{tree[0]['window']}", "", ""
    else:
        return "Name what it sits beside: a session, like 04, or a row, like row 2."
    if side == "new tab":
        k = max([int(r["tab"][1:]) for r in rows if r.get("win") == win
                 and re.fullmatch(r"N\d+", str(r.get("tab") or ""))], default=0)
        target.update(win=win, tab=f"N{k + 1}", at=None)
    else:
        target.update(win=win, tab=tab, at={"anchor": anchor, "side": SIDES[side]})
    return ""


def written(row: str, name: str, message: str, n: str, account: str, model: str, effort: str,
            drive: str, remove: str, near: str = "", side: str = "", clone: str = "") -> tuple:
    """One row the app chat writes on my own launch page, saved as the page
    saves, and bordered there, moving no page. It holds its name and first message, and
    only what I named; system sets a pill back to System's. With row, a row
    the app chat wrote changes, or goes. It never launches. A number written into the
    name leaves it, for the number field when that is empty. Near and side
    place it: placed(). Clone names the session it starts forked from."""
    on = lambda v: v.lower() in ("true", "yes")
    if seat := SEATED.match(name):
        name, n = name[seat.end():].strip(), n or seat.group(1)
    account = re.sub(r"(?i)^account\s*", "", account)
    model, effort = model and spoken_model(model), effort.lower()
    if n and not NN.fullmatch(n):
        return 409, "A number is two digits, like 02. Nothing was written."
    clone = f"{int(clone):02d}" if clone.strip().isdigit() else clone.strip()
    if clone and not launch.cloned(clone):
        return 409, launch.refuse_clone(clone)
    with WRITING:
        rows = page.tool("launch-page").load(MINE)
        seen = [r["uid"] for r in rows]
        if row:
            i = int(row) - 1 if row.isdigit() else -1
            if not 0 <= i < len(rows):
                return 409, f"Your launch page has no row {row}. Nothing was written."
            if rows[i].get("by") != APP:
                return 409, f"Row {row} is yours, not the app chat's. It stays as it is."
            target, done = rows[i], f"Row {row} on your launch page changed."
        else:
            if not message:
                return 409, "No words to open the session with. Nothing was written."
            target = {"uid": max(seen, default=0) + 1, "by": APP}
            rows.append(target)
            done = f"Row {len(rows)} on your launch page holds {name or 'a new session'}."
        gone = bool(row) and on(remove)
        if gone:
            rows.pop(i)
            done = f"Row {row} is gone from your launch page."
        else:
            for k, v in (("name", name), ("message", message), ("n", n), ("account", account),
                         ("model", model), ("effort", effort), ("clone", clone)):
                if v == "system" and k in ("account", "model", "effort"):
                    target[k] = page.tool("launch-page").system(target, k)
                elif v:
                    target[k] = v
            if drive:
                target["drive"] = on(drive)
            if not launch.line({**target, "account": target.get("account") or accounts.FALLBACK, "n": "01"}):
                return 409, "That account, model or effort is refused. Nothing was written."
            if (near or side) and (why := placed(rows, target, near, side)):
                return 409, why + " Nothing was written."
            if near or side:
                s, by = side.strip().lower(), near.strip()
                by = f"session {int(by):02d}" if by.isdigit() else by
                done += f" It lands in a {s}." if s in NEW else f" It lands {s or 'below'} {by}."
        status, said = pressed(serve.address("launch", MINE),
                               {"act": "save", "rows": json.dumps(rows), "seen": json.dumps(seen)})
    if status != 200 or said:
        return 409, said or "1100 refused it."
    show.show("launch", mark="#rows", stay=True)
    return 200, done + ("" if gone else " It waits there for you to fine-tune, and launches on your press or your word.")


def drafted(nn: str, text: str) -> tuple:
    """My reply put in session NN's box on my own 1100, unsent, and bordered
    there for a moment. It moves no page. I press Send myself."""
    if not text.strip():
        return 409, "Nothing to draft."
    said = show.show(f"{nn}:transcript", "", text, mark="#words", stay=True)
    return (200, f"Your reply to session {nn} waits in its box, unsent.") if said.startswith("1100 shows") \
        else (409, said)


def answered_item(nn: str, item: str, answer: str, text: str) -> tuple:
    """Agree, or my feedback, on one item of session NN's wave waiting on me,
    pressed as its button on the Clarify tab presses it. Send stays mine."""
    if answer == "feedback" and not text.strip():
        return 409, "Feedback needs its words. Nothing was saved."
    if answer not in ("agree", "feedback"):
        return 409, "Answer agree or feedback. Nothing was saved."
    form = {"act": "agree", "n": item, "on": "yes"} if answer == "agree" else {"act": "feedback", "n": item, "text": text}
    status, said = pressed(serve.address("clarify", nn), form)
    if status != 200 or said:
        return 409, said or "1100 refused it."
    show.show(f"{nn}:clarify", mark=f"#t-{item}", stay=True)
    return 200, f"Item {item}: {answer} saved on session {nn}'s Clarify tab. Send stays yours."


def hooked(path: str):
    """A hook, loaded as a module, never run."""
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3].replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reaper():
    """The /reaper hook: its end() and close()."""
    return hooked(REAPER)


def reaped(nn: str) -> tuple:
    """Session NN ended as /reaper ends it: its ports, its pid, its folder,
    then its pane, closed off the call once it has gone."""
    record = registry.entries().get(nn)
    if not record or not registry.pid_of(record):
        return 409, f"Session {nn} is not running. Nothing was ended."
    r = reaper()
    pane = r.panes.pane(record)
    pid, winners = r.end(nn, record)
    threading.Thread(target=r.close, args=([pid] if pid else [], [pane] if pane else []), daemon=True).start()
    return 200, (f"Session {nn} ended. Its folder was deleted."
                 + (f" Winner {', '.join(winners)} removed." if winners else ""))


# ---- clarify waves, clarify-page.py's ---------------------------------------------------

# An item's fields as read aloud, in the page's order. Agree and feedback
# read as My answer.
SAID = {"from": "From my words", "after": "After", "question": "Question", "decision": "Decision", "why": "Why",
        "wrong": "Wrong if", "show": "Picture", "today": "Today", "instead": "Instead", "split": "How I read it",
        "context": "Context", "what": "What", "for": "For", "against": "Against", "recommendation": "Recommendation",
        "answer": "Answer", "changed": "Changed", "led": "Led", "sources": "Sources"}


def wave(nn: str, number: str, item: str) -> tuple:
    """Session NN's newest wave, or the one numbered, sent or not, as plain
    text: its state, then each item's number, title, question, decision, my
    answer and any proposal. An item: every field it holds, from the wave
    numbered, or with no wave, from whichever wave holds it."""
    c = page.tool("clarify-page")
    found = c.waves(nn)
    if not found:
        return 409, f"Session {nn} has no wave."
    if item and not number:
        for w, p in reversed(found):
            with open(p) as f:
                if any(x["n"] == item.strip() for x in c.parse(f.read())[1]):
                    number = str(w)
                    break
        else:
            return 409, f"No wave of session {nn} holds item {item}."
    n, path = found[-1] if not number else next(((w, p) for w, p in found if str(w) == number.strip()), (0, ""))
    if not n:
        return 409, f"Session {nn} has no wave {number}. Its waves run 1 to {found[-1][0]}."
    with open(path) as f:
        head, items = c.parse(f.read())
    mine = lambda it: (f"agreed, with feedback: {it['feedback']}" if it.get("feedback") and it.get("agree") == "yes"
                       else f"feedback: {it['feedback']}" if it.get("feedback")
                       else "agreed, locked" if it.get("status") == "agreed"
                       else "agreed" if c.answered(it) else "none yet")
    offered = lambda it: (lambda v, w: f"Proposed: {v}" + (f", {w}" if w else "") + ".")(*c.suggested(it))
    if item:
        it = next((x for x in items if x["n"] == item.strip()), None)
        if not it:
            return 409, f"Wave {n} has no item {item}."
        out = [f"Wave {n}, item {it['n']}, {it['title']}."]
        out += [f"{word}: {it[k]}" for k, word in SAID.items() if it.get(k)]
        return 200, "\n".join(out + [f"My answer: {mine(it)}."] + ([offered(it)] if it.get("proposed") else []))
    left = sum(not c.answered(x) and not c.proposes(x) for x in items)
    state = ("sent" if head.get("sent") else "closed in chat" if head.get("closed") else
             "ready to send" if not left else f"waiting on you, {left} left")
    out = [f"Session {nn}'s wave {n} of {found[-1][0]}, {page.count(len(items), 'item')}, {state}."]
    out += [f"Send types {c.then(head)}."] if not head.get("sent") else []
    for it in items:
        out += ["", f"Item {it['n']}, {it['title']}.", f"Question: {it.get('question') or it['title']}",
                f"Decision: {it.get('decision', '')}", f"My answer: {mine(it)}."] + (
            [offered(it)] if it.get("proposed") else [])
    return 200, "\n".join(out)


# ---- the agenda, lib/agenda.py's -------------------------------------------------------

def mine(it: dict) -> bool:
    """Whether an item waits on me: its note holds a Mine line."""
    return any(name == "Mine" for name, _ in agenda.note_lines(it["note"]))


def agended(query: str, item: str, topic: str, order: str, start: str, count: str) -> tuple:
    """Without a choice, each phase's counts and titles, those waiting on me
    first, then the topics and orders. An item, by its title or file name:
    it whole, with what it waits on and what waits on it. A topic, or an
    order as the page's columns number them: its items. A query: each item
    whose title or note holds every word, title hits first."""
    w, (raw, _) = agenda.world(), agenda.read()
    items, column = w["items"], agenda.columns(raw)
    title = lambda i: raw[i]["title"] if i in raw else i
    line = lambda it: f"{it['title']}, order {column.get(it['id'], 1)}{', waits on you' if mine(it) else ''}."
    if item:
        try:
            i = agenda.find(raw, item.strip().removesuffix(".md"))
        except agenda.Refused:
            i = ""
        it = next((x for x in items if x["id"] == i), None)
        if not it:
            return 409, f"No agenda item {item}."
        after = [title(p) for p in it["after"]]
        waiting = [title(c) for c in agenda.waiting(raw, i)]
        return 200, "\n".join([f"{it['title']}. File {i}. Order {column.get(i, 1)}."
                               + (f" {agenda.HEADINGS.get(it['phase']) or 'Phase ' + it['phase']}." if it["phase"] else ""),
                               f"Topics: {', '.join(it['topics']) or 'none'}.",
                               f"Waits on: {'; '.join(after) or 'nothing'}.",
                               f"Waiting on it: {'; '.join(waiting) or 'nothing'}.", "", it["note"]])
    if topic or order:
        hits = ([it for it in items if topic.casefold() in (t.casefold() for t in it["topics"])] if topic
                else [it for it in items if str(column.get(it["id"], 1)) == order.strip()])
        if not hits:
            return 409, f"No agenda item sits in {f'topic {topic}' if topic else f'order {order}'}."
        hits.sort(key=lambda it: (column.get(it["id"], 1), it["title"].casefold()))
        return 200, "\n".join([f"{f'Topic {topic}' if topic else f'Order {order}'}: {page.count(len(hits), 'item')}."]
                              + paged([line(it) for it in hits], start, count, 30))
    if query:
        words = query.lower().split()
        hits = [it for it in items if all(x in f"{it['title']} {it['note']}".lower() for x in words)]
        if not hits:
            return 200, f"No agenda item matches {query}."
        hits.sort(key=lambda it: not all(x in it["title"].lower() for x in words))
        out = [f"{len(hits)} item{'s match' if len(hits) != 1 else ' matches'} {query}."]
        return 200, "\n".join(out + paged([f"\n{it['title']}\n{it['note']}" for it in hits], start, count, 10))
    out = []
    for p in agenda.PHASES or [""]:
        group = [it for it in items if it["phase"] == p]
        waits = sorted((it["title"] for it in group if mine(it)), key=str.casefold)
        rest = [it["title"] for it in group if not mine(it)]
        out += [f"{agenda.HEADINGS.get(p) or (f'Phase {p}' if p else 'My agenda')}: "
                f"{len(group)} item{'s' * (len(group) != 1)}, {len(waits)} wait{'s' * (len(waits) == 1)} on you."]
        out += [f"Mine: {'; '.join(waits)}."] if waits else []
        out += [f"Others: {'; '.join(rest)}."] if rest else []
        out.append("")
    out.append(f"Topics: {', '.join(agenda.NAMES)}. Orders: 1 to {max(column.values(), default=1)}.")
    if w["broken"]:
        out.append(f"Could not be read: {', '.join(map(str, w['broken']))}.")
    return 200, "\n".join(out).strip()


# ---- System, sessions-dashboard.py's ---------------------------------------------------

def dash():
    """1100's own server file, loaded once, for System's reads."""
    return page.tool("sessions-dashboard")


def at(epoch: float) -> str:
    """An instant on this Mac's clock, and how far it is from now."""
    s = epoch - time.time()
    m = round(abs(s) / 60)
    h, d = round(m / 60), round(m / 1440)
    span = ("under a minute" if m < 1 else f"{m} minute{'s' * (m != 1)}" if m < 60
            else f"{h} hour{'s' * (h != 1)}" if h < 48 else f"{d} days")
    return f"{dash().clock(int(epoch))}, {f'in {span}' if s > 0 else f'{span} ago'}"


def usage_part(short: bool) -> list:
    """Each account's two windows and the sessions on it, as System's cards."""
    d = dash()
    use = d.usage(registry.entries())
    if short:
        wins = "; ".join(f"claude-{a} " + (f"{u['five'][0]:.0f}% of 5 hours used, {u['week'][0]:.0f}% of 7 days used"
                                           if u["read"] else "not read yet") for a, u in use.items())
        return [f"Usage: {wins}.",
                "Sessions: " + "; ".join(f"claude-{a} {', '.join(u['on']) or 'none'}" for a, u in use.items()) + "."]
    out = []
    for a, u in use.items():
        head = f"claude-{a}" + (f", {d.PLANS[a]}" if d.PLANS.get(a) else "")
        on = f"Sessions {', '.join(u['on'])}." if u["on"] else "No session runs on it."
        if not u["read"]:
            out.append(f"{head}: no reading yet. {on}")
            continue
        wins = [f"{word} {pct:.0f}% used" + (f", reset{'s' * (reset > time.time())} {at(reset)}" if reset else "")
                for word, (pct, reset) in (("5-hour", u["five"]), ("7-day", u["week"]))]
        out.append(f"{head}: {'; '.join(wins)}. Last read {at(u['read'])}. {on}")
    return out


def ports_part(short: bool) -> list:
    """Band 00, the database first, then this project's other ports, as
    System shows them. Other apps' ports are only counted."""
    d = dash()
    state, listening = d.seen()
    titles = {nn: r.get("title", nn) for nn, r in registry.entries().items()}
    others = d.other(titles, listening)
    mine = [o for o in others if ports.in_scheme(o[0])]
    rest = len(others) - len(mine)
    groups = [*([d.DATABASE] if d.DATABASE else []), *d.BAND]
    down = [f"{p} {name}" for _, g in groups for p, name in g if not state.get(p)]
    band = (f"Band 00: {sum(map(bool, state.values()))} of {len(state)} up"
            + (f"; down: {', '.join(down)}." if down else ".")) if groups else "This project runs no band 00."
    if short:
        return [band, f"Other ports: {len(mine)} of this project's, {rest} of other apps'."]
    out = [f"{label}: " + ", ".join(f"{p} {name} {'up' if state.get(p) else 'down'}" for p, name in g) + "."
           for label, g in groups] or [band]
    out += [f"Port {p}, {proc}" + (f", {who}" if who else "") + "." for p, proc, who in mine]
    return out + [f"And {page.count(rest, 'port')} of other apps." if rest else "No other app's port."]


def guard_part(short: bool) -> list:
    """The memory guard's open findings, each its id, line and acts."""
    d = dash()
    found = d.findings()
    if found is None:
        return ["The memory guard's findings cannot be read."]
    if not found:
        return ["Memory guard: nothing is wrong."]
    try:
        if short:
            return [f"Memory guard: {page.count(len(found), 'finding')} open.",
                    "; ".join(f["title"].removeprefix("Memory guard: ") for f in found) + "."]
        out = []
        for f in found:
            out.append(f"Finding {f['id']}, {d.LEVELS.get(f['level'], ('', f['level']))[1]}: {f['line']}")
            out.append("Its acts: " + "; ".join(f"{b['verb']}, {b['label']}" for b in f["buttons"]) + ".")
            out += [f"Idle: session {s['number']}, {s['gb']:.1f} GB, {s['idle']} minutes." for s in f.get("sessions", [])]
        return out
    except (KeyError, TypeError, AttributeError):
        return ["The memory guard's findings cannot be read."]


def settings_part(short: bool) -> list:
    """System's defaults: the account order, effort and model, each
    account's own, the outsource engine and both thresholds."""
    o = accounts.read()
    order = (f"{' '.join(o['order'])}, the next launch takes {o['order'][o['next']]}" if o["order"]
             else f"none set, every launch takes account {accounts.FALLBACK}")
    effort, model = accounts.effort(), models.name(accounts.model())
    own = "; ".join(f"claude-{a} " + ((models.name(m["model"]) if m["model"] else m["saved"])
                                      + (f", {m['effort']}" if m["effort"] else "") if m["saved"] else "nothing saved")
                    for a, m in ((a, accounts.own(a)) for a in accounts.KNOWN))
    d = dash()
    eng = "; ".join(f"{d.engines.NAMES[e]} {s['set']['model']}" + (f", {s['set']['effort']}" if s["set"].get("effort") else "")
                    for e, s in d.engines_seen().items()) or "none set up"
    limits = f"handover at {context.threshold()}% of context, wrap-up at {context.wrapup()}%"
    if short:
        return [f"Settings: order {order}; effort {effort}; model {model}; {limits}.",
                f"Started by hand: {own}. Outsource: {eng}."]
    return [f"Account order: {order}.", f"Default effort: {effort}.", f"Default model: {model}.",
            f"Started by hand: {own}.", f"Outsource engines: {eng}.", limits[0].upper() + limits[1:] + "."]


PARTS = {"usage": usage_part, "ports": ports_part, "guard": guard_part, "settings": settings_part}


def system(part: str) -> tuple:
    """One part of System whole, or each part in two lines."""
    part = part.lower()
    if part and part not in PARTS:
        return 409, f"A part is one of {', '.join(PARTS)}."
    if part:
        return 200, "\n".join(PARTS[part](False))
    return 200, "\n\n".join("\n".join(f(True)) for f in PARTS.values())


# A setting, as System's own field posts it, and what the answer names it.
SETTINGS = {"order": "The account order", "effort": "The default effort", "model": "The default model",
            "own_model": "own model", "own_effort": "own effort", "engine_model": "model",
            "engine_effort": "effort", "threshold": "The handover threshold", "wrapup": "The wrap-up threshold"}


def setting(name: str, value: str, account: str, engine: str) -> tuple:
    """One setting saved, as System's page posts it to /. 1100's refused()
    answers a bad value. The door switch is never the app chat's: shut,
    this chat could not open it again."""
    name = name.lower().replace("-", "_")
    if name == "door":
        return 409, "I never set the app door: shut, it cannot be opened from this chat. Nothing was changed."
    if name not in SETTINGS:
        return 409, f"A setting is one of {', '.join(SETTINGS)}. Nothing was changed."
    if not value:
        return 409, "Name its value. Nothing was changed."
    if name.startswith("own_"):
        if not account:
            return 409, "Name the account, like 2. Nothing was changed."
        form, done = {"own": account, name: value}, f"claude-{account}'s {SETTINGS[name]} is now {value}."
    elif name.startswith("engine_"):
        if not engine:
            return 409, "Name the engine, codex. Nothing was changed."
        form, done = {"engine": engine.lower(), name: value}, f"{engine.capitalize()}'s {SETTINGS[name]} is now {value}."
    else:
        form, done = {name: value}, f"{SETTINGS[name]} is now {value}."
    status, said = pressed("/", form)
    if status == 200:
        spot = (f'.own[data-a="{account}"]' if name.startswith("own_") else f'.eng[data-e="{engine.lower()}"]'
                if name.startswith("engine_") else {"wrapup": "#wrap"}.get(name, f"#{name}"))
        show.show("system", mark=spot, stay=True)
    return status, (done if status == 200 else said)


# ---- a prototype as I name it, for show_page ---------------------------------------------

# A variation as I say it: g2/v3, 2/v3 or g2 v3.
PICK = re.compile(r"g?(\d+)\s*[/ ]\s*(v\d+)")


def subject_of(said: str) -> str:
    """A subject as I say it, in its kebab name."""
    return re.sub(r"\s+", "-", said.strip().lower())


# ---- the project's files, only those git tracks ----------------------------------------

# The door's own key and log, never read aloud, whatever git says.
SECRET = ".claude/state/door/"


def tracked() -> set:
    """Every file git tracks, as git names it from the project's root."""
    r = subprocess.run(["git", "-C", door.ROOT, "ls-files", "-z"], capture_output=True, text=True, timeout=10)
    return {f for f in r.stdout.split("\0") if f and not f.startswith(SECRET)}


def where(path: str):
    """A path as I name it, and where it really leads, both from the
    project's root: "" for the root itself. None when either leaves it."""
    root = os.path.realpath(door.ROOT)
    rel = os.path.normpath(path.strip().strip("/") or ".")
    real = os.path.realpath(os.path.join(root, rel))
    if real != root and not real.startswith(root + os.sep):
        return None
    return ("" if rel == "." else rel), ("" if real == root else os.path.relpath(real, root))


def kind(name: str) -> str:
    mime = mimetypes.guess_type(name)[0] or ""
    ext = os.path.splitext(name)[1][1:].lower()
    return "picture" if mime.startswith("image/") else "clip" if mime.startswith("video/") else (
        f"{ext} file" if ext else "file")


def folder(path: str, start: str, count: str) -> tuple:
    """A tracked folder's folders, each its count of files, then its files,
    each its kind and size, 60 at a time."""
    files, got = tracked(), where(path)
    holds = lambda rel: rel == "" or any(f.startswith(rel + "/") for f in files)
    if got is None or not all(map(holds, got)):
        if got and all(x in files for x in got):
            return 409, f"{got[0]} is a file. read_file reads it."
        return 409, f"Git tracks no folder {path.strip()}. Nothing is listed."
    prefix = got[0] + "/" if got[0] else ""
    folders, here = {}, []
    for f in files:
        if f.startswith(prefix):
            top, deeper, _ = f[len(prefix):].partition("/")
            if deeper:
                folders[top] = folders.get(top, 0) + 1
            else:
                here.append(top)
    full = lambda n: os.path.join(door.ROOT, prefix + n)
    rows = [f"{n}/, folder, {page.count(c, 'file')}" for n, c in sorted(folders.items())]
    rows += [f"{n}, {kind(n)}, " + (dash().size(os.path.getsize(full(n))) if os.path.isfile(full(n)) else "gone from disk")
             for n in sorted(here)]
    head = f"{got[0] or 'The project'}: {page.count(len(folders), 'folder')}, {page.count(len(here), 'file')}."
    return 200, "\n".join([head] + paged(rows, start, count, 60))


def filed(path: str, start: str, lines: str) -> tuple:
    """A tracked file's lines, 200 from START by default. A picture or any
    file that is no text says what it is."""
    files, got = tracked(), where(path)
    if got is None or not all(x in files for x in got) or not os.path.isfile(os.path.join(door.ROOT, got[1])):
        return 409, f"Git tracks no file {path.strip()}. Nothing was read."
    return text_lines(got[0], os.path.join(door.ROOT, got[1]), start, lines)


def text_lines(rel: str, full: str, start: str, lines: str) -> tuple:
    """A file's lines, 200 from START by default, named REL. A picture or
    any file that is no text says what it is."""
    with open(full, "rb") as f:
        data = f.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = "\0"
    if "\0" in text:
        mime = mimetypes.guess_type(rel)[0]
        return 200, f"{rel} is a {kind(rel)}{f', {mime}' if mime else ''}, {dash().size(len(data))}. It holds no text."
    every = text.splitlines()
    first = max(int(start), 1) if start.isdigit() else 1
    count = min(max(int(lines), 1), 1000) if lines.isdigit() else 200
    if not every:
        return 200, f"{rel} is empty."
    if first > len(every):
        return 409, f"{rel} has only {len(every)} lines."
    last = min(first + count - 1, len(every))
    return 200, f"{rel}, lines {first} to {last} of {len(every)}.\n\n" + "\n".join(every[first - 1:last])


# ---- a long list, read the same way everywhere ------------------------------------------

def paged(lines: list, start: str, count: str, per: int = 20) -> list:
    """A list's lines from START, COUNT of them, PER by default: where they
    sit in it first, and the start that reads on last."""
    total = len(lines)
    first = max(int(start), 1) if start.isdigit() else 1
    many = min(max(int(count), 1), 200) if count.isdigit() else per
    if not total:
        return []
    if first > total:
        return [f"It holds only {total}. Nothing from {first}."]
    end = min(first + many - 1, total)
    head = [] if first == 1 and end == total else [f"{first} to {end} of {total}."]
    return head + lines[first - 1:end] + ([f"More from start {end + 1}."] if end < total else [])


# The arguments every list takes, in each tool's schema.
START = {"type": "integer", "description": "The first of a long list to read, 1 by default."}
COUNT = {"type": "integer", "description": "How many to read from start."}
PAGING = {"start": START, "count": COUNT}


# ---- Files, sessions-dashboard.py's: each session's own folder --------------------------

def session_files(nn: str, path: str, start: str, count: str) -> tuple:
    """Without a session, every session's folder and its count of files.
    With one, a folder inside it in the Files page's order, or a file's
    lines. Nothing outside a session's own folder, as the page."""
    d, held = dash(), registry.entries()
    if not nn:
        lines = [f"Session {n}, {r.get('title') or n}: {page.count(d.count(os.path.realpath(registry.folder(n))), 'file')}."
                 for n, r in sorted(held.items())]
        return 200, "\n".join([f"{page.count(len(held), 'session folder')}."] + paged(lines, start, count, 40))
    if nn not in held:
        return 409, f"Session {nn} has no folder."
    root, rel = os.path.realpath(registry.folder(nn)), path.strip().strip("/")
    named_as = f".claude/state/sessions/{nn}/" + rel
    if rel and (full := d.inside(nn, rel)):
        return text_lines(named_as, full, start, count)
    want = os.path.realpath(os.path.join(root, rel))
    if not ((want == root or want.startswith(root + os.sep)) and os.path.isdir(want)):
        return 409, f"Session {nn}'s folder holds no {rel}."
    rows = []
    for p in d.listed(want):
        name = os.path.basename(p)
        if os.path.isdir(p):
            rows.append(f"{name}/, folder, {page.count(d.count(p), 'file')}.")
        elif os.path.isfile(p):
            st = os.stat(p)
            rows.append(f"{name}, {kind(name)}, {d.size(st.st_size)}, changed {at(st.st_mtime)}.")
    return 200, "\n".join([f"{named_as.rstrip('/')}: {page.count(len(rows), 'entry', 'entries')}."]
                          + paged(rows, start, count, 40))


# ---- the library, library-page.py's ---------------------------------------------------

def shelf_of_words() -> tuple:
    """The library page, and its rail's every row, numbered as it numbers
    them: chapters, subchapters, sections, graphs and words."""
    lib = page.tool("library-page")
    return lib, lib.numbered(lib.tree(lib.read(os.path.join(lib.LIBRARY, lib.MOC)) or ""))


def named(row: dict) -> str:
    """A row as the app chat names it: its number and its name, never where it
    sits. A graph is lettered under its subchapter."""
    if row["kind"] == "graph":
        return f"Graph {row['n'].rsplit('.', 1)[1]} of subchapter {row['up']}, {row['name']}"
    held = f", {page.count(row['count'], 'item')}" if row["kind"] in ("chapter", "subchapter", "section") else ""
    return f"{row['kind'].capitalize()} {row['n']}, {row['name']}{held}"


def row_of(rows: list, said: str, kinds=("word", "graph")):
    """The row a number, slug or name I said picks, of those kinds, or None."""
    said = said.strip().removeprefix("#")
    for test in (lambda r: r["n"].casefold() == said.casefold(),
                 lambda r: r["slug"] == re.sub(r"\s+", "-", said.lower()),
                 lambda r: r["name"].casefold() == said.casefold()):
        if got := next((r for r in rows if r["kind"] in kinds and test(r)), None):
            return got
    return None


def library(at: str, start: str, count: str) -> tuple:
    """The library's contents by its numbers. Nothing named: each chapter
    and its subchapters. A chapter: its subchapters. A subchapter: its
    graphs, then its words or sections. A section: its words. A word or a
    graph: its page, as read_word and read_graph read it."""
    lib, rows = shelf_of_words()
    if not rows:
        return 409, "The library holds nothing."
    at = at.strip()
    if not at:
        lines = [ended(named(r)) for r in rows if r["kind"] in ("chapter", "subchapter")]
        return 200, "\n".join([f"The library, {page.count(sum(r['kind'] == 'chapter' for r in rows), 'chapter')}."]
                              + paged(lines, start, count, 60))
    got = row_of(rows, at, ("chapter", "subchapter", "section", "word", "graph"))
    if not got:
        return 409, f"The library holds no {at}. Name a number like 2, 2.1, 2.1.3 or 2.1.A."
    if got["kind"] == "word":
        return worded(got["n"])
    if got["kind"] == "graph":
        return graphed(got["n"])
    kids = [ended(named(r)) for r in rows if r["up"] == got["n"]]
    return 200, "\n".join([ended(named(got))] + (paged(kids, start, count, 40) or ["It holds nothing yet."]))


def library_marked(said: str, to: str) -> tuple:
    """One word or graph marked reviewed or not, as its button on the
    library page marks it."""
    ok, line = page.tool("library-review").marked(said, to)
    if ok:
        show.show("library", mark=".rv-line", stay=True)
    return (200 if ok else 409), line


def spoken(text: str) -> str:
    """A line as it reads aloud: a link as its name, no backticks or bold."""
    lib = page.tool("library-page")
    return lib.LINK.sub(lambda m: m.group(2) or m.group(1).replace("-", " "), text).replace("`", "").replace("**", "")


def ended(text: str) -> str:
    """A line closed with a full stop, unless it already ends a sentence."""
    return text if text.endswith((".", "?", "!", ":", "…")) else text + "."


def text_of(lib, row: dict):
    """A word's or a graph's file, or None when it has none."""
    folder = os.path.join(lib.LIBRARY, lib.GRAPHS) if row["kind"] == "graph" else lib.LIBRARY
    return lib.read(os.path.join(folder, f"{row['slug']}.md"))


def library_found(query: str, start: str, count: str) -> tuple:
    """Each word and graph whose name, slug or text holds every word of the
    query, those whose name holds it first, each by its number."""
    words = query.lower().split()
    if not words:
        return 409, "Give the words to find."
    lib, rows = shelf_of_words()
    hits, seen = [], set()
    for r in rows:
        if r["kind"] in ("word", "graph") and (r["kind"], r["slug"]) not in seen:
            seen.add((r["kind"], r["slug"]))
            if all(w in f"{r['slug']} {r['name']} {text_of(lib, r) or ''}".lower() for w in words):
                hits.append((not all(w in r["name"].lower() for w in words), ended(named(r))))
    if not hits:
        return 200, f"No word or graph in the library holds {query}."
    lines = [line for _, line in sorted(hits, key=lambda h: h[0])]
    return 200, "\n".join([f"{page.count(len(lines), 'match', 'matches')} for {query}."]
                          + paged(lines, start, count, 15))


def neighbours(rows: list, got: dict) -> list:
    """The rows before and after one, under the same subchapter or section."""
    kin = [r for r in rows if r["up"] == got["up"] and r["kind"] in ("word", "graph")]
    i = next(i for i, r in enumerate(kin) if r["n"] == got["n"])
    return ([ended(f"Before it: {named(kin[i - 1])}")] if i else []) + (
        [ended(f"After it: {named(kin[i + 1])}")] if i + 1 < len(kin) else [])


def worded(said: str) -> tuple:
    """One word's page, as plain text: its number, its sections, the graphs
    explaining it, its source, then the words beside it."""
    lib, rows = shelf_of_words()
    got = row_of(rows, said, ("word",))
    if not got:
        return 409, f"The library holds no word {said}."
    text = text_of(lib, got)
    out = [ended(named(got))]
    out += [f"Also word {r['n']}." for r in rows if r["kind"] == "word" and r["slug"] == got["slug"] and r is not got]
    sections, source = lib.parts(text) if text is not None else ([], "")
    out += [] if text is not None else ["It has no page yet."]
    for heading, paragraphs in sections:
        out += ["", f"{heading}."] + [spoken(p) for p in paragraphs]
    out += ["\n" + ended(f"Explained in {named(g)[0].lower() + named(g)[1:]}") for g in rows
            if g["kind"] == "graph" and got["slug"] in lib.linked(text_of(lib, g))]
    return 200, "\n".join(out + ([f"\nSource: {source}"] if source else []) + [""] + neighbours(rows, got))


def boxed_as(rows: list, box: tuple) -> str:
    """A box's words, and the word it links by its number, when it has one."""
    w = next((r for r in rows if r["kind"] == "word" and r["slug"] == box[1]), None) if box[1] else None
    return spoken(box[0]) + (f" (word {w['n']}, {w['name']})" if w else "")


def graphed(said: str) -> tuple:
    """One graph, as plain text: its text, then each lane's steps in order,
    each branch beside its step and each box's word, then its figure and
    sources, then what sits beside it."""
    lib, rows = shelf_of_words()
    got = row_of(rows, said, ("graph",))
    text = text_of(lib, got) if got else None
    if text is None:
        return 409, f"The library holds no graph {said}."
    g = lib.chart(text)
    out = [ended(named(got))]
    out += [f"Series: {g['series']}."] if g["series"] else []
    out += [f"{line[0]}: {spoken(line[1])}" if k == "fact" else spoken(line) for k, line in g["text"]]
    lanes = g["lanes"]
    out += ["", f"The graph, {page.count(len(lanes), 'lane')}." if len(lanes) > 1 else "The graph."]
    for i, lane in enumerate(lanes, 1):
        out += [f"Lane {i}, {spoken(lane['name'])}:"] if len(lanes) > 1 else []
        for j, step in enumerate(lane["steps"], 1):
            branch = step["branch"]
            out.append(ended(f"Step {j}: {boxed_as(rows, step['box'])}")
                       + (" " + ended(f"If {branch[0]}: {boxed_as(rows, branch[1])}") if branch else ""))
        out += [spoken(u) for u in lane["unproven"]]
    out += ([f"Figure: {spoken(g['caption'])}"] if g["caption"] else []) + [spoken(u) for u in g["unproven"]]
    return 200, "\n".join(out + [f"Source: {s}" for s in g["sources"]] + [""] + neighbours(rows, got))


# ---- skills, skills-page.py's ---------------------------------------------------------

def skilled(query: str, family: str, start: str, count: str) -> tuple:
    """Without a query or a family, each family and its commands, No family
    first as the page shows it. A family by its digit, or No family by
    none: its skills whole. A query: each skill whose command, arguments or
    intent holds every word. Each skill read whole is its command, its
    arguments and its intent."""
    sk = page.tool("skills-page")
    found = sk.heads()
    intent = lambda d: (re.match(r".*?[.!?](?=\s|$)", d) or [d])[0]
    whole = lambda ss: [f"/{n}" + (f", arguments: {a}" if a else "") + f". {intent(d)}" for n, d, a in ss]
    groups = sk.families(found)
    groups = groups[-1:] + groups[:-1]
    if family:
        got = next((g for g in groups if g[0] == family.strip() or (family.strip().lower() == "none" and not g[0])), None)
        if not got:
            return 409, f"No family {family}. A family is its digit, like 3, or none."
        title = f"{got[1].replace('-', ' ').capitalize()}, family {got[0]}" if got[0] else "No family"
        return 200, "\n".join([f"{title}, {page.count(len(got[2]), 'skill')}."] + paged(whole(got[2]), start, count, 30))
    if query:
        words = query.lower().split()
        hits = [s for s in found if all(w in f"{s[0]} {s[2]} {intent(s[1])}".lower() for w in words)]
        if not hits:
            return 200, f"No skill's command, arguments or intent holds {query}."
        return 200, "\n".join([f"{page.count(len(hits), 'skill')} for {query}."] + paged(whole(hits), start, count, 15))
    out = [f"{page.count(len(found), 'skill')}."]
    for digit, fam, skills in groups:
        if skills:
            title = f"{fam.replace('-', ' ').capitalize()}, family {digit}" if digit else "No family"
            out.append(f"{title}: " + ", ".join(f"/{s[0]}" for s in skills) + ".")
    return 200, "\n".join(out)


# ---- a session's explanations, explanation-page.py's -------------------------------------

def explained(nn: str, name: str, section: str) -> tuple:
    """Without a name, session NN's documents, highest number first, each
    its title, its lede and times. With a name or a number, that document's
    title, lede and numbered sections, as its contents rail. With a section
    too, that section's text, or all for the whole document."""
    ep = page.tool("explanation-page")
    found = ep.numbered(nn)
    if not found:
        return 409, f"Session {nn} holds no explanation document."
    if not name:
        return 200, "\n".join([f"Session {nn}'s {page.count(len(found), 'document')}, newest first:"]
                              + [f"Document {n}, {(h := ep.heading(p))[0] or f}, named {f}. {h[1]} {ep.when(p, made)}."
                                 for n, f, p, made in found])
    name = name.strip().lower().removesuffix(".md")
    got = next(((n, p) for n, f, p, _ in found if name in (f, str(n))), None)
    if not got:
        return 409, f"Session {nn} holds no document {name}."
    n, path = got
    text = ep.text(path)
    if section.strip().lower() == "all":
        return 200, text
    head, *parts = re.split(r"(?m)^(?=## )", text)
    title, lede = ep.heading(path)
    if not section:
        return 200, "\n".join([f"Document {n} of {found[0][0]}, {title}.", lede, ""]
                              + [f"Section {i}, {p.splitlines()[0][3:].strip()}." for i, p in enumerate(parts, 1)]
                              + ["", "Read one with its section number, or all."])
    if not section.isdigit() or not 1 <= int(section) <= len(parts):
        return 409, f"Document {n} has sections 1 to {len(parts)}."
    i = int(section)
    return 200, f"Document {n}, section {i} of {len(parts)}.\n\n" + parts[i - 1].strip()


# ---- one item on show, show.py's place --------------------------------------------------

def place_of(target: str, at: str) -> tuple:
    """The end of a page's address naming one item in it, as (place, why
    not). A library word or graph by number or name, a Files file as
    NN/path, a document by name or number, a jury run, a screenshot by its
    number, a prototype subject on 1400, or a variation in a session's."""
    target, at = target.strip().lower(), at.strip()
    kind = target.partition(":")[2]
    nn = target.partition(":")[0]
    if target == "library":
        _, rows = shelf_of_words()
        r = row_of(rows, at)
        return (("#graph:" if r["kind"] == "graph" else "#") + r["slug"], "") if r else (
            "", f"The library holds no word or graph {at}.")
    if target == "files":
        return "?f=" + urllib.parse.quote(at.strip("/")), ""
    if target == "prototypes":
        return "?" + urllib.parse.urlencode({"subject": subject_of(at)}), ""
    if kind == "prototype":
        m = PICK.fullmatch(at.lower())
        return (f"#{m[1]}/{m[2]}", "") if m else (("#pick", "") if at.lower() == "pick" else (
            "", "Name a variation like g2/v3, or pick."))
    if kind == "explanation":
        found = page.tool("explanation-page").numbered(nn)
        f = next((f for n, f, _, _ in found if at.lower().removesuffix(".md") in (f, str(n))), "")
        return ("/" + f, "") if f else ("", f"Session {nn} holds no document {at}.")
    if kind == "jury":
        return "?" + urllib.parse.urlencode({"run": at}), ""
    if kind == "shots":
        return (f"#{at}", "") if at.isdigit() else ("", "Name the screenshot by its number, like 4.")
    if kind == "clarify":
        return (f"#{at}", "") if at.isdigit() else ("", "Name the item by its number, like 12.")
    return "", f"{target} opens no item inside it. Show it without at."


# ---- the door -------------------------------------------------------------------------
# MCP over streamable HTTP, the plainest form: each POST carries one JSON-RPC
# message and gets one JSON answer. No stream, no session id, no package.

# The Claude app never shows a connector's own instructions to its chat; only
# tool descriptions reach it. So each description carries its own short rule,
# and read_rules hands over the whole set, from a file git versions.
RULES = os.path.join(HERE, "app-rules.md")
# What the chat last read, by fingerprint: my rules at read_rules, the tool
# list at tools/list, and the tool list it was last told changed. Kept in the
# door's own folder, so a restart remembers them. The door cannot tell two
# chats apart, so one chat's read counts for both.
READ = os.path.join(door.STATE, "read.json")
KEEPING = threading.Lock()


def fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def rules_now() -> str:
    with open(RULES, "rb") as f:
        return fingerprint(f.read())


def tools_now() -> str:
    return fingerprint(json.dumps(TOOLS, sort_keys=True).encode())


def last_read() -> dict:
    try:
        with open(READ) as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {}
    except (OSError, ValueError):
        return {}


def mark_read(**prints) -> None:
    with KEEPING:
        kept = {**last_read(), **prints}
        os.makedirs(os.path.dirname(READ), exist_ok=True)
        with open(READ, "w") as f:
            json.dump(kept, f)


# Every tool, as written. TOOLS, below, is what the app lists: numbered, in my order.
DEFINED = [
    {"name": "read_rules",
     "description": "My full rules for you, the app chat. Call it first in every chat, before any other "
                    "tool, and again whenever a tool says my rules changed. Follow them.",
     "inputSchema": {"type": "object", "properties": {}},
     "annotations": {"title": "Read my rules", "readOnlyHint": True, "openWorldHint": False}},
    {"name": "list_sessions",
     "description": "Every session running on my Mac, one line each: its number, its name, "
                    "and whether it works or waits on me. Call read_rules first in every chat.",
     "inputSchema": {"type": "object", "properties": {}},
     "annotations": {"title": "List sessions", "readOnlyHint": True, "openWorldHint": False}},
    {"name": "read_session",
     "description": "One session. Bare: its state, its move, its last words since my last message, a dialog "
                    "waiting with its choices, its mode, and whether a handover waits. Tell me its move in a "
                    "sentence or two. With start or count: its turns, one line each. "
                    "With turn: that turn whole, every step it took.",
     "inputSchema": {"type": "object", "required": ["session"],
                     "properties": {"session": {"type": "string",
                                                "description": "The session's two-digit number, like 02."},
                                    "turn": {"type": "string", "description": "A turn's number, as its page "
                                             "numbers it, or last."}, **PAGING}},
     "annotations": {"title": "Read a session", "readOnlyHint": True, "openWorldHint": False}},
    # No tool is marked destructive: my app's own setting, Needs approval,
    # asks my click instead, as app-rules.md says.
    {"name": "stop_session",
     "description": "Ends one running session for good: its process, its pane and its folder go. "
                    "It cannot be undone. My click on the app's prompt is my yes.",
     "inputSchema": {"type": "object", "required": ["session"],
                     "properties": {"session": {"type": "string",
                                                "description": "The session's two-digit number, like 02."}}},
     "annotations": {"title": "End a session", "readOnlyHint": False, "destructiveHint": False,
                     "openWorldHint": False}},
    {"name": "show_page",
     "description": "Switches your own view of my session dashboard, and no other chat's, to a page or a "
                    "session's tab. Your view is the number in the address you opened: ?app is 1, ?app=2 is 2. "
                    "A page is one of: "
                    "skills, system, agenda, launch, prototypes, files, library, a session like 05, "
                    "or a tab like 05:clarify. With at, one item inside it: on library a word or graph by its "
                    "number, on files a file as 05/path, on prototypes a subject, on NN:prototype a variation "
                    "like g2/v3, on NN:explanation a document, on NN:jury a run, on NN:shots a screenshot's "
                    "number, on NN:clarify an item's number. Show at once, never saying it back first.",
     "inputSchema": {"type": "object", "required": ["target", "view"],
                     "properties": {"target": {"type": "string", "description": "A page, NN, or NN:tab."},
                                    "view": {"type": "string", "description": "Your view's number, like 1."},
                                    "at": {"type": "string", "description": "One item inside it."}}},
     "annotations": {"title": "Show a page", "readOnlyHint": False, "destructiveHint": False,
                     "openWorldHint": False}},
    {"name": "read_wave",
     "description": "One session's clarify wave, its newest or the one numbered, sent or not: its state, "
                    "then each item's number, title, question, decision, my answer and any proposal. "
                    "With item, every field that item holds, found in whichever wave holds it.",
     "inputSchema": {"type": "object", "required": ["session"],
                     "properties": {"session": {"type": "string",
                                                "description": "The session's two-digit number, like 02."},
                                    "wave": {"type": "string", "description": "A wave's number, like 3. "
                                             "Left out, the newest."},
                                    "item": {"type": "string", "description": "An item's number, like 12. "
                                             "Without wave, every wave is searched."}}},
     "annotations": {"title": "Read a wave", "readOnlyHint": True, "openWorldHint": False}},
    {"name": "read_agenda",
     "description": "My agenda. Without a choice, each phase's counts and titles, those waiting on me first, "
                    "then its topics and orders. With an item, it whole: its note, topics, order, what it waits on "
                    "and what waits on it. With a topic or an order, its items. With a query, each matching item.",
     "inputSchema": {"type": "object",
                     "properties": {"query": {"type": "string", "description": "Words to find in titles and notes."},
                                    "item": {"type": "string", "description": "An item's title or file name."},
                                    "topic": {"type": "string", "description": "A topic's name."},
                                    "order": {"type": "string", "description": "An order's number, like 2."},
                                    **PAGING}},
     "annotations": {"title": "Read my agenda", "readOnlyHint": True, "openWorldHint": False}},
]


def tool(name: str, title: str, description: str, properties: dict, required=(), reads=True) -> dict:
    """One more tool, in the shape of those above."""
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties, **({"required": list(required)} if required else {})},
            "annotations": {"title": title, "readOnlyHint": reads, "openWorldHint": False,
                            **({} if reads else {"destructiveHint": False})}}


SESSION = {"type": "string", "description": "The session's two-digit number, like 02."}
TEXT = lambda said: {"type": "string", "description": said}

DEFINED += [
    tool("read_system", "Read System",
         "My System page: usage, ports, guard or settings whole, or each in two lines when no part is named.",
         {"part": {"type": "string", "enum": list(PARTS)}}),
    tool("set_system", "Set a System setting",
         "Saves one setting on my System page: order, effort, model, an account's own_model or own_effort, "
         "an engine's engine_model or engine_effort, threshold or wrapup. Never the app door. "
         "Set at once, never saying it back first.",
         {"setting": {"type": "string", "enum": list(SETTINGS)}, "value": TEXT("The new value, like high, or 1 2 3."),
          "account": TEXT("The account, like 2, for own_model and own_effort."),
          "engine": TEXT("codex, for engine_model and engine_effort.")},
         ["setting", "value"], reads=False),
    tool("list_folder", "List a folder",
         "One folder of my project, only what git tracks: each name, its kind and size. "
         "Without a path, the project's top.", {"path": TEXT("A folder from the project's top, like .claude/tools."),
                                                **PAGING}),
    tool("read_session_files", "Read a session's files",
         "My Files page: each session's own folder. Without a session, every folder and its count of files. "
         "With one, a folder inside it, or a file's lines, 200 at a time.",
         {"session": SESSION, "path": TEXT("A folder or file inside the session's folder, like playwright."), **PAGING}),
    tool("read_file", "Read a file",
         "One file of my project git tracks, 200 lines at a time by default. Read it at once.",
         {"path": TEXT("The file from the project's top, like CLAUDE.md."),
          "start": {"type": "integer", "description": "The first line, 1 by default."},
          "lines": {"type": "integer", "description": "How many lines, 200 by default."}}, ["path"]),
    tool("read_library", "Read my library",
         "My library's contents, numbered as its page numbers them. Without at, each chapter and subchapter. "
         "At a chapter like 2, its subchapters. At a subchapter like 2.1, its graphs A, B, then its words or "
         "sections. At a section like 2.1.3, its words. At a word like 2.1.3 or a graph like 2.1.A, its page. "
         "Name a library item by its number alone, like subchapter 2.1 or graph A of subchapter 2.1.",
         {"at": TEXT("A number like 2, 2.1, 2.1.3 or 2.1.A, or a word's or graph's name."), **PAGING}),
    tool("search_library", "Search my library",
         "Finds the words and graphs in my library holding every word of my query, each by its number.",
         {"query": TEXT("Words to find."), **PAGING}, ["query"]),
    tool("read_word", "Read a library word",
         "One word's page in my library, then the words before and after it.",
         {"slug": TEXT("The word's number like 2.1.3, its slug like api-key, or its name.")}, ["slug"]),
    tool("read_graph", "Read a library graph",
         "One graph in my library: its text, then each lane's steps in order, each box's word by its number.",
         {"slug": TEXT("The graph's number like 2.1.A, its slug, or its name.")}, ["slug"]),
    tool("mark_library_review", "Mark a library item reviewed",
         "Marks one word or graph of my library reviewed, or not reviewed, as its button on the library page does. "
         "Reviewed keeps a copy of its page as it reads now; a later change to it shows as changed since review.",
         {"at": TEXT("A number like 1.2.5 or 1.2.A, or a word's or graph's name."),
          "to": {"type": "string", "enum": ["reviewed", "not-reviewed"]}}, ["at", "to"], reads=False),
    tool("read_skills", "Read my skills",
         "My skills: without a query or a family, each family and its commands. With a family, its skills whole: "
         "command, arguments and intent. With a query, each matching skill whole.",
         {"query": TEXT("Words to find in a command, its arguments or its intent."),
          "family": TEXT("A family's digit, like 3, or none for No family."), **PAGING}),
    tool("read_launch", "Read a launch page",
         "One session's launch page, 00 being my own: each row as written, its session or browser, its pills, "
         "its status and first message, and whether a stage's close launches it.", {"session": SESSION}, ["session"]),
    tool("launch_rows", "Launch a launch page",
         "Presses Launch on one session's launch page, 00 being my own: its rows launch as written. "
         "On my own, only the rows you wrote launch; mine wait for my press. "
         "Launch at once, never saying it back first.", {"session": SESSION}, ["session"], reads=False),
    tool("write_launch", "Write my launch page",
         "Every session I want: one row on my own launch page, for me to fine-tune. It moves no page I see. "
         "It holds the session's name and first message, plus only what I named. With row, changes or removes "
         "a row you wrote, and only what you pass changes. It never launches. Write at once, never saying it back first.",
         {"row": TEXT("A row you wrote, by its number on the page, like 2. Left out, a new row."),
          "name": TEXT("A few words naming its work, like web app walker. Never its number: number holds that."),
          "message": TEXT("Its first message."),
          "number": TEXT("Its seat, two digits, like 09. Left out, the lowest free seat."),
          "account": TEXT("An account number, like 2, or system for my order's next."),
          "model": TEXT("A model, like opus, sonnet, haiku, fable or claude-opus-5-5, or system for my System page's."),
          "effort": TEXT("low, medium, high, xhigh or max, or system for my System page's."),
          "self_drive": {"type": "boolean", "description": "True: it takes the work to its end alone. False: it waits on me."},
          "remove": {"type": "boolean", "description": "True: the row named goes."},
          "near": TEXT("What its pane sits beside: a session, like 04, or a row above it, like row 2."),
          "side": TEXT("below, above, left or right of near, below by default; or new tab, or new window."),
          "clone": TEXT("A session it starts as a fork of, two digits, like 01.")},
         reads=False),
    tool("read_explanation", "Read an explanation",
         "One session's explanation documents: without a name, the list. With a name or number, its title, "
         "its lede and its numbered sections. With a section too, that section's text, or all for the whole. "
         "Read it at once.",
         {"session": SESSION, "name": TEXT("The document's name or number."),
          "section": TEXT("A section's number, like 2, or all.")}, ["session"]),
    tool("draft_reply", "Draft a reply in a session's box",
         "Puts your words in one session's box, on its Transcript tab on your own 1100, unsent. "
         "It moves nothing I see. "
         "Call it on my word to send, with the message shown in the same reply, or once I agree to a message "
         "you brought. "
         "I press Send myself. Never sends, never presses Return.",
         {"session": SESSION, "text": TEXT("The whole message, written as me: I, never my name.")},
         ["session", "text"], reads=False),
    tool("answer_item", "Answer a wave item",
         "Agree, or my feedback, on one item of a session's wave waiting on me, as its button on 1100's "
         "Clarify tab saves it. Only on my ruling: agree, my own words, or the copy you showed when I take it. "
         "I press Send myself.",
         {"session": SESSION, "item": TEXT("The item's number, like 12."),
          "answer": {"type": "string", "enum": ["agree", "feedback"]},
          "text": TEXT("With feedback, my whole feedback, written as me.")},
         ["session", "item", "answer"], reads=False),
]

# The order the Claude app lists them in, each title wearing its number.
# The first READ_ONLY are marked read-only: I want every tool I always allow
# in the app's first group, its read-only one. show_page, draft_reply and
# mark_library_review write, but none of them sends anything to a session.
ORDER = ["read_rules", "list_sessions", "read_session", "read_session_files", "read_file", "list_folder",
         "read_wave", "read_agenda", "read_system", "read_skills", "read_launch", "read_explanation",
         "read_library", "search_library", "read_word", "read_graph", "show_page", "draft_reply",
         "mark_library_review",
         "write_launch", "launch_rows", "stop_session", "set_system", "answer_item"]
READ_ONLY = 19


def numbered(t: dict, n: int) -> dict:
    """Tool t as the app lists it, number n: its title numbered, its group's hints.
    Two digits, "01", so the app's sort by title keeps my order: "2" sorts after "19"."""
    reads = n <= READ_ONLY
    marks = {k: v for k, v in t["annotations"].items() if k != "destructiveHint"}
    return {**t, "annotations": {**marks, "title": f"{n:02d} {marks['title']}", "readOnlyHint": reads,
                                 **({} if reads else {"destructiveHint": False})}}


TOOLS = [numbered(next(t for t in DEFINED if t["name"] == name), n) for n, name in enumerate(ORDER, 1)]

# What each tool above takes, by argument: get(k) is one argument as text.
PLAIN = {
    "read_system": lambda get: system(get("part")),
    "set_system": lambda get: setting(get("setting"), get("value"), get("account"), get("engine")),
    "list_folder": lambda get: folder(get("path"), get("start"), get("count")),
    "read_file": lambda get: filed(get("path"), get("start"), get("lines")),
    "read_session_files": lambda get: session_files(f"{int(s):02d}" if (s := get("session")).isdigit() else s,
                                                     get("path"), get("start"), get("count")),
    "read_library": lambda get: library(get("at"), get("start"), get("count")),
    "search_library": lambda get: library_found(get("query"), get("start"), get("count")),
    "read_word": lambda get: worded(get("slug")),
    "read_graph": lambda get: graphed(get("slug")),
    "mark_library_review": lambda get: library_marked(get("at"), get("to")),
    "read_skills": lambda get: skilled(get("query"), get("family"), get("start"), get("count")),
    "write_launch": lambda get: written(get("row"), get("name"), get("message"), get("number"), get("account"),
                                        get("model"), get("effort"), get("self_drive"), get("remove"), get("near"), get("side"),
                                        get("clone")),
}
SESSIONED = {
    "read_explanation": lambda nn, get: explained(nn, get("name"), get("section")),
    "draft_reply": lambda nn, get: drafted(nn, get("text")),
    "answer_item": lambda nn, get: answered_item(nn, get("item"), get("answer"), get("text")),
    "read_launch": lambda nn, get: launch_rows(nn),
    "launch_rows": lambda nn, get: launched_rows(nn),
}

# Every press a person can make on 1100 or 1400, as (page, act or field),
# and the door's tool that covers it. app-door-test.py reads each
# page's take() and fails on a press missing here or in DISPLAY_ONLY.
PRESSES = {
    # A launch page, launch-page.py: its rows saved, as the app chat writes
    # its own on mine, or Launch, which on mine launches only those rows.
    ("launch", "rows"): "write_launch",
    ("launch", "launch"): "launch_rows",
    # The library, library-page.py: a word's or a graph's review button.
    ("library", "review"): "mark_library_review",
    # The system page, sessions-dashboard.py's take() at /: its fields.
    ("system", "order"): "set_system",
    ("system", "effort"): "set_system",
    ("system", "model"): "set_system",
    ("system", "own"): "set_system",
    ("system", "engine"): "set_system",
    ("system", "threshold"): "set_system",
    ("system", "wrapup"): "set_system",
    # The app chat no longer presses these.
    ("transcript", "send"): None, ("transcript", "hand"): None, ("transcript", "stop"): None,
    ("transcript", "answer"): None, ("transcript", "mode"): None, ("transcript", "close"): None,
    ("transcript", "advise"): None,
    ("advisor", "type"): None, ("advisor", "send"): None, ("advisor", "follow"): None,
    ("advisor", "unfollow"): None, ("advisor", "drive"): None, ("advisor", "undrive"): None,
    # The Clarify tab, clarify-page.py: an item's Agree, or its feedback.
    ("clarify", "agree"): "answer_item", ("clarify", "feedback"): "answer_item",
    ("clarify", "send"): None, ("clarify", "propose"): None, ("clarify", "fix"): None,
    ("assistant", "auto"): None, ("assistant", "answers"): None, ("assistant", "type"): None,
    ("assistant", "drive"): None, ("assistant", "stage"): None, ("assistant", "plan"): None,
    ("assistant", "pause"): None, ("assistant", "resume"): None, ("assistant", "paste"): None,
    ("handover", "press"): None, ("jury", "plan"): None, ("jury", "launch"): None,
    ("agenda", "start"): None, ("system", "act"): None, ("prototype", "send"): None,
    ("teams", "set"): None,
}
# Every page 1100 and 1400 draw, by its tab kind or rail tool, and the door's
# tool that reads what it shows, None where no tool reads it any more.
# app-door-test.py reads page.TAB_KINDS and show.py's TOOLS and KINDS, and
# fails on a page missing here.
READS = {
    "transcript": "read_session", "handover": "read_session", "clarify": "read_wave", "assistant": None,
    "jury": None, "launch": "read_launch", "prototype": None,
    "explanation": "read_explanation", "walk": None, "shots": None, "teams": None,
    "skills": "read_skills", "system": "read_system", "agenda": "read_agenda", "prototypes": None,
    "files": "read_session_files", "library": "read_library",
}
# Presses the door skips: each only keeps something on this Mac or the phone.
DISPLAY_ONLY = {
    ("push", "subscribe"),  # the phone's buzz subscription, posted by home
    ("explanation", "download"),  # Download all, a zip saved on this Mac
    ("app", "held"),  # the app home saying it holds my cursor, posted by home
    ("app", "taken"),  # Copy on the panel's line, a copy on this Mac
}
# The Claude app gives up on a tool call still unanswered at 30 seconds, so
# no tool here waits. Nothing ever types into the app.
VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]


def call(name: str, args: dict) -> tuple:
    """One tool call: (words, failed). Every call is logged. A call made on
    rules older than app-rules.md is refused until read_rules; an answer
    made after the tools changed says so, once."""
    if door.shut():
        return "The door is shut. Open it with app-door.py open.", True
    nn = str(args.get("session", "")).strip()
    nn = f"{int(nn):02d}" if nn.isdigit() else nn
    # A false boolean stays "false", so self_drive false turns self-drive off.
    get = lambda k: "false" if args.get(k) is False else str(args.get(k) or "").strip()
    try:
        if name == "read_rules":
            with open(RULES, "rb") as f:
                data = f.read()
            mark_read(rules=fingerprint(data))
            status, words, nn = 200, data.decode("utf-8"), ""
        elif last_read().get("rules") != rules_now():
            status, words = 409, "My rules changed since you read them. Call read_rules, then make this call again."
        elif name == "list_sessions":
            status, words, nn = 200, home(), ""
        elif name == "show_page":
            # The door cannot tell two chats apart, so each names its own view.
            view = show.viewed(get("view"))
            place, why = ("", show.NO_VIEW) if not view else place_of(get("target"), get("at")) if get("at") else ("", "")
            said = why or show.show(get("target"), place, view=view)
            said += f" It opens {get('at')}." if place and said.startswith("1100 shows") else ""
            said += f" {open_twice(view)}".rstrip() if said.startswith("1100 shows") else ""
            status, words, nn = (200 if said.startswith("1100 shows") else 409), said, ""
        elif name == "read_agenda":
            status, words, nn = *agended(get("query"), get("item"), get("topic"), get("order"),
                                         get("start"), get("count")), ""
        elif name in PLAIN:
            status, words, nn = *PLAIN[name](get), ""
        elif name not in ("read_session", "stop_session", "read_wave", *SESSIONED):
            return f"No tool {name!r}.", True
        elif not NN.fullmatch(nn):
            status, words = 409, "Name the session by its two digits."
        elif name in SESSIONED:
            status, words = SESSIONED[name](nn, get)
        elif name == "read_session":
            status, words = last(nn, get("turn"), get("start"), get("count"))
        elif name == "stop_session":
            status, words = reaped(nn)
        else:
            status, words = wave(nn, get("wave"), get("item"))
    except Exception as e:
        status, words = 500, f"The door failed: {e}"
    door.log("app", name, nn, "" if status == 200 else words)
    words = words.strip() or "Done."
    if (seen := last_read()).get("tools") != (now := tools_now()) and seen.get("told") != now:
        mark_read(told=now)
        words += "\n\nMy tools changed since this chat began. Quit and reopen the Claude app to get them."
    return words, status != 200


def answer(msg) -> dict:
    """One JSON-RPC message's answer, or None for a notification."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Not a JSON-RPC message."}}
    if "id" not in msg:
        return None
    method, params, mid = msg.get("method"), msg.get("params") or {}, msg["id"]
    ok = lambda result: {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "initialize":
        asked_for = params.get("protocolVersion")
        return ok({"protocolVersion": asked_for if asked_for in VERSIONS else VERSIONS[1],
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": {"name": SLUG + "-sessions", "title": f"{project.NAME} sessions", "version": "11"}})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        # Logged, so a stale tool list in the Claude app shows as no fetch here.
        door.log("app", "tools/list", "", "")
        mark_read(tools=tools_now())
        return ok({"tools": TOOLS})
    if method == "tools/call":
        words, failed = call(str(params.get("name", "")), params.get("arguments") or {})
        return ok({"content": [{"type": "text", "text": words}], "isError": failed})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"No method {method!r}."}}


def stdio() -> None:
    """The desktop extension's door: one JSON-RPC message per line in, its
    answer per line out. Only the app holds the pipe, so no key. A stray
    print goes to stderr, never into the pipe."""
    out, sys.stdout = sys.stdout, sys.stderr
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            got = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Not JSON."}}
        else:
            got = [a for a in map(answer, msg) if a] if isinstance(msg, list) else answer(msg)
        if got:
            out.write(json.dumps(got) + "\n")
            out.flush()


def from_the_app() -> bool:
    """Whether the Claude app's extension started this door: its parent is
    the app's own helper, running the installed starter."""
    r = subprocess.run(["/bin/ps", "-o", "command=", "-p", str(os.getppid())], capture_output=True, text=True)
    return "/Applications/Claude.app/" in r.stdout and "/Claude Extensions/" in r.stdout


def trial_stdio(record: str) -> None:
    """The door on stand-ins, for a test chat: lib/trial.py's made-up
    sessions, and every act kept in `record`, never pressed on 1100, never
    ending a process. Its log and its read marks stay in `record` too, and
    so do calls to the Claude app's own tools, stood in for here."""
    import trial
    os.makedirs(record, exist_ok=True)
    acts = os.path.join(record, "acts.jsonl")

    def kept(kind: str, **what) -> None:
        with open(acts, "a") as f:
            f.write(json.dumps({"act": kind, **what}) + "\n")

    def press(path, form):
        kept("press", path=path, form=form)
        return 200, ""

    def reap(nn):
        kept("stop", session=nn)
        return 200, f"Session {nn} ended. Its folder was deleted."

    def mark(said, to):
        kept("review", at=said, to=to)
        return 200, f"{said} marked {to}."

    # The Claude app's own tools, stood in for: those my rules allow, and those
    # they took away, so a call to one shows. Each call kept, a tap answered
    # as TRIAL_TAP says, Agree by default.
    app_tools = {name: {"name": name, "description": f"Stand-in for the Claude app's own {name}: {what}",
                        "inputSchema": {"type": "object", "additionalProperties": True}}
                 for name, what in (("show_widget", "draws a chart or a picture in our chat."),
                                    ("send_later", "sends a message back into our chat later."),
                                    ("PushNotification", "buzzes my phone."),
                                    ("AskUserQuestion", "shows options I tap, and returns my tap."),
                                    ("SendUserMessage", "shows me a message whole in our chat, mid-turn."))}
    real_call = call

    def called(name, args):
        if name not in app_tools:
            return real_call(name, args)
        kept(name, input=args)
        tap = os.environ.get("TRIAL_TAP", "Agree")
        return (f"I tapped: {tap}." if name == "AskUserQuestion" else "Done."), False

    me = sys.modules[__name__]
    stood = [(show, "FOLDER", record), (show, "ORDER", os.path.join(record, "order.json")),
             (door, "LOG", os.path.join(record, "log.jsonl")), (me, "READ", os.path.join(record, "read.json")),
             (me, "pressed", press), (me, "fetched", lambda path: ""),
             (me, "reaped", reap), (me, "library_marked", mark),
             (me, "TOOLS", TOOLS + list(app_tools.values())), (me, "call", called)]
    with trial.world() as w, contextlib.ExitStack() as stack:
        for module, name, stand_in in stood:
            stack.enter_context(mock.patch.object(module, name, stand_in))
        # A test's own wave for stand-in 05, in place of the made-up one:
        # TRIAL_WAVE names a JSON list of items, as clarify-page.py holds them.
        if os.environ.get("TRIAL_WAVE"):
            with open(os.environ["TRIAL_WAVE"]) as f:
                w.put("05", "waves/wave-1.md", page.tool("clarify-page").dump(1, {"sent": "", "then": ""}, json.load(f)))
        # Where each stand-in's transcript sits, so a test can act as me
        # between two turns, unsaid: tools/test-chat.py --sent.
        with open(os.path.join(record, "world.json"), "w") as f:
            json.dump({nn: r["transcript"] for nn, r in w.held.items()}, f)
        stdio()


def extension() -> str:
    """The .mcpb the desktop app installs: a manifest, and a starter that
    runs this file's stdio on this Mac's python3. Returns its path."""
    slug = SLUG + "-sessions"
    manifest = {
        "manifest_version": "0.3", "name": slug, "display_name": f"{project.NAME} sessions",
        "version": "1.0.0", "description": f"{project.NAME}'s sessions on this Mac, through its app door.",
        "author": {"name": project.NAME},
        "server": {"type": "python", "entry_point": "server/main.py",
                   "mcp_config": {"command": BREW, "args": ["${__dirname}/server/main.py"], "env": {}}},
        "tools": [{"name": t["name"], "description": t["description"]} for t in TOOLS],
        "compatibility": {"platforms": ["darwin"], "runtimes": {"python": ">=3.10"}},
    }
    starter = ("import os, sys\n"
               f"DOOR = {os.path.abspath(__file__)!r}\n"
               "os.execv(sys.executable, [sys.executable, DOOR, \"stdio\"])\n")
    path = os.path.join(door.STATE, slug + ".mcpb")
    os.makedirs(door.STATE, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=1))
        z.writestr("server/main.py", starter)
    return path


def install() -> None:
    if not BREW or subprocess.run([BREW, "-c", "import sys; sys.exit(sys.version_info < (3, 10))"]).returncode:
        print(f"Refused: no python3 of 3.10 or newer on the path ({BREW or 'none'}). Nothing was installed.")
        return
    os.makedirs(door.STATE, exist_ok=True)
    with open(PLIST, "wb") as f:
        f.write(plistlib.dumps({"Label": LABEL, "ProgramArguments": [BREW, os.path.abspath(__file__), "keep"],
                                "RunAtLoad": True, "KeepAlive": True, "ProcessType": "Interactive",
                                "ThrottleInterval": 10, "WorkingDirectory": door.ROOT,
                                "StandardOutPath": OUT, "StandardErrorPath": OUT}))
    domain = f"gui/{os.getuid()}"
    subprocess.run(["/bin/launchctl", "bootout", f"{domain}/{LABEL}"], capture_output=True)
    for _ in range(10):
        r = subprocess.run(["/bin/launchctl", "bootstrap", domain, PLIST], capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(0.5)
    print(r.stderr.strip() or f"{LABEL} handed to launchd. Its log: {OUT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["stdio", "trial", "extension", "keep", "install", "open", "shut", "log"])
    ap.add_argument("what", nargs="?", default="")
    a = ap.parse_args()
    if a.verb == "stdio":
        # A test never reaches a real session: anything but the app's own
        # extension gets stand-ins, through tools/test-chat.py.
        if not from_the_app():
            sys.exit("Refused: only the Claude app's extension opens the door on real sessions. "
                     "A test chat runs on stand-ins: python3 .claude/tools/test-chat.py \"<your words>\".")
        stdio()
    elif a.verb == "trial":
        trial_stdio(a.what or tempfile.mkdtemp(prefix="door-trial-"))
    elif a.verb == "extension":
        print(f"The desktop extension is packed: {extension()}")
    elif a.verb == "keep":
        # 1100 back within ten seconds of dying or of freezing, and a minute
        # after a stop on purpose: lib/serve.py's keep().
        serve.keep("sessions-dashboard", serve.PORT, DASHBOARD)
    elif a.verb in ("open", "shut"):
        door.switch(a.verb == "open")
        print(f"The door is {a.verb}.")
    elif a.verb == "log":
        try:
            with open(door.LOG) as f:
                lines = f.readlines()[-(int(a.what) if a.what.isdigit() else 20):]
        except OSError:
            lines = []
        for line in lines:
            e = json.loads(line)
            print(f"{e['at']}  {e['bot']:<9} {e['act']:<20} {e['session']:<3} {e['said']}")
    else:
        install()


if __name__ == "__main__":
    main()
