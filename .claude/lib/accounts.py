#!/usr/bin/env python3
"""accounts.py — this Mac's Claude accounts, and the one a launched session runs under, when none is named.

An account is a folder. Claude Code keeps a login, its settings and its
transcripts in one, and CLAUDE_CONFIG_DIR names it. Its own, ~/.claude,
needs no naming.

Every account on this Mac sits in one list, outside every project, so
each project here reads the same ones: ~/.claude-accounts.json.

  {"accounts": {"1": {"folder": "~/.claude", "plan": "20x", "name": "cesar"},
                "2": {"folder": "~/.claude-acct2", "plan": "20x", "name": "ahmad"}},
   "chrome": "1"}

An account's number is one digit. Its plan shows on 1100/system, and its
name on its status line. Chrome names the account that drives my Chrome;
naming none, the first account does. An account with no folder, or one
another account already holds, is left out. With no list, or one that
cannot be read, there is one account: 1, in ~/.claude. Every reader takes
the accounts from here, and reads the list once, as it starts.

I set an order on 1100/system, as 3 2 1 3 2. Each session launched with
no account named takes the next one, and the order starts over at its end,
so the order is also each account's share of the launches. A turn naming
an account the list lacks is passed over, and keeps its place, so a list
mended later finds the order whole. With no order, a launch takes the
first account.

A named account always wins, and takes no turn: a flag, a pill picked on
the launch page, an account a handover names. A successor named none
takes the next turn, like any launch.

The order, and the turn the next launch takes, sit in
.claude/state/accounts/order.json. The file is locked while a turn is
taken, so two launches at once never take the same one.

Beside the order sits the effort a launched session starts at, when none
is named. It is the same whatever the account. With none set, it is max.
It sits in .claude/state/accounts/effort.json.

The model works the same way, in model.json, as a family: a launch
starts on its newest model, lib/models.py's. With none set, it is opus.

An account may also be pinned to a family, in pins.json, as {"2": "opus",
"3": "sonnet"}. A session booted on a pinned account runs that family's
newest model, whatever its launch named, so no launch puts a model on an
account I ruled out for it. With no file, no account is pinned.

Each account also keeps its own default: the model and effort a session
I start myself on it takes, in any project. They sit in the account's own
settings.json, where /model and /effort in any of its sessions write too.
Claude Code keeps an effort per model, under modelSettings, and keeps max
for one session only, so max is never saved there.

It stays on Python 3.9, and so does models.py, which it imports.
memory-guard.py imports it, and launchd runs that on macOS's own
/usr/bin/python3, 3.9, which never moves with Homebrew.

Imported, never run.
"""

from __future__ import annotations

import fcntl
import json
import os
import re

import models

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIST = os.path.expanduser("~/.claude-accounts.json")
# Claude Code's own folder: a session runs under it when CLAUDE_CONFIG_DIR
# names none.
DEFAULT = os.path.expanduser("~/.claude")
# One digit, since an order is typed as 32132, one account to a character.
NUMBER = re.compile(r"[1-9]")
FILE = os.path.join(ROOT, ".claude", "state", "accounts", "order.json")
EFFORT = os.path.join(ROOT, ".claude", "state", "accounts", "effort.json")
# The settings files cannot hold max, so it rides each launch's --effort.
EFFORT_FALLBACK = "max"
MODEL = os.path.join(ROOT, ".claude", "state", "accounts", "model.json")
MODEL_FALLBACK = "opus"
PINS = os.path.join(ROOT, ".claude", "state", "accounts", "pins.json")
# The efforts an account's settings.json can keep.
SAVED = ("low", "medium", "high", "xhigh")


def mac(path: str = LIST) -> dict:
    """The list at PATH, kept to what it may hold: {"accounts": {"1":
    {"folder": "/Users/me/.claude", "plan": "20x", "name": "cesar"}},
    "chrome": "1"}, each folder absolute. With no account it can read,
    one: 1, in ~/.claude."""
    try:
        with open(path) as f:
            got = json.load(f)
    except (OSError, ValueError):
        got = {}
    got = got if isinstance(got, dict) else {}
    raw = got.get("accounts") if isinstance(got.get("accounts"), dict) else {}
    out = {}
    for n, a in sorted(raw.items()):
        folder = a.get("folder") if isinstance(a, dict) else None
        if not (NUMBER.fullmatch(n) and isinstance(folder, str) and folder.startswith(("~", "/"))):
            continue
        folder = os.path.abspath(os.path.expanduser(folder))
        if any(o["folder"] == folder for o in out.values()):
            continue
        out[n] = {"folder": folder, "plan": str(a.get("plan") or ""), "name": str(a.get("name") or "")}
    out = out or {"1": {"folder": DEFAULT, "plan": "", "name": ""}}
    chrome = str(got.get("chrome", ""))
    return {"accounts": out, "chrome": chrome if chrome in out else min(out)}


