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
my answer shows it open. A save of my own never reloads the page; any
other change to the wave does, so it never shows an answer the file no
longer holds: key() says which. The
session writes a wave only once I am done with its page, so the two never
write one file at once. Send types the wave's then: line into the
session's pane, or /clarify-items when it has none, and only a line that
typed marks the wave sent. A pane gone, or Claude gone from it, marks
nothing, and the page says so. A wave closed in chat never needs Send,
answered or not: close --chat marks it sent from chat, and types nothing.
open_wave() is the wave still open, for the hooks that warn of it:
hooks/wave-open.py on each message of mine, hooks/9-session-stop.py at a stop.

A fence in a field draws as itself. ```mermaid is a chart, in one standard:
the session tags a node :::you, :::session, :::done or :::today, and the
page adds the colours and the legend. A chart sits under the decision,
drawn left to right, and its strip zooms it, fits it and flips it top to
bottom. Its bottom edge drags down, and the chart grows with it. A
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
file for render and take, and serves them; nothing here runs a server.

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
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402

WAVE =re.compile(r"wave-(\d+)\.md")
NUMBERED = re.compile(r"^## (\d+) ·", re.M)

# The lines a wave carries above its first item.
HEAD = ("sent", "then", "closed")

# What a session writes on an item. Each one line, but a picture.
GIVEN = ("question", "decision", "why", "wrong", "from", "after", "show",
         "today", "instead", "sources")

# Every line an item may carry, in the order a wave file writes them. An
# assistant's proposal follows what the session wrote. The row after it is a
# wave written by hand, kept so a round still open reads, and loses nothing.
FIELDS = GIVEN + ("proposed",) + (
    "status", "split", "answer", "changed", "led", "context", "what", "for",
    "against", "recommendation") + ("agree", "feedback")


def fail(why: str) -> None:
    print(why, file=sys.stderr)
    sys.exit(1)


def folder(nn: str) -> str:
    return os.path.join(registry.folder(nn), registry.WAVES)


def waves(nn: str) -> list:
    """Every wave in a session's waves/, as (number, path), oldest first."""
    try:
        names = os.listdir(folder(nn))
    except OSError:
        return []
    return sorted((int(m.group(1)), os.path.join(folder(nn), n))
                  for n in names if (m := WAVE.fullmatch(n)))


def parse(text: str) -> tuple:
    """A wave as (head, items).

    A line that names no field continues the one above it. A wave indents
    those lines, so a line of mine starting "why:" stays mine. A line keeps
    whatever indentation it carries past the wave's own two spaces, so a
    tree or a chart keeps its shape.
    """
    head, items, last = {"sent": "", "then": "", "closed": ""}, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            n, _, title = line[3:].partition("·")
            items.append({"n": n.strip(), "title": title.strip() or n.strip()})
            last = None
            continue
        if not line.strip():
            continue
        target = items[-1] if items else head
        key, sep, value = line.partition(":")
        key = key.strip().lower()
        if not line.startswith((" ", "\t")) and sep and key in (FIELDS if items else HEAD):
            target[key] = value.strip()
            last = key
        elif last:
            kept = line[2:] if line.startswith("  ") else line.strip()
            target[last] = (target[last] + "\n" + kept.rstrip()).strip("\n")
    return head, items


def dump(wave: int, head: dict, items: list) -> str:
    def field(k, v):
        first, *rest = (v or "").split("\n")
        return [f"{k}: {first}".rstrip()] + [f"  {r}".rstrip() for r in rest]
    out = [f"# Wave {wave}", f"sent: {head.get('sent', '')}".rstrip()]
    out += [f"{k}: {head[k]}" for k in ("then", "closed") if head.get(k)]
    out.append("")
    for it in items:
        out.append(f"## {it['n']} · {it['title']}")
        for k in FIELDS:
            if k in it or k in ("agree", "feedback"):
                out += field(k, it.get(k, ""))
        out.append("")
    return "\n".join(out)


def newest(nn: str) -> tuple:
    """The newest wave as (number, path, head, items), or number 0."""
    found = waves(nn)
    if not found:
        return 0, "", {}, []
    wave, path = found[-1]
    with open(path) as f:
        return (wave, path, *parse(f.read()))


def answered(it: dict) -> bool:
    """Agreed, now or in a wave written by hand, or carrying feedback."""
    return bool(it.get("feedback")) or it.get("agree") == "yes" \
        or it.get("status") == "agreed"


def open_wave(nn: str) -> tuple:
    """The newest wave not closed, as (number, head, the items I left
    unanswered, each "N · title"). Waiting on me, or sent and never folded.
    Number 0 when none is open."""
    wave, _, head, items = newest(nn)
    if not wave or head.get("closed"):
        return 0, {}, []
    return wave, head, [f"{it['n']} · {it['title']}" for it in items if not answered(it)]


SKILLS = os.path.join(registry.ROOT, ".claude", "skills")


def then(head: dict) -> str:
    """The line Send types: the wave's own slash command, when that skill
    still exists, or /clarify-items. A skill renamed since never types."""
    line = " ".join(head.get("then", "").split())
    name = line[1:].split(" ", 1)[0] if line.startswith("/") else ""
    return line if name and os.path.isfile(os.path.join(SKILLS, name, "SKILL.md")) else "/clarify-items"


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
    used = [int(n) for _, path in waves(nn)
            for n in NUMBERED.findall(open(path).read())]
    first = max(used, default=0) + 1
    for i, it in enumerate(items):
        # parse() split the title at its first "·". This puts it back whole.
        title = it["n"] if it["title"] == it["n"] else f"{it['n']} · {it['title']}"
        if not it.get("question") or not it.get("decision"):
            fail(f"'{title}' needs a question and a decision.")
        it["n"], it["title"] = str(first + i), title
    os.makedirs(folder(nn), exist_ok=True)
    head = {"sent": "", "then": then_line}
    with open(os.path.join(folder(nn), f"wave-{wave + 1}.md"), "w") as f:
        f.write(dump(wave + 1, head, items))
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
        with open(path, "w") as f:
            f.write("\n".join(lines))
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
    if not wave or head.get("sent"):
        return ""
    act = one(form, "act")
    if act == "send":
        if not items:
            return ""
        left = [it["n"] for it in items if not answered(it)]
        if left:
            return f"Wave {wave} still waits on item {', '.join(left)}. Nothing was typed."
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
                with open(where, "w") as f:
                    f.write(dump(now, top, rest))
            return ""
        return serve.Typing(typed, sent)
    it = next((i for i in items if i["n"] == one(form, "n")), None)
    if it is None:
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
    elif act == "propose":
        it["proposed"] = one(form, "text").replace("\r\n", "\n").strip()
    else:
        return ""
    with open(path, "w") as f:
        f.write(dump(wave, head, items))
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


SCRIPT = """<script>
const D = %s;
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
const find = n => D.items.find(it => it.n === String(n));
const locked = it => it.status === 'agreed';
const agreed = it => locked(it) || it.agree === 'yes';

/* This page's own colours, per wave. Red: feedback given, and it always
   wins. Green: agreed. Grey: unanswered. */
const colour = it => it.feedback ? 'red' : agreed(it) ? 'green' : 'grey';
const answered = it => colour(it) !== 'grey';
/* An assistant's proposal outlines a number still grey: green for agree, red for feedback. */
const hint = it => !it.proposed || answered(it) ? '' : parts(it).v === 'agree' ? 'green' : 'red';
const lines = s => String(s || '').split('\\n').map(x => x.trim()).filter(Boolean);
const bullets = s => lines(s).map(x => x.replace(/^[-•]\\s*/, ''));
const link = s => esc(s).replace(/\\bitems? (\\d+)/gi,
  (m, n) => find(n) ? `<a class="link" onclick="go('${n}')">${m}</a>` : m);
const ul = (html, cls) => html.length
  ? `<ul class="b ${cls || ''}">${html.map(x => `<li>${x}</li>`).join('')}</ul>` : '';
/* cur is the item at the top, and part how far into it main shows, as a
   share of its height: what a zoom from home keeps. */
let cur = null, part = 0, timer = null, pending = null;
const PHONE = matchMedia('(hover: none) and (pointer: coarse)').matches;

/* A field is lines, and fences. A fence keeps its lines as they are. */
const fences = s => { const out = []; let buf = [], f = null;
  for (const l of String(s || '').split('\\n')) {
    const m = l.trim().match(/^```(\\w*)$/);
    if (m && f === null) { if (buf.length) out.push({t: buf.join('\\n')}); buf = []; f = m[1] || 'text'; }
    else if (m) { out.push({f, t: buf.join('\\n')}); buf = []; f = null; }
    else buf.push(l); }
  if (buf.length) out.push(f === null ? {t: buf.join('\\n')} : {f, t: buf.join('\\n')});
  return out; };

