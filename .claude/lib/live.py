#!/usr/bin/env python3
"""live.py — a page's contract, and the picture 1100 keeps of each open page.

A page on the contract states four things, as a Page: its address, what
it draws, which files move it, and how it takes a press. What no file
carries, as a pane closing, it names as a look. A Table lists every such
page, and 1100's router asks it before any older route.

The table keeps each open page's last picture, and a page's key is the
mark of that picture. A page is drawn again only once a file it names is
written, a look it names reads differently, or CHECK seconds on. Drawn
afresh then, a page found moved with nothing it names written is named
in the log: its contract misses a file. Nothing written, nothing drawn.

A press carries its own id. Sent twice, it acts once, and both are
answered alike. Typing into one session's pane goes one press at a time.

A part of a page that fails says so in its place, part(), and a page
that fails whole says so in the shell, failed(). Every other part and
page draws on.

Every page on the contract shares one script, .claude/pages/scripts/live.js,
which watch() puts first in the page. It asks what moved, puts a changed
picture in place part by part, keeps my unsent words on my device, and
sends each press.

riding() hands serve.run its route, keyof, take and hears, the table
asked first. A page not yet on the contract rides on as it is.

Imported, never run.
"""

import collections
import hashlib
import html
import os
import re
import sys
import threading
import time
import traceback

import page
import serve

# Every script the pages on the contract share or own, one file each:
# lib/page.py's folder. Each style sits beside it, in page.STYLES.
SCRIPTS = page.SCRIPTS
# A picture this many seconds old is drawn afresh and compared, whatever
# was written: the safety net for a file its page forgot to name.
CHECK = 25
# A picture drawn this beat, and this young, is answered as it is, its
# files and looks unread: a page's key and the page itself, asked a moment
# apart, are one draw, however fast its files are written. Every beat
# reads them again, so no write and no look is ever passed over.
YOUNG = 0.2
# A page nobody asked about for this long is forgotten, its picture with it.
FORGOTTEN = 600
# A file a page names is heard for this long after its page was last asked about.
HEARD = 60
# How many presses' answers are kept, for the same press sent again.
PRESSES = 256
# How long the same press, sent again, waits on the first one's answer.
PRESSING = 120
# What a press answers at an address that takes none, when its take
# raised, and when the same press, sent again, outwaited the first.
NO_PRESS = "Nothing at this address takes a press."
FAILED = "This press failed. The log holds the whole error."
STILL = "This press is still running. Nothing more was done."
# What each kind of shared file goes as.
KINDS = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
ASSET = re.compile(r"/pages/([\w-]+\.(?:js|css))")

# Each shared file as first read, and each failure already in the log.
ASSETS: dict = {}
LOGGED: set = set()


def logged(name: str, what: str) -> None:
    """The error being handled, into the server's log, once per name,
    under a dated line saying `what` failed."""
    if len(LOGGED) > 512:
        LOGGED.clear()
    if name not in LOGGED:
        LOGGED.add(name)
        print(f"{serve.stamp()} live: {what} failed", file=sys.stderr)
        traceback.print_exc()


def asset(name: str) -> tuple:
    """One file of .claude/pages/, as (its bytes, their mark), read once per
    process: 1100 serves the scripts it started with, as it runs the
    Python it started with."""
    if name not in ASSETS:
        with open(page.where(name), "rb") as f:
            raw = f.read()
        ASSETS[name] = (raw, hashlib.sha1(raw).hexdigest()[:12])
    return ASSETS[name]


def src(name: str) -> str:
    """Where a page loads one such file from, its mark in the address: a
    changed script is a changed address, so an open page learns that its
    own code changed."""
    return f"/pages/{name}?v={asset(name)[1]}"


def watch(session: str = "") -> str:
    """What opens a page on the contract, first in its body: its watch,
    wearing the mark of the whole draw once page.render fills it in, then
    the shared script, loaded before any script of the page's own.

    `session` is the id of the session the page is about. My unsent words
    there belong to that session, never to its number: a number is used
    again. serve.KEY reads a page's first data-key, so no element before
    this one may carry one."""
    return (f'<div id="watch" data-key="whole" data-session="{html.escape(session)}" hidden></div>\n'
            f'<script src="{src("live.js")}"></script>\n')


