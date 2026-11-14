#!/usr/bin/env python3
"""Check a save never moves my browser, on stand-ins, in WebKit and Chromium.

A server on this session's port, 11NN, draws 1100's home, opened as the
app chat's own, /?app, on one made-up session's tab, its item 1 drawn as
Clarify ids it. The app door's orders reach it as its saves make them: a
wave answer on that tab, then a
setting on System, each staying. Then one order that moves, as show_page
makes it. It passes when:

  The wave answer's order leaves home where it stood, and borders the
  spot it changed in the page it already shows.
  The setting's order leaves home where it stood: System never opens.
  show_page's order, the control, does open System.

  stay-test.py [NN]

NN is this session's number, 99 when none is given.
"""

import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import trial  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "99"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"stay-test-{NN}"
SERVING = len(sys.argv) > 3 and sys.argv[2] == "serve"
TMP = sys.argv[3] if SERVING else tempfile.mkdtemp(prefix="stay-test-")
KIND = "explanation"
FRAMED = serve.address(KIND, NN)


def framed(nn: str) -> str:
    """The made-up Clarify tab: one item, as clarify-page.py ids it."""
    return page.render(f"{nn}-framed", [("", live.watch("s-home")
                                         + '<section class="item" id="t-1"><p>Item 1, Port.</p></section>')], refresh=0)


def model() -> dict:
    return {"sessions": {NN: {"name": "stay", "colour": "red", "dashed": False, "tag": NN, "by": "", "topic": ""}},
            "pages": {f"{KIND}:{NN}": {"kind": KIND, "nn": NN, "label": "1 item", "waits": False,
                                       "since": 0, "port": 0, "path": FRAMED, "up": True, "side": "r"}},
            "hubs": {NN: {"overview": "", "tabs": [f"{KIND}:{NN}"], "nn": NN, "members": []}},
            "waits": [], "rail": [NN], "pid": os.getpid(), "code": "stay"}


def route(path: str):
    bare = path.partition("?")[0]
    if bare == "/":
        return None
    if bare == "/model":
        return json.dumps(model()).encode(), "application/json"
    if bare == "/show":
        return json.dumps(show.read()).encode(), "application/json"
    if bare == "/app":
        return b'{"line": ""}', "application/json"
    return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404


def keyof(path: str):
    bare = path.partition("?")[0]
    return show.key() if bare == "/show" else "" if bare == "/app" else None


def take(form: dict, path: str) -> str:
    """The test's one press: an order written as the app door writes it."""
    if path == "/trial/order":
        order = {**json.loads(form["text"][0]), "at": int(time.time() * 1000)}
        registry.write_whole(show.ORDER, json.dumps(order) + "\n")
        return ""
    return "Nothing at this address takes a press."


if SERVING:
    show.FOLDER, show.ORDER = TMP, os.path.join(TMP, "order.json")
    workstation = page.tool("workstation")
    workstation.model = model
    table = live.Table([live.Page(serve.address(KIND, r"(\d{2})"), framed, files=lambda nn: [])])
    serve.run(SKILL, PORT, workstation.home, recheck=1, **table.riding(route=route, keyof=keyof, take=take,
                                                                          hears=lambda: []))
    sys.exit(0)


BROWSERS = trial.SERVER + r"""
const nn = process.env.STAY_NN, framed = process.env.STAY_FRAMED, kind = process.env.STAY_KIND;
const order = o => post('/trial/order', {text: JSON.stringify(o)});
(async () => {
  for (const engine of engines) {
    await up();
    const browser = await engine.launch({headless: true});
    const page = await (await browser.newContext({viewport: {width: 1400, height: 900}})).newPage();
    await page.goto(base + '/?app#' + nn + '/' + kind + ':' + nn);
    const inner = () => page.frames().find(f => new URL(f.url()).pathname === framed);
    for (let i = 0; i < 100 && !(inner() && await inner().$('#t-1')); i++) await wait(100);
    await wait(1500);
    if (!inner()) throw new Error('no framed tab: ' + page.url() + ' frames ' + page.frames().map(f => f.url()).join(' '));
    const where = () => page.evaluate(() => location.href + ' | ' + [...document.querySelectorAll('iframe')]
      .filter(f => f.offsetParent).map(f => new URL(f.src, location.href).pathname).join(','));
    const start = await where();

    await order({target: nn + ':' + kind, place: '', mark: '#t-1', stay: true});
    await wait(500);
    const marked = await inner().evaluate(() => document.getElementById('t-1').classList.contains('ws-mark'));
    await wait(2500);
    const afterAnswer = await where();

    await order({target: 'system', place: '', mark: '#order', stay: true});
    await wait(3000);
    const afterSetting = await where();

    await order({target: 'system', place: ''});
    await wait(3000);
    const afterShow = await where();

    console.log(JSON.stringify({engine: engine.name(), start, afterAnswer, marked, afterSetting, afterShow}));
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

try:
    with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", TMP], PORT, TMP):
        r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "STAY_NN": NN, "STAY_FRAMED": FRAMED,
                                           "STAY_KIND": KIND})
finally:
    with open(os.path.join(TMP, "server.log")) as f:
        logged = f.read()
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    shutil.rmtree(TMP, ignore_errors=True)

seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
ok = len(seen) == 2
for s in seen:
    held = {"The wave answer moved nothing": s["afterAnswer"] == s["start"],
            "Its spot was bordered": s["marked"],
            "The setting moved nothing": s["afterSetting"] == s["start"],
            "show_page moved home, the control": s["afterShow"] != s["start"]}
    for name, good in held.items():
        print(("" if good else "FAILED: ") + f"{name}, in {s['engine']}.")
        ok = ok and good
    print(f"  {s['engine']}: stood at {s['start']}; after show_page {s['afterShow']}")
if len(seen) != 2:
    print(f"FAILED: the browsers ended early. {r.stdout.strip()[-800:]} {r.stderr.strip()[-1500:]}")
    if "Traceback" in logged:
        print(logged.strip()[-1500:])
sys.exit(0 if ok else 1)
