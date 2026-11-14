#!/usr/bin/env python3
"""Check each app chat's view follows only its own orders, on stand-ins, in WebKit and Chromium.

A server on this session's port, 11NN, draws 1100's home. Two homes stay
open side by side: /?app, view 1, and /?app=12, view 12, each on one made-up
session's tab. Orders reach them as lib/show.py's show() writes them, the
call the app door's show_page makes. It passes when:

  An order that stays moves neither view, and borders its spot in both.
  View 1's order opens System in view 1, and leaves view 12 where it stood.
  View 12's order opens Agenda in view 12, and leaves view 1 on System.
  View 1's next order opens Files in view 1, and leaves view 12 on Agenda.
  An order naming no view is refused, and moves neither.
  A second panel opened on view 12 is counted: 1100 says two hold it, and
  "View 12 is already open." Closed, it is gone within show.OPEN seconds,
  with no mark left behind.

  views-test.py [NN]

NN is this session's number, 99 when none is given.
"""

import json
import os
import shutil
import sys
import tempfile
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import trial  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "99"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"views-test-{NN}"
SERVING = len(sys.argv) > 3 and sys.argv[2] == "serve"
TMP = sys.argv[3] if SERVING else tempfile.mkdtemp(prefix="views-test-")
KIND = "explanation"
FRAMED = serve.address(KIND, NN)


def framed(nn: str) -> str:
    """The made-up tab: one item, as clarify-page.py ids it."""
    return page.render(f"{nn}-framed", [("", live.watch("s-home")
                                         + '<section class="item" id="t-1"><p>Item 1, Port.</p></section>')], refresh=0)


def model() -> dict:
    return {"sessions": {NN: {"name": "views", "colour": "red", "dashed": False, "tag": NN, "by": "", "topic": ""}},
            "pages": {f"{KIND}:{NN}": {"kind": KIND, "nn": NN, "label": "1 item", "waits": False,
                                       "since": 0, "port": 0, "path": FRAMED, "up": True, "side": "r"}},
            "hubs": {NN: {"overview": "", "tabs": [f"{KIND}:{NN}"], "nn": NN, "members": []}},
            "waits": [], "rail": [NN], "pid": os.getpid(), "code": "views"}


def view_of(path: str) -> str:
    """The view /show's address names, as sessions-dashboard.py reads it."""
    return (urllib.parse.parse_qs(path.partition("?")[2]).get("view") or ["1"])[0]


def route(path: str):
    bare = path.partition("?")[0]
    if bare == "/":
        return None
    if bare == "/model":
        return json.dumps(model()).encode(), "application/json"
    if bare == "/show":
        return json.dumps(show.read(view_of(path))).encode(), "application/json"
    if bare == "/views":
        return json.dumps(show.homes()).encode(), "application/json"
    if bare == "/app":
        return b'{"line": ""}', "application/json"
    return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404


def keyof(path: str):
    bare = path.partition("?")[0]
    if bare == "/show":
        # As sessions-dashboard.py's keyof: an app home names itself.
        show.asked(view_of(path), (urllib.parse.parse_qs(path.partition("?")[2]).get("home") or [""])[0])
        return show.key(view_of(path))
    return "" if bare == "/app" else None


def take(form: dict, path: str) -> str:
    """The test's one press: an order made by show(), as the app door makes
    it. What show() said goes to the server's log."""
    if path == "/trial/order":
        said = show.show(**json.loads(form["text"][0]))
        print(f"SAID {said}", flush=True)
        return ""
    return "Nothing at this address takes a press."


if SERVING:
    show.FOLDER, show.ORDER = TMP, os.path.join(TMP, "order.json")
    # The made-up session is the one show() finds running.
    show.launch.live = lambda: {NN}
    workstation = page.tool("workstation")
    workstation.model = model
    table = live.Table([live.Page(serve.address(KIND, r"(\d{2})"), framed, files=lambda nn: [])])
    serve.run(SKILL, PORT, workstation.home, recheck=1, **table.riding(route=route, keyof=keyof, take=take,
                                                                          hears=lambda: [TMP]))
    sys.exit(0)


