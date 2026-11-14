#!/usr/bin/env python3
"""Check 1100's home on the contract, in WebKit and in Chromium.

A server on this session's port, 11NN, draws home's own script around one
made-up page on the contract, as a program of its own, so the test can
kill it and start it again. Each engine opens home on that page's tab and
checks, in order:

  Home holds one request, for itself and the page it frames. The page is
  told through it, changes in place, and never reloads.
  I type in the framed page, and the server restarts on the same code:
  neither home nor the page reloads, and my words and my cursor hold.
  The server silent for five seconds, home says so in one line, and goes
  on once it is back.
  Shown again, home asks at once.
  Home's own code changed: home reloads once, after I stop typing, and my
  unsent words in the framed page come back.

  live-home-test.py [NN]

NN is this session's number, 02 when none is given.
"""

import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import trial  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "02"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"live-home-test-{NN}"
SERVING = len(sys.argv) > 3 and sys.argv[2] == "serve"
TMP = sys.argv[3] if SERVING else tempfile.mkdtemp(prefix="live-home-test-")
STATE, CODE = (os.path.join(TMP, n) for n in ("state.json", "code"))
# The framed page's address: a tab home frames.
FRAMED = serve.address("explanation", NN)


def read(path: str) -> str:
    with open(path) as f:
        return f.read()


def framed(nn: str) -> str:
    s = json.loads(read(STATE))
    return page.render(f"{nn}-framed", [("", live.watch("s-home") + f'<h1 id="title">{page.esc(s["title"])}</h1>'
                                         f'<textarea id="box" rows="3">{page.esc(s["saved"])}</textarea>')], refresh=0)


def model() -> dict:
    """Home's whole model: one session, one hub, one tab, and the mark of home's code."""
    return {"sessions": {NN: {"name": "home", "colour": "red", "dashed": False, "tag": NN, "by": "", "topic": ""}},
            "pages": {f"explanation:{NN}": {"kind": "explanation", "nn": NN, "label": "1 document", "waits": False,
                                            "since": 0, "port": 0, "path": FRAMED, "up": True, "side": "r"}},
            "hubs": {NN: {"overview": "", "tabs": [f"explanation:{NN}"], "nn": NN, "members": []}},
            "waits": [], "rail": [NN], "pid": os.getpid(), "code": read(CODE)}


def old_route(path: str):
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


def old_keyof(path: str):
    bare = path.partition("?")[0]
    return show.key() if bare == "/show" else "" if bare == "/app" else None


def old_take(form: dict, path: str) -> str:
    """The test's own presses: a file written whole, and the server dying."""
    if path in ("/trial/set", "/trial/code"):
        into = STATE if path == "/trial/set" else CODE
        with open(into + ".tmp", "w") as f:
            f.write(form["text"][0])
        os.replace(into + ".tmp", into)
        return ""
    if path == "/trial/die":
        trial.die(TMP, form["down"][0])
    return "Nothing at this address takes a press."


if SERVING:
    workstation = page.tool("workstation")
    workstation.model = model
    table = live.Table([live.Page(serve.address("explanation", r"(\d{2})"), framed, files=lambda nn: [STATE])])
    serve.run(SKILL, PORT, workstation.home, recheck=1,
              **table.riding(route=old_route, keyof=old_keyof, take=old_take, hears=lambda: []))
    sys.exit(0)


