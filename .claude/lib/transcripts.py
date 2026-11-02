"""transcripts.py — every session's transcript, read as what was said.

A transcript is mostly tool traffic. turns() keeps what was said: my
turns, the session's turns, and one line for each skill it ran and each
file it wrote. A live session is found by its record, an ended one by its
title, which opens with its number.

last_said() keeps only a session's last words since my turn, and its
move.

copy() writes a session's transcript as something I can read.

thread() reads it whole: inside each of the session's turns, its text, each skill, each file and every other tool
call, in order, numbered as turns() numbers them. A command and an agent
also keep the first lines of what came back, and, sent to the background,
whether they still run, until a task's notice says how they ended. A turn
that something other than me started, an agent's report or a task's
notice, keeps a wake where it began. Read again, it reads only what was
written since.

Both match the pane. A prompt I took back with Escape is never kept:
settles() tells which, as the records after it arrive.

since() finds every transcript written since a time, for a checkup.

touched() finds the files one transcript wrote, with a tool or the shell.

Every tool reading a transcript reads it here, once.
"""

import base64
import datetime
import glob
import io
import json
import keyword
import os
import re
import struct
import textwrap
import threading
import time
import tokenize
import traceback

import registry

ROOT = registry.ROOT

# Every account directory in registry.LIVE holds one folder per project,
# named after its path with every separator turned into a dash.
SLUG = ROOT.replace("/", "-")

# A bookmark: a record's time on this Mac's clock, to the second.
STAMP = "%Y-%m-%dT%H:%M:%S"

# The tool calls that write a file.
WRITERS = ("Write", "Edit", "MultiEdit", "NotebookEdit")

# Wrappers the harness adds around what was actually said.
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
NOISE = ("<local-command-", "<bash-input>", "<bash-stdout>", "<bash-stderr>",
         "Caveat:", "[Request interrupted", "[Your previous response")
PASTED = re.compile(r"<pasted_content[^>]*>(.*?)</pasted_content[^>]*>", re.S)
TYPED = re.compile(r"<command-name>(/[^<]+)</command-name>"
                   r"(?:\s*<command-args>(.*?)</command-args>)?", re.S)
BODY = re.compile(r"Base directory for this skill: ")
# What one of Claude Code's own commands answered, as /context's grid.
OUT = re.compile(r"<local-command-std(?:out|err)>(.*?)</local-command-std(?:out|err)>", re.S)
# A line I typed after !, run in the pane's shell, and what it printed.
BASH_IN = re.compile(r"<bash-input>(.*?)</bash-input>", re.S)
BASH_OUT = re.compile(r"<bash-std(?:out|err)>(.*?)</bash-std(?:out|err)>", re.S)
# The colours a terminal draws an answer in.
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
REPORT = re.compile(r"Session (\d{2}) reports:")
# A turn's move, however its label is marked: "**Your move.**", "**Your move:**"
# or "**Your move**", then the move on the same line or the next.
MOVE = re.compile(r"\*\*Your move[.:]?\*\*[.:]?\s*(.+)")


def records(path: str):
    with open(path, errors="ignore") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def title_of(path: str) -> str:
    """The last title a transcript carries. A rename wins over Claude Code's own."""
    custom = ai = ""
    for d in records(path):
        custom = d.get("customTitle") or custom
        ai = d.get("aiTitle") or ai
    return custom or ai


def find(number: str) -> tuple:
    """Session NN's transcript and title. Its record first, then the newest title."""
    rec = registry.entries().get(number)
    if rec and os.path.isfile(rec.get("transcript", "")):
        return rec["transcript"], rec.get("title", number)
    found = []
    for account in registry.LIVE:
        found += glob.glob(os.path.expanduser(f"{account}/projects/{SLUG}/*.jsonl"))
    for path in sorted(found, key=os.path.getmtime, reverse=True):
        title = title_of(path)
        if title.startswith(f"{number}-") or title == number:
            return path, title
    return "", ""


def since(t: datetime.datetime, agents: bool = False) -> list:
    """Every transcript written since `t`, account by account, and its
    subagents' too when asked."""
    found = []
    for account in registry.LIVE:
        base = os.path.expanduser(f"{account}/projects/{SLUG}")
        for path in glob.glob(f"{base}/*.jsonl") + (glob.glob(f"{base}/*/subagents/*.jsonl") if agents else []):
            if os.path.getmtime(path) < t.timestamp():
                continue
            found.append(path)
    return found


def moment(d: dict):
    """A record's time, or None when it carries none."""
    try:
        return datetime.datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return None


def when(d: dict, form: str) -> str:
    at = moment(d)
    return at.astimezone().strftime(form) if at else ""


def clock(d: dict) -> str:
    return when(d, "%H:%M")


def stamp(d: dict) -> str:
    """A record's time on this Mac's clock, to the second. A bookmark is one."""
    return when(d, STAMP)


def texts(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or []
                     if isinstance(b, dict) and b.get("type") == "text")


