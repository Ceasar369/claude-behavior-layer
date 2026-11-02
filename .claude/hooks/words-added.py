#!/usr/bin/env python3
"""words-added.py — a session told how many words its edit added to a document, with the four questions.

A PostToolUse hook on Write and Edit, with no skill behind it. A document
grows one edit at a time, so the questions arrive as each edit lands.

    an Edit adds 42 words to knowledge/standard.md
        the session reads the count and the four questions beside the result

An edit that adds nothing passes in silence. The questions are
`.claude/rules/thinking.md`'s, under "The least that works".
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import project  # noqa: E402

# The vault, and the docs folder .claude/project.json names, when it names one.
PATTERN = (rf"^{re.escape(hook.ROOT)}/(knowledge/" + (f"|{re.escape(project.DOCS)}" if project.DOCS else "")
           + r").+\.md$")

QUESTIONS = ("Does it need to exist? Does it exist already? "
             "Can something that exists do it? What is the smallest version that works?")


def added(event: dict) -> int:
    """Words on the patch's new lines, less words on its removed ones.
    A new file carries no patch, so its whole content counts."""
    response = event.get("tool_response") or {}
    if response.get("type") == "create":
        return len((response.get("content") or "").split())
    count = 0
    for hunk in response.get("structuredPatch") or []:
        for line in hunk.get("lines") or []:
            if line and line[0] in "+-":
                count += len(line[1:].split()) * (1 if line[0] == "+" else -1)
    return count


def main() -> None:
    found, event = hook.written(PATTERN)
    n = added(event)
    if n <= 0:
        sys.exit(0)
    rel = found.group(0)[len(hook.ROOT) + 1:]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": f"This edit added {n} words to `{rel}`. "
                             f"A line added to a document is something new. {QUESTIONS}"}}))


if __name__ == "__main__":
    main()
