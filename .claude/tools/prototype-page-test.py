#!/usr/bin/env python3
"""Check the Prototype page: its press, what it draws on the contract, and its page in WebKit and Chromium.

Presses: Send types my pick, its looks and my feedback; a press naming
another act is refused, and so is a pick naming no variation.

Drawn: on lib/trial.py's made-up folder, with a made-up prototypes app of
its own, 1100 draws a subject's page and the library, starts no program,
hands the page's script its data alone, names the files that move it, and
draws a generation cut short at any length, as unreadable. A library
draw wants its pictures, and the reader starts their job, one at a time.
Home names the page 1100's own once 1100's table holds its address.

Browser: a server on this session's port, 11NN, draws the made-up page,
as a program of its own, beside a variation it serves as 1400 would. Each
engine checks, in order:

  A changed page, put in place, equals the page drawn fresh on the same
  view, state by state.
  My feedback holds while the page changes, comes back once the server
  was killed and the page reloaded, and Send types it with my pick, then
  empties the box. A new generation then opens on its first variation,
  Send open again.

  prototype-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 16 when none is given.
"""

import contextlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prototype_page_test", os.path.join(HERE, "prototype-page.py"))
proto = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proto)
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "16")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"prototype-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

G1 = {"generation": 1, "variations": [
    {"id": "v1", "route": "/trial/g1/v1", "direction": "A grid of <cards>."},
    {"id": "v2", "real": False, "direction": "A list, gone."}]}
G2 = {"generation": 2, "variations": [
    {"id": "v1", "route": "/trial/g2/v1", "from": "1/v1", "direction": "The grid, denser.",
     "looks": [{"n": "1", "title": "Tight", "group": "A"}, {"n": "2", "title": "Loose", "group": "A"},
               {"n": "3", "title": "Shown only"}]}]}
G3 = {"generation": 3, "variations": [{"id": "v1", "real": False, "direction": "A third try."}]}
# Each state the browser asks for by name: each generation's file, as its text, and whether session 05 works.
STATES = {
    "a": ({"g1": G1, "g2": G2}, "idle"),
    "b": ({"g1": G1, "g2": G2, "g3": G3}, "idle"),
    "c": ({"g1": G1, "g2": json.dumps(G2)[:40]}, "idle"),
    "d": ({"g1": G1, "g2": G2}, "busy"),
}
SUBJECT = "/proto/?subject=trial&session=05"


def put(w, app: str, name: str) -> None:
    """The made-up subject, as state NAME holds it."""
    gens, status = STATES[name]
    home = os.path.join(app, "trial")
    for f in os.listdir(home):
        if re.fullmatch(r"g\d+\.json", f) and f[:-5] not in gens:
            os.remove(os.path.join(home, f))
    for g, body in gens.items():
        path = os.path.join(home, f"{g}.json")
        text = body if isinstance(body, str) else json.dumps(body)
        try:
            with open(path) as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        registry.rewrite(path, text)
    record = os.path.join(w.account, "sessions", "40005.json")
    with open(record) as f:
        d = json.load(f)
    if d["status"] != status:
        registry.rewrite(record, json.dumps({**d, "status": status}))


@contextlib.contextmanager
def made_up():
    """lib/trial.py's world, with a prototypes app of its own, session 05 holding its subject."""
    app = tempfile.mkdtemp(prefix="prototypes-")
    routes, shots = os.path.join(app, "src", "routes"), os.path.join(app, "shots")
    os.makedirs(os.path.join(app, "trial"))
    os.makedirs(os.path.join(app, "saved"))
    os.makedirs(shots)
    with open(os.path.join(app, "saved", "g1.json"), "w") as f:
        json.dump({**G3, "generation": 1}, f)
    try:
        with trial.world() as w, contextlib.ExitStack() as stack:
            for owner in (proto, prototypes):
                stack.enter_context(patch.object(owner, "APP", app))
                stack.enter_context(patch.object(owner, "ROUTES", routes))
            stack.enter_context(patch.object(proto, "SHOTS", shots))
            w.put("05", registry.PROTOTYPE, "trial\n")
            put(w, app, "a")
            yield w, app
    finally:
        shutil.rmtree(app, ignore_errors=True)


