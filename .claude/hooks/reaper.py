#!/usr/bin/env python3
"""reaper.py — the hook behind /reaper.

    /reaper 03              end session 03
    /reaper 03 04 05        end all three

A pane is one way to reach a session. The pid is the other, and it
outlives the pane. This takes the pid, so a closed pane changes nothing.
A pane still up closes once its session has gone, five seconds at most.

Ending a session deletes its folder whole, record and work, the prototype
subject it held too. A winner it built goes whole, unless another session
still builds it, through prototypes.built. Nothing is kept. A folder with
no record is a session already ended, and it goes the same way.

It never reads this session's own pane. /9-session-stop owns that.
It carries no digit, because it runs rarely.
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import iterm  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

TRIGGER = "/reaper"
WAIT = 5  # seconds every session has to exit before its pane closes anyway


def end(number: str, record: dict) -> tuple:
    """Stop one number's ports, then its session, then delete its folder.

    Returns the pid signalled, or 0, and the winners it removed. Its pane
    closes later, in close().
    """
    ports.stop(ports.held(number))
    pid = registry.pid_of(record)
    if pid:
        ports.end(pid)
    winners = prototypes.built(number)
    registry.remove(number)
    serve.forget(number)
    return pid, winners


def close(pids: list, shut: list) -> None:
    """Once every session has exited, close the panes still up.

    Waiting first lets Claude Code exit on its own. A slow one is closed
    anyway. The close goes through iTerm's API, so nothing is typed.
    """
    ports.gone(pids, WAIT)
    for pane in shut:
        iterm.close(pane)


def main() -> None:
    args = hook.words(TRIGGER)
    mine = registry.number_of(args.event.get("session_id") or "")
    if not args:
        hook.done("Name the sessions to end. `/reaper 03 04`.")

    numbers = []
    for word in args:
        if not word.isdigit():
            hook.done(f"`{word}` is not a session number.")
        if not 1 <= int(word) <= 99:
            hook.done(f"`{word}` is not a session number. A number is 01 to 99.")
        numbers.append(f"{int(word):02d}")

    # This session is never a target. Signalling my own pid would kill the
    # process this hook is reporting to.
    if mine in numbers:
        hook.done(f"Session {mine} is this one. `/9-session-stop` closes it.")

    held = registry.entries()
    ended = [n for n in numbers
             if n in held or os.path.isdir(registry.folder(n))]
    missing = [n for n in numbers if n not in ended]

    # Each pane is found before its session ends: its terminal goes with it.
    pids, shut, winners = [], [], []
    for number in ended:
        record = held.get(number, {})
        pane = panes.pane(record) if record else ""
        pid, gone = end(number, record)
        pids.append(pid)
        winners += gone
        if pane:
            shut.append(pane)
    close([p for p in pids if p], shut)

    if not ended:
        hook.done(f"No folder for {', '.join(missing)}. Nothing was ended.")

    line = f"{len(ended)} successfully ended: {', '.join(ended)}."
    line += " Its folder was deleted." if len(ended) == 1 else \
        " Their folders were deleted."
    if winners:
        line += f" Winner {', '.join(winners)} removed."
    if missing:
        line += f" No folder for {', '.join(missing)}."
    hook.done(line)


if __name__ == "__main__":
    main()
