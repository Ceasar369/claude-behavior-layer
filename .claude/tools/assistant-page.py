#!/usr/bin/env python3
"""assistant-page.py — the assistant's page, drawn by 1100 at /p/assistant/NN.

An assistant runs other sessions for me, stage by stage. Its plan is one
file in its own folder, stages.json: stages A, B, C, in the order they
run, or, in an open plan, names grouping missions, and in each its
missions, A1, A2. Its latest answer for a mission is
one file beside it, answers/A1.md.

The rail lists the missions by id, each stage's letter above its own, a
thin line between two stages. Each id wears its session's live state, as
1100 reads it.

A session in a stage reads number first, then mission: 21-B1. A mission
with no session yet reads by its id alone.

A stage, opened by its letter or its heading, heads with its name, its
count, then Send this stage and Drive the stage, save the active stage,
whose two sit in the team bar. Its finished missions fold into one lighter
line under its name, and a click unfolds them. Its live missions sit side
by side below, one card each: the tag and the state, the name, what it
asks or its latest answer in brief, then its buttons at the foot. An
answer in brief is its headline, its moves, and a chip per item, green
agree, red feedback. A chip opens its item under the mission. An answer
to a wave I have since sent is spent, and shows nowhere, bar its words
still to send to another session. So is an answer whose move's words each
reached their session.

A mission, opened by its card's name or its id, shows its way back to its
stage, its tag and state, the assistant's latest answer for it, its
buttons, then the whole mission. A mission whose session stopped reads
completed, and carries no button, bar its words still to send to another
session.

While a mission's session has a wave waiting on me, its card and its
card's name open that wave's Clarify tab in 1100's home instead, and so
does its Waiting on you. Its id still opens the mission.

The whole plan is a row per stage, a card per mission. Its finished
stages fold into one line above the rest. An open plan's stage folds there
only once I close it, and wears Open until then. Main opens on the current
stage, the first with a mission not stopped.

The top rail is the team bar: the page's tools, one row, each button
small, its colour by where it goes. The plan's come first: See the whole
plan, which brings it back, then lib/drive.py's two, Drive the whole plan
and play/pause, then Auto-send, on or off. The active stage's follow,
only while one of its missions started and not every one stopped: the
stage's name, Send this stage and Drive the stage. Between stages they
are gone. While the stage's own view shows, its heading names it, and
the bar's name goes. On my phone the bar packs as tight as it goes: no label but
the stage's, no icon on a worded button. Auto-send's pills sit beside
See the whole plan, the drive's two under them, and the stage's on a
raised band below.

While the plan is driven, each stage row shows its three moments, kick
off, work and close, and the first stage not kicked off holds Launch
page. An open plan's rows show neither.

Auto-send hands my assistant a session waiting on me. A mission's session
whose number turns from green to red, its clarify wave not sent, has its
assistant typed the line its card's Send types: /assistant-answer, the
mission's id and its name. The assistant drafts that wave's answers. Once
per wave. One whose need is check, its work reported done, has it typed
/assistant-check and the mission's id instead. The assistant checks that
work. Once per finish. A command typed while it works waits for its turn's
end. A session a drive holds, running or paused, is the drive's, and gets
none. Nor does
one holding a prototype whose winner I have not locked in yet. Auto-send
is on until I turn it off, and its pills say which: auto-send.json in the
assistant's folder, {"on": false} while off. 1100 runs it from its colour
watch, page.reddened's: sent().

The page draws again whenever anything it shows moves. The view I left,
each fold I opened and where I scrolled stay.

A live mission's buttons are Type, Send and Drive, one width each, in
that order. Type types /assistant-answer, the mission's id and its name
into the assistant's pane, and never sends, so I can add my own words
first. Send, in gold, types the same line and sends it; after Type, it
presses Return alone, so the line goes once, with my words. While the
mission's session waits on me with a wave whose items the assistant has
answered, the wave's title on its card carries Send answers to 21, naming
that session. It takes each answer through the clarify page's own
Take, then presses its Send. Drive, in gold, sends
/1-assistant drive and the mission's id, or "Drive A2." while the
assistant works. Drive the stage sends the stage's letter the same way.
Send this stage, in gold, sends /1-assistant and the stage's letter: the
assistant sees to each of its sessions whose need is answer, send, waiting
on you or check.

A button's line types before its press is answered. A pane gone, Claude
gone from it, or a dialog waiting there, the button says so, and nothing
is typed.

Once the assistant has taken a hand-off, its Drive shows it: green, and a
check. Taken means the drive line reached it, as a prompt or as a
message queued mid-turn, after the mission's session claimed. A stage's
Drive shows it once every live session of the stage is taken.

A move's words, written by the assistant for one session, carry Copy,
Type and Send to 43 above them. The last two type the words into the
pane of the session its move names, so I never paste: "Send to session
43." is 43's. Its send button wears its receiver's colour.

A move's words wait for my send while the session they go to is idle,
and has not heard from me since the answer was written. Sent, they start
that session's next turn: the wait ends, and the answer is spent. Words
for another session outlive what hides the rest of the answer: its own
session's stop, a newer ask, a wave since sent. They stay on the card,
under Still to send, until the session they go to hears them, while it
is the session they were written for.

The page waits on me in 1100's home while a live mission needs my hand,
and opens once on its stage, whatever view I left: due(). Its words wait
for my send. Or it needs the assistant to answer or check it, and
auto-send will not hand it over: a question outside a wave, which
auto-send never hands, or a finish to check while auto-send is off. Or
its session is gone, which holds its stage. A wave waiting on me is its
session's own Clarify, never this page's. A mission a drive holds never
waits on me: the drive answers it.

What a session asked after the answer on the page shows in the answer's
place, on its card and under its heading. A newer wave still waiting on
me shows its items, grey. Otherwise, a turn of the session's own after the
answer's bookmark, while it waits on me, shows its move. Both are read from
disk, so no session spends a token on it.

states reads each launched session's finish as lib/finish.py reads it,
since its answer's bookmark, and prints the need it makes. Gone comes
first, even before a wave: an answer to it never sends. A wave, or a
move asking me anything, needs an answer. A move proposing the session's
own stop, or one handing the assistant a report, needs a check. A Wait
prints working. Any other finish prints its own word, finish.word's. One that finished
nothing since its answer prints working or idle, and a mission with no
session prints not started or stopped. An idle session with its answer
unsent needs its send, once that answer holds a verdict of the assistant's
own and its wave no draft of mine. A line moving an item to chat is no
verdict. Otherwise it prints waiting on you: the wave waits for my Send.

A helper a mission's session started, through helper-session, shows under
that mission: a line on its card, and one under its heading, each with
its own live state.

    {"stages": [
      {"name": "Stage B",
       "missions": [
         {"id": "B1", "name": "machine proposals",
          "file": ".claude/state/sessions/07/missions/B1-machine-proposals.md",
          "queued": "2026-09-23T15:40:12",
          "session": "21", "title": "21-machine-proposals"}]}]}

A mission's name is one to three words, and its launch row carries them,
so its session is named NN-machine-proposals. Queue stamps each mission
just before its launch. The one session with that name, claimed since, is
its own, and its claim writes its number and title into the plan. A number
is handed out again once its session closes, so only a running session
under that title is the mission's own.

The page stores nothing. Every request reads the folder, and finds a
launched mission's session the way the claim does. The match is
lib/plans.py's, never a copy. 1100 imports this file for render and take,
and serves them; nothing here runs a server.

  assistant-page.py queue  07 A1 A2    they launch next
  assistant-page.py states 07          each mission's id, need and session

Both take the assistant's number. An older --port 1307 still names 07.

Queue refuses while a stage before them holds a gone session: its process
ended with no stop, and its folder stands, so its stage never reads done.
It names each, with both ways out: keep it, then /reaper it, or resume it.
An open plan's stages wait on none before them, so its queue never refuses.

The shell and the colours are shared. See .claude/lib/.
It keeps the page rules atop .claude/lib/page.py.
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import drive  # noqa: E402
import finish  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import transcripts  # noqa: E402

# A session's waves are read the clarify page's own way, never a copy.
clarify = page.tool("clarify-page")

# Auto-send wears the launch page's own pills: its .pills rules alone.
launcher = page.tool("launch-page")
PILLS = page.rules(launcher.CSS, ".pills")

# Auto-send's switch, in the assistant's folder. No file is on.
AUTO = "auto-send.json"
# Each (session, wave) auto-send already handed its assistant.
SENT: set = set()

CODE = re.compile(r"`([^`]+)`")
STAMP = "%Y-%m-%dT%H:%M:%S"  # the registry's own, for "claimed"
ANSWERED = re.compile(r"# Wave (\d+)")
BOOKMARK = re.compile(r"read to (\S+)")
# A hand-off, as the drive button types it: "/1-assistant drive A2", or
# "Drive A2." while the assistant works. It names a mission or a stage.
# Older transcripts hold /3-assistant, the family's number before.
DRIVE = re.compile(r"^(?:/[13]-assistant drive|Drive) ([A-Z]\d*)\b")


def helpers(m: dict, held: dict) -> list:
    """The helper sessions a mission's session started, as (number, record).

    helper-session names each "<id> helper <words>", so its title reads
    NN-c1-helper-frontend. Only one not yet stopped has a record. Its
    launch writes who started it into that record, `by`, so another team's
    helper for a mission of the same id never shows here.
    """
    if not m.get("session"):
        return []
    lead = f"{registry.kebab(m['id'])}-helper"
    return sorted((n, r) for n, r in held.items()
                  if r.get("title", "")[3:].startswith(lead) and n != m["session"]
                  and r.get("by", m["session"]) == m["session"])


def state(m: dict, held: dict, live: dict, open_ids) -> tuple:
    """A mission's word, its colour, and its look: 1100's own, once it launches.

    Before that, it is not started. Stopped with the skill, its session's
    folder is gone, and its number may run another session: completed, and
    a dashed grey bar, so it sits in the background.
    """
    if not m.get("session"):
        return "not started", "grey", ""
    mine = held.get(m["session"])
    rec = live.get((mine or {}).get("session_id"))
    if not mine or m.get("title") not in (None, mine.get("title"), (rec or {}).get("name")):
        return "completed", "grey", " done"
    word, colour, look = page.live_state(rec, mine, open_ids)
    return word, colour, f" {look}" if look else ""


def stranded(nn: str, p: dict, ids: list) -> list:
    """Each mission of a stage before the first holding these ids whose
    session is gone: its process ended with no stop, and its folder stands.

    Until a stop or /reaper deletes that folder, the mission never reads
    completed, its stage never reads done, and main stays on it while the
    next stage runs. Queue refuses while one stands. An open plan's stages
    wait on none before them, so none is stranded there.
    """
    if plans.opened(p):
        return []
    held, live = registry.entries(), registry.claude_records()
    out = []
    for s in p.get("stages", []):
        ms = [{**m, **plans.found(m, held, nn)} for m in s.get("missions", [])]
        if any(m["id"] in ids for m in ms):
            break
        out += [m for m in ms if state(m, held, live, None)[0] == "gone"]
    return out


def named(m: dict) -> str:
    """The mission's own name until it launches, then its session's: 13-web-app."""
    return m.get("title") or m["name"]


def short(m: dict) -> str:
    """A card's name. Its tag already reads its number, so the name drops it."""
    return re.sub(r"^\d{2}-", "", m.get("title") or "") or m["name"]


