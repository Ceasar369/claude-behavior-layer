#!/usr/bin/env python3
"""trial.py — what a test of 1100 stands on: a made-up sessions folder, and the one way it opens a browser.

A test never reads or writes a real session's folder, never asks iTerm,
and starts no program. world() stands a temporary folder in
registry.WORK's place for as long as its block runs, with four sessions
that between them hold every kind of page: 05 waits on me with a wave,
launch rows, an explanation, a jury's plan, a walk and a context past the
handover threshold; 10 leads a plan of three missions; 11 works one;
12, gone with its transcript, held another. Each one's
transcript holds every kind of line lib/transcripts.py reads. What a draw
reads outside the folder is stood in for: Claude Code's records, iTerm's
panes and layout, the process table, the models, the account order. A
program a draw starts all the same is refused, and kept in `started`.
clock() moves the time on, by LATER or any other step, so a draw that
leans on the clock shows.

A test of a page's script runs it in WebKit, my pane's engine, and in
Chromium, the Claude app's and Chrome's. browsers() runs one Node script
with the Playwright .mcp.json pins, fetched by npx, so no test names a
version of its own. The script opens with PRELUDE: `webkit`, `chromium`,
`engines`, each one whose build is installed, and `wait(ms)`. An engine
with no build is said on its own line, "webkit missing", never passed over
in silence: `npx -p <the pin> playwright install webkit` fetches it.

A test that kills its server mid-word runs it through kept_up(), which
starts it again each time it dies. The server dies through die(), and a
browser script reaches it with SERVER's post, die and up.

Imported, never run.
"""

import base64
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from unittest import mock

import accounts
import context
import iterm
import models
import page
import panes
import ports
import push
import registry
import transcripts

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# One white pixel, as a walk's screenshot or a picture in a prompt.
PIXEL = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
# The one model the made-up world knows, 200,000 tokens wide.
MODEL = "claude-opus-5-5"
CATALOG = {"models": [{"id": MODEL, "family": "opus", "name": "Opus 5.5", "window": 200000}],
           "latest": {"opus": MODEL}}


class Started(RuntimeError):
    """A program started inside a made-up folder."""