/* The tree standard. A marker says what changes: after the name, past two
   spaces, or first on the line, as a diff puts it. An unmarked line is
   today, and dims. */
const MARK = /\\s{2,}([+~-])(\\s|$)|^\\s*([+~-])\\s/;
const mark = l => { const m = l.match(MARK); return m ? m[1] || m[3] : ''; };
const TREE = {'+': 'New', '~': 'Changes', '-': 'Goes'};
function pre(t) {
  const ls = t.split('\\n'), marks = ls.map(mark).filter(Boolean);
  if (!marks.length) return `<pre class="pre">${esc(t)}</pre>`;
  const body = ls.map(l => MARK.test(l) ? esc(l) : `<span class="dim">${esc(l)}</span>`).join('\\n');
  const used = Object.keys(TREE).filter(k => marks.includes(k))
    .map(k => `<span class="lg"><b>${k}</b>${TREE[k]}</span>`);
  if (ls.some(l => !MARK.test(l))) used.push('<span class="lg"><b class="dim">dim</b>Unchanged</span>');
  return `<pre class="pre">${body}</pre><div class="legend">${used.join('')}</div>`;
}

/* The chart standard. Colour says who acts, and grey says unchanged. A
   diamond is a condition, a cylinder a file. A solid arrow means then, a
   dashed one reads. The legend lists only what a chart uses. */
const STD = {
  you: 'fill:#3b2226,stroke:#f87171,stroke-width:2px,color:#e6e8ee',
  session: 'fill:#1e2b40,stroke:#60a5fa,stroke-width:2px,color:#e6e8ee',
  done: 'fill:#1b3326,stroke:#4ade80,stroke-width:2px,color:#e6e8ee',
  today: 'fill:#1a1d26,stroke:#4b5162,stroke-width:1px,color:#8b91a3'};
const WORD = {you: 'You act', session: 'A session or tool acts', done: 'Settled', today: 'Unchanged'};
const flow = src => /^\\s*(flowchart|graph)\\b/.test(src);
const standard = src => flow(src)
  ? src + '\\n' + Object.entries(STD).map(([k, v]) => `classDef ${k} ${v}`).join('\\n') : src;