def tag(m: dict) -> str:
    """Number first, then mission: 21-B1. A mission with no session reads B1."""
    return f"{m['session']}-{m['id']}" if m.get("session") else m["id"]


def typed(nn: str, k: str) -> str:
    """The line Type leaves in the assistant's prompt: /assistant-answer A2 12-sign-in.

    It ends on a space, so my own words follow straight on.
    """
    m = plans.mission(nn, k)
    return f"/assistant-answer {k} {named({**m, **plans.found(m, registry.entries(), nn)})} " if m else ""


def handed(nn: str, k: str) -> str:
    """The line the drive button sends the assistant: /1-assistant drive A2.

    k is one mission's id, or one stage's letter, as the plan holds them.
    A command typed into a working session waits until its turn ends, while
    plain words land at its next step. An assistant already working, as
    one driving other sessions, takes plain words: "Drive A2."
    """
    stages = plans.plan(nn).get("stages", [])
    known = {chr(65 + i) for i in range(len(stages))} | {
        m["id"] for s in stages for m in s.get("missions", [])}
    return drive.handed(nn, k) if k in known else ""


# Each transcript's hand-offs, read once and then only as it grows: its
# path, then how far it was read and every (key, stamp) found in it.
DRIVES: dict = {}


def drives(path: str) -> list:
    """Every hand-off an assistant's transcript received, as (key, stamp).

    A prompt I sent counts, and so does a message queued while it worked.
    A line still waiting in its queue is not in the transcript yet.
    """
    try:
        size = os.path.getsize(path)
    except OSError:
        return []
    at, found = DRIVES.get(path, (0, []))
    if size < at:
        at, found = 0, []
    with open(path, "rb") as f:
        f.seek(at)
        data = f.read(size - at)
    end = data.rfind(b"\n") + 1
    for line in data[:end].splitlines():
        if b"rive" not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        said = transcripts.mine(d) if d.get("type") == "user" else ""
        queued = d.get("attachment") if isinstance(d.get("attachment"), dict) else {}
        if queued.get("type") == "queued_command" and (queued.get("origin") or {}).get("kind") == "human":
            said = str(queued.get("prompt", ""))
        hit = DRIVE.match(said.strip())
        if hit:
            found.append((hit.group(1), transcripts.stamp(queued if queued.get("timestamp") else d)))
    DRIVES[path] = (at + end, found)
    return found


def taken(m: dict, letter: str, got: list, held: dict) -> bool:
    """Whether the assistant took a hand-off of this mission's session: a
    drive line naming it or its stage, after its session claimed."""
    mine = held.get(m.get("session") or "") or {}
    since = mine.get("claimed", "")
    return bool(since) and any(k in (m["id"], letter) and at >= since for k, at in got)


def aimed(nn: str, k: str, key: str) -> tuple:
    """A move's paste, found again by its key: the session it is for, and its words.

    The words come from the answer file, never from the click, so a click
    types only what the assistant wrote.
    """
    if not re.fullmatch(r"[A-Z]+\d+", k):
        return "", ""
    found = []
    answer(read(os.path.join(registry.folder(nn), "answers", f"{k}.md")), k, found)
    return next(((to, words) for to, words in found if sign(words) == key), ("", ""))


