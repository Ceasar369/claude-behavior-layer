#!/usr/bin/env python3
"""Validate source and run the existing tests that use isolated fixtures.

No Claude session, browser, iTerm pane, dashboard, or account setup starts.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS = ("walk-clear-test.py", "drive-test.py", "follow-test.py", "launch-plan-test.py")


def main() -> None:
    python_files = sorted((ROOT / ".claude").rglob("*.py"))
    for path in python_files:
        ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))
    for path in (ROOT / ".claude/settings.json", ROOT / ".claude/project.example.json",
                 ROOT / ".mcp.json", ROOT / ".claude/mods/.claude-plugin/marketplace.json",
                 ROOT / ".claude/mods/zero-turn/.claude-plugin/plugin.json"):
        json.loads(path.read_text())
    print(f"Parsed {len(python_files)} Python files and five JSON files.", flush=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for name in TESTS:
        print(f"Checking {name}", flush=True)
        subprocess.run([sys.executable, str(ROOT / ".claude/tools" / name)],
                       cwd=ROOT, env=env, check=True)
    print("All isolated checks passed.")


if __name__ == "__main__":
    main()
