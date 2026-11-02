#!/usr/bin/env python3
"""plans.py — an assistant's plan, and the session each queued mission became.

An assistant's plan is one file in its own folder, stages.json. Queue
stamps a mission `queued` just before its launch. The session launched
under the mission's name then claims a number, and that number and its
title are written into the mission as `session` and `title`.

The claim hook writes them, the moment the session claims. The assistant's
page finds the same session the same way, for a mission not written yet.
Both match here, so a mission is never matched two ways. A session
renaming itself under its own number takes its mission's title along.

A mission is looked up by its id here too, so every caller finds the same one.

A plan runs in order, or is open: {"kind": "open", "stages": [...]}. A
plan with no kind runs in order. Open, a stage is a name grouping its
missions: each launches once I rule it, and no stage closes or ends the
plan but on my word. knowledge/0010-playbook/0011-assisting/the-stages.md
rules both kinds.

Imported, never run.
"""

import json
import os
import re

import registry

PLAN = "stages.json"


def plan(nn: str) -> dict:
    """One assistant's plan, or an empty one."""
    try:
        with open(os.path.join(registry.folder(nn), PLAN)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"stages": []}


def opened(p: dict) -> bool:
    """Whether plan P is open. With no kind, it runs in order."""
    return p.get("kind") == "open"


def save(nn: str, p: dict) -> None:
    with open(os.path.join(registry.folder(nn), PLAN), "w") as f:
        json.dump(p, f, indent=1)
        f.write("\n")


def mission(nn: str, k: str) -> dict:
    """Mission K of assistant NN's plan, or nothing."""
    for s in plan(nn).get("stages", []):
        for m in s.get("missions", []):
            if m.get("id") == k:
                return m
    return {}


def found(m: dict, held: dict, nn: str) -> dict:
    """The session a queued mission of plan NN became: its number and title, or nothing.

    It carries the mission's name, and claimed at or after its queue stamp.
    An assistant on a zero seat launches its missions into its own ten, so
    its session sits there: plans 30 and 40 both queuing a thinker never
    take each other's. None, or two, finds nothing. A guess would colour the
    wrong card.
    """
    if m.get("session") or not m.get("queued"):
        return {}
    words = registry.kebab(m["name"])
    hits = [(n, r["title"]) for n, r in held.items()
            if r.get("title", "")[3:] == words and r.get("claimed", "") >= m["queued"]
            and (nn[1] != "0" or n[0] == nn[0])]
    return {"session": hits[0][0], "title": hits[0][1]} if len(hits) == 1 else {}


def owners(held: dict) -> dict:
    """Each live session a plan's mission became, by number: (the plan's
    session, the mission's id).

    A number is handed out again once its session stops, so a mission is a
    session's own only while that session still holds the mission's title.
    """
    out = {}
    for nn in held:
        for s in plan(nn).get("stages", []):
            for m in s.get("missions", []):
                m = {**m, **found(m, held, nn)}
                n = m.get("session")
                if n in held and n != nn and m.get("title") == held[n].get("title"):
                    out[n] = (nn, m["id"])
    return out


def tag(number: str, owned: dict | None = None) -> str:
    """A session's name on every page: its number, then its mission's id
    while it runs one, number first. Session 23 on mission A3 reads 23-A3."""
    owned = owners(registry.entries()) if owned is None else owned
    return f"{number}-{owned[number][1]}" if number in owned else number


def claim(number: str) -> str:
    """Write a claim into the one queued mission it became, in the plan that queued it.

    Every plan on disk is read, and each queued mission matched by found().
    The one found to be this number's is written. None, or two, writes
    nothing. Returns the plan's number and the mission's id, as "10 A1".
    """
    held = registry.entries()
    hits = []
    for nn in sorted(n for n in registry.listing(registry.WORK) if re.fullmatch(r"\d{2}", n)):
        p = plan(nn)
        for s in p.get("stages", []):
            for m in s.get("missions", []):
                got = found(m, held, nn)
                if got.get("session") == number:
                    hits.append((nn, p, m, got))
    if len(hits) != 1:
        return ""
    nn, p, m, got = hits[0]
    m.update(got)
    save(nn, p)
    return f"{nn} {m['id']}"


def renamed(number: str, old: str, new: str) -> None:
    """Carry a rename into the mission it runs, in the plan that queued it.

    A session renaming itself under its own number stays on its mission.
    owners() matches by title, so each mission written as this number under
    its old title takes the new one.
    """
    for nn in sorted(n for n in registry.listing(registry.WORK) if re.fullmatch(r"\d{2}", n)):
        p = plan(nn)
        ms = [m for s in p.get("stages", []) for m in s.get("missions", [])
              if m.get("session") == number and m.get("title") == old]
        for m in ms:
            m["title"] = new
        if ms:
            save(nn, p)