MAC = mac()
# Every account, by number.
ACCOUNTS = MAC["accounts"]
KNOWN = sorted(ACCOUNTS)
# Each account's folder, where Claude Code keeps its sessions and transcripts.
FOLDERS = tuple(ACCOUNTS[a]["folder"] for a in KNOWN)
# The account that drives my Chrome: tools/chrome.py.
CHROME = MAC["chrome"]
FALLBACK = KNOWN[0]


def parse(text: str) -> list | None:
    """An order as I type it: 3 2 1 3 2, or 3,2,1, or 32132. None when it
    holds anything but accounts, spaces and commas."""
    s = re.sub(r"[\s,]+", "", text or "")
    return list(s) if all(c in KNOWN for c in s) else None


def shape(d) -> dict:
    """What the file holds, kept to what it may: account numbers, and a turn
    inside the order. An account the list lacks keeps its place."""
    d = d if isinstance(d, dict) else {}
    raw = d.get("order") if isinstance(d.get("order"), list) else []
    order = [str(a) for a in raw if NUMBER.fullmatch(str(a))]
    try:
        at = int(d.get("next", 0)) % len(order) if order else 0
    except (TypeError, ValueError):
        at = 0
    return {"order": order, "next": at}


def due(d: dict) -> int | None:
    """Where the next launch's turn sits in a shaped order: the next turn,
    or the first after it whose account is listed. None when none is."""
    n = len(d["order"])
    return next((i % n for i in range(d["next"], d["next"] + n) if d["order"][i % n] in KNOWN), None)


def read() -> dict:
    """The order as launches take it, and the turn the next one takes. A
    turn the list lacks is left out. An empty order when none is set."""
    try:
        with open(FILE) as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            d = shape(json.load(f))
    except (OSError, ValueError):
        d = shape({})
    at = due(d)
    if at is None:
        return {"order": [], "next": 0}
    return {"order": [a for a in d["order"] if a in KNOWN],
            "next": sum(a in KNOWN for a in d["order"][:at])}


def write(f, d: dict) -> None:
    f.seek(0)
    f.truncate()
    json.dump(d, f)
    f.write("\n")
    f.flush()


def save(order: list) -> None:
    """Set a new order. Its first account is the next launch's."""
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        write(f, shape({"order": order, "next": 0}))


def take() -> str:
    """The next launch's account. Its turn is taken, so the one after moves
    up. A turn the list lacks is passed over, never taken."""
    try:
        f = open(FILE, "r+")
    except OSError:
        return FALLBACK
    with f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            d = shape(json.load(f))
        except ValueError:
            return FALLBACK
        at = due(d)
        if at is None:
            return FALLBACK
        write(f, {"order": d["order"], "next": (at + 1) % len(d["order"])})
        return d["order"][at]


def effort() -> str:
    """The effort a launched session starts at, when none is named."""
    import panes  # panes imports this module, so it comes in here
    try:
        with open(EFFORT) as f:
            got = json.load(f).get("effort")
    except (OSError, ValueError, AttributeError):
        got = None
    return got if got in panes.EFFORTS else EFFORT_FALLBACK


def save_effort(level: str) -> None:
    """Set the effort every launch starts at. A level Claude Code refuses is ignored."""
    import panes  # panes imports this module, so it comes in here
    if level not in panes.EFFORTS:
        return
    os.makedirs(os.path.dirname(EFFORT), exist_ok=True)
    with open(EFFORT + ".new", "w") as f:
        json.dump({"effort": level}, f)
        f.write("\n")
    os.replace(EFFORT + ".new", EFFORT)


def model() -> str:
    """The model a launched session starts at, when none is named: the
    newest of the family set. A model saved before families were kept
    stands for its own family."""
    try:
        with open(MODEL) as f:
            got = json.load(f).get("model")
    except (OSError, ValueError, AttributeError):
        got = None
    return models.newest(got if isinstance(got, str) and re.fullmatch(r"[A-Za-z0-9.-]+", got)
                         else MODEL_FALLBACK)


