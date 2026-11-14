#!/usr/bin/env python3
"""door.py — the app door's switch, and its log.

My app chat, a Claude app chat, reaches my sessions only through the
app door, tools/app-door.py, which the project's desktop extension runs.

Every act the door takes is logged. The switch, app-door.py open or
shut, shuts the door until it opens again.

Imported, never run.
"""

import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, ".claude", "state", "door")
# Present, the door is shut: every call is refused until it goes.
SHUT = os.path.join(STATE, "shut")
LOG = os.path.join(STATE, "log.jsonl")


def shut() -> bool:
    return os.path.exists(SHUT)


def switch(on: bool) -> None:
    """Open the door, or shut it."""
    if on:
        if os.path.exists(SHUT):
            os.remove(SHUT)
    else:
        os.makedirs(STATE, exist_ok=True)
        open(SHUT, "w").close()


def log(bot: str, act: str, session: str = "", said: str = "") -> None:
    """One line per act: when, who, what, on which session, and the refusal
    it met, if any."""
    os.makedirs(STATE, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "bot": bot, "act": act,
                            "session": session, "said": said}) + "\n")
