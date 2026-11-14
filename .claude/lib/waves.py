#!/usr/bin/env python3
"""waves.py — a clarify wave's file, read and written.

A wave is .claude/state/sessions/NN/waves/wave-K.md: a head, then each
item, one field a line. tools/clarify-page.py draws it and takes my
answers. Two hooks read it on every message and at every stop, and what
every session loads stays small: so the file's own reading sits here,
apart from the page.

open_wave() is the wave still open, for the hooks that warn of it:
hooks/wave-open.py on each message of mine, hooks/9-session-stop.py at a
stop. then() is the line its Send types.

Imported, never run.
"""

import os
import re

import registry

WAVE = re.compile(r"wave-(\d+)\.md")
NUMBERED = re.compile(r"^## (\d+) ·", re.M)

# The lines a wave carries above its first item.
HEAD = ("sent", "then", "closed")

# What a session writes on an item. Each one line, but a picture.
GIVEN = ("question", "decision", "why", "wrong", "from", "after", "show",
         "today", "instead", "sources")

# Every line an item may carry, in the order a wave file writes them. An
# assistant's proposal follows what the session wrote. The row after it is a
# wave written by hand, kept so a round still open reads, and loses nothing.
FIELDS = GIVEN + ("proposed",) + (
    "status", "split", "answer", "changed", "led", "context", "what", "for",
    "against", "recommendation") + ("agree", "feedback")

SKILLS = os.path.join(registry.ROOT, ".claude", "skills")


def folder(nn: str) -> str:
    return os.path.join(registry.folder(nn), registry.WAVES)


def waves(nn: str) -> list:
    """Every wave in a session's waves/, as (number, path), oldest first."""
    try:
        names = os.listdir(folder(nn))
    except OSError:
        return []
    return sorted((int(m.group(1)), os.path.join(folder(nn), n))
                  for n in names if (m := WAVE.fullmatch(n)))


def parse(text: str) -> tuple:
    """A wave as (head, items).

    A line that names no field continues the one above it. A wave indents
    those lines, so a line of mine starting "why:" stays mine. A line keeps
    whatever indentation it carries past the wave's own two spaces, so a
    tree or a chart keeps its shape.
    """
    head, items, last = {"sent": "", "then": "", "closed": ""}, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            n, _, title = line[3:].partition("·")
            items.append({"n": n.strip(), "title": title.strip() or n.strip()})
            last = None
            continue
        if not line.strip():
            continue
        target = items[-1] if items else head
        key, sep, value = line.partition(":")
        key = key.strip().lower()
        if not line.startswith((" ", "\t")) and sep and key in (FIELDS if items else HEAD):
            target[key] = value.strip()
            last = key
        elif last:
            kept = line[2:] if line.startswith("  ") else line.strip()
            target[last] = (target[last] + "\n" + kept.rstrip()).strip("\n")
    return head, items


def dump(wave: int, head: dict, items: list) -> str:
    def field(k, v):
        first, *rest = (v or "").split("\n")
        return [f"{k}: {first}".rstrip()] + [f"  {r}".rstrip() for r in rest]
    out = [f"# Wave {wave}", f"sent: {head.get('sent', '')}".rstrip()]
    out += [f"{k}: {head[k]}" for k in ("then", "closed") if head.get(k)]
    out.append("")
    for it in items:
        out.append(f"## {it['n']} · {it['title']}")
        for k in FIELDS:
            if k in it or k in ("agree", "feedback"):
                out += field(k, it.get(k, ""))
        out.append("")
    return "\n".join(out)


def newest(nn: str) -> tuple:
    """The newest wave as (number, path, head, items), or number 0."""
    found = waves(nn)
    if not found:
        return 0, "", {}, []
    wave, path = found[-1]
    with open(path) as f:
        return (wave, path, *parse(f.read()))


def answered(it: dict) -> bool:
    """Agreed, now or in a wave written by hand, or carrying feedback."""
    return bool(it.get("feedback")) or it.get("agree") == "yes" \
        or it.get("status") == "agreed"


def open_wave(nn: str) -> tuple:
    """The newest wave not closed, as (number, head, the items I left
    unanswered, each "N · title"). Waiting on me, or sent and never folded.
    Number 0 when none is open."""
    wave, _, head, items = newest(nn)
    if not wave or head.get("closed"):
        return 0, {}, []
    return wave, head, [f"{it['n']} · {it['title']}" for it in items if not answered(it)]


def then(head: dict) -> str:
    """The line Send types: the wave's own slash command, when that skill
    still exists, or /clarify-items. A skill renamed since never types."""
    line = " ".join(head.get("then", "").split())
    name = line[1:].split(" ", 1)[0] if line.startswith("/") else ""
    return line if name and os.path.isfile(os.path.join(SKILLS, name, "SKILL.md")) else "/clarify-items"