class Presses(unittest.TestCase):

    def setUp(self):
        world = made_up()
        self.w, self.app = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.typed = []
        p = patch.object(panes, "say", lambda pane, line, **more: self.typed.append(line) or True)
        p.start()
        self.addCleanup(p.stop)

    def press(self, **form):
        return live.Table([proto.LIVE]).take({k: [v] for k, v in {"session": "05", **form}.items()}, "/proto/")

    def test_send_types_my_pick_its_looks_and_my_feedback(self):
        self.assertEqual(self.press(act="send", pick="2/v1", looks="A:1", feedback="Keep it."), "")
        self.assertEqual(self.typed, ["g2/v1 · A: look 1 — Keep it."])

    def test_a_press_naming_no_session_types_into_none(self):
        self.assertEqual(self.press(session="", act="send", pick="1/v1"), "There is no session 00. Nothing was typed.")
        self.assertEqual(self.typed, [])

    def test_the_app_doors_press_names_no_act_and_still_sends(self):
        self.assertEqual(self.press(pick="1/v2", looks="", feedback=""), "")
        self.assertEqual(self.typed, ["g1/v2"])

    def test_another_act_is_refused(self):
        self.assertEqual(self.press(act="shout", pick="1/v1"), proto.NO_SUCH)
        self.assertEqual(self.typed, [])

    def test_a_pick_naming_no_variation_is_refused(self):
        self.assertEqual(self.press(act="send", pick="nothing"), "That pick names no variation. Nothing was typed.")


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = made_up()
        self.w, self.app = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def draw(self, query: str = "subject=trial&session=05") -> str:
        return live.Table([proto.LIVE]).route("/proto/?" + query)

    def test_a_subject_draws_every_generation_and_its_data(self):
        got = self.draw()
        for part in ('id="t-2/v1"', 'id="t-1/v2"', 'id="t-pick"', 'class="opt lo" data-k="2/v1" data-g="A" data-n="1"',
                     "A grid of &lt;cards&gt;.", '<textarea id="fb"', 'id="watch"', live.src("prototype.js")):
            self.assertIn(part, got, part)
        self.assertNotIn("onclick", got.split("<main>")[1].split('<script type="application/json"')[0])
        data = json.loads(re.search(r'<script type="application/json" id="proto">(.*?)</script>', got, re.S).group(1))
        self.assertEqual(data["FIRST"], "2/v1")
        self.assertEqual(data["GROUPS"], {"2/v1": ["A"]})
        self.assertEqual(data["ROUTES"]["1/v2"], "")
        self.assertFalse(data["BUSY"])

    def test_a_working_session_greys_send(self):
        put(self.w, self.app, "d")
        data = json.loads(re.search(r'id="proto">(.*?)</script>', self.draw(), re.S).group(1))
        self.assertTrue(data["BUSY"])

    def test_the_library_draws_and_starts_no_program(self):
        with patch.object(proto.os.path, "exists", lambda p: True if p == proto.CHROME else os.path.lexists(p)):
            got = self.draw("")
        self.assertIn("Saved · 1", got)
        self.assertIn('id="watch"', got)
        self.assertEqual(self.w.started, [])

    def test_a_generation_cut_short_at_any_length_draws_as_unreadable(self):
        whole = json.dumps(G2)
        path = os.path.join(self.app, "trial", "g2.json")
        for cut in range(len(whole)):
            with open(path, "w") as f:
                f.write(whole[:cut])
            got = proto.drawn("subject=trial&session=05")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertIn("This generation's file is unreadable.", got, f"cut at {cut}")
            self.assertIn('id="t-1/v1"', got, f"cut at {cut}")

    def test_its_files_name_the_subject_and_a_generation_coming_later(self):
        named = proto.files("subject=trial&session=05")
        for f in (os.path.join(self.app, "trial"), os.path.join(self.app, "trial", "g2.json"),
                  os.path.join(self.w.work, "05"), os.path.join(self.w.work, "10", "stages.json")):
            self.assertIn(f, named)
        self.assertIn(os.path.join(self.app, "saved"), proto.files(""))

    def test_a_query_no_subject_could_take_draws_the_library(self):
        self.assertIn("Saved · ", proto.drawn("subject=../etc&session=05"))

    def test_a_library_draw_wants_its_pictures_and_the_reader_starts_one_job_at_a_time(self):
        class Job:
            ended = None

            def poll(self):
                return self.ended

        jobs = []
        with patch.object(proto, "missing", lambda d: True), patch.object(proto.ports, "answering", lambda port: True), \
                patch.object(proto, "shot", lambda: jobs.append(Job()) or jobs[-1]), \
                patch.object(proto, "JOB", [None]), patch.object(proto.PICTURES, "asked", 0.0):
            proto.shooting()
            self.assertEqual(len(jobs), 0, "no draw wanted the pictures yet")
            self.draw("")
            proto.shooting()
            proto.shooting()
            self.assertEqual(len(jobs), 1, "one job while it runs")
            jobs[0].ended = 0
            proto.shooting()
            self.assertEqual(len(jobs), 2, "the next once the last ended")
        self.assertEqual(self.w.started, [])

    def test_home_names_the_page_at_an_address_1100s_table_holds(self):
        got = page.tool("workstation").model()["pages"]["prototype:05"]
        self.assertEqual(got["path"], SUBJECT)
        self.assertIsNotNone(live.Table([proto.LIVE]).find(got["path"].partition("?")[0]))
        self.assertNotIn("port", got)