def take(nn: str, form: dict) -> str:
    """A button on the page, clicked, or Auto-send turned: its act names which.

    On a mission, the pane is the assistant's own, as it stands now. On a
    move's paste, it is the pane of the session the move names. The line
    types off 1100's draw queue, serve.Typing's, before the page is
    answered, so a pane gone is said. So is Claude gone from it, or a
    dialog waiting there, checked here first: the shell left there would
    run the line as a command, and a dialog's Return approves its first
    option. Nothing to type is said too, so no press flashes green for
    nothing.
    """
    act, k = (form.get("act") or [""])[0], (form.get("id") or [""])[0]
    to = nn
    if act == "auto":
        return switch(nn, k == "on")
    if act == "answers":
        return answers(nn, k)
    if act == "type":
        line = typed(nn, k)
    elif act == "drive":
        line = handed(nn, k)
    elif act == "stage":
        line = f"/1-assistant {k}" if re.fullmatch(r"[A-Z]", k) and ord(k) - 65 < len(
            plans.plan(nn).get("stages", [])) else ""
    elif act in (drive.PLAN, "pause", "resume"):
        line = drive.line(nn, act)
    elif act == "paste":
        to, line = aimed(nn, k, (form.get("key") or [""])[0])
    else:
        return f"This button does nothing here: {act or 'no act'}. Nothing was typed."
    send = (form.get("send") or [""])[0] == "yes"
    if not line:
        return f"Nothing to type for {k or act}: the plan or its answer changed. Reload the page."
    why, _, pane = page.typable(to, ("idle", "shell", "busy"))
    if why:
        return why
    # A Send after its Type presses Return alone: the line already sits in
    # the prompt, with any words I added.
    only = send and (form.get("only") or [""])[0] == "return"
    text = "" if only else line.rstrip() if send else line
    return serve.Typing(lambda: "" if panes.say(pane, text, enter=send) else page.gone(to))


def inline(s: str) -> str:
    return CODE.sub(r"<code>\1</code>", html.escape(s))


def sign(words: str) -> str:
    """A paste's key: the page names a paste by it, and the server finds it again."""
    return hashlib.sha1(words.encode()).hexdigest()[:12]


def answer(text: str, k: str = "", found: list | None = None) -> str:
    """An answer file, drawn. A small, closed set of lines.

    `# ` is the headline. `## ` opens one item, and a last word of agree or
    feedback becomes its chip. `- ` is a bullet. `> ` lines are one paste,
    with its own Copy button. Anything else is a line said plainly.

    A paste is a move's when the line above it reads "Send to session 43.",
    talking.md's hand-off shape, and never under an item. Copy, Type and
    Send to 43 sit above its words, and the last two type it into that
    session's pane, so I never paste. A line merely naming a session aims
    nothing, so its paste keeps Copy alone. Each move's paste lands in
    `found`, as its session and its words.
    """
    out, paste, bullets = [], [], []
    to, item = "", False

    def flush():
        if paste:
            words = "\n".join(paste)
            aim = "" if item else to
            if aim and found is not None:
                found.append((aim, words))
            if aim and k:
                out.append(f'<div class="paste to"><div class="acts">{twin(k, sign(words), aim)}</div>'
                           f'<div class="txt">{html.escape(words)}</div></div>')
            else:
                out.append('<div class="paste"><div class="txt">' + html.escape(words)
                           + '</div><button onclick="copy(this)">Copy</button></div>')
            paste.clear()
        if bullets:
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for line in text.splitlines():
        if line.startswith("> ") or line == ">":
            if bullets:
                flush()
            paste.append(line[2:])
            continue
        if line.startswith("- "):
            if paste:
                flush()
            bullets.append(line[2:])
            continue
        flush()
        if line.strip():
            says = page.SEND_TO.search(line)
            to = says.group(1) if says else ""
        if line.startswith("## "):
            head, _, verdict = line[3:].rpartition(" · ")
            chip = {"agree": ("Agree", "green"), "feedback": ("Feedback", "red")}.get(verdict)
            item = bool(chip)
            if chip:
                out.append(f'<h3>{inline(head)}<span class="chip" '
                           f'style="--c:var(--{chip[1]})">{chip[0]}</span></h3>')
            else:
                out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.startswith("# "):
            out.append(f'<p class="hl">{inline(line[2:])}</p>')
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "".join(out)


def read(path: str) -> str:
    try:
        with open(path if os.path.isabs(path) else os.path.join(registry.ROOT, path)) as f:
            return f.read()
    except OSError:
        return ""


def brief(k: str, text: str, btn: str = "") -> str:
    """An answer, as its card shows it: the headline, the moves, a chip per item.

    The headline drops its bookmark. The moves are the numbered lines and
    pastes under `## Your moves`. An older answer has none, and names its
    move in the heading over its paste. A chip is coloured by its verdict.
    It reads a wave item's number, from a title shaped "Item N", or else its
    place among the chips. Its count among the `## ` lines finds the item again.
    """
    head, moves, chips = "", [], []
    n, section, said = -1, None, False
    for line in text.splitlines():
        if line.startswith("# ") and not head:
            head = line[2:].split(" · read to ")[0]
        elif line.startswith("## "):
            n += 1
            title, _, verdict = line[3:].rpartition(" · ")
            colour = {"agree": "green", "feedback": "red"}.get(verdict)
            if colour:
                num = re.fullmatch(r"Item (\d+)", title)
                label = num.group(1) if num else str(len(chips) + 1)
                chips.append(f'<span class="chip" style="--c:var(--{colour})" '
                             f'title="{page.esc(title)} · {verdict}" '
                             f'onclick="jump(\'{k}\', {n})">{label}</span>')
                section = None
            else:
                section = line[3:].strip()
                said = section.lower() == "your moves"
        elif section and said and re.match(r"\d+\. ", line):
            moves.append(line)
        elif section and line.startswith(">"):
            if not said:
                moves.append(section)
                said = True
            moves.append(line)
    if not head:
        return '<p class="none">No answer yet.</p>'
    return (f'<div class="hlrow"><p class="hl">{inline(head)}</p>{btn}</div>' + answer("\n".join(moves), k)
            + (f'<div class="vs">{"".join(chips)}</div>' if chips else ""))


def twin(k: str, key: str, to: str) -> str:
    """A move's paste: Copy, Type, then Send to NN, coloured by its receiver, one width each."""
    copy = page.CP.replace("<button ", '<button onclick="copied(this)" ', 1)
    return (f'<span class="group">{copy}'
            f'<button class="btn" onclick="pressType(this,\'{k}\', false, \'{key}\')">Type</button>'
            f'<button class="{page.into(to)}" onclick="pressType(this,\'{k}\', true, \'{key}\')">'
            f'{page.icon("send", 11)}Send to {to}</button></span>')


def answers(nn: str, k: str) -> str:
    """Send answers, clicked on a mission whose session waits on me: the
    clarify page's own take_all, on that session's wave."""
    session = (plans.mission(nn, k) or {}).get("session") or ""
    return clarify.take_all(session) if session else ""


def acts(k: str, took: bool) -> str:
    """A live mission's buttons, at its foot: Type, Send, Drive, one width each."""
    drive = (f'<button class="btn ask{" taken" if took else ""}" title="'
             + ("The assistant took this hand-off" if took else "Hand this session to the assistant")
             + f'" onclick="pressType(this,\'{k}\', true, \'\', \'drive\')">'
             f'{page.icon("check" if took else "drive", 12)}Drive</button>')
    return (f'<div class="acts3"><button class="btn" onclick="pressType(this,\'{k}\', false, \'\')">Type</button>'
            f'<button class="btn ask" onclick="pressType(this,\'{k}\', true, \'\')">'
            f'{page.icon("send", 11)}Send</button>{drive}</div>')


def stage_acts(at: str, took: bool) -> str:
    """A stage's head, or the team bar's second row: Send this stage, then
    Drive the stage, one width."""
    return (f'<span class="group"><button class="btn ask" onclick="pressType(this,\'{at}\', true, \'\', \'stage\')">'
            f'{page.icon("send", 11)}Send this stage</button>'
            f'<button class="btn ask{" taken" if took else ""}" '
            f'onclick="pressType(this,\'{at}\', true, \'\', \'drive\')">'
            f'{page.icon("check" if took else "drive", 11)}Drive the stage</button></span>')


