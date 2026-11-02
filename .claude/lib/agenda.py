"""agenda.py — my agenda's folder: read, checked and written.

The agenda is mine alone: what I want worked on or set aside, and what
waits on what. Its folder, .claude/state/agenda/, holds README.md, which
says what the agenda is and is not, and one file per item. A folder with
no README takes the layer's, tools/agenda-readme.md, at its first read.
One already there is never overwritten.

Its topics, TOPICS, in their order, are rectangles down the chart's first
column, each wearing its own colour. They are headings, never items, and
never come down. A project names them in the folder's topics.json, each
with its colour, and the screens an item may name beside them:

    {"topics": [{"name": "Web app", "colour": "#2dd4bf"},
                {"name": "Behaviour", "colour": "#94a3b8"}],
     "screens": ["web app", "demo"]}

Named nowhere, Behaviour stands in alone, and no item names a screen. A
topics.json that cannot be read gives the same, and the check says why.
Both are read once, from the project's own folder, when this is imported.

A project may split its agenda into phases, PHASES, named there too, in
order, as "phases": ["1", "2"]. Every item then names one on a "Phase"
line under its "Topics" line, and no wait joins two phases: a write
refuses one, and the check names any. The page draws each phase as its
own chart, under its heading, HEADINGS, as "headings": {"1": "Phase 1:
Launch"}, or "Phase 1" when none is named. Named nowhere, the agenda has
no phase, and no item names one.

Every item names its topics, one or more of them, on a "Topics" line
under its "Waits on" line:

    Read README.md first. This item is part of my agenda, and mine alone.

    # Reports kept after a crash

    Waits on: panes-closed-on-crash
    Topics: Behaviour

    What: Fix, small: keep a session's report when its pane crashes.
    Why: until then, the handover's "Nothing you said is lost." is not true.
    Done when: a crashed pane's report reaches its successor, as the handover says.
    Sources: .claude/skills/session-report/SKILL.md

"Waits on" lists file names, so a name holding a comma never breaks it.
An item's column is one past the furthest item it waits on.

Every line keeps its meaning: the items most on the left are dealt with
first. An item waiting on nothing comes out of each of its topics'
rectangles; one waiting on other items comes out of them alone. An item
wears no colour of its own. The page draws the colours.

Its note runs What, Why, Done when, Mine and Sources, each on one line,
once at most, 60 words in all. Only What is needed. A write refuses a
note breaking that shape. A note written before the shape opens with no
What line, and stands until a session next writes it.

Its What opens with its action and its size, as "Fix, small: …". The
action is Look at, Verify, Fix, Do or Decide; the size small, medium or
large. After its size, an item whose result shows on a screen names it,
one of SCREENS, as "Fix, small, web app: …". A write refuses any other
opening.

Every write takes the folder's lock, writes a temporary file, then swaps
it in, so 1100 never reads half a file. A link that would close a loop is
refused, with the loop's whole path.

An item coming down hands what waited on it to what it waited on, so no
wait is lost.

Every tool reading the agenda reads it here, once.

Imported, never run.
"""

import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import unicodedata

import registry

FOLDER = os.path.join(registry.ROOT, ".claude", "state", "agenda")
README = "README.md"
# The README a folder with none takes, shipped with the layer.
SHIPPED = os.path.join(registry.ROOT, ".claude", "tools", "agenda-readme.md")
# Where a project names its own topics, screens and phases, beside its README.
TOPICS_FILE = "topics.json"
# Named nowhere, one topic stands in, until the project names its own.
STAND_IN = (("Behaviour", "#94a3b8"),)
POINTER = "Read README.md first. This item is part of my agenda, and mine alone."
# Names no item's file can take.
RESERVED = {"readme"}
LONGEST = 80
# A note's lines, in order. Only What is needed.
LINES = ("What", "Why", "Done when", "Mine", "Sources")
# At most this many words in one note, every word counted.
WORDS = 60
# A What opens with one action and one size, then its object: "Fix, small: …".
ACTIONS = ("Look at", "Verify", "Fix", "Do", "Decide")
SIZES = ("small", "medium", "large")
# A topic's colour, as the page mixes it.
COLOUR = re.compile(r"#[0-9a-fA-F]{6}")
# The lines an item's file holds between its title and its note. No item
# wears a colour, but a Colour line is read, so a check names it.
HEAD = ("Waits on", "Topics", "Phase", "Colour")


