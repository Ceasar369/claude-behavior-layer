"""prototypes.py — where the prototypes app lives, what may name a subject,
which subject a session holds, where each subject shows, how a subject
ends, and how a variation's looks split into groups.

The app is code/prototypes/, one Vite app, and band 00 serves it on 1400
for every session. A project without it says so in one line, NO_APP,
until its first prototype mission builds one.

A subject is one folder there, and its routes one
folder under src/routes/. Its name is kebab-case, and never one of the
app's own folders.

A session's current subject is one line in its own folder, in the file
`prototype`. One session holds a subject at a time. A claim, a renumber
and a stop take the file with the folder, so none of them needs a word
from here. Removing the subject takes every session's `prototype` and
`building` file that names it.

Each hold stamps the subject with its session's number and title, in
`session.json` beside its generations, so both outlive the session's
folder.

While a session's process runs and its subject is not locked in, 1100
frames the subject in its hub, from 1400. Every other subject shows on
1400's library, at /: each winner under Locked, the rest under Saved.

A lock-in marks the one generation it keeps. Its one variation is the
winner. The session that builds it takes it down once its real version is
live, and its stop takes down any it forgot, unless another session still
builds it. The session that made it never does. A session coding a
winner, whoever made it, marks it built: prototype.py build writes one
line per winner in its own folder, the file `building`, which goes with
the folder too. A session whose mission names the winner's file builds it
with no line.

The prototype tools, hooks and 1100's views need these. They live here,
once.

Imported, never run.
"""

import glob
import json
import os
import re
import shutil

import plans
import project
import registry

APP = os.path.join(registry.ROOT, "code", "prototypes")
ROUTES = os.path.join(APP, "src", "routes")
# What the family says, in one line, in a project without the app.
NO_APP = "This project has no prototypes app in code/prototypes/. Its first prototype mission builds one."
SUBJECT = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

# The one app, band 00's, with the shift in force: 21400 while it holds.
PORT = 1400 + project.SHIFT

# Folders of the app itself, which a subject's name can never take.
TAKEN = {"src", "node_modules", "public"}

# The key a lock-in writes into the one generation it keeps.
LOCKED = "locked"

# The session that last held a subject, beside its generations.
STAMP = "session.json"

GEN = re.compile(r"g(\d+)\.json")


def generations(folder: str) -> list:
    """Every generation in a folder, as (number, path), oldest first."""
    found = []
    for path in glob.glob(os.path.join(folder, "g*.json")):
        if m := GEN.fullmatch(os.path.basename(path)):
            found.append((int(m.group(1)), path))
    return sorted(found)


def subject_file(nn: str) -> str:
    return os.path.join(registry.folder(nn), registry.PROTOTYPE)


def subject_of(nn: str) -> str:
    """The subject session NN holds, or nothing."""
    try:
        with open(subject_file(nn)) as f:
            return f.read().strip()
    except OSError:
        return ""


def holders(subject: str) -> list:
    """Every session holding this subject, lowest number first."""
    return [nn for nn in sorted(registry.listing(registry.WORK))
            if re.fullmatch(r"\d{2}", nn) and subject_of(nn) == subject]


def stamped(subject: str) -> tuple:
    """The session that last held this subject, as (number, title), or two blanks."""
    try:
        with open(os.path.join(APP, subject, STAMP)) as f:
            d = json.load(f)
        return d.get("number", ""), d.get("title", "")
    except (OSError, ValueError, AttributeError):
        return "", ""


def stamp(nn: str, subject: str) -> None:
    """Stamp session NN's number and title on this subject. Written only
    when it changes."""
    title = (registry.entries().get(nn) or {}).get("title", nn)
    if stamped(subject) == (nn, title) or not os.path.isdir(os.path.join(APP, subject)):
        return
    with open(os.path.join(APP, subject, STAMP), "w") as f:
        json.dump({"number": nn, "title": title}, f, indent=2, ensure_ascii=False)
        f.write("\n")


def hold(nn: str, subject: str) -> None:
    """Session NN now holds this subject, and no other session does. The
    hold is written only when it changes, so 1100 hears a new subject,
    never a rewrite."""
    if not os.path.isdir(registry.folder(nn)):
        return
    for other in holders(subject):
        if other != nn:
            try:
                os.remove(subject_file(other))
            except OSError:
                pass
    stamp(nn, subject)
    if subject_of(nn) != subject:
        with open(subject_file(nn), "w") as f:
            f.write(subject + "\n")


def release(nn: str) -> str:
    """Session NN lets go of its subject, which stays whole. The subject,
    or nothing."""
    subject = subject_of(nn)
    if subject:
        try:
            os.remove(subject_file(nn))
        except OSError:
            pass
    return subject


def on_hub(nn: str, rec) -> str:
    """The subject session NN's hub frames, or nothing: one it holds, not
    locked in, while its process runs. `rec` is Claude Code's record for
    it, None once its process is gone."""
    subject = subject_of(nn)
    if not rec or not subject or not os.path.isdir(os.path.join(APP, subject)) or winner(subject):
        return ""
    return subject


