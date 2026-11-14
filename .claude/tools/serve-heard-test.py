#!/usr/bin/env python3
"""Check that a held /heard survives a socket numbered past 1024.

A held watch asks whether its asker hung up. select() refuses a file
numbered 1024 or more, so at 12:16 on 6 November, once 1100 held that
many, every held watch broke. Here a server on this session's port,
11NN, holds a watch on a socket numbered past 1024. It must answer once
the hold is up. NN is the first argument, 02 when none is given.

A page drawn off the queue, as the launch page is, must hold its watch
once it wears its new key, though no file was written: at 09:24 on 10
November one reloaded 353 times in ten seconds.
"""

import http.client
import io
import os
import resource
import shutil
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import serve  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "02"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"serve-heard-test-{NN}"
serve.HOLD = 2
# A page drawn off the queue, as the launch page is, whose key moves with
# no file written, as a pane opening moves it.
MOVES = ["a"]


def route(path):
    if path != "/typed":
        return None
    worn = MOVES[0]
    return serve.Typing(lambda: f'<div id="watch" data-key="{worn}"></div>')


threading.Thread(target=serve.run, args=(SKILL, PORT, lambda: '<div id="watch" data-key="k"></div>'),
                 kwargs={"recheck": 1.5, "route": route,
                         "keyof": lambda p: MOVES[0] if p == "/typed" else None}, daemon=True).start()
for _ in range(50):
    if os.path.exists(serve.pidfile(SKILL)):
        break
    time.sleep(0.1)
# A new socket takes the lowest free number: fill every one below 1100,
# so both ends of the watch land past 1024.
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (max(soft, min(hard, 4096)), hard))
filler = []
while True:
    fd = os.open(os.devnull, os.O_RDONLY)
    if fd >= 1100:
        os.close(fd)
        break
    filler.append(fd)
try:
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    c.request("GET", "/heard?path=/&key=k")
    try:
        r = c.getresponse()
        held = r.status == 200 and r.read() == b"k"
    except (http.client.RemoteDisconnected, ConnectionError):
        held = False
finally:
    for fd in filler:
        os.close(fd)
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
print("A watch held on a socket past file 1024 " + ("answered once its hold was up." if held
                                                     else "broke before it answered."))

# A burst names itself: one watch held, then BURST draws of a launch page
# asked by home, from one browser.
said, sys.stderr = sys.stderr, io.StringIO()
watcher = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
watcher.request("GET", "/heard?path=/&key=k")
time.sleep(0.3)
for _ in range(serve.BURST):
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    c.request("GET", "/p/launch/00", headers={"Referer": f"http://127.0.0.1:{PORT}/",
                                               "User-Agent": "Mozilla/5.0 (Macintosh) Chrome/156.0 Safari/537.36"})
    c.getresponse().read()
logged, sys.stderr = sys.stderr.getvalue(), said
named = f"{serve.BURST} draws in 10 seconds, 1 watches held, from /p/launch/00 for / by Chrome/156.0 Safari/537.36" in logged
print("A burst of draws " + ("names its address, its page, its browser and the watches held."
                             if named else f"was named as: {logged.strip() or 'nothing'}"))
watcher.close()


def get(path: str) -> str:
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    c.request("GET", path)
    return c.getresponse().read().decode()


# A page drawn off the queue, its key moved with no file written, is never
# told it moved once it wears the new key: its watch holds.
was = get("/typed").split('data-key="')[1].split('"')[0]
threading.Thread(target=get, args=(f"/heard?path=/typed&key={was}",), daemon=True).start()
time.sleep(0.2)
MOVES[0] = "b"
wears = get("/typed").split('data-key="')[1].split('"')[0]
asked = time.time()
told = get(f"/heard?path=/typed&key={wears}")
calm = wears == "b" and told == "b" and time.time() - asked >= 1
print("A page drawn off the queue " + ("holds its watch once it wears its new key." if calm
                                       else f"wears {wears}, and was told {told} at once: it reloads nonstop."))
sys.exit(0 if held and named and calm else 1)
