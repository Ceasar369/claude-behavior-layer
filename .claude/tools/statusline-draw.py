#!/usr/bin/env python3
"""statusline-draw.py — the two lines every session's status line shows.

Claude Code hands the status line a payload on stdin. tools/statusline.py
keeps what it needs from it, then hands it here, and prints what this
prints. Run alone, it is a status line of its own.

  Line 1 — identity: who, which session, which model, what effort.
  Line 2 — meters: context, quotas, spend.

  [cesar] 91-accounts-and-paths · Opus 5.5 max
  ctx:12%  5h:36%(9:30PM)  7d:10%(Mon 11:00PM)  $4.21

Who is the session's account, by its name in this Mac's list,
lib/accounts.py's: its number when the list gives it no name, and ? for
an account the list lacks, or a list that cannot load. A reset is on this
Mac's clock.

Plain white throughout, no colour, no dim. Colour here would compete with
the agent colours in the task list above, where a hue means one agent.
The status line is chrome: it states, it never signals.

A malformed or partial payload never raises: each value falls back.
"""

import json
import locale
import math
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))


def at(d, *keys, default=None):
    """The value at KEYS, or DEFAULT when it is missing, null or false."""
    for k in keys:
        d = d.get(k) if isinstance(d, dict) else None
    return default if d is None or d is False else d


def number(v) -> float | None:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def percent(v) -> str:
    """A window's use, as 36%, or ? when the payload holds none."""
    n = number(v)
    return "?" if n is None else f"{n:.0f}%"


def clock(v, form: str) -> str:
    """A reset on this Mac's clock, its hour's leading zero dropped: 9:30PM,
    or Mon 11:00PM. ? when the payload holds none."""
    n = number(v)
    if n is None:
        return "?"
    return re.sub(r"(^| )0", r"\1", time.strftime(form, time.localtime(int(n))), count=1)


def account() -> str:
    """Who, as the list names the session's account. lib/accounts.py and
    lib/registry.py are imported only here, so one another session is
    mid-way through editing reads ?, never a blank line."""
    try:
        import accounts
        import registry
        a = registry.account()
        return (accounts.ACCOUNTS[a]["name"] or a) if a in accounts.ACCOUNTS else "?"
    except Exception:
        return "?"


def draw(d: dict) -> str:
    """Payload D's two lines, each ending on a newline."""
    who = account()
    session, effort = str(at(d, "session_name", default="")), str(at(d, "effort", "level", default=""))
    used = number(at(d, "context_window", "used_percentage", default=0))
    cost = number(at(d, "cost", "total_cost_usd", default=0))
    line1 = (f"[{who}]" + (f" {session}" if session else "")
             + f" · {at(d, 'model', 'display_name', default='unknown')}" + (f" {effort}" if effort else ""))
    line2 = (f"ctx:{math.floor(used) if used is not None and used >= 0 else 0}%"
             f"  5h:{percent(at(d, 'rate_limits', 'five_hour', 'used_percentage'))}"
             f"({clock(at(d, 'rate_limits', 'five_hour', 'resets_at'), '%I:%M%p')})"
             f"  7d:{percent(at(d, 'rate_limits', 'seven_day', 'used_percentage'))}"
             f"({clock(at(d, 'rate_limits', 'seven_day', 'resets_at'), '%a %I:%M%p')})"
             f"  ${cost if cost is not None and cost >= 0 else 0:.2f}")
    return f"{line1}\n{line2}\n"


def main() -> None:
    try:
        locale.setlocale(locale.LC_TIME, "")
    except locale.Error:
        pass
    try:
        d = json.loads(sys.stdin.read())
    except ValueError:
        d = {}
    sys.stdout.write(draw(d if isinstance(d, dict) else {}))


if __name__ == "__main__":
    main()