class Refused(Exception):
    """A write refused, with the sentence saying why."""


# ---- the project's topics ---------------------------------------------------------------

def project(folder: str = FOLDER) -> tuple:
    """The topics a project names in `folder`'s topics.json, each as (name,
    colour), in order, the screens an item may name, its phases, and their
    headings, as (topics, screens, phases, headings, why). Named nowhere,
    the stand-in, no screen, no phase and no heading, and why is "". A file
    that cannot be read gives the same, and why says so."""
    path = os.path.join(folder, TOPICS_FILE)
    if not os.path.exists(path):
        return STAND_IN, (), (), {}, ""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        topics = tuple((t["name"].strip(), t["colour"]) for t in d["topics"])
        screens = tuple(s.strip() for s in d.get("screens", []))
        phases = tuple(p.strip() for p in d.get("phases", []))
        headings = {p.strip(): h.strip() for p, h in d.get("headings", {}).items()}
    except (OSError, ValueError, AttributeError, KeyError, TypeError):
        topics, screens, phases, headings = (), (), (), {}
    if (topics and all(n and isinstance(c, str) and COLOUR.fullmatch(c) for n, c in topics) and all(screens)
            and all(phases) and len(set(phases)) == len(phases) and all(headings.values())):
        return topics, screens, phases, headings, ""
    return STAND_IN, (), (), {}, (f"{TOPICS_FILE} cannot be read: it lists one topic at least, each with a name "
                                  "and a colour as #94a3b8, then its screens' names, then its phases', each once, "
                                  "then each phase's heading.")


# The project's topics, each with its rectangle's colour; the screens an
# item's result may show on, named after its size: "Fix, small, web app: …";
# its phases, in order, and each one's heading; and why its topics.json
# could not be read, or "".
TOPICS, SCREENS, PHASES, HEADINGS, UNREAD = project()
NAMES = tuple(name for name, _ in TOPICS)
OPENING = re.compile(rf"({'|'.join(ACTIONS)}), ({'|'.join(SIZES)})"
                     + (rf"(?:, ({'|'.join(map(re.escape, SCREENS))}))?" if SCREENS else "") + r": \S")


# ---- reading ----------------------------------------------------------------------------

def slug(name: str) -> str:
    """The file name an item's name takes: plain letters and digits,
    lowercase, dashes between, 80 at most."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")[:LONGEST].rstrip("-")


def parse(text: str) -> dict:
    """One item's file, as {"title", "after", "topics", "phase", "colour",
    "note", "pointed"}: its topics as its Topics line writes them, its
    phase "" when it names none. Raises ValueError when it holds no title
    or no "Waits on" line."""
    lines = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    pointed = bool(lines) and lines[0].strip() == POINTER
    at = next((i for i, line in enumerate(lines) if line.startswith("# ")), None)
    if at is None:
        raise ValueError("no title")
    title = lines[at][2:].strip()
    after, topics, phase, colour, i = None, [], "", "", at + 1
    while i < len(lines):
        line = lines[i].strip()
        key, colon, value = line.partition(":")
        if line and not (colon and key in HEAD):
            break
        if key == "Waits on":
            value = value.strip()
            after = [] if value in ("", "nothing") else [v.strip() for v in value.split(",") if v.strip()]
        elif key == "Topics":
            topics = [v.strip() for v in value.split(",") if v.strip()]
        elif key == "Phase":
            phase = value.strip()
        elif key == "Colour":
            colour = value.strip().lower()
        i += 1
    if not title or after is None:
        raise ValueError("no title" if not title else "no Waits on line")
    note = "\n".join(lines[i:]).strip()
    return {"title": title, "after": after, "topics": topics, "phase": phase, "colour": colour, "note": note,
            "pointed": pointed}


def note_lines(note: str) -> list:
    """A note's lines, in order, as (name, text). The name is What, Why,
    Done when, Mine or Sources when the line opens with it and a colon;
    otherwise it is "", and the text is the whole line."""
    out = []
    for row in note.strip().splitlines():
        row = row.strip()
        name, colon, text = row.partition(":")
        out.append((name, text.strip()) if colon and name in LINES else ("", row))
    return out


def shape(note: str) -> str:
    """The first way a note breaks its shape, as a clause, or "" when it
    keeps it: What first, then Why, Done when, Mine and Sources, each on
    one line, once at most, holding words, 60 words in all."""
    rows = note_lines(note)
    if not rows or rows[0][0] != "What":
        return "it opens with no What line"
    at = -1
    for name, text in rows:
        if not name:
            return f"{text[:40]!r} is no line a note holds" if text else "it holds a blank line"
        if LINES.index(name) <= at:
            return f"its {name} line comes " + ("twice" if LINES.index(name) == at else "out of order")
        if not text:
            return f"its {name} line holds nothing"
        at = LINES.index(name)
    if (n := len(note.split())) > WORDS:
        return f"it holds {n} words, past {WORDS}"
    return ""


def action(note: str) -> str:
    """The action a note's What opens with, or "" when it opens with none."""
    rows = note_lines(note)
    m = OPENING.match(rows[0][1]) if rows and rows[0][0] == "What" else None
    return m.group(1) if m else ""


