#!/usr/bin/env python3
"""serve.py — one page server on one port, and how any server starts and stops.

1100 is the only page server. It draws every page itself, each at its own
address, through `route`, bar a prototype, framed from 1400. A session may
serve its own copy on 11NN to try new code:
session 08 tries 1100 on 1108.

A server is then a render function and one call. Nothing about HTTP, pid
files or stopping is written twice.

A page is told when it moves, never asks on a clock. Its watch asks
/heard, and the server holds the answer until the page's key changes.
One thread per server hears the writes to the files its pages name, and
a burst of them is one beat. A recheck is a beat too, the safety net for
what no file carries: a pane closing, a port going down. A page's key is
drawn once per beat, however many requests hold it. A page drawn only to
read its key is kept a moment: told it moved, its page asks for itself at
once, and gets that same draw, never a second. A page's key is read before
its draw, so a write landing during the draw is told. A watch whose asker
hung up, as home does to ask anew, is drawn for no more. Typing into a
pane, slow by its own delays, runs off the queue: Typing. Its checks and
the write a typed line earns stay on it. So does a draw's read of what
only iTerm holds, a pane's screen or its layout, so no page waits on iTerm.

A browser holds six requests to one host at once, and each held watch is
one. So one /heard carries any number of pages, and 1100's home holds one
for itself and every page of its own inside it.

Whether a port is answering is the port scheme's, and ports.py holds it.

Imported, never run.
"""

import contextlib
import glob
import hashlib
import html
import http.server
import json
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Every server's pid and log, one folder each. A page's folder ends in its
# session's number, so a session's end deletes its own and nothing else.
SERVERS = os.path.join(ROOT, ".claude", "state", "servers")
# The key a page wears, as page.watch writes it.
KEY = re.compile(r'data-key="([^"]*)"')
# A burst of writes is heard as one: a beat comes at most this often, and
# a write inside the gap waits it out, so none is ever missed.
GAP = 0.3
# A held /heard answers after this long, moved or not, and is asked again
# at once. A tab closed mid-hold frees its thread by then.
HOLD = 25
# How long a page drawn for its key is kept for the ask that follows.
KEPT = 2
# 1100, the one page server, with the shift in force: 21100 while it holds.
# Every file that reaches it reads this.
PORT = 1100 + ports.SHIFT


def hashed(page: str) -> str:
    """The key of a page that wears none: a hash of the whole answer. Home
    starts its watch from the one its own model gets."""
    return hashlib.sha1(page.encode()).hexdigest()[:12]


def address(kind: str, nn: str) -> str:
    """Where 1100 draws session NN's page of KIND: /p/clarify/07.

    1100's router parses what this builds, so the two never drift."""
    return f"/p/{kind}/{nn}"