def shelf() -> tuple:
    """1400's library, as (locked, saved), each newest first.

    Locked holds every winner. Saved holds every other subject no hub
    frames. Each entry names its subject, its session's number and title,
    its newest generation, that generation's count of variations, a
    winner's pick, and the variation that stands for it, with its route:
    the winner, else the newest generation's first. A subject names the
    session its stamp names, else the one holding it, else none."""
    held, live = registry.entries(), registry.claude_records()
    holding, framed = {}, set()
    for nn, mine in held.items():
        if subject := subject_of(nn):
            holding.setdefault(subject, nn)
            if on_hub(nn, live.get(mine.get("session_id"))):
                framed.add(subject)
    locked, saved = [], []
    for home in glob.glob(os.path.join(APP, "*", "")):
        subject = os.path.basename(os.path.dirname(home))
        gens = generations(home)
        if subject in TAKEN or not gens or subject in framed:
            continue
        try:
            with open(gens[-1][1]) as f:
                newest = json.load(f)
        except (OSError, ValueError):
            continue
        number, title = stamped(subject)
        if not number and subject in holding:
            number = holding[subject]
            title = held[number].get("title", number)
        pick = winner(subject)
        first = (newest.get("variations") or [{}])[0]
        g = newest.get("generation", gens[-1][0])
        entry = {"subject": subject, "number": number, "title": title, "generation": g,
                 "variations": len(newest.get("variations") or []), "pick": pick,
                 "shown": f"g{g}/{first.get('id', '')}",
                 "route": first.get("route", "") if first.get("real", True) else "",
                 "at": os.path.getmtime(gens[-1][1])}
        (locked if pick else saved).append(entry)
    newest_first = lambda xs: sorted(xs, key=lambda e: -e["at"])
    return newest_first(locked), newest_first(saved)


def building(nn: str) -> list:
    """Every subject whose winner session NN builds, one per line."""
    try:
        with open(os.path.join(registry.folder(nn), registry.BUILDING)) as f:
            return [line.strip() for line in f if line.strip()]
    except OSError:
        return []


def build(nn: str, subject: str) -> None:
    """Session NN now builds this subject's winner too."""
    if subject in building(nn) or not os.path.isdir(registry.folder(nn)):
        return
    with open(os.path.join(registry.folder(nn), registry.BUILDING), "a") as f:
        f.write(subject + "\n")


def builds(nn: str, subject: str) -> bool:
    """Whether session NN builds this subject's winner: its `building`
    names the subject, or its mission names the winner's file."""
    pick = winner(subject)
    if not nn or not pick:
        return False
    if subject in building(nn):
        return True
    owned = plans.owners(registry.entries())
    if nn not in owned:
        return False
    g, v = pick.split("/")
    path = os.path.relpath(os.path.join(ROUTES, subject, g, f"{v}.tsx"), registry.ROOT)
    m = plans.mission(*owned[nn])
    if not m.get("file"):
        return False
    try:
        with open(os.path.join(registry.ROOT, m["file"])) as f:
            return path in f.read()
    except OSError:
        return False


def built(nn: str) -> list:
    """Remove every winner session NN builds, as it stops, unless another
    session still builds it. The subjects removed."""
    gone = []
    for home in glob.glob(os.path.join(APP, "*", "")):
        subject = os.path.basename(os.path.dirname(home))
        if subject in TAKEN or not builds(nn, subject):
            continue
        if any(builds(other, subject) for other in registry.entries() if other != nn):
            continue
        remove(subject)
        gone.append(subject)
    return gone


def winner(subject: str) -> str:
    """The variation a lock-in kept, as g2/v3, or nothing.

    Only the newest generation decides: a generation built on a winner, as
    one restored from git to rework, reopens it, until a lock-in again. It
    stays until the session building it removes it, or the last one
    building it stops."""
    gens = generations(os.path.join(APP, subject))
    if not gens:
        return ""
    path = gens[-1][1]
    try:
        with open(path) as f:
            gen = json.load(f)
    except (OSError, ValueError):
        return ""
    if gen.get(LOCKED) and gen.get("variations"):
        return f"{os.path.basename(path)[:-5]}/{gen['variations'][0]['id']}"
    return ""


def looks(variation: dict) -> tuple:
    """A variation's looks, as (groups, shown). Looks in one group compete, and
    I pick one. A look with no group is only shown. Groups keep the order they
    first appear in. A variation naming none has neither. An entry with no
    number is no look, and nothing stops for it."""
    groups, shown = {}, []
    for look in variation.get("looks") or []:
        if not isinstance(look, dict) or look.get("n") in (None, ""):
            continue
        if look.get("group"):
            groups.setdefault(str(look["group"]), []).append(look)
        else:
            shown.append(look)
    return groups, shown


def remove(subject: str) -> str:
    """Delete one subject whole: its generations and its routes, and every
    session's hold and build line on it."""
    gone = [d for d in (os.path.join(APP, subject), os.path.join(ROUTES, subject))
            if os.path.isdir(d)]
    for d in gone:
        shutil.rmtree(d)
    for nn in registry.listing(registry.WORK):
        if not re.fullmatch(r"\d{2}", nn):
            continue
        if subject_of(nn) == subject:
            try:
                os.remove(subject_file(nn))
            except OSError:
                pass
        if subject in (left := building(nn)):
            # The other winners it builds keep their lines.
            path = os.path.join(registry.folder(nn), registry.BUILDING)
            rest = [s for s in left if s != subject]
            try:
                if rest:
                    registry.write_whole(path, "".join(s + "\n" for s in rest))
                else:
                    os.remove(path)
            except OSError:
                pass
    return f"{subject} removed." if gone else f"{subject} holds nothing."
