#!/usr/bin/env python3
"""project.py — this project's own facts, from its one file.

The layer runs in any project. What one project holds and another lacks
sits in .claude/project.json, tracked in git, and only this reads it.
Every key is optional. A missing file or key takes the fallback named
here, so a project naming nothing runs 1100 alone, on `work`, under its
folder's name. A file that cannot be read names nothing.

  name      the project's name, on 1100's phone app, each buzz and the
            Dock app. Its folder's name.
  branch    the one branch /8-ship commits. work.
  ports     "folders", the first digits this project's ports may take,
            beside the behaviour layer's own 1, and "roles", the second.
            Folder 7 with roles 1 and 2 gives session 05 7105 and 7205.
            "sites" gives a folder its own second digits in place of the
            roles: folder 2 with sites 2 and 3 gives 2205 and 2305.
            No folders: 1100 and its copies alone. No roles: 1 and 2.
            No sites: every folder takes the roles.
  band      band 00: its "servers", one group per layer, port by port; the
            "command" that starts them all; and "match", what the memory
            guard finds in their command lines. No servers or no command:
            1100 runs alone. No match: the command.
  database  the one database System shows a dot for: its "port", its
            "name", and the "pg_isready" that asks it. No port: no dot.
            No name: Database. No pg_isready: green while the port answers.
  docs      the docs folder coder-check counts and searches, from the
            root. None.
  dock      the Dock launcher's "editor", the command that opens a file in
            it, and its "workspace" file, from the root. No editor: the
            click opens none. No workspace: the project's folder.
  shift     a shift this project always takes, and flip then refuses.
            None: the state file's, or 0.

A shift moves every port of this project clear of another project's, so
both run on one Mac: 20000 puts 1100 on 21100, and session 05's 7205 on
27205. Unfixed, it sits in .claude/state/ports/shift.json, outside git,
since it follows what I work on, and /00-sessions-dashboard flip writes
it. Band 00's ports move with it, wherever its command and its match
name one. None: 0.

Unshifted, one project runs at a time on a Mac: two would share 1100, and
each registry would hand one number, so one port, to two sessions. A
dashboard answers ASKED with identity(), and refusal() reads another's.

Two facts no file names sit here too, each read by two tools: TRAILER,
the line /8-ship's commit and the export's close on, and STACK, the
stack's folder, which coder-check counts and behaviour-doctor leaves out.

  project.py [ROOT]    print the facts of the project at ROOT, this one by default

Standard library only. The memory guard imports it on macOS's own Python,
3.9, so nothing here needs a newer one.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Where a dashboard says which project it serves.
ASKED = "/project"
# The shift's file, under the project at a root.
SHIFT_FILE = os.path.join(".claude", "state", "ports", "shift.json")
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
STACK = "knowledge/0010-playbook/0015-coding/the-stack/"


def read(root: str) -> dict:
    """What the file of the project at ROOT holds. Nothing when it cannot be read."""
    try:
        with open(os.path.join(root, ".claude", "project.json")) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return got if isinstance(got, dict) else {}


def part(d: dict, key: str) -> dict:
    return d[key] if isinstance(d.get(key), dict) else {}


def text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def digits(value) -> list:
    """The digits a list names, 1 to 9. 0 is never a folder, nor a role."""
    return [d for d in value if type(d) is int and 1 <= d <= 9] if isinstance(value, list) else []


def words(value) -> list:
    """A command as its words: a list as it stands, one string as one word."""
    value = [value] if isinstance(value, str) else value
    return [w for w in value if isinstance(w, str) and w] if isinstance(value, list) else []


def servers(value) -> list:
    """Band 00 in the file's order: [(group, [(port, name), ...]), ...]."""
    groups = value.items() if isinstance(value, dict) else []
    return [(group, [(int(port), text(name) or port) for port, name in held.items() if port.isdigit()])
            for group, held in groups if isinstance(held, dict)]


def fixed(root: str) -> int:
    """The shift project.json fixes for the project at ROOT. 0 when it fixes
    none, or one that would push a port past 65535."""
    got = read(root).get("shift")
    return got if type(got) is int and 0 < got <= 50000 else 0