def opener(d: dict) -> bool:
    """A record that starts a turn: my prompt, a picture alone too, or a
    task's notice. A tool's result and a skill's body arrive mid-turn."""
    if d.get("type") != "user" or d.get("isMeta") or d.get("sourceToolUseID"):
        return False
    content = (d.get("message") or {}).get("content")
    return not (isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content))


def mine(d: dict) -> str:
    """What I said in one record, or "" when it holds nothing of mine.

    A task's notice and another agent's report arrive as user records too.
    Their origin says so. A compaction's summary arrives as one too, marked
    isCompactSummary. A line typed while the session worked, that it read
    mid-turn, arrives as a queued command, its origin mine.
    """
    if d.get("type") == "attachment":
        queued = d.get("attachment") or {}
        if (not isinstance(queued, dict) or queued.get("type") != "queued_command"
                or (queued.get("origin") or {}).get("kind") != "human"):
            return ""
        d = {"message": {"content": queued.get("prompt")}}
    if d.get("isMeta") or d.get("sourceToolUseID") or d.get("isCompactSummary"):
        return ""
    if (d.get("origin") or {}).get("kind", "human") != "human":
        return ""
    text = texts(d.get("message") or {}).strip()
    typed = TYPED.search(text) if text.startswith("<command-") else None
    if typed:
        return f"{typed.group(1)} {(typed.group(2) or '').strip()}".strip()
    if BODY.match(text):
        return ""
    held = PASTED.findall(text)
    text = "\n\n".join(p.strip() for p in held) if held else REMINDER.sub("", text).strip()
    if not text or any(text.startswith(n) for n in NOISE):
        return ""
    return text


def last_said(path: str) -> tuple:
    """A session's last words since my turn, as (words, record, move).

    The record is the one carrying the words, so clock() and stamp() read
    their time. The move is the words' Your move line, else their last
    line. Nothing said since my turn gives ("", {}, ""). A prompt I took
    back is no turn of mine: the words before it stand.
    """
    said, at, waits = "", {}, None
    for d in registry.tail(path):
        if waits and (got := settles(d, waits[1])):
            said, at = waits[0] if got == "back" else (said, at)
            waits = None
        if d.get("type") == "assistant":
            text = texts(d.get("message") or {}).strip()
            if text:
                said, at = text, d
        elif d.get("type") == "user" and mine(d):
            waits = ((said, at), d.get("parentUuid")) if d.get("uuid") else None
            said, at = "", {}
    if waits and idle(path):
        said, at = waits[0]
    if not said:
        return "", {}, ""
    moves = MOVE.findall(said)
    move = moves[-1] if moves else said.splitlines()[-1]
    return said, at, move.replace("**", "").strip()


def written(block: dict) -> str:
    """The file one tool call writes, or "" when it writes none."""
    if block.get("type") != "tool_use" or block.get("name") not in WRITERS:
        return ""
    got = block.get("input") or {}
    return got.get("file_path") or got.get("notebook_path") or ""


def acts(message: dict) -> list:
    """One line per skill run and per file written."""
    out = []
    for b in message.get("content") or []:
        if not isinstance(b, dict) or b.get("type") != "tool_use":
            continue
        got = b.get("input") or {}
        if b.get("name") == "Skill":
            out.append(f"→ ran {got.get('skill', '')} {got.get('args', '')}".rstrip())
        elif written(b):
            out.append(f"→ wrote {os.path.relpath(written(b), ROOT)}")
    return out


def settles(d: dict, parent) -> str:
    """What one record says of my prompt nothing has answered yet, whose
    record follows `parent`: "back" when I took it back, "kept" when
    something answered it, "" when it says neither.

    Escape pulls a prompt just sent back out of the pane, before any
    answer. Claude Code writes nothing to say so. The next record it writes
    follows the prompt's own parent, as if it was never sent. Anything else
    answers it, even a command's output. A notice attached, or a skill's
    body written with the prompt, says neither.
    """
    if not d.get("uuid"):
        return ""
    if d.get("parentUuid") == parent:
        return "back"
    return "" if d.get("type") == "attachment" or d.get("isMeta") else "kept"


def idle(path: str) -> bool:
    """Whether the session writing this transcript runs, and waits on me.
    Idle, with my last prompt unanswered, it took that prompt back. An
    ended session's last prompt stands: often a stop it obeyed."""
    rec = registry.claude_records().get(os.path.basename(path).removesuffix(".jsonl"))
    return (rec or {}).get("status") == "idle"


def ended(path: str) -> bool:
    """Whether the session writing this transcript ended its last turn.
    Claude Code closes a turn with one record, its turn_duration. A word or
    act after it, mine or the session's, opens the next."""
    for d in reversed(registry.tail(path)):
        if d.get("isSidechain"):
            continue
        if d.get("type") == "system" and d.get("subtype") == "turn_duration":
            return True
        if d.get("type") in ("user", "assistant"):
            return False
    return False