def start(folder: str) -> None:
    """A folder's first read: the layer's README, copied in when none is
    there. One already there is never overwritten: the copy is linked in
    whole, and any README that beat it wins."""
    path = os.path.join(folder, README)
    if os.path.lexists(path):
        return
    os.makedirs(folder, exist_ok=True)
    tmp = os.path.join(folder, f".{README}.{os.getpid()}.tmp")
    shutil.copyfile(SHIPPED, tmp)
    try:
        os.link(tmp, path)
    except FileExistsError:
        pass
    finally:
        os.remove(tmp)


def read(folder: str = FOLDER) -> tuple:
    """Every item, by its file name, and the files that could not be read.
    The README and hidden files are no items. A folder with no README
    first takes the layer's."""
    start(folder)
    items, broken = {}, []
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return items, broken
    for name in names:
        if name.startswith(".") or not name.endswith(".md") or name == README:
            continue
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                items[name[:-3]] = parse(f.read())
        except (OSError, UnicodeDecodeError, ValueError):
            broken.append(name)
    return items, broken


def key(folder: str = FOLDER) -> str:
    """What the folder holds now, as a short key: every file's name, size
    and time. Any write moves it."""
    seen = []
    try:
        for name in sorted(os.listdir(folder)):
            if not name.startswith("."):
                s = os.stat(os.path.join(folder, name))
                seen.append((name, s.st_size, s.st_mtime_ns))
    except OSError:
        pass
    return hashlib.sha1(repr(seen).encode()).hexdigest()[:12]


def topic(word: str) -> str:
    """The topic a word names, as TOPICS write it, or "" when it names
    none: "web app" and "web-app" both name Web app."""
    return next((name for name in NAMES if slug(name) == slug(word)), "")


def placed(it: dict) -> list:
    """An item's topics among TOPICS, in their order."""
    mine = {topic(t) for t in it["topics"]}
    return [name for name in NAMES if name in mine]


def world(folder: str = FOLDER) -> dict:
    """The agenda's items as the page draws them, each under its topics,
    in its phase."""
    items, broken = read(folder)
    return {"items": [{"id": i, "title": it["title"], "after": it["after"], "topics": placed(it),
                       "phase": it["phase"], "note": it["note"]} for i, it in items.items()],
            "broken": broken}


def apart(one: dict, two: dict) -> bool:
    """Whether two items sit in two phases, each naming its own."""
    return bool(one["phase"] and two["phase"] and one["phase"] != two["phase"])


# ---- the drawing's rules ----------------------------------------------------------------

def loops(items: dict) -> set:
    """Each link a hand-made loop holds, as "parent>child", met as the
    page meets it: items walked in file-name order, links in file order.
    The page leaves these links out, and so does columns()."""
    found, state = set(), {}

    def walk(i: str) -> None:
        state[i] = "walking"
        for p in items[i]["after"]:
            if p not in items:
                continue
            if state.get(p) == "walking":
                found.add(f"{p}>{i}")
            elif p not in state:
                walk(p)
        state[i] = "done"

    for i in sorted(items):
        if i not in state:
            walk(i)
    return found


