#!/usr/bin/env python3
"""handover-resume.py — the hook behind /handover-resume.

    /handover-resume 23                  launch session 23's successor
    /handover-resume 23 account 1 high   with settings of my own
    /handover-resume 23 model system     on System's model, whatever 23 was named

Each of account, model and effort comes from my words, then resume.json,
then the model and effort 23's launch named: lib/handover.py's carried().
Only those ride as flags. What none names takes launch.py's own: the
order's next account, and the model and effort set on System. The
successor's folder keeps what its flags named, so its own successor
takes the same. lib/handover.py reads the words and writes the message.

The successor opens below the pane that typed this. It takes seat 23,
which ends session 23 and closes its pane, then reads every copy in its
handovers/, oldest first. Nothing is written in 23's folder here.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import handover  # noqa: E402
import hook  # noqa: E402
import registry  # noqa: E402

TRIGGER = "/handover-resume"
LAUNCH = os.path.join(hook.ROOT, ".claude", "tools", "launch.py")


def main() -> None:
    args = hook.words(TRIGGER)
    if not args or not re.fullmatch(r"\d{1,2}", args[0]):
        hook.done("Name the seat to resume, as in /handover-resume 23. Nothing was launched.")
    nn = f"{int(args[0]):02d}"

    try:
        with open(os.path.join(registry.folder(nn), registry.RECORD)) as f:
            record = json.load(f)
    except (OSError, ValueError):
        hook.done(f"There is no seat {nn}. Nothing was launched.")
    if not handover.copies(nn):
        hook.done(f"handover-prepare was never run on {nn}. Nothing was launched.")

    named, odd = handover.settings(list(args[1:]))
    if odd:
        hook.done(f"{' '.join(odd)}: not a setting. Name an account, a model or an effort. "
                  "Nothing was launched.")
    chosen = handover.carried(nn, named)

    # The successor's name is the seat's own words, without its number.
    title = record.get("title", "")
    cmd = [sys.executable, LAUNCH, "session",
           "--name", title[3:] if re.match(r"\d{2}-", title) else "",
           "--message", handover.message(nn), "--where", "down"]
    for setting in ("account", "model", "effort"):
        if chosen.get(setting):
            cmd += [f"--{setting}", chosen[setting]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        hook.done(f"{r.stderr.strip() or 'The launch failed.'} Seat {nn} is unchanged.")

    hook.done(f"Session {nn}'s successor successfully launched. "
              f"It takes seat {nn} now, and {nn}'s pane closes.")


if __name__ == "__main__":
    main()
