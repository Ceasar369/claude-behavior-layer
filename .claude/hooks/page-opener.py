#!/usr/bin/env python3
"""page-opener.py — every session's commands find tools/page-opener/open first.

A SessionStart hook, with no skill behind it. Claude Code sources the file
CLAUDE_ENV_FILE names before each shell command, so the PATH written there
holds for the whole session, and for every program a command starts. A
page any of them opens then lands in its own Chrome profile, as
tools/page-opener/open says.

It prints nothing.
"""

import os

OPENER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "tools", "page-opener")

target = os.environ.get("CLAUDE_ENV_FILE")
if target:
    with open(target, "a") as f:
        f.write(f'export PATH="{OPENER}:$PATH"\n')