BROWSERS = trial.SERVER + r"""
const framed = process.env.HOME_FRAMED, nn = process.env.HOME_NN;
const set = (title, saved = '') => post('/trial/set', {text: JSON.stringify({title, saved})});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    await post('/trial/code', {text: 'code-one'});
    await set('First title');
    await die(0);
    await up();
    const browser = await engine.launch({headless: true});
    const page = await (await browser.newContext({viewport: {width: 1400, height: 900}})).newPage();
    let homes = 0, frames = 0, asks = [];
    page.on('request', r => {
      const u = new URL(r.url());
      if (r.isNavigationRequest() && u.pathname === '/') homes++;
      if (r.isNavigationRequest() && u.pathname === framed) frames++;
      if (u.pathname === '/heard') asks.push(u.searchParams.getAll('path'));
    });
    await page.goto(base + '/#' + nn + '/explanation:' + nn);
    for (let i = 0; i < 150 && !asks.some(a => a.includes(framed)); i++) await wait(100);
    const inner = () => page.frames().find(f => new URL(f.url()).pathname === framed);
    const title = (t, ms = 5000) => inner().waitForFunction(t => document.getElementById('title').textContent === t, t, {timeout: ms});
    const box = () => inner().evaluate(() => ({words: document.getElementById('box').value, active: document.activeElement.id}));
    const away = () => page.evaluate(() => { const p = document.getElementById('away'); return p && !p.hidden ? p.textContent : ''; });

    // Home holds one request, for itself and the page it frames.
    let began = Date.now();
    await set('Second title');
    await title('Second title');
    const took = Date.now() - began;
    const one = asks.length > 0 && asks.every(a => a[0] === '/model') && asks.some(a => a.includes(framed));
    said('one', one && took < 1500 && homes === 1 && frames === 1,
         `the framed page changed ${took} ms on, told through home's own ask: ${one}; home loaded ${homes} time, the page ${frames}`);

    // I type in the framed page, and the server restarts on the same code.
    await inner().click('#box');
    await page.keyboard.type('hello');
    await die(1);
    await up();
    await wait(2500);
    const stood = await box();
    await set('Third title');
    await title('Third title');
    said('restart', homes === 1 && frames === 1 && stood.words === 'hello' && stood.active === 'box',
         `after a restart home loaded ${homes} time and the page ${frames}; my words "${stood.words}", my cursor ${stood.active === 'box' ? 'held' : 'lost'}; the next change still came`);

    // The server silent for five seconds, home says so in one line.
    began = Date.now();
    await die(8);
    await wait(3500);
    const early = await away();
    await page.waitForFunction(() => { const p = document.getElementById('away'); return p && !p.hidden; }, null, {timeout: 9000});
    const shown = Date.now() - began, words = await away();
    await up();
    await page.waitForFunction(() => { const p = document.getElementById('away'); return p && p.hidden; }, null, {timeout: 8000});
    await set('Fourth title');
    await title('Fourth title');
    said('silent', !early && shown >= 4500 && /is not answering/.test(words) && homes === 1 && frames === 1,
         `the line showed ${shown} ms on: "${words}"; it went once the server was back, and nothing reloaded`);

    // Shown again, home asks at once.
    await wait(1200);
    const before = asks.length;
    await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
    await wait(400);
    said('shown', asks.length > before, `shown again, home asked ${asks.length - before} time within 400 ms`);

    // Home's own code changed, and the server restarted on it, while I type:
    // home reloads once, after I stop.
    await inner().click('#box');
    for (let i = 0; i < 2; i++) { await page.keyboard.type('x'); await wait(400); }
    await post('/trial/code', {text: 'code-two'});
    await die(0.2);
    let last = 0;
    for (let i = 0; i < 8; i++) { await page.keyboard.type('x'); last = Date.now(); await wait(400); }
    const during = homes, mine = (await box()).words;
    for (let i = 0; i < 120 && homes < 2; i++) await wait(100);
    const paused = Date.now() - last;
    await wait(5000);
    const kept = inner() ? (await box()).words : '';
    said('code', during === 1 && homes === 2 && paused >= 2500 && kept === mine && /^hellox{10}$/.test(kept),
         `home reloaded ${during - 1} times while I typed, and ${homes - 1} time ${paused} ms after my last key; my words came back: "${kept}"`);

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

# What each check says, by its name.
NAMES = {"one": "One request for home and its page", "restart": "A restart on the same code",
         "silent": "The server silent", "shown": "Home shown again", "code": "Home's own code changed"}

for path, text in ((STATE, '{"title": "", "saved": ""}'), (CODE, "code-one")):
    with open(path, "w") as f:
        f.write(text)
try:
    with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", TMP], PORT, TMP):
        r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "HOME_FRAMED": FRAMED, "HOME_NN": NN})
finally:
    logged = read(os.path.join(TMP, "server.log"))
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    shutil.rmtree(TMP, ignore_errors=True)

seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
for engine in [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]:
    print(f"FAILED: {engine} was not run: its build is not installed.")
for s in seen:
    print(("" if s["held"] else "FAILED: ") + f"{NAMES[s['name']]}, in {s['engine']}: {s['seen']}.")
ran = {s["engine"] for s in seen}
whole = ran == {"webkit", "chromium"} and all(len([s for s in seen if s["engine"] == e]) == len(NAMES) for e in ran)
if r.returncode or not whole:
    print(f"FAILED: the browsers ended early. {r.stderr.strip()[-1500:]}")
    if "Traceback" in logged:
        print(logged.strip()[-1500:])
sys.exit(0 if whole and not r.returncode and all(s["held"] for s in seen) else 1)