def parents(items: dict, i: str, skip: set) -> list:
    return [p for p in items[i]["after"] if p in items and f"{p}>{i}" not in skip]


def columns(items: dict) -> dict:
    """Each item's column: one past the furthest item it waits on."""
    skip, out = loops(items), {}

    def column(i: str) -> int:
        if i not in out:
            out[i] = 1 + max([0] + [column(p) for p in parents(items, i, skip)])
        return out[i]

    for i in items:
        column(i)
    return out


def loop_path(items: dict, child: str, parent: str) -> list:
    """The items a link from `parent` to `child` would close a loop through,
    from `child` back to itself, or [] when it closes none."""
    seen = set()

    def back(i: str) -> list:
        if i == child:
            return [i]
        if i in seen or i not in items:
            return []
        seen.add(i)
        for p in items[i]["after"]:
            path = back(p)
            if path:
                return path + [i]
        return []

    path = back(parent)
    return path + [child] if path else []


def waiting(items: dict, i: str) -> list:
    """The items waiting on `i`."""
    return [c for c, it in items.items() if i in it["after"]]


def moved(before: dict, after: dict, items: dict) -> list:
    """Each item whose column a write changed, as "Billing: column 4 → 5"."""
    return [f"{items[i]['title']}: column {before[i]} → {after[i]}"
            for i in sorted(after, key=lambda i: (after[i], i)) if i in before and before[i] != after[i]]


def problems(folder: str = FOLDER) -> list:
    """What a hand edit broke: a topics.json that cannot be read, an
    unreadable file, a file with no pointer line, a note opening with What
    that breaks its shape, a link to no item, a loop, an item under no
    topic or under one outside TOPICS, an item in no phase or one outside
    PHASES, a wait joining two phases, and a colour, which no item wears."""
    items, broken = read(folder)
    out = ([UNREAD] if UNREAD else []) + [f"{name} cannot be read." for name in broken]
    for i, it in sorted(items.items()):
        if not it["pointed"]:
            out.append(f"{i}.md does not open with the pointer line.")
        if it["note"].startswith("What:") and (why := shape(it["note"])):
            out.append(f"{i}.md's note breaks its shape: {why}.")
        for p in it["after"]:
            if p not in items:
                out.append(f"{i}.md waits on {p}, which is no item.")
            elif apart(it, items[p]):
                out.append(f"{i}.md, in phase {it['phase']}, waits on {p}.md, in phase {items[p]['phase']}.")
        if PHASES and not it["phase"]:
            out.append(f"{i}.md names no phase.")
        elif it["phase"] and it["phase"] not in PHASES:
            out.append(f"{i}.md names phase {it['phase']}, which is none of the phases"
                       + (f": {', '.join(PHASES)}." if PHASES else "."))
        if not it["topics"]:
            out.append(f"{i}.md names no topic.")
        for t in it["topics"]:
            if not topic(t):
                out.append(f"{i}.md names {t}, which is none of the topics.")
        if it["colour"]:
            out.append(f"{i}.md wears a colour, but an item wears none of its own.")
    for link in sorted(loops(items)):
        p, _, c = link.partition(">")
        out.append(f"{c}.md and {p}.md close a loop.")
    return out


# ---- writing ----------------------------------------------------------------------------

@contextlib.contextmanager
def locked(folder: str):
    """The folder's lock, held while one write reads and writes."""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, ".lock"), "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def text_of(it: dict) -> str:
    head = [POINTER, "", f"# {it['title']}", "", f"Waits on: {', '.join(it['after']) or 'nothing'}",
            f"Topics: {', '.join(it['topics'])}"] + ([f"Phase: {it['phase']}"] if it["phase"] else [])
    return "\n".join(head) + "\n" + (f"\n{it['note'].strip()}\n" if it["note"].strip() else "")


def _write(folder: str, i: str, it: dict) -> None:
    registry.write_whole(os.path.join(folder, f"{i}.md"), text_of(it))