# ---- the team bar, and auto-send --------------------------------------------------

def auto_on(nn: str) -> bool:
    """Whether assistant NN's auto-send is on. No file, or one unread, is on."""
    try:
        with open(os.path.join(registry.folder(nn), AUTO)) as f:
            return json.load(f).get("on") is not False
    except (OSError, ValueError, AttributeError):
        return True


def switch(nn: str, on: bool) -> str:
    """Auto-send turned on or off, by its pills."""
    with open(os.path.join(registry.folder(nn), AUTO), "w") as f:
        json.dump({"on": on}, f)
        f.write("\n")
    return ""


def bar(nn: str, driven: dict, active: tuple) -> str:
    """The team bar: the plan's tools, then the active stage's. `active` is
    the active stage, as (letter, its name already escaped, taken), or ()
    between stages."""
    on = auto_on(nn)
    pill = lambda v, word, tone: (f'<button type="button" data-v="{v}" class="{"on" if (v == "on") == on else ""}" '
                                  f'style="--g:var(--{tone})" onclick="autoSend(this)">{word}</button>')
    row = ('<div class="tb-row"><h2 class="tb-label">Plan</h2>'
           '<button class="btn" onclick="tab(\'all\')">See the whole plan</button>'
           + drive.controls(nn, driven)
           + '<span class="cut"></span><h2 class="tb-label">Auto-send</h2>'
           f'<span class="pills" id="auto" title="On: a session of this team waiting on you, its clarify page '
           f'not sent or its work reported done, is handed to your assistant. One holding a prototype you have '
           f'not locked in never is">'
           f'{pill("on", "On", "green")}{pill("off", "Off", "dim")}</span></div>')
    if active:
        at, name, took = active
        row += f'<div class="tb-row tb-stage" data-at="{at}"><h2>{name}</h2>{stage_acts(at, took)}</div>'
    return row


def sent(n: str, *_) -> None:
    """Session N just turned red. While it runs a mission, its assistant
    takes it: its newest wave waiting on me, the assistant drafts that
    wave's answers, once per wave; otherwise its need a check, the
    assistant checks its work, once per finish. Each only with auto-send
    on, no drive holding it, the assistant's pane there with no dialog
    waiting in it, and no prototype held whose winner I have not locked in
    yet."""
    subject = prototypes.subject_of(n)
    if subject and not prototypes.winner(subject):
        return
    held = registry.entries()
    owner = plans.owners(held).get(n)
    if not owner:
        return
    nn, k = owner
    if not auto_on(nn):
        return
    wave, _, head, _ = clarify.newest(n)
    if wave and not head.get("sent"):
        once, line = (n, wave), typed(nn, k).rstrip()
    elif need(nn, {"id": k, "session": n}, held) == "check":
        once, line = (n, finish.read(n)["at"]), f"/assistant-check {k}"
    else:
        return
    if once in SENT:
        return
    stages = plans.plan(nn).get("stages", [])
    letter = next((chr(65 + i) for i, s in enumerate(stages)
                   if any(m.get("id") == k for m in s.get("missions", []))), "")
    d = drive.read(nn)
    if drive.driving(d) and {drive.PLAN, letter, k} & set(drive.words(d)):
        return
    why, _, pane = page.typable(nn, ("idle", "shell", "busy"))
    if why:
        return
    # A line iTerm never typed counts for nothing: the session's next turn
    # to red tries it again.
    if panes.say(pane, line):
        SENT.add(once)


def asks(m: dict, mine: dict, word: str, got: str) -> dict:
    """What a mission's session asked after the answer shown, read from disk.

    The answer names the wave it answered, and the bookmark it read to. A
    newer wave still waiting on me wins: its number and items. Otherwise,
    while the session waits on me, its own last turn after the bookmark:
    when, and its move, as transcripts.last_said reads them. Nothing asked
    since gives {}.

    The page draws it, and states reads a newer wave here too.
    """
    wave, _, head, items = clarify.newest(m["session"])
    answered = ANSWERED.match(got)
    if wave and not head.get("sent") and wave > (int(answered.group(1)) if answered else 0):
        return {"wave": wave, "items": items}
    if word not in ("idle", "waiting"):
        return {}
    said, at, move = transcripts.last_said(mine.get("transcript", ""))
    when = transcripts.moment(at)
    if not said or not when:
        return {}
    kept = BOOKMARK.search(got.split("\n", 1)[0])
    if kept and transcripts.stamp(at) <= kept.group(1):
        return {}
    return {"when": when.astimezone(), "move": move}


def answered_wave(m: dict, text: str) -> tuple:
    """The wave an answer names, as (head, items). None found gives ({}, [])."""
    answered = ANSWERED.match(text)
    path = dict(clarify.waves(m["session"])).get(int(answered.group(1))) if answered else ""
    return clarify.parse(read(path)) if path else ({}, [])


def spent(m: dict, text: str) -> bool:
    """An answer to a wave I have since sent. Nothing waits on it any more."""
    return bool(answered_wave(m, text)[0].get("sent"))


def verdicts(text: str) -> list:
    """An answer's items, as (verdict, words): each `## ` line's last word,
    and its `> ` lines, as one line."""
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            out.append((line.rpartition(" · ")[2], []))
        elif out and (line.startswith("> ") or line == ">"):
            out[-1][1].append(line[2:])
    return [(verdict, " ".join(" ".join(words).split())) for verdict, words in out]


def sendable(m: dict, text: str) -> bool:
    """An answer the assistant sends itself: a verdict of its own, on a wave
    holding no draft of mine. Moving an item to chat answers nothing."""
    head, items = answered_wave(m, text)
    if not head or any(clarify.answered(it) for it in items):
        return False
    return any(verdict == "agree" or (verdict == "feedback" and words != clarify.MOVED)
               for verdict, words in verdicts(text))


def need(nn: str, m: dict, held: dict) -> str:
    """A launched session's need: answer, send, waiting on you, check, or its
    finish's own word.

    lib/finish.py reads its finish since its answer's bookmark. Gone comes
    first: an answer to it never sends, so even a wave waiting on me waits
    behind it. Otherwise a newer wave waiting on me needs an answer. Then
    asking needs an answer, done a check. Any other finish prints its own
    word, finish.word's. An idle session with its answer
    unsent needs its send, when the assistant may send it. Otherwise it is
    waiting on you.
    """
    got = read(os.path.join(registry.folder(nn), "answers", f"{m['id']}.md"))
    kept = BOOKMARK.search(got.split("\n", 1)[0])
    f = finish.read(m["session"], kept.group(1) if kept else "")
    if f["kind"] == "gone":
        return "gone"
    if "wave" in asks(m, held.get(m["session"]) or {}, "", got):
        return "answer"
    word = {"asking": "answer", "done": "check"}.get(f["kind"], finish.word(f))
    if word != "idle" or not ANSWERED.match(got) or spent(m, got):
        return word
    return "send" if sendable(m, got) else "waiting on you"


# Each move's words heard, by their session's transcript and when they
# were written. A line of mine stays in its transcript, so heard is final.
HEARD: set = set()
# Each move's words not heard yet, the same way: how far its transcript
# was read, to a line's end. A draw reads only what was written since.
UNHEARD: dict = {}