def turns(path: str, number: str) -> list:
    """Every turn, in order, as (speaker, time, lines, end). A session's text
    and acts between two of my turns are one turn. `end` is its last record's
    stamp, so a turn still being written when a bookmark was kept is read
    again next time. A line of mine it read mid-turn splits its turn. A
    prompt I took back is dropped."""
    out, waits = [], None
    for d in records(path):
        if waits and (got := settles(d, waits[1])):
            out = [t for t in out if t is not waits[0]] if got == "back" else out
            waits = None
        kind = d.get("type")
        if kind in ("user", "attachment"):
            said = mine(d)
            if said:
                sender = REPORT.match(said)
                who = f"Session {sender.group(1)} · report" if sender else "User"
                out.append([who, clock(d), [said], stamp(d)])
                waits = (out[-1], d.get("parentUuid")) if kind == "user" and d.get("uuid") else waits
        elif kind == "assistant":
            message = d.get("message") or {}
            lines = ([t] if (t := texts(message).strip()) else []) + acts(message)
            if not lines:
                continue
            if not out or out[-1][0] != f"Session {number}":
                out.append([f"Session {number}", clock(d), [], ""])
            out[-1][2] += lines
            out[-1][3] = stamp(d)
    if waits and idle(path):
        out = [t for t in out if t is not waits[0]]
    return out


def drawn(said: list, first: int = 1) -> list:
    return [f"## {i} · {at} · {who}\n\n" + "\n\n".join(lines)
            for i, (who, at, lines, _) in enumerate(said, first)]


def copy(number: str, out: str) -> list:
    """Session NN's transcript, written whole into `out`: its title, its
    path, its turns and their span, then every turn, numbered. A copy made
    again replaces the last. Returns the head's lines, or [] when the
    session has no transcript."""
    path, title = find(number)
    if not path:
        return []
    said = turns(path, number)
    head = [f"# {title}", "", f"Transcript: {path}",
            f"Turns: {len(said)}, from {said[0][1]} to {said[-1][1]}." if said else "Turns: 0.", ""]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(head) + "\n" + "\n\n".join(drawn(said)) + "\n")
    return head


# ---- the files a transcript wrote, for a checkup and a session's check --------

# A shell command writes a file when it redirects into it, opens it for
# writing, or names it in a command that edits in place, moves, copies or
# deletes. A script writes what its write aims at: what open() takes for
# writing, or what write_text() is called on. A variable there holds what
# last set it: its value, its loop's list, or what each call of its
# function passes it. A name may drop its leading folders, down to its own
# folder and file, since sessions often work from inside one.
SEGMENT = re.compile(r"&&|\|\||;|\||\n")
EDITS = re.compile(r"^\s*(?:sed -i|tee|mv|cp|rm|git mv|git rm)\b")
SCRIPTED = re.compile(r"\bopen\(\s*([A-Za-z_][\w.]*)\s*,\s*['\"][wa]|([\w.]*(?:\([^()]*\))?)\.write_text\(")
# Where a script sets a variable: assigned, looped over, or a parameter of
# a function it defines.
SETS = (r"(?m)(?:^|;)[ \t]*(?:(?P<value>{v}[ \t]*=(?!=))|(?P<loop>for\b[^\n]*?\b{v}\b[^\n]*?\bin\b)"
        r"|def[ \t]+(?P<fn>\w+)\((?P<params>[^)\n]*\b{v}\b[^)\n]*)\))")
