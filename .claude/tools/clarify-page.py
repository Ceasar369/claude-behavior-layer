#!/usr/bin/env python3
"""clarify-page.py — the page 1100 draws for clarify-items, at /p/clarify/NN, and the wave file behind it.

Every item a wave shows is new, numbered in the order I read it, from one
count per session. A session never writes a wave file. It hands
this tool its items, and asks it for my answers.

  clarify-page.py wave    NN [--then "/clarify-items"]   the next wave, items on stdin
  clarify-page.py answers NN [--since K]                 my answers, and nothing else
  clarify-page.py close   NN [--chat]                    the round, closed
  clarify-page.py propose NN --item N --agree|--feedback --by MM [--why "…"]
                                                         an assistant's answer, under its item
  clarify-page.py rule    NN --item N --agree|--feedback   my answer, given for me
  clarify-page.py send    NN                             Send, pressed for me
  clarify-page.py fix     NN --item N                    one unanswered item, replaced, on stdin

wave numbers each item and writes .claude/state/sessions/NN/waves/wave-N.md.
No server starts and no pane opens: 1100 hears the file, and shows the
page in the session's hub until the wave is sent. A session another
drives wears a band under the page's head naming its driver,
lib/successor.py's, and a partial drive's topic: its items off it are mine.
The session lays the same items
out in chat. An item opens with "## " and its title. A field's first line sits after its name,
and every further line is indented two spaces. No --then types
/clarify-items on Send. A wave never inherits another's.

My answers go into the wave, as each item's agree and feedback lines.
Every item shows, one under the other, a tall rectangle between each
two. A number on the left brings its item's top to the top. Each item
carries its own feedback box at its foot. Anything I type in one is my
answer to its item, saved as I type. Agree and the rail's outline follow
the item whose box holds the cursor, else the item at the top. On my
Mac, Return in a box moves on to the next open item, the cursor in its
box, and sends once all are answered. Shift+Return makes a new line. A
box is one line at rest, and grows with the text. On my Mac, a letter or
a paste anywhere on the page lands in the box of the item at the top,
with no click, and so does one on 1100's home around it. An item holding
my answer shows it open. The
session writes a wave only once I am done with its page, so the two never
write one file at once. Send types the wave's then: line into the
session's pane, or /clarify-items when it has none, and only a line that
typed marks the wave sent. A pane gone, or Claude gone from it, marks
nothing, and the page says so. A wave closed in chat never needs Send,
answered or not: close --chat marks it sent from chat, and types nothing.
open_wave() is the wave still open, for the hooks that warn of it:
hooks/wave-open.py on each message of mine, hooks/9-session-stop.py at a stop.

A fence in a field draws as itself. ```mermaid is a chart, in one standard:
the session tags a node :::you, :::session, :::done, :::today or
:::assumed, and the page adds the colours and the legend:
.claude/pages/scripts/charts.js. A chart sits under the decision,
drawn left to right, and its strip zooms it, fits it and flips it top to
bottom. Its title, "Figure: …", the first line under its fence, sits
under it, centered; wave refuses a chart with none. Its bottom edge drags down, and the chart grows with it. A
scroll bar shows on each edge the chart runs past. The browser does all of it, so none costs a token. Any other fence
is text. A text line
marked in a column of its own, + new, ~ changes or - goes, stays bright,
and the lines around it dim.

An assistant that answers for me puts each verdict under its item, with
propose. A feedback's words come on stdin. The page shows it with one
button, Take it: an agree presses Agree, a feedback writes its words as my
feedback, still mine to edit. Either moves on to the next open item, as
Agree does. It goes through 1100 while 1100 is up, so it lands between my
keystrokes, never over them.

rule and send are session-control's, for each session it drives.
clarify-items uses rule too, to mark on the page what I answered in chat. They go through 1100, as my
own clicks do.

A wave written by hand, the older way, still draws: its status, its case
and its split.

Nothing is stored here. Every request reads the folder. 1100 imports this
file for its LIVE, lib/live.py's: drawn(), files() and take(). Nothing
here runs a server.

The shell and the colours are shared. See .claude/lib/.
It keeps the page rules atop .claude/lib/page.py.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402
# The wave file's own reading and writing, lib/waves.py's. Each name stays
# this tool's too, for the files that read a wave through it.
from waves import GIVEN, NUMBERED, answered, dump, folder, newest, parse, then, waves  # noqa: E402


def fail(why: str) -> None:
    print(why, file=sys.stderr)
    sys.exit(1)


def untitled(it: dict) -> bool:
    """Whether a field of the item holds a picture, any fence, a chart, a
    table, a tree or text, with no "Figure: …" as the first line under it."""
    for k in GIVEN:
        ls = (it.get(k) or "").split("\n")
        i = 0
        while i < len(ls):
            if not ls[i].strip().startswith("```"):
                i += 1
                continue
            j = next((j for j in range(i + 1, len(ls)) if ls[j].strip().startswith("```")), len(ls))
            under = next((x.strip() for x in ls[j + 1:] if x.strip()), "")
            if not under.startswith("Figure:"):
                return True
            i = j + 1
    return False


def whole(it: dict) -> str:
    """An item's title as written: parse() split it at its first "·"."""
    return it["n"] if it["title"] == it["n"] else f"{it['n']} · {it['title']}"