def moved(to: str, written: float, held: dict) -> bool:
    """Whether session `to` heard from me after `written`. Its transcript is
    read back as far as `written` once: from its tail, or whole when the
    tail starts later. After that, only what it gained is read."""
    path = (held.get(to) or {}).get("transcript", "")
    if (path, written) in HEARD:
        return True
    try:
        size = os.path.getsize(path)
    except OSError:
        return False
    at = UNHEARD.get((path, written))
    if at is None:
        first = next((w for w in map(transcripts.moment, registry.tail(path)) if w), None)
        at = 0 if first and first.timestamp() > written else max(0, size - registry.TAIL)
    at = 0 if at > size else at
    with open(path, "rb") as f:
        f.seek(at)
        data = f.read(size - at)
    end = data.rfind(b"\n") + 1
    for line in data[:end].splitlines():
        if b'"user"' not in line and b'"attachment"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        when = transcripts.moment(d) if isinstance(d, dict) else None
        if (when and when.timestamp() > written and d.get("type") in ("user", "attachment")
                and transcripts.mine(d)):
            HEARD.add((path, written))
            UNHEARD.pop((path, written), None)
            return True
    UNHEARD[(path, written)] = at + end
    return False


def delivered(text: str, k: str, written: float, held: dict) -> bool:
    """An answer whose move's words each reached their session: it heard
    from me since the answer was written. Like a sent wave's, it is spent.
    An answer with no move never is."""
    found = []
    answer(text, k, found)
    return bool(found) and all(moved(to, written, held) for to, _ in found)


def owed(to: str, written: float, held: dict, live: dict, open_ids) -> bool:
    """Whether session `to` still waits for words written at `written`: it
    is idle, and has not heard from me since."""
    mine = held.get(to)
    if not mine or page.live_state(live.get(mine.get("session_id")), mine, open_ids)[0] not in ("idle", "waiting"):
        return False
    return not moved(to, written, held)


def same(to: str, written: float, held: dict) -> bool:
    """Whether session `to` is still the one words written at `written` were
    for: it claimed before them. A number is handed out again once its
    session closes, and a newcomer never gets another's words."""
    claimed = (held.get(to) or {}).get("claimed", "")
    return bool(claimed) and claimed <= time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(written))


def still(m: dict, text: str, written: float, held: dict) -> str:
    """An answer's moves for another session that session has not heard
    yet, as answer lines: each move's line, then its words. They outlive
    what hides the rest of the answer: its own session's stop, a newer
    ask, a wave since sent."""
    found = []
    answer(text, m["id"], found)
    left = {words for to, words in found
            if to != m.get("session") and same(to, written, held) and not moved(to, written, held)}
    out, said, paste = [], "", []
    for line in text.splitlines() + [""]:
        if line.startswith("> ") or line == ">":
            paste.append(line)
            continue
        if paste and "\n".join(p[2:] for p in paste) in left:
            out += [said, *paste]
        paste = []
        if line.strip():
            said = line
    return "\n".join(out)


def quiet(m: dict, held: dict) -> int:
    """When a mission's session last wrote: its turn's end, or its last
    words before it went."""
    try:
        return int(os.path.getmtime((held.get(m["session"]) or {}).get("transcript", "")))
    except OSError:
        return int(time.time())


def due(nn: str, held: dict, live: dict, open_ids) -> list:
    """Each live mission waiting on my hand, as (id, stage letter, since
    when), as the page waits on me in 1100's home. Its answer's words
    wait for my send. Or it needs the assistant to answer or check it, and
    auto-send will not hand it over. Or its session is gone. A completed
    mission waits only on its words for another session, and one a drive
    holds never waits."""
    out, d, auto = [], drive.read(nn), auto_on(nn)
    for i, s in enumerate(plans.plan(nn).get("stages", [])):
        letter = chr(65 + i)
        for m in s.get("missions", []):
            m = {**m, **plans.found(m, held, nn)}
            if not m.get("session") or drive.driving(d) and {drive.PLAN, letter, m["id"]} & set(drive.words(d)):
                continue
            path = os.path.join(registry.folder(nn), "answers", f"{m['id']}.md")
            text = read(path)
            written = os.path.getmtime(path) if text else 0
            word, _, look = state(m, held, live, open_ids)
            done, found = look == " done", []
            answer(still(m, text, written, held) if done else text, m["id"], found)
            if any(owed(to, written, held, live, open_ids) for to, _ in found):
                out.append((m["id"], letter, int(written)))
            elif not done and word != "working":
                # A wave waiting on me is its session's own Clarify. A
                # question outside one auto-send never hands; a check it
                # hands while on.
                needs = "gone" if word == "gone" else need(nn, m, held)
                wave, _, head, _ = clarify.newest(m["session"])
                if (needs == "gone" or needs == "check" and not auto
                        or needs == "answer" and not (wave and not head.get("sent"))):
                    out.append((m["id"], letter, quiet(m, held)))
    return out


def answer_btn(k: str, to: str) -> str:
    """Send answers to NN, beside a wave's title, coloured by its receiver. Its click never opens the card."""
    return (f'<button class="{page.into(to)}" onclick="event.stopPropagation();'
            f'pressType(this,\'{k}\', true, \'\', \'answers\')">{page.icon("send", 11)}Send answers to {to}</button>')


def since(ask: dict, btn: str = "") -> str:
    """What a session asked, drawn in its answer's place.

    A wave shows its items, grey, and beside its title the button, when there is one. A turn shows
    when it asked, and its move. Nothing asked gives "".
    """
    if "wave" in ask:
        chips = "".join(f'<span class="chip g" style="--c:var(--grey)" title="{page.esc(it.get("title", ""))}">'
                        f'{page.esc(it["n"])}</span>' for it in ask["items"])
        return (f'<div class="hlrow"><p class="hl">Wave {ask["wave"]} · {page.count(len(ask["items"]), "new item")}, '
                'not answered yet</p>'
                f'{btn}</div><div class="vs">{chips}</div>')
    if not ask:
        return ""
    when, move = ask["when"], ask["move"]
    return (f'<p class="hl">Asked you at {when.strftime("%H:%M")}, not answered yet</p>'
            + (f'<p>{inline(move)}</p>' if move else ""))


def fin(m: dict) -> str:
    """A completed mission's mark, in place of its latest answer and its buttons."""
    who = f"Session {m['session']}" if m.get("session") else "Its session"
    return f'<div class="fin"><b>✓ Completed</b><span>{who} finished, and stopped.</span></div>'


def face(m: dict, grey: str, word: str, aides: list, go: str = "") -> str:
    """A card's top: the tag and the state, the name, then each helper."""
    return (f'<div class="hd"><span class="chip{grey}">{page.esc(tag(m))}</span>'
            f'<span class="st">{page.esc(word)}</span></div>'
            f'<div class="nm"{go}>{page.esc(short(m))}</div>'
            + "".join(f'<div class="hp"><span class="chip" style="--c:var(--{c})">{n}</span>'
                      f' helper · {page.esc(w)}</div>' for n, r, w, c, _ in aides))


def folded(label: str, marks: list) -> str:
    """Finished work, folded into one line. A click unfolds what sits under it."""
    return (f'<button class="finl" onclick="unfold(this)" aria-expanded="false">'
            f'<span class="car">{page.icon("right", 12)}</span>'
            f'<span class="ok">{page.icon("check", 12)}{label}</span>{"".join(marks)}</button>')


