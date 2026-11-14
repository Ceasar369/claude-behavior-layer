#!/usr/bin/env python3
"""Check what lib/live.py promises, on a made-up table of pages.

A server on this session's port, 11NN, draws a few made-up pages from a
temporary folder, each on the contract, with what is no page riding on.
Each check holds a watch as a browser does, writes a file or sends a
press, and reads what came back.

  A write shows in the next answer, within a second.
  Another page's write wakes nothing, and nothing written draws nothing.
  A page moved with no file it names written is caught at the check, and
  named, and at live.py's own 25 seconds too.
  A look, which no file carries, moves its page.
  A pane closing, or a session's program ending, shows within 4 seconds,
  on 1100's own timers: iTerm and ps alone are stood in.
  A part that fails leaves the others, and a page that fails leaves the rest.
  A press sent twice acts once, and typing into one pane goes one at a time.
  Data is kept as a page is, what is no page rides on, and a fresh table
  draws the same key.
  A file written a thousand times in a second draws its page five times at most.
  A page asked about for the first time hears a write at once.
  A look read in the background moves its page the moment its answer does.
  Under a prefix passed through to another port, a page the table holds
  stays here, and any other address goes through.

  live-test.py [NN]

NN is this session's number, 02 when none is given.
"""

import collections
import http.client
import inspect
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import reader  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "02"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"live-test-{NN}"
# The pulse rechecks as 1100's does, serve.run's own default, 3 seconds.
# The check's CHECK is kept as live.py states it, before any check moves
# it. A held watch answers after four seconds here, and is asked again.
RECHECK = inspect.signature(serve.run).parameters["recheck"].default
CHECKED = live.CHECK
serve.HOLD = 4
# What 1100 promises: a pane closing, or a program ending, shows within
# 4 seconds, and an open page is drawn afresh and compared every 25.
SHOWN, AFRESH = 4, 25
# Long enough for the pulse to hear a file first named a moment ago.
HEARD = RECHECK + serve.GAP + 0.4
TMP = tempfile.mkdtemp(prefix="live-test-")
# Each page's draws, each press that acted, and the most typing at once in one pane.
DREW: dict = {}
ACTED: list = []
TYPING = {"now": 0, "most": 0}
LOOK = [0]
# What a reader reads in the background here, every tenth of a second: lib/reader.py.
SEEN = [0]
READ = reader.Reader(lambda: SEEN[0], every=0.1)
# What iTerm and ps answer here, and when each was asked: a pane list and a
# process list, read by 1100's own readers on their own timers, panes.py's
# refresher every panes.FRESH seconds and ports.PROCESSES every 3. Beside
# them, only the folder Claude Code's records are read from is stood in.
PANES = {"05000000-0000-0000-0000-000000000000": "/dev/ttys005",
         "06000000-0000-0000-0000-000000000000": "/dev/ttys006"}
PS = {40005: (1, "Mon Nov 10 09:00:00 2026", "ttys005", "claude"),
      40006: (1, "Mon Nov 10 09:00:00 2026", "ttys006", "claude")}
ITERM_ASKED: list = []
PS_ASKED: list = []
ACCOUNT = os.path.join(TMP, "account")


def iterm(script: str, timeout: float = 10) -> str:
    """iTerm's answer to panes.py's list of panes, each ask's time kept."""
    said = "\n".join(f"{p} {t}" for p, t in PANES.items())
    ITERM_ASKED.append(time.time())
    return said


def ps() -> dict:
    """ps's answer to ports.everything, each ask's time kept."""
    said = dict(PS)
    PS_ASKED.append(time.time())
    return said


class Pgrep:
    """subprocess as panes.py reaches it, pgrep saying iTerm2 runs."""

    def __getattr__(self, name):
        return getattr(subprocess, name)

    @staticmethod
    def run(argv, *given, **named):
        if argv[:1] == ["/usr/bin/pgrep"]:
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        return subprocess.run(argv, *given, **named)


def file(name: str) -> str:
    return os.path.join(TMP, f"{name}.txt")