def unfit(it: dict, title: str) -> str:
    """Why an item cannot go on a wave, or ""."""
    if not it.get("question") or not it.get("decision"):
        return f"'{title}' needs a question and a decision."
    if untitled(it):
        return (f"'{title}' has a picture with no title. Its title, what it shows and how to read it, "
                "is the first line under its fence: Figure: …")
    return ""


def fix(nn: str, item: str) -> None:
    """One item of the wave still waiting on me, replaced under its own
    number, from the one item on stdin. An item holding my answer stays."""
    _, got = parse(sys.stdin.read())
    if len(got) != 1:
        fail("fix takes one item on stdin, opening with '## ' and its title.")
    if why := unfit(got[0], whole(got[0])):
        fail(why)
    said = through(nn, {"act": "fix", "n": item, "text": dump(0, {}, got)})
    if said:
        fail(said)
    print(f"Item {item} fixed.")


def write(nn: str, then_line: str) -> None:
    """The next wave, from the items on stdin. It refuses what it cannot number."""
    text = sys.stdin.read()
    wave, _, head, _ = newest(nn)
    if wave and not head.get("closed"):
        fail(f"Wave {wave} is still open. Fold it and close it first.")
    for line in text.splitlines():
        key, sep, _ = line.partition(":")
        if (sep and line[:1].isalpha() and not line.startswith("## ")
                and key.strip().lower() not in GIVEN):
            fail(f"'{key.strip()}' is no field. The fields: {', '.join(GIVEN)}.")
    _, items = parse(text)
    if not items:
        fail("No item came in. Each opens with '## ' and its title.")
    # Five at most, and Open questions after them. The rest wait for the next wave.
    if len(items) > 6 or (len(items) == 6 and not whole(items[-1]).lower().startswith("open questions")):
        fail(f"{len(items)} items came in. A wave holds five, then Open questions. The rest wait.")
    used = [int(n) for _, path in waves(nn)
            for n in NUMBERED.findall(open(path).read())]
    first = max(used, default=0) + 1
    for i, it in enumerate(items):
        title = whole(it)
        if why := unfit(it, title):
            fail(why)
        it["n"], it["title"] = str(first + i), title
    os.makedirs(folder(nn), exist_ok=True)
    head = {"sent": "", "then": then_line}
    registry.write_whole(os.path.join(folder(nn), f"wave-{wave + 1}.md"), dump(wave + 1, head, items))
    last = first + len(items) - 1
    print(f"Wave {wave + 1} written: " + (f"items {first} to {last}." if last > first
                                          else f"item {first}."))


def answers(nn: str, since: int = 0) -> None:
    """My answers, one line an item, and my feedback whole.

    The newest wave alone, or every wave from `since` on.
    """
    found = waves(nn)
    if not found:
        print("No wave yet.")
        return
    for wave, path in [w for w in found if w[0] >= since] if since else found[-1:]:
        with open(path) as f:
            head, items = parse(f.read())
        state = "closed" if head.get("closed") else "sent" if head.get("sent") else "waiting on you"
        print(f"Wave {wave} · {state}")
        said(items)