BROWSERS = trial.SERVER + r"""
const nn = process.env.VIEWS_NN, framed = process.env.VIEWS_FRAMED, kind = process.env.VIEWS_KIND;
const order = o => post('/trial/order', {text: JSON.stringify(o)});
(async () => {
  for (const engine of engines) {
    await up();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1400, height: 900}});
    const views = [];
    for (const address of ['/?app', '/?app=12']) {
      const page = await context.newPage();
      await page.goto(base + address + '#' + nn + '/' + kind + ':' + nn);
      views.push(page);
    }
    const inner = page => page.frames().find(f => new URL(f.url()).pathname === framed);
    for (const page of views) {
      for (let i = 0; i < 100 && !(inner(page) && await inner(page).$('#t-1')); i++) await wait(100);
      if (!inner(page)) throw new Error('no framed tab: ' + page.url());
    }
    await wait(1500);
    // Where a view stands: the visible frames' addresses, or home's own hash.
    const where = page => page.evaluate(() => location.hash + ' | ' + [...document.querySelectorAll('iframe')]
      .filter(f => f.offsetParent).map(f => new URL(f.src, location.href).pathname).join(','));
    const both = async () => [await where(views[0]), await where(views[1])];
    const start = await both();

    await order({target: nn + ':' + kind, mark: '#t-1', stay: true});
    await wait(500);
    const marked = [];
    for (const page of views) marked.push(await inner(page).evaluate(() => document.getElementById('t-1').classList.contains('ws-mark')));
    await wait(2500);
    const afterStay = await both();

    await order({target: 'system', view: '1'});
    await wait(3000);
    const afterOne = await both();

    await order({target: 'agenda', view: '12'});
    await wait(3000);
    const afterTwo = await both();

    await order({target: 'files', view: '1'});
    await wait(3000);
    const afterThird = await both();

    await order({target: 'library'});
    await wait(3000);
    const afterNone = await both();

    // The panels 1100 counts right now, then with a second one on view 12, then with it closed.
    const counted = async () => await (await fetch(base + '/views')).json();
    const alone = await counted();
    const second = await context.newPage();
    await second.goto(base + '/?app=12');
    await wait(4000);
    const twice = await counted();
    await second.close();
    await wait((+process.env.VIEWS_OPEN + 5) * 1000);
    const closed = await counted();

    console.log(JSON.stringify({engine: engine.name(), start, marked, afterStay, afterOne, afterTwo, afterThird, afterNone,
                                alone, twice, closed}));
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

try:
    with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", TMP], PORT, TMP):
        r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "VIEWS_NN": NN, "VIEWS_FRAMED": FRAMED,
                                           "VIEWS_KIND": KIND, "VIEWS_OPEN": str(show.OPEN)})
finally:
    with open(os.path.join(TMP, "server.log")) as f:
        logged = f.read()
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    shutil.rmtree(TMP, ignore_errors=True)

seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
refused = logged.count(f"SAID {show.NO_VIEW}")
ok = len(seen) == 2 and refused == len(seen)
for s in seen:
    one, two = 0, 1
    held = {"The order that stays moved neither view": s["afterStay"] == s["start"],
            "Its spot was bordered in both views": s["marked"] == [True, True],
            "View 1's order moved view 1": s["afterOne"][one] != s["start"][one],
            "View 1's order left view 12 where it stood": s["afterOne"][two] == s["start"][two],
            "View 12's order moved view 12": s["afterTwo"][two] != s["afterOne"][two],
            "View 12's order left view 1 where it stood": s["afterTwo"][one] == s["afterOne"][one],
            "The two views stand on different pages": s["afterTwo"][one] != s["afterTwo"][two],
            "View 1's next order moved view 1 again": s["afterThird"][one] != s["afterTwo"][one],
            "View 1's next order left view 12 where it stood": s["afterThird"][two] == s["afterTwo"][two],
            "An order naming no view moved neither": s["afterNone"] == s["afterThird"],
            "One panel holds each view": s["alone"] == {"1": 1, "12": 1},
            "A second panel on view 12 is counted": s["twice"] == {"1": 1, "12": 2},
            "The chat is told View 12 is already open": show.already("12", s["twice"].get("12", 0)) == "View 12 is already open.",
            "The closed panel is gone, with no mark left": s["closed"] == {"1": 1, "12": 1}}
    for name, good in held.items():
        print(("" if good else "FAILED: ") + f"{name}, in {s['engine']}.")
        ok = ok and good
    print(f"  {s['engine']}: view 1 {s['start'][one]} → {s['afterOne'][one]} → {s['afterThird'][one]}; "
          f"view 12 {s['start'][two]} → {s['afterTwo'][two]}; panels {s['alone']} → {s['twice']} → {s['closed']}")
print(("" if refused == len(seen) else "FAILED: ") + f"The order naming no view was refused, {refused} of {len(seen)} times.")
if len(seen) != 2:
    print(f"FAILED: the browsers ended early. {r.stdout.strip()[-800:]} {r.stderr.strip()[-1500:]}")
    if "Traceback" in logged:
        print(logged.strip()[-1500:])
sys.exit(0 if ok else 1)
