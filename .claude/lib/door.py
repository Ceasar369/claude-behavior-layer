#!/usr/bin/env python3
"""door.py — Grok's door to 1100: its keys, its switch, and its log.

Grok Bot runs on its own cloud computer, outside this Mac. It reaches 1100
only through the door, tools/grok-door.py, over Tailscale. Each bot holds
a key of its own, and a key carries only its bot's job:

  assistant  my executive assistant: every job below, alone
  operator   reads, and presses: types, Escape, a choice, a round's rulings,
             Send, a launch
  asker      Ask alone: a Sonnet session answers, and the door brings back
             its headline
  watcher    reads, What's new among it

Every act the door takes is logged under its bot's name. The switch on
1100's System page shuts the door for every bot at once. Both 1100 and
the door read this module, so the switch is one file both hear.

Imported, never run.
"""

import json
import os
import secrets
import time

import ports

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, ".claude", "state", "door")
KEYS = os.path.join(STATE, "keys.json")
# Present, the door is shut: every bot is refused until it goes.
SHUT = os.path.join(STATE, "shut")
LOG = os.path.join(STATE, "log.jsonl")
# Band 00's door, beside 1100: session 01 tries it on 1201. Grok's
# computer reaches this Mac on this port alone: Tailscale's policy lets
# tag:grok open it and nothing else.
PORT = 1200 + ports.SHIFT

JOBS = {"assistant": {"read", "press", "ask"}, "operator": {"read", "press"},
        "asker": {"ask"}, "watcher": {"read"}}


def _keys() -> dict:
    try:
        with open(KEYS) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def make(bot: str) -> str:
    """A new key for one bot, replacing its old one. Only the file holds
    it, readable by me alone."""
    os.makedirs(STATE, exist_ok=True)
    keys = _keys()
    key = secrets.token_urlsafe(32)
    keys[bot] = key
    fd = os.open(KEYS, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(keys, f, indent=1)
    return key


def bot_of(key: str) -> str:
    """The bot a key belongs to, or ""."""
    for bot, k in _keys().items():
        if key and secrets.compare_digest(k, key):
            return bot
    return ""


def may(bot: str, need: str) -> bool:
    return need in JOBS.get(bot, set())


def shut() -> bool:
    return os.path.exists(SHUT)


def switch(on: bool) -> None:
    """Open the door, or shut it for every bot."""
    if on:
        if os.path.exists(SHUT):
            os.remove(SHUT)
    else:
        os.makedirs(STATE, exist_ok=True)
        open(SHUT, "w").close()


def log(bot: str, act: str, session: str = "", said: str = "") -> None:
    """One line per act: when, which bot, what, on which session, and the
    refusal it met, if any."""
    os.makedirs(STATE, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "bot": bot, "act": act,
                            "session": session, "said": said}) + "\n")