def said(items: list) -> None:
    for it in items:
        fb = it.get("feedback", "")
        word = ("agreed, and feedback:" if fb and it.get("agree") == "yes"
                else "feedback:" if fb
                else "agreed" if answered(it) else "unanswered")
        print(f"{it['n']} · {word}")
        for line in fb.split("\n") if fb else []:
            print(f"  {line}")


def close(nn: str, chat: bool = False) -> None:
    """The one line a sent wave takes after Send. A wave closed in chat,
    answered, moved on from or pulled back, takes --chat, and one line
    more: sent from chat. Nothing is typed."""
    wave, path, head, items = newest(nn)
    if not wave or not (head.get("sent") or chat):
        fail("No sent wave to close. One closed in chat takes --chat.")
    unsent = not head.get("sent")
    if not head.get("closed"):
        # Lines in, and nothing else touched. A sent wave is my record.
        with open(path) as f:
            lines = f.read().split("\n")
        at = next(i for i, line in enumerate(lines) if line.startswith("sent:"))
        if unsent:
            lines[at] = "sent: chat"
        lines.insert(at + 1, "closed: yes")
        registry.rewrite(path, "\n".join(lines))
    agreed = sum(1 for it in items if it.get("agree") == "yes")
    print(f"Wave {wave} closed{' from chat' if unsent else ''}: {agreed} of {len(items)} agreed.")


def propose(nn: str, item: str, verdict: str, by: str, why: str) -> None:
    """An assistant's verdict on one item, under it on the page."""
    words = sys.stdin.read().strip() if verdict == "feedback" else ""
    if verdict == "feedback" and not words:
        fail("A feedback proposal takes its words on stdin.")
    wave, _, head, items = newest(nn)
    if not wave or head.get("sent"):
        fail(f"Session {nn} has no wave waiting on me.")
    if not any(it["n"] == item for it in items):
        fail(f"Wave {wave} has no item {item}.")
    text = "\n".join([verdict, f"by: {by}"] + ([f"why: {' '.join(why.split())}"] if why.strip() else [])
                     + ([f"> {w.rstrip()}" for w in words.split("\n")] if words else []))
    through(nn, {"act": "propose", "n": item, "text": text}, 10)
    _, _, _, items = newest(nn)
    if next(it for it in items if it["n"] == item).get("proposed") != text:
        fail(f"Item {item}'s proposal did not land.")
    print(f"Item {item}: {verdict} proposed.")


def through(nn: str, form: dict, timeout: float = 45) -> str:
    """One answer posted to a session's page, as my own click posts it.
    What the page refused, in its own sentence, or nothing.

    It goes through 1100 while 1100 is up, so it lands between my
    keystrokes, never over them, and Send types from there. With 1100
    down, it is taken here.
    """
    if not ports.answering(serve.PORT):
        got = take(nn, {k: [v] for k, v in form.items()})
        return got.run() if isinstance(got, serve.Typing) else got
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{serve.PORT}{serve.address('clarify', nn)}",
                               data=urllib.parse.urlencode(form).encode(), timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code != 409:
            raise
        return e.read().decode()
    return ""


def rule(nn: str, item: str, verdict: str) -> None:
    """My agree or my feedback on one item, given for me by a controlling
    session, or by clarify-items from my chat. It replaces a draft of mine
    on the page: an agree clears its feedback, a feedback its agree."""
    words = sys.stdin.read().strip() if verdict == "feedback" else ""
    if verdict == "feedback" and not words:
        fail("Feedback takes its words on stdin.")
    wave, _, head, items = newest(nn)
    if not wave or head.get("sent"):
        fail(f"Session {nn} has no wave waiting on me.")
    it = next((i for i in items if i["n"] == item), None)
    if it is None:
        fail(f"Wave {wave} has no item {item}.")
    if verdict == "agree":
        if it.get("feedback"):
            through(nn, {"act": "feedback", "n": item, "text": ""})
        through(nn, {"act": "agree", "n": item, "on": "yes"})
    if verdict == "feedback":
        if it.get("agree") == "yes":
            through(nn, {"act": "agree", "n": item, "on": ""})
        through(nn, {"act": "feedback", "n": item, "text": words})
    print(f"Item {item}: {verdict}.")