def part(what: str, fn, *args) -> str:
    """One part of a page: what `fn` draws, or, when it raises, one line in
    its place saying so, the whole error in the log. `what` names the part
    as that line says it: "The items"."""
    try:
        return fn(*args)
    except Exception as e:
        line = f"{type(e).__name__}: {e}"
        logged(f"{what}: {line}", f"the draw of {what.lower()}")
        return (f'<p class="note">{html.escape(what)} failed to draw: {html.escape(line)}. '
                'The log holds the whole error.</p>')


def failed(line: str) -> str:
    """The page a draw that raised whole answers with, in the shell: it says
    so, shows the error's last line, and still wears its watch, so it draws
    itself again once a file it names is written."""
    return page.render("00-failed", [("", watch() + '<p class="note">This page failed to draw. The log holds '
                                      f'the whole error.</p><pre class="doc">{html.escape(line)}</pre>')], refresh=0)


def mark(path: str):
    """One file's mark: which file it is, its size, and when it was last
    written, or None while it is missing. A folder's moves when a name in
    it is added, removed or renamed. A file swapped whole is another file."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    return st.st_ino, st.st_size, st.st_mtime_ns


class Page:
    """One page's contract.

    `at` is its address, a pattern over the bare path. Each group it
    catches, as a session's number, is handed to everything below. With
    `query`, the address's query follows them, for `draw` and `files`
    alone: a press is posted to the bare address.

    `draw` answers its picture: its HTML, opened by watch(), or bytes and
    their type when it is data. It reads files and answers already in
    hand. It starts no program, and it draws nothing that ticks.

    `files` answers every file and folder whose write can move that
    picture. A file that may come later is named by its folder.

    `looks` are what no file carries. Each answers what it reads now, from
    an answer already in hand, and is asked on every beat.

    `take` is given the posted form after the groups. It answers "" once
    done, one sentence when refused, a serve.Said, or a serve.Typing when
    it types into the session's pane.
    """

    def __init__(self, at: str, draw, files=None, looks=(), take=None, query: bool = False):
        self.at, self.draw, self.files, self.take, self.query = re.compile(at), draw, files, take, query
        self.looks = tuple(looks)

    def marks(self, path: str, args: tuple) -> tuple:
        """What this page's files and looks read as now. A look or a list
        of files that raises reads as its error, and is logged once."""
        try:
            files = tuple((f, mark(f)) for f in (self.files(*args) if self.files else ()))
        except Exception as e:
            logged(f"files {path} {type(e).__name__}", f"the files of {path}")
            files = ((f"{type(e).__name__}: {e}", None),)
        seen = []
        for look in self.looks:
            try:
                seen.append(look())
            except Exception as e:
                logged(f"look {path} {type(e).__name__}", f"a look of {path}")
                seen.append(f"{type(e).__name__}: {e}")
        return files, seen

    def drawn(self, path: str, args: tuple):
        """This page's picture, drawn now. A draw that raises answers failed()."""
        try:
            return self.draw(*args)
        except Exception as e:
            line = f"{type(e).__name__}: {e}"
            logged(f"draw {path} {line}", f"the draw of {path}")
            return failed(line)


class Picture:
    """One open page's last picture: its key, what was drawn, what its
    files and looks read as just before, when it was drawn, in which beat
    of the server's pulse, and when it was last asked about."""
    __slots__ = ("key", "body", "marks", "drawn", "beat", "asked")

    def __init__(self, key: str, body, marks: tuple, now: float, beat: int = 0):
        self.key, self.body, self.marks, self.drawn, self.beat, self.asked = key, body, marks, now, beat, now


