#!/usr/bin/env python3
"""wave-open.py — while a session's clarify wave is open, my message
reaches it with the wave named, so I can answer in chat.

A UserPromptSubmit hook, with no skill behind it. A session folded my chat
answers only when it ran clarify-items again by itself, so a wave I
answered, or moved on from, in chat stayed on my page. While this
session's newest wave is open, every message I type carries one line more:
the wave, each item I left unanswered, by number and title, and the line
Send would type, so the skill waiting on the wave goes on as after Send.
clarify-items Step 1 then judges my message against the wave.

    session 04 · wave 3 waits, items 12 and 13 unanswered · I type "agree 12"
        the session runs clarify-items, which folds 12 and brings 13 back

A wave sent and never folded is open too: Send's line never reached the
session. The line Send types hears nothing, nor /clarify-items, nor a
task's notice or an agent's report, which Claude Code queues as prompts.
A failure says nothing: this runs on every message of every session.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import registry  # noqa: E402

# What a notice opens with. I typed none of them.
NOTICE = ("<task-notification", "<agent-message", "Another Claude session sent a message")


def line(prompt: str, session_id: str) -> str:
    """The line my message carries, or nothing."""
    if not prompt or prompt.startswith(NOTICE) or prompt.startswith("/clarify-items"):
        return ""
    number = registry.number_of(session_id)
    # Most sessions hold no wave. Only one that does loads the tool.
    if not number or not os.path.isdir(os.path.join(registry.folder(number), registry.WAVES)):
        return ""
    clarify = page.tool("clarify-page")
    wave, head, left = clarify.open_wave(number)
    if not wave or " ".join(prompt.split()) == clarify.then(head):
        return ""
    turn = f"Before anything else, run `{clarify.then(head)}` through the Skill tool, as Send would"
    if head.get("sent"):
        return f"Wave {wave} was sent on my page, and never folded. {turn}: it folds what I sent."
    waits = (f"Wave {wave} waits on my page, unanswered there: {'; '.join(left)}." if left
             else f"Wave {wave} waits on my page, every item drafted there, unsent.")
    return (f"{waits} Does my message answer all of it, some, or none? {turn}. "
            "clarify-items Step 1 judges my message against the wave.")


def main() -> None:
    try:
        event = json.load(sys.stdin)
        said = line((event.get("prompt") or "").strip(), event.get("session_id") or "")
    except Exception:
        sys.exit(0)
    if said:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": said}}))


if __name__ == "__main__":
    main()