def send(nn: str) -> None:
    """Send, pressed for me. It refuses while an item is unanswered, and
    says so when the session's pane is gone, or Claude is gone from it."""
    wave, _, head, items = newest(nn)
    if not wave or head.get("sent"):
        fail(f"Session {nn} has no wave waiting on me.")
    left = [it["n"] for it in items if not answered(it)]
    if left:
        fail(f"Wave {wave} still waits on item {', '.join(left)}.")
    why = through(nn, {"act": "send"})
    if why:
        fail(f"Wave {wave} was not sent. {why}")
    print(f"Wave {wave} sent. {then(head)} typed into session {nn}'s pane.")


def one(form: dict, name: str) -> str:
    return (form.get(name) or [""])[0]


def take(nn: str, form: dict) -> str:
    """One answer, as I give it. A sent wave is closed, and takes nothing more.

    Send types first, and only a line that typed marks the wave sent. A
    pane gone, or Claude gone from it, leaves it unsent, and the page is
    told why. The typing runs off 1100's draw queue, serve.Typing's; its
    checks, and the sent line it earns, stay on it.
    """
    wave, path, head, items = newest(nn)
    act = one(form, "act")
    nothing = "Nothing was typed." if act == "send" else "Nothing was saved."
    if not wave or head.get("sent"):
        return f"Session {nn} has no wave waiting on you. {nothing}"
    if act == "send":
        if not items:
            return f"Wave {wave} holds no items. Nothing was typed."
        left = [it["n"] for it in items if not answered(it)]
        if left:
            return f"Wave {wave} still waits on item {', '.join(left)}. Nothing was typed."
        # A page behind the file never sends what it no longer shows.
        if one(form, "worn") and one(form, "worn") != key(nn):
            return "This wave changed since this page drew it. Nothing was typed. Read it again, then send."
        # The pane is the session's own, as it stands now. Never panes.me(),
        # which is whichever pane happened to start 1100. With Claude gone
        # from it, its shell would run the line as a command. With a dialog
        # waiting there, Return would approve its first option.
        why, _, pane = page.typable(nn, ("idle", "shell", "busy"))
        if why:
            return why
        line = then(head)

        def typed() -> str:
            return "" if panes.say(pane, line, clear=True) else page.gone(nn)

        def sent(said: str) -> str:
            # The line typed, the wave is marked sent, read again first: an
            # answer may have landed while it typed.
            if said:
                return said
            now, where, top, rest = newest(nn)
            if now == wave and not top.get("sent"):
                top["sent"] = "yes"
                registry.rewrite(where, dump(now, top, rest))
            return ""
        return serve.Typing(typed, sent)
    if act not in ("agree", "feedback", "propose", "fix"):
        return "This page takes no such press. Nothing was saved."
    it = next((i for i in items if i["n"] == one(form, "n")), None)
    if it is None:
        return f"Wave {wave} has no item {one(form, 'n') or 'unnamed'}. Nothing was saved."
    if act == "fix":
        if answered(it) or it.get("feedback") or it.get("proposed"):
            return f"Item {it['n']} holds an answer. Nothing was changed."
        _, got = parse(one(form, "text"))
        if len(got) != 1:
            return "A fix takes one item. Nothing was changed."
        new = got[0]
        new["n"], new["title"] = it["n"], whole(new)
        items[items.index(it)] = new
        registry.rewrite(path, dump(wave, head, items))
        return ""
    if act == "agree":
        # An agreement from a wave written by hand never undoes by a
        # click. Only feedback reopens it.
        if it.get("status") == "agreed":
            return ""
        # The press says what it means, agreed or not. A toggle, on a
        # page drawn before a controller answered, would undo its answer.
        it["agree"] = "yes" if one(form, "on") == "yes" else ""
    elif act == "feedback":
        text = one(form, "text").replace("\r\n", "\n").strip("\n")
        it["feedback"] = "\n".join(line.rstrip() for line in text.split("\n"))
    else:
        it["proposed"] = one(form, "text").replace("\r\n", "\n").strip()
    # Swapped in whole, so no reader ever meets half a wave.
    registry.rewrite(path, dump(wave, head, items))
    return ""


