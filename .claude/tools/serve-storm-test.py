#!/usr/bin/env python3
"""Replay the reload storm on the contract, and check 1100 stays whole through it.

At 09:19 on 10 November my launch page for session 20, framed by home,
moved with no file written, and was asked about without pause. Its draw
waited on iTerm, so each load given up left a thread waiting. 1100 ran out
of open files, then of threads, and by 09:24 that page was drawn 353 times
in ten seconds.

Here a server on this session's port, 11NN, draws home's own script around
pages on the contract, lib/live.py's. Each moves with no file written: a
look, as a pane opening, reads anew four times a second. The fast page
draws at once; the slow one takes three seconds, as a launch page waiting
on iTerm. WebKit, my pane's engine, and Chromium each open both, alone and
then framed in home, and check promise 9: never more than one /heard open
at a time for a page, its asks and picture fetches under the bounds named
below, the picture seen moving, and current once the look stops.

Then 400 loads of a third page are given up while the slow one draws, and
cost no draw; 200 watches are held at once; a route fails. Through it all,
promise 10: threads and open files stay under the ceilings named below,
and no more than serve.MOST requests are served at once.

  serve-storm-test.py [NN] [--count]

NN is this session's number, 02 when none is given. --count prints what it
counted and judges nothing.
"""

import http.client
import json
import os
import shutil
import socket
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import trial  # noqa: E402

NAMED = [a for a in sys.argv[1:] if not a.startswith("--")]
NN = NAMED[0] if NAMED else "02"
COUNT = "--count" in sys.argv
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"serve-storm-test-{NN}"
# A held watch answers after this long, so the 200 held at once end soon.
serve.HOLD = 4
# The most requests served at once, as lib/serve.py holds it when this file
# is read. Promise 10's ceilings are drawn from it.
MOST = serve.MOST
# The server's safety-net beat, in seconds: with no file written, a beat
# comes this often, and only a beat moves a page's key at /heard.
RECHECK = 1
# One draw of the slow page, in seconds.
SLOW = 3
# Each page's address. Home frames the fast and the slow one, as tabs. The
# third is only ever loaded and given up.
AT = {"fast": serve.address("explanation", NN), "slow": serve.address("launch", NN),
      "given": serve.address("handover", NN)}
KIND = {"fast": "explanation", "slow": "launch"}
# How long each page is watched while it moves, in seconds.
WATCHED = {"fast": 8, "slow": 20}
# The look every page reads, as a pane opening: TICK, moved four times a
# second while MOVING. The third page's look reads anew on every read.
TICK, MOVING, READS, TICKING = [0], [False], [0], threading.Lock()
# Each page's draws begun.
DREW = {k: 0 for k in AT}
# The most threads and open files seen: the whole run's, and since the last
# reset. Open files leave out the test's own client sockets, OWN.
PEAK = {"threads": 0, "files": 0}
PHASE = {"threads": 0, "files": 0}
OWN, OWNING = [0], threading.Lock()
# Home's whole model: one session, one hub, two tabs, and the mark of home's
# own code, which never moves here, so home never reloads.
MODEL = {"sessions": {NN: {"name": "storm", "colour": "red", "dashed": False, "tag": NN, "by": "", "topic": ""}},
         "pages": {f"{KIND[w]}:{NN}": {"kind": KIND[w], "nn": NN, "label": w, "waits": False, "since": 0,
                                       "port": 0, "path": AT[w], "up": True, "side": "r"} for w in KIND},
         "hubs": {NN: {"overview": "", "tabs": [f"{KIND[w]}:{NN}" for w in KIND], "nn": NN, "members": []}},
         "waits": [], "rail": [NN], "code": "storm"}

workstation = page.tool("workstation")
workstation.model = lambda: MODEL


def own(n: int) -> None:
    with OWNING:
        OWN[0] += n


def ticker() -> None:
    while True:
        with TICKING:
            if MOVING[0]:
                TICK[0] += 1
        time.sleep(0.25)


def drawn(which: str, nn: str) -> str:
    """One page on the contract: the look as it read, and how often it was
    drawn, which moves on every draw with nothing it names moved."""
    tick = TICK[0]
    DREW[which] += 1
    if which == "slow":
        time.sleep(SLOW)
    return page.render(f"{nn}-{which}", [("", live.watch(f"storm-{which}") + f'<p id="tick">{tick}</p>'
                                          f'<p>Drawn {DREW[which]} times.</p>')], refresh=0)