def spoken(sid: str, title: str, working: bool = False) -> list:
    """One transcript's lines, holding every kind lib/transcripts.py reads:
    my prompt, the session's notes and calls of each kind with what came
    back, a command and an agent sent to the background and their notices,
    a line of mine read mid-turn, a slash command, one of Claude Code's
    own, a shell line, a picture, a report, a compaction, and a move.
    `working`, a prompt of mine follows its last turn, still unanswered."""
    lines = [{"type": "custom-title", "customTitle": title, "sessionId": sid}]

    def say(kind: str, **more) -> str:
        n = len(lines)
        lines.append({"type": kind, "sessionId": sid, "timestamp": f"2026-11-01T09:{n // 60:02d}:{n % 60:02d}.000Z",
                      "uuid": f"u{n}", "parentUuid": f"u{n - 1}" if n > 1 else None, **more})
        return f"u{n}"

    def mine(content, **more) -> str:
        return say("user", message={"role": "user", "content": content}, **more)

    def its(*blocks, **more) -> str:
        return say("assistant", message={"role": "assistant", "model": MODEL, "content": list(blocks),
                                         "usage": {"input_tokens": 150000, "cache_creation_input_tokens": 0,
                                                   "cache_read_input_tokens": 0}}, **more)

    def call(tool: str, uid: str, given: dict, back, result: dict) -> None:
        asked = its({"type": "tool_use", "id": uid, "name": tool, "input": given})
        mine([{"type": "tool_result", "tool_use_id": uid, "content": back}], sourceToolAssistantUUID=asked,
             toolUseResult=result)

    mine("Build the trial.", origin={"kind": "human"})
    say("attachment", attachment={"type": "output_style"})
    its({"type": "thinking", "thinking": "A thought.", "signature": "x"})
    its({"type": "text", "text": "Starting."})
    call("Bash", "t1", {"command": "ls", "description": "List files"}, "a\nb",
         {"stdout": "a\nb", "stderr": "", "interrupted": False})
    call("Read", "t2", {"file_path": "/x/a.py", "offset": 1, "limit": 5}, "1\tx = 1", {})
    call("Write", "t3", {"file_path": os.path.join(ROOT, "notes.md"), "content": "x"}, "Written.", {})
    call("Skill", "t4", {"skill": "clarify-items", "args": ""}, "Launching skill: clarify-items", {})
    mine([{"type": "text", "text": "Base directory for this skill: /x"}], isMeta=True, sourceToolUseID="t4")
    call("Bash", "t5", {"command": "sleep 60", "run_in_background": True, "description": "Wait"}, "",
         {"backgroundTaskId": "b1", "stdout": "", "stderr": "", "interrupted": False})
    call("Agent", "t6", {"description": "Study it", "prompt": "Study it.", "subagent_type": "Explore"}, "",
         {"agentId": "ag1", "isAsync": True, "status": "async_launched"})
    call("Bash", "t7", {"command": "cat picture.png", "description": "Show a picture"},
         [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": PIXEL}}], {})
    lines.append({"type": "queue-operation", "operation": "enqueue", "sessionId": sid,
                  "timestamp": "2026-11-01T09:30:00.000Z", "content": "Also check the docs."})
    say("attachment", attachment={"type": "queued_command", "prompt": "Also check the docs.",
                                  "origin": {"kind": "human"}})
    its({"type": "text", "text": "Done.\n\n**Your move.** Ruling: pick a port."})
    say("system", subtype="turn_duration", durationMs=5000, isMeta=False)
    mine("<task-notification>\n<task-id>b1</task-id>\n<tool-use-id>t5</tool-use-id>\n<status>completed</status>\n"
         "<summary>Wait ended</summary>\n<result>slept</result>\n<tool_uses>7</tool_uses>\n"
         "<duration_ms>42000</duration_ms>\n</task-notification>",
         origin={"kind": "task-notification"}, turnOrigin="task_notification")
    mine('<agent-message from="ag1">It holds.</agent-message>', turnOrigin="peer",
         origin={"kind": "peer", "from": "ag1", "senderTaskId": "ag1", "name": "Study it", "handback": True,
                 "body": "Agent handed back.\nThe report follows:\n  It holds."})
    its({"type": "text", "text": "Both ended."})
    say("system", subtype="turn_duration", durationMs=900, isMeta=False)
    mine("<command-message>clarify-items</command-message>\n<command-name>/clarify-items</command-name>\n"
         "<command-args>now</command-args>")
    say("system", subtype="local_command", level="info", isMeta=False,
        content="<command-name>/context</command-name>\n<command-message>context</command-message>\n"
                "<command-args></command-args>")
    say("system", subtype="local_command", content="<local-command-stdout>Context 40%</local-command-stdout>")
    mine("<bash-input>pwd</bash-input>")
    mine("<bash-stdout>/tmp</bash-stdout><bash-stderr></bash-stderr>")
    mine([{"type": "text", "text": "See this."},
          {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": PIXEL}}],
         origin={"kind": "human"})
    mine("Session 03 reports: done.", origin={"kind": "human"})
    say("system", subtype="compact_boundary", compactMetadata={"postTokens": 40000})
    mine("A summary of what came before.", isCompactSummary=True)
    its({"type": "text", "text": "All read.\n\n**Your move.** Ruling: keep the port."})
    say("system", subtype="turn_duration", durationMs=1200, isMeta=False)
    if working:
        mine("Go on.", origin={"kind": "human"})
    return lines


class World:
    """The made-up folder: `work` stands in registry.WORK's place, `held`
    is each session's record, and `started` each program a draw tried to
    start."""

    def __init__(self, root: str):
        self.root, self.work, self.account = root, os.path.join(root, "sessions"), os.path.join(root, "account")
        self.held, self.started = {}, []

    def put(self, nn: str, name: str, text) -> str:
        """One file in session NN's folder, written whole."""
        path = os.path.join(self.work, nn, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb" if isinstance(text, bytes) else "w") as f:
            f.write(text)
        return path

    def session(self, nn: str, name: str, status: str = "idle") -> dict:
        """Session NN, registered and running: its record, its transcript,
        and Claude Code's own record of it, reading `status`. With no
        status it is gone: its record stands, Claude Code holds none, and
        its transcript is gone too."""
        sid, title = f"00000000-0000-4000-8000-0000000000{nn}", f"{nn}-{name}"
        heard = os.path.join(self.root, "transcripts", f"{sid}.jsonl")
        os.makedirs(os.path.dirname(heard), exist_ok=True)
        with open(heard, "w") as f:
            f.write("".join(json.dumps(line) + "\n" for line in spoken(sid, title, status == "busy")))
        self.held[nn] = {"number": nn, "title": title, "session_id": sid, "pid": 40000 + int(nn),
                         "pane": f"{nn}000000-0000-0000-0000-000000000000", "cwd": ROOT, "account": "1",
                         "transcript": heard, "claimed": "2026-11-01T09:00:00"}
        self.put(nn, registry.RECORD, json.dumps(self.held[nn], indent=2) + "\n")
        if not status:
            os.remove(heard)
            return self.held[nn]
        os.makedirs(os.path.join(self.account, "sessions"), exist_ok=True)
        with open(os.path.join(self.account, "sessions", f"{40000 + int(nn)}.json"), "w") as f:
            json.dump({"pid": 40000 + int(nn), "sessionId": sid, "cwd": ROOT, "startedAt": 1793523600000,
                       "status": status, "name": title, "updatedAt": 1793523600000,
                       "statusUpdatedAt": 1793523600000}, f)
        return self.held[nn]

    def layout(self) -> list:
        """iTerm's layout, as lib/iterm.py's tree() answers: one window,
        one tab, each session's pane side by side."""
        leaves = [{"pane": r["pane"], "name": r["title"], "w": 600, "h": 600} for r in self.held.values()]
        root = leaves[0] if len(leaves) == 1 else {"split": "columns", "children": leaves}
        return [{"window": "w1", "tabs": [{"tab": "t1", "root": root}]}]


def filled(w: World) -> None:
    """The four sessions, and every kind of page between them."""
    w.session("05", "trial")
    w.session("10", "trial-team")
    w.session("11", "trial-work", "busy")
    w.session("12", "gone-work", "")
    clarify = page.tool("clarify-page")
    w.put("05", "waves/wave-1.md", clarify.dump(1, {"sent": "", "then": ""}, [
        {"n": "1", "title": "Port", "question": "Which port?", "decision": "1100.", "why": "It is the one page server.",
         "show": "```mermaid\nflowchart TB\n  a[\"Ask\"]:::you --> b[\"Answer\"]:::session\n```\nFigure: one ask, one answer"},
        {"n": "2", "title": "Name", "question": "Which name?", "decision": "trial.", "agree": "yes"}]))
    w.put("05", "launch.json", json.dumps({"rows": [
        {"uid": 1, "n": "07", "name": "trial", "message": "Hello.", "account": "1", "model": MODEL, "effort": "high"},
        {"uid": 2, "kind": "browser", "site": "1100"}]}, indent=2) + "\n")
    w.put("05", "explanations/trial.md", "# A trial document\nFor a test, from made-up state.\n\n"
                                         "## One section\nA paragraph.\n")
    w.put("05", "walk-list.md", "# A trial walk\n\n- app/trial · Sign up\n")
    w.put("05", "walk/app/trial/sign-up/1.png", base64.b64decode(PIXEL))
    w.put("05", "named.json", json.dumps({"model": "opus", "effort": "high"}))
    with contextlib.redirect_stdout(io.StringIO()):
        page.tool("jury").draft("05", {"shape": "one pick", "question": "Does it hold?", "from": {"label": "Trial"},
                                       "context": ["Made up."], "claims": [{"text": "Port is 1100.", "source": ""}]})
    w.put("10", "stages.json", json.dumps({"stages": [{"name": "Stage A", "missions": [
        {"id": "A1", "name": "trial work", "session": "11", "title": "11-trial-work", "queued": "2026-11-01T08:59:00"},
        {"id": "A2", "name": "later work"},
        {"id": "A3", "name": "gone work", "session": "12", "title": "12-gone-work",
         "queued": "2026-11-01T08:58:00"}]}]}, indent=2) + "\n")
    w.put("10", "answers/A1.md", "# Holds\n\nIt holds.\n")


def forget() -> None:
    """Every answer a library keeps from one read to the next, dropped, so
    a made-up folder and the real one never read each other's."""
    registry.PUBLISHED[:] = [0.0, None]
    panes.LAST[:] = [0.0, None]
    panes.TTYS[:] = [0.0, {}]
    for kept in (registry.TAILS, transcripts.THREADS, transcripts.LAST_USED, context.KEPT, models.KEPT):
        kept.clear()


@contextlib.contextmanager
def world():
    """The made-up folder, standing for as long as the block runs, with
    every read outside it stood in for: the World it yields."""
    root = tempfile.mkdtemp(prefix="trial-")
    w = World(root)

    def refuse(argv, *given, **named):
        w.started.append(argv if isinstance(argv, str) else " ".join(map(str, argv)))
        raise Started(f"A draw started a program in a made-up folder: {w.started[-1][:120]}")

    stood = [(registry, "WORK", w.work), (registry, "LIVE", [w.account]),
             (ports, "started", lambda pids, fresh=False: {int(p): "" for p in pids}),
             (ports, "alive", lambda pid: False), (ports, "table", lambda environment=False: {}),
             (panes, "ids", lambda within=0: {r["pane"] for r in w.held.values()}),
             (panes, "pane", lambda record, pid=None, within=0: record.get("pane", "")),
             (panes, "numbers", lambda within=0: {r["pane"]: nn for nn, r in w.held.items()}),
             (panes, "terminals", lambda within=0: {r["pane"]: f"/dev/ttys0{nn}" for nn, r in w.held.items()}),
             (panes, "tty_of", lambda pid: ""),
             (iterm, "tree", w.layout), (iterm, "screen", lambda pane: []),
             (context, "FILE", os.path.join(root, "threshold.json")),
             (models, "catalog", lambda: CATALOG),
             (accounts, "read", lambda: {"order": [], "next": 0}), (accounts, "take", lambda: accounts.FALLBACK),
             (accounts, "model", lambda: MODEL), (accounts, "effort", lambda: "high"),
             (accounts, "login", lambda account: {}), (accounts, "shared", lambda: None),
             (push, "public", lambda: ""), (subprocess, "Popen", refuse)]
    with contextlib.ExitStack() as stack:
        for module, name, stand_in in stood:
            stack.enter_context(mock.patch.object(module, name, stand_in))
        forget()
        try:
            filled(w)
            yield w
        finally:
            forget()
            shutil.rmtree(root, ignore_errors=True)


# 400 days, an hour, a minute and a second: on from any moment, the year,
# the date, the weekday, the hour, the minute and the second all read
# differently, so a draw leaning on any of them shows at any time of day.
LATER = 400 * 86400 + 3661


@contextlib.contextmanager
def clock(seconds: float = LATER):
    """The time moved `seconds` on, for as long as the block runs: every
    read of the clock through `time` answers that much later."""
    now, local, said = time.time, time.localtime, time.strftime
    with mock.patch.object(time, "time", lambda: now() + seconds), \
            mock.patch.object(time, "localtime", lambda at=None: local(now() + seconds if at is None else at)), \
            mock.patch.object(time, "strftime", lambda form, at=None: said(form, local(now() + seconds)
                                                                              if at is None else at)):
        yield

PRELUDE = r"""
const path = require('path'), fs = require('fs');
const bin = process.env.PATH.split(':').find(p => p.includes('_npx') && p.endsWith(path.join('node_modules', '.bin')));
const {chromium, webkit} = require(path.join(bin, '..', 'playwright'));
const engines = [webkit, chromium].filter(e => fs.existsSync(e.executablePath()) || console.log(e.name() + ' missing'));
const wait = ms => new Promise(r => setTimeout(r, ms));
"""


def browsers(script: str, env: dict | None = None, stdin: str = "") -> subprocess.CompletedProcess:
    """One Node script, run after PRELUDE with the pinned Playwright in
    reach. `env` adds to its environment, and `stdin` is what it reads.
    What it printed and how it ended come back as they are."""
    with open(os.path.join(ROOT, ".mcp.json")) as f:
        pin = re.search(r"@playwright/mcp@[\w.-]+", f.read()).group()
    return subprocess.run(["npx", "-y", "-p", pin, "-c", 'node -e "$TRIAL_SCRIPT"'], input=stdin,
                          capture_output=True, text=True,
                          env={**os.environ, **(env or {}), "TRIAL_SCRIPT": PRELUDE + script})


# What a browser script says to a server kept_up() runs, at TRIAL_BASE:
# post(path, data) sends one press, die(seconds) kills the server for that
# long through its own dying press, /trial/die, and up() waits until it
# answers again.
SERVER = r"""
const base = process.env.TRIAL_BASE;
const post = (path, data) => fetch(base + path, {method: 'POST', redirect: 'manual', body: new URLSearchParams(data)}).catch(() => null);
const die = down => post('/trial/die', {down: String(down)});
async function up() {
  for (let i = 0; i < 300; i++) { try { await fetch(base + '/health'); return; } catch (e) { await wait(100); } }
  throw new Error('the server never came back');
}
"""


def die(folder: str, seconds: str) -> None:
    """This server, dead at once, as if killed: kept_up() starts it again
    `seconds` on. A test's server calls it from its dying press."""
    with open(os.path.join(folder, "down"), "w") as f:
        f.write(seconds)
    os._exit(1)


@contextlib.contextmanager
def kept_up(argv: list, port: int, folder: str):
    """One server, `argv`, run as a program of its own for as long as the
    block runs, its output in FOLDER/server.log. It is started again each
    time it dies, once the seconds die() left in FOLDER/down have passed.
    So a test kills its server mid-word, and has it back. Killed at the end."""
    def spawn() -> subprocess.Popen:
        with open(os.path.join(folder, "server.log"), "ab") as log:
            return subprocess.Popen(argv, stdout=log, stderr=log)

    held, done = [spawn()], threading.Event()

    def keep() -> None:
        while not done.is_set():
            if held[0].poll() is not None:
                try:
                    with open(os.path.join(folder, "down")) as f:
                        down = float(f.read().strip() or 0)
                    os.remove(os.path.join(folder, "down"))
                except (OSError, ValueError):
                    down = 0
                done.wait(down)
                if not done.is_set():
                    held[0] = spawn()
            done.wait(0.05)

    keeper = threading.Thread(target=keep, daemon=True)
    keeper.start()
    for _ in range(100):
        if ports.answering(port):
            break
        time.sleep(0.1)
    try:
        yield
    finally:
        done.set()
        keeper.join(2)
        held[0].kill()
        held[0].wait(5)
