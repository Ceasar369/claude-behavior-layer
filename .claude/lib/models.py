#!/usr/bin/env python3
"""models.py — every model a session can launch on, read from Claude Code's own catalog.

Claude Code carries its model catalog inside its binary: each model, its
family, the name people read, its context window, and each family's
newest model. Claude Code updates itself, and a new model arrives with
the update. So Opus 5.6 shows here once Claude Code knows it, and no list
here is kept by hand.

A model is named as --model takes it, and as a transcript records it:
claude-opus-5-5, claude-haiku-4-5-20251001.

A family stands for its newest model. The model set on 1100/system is a
family, so it moves with each.

The binary is the claude the PATH finds, then ~/.local/bin/claude, where
Claude Code's own installer puts it: binary().

The catalog is read once per binary, and kept in
.claude/state/models/catalog.json beside the binary it came from. A new
binary is read again. One whose catalog cannot be read keeps the last
catalog kept. With none ever kept, a family is passed on as itself:
--model opus takes Claude Code's own newest Opus.

It stays on Python 3.9: lib/accounts.py imports it, and memory-guard.py
imports that.

Imported, never run.
"""

import json
import mmap
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = os.path.join(ROOT, ".claude", "state", "models", "catalog.json")
# Where a hook looks when its PATH is too thin to find claude.
BINARY = os.path.expanduser("~/.local/bin/claude")
# The window Claude Code gives a model it does not know.
WINDOW = 200_000

# The binary last read, and its catalog.
KEPT: dict = {}

# The catalog, as Claude Code's minifier writes it: an object literal. A
# string is kept whole, a bare key is quoted, and !0, !1 and void 0 are
# JSON's true, false and null.
TOKEN = re.compile(r'("(?:[^"\\]|\\.)*")|([A-Za-z_$][\w$]*)(?=:)|!0|!1|void 0|(?<=[:,\[])(-?)\.(?=\d)')


def jsonify(js: str) -> str:
    def one(m):
        if m.group(1):
            return m.group(1)
        if m.group(2):
            return f'"{m.group(2)}"'
        if m.group(3) is not None:
            return m.group(3) + "0."
        return {"!0": "true", "!1": "false"}.get(m.group(0), "null")
    return TOKEN.sub(one, js)


def parse(path: str) -> dict:
    """The catalog inside binary `path`, kept to what this layer reads.
    Raises when it is not there."""
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
        end = data.find(b"latest_per_family:{")
        start = data.rfind(b"models:[{id:", 0, end)
        close = data.find(b"}", end)
        if min(end, start, close) < 0:
            raise ValueError("no catalog")
        raw = json.loads(jsonify("{" + data[start:close + 1].decode() + "}"))
    ids = {m["id"]: (m.get("provider_ids") or {}).get("first_party") or m["id"] for m in raw["models"]}
    return {"binary": path,
            "models": [{"id": ids[m["id"]], "family": m.get("family", ""),
                        "name": m.get("display_name") or ids[m["id"]],
                        "window": int((m.get("context") or {}).get("window") or WINDOW)}
                       for m in raw["models"]],
            "latest": {k: ids.get(v, v) for k, v in raw["latest_per_family"].items()}}


def binary() -> str:
    """The claude a launch runs: the one the PATH finds, then BINARY. Empty
    when neither is there."""
    found = shutil.which("claude") or BINARY
    return found if os.path.exists(found) else ""


def catalog() -> dict:
    """Claude Code's catalog, from the binary a launch runs."""
    path = os.path.realpath(binary() or BINARY)
    if KEPT.get("binary") == path:
        return KEPT
    try:
        with open(FILE) as f:
            kept = json.load(f)
    except (OSError, ValueError):
        kept = {}
    if kept.get("binary") != path:
        try:
            got = parse(path)
        except (OSError, ValueError, KeyError, TypeError, UnicodeDecodeError):
            return kept or {"models": [], "latest": {}}
        # Two processes may read a new binary at once. Each writes its own copy.
        os.makedirs(os.path.dirname(FILE), exist_ok=True)
        fresh = f"{FILE}.{os.getpid()}.new"
        with open(fresh, "w") as f:
            json.dump(got, f, indent=1)
            f.write("\n")
        os.replace(fresh, FILE)
        kept = got
    KEPT.clear()
    KEPT.update(kept)
    return KEPT


def entry(model: str) -> dict:
    return next((m for m in catalog()["models"] if m["id"] == model), {})


def family(model: str) -> str:
    """A model's family. A family is its own. Empty when Claude Code knows neither."""
    return model if model in catalog()["latest"] else entry(model).get("family", "")


def newest(value: str) -> str:
    """The newest model of `value`'s family, `value` being a family or any
    model of it. Anything else is passed on as it is."""
    return catalog()["latest"].get(family(value)) or value


def name(model: str) -> str:
    """A model's name as people read it: Opus 5.5."""
    return entry(model).get("name") or model


def window(model: str) -> int:
    return entry(model).get("window") or WINDOW


def families() -> list:
    """Each family's newest model, as (family, model), in the catalog's order."""
    return list(catalog()["latest"].items())