# A string's words, whole, or between an f-string's fields.
TEXT = (tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", tokenize.STRING))


def statement(text: str) -> list:
    """The tokens of the Python statement `text` opens with: its line, and
    every line after it a bracket or a string keeps open."""
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.NEWLINE:
                return out
            out.append(tok)
    except (tokenize.TokenError, SyntaxError):
        pass
    return [t for t in out if t.start[0] == 1]


def reads(toks: list) -> list:
    """The variables a statement reads: each name but a keyword or an attribute."""
    return [t.string for i, t in enumerate(toks) if t.type == tokenize.NAME
            and not keyword.iskeyword(t.string) and not (i and toks[i - 1].string == ".")]


def argument(toks: list, k: int) -> list:
    """The tokens of a call's k-th argument."""
    depth, at, out = 0, 0, []
    for t in toks:
        if t.string in (")", "]", "}"):
            depth -= 1
        if depth == 1 and t.string == ",":
            at += 1
        elif depth and at == k:
            out.append(t)
        if t.string in ("(", "[", "{"):
            depth += 1
    return out


def holds(cmd: str, var: str, at: int, steps: int = 3) -> list:
    """The strings a script's variable holds where it is read, `at`
    characters into the command: what last set it before then, and what
    the variables there hold, `steps` deep."""
    sets = list(re.finditer(SETS.format(v=re.escape(var)), cmd[:at])) if steps else []
    if not sets:
        return []
    got = sets[-1]
    if got.group("fn"):
        params = [p.split("=")[0].split(":")[0].strip(" *") for p in got.group("params").split(",")]
        if var not in params:
            return []
        calls = re.finditer(rf"(?m)^[ \t]*({re.escape(got.group('fn'))}\()", cmd)
        found = [(c.start(1), argument(statement(cmd[c.start(1):]), params.index(var))) for c in calls]
    else:
        toks = statement(cmd[got.start("value") if got.group("value") else got.start("loop"):])
        cut = next((i for i, t in enumerate(toks) if t.string == ("=" if got.group("value") else "in")), len(toks))
        found = [(got.start(), toks[cut + 1:])]
    out = []
    for where, toks in found:
        out += [t.string for t in toks if t.type in TEXT]
        for name in reads(toks):
            out += holds(cmd, name, where, steps - 1)
    return out


def aimed(cmd: str) -> list:
    """What each scripted write in a command aims at, as the strings naming it."""
    out = []
    for m in SCRIPTED.finditer(cmd):
        toks = statement(m.group(1) or m.group(2))
        out.append("\n".join([t.string for t in toks if t.type in TEXT]
                             + [s for name in reads(toks) for s in holds(cmd, name, m.start())]))
    return out


def shell_writes(cmd: str, files: set) -> set:
    """The files among `files` one shell command writes, moves or deletes.

    A command names its files in free text, so it is searched only for the
    files asked about: behaviour-doctor asks about a checkup's window, and
    coder-check about what git shows changed since a session's last check.
    """
    hit, aims = set(), aimed(cmd)
    for f in files:
        parts = f.split("/")
        for name in {f} | {"/".join(parts[i:]) for i in range(1, len(parts) - 1)}:
            if name not in cmd:
                continue
            quoted = re.escape(name)
            if (re.search(rf">>?\s*['\"]?[\w./-]*{quoted}\b", cmd)
                    or re.search(rf"open\(\s*['\"][\w./-]*{quoted}['\"]\s*,\s*['\"][wa]", cmd)
                    or any(name in a for a in aims)
                    or any(EDITS.match(s) and name in s for s in SEGMENT.split(cmd))):
                hit.add(f)
    return hit


def touched(path: str, since: datetime.datetime, files: set) -> set:
    """The files among `files` one transcript wrote after `since`: each a
    Write or an Edit named, and each a shell command wrote, moved or deleted.

    behaviour-doctor finds a checkup's writers with it, and coder-check the
    files a session wrote, so both read a write the same way.
    """
    hit = set()
    for d in records(path):
        at = moment(d)
        if not at or at < since:
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if not isinstance(b, dict) or b.get("type") != "tool_use":
                continue
            target = written(b)
            if target and os.path.relpath(target, ROOT) in files:
                hit.add(os.path.relpath(target, ROOT))
            elif b.get("name") == "Bash":
                hit |= shell_writes((b.get("input") or {}).get("command", ""), files)
    return hit


# ---- the whole thread, as the transcript page draws it ------------------------

BROWSER = "mcp__playwright__browser_"
# A browser step, in words. Any other says its own name.
STEPS = {"navigate": "Opened {url}", "navigate_back": "Went back",
         "resize": "Resized the browser to {width} × {height}", "take_screenshot": "Took a screenshot",
         "console_messages": "Read the browser's console", "run_code_unsafe": "Ran a script in the browser",
         "evaluate": "Ran a script in the browser", "click": "Clicked {element}",
         "snapshot": "Read the page's structure", "close": "Closed the browser"}
# What a task's notice or an agent's report opens with, queued like my lines.
NOTICE = ("<task-notification", "<agent-message")
# A command and an agent each take a line of their own on the page, with
# the first lines of what came back.
LOUD = ("command", "agent")
PEEK = 4
# A browser call still running after two minutes, which Claude Code moves
# to the background, as its answer says.
MOVED = re.compile(r"moved to the background as task (\w+)")
# The tools that stop a background task by hand.
STOPS = ("TaskStop", "KillShell", "KillBash")
# A server, as the command starting it reads. It runs all session long, so
# it never counts as work still running.
SERVER = re.compile(r"\bPORT=\d+|\b(?:pnpm|npm run) dev\b")
# A task's notice names the call it answers, how it ended, and what it took.
TOLD = re.compile(r"<tool-use-id>([^<\s]+)</tool-use-id>")
# An agent's last notice can name only its task.
TASK = re.compile(r"<task-id>([^<\s]+)</task-id>")
ENDED = re.compile(r"<status>([^<\s]+)</status>")
USED = re.compile(r"<tool_uses>(\d+)</tool_uses>")
TOOK = re.compile(r"<duration_ms>(\d+)</duration_ms>")
RESULT = re.compile(r"<result>([\s\S]*?)</result>")
# Claude Code marks the record that starts each turn with what started it.
# These two are not me: an agent's report, and a task's notice.
WAKES = ("peer", "task_notification")
# An agent's report sits under the harness's frame, each line indented.
FOLLOWS = "The report follows:\n"
# A notice whose result only points at the report, already delivered.
POINTED = "delivered to you as a message"
# A notice from an agent waiting on background work of its own. It is not
# done: its report comes later.
INTERIM = "has not reported yet"


def shown(path: str) -> str:
    """A path as I read it: from the project's root, when it sits inside."""
    path = str(path)
    return os.path.relpath(path, ROOT) if os.path.isabs(path) else path


def bare(url: str) -> str:
    return re.sub(r"^[a-z]+://", "", str(url))


def peek(content) -> tuple:
    """What came back, as its first lines, each cut short, and how many
    lines more there are."""
    text = content if isinstance(content, str) else "\n".join(
        x.get("text", "") for x in content or [] if isinstance(x, dict) and x.get("type") == "text")
    lines = text.rstrip().split("\n") if text.strip() else []
    return [line[:160] for line in lines[:PEEK]], max(0, len(lines) - PEEK)


def summary(name: str, got: dict) -> tuple:
    """One tool call as one line: its kind, and what it did."""
    if name == "Bash":
        return "command", str(got.get("description") or (str(got.get("command", "")).splitlines() or [""])[0])
    if name == "Read":
        start, many = got.get("offset"), got.get("limit")
        first = int(start or 1) if str(start or 1).isdigit() else 1
        span = (f" · lines {first}–{first + int(many) - 1}" if str(many or "").isdigit()
                else f" · from line {first}" if start else "")
        return "read", f"Read {shown(got.get('file_path', ''))}{span}"
    if name in ("Grep", "Glob"):
        where = f" in {shown(got['path'])}" if got.get("path") else ""
        return "search", f"Searched “{got.get('pattern', '')}”{where}"
    if name == "WebSearch":
        return "search", f"Searched “{got.get('query', '')}”"
    if name == "WebFetch":
        return "fetch", f"Fetched {bare(got.get('url', ''))}"
    if name == "ToolSearch":
        asked = str(got.get("query", ""))
        return "load", (f"Loaded {', '.join(asked[7:].split(','))}" if asked.startswith("select:")
                        else f"Looked for tools: {asked}")
    if name in ("Agent", "Task"):
        return "agent", str(got.get("description") or "An agent")
    if name.startswith(BROWSER):
        step = name[len(BROWSER):]
        try:
            return "browser", STEPS[step].format(**{**got, "url": bare(got.get("url", ""))})
        except (KeyError, IndexError, ValueError):
            return "browser", f"Browser: {step.replace('_', ' ')}"
    return "other", str(got.get("description") or name)


def changed(name: str, got: dict) -> tuple:
    """The file one call writes, as (verb, path, lines added, lines removed)."""
    lines = lambda s: str(s).count("\n") + 1 if s else 0
    path = got.get("file_path") or got.get("notebook_path") or ""
    if name == "Write":
        return "wrote", path, lines(got.get("content")), 0
    if name == "MultiEdit":
        edits = [e for e in got.get("edits") or [] if isinstance(e, dict)]
        return ("edited", path, sum(lines(e.get("new_string")) for e in edits),
                sum(lines(e.get("old_string")) for e in edits))
    if name == "NotebookEdit":
        return "edited", path, lines(got.get("new_source")), 0
    return "edited", path, lines(got.get("new_string")), lines(got.get("old_string"))


def went_in(name: str, got: dict) -> str:
    """What one call was handed, as I would read it."""
    if name == "Bash":
        return str(got.get("command", ""))
    if name == "Read":
        return str(got.get("file_path", ""))
    if name in ("WebSearch", "ToolSearch"):
        return str(got.get("query", ""))
    if name == "WebFetch":
        return f"{got.get('url', '')}\n\n{got.get('prompt', '')}".strip()
    if name in ("Agent", "Task"):
        return str(got.get("prompt", ""))
    for k in ("code", "function", "url"):
        if name.startswith(BROWSER) and isinstance(got.get(k), str):
            return got[k]
    return json.dumps(got, ensure_ascii=False)


def images(d: dict) -> list:
    """Every picture one record carries, in order: mine, or one a call brought back."""
    content = (d.get("message") or {}).get("content")
    out = []
    for b in content if isinstance(content, list) else []:
        if not isinstance(b, dict):
            continue
        inner = b.get("content") if b.get("type") == "tool_result" else [b]
        out += [x["source"] for x in inner if isinstance(inner, list) and isinstance(x, dict)
                and x.get("type") == "image" and isinstance(x.get("source"), dict)]
    return out


def dimensions(source: dict) -> tuple:
    """A picture's width and height, read from its first bytes, or (0, 0)."""
    try:
        head = base64.b64decode(str(source.get("data", ""))[:87384])
    except ValueError:
        return 0, 0
    if head[:8] == b"\x89PNG\r\n\x1a\n" and len(head) >= 24:
        return struct.unpack(">II", head[16:24])
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", head[6:10])
    i = 2 if head[:2] == b"\xff\xd8" else len(head)
    while i + 9 < len(head):
        if head[i] != 0xFF:
            i += 1
            continue
        mark = head[i + 1]
        if mark in (0xD8, 0x01, 0xFF) or 0xD0 <= mark <= 0xD7:
            i += 1 if mark == 0xFF else 2
            continue
        if 0xC0 <= mark <= 0xCF and mark not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", head[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", head[i + 2:i + 4])[0]
    return 0, 0