def shift(root: str) -> int:
    """The shift every port of the project at ROOT takes. The one project.json
    fixes, else the state file's. 0 with none, or one that would push a port
    past 65535."""
    by = fixed(root)
    if by:
        return by
    try:
        with open(os.path.join(root, SHIFT_FILE)) as f:
            got = json.load(f).get("shift")
    except (OSError, ValueError, AttributeError):
        return 0
    return got if type(got) is int and 0 <= got <= 50000 else 0


def moved(command: str, band: list, by: int) -> str:
    """A command with each of band 00's ports moved by BY, whole numbers only:
    --port 1400 becomes --port 21400, and 31400 stays."""
    named = sorted({str(p) for _, held in band for p, _ in held}, key=len, reverse=True)
    if not by or not named:
        return command
    return re.sub(r"(?<!\d)(%s)(?!\d)" % "|".join(named), lambda m: str(int(m.group(1)) + by), command)


def database(d: dict) -> dict:
    """The database's port, name and pg_isready. Nothing without a port."""
    if type(d.get("port")) is not int:
        return {}
    return {"port": d["port"], "name": text(d.get("name")) or "Database", "pg_isready": text(d.get("pg_isready"))}


def facts(root: str) -> dict:
    """Every fact of the project at ROOT, each fallback in place."""
    got = read(root)
    ports, band, dock = part(got, "ports"), part(got, "band"), part(got, "dock")
    start, docs, workspace = text(band.get("command")), text(got.get("docs")).rstrip("/"), text(dock.get("workspace"))
    by, held = shift(root), servers(band.get("servers"))
    return {
        "name": text(got.get("name")) or os.path.basename(os.path.abspath(root)),
        "branch": text(got.get("branch")) or "work",
        "folders": digits(ports.get("folders")),
        "roles": digits(ports["roles"]) if "roles" in ports else [1, 2],
        "sites": {int(k): digits(v) for k, v in part(ports, "sites").items() if k.isdigit()},
        "shift": by,
        "fixed": fixed(root),
        "band": [(group, [(p + by, n) for p, n in each]) for group, each in held],
        "command": moved(start, held, by),
        "match": moved(text(band.get("match")) or start, held, by),
        "database": database(part(got, "database")),
        "docs": docs + "/" if docs else "",
        "editor": words(dock.get("editor")),
        "workspace": os.path.join(root, workspace) if workspace else root,
    }


FACTS = facts(ROOT)
NAME, BRANCH = FACTS["name"], FACTS["branch"]
FOLDERS, ROLES, SITES, SHIFT = FACTS["folders"], FACTS["roles"], FACTS["sites"], FACTS["shift"]
FIXED = FACTS["fixed"]
BAND, COMMAND, MATCH = FACTS["band"], FACTS["command"], FACTS["match"]
DATABASE, DOCS = FACTS["database"], FACTS["docs"]
EDITOR, WORKSPACE = FACTS["editor"], FACTS["workspace"]


def identity() -> str:
    """What a dashboard answers at ASKED: the project it serves, by name and folder."""
    return json.dumps({"name": NAME, "root": ROOT})


def refusal(port: int) -> str:
    """One sentence when another project's dashboard answers on PORT. Empty
    when none does, or this project's does. Two folders are two projects,
    whatever their names. A server naming no project is never refused: the
    sentence names the project, so only a named one is refused."""
    import urllib.request
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{port}{ASKED}", timeout=3) as r:
            got = json.loads(r.read().decode())
        name, root = str(got["name"]), str(got["root"])
    except (OSError, ValueError, KeyError, TypeError):
        return ""
    if os.path.realpath(root) == os.path.realpath(ROOT):
        return ""
    return (f"Refused: {name} already answers on {port}, from {root}. One project runs at a time: "
            "type /00-sessions-dashboard stop there first.")


if __name__ == "__main__":
    print(json.dumps(facts(os.path.abspath(sys.argv[1]) if sys.argv[1:] else ROOT), indent=1))