def save_model(name: str) -> None:
    """Set the family every launch starts on. A model names its own family.
    A name `--model` cannot take is ignored."""
    if not re.fullmatch(r"[A-Za-z0-9.-]+", name or ""):
        return
    os.makedirs(os.path.dirname(MODEL), exist_ok=True)
    with open(MODEL + ".new", "w") as f:
        json.dump({"model": models.family(name) or name}, f)
        f.write("\n")
    os.replace(MODEL + ".new", MODEL)


def pinned(account: str) -> str:
    """The model account ACCOUNT is pinned to: its family's newest. Empty
    when it is pinned to none, or to a family models.py does not know."""
    try:
        with open(PINS) as f:
            got = json.load(f).get(str(account))
    except (OSError, ValueError, AttributeError):
        got = None
    return models.newest(got) if isinstance(got, str) and got in dict(models.families()) else ""


def logins() -> dict:
    """Each account's login, by the uuid Claude Code signed it in under:
    {"<uuid>": ("2", "me@example.com")}. Claude Code keeps its own folder's
    beside it, in ~/.claude.json, and every other folder's inside it. A
    Chrome extension and the desktop app name a login only by its uuid:
    tools/chrome.py and lib/registry.py read them here."""
    out = {}
    for n in KNOWN:
        folder = ACCOUNTS[n]["folder"]
        path = (os.path.expanduser("~/.claude.json") if folder == DEFAULT
                else os.path.join(folder, ".claude.json"))
        try:
            with open(path, encoding="utf-8") as f:
                who = json.load(f).get("oauthAccount") or {}
        except (OSError, ValueError, AttributeError):
            continue
        if who.get("accountUuid"):
            out[who["accountUuid"]] = (n, who.get("emailAddress", ""))
    return out


def settings_file(account: str) -> str:
    """Account ACCOUNT's settings.json, in its folder."""
    return os.path.join(ACCOUNTS[account]["folder"], "settings.json")


def settings(account: str) -> dict | None:
    """What account ACCOUNT's settings.json holds: {} with no file, None
    when it holds anything but a JSON object."""
    try:
        with open(settings_file(account)) as f:
            got = json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        return None
    return got if isinstance(got, dict) else None


def own(account: str) -> dict:
    """Account ACCOUNT's own default, as {"saved": "opus", "model":
    "claude-opus-5-5", "effort": "xhigh"}. Saved is the model as its file
    names it. Model is the one it starts on: a family's newest, or the model
    saved. Effort is the one kept for that model. Each is empty when none
    is: with no model saved, Claude Code picks its own."""
    d = settings(account) or {}
    saved = d.get("model") if isinstance(d.get("model"), str) else ""
    base = re.sub(r"\[\w+\]$", "", saved)
    model = models.newest(base) if base in dict(models.families()) else base
    per = d.get("modelSettings") if isinstance(d.get("modelSettings"), dict) else {}
    kept = per.get(model) if isinstance(per.get(model), dict) else {}
    return {"saved": saved, "model": model,
            "effort": kept.get("effortLevel") if kept.get("effortLevel") in SAVED else ""}


def save_own(account: str, family: str = "", effort: str = "") -> None:
    """Set account ACCOUNT's own default model, as a family, so it moves
    with each new one. Or set the effort kept for the model it starts on,
    as /effort keeps it. A file that is not a JSON object is never written,
    nor an effort before a model is saved."""
    if account not in KNOWN:
        return
    d = settings(account)
    if d is None:
        return
    if family:
        if family not in dict(models.families()):
            return
        d["model"] = family
    if effort:
        at = own(account)["model"]
        if effort not in SAVED or not at:
            return
        per = d.get("modelSettings") if isinstance(d.get("modelSettings"), dict) else {}
        per[at] = {**(per[at] if isinstance(per.get(at), dict) else {}), "effortLevel": effort}
        d["modelSettings"] = per
    path = settings_file(account)
    try:
        mode = os.stat(path).st_mode & 0o777
    except OSError:
        mode = 0o600
    # Written as Claude Code writes it, beside it, then swapped in whole.
    fresh = f"{path}.{os.getpid()}.new"
    with open(fresh, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.chmod(fresh, mode)
    os.replace(fresh, path)