class Table:
    """Every page on the contract, and each open one's picture."""

    def __init__(self, pages):
        self.pages = list(pages)
        self.lock = threading.Lock()
        # Each open page's picture, by its whole address.
        self.kept: dict = {}
        # Each press by its id: whether it is answered, and its answer.
        self.pressed: collections.OrderedDict = collections.OrderedDict()
        # One lock per pane typed into, by its session's number.
        self.typing: dict = {}
        # When each page that moved with no file written was last named.
        self.named: dict = {}

    def find(self, path: str):
        """The page at `path` and what its address hands it, or None."""
        bare, _, query = path.partition("?")
        for page in self.pages:
            if m := page.at.fullmatch(bare):
                return page, (*m.groups(), query) if page.query else m.groups()
        return None

    def picture(self, path: str):
        """The picture of the page at `path`, or None when the table holds
        no such page. The one kept is answered while every file and look
        the page names reads as it did, CHECK seconds at most, and, within
        the beat it was drawn in, for its first YOUNG seconds unread.

        The marks are read before the draw, so a write landing during it
        is seen by the next ask."""
        found = self.find(path)
        if found is None:
            return None
        page, args = found
        now, beat, held = time.time(), serve.BEATS[0], self.kept.get(path)
        if held and held.beat == beat and 0 <= now - held.drawn < YOUNG:
            held.asked = now
            return held
        marks = page.marks(path, args)
        if held and held.marks == marks and 0 <= now - held.drawn < CHECK:
            held.asked = now
            return held
        body = page.drawn(path, args)
        got = Picture(serve.worn(body), body, marks, now, beat)
        if held and held.marks == marks and held.key != got.key and now - self.named.get(path, 0) >= 60:
            self.named[path] = now
            print(f"{serve.stamp()} live: {path} moved with no file it names written", file=sys.stderr, flush=True)
        with self.lock:
            self.kept[path] = got
            for old in [p for p, k in self.kept.items() if not 0 <= now - k.asked < FORGOTTEN]:
                del self.kept[old]
        return got

    def route(self, path: str):
        """What `path` answers: a shared file, a page's picture, or None
        when the table holds neither."""
        if m := ASSET.fullmatch(path.partition("?")[0]):
            try:
                return asset(m.group(1))[0], KINDS[os.path.splitext(m.group(1))[1]]
            except OSError:
                return None
        got = self.picture(path)
        return None if got is None else got.body

    def keyof(self, path: str):
        """The key of the page at `path`, or None when the table holds none."""
        got = self.picture(path)
        return None if got is None else got.key

    def hears(self) -> list:
        """Every file named by a page asked about in the last HEARD seconds."""
        now = time.time()
        with self.lock:
            open_now = [k for k in self.kept.values() if 0 <= now - k.asked < HEARD]
        return [f for k in open_now for f, _ in k.marks[0]]

    def take(self, form: dict, path: str):
        """A press at `path`, answered by its page's take, or None when the
        table holds no page there.

        A press naming its id, in `press`, acts once: sent again, it waits
        off the queue for the first one's answer, and answers the same. A
        take that types is handed back with its typing held to one press
        at a time per pane."""
        found = self.find(path)
        if found is None:
            return None
        page, args = found
        if page.take is None:
            return NO_PRESS
        sent = (form.get("press") or [""])[0]
        flight = None
        if sent:
            with self.lock:
                flight = self.pressed.get(sent)
                first = flight is None
                if first:
                    flight = self.pressed[sent] = [threading.Event(), STILL]
                    while len(self.pressed) > PRESSES:
                        self.pressed.popitem(last=False)
            if not first:
                if flight[0].is_set():
                    return flight[1]
                return serve.Typing(lambda: flight[1] if flight[0].wait(PRESSING) else STILL)

        def done(answer):
            if flight:
                flight[1] = answer
                flight[0].set()
            return answer

        try:
            # A press is posted to the bare address: its take gets no query.
            answer = page.take(*(args[:-1] if page.query else args), form)
        except Exception:
            done(FAILED)
            raise
        if not isinstance(answer, serve.Typing):
            return done(answer)
        with self.lock:
            pane = self.typing.setdefault(args[0] if args else path, threading.Lock())
        outside, inside = answer.outside, answer.inside

        def typed():
            with pane:
                try:
                    return outside()
                except Exception:
                    print(f"{serve.stamp()} live: a press at {path} failed", file=sys.stderr)
                    traceback.print_exc()
                    return FAILED

        def after(said):
            try:
                return done(inside(said) if inside else said)
            except Exception:
                done(FAILED)
                raise

        return serve.Typing(typed, after)

    def riding(self, route=None, keyof=None, take=None, hears=None) -> dict:
        """What serve.run takes as route, keyof, take and hears: this table
        asked first, then the older four, for every address it does not
        hold. A page not yet on the contract rides on as it is."""
        def routed(path: str):
            got = self.route(path)
            return got if got is not None else route(path) if route else None

        def keyed(path: str):
            got = self.keyof(path)
            return got if got is not None else keyof(path) if keyof else None

        def took(form: dict, path: str = "/"):
            got = self.take(form, path)
            return got if got is not None else take(form, path) if take else NO_PRESS

        def heard() -> list:
            return self.hears() + (hears() if hears else [])

        return {"route": routed, "keyof": keyed, "take": took, "hears": heard}