class Thread:
    """One transcript, read as the transcript page draws it.

    `turns` holds every turn in order. Mine carry my words and my pictures,
    and `mid` on a line it read mid-turn, which starts no turn of its own.
    The session's carry its steps in order: its text, each skill it ran,
    each file it wrote, and each other tool call, with where its call and
    its answer sit in the file, so a detail is read only when opened. A
    wake marks where something other than me started its next turn, and
    an agent's report read while it worked sits where it arrived. Its
    thinking and the harness's notices are never kept.

    A turn of the session's is numbered only once it holds text, a skill or
    a file, as turns() counts one, so the page and the copy number alike.
    One carrying on past lines of mine the copy never counts, a ! line, one
    of Claude Code's own commands or a prompt I took back, is the same turn
    there, `cont`, and keeps its number: numbered().
    `queue` holds what was typed while it worked, until it reads it.
    `tasks` holds each call sent to the background, by its task's id.
    """

    def __init__(self):
        self.turns, self.calls, self.queue, self.tasks = [], {}, [], {}
        # My newest prompt nothing has answered yet, and its record's parent.
        self.waits = None

    def hidden(self, turn: dict, idle: bool) -> bool:
        """A prompt of mine the pane no longer shows: one I took back, or my
        last, unanswered while the session runs idle. Its place stays, so
        every turn after it keeps its index."""
        return bool(turn.get("back")) or (idle and self.waits is not None and turn is self.waits[0])

    def numbered(self, idle: bool) -> list:
        """Each turn shown, as (index, turn, its number), 0 for one the copy
        never counts. A turn carrying on keeps its first part's number."""
        out, n, last = [], 0, 0
        for i, t in enumerate(self.turns):
            if self.hidden(t, idle):
                continue
            if t.get("cont") and last:
                shown = last
            else:
                n += 1 if t["counted"] else 0
                shown = n if t["counted"] else 0
            if t["who"] == "session":
                last = shown
            out.append((i, t, shown))
        return out

    def carried(self) -> bool:
        """Whether the session's next turn carries on its last: every turn of
        mine since is one the copy never counts."""
        for t in reversed(self.turns):
            if t["who"] == "session":
                return True
            if t["counted"] and not t.get("back"):
                return False
        return False

    def take(self, d: dict, at: int) -> None:
        if self.waits and (got := settles(d, self.waits[1])):
            self.waits[0]["back"] = got == "back"
            self.waits = None
        kind = d.get("type")
        if kind == "queue-operation":
            self.queued(d.get("operation"), d.get("content"))
            self.notice(d.get("content"))
            return
        if kind == "attachment":
            got = d.get("attachment") or {}
            self.notice(got.get("prompt"))
            # An agent's report, read while the session worked.
            if (got.get("origin") or {}).get("kind") == "peer":
                self.woke(d, at, got.get("prompt"), got["origin"], "arrived")
        if kind == "system" and d.get("subtype") == "local_command":
            self.ran(d)
            return
        if kind == "user" and self.shell(d):
            return
        said = mine(d) if kind in ("user", "attachment") else ""
        if said:
            sender = REPORT.match(said)
            pics = [(at, k, *dimensions(s)) for k, s in enumerate(images(d))]
            self.turns.append({"who": "you", "at": clock(d), "text": said, "pics": pics,
                               "from": sender.group(1) if sender else "", "counted": True,
                               "mid": kind == "attachment"})
            if kind == "user" and d.get("uuid"):
                self.waits = (self.turns[-1], d.get("parentUuid"))
            return
        if kind == "user":
            content = (d.get("message") or {}).get("content")
            self.notice(content)
            if d.get("turnOrigin") in WAKES:
                self.woke(d, at, content, d.get("origin") or {})
            for b in content if isinstance(content, list) else []:
                step = self.calls.get(b.get("tool_use_id")) if isinstance(b, dict) else None
                if step is not None:
                    step.update(out=at, err=bool(b.get("is_error")), pics=len(images(
                        {"message": {"content": [b]}})))
                    if step.get("tool") in LOUD:
                        sent = d.get("toolUseResult") if isinstance(d.get("toolUseResult"), dict) else {}
                        step.update(peek=peek(b.get("content")),
                                    bg=bool(sent.get("isAsync") or sent.get("backgroundTaskId")))
                        task = sent.get("agentId") or sent.get("backgroundTaskId")
                        if task:
                            self.tasks[str(task)] = step
                    elif step.get("tool") == "browser" and (moved := MOVED.search(str(b.get("content")))):
                        step.update(bg=True)
                        self.tasks[moved.group(1)] = step
                    if step.get("bg"):
                        step.update(began=moment(d))
                    self.last(d)
            return
        if kind != "assistant":
            return
        for b in (d.get("message") or {}).get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and b.get("text", "").strip():
                self.add(d, {"k": "text", "t": b["text"].strip()}, True)
            elif b.get("type") == "tool_use":
                name, got, uid = b.get("name", ""), b.get("input") or {}, b.get("id", "")
                # A task stopped by hand sends no notice. Its stop ends it.
                stopped = self.tasks.get(str(got.get("task_id") or got.get("shell_id") or ""))
                if name in STOPS and stopped is not None and not stopped["done"]:
                    stopped["done"] = "killed"
                if name == "Skill":
                    step = {"k": "skill", "name": str(got.get("skill", "")), "args": str(got.get("args", ""))}
                elif name in WRITERS:
                    verb, path, add, cut = changed(name, got)
                    step = {"k": "file", "verb": verb, "path": shown(path), "add": add, "del": cut}
                else:
                    tool, say = summary(name, got)
                    step = {"k": "call", "tool": tool, "say": say,
                            "server": name == "Bash" and bool(SERVER.search(str(got.get("command", ""))))}
                step.update(id=uid, use=at, out=-1, err=False, pics=0, peek=None, bg=False, done="")
                self.calls[uid] = step
                self.add(d, step, step["k"] != "call")

    def ran(self, d: dict) -> None:
        """One of Claude Code's own commands, as /context: a turn of mine,
        then what it answered beneath it, its colours stripped. Never
        counted, as the copy never counts it."""
        text = str(d.get("content") or "")
        typed = TYPED.search(text)
        if typed:
            args = re.search(r"<command-args>(.*?)</command-args>", text, re.S)
            self.turns.append({"who": "you", "at": clock(d), "pics": [], "from": "", "counted": False, "out": "",
                               "text": f"{typed.group(1)} {(args.group(1) if args else '').strip()}".strip()})
        elif (out := OUT.search(text)) and self.turns and self.turns[-1]["who"] == "you":
            said = ANSI.sub("", out.group(1)).strip()
            self.turns[-1]["out"] = f"{self.turns[-1].get('out', '')}\n{said}".strip()

    def shell(self, d: dict) -> bool:
        """A line I typed after !, as ! kill 75163: a turn of mine, then what
        the shell printed beneath it. Never counted, as the copy never counts
        it."""
        text = texts(d.get("message") or {}).strip()
        if typed := BASH_IN.fullmatch(text):
            self.turns.append({"who": "you", "at": clock(d), "pics": [], "from": "", "counted": False, "out": "",
                               "text": f"! {typed.group(1).strip()}", "shell": True})
            return True
        if not text.startswith("<bash-std"):
            return False
        said = "\n".join(s for s in (ANSI.sub("", m).strip() for m in BASH_OUT.findall(text)) if s)
        if said and self.turns and self.turns[-1]["who"] == "you":
            self.turns[-1]["out"] = f"{self.turns[-1].get('out', '')}\n{said}".strip()
        return True

    def add(self, d: dict, step: dict, counted: bool) -> None:
        if not self.turns or self.turns[-1]["who"] != "session":
            self.turns.append({"who": "session", "at": clock(d), "start": moment(d), "end": moment(d),
                               "steps": [], "counted": False, "cont": self.carried()})
        turn = self.turns[-1]
        turn["steps"].append(step)
        turn["counted"] = turn["counted"] or counted
        self.last(d)

    def last(self, d: dict) -> None:
        """The session's turn ran at least until this record."""
        if self.turns and self.turns[-1]["who"] == "session" and moment(d):
            self.turns[-1]["end"] = moment(d)

    def queued(self, op, content) -> None:
        """One move of what waits typed, as Claude Code logs it: added, read
        at the turn's end, read mid-turn, or taken back to edit."""
        if op == "enqueue":
            self.queue.append(content if isinstance(content, str) else "")
        elif op == "dequeue":
            self.queue[:1] = []
        elif op == "remove":
            i = self.queue.index(content) if content in self.queue else 0
            self.queue[i:i + 1] = []
        elif op == "popAll":
            self.queue = []

    def notice(self, text) -> None:
        """A task's notice: the background call it names has ended, how,
        and, for an agent, after how many steps and how long."""
        if not isinstance(text, str) or not text.lstrip().startswith(NOTICE[0]):
            return
        found, task = TOLD.search(text), TASK.search(text)
        step = self.calls.get(found.group(1)) if found else self.tasks.get(task.group(1)) if task else None
        if step is None or INTERIM in text:
            return
        how, used, took = ENDED.search(text), USED.search(text), TOOK.search(text)
        step.update(done=how.group(1) if how else "completed", used=int(used.group(1)) if used else 0,
                    took=int(took.group(1)) / 1000 if took else 0)

    def woke(self, d: dict, at: int, content, origin: dict, k: str = "wake") -> None:
        """Something other than me started the session's next turn: an
        agent's report, or a task's notice. The turn keeps a wake there,
        with the call it answers and whether it brought words to read. A
        report read while the session worked arrives the same way, its `k`
        "arrived", and starts nothing. An agent that reported is done,
        before its notice says so."""
        text = content if isinstance(content, str) else ""
        if origin.get("kind") == "peer":
            call = self.tasks.get(str(origin.get("senderTaskId") or origin.get("from") or ""))
            how, has = ("report" if origin.get("handback") else "message"), bool(origin.get("body"))
            if call is not None and how == "report" and not call["done"]:
                call["done"] = "completed"
        else:
            told, task, result = TOLD.search(text), TASK.search(text), RESULT.search(text)
            call = self.calls.get(told.group(1)) if told else self.tasks.get(task.group(1)) if task else None
            words = result.group(1) if result else ""
            has = bool(words.strip()) and POINTED not in words and INTERIM not in words
            how = "waiting" if INTERIM in words else "report" if has else "ended"
        step = {"k": k, "id": f"w{at}", "how": how, "call": call, "has": has,
                "name": str(origin.get("name") or ""), "use": at, "at": clock(d)}
        self.calls[step["id"]] = step
        self.add(d, step, False)

    def running(self, since) -> list:
        """Every call sent to the background since `since` and not ended: an
        agent, a command, a browser script, a wait. A server never counts.
        `since` is its process's start, so a restart's dead tasks drop out."""
        return [s for s in self.calls.values()
                if s["k"] == "call" and s["bg"] and not s["done"] and not s.get("server")
                and s.get("began") and s["began"] >= since]

    def waiting(self) -> list:
        """My lines typed while it worked, that it has not read yet."""
        said = [mine({"type": "user", "message": {"content": q}}) for q in self.queue if q]
        return [s for s in said if s and not s.startswith(NOTICE)]