# The feedback an assistant gives an item my rulings cannot answer, word for
# word, as session-control Step 2 holds it. It passes the item to me, and
# answers nothing.
MOVED = "This one moves to chat. My answer comes there. Go on with everything else."


def suggested(it: dict) -> tuple:
    """An item's proposal as (verdict, words), as Take it reads it: the first
    line is the verdict, and its "> " lines are the words, as one line."""
    lines = str(it.get("proposed") or "").split("\n")
    return lines[0], " ".join(line[2:] for line in lines[1:] if line.startswith("> ")).strip()


def proposes(it: dict) -> bool:
    """Whether an item's proposal answers it, once taken. Moving it to chat answers nothing."""
    verdict, words = suggested(it)
    return verdict == "agree" or verdict == "feedback" and bool(words) and words != MOVED


def ready(nn: str) -> bool:
    """Whether session NN's wave waiting on me can be sent as a whole: every
    item answered, or holding a proposal that answers it. Items I answered
    by hand count too, so a wave I filled myself still sends."""
    wave, _, head, items = newest(nn)
    return bool(wave and not head.get("sent") and items
                and all(answered(it) or proposes(it) for it in items))


def take_all(nn: str) -> str:
    """Send answers, pressed: each open item takes its proposal, as Take it
    does, then Send is pressed, as if I had clicked each button. A wave with
    an item that has neither an answer nor a proposal takes nothing."""
    wave, _, head, items = newest(nn)
    if not wave or head.get("sent"):
        return f"Session {nn} has no wave waiting on you. Nothing was sent."
    if not ready(nn):
        return f"Wave {wave} has an item with no answer and no proposal. Nothing was sent."
    for it in items:
        if not answered(it):
            verdict, words = suggested(it)
            form = ({"act": "agree", "n": it["n"], "on": "yes"} if verdict == "agree"
                    else {"act": "feedback", "n": it["n"], "text": words})
            take(nn, {key: [value] for key, value in form.items()})
    return take(nn, {"act": ["send"]})


def key(nn: str) -> str:
    """The wave as it stands: sent or closed, every item's answer and
    proposal, and who drives the session. Send wears it, so a page behind
    the file never sends."""
    wave, _, head, items = newest(nn)
    given = hashlib.sha1("".join(f"{it.get('agree', '')}\n{it.get('feedback', '')}\n{it.get('proposed', '')}\n"
                                 for it in items).encode()).hexdigest()[:12]
    return (f"{wave}:{head.get('sent', '')}:{head.get('closed', '')}:{given}:{successor.driven(nn)}"
            f":{successor.topics().get(nn, '')}")


def band(by: str, topic: str) -> str:
    """The band under the top rail of a session another drives: its driver,
    and a partial drive's topic, whose items off it are mine."""
    if not by:
        return ""
    return f"{by} drives this session on {topic}. Items off it are yours." if topic \
        else f"{by} drives this session, and answers this wave."


# ---- the page ------------------------------------------------------------------
#
# 1100 draws every item itself, so a change lands part by part:
# lib/live.py. The page's own script,
# .claude/pages/scripts/clarify.js, then only moves about the page, saves my words
# and sends each press. It draws what the browser alone can: the charts,
# .claude/pages/scripts/charts.js's.

FENCE = re.compile(r"```(\w*)", re.A)
REFERS = re.compile(r"\bitems? (\d+)", re.A | re.I)
# The tree standard: a marker says what changes, after the name, past two
# spaces, or first on the line, as a diff puts it. An unmarked line dims.
MARK = re.compile(r"\s{2,}([+~-])(\s|$)|^\s*([+~-])\s")
TREE = {"+": "New", "~": "Changes", "-": "Goes"}
FIGURE = re.compile(r"\s*Figure:\s*(.*)")


