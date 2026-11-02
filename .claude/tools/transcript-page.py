#!/usr/bin/env python3
"""transcript-page.py — one session's whole transcript, as its Transcript tab draws it.

1100 draws it at /p/transcript/NN, a tab in every place, on my Mac and
my phone. lib/transcripts.py reads it from disk, and numbers every turn
as transcript.py's copy numbers it, so I can point at one. An ended
session's still draws, found by its title.

My turns are edged white. One of Claude Code's own commands I typed, as
/context, reads as a turn of mine, uncounted, with what it answered grey
beneath it, its colours stripped. So does a line I typed after !, as
! kill 75163, with what the shell printed. The session's newest turn, while nothing
follows it, is edged by its state, the colours 1100's rail wears: green
while it works, red once it stops. Its older turns are edged grey.

Inside a session's turn, what it said and what it did keep their order:
its notes draw as its reply does, without the card, and each skill it ran
and each file it wrote is a line of its own. Each command and each agent
is a line of its own too, its kind named, with what came back beneath it,
as my terminal shows it: a command's first lines, an agent's running or
how it ended. Every other tool call folds, a run of them into one line,
and unfolds to each call. Any call unfolds to what went in and what came
back, read from disk only then; an agent sent to the background, to what
went in alone. Its last words are its reply, drawn as a card, its move
marked. A table in it, or in an agent's report, draws as a grid, scrolling
sideways when wider than the card. A list keeps the numbers the pane
shows, across the blank lines between its items. Its thinking and the
harness's notices never show.

A copy block wears Copy. A hand-off, in one of talking.md's shapes, wears
one group: Copy, Type, then Send, naming its receiver unless it is this
session. A copy block under "Send to session 12." types its words into
12's pane; "Type `/9-session-stop`." types the command here, and "... in
session 20." into 20's. Each press reads the words again from the
transcript. "Send my verdicts on session 02's page." wears Send answers to
02 alone, greyed while an item there has neither an answer nor a
proposal. "Paste `path` into ChatGPT." wears Copy file. A Send into a
session steering others, an assistant or the advisor, is gold.

A turn can wake without me: an agent's report, or a command it left
running ending, a drive's wait. Each wake draws a line across the turn,
its time and what woke it, then what happened: an agent's report unfolds
from there. What follows reads as a stretch of its own, its last words
its own card. The turn keeps its one number, as the copy numbers it. An
agent's report read while the session worked draws the same line where it
arrived, and splits nothing.

While anything it sent to the background runs, the foot counts and names
each one. Once nothing runs, or the session is gone, the count goes.

It opens at its newest turn, and moves as the session writes, told the
way 1100's other pages are, never on a clock. Told, it asks again for its
last turn, what came after, and every turn still showing something
running, and draws again only the pieces of them that moved, in place, so
what I unfolded, highlighted, where I scrolled and what I typed all stay.
A call I unfolded while it ran shows what came back once it ends. Framed
by home, home tells it; alone, it asks /heard itself. 1100 hears a
transcript only while a page asks about it.

The advisor's alone wears the Advise tab at its top left, opening every
session to advise on, follow or drive: advisor-page.py's panel, its rows
drawn again each time the page is told, its presses taken there.

On my Mac and my phone alike, the box I type into sits pinned beneath
it: a menu, two arrows, the text and Send. On my phone, the text takes
the whole width, two lines tall, its hint short, and the rest sit on a
line beneath it, Send at its end. On my Mac, a letter or a paste
anywhere on the page, or on 1100's home around it, lands in the box.
On my Mac, the box holds the cursor, so a dictation tool always finds
it: it takes it when the page shows, and back after a click on the page
or on home around it, unless text stays highlighted, or another field
or page beside it holds the cursor. After a click on the page, it waits
half a second, so a double or triple click highlights first. Send types the line into the session's
pane, as panes.say types, then presses Return, so a press and my typing
do the same. A file from the paperclip is kept in the session's own
folder, under sent/, and its path follows my words on the line. A line
typed while the session works waits, queued, at the transcript's foot,
until it reads it. A pane gone, or Claude gone, refuses in one sentence,
and nothing is typed. On my Mac, Return sends too, and
Shift+Return adds a line. My phone sends only
from Send. Dictation is the keyboard's own
mic key: a home-screen web app cannot start it from a page's button.

A / opening the box lists every skill above it, each with its first
sentence, then Claude Code's own commands that need no picker, and
narrows them as I type. A tap, Tab or Return fills one in. On my Mac, the
up arrow in an empty box brings back my last line, again the one before,
and the down arrow returns. A picture pasted there, on my Mac or my
phone, is held as the paperclip holds it.

While the session works, an empty box's Send reads Stop. A press is
Escape in its pane, and the turn stops. Send and Stop are the largest
controls on the line, after the text.

The menu, one small button at the line's start, keeps everything else
off the line, so the text has the room. It holds what the session's status line
last printed, whole. Then its mode, as its pane's foot names it: a tap is
Shift+Tab there, the next mode. Then the paperclip.

Beside it, two arrows step through my turns, landing each at the top:
up, the nearest one starting above the transcript's top edge; down, the
nearest starting below it, and past my last, the transcript's foot. With
none that way, an arrow greys.

Once a turn ends, the reply Claude Code suggests, faint in its pane,
shows above the box: a tap, or Tab on my Mac, fills the box with it,
wherever on the page or on 1100's home around it the Tab lands. A
dialog waiting in the pane shows above the box instead, its words and
each choice a button: a tap types the choice's number, as my keyboard
would. Its words scroll on their own, a file's preview among them, so its
question and its choices always show. A panel with no choices, as /usage
opens, shows Close, which is Escape there. Send, meanwhile, types my own
words into the dialog's own field: its "Type something.", else the reason
a No carries. 1100 reads all of it off the pane's screen, through iTerm,
only when the session's state moves, and never while its tab is hidden:
a hidden tab reads it once it shows.

  transcript-page.py draw NN    the page, printed, as 1100 draws it

sessions-dashboard.py routes its addresses. Imported, or run to draw.
"""

import argparse
import base64
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import iterm  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import transcripts  # noqa: E402
import wake  # noqa: E402

esc = page.esc

# 1100/skills reads every skill's head. The / menu lists the same.
skills_page = page.tool("skills-page")
# A session's waves are read and sent the clarify page's own way.
clarify = page.tool("clarify-page")
# The advisor's panel: advisor-page.py's.
advisor = page.tool("advisor-page")

# Each kind of tool call, said once and said many.
WORDS = {"command": ("command", "commands"), "read": ("read", "reads"), "search": ("search", "searches"),
         "fetch": ("page fetched", "pages fetched"), "browser": ("browser step", "browser steps"),
         "load": ("tool loaded", "tools loaded"), "agent": ("agent", "agents"), "other": ("other", "others")}

# What went in and what came back shows this much, then is cut.
SHOWN = 20_000

# A transcript a page asked about this recently is one 1100 hears.
LATELY = 60

# Each session a page asked about, and when, so 1100 hears only those.
ASKED: dict = {}

# An ended session's transcript, found by its title, and when. Finding it
# reads every transcript's title, seconds of work under 1100's lock, so only
# opening its page looks, once a minute at most.
ENDED: dict = {}


def located(nn: str, look: bool = False) -> str:
    """Session NN's transcript: its record's while it is registered, even
    before its first word, else the newest one titled with its number, as
    `look` last found it."""
    rec = registry.entries().get(nn)
    if rec:
        return rec.get("transcript", "")
    at, path = ENDED.get(nn, (0.0, ""))
    if look and time.time() - at > LATELY:
        path = transcripts.find(nn)[0]
        ENDED[nn] = (time.time(), path)
    return path


def status(nn: str) -> str:
    """Claude Code's word for session NN, read from its record alone, so a
    key can carry it: busy, idle, shell or waiting, else nothing."""
    sid = (registry.entries().get(nn) or {}).get("session_id")
    for base in registry.LIVE if sid else ():
        for f in glob.glob(os.path.expanduser(f"{base}/sessions/*.json")):
            try:
                with open(f) as fh:
                    d = json.load(fh)
            except (OSError, ValueError):
                continue
            if d.get("sessionId") == sid:
                return str(d.get("status", ""))
    return ""


def key(nn: str) -> str:
    """The page's key, without drawing it: its transcript's size and time,
    and the session's state, so a turn ending tells the page even when the
    transcript stays still. The advisor's adds its panel's. Asked, 1100
    hears that transcript for a while."""
    ASKED[nn] = time.time()
    try:
        st = os.stat(located(nn))
    except OSError:
        return ""
    return f"{st.st_size}-{st.st_mtime_ns}-{status(nn)}" + (f"-{advisor.key(nn)}" if advisor.seat(nn) else "")


def heard() -> list:
    """Every transcript a page asked about lately: a write to one moves it."""
    now = time.time()
    return [p for nn, at in list(ASKED.items()) if now - at < LATELY and (p := located(nn))]


# ---- a reply's words, as the turn's shape writes them ---------------------------

