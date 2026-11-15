#!/usr/bin/env python3
"""serve.py — one page server on one port, and how any server starts and stops.

1100 is the only page server. It draws every page itself, each at its own
address, through `route`. A prototype's variations are 1400's: 1100 passes
/proto/ through to 1400, `through`, so each shows from 1100's own origin.
Before the contract, 1400 draws the prototype page too. A session may
serve its own copy on 11NN to try new code:
session 08 tries 1100 on 1108.

A server is then a render function and one call. Nothing about HTTP, pid
files or stopping is written twice. keep() keeps one up: back within ten
seconds of dying or of freezing.

A page is told when it moves, never asks on a clock. Its watch asks
/heard, and the server holds the answer until the page's key changes.
One thread per server hears the writes to the files its pages name, and
a burst of them is one beat. A recheck is a beat too, the safety net for
what no file carries: a pane closing, a port going down. A page's key is
drawn once per beat, however many requests hold it. A page drawn only to
read its key is kept a moment: told it moved, its page asks for itself at
once, and gets that same draw, never a second. A page's key is read before
its draw, so a write landing during the draw is told. A watch whose asker
hung up, as home does to ask anew, is drawn for no more, and neither is a
page whose asker gave up its load. A server serves MOST requests at once,
presses apart, and tells the rest busy. Typing into a
pane, slow by its own delays, runs off the queue: Typing. Its checks and
the write a typed line earns stay on it. So does a draw's read of what
only iTerm holds, a pane's screen or its layout, so no page waits on iTerm.
One such read runs per address at a time, and an ask landing meanwhile is
answered with its page.

A browser holds six requests to one host at once, and each held watch is
one. So one /heard carries any number of pages, and 1100's home holds one
for itself and every page of its own inside it.

Whether a port is answering is the port scheme's, and ports.py holds it.

Imported, never run.
"""

import collections
import contextlib
import glob
import hashlib
import html
import http.client
import http.server
import mimetypes
import os
import re
import resource
import select
import shutil
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse

import hear
import ports
import reader

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Every server's pid and log, one folder each. A page's folder ends in its
# session's number, so a session's end deletes its own and nothing else.
SERVERS = os.path.join(ROOT, ".claude", "state", "servers")
# The key a page wears, as live.watch() writes it.
KEY = re.compile(r'data-key="([^"]*)"')
# A burst of writes is heard as one: a beat comes at most this often, and
# a write inside the gap waits it out, so none is ever missed.
GAP = 0.3
# Every beat this process's pulse has given. lib/live.py reads it: a
# picture is answered unread only within the beat it was drawn in.
BEATS = [0]
# A held /heard answers after this long, moved or not, and is asked again
# at once. A tab closed mid-hold frees its thread by then.
HOLD = 25
# How long a page drawn for its key is kept for the ask that follows.
KEPT = 2
# A burst of draws is named in the log, once a minute at most: each address
# drawn, the page that asked and its browser, and how many watches are held
# then. At 12:16 on 6 November a launch page was drawn 48 times in ten
# seconds, and no line said which, or for whom.
BURST, BURST_SECONDS = 30, 10
# The most requests one server serves at once, presses apart: a press always
# lands. Past it, a request is told busy at once, and asks again. At 09:22
# on 10 November, with no ceiling, 1100 could start no new thread.
MOST = 128
# Past either, half of each ceiling, the log counts threads and open files,
# once a minute at most.
MANY_THREADS, MANY_FILES = 64, 2048
# What a page asked for past MOST shows, in the shell's own dark and dim.
BUSY = ('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="2">'
        '<body style="margin:0;padding:24px;background:#0f1115;color:#8b91a3;'
        'font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace">'
        '{port} is busy. This page asks again in two seconds.')
# 1100, the one page server, with the shift in force: 21100 while it holds.
# Every file that reaches it reads this.
PORT = 1100 + ports.SHIFT


def hashed(page: str) -> str:
    """The key of a page that wears none: a hash of the whole answer. Home
    starts its watch from the one its own model gets."""
    return hashlib.sha1(page.encode()).hexdigest()[:12]