def colour(it: dict) -> str:
    """An item's colour, per wave. Red: feedback given, and it always wins.
    Green: agreed. Grey: unanswered."""
    return "red" if it.get("feedback") else "green" if answered(it) else "grey"


def verdict(it: dict) -> dict:
    """An assistant's proposal, in its parts: its verdict, who gave it, why,
    and a feedback's words."""
    first, *rest = str(it.get("proposed") or "").split("\n")
    field = lambda k: " ".join(line[len(k) + 1:].strip() for line in rest if line.startswith(k + ":"))
    return {"v": first.strip().lower(), "by": field("by"), "why": field("why"),
            "words": "\n".join(re.sub(r"^>\s?", "", line) for line in rest if line.startswith(">"))}


def hint(it: dict) -> str:
    """The outline a proposal gives a number still grey: green for agree, red for feedback."""
    if not it.get("proposed") or colour(it) != "grey":
        return ""
    return "green" if verdict(it)["v"] == "agree" else "red"


def drawn(nn: str) -> str:
    """Session NN's wave, every item drawn. Its answers, and nothing else,
    go as data beside them, for the page's own script."""
    wave, _, head, items = newest(nn)
    known = {it["n"] for it in items}
    sent = bool(head.get("sent"))
    esc = page.esc

    def link(s) -> str:
        """Words, with each "item 3" a link to that item when this wave holds it."""
        return REFERS.sub(lambda m: f'<a class="link" data-go="{m.group(1)}">{m.group(0)}</a>'
                          if m.group(1) in known else m.group(0), esc(s))

    lines = lambda s: [x.strip() for x in str(s or "").split("\n") if x.strip()]
    bullets = lambda s: [re.sub(r"^[-•]\s*", "", x) for x in lines(s)]
    ul = lambda found, cls="": f'<ul class="b {cls}">{"".join(f"<li>{x}</li>" for x in found)}</ul>' if found else ""

    def fences(s) -> list:
        """A field as lines, and fences: each (kind, text), kind "" for lines."""
        out, buf, kind = [], [], None
        for line in str(s or "").split("\n"):
            m = FENCE.fullmatch(line.strip())
            if m and kind is None:
                if buf:
                    out.append(["", "\n".join(buf)])
                buf, kind = [], m.group(1) or "text"
            elif m:
                out.append([kind, "\n".join(buf)])
                buf, kind = [], None
            else:
                buf.append(line)
        if buf:
            out.append([kind or "", "\n".join(buf)])
        # A picture's title is the first line under its fence: Figure: …
        for i, x in enumerate(out):
            x.append("")
            if x[0] and i + 1 < len(out) and not out[i + 1][0]:
                under = out[i + 1][1].split("\n")
                at = next((j for j, line in enumerate(under) if line.strip()), -1)
                m = FIGURE.fullmatch(under[at]) if at >= 0 else None
                if m:
                    x[2] = m.group(1)
                    del under[at]
                    out[i + 1][1] = "\n".join(under)
        return out

    def tree(text: str) -> str:
        ls = text.split("\n")
        marks = [m.group(1) or m.group(3) for m in map(MARK.search, ls) if m]
        if not marks:
            return f'<pre class="pre">{esc(text)}</pre>'
        body = "\n".join(esc(x) if MARK.search(x) else f'<span class="dim">{esc(x)}</span>' for x in ls)
        used = [f'<span class="lg"><b>{k}</b>{word}</span>' for k, word in TREE.items() if k in marks]
        if any(not MARK.search(x) for x in ls):
            used.append('<span class="lg"><b class="dim">dim</b>Unchanged</span>')
        return f'<pre class="pre">{body}</pre><div class="legend">{"".join(used)}</div>'

    def block(kind: str, text: str, title: str) -> str:
        drawn = tree(text) if kind != "mermaid" else f'<pre class="mmd">{esc(text)}</pre>'
        return f'<figure class="cfig">{drawn}<figcaption>{link(title)}</figcaption></figure>' if title else drawn

    para = lambda s: "".join(block(k, t, title) if k else "".join(f"<p>{link(y)}</p>" for y in lines(t))
                             for k, t, title in fences(s))
    listed = lambda s: "".join(block(k, t, title) if k else ul([link(x) for x in bullets(t)])
                               for k, t, title in fences(s))

    def proposal(it: dict) -> str:
        """An assistant's proposal, under the decision and above its why."""
        if not it.get("proposed"):
            return ""
        p = verdict(it)
        agree = p["v"] == "agree"
        taken = it.get("agree") == "yes" if agree else (it.get("feedback") or "").strip() == p["words"].strip()
        who = f'Session {esc(p["by"])}, your assistant,' if p["by"] else "Your assistant"
        return (f'<div class="prop"><div class="ph">{who} proposes · {"Agree" if agree else "Feedback"}</div>'
                + (f'<p class="pw">{link(p["why"])}</p>' if p["why"] else "")
                + (f'<blockquote class="pq">{esc(p["words"])}</blockquote>' if p["words"] else "")
                + f'<button class="take" data-take="{esc(it["n"])}"{" disabled" if taken or sent else ""}>'
                + ("✓ Taken" if taken else "Take it · Agree" if agree else "Take it · into the feedback box")
                + "</button></div>")

    def split(s) -> str:
        def one_line(x: str) -> str:
            a, *b = re.split(r"\s*→\s*", x)
            return link(a) + (f' <span class="out">→ {link(b[0])}</span>' if b and b[0] else "")
        return ul([one_line(x) for x in bullets(s)], "split")

    def card(it: dict) -> str:
        """One item: its number, in its colour, then the question, the
        decision, an assistant's proposal, why, and the picture under them.
        Wrong if, from, after, today, instead and sources fold under one
        closed line, The case. A wave written by hand adds its split and its
        own case. Its feedback box closes it."""
        c, n = colour(it), esc(it["n"])
        s = (f'<h1 class="q"><span class="chip{" g" if c == "grey" else ""}">{n}</span>'
             f'{esc(it.get("question") or it.get("title", ""))}</h1>'
             f'<p class="dec"><span class="arr">→</span>{link(it.get("decision"))}</p>' + proposal(it))
        if it.get("why"):
            s += f'<p class="why"><span class="k">Why</span>{link(it["why"])}</p>'
        s += para(it["show"]) if it.get("show") else ""
        for k, title, draw in (("split", '<h3 class="sub">How I read it</h3>', split),
                               ("answer", '<h3 class="sub">My answer</h3>', para),
                               ("changed", '<h3 class="sub">What changed</h3>', listed),
                               ("led", '<h2 class="sec">Led to</h2>', para)):
            if it.get(k):
                s += title + draw(it[k])
        if it.get("context") or it.get("for") or it.get("against"):
            s += '<h2 class="sec">The case</h2>'
            for k, word, draw in (("context", "Context", para), ("for", "For", listed), ("against", "Against", listed)):
                if it.get(k):
                    s += f'<div class="row"><span class="k">{word}</span><div class="v">{draw(it[k])}</div></div>'
        case = "".join(f'<p class="why"><span class="k">{word}</span>{link(it[k])}</p>'
                       for k, word in (("wrong", "Wrong if"), ("from", "From"), ("after", "After")) if it.get(k))
        for k, title, draw in (("today", '<h2 class="sec">Today</h2>', para),
                               ("instead", '<h2 class="sec">Instead</h2>', listed)):
            if it.get(k):
                case += title + draw(it[k])
        if it.get("sources"):
            case += f'<p class="srcs">{esc(it["sources"])}</p>'
        if case:
            s += f'<details class="case"><summary>The case</summary>{case}</details>'
        # The box's words are 1100's own, so the page keeps mine until they land.
        return (f'<section class="item" id="t-{n}" style="--c:var(--{c})">{s}<div class="fbx"><div class="lab">'
                f'<span>Your feedback on item {n}</span><span class="st"></span></div>'
                f'<textarea id="fb-{n}" data-n="{n}" placeholder="Your feedback on item {n}."'
                f'{" disabled" if sent else ""}>{esc(it.get("feedback", ""))}</textarea></div></section>')

    def tab(it: dict) -> str:
        c, h, n = colour(it), hint(it), esc(it["n"])
        return (f'<div class="tab{" g" if c == "grey" else ""}{" hint" if h else ""}" id="r-{n}" data-k="{n}" '
                f'style="--c:var(--{c});--h:var(--{h or c})" '
                f'title="{esc(it.get("question") or it.get("title", ""))}">{n}</div>')

    by = successor.driven(nn)
    tools = ('<span class="group"><button id="agree" class="agree"></button><button id="send"></button></span>'
             if items else "")
    top = page.head("clarify", plans.tag(nn), f"Wave {wave}" if wave else "", tools,
                    band(by, successor.topics().get(nn, "")) if items else "")
    mine = (registry.entries().get(nn) or {}).get("session_id", "")
    # The answers alone, as the page's own script reads them, and the key
    # Send names, so a page behind the file never sends. The same scripts
    # with no item at all, so a wave arriving reloads nothing.
    data = json.dumps({"wave": wave, "sent": head.get("sent", ""), "key": key(nn),
                       "items": [{k: it.get(k, "") for k in ("n", "agree", "feedback", "status", "proposed")}
                                 for it in items]}).replace("</", "<\\/")
    scripts = (page.TABS + page.ANYWHERE + page.ZOOM
               + f'<script src="{live.src("charts.js")}"></script>\n<script src="{live.src("clarify.js")}"></script>\n')
    body = (live.watch(mine)
            + (live.part("The items", lambda: f'<div id="items">{"".join(map(card, items))}</div>\n') if items
               else page.blank("No items wait") + "\n")
            + f'<script type="application/json" id="wave">{data}</script>\n' + scripts)
    rail = top + (live.part("The rail", lambda: f'<nav class="nums" id="index">{"".join(map(tab, items))}</nav>\n')
                  if items else "")
    return page.render(f"{nn}-clarify", [("", body)], rail, refresh=0)