# The pane draws a reply through Claude Code's own markdown, and the card
# reads it the same way. A list keeps its numbers across the blank lines
# between its items, as 1. to 5. with a line under 1. stays 1. to 5. A list
# inside an item stays inside it, numbered a, b, c, as the pane numbers it.
# A quote, a rule, italics and struck words draw as they do there.
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEAD = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+|$)")
# A list item's marker: its indent, the marker, its number if it counts,
# then the space before its words.
LIST = re.compile(r"^( {0,3})([-*+]|(\d{1,9})[.)])( +|$)")
HR = re.compile(r"^ {0,3}([-*_])(?: *\1){2,} *$")
QUOTE = re.compile(r"^ {0,3}> ?")
# A paragraph's last line underlined, as "Title" over "---", makes it a heading.
UNDER = re.compile(r"^ {0,3}(?:=+|-+) *$")
INDENTED = re.compile(r"^ {4}")
START, END = "▼▼▼ START COPY ▼▼▼", "▲▲▲ END COPY ▲▲▲"
# A hand-off written inside a paragraph, in one of talking.md's shapes: a
# command to type, here or in session 20; my verdicts on a session's page;
# a file to paste elsewhere.
TYPED = re.compile(r"\btype `([^`\n]+)`(?: here| in session (\d{2}))?(?=[.,;:]|[ \t]*(?:\n|$))", re.I)
VERDICTS = re.compile(r"\bsend my verdicts on session (\d{2})['’]s page\b", re.I)
FILED = re.compile(r"\bpaste `([^`\n]+)` into\b", re.I)
LABEL = re.compile(r"^\*\*([^*\n]+)\*\*$")
# A table's second line: dashes between pipes, as |---|---|.
GRID = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
# "**Your move.** Wait: session 22 stops." carries its move on its own line.
MOVED = re.compile(r"^\*\*(Your move[.:]?)\*\*[.:]?[ \t]+(\S[\s\S]*)$")
MOVE = re.compile(r"^Your move[.:]?$")
# Inside a line, first a code span, or a backslash keeping a mark as itself.
SPAN = re.compile(r"(`+)([\s\S]*?[^`])\1(?!`)|\\([!-/:-@\[-`{-~])")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
# A link opens only the web, a mail, or a page of 1100's own.
SAFE = re.compile(r"^(https?:|mailto:|/|#)")
# Then bold, italic and struck words, the widest mark first.
MARKS = [(re.compile(r"\*\*\*(?=\S)(.+?)(?<=\S)\*\*\*"), "<b><i>{}</i></b>"),
         (re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*"), "<b>{}</b>"),
         (re.compile(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)"), "<b>{}</b>"),
         (re.compile(r"\*(?=[^\s*])(.+?)(?<=[^\s*])\*"), "<i>{}</i>"),
         (re.compile(r"(?<!\w)_(?=[^\s_])(.+?)(?<=[^\s_])_(?!\w)"), "<i>{}</i>"),
         (re.compile(r"~~(?=\S)(.+?)(?<=\S)~~"), "<del>{}</del>")]
HELD = re.compile("\x00(\\d+)\x00")


def inline(text: str) -> str:
    held = []

    def hold(html: str) -> str:
        held.append(html)
        return f"\x00{len(held) - 1}\x00"

    def span(m) -> str:
        if m.group(3):
            return hold(esc(m.group(3)))
        body = m.group(2).replace("\n", " ")
        return hold(f"<code>{esc(body[1:-1] if body[:1] == body[-1:] == ' ' and body.strip() else body)}</code>")

    def marked(s: str) -> str:
        s = esc(s)
        for mark, tag in MARKS:
            s = mark.sub(lambda m: tag.format(m.group(1)), s)
        return s

    def link(m) -> str:
        if not SAFE.match(m.group(2)):
            return m.group(0)
        return hold(f'<a href="{esc(m.group(2))}" target="_blank" rel="noreferrer">{marked(m.group(1))}</a>')

    out = marked(LINK.sub(link, SPAN.sub(span, text))).replace("\n", "<br>")
    while HELD.search(out):
        out = HELD.sub(lambda m: held[int(m.group(1))], out)
    return out


def cells(line: str) -> list:
    """One table row's cells, its outer pipes dropped."""
    row = line.strip()
    return [c.strip() for c in row[row.startswith("|"):len(row) - row.endswith("|")].split("|")]


def margin(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def interrupts(line: str) -> bool:
    """Whether a line ends the paragraph above it. Of lists, only a bullet
    or a 1. does, so "Steps:" over "2. Ship" reads as one paragraph."""
    m = LIST.match(line)
    return bool(FENCE.match(line) or HEAD.match(line) or HR.match(line) or QUOTE.match(line)
                or line.strip() == START or m and line[m.end():].strip() and m.group(3) in (None, "1"))


def item(lines: list, i: int) -> tuple:
    """The list item opening at line i: its own lines, its indent taken off,
    and the line after it. A line indented to its words, or one carrying on
    its paragraph, is still the item's, even past a blank line."""
    m = LIST.match(lines[i])
    words = lines[i][m.end():]
    at = len(m.group(1)) + len(m.group(2)) + (1 if not words.strip() or len(m.group(4)) > 4 else len(m.group(4)))
    body, j, fenced = [lines[i][at:] if words.strip() else ""], i + 1, bool(FENCE.match(words))
    while j < len(lines):
        line = lines[j]
        if line.strip() and margin(line) < at and (fenced or not body[-1].strip() or interrupts(line)
                                                     or LIST.match(line)):
            break
        body.append(line[at:] if margin(line) >= at else line.strip())
        fenced ^= bool(FENCE.match(body[-1]))
        j += 1
    while len(body) > 1 and not body[-1].strip():
        body.pop()
        j -= 1
    return body, j


def listed(lines: list, i: int) -> tuple:
    """The list opening at line i: whether it counts, its first number, its
    items, and the line after it. Blank lines between items keep it one list."""
    first = LIST.match(lines[i])
    sort = lambda m: (m.group(3) is not None, m.group(2)[-1])
    items, start = [], int(first.group(3)) if first.group(3) else 0
    while True:
        body, i = item(lines, i)
        items.append(body)
        k = i
        while k < len(lines) and not lines[k].strip():
            k += 1
        m = k < len(lines) and not HR.match(lines[k]) and LIST.match(lines[k])
        if not m or sort(m) != sort(first):
            return first.group(3) is not None, start, items, i
        i = k


def blocks(src: str, top: bool = True) -> list:
    """A reply's blocks, in order: (kind, text); a list's (kind, (start,
    items)), each item its own blocks; a quote's (kind, blocks); a table's
    (kind, rows), its head first; a paste's (kind, (session, words)); or,
    after a paragraph, each hand-off it writes, (kind, (how, session,
    words)). A label and the move are read at the top alone."""
    lines = [re.sub(r"^[ \t]+", lambda m: m.group(0).expandtabs(4), s) for s in src.split("\n")]
    out, i = [], 0
    grid = lambda k: k + 1 < len(lines) and "|" in lines[k] and "|" in lines[k + 1] and GRID.match(lines[k + 1])
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif FENCE.match(line) or line.strip() == START:
            if line.strip() == START:
                shut, drop = (lambda s: s.strip() == END), 0
            else:
                mark = FENCE.match(line).group(1)
                shut = lambda s, mark=mark: re.match(rf"^ {{0,3}}{mark[0]}{{{len(mark)},}} *$", s)
                drop = margin(line)
            body, i = [], i + 1
            while i < len(lines) and not shut(lines[i]):
                body.append(lines[i][min(drop, margin(lines[i])):])
                i += 1
            i += 1
            if line.strip() != START:
                out.append(("pre", "\n".join(body)))
                continue
            # A copy block under "Send to session 12." is for 12's pane.
            last = next((b for b in reversed(out) if b[0] != "hand"), ("", ""))
            above = last[1].split("\n")[-1] if last[0] in ("p", "label") else ""
            to = page.SEND_TO.search(above)
            out.append(("paste", (to.group(1), "\n".join(body).strip())) if to else ("copy", "\n".join(body).strip()))
        elif HR.match(line):
            out.append(("hr", ""))
            i += 1
        elif HEAD.match(line):
            out.append(("h", re.sub(r"(?:^|[ \t]+)#+[ \t]*$", "", HEAD.sub("", line).strip())))
            i += 1
        elif QUOTE.match(line):
            body = []
            while i < len(lines) and lines[i].strip() and (QUOTE.match(lines[i]) or not interrupts(lines[i])):
                body.append(QUOTE.sub("", lines[i], 1))
                i += 1
            out.append(("quote", blocks("\n".join(body), False)))
        elif LIST.match(line):
            counts, start, items, i = listed(lines, i)
            got = [blocks("\n".join(body), False) for body in items]
            out.append(("ol", (start, got)) if counts else ("ul", got))
        elif INDENTED.match(line):
            body = []
            while i < len(lines) and (INDENTED.match(lines[i]) or not lines[i].strip()):
                body.append(lines[i][4:])
                i += 1
            while body and not body[-1].strip():
                body.pop()
            out.append(("pre", "\n".join(body)))
        elif grid(i):
            rows, i = [cells(line)], i + 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                rows.append(cells(lines[i]))
                i += 1
            out.append(("table", rows))
        else:
            para, under = [], False
            while i < len(lines) and lines[i].strip():
                if para and UNDER.match(lines[i]):
                    under, i = True, i + 1
                    break
                if para and (interrupts(lines[i]) or grid(i)):
                    break
                para.append(lines[i].strip())
                i += 1
            text = "\n".join(para)
            if under:
                out.append(("h", text))
            elif top and (m := LABEL.match(text)):
                out.append(("label", m.group(1)))
            elif top and (m := MOVED.match(text)):
                out += [("label", m.group(1)), ("p", m.group(2))]
            else:
                out.append(("p", text))
            if out[-1][0] == "p":
                out += [("hand", h) for h in handed(out[-1][1])]
    return out


def handed(text: str) -> list:
    """Each hand-off a paragraph writes, in order, as (how, session, words):
    a command to type, its session "" for this page's own; my verdicts on
    a session's page; a file to paste elsewhere."""
    found = ([(m.start(), ("type", m.group(2) or "", m.group(1))) for m in TYPED.finditer(text)]
             + [(m.start(), ("answers", m.group(1), "")) for m in VERDICTS.finditer(text)]
             + [(m.start(), ("file", "", m.group(1))) for m in FILED.finditer(text)])
    return [h for _, h in sorted(found)]


def listing(kind: str, got, depth: int, own: str = "") -> str:
    """A list, as the pane numbers it: from its own first number, then a,
    b, c one list down, then i, ii, iii. `own` is block()'s."""
    items = got[1] if kind == "ol" else got
    head = "<ul>"
    if kind == "ol":
        start, last = got[0], got[0] + len(got[1]) - 1
        style = "a" if depth == 1 and start >= 1 else "i" if depth == 2 and start >= 1 and last <= 3999 else ""
        head = f'<ol start="{start}"' + (f' type="{style}"' if style else "") + ">"
    li = lambda b: (inline(b[0][1]) if len(b) == 1 and b[0][0] == "p"
                    else "".join(block(*x, depth=depth + 1, own=own) for x in b))
    return head + "".join(f"<li>{li(b)}</li>" for b in items) + f"</{kind}>"


def block(kind: str, got, depth: int = 0, own: str = "") -> str:
    """One block, drawn. `own` is the number of the session whose page
    draws it, so its own hand-off reads Send, as group() says."""
    if kind == "table":
        row = lambda r, tag: "<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>"
        return (f'<div class="fence"><div class="grid"><table><thead>{row(got[0], "th")}</thead>'
                f'<tbody>{"".join(row(r, "td") for r in got[1:])}</tbody></table></div></div>')
    if kind in ("ul", "ol"):
        return listing(kind, got, depth, own)
    if kind == "quote":
        return "<blockquote>" + "".join(block(*b, own=own) for b in got) + "</blockquote>"
    if kind == "hr":
        return "<hr>"
    if kind == "h":
        return f"<h3>{inline(got)}</h3>"
    if kind == "label":
        return f'<div class="lab">{inline(got)}</div>'
    if kind == "pre":
        return f'<div class="fence"><pre>{esc(got)}</pre></div>'
    if kind == "copy":
        return f'<div class="copy"><div class="txt">{esc(got)}</div>{page.CP}</div>'
    if kind == "paste":
        to, words = got
        return (f'<div class="copy to"><div class="txt">{esc(words)}</div>'
                f'{group(sign("type", to, words), to, own)}</div>')
    if kind == "hand":
        return handoff(*got, own=own)
    return f"<p>{inline(got)}</p>"


def group(key: str, to: str, own: str = "") -> str:
    """A hand-off's group, one width each (page rules 4 and 40): Copy, Type,
    then Send, naming its receiver unless it is this page's own session,
    `own`, and wearing its colour. The group names the hand-off by its key
    alone."""
    send = (f'<button class="{page.into(to)}" data-send="yes">{page.icon("send", 11)}Send to {to}</button>'
            if to and to != own
            else f'<button class="btn go own" data-send="yes">{page.icon("send", 11)}Send</button>')
    return f'<span class="group" data-hand="{key}">{page.CP}<button class="btn">Type</button>{send}</span>'


def handoff(how: str, to: str, words: str, own: str = "") -> str:
    """A hand-off written inside a paragraph, its buttons under it. A
    command: group()'s three. My verdicts: Send answers to NN, greyed while
    an item there has neither an answer nor a proposal. A file: Copy file,
    holding its words as they read now."""
    key = sign(how, to, words)
    if how == "file":
        text = filed(words)
        return "" if text is None else (f'<div class="hand"><div class="txt" hidden>{esc(text)}</div>'
                                        + page.CP.replace("<span>Copy</span>", "<span>Copy file</span>") + "</div>")
    if how == "answers":
        off = "" if clarify.ready(to) else " disabled"
        return (f'<div class="hand"><span class="group" data-hand="{key}"><button class="{page.into(to)}" '
                f'data-send="yes"{off}>{page.icon("send", 11)}Send answers to {to}</button></span></div>')
    return f'<div class="hand"><div class="txt" hidden>{esc(words)}</div>{group(key, to, own)}</div>'


def filed(path: str):
    """The words of a file a hand-off names, while it sits inside the project
    and reads as text. None otherwise, and for a .env file, since it holds
    secrets: blurb.py refuses one alike."""
    root = os.path.realpath(registry.ROOT)
    whole = os.path.realpath(os.path.join(root, path))
    if (not whole.startswith(root + os.sep) or not os.path.isfile(whole)
            or os.path.basename(whole).startswith(".env")):
        return None
    try:
        with open(whole) as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def reply(text: str, own: str = "") -> str:
    """Its last words, as a card. "Your move" and what follows is boxed.
    `own` is block()'s."""
    found = blocks(text)
    at = next((i for i, (k, t) in enumerate(found) if k == "label" and MOVE.match(t)), -1)
    body = "".join(block(*b, own=own) for b in (found if at < 0 else found[:at]))
    move = "" if at < 0 else ('<div class="move"><div class="lab">Your move</div>'
                              + "".join(block(*b, own=own) for b in found[at + 1:]) + "</div>")
    return f'<div class="reply">{body}{move}</div>'


def sign(how: str, to: str, words: str) -> str:
    """A hand-off's key: the page names a hand-off by it, and the server finds it again."""
    return hashlib.sha1(f"{how}\n{to}\n{words}".encode()).hexdigest()[:12]


def handoffs(found: list) -> list:
    """Every hand-off among blocks, as (how, session, words), inside lists
    and quotes too. A copy block under "Send to session 12." types, as a
    command does."""
    out = []
    for kind, got in found:
        if kind == "paste":
            out.append(("type", *got))
        elif kind == "hand":
            out.append(got)
        elif kind == "quote":
            out += handoffs(got)
        elif kind in ("ul", "ol"):
            for b in got[1] if kind == "ol" else got:
                out += handoffs(b)
    return out


def aimed(nn: str, key: str) -> tuple:
    """A hand-off, found again by its key in session NN's transcript, newest
    first, as (how, session, words). The words come from the transcript,
    never from the click, so a click types only what the session wrote."""
    path = located(nn, look=True)
    th = transcripts.thread(path) if path else None
    for t in reversed(th.turns if th else []):
        if t["who"] == "session":
            said = "\n\n".join(s["t"] for s in t["steps"] if s["k"] == "text")
            got = next((h for h in handoffs(blocks(said, False)) if sign(*h) == key), None)
            if got:
                return got
    return "", "", ""


def hand(nn: str, form: dict) -> str:
    """A hand-off's button, pressed in session NN's transcript.

    Type and Send work as the stage page's pair: Type leaves the words in
    the pane of the session they are for, this one's when none is named,
    no Return; Send types them and presses Return, or Return alone right
    after its own Type. Working, that session reads them once it can. Send
    answers is the clarify page's own take_all, on the named session's
    wave. A pane gone, Claude gone or a dialog waiting there refuses, in one
    sentence, and nothing is typed."""
    get = lambda k: (form.get(k) or [""])[0]
    how, to, words = aimed(nn, get("key"))
    if how == "answers":
        return clarify.take_all(to)
    if how != "type":
        return "That hand-off is no longer in the transcript. Reload the page."
    to = to or nn
    why, _, pane = page.typable(to, ("idle", "shell", "busy"))
    if why:
        return why
    send = get("send") == "yes"
    text = "" if send and get("only") == "return" else words
    return serve.Typing(lambda: "" if panes.say(pane, text, enter=send) else page.gone(to))


# ---- the turns --------------------------------------------------------------------

# A command I typed, or one a page typed for me, reads as a command.
COMMAND = re.compile(r"^(/[\w:-]+)(?=\s|$)\s*([\s\S]*)$")


def tag_of(nn: str) -> str:
    """The session as its turns name it: 81-C1, its number alone once it ended."""
    held = registry.entries()
    return plans.tag(nn, plans.owners(held)) if nn in held else nn


def worked(seconds: float) -> str:
    s = round(seconds)
    if s < 60:
        return f"{s} s"
    m = round(s / 60)
    return f"{m} min" if m < 60 else f"{m // 60} h {m % 60} min"


def thumb(nn: str, at: int, k: int, w: int, h: int) -> str:
    """A picture, its box held at its size before it loads. A tap opens it."""
    src = f"{serve.address('transcript', nn)}/pic/{at}/{k}"
    size = f' width="{w}" height="{h}"' if w and h else ""
    return (f'<button class="b0 pic" data-src="{src}" aria-label="Picture {k + 1}">'
            f'<img src="{src}"{size} alt="" loading="lazy"></button>')


def number(n: int) -> str:
    return f'<span class="n">#{n}</span>' if n else ""


def mark(html: str) -> str:
    """A piece's mark: a hash of what it draws. A told page sends back the
    marks it shows, and a piece whose mark still holds goes as its mark alone."""
    return hashlib.sha1(html.encode()).hexdigest()[:8]


def yours(i: int, n: int, t: dict, nn: str, have: list | None = None) -> str:
    text = re.sub(r"\[Image #\d+\]\s*", "", t["text"]).strip()
    cmd = COMMAND.match(text)
    said = (f'<div class="said"><code class="cmd">{esc(text)}</code></div>' if t.get("shell")
            else f'<div class="said"><code class="cmd">{esc(cmd.group(1))}</code>'
            f'{" " + esc(cmd.group(2)) if cmd.group(2) else ""}</div>' if cmd
            else f'<div class="said">{esc(text)}</div>' if text else "")
    pics = "".join(thumb(nn, *p) for p in t["pics"])
    # What one of Claude Code's own commands answered, beneath it.
    out = f'<div class="out"><pre>{esc(cut(t["out"]))}</pre></div>' if t.get("out") else ""
    who = f"Session {t['from']} · report" if t["from"] else "You"
    # Mine alone are the lines the up arrow brings back.
    cls = f'turn you{"" if t["from"] else " mine"}'
    inner = (f'<header><b class="by">{esc(who)}</b><span class="at">{esc(t["at"])}</span>{number(n)}</header>'
             f'{said}{out}' + (f'<div class="pics">{pics}</div>' if pics else ""))
    h = mark(cls + inner)
    if have == [h]:
        return f'<section class="{cls}" data-i="{i}" data-h="{h}" data-same></section>'
    return f'<section class="{cls}" data-i="{i}" data-h="{h}">{inner}</section>'


def row(s: dict) -> str:
    """One step as one line, and the detail it unfolds to. A file's and a
    call's detail is read from disk once opened; a skill's is its words."""
    bad = '<span class="bad">failed</span>' if s["err"] else ""
    uid = esc(s["id"])
    if s["k"] == "skill":
        rest = f'<span class="rest">{esc(s["args"])}</span>' if s["args"] else ""
        detail = (f'<div class="detail" data-got="1" hidden><div class="k">Its words</div>'
                  f'<pre>{esc(s["args"])}</pre></div>' if s["args"] else "")
        return (f'<button class="b0 row did" data-id="{uid}" aria-expanded="false">{page.icon("command", 15)}'
                f'<span class="what">Ran /{esc(s["name"])}</span>{rest}</button>{detail}')
    if s["k"] == "file":
        cut = s["path"].rfind("/")
        tail = f'{s["add"]} lines' if s["verb"] == "wrote" else f'+{s["add"]} −{s["del"]}'
        return (f'<button class="b0 row did" data-id="{uid}" aria-expanded="false" title="{esc(s["path"])}">'
                f'{page.icon(s["verb"], 15)}<span class="what">{"Wrote" if s["verb"] == "wrote" else "Edited"} '
                f'{esc(s["path"][cut + 1:])}</span><span class="rest">{esc(s["path"][:max(cut, 0)])}</span>'
                f'<span class="tail">{tail}</span>{bad}</button><div class="detail" hidden></div>')
    return (f'<button class="b0 row call" data-id="{uid}" aria-expanded="false">{page.icon(s["tool"], 15)}'
            f'<span class="rest">{esc(s["say"])}</span>{bad}</button><div class="detail" hidden></div>')


# How a call sent to the background ended, as its notice says it.
ENDS = {"completed": "Done", "failed": "Failed", "killed": "Stopped"}
# The harness's words for a command that printed nothing.
QUIET = "(Bash completed with no output)"


def came_back(s: dict) -> str:
    """What a command or an agent gave back, under its line: running, how a
    call sent to the background ended, else what came back's first lines."""
    if s["out"] < 0 or (s["bg"] and not s["done"]):
        return '<div class="peek run"><i></i>Running…</div>'
    if s["bg"]:
        end = ENDS.get(s["done"], s["done"].capitalize())
        if s["tool"] == "agent" and s.get("used"):
            end += f' · {s["used"]} step{"s" if s["used"] != 1 else ""} · {worked(s.get("took", 0))}'
        return f'<div class="peek{" bad" if s["done"] in ("failed", "killed") else ""}">{esc(end)}</div>'
    lines, more = s["peek"] or ([], 0)
    if not lines or lines == [QUIET]:
        return '<div class="peek">No output</div>'
    rest = f'<span class="more">+{more} line{"s" if more != 1 else ""}</span>' if more else ""
    return f'<div class="peek"><pre>{esc(chr(10).join(lines))}</pre>{rest}</div>'


def loud(s: dict) -> str:
    """A command or an agent: a line of its own, its kind named, and what
    came back beneath it. A tap unfolds the whole of what went in and out."""
    bad = '<span class="bad">failed</span>' if s["err"] else ""
    return (f'<button class="b0 row call loud {s["tool"]}" data-id="{esc(s["id"])}" aria-expanded="false">'
            f'{page.icon(s["tool"], 15)}<span class="what">{"Command" if s["tool"] == "command" else "Agent"}</span>'
            f'<span class="rest">{esc(s["say"])}</span>{bad}</button><div class="detail" hidden></div>{came_back(s)}')


def fold(run: list) -> str:
    """A run of finished calls as one line: how many, and of what, in words (rule 8)."""
    kinds: dict = {}
    for s in run:
        kinds[s["tool"]] = kinds.get(s["tool"], 0) + 1
    words = " · ".join(f"{n} {WORDS[k][0 if n == 1 else 1]}" for k, n in kinds.items())
    return (f'<button class="b0 row fold" data-id="f:{esc(run[0]["id"])}" aria-expanded="false">'
            f'{page.icon("right", 15, "i shut")}{page.icon("down", 15, "i open")}<span class="what">{len(run)} steps</span>'
            f'<span class="rest">{words}</span></button>'
            f'<div class="sub" hidden>{"".join(row(s) for s in run)}</div>')


# What a wake from an agent says happened. Any other says how its call ended.
WOKE = {"report": "Report", "message": "Message", "waiting": "Still working"}


def woke(s: dict) -> str:
    """A wake: a line across the turn, its time and what woke it, then what
    happened. One that brought words unfolds to them, read from disk only
    then."""
    call = s["call"] or {}
    tool = call.get("tool") or ("agent" if s["how"] in WOKE else "other")
    word = WOKE.get(s["how"]) or ENDS.get(call.get("done", ""), "Ended")
    used = call.get("used", 0)
    tail = f'{used} step{"s" if used != 1 else ""} · {worked(call.get("took", 0))}' if tool == "agent" and used else ""
    line = f'<div class="wake"><b>{esc(s["at"])}</b><span>{esc(call.get("say") or s["name"] or "A task")}</span></div>'
    what = f'{page.icon(tool, 15)}<span class="what">{word}</span><span class="rest">{esc(tail)}</span>'
    if not s["has"]:
        return line + f'<div class="row wk {tool}">{what}</div>'
    return (line + f'<button class="b0 row wk {tool}" data-id="{esc(s["id"])}" aria-expanded="false">{what}'
            f'{page.icon("right", 15, "i shut")}{page.icon("down", 15, "i open")}</button>'
            '<div class="detail" hidden></div>')


def stretch(steps: list, own: str = "") -> list:
    """The session's work from a wake to the next, in order: its notes and
    acts, then its reply, the words after its last act. `own` is the
    session's number, block()'s."""
    last = max((k for k, s in enumerate(steps) if s["k"] != "text"), default=-1)
    out, run = [], []
    for s in steps[:last + 1] + [None]:
        if s is not None and s["k"] == "call" and s["tool"] not in transcripts.LOUD:
            run.append(s)
            continue
        if run:
            out.append(row(run[0]) if len(run) == 1 else fold(run))
            run = []
        if s is None:
            break
        if s["k"] == "text":
            out += [f'<div class="nt">{inline(t) if k == "p" else block(k, t, own=own)}</div>'
                    for k, t in blocks(s["t"], False)]
        elif s["k"] == "call":
            out.append(loud(s))
        elif s["k"] == "arrived":
            out.append(woke(s))
        else:
            out.append(row(s))
    words = [s["t"] for s in steps[last + 1:]]
    if words:
        out.append(reply("\n\n".join(words), own))
    return out


def theirs(i: int, n: int, t: dict, tag: str, have: list | None = None, own: str = "") -> str:
    """The session's turn, each piece of its thread wearing its mark: a
    piece `have` already shows, unmoved at its place, goes as its mark alone.
    `own` is the session's number, block()'s."""
    steps, out, cut = t["steps"], [], 0
    for k, s in enumerate(steps + [None]):
        if s is None or s["k"] == "wake":
            out += stretch(steps[cut:k], own)
            out += [woke(s)] if s else []
            cut = k + 1
    took = (t["end"] - t["start"]).total_seconds() if t["start"] and t["end"] else 0
    have = have or []
    pieces = "".join(f'<div class="pc" data-h="{h}" data-same></div>' if j < len(have) and have[j] == h
                     else f'<div class="pc" data-h="{h}">{p}</div>'
                     for j, (h, p) in enumerate((mark(p), p) for p in out))
    return (f'<section class="turn ses" data-i="{i}"><header><b class="by">{esc(tag)}</b>'
            f'<span class="at">{esc(t["at"])}</span>'
            + (f'<span class="at">· worked {worked(took)}</span>' if took >= 1 else "")
            + f'{number(n)}</header><div class="thread">{pieces}</div></section>')


def drawn(nn: str, th, first: int = 0, have: dict | None = None) -> str:
    """Every turn from `first` on, and each turn `have` names, numbered as
    the copy numbers it. A prompt I took back is skipped, as the pane no
    longer shows it. `have` holds the marks a told page shows, by turn."""
    tag, out, idle = tag_of(nn), [], status(nn) == "idle"
    for i, t, n in th.numbered(idle):
        if i >= first or i in (have or {}):
            out.append(yours(i, n, t, nn, (have or {}).get(i)) if t["who"] == "you"
                       else theirs(i, n, t, tag, (have or {}).get(i), nn))
    return "".join(out)


def queued(th) -> str:
    """My lines typed while it worked, at the foot, until it reads them."""
    return '<div id="queued">' + "".join(
        f'<section class="turn you queued"><header><b class="by">You</b>'
        f'<span class="at">Queued · it reads this when its turn ends</span></header>'
        f'<div class="said">{esc(s)}</div></section>' for s in th.waiting()) + "</div>"


def running(th, nn: str, now: str) -> str:
    """Everything still running, counted and named, at the transcript's
    foot: each agent, command, browser script and wait it sent to the
    background, whatever its state. A server never shows. An agent it
    waits on inside its turn shows only while it works."""
    mine = registry.entries().get(nn) or {}
    rec = registry.claude_records().get(mine.get("session_id")) if mine else None
    steps = th.running(wake.started(rec)) if th and rec else []
    steps += [s for s in th.calls.values() if s["k"] == "call" and s["tool"] == "agent"
              and s["out"] < 0] if th and now == "working" else []
    if not steps:
        return '<div id="running"></div>'
    return (f'<div id="running"><div class="running"><div class="rh"><i></i>{len(steps)} running</div>'
            + "".join(f'<div class="rn">{page.icon(s["tool"], 14)}<span>{esc(s["say"])}</span></div>'
                      for s in steps)
            + "</div></div>")


def state(nn: str) -> str:
    """The session's state, as the rail reads it: working, idle, waiting,
    closed or gone. It colours the newest turn's edge, and shows nowhere
    else: the rail and the tab already wear it."""
    mine = registry.entries().get(nn)
    rec = registry.claude_records().get(mine.get("session_id")) if mine else None
    return page.shown(nn, mine, rec)[1] if mine else "gone"


# ---- the page, and what it asks for -------------------------------------------------

# Claude Code's own commands that need no picker, after my skills in the /
# menu, each in its docs' words.
COMMANDS = [("clear", "Start a new conversation with empty context."),
            ("compact", "Free up context by summarizing the conversation so far."),
            ("context", "Visualize current context usage as a colored grid.")]

def render(nn: str) -> str:
    path = located(nn, look=True)
    th = transcripts.thread(path) if path else None
    turns = drawn(nn, th) if th else ""
    empty = f"Session {nn} has no transcript." if not path else "Nothing said yet."
    now = state(nn)
    menu = [(name, re.split(r"(?<=\.)\s", said, maxsplit=1)[0]) for name, said, _ in skills_page.heads()] + COMMANDS
    # A hand-off's Send into this session wears its colour: steers, gold.
    steers = " data-steers" if page.into(nn) == "btn ask" else ""
    # The advisor's turns sit under its panel.
    adv = advisor.seat(nn)
    body = (STYLE + f'<div class="tx" id="tx" data-state="{esc(now)}" data-claude="{esc(status(nn))}"'
            f' data-t="{esc(os.path.basename(path))}"{steers}>'
            + (f'<div class="tp">{advisor.panel(nn)}' if adv else "") + '<div class="scroll" id="scroll">'
            f'<div id="turns">{turns}</div>' + running(th, nn, now)
            + (queued(th) if th else '<div id="queued"></div>') + f'{page.blank(empty)}</div>'
            + ("</div>" if adv else "")
            + BOX.format(nn=nn, clip=page.icon("clip", 16), play=page.icon("play", 16), more=page.icon("more", 20),
                         up=page.icon("up", 20), down=page.icon("down", 20), meter=meter(nn)) + "</div>"
            + f'<div class="viewer" id="viewer" hidden><img alt=""><button class="b0 shut" aria-label="Close">'
            f'{page.icon("close", 20)}</button></div>' + page.ANYWHERE + page.COPY + page.TYPING + HAND
            + SCRIPT.replace("%BASE%", json.dumps(serve.address("transcript", nn)))
            .replace("%ICONS%", json.dumps({"file": page.icon("read", 18), "x": page.icon("close", 16)}))
            .replace("%SKILLS%", json.dumps(menu).replace("</", "<\\/")) + page.watch(key(nn)))
    return page.render(f"{nn}-transcript", [("", body)], refresh=0)


def meter(nn: str) -> str:
    """What its status line last printed, atop the menu, whole. Nothing
    kept yet, nothing shows."""
    try:
        with open(os.path.join(registry.folder(nn), registry.STATUSLINE)) as f:
            lines = [transcripts.ANSI.sub("", line).strip() for line in f.read().splitlines()]
    except OSError:
        lines = []
    return '<div class="meter" id="meter">' + "".join(f"<div>{esc(line)}</div>" for line in lines if line) + "</div>"


def tail(nn: str, first: int, have: dict) -> str:
    """The turns from `first` on, and each `have` names, what still runs,
    what waits queued, and the session's state: what a told page draws
    again. The advisor's adds its panel's rows."""
    path, now = located(nn), state(nn)
    th = transcripts.thread(path)
    return (f'<div id="tail" data-state="{esc(now)}" data-claude="{esc(status(nn))}"'
            f' data-t="{esc(os.path.basename(path))}">{drawn(nn, th, first, have)}</div>'
            f'{running(th, nn, now)}{queued(th)}{meter(nn)}' + (advisor.rows(nn) if advisor.seat(nn) else ""))


def marks(asked: str) -> dict:
    """The marks a told page shows, by turn, as it asks: 4:a1b2c3d4~9:e5f6a7b8.c9d0e1f2."""
    out = {}
    for part in asked.split("~"):
        i, _, got = part.partition(":")
        if i.isdigit():
            out[int(i)] = got.split(".") if got else []
    return out


def cut(text: str) -> str:
    return text if len(text) <= SHOWN else text[:SHOWN] + "\n…"


def detail(nn: str, uid: str) -> str:
    """What one call was handed and what came back, or a file's change."""
    path = located(nn)
    step = transcripts.thread(path).calls.get(uid) if path else None
    if not step:
        return '<div class="k">Not in this transcript</div>'
    if step["k"] in ("wake", "arrived"):
        words = transcripts.brought(path, step)
        return (f'<div class="reply">{"".join(block(*b, own=nn) for b in blocks(cut(words)))}</div>' if words
                else '<div class="k">It brought nothing to read</div>')
    name, got, back = transcripts.call_of(path, step)
    part = lambda k, text: f'<div class="k">{k}</div><pre>{esc(cut(str(text)))}</pre>'
    if step["k"] == "file":
        edits = got.get("edits") if name == "MultiEdit" else [got] if name == "Edit" else []
        out = "".join(part("Before", e.get("old_string", "")) + part("After", e.get("new_string", ""))
                      for e in edits if isinstance(e, dict))
        if name == "Write":
            out = part("Its first lines", "\n".join(str(got.get("content", "")).split("\n")[:60]))
        elif name == "NotebookEdit":
            out = part("After", got.get("new_source", ""))
        return out + (part("What came back", back) if step["err"] and back else "")
    sent = transcripts.went_in(name, got)
    # An agent sent to the background hands back only Claude Code's own note
    # here. Its report arrives later, at its wake.
    if step.get("tool") == "agent" and step.get("bg"):
        return part("What went in", sent)
    pics = [(step["out"], k, *transcripts.dimensions(s))
            for k, s in enumerate(transcripts.images(transcripts.record(path, step["out"])))] if step["pics"] else []
    said = back if back else "A picture." if pics else "Still running." if back is None else "Nothing."
    # A call still running is read again by an open page each time it is
    # told, never kept: data-live.
    live = '<i data-live hidden></i>' if back is None and not pics else ""
    return ((part("What went in", sent) if sent else "") + part("What came back", said) + live
            + (f'<div class="pics small">{"".join(thumb(nn, *p) for p in pics)}</div>' if pics else ""))


def picture(nn: str, at: str, k: str):
    """One picture a record carries, as its bytes and their type."""
    path = located(nn)
    found = transcripts.images(transcripts.record(path, int(at))) if path and at.isdigit() else []
    if not k.isdigit() or int(k) >= len(found):
        return b"", "text/plain; charset=utf-8"
    s = found[int(k)]
    try:
        return base64.b64decode(str(s.get("data", ""))), str(s.get("media_type") or "image/png")
    except ValueError:
        return b"", "text/plain; charset=utf-8"


def answer(nn: str, rest: str, query: str):
    """The page, or one of its parts: /tail, /pane, /step/ID, /pic/AT/K."""
    if not rest:
        return render(nn)
    if rest == "/pane":
        return offer(nn)
    if rest == "/tail":
        q = urllib.parse.parse_qs(query)
        first = (q.get("from") or ["0"])[0]
        return tail(nn, int(first) if first.isdigit() else 0, marks((q.get("have") or [""])[0]))
    if m := re.fullmatch(r"/step/([\w-]+)", rest):
        return detail(nn, m.group(1))
    if m := re.fullmatch(r"/pic/(\d+)/(\d+)", rest):
        return picture(nn, m.group(1), m.group(2))
    return None


# ---- what only its pane shows: a suggested reply, a dialog ------------------------------

# A dialog's choice, as "❯ 1. Yes", the arrow on the one picked.
CHOICE = re.compile(r"^\s*(?:❯\s*)?([1-9])\.\s+(.*?)(?:\s+·)?\s*$")
# A rule across the pane: above its prompt, beneath it, and above a dialog.
RULE = re.compile(r"^\s*─{8,}")
# The dashes around a command a permission dialog quotes.
DASHED = re.compile(r"^\s*╌{8,}$")
# The grey Claude Code draws a choice's note in, beneath its label.
GREY = "153,153,153"
# The choice that opens a field inside a question's dialog, for my own words.
FREE = "Type something."
# A permission dialog's foot, when its last choice, No, carries my reason.
AMEND = "Tab to amend"
# The mode on the pane's foot, as "⏵⏵ auto mode on" or "⏸ plan mode on".
MODE = re.compile(r"(?:⏸|⏵⏵)\s+(.+?)\s+on\b")


def pane_of(nn: str) -> str:
    """Session NN's pane, read as a page reads it, at most panes.FRESH old."""
    mine = registry.entries().get(nn)
    rec = registry.claude_records().get(mine.get("session_id")) if mine else None
    return panes.pane(mine, int(rec["pid"]), panes.FRESH) if rec else ""


def screen(nn: str) -> list:
    """Session NN's pane, as iTerm draws it: each line as runs of one look."""
    pane = pane_of(nn)
    return iterm.screen(pane) if pane else []


def text_of(runs: list) -> str:
    return "".join(r[0] for r in runs).rstrip()


def hint(lines: list) -> str:
    """The reply Claude Code suggests: faint text alone on its prompt, the
    lines between the rule above it and the one beneath. Words typed there,
    in the pane, mean none."""
    texts = [text_of(runs) for runs in lines]
    at = next((i for i in range(len(texts) - 1, 0, -1)
               if texts[i].lstrip().startswith("❯") and RULE.match(texts[i - 1])), -1)
    faint, typed = [], ""
    for i in range(at, len(lines)) if at > 0 else ():
        if i > at and RULE.match(texts[i]):
            break
        faint.append("".join(t for t, _, dim in lines[i] if dim))
        typed += "".join(t for t, _, dim in lines[i] if not dim)
    return "" if typed.replace("❯", "").strip() else " ".join(" ".join(faint).split())


def ask(lines: list) -> tuple:
    """A dialog waiting at the screen's foot: its words, line by line, its
    choices as [number, label, note], and its foot. Nothing, unless its
    foot says how to close it."""
    texts = [text_of(runs) for runs in lines]
    first = next((i for i in range(len(texts) - 1, -1, -1)
                  if (m := CHOICE.match(texts[i])) and m.group(1) == "1"), -1)
    if first < 0:
        return [], [], ""
    top = next((i for i in range(first - 1, -1, -1) if RULE.match(texts[i])), -1)
    words = [t.strip() for t in texts[top + 1:first] if t.strip() and not DASHED.match(t)]
    choices, foot = [], ""
    for runs, t in zip(lines[first:], texts[first:]):
        m = CHOICE.match(t)
        if m and int(m.group(1)) == len(choices) + 1:
            # "Yes, and switch to auto mode · auto mode handles…": its label, then its note.
            label, _, note = m.group(2).partition(" · ")
            choices.append([m.group(1), label, note])
        elif not t.strip() or RULE.match(t):
            continue
        elif len(t) - len(t.lstrip()) < 3:
            foot = t.strip()
            break
        else:
            k = 2 if all(c == GREY for s, c, _ in runs if s.strip()) else 1
            choices[-1][k] = f"{choices[-1][k]} {t.strip()}".strip()
    return (words, choices, foot) if "Esc" in foot else ([], [], "")


def mode(lines: list) -> str:
    """The session's mode, as its pane's foot names it, "mode" dropped:
    auto, manual, plan, accept edits. Hidden under a dialog: nothing."""
    found = [m.group(1) for runs in lines if (m := MODE.search(text_of(runs)))]
    return found[-1].removesuffix(" mode") if found else ""


# A session waiting with no choices to read: a panel, as /usage opens. Close
# is Escape there.
PANEL = ('<div class="ask"><div class="q">A panel waits in its pane.</div>'
         '<button class="b0 ch shut"><span>Close</span></button></div>')


def offer(nn: str):
    """What only the pane shows: its mode, in the menu, and above the box a
    dialog waiting, else the reply Claude Code suggests once a turn ends.
    The pane's screen is read off 1100's queue, serve.Typing's, so no page
    waits on iTerm."""
    now = status(nn)
    pane = pane_of(nn) if now in ("idle", "shell", "busy", "waiting") else ""
    return serve.Typing(lambda: offered(now, iterm.screen(pane) if pane else []))


def offered(now: str, lines: list) -> str:
    """offer()'s answer, from the session's status and its pane's screen."""
    words, choices, _ = ask(lines) if now == "waiting" else ([], [], "")
    tip = hint(lines) if now == "idle" and not choices else ""
    shown = [c for c in choices if c[1] != FREE]
    # Its words above its question scroll on their own, a file's preview
    # among them, so the question and its choices always show.
    above = ('<div class="ask">' + (f'<div class="ctx">{esc(chr(10).join(words[:-1]))}</div>' if words[1:] else "")
             + f'<div class="q">{esc(words[-1] if words else "")}</div>'
             + "".join(f'<button class="b0 ch" data-n="{n}"><b>{n}</b><span>{esc(label)}'
                       + (f"<small>{esc(note)}</small>" if note and note != label else "")
                       + "</span></button>" for n, label, note in shown) + "</div>" if shown
             else f'<button class="b0 hint" data-text="{esc(tip)}"><span>{esc(tip)}</span><kbd>Tab</kbd></button>'
             if tip else PANEL if now == "waiting" else "")
    at = mode(lines)
    return (f'<div id="offer">{above}</div>'
            + (f'<button class="b0 mode" id="mode" title="Shift+Tab: its next mode">{esc(at)}</button>' if at else ""))


def amend(nn: str, pane: str, line: str) -> str:
    """My own words into a waiting dialog's own field: its "Type something."
    picked, else its last choice, No, with Tab, then the words and Return."""
    _, choices, foot = ask(screen(nn))
    free = next((n for n, label, _ in choices if label == FREE), "")
    if free:
        done = panes.say(pane, free, enter=False) and panes.say(pane, line)
    elif AMEND in foot and choices and choices[-1][1].startswith("No"):
        done = panes.press(pane, *["down"] * (len(choices) - 1), "tab") and panes.say(pane, line)
    else:
        return "This dialog takes no words. Tap one of its choices."
    return "" if done else page.gone(nn)


# ---- the box I type into ---------------------------------------------------------------

def keep(nn: str, name: str, data: str) -> str:
    """A file from the paperclip, kept in the session's own folder, under
    sent/. A name already there takes a number. Its path, whole."""
    folder = os.path.join(registry.folder(nn), "sent")
    os.makedirs(folder, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", os.path.basename(name)).strip("-.") or "file"
    stem, ext = os.path.splitext(safe)
    path, i = os.path.join(folder, safe), 2
    while os.path.exists(path):
        path, i = os.path.join(folder, f"{stem}-{i}{ext}"), i + 1
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
    return path


def take(nn: str, form: dict) -> str:
    """Send, pressed: my words, then each file's path, typed into the
    session's pane, then Return. Working, it reads the line once its turn
    ends. Whatever would type into the wrong place is refused, in one
    sentence, and nothing is typed. Stop, pressed, is Escape in the pane;
    a choice, pressed, its number; the mode, pressed, Shift+Tab; Close, on
    a panel, Escape; a hand-off's button, hand(); a press on the advisor's
    panel, advisor-page.py's take(). Each types off 1100's draw queue,
    serve.Typing's; the checks, and a file kept, come first, on it."""
    get = lambda k: (form.get(k) or [""])[0]
    if get("act") == "hand":
        return hand(nn, form)
    if get("act") == "advise":
        return advisor.take(nn, form)
    if get("act") == "stop":
        return stop(nn)
    if get("act") == "answer":
        return answered(nn, get("n"))
    if get("act") == "mode":
        return moved(nn)
    if get("act") == "close":
        return shut(nn)
    if get("act") != "send":
        return ""
    text, files = get("text").strip(), list(zip(form.get("name", []), form.get("data", [])))
    if not text and not files:
        return ""
    # A dialog waiting takes my words into its own field.
    asked = status(nn) == "waiting"
    why, _, pane = page.typable(nn, ("waiting",) if asked else ("idle", "shell", "busy"))
    if why:
        return why
    try:
        paths = [keep(nn, name, data) for name, data in files]
    except (OSError, ValueError):
        return "A file could not be kept. Nothing was typed."
    line = " ".join([text] + paths if text else paths)
    if asked:
        return serve.Typing(lambda: amend(nn, pane, line))
    return serve.Typing(lambda: "" if panes.say(pane, line) else page.gone(nn))


def stop(nn: str) -> str:
    """Escape, pressed in the pane of a session at work: its turn stops.
    Its turn already over, nothing is pressed."""
    if status(nn) != "busy":
        return f"Session {nn} is not working. Nothing was stopped."
    why, _, pane = page.typable(nn, ("busy",))
    if why:
        return why
    return serve.Typing(lambda: "" if panes.press(pane, "escape") else page.gone(nn))


def moved(nn: str) -> str:
    """Shift+Tab, pressed in the pane: the session's next mode. Never while
    a dialog waits, where Shift+Tab answers it."""
    why, _, pane = page.typable(nn, ("idle", "shell", "busy"))
    if why:
        return why
    return serve.Typing(lambda: "" if panes.press(pane, "shift-tab") else page.gone(nn))


def shut(nn: str) -> str:
    """Escape, pressed in the pane while a panel waits there: it closes."""
    if status(nn) != "waiting":
        return f"Nothing waits in session {nn}. Nothing was pressed."
    why, _, pane = page.typable(nn, ("waiting",))
    if why:
        return why
    return serve.Typing(lambda: "" if panes.press(pane, "escape") else page.gone(nn))


def answered(nn: str, n: str) -> str:
    """A dialog's choice, its number typed into the pane, as my keyboard
    would. Its dialog already closed, nothing is typed."""
    if not re.fullmatch(r"[1-9]", n):
        return ""
    if status(nn) != "waiting":
        return f"No dialog waits in session {nn}. Nothing was typed."
    why, _, pane = page.typable(nn, ("waiting",))
    if why:
        return why
    return serve.Typing(lambda: "" if panes.say(pane, n, enter=False) else page.gone(nn))


BOX = """<div class="box" id="box"><div class="menu" id="menu" hidden></div><div id="offer"></div>
<div class="att" id="att" hidden></div><p class="why" id="why" hidden></p>
<div class="pop" id="pop" hidden>{meter}
<button class="b0 item" id="mode" title="Shift+Tab: its next mode" hidden>{play}<span>Mode</span><b id="modev"></b></button>
<button class="b0 item" id="clip">{clip}<span>Attach a photo or a file</span></button></div>
<div class="line"><button class="b0 more" id="more" aria-label="Status, mode and attach" aria-expanded="false">{more}</button>
<button class="b0 jump" id="prev" aria-label="Previous prompt" title="Previous prompt" disabled>{up}</button>
<button class="b0 jump" id="next" aria-label="Next prompt" title="Next prompt" disabled>{down}</button>
<textarea id="words" rows="1" placeholder="Type or dictate" aria-label="A line for session {nn}"></textarea>
<button class="b0 send" id="send" disabled>Send</button></div>
<input id="pick" type="file" multiple hidden></div>"""


# ---- the look: page.py's tokens, then the transcript's own -----------------------------

STYLE = """<style>
  body > main { padding:0; overflow:hidden; display:flex; flex-direction:column; }
  .b0 { font:inherit; color:inherit; background:none; border:0; margin:0; padding:0; border-radius:4px;
    cursor:pointer; text-align:left; touch-action:manipulation; }
  .b0:focus-visible { outline:2px solid var(--blue); outline-offset:1px; }

  /* The transcript: it scrolls as one, the box beneath it stays (rule 18). */
  .tx { flex:1; min-width:0; min-height:0; display:flex; flex-direction:column; }
  .tx .scroll { flex:1; min-height:0; overflow-y:auto; overscroll-behavior:contain; padding:12px 14px 18px; }
  .tx .empty { min-height:100%; }
  #turns:not(:empty) ~ .empty, #queued:not(:empty) ~ .empty { display:none; }

  /* A turn. Its edge says who: white, mine; grey, the session's. Its newest
     turn, while nothing follows it, wears its state: green working, red
     stopped, as on 1100's rail. */
  .turn { margin:0 0 14px; padding:8px 12px 10px; border-left:3px solid var(--e); border-radius:2px 6px 6px 2px; }
  #turns > .turn:last-child, #queued > .turn:last-child { margin-bottom:0; }
  #turns:not(:empty) ~ #running:not(:empty), #turns:not(:empty) ~ #queued:not(:empty) { margin-top:14px; }
  .turn.you { --e:#fff; background:var(--panel); }
  .turn.ses { --e:var(--grey); padding-right:0; }
  .tx[data-state="working"] #turns > .turn.ses:last-child { --e:var(--green); }
  .tx[data-state="idle"] #turns > .turn.ses:last-child,
  .tx[data-state="waiting"] #turns > .turn.ses:last-child { --e:var(--red); }
  .turn > header { display:flex; align-items:baseline; gap:8px; min-width:0; margin-bottom:6px; white-space:nowrap; }
  .turn > header .by { font-size:13px; color:var(--e); }
  .turn > header .at { color:var(--dim); font-size:12px; }
  .turn > header .n { margin-left:auto; color:var(--dim); font-size:12px; }
  .turn.ses > header .n { padding-right:12px; }
  .said { font-size:14px; line-height:1.55; white-space:pre-wrap; overflow-wrap:anywhere; }
  .said .cmd { padding:1px 6px; border-radius:4px; background:var(--raised); font-weight:700; }
  /* What one of Claude Code's own commands answered, grey, beneath it. */
  .out { margin-top:6px; padding:1px 0 1px 12px; border-left:1px solid var(--grey); color:var(--dim); }
  .out pre { margin:0; font:inherit; font-size:12px; line-height:1.4; white-space:pre-wrap; overflow-wrap:anywhere; }
  .pics { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
  .pic { display:block; height:150px; overflow:hidden; border:1px solid var(--line); border-radius:6px;
    background:var(--bg); }
  .pic img { display:block; height:100%; width:auto; }
  .pics.small .pic { height:96px; }

  /* What the session said and did, in order. Each piece wears its mark on
     a box that takes no room of its own. */
  .thread { display:flex; flex-direction:column; }
  .pc { display:contents; }
  .nt { position:relative; padding:3px 12px 3px 16px; color:var(--dim); font-size:13px; line-height:1.5;
    overflow-wrap:anywhere; }
  .nt::before { content:""; position:absolute; left:4px; top:11px; width:5px; height:5px; border-radius:50%;
    background:var(--blue); }
  .nt code { padding:0 3px; border-radius:3px; background:var(--raised); font-size:.93em; }
  .nt a { color:var(--blue); }
  div.nt h3 { margin:0; font-size:14px; }
  div.nt > :last-child { margin-bottom:0; }
  .row { display:flex; align-items:center; gap:8px; width:100%; min-width:0; min-height:26px;
    padding:2px 12px 2px 0; font-size:12.5px; white-space:nowrap; }
  .row:hover { background:var(--hover); }
  .row .what { flex:none; font-weight:700; }
  .row .rest { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; color:var(--dim); }
  .row .tail { flex:none; color:var(--dim); font-size:11px; }
  .row.did { color:var(--text); }
  .row.did svg.i { color:var(--blue); }
  .row.call, .row.fold { color:var(--dim); }
  .row .bad { flex:none; color:var(--red); font-size:11px; font-weight:700; }
  /* A command and an agent: a line of its own, its kind named and tinted,
     and what came back beneath it, as my terminal shows it. */
  .row.loud { color:var(--text); }
  .row.loud.command svg.i { color:var(--blue); }
  .row.loud.agent svg.i { color:var(--gold); }
  .peek { margin:0 12px 6px 7px; padding:1px 0 1px 15px; border-left:1px solid var(--grey); color:var(--dim);
    font-size:12px; line-height:1.4; }
  .peek pre { margin:0; font:inherit; white-space:pre-wrap; overflow-wrap:anywhere; }
  .peek .more { display:block; font-size:11px; }
  .peek.bad { color:var(--red); }
  .peek.run { display:flex; align-items:center; gap:7px; color:var(--green); }
  .peek.run i { flex:none; width:7px; height:7px; border-radius:50%; background:currentColor;
    animation:beat 1.4s ease-in-out infinite; }
  @keyframes beat { 50% { opacity:.25; } }
  /* Unfolded, the whole of what came back replaces its first lines. */
  .detail:not([hidden]) + .peek { display:none; }
  .row.fold[aria-expanded="true"] .shut, .row.fold[aria-expanded="false"] .open { display:none; }
  .sub { margin-left:7px; padding-left:10px; border-left:1px dashed var(--grey); }
  .sub[hidden], .detail[hidden] { display:none; }
  .detail { margin:2px 12px 8px 23px; display:flex; flex-direction:column; gap:4px; min-width:0; }
  .detail .k { margin-top:4px; font-size:10px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); font-weight:700; }
  .detail pre { margin:0; padding:8px 10px; background:var(--panel); border:1px solid var(--line);
    border-radius:5px; font:inherit; font-size:12px; line-height:1.4; white-space:pre-wrap; overflow-wrap:anywhere; }
  .detail .reply { margin:2px 0 0; }

  /* A wake: a line across the turn, its time and what woke it, then what
     happened. Its words, when it brought some, unfold beneath. */
  .wake { display:flex; align-items:center; gap:7px; min-width:0; margin:16px 12px 2px 0; color:var(--dim);
    font-size:12px; white-space:nowrap; }
  .wake::before { content:""; flex:0 0 10px; height:1px; background:var(--grey); }
  .wake::after { content:""; flex:1 0 16px; height:1px; background:var(--grey); }
  .wake b { flex:none; color:var(--text); }
  .wake span { min-width:0; overflow:hidden; text-overflow:ellipsis; }
  .row.wk { color:var(--text); }
  div.row.wk:hover { background:none; }
  .row.wk.agent svg.i:first-child { color:var(--gold); }
  .row.wk.command svg.i:first-child { color:var(--blue); }
  .row.wk[aria-expanded="true"] .shut, .row.wk[aria-expanded="false"] .open { display:none; }
  .wake + .row.wk + .detail:not([hidden]) { margin-bottom:10px; }

  /* Everything still running, counted and named, at the transcript's foot. */
  .running { padding:8px 12px 9px; background:var(--panel); border-left:3px solid var(--green);
    border-radius:2px 6px 6px 2px; }
  .running .rh { display:flex; align-items:center; gap:7px; color:var(--green); font-size:13px; font-weight:700; }
  .running .rh i { flex:none; width:7px; height:7px; border-radius:50%; background:currentColor;
    animation:beat 1.4s ease-in-out infinite; }
  .running .rn { display:flex; align-items:center; gap:7px; min-width:0; margin-top:4px; padding-left:14px;
    color:var(--dim); font-size:12.5px; white-space:nowrap; }
  .running .rn svg.i { color:var(--gold); }
  .running .rn span { min-width:0; overflow:hidden; text-overflow:ellipsis; }

  /* Its reply: a card, in the turn's own shape. */
  .reply { margin:6px 12px 2px 0; padding:12px 14px; background:var(--panel); border:1px solid var(--line);
    border-radius:6px; font-size:14px; line-height:1.55; overflow-wrap:anywhere; }
  :is(.reply, .nt) h3 { margin:0 0 8px; font-size:17px; line-height:1.3; }
  :is(.reply, .nt) p { margin:0 0 8px; }
  .reply .lab { margin:14px 0 6px; font-size:11px; letter-spacing:.09em; text-transform:uppercase;
    color:var(--dim); font-weight:700; }
  :is(.reply, .nt) ul, :is(.reply, .nt) ol { margin:0 0 8px; padding-left:22px; }
  :is(.reply, .nt) li { margin:0 0 3px; }
  :is(.reply, .nt) li > ul, :is(.reply, .nt) li > ol { margin:3px 0 0; }
  :is(.reply, .nt) li > :last-child, :is(.reply, .nt) blockquote > :last-child { margin-bottom:0; }
  :is(.reply, .nt) blockquote { margin:0 0 8px; padding:0 0 0 12px; border-left:3px solid var(--line); color:var(--dim); }
  :is(.reply, .nt) hr { margin:10px 0; border:0; border-top:1px solid var(--line); }
  :is(.reply, .nt) .fence { position:relative; margin:4px 0 10px; }
  :is(.reply, .nt) pre { margin:0; padding:8px 10px; background:var(--bg); border:1px solid var(--line);
    border-radius:5px; font:inherit; font-size:12px; line-height:1.4; white-space:pre; overflow-x:auto;
    overflow-wrap:normal; }
  :is(.reply, .nt) .fence.more::after { content:""; position:absolute; top:1px; right:1px; bottom:1px; width:36px;
    border-radius:0 5px 5px 0; background:linear-gradient(to right, rgba(15,17,21,0), var(--bg) 85%);
    pointer-events:none; }
  /* A table: a grid, as wide as its widest cells. Wider than its card, it
     scrolls sideways and fades where more waits, as a fence does. */
  :is(.reply, .nt) .grid { display:inline-block; max-width:100%; vertical-align:top; overflow-x:auto; background:var(--bg);
    border:1px solid var(--line); border-radius:5px; }
  :is(.reply, .nt) table { border-collapse:collapse; font-size:12.5px; line-height:1.4; }
  :is(.reply, .nt) th, :is(.reply, .nt) td { padding:5px 10px; text-align:left; vertical-align:top; white-space:nowrap;
    border-bottom:1px solid var(--line); }
  :is(.reply, .nt) th + th, :is(.reply, .nt) td + td { border-left:1px solid var(--line); }
  :is(.reply, .nt) th { color:var(--dim); font-size:11px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }
  :is(.reply, .nt) tbody tr:last-child td { border-bottom:0; }
  :is(.reply, .nt) code { padding:0 3px; border-radius:3px; background:var(--raised); font-size:.93em; }
  :is(.reply, .nt) a { color:var(--blue); }
  .reply > :last-child, .reply .move > :last-child { margin-bottom:0; }
  .copy { position:relative; margin:6px 0 10px; padding:10px 96px 10px 12px; background:var(--bg);
    border-left:3px solid var(--blue); border-radius:0 5px 5px 0; }
  .copy .txt { white-space:pre-wrap; overflow-wrap:anywhere; }
  .copy > .cp { position:absolute; top:6px; right:6px; }
  /* A paste: Copy, Type and Send to 12 above its words, on the right, and
     the words take the whole width. */
  .copy.to { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:6px; padding:6px 6px 10px 12px; }
  .copy.to .txt { order:1; flex-basis:100%; padding-right:6px; }
  /* A hand-off inside a paragraph: its group under it, on the right. */
  .hand { display:flex; justify-content:flex-end; margin:4px 0 10px; }
  .move { margin-top:14px; padding:10px 12px; background:var(--bg); border:1px solid var(--grey); border-radius:6px; }
  .move .lab { margin:0 0 4px; color:var(--text); }
  .move p { font-weight:700; }

  /* A picture, opened over the page. A tap anywhere closes it. */
  .viewer { position:fixed; inset:0; z-index:20; display:flex; align-items:center; justify-content:center;
    padding:12px; background:#08090c; }
  .viewer[hidden] { display:none; }
  .viewer img { max-width:100%; max-height:100%; object-fit:contain; border-radius:6px; }
  .viewer .shut { position:absolute; top:8px; right:8px; display:inline-flex; align-items:center;
    justify-content:center; width:32px; height:32px; background:var(--raised); border-radius:6px; }

  /* The box I type into, pinned beneath the transcript, on my Mac and my
     phone alike. */
  .box { position:relative; flex:none; display:flex; flex-direction:column; gap:6px;
    padding:6px 8px calc(6px + var(--ib, 0px)); background:var(--panel); border-top:1px solid var(--line); }
  .box .line { display:flex; align-items:flex-end; gap:6px; }
  .box .more, .box .jump { flex:none; display:inline-flex; align-items:center; justify-content:center; width:36px;
    height:36px; color:var(--text); border:1px solid var(--line); border-radius:6px; }
  .box .jump:disabled { opacity:.35; cursor:default; }
  .box textarea { flex:1; min-width:0; height:36px; min-height:36px; resize:none; font:inherit;
    line-height:1.4; padding:7px 10px; border-radius:6px; background:var(--bg); color:var(--text);
    border:2px solid var(--line); }
  .box textarea:focus { outline:none; border-color:var(--blue); }
  .box textarea::placeholder { color:var(--dim); }
  .box .send { flex:none; height:36px; min-width:76px; padding:0 18px; font-size:14px; font-weight:700;
    text-align:center; border-radius:6px; position:relative;
    background:#fff; color:#000; --spin:#000; }
  .box .send:disabled { background:var(--grey); color:var(--text); opacity:.6; cursor:default; }
  /* While it types, its word gives way to a spinner. */
  .box .send.busy:disabled { background:#fff; color:transparent; opacity:1; cursor:progress; }
  .box .send.stop.busy:disabled { background:none; --spin:var(--red); }
  .box .send.busy::after { content:""; position:absolute; inset:0; margin:auto; width:16px; height:16px;
    border-radius:50%; border:2px solid transparent; border-top-color:var(--spin);
    border-right-color:var(--spin); animation:spin .7s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  .box .send.done { background:var(--green); color:var(--bg); opacity:1; }
  .box .send.gone { background:var(--red); color:var(--bg); opacity:1; }
  .box .why { margin:0; color:var(--red); font-size:13px; }
  .box .why[hidden], .box .att[hidden] { display:none; }
  .box .att { display:flex; gap:6px; overflow-x:auto; }
  .box .chipf { flex:none; display:inline-flex; align-items:center; gap:6px; max-width:220px; height:34px;
    padding-left:6px; background:var(--bg); border:1px solid var(--line); border-radius:6px; }
  .box .chipf img { width:24px; height:24px; object-fit:cover; border-radius:4px; }
  .box .chipf .fi { display:inline-flex; color:var(--dim); }
  .box .chipf .nm { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:12px; }
  .box .chipf .x { flex:none; display:inline-flex; align-items:center; justify-content:center; width:32px;
    height:32px; color:var(--dim); }
  /* The menu beside the text, opened above the line: what its status line
     last printed, its mode, a tap moving it on, then the paperclip. As wide
     as its longest line, so each status line keeps to one where it fits. */
  .box .more[aria-expanded="true"] { border-color:var(--blue); }
  .box .pop { position:absolute; left:8px; bottom:calc(100% + 6px); z-index:5; display:flex; flex-direction:column;
    gap:2px; width:max-content; max-width:calc(100% - 16px); padding:6px; background:var(--panel); border:1px solid var(--line);
    border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,.45); }
  .box .pop[hidden], .box .item[hidden] { display:none; }
  .box .meter { margin-bottom:4px; padding:6px 8px 8px; border-bottom:1px solid var(--line); color:var(--dim);
    font-size:13px; line-height:1.5; white-space:pre-wrap; overflow-wrap:anywhere; }
  .box .meter:empty { display:none; }
  .box .item { display:flex; align-items:center; gap:8px; min-height:34px; padding:4px 8px; border-radius:6px;
    font-size:13px; }
  .box .item:hover { background:var(--hover); }
  .box .item b { margin-left:auto; color:var(--dim); font-weight:400; }
  /* Stop: Send, while the session works and the box is empty. */
  .box .send.stop { background:none; color:var(--red); box-shadow:inset 0 0 0 1px var(--red); }

  /* Every skill, under a / opening the box, narrowed as I type. Heights
     share the glass by page.py's --vh, which holds at any zoom of home's. */
  .box .menu { max-height:min(260px, calc(40 * var(--vh, 1vh))); overflow-y:auto; background:var(--bg); border:1px solid var(--line);
    border-radius:6px; }
  .box .menu[hidden] { display:none; }
  .box .sk { display:flex; align-items:baseline; gap:10px; width:100%; min-width:0; padding:6px 10px;
    white-space:nowrap; font-size:13px; }
  .box .sk.on, .box .sk:hover { background:var(--hover); }
  .box .sk b { flex:none; }
  .box .sk span { min-width:0; overflow:hidden; text-overflow:ellipsis; color:var(--dim); font-size:12px; }

  /* What only the pane shows: the reply it suggests, while the box is
     empty, or a dialog waiting, each choice a button. */
  #offer:empty, .box.typed .hint { display:none; }
  .box .hint { display:flex; align-items:center; gap:8px; width:100%; min-width:0; min-height:32px;
    padding:4px 10px; border:1px dashed var(--grey); border-radius:6px; color:var(--dim); font-size:13px; }
  .box .hint span { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .box .hint kbd { flex:none; padding:0 5px; border:1px solid var(--line); border-radius:4px; font:inherit;
    font-size:11px; }
  .box .ask { display:flex; flex-direction:column; gap:4px; padding:8px 10px; background:var(--bg);
    border-left:3px solid var(--red); border-radius:2px 6px 6px 2px; }
  .box .ask { max-height:calc(60 * var(--vh, 1vh)); overflow-y:auto; }
  .box .ask .ctx { flex:none; max-height:calc(22 * var(--vh, 1vh)); overflow-y:auto; padding:6px 8px; background:var(--panel);
    border-radius:4px; color:var(--dim); font-size:12px; line-height:1.4; white-space:pre-wrap; overflow-wrap:anywhere; }
  .box .ask .q { margin:2px 0 4px; font-size:13px; font-weight:700; line-height:1.45; overflow-wrap:anywhere; }
  .box .ch { display:flex; align-items:baseline; gap:8px; min-height:32px; padding:5px 10px; font-size:13px;
    border:1px solid var(--line); border-radius:6px; }
  .box .ch:hover { background:var(--hover); }
  .box .ch b { flex:none; color:var(--dim); }
  .box .ch span { min-width:0; overflow-wrap:anywhere; }
  .box .ch small { display:block; color:var(--dim); font-size:12px; }

  /* My phone, and never a Mac, however narrow its pane. Every control takes
     a fingertip: 44 by 44, Apple's least touch size (rule 20). The text is
     16px, so a tap into it zooms nothing. The home bar's band stays clear. */
  @media (hover:none) and (pointer:coarse) {
    .tx .scroll { padding:10px 10px 14px; }
    .row { min-height:44px; }
    .pic { height:120px; }
    .reply { padding:10px 12px; }
    .copy { min-height:56px; }
    .copy .btn, .hand .btn { height:44px; }
    .viewer .shut { width:44px; height:44px; }
    .box .more, .box .jump { width:48px; height:48px; }
    .box .item, .box .meter { font-size:15px; }
    .box .item { min-height:44px; }
    /* The text takes the whole width, two lines tall. The menu, the arrows
       and Send wrap onto a line beneath it, Send at its end. */
    .box .line { flex-wrap:wrap; }
    .box textarea { order:-1; flex-basis:100%; height:72px; min-height:72px; font-size:16px; padding:11px 12px; }
    .box .send { margin-left:auto; height:48px; min-width:84px; padding:0 20px; font-size:16px; }
    .box .chipf { height:46px; }
    .box .chipf img { width:32px; height:32px; }
    .box .chipf .x { width:44px; height:44px; }
    .box .sk { min-height:44px; align-items:center; font-size:15px; }
    .box .hint, .box .ch { min-height:44px; font-size:15px; }
    .box .hint kbd { display:none; }
  }
</style>
"""

# A hand-off's button, pressed: Type leaves
# its words in its session's prompt, and its Send then presses Return
# alone. Copy is the page's own click, copied().
HAND = """<script>
document.addEventListener('click', async e => {
  const b = e.target.closest('.group[data-hand] > button:not(.cp)');
  if (!b || b.disabled) return;
  const pair = b.parentElement, send = !!b.dataset.send;
  const only = send && pair.dataset.typed ? 'return' : '';
  if (await pressed(b, {act: 'hand', key: pair.dataset.hand, send: send ? 'yes' : '', only}, !send) !== '') return;
  if (send) delete pair.dataset.typed;
  else pair.dataset.typed = '1';
});
</script>
"""

SCRIPT = r"""<script>
(() => {
  const BASE = %BASE%, ICONS = %ICONS%, SKILLS = %SKILLS%;
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const nap = ms => new Promise(f => setTimeout(f, ms));
  const tx = $('tx'), scroll = $('scroll'), turns = $('turns');

  // It opens at its newest turn, and stays there while I read there.
  const pinned = () => scroll.scrollTop + scroll.clientHeight >= scroll.scrollHeight - 48;
  const bottom = () => { scroll.scrollTop = scroll.scrollHeight; };
  let stuck = true, share = 0;
  scroll.addEventListener('scroll', () => {
    stuck = pinned();
    share = scroll.scrollTop / (scroll.scrollHeight || 1);
  }, {passive: true});
  new ResizeObserver(() => { if (stuck) bottom(); fences(); }).observe(scroll);
  // Home's zoom reflows the transcript under the same scrollTop, and the
  // scroll it causes would unpin it. Read at its newest turn, it stays
  // there; read anywhere else, it keeps its share of the way down.
  addEventListener('ws-zoom', () => {
    const was = stuck, at = share;
    requestAnimationFrame(() => {
      if (was) bottom();
      else scroll.scrollTop = at * scroll.scrollHeight;
      stuck = was;
    });
  });

  // A fence or a table wider than its card scrolls sideways, and fades where
  // more waits.
  const WIDE = '.fence pre, .fence .grid';
  const fade = p => p.parentNode.classList.toggle('more', p.scrollLeft + p.clientWidth < p.scrollWidth - 2);
  const fences = () => document.querySelectorAll(WIDE).forEach(fade);
  document.addEventListener('scroll', e => { if (e.target.matches && e.target.matches(WIDE)) fade(e.target); }, true);

  // What I unfolded, by id, so a turn drawn again keeps it open. A detail
  // is read from disk once, bar a call still running: data-live. An open
  // one is read again each time the page is told, until its call ends.
  const open = new Set(), got = {};
  async function unfold(b, on) {
    const id = b.dataset.id, next = b.nextElementSibling;
    const box = next && next.matches('.detail, .sub') ? next : null;
    b.setAttribute('aria-expanded', on);
    if (on) open.add(id); else open.delete(id);
    if (box) box.hidden = !on;
    if (!on || !box || !box.classList.contains('detail') || box.dataset.got) return;
    await load(id, box);
  }
  async function load(id, box) {
    box.dataset.got = '1';
    try {
      let html = got[id];
      if (html === undefined) {
        const r = await fetch(BASE + '/step/' + encodeURIComponent(id));
        if (!r.ok) throw r;
        html = await r.text();
      }
      box.innerHTML = html;
      if (!box.querySelector('[data-live]')) got[id] = html;
      fences();
    } catch (e) { delete box.dataset.got; }
  }
  const relive = () => turns.querySelectorAll('.detail:not([hidden])').forEach(box => {
    const b = box.previousElementSibling;
    if (b && box.querySelector('[data-live]')) load(b.dataset.id, box);
  });
  function reopen() {
    for (const id of open) {
      const b = turns.querySelector(`.row[data-id="${CSS.escape(id)}"]`);
      if (b && b.getAttribute('aria-expanded') !== 'true') unfold(b, true);
    }
  }

  // A picture opens over the page; a tap anywhere closes it.
  const viewer = $('viewer'), big = viewer.querySelector('img');
  viewer.onclick = () => { viewer.hidden = true; big.removeAttribute('src'); };
  scroll.addEventListener('click', e => {
    const p = e.target.closest('.pic'), c = e.target.closest('.cp'), b = e.target.closest('button.row');
    if (p) { big.src = p.dataset.src; viewer.hidden = false; }
    else if (c) copied(c);
    else if (b) unfold(b, b.getAttribute('aria-expanded') !== 'true');
  });

  // Told the transcript moved: its last turn, what came after, and every
  // turn still showing something running are asked again, each with the
  // marks of the pieces it shows. A piece unmoved comes back as its mark
  // alone, and stays as it is, so what I highlighted, unfolded or scrolled
  // to stays too. Told again meanwhile, it asks once more after. A new
  // transcript, as /clear starts, is drawn whole.
  const marks = s => s.classList.contains('ses')
    ? [...s.querySelectorAll(':scope > .thread > .pc')].map(p => p.dataset.h) : [s.dataset.h];
  function patch(old, s) {
    if ('same' in s.dataset) return;
    if (!old.classList.contains('ses') || !s.classList.contains('ses')) return old.replaceWith(s);
    const oh = old.querySelector(':scope > header'), nh = s.querySelector(':scope > header');
    if (oh.outerHTML !== nh.outerHTML) oh.replaceWith(nh);
    const ot = old.querySelector(':scope > .thread'), was = [...ot.children];
    const now = [...s.querySelector(':scope > .thread').children];
    now.forEach((p, j) => {
      if ('same' in p.dataset && was[j]) return;
      if (was[j]) was[j].replaceWith(p); else ot.append(p);
    });
    was.slice(now.length).forEach(p => p.remove());
  }
  let drawing = false, again = false, whole = false;
  async function told(now) {
    const w = $('watch');
    if (w && now !== undefined) w.dataset.key = now;
    if (drawing) { again = true; return; }
    drawing = true;
    try {
      do {
        again = false;
        const last = whole ? null : turns.lastElementChild, from = last ? +last.dataset.i : 0;
        const asked = last ? [...new Set([...turns.querySelectorAll('.peek.run')]
          .map(p => p.closest('.turn')).concat(last))] : [];
        const have = asked.map(s => s.dataset.i + ':' + marks(s).join('.')).join('~');
        const r = await fetch(BASE + '/tail?from=' + from + '&have=' + encodeURIComponent(have));
        if (!r.ok) break;
        const t = document.createElement('template');
        t.innerHTML = await r.text();
        const stay = pinned(), tail = t.content.getElementById('tail');
        // A session gone names no transcript for a while: what shows stays.
        if (!tail.dataset.t && tx.dataset.t) break;
        if (tail.dataset.t !== tx.dataset.t) { tx.dataset.t = tail.dataset.t; whole = again = true; continue; }
        if (whole) turns.replaceChildren();
        whole = false;
        const was = tx.dataset.claude;
        tx.dataset.state = tail.dataset.state;
        tx.dataset.claude = tail.dataset.claude;
        if (was !== tx.dataset.claude || tx.dataset.claude === 'waiting') looking();
        ready();
        const got = [...tail.children], kept = new Set(got.map(s => s.dataset.i));
        // A turn asked for and not sent back is one the pane no longer shows.
        asked.forEach(s => { if (!kept.has(s.dataset.i)) s.remove(); });
        for (const s of got) {
          const old = turns.querySelector(`:scope > .turn[data-i="${s.dataset.i}"]`);
          if (old) { patch(old, s); continue; }
          turns.insertBefore(s, [...turns.children].find(o => +o.dataset.i > +s.dataset.i) || null);
        }
        $('running').replaceWith(t.content.getElementById('running'));
        $('queued').replaceWith(t.content.getElementById('queued'));
        $('meter').replaceWith(t.content.getElementById('meter'));
        if (window.advRows) advRows(t.content.getElementById('advrows'));
        relive();
        reopen();
        fences();
        if (stay) bottom();
        jumps();
      } while (again);
    } catch (e) {}
    drawing = false;
  }
  window.told = told;

  // ---- the box I type into ----

  const words = $('words'), send = $('send'), pick = $('pick'), att = $('att'), why = $('why');
  const box = $('box'), menu = $('menu');
  let held = [], busy = false;
  // While the session works, an empty box's Send reads Stop.
  const stopping = () => tx.dataset.claude === 'busy' && !words.value.trim() && !held.length;
  function ready() {
    const stop = stopping();
    send.textContent = stop ? 'Stop' : 'Send';
    send.classList.toggle('stop', stop);
    send.classList.toggle('busy', busy);
    send.disabled = busy || !(stop || words.value.trim() || held.length);
    box.classList.toggle('typed', !!words.value);
  }
  const say = s => { why.textContent = s; why.hidden = !s; };
  // The box grows with its text, up to two fifths of the transcript's height.
  function grow() {
    const cap = Math.max(parseFloat(getComputedStyle(words).minHeight) || 44, Math.round(tx.clientHeight * 0.4));
    words.style.height = 'auto';
    words.style.height = Math.min(words.scrollHeight + 4, cap) + 'px';
  }
  function chips() {
    att.hidden = !held.length;
    att.innerHTML = held.map((h, i) => `<span class="chipf">${h.file.type.startsWith('image/')
      ? `<img src="${h.url}" alt="">` : `<span class="fi">${ICONS.file}</span>`}<span class="nm">${esc(h.file.name)}</span>`
      + `<button class="b0 x" data-i="${i}" aria-label="Remove ${esc(h.file.name)}">${ICONS.x}</button></span>`).join('');
  }
  // A / opening the box lists every skill, those starting with what I
  // typed first, then those holding it. Esc shuts the list until I type.
  let rows = [], at = 0, shut = false;
  function slash() {
    const m = /^\/([\w:-]*)$/.exec(words.value), q = m ? m[1].toLowerCase() : '';
    rows = !m || shut ? [] : SKILLS.filter(s => s[0].startsWith(q))
      .concat(SKILLS.filter(s => !s[0].startsWith(q) && s[0].includes(q)));
    at = 0;
    list();
  }
  function list() {
    menu.hidden = !rows.length;
    menu.innerHTML = rows.map((s, i) => `<button class="b0 sk${i === at ? ' on' : ''}" data-i="${i}" tabindex="-1">`
      + `<b>/${esc(s[0])}</b><span>${esc(s[1])}</span></button>`).join('');
    menu.querySelector('.on')?.scrollIntoView({block: 'nearest'});
  }
  function fill(text) {
    words.value = text;
    rows = [];
    list();
    grow();
    ready();
    words.focus();
    words.setSelectionRange(text.length, text.length);
  }
  menu.addEventListener('pointerdown', e => e.preventDefault());
  menu.onclick = e => {
    const s = e.target.closest('.sk');
    if (s) fill('/' + rows[+s.dataset.i][0] + ' ');
  };

  // On my Mac, the up arrow in an empty box brings back my last line, again
  // the one before; the down arrow returns. Only an untouched line moves on.
  let back = -1;
  const mine = () => [...turns.querySelectorAll('.turn.mine .said')].map(s => s.textContent.trim())
    .filter((s, i, all) => s && s !== all[i - 1]);
  function recall(up) {
    const lines = mine(), now = back < 0 ? '' : lines[lines.length - 1 - back];
    const next = back + (up ? 1 : -1);
    if (words.value !== now || next < -1 || next >= lines.length) return false;
    back = next;
    shut = true;
    fill(back < 0 ? '' : lines[lines.length - 1 - back]);
    return true;
  }

  words.addEventListener('input', () => {
    back = -1;
    shut = false;
    slash();
    grow(); ready(); say(''); send.classList.remove('gone');
  });
  // On my Mac, Return sends, as Send does; Shift+Return adds a line. My
  // phone sends only from Send. Neither ever stops: only Stop, pressed, does.
  const PHONE = matchMedia('(hover: none) and (pointer: coarse)').matches;
  words.addEventListener('keydown', e => {
    if (e.isComposing) return;
    const plain = !(e.shiftKey || e.metaKey || e.altKey || e.ctrlKey);
    if (rows.length && plain && /^(ArrowUp|ArrowDown|Tab|Enter|Escape)$/.test(e.key)) {
      e.preventDefault();
      if (e.key === 'Escape') { shut = true; slash(); }
      else if (e.key.startsWith('Arrow')) { at = (at + (e.key === 'ArrowUp' ? -1 : 1) + rows.length) % rows.length; list(); }
      else fill('/' + rows[at][0] + ' ');
      return;
    }
    if (PHONE) return;
    const tip = $('offer').querySelector('.hint');
    if (tip && !words.value && plain && (e.key === 'Tab' || e.key === 'ArrowRight')) {
      e.preventDefault();
      fill(tip.dataset.text);
      return;
    }
    if (plain && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      if (recall(e.key === 'ArrowUp')) e.preventDefault();
      return;
    }
    if (e.key !== 'Enter' || e.shiftKey || e.altKey || e.ctrlKey) return;
    e.preventDefault();
    if (!stopping()) send.click();
  });

  // What only the pane shows, read each time the session's state moves:
  // its mode, and a dialog while it waits, else the reply it suggests once
  // its turn ends. The suggestion lands a moment after the turn, so a miss
  // is read again, twice. A mode hidden under a dialog keeps the last. A
  // page in a hidden frame has no width, and reads nothing until it shows:
  // home opens every tab of a hub ahead, hidden.
  const mode = $('mode');
  let reading = 0, unread = false;
  // A dialog waiting takes my words into its own field.
  // On my phone, its hint is short.
  const asking = () => {
    const ask = !!$('offer').querySelector('.ask');
    words.placeholder = PHONE ? (ask ? 'Or answer' : 'Type') : ask ? 'Or answer in your own words' : 'Type or dictate';
  };
  mode.onclick = async () => {
    mode.disabled = true;
    try {
      const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual', body: new URLSearchParams({act: 'mode'})});
      if (r.status === 409) say(await r.text());
      else { await nap(500); await looking(); }
    } catch (e) { say('1100 did not answer.'); }
    mode.disabled = false;
  };
  async function looking() {
    if (!innerWidth) { unread = true; return; }
    const ticket = ++reading, now = tx.dataset.claude;
    if (!now) { $('offer').innerHTML = ''; asking(); return; }
    for (const wait of now === 'idle' || now === 'waiting' ? [0, 1500, 4000] : [0]) {
      if (wait) await nap(wait);
      if (ticket !== reading) return;
      try {
        const r = await fetch(BASE + '/pane');
        if (!r.ok || ticket !== reading) return;
        const t = document.createElement('template');
        t.innerHTML = await r.text();
        $('offer').replaceWith(t.content.getElementById('offer'));
        const m = t.content.getElementById('mode');
        if (m) { $('modev').textContent = m.textContent; mode.hidden = false; }
        asking();
        // A panel's Close may show before its dialog draws: read again.
        if ($('offer').querySelector('.hint, .ch[data-n]')) return;
      } catch (e) { return; }
    }
  }
  box.addEventListener('click', async e => {
    const tip = e.target.closest('.hint'), ch = e.target.closest('.ch');
    if (tip) fill(tip.dataset.text);
    if (!ch) return;
    ch.parentNode.querySelectorAll('.ch').forEach(b => { b.disabled = true; });
    try {
      const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual',
        body: new URLSearchParams(ch.dataset.n ? {act: 'answer', n: ch.dataset.n} : {act: 'close'})});
      if (r.status === 409) { say(await r.text()); looking(); }
      else $('offer').innerHTML = '';
    } catch (e) { say('1100 did not answer.'); }
  });
  // A picture pasted, on my Mac or my phone, is held as the paperclip holds it.
  addEventListener('paste', e => {
    const pics = [...(e.clipboardData?.files || [])].filter(f => f.type.startsWith('image/'));
    if (pics.length) { e.preventDefault(); hold(pics); }
  });
  // On my Mac, a letter or a paste anywhere on the page lands in the box,
  // with no click. Home hands it one landing on home itself, through
  // typeIn. Tab outside the box, or on home around it, fills the empty box
  // with the reply Claude Code suggests, as Tab in the box does.
  anywhere(text => {
    words.focus();
    words.setRangeText(text, words.value.length, words.value.length, 'end');
    words.dispatchEvent(new Event('input'));
    return true;
  }, () => {
    const tip = $('offer').querySelector('.hint');
    if (!tip || words.value) return false;
    fill(tip.dataset.text);
    return true;
  });
  // On my Mac, the box holds the cursor, so a dictation tool always finds a
  // field to paste into. It takes it when the page opens, and back half a
  // second after a click on the page, the Mac's double-click time, so a
  // double or triple click highlights first. Home hands it back, through
  // holdCursor, when the page comes on show and after a click on home
  // itself. Text left highlighted keeps it out, and so does another field
  // holding it, or another page beside it.
  const field = el => !!el && el.matches('input, textarea, select, [contenteditable]');
  function holdCursor() {
    if (!innerWidth || field(document.activeElement)) return document.activeElement === words;
    const s = getSelection();
    if (s && !s.isCollapsed) return false;
    try {
      const at = parent !== window && parent.document.activeElement;
      if (at && (field(at) || (at.tagName === 'IFRAME' && at !== frameElement))) return false;
      words.focus({preventScroll: true});
    } catch (e) { return false; }
    return true;
  }
  if (!PHONE) {
    window.holdCursor = holdCursor;
    let settle = 0;
    addEventListener('click', () => { clearTimeout(settle); settle = setTimeout(holdCursor, 500); });
    holdCursor();
  }
  // iOS's paperclip menu comes from a file input with no accept: Photo
  // Library, Take Photo or Video, Choose Files.
  // The menu beside the text opens above the line, and shuts on a tap
  // anywhere else, on Esc, or once the paperclip is chosen.
  const more = $('more'), pop = $('pop');
  const popped = on => { pop.hidden = !on; more.setAttribute('aria-expanded', on); };
  more.onclick = () => popped(pop.hidden);
  addEventListener('pointerdown', e => {
    if (!pop.hidden && !pop.contains(e.target) && !more.contains(e.target)) popped(false);
  });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) popped(false); });
  $('clip').onclick = () => { popped(false); pick.click(); };
  // Two arrows step through my turns, landing each at the top: up, the
  // nearest starting above the top edge; down, the nearest below it, and
  // past my last, the foot. With none that way, an arrow greys. A turn's
  // place is read from offsetTop, in scrollTop's own pixels: the zoom from
  // home's rail scales getBoundingClientRect, and never those two.
  const prev = $('prev'), next = $('next');
  function aims() {
    const now = scroll.scrollTop, max = scroll.scrollHeight - scroll.clientHeight;
    const top = scroll.offsetTop + (parseFloat(getComputedStyle(scroll).paddingTop) || 0);
    const all = [...scroll.querySelectorAll('.turn.you')]
      .map(s => Math.min(max, Math.max(0, s.offsetTop - top))).concat(max);
    return [all.filter(a => a < now - 2).pop(), all.find(a => a > now + 2)];
  }
  function jumps() {
    const [up, down] = aims();
    prev.disabled = up === undefined;
    next.disabled = down === undefined;
  }
  prev.onclick = () => { const a = aims()[0]; if (a !== undefined) scroll.scrollTop = a; };
  next.onclick = () => { const a = aims()[1]; if (a !== undefined) scroll.scrollTop = a; };
  scroll.addEventListener('scroll', jumps, {passive: true});
  const sized = new ResizeObserver(jumps);
  sized.observe(scroll);
  sized.observe(turns);
  function hold(files) {
    for (const file of files) held.push({file, url: URL.createObjectURL(file)});
    chips();
    ready();
  }
  pick.onchange = () => { hold([...pick.files]); pick.value = ''; };
  att.onclick = e => {
    const x = e.target.closest('.x');
    if (!x) return;
    URL.revokeObjectURL(held.splice(+x.dataset.i, 1)[0].url);
    chips();
    ready();
  };
  const b64 = f => new Promise((ok, no) => {
    const r = new FileReader();
    r.onload = () => ok(String(r.result).split(',')[1] || '');
    r.onerror = no;
    r.readAsDataURL(f);
  });
  // It spins while it types, then flashes green. Refused, it turns red, and
  // the one sentence why shows above the line; my words stay. Sent, only
  // what went leaves the box: words typed and files added meanwhile stay.
  send.onclick = async () => {
    if (send.disabled) return;
    const stop = send.classList.contains('stop');
    const text = stop ? '' : words.value, went = stop ? [] : [...held];
    busy = true;
    ready();
    send.classList.remove('gone', 'done');
    say('');
    try {
      const data = new URLSearchParams(stop ? {act: 'stop'} : {act: 'send', text});
      for (const h of went) { data.append('name', h.file.name); data.append('data', await b64(h.file)); }
      const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual', body: data});
      if (r.status === 409) {
        say(await r.text());
        send.classList.add('gone');
      } else {
        if (words.value.startsWith(text)) words.value = words.value.slice(text.length).trimStart();
        slash();
        went.forEach(h => URL.revokeObjectURL(h.url));
        held = held.filter(h => !went.includes(h));
        chips();
        grow();
        send.classList.add('done');
        setTimeout(() => send.classList.remove('done'), 1500);
      }
    } catch (e) { say('1100 did not answer.'); }
    busy = false;
    ready();
  };
  // iOS gives a framed page no home-bar band, so the home's own is measured.
  // It is the glass's pixels, and this page's own are home's zoom of them.
  function inset() {
    let band = 0;
    try {
      const doc = parent !== window ? parent.document : document, probe = doc.createElement('div');
      probe.style.cssText = 'position:fixed;left:0;bottom:0;width:0;visibility:hidden;'
        + 'height:env(safe-area-inset-bottom, 0px)';
      doc.body.appendChild(probe);
      band = probe.offsetHeight;
      probe.remove();
    } catch (e) {}
    const zoom = parseFloat(document.documentElement.style.zoom) || 1;
    document.documentElement.style.setProperty('--ib', band / zoom + 'px');
  }
  addEventListener('resize', inset);
  addEventListener('ws-zoom', inset);
  addEventListener('resize', () => { if (unread && innerWidth) { unread = false; looking(); } });
  addEventListener('orientationchange', inset);
  inset();

  requestAnimationFrame(() => { bottom(); fences(); });
  ready();
  asking();
  looking();
})();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["draw"])
    ap.add_argument("number")
    args = ap.parse_args()
    print(render(f"{int(args.number):02d}"))


if __name__ == "__main__":
    main()