def worn(page) -> str:
    """The key a page wears, as its browser reads it: unescaped, as
    dataset.key hands it over. A hash of the whole page when it wears none,
    and of its bytes when it is no page. lib/live.py keys its pictures by it."""
    if isinstance(page, tuple):
        body = page[0] if isinstance(page[0], bytes) else str(page[0]).encode()
        return hashlib.sha1(body).hexdigest()[:12]
    got = KEY.search(page)
    return html.unescape(got.group(1)) if got else hashed(page)


def stamp() -> str:
    """Now, as each of a server's own log lines opens: its date, then its time."""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def address(kind: str, nn: str) -> str:
    """Where 1100 draws session NN's page of KIND: /p/clarify/07.

    1100's router parses what this builds, so the two never drift."""
    return f"/p/{kind}/{nn}"


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Requests side by side, so one held by /heard never blocks a click."""
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        """A request that failed past its handler, dated in the log."""
        print(f"{stamp()} serve: a request from {client_address[0]} failed", file=sys.stderr)
        traceback.print_exc()


class Turns:
    """One draw at a time, mine first. A draw I asked for, a page or a take,
    goes ahead of every draw that only reads a key for a watch, so it waits
    at most for the one draw already running."""

    def __init__(self):
        self.cond = threading.Condition()
        self.busy = False
        self.asked = 0

    @contextlib.contextmanager
    def take(self, mine: bool):
        with self.cond:
            self.asked += mine
            self.cond.wait_for(lambda: not self.busy and (mine or not self.asked))
            self.asked -= mine
            self.busy = True
        try:
            yield
        finally:
            with self.cond:
                self.busy = False
                self.cond.notify_all()


class Typing:
    """What a take answers when it types into a pane, or does anything else
    slow, and what a route answers when its draw waits on iTerm.

    `outside` types, off the draw queue, so no draw waits on the typing,
    and answers the one sentence a refusal says, "" once typed. `inside`,
    when given, runs back on the queue with that answer, and answers in its
    place: the write a typed line earns, as a wave's sent line. The take
    ran its checks on the queue before handing this back.

    A route's `outside` reads what only iTerm holds, as a pane's screen or
    its layout, off the queue too, and answers what is sent. The route read
    everything else on the queue first.
    """

    def __init__(self, outside, inside=None):
        self.outside, self.inside = outside, inside

    def run(self) -> str:
        """Both halves, now: for a caller with no queue, a tool run alone."""
        said = self.outside()
        return self.inside(said) if self.inside else said


class Said(str):
    """What a take answers when it did what was asked and has one line to
    show for it: a 200, the line its body. A plain sentence is a refusal."""


class Pulse:
    """Every write a server's pages hear, heard once for the whole server.

    One thread watches the files `hears` names. A burst of writes is one
    beat, and so is each recheck. Every held /heard wakes on a beat, and
    asks its pages' keys again. renew() sets the watch again at once, for
    a page just opened, whose files `hears` names from now on.
    """

    def __init__(self, hears, recheck: float):
        self.beat = 0
        self.cond = threading.Condition()
        # A byte written here ends the wait for a write: renew().
        self.renewed = os.pipe()
        for fd in self.renewed:
            os.set_blocking(fd, False)
        threading.Thread(target=self.listen, args=(hears, recheck), daemon=True).start()

    def renew(self) -> None:
        """End the wait now, so the watch is set again on what `hears`
        names now, and a beat follows."""
        with contextlib.suppress(OSError):
            os.write(self.renewed[1], b"1")

    def bump(self) -> None:
        with self.cond:
            self.beat += 1
            BEATS[0] += 1
            self.cond.notify_all()

    def wait(self, beat: int, seconds: float) -> None:
        """Until a beat after `beat`, or `seconds` out."""
        with self.cond:
            self.cond.wait_for(lambda: self.beat != beat, max(0.0, seconds))

    def listen(self, hears, recheck: float) -> None:
        while True:
            try:
                self.once(hears, recheck)
            except Exception:
                time.sleep(recheck)

    def once(self, hears, recheck: float) -> None:
        """Set the watch, beat, then wait for a write or the recheck.

        The watch is set before the beat, so a write landing while it is
        set is already seen by whatever the beat wakes, and a file made
        since the last beat is heard from this one on.
        """
        kq, fds = select.kqueue(), []
        try:
            try:
                # A path named twice is opened once.
                paths = list(dict.fromkeys(hears())) if hears else []
            except Exception:
                paths = []
            for path in paths:
                try:
                    fd = os.open(path, hear.EVENTS)
                except OSError:
                    continue
                fds.append(fd)
                kq.control([select.kevent(fd, select.KQ_FILTER_VNODE,
                                          select.KQ_EV_ADD | select.KQ_EV_CLEAR, hear.WRITTEN)], 0)
            kq.control([select.kevent(self.renewed[0], select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0)
            self.bump()
            got = kq.control(None, 8, recheck)
            # A renew alone sets the watch again at once. A write waits
            # out its burst first.
            if any(e.ident != self.renewed[0] for e in got):
                time.sleep(GAP)
            with contextlib.suppress(OSError):
                os.read(self.renewed[0], 4096)
        finally:
            for fd in fds:
                os.close(fd)
            kq.close()


def pidfile(skill: str) -> str:
    return os.path.join(SERVERS, skill, "server.pid")


def logfile(skill: str) -> str:
    return os.path.join(SERVERS, skill, "server.log")


# A log past LONG keeps only its newest KEEP, about a day of band 00's
# lines. A walk reads each email the stubs send from them.
LONG = 200 * 1024 * 1024
KEEP = 100 * 1024 * 1024


def trim(path: str) -> None:
    """Cut one log past LONG down to its newest KEEP, from a line's start.

    Its server writes in append mode, so each write lands at the new end.
    A line written during the cut can be lost."""
    try:
        if os.path.getsize(path) <= LONG:
            return
        with open(path, "r+b") as f:
            f.seek(-KEEP, os.SEEK_END)
            kept = f.read()
            kept = kept[kept.find(b"\n") + 1:]
            f.seek(0)
            f.write(kept)
            f.truncate()
    except OSError:
        pass


def keep_short(skill: str) -> None:
    """One server's log, kept short on a thread of its own, for as long as
    1100 runs. It sleeps until the log or its folder is written."""
    log = logfile(skill)
    while True:
        try:
            trim(log)
            hear.until(lambda: os.path.getsize(log) > LONG if os.path.exists(log) else False,
                       [log, os.path.dirname(log)], seconds=3600)
        except Exception:
            time.sleep(60)


def forget(number: str) -> None:
    """Delete every server folder one session left. Its ports are already stopped.

    Band 00's folder ends in 00 too. No session holds 00, so it is never touched.
    """
    if number == "00":
        return
    for d in glob.glob(os.path.join(SERVERS, f"*-{number}")):
        shutil.rmtree(d, ignore_errors=True)


def tunnel(h, port: int) -> None:
    """One request, passed whole to `port` on this Mac, and its answer back
    as it comes: a held watch, a post, a websocket alike.

    The far server sees itself asked by its own name, Host and Origin both,
    since this server already welcomed the caller. "localhost", never
    127.0.0.1: a Vite server binds [::1] alone. The connection closes once
    the answer ends, or, upgraded, once either end hangs up."""
    try:
        far = socket.create_connection(("localhost", port), timeout=5)
    except OSError:
        h.send(f"{port} is not answering.".encode(), "text/plain; charset=utf-8", status=502)
        return
    far.settimeout(None)
    h.close_connection = True
    upgrade = h.headers.get("Upgrade")
    lines = [f"{h.command} {h.path} HTTP/1.1"]
    lines += [f"{k}: {v}" for k, v in h.headers.items()
              if k.lower() not in ("host", "origin", "connection", "keep-alive")]
    lines.append(f"Host: localhost:{port}")
    if h.headers.get("Origin"):
        lines.append(f"Origin: http://localhost:{port}")
    lines.append("Connection: " + ("Upgrade" if upgrade else "close"))

    def copy(src, dst) -> None:
        try:
            while piece := src.recv(1 << 16):
                dst.sendall(piece)
        except OSError:
            pass
        with contextlib.suppress(OSError):
            dst.shutdown(socket.SHUT_WR)

    try:
        far.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("latin-1"))
        if size := int(h.headers.get("Content-Length") or 0):
            far.sendall(h.rfile.read(size))
        if upgrade:
            threading.Thread(target=copy, args=(h.connection, far), daemon=True).start()
        copy(far, h.connection)
    except OSError:
        pass
    finally:
        far.close()


def run(skill: str, port: int, render, take=None, route=None,
        hears=None, recheck: float = 3, keyof=None, raw=None, through=None) -> None:
    """Serve one page until killed. `render` returns the HTML, per request.

    `through` is (prefix, port): every address under the prefix, any method,
    goes whole to that port, through `tunnel`. 1100 passes /proto/ to 1400.
    A third part is asked each such address, and one it says is this
    server's own stays here: on the contract, the prototype page itself.
    A request asking to upgrade, a websocket's, goes through all the same.

    `raw` is for a file too big to draw into a page, as a clip. It is given
    the path, and returns the file on disk to send, or None. The file goes
    in pieces, as a player asks for them by Range, off the queue, so no
    page waits on it.

    `take` is for a page I act on. It is given the posted form, already
    parsed into a dict of lists, and the page is drawn again afterwards.
    A page that only shows things passes nothing, and answers no POST.
    A take that could not do what was asked returns one sentence saying
    why, and the POST answers with it, status 409, in place of the
    redirect: a page typing into a pane that is gone says so this way. One
    that did it, with a line to show, returns a Said: a 200, the line its
    body. A take that types into a pane returns a Typing: its typing runs off the
    queue, its checks and writes on it.

    `route` is for a page with more than one address. It is given the path,
    and returns the HTML for it, or None to draw the page itself. A file
    that is no page, as a picture, it returns as its bytes and their type,
    sent as they are. A draw waiting on iTerm returns a Typing, finished
    off the queue. A server with routes hands `take` the path posted to
    as well, and redirects back to it, since each of its pages takes its
    own posts.

    `keyof` is given a path, and returns a cheap key for that page, or None
    to draw it and read the key it wears.

    `hears` is for a page that can be told. It returns the files and folders
    whose writes can move the page. /heard?path=P&key=K holds its answer
    until the page's key at P is no longer K, and answers with the new one.
    It takes any number of path and key pairs, and answers each page's key,
    one per line, in the order asked, once any one has moved. The key is
    keyof's, or the one the page's HTML wears, or a hash of the whole answer.
    `recheck` is the safety net, in seconds: a beat comes then, whatever
    was heard. With no `hears`, only it wakes /heard.

    Every draw and every take runs one at a time, as when the server took
    one request at a time. Only the waiting runs beside. A page or a take I
    asked for goes ahead of every draw that only reads a watch's key:
    Turns. A take is a beat, so no key drawn before it is answered after it.

    The answer to a POST is a redirect, so a refresh never posts twice.
    """
    turns = Turns()
    pulse = Pulse(hears, recheck)
    # A pane or a process read in the background writes no file: the
    # moment its answer moves, a beat follows, and each look is read again.
    reader.MOVED.append(pulse.renew)
    # Each page's key, and the beat it was drawn at.
    keys = {}
    # Each page drawn for its key alone: the beat, when, and the page.
    kept = {}
    # The last BURST_SECONDS of draws, when the last burst was named, and
    # how many /heard are held now.
    draws, told, held, tally = collections.deque(), [0.0], [0], threading.Lock()
    # A place for each request served now, presses apart: MOST.
    serving = threading.BoundedSemaphore(MOST)
    # When threads and open files are next counted.
    weighed = [0.0]
    # Each address drawing off the queue now: whether it is done, and its page.
    flights = {}
    # When a watch last asked about each address.
    watched = {}

    def weigh() -> None:
        """Count threads and open files, every ten seconds at most. Past
        MANY_THREADS or MANY_FILES, one line says both, once a minute at
        most. Never raises."""
        try:
            now = time.time()
            if now < weighed[0]:
                return
            threads, files = threading.active_count(), len(os.listdir("/dev/fd"))
            high = threads > MANY_THREADS or files > MANY_FILES
            weighed[0] = now + (60 if high else 10)
            if not high:
                return
        except Exception:
            return
        print(f"{stamp()} serve: {threads} threads and {files} open files, {held[0]} watches held",
              file=sys.stderr, flush=True)

    def counted(h) -> None:
        """Count one draw, and name the burst once draws flood. Never raises."""
        try:
            now = time.time()
            agent = " ".join(re.findall(r"[A-Za-z]+/[\d.]+", h.headers.get("User-Agent", ""))[-2:])
            page = urllib.parse.urlsplit(h.headers.get("Referer", "")).path
            with tally:
                draws.append((now, f"{h.path} for {page or 'no page'} by {agent or 'no browser'}"))
                while now - draws[0][0] > BURST_SECONDS:
                    draws.popleft()
                if len(draws) < BURST or now - told[0] < 60:
                    return
                told[0], count, watches = now, len(draws), held[0]
                top = collections.Counter(w for _, w in draws).most_common(5)
        except Exception:
            return
        print(f"{stamp()} serve: {count} draws in {BURST_SECONDS} seconds, "
              f"{watches} watches held, from " + ", ".join(f"{w} ({n})" for w, n in top),
              file=sys.stderr, flush=True)

    def draw(path: str) -> str:
        other = route(path) if route else None
        return other if other is not None else render()

    def cheap(path: str):
        """The page's key without drawing it, or None when only a draw tells."""
        return keyof(path) if keyof else None

    def drawn(path: str, left=None):
        """A page, drawn now, or the draw its key was read from this beat, a
        moment ago. The key it wears is its key for this beat, so a watch
        asking the moment it loads is never told of an older one. None once
        its asker hung up, `left`, while it waited its turn: a load given up
        is drawn for nobody."""
        beat = pulse.beat
        with turns.take(mine=True):
            if left and left():
                return None
            got = kept.pop(path, None)
            if got and got[0] == beat and time.time() - got[1] < KEPT:
                return got[2]
            # The key first, then the draw, and the page wears that key: a
            # write landing during the draw moves the key, and the page's
            # watch is told of it.
            now = keyof(path) if keyof else None
            page = draw(path)
            # A draw finished off the queue wears this key too, and it
            # becomes this beat's. Otherwise a pane opening, which writes no
            # file, leaves the beat's older key, and every fresh draw is told
            # it moved until the recheck: at 09:24 on 10 November, a launch
            # page reloaded 353 times in ten seconds.
            if isinstance(page, Typing) and now is not None:
                keys[path] = (beat, now)
                finish = page.outside

                def outside():
                    got = finish()
                    return KEY.sub(lambda m: f'data-key="{html.escape(now)}"', got, 1) if isinstance(got, str) else got
                page.outside = outside
            if isinstance(page, str):
                if now is not None:
                    page = KEY.sub(lambda m: f'data-key="{html.escape(now)}"', page, 1)
                keys[path] = (beat, worn(page) if now is None else now)
                # A key from an older beat is never read again: once many
                # pile up, as a transcript's asks each wear their own
                # address, they go.
                if len(keys) > 512:
                    for old in [p for p, (b, _) in keys.items() if b != beat]:
                        del keys[old]
            return page

    def known(path: str) -> str:
        """The page's key at `path`, drawn once per beat, whoever asks."""
        beat = pulse.beat
        with turns.take(mine=False):
            got = keys.get(path)
            if got and got[0] == beat:
                return got[1]
            now = cheap(path)
            if now is None:
                page = draw(path)
                now = worn(page)
                if isinstance(page, str):
                    kept[path] = (beat, time.time(), page)
            keys[path] = (beat, now)
            return now

    # What a draw that raised answers, in place of its page.
    failed = (f"{port} failed on this draw. Its log holds the whole error.\n".encode(),
              "text/plain; charset=utf-8", 500)

    def finished(path: str, page: Typing, left):
        """A draw finished off the queue, one per address at a time. An ask
        landing meanwhile waits for that same page, and leaves once its
        asker hung up, `left`: None. At 09:19 on 10 November each load given
        up still waited on iTerm, and 1100 ran out of open files."""
        with tally:
            flight = flights.get(path)
            first = flight is None
            if first:
                flight = flights[path] = [threading.Event(), None]
        if not first:
            while not flight[0].wait(0.1):
                if left():
                    return None
            return flight[1]
        try:
            flight[1] = page.outside()
        except Exception:
            print(f"{stamp()} serve: {port} failed on {path}", file=sys.stderr)
            traceback.print_exc()
            flight[1] = failed
        finally:
            with tally:
                flights.pop(path, None)
            flight[0].set()
        return flight[1]

    def hung_up(sock) -> bool:
        """Whether the asker closed its end: its socket reads end of file.
        Asked by poll, never select, which refuses a socket numbered 1024
        or more: past that, every held watch broke."""
        try:
            ready = select.poll()
            ready.register(sock, select.POLLIN)
            return bool(ready.poll(0)) and not sock.recv(1, socket.MSG_PEEK)
        except OSError:
            return True

    def heard(asked: list, left) -> list | None:
        """Each page's key once one is no longer the key it was asked
        with, or once the hold is up. None once the asker hung up, `left`:
        a page that let go of its watch, as home does to ask anew, has its
        pages drawn for no more."""
        end = time.time() + HOLD
        # A page no watch asked about in the last beats was just opened, or
        # shown again. `hears` names its files only once its key is read,
        # below, so the pulse sets its watch again after that. The beat
        # that follows wakes this ask, which reads the keys once more: a
        # write landing meanwhile is not missed.
        opened = any(end - HOLD - watched.get(path, 0) > recheck + 2 for path, _ in asked)
        while True:
            beat = pulse.beat
            now = [known(path) for path, _ in asked]
            at = time.time()
            watched.update((path, at) for path, _ in asked)
            if len(watched) > 512:
                for old in [p for p, was in list(watched.items()) if at - was > 60]:
                    watched.pop(old, None)
            if any(n != k for n, (_, k) in zip(now, asked)) or at >= end:
                return now
            if opened:
                pulse.renew()
                opened = False
            pulse.wait(beat, end - time.time())
            if left():
                return None

    # The server types into panes, so only two callers ever reach it: this
    # Mac, by its own name, and my phone, through `tailscale serve`, which
    # names who sent it and strips that header from anyone else. A post
    # from another site, on either, is refused: a page I happen to visit
    # never drives a pane.
    local = {f"127.0.0.1:{port}", f"localhost:{port}"}

    def passed(h) -> bool:
        """Whether request `h` goes whole to `through`'s port: under its
        prefix, and not this server's own. One asking to upgrade always
        goes: Vite's socket connects at the bare prefix, where the
        prototype page lives."""
        return (bool(through) and h.path.startswith(through[0])
                and (bool(h.headers.get("Upgrade")) or not any(own(h.path) for own in through[2:])))

    def welcome(h) -> bool:
        host = h.headers.get("Host", "")
        name = host.rsplit(":", 1)[0]
        mine = host in local or (name.endswith(".ts.net") and h.headers.get("Tailscale-User-Login"))
        origin = h.headers.get("Origin")
        return bool(mine) and (not origin or urllib.parse.urlsplit(origin).netloc == host)

    class Handler(http.server.BaseHTTPRequestHandler):
        def send(self, page: bytes, kind: str = "text/html; charset=utf-8",
                 told: bool = False, status: int = 200) -> None:
            self.answered = True
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(page)))
            # A watch that finds this header was told. One that does not is
            # on a server that cannot hold, and asks on a clock instead.
            if told:
                self.send_header("X-Heard", "1")
            # A page that let go of its watch, as home does to ask anew,
            # is gone before its answer. Nothing is owed to it.
            try:
                self.end_headers()
                self.wfile.write(page)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def stream(self, file: str) -> None:
            """One file, whole or the Range a player asks for, in pieces."""
            self.answered = True
            try:
                size = os.path.getsize(file)
            except OSError:
                self.send_error(404)
                return
            start, end = 0, size - 1
            asked = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "").strip())
            if asked and size:
                a, b = asked.groups()
                start, end = (int(a), min(int(b), end) if b else end) if a else (max(0, size - int(b or 0)), end)
                if start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    return
            self.send_response(206 if asked and size else 200)
            self.send_header("Content-Type", mimetypes.guess_type(file)[0] or "application/octet-stream")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            if asked and size:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            try:
                with open(file, "rb") as f:
                    f.seek(start)
                    left = end - start + 1
                    while left > 0 and (piece := f.read(min(1 << 20, left))):
                        self.wfile.write(piece)
                        left -= len(piece)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass

        def do_GET(self):
            if not welcome(self):
                self.send_error(403)
                return
            if passed(self):
                return tunnel(self, through[1])
            # Answered apart from the ceiling and the queue, so a keeper
            # learns at once whether this server still answers: keep().
            if self.path == "/health":
                return self.send(b"ok\n", "text/plain; charset=utf-8")
            weigh()
            # Past the ceiling, a page is told busy, and loads itself again.
            # A watch that finds no X-Heard asks again on its own.
            if not serving.acquire(blocking=False):
                self.send(BUSY.format(port=port).encode(), status=503)
                return
            # A request that raises answers in one sentence, as a failed
            # press does, never with a dropped connection.
            try:
                self.get()
            except Exception:
                print(f"{stamp()} serve: {port} failed on {self.path}", file=sys.stderr)
                traceback.print_exc()
                if not getattr(self, "answered", False):
                    self.send(*failed[:2], status=failed[2])
            finally:
                serving.release()

        def get(self):
            bare, _, query = self.path.partition("?")
            if raw and (file := raw(bare)):
                return self.stream(file)
            if bare == "/heard":
                # Blanks are kept, so a page asking with no key yet keeps
                # its place in the pairs.
                q = urllib.parse.parse_qs(query, keep_blank_values=True)
                paths, was = q.get("path", []), q.get("key", [])
                asked = [((paths[i] if i < len(paths) else "") or "/",
                          was[i] if i < len(was) else "")
                         for i in range(max(len(paths), len(was), 1))]
                with tally:
                    held[0] += 1
                try:
                    got = heard(asked, lambda: hung_up(self.connection))
                finally:
                    with tally:
                        held[0] -= 1
                if got is not None:
                    self.send("\n".join(got).encode(), "text/plain; charset=utf-8", told=True)
                return
            counted(self)
            left = lambda: hung_up(self.connection)
            got = drawn(self.path, left)
            # A draw waiting on iTerm finishes off the queue: Typing.
            if isinstance(got, Typing):
                got = finished(self.path, got, left)
            # Its asker hung up: nothing is drawn for it, and nothing owed.
            if got is None:
                return
            # A file that is no page goes as it is: its bytes, their type,
            # and a status when it is not 200, as not found.
            if isinstance(got, tuple):
                self.send(got[0], got[1], status=got[2] if len(got) > 2 else 200)
            else:
                self.send(got.encode())

        def do_POST(self):
            if not welcome(self):
                self.send_error(403)
                return
            if passed(self):
                return tunnel(self, through[1])
            if take is None:
                self.send_error(405)
                return
            size = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(size).decode("utf-8", "replace")
            bare = self.path.partition("?")[0]
            form = urllib.parse.parse_qs(body, keep_blank_values=True)
            # A take that raises answers in one sentence, as a refusal does,
            # never with a dropped connection, and its error goes to the log.
            try:
                with turns.take(mine=True):
                    why = take(form, bare) if route else take(form)
                if isinstance(why, Typing):
                    said = why.outside()
                    if why.inside:
                        with turns.take(mine=True):
                            said = why.inside(said)
                    why = said
            except Exception:
                print(f"{stamp()} serve: {port} failed on a press at {bare}", file=sys.stderr)
                traceback.print_exc()
                why = f"{port} failed on this press. Its log holds the whole error."
            pulse.bump()
            # A page gone before its answer is owed nothing, as send() says.
            try:
                if isinstance(why, Said):
                    said = str(why).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(said)))
                    self.end_headers()
                    self.wfile.write(said)
                    return
                if why:
                    said = str(why).encode()
                    self.send_response(409)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(said)))
                    self.end_headers()
                    self.wfile.write(said)
                    return
                self.send_response(303)
                self.send_header("Location", bare if route else "/")
                self.send_header("Content-Length", "0")
                self.end_headers()
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            return

    # Each held request holds a socket, and the pulse a file for each one
    # its pages hear. The soft limit on open files is raised to 4096, or the
    # hard limit when lower, so a few open tabs never run out.
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (max(soft, min(hard, 4096)), hard))
    with Server(("127.0.0.1", port), Handler) as httpd:
        os.makedirs(os.path.dirname(pidfile(skill)), exist_ok=True)
        with open(pidfile(skill), "w") as f:
            f.write(str(os.getpid()))
        httpd.serve_forever()