# Each transcript read so far, by path: how far into it, and what it held;
# and when each was last used. A big transcript's thread takes a few
# megabytes, so one not used in ten minutes is forgotten, its tail with
# it: a stopped session's, or a page long closed.
THREADS: dict = {}
LAST_USED: dict = {}
FORGOTTEN = 10 * 60
# One reader at a time. Two reading one transcript at once, a draw and the
# buzz, would each take the same new lines, and its thread would hold every
# turn twice from then on.
READING = threading.Lock()
# Claude Code's api-request records, and their -blob and -shape kin: most of
# a transcript's bytes, and nothing here reads one, so none is decoded.
UNREAD = b'{"type":"api-request'


def thread(path: str) -> Thread:
    """A transcript's whole thread. Read again, only what was written since
    the last read is read. One not used in ten minutes is forgotten here."""
    with READING:
        now = time.time()
        for old in [p for p, at in LAST_USED.items() if now - at > FORGOTTEN and p != path]:
            LAST_USED.pop(old, None)
            THREADS.pop(old, None)
            registry.TAILS.pop(old, None)
        LAST_USED[path] = now
        try:
            size = os.path.getsize(path)
        except OSError:
            return Thread()
        at, got = THREADS.get(path, (0, None))
        if got is None or size < at:
            at, got = 0, Thread()
        # Line by line, so a big transcript never sits in memory whole. A
        # line half written waits for the next read. One that raises is
        # logged and passed, never taken again.
        with open(path, "rb") as f:
            f.seek(at)
            for line in f:
                if not line.endswith(b"\n"):
                    break
                if not line.startswith(UNREAD):
                    try:
                        d = json.loads(line)
                    except ValueError:
                        d = None
                    if isinstance(d, dict):
                        try:
                            got.take(d, at)
                        except Exception:
                            traceback.print_exc()
                at += len(line)
        THREADS[path] = (at, got)
        return got


