#!/usr/bin/env python3
"""9-session-stop.py — the hook behind /9-session-stop.

All of the stop's work is here. My bare typed command checks first: this
hook lets it pass, and the skill's body asks whether anything I asked for
still holds it. Nothing does → the session
calls the skill itself. That call, and `now`, are answered here before the body loads, so
they cost no model turn and no tokens. The call also ends the session's
turn, so it writes nothing after.

    /9-session-stop         the session checks, then stops itself
    /9-session-stop now     stop this session's ports, delete its folder, exit

It stops everything serving this session's own ports, as lib/ports.py's
sweep finds it: what listens, the launchers above it, and a watcher
waiting with no server, which would bring one back on the next edit.
Band 00 and every other session are untouched.

Stopping deletes this session's folder whole, record and work, so nothing
accumulates under a number. The prototype subject it held goes with the
folder. A winner it built goes whole, unless another session still builds
it, through prototypes.built. A clarify wave still open goes too: the
stop's line names it, and each item I left unanswered, so none drops unseen. The stop itself
never asks. Any word after the trigger but `now` is ignored, so a spoken
stop always works.

It takes down every pane the session opened. A browser pane is its own
when it shows one of its ports, or carries its name, NN-browser-K. Those
close first. Its own pane closes last: /exit is typed into it, and once
Claude has gone, iTerm closes it. A pane another session opened is never
touched.

A shell its Bash tool left running in the background, a wait among them,
ends before /exit. Left running, /exit would stop at Claude Code's
question about background work, and the pane would close only at WAIT.

Closing its own pane ends this process, so that waits in a process of
its own, started as `9-session-stop.py after PID PANE NN`. Each stop writes
one line to .claude/state/9-session-stop/closes.log: how long Claude took
to exit, and whether its pane closed or was left open.
"""

import os
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import wake  # noqa: E402

TRIGGER = "/9-session-stop"
WAIT = 60  # seconds Claude has to exit before its pane closes anyway
# One line per stop, on how its pane closed, so a pane left open leaves evidence.
LOG = os.path.join(registry.ROOT, ".claude", "state", "9-session-stop", "closes.log")


def theirs(number: str) -> list:
    """The browser panes this session opened: one of its ports, or its name."""
    out = []
    for b in iterm.browsers():
        port = ports.of(b["url"])
        if (ports.in_scheme(port) and str(ports.plain(port))[2:] == number) \
                or launch.browser_number(number, b.get("name")):
            out.append(b["pane"])
    return out


def shells(pid: int) -> list:
    """Every shell the Bash tool started for Claude process PID, and every
    process under each, deepest first."""
    under = {}
    for p, parent, command in wake.table():
        under.setdefault(parent, []).append((p, command))
    found, todo = [], [p for p, command in under.get(pid, []) if wake.TOOL in command]
    while todo:
        p = todo.pop()
        found.append(p)
        todo += [c for c, _ in under.get(p, [])]
    return found[::-1]


def note(number: str, pane: str, what: str) -> None:
    """One line in the log: when, which session, its pane, and what happened."""
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} · {number or 'no number'} · "
                f"pane {pane[:8] or 'none'} · {what}\n")


def after(pid: int, pane: str, number: str) -> None:
    """Once Claude has exited, close its pane. A slow exit is closed anyway.
    The log gets how long Claude took, and whether the pane is gone."""
    began = time.time()
    exited = ports.gone([pid], WAIT)
    waited = f"Claude exited in {time.time() - began:.0f}s" if exited else f"Claude still ran at {WAIT}s"
    closed = iterm.close(pane)
    left = pane in (panes.ids() or set())
    note(number, pane, f"{waited} · " + ("pane left open" if left
                                         else "pane closed" if closed else "no pane to close"))


def main() -> None:
    if sys.argv[1:2] == ["after"]:
        after(int(sys.argv[2]), sys.argv[3], sys.argv[4])
        return

    args = hook.words(TRIGGER)
    if hook.answering == "UserPromptSubmit" and args.first() != "now":
        sys.exit(0)

    held = registry.entries()
    session_id = args.event.get("session_id") or ""
    number = registry.number_of(session_id, held)
    pid = int((registry.claude_records().get(session_id) or {}).get("pid") or 0)

    # The Playwright server starts before any number is claimed, so it
    # writes under the session id. A claim points that path into the
    # session's folder, which goes below. The pointer goes here, and so
    # does the whole folder of a session that never claimed a number.
    if session_id:
        shots = os.path.join(registry.ROOT, ".claude", "state",
                             "playwright-mcp", session_id)
        if os.path.islink(shots):
            os.unlink(shots)
        else:
            shutil.rmtree(shots, ignore_errors=True)

    kept = len(registry.files(number)) if number else 0
    try:
        wave, head, left = page.tool("clarify-page").open_wave(number) if number else (0, {}, [])
    except Exception:  # a wave that will not read never holds the stop
        wave, head, left = 0, {}, []

    stopped = ports.sweep(number) if number else []
    winners = prototypes.built(number) if number else []
    if number:
        registry.remove(number)
        serve.forget(number)
        for pane in theirs(number):
            iterm.close(pane)

    for p in shells(pid) if pid else []:
        if p in (os.getpid(), os.getppid()):
            continue
        try:
            os.kill(p, signal.SIGTERM)
        except OSError:
            pass

    me = panes.me()
    # Only a line that exits says "successfully". A pane not found is no
    # stop: nothing types /exit, so the line asks for it.
    gone = f" {kept} dropped." if kept else ""
    if winners:
        gone += f" Winner {', '.join(winners)} removed."
    if wave:
        gone += (f" Wave {wave} dropped, sent and never folded." if head.get("sent")
                 else f" Wave {wave} dropped unsent" + (f", unanswered: {'; '.join(left)}." if left else "."))
    if not me:
        line = (f"Session {number} stopped its ports." if number
                else "This session holds no number.") + \
            " Its pane was not found, so Claude still runs: type /exit in it."
    elif stopped:
        line = (f"Session {number} successfully stopped: "
                f"{', '.join(stopped)}.{gone} Exiting.")
    elif number:
        line = f"Session {number} successfully stopped. No port was running.{gone} Exiting."
    else:
        line = "This session successfully stopped. It held no number. Exiting."

    panes.say(me, "/exit", 2)
    if pid and me:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "after", str(pid), me,
                          number or ""],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    else:
        note(number, me, "pane left open: " + ("no pane id" if not me else "no Claude pid found"))
    hook.done(line, end=True)


if __name__ == "__main__":
    main()
