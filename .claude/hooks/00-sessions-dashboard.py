#!/usr/bin/env python3
"""00-sessions-dashboard.py — the hook behind /00-sessions-dashboard.

    /00-sessions-dashboard           start 1100 and band 00, fresh
    /00-sessions-dashboard status    say whether it is live
    /00-sessions-dashboard restart   1100 alone, on the code on disk
    /00-sessions-dashboard stop      stop 1100 and band 00
    /00-sessions-dashboard flip      move 1100 and band 00 to the shifted ports, or back

Nothing is the common case, so nothing starts it. Four words exist.

Flip stops 1100 and band 00 on the ports they hold, moves the shift, then
starts both on the new ones: 1100 on 21100, or back. Another project
holding the old 1100 means nothing of this one runs there, so nothing
stops. Every session's own servers keep the ports they bound. A project
whose project.json fixes its shift refuses flip.

Band 00 is the project's own, as .claude/project.json names it. A
project naming none runs 1100 alone.

Typed while anything of it answers, the bare command stops all of it
first, then starts it, so one command always leaves it fresh. Every
session's own servers stay up through both.

While another project's 1100 answers on this one's, every word but flip
is refused, naming that project: lib/project.py's refusal. Flip is
refused only by one answering on the port it moves to.

A running 1100 keeps the code it started with. Restart swaps it only once
the new code draws, so a broken edit never takes the page down.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import serve  # noqa: E402

TRIGGER = "/00-sessions-dashboard"
SKILL = "sessions-dashboard"
TOOL =os.path.join(hook.ROOT, ".claude", "tools", "sessions-dashboard.py")


def main() -> None:
    args = hook.words(TRIGGER)
    word = args.first()

    refused = project.refusal(serve.PORT) if word in ("", "status", "restart", "stop") else ""
    if refused:
        hook.done(refused)

    if word == "":
        # The tool's stop waits until all of it is gone, so the start below
        # never finds a port still answering.
        up = ports.answering(serve.PORT) or bool(ports.held("00"))
        if up:
            subprocess.run([sys.executable, TOOL, "stop"], capture_output=True, text=True)
        problem = serve.start(SKILL, serve.PORT, TOOL)
        if problem:
            hook.done(problem)
        # The band is the tool's, next to the stop that takes it down.
        r = subprocess.run([sys.executable, TOOL, "band"],
                           capture_output=True, text=True)
        hook.done(f"Dashboard successfully {'restarted' if up else 'started'} on port "
                  f"{serve.PORT}. " + r.stdout.strip())
    if word == "status":
        live = ports.answering(serve.PORT)
        hook.done("Dashboard is live." if live else "Dashboard is not live.")
    if word == "restart":
        r = subprocess.run([sys.executable, TOOL, "restart"],
                           capture_output=True, text=True)
        hook.done(r.stdout.strip() or (r.stderr.strip().splitlines() or ["1100 could not restart."])[-1])
    if word == "stop":
        r = subprocess.run([sys.executable, TOOL, "stop"],
                           capture_output=True, text=True)
        hook.done(r.stdout.strip() or "Nothing was running.")
    if word == "flip":
        if project.FIXED:
            hook.done(f"Refused: .claude/project.json fixes this project's shift at {project.FIXED}, "
                      "so its ports do not flip.")
        if not project.refusal(serve.PORT):
            subprocess.run([sys.executable, TOOL, "stop"], capture_output=True, text=True)
        # The new port is read here, and the tool's every child reads the
        # file itself, so each starts on the shift just written.
        port = serve.PORT - ports.SHIFT + ports.flip()
        refused = project.refusal(port)
        if refused:
            hook.done(f"Ports moved, and nothing started. {refused}")
        problem = serve.start(SKILL, port, TOOL)
        if problem:
            hook.done(problem)
        r = subprocess.run([sys.executable, TOOL, "band"],
                           capture_output=True, text=True)
        back = "back to its own ports" if port == serve.PORT - ports.SHIFT else "clear of another project's"
        hook.done(f"Ports flipped, {back}: the dashboard successfully started on port {port}. "
                  + r.stdout.strip())

    hook.done("Say nothing to start it, or `status`, `restart`, `stop` or `flip`.")


if __name__ == "__main__":
    main()