def write(name: str, text: str) -> None:
    with open(file(name), "w") as f:
        f.write(text)


def read(name: str) -> str:
    with open(file(name)) as f:
        return f.read()


def shell(nn: str, body: str) -> str:
    return page.render(f"{nn}-trial", [("", live.watch(f"session-{nn}") + body)], refresh=0)


def trial(nn: str) -> str:
    DREW[nn] = DREW.get(nn, 0) + 1
    return shell(nn, f'<p id="said">{page.esc(read(nn))}</p>')


def blind(nn: str) -> str:
    return shell(nn, f'<p id="said">{page.esc(read("blind"))}</p>')


def parts(nn: str) -> str:
    def first() -> str:
        raise KeyError("no such item")
    return shell(nn, live.part("The first part", first) + live.part("The second part", lambda: "<p>Second part stands.</p>"))


def seated(nn: str) -> str:
    """Every open pane and how many sessions' programs run, as 1100 last read them."""
    return shell(nn, f'<p id="panes">{page.esc(" ".join(sorted(panes.terminals(panes.FRESH) or ())))}</p>'
                     f'<p id="programs">Programs running: {len(registry.claude_records())}.</p>')


def broken(nn: str) -> str:
    raise ValueError("this page is broken")


def typed() -> str:
    TYPING["now"] += 1
    TYPING["most"] = max(TYPING["most"], TYPING["now"])
    time.sleep(0.5)
    TYPING["now"] -= 1
    ACTED.append("type")
    return ""


def take(nn: str, form: dict):
    act = (form.get("act") or [""])[0]
    if act == "mark":
        ACTED.append("mark")
        return ""
    if act == "refuse":
        ACTED.append("refuse")
        return "This press is refused. Nothing was done."
    if act == "type":
        return serve.Typing(typed)
    return "This page takes no such press. Nothing was done."


PAGES = [
    live.Page(serve.address("trial", r"(\d{2})"), trial, files=lambda nn: [file(nn)], take=take),
    live.Page(serve.address("blind", r"(\d{2})"), blind),
    live.Page(serve.address("parts", r"(\d{2})"), parts),
    live.Page(serve.address("broken", r"(\d{2})"), broken),
    live.Page(serve.address("looks", r"(\d{2})"), lambda nn: shell(nn, f"<p>{LOOK[0]}</p>"), looks=[lambda: LOOK[0]]),
    live.Page(serve.address("read", r"(\d{2})"), lambda nn: shell(nn, f"<p>{READ.last()}</p>"), looks=[READ.last]),
    live.Page(serve.address("panes", r"(\d{2})"), seated,
              looks=(lambda: sorted(panes.terminals(panes.FRESH) or ()), lambda: sorted(registry.claude_records()))),
    live.Page(r"/data/(\d{2})", lambda nn: (json.dumps({"nn": nn}).encode(), "application/json")),
    live.Page(r"/far/(\d{2})", trial, files=lambda nn: [file(nn)], take=take),
]
TABLE = live.Table(PAGES)
# The prefix this server passes through, to a port nothing answers on.
FAR = ("/far/", 1)


def rides(path: str):
    """What 1100 answers behind the table, at an address that is no page: a
    pane's lines, read off the queue as iTerm's are, a folder's listing as
    data, or not found."""
    bare = path.partition("?")[0]
    if bare == "/p/trial/05/pane":
        return serve.Typing(lambda: '<div id="offer">A pane\'s last lines.</div>')
    if bare == "/tree/05/":
        return json.dumps({"listed": ["a.md"]}).encode(), "application/json"
    return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404


def ask(method: str, path: str, body: str = "", timeout: float = 15, headers: dict | None = None) -> tuple:
    """One request's status and body, or (0, why) when the server dropped it."""
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=timeout)
    try:
        c.request(method, path, body or None, headers or {})
        r = c.getresponse()
        return r.status, r.read().decode("utf-8", "replace")
    except (http.client.HTTPException, OSError) as e:
        return 0, type(e).__name__
    finally:
        c.close()


