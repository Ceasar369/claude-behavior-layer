#!/usr/bin/env python3
"""blurb.py — one blurb, written to its session's folder, its path printed.

The blurb arrives on stdin. Its file holds the blurb alone, and is named
for the skill that wrote it and the minute it was written. A name already
taken gains -2, -3.

  blurb.py NN session          < blurb    blurb-session-YYYY-MM-DD-HHMM.md
  blurb.py NN browser          < blurb    blurb-browser-YYYY-MM-DD-HHMM.md
  blurb.py NN gpt [FILE ...]   < ask      blurb-gpt-YYYY-MM-DD-HHMM.md

A browser reader holds nothing of this repo. So its blurb opens on my
rule files in full, as a GPT blurb carries them, bar the vault's front
door, which sends it to files it cannot open. Of this repo's CLAUDE.md it
carries the Communication section alone, read from the file each time:
the turn's shape. The rest of it sends the reader to files too.

A GPT reader holds nothing of this machine and opens no path. So its blurb
carries every file in full, under its absolute path: what Claude Code
loads every time, then the files the ask touches. It opens on a line
naming AGENTS.md, then a check, and closes on a fresh code word, so a reply
quoting that word proves the whole file was read. A .env file never goes,
since it holds secrets.
"""

import argparse
import glob
import os
import secrets
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import registry  # noqa: E402

ROOT = registry.ROOT

KINDS = ("session", "browser", "gpt")

MOC = os.path.join(ROOT, "knowledge", "MOC.md")
OWN = os.path.join(ROOT, "CLAUDE.md")
# The one section of OWN a browser blurb carries.
COMMUNICATION = "Communication"

AGENTS = "I keep an AGENTS.md, this project's CLAUDE.md for Codex. Respect it."

CHECK = "Your reply's Title is this file's last line, word for word."

RULES = """The files below are my rules. Follow them in every reply, for this whole conversation.

Rules about sessions, panes, skills, hooks and git govern my Claude Code sessions. They do not bind you."""

ANSWER = f"""How to answer

You have no tools, and no access to my machine. Everything you need is in this file.

{RULES}

When you propose a change to a file, name its absolute path and give its full new text."""


def loaded() -> list:
    """The CLAUDE.md files Claude Code loads every time: the project's, the
    running account's own and ~/.claude's, each when it exists. ~/.claude's
    loads in every project under my home, on every account."""
    own = os.path.join(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or accounts.DEFAULT), "CLAUDE.md")
    home = os.path.expanduser("~/.claude/CLAUDE.md")
    return [p for p in dict.fromkeys(map(os.path.abspath, (OWN, own, home)))
            if os.path.isfile(p)]


def rules() -> list:
    """What Claude Code loads every time: the CLAUDE.md files, then the
    rules. The vault's front door closes the list."""
    return [*loaded(), *sorted(glob.glob(os.path.join(ROOT, ".claude", "rules", "*.md"))), MOC]


def browser() -> list:
    """What a browser blurb carries above the blurb, in rules()'s order:
    each file in full, bar the vault's front door, and of this repo's
    CLAUDE.md its Communication section alone."""
    return [part(OWN, COMMUNICATION) if p == OWN else section(p) for p in rules() if p != MOC]


def carried(names: list) -> list:
    """Every file the GPT blurb carries, absolute, each once. Refuses a bad one."""
    out = []
    for name in rules() + [os.path.join(ROOT, n) for n in names]:
        path = os.path.abspath(name)
        if os.path.basename(path).startswith(".env"):
            sys.exit(f"Refused: {path} is a .env file.")
        if not os.path.isfile(path):
            sys.exit(f"Refused: {path} is not a file.")
        if path not in out:
            out.append(path)
    return out


def section(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        text = f.read().rstrip("\n")
    return f"=== FILE {path} ===\n\n{text}\n\n=== END FILE {path} ==="


def part(path: str, heading: str) -> str:
    """One `## ` section of a file, its heading to the next one's, framed
    as section() frames a file. Refuses a file without it."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if f"## {heading}" not in lines:
        sys.exit(f"Refused: {path} holds no {heading} section.")
    start = lines.index(f"## {heading}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    text = "\n".join(lines[start:end]).strip("\n")
    return f"=== FILE {path}, its {heading} section alone ===\n\n{text}\n\n=== END FILE {path} ==="


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("number")
    p.add_argument("kind", choices=KINDS)
    p.add_argument("files", nargs="*")
    a = p.parse_args()
    if a.files and a.kind != "gpt":
        sys.exit("Refused: only a gpt blurb carries files.")
    body = sys.stdin.read().strip("\n")
    if not body.strip():
        sys.exit("Refused: no blurb on stdin.")
    word = ""
    if a.kind == "browser":
        body = "\n\n".join([RULES, *browser(), body])
    if a.kind == "gpt":
        word = f"Code word: {secrets.token_hex(4)}"
        parts = [AGENTS, CHECK, body, ANSWER, *map(section, carried(a.files)), word]
        body = "\n\n".join(parts)
    folder = registry.folder(a.number)
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, f"blurb-{a.kind}-{time.strftime('%Y-%m-%d-%H%M')}")
    path, n = stem + ".md", 2
    while os.path.exists(path):
        path, n = f"{stem}-{n}.md", n + 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "\n")
    print(path)
    if word:
        print(word)


if __name__ == "__main__":
    main()
