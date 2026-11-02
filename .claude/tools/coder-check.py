#!/usr/bin/env python3
"""coder-check.py — the files one session wrote since its last check.

coder-check reads them against the vault. A file counts when git shows it
changed since the last check closed, in a commit or not yet committed, and
the session or its agents wrote, moved or deleted it after then: with a
Write or an Edit, or with the shell, as transcripts.touched() reads a
command. Only `code/`, the vault and the docs folder .claude/project.json
names count, and of the playbook only its stack, which describes the
code: behaviour-doctor checks `.claude/` and the rest of the playbook. No
check closed yet, the whole transcript counts.

  coder-check.py open 04    every file session 04 wrote since its last check
  coder-check.py close 04   the next check starts from now

open prints one path per line, from the project's root. A path no longer
on disk carries "gone". close keeps the time in
.claude/state/sessions/NN/coder-check.
"""

import argparse
import datetime
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import project  # noqa: E402
import registry  # noqa: E402
import transcripts  # noqa: E402

ROOT = registry.ROOT
COUNTED = ("code/", "knowledge/") + ((project.DOCS,) if project.DOCS else ())
SKIPPED = "knowledge/0010-playbook/"
SPARED = project.STACK


def mark(nn: str) -> str:
    return os.path.join(registry.folder(nn), "coder-check")


def last_check(nn: str):
    """When the last check closed, or None when none has."""
    try:
        with open(mark(nn)) as f:
            return datetime.datetime.fromisoformat(f.read().strip())
    except (OSError, ValueError):
        return None


def changed(since: datetime.datetime) -> set:
    """Every counted path git shows changed since `since`: in a commit since
    then, or not yet committed, untracked files included."""
    log = subprocess.run(["git", "log", f"--since={since.isoformat()}", "--no-renames", "--name-only", "--format="],
                         cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    status = subprocess.run(["git", "status", "--porcelain", "--no-renames", "--untracked-files=all"],
                            cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    return {p for p in log + [line[3:] for line in status]
            if p.startswith(COUNTED) and (p.startswith(SPARED) or not p.startswith(SKIPPED))}


def written(nn: str) -> list:
    """Every counted file the session and its agents wrote since its last check."""
    path, _ = transcripts.find(nn)
    if not path:
        sys.exit(f"No transcript for session {nn}.")
    since = last_check(nn) or next(filter(None, map(transcripts.moment, transcripts.records(path))), None)
    if not since:
        return []
    files = changed(since)
    found = set()
    for one in [path] + glob.glob(f"{path[:-len('.jsonl')]}/subagents/*.jsonl"):
        found |= transcripts.touched(one, since, files)
    return sorted(found)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["open", "close"])
    ap.add_argument("nn")
    args = ap.parse_args()
    if args.verb == "open":
        for rel in written(args.nn):
            gone = "" if os.path.exists(os.path.join(ROOT, rel)) else "  gone"
            print(f"{rel}{gone}")
        return
    os.makedirs(registry.folder(args.nn), exist_ok=True)
    with open(mark(args.nn), "w") as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat())
    print(f"Session {args.nn}'s next check starts now.")


if __name__ == "__main__":
    main()
