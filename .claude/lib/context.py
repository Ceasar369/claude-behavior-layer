#!/usr/bin/env python3
"""context.py — how full each session's context is, and System's two
thresholds: the handover threshold, past which a session is handed over,
and the wrap-up threshold, past which a working session is told to wrap up.

A session's context is its transcript's last usage: input, cache reads and
cache writes, over its model's window, rounded, as its status line's ctx:
reads it. A <synthetic> record, from a resumed or failed turn, carries no
usage, and is skipped. Right after /compact the status line reads 0 until
the next call, so a compact boundary newer than every usage counts its
postTokens. A session whose process is gone has no context.

The transcript is read from its end, as far back as a question needs, so a
long one costs only what is walked.

Both thresholds are set on 1100/system, and sit in
.claude/state/context/threshold.json. The wrap-up threshold never sits
under the handover one.

Imported, never run.
"""

import json
import math
import os

import models
import registry
import transcripts

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = os.path.join(ROOT, ".claude", "state", "context", "threshold.json")
# Stand-in: 70, until I set the threshold on System.
FALLBACK = 70
# Stand-in: 80, until I set the wrap-up threshold on System.
WRAPUP = 80

CHUNK = 262_144

# Each question's answer, kept while its transcript's size and time hold.
KEPT: dict = {}


def share(tokens: int, model: str) -> int:
    """Tokens over the model's window, as Claude Code's catalog gives it,
    in whole percent, held to 0 to 100. A half rounds up, as Claude Code
    rounds it."""
    return min(100, max(0, math.floor(tokens * 100 / models.window(model) + 0.5)))


def point(line: bytes):
    """One record's usage, as (tokens, model, when), or None. A compact
    boundary carries no model."""
    if b'"usage"' not in line and b'"compact_boundary"' not in line:
        return None
    try:
        d = json.loads(line)
    except ValueError:
        return None
    if not isinstance(d, dict):
        return None
    at = transcripts.moment(d)
    when = int(at.timestamp()) if at else 0
    if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
        post = (d.get("compactMetadata") or {}).get("postTokens")
        return (int(post), "", when) if isinstance(post, int) else None
    message = d.get("message") if d.get("type") == "assistant" else None
    usage = message.get("usage") if isinstance(message, dict) else None
    if not isinstance(usage, dict) or message.get("model") == "<synthetic>":
        return None
    tokens = sum(usage.get(k) or 0 for k in
                 ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return tokens, message.get("model") or "", when


def points(path: str):
    """Every usage in a transcript, newest first."""
    try:
        f = open(path, "rb")
    except OSError:
        return
    with f:
        end = f.seek(0, os.SEEK_END)
        cut = b""
        while end > 0:
            start = max(0, end - CHUNK)
            f.seek(start)
            lines = (f.read(end - start) + cut).split(b"\n")
            # A chunk starts mid-line, so its first piece joins the chunk before it.
            cut = lines.pop(0) if start else b""
            end = start
            for line in reversed(lines):
                if got := point(line):
                    yield got


def kept(path: str, question, answer):
    """A question about a transcript, answered once while it stands still."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    mark = (st.st_size, st.st_mtime_ns)
    if (got := KEPT.get((path, question))) and got[0] == mark:
        return got[1]
    found = answer()
    KEPT[(path, question)] = (mark, found)
    return found


def last(path: str):
    """The transcript's context now, as (tokens, model), or None before its
    first answer. A compact boundary's tokens take the model of the answer
    before it."""
    def answer():
        tokens = None
        for got, model, _ in points(path):
            tokens = got if tokens is None else tokens
            if model:
                return tokens, model
        return None if tokens is None else (tokens, "")
    return kept(path, "last", answer)


def percent(record: dict, running: dict):
    """A registered session's context, in whole percent, or None. `running`
    is registry.claude_records()."""
    if record.get("session_id") not in running:
        return None
    got = last(record.get("transcript", ""))
    return share(*got) if got else None


def crossed(path: str, limit: int) -> int:
    """When the transcript's context last rose to `limit` percent, in epoch
    seconds: its oldest usage in the newest run at or past it. 0 under it."""
    def answer():
        got, at = last(path), 0
        for tokens, _, when in points(path) if got else ():
            if share(tokens, got[1]) < limit:
                break
            at = when
        return at
    return kept(path, ("crossed", limit), answer) or 0


def held() -> dict:
    """Both thresholds as System saved them. A file never written holds none."""
    try:
        with open(FILE) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return got if isinstance(got, dict) else {}


def percent_of(got) -> int | None:
    """A saved threshold, when it is a whole percent, 1 to 99."""
    return got if isinstance(got, int) and 1 <= got <= 99 else None


def threshold() -> int:
    """The context, in whole percent, past which a session is handed over:
    its page invites me, and its driver hands it over."""
    return percent_of(held().get("threshold")) or FALLBACK


def wrapup() -> int:
    """The context, in whole percent, past which a working session is told
    to wrap up its turn. Never under the handover threshold."""
    return max(percent_of(held().get("wrapup")) or WRAPUP, threshold())


def save(name: str, text: str) -> None:
    """Set one threshold, threshold or wrapup, and keep the other. Anything
    but a whole percent, 1 to 99, is ignored."""
    s = str(text).strip()
    if not (s.isdigit() and 1 <= int(s) <= 99):
        return
    registry.write_whole(FILE, json.dumps({**held(), name: int(s)}) + "\n")