def render(nn: str) -> str:
    p = plans.plan(nn)
    stages, opened = p.get("stages", []), plans.opened(p)
    held, live, open_ids = registry.entries(), registry.claude_records(), panes.ids(panes.FRESH)
    folder = registry.folder(nn)
    got = drives((held.get(nn) or {}).get("transcript", ""))
    driven, ahead, active = drive.read(nn), "", ()
    owing = due(nn, held, live, open_ids)

    # The rail is clarify's: ids only, a thin line between two stages, and
    # each stage's letter above its own.
    rail, done_rows, rows, views, items = [], [], [], [], []
    marks = {"done": ("ok", "✓", "stopped", "grey"), "new": ("no", "–", "not started", "grey"),
             "on": ("on", "●", "running", "blue")}
    first = ""
    for i, s in enumerate(stages):
        at = chr(65 + i)
        name = page.esc(s["name"])
        if rail:
            rail.append('<div class="gap"></div>')
        rail.append(f'<div class="tab stg" data-k="{at}" title="{name}" onclick="tab(\'{at}\')">{at}</div>')
        cards, cols, fins, finls, looks, handoffs, ms = [], [], [], [], [], [], []
        for m in s.get("missions", []):
            m = {**m, **plans.found(m, held, nn)}
            ms.append(m)
            k = page.esc(m["id"])
            word, colour, look = state(m, held, live, open_ids)
            done = look == " done"
            running = not done and word != "not started"
            aides = [(n, r, *page.live_state(live.get(r.get("session_id")), r, open_ids))
                     for n, r in helpers(m, held)]
            looks.append(look or word)
            grey = (" g" if colour == "grey" else "") + look
            go = f' onclick="tab(\'{k}\')"'
            answer_file = os.path.join(folder, "answers", f"{m['id']}.md")
            text = read(answer_file)
            written = os.path.getmtime(answer_file) if text else 0
            gone = bool(m.get("session")) and (spent(m, text) or delivered(text, m["id"], written, held))
            ask = {} if done or not m.get("session") else asks(m, held.get(m["session"]) or {}, word, text)
            ready = running and bool(m.get("session")) and clarify.ready(m["session"])
            asked = since(ask, answer_btn(k, m["session"]) if ready else "")
            # Words for another session outlive what hides the rest of the
            # answer: its own session's stop, a newer ask, a wave since sent.
            left = answer(still(m, text, written, held), k) if m.get("session") and (done or asked or gone) else ""
            # A session whose wave waits on me opens its Clarify tab instead.
            nw, _, top, _ = clarify.newest(m["session"]) if m.get("session") and not done else (0, "", {}, [])
            waves = bool(nw) and not top.get("sent")
            opens = f' onclick="toClarify(\'{page.esc(m["session"])}\')"' if waves else go
            took = running and taken(m, at, got, held)
            if running and m.get("session"):
                handoffs.append(took)
            rail.append(f'<div class="tab{grey}" data-k="{k}" style="--c:var(--{colour})" '
                        f'title="{page.esc(m["name"])}"{go}>{k}</div>')
            cards.append(f'<div class="card{grey}" style="--c:var(--{colour})"{opens}>'
                         + face(m, grey, word, aides) + '</div>')
            more = f'<p class="hl">Still to send</p>{left}' if left else ""
            summary = (asked + more or ("" if gone else brief(k, text, answer_btn(k, m["session"]) if ready else ""))) \
                if m.get("session") else '<p class="none">Not started.</p>'
            if done and not left:
                finls.append(f'<span class="one"><span class="chip{grey}" style="--c:var(--{colour})">'
                             f'{page.esc(tag(m))}</span>'
                             f'{page.esc(short(m))}</span>')
                fins.append(f'<div class="col{grey}" style="--c:var(--{colour})">'
                            + face(m, grey, word, aides, go) + fin(m) + '</div>')
            else:
                cols.append(f'<div class="col{grey}" style="--c:var(--{colour})">'
                            + face(m, grey, word, aides, opens) + (fin(m) if done else "")
                            + (f'<div class="sum">{summary}</div>' if summary else "")
                            + (acts(k, took) if running else "") + '</div>')
            mission = read(m.get("file", ""))
            items.append(
                f'<section class="item" id="t-{k}" style="--c:var(--{colour})">'
                f'<button class="back" onclick="tab(\'{at}\')">{page.icon("back", 12)}{name}</button>'
                f'<div class="hd"><span class="chip{grey}">{page.esc(tag(m))}</span>'
                f'<b class="st">{page.esc(word)}</b></div>'
                + "".join(f'<p class="kick">Helper · session {n}, {page.esc(r.get("title", ""))} · '
                          f'<b>{page.esc(w)}</b></p>' for n, r, w, c, _ in aides)
                + f'<h1 class="q">{page.esc(short(m))}</h1>'
                + (fin(m) if done
                   else f'<h2 class="sec">Waiting on you</h2><div class="ans{" go" if "wave" in ask else ""}"'
                        f'{opens if "wave" in ask else ""}>{asked}</div>' if asked
                   else "" if gone
                   else '<h2 class="sec">Latest answer</h2>'
                   + (f'<div class="ans">{answer(text, k)}</div>' if text
                      else '<p class="kick">No answer yet.</p>'))
                + (f'<h2 class="sec">Still to send</h2><div class="ans">{left}</div>' if left else "")
                + (acts(k, took) if running else "")
                + f'<h2 class="sec">Mission · {page.esc(os.path.basename(m.get("file", "")) or "none yet")}</h2>'
                + (f'<pre class="doc">{page.esc(mission)}</pre>' if mission
                   else '<p class="kick">Not written yet.</p>')
                + "</section>")
        # A stage is done when every mission stopped, new when none started.
        # The first not done is the current one, and main opens on it.
        cls, mark, said, tone = marks["done" if all(x == " done" for x in looks)
                                     else "new" if all(x == "not started" for x in looks) else "on"]
        if not first and cls != "ok":
            first = at
        # The first stage started and not done is the active one, and the
        # team bar's second row is its. A drive holding it takes it too.
        if cls == "on" and not active:
            held_by = drive.driving(driven) and {drive.PLAN, at} & set(drive.words(driven))
            active = (at, name, bool(held_by) or bool(handoffs) and all(handoffs))
        # The first stage not kicked off holds Launch page, while the
        # assistant has a launch page to open.
        if not ahead and not any(x.get("session") for x in ms):
            ahead = at
        # An open plan's stage stays open, and in place, until I close it.
        shut = at in driven.get("closed", {}) if opened else cls == "ok"
        row = (f'<div class="stage"><h3 class="sub go" title="Open {name}" onclick="tab(\'{at}\')">'
               f'<span class="mk {cls}">{mark}</span>{name}'
               + (' <span class="chip g">Open</span>' if opened and not shut else "") + '</h3>'
               + ("" if opened else drive.moments(driven, at, ms, cls == "ok",
                                                 ahead == at and os.path.isfile(os.path.join(registry.folder(nn),
                                                                                             "launch.json"))))
               + f'<div class="cards">{"".join(cards)}</div></div>')
        (done_rows if shut else rows).append((name, row))
        head = (f'<div class="shead"><h1 class="q">{name}</h1>'
                f'<span class="dim">{page.count(len(looks), "mission")}</span>'
                + (stage_acts(at, all(handoffs)) if handoffs and active[:1] != (at,) else "") + '</div>')
        views.append(f'<section class="item" id="t-{at}" style="--c:var(--{tone})">{head}'
                     + (folded(f"{len(fins)} finished", finls)
                        + f'<div class="fins">{"".join(fins)}</div>' if fins else "")
                     + (f'<div class="cols">{"".join(cols)}</div>' if cols else "")
                     + '</section>')
    # A mission waiting on my hand opens its stage instead, once.
    first = owing[0][1] if owing else first
    owed_key = " ".join(f"{k}@{t}" for k, _, t in owing)
    count = sum(len(s.get("missions", [])) for s in stages)
    past = (folded(f"{len(done_rows)} {'closed' if opened else 'finished'}",
                   [f'<span class="one">{n}</span>' for n, _ in done_rows])
            + f'<div class="fins rows">{"".join(r for _, r in done_rows)}</div>') if done_rows else ""
    items = ['<section class="item" id="t-all">'
             f'<p class="kick">{page.count(len(stages), "stage")} · {page.count(count, "mission")}</p>'
             f'<div class="phead"><h1 class="q">The whole plan</h1></div>'
             f'{past}{"".join(r for _, r in rows)}</section>'] + views + items

    tag_ = plans.tag(nn, plans.owners(held))
    if not stages:
        return page.render(f"{nn}-assistant", [("", page.blank("No plan yet") + page.watch())],
                           page.head("assistant", tag_), refresh=0)
    return page.render(f"{nn}-assistant",
                       [("", f'<div id="items" data-first="{first or "all"}" data-due="{page.esc(owed_key)}">'
                             f'{"".join(items)}</div>'
                         + page.watch() + page.TYPING + page.COPY + PILLS + SCRIPT + drive.STYLE)],
                       page.head("assistant", tag_, "", bar(nn, driven, active))
                       + f'<nav class="nums" id="index">{"".join(rail)}</nav>\n', refresh=0)