def record(path: str, at: int) -> dict:
    """The record starting `at` bytes into a transcript."""
    try:
        with open(path, "rb") as f:
            f.seek(at)
            d = json.loads(f.readline())
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def call_of(path: str, step: dict) -> tuple:
    """A call's whole: (its tool's name, what it was handed, what came back).
    What came back is None while it runs."""
    use = next((b for b in (record(path, step["use"]).get("message") or {}).get("content") or []
                if isinstance(b, dict) and b.get("id") == step["id"]), {})
    back = None
    if step["out"] >= 0:
        for b in (record(path, step["out"]).get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("tool_use_id") == step["id"]:
                content = b.get("content")
                back = content if isinstance(content, str) else "\n".join(
                    x.get("text", "") for x in content or [] if isinstance(x, dict) and x.get("type") == "text")
    return use.get("name", ""), use.get("input") or {}, back


def brought(path: str, step: dict) -> str:
    """The words a wake brought: an agent's report, out of the harness's
    frame, or the result a task's notice carries. "" when it brought none."""
    d = record(path, step["use"])
    body = str((d.get("origin") or (d.get("attachment") or {}).get("origin") or {}).get("body") or "")
    if body:
        _, frame, report = body.partition(FOLLOWS)
        return textwrap.dedent(report).strip() if frame else body.strip()
    found = RESULT.search(texts(d.get("message") or {}))
    return found.group(1).strip() if found else ""