def find(items: dict, name: str) -> str:
    """An item by its file name or its name, or Refused."""
    if name in items:
        return name
    if (s := slug(name)) in items:
        return s
    hit = [i for i, it in items.items() if it["title"].lower() == name.strip().lower()]
    if len(hit) == 1:
        return hit[0]
    raise Refused(f"No item is named {name!r}.")


def _free(items: dict, name: str, but: str = "") -> str:
    i = slug(name)
    if not name.strip() or not i:
        raise Refused("An item needs a name with a letter or a digit in it.")
    if i in RESERVED:
        raise Refused(f"{name!r} would be named {i}, which the folder keeps for itself.")
    if i in items and i != but:
        raise Refused(f"{name!r} would be named {i}, and {items[i]['title']!r} already is.")
    return i


def listed(words) -> str:
    """Words as a sentence lists them: "a, b or c"."""
    *rest, last = words
    return f"{', '.join(rest)} or {last}" if rest else last


def _shaped(note: str) -> str:
    """The note, each line trimmed, or Refused when it breaks its shape or
    its What opens with no action and size."""
    if why := shape(note):
        raise Refused(f"The note breaks the README's item shape: {why}.")
    if not action(note):
        raise Refused("The note's What opens with no action and size, as \"What: Fix, small: …\". "
                      "The action is Look at, Verify, Fix, Do or Decide; the size small, medium or large."
                      + (f" A screen may follow the size: {listed(SCREENS)}." if SCREENS else ""))
    return "\n".join(row.strip() for row in note.strip().splitlines())


def topics_of(words) -> list:
    """The topics named, in TOPICS' order, or Refused: none named, or one
    outside them. A word may hold several, between commas."""
    named = [w.strip() for word in words for w in word.split(",") if w.strip()]
    if not named:
        raise Refused(f"An item sits under one topic at least. The topics: {', '.join(NAMES)}.")
    for word in named:
        if not topic(word):
            raise Refused(f"{word!r} is none of the topics: {', '.join(NAMES)}.")
    return placed({"topics": named})


def phase_of(word: str) -> str:
    """The phase a word names, or Refused: none named while the project
    names phases, or one outside them. With no phases, ""."""
    word = (word or "").strip()
    if not PHASES:
        if word:
            raise Refused("This agenda has no phases.")
        return ""
    if word not in PHASES:
        raise Refused(f"An item sits in one phase: {listed(PHASES)}.")
    return word


def _across(child: dict, parent: dict) -> None:
    """Refused when the wait would join two phases."""
    if apart(child, parent):
        raise Refused(f"{child['title']}, in phase {child['phase']}, cannot wait on {parent['title']}, in phase "
                      f"{parent['phase']}. A phase's items wait only on its own.")


def _waits(items: dict, ps: list) -> str:
    return "waiting on " + ", ".join(items[p]["title"] for p in ps) + "." if ps else "waiting on nothing."


def add(folder: str, name: str, topics, after: list = (), note: str = "", phase: str = "") -> list:
    """A new item under `topics`, in `phase`, waiting on `after`, its note
    holding its What at least."""
    with locked(folder):
        items, _ = read(folder)
        i = _free(items, name)
        tops = topics_of(topics)
        note = _shaped(note)
        it = {"title": name.strip(), "after": [], "topics": tops, "phase": phase_of(phase), "colour": "",
              "note": note, "pointed": True}
        for p in after:
            p = find(items, p)
            _across(it, items[p])
            if p not in it["after"]:
                it["after"].append(p)
        _write(folder, i, it)
        items[i] = it
        return [f"Added {it['title']} as {i}.md, under {', '.join(tops)}"
                + (f", in phase {it['phase']}" if it["phase"] else "") + f", {_waits(items, it['after'])}"]


def set_topics(folder: str, item: str, topics) -> list:
    """`item`'s topics, replaced by `topics`."""
    with locked(folder):
        items, _ = read(folder)
        i = find(items, item)
        tops = topics_of(topics)
        if tops == items[i]["topics"]:
            raise Refused(f"{items[i]['title']} already sits under {', '.join(tops)}.")
        items[i]["topics"] = tops
        _write(folder, i, items[i])
        return [f"{items[i]['title']} now sits under {', '.join(tops)}."]