def fixture(path: str) -> tuple:
    """A page tool's try fixture, as (load, mark): load reads the JSON file
    whole, mark is its key, a hash of the file. Every page tool draws one
    until I lock it, so this is written once."""
    def load() -> dict:
        with open(path) as f:
            return json.load(f)

    def mark(_path: str = "") -> str:
        with open(path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:12]

    return load, mark


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Requests side by side, so one held by /heard never blocks a click."""
    daemon_threads = True
    allow_reuse_address = True


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


class Pulse:
    """Every write a server's pages hear, heard once for the whole server.

    One thread watches the files `hears` names. A burst of writes is one
    beat, and so is each recheck. Every held /heard wakes on a beat, and
    asks its pages' keys again.
    """

    def __init__(self, hears, recheck: float):
        self.beat = 0
        self.cond = threading.Condition()
        threading.Thread(target=self.listen, args=(hears, recheck), daemon=True).start()

    def bump(self) -> None:
        with self.cond:
            self.beat += 1
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
            self.bump()
            if kq.control(None, 8, recheck):
                time.sleep(GAP)
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


def run(skill: str, port: int, render, take=None, key=None, route=None,
        hears=None, recheck: float = 3, keyof=None, raw=None) -> None:
    """Serve one page until killed. `render` returns the HTML, per request.

    `raw` is for a file too big to draw into a page, as a clip. It is given
    the path, and returns the file on disk to send, or None. The file goes
    in pieces, as a player asks for them by Range, off the queue, so no
    page waits on it.

    `take` is for a page I act on. It is given the posted form, already
    parsed into a dict of lists, and the page is drawn again afterwards.
    A page that only shows things passes nothing, and answers no POST.
    A take that could not do what was asked returns one sentence saying
    why, and the POST answers with it, status 409, in place of the
    redirect: a page typing into a pane that is gone says so this way. A
    take that types into a pane returns a Typing: its typing runs off the
    queue, its checks and writes on it.

    `key` is for a page whose render is costly. /key answers with it alone,
    so a page asking whether anything moved never pays for a full draw.

    `route` is for a page with more than one address. It is given the path,
    and returns the HTML for it, or None to draw the page itself. A file
    that is no page, as a picture, it returns as its bytes and their type,
    sent as they are. A draw waiting on iTerm returns a Typing, finished
    off the queue. A server with routes hands `take` the path posted to
    as well, and redirects back to it, since each of its pages takes its
    own posts.

    `keyof` is `key` for a server with routes: given a path, a cheap key
    for that page, or None to draw it and read the key it wears.

    `hears` is for a page that can be told. It returns the files and folders
    whose writes can move the page. /heard?path=P&key=K holds its answer
    until the page's key at P is no longer K, and answers with the new one.
    It takes any number of path and key pairs, and answers each page's key,
    one per line, in the order asked, once any one has moved. The key is
    key(), or the one the page's HTML wears, or a hash of the whole answer.
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
    # Each page's key, and the beat it was drawn at.
    keys = {}
    # Each page drawn for its key alone: the beat, when, and the page.
    kept = {}

    def draw(path: str) -> str:
        other = route(path) if route else None
        return other if other is not None else render()

    def worn(page: str) -> str:
        """The key a page wears, as its browser reads it: unescaped, as
        dataset.key hands it over. A hash of the whole page when it wears none,
        and of its bytes when it is no page."""
        if isinstance(page, tuple):
            body = page[0] if isinstance(page[0], bytes) else str(page[0]).encode()
            return hashlib.sha1(body).hexdigest()[:12]
        got = KEY.search(page)
        return html.unescape(got.group(1)) if got else hashed(page)

    def cheap(path: str):
        """The page's key without drawing it, or None when only a draw tells."""
        if key and not route:
            return key()
        return keyof(path) if keyof else None

    def drawn(path: str) -> str:
        """A page, drawn now, or the draw its key was read from this beat, a
        moment ago. The key it wears is its key for this beat, so a watch
        asking the moment it loads is never told of an older one."""
        beat = pulse.beat
        with turns.take(mine=True):
            got = kept.pop(path, None)
            if got and got[0] == beat and time.time() - got[1] < KEPT:
                return got[2]
            # The key first, then the draw, and the page wears that key: a
            # write landing during the draw moves the key, and the page's
            # watch is told of it.
            now = keyof(path) if keyof and not (key and not route) else None
            page = draw(path)
            if isinstance(page, str) and not (key and not route):
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

    def hung_up(sock) -> bool:
        """Whether the asker closed its end: its socket reads end of file."""
        try:
            return bool(select.select([sock], [], [], 0)[0]) and not sock.recv(1, socket.MSG_PEEK)
        except OSError:
            return True

    def heard(asked: list, left) -> list | None:
        """Each page's key once one is no longer the key it was asked
        with, or once the hold is up. None once the asker hung up, `left`:
        a page that let go of its watch, as home does to ask anew, has its
        pages drawn for no more."""
        end = time.time() + HOLD
        while True:
            beat = pulse.beat
            now = [known(path) for path, _ in asked]
            if any(n != k for n, (_, k) in zip(now, asked)) or time.time() >= end:
                return now
            pulse.wait(beat, end - time.time())
            if left():
                return None

    # The server types into panes, so only two callers ever reach it: this
    # Mac, by its own name, and my phone, through `tailscale serve`, which
    # names who sent it and strips that header from anyone else. A post
    # from another site, on either, is refused: a page I happen to visit
    # never drives a pane.
    local = {f"127.0.0.1:{port}", f"localhost:{port}"}

    def welcome(h) -> bool:
        host = h.headers.get("Host", "")
        mine = host in local or (host.endswith(".ts.net") and h.headers.get("Tailscale-User-Login"))
        origin = h.headers.get("Origin")
        return bool(mine) and (not origin or urllib.parse.urlsplit(origin).netloc == host)

    class Handler(http.server.BaseHTTPRequestHandler):
        def send(self, page: bytes, kind: str = "text/html; charset=utf-8",
                 told: bool = False, status: int = 200) -> None:
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
                got = heard(asked, lambda: hung_up(self.connection))
                if got is not None:
                    self.send("\n".join(got).encode(), "text/plain; charset=utf-8", told=True)
                return
            if key and self.path == "/key":
                with turns.take(mine=False):
                    self.send(key().encode())
                return
            got = drawn(self.path)
            # A draw waiting on iTerm finishes off the queue: Typing.
            if isinstance(got, Typing):
                try:
                    got = got.outside()
                except Exception:
                    traceback.print_exc()
                    got = (f"{port} failed on this draw. Its log holds the whole error.\n".encode(),
                           "text/plain; charset=utf-8", 500)
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
                traceback.print_exc()
                why = f"{port} failed on this press. Its log holds the whole error."
            pulse.bump()
            # A page gone before its answer is owed nothing, as send() says.
            try:
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
    saved = 0
    p = pidfile(skill)
    if os.path.isfile(p):
        with open(p) as f:
            saved = int(f.read().strip() or 0)
        os.remove(p)
    pid = holder(port) if port else (saved if ports.alive(saved) else 0)
    if pid <= 0:
        return False
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return False
    return True
