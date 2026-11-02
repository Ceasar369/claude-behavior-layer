#!/usr/bin/env python3
"""handover-prepare.py — the hook behind /handover-prepare.

    /handover-prepare                       save this conversation
    /handover-prepare account 2             and the successor's account
    /handover-prepare model M effort high   its model and its effort
    /handover-prepare account 3 max         a bare effort word is its effort
    /handover-prepare effort system         System's effort, whatever this seat was named

The conversation is copied as transcript.py copies it, into handovers/K.md,
K one more than the newest copy there. A setting named goes into
resume.json, and one not named keeps what resume.json held. lib/handover.py
reads the words and keeps the files.

Nothing launches, and this session runs on. handover-resume launches the
successor later, from any session. The copy is taken at once, so an agent
still running ends outside it.

The sentence back reminds me to name what still runs. An agent, a wait,
another session I watch: any of those can wake this session headless
later, however long after its pane is closed, and it will not show closed
again on its own.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import handover  # noqa: E402
import hook  # noqa: E402
import registry  # noqa: E402

TRIGGER = "/handover-prepare"
TRANSCRIPT = os.path.join(hook.ROOT, ".claude", "tools", "transcript.py")


def main() -> None:
    args = hook.words(TRIGGER)
    nn = registry.number_of(args.event.get("session_id") or "")
    if not nn:
        hook.done("This session holds no number. Nothing was saved.")

    named, odd = handover.settings(list(args))
    if odd:
        hook.done(f"{' '.join(odd)}: not a setting. Name an account, a model or an effort. "
                  "Nothing was saved.")

    r = subprocess.run([sys.executable, TRANSCRIPT, "copy", nn, "--into", nn],
                       capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        hook.done(f"{r.stderr.strip() or 'The copy failed.'} Nothing was saved.")

    have = handover.copies(nn)
    k = int(have[-1][:-3]) + 1 if have else 1
    into = os.path.join(registry.folder(nn), handover.HANDOVERS)
    os.makedirs(into, exist_ok=True)
    os.replace(os.path.join(hook.ROOT, r.stdout.splitlines()[0]), os.path.join(into, f"{k}.md"))
    if named:
        handover.keep(nn, named)

    hook.done(f"Session {nn} successfully saved as handovers/{k}.md. Name what still runs in "
              f"your reply, an agent, a wait, another session — it can wake you headless later. "
              f"Run handover-resume {nn} from a fresh session.")


if __name__ == "__main__":
    main()
