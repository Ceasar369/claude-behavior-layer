#!/usr/bin/env python3
"""0-session-start.py — the hook behind /0-session-start.

Naming the tab is panes.say. Every pane is reached there.

    /0-session-start                 lowest free side number, Claude Code's words
    /0-session-start 07              that number, Claude Code's words
    /0-session-start payments api    lowest free side number, those words
    /0-session-start 07 payments     both mine
    /0-session-start 07 keep         take 07 over: end its session, keep its folder and name

A session that already holds a number and claims another takes its folder
along. A session launched for an assistant's queued mission writes itself
into the plan that queued it. Renamed under the same number, it stays on
that mission.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

TRIGGER = "/0-session-start"


def from_transcript(path: str) -> str:
    # Claude Code names every session itself and writes that name into the
    # transcript as an ai-title record. The last one is the current name.
    title = ""
    try:
        with open(path) as f:
            for line in f:
                if '"ai-title"' not in line:
                    continue
                try:
                    got = json.loads(line).get("aiTitle", "")
                except Exception:
                    continue
                if got:
                    title = got
    except Exception:
        return ""
    return registry.kebab(title)


def end(record: dict) -> bool:
    """End the session holding a number, then close its pane. Its folder stays.

    Only a take-over calls this. Its pane is found first, since its
    terminal goes with the process. The pane closes once the process is
    gone, so nothing is ever typed into a Claude Code still running.
    """
    pid = registry.pid_of(record)
    pane = panes.pane(record, pid)
    ports.end(pid)
    if not ports.gone([pid], 5):
        return False
    if pane:
        iterm.close(pane)
    return True


def carry(old: str, new: str) -> None:
    """Move a session's folder from its old number to its new one.

    A band belongs to its number, so every port the old band holds stops,
    and each server among them is the session's own to start again. Its
    pages need nothing: 1100 draws them from the folder, under the new
    number, with the prototype subject it holds.
    """
    up = ports.held(old)
    ports.stop(up)
    ports.gone(list(up.values()), 5)
    serve.forget(old)
    registry.move(old, new)


def main() -> None:
    args = hook.words(TRIGGER)
    event = args.event

    number = None
    if args and re.fullmatch(r"\d{1,2}", args[0]):
        number = f"{int(args[0]):02d}"
        if number == "00":
            hook.done("00 is band 00, no session's. A number is 01 to 99.")
        args = args[1:]
    keep = number is not None and [w.lower() for w in args] == ["keep"]

    held = registry.entries()
    session_id = event.get("session_id") or ""
    mine = registry.number_of(session_id, held)

    if number is None:
        number = mine or next(iter(launch.free()), None)
        if number is None:
            hook.done("Every number outside an assistant's ten is held. Close a session first.")
    else:
        taken = held.get(number)
        if keep and not taken:
            hook.done(f"No session {number} to take over.")
        if taken and registry.pid_of(taken) \
                and taken.get("session_id") != session_id:
            if not keep:
                hook.done(f"Session {number} is already held by a live session.")
            if not end(taken):
                hook.done(f"Session {number} did not end. Nothing changed.")

    # A name is its own number and one to three words. Nothing else.
    # A take-over keeps the name it takes.
    if keep:
        title = held[number].get("title") or number
    else:
        said = " ".join(args)
        words = registry.kebab(said) if said else from_transcript(
            event.get("transcript_path") or "")
        # A session renamed through /rename gets no ai-title, and every
        # claimed session is, so a bare claim keeps the words it carries.
        if not words and mine:
            words = held[mine].get("title", "").partition("-")[2]
        title = f"{number}-{words}" if words else number

    # Claiming a number is the moment it changes hands, so the folder is
    # emptied here, before the record is written. A session that died
    # without stopping left its work behind, and this keeps it off a
    # stranger. Renaming under the number it already holds keeps its work,
    # and so does a take-over: that work is what it goes on with.
    was = registry.clear(number) if number != mine and not keep else 0
    swept = f" {was} left under it were swept." if was else ""

    # A session changing numbers takes its folder along, and so does a
    # take-over. Its old folder's work moves under the new number, and the
    # old folder goes with its record, so no folder is left without one.
    moved = mine and mine != number
    if moved:
        carry(mine, number)
    along = f" {mine}'s folder moved into it." if moved else ""

    pane = panes.me()
    registry.write({
        "number": number,
        "title": title,
        "session_id": session_id,
        "pid": int(os.environ.get("CLAUDE_PID") or 0),
        "pane": pane,
        "cwd": event.get("cwd") or "",
        "account": registry.account(),
        "transcript": event.get("transcript_path") or "",
        "claimed": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    # A session launched for a queued mission writes itself into the plan
    # that queued it, so the plan holds it once the session stops. One
    # renaming itself under its own number takes its mission's title along.
    plans.claim(number)
    if mine == number and held[mine].get("title") != title:
        plans.renamed(number, held[mine].get("title", ""), title)

    # The Playwright server starts before any number exists, and writes
    # under the session id. That path now points into this folder, so
    # the browser's files live and go with the session. A real folder
    # already there means the browser ran before the claim; it stays.
    # Each claim also sweeps the link of every session no longer running,
    # however it ended: a stop, the reaper, a closed pane, a take-over.
    # Only a claimer that sees itself running trusts the list it sweeps by.
    if session_id:
        browser = os.path.join(registry.ROOT, ".claude", "state", "playwright-mcp")
        shots = os.path.join(registry.folder(number), "playwright")
        link = os.path.join(browser, session_id)
        try:
            live = registry.claude_records(fresh=True)
            if session_id in live:
                for name in os.listdir(browser):
                    if name not in live and os.path.islink(os.path.join(browser, name)):
                        os.unlink(os.path.join(browser, name))
        except OSError:
            pass
        try:
            os.makedirs(shots, exist_ok=True)
            if os.path.islink(link):
                os.unlink(link)
            if not os.path.exists(link):
                os.makedirs(os.path.dirname(link), exist_ok=True)
                os.symlink(os.path.relpath(shots, os.path.dirname(link)), link)
        except OSError:
            pass

    # A spoken start rides in the same message as the work. The turn is
    # still mine, so the session is told to carry on with it.
    rest = " Go on with the rest of my message." \
        if hook.answering == "PreToolUse" else ""
    panes.say(pane, f"/rename {title}", 1.5)
    if keep:
        hook.done(f"Session successfully took over {title}. Its folder was kept.{along}{rest}")
    hook.done(f"Session successfully renamed to {title}.{swept}{along}{rest}")


if __name__ == "__main__":
    main()