def start(skill: str, port: int, tool: str) -> str:
    """Bring a page up. A port already answering is left alone.

    No browser is opened: 1100 already shows in its own pane. The call
    waits for the port to answer, so that pane's watch finds it up.
    Restarting a live page would drop the one I am looking at.
    """
    if ports.answering(port):
        return ""
    _, up = spawn(skill, port, [sys.executable, tool, "serve", "--port", str(port)])
    return "" if up else f"could not bind {port}. See {logfile(skill)}"


def spawn(skill: str, port: int, cmd: list, cwd: str | None = None,
          env: dict | None = None, seconds: float = 4) -> tuple:
    """Start one server detached, its output in its log, then wait up to
    `seconds` for its port to answer. Its pid, and whether it answered.

    The wait is heard. A page of this band writes its pid file the moment
    its port is bound, and any other server writes its log. A server that
    dies ends the wait at once.
    """
    folder = os.path.dirname(logfile(skill))
    os.makedirs(folder, exist_ok=True)
    with open(logfile(skill), "ab") as f:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=f, stderr=f,
                                start_new_session=True)
    hear.until(lambda: ports.answering(port) or proc.poll() is not None,
               files=[folder, pidfile(skill), logfile(skill)], pids=[proc.pid], seconds=seconds)
    return proc.pid, ports.answering(port)