def files(nn: str) -> list:
    """Every file whose write can move session NN's page: its wave, and who
    drives it, whose mission it is, and what each session is named."""
    out = registry.watched([nn])
    for n in registry.entries():
        own = registry.folder(n)
        out += [os.path.join(own, registry.RECORD), os.path.join(own, plans.PLAN), successor.path(n)]
    return out


# The page's contract, lib/live.py's: its address, its draw, its files, its take.
LIVE = live.Page(serve.address("clarify", r"(\d{2})"), drawn, files=files, take=take)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["wave", "answers", "close", "propose", "rule", "send", "fix"])
    ap.add_argument("nn")
    ap.add_argument("--then", default="")
    ap.add_argument("--since", type=int, default=0)
    ap.add_argument("--chat", action="store_true")
    ap.add_argument("--item", default="")
    verdict = ap.add_mutually_exclusive_group()
    verdict.add_argument("--agree", action="store_const", const="agree", dest="verdict")
    verdict.add_argument("--feedback", action="store_const", const="feedback", dest="verdict")
    ap.add_argument("--by", default="")
    ap.add_argument("--why", default="")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{2}", args.nn):
        fail(f"{args.verb} takes a session number, like 07.")
    if args.verb == "wave":
        write(args.nn, " ".join(args.then.split()))
    elif args.verb == "answers":
        answers(args.nn, args.since)
    elif args.verb == "close":
        close(args.nn, args.chat)
    elif args.verb == "send":
        send(args.nn)
    elif args.verb == "fix":
        if not args.item:
            fail("fix takes --item N, and the item on stdin.")
        fix(args.nn, args.item)
    elif args.verb == "rule":
        if not (args.item and args.verdict):
            fail("rule takes --item N, and --agree or --feedback.")
        rule(args.nn, args.item, args.verdict)
    elif not (args.item and args.verdict and re.fullmatch(r"\d{2}", args.by)):
        fail("propose takes --item N, --agree or --feedback, and --by MM.")
    else:
        propose(args.nn, args.item, args.verdict, args.by, args.why)


if __name__ == "__main__":
    main()