SCRIPT = """<style>
  /* The team bar: one row across the whole head, the plan's label and
     buttons, then the active stage's, left first. Every button is small,
     the Launch page button's size, its colour where it goes. */
  header.top.fam.assistant { display:block; padding:6px 10px; }
  header.top.fam.assistant .mid { display:none; }
  header.top.fam.assistant .acts { display:flex; flex-wrap:wrap; justify-self:stretch; }
  .tb-row { display:flex; flex-wrap:wrap; align-items:center; gap:6px; min-height:28px; }
  .tb-row h2 { margin:0 2px 0 0; }
  .tb-row > h2:not(:first-child) { margin-left:2px; }
  .tb-row .cut, .tb-stage::before { width:1px; height:16px; background:var(--line); margin:0 6px; }
  .tb-stage::before { content:""; }
  /* The active stage's own view names it in its heading: the bar's name goes. */
  .tb-stage.here h2 { display:none; }
  header.top.fam .btn { height:22px; padding:0 8px; font-size:11px; gap:5px; }
  header.top.fam .btn.sq { width:22px; padding:0; }
  #items h3.sub .mk { display:inline-block; width:1.4em; }
  #items h3.sub .mk.ok { color:var(--green); }
  #items h3.sub .mk.on { color:var(--blue); }
  #items .stage { margin:0 0 20px; }
  #items .cards { display:grid; gap:10px; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); }
  #items .card { background:var(--panel); border:1px solid var(--line);
    border-left:4px solid var(--c); border-radius:6px; padding:8px 10px; cursor:pointer; }
  #items .card:hover { border-color:var(--text); border-left-color:var(--c); }
  #items .card.done, #items .col.done, #items .card.dashed, #items .col.dashed { border-left-style:dashed; }
  #items .card .hd, #items .col .hd, #items .item > .hd { display:flex; align-items:center; gap:8px; }
  #items .card .st, #items .col .st { margin-left:auto; color:var(--c); font-size:11px; font-weight:700; }
  #items .item > .hd { margin:0 0 6px; }
  #items .item > .hd .st { color:var(--c); font-size:12px; }
  #items .card .nm, #items .col .nm { font-size:14px; font-weight:700; margin:6px 0 0; overflow-wrap:anywhere; }
  #items .card.done .nm, #items .col.done .nm { color:var(--dim); }
  #items .col .nm { cursor:pointer; }
  #items .col .nm:hover { text-decoration:underline; }
  /* A stage's head: its name and count, then Drive the stage on the right. */
  #items .shead { display:flex; align-items:center; flex-wrap:wrap; gap:8px 12px; margin:0 0 10px; }
  #items .shead h1.q { margin:0; }
  #items .shead .group { margin-left:auto; }
  /* Finished work, folded into one lighter line above what is still live. */
  #items .finl { display:flex; align-items:center; flex-wrap:wrap; gap:6px 10px; width:100%; margin:0 0 10px;
    padding:6px 10px; font:inherit; font-size:12px; text-align:left; cursor:pointer; color:var(--dim);
    background:var(--raised); border:1px solid var(--line); border-radius:6px; }
  #items .finl:hover { background:var(--hover); }
  #items .finl[aria-expanded="true"] .car { display:inline-block; transform:rotate(90deg); }
  #items .finl .ok { display:inline-flex; align-items:center; gap:5px; color:var(--green); font-weight:700; }
  #items .finl .one { display:inline-flex; align-items:center; gap:6px; }
  #items .fins { display:none; gap:8px; margin:0 0 12px;
    grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); }
  #items .fins.open { display:grid; }
  #items .fins.rows.open { display:block; }
  /* A stage's live missions, side by side: the card, what it asks, then its buttons at the foot. */
  #items .cols { display:grid; gap:10px; align-items:start; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); }
  #items .col { display:flex; flex-direction:column; min-width:0; background:var(--panel);
    border:1px solid var(--line); border-left:4px solid var(--c); border-radius:6px; padding:10px 12px; }
  #items .col .sum { margin-top:8px; padding-top:8px; border-top:1px solid var(--line); }
  #items .item .col p { font-size:14px; line-height:1.5; margin:0 0 4px; }
  #items .item .col p.hl { font-size:14px; font-weight:700; margin:0 0 6px; }
  #items .hlrow { display:flex; align-items:center; flex-wrap:wrap; gap:6px 10px; margin:0 0 6px; }
  #items .hlrow p.hl { margin:0; }
  #items .item .col p.none, #items .item p.none { color:var(--dim); }
  #items .col .paste { margin:4px 0 8px; padding:8px 10px; }
  #items .col .paste .txt { font-size:13px; }
  #items .vs { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
  #items .vs .chip { cursor:pointer; min-width:28px; }
  #items .vs .chip.g { cursor:default; }
  /* Type, Send and Drive: one width each, in that order, never wider than they need. */
  #items .acts3 { display:grid; grid-template-columns:repeat(3, minmax(0, 96px)); gap:6px;
    margin-top:10px; padding-top:10px; border-top:1px solid var(--line); }
  #items .acts3 .btn { min-width:0; padding:0 6px; }
  #items .item > .acts3 { max-width:360px; border-top:0; padding-top:0; }
  #items .hp { display:flex; align-items:center; gap:6px; margin-top:6px; color:var(--dim); font-size:12px; }
  #items .fin { margin-top:10px; padding:8px 10px; border:1px solid var(--green); border-radius:4px;
    display:flex; flex-direction:column; gap:2px; }
  #items .fin b { color:var(--green); font-size:14px; }
  #items .fin span { color:var(--dim); font-size:12px; }
  #items .back { display:inline-flex; align-items:center; gap:5px; margin:0 0 8px; padding:0; border:0;
    background:none; color:var(--blue); cursor:pointer; font:inherit; font-size:12px; font-weight:700; }
  #items .ans.go { cursor:pointer; }
  #items .ans.go:hover p.hl { text-decoration:underline; }
  #items .ans h3.hit { outline:2px solid var(--text); outline-offset:6px; border-radius:2px; }
  #items .ans p.hl { font-size:21px; font-weight:700; }
  #items .ans h3 { display:flex; gap:10px; align-items:center; font-size:16px; margin:18px 0 6px; }
  #items .ans ul { margin:0 0 10px; padding-left:20px; }
  #items code { background:var(--panel); padding:0 4px; border-radius:3px; }
  @media (max-width:520px) {
    #items { padding:10px 10px 14px; }
    #items .item h1.q { font-size:20px; }
  }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    header.top button { min-height:44px; }
    nav.nums .tab { width:44px; padding:0; line-height:44px; }
    #items .btn { height:44px; }
    #items .vs .chip { min-width:44px; height:44px; line-height:44px; }
    #items .col .nm, #items h3.sub.go { display:flex; align-items:center; min-height:44px; }
    #items .finl, #items .back { min-height:44px; }
    #items .paste { min-height:60px; }
    #items .paste > button { min-height:44px; }
    /* The team bar packs as tight as it goes: no label but the stage's,
       no icon on a worded button. Auto-send's pills sit beside See the
       whole plan, the drive's two under them. The stage's sit as the
       driven band does: edge to edge, raised, under the plan's. */
    header.top.fam.assistant { padding:6px 8px; }
    header.top.fam.assistant .acts { display:block; }
    #auto { order:1; }
    .tb-row > .btn.ask { order:2; }
    .tb-stage { margin:6px -8px -6px; padding:6px 8px; background:var(--raised);
      border-top:1px solid var(--line); }
    .tb-stage::before { content:none; }
    header.top.fam .btn, header.top.fam .pills button { height:44px; min-width:44px; padding:0 10px; }
    header.top.fam .btn.sq { width:44px; padding:0; }
    header.top.fam .btn:not(.sq) .i { display:none; }
    .tb-row .tb-label, .tb-row .cut { display:none; }
  }
</style>
<script>
// Auto-send's pills: the one pressed shows at once, and the switch is kept.
function autoSend(b) {
  document.querySelectorAll('#auto button').forEach(x => x.classList.toggle('on', x === b));
  typePost({act: 'auto', id: b.dataset.v});
}
function copy(b) {
  navigator.clipboard.writeText(b.previousElementSibling.textContent).then(() => {
    b.textContent = 'Copied'; b.classList.add('done');
    setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('done'); }, 1500);
  });
}
// A button that types. Never named typeIn: home hands my typing anywhere to
// a page's window.typeIn, page.py's ANYWHERE, and this page takes none.
// Once Type typed a line, the Send beside it presses Return alone, so the
// line goes with any words I added, never typed twice.
async function pressType(b, k, send, key, act) {
  act = act || (key ? 'paste' : 'type');
  const pair = b.parentElement, mine = act + '|' + k + '|' + (key || '');
  const only = send && pair.dataset.typed === mine ? 'return' : '';
  const said = await pressed(b, {act, id: k, key: key || '', send: send ? 'yes' : '', only}, !send);
  if (said !== '') return;
  if (send) delete pair.dataset.typed;
  else pair.dataset.typed = mine;
}
// A folded line opens what it holds, and closes it again.
function unfold(b) {
  const open = b.getAttribute('aria-expanded') !== 'true';
  b.setAttribute('aria-expanded', open);
  b.nextElementSibling.classList.toggle('open', open);
}
// A session whose wave waits on me opens its Clarify tab, in 1100's home,
// or its clarify page when this page stands alone.
function toClarify(nn) {
  if (parent !== window) parent.postMessage({ws: 1, open: 'clarify', nn}, '*');
  else location.href = '/p/clarify/' + nn;
}
// A chip opens its mission, and brings its item into view.
function jump(k, n) {
  tab(k);
  const h = document.querySelectorAll('#t-' + CSS.escape(k) + ' .ans h3')[n];
  if (!h) return;
  h.scrollIntoView({block: 'center'});
  h.classList.add('hit');
  setTimeout(() => h.classList.remove('hit'), 1600);
}
const opening = document.getElementById('items').dataset.first;
// A fact shows once: while the active stage's own view shows, its heading
// names the stage, and the team bar's name goes.
(() => {
  const bar = document.querySelector('.tb-stage'), shown = tab;
  if (bar) tab = k => { shown(k); bar.classList.toggle('here', String(k) === bar.dataset.at); };
})();
// 1100's team number and Team tab bring the page back to its current stage.
addEventListener('ws-home', () => tab(opening));
// Words newly waiting for my send open their stage once, whatever view I
// left. After that, a reload keeps the view I pick.
const due = document.getElementById('items').dataset.due, shown = 'due:' + location.pathname;
// A view the plan no longer holds, as a mission gone with a new plan, opens
// the current stage instead of a blank page.
const asked = decodeURIComponent(location.hash.slice(1));
if (due && sessionStorage.getItem(shown) !== due) {
  sessionStorage.setItem(shown, due);
  tab(opening);
} else tab(asked && document.getElementById('t-' + asked) ? asked : opening);
// A reload keeps my place while the view stays the one I left: each fold I
// opened, and main's scroll. A hidden frame has no scroll to keep, so it
// keeps the last, and takes it once it shows.
(() => {
  const main = document.querySelector('main'), K = 'place:' + location.pathname;
  addEventListener('beforeunload', () => {
    if (innerWidth) sessionStorage.setItem(K, JSON.stringify({view: location.hash, top: main.scrollTop,
      open: [...document.querySelectorAll('#items .item > .finl[aria-expanded="true"]')].map(b => b.parentNode.id)}));
  });
  let was = null;
  try { was = JSON.parse(sessionStorage.getItem(K) || 'null'); } catch (e) {}
  if (!was || was.view !== location.hash) return;
  was.open.forEach(id => { const b = document.querySelector('#' + CSS.escape(id) + ' > .finl'); if (b) unfold(b); });
  const scroll = () => {
    if (!innerWidth) return;
    removeEventListener('resize', scroll);
    main.scrollTop = was.top;
  };
  addEventListener('resize', scroll);
  scroll();
})();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["queue", "states"])
    ap.add_argument("words", nargs="*")
    ap.add_argument("--port", type=int)
    args = ap.parse_args()
    words = list(args.words)
    if args.port is not None:
        nn = f"{args.port % 100:02d}"
    elif words and re.fullmatch(r"\d{2}", words[0]):
        nn = words.pop(0)
    else:
        sys.exit(f"{args.verb} takes the assistant's number, like 07.")
    p = plans.plan(nn)
    missions = [m for s in p.get("stages", []) for m in s.get("missions", [])]

    if args.verb == "queue":
        now = time.strftime(STAMP)
        hit = [m for m in missions if m["id"] in words]
        if hit and (gone := stranded(nn, p, words)):
            sys.exit("\n".join(
                ["Nothing queued. Each of these ended with no stop, and its folder stands:"]
                + [f"  {tag(m)}: keep it, python3 .claude/tools/drive.py keep {nn} {m['id']}, "
                   f"then end it, /reaper {m['session']}. Or resume it." for m in gone]))
        for m in hit:
            m["queued"] = now
        if hit:
            plans.save(nn, p)
        print(" ".join(m["id"] for m in hit) + f" queued at {now}." if hit else "No mission matched.")
    else:
        held, live, open_ids = registry.entries(), registry.claude_records(), panes.ids()
        for m in missions:
            m = {**m, **plans.found(m, held, nn)}
            word, _, look = state(m, held, live, open_ids)
            if look == " done":
                word = "stopped"
            elif m.get("session"):
                word = need(nn, m, held)
            print(f'{m["id"]} · {word} · {m.get("title") or m["name"]}')
            for n, r in helpers(m, held):
                w = page.live_state(live.get(r.get("session_id")), r, open_ids)[0]
                print(f'{m["id"]} helper · {w} · {r.get("title", n)}')


if __name__ == "__main__":
    main()