def read() -> int:
    READS[0] += 1
    return READS[0]


TABLE = live.Table([
    live.Page(serve.address("explanation", r"(\d{2})"), lambda nn: drawn("fast", nn), looks=(lambda: TICK[0],)),
    live.Page(serve.address("launch", r"(\d{2})"), lambda nn: drawn("slow", nn), looks=(lambda: TICK[0],)),
    live.Page(serve.address("handover", r"(\d{2})"), lambda nn: drawn("given", nn), looks=(read,)),
])


def counts(reset: bool) -> bytes:
    """What the server counted, and its peaks since the last reset."""
    got = {"pid": os.getpid(), "drew": dict(DREW), "tick": TICK[0], "threads": threading.active_count(),
           **{f"most_{k}": v for k, v in PHASE.items()}}
    if reset:
        PHASE.update(threads=0, files=0)
    return json.dumps(got).encode()


def route(path: str):
    bare, _, query = path.partition("?")
    if bare == "/":
        return None
    if bare == "/model":
        return json.dumps(MODEL).encode(), "application/json"
    if bare == "/show":
        return json.dumps(show.read()).encode(), "application/json"
    if bare == "/app":
        return b'{"line": ""}', "application/json"
    if bare == "/trial/move":
        with TICKING:
            MOVING[0] = query == "on"
            return json.dumps({"tick": TICK[0]}).encode(), "application/json"
    if bare == "/counts":
        return counts(query == "reset"), "application/json"
    if bare == "/raise":
        raise ValueError("this route fails")
    return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404


def keyof(path: str):
    bare = path.partition("?")[0]
    return show.key() if bare == "/show" else "" if bare == "/app" else None


def peaks() -> None:
    """Threads, the threads serve.run serves requests on, by the name
    socketserver gives them, and open files, every 20 ms."""
    while True:
        every = threading.enumerate()
        threads, files = len(every), len(os.listdir("/dev/fd")) - OWN[0]
        served = sum("process_request_thread" in t.name for t in every)
        for p in (PEAK, PHASE):
            p["threads"], p["files"] = max(p["threads"], threads), max(p["files"], files)
            p["served"] = max(p.get("served", 0), served)
        time.sleep(0.02)


def ask(method: str, path: str, body: str = "") -> tuple:
    """One request's status and body, or (0, why) when the server dropped it."""
    own(1)
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=15)
    try:
        c.request(method, path, body or None)
        r = c.getresponse()
        return r.status, r.read().decode("utf-8", "replace")
    except (http.client.HTTPException, OSError) as e:
        return 0, type(e).__name__
    finally:
        c.close()
        own(-1)


def raw(path: str) -> socket.socket:
    """One GET sent on a socket of its own, its answer left unread. Counted
    as the test's own until shut()."""
    own(1)
    s = socket.create_connection(("127.0.0.1", PORT), timeout=15)
    s.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{PORT}\r\n\r\n".encode())
    return s


def shut(s: socket.socket) -> None:
    s.close()
    own(-1)


def status(s: socket.socket) -> int:
    """The status a raw GET was answered with, or 0 when it was dropped."""
    try:
        head = s.recv(64)
        return int(head.split()[1]) if head.startswith(b"HTTP/") else 0
    except (OSError, ValueError, IndexError):
        return 0
    finally:
        shut(s)


# Promise 9's bounds, for a page seen `seconds` while its look moves.
#
# A page's key at /heard moves only on a beat: serve.py's known() draws it
# once a beat, whoever asks. With no file written, a beat comes every
# RECHECK seconds, plus one when a watch is first opened: beats.
#
# Picture fetches: a page is told at most once a beat, and fetches its
# picture once per telling, so at most beats + 1. live.js's own floor, one
# fetch per 200 ms, is 5 a second whatever the server does.
#
# Asks: each /heard waits for its answer before the next. One answers on a
# beat that moved the page, or HOLD seconds on. Home also asks once more
# at once after telling a page, and then, told nothing, waits a second.
# So at most 2 beats + seconds / HOLD + 2.
#
# Seen moving, the lower bound: a fast page takes at most two beats to
# show a move. A slow one takes the draw in flight, the draw of its key,
# and the two draws of its fetch, serve.py's drawn() asking keyof and then
# route: 4 SLOW + 2 beats. So at least 1 + seconds // that many distinct
# pictures. Current once the look stops: within that same span, plus the
# second home waits after telling nothing.
def cycle(which: str) -> float:
    return 2 * RECHECK + (4 * SLOW if which == "slow" else 0)


