#!/usr/bin/env python3
"""Check a kept server comes back by itself: killed, frozen, and stopped on purpose.

The app door keeps 1100 up through lib/serve.py's keep(). Here keep()
keeps a server of one page on this session's port, 11NN. It is killed,
then frozen, and each time must answer again within ten seconds. Stopped
on purpose, it must stay down until the keeper's wait is over, cut here to
four seconds, then answer again.

Then keep() keeps `sessions-dashboard.py serve` itself, 1100's own code,
on the same port, over lib/trial.py's made-up folder, as the app door
keeps 1100. It is killed, then frozen, and each time must answer /health
within ten seconds of the kill, drawing the made-up folder again.

  serve-keeper-test.py [NN]              the checks; NN is 02 when none is given
  serve-keeper-test.py serve --port P    the server they keep
"""

import importlib.util
import json
import os
import shutil
import signal
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import serve  # noqa: E402

DASHBOARD = os.path.join(ROOT, ".claude", "tools", "sessions-dashboard.py")
# Set to a folder, the server kept is sessions-dashboard.py serve, its made-up folder made inside that one.
MADE_UP = "SERVE_KEEPER_TEST_MADE_UP"

if sys.argv[1:2] == ["serve"]:
    port = int(sys.argv[sys.argv.index("--port") + 1])
    if os.environ.get(MADE_UP):
        # A server killed leaves its made-up folder behind: inside the test's, which goes at its end.
        tempfile.tempdir = os.environ[MADE_UP]
        spec = importlib.util.spec_from_file_location("sessions_dashboard", DASHBOARD)
        dashboard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dashboard)
        with dashboard.trial.world():
            sys.argv = [DASHBOARD, "serve", "--port", str(port)]
            dashboard.main()
    else:
        serve.run(f"serve-keeper-test-{port % 100:02d}", port, lambda: "<p>kept</p>")
    sys.exit(0)

NN = sys.argv[1] if len(sys.argv) > 1 else "02"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"serve-keeper-test-{NN}"
serve.LEFT_DOWN = 4


def back(seconds: float, other_than: int = 0) -> float:
    """How long until the server answers again, under a pid other than
    `other_than`, or -1 once `seconds` are up."""
    began = time.time()
    while time.time() - began < seconds:
        if serve.healthy(PORT, 0.5) and serve.holder(PORT) != other_than:
            return time.time() - began
        time.sleep(0.1)
    return -1


good = []
problem = serve.start(SKILL, PORT, os.path.abspath(__file__))
if problem:
    print(f"The server to keep never came up: {problem}")
    sys.exit(1)
threading.Thread(target=serve.keep, args=(SKILL, PORT, os.path.abspath(__file__)), daemon=True).start()
try:
    pid = serve.holder(PORT)
    os.kill(pid, signal.SIGKILL)
    took = back(15, pid)
    good.append(0 <= took <= 10)
    print("Killed, the kept server " + (f"answered again {took:.1f} seconds on." if took >= 0
                                        else "never answered again."))

    pid = serve.holder(PORT)
    os.kill(pid, signal.SIGSTOP)
    took = back(20, pid)
    good.append(0 <= took <= 10)
    print("Frozen, the kept server " + (f"was replaced, and answered again {took:.1f} seconds on." if took >= 0
                                        else "was never replaced."))
    if took < 0:
        os.kill(pid, signal.SIGKILL)

    serve.stop(SKILL, PORT)
    time.sleep(2.5)
    stayed = not serve.ports.answering(PORT)
    took = back(15)
    good.append(stayed and took >= 0)
    print("Stopped on purpose, the kept server " + ("stayed down" if stayed else "came back at once")
          + (f", then answered again {took + 2.5:.1f} seconds after its stop." if took >= 0
             else ", and never answered again."))
finally:
    # The keeper leaves it down for good, then it stops, and its folder goes.
    serve.LEFT_DOWN = 10 ** 9
    serve.stop(SKILL, PORT)
    time.sleep(0.5)
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)


def made_up() -> bool:
    """Whether the server on PORT draws the made-up folder: home's model
    names its session 05's launch page."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/model", timeout=5) as r:
            return "launch:05" in json.loads(r.read())["pages"]
    except (OSError, ValueError, KeyError, TypeError):
        return False


def quiet(seconds: float = 5) -> None:
    """Wait until nothing answers on PORT, `seconds` at most."""
    began = time.time()
    while serve.ports.answering(PORT) and time.time() - began < seconds:
        time.sleep(0.1)


def dashboard() -> list:
    """1100's own code, sessions-dashboard.py serve, on PORT over the made-up
    folder, kept as the app door keeps 1100: killed, then frozen. Whether
    each came back within ten seconds of the kill, drawing the made-up
    folder again. A copy on a session's port keeps its pid in that
    session's server folder, which was there before the test, so only its
    pid file goes at the end."""
    skill, kept, held = f"sessions-dashboard-{PORT % 100:02d}", [], tempfile.mkdtemp(prefix="serve-keeper-test-")
    quiet()
    os.environ[MADE_UP] = held
    try:
        why = serve.start(skill, PORT, os.path.abspath(__file__))
        if why or not made_up():
            print(f"1100's code never came up on {PORT} over the made-up folder: {why or 'it draws another'}")
            return [False]
        threading.Thread(target=serve.keep, args=(skill, PORT, os.path.abspath(__file__)), daemon=True).start()
        for word, sig, seconds in (("Killed", signal.SIGKILL, 15), ("Frozen", signal.SIGSTOP, 20)):
            pid = serve.holder(PORT)
            if not pid:
                print(f"{word}: nothing listened on {PORT}, so 1100's code was never {word.lower()}.")
                kept.append(False)
                continue
            os.kill(pid, sig)
            took = back(seconds, pid)
            drawn = took >= 0 and made_up()
            kept.append(0 <= took <= 10 and drawn)
            print(f"{word}, 1100's code, kept, " + (
                f"answered /health again {took:.1f} seconds after, "
                + ("drawing the made-up folder." if drawn else "drawing something else.")
                if took >= 0 else f"never answered again in {seconds} seconds."))
            if took < 0 and sig == signal.SIGSTOP:
                os.kill(pid, signal.SIGKILL)
        return kept
    finally:
        # Its keeper leaves it down for good once its pid file goes.
        serve.stop(skill, PORT)
        quiet()
        del os.environ[MADE_UP]
        shutil.rmtree(held, ignore_errors=True)


sys.exit(0 if all(good + dashboard()) else 1)
