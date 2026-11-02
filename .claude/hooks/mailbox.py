#!/usr/bin/env python3
"""mailbox.py — refuses SendMessage, in every session.

A PreToolUse hook, matcher SendMessage, with no skill behind it. A session
reaches another by typing into its pane, through the skill its work names.
A mailed line never arrives. The session reads the refusal as the call's
answer.
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402


def main() -> None:
    sys.stdin.read()
    hook.answering = "PreToolUse"
    hook.done("SendMessage is never used. Type into the session's pane, through the skill your work names. "
              "The message skill is for when I ask.")


if __name__ == "__main__":
    main()