def wears(path: str) -> str:
    """The key the page at `path` wears now."""
    return serve.worn(ask("GET", path)[1])


class Held:
    """One watch held on a thread of its own: its answer, and how long it
    took. `again`, it asks again each time a hold ends unmoved, as a
    browser does, for that many seconds."""

    def __init__(self, path: str, key: str, again: float = 0):
        self.got, self.took = None, 0.0
        self.thread = threading.Thread(target=self.run, args=(path, key, again), daemon=True)
        self.thread.start()
        time.sleep(0.3)

    def run(self, path: str, key: str, again: float) -> None:
        began = time.time()
        while True:
            self.got = ask("GET", f"/heard?path={path}&key={key}")[1]
            if self.got != key or time.time() - began >= again:
                break
        self.took = time.time() - began

    def answer(self, since: float, within: float = 10) -> tuple:
        """Its answer, and the seconds from `since` to it."""
        self.thread.join(within)
        return self.got, time.time() - since


def until(held, seconds: float = 10) -> None:
    """Wait for `held` to hold, `seconds` at most."""
    end = time.time() + seconds
    while not held() and time.time() < end:
        time.sleep(0.01)


def worst(asked: list, every: float, path: str, change) -> tuple:
    """A change no file carries, landed at its worst: just after its reader
    read, so it waits out the reader's whole period, `every`, with the
    pulse's recheck set to fall a second before the read that sees it. The
    watch's first ask beats the pulse, so its rechecks follow from there.

    The key the page wore, the key its watch was told, the reader's period
    as measured, how long before that read the pulse beat, and the seconds
    from the change to the telling."""
    was = wears(path)
    seen = len(asked)
    until(lambda: len(asked) > seen)
    time.sleep(max(0.0, asked[-1] + every - 1 - time.time()))
    seen, began = len(asked), time.time()
    watch = Held(path, was, again=10)
    until(lambda: len(asked) > seen)
    change()
    at, read, before = time.time(), asked[-1], asked[-2]
    beat = next((when for when, _ in list(NAMED) if when >= began), read)
    now, took = watch.answer(at, within=15)
    return was, now, read - before, read - beat, took


GOOD: list = []


def check(held: bool, line: str) -> None:
    GOOD.append(held)
    print(("" if held else "FAILED: ") + line)


for name in ("05", "06", "blind"):
    write(name, f"{name} as first written")
riding = TABLE.riding(route=rides, keyof=lambda path: "tree-key" if path == "/tree/05/" else None,
                      take=lambda form, path: "An address no page holds took this press.", hears=lambda: [])
# Each time the pulse set its watch: when, and the files it was handed.
NAMED: collections.deque = collections.deque(maxlen=64)
handed = riding["hears"]
riding["hears"] = lambda: NAMED.append((time.time(), found := handed())) or found
READ.start()
# Claude Code's record of each session whose program runs, 05's and 06's.
os.makedirs(os.path.join(ACCOUNT, "sessions"))
for pid in PS:
    with open(os.path.join(ACCOUNT, "sessions", f"{pid}.json"), "w") as f:
        json.dump({"pid": pid, "sessionId": f"00000000-0000-4000-8000-0000000{pid}"}, f)
# Stood in before 1100's two readers start, as 1100 starts them, since each reads at once.
panes.run, panes.subprocess, ports.PROCESSES.read, registry.LIVE = iterm, Pgrep(), ps, [ACCOUNT]
threading.Thread(target=panes.freshen, daemon=True).start()
ports.PROCESSES.start()
threading.Thread(target=serve.run, args=(SKILL, PORT, lambda: "home"),
                 kwargs={"recheck": RECHECK, "through": (*FAR, lambda path: TABLE.find(path) is not None), **riding},
                 daemon=True).start()
for _ in range(50):
    if os.path.exists(serve.pidfile(SKILL)):
        break
    time.sleep(0.1)