def link(folder: str, item: str, parent: str) -> list:
    """`item` now waits on `parent` too. An item waiting on nothing no longer
    comes out of its rectangles."""
    with locked(folder):
        items, _ = read(folder)
        c, p = find(items, item), find(items, parent)
        if p in items[c]["after"]:
            raise Refused(f"{items[c]['title']} already waits on {items[p]['title']}.")
        _across(items[c], items[p])
        path = loop_path(items, c, p)
        if path:
            raise Refused("That link would close a loop: " + " → ".join(items[x]["title"] for x in path)
                          + ". Propose one item both share, and hang both on it.")
        before = columns(items)
        items[c]["after"].append(p)
        _write(folder, c, items[c])
        return [f"{items[c]['title']} now waits on {items[p]['title']}."] + moved(before, columns(items), items)


def unlink(folder: str, item: str, parent: str) -> list:
    """`item` no longer waits on `parent`. Waiting on nothing, it comes out
    of its topics' rectangles."""
    with locked(folder):
        items, _ = read(folder)
        c, p = find(items, item), find(items, parent)
        if p not in items[c]["after"]:
            raise Refused(f"{items[c]['title']} does not wait on {items[p]['title']}.")
        before = columns(items)
        items[c]["after"].remove(p)
        _write(folder, c, items[c])
        return [f"{items[c]['title']} no longer waits on {items[p]['title']}."] + moved(before, columns(items), items)


def rename(folder: str, item: str, name: str) -> list:
    """`item` takes a new name, and its file the name's. Every item waiting
    on it is rewritten first, the old file deleted last."""
    with locked(folder):
        items, _ = read(folder)
        old = find(items, item)
        new = _free(items, name, but=old)
        was = items[old]["title"]
        items[old]["title"] = name.strip()
        _write(folder, new, items[old])
        if new != old:
            for i, it in items.items():
                if old in it["after"]:
                    it["after"] = [new if p == old else p for p in it["after"]]
                    _write(folder, i, it)
            os.remove(os.path.join(folder, f"{old}.md"))
        return [f"{was} is now {name.strip()}, in {new}.md."]


def set_phase(folder: str, item: str, phase: str) -> list:
    """`item` moves to `phase`. Refused while it waits on, or is waited on
    by, an item in another phase."""
    with locked(folder):
        items, _ = read(folder)
        i = find(items, item)
        to = phase_of(phase)
        if to == items[i]["phase"]:
            raise Refused(f"{items[i]['title']} already sits in phase {to}.")
        moving = {**items[i], "phase": to}
        for p in items[i]["after"]:
            if p in items:
                _across(moving, items[p])
        for c in waiting(items, i):
            _across(items[c], moving)
        items[i] = moving
        _write(folder, i, moving)
        return [f"{moving['title']} now sits in phase {to}."]


def set_note(folder: str, item: str, note: str) -> list:
    """`item`'s note, replaced whole. Refused when it breaks its shape."""
    with locked(folder):
        items, _ = read(folder)
        i = find(items, item)
        items[i]["note"] = _shaped(note)
        _write(folder, i, items[i])
        return [f"{items[i]['title']}'s note is written."]


def down(folder: str, item: str) -> list:
    """`item`, dealt with, comes down with its lines. What waited on it now
    waits on what it waited on, so no wait is lost; one left waiting on
    nothing comes out of its topics' rectangles. What waited on it is
    rewritten first, its file deleted last."""
    with locked(folder):
        items, _ = read(folder)
        i = find(items, item)
        ups = [p for p in items[i]["after"] if p in items]
        before = columns(items)
        freed, handed = [], []
        for c in waiting(items, i):
            it = items[c]
            it["after"] = [p for p in it["after"] if p != i] + [p for p in ups if p not in it["after"]]
            _write(folder, c, it)
            if not it["after"]:
                freed.append(it["title"])
            elif ups:
                handed.append(it["title"])
        title = items.pop(i)["title"]
        os.remove(os.path.join(folder, f"{i}.md"))
        said = [f"{title} came down."]
        if handed:
            said.append(f"Now waiting on {', '.join(items[p]['title'] for p in ups)}: {', '.join(handed)}.")
        if freed:
            said.append("Now waiting on nothing, out of their topics' rectangles: " + ", ".join(freed) + ".")
        return said + moved(before, columns(items), items)