function legend(src) {
  if (!flow(src)) return '';
  const colour = {you: 'red', session: 'blue', done: 'green', today: 'grey'};
  const used = Object.keys(STD).filter(k => new RegExp(`:::${k}\\\\b`).test(src))
    .map(k => `<span class="lg"><i class="sw" style="--c:var(--${colour[k]})"></i>${WORD[k]}</span>`);
  if (/\\w\\{/.test(src)) used.push('<span class="lg"><i class="sh dia"></i>A condition</span>');
  if (/\\[\\(/.test(src)) used.push('<span class="lg"><i class="sh cyl"></i>A file</span>');
  if (/-->/.test(src)) used.push('<span class="lg"><i class="ar"></i>Then</span>');
  if (/-\\.->|-\\.\\s/.test(src)) used.push('<span class="lg"><i class="ar dash"></i>Reads</span>');
  return used.length ? `<div class="legend">${used.join('')}</div>` : '';
}
const block = x => x.f === 'mermaid' ? `<pre class="mmd">${esc(x.t)}</pre>` : pre(x.t);
const para = s => fences(s).map(x => x.f ? block(x) : lines(x.t).map(y => `<p>${link(y)}</p>`).join('')).join('');
const list = s => fences(s).map(x => x.f ? block(x) : ul(bullets(x.t).map(link))).join('');

/* Mermaid loads only when a chart waits. Offline, a chart stays its source.
   Every chart draws left to right, whatever way it was written. Its strip
   flips it top to bottom, and back. The browser draws both ways, so a
   flip costs the session nothing. A label is SVG text, never HTML: WebKit
   measures HTML in a chart at the page's zoom, so zoomed in, a long label
   never wrapped, and its box cut it off. */
let M = null;
const mermaid = () => M = M || import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs')
  .then(x => { const m = x.default;
    m.initialize({ startOnLoad: false, htmlLabels: false, theme: 'dark', fontFamily: 'ui-monospace, Menlo, monospace',
      flowchart: { padding: 12 },
      themeVariables: { background: '#161922', primaryColor: '#1d212c', primaryBorderColor: '#8b91a3',
        primaryTextColor: '#e6e8ee', lineColor: '#8b91a3', fontSize: '13px' } });
    return m; });
const orient = (src, dir) => { const ls = src.split('\\n'), first = ls.findIndex(l => l.trim());
  return ls.map((l, i) => i === first
    ? l.replace(/^(\\s*)(?:flowchart|graph)\\b(?:\\s+(?:TB|TD|BT|LR|RL)\\b)?/, '$1flowchart ' + dir)
    : l.replace(/^(\\s*)direction\\s+(?:TB|TD|BT|LR|RL)\\b/, '$1direction ' + dir)).join('\\n'); };

/* Each chart draws once per direction, one render at a time. A flip is kept
   by its source, so a redraw of the page keeps it. */
const SVG = {}, DIR = {};
let queue = Promise.resolve(), ids = 0;
function svgOf(src, dir) {
  const key = dir + '\\n' + src;
  if (!SVG[key]) SVG[key] = queue = queue.catch(() => {}).then(mermaid)
    .then(m => m.render('mmd' + ids++, standard(orient(src, dir)))).then(r => r.svg);
  return SVG[key];
}
/* A page in a hidden frame has no width, so Mermaid measures nothing and
   fails. Its charts wait, and draw once the frame shows and resizes. */
async function charts() {
  if (!innerWidth) return;
  for (const el of [...document.querySelectorAll('pre.mmd')]) {
    const src = el.textContent;
    let svg;
    try { svg = await svgOf(src, DIR[src] || 'LR'); } catch (e) { el.className = 'pre'; continue; }
    if (!el.isConnected) continue;
    const d = chart(src, svg);
    el.replaceWith(d);
    measure(d.chart);
  }
}

/* A chart is a frame: its strip, then a window it zooms and pans inside,
   then its legend. It keeps its natural size, and shrinks only when it is
   wider than the window, or taller than main.
   Narrower than the window, it sits in the middle. The window is as tall
   as the fitted chart, so the page never moves when the chart zooms.
   Its bottom edge drags down: the window grows, and the chart zooms with
   it, its top held still. Fit brings both back. */
const FIT = {k: 1, x: 0, y: 0}, MAX = 6;
const FLIP = {TB: ['LR', '↔ Horizontal'], LR: ['TB', '↕ Vertical']};
const atFit = v => v.k === 1 && v.x === 0 && v.y === 0;
const home = f => f ? Math.max(0, (f.vw - f.w) / 2) : 0;
/* The window's height: the fitted chart's, or more once its edge is dragged. */
const tall = c => Math.max(c.tall || 0, c.fit.h);
/* How many of the screen's pixels one of the window's own takes: home's
   zoom of the whole page. A pointer and a box's rectangle are the screen's;
   the chart's sizes and moves are the window's own, so each is divided. */
const scaleOf = c => { const p = c.el.querySelector('.cv');
  return p.offsetWidth ? p.getBoundingClientRect().width / p.offsetWidth : 1; };
function chart(src, svg) {
  const d = document.createElement('div');
  d.className = 'chart';
  d.innerHTML = '<div class="cf"><div class="strip">' + ZOOM_TOOLS
    + (flow(src) ? '<button class="flip" onmousedown="event.preventDefault()"></button>' : '')
    + '<span class="tip"></span></div><div class="cv"><div class="cz"></div>'
    + '<div class="sb x"><i></i></div><div class="sb y"><i></i></div></div>'
    + '<div class="grip" title="Drag down to make the chart bigger"></div></div>' + legend(src);
  const c = d.chart = {el: d, src, dir: DIR[src] || 'LR'};
  put(c, svg);
  wire(c);
  return d;
}
function put(c, svg) {
  const z = c.el.querySelector('.cz');
  z.innerHTML = svg;
  const box = z.querySelector('svg').viewBox.baseVal;
  c.nat = box && box.width ? {w: box.width, h: box.height} : {w: 400, h: 300};
  c.view = {...FIT};
  c.fit = null;
  c.tall = 0;
  measure(c);
}
/* A chart with no width yet measures nothing. It measures once it has one. */
function measure(c) {
  const p = c.el.querySelector('.cv');
  if (c.el.isConnected && p.clientWidth) {
    const main = c.el.closest('main');
    const area = main ? main.clientHeight : innerHeight;
    const extra = (c.el.getBoundingClientRect().height - p.getBoundingClientRect().height) / scaleOf(c) + 14;
    const vw = p.clientWidth, s = Math.min(1, vw / c.nat.w, Math.max(120, area - extra) / c.nat.h);
    c.fit = {s, w: c.nat.w * s, h: c.nat.h * s, vw};
    c.view = clampView(c, c.view);
  }
  repaint(c);
}
function repaint(c) {
  const d = c.el, f = c.fit, v = c.view, away = !atFit(v), b = d.querySelector('.flip');
  if (b) b.textContent = FLIP[c.dir][1];
  if (!f) return;
  const p = d.querySelector('.cv'), z = d.querySelector('.cz');
  p.style.height = tall(c) + 'px';
  z.style.width = f.w + 'px';
  z.style.height = f.h + 'px';
  z.style.transform = `translate(${home(f) + v.x}px, ${v.y}px) scale(${v.k})`;
  p.classList.toggle('away', away);
  bars(c);
  if (c.paint) c.paint();
  d.querySelector('.tip').textContent = away ? 'drag or swipe to pan'
    : f.s < 0.995 ? 'shrunk to fit · pinch to read' : 'pinch to zoom';
}
/* A scroll bar shows on an edge of the window only while the chart runs
   past it that way: along the bottom when it is wider, down the right when
   it is taller. Its thumb's length is how much of the chart shows, and it
   sits where the window looks. */
function bars(c) {
  const f = c.fit, v = c.view, d = c.el;
  axis(d.querySelector('.sb.x'), f.vw, f.w * v.k, -(home(f) + v.x), true);
  axis(d.querySelector('.sb.y'), tall(c), f.h * v.k, -v.y, false);
}
function axis(bar, frame, content, at, wide) {
  const on = content > frame + 0.5;
  bar.classList.toggle('on', on);
  if (!on) return;
  const t = bar.firstChild, track = wide ? bar.clientWidth : bar.clientHeight;
  const len = Math.max(24, track * frame / content), spot = Math.min(1, Math.max(0, at / (content - frame)));
  t.style[wide ? 'width' : 'height'] = len + 'px';
  t.style[wide ? 'left' : 'top'] = spot * (track - len) + 'px';
}
/* Bigger than the window, no edge comes inside it. Smaller, half of it
   stays in view. x counts from the middle, where the chart sits at Fit. */
const keep = (pos, content, frame, from = 0) => { const [lo, hi] = content > frame
  ? [frame - content, 0] : [-content / 2, frame - content / 2];
  return Math.min(hi - from, Math.max(lo - from, pos)); };
/* The rows of the window I can see. The page may scroll its top above
   main, or its bottom below it. A chart pans between these, so its top
   and bottom always come into sight. */
function seen(c) {
  const k = scaleOf(c), r = c.el.querySelector('.cv').getBoundingClientRect(), main = c.el.closest('main');
  const m = main ? main.getBoundingClientRect() : {top: 0, bottom: innerHeight};
  const t = Math.max(0, (m.top - r.top) / k);
  const b = Math.min(tall(c), (m.bottom - r.top) / k);
  return b > t ? {t, b} : {t: 0, b: tall(c)};
}
const clampView = (c, v) => { if (!c.fit) return v; const s = seen(c);
  return {k: v.k, x: keep(v.x, c.fit.w * v.k, c.fit.vw, home(c.fit)), y: keep(v.y, c.fit.h * v.k, s.b - s.t, -s.t)}; };
function zoomTo(c, k, at) {
  const v = c.view, next = Math.min(MAX, Math.max(1, k));
  if (!c.fit || next === v.k) return;
  if (next <= 1) { c.view = {...FIT}; return repaint(c); }
  const r = next / v.k, ax = at.x - home(c.fit);
  c.view = clampView(c, {k: next, x: ax - (ax - v.x) * r, y: at.y - (at.y - v.y) * r});
  repaint(c);
}
/* + and − zoom around the middle of what shows. */
function centre(c) {
  const f = c.fit, v = c.view;
  if (!f) return {x: 0, y: 0};
  const left = home(f) + v.x, x0 = Math.max(0, left), x1 = Math.min(f.vw, left + f.w * v.k);
  const s = seen(c), y0 = Math.max(s.t, v.y), y1 = Math.min(s.b, v.y + f.h * v.k);
  return {x: x1 > x0 ? (x0 + x1) / 2 : f.vw / 2, y: y1 > y0 ? (y0 + y1) / 2 : (s.t + s.b) / 2};
}
async function flipIt(c) {
  const b = c.el.querySelector('.flip'), to = FLIP[c.dir][0];
  b.disabled = true;
  try { const svg = await svgOf(c.src, to); c.dir = DIR[c.src] = to; put(c, svg); } catch (e) {}
  b.disabled = false;
}
/* The strip's zoom tools, and a pinch, are page.py's: ZOOM. A chart's own
   zoom, k, counts from its fitted size, so its size is the fit's times k.
   A swipe scrolls the page at Fit, and pans the chart away from it. A
   drag pans too. */
function wire(c) {
  const d = c.el, p = d.querySelector('.cv'), b = d.querySelector('.flip');
  c.paint = zoomer(d.querySelector('.zt'), p, {
    scale: () => c.fit ? c.fit.s * c.view.k : 0,
    bounds: () => [c.fit.s, c.fit.s * MAX],
    to: (s, at) => zoomTo(c, s / c.fit.s, at ? {x: at.x / scaleOf(c), y: at.y / scaleOf(c)} : centre(c)),
    fit: () => { c.view = {...FIT}; c.tall = 0; repaint(c); },
    fitted: () => atFit(c.view) && tall(c) === c.fit.h});
  if (b) b.onclick = () => flipIt(c);
  scrub(c, d.querySelector('.sb.x'), true);
  scrub(c, d.querySelector('.sb.y'), false);
  /* The bottom edge, dragged, sets the window's height. The zoom grows in
     step with it, around the window's middle, its top held still. The edge
     stays under the pointer. Held past the bottom of main, the page
     scrolls on, and the window keeps growing. */
  const g = d.querySelector('.grip');
  const pull = () => { const q = c.pull, f = c.fit;
    if (!q || !f) return;
    const top = p.getBoundingClientRect().top;
    const h = Math.min(q.h * MAX / q.v.k, Math.max(f.h, (q.at - q.off - top) / scaleOf(c)));
    const k = Math.max(1, q.v.k * h / q.h), r = k / q.v.k, ax = f.vw / 2 - home(f);
    c.tall = h;
    c.view = clampView(c, {k, x: ax - (ax - q.v.x) * r, y: q.v.y * r});
    repaint(c); };
  const roll = () => { const q = c.pull;
    if (!q) return;
    const main = d.closest('main');
    const floor = main ? main.getBoundingClientRect().bottom : innerHeight;
    if (main && q.at > floor && tall(c) < q.h * MAX / q.v.k - 0.5) { main.scrollTop += Math.min(20, 1 + (q.at - floor) / 3); pull(); }
    requestAnimationFrame(roll); };
  g.addEventListener('pointerdown', e => {
    if (e.button !== 0 || !c.fit) return;
    e.preventDefault();
    c.pull = {id: e.pointerId, at: e.clientY, off: e.clientY - p.getBoundingClientRect().bottom, h: tall(c), v: {...c.view}};
    g.setPointerCapture(e.pointerId);
    g.classList.add('drag');
    requestAnimationFrame(roll);
  });
  g.addEventListener('pointermove', e => {
    if (c.pull && c.pull.id === e.pointerId) { c.pull.at = e.clientY; pull(); } });
  const release = e => { if (c.pull && c.pull.id === e.pointerId) { c.pull = null; g.classList.remove('drag'); } };
  g.addEventListener('pointerup', release);
  g.addEventListener('pointercancel', release);
  p.addEventListener('wheel', e => {
    if (!c.fit || e.ctrlKey) return;
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? p.clientHeight : 1 / scaleOf(c);
    const v = c.view;
    if (atFit(v)) return;
    const next = clampView(c, {k: v.k, x: v.x - e.deltaX * unit, y: v.y - e.deltaY * unit});
    if (next.x === v.x && next.y === v.y) return;
    e.preventDefault();
    c.view = next;
    repaint(c);
  }, {passive: false});
  p.addEventListener('pointerdown', e => {
    if (e.button !== 0 || atFit(c.view)) return;
    c.drag = {id: e.pointerId, x: e.clientX, y: e.clientY, vx: c.view.x, vy: c.view.y, k: scaleOf(c)};
    p.setPointerCapture(e.pointerId);
    p.classList.add('drag');
  });
  p.addEventListener('pointermove', e => { const g = c.drag;
    if (!g || g.id !== e.pointerId) return;
    c.view = clampView(c, {k: c.view.k, x: g.vx + (e.clientX - g.x) / g.k, y: g.vy + (e.clientY - g.y) / g.k});
    repaint(c); });
  const up = e => { if (c.drag && c.drag.id === e.pointerId) { c.drag = null; p.classList.remove('drag'); } };
  p.addEventListener('pointerup', up);
  p.addEventListener('pointercancel', up);
}
/* A scroll bar's thumb drags the chart along its edge. A press on the bar
   beside the thumb brings the thumb there first. The bar never pans the
   window under it. */
function scrub(c, bar, wide) {
  const t = bar.firstChild, along = e => wide ? e.clientX : e.clientY;
  bar.addEventListener('pointerdown', e => {
    if (e.button !== 0 || !c.fit) return;
    e.stopPropagation();
    e.preventDefault();
    const f = c.fit, v = c.view, r = bar.getBoundingClientRect(), k = scaleOf(c);
    const frame = wide ? f.vw : tall(c), content = (wide ? f.w : f.h) * v.k;
    const len = wide ? t.offsetWidth : t.offsetHeight, room = (wide ? r.width : r.height) / k - len;
    if (room <= 0) return;
    const per = (content - frame) / room, from = along(e);
    const at = e.target === t ? (wide ? -(home(f) + v.x) : -v.y) : ((from - (wide ? r.left : r.top)) / k - len / 2) * per;
    const go = m => { const to = at + (along(m) - from) / k * per;
      c.view = clampView(c, wide ? {...c.view, x: -to - home(f)} : {...c.view, y: -to});
      repaint(c); };
    go(e);
    bar.setPointerCapture(e.pointerId);
    bar.classList.add('drag');
    bar.onpointermove = go;
    bar.onpointerup = bar.onpointercancel = () => { bar.onpointermove = null; bar.classList.remove('drag'); };
  });
}
const fitAll = () => document.querySelectorAll('#items .chart').forEach(d => measure(d.chart));
addEventListener('resize', () => { charts(); fitAll(); });

/* An assistant's proposal, under the session's own decision and above its
   why, so I read the decision first. Take it presses
   Agree, or writes its words as my feedback, still mine to edit. Either
   moves on to the next open item, as Agree does. */
function parts(it) {
  const [verdict, ...rest] = String(it.proposed || '').split('\\n');
  const field = k => rest.filter(l => l.startsWith(k + ':')).map(l => l.slice(k.length + 1).trim()).join(' ');
  return {v: verdict.trim().toLowerCase(), by: field('by'), why: field('why'),
    words: rest.filter(l => l.startsWith('>')).map(l => l.replace(/^>\\s?/, '')).join('\\n')};
}
function proposal(it) {
  if (!it.proposed) return '';
  const p = parts(it), agree = p.v === 'agree';
  const taken = agree ? it.agree === 'yes' : (it.feedback || '').trim() === p.words.trim();
  return `<div class="prop"><div class="ph">${p.by ? 'Session ' + esc(p.by) + ', your assistant,' : 'Your assistant'}`
    + ` proposes · ${agree ? 'Agree' : 'Feedback'}</div>`
    + (p.why ? `<p class="pw">${link(p.why)}</p>` : '')
    + (p.words ? `<blockquote class="pq">${esc(p.words)}</blockquote>` : '')
    + `<button class="take" onclick="takeIt('${esc(it.n)}')" ${taken || D.sent ? 'disabled' : ''}>`
    + `${taken ? '✓ Taken' : agree ? 'Take it · Agree' : 'Take it · into the feedback box'}</button></div>`;
}
function takeIt(n) {
  const it = find(n);
  if (!it || D.sent) return;
  const p = parts(it);
  if (p.v === 'agree') {
    if (it.agree !== 'yes') { it.agree = 'yes'; post({act: 'agree', n: it.n, on: 'yes'}); }
    refresh(it);
    if (!it.feedback) go(next(it.n));
    return;
  }
  it.feedback = p.words;
  pending = it;
  flush();
  refresh(it);
  go(next(it.n));
}

function splitList(s) {
  return ul(bullets(s).map(x => { const [a, b] = x.split(/\\s*→\\s*/);
    return link(a) + (b ? ` <span class="out">→ ${link(b)}</span>` : ''); }), 'split');
}

/* Each item's own feedback box, at its foot. Its words are set once the
   card is drawn, as a box's value. */
const box = it => `<div class="fbx"><div class="lab"><span>Your feedback on item ${esc(it.n)}</span>`
  + `<span class="st"></span></div><textarea id="fb-${esc(it.n)}" data-n="${esc(it.n)}"`
  + ` placeholder="Your feedback on item ${esc(it.n)}${PHONE ? '.'
    : ': type or paste anywhere. Return moves on, and sends once all are answered. Shift+Return makes a new line.'}"`
  + `${D.sent ? ' disabled' : ''}></textarea></div>`;

/* The item's number, in its colour, then the question, the decision, an
   assistant's proposal, then the decision's lines, then the picture under
   them, always. Then today and instead. A wave written by hand adds its
   case and its split, as it always drew them. Its feedback box closes it. */
function card(it) {
  const c = colour(it);
  let a = `<p class="dec"><span class="arr">→</span>${link(it.decision)}</p>` + proposal(it);
  for (const [k, word] of [['why', 'Why'], ['wrong', 'Wrong if'], ['from', 'From'], ['after', 'After']])
    if (it[k]) a += `<p class="why"><span class="k">${word}</span>${link(it[k])}</p>`;
  let s = `<h1 class="q"><span class="chip${c === 'grey' ? ' g' : ''}">${esc(it.n)}</span>${esc(it.question)}</h1>`
    + a + (it.show ? para(it.show) : '');
  if (it.split) s += `<h3 class="sub">How I read it</h3>` + splitList(it.split);
  if (it.answer) s += `<h3 class="sub">My answer</h3>` + para(it.answer);
  if (it.changed) s += `<h3 class="sub">What changed</h3>` + list(it.changed);
  if (it.led) s += `<h2 class="sec">Led to</h2>` + para(it.led);
  if (it.today) s += `<h2 class="sec">Today</h2>` + para(it.today);
  if (it.instead) s += `<h2 class="sec">Instead</h2>` + list(it.instead);
  if (it.context || it.for || it.against) {
    s += `<h2 class="sec">The case</h2>`;
    if (it.context) s += `<div class="row"><span class="k">Context</span><div class="v">${para(it.context)}</div></div>`;
    if (it.for) s += `<div class="row"><span class="k">For</span><div class="v">${list(it.for)}</div></div>`;
    if (it.against) s += `<div class="row"><span class="k">Against</span><div class="v">${list(it.against)}</div></div>`;
  }
  if (it.sources) s += `<p class="srcs">${esc(it.sources)}</p>`;
  return `<section class="item" id="t-${esc(it.n)}" style="--c:var(--${c})">${s}${box(it)}</section>`;
}


/* Every item, drawn once. After that, an answer repaints only its own
   item, so no chart ever draws twice and the page never jumps. */
function draw() {
  const items = D.items;
  document.getElementById('index').innerHTML =
    items.map(it => { const c = colour(it);
      return `<div class="tab${c === 'grey' ? ' g' : ''}${hint(it) ? ' hint' : ''}" data-k="${esc(it.n)}" style="--c:var(--${c});--h:var(--${hint(it) || c})"
        title="${esc(it.question)}" onclick="go('${esc(it.n)}')">${esc(it.n)}</div>`; }).join('');
  document.getElementById('items').innerHTML = items.map(card).join('');
  document.querySelectorAll('#items .fbx textarea').forEach(t => listen(t, find(t.dataset.n)));
  sendButton();
  room();
  const want = decodeURIComponent(location.hash.slice(1));
  const first = (items.find(it => !answered(it)) || items[0] || {}).n || '';
  const landed = find(want) ? want : first;
  go(landed);
  /* A chart drawn above the item pushes it down. Unless I moved, it goes
     back to the top. */
  charts().then(() => { if (cur === landed && !typing) go(landed); });
}

/* The item Agree acts on: the one whose box holds the cursor, else the
   one at the top. The rail's outline sits on it too. */
let typing = null;
const at = () => typing || cur;
const boxOf = n => document.getElementById('fb-' + n);
const main = () => document.querySelector('main');

/* An item's top, under its rectangle, in main's scroll pixels. The visible
   rectangles agree across browsers; main's scale converts them to scroll
   pixels when home's zoom changes. */
function placeOf(el) {
  const m = main(), mr = m.getBoundingClientRect(), er = el.getBoundingClientRect();
  const scale = mr.height / m.offsetHeight || 1;
  return m.scrollTop + (er.top - mr.top) / scale + el.clientTop - m.clientTop;
}

/* A number brings its item's top, under its rectangle, to the top of main. */
function go(k, focus) {
  flush();
  cur = String(k);
  part = 0;
  const el = document.getElementById('t-' + cur);
  if (el) main().scrollTop = placeOf(el);
  if (focus && boxOf(cur)) boxOf(cur).focus({preventScroll: true});
  outline();
}

/* The item at the top follows the scroll: the last whose top sits within
   80px of main's top. */
function spy() {
  const now = main().scrollTop;
  let to = (D.items[0] || {}).n;
  for (const it of D.items) {
    const el = document.getElementById('t-' + it.n);
    if (el && placeOf(el) - now <= 80) to = it.n;
  }
  const el = to && document.getElementById('t-' + to);
  part = el && el.offsetHeight ? (now - placeOf(el)) / el.offsetHeight : 0;
  if (to && to !== cur) { cur = to; outline(); }
}

/* Home's zoom reflows the page under the same scrollTop, and the scroll it
   causes would move the item at the top. So, after the reflow, each chart
   fits again, and the item I was reading comes back as far into it as I was,
   still the one Agree and my typing go to. */
addEventListener('ws-zoom', () => {
  const n = cur, into = part;
  requestAnimationFrame(() => {
    fitAll();
    room();
    const el = document.getElementById('t-' + n);
    if (el) main().scrollTop = placeOf(el) + into * el.offsetHeight;
    cur = n;
    part = into;
    outline();
  });
});

/* Room after the last item, so a number brings even its top to the top. */
function room() {
  const last = document.querySelector('#items .item:last-child');
  if (!last) return;
  const pad = parseFloat(getComputedStyle(document.getElementById('items')).paddingBottom) || 0;
  last.style.minHeight = (main().clientHeight + last.clientTop - pad) + 'px';
}

function outline() {
  tab(at());
  tools();
}

function tools() {
  const it = find(at()), a = document.getElementById('agree');
  a.className = 'agree' + (it && agreed(it) ? ' on' : '') + (it && locked(it) ? ' locked' : '');
  a.disabled = !it || !!D.sent || locked(it);
  a.textContent = !it ? 'Agree' : locked(it) ? 'Agreed before' : agreed(it) ? '✓ Agreed' : 'Agree';
}

/* A box is one line at rest. It opens while I type in it, or while it
   holds my answer, and grows with the text. */
function fit(t) {
  const open = document.activeElement === t || !!t.value.trim();
  t.parentNode.classList.toggle('open', open);
  t.style.height = 'auto';
  t.style.height = (open ? Math.max(t.scrollHeight + 4, 84) : 40) + 'px';
}

/* Paints what one answer changes, and leaves its box alone. */
function paint(it) {
  const c = colour(it);
  const rail = document.querySelector(`#index .tab[data-k="${it.n}"]`);
  rail.style.setProperty('--c', `var(--${c})`);
  rail.classList.toggle('g', c === 'grey');
  rail.classList.toggle('hint', !!hint(it));
  rail.style.setProperty('--h', `var(--${hint(it) || c})`);
  const sec = document.getElementById('t-' + it.n);
  sec.style.setProperty('--c', `var(--${c})`);
  sec.querySelector('h1.q .chip').classList.toggle('g', c === 'grey');
  sendButton();
  status(it);
}

/* One item repainted where it stands: its colours, its proposal, its box. */
function refresh(it) {
  const p = document.querySelector(`#t-${it.n} .prop`), t = boxOf(it.n);
  if (p) p.outerHTML = proposal(it);
  if (t.value !== (it.feedback || '')) t.value = it.feedback || '';
  t.disabled = !!D.sent;
  fit(t);
  paint(it);
}

function status(it, text) {
  document.querySelector(`#t-${it.n} .fbx .st`).textContent = D.sent ? 'This wave is sent.' : text
    || (it.feedback ? 'Saved. It counts as your answer.' : 'Anything you type counts as your answer.');
}

/* Send reads Sent, what is left, or Not typed when the last press typed
   nothing, its reason on hover. It spins while its line types. */
function sendButton() {
  const left = D.items.filter(it => !answered(it)).length;
  const button = document.getElementById('send');
  const lost = !D.sent && !left && D.gone;
  button.disabled = !!D.sent || left > 0 || !!D.typing;
  button.classList.toggle('sent', !!D.sent);
  button.classList.toggle('gone', !!lost);
  button.classList.toggle('busy', !!D.typing);
  button.title = lost || '';
  button.textContent = D.sent ? 'Sent' : left ? 'Send · ' + left + ' left' : lost ? NOT_TYPED : 'Send';
}

/* Every keystroke is the answer. It is posted half a second after the
   last one, and at once when I leave the box or press Send. */
function typed(it, t) {
  if (D.sent) return;
  it.feedback = t.value;
  pending = it;
  paint(it);
  status(it, 'Saving…');
  clearTimeout(timer);
  timer = setTimeout(flush, 500);
}

/* A save that never landed says so, and is tried again with the next
   keystroke or the next flush. */
function flush() {
  clearTimeout(timer);
  if (!pending) return Promise.resolve();
  const it = pending;
  pending = null;
  return post({act: 'feedback', n: it.n, text: it.feedback}).then(landed => {
    if (landed) return status(it);
    if (!pending) pending = it;
    status(it, 'Not saved: 1100 did not answer. It saves again as you type.');
  });
}

function next(n) {
  const open = D.items.filter(it => !answered(it)).map(it => it.n);
  return open.find(k => Number(k) > Number(n)) || open[0] || n;
}

/* A second click cancels this wave's Agree. An agree moves on to the next
   open item, and a box holding the cursor hands it to that item's box. */
function agree() {
  const it = find(at());
  if (!it || D.sent || locked(it)) return;
  it.agree = it.agree === 'yes' ? '' : 'yes';
  post({act: 'agree', n: it.n, on: it.agree});
  refresh(it);
  const n = next(it.n);
  if (it.agree === 'yes' && !it.feedback && n !== it.n) go(n, !!typing);
  else tools();
}

/* Send waits for the last keystroke to land, so the session reads it.
   Only a line that typed reads Sent. Anything else says why. */
function send() {
  if (D.sent || D.typing || !D.items.every(answered)) return;
  D.typing = true;
  D.gone = '';
  refusal('');
  sendButton();
  flush().then(() => typePost({act: 'send'})).then(why => {
    D.typing = false;
    if (why === '') D.sent = 'yes';
    else refusal(D.gone = why || UNANSWERED);
    D.items.forEach(refresh);
    tools();
  });
}

/* On my Mac, Return in a box moves on to the next open item, the cursor
   in its box. With none left open, it sends. Shift+Return makes a new
   line. My phone's Return makes a new line. */
function listen(t, it) {
  t.value = it.feedback || '';
  t.addEventListener('input', () => { typed(it, t); fit(t); });
  t.addEventListener('keydown', e => {
    if (PHONE || e.isComposing || e.key !== 'Enter' || e.shiftKey || e.altKey || e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    const n = next(it.n);
    if (n === it.n && D.items.every(answered)) send();
    else go(n, true);
  });
  t.addEventListener('focus', () => { typing = it.n; fit(t); outline(); });
  t.addEventListener('blur', () => { if (typing === it.n) typing = null; fit(t); flush(); outline(); });
  fit(t);
  status(it);
}

/* On my Mac, a letter or a paste anywhere on the page lands in the box of
   the item at the top, with no click. Home hands it one landing on home
   itself, through typeIn. */
anywhere(text => {
  const it = find(at()), t = it && boxOf(it.n);
  if (!t || t.disabled) return false;
  t.focus();
  t.setRangeText(text, t.value.length, t.value.length, 'end');
  t.dispatchEvent(new Event('input'));
  return true;
});
main().addEventListener('scroll', spy, {passive: true});
/* Main's own size is watched, so the room after the last item follows the
   glass, home's rail and home's zoom alike. */
new ResizeObserver(room).observe(main());
addEventListener('beforeunload', flush);
draw();
</script>
"""


def key(nn: str) -> str:
    """What the page reloads on: the wave, sent or closed, every item's
    answer and proposal, and who drives the session. A controller's rule, an
    assistant's proposal or its Send answers each move it, so the page never
    shows an answer the file no longer holds. My own typing moves it too:
    the page saves it through page.py's post(), which takes the key the
    save left, so its own save never reloads it."""
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


def render(nn: str) -> str:
    wave, _, head, items = newest(nn)
    worn = key(nn)
    by = successor.driven(nn)
    # The top rail: the family and the session, the wave, then Agree and
    # Send side by side. A session another drives wears a band under it,
    # naming its driver, and a partial drive's topic. A press on Agree
    # leaves the cursor in its box, so Agree acts on that box's item.
    tools = ('<span class="group"><button id="agree" class="agree" onmousedown="event.preventDefault()"'
             ' onclick="agree()"></button>'
             '<button id="send" onclick="send()"></button></span>') if items else ""
    top = page.head("clarify", plans.tag(nn), f"Wave {wave}" if wave else "", tools,
                    band(by, successor.topics().get(nn, "")) if items else "")
    if not items:
        body = page.blank("No items wait") + "\n" + page.watch(worn)
        return page.render(f"{nn}-clarify", [("", body)], top, refresh=0)
    rail = top + '<nav class="nums" id="index"></nav>\n'
    for it in items:
        it["question"] = it.get("question") or it.get("title", "")
    data = json.dumps({"wave": wave, "sent": head.get("sent", ""), "items": items})
    body = ('<div id="items"></div>\n'
            + page.watch(worn) + page.POST + page.TYPING + page.ANYWHERE + page.ZOOM
            + SCRIPT % data.replace("</", "<\\/"))
    return page.render(f"{nn}-clarify", [("", body)], rail, refresh=0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["wave", "answers", "close", "propose", "rule", "send"])
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