def bounds(b: dict) -> dict:
    beats = b["seconds"] / RECHECK + 1
    return {"asks": 2 * beats + b["seconds"] / serve.HOLD + 2, "pictures": beats + 1,
            "distinct": 1 + int(WATCHED[b["which"]] // cycle(b["which"])),
            "current": (cycle(b["which"]) + 1) * 1000}


# What each page counts in itself: every /heard it opens, how many stand
# open at once, which pages it asked about, and each fetch of its own
# picture. The fetch handed back resolves once the count is down, so an ask
# that follows an aborted one is never counted as standing beside it.
COUNTER = r"""() => {
  const f = window.fetch, s = window.__storm = {open: 0, most: 0, asks: 0, pictures: 0, about: []};
  window.fetch = function (input, options) {
    const u = new URL(typeof input === 'string' ? input : input.url, location.href);
    const heard = u.pathname === '/heard';
    if (heard) {
      s.asks++; s.open++; s.most = Math.max(s.most, s.open);
      for (const p of u.searchParams.getAll('path')) if (!s.about.includes(p)) s.about.push(p);
    } else if (u.pathname === location.pathname && !(options && options.method && options.method !== 'GET')) s.pictures++;
    const p = f.apply(this, arguments);
    return heard ? p.finally(() => { s.open--; }) : p;
  };
}"""

# Each engine opens the fast and the slow page, alone and then framed in
# home. Once the page is watched, its look moves for WATCHED seconds, the
# picture shown read every 250 ms; then the look stops, and the page is
# read until it shows the last tick.
BROWSERS = r"""
const base = process.env.STORM_BASE, nn = process.env.STORM_NN, at = JSON.parse(process.env.STORM_AT);
const kind = JSON.parse(process.env.STORM_KIND), watched = JSON.parse(process.env.STORM_WATCHED);
const current = JSON.parse(process.env.STORM_CURRENT), slow = +process.env.STORM_SLOW;
const get = async p => (await fetch(base + p)).json();
(async () => {
  for (const engine of engines) {
    const browser = await engine.launch({headless: true});
    for (const framed of [false, true]) for (const which of ['fast', 'slow']) {
      const path = at[which];
      await get('/trial/move?on');
      const context = await browser.newContext({viewport: {width: 1400, height: 900}});
      await context.addInitScript(COUNTER);
      const page = await context.newPage();
      let loads = 0, homes = 0;
      page.on('request', r => {
        if (!r.isNavigationRequest()) return;
        const u = new URL(r.url());
        if (u.pathname === path) loads++;
        if (u.pathname === '/') homes++;
      });
      await page.goto(base + (framed ? '/#' + nn + '/' + kind[which] + ':' + nn : path));
      const inner = () => framed ? page.frames().find(f => f !== page.mainFrame() && new URL(f.url()).pathname === path)
                                 : page.mainFrame();
      const read = async (frame, fn) => { try { return frame ? await frame.evaluate(fn) : null; } catch (e) { return null; } };
      const stats = frame => read(frame, () => window.__storm && {...window.__storm, at: Date.now()});
      const tick = () => read(inner(), () => { const t = document.getElementById('tick'); return t && t.textContent; });
      let armed = false;
      for (let i = 0; i < 300 && !armed; i++) {
        const s = await stats(page.mainFrame());
        armed = !!s && s.about.includes(path) && !!(await tick());
        if (!armed) await wait(100);
      }
      if (!armed) throw new Error(engine.name() + ': ' + path + ' was never watched');
      await wait(1000);
      const a0 = await stats(page.mainFrame()), p0 = await stats(inner()), c0 = await get('/counts');
      const seen = new Set(), began = Date.now();
      while (Date.now() - began < watched[which] * 1000) { const t = await tick(); if (t) seen.add(t); await wait(250); }
      const a1 = await stats(page.mainFrame()), p1 = await stats(inner()), c1 = await get('/counts');
      const last = String((await get('/trial/move?off')).tick), stopped = Date.now();
      let ended = -1;
      while (Date.now() - stopped < current[which] + 5000) {
        if (await tick() === last) { ended = Date.now() - stopped; break; }
        await wait(100);
      }
      const a2 = await stats(page.mainFrame()), p2 = await stats(inner());
      console.log(JSON.stringify({engine: engine.name(), mode: framed ? 'framed' : 'alone', which,
                                  seconds: (a1.at - a0.at) / 1000, asks: a1.asks - a0.asks,
                                  pictures: p1.pictures - p0.pictures, drew: c1.drew[which] - c0.drew[which],
                                  most: a2.most, own: framed ? p2.asks : 0, loads, homes,
                                  distinct: seen.size, ended}));
      await context.close();
      // The draws a closed page left in flight end before the next is counted.
      await wait(which === 'slow' ? 2 * slow * 1000 + 1000 : 1000);
    }
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
""".replace("COUNTER", COUNTER)


def browsers() -> list:
    """Each engine's counts, read from the browsers' own lines. An engine
    with no build is said so, and counts as not run."""
    r = trial.browsers(BROWSERS, {"STORM_BASE": f"http://127.0.0.1:{PORT}", "STORM_NN": NN,
                                  "STORM_AT": json.dumps(AT), "STORM_KIND": json.dumps(KIND),
                                  "STORM_WATCHED": json.dumps(WATCHED), "STORM_SLOW": str(SLOW),
                                  "STORM_CURRENT": json.dumps({w: (cycle(w) + 1) * 1000 for w in KIND})})
    if r.returncode:
        print(r.stderr.strip() or "The browsers ended with no word.", file=sys.stderr)
    return ([json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
            + [{"engine": line.split()[0], "missing": True} for line in r.stdout.splitlines()
               if line.endswith(" missing")])


def given_up(many: int = 400) -> dict:
    """`many` loads of the third page, each given up 30 ms on, while the
    slow page's draw holds the queue, then a press. The third page's look
    reads anew on every read, so any load that reached its turn would draw
    it: only serve.py's drawn(), finding its asker hung up, spares it."""
    with TICKING:
        MOVING[0] = True
        was = TICK[0]
    # The look moves first, so the slow page's picture is due a draw.
    while TICK[0] == was:
        time.sleep(0.05)
    drew, blocked = dict(DREW), []
    blocker = threading.Thread(target=lambda: blocked.append(ask("GET", AT["slow"])[0]))
    blocker.start()
    for _ in range(100):
        if DREW["slow"] > drew["slow"]:
            break
        time.sleep(0.02)
    asked = [raw(AT["given"]) for _ in range(many)]
    time.sleep(0.03)
    for s in asked:
        shut(s)
    press = ask("POST", "/", "x=1")[0]
    blocker.join()
    time.sleep(1)
    with TICKING:
        MOVING[0] = False
    return {"drew": DREW["given"] - drew["given"], "slow": DREW["slow"] - drew["slow"],
            "blocked": blocked[0] if blocked else 0, "press": press}


def held(many: int = 200) -> dict:
    """`many` watches held at once, a press posted while they stand, then
    each one's answer."""
    base = threading.active_count()
    PHASE.update(threads=0, files=0)
    worn = serve.hashed(json.dumps(MODEL))
    asked = [raw(f"/heard?path=/model&key={worn}") for _ in range(many)]
    time.sleep(0.5)
    press = ask("POST", "/", "x=1")[0]
    got = [status(s) for s in asked]
    return {"held": got.count(200), "shed": got.count(503), "dropped": got.count(0),
            "most": PHASE["threads"] - base, "press": press}


threading.Thread(target=serve.run, args=(SKILL, PORT, workstation.home),
                 kwargs={"recheck": RECHECK, **TABLE.riding(route=route, keyof=keyof, take=lambda form, path: "",
                                                             hears=lambda: [])},
                 daemon=True).start()
for _ in range(50):
    if os.path.exists(serve.pidfile(SKILL)):
        break
    time.sleep(0.1)
threading.Thread(target=ticker, daemon=True).start()
threading.Thread(target=peaks, daemon=True).start()
time.sleep(0.2)
# The port answers from this process, or another server holds it.
mine = ask("GET", "/counts")
if mine[0] != 200 or json.loads(mine[1] or "{}").get("pid") != os.getpid():
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    sys.exit(f"{PORT} is not this test's server: {mine[0] or mine[1]}. Nothing was checked.")
# Promise 10's ceilings, drawn from what stands before any storm: this
# process's threads now (main, serve.run's, the pulse, the ticker and the
# peaks), and its open files now (the listening socket, the pulse's pipe and
# kqueue, the log and the interpreter's own).
#
# Threads serving requests: every request served holds one, at most MOST
# at once (serve.run's BoundedSemaphore), and a press, served apart from
# it, one more: MOST + 1. Threads in all: FIXED + MOST + 1, and the one the
# test itself starts to hold the slow draw while loads are given up.
#
# Open files, the test's own client sockets apart: every request served
# holds its socket, MOST + 1; the browsers' Node holds three pipes to this
# process; the pulse opens one kqueue each beat before it closes the last:
# FIXED + MOST + 1 + 3 + 1.
FIXED = {"threads": threading.active_count(), "files": len(os.listdir("/dev/fd")) - OWN[0]}
NAMES = sorted(t.name for t in threading.enumerate())
CEILING = {"served": MOST + 1, "threads": FIXED["threads"] + MOST + 1 + 1, "files": FIXED["files"] + MOST + 1 + 3 + 1}
PEAK.update(threads=0, files=0, served=0)
try:
    seen = browsers()
    gone = given_up()
    watches = held()
    failed = ask("GET", "/raise")
finally:
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)

good = []
for b in seen:
    if b.get("missing"):
        print(f"Home in {b['engine']} was not run: its build is not installed.")
        good.append(False)
        continue
    most = bounds(b)
    calm = (b["most"] <= 1 and b["own"] == 0 and b["loads"] == 1 and b["homes"] == (b["mode"] == "framed")
            and b["asks"] <= most["asks"] and b["pictures"] <= most["pictures"])
    current = b["distinct"] >= most["distinct"] and 0 <= b["ended"] <= most["current"]
    good.append(calm and current)
    print(f"{b['which'].capitalize()} page {b['mode']} in {b['engine']}, {b['seconds']:.1f} s moving: "
          f"{b['asks']} asks (at most {most['asks']:.0f}), {b['pictures']} picture fetches (at most "
          f"{most['pictures']:.0f}), {b['drew']} draws, {b['most']} /heard open at once, {b['own']} of its own "
          f"when framed, {b['loads']} load, {b['distinct']} pictures seen (at least {most['distinct']}), "
          f"current {b['ended']} ms after it stopped (within {most['current']:.0f})"
          + (": calm and current." if calm and current else ": calm, but stale." if calm
             else ": a storm."))
good.append({b["engine"] for b in seen if not b.get("missing")} == {"webkit", "chromium"})
spared = gone["drew"] == 0 and gone["slow"] >= 1 and gone["blocked"] == 200 and gone["press"] == 303
good.append(spared)
print(f"400 loads given up while the slow page drew {gone['slow']} times: {gone['drew']} draws of theirs, "
      f"the slow load answered {gone['blocked']}, and a press answered {gone['press']}"
      + (": none was drawn for nobody." if spared else ": 1100 drew for askers long gone."))
capped = watches["held"] <= MOST and watches["held"] + watches["shed"] == 200 and watches["press"] == 303
good.append(capped)
print(f"200 watches held at once: {watches['held']} held, {watches['shed']} told busy, {watches['dropped']} dropped, "
      f"{watches['most']} threads at most, and a press answered {watches['press']}"
      + (f": the ceiling of {MOST} held." if capped else ": no ceiling held."))
under = all(PEAK[k] <= CEILING[k] for k in CEILING)
good.append(under)
print(f"Through the storm, {PEAK['served']} threads serving requests at most (ceiling {CEILING['served']}: "
      f"{MOST} served + 1 press), {PEAK['threads']} threads in all (ceiling {CEILING['threads']}: "
      f"{FIXED['threads']} standing, {', '.join(NAMES)}, + {MOST} served + 1 press + the test's own blocker) "
      f"and {PEAK['files']} open files at most "
      f"(ceiling {CEILING['files']}: {FIXED['files']} standing + {MOST} served + 1 press + 3 pipes + 1 kqueue)"
      + (": both held." if under else ": a ceiling broke."))
said = failed[0] == 500 and failed[1].strip().endswith(".")
good.append(said)
print("A route that fails " + (f"answered 500: {failed[1].strip()}" if said
                               else f"answered {failed[0] or 'nothing'}: {failed[1].strip()[:80]}"))
sys.exit(0 if COUNT or all(good) else 1)