said, sys.stderr = sys.stderr, io.StringIO()
try:
    # A write shows in the next answer, within a second.
    live.CHECK = 60
    path = serve.address("trial", "05")
    was = wears(path)
    time.sleep(HEARD)
    drew, watch = DREW["05"], Held(path, was)
    at = time.time()
    write("05", "05 as written again")
    now, took = watch.answer(at)
    status, body = ask("GET", path)
    check(bool(now) and now != was and took < 1 and serve.worn(body) == now and "05 as written again" in body
          and DREW["05"] == drew + 1,
          f"A write showed {took:.2f} seconds on, in one draw: the watch was told {now}, and the page wears "
          f"{serve.worn(body)}.")

    # Another page's write wakes nothing. Nothing written, nothing drawn.
    other = serve.address("trial", "06")
    wears(other)
    time.sleep(HEARD)
    drew, drew_other, watch = DREW["05"], DREW["06"], Held(path, now)
    at = time.time()
    write("06", "06 as written again")
    still, took = watch.answer(at)
    quiet = still == now and took > serve.HOLD - 1.5 and DREW["05"] == drew and DREW["06"] == drew_other
    seen = "06 as written again" in ask("GET", other)[1] and DREW["06"] == drew_other + 1
    check(quiet and seen,
          f"Another page's write woke nothing: the watch held {took:.1f} seconds, through {int(took // RECHECK)} "
          f"rechecks, and page 05 was drawn {DREW['05'] - drew} times. Page 06 drew it once, when asked.")

    # A page moved with no file it names written is caught at the check, and named.
    live.CHECK = 2
    path = serve.address("blind", "05")
    was = wears(path)
    watch = Held(path, was, again=10)
    at = time.time()
    write("blind", "blind as written again")
    now, took = watch.answer(at, within=15)
    named = f"live: {path} moved with no file it names written" in sys.stderr.getvalue()
    check(bool(now) and now != was and took < live.CHECK + RECHECK + 1.5 and named,
          f"A page whose contract names no file was caught {took:.1f} seconds on, at the check"
          + (", and the log names it." if named else ". The log does not name it."))

    # Every 25 seconds, on live.py's own CHECK, an open page is drawn afresh
    # and compared: one moved with no file it names written is told, within
    # one recheck, and its address is named in the log.
    live.CHECK = CHECKED
    path = serve.address("blind", "06")
    began = time.time()
    was = wears(path)
    watch = Held(path, was, again=2 * AFRESH)
    write("blind", "blind as written once more")
    now, took = watch.answer(began, within=2 * AFRESH + serve.HOLD + 1)
    named = f"live: {path} moved with no file it names written" in sys.stderr.getvalue()
    check(bool(now) and now != was and CHECKED - 1 < took < AFRESH + RECHECK + 1 and named
          and "blind as written once more" in ask("GET", path)[1],
          f"A page moved with no file it names was told {took:.1f} seconds after its draw, at the {CHECKED}-second "
          f"check, within {AFRESH} and one {RECHECK}-second recheck"
          + (", and the log names its address." if named else ". The log does not name its address."))
    live.CHECK = 60

    # A look, which no file carries, moves its page.
    path = serve.address("looks", "05")
    was = wears(path)
    watch = Held(path, was)
    at = time.time()
    LOOK[0] += 1
    now, took = watch.answer(at)
    check(bool(now) and now != was and took < RECHECK + 1,
          f"A look that read differently moved its page {took:.1f} seconds on, with no file written.")

    # A pane closing, or a session's program ending, shows within 4 seconds,
    # on 1100's own timers. Each lands just after its reader read, and is
    # told once the next read moves, reader.moved(), never a recheck later.
    gone = "06000000-0000-0000-0000-000000000000"
    path = serve.address("panes", "05")
    was, now, every, lead, took = worst(ITERM_ASKED, panes.FRESH, path, lambda: PANES.pop(gone))
    body = ask("GET", path)[1]
    check(bool(now) and now != was and took < SHOWN and serve.worn(body) == now and gone not in body,
          f"A pane closed just after iTerm was read, every {every:.2f} seconds, the pulse beating {lead:.2f} "
          f"seconds before the next read: its page was told {took:.2f} seconds on, within {SHOWN}.")
    path = serve.address("panes", "06")
    was, now, every, lead, took = worst(PS_ASKED, ports.PROCESSES.every, path, lambda: PS.pop(40006))
    body = ask("GET", path)[1]
    check(bool(now) and now != was and took < SHOWN and serve.worn(body) == now and "Programs running: 1." in body,
          f"A session's program ended just after ps was read, every {every:.2f} seconds, the pulse beating "
          f"{lead:.2f} seconds before the next read: its page was told {took:.2f} seconds on, within {SHOWN}.")

    # A part that fails leaves the others. A page that fails leaves the rest.
    status, body = ask("GET", serve.address("parts", "05"))
    stands = status == 200 and "Second part stands." in body and "The first part failed to draw: KeyError" in body
    status, body = ask("GET", serve.address("broken", "05"))
    whole = (status == 200 and "This page failed to draw." in body and "ValueError: this page is broken" in body
             and serve.worn(body) not in ("", "whole"))
    check(stands and whole and ask("GET", serve.address("trial", "05"))[0] == 200,
          "A part that failed said so in its place, and the part after it drew. A page that failed whole said so, "
          "wears a key, and the page beside it drew.")

    # A press sent twice acts once, refused or done.
    path = serve.address("trial", "05")
    first, again = ask("POST", path, "act=mark&press=p1"), ask("POST", path, "act=mark&press=p1")
    refused, refused_again = ask("POST", path, "act=refuse&press=p2"), ask("POST", path, "act=refuse&press=p2")
    other = ask("POST", path, "act=mark&press=p3")
    once = (first[0] == again[0] == other[0] == 303 and ACTED.count("mark") == 2 and refused == refused_again
            and refused[0] == 409 and ACTED.count("refuse") == 1)
    # Sent again while the first still types, it waits, and answers the same.
    both: list = []
    senders = [threading.Thread(target=lambda: both.append(ask("POST", path, "act=type&press=p4"))) for _ in range(2)]
    for t in senders:
        t.start()
    for t in senders:
        t.join()
    flight = [s for s, _ in both] == [303, 303] and ACTED.count("type") == 1
    check(once and flight,
          f"A press sent twice acted once: done answered {first[0]} then {again[0]}, refused {refused[0]} then "
          f"{refused_again[0]}, and one sent again while it typed acted {ACTED.count('type')} time.")

    # Typing into one pane goes one press at a time.
    TYPING["most"] = 0
    senders = [threading.Thread(target=ask, args=("POST", path, f"act=type&press=t{i}")) for i in range(3)]
    for t in senders:
        t.start()
    for t in senders:
        t.join()
    check(TYPING["most"] == 1 and ACTED.count("type") == 4,
          f"Three presses typing into one pane typed {TYPING['most']} at a time.")

    # Data is kept as a page is. What is no page rides on behind the table:
    # its route, its key and its press. A fresh table draws the same key.
    status, body = ask("GET", "/data/05")
    data = status == 200 and json.loads(body) == {"nn": "05"} and TABLE.keyof("/data/05") == serve.worn((body.encode(),))
    lines, tree = ask("GET", "/p/trial/05/pane"), ask("GET", "/tree/05/")
    rode = (lines == (200, '<div id="offer">A pane\'s last lines.</div>') and tree[0] == 200
            and json.loads(tree[1]) == {"listed": ["a.md"]} and ask("GET", "/heard?path=/tree/05/&key=stale")[1] == "tree-key"
            and ask("POST", "/push", "x=1") == (409, "An address no page holds took this press.")
            and ask("GET", "/nowhere")[0] == 404)
    script = ask("GET", live.src("live.js"))
    shared = script[0] == 200 and script[1].startswith("/* live.js") and ask("GET", "/pages/nowhere.js")[0] == 404
    fresh = live.Table(PAGES).keyof(path) == wears(path)
    check(data and rode and shared and fresh,
          "Data is kept as a page is. A pane's lines and a folder's listing rode on behind the table, with their "
          "own key and press, the shared script is served, and a fresh table drew the same key.")

    # A file written as fast as it goes for a second, a thousand times and
    # more, draws its page five times at most, and the page ends on the last.
    path = serve.address("trial", "05")
    wears(path)
    time.sleep(HEARD)
    drew, end, stormed = DREW["05"], time.time() + 1, 0

    def asking() -> None:
        """A page's own loop: asks, is told, fetches its picture, asks again."""
        key = wears(path)
        while time.time() < end + 1:
            got = ask("GET", f"/heard?path={path}&key={key}", timeout=6)[1]
            if got and got != key:
                key = serve.worn(ask("GET", path)[1])

    asker = threading.Thread(target=asking, daemon=True)
    asker.start()
    while time.time() < end:
        stormed += 1
        write("05", f"written {stormed}")
    during = DREW["05"] - drew
    asker.join(8)
    check(stormed >= 1000 and 1 <= during <= 5 and f"written {stormed}" in ask("GET", path)[1],
          f"A file written {stormed} times in a second drew its page {during} times meanwhile, and the page ended "
          "on the last write.")

    # A page asked about for the first time hears a write at once: the pulse
    # sets its watch again, never waiting for its recheck.
    first_heard = []
    for name in ("07", "08", "09"):
        write(name, f"{name} as first written")
        path = serve.address("trial", name)
        was, began = wears(path), time.time()
        watch = Held(path, was)
        named = next((at - began for at, files in list(NAMED) if at >= began and file(name) in files), 99.0)
        at = time.time()
        write(name, f"{name} as written again")
        now, took = watch.answer(at)
        first_heard.append((named, took if now and f"{name} as written again" in ask("GET", path)[1] else 99.0))
    check(all(named < 0.25 and took < 1 for named, took in first_heard),
          "Three pages asked about for the first time: the pulse held each one's file "
          f"{', '.join(f'{named:.2f}' for named, _ in first_heard)} seconds after its first watch, and its write "
          f"showed {', '.join(f'{took:.2f}' for _, took in first_heard)} seconds on.")

    # A look read in the background moves its page the moment its reader's
    # answer does: a beat follows it at once, never a recheck later.
    path, read_told = serve.address("read", "05"), []
    for _ in range(3):
        watch = Held(path, wears(path))
        at = time.time()
        SEEN[0] += 1
        now, took = watch.answer(at)
        beat = next((when - at for when, _ in list(NAMED) if when >= at), 99.0)
        read_told.append((beat, took if now else 99.0))
    check(all(beat < 0.35 and took < 1 for beat, took in read_told),
          "Three answers read in the background moved: a beat followed "
          f"{', '.join(f'{beat:.2f}' for beat, _ in read_told)} seconds on, and the page was told "
          f"{', '.join(f'{took:.2f}' for _, took in read_told)} seconds on.")

    # Under a prefix passed through, a page the table holds stays here. Any
    # other address goes through, and so does a websocket asking at the page's own.
    kept, press = ask("GET", "/far/05?any=query"), ask("POST", "/far/05", "act=refuse&press=f1")
    gone = [ask("GET", "/far/elsewhere"), ask("POST", "/far/elsewhere", "act=mark"), ask("GET", "/far/"),
            ask("GET", "/far/05?token=t", headers={"Connection": "Upgrade", "Upgrade": "websocket"})]
    check(kept[0] == 200 and page.esc(read("05")) in kept[1] and press == (409, "This press is refused. Nothing was done.")
          and all(got == (502, f"{FAR[1]} is not answering.") for got in gone),
          f"Under a prefix passed through, the page the table holds was drawn and pressed here, {kept[0]} and "
          f"{press[0]}. Three other addresses, and a websocket asking at the page's own, went through, to a port "
          f"nothing answers on: {', '.join(str(s) for s, _ in gone)}.")
finally:
    logged, sys.stderr = sys.stderr.getvalue(), said
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    shutil.rmtree(TMP, ignore_errors=True)
if not all(GOOD):
    print(logged.strip(), file=sys.stderr)
sys.exit(0 if GOOD and all(GOOD) else 1)