def holder(port: int) -> int:
    """The pid listening on one port, or 0.

    A pidfile can be lost while its server lives on. The port itself is the
    second record, and it cannot go stale. Bounded to the port passed in.
    """
    r = subprocess.run(
        ["/usr/sbin/lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True, text=True)
    first = r.stdout.split()
    return int(first[0]) if first else 0


def stop(skill: str, port: int) -> bool:
    """Stop this skill's page. True when something was running.

    The port's listener is the page, and it cannot go stale. A pidfile can:
    its process may be long gone, and its pid handed to another program. So
    a pidfile is only asked when there is no port, as for band 00's pnpm.
    """
    saved, p = kept(skill), pidfile(skill)
    if os.path.isfile(p):
        os.remove(p)
    pid = holder(port) if port else (saved if ports.alive(saved) else 0)
    if pid <= 0:
        return False
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return False
    return True


# A stop on purpose takes the pid file with it. A keeper leaves that server
# down this many seconds before it starts it again.
LEFT_DOWN = 60


def healthy(port: int, seconds: float = 1.5) -> bool:
    """Whether the server on `port` answers /health within `seconds`, with
    anything at all: a server from before /health answers not found, and
    still answers. A frozen one answers nothing."""
    asked = http.client.HTTPConnection("127.0.0.1", port, timeout=seconds)
    try:
        asked.request("GET", "/health")
        asked.getresponse()
        return True
    except (OSError, http.client.HTTPException):
        return False
    finally:
        asked.close()


def keep(skill: str, port: int, tool: str, every: float = 1.5) -> None:
    """One server kept up for as long as the caller runs: back within ten
    seconds of dying or of freezing. A timer, since neither writes a file.

    Nothing listening and its pid file standing, it died: it starts again
    at once. Its pid file gone, it was stopped on purpose, or a restart is
    under way: it is left LEFT_DOWN seconds, then started. Listening, and
    /health unanswered three asks running, it froze: it is killed, then
    started, when its pid file names the listener. Any other program on
    its port is left alone. A frozen server's port can refuse a connection
    once asks pile up on it, so who listens is lsof's to say, holder().
    A start that fails is tried again ever later, to a minute apart.
    """
    missed, down, failed = 0, 0.0, 0
    while True:
        try:
            if healthy(port):
                missed, down, failed = 0, 0.0, 0
            elif pid := holder(port):
                down, missed = 0.0, missed + 1
                if missed >= 3 and pid == kept(skill):
                    missed = 0
                    os.kill(pid, signal.SIGKILL)
                    ports.gone([pid], 3)
                    print(f"{stamp()} serve: {port} answered nothing three asks running. It was killed, "
                          "and starts again.", file=sys.stderr, flush=True)
                    failed = failed + 1 if start(skill, port, tool) else 0
            else:
                missed, down = 0, down or time.time()
                if os.path.isfile(pidfile(skill)) or time.time() - down >= LEFT_DOWN:
                    failed = failed + 1 if start(skill, port, tool) else 0
        except Exception:
            traceback.print_exc()
        time.sleep(min(60, every * 2 ** failed))


def kept(skill: str) -> int:
    """The pid a server's pid file names, or 0 with none to read."""
    try:
        with open(pidfile(skill)) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0