BROWSERS = trial.SERVER + r"""
const url = base + process.env.PAGE;
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       n.style ? n.style.cssText : '', n.disabled === true, n.matches('textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('nav.nums')), walk(document.querySelector('main'))]);
});
const GENS = {a: 2, b: 3, c: 2, d: 2};
const settled = async (p, name) => {
  await p.waitForFunction(([n, busy]) => document.querySelectorAll('nav.nums .lbl').length === n
    && JSON.parse(document.getElementById('proto').textContent).BUSY === busy
    && !('busy' in document.getElementById('watch').dataset), [GENS[name], name === 'd'], {timeout: 20000, polling: 100})
    .catch(async e => {
      const now = await p.evaluate(() => ({gens: document.querySelectorAll('nav.nums .lbl').length, at: Date.now(),
        data: (document.getElementById('proto') || {}).textContent, busy: 'busy' in document.getElementById('watch').dataset}));
      throw new Error(`state ${name} never stood on ${p.url()}, ${p.loads} load, it shows ${JSON.stringify(now)}: ${e.message}`);
    });
  await wait(400);
};

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1200, height: 800}});
    const open = async () => {
      const p = await context.newPage();
      p.loads = 0;
      p.on('request', r => { if (r.isNavigationRequest() && r.frame() === p.mainFrame()) p.loads++; });
      return p;
    };

    // A changed page, put in place, equals the page drawn fresh on the same
    // view, state by state. Its view rides in its address, after the #.
    await state('a');
    const b = await open(), c = await open();
    await b.goto(url);
    await settled(b, 'a');
    let same = [];
    for (const name of ['b', 'c', 'd', 'a', 'b']) {
      await state(name);
      await settled(b, name);
      await c.goto('about:blank');
      await c.goto(b.url());
      await settled(c, name);
      const x = await snap(b), y = await snap(c);
      let i = 0;
      while (i < x.length && x[i] === y[i]) i++;
      same.push(x === y ? name : `${name} differs, put in place ${x.slice(i - 60, i + 60)}, fresh ${y.slice(i - 60, i + 60)}`);
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My feedback holds while the page changes, outlives the server, and Send types it.
    await state('a');
    const a = await open();
    await a.goto(url);
    await settled(a, 'a');
    await a.click('#fb');
    await a.keyboard.type('Keep the grid.');
    await state('b');
    await settled(a, 'b');
    const held = await a.evaluate(() => ({words: document.getElementById('fb').value, active: document.activeElement.id}));
    const loads = a.loads;
    await die(2);
    await wait(500);
    await up();
    await state('a');
    await a.reload();
    await settled(a, 'a');
    await wait(300);
    const back = await a.evaluate(() => document.getElementById('fb').value);
    await a.click('.card[data-k="2/v1"] .pick');
    const label = await a.evaluate(() => document.getElementById('send').textContent);
    await a.click('#send');
    await a.waitForFunction(() => document.getElementById('send').textContent !== 'Send · 1 open, with feedback', null, {timeout: 6000}).catch(() => {});
    const done = await a.evaluate(() => document.getElementById('send').textContent);
    const line = await (await fetch(base + '/trial/said')).text();
    const left = await a.evaluate(() => document.getElementById('fb').value
      + Object.keys(localStorage).filter(k => k.startsWith('draft:')).join(''));
    const before = a.loads;
    await state('b');
    await settled(a, 'b');
    const next = await a.evaluate(() => ({now: document.getElementById('now').textContent,
      send: document.getElementById('send').textContent, picked: document.querySelectorAll('.picked').length}));
    said('feedback', held.words === 'Keep the grid.' && held.active === 'fb' && loads === 1 && back === 'Keep the grid.'
         && label === 'Send · 1 open, with feedback' && done === 'Sent' && line === 'g2/v1 · A: open — Keep the grid.'
         && left === '' && next.now.startsWith('G3 · v1') && next.send === 'Send' && next.picked === 0 && a.loads === before,
         `typed words held while a generation arrived: "${held.words}", my cursor in ${held.active}, ${loads} load; `
         + `the server killed and the page reloaded, the box reads "${back}"; Send read "${label}", then "${done}", and typed "${line}"; `
         + `the box then held "${left}"; a new generation shows "${next.now}", Send reads "${next.send}", `
         + `${next.picked} picked, ${a.loads - before} reload`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "feedback": "My feedback"}

VARIATION = b"<!doctype html><body style='margin:0;font:20px sans-serif'>A variation, as 1400 serves it.</body>"


def serving(tmp: str) -> None:
    """The made-up prototype, on the contract, beside its variations, with the test's own presses."""
    said = os.path.join(tmp, "said")
    with made_up() as (w, app), patch.object(panes, "say", lambda pane, line, **more: open(said, "w").write(line) or True):
        table = live.Table([proto.LIVE])

        def old_route(at: str):
            bare = at.partition("?")[0]
            if bare.startswith("/proto/trial/"):
                return VARIATION, "text/html; charset=utf-8"
            if bare == "/trial/said":
                try:
                    with open(said) as f:
                        return f.read().encode(), "text/plain; charset=utf-8"
                except OSError:
                    return b"", "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                put(w, app, form["name"][0])
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1,
                  **table.riding(route=old_route, take=old_take, hears=lambda: []))


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="prototype-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "PAGE": SUBJECT})
            with open(os.path.join(tmp, "server.log"), errors="replace") as f:
                cls.logged = f.read()
        finally:
            shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
            shutil.rmtree(tmp, ignore_errors=True)
        cls.seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
        cls.ended = r.stderr.strip()[-1500:] if r.returncode else ""
        cls.missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
        for s in cls.seen:
            print(("" if s["held"] else "FAILED: ") + f"{NAMES[s['name']]}, in {s['engine']}: {s['seen']}.", flush=True)

    def held(self, name: str) -> None:
        self.assertEqual(self.missing, [], "an engine's build is not installed")
        mine = [s for s in self.seen if s["name"] == name]
        self.assertEqual(sorted(s["engine"] for s in mine), ["chromium", "webkit"],
                         f"the browsers ended early. {self.ended} {self.logged[-800:] if 'Traceback' in self.logged else ''}")
        for s in mine:
            self.assertTrue(s["held"], f"{NAMES[name]}, in {s['engine']}: {s['seen']}")

    def test_a_changed_page_put_in_place_equals_the_page_drawn_fresh(self):
        self.held("fresh")

    def test_my_feedback_holds_outlives_the_server_and_sends(self):
        self.held("feedback")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
