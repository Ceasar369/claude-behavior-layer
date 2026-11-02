#!/usr/bin/env python3
"""walker-scripts.py — holds a walker to the scripts walk-drive names.

A PreToolUse hook, matcher browser_evaluate and browser_run_code_unsafe,
with no skill behind it. A walker is a session whose own folder holds
walk.json. It runs only the scripts walk-drive's js fences hold, copied
whole: the passkey, offline and back online, the whole page's height, the
page text and a docs page's text. Spaces never count. In the page text,
only the move's words vary, and they never hold a backtick, a $ or a
backslash. Anything else is refused, and the walker asks its lead. Every
other session runs any script.

It reads the fences each call, and holds no copy of them.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import registry  # noqa: E402

SKILL = os.path.join(registry.ROOT, ".claude", "skills", "walk-drive", "SKILL.md")
FENCE = re.compile(r"```js\n(.*?)\n```", re.S)
MOVE = "<themove>"


def bare(script: str) -> str:
    return re.sub(r"\s+", "", script)


def allowed() -> list:
    """Each fence of walk-drive, as a pattern a script must match whole."""
    try:
        with open(SKILL) as f:
            text = f.read()
    except OSError:
        return []
    return [re.compile(re.escape(bare(s)).replace(re.escape(MOVE), r"[^`$\\]*"))
            for s in FENCE.findall(text)]


def walker(session_id: str) -> bool:
    nn = registry.number_of(session_id)
    return bool(nn) and os.path.isfile(os.path.join(registry.folder(nn), "walk.json"))


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    given = event.get("tool_input") or {}
    script = given.get("function") or given.get("code") or ""
    if not walker(event.get("session_id") or ""):
        return
    # A run_code filename loads a script from a file; an evaluate's saves its answer.
    loads = event.get("tool_name", "").endswith("run_code_unsafe") and given.get("filename")
    if not loads and any(p.fullmatch(bare(script)) for p in allowed()):
        return
    hook.answering = "PreToolUse"
    hook.done("A walker runs only the scripts walk-drive names, copied whole. "
              "Ask your lead, walk-drive Step 7, quoting what you meant to run.")


if __name__ == "__main__":
    main()
