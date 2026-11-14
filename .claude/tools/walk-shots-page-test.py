#!/usr/bin/env python3
"""Check the Screenshots tab: what it draws on the contract, and its page in WebKit and Chromium.

Drawn: on lib/trial.py's made-up folder, with made-up cases of its own,
1100 draws each journey and screenshot in walked order, marks one a case
names in red, hands the page's script the screenshots alone, names the
files that move it, and draws a walk.json or a case cut short at any
length.

Browser: a server on this session's port, 11NN, draws the made-up walk,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  Next, the arrow keys and a click walk the screenshots, and a screenshot
  arriving keeps the one I was on, in one load.

  walk-shots-page-test.py [NN] [Drawn|Browser]

NN is this session's number, 16 when none is given.
"""

import base64
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
spec = importlib.util.spec_from_file_location("walk_shots_page_test", os.path.join(HERE, "walk-shots-page.py"))
shots = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shots)
import live  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "16")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"walk-shots-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

# A fixed moment, so every screenshot's time reads the same on each run.
T = 1793520000
# Each state the browser asks for by name: its screenshots, as (journey,
# name, seconds after T), and the screenshots its case names under Issues.
STATES = {
    "a": ([("sign-up", "1", 0), ("sign-up", "2", 10)], []),
    "b": ([("sign-up", "1", 0), ("sign-up", "2", 10), ("log-in", "3", 20)], ["sign-up/1"]),
    "c": ([("sign-up", "1", 0), ("sign-up", "2-1", 11), ("sign-up", "2-2", 12), ("log-in", "3", 20)], []),
    "d": ([], []),
    "e": ([("start", "0", -10), ("sign-up", "1", 0), ("sign-up", "2", 10)], []),
}


def put(w, name: str) -> None:
    """Session 05's walk/ and its case, as state NAME holds them."""
    got, named = STATES[name]
    base = os.path.join(w.work, "05", shots.WALK)
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    for journey, shot, at in got:
        path = w.put("05", f"{shots.WALK}/app/trial/{journey}/{shot}.png", base64.b64decode(trial.PIXEL))
        os.utime(path, (T + at, T + at))
    for old in os.listdir(shots.CASES):
        os.remove(os.path.join(shots.CASES, old))
    if named:
        case = os.path.join(shots.CASES, "05-trial.md")
        with open(case, "w") as f:
            f.write("# A case\n\n## Issues\n" + "".join(f"- app/trial/{n}.png is wrong.\n" for n in named))
        os.utime(case, (T + 100, T + 100))


@contextlib.contextmanager
def made_up():
    """lib/trial.py's world, its walk named by walk.json, with a cases folder of its own."""
    cases = tempfile.mkdtemp(prefix="cases-")
    try:
        with trial.world() as w, patch.object(shots, "CASES", cases):
            w.put("05", "walk.json", json.dumps({"main": "04"}))
            yield w
    finally:
        shutil.rmtree(cases, ignore_errors=True)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = made_up()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def rail(self, got: str) -> str:
        return re.search(r'<aside id="rail">(.*?)</aside>', got, re.S).group(1)

    def test_every_journey_and_screenshot_draws_in_walked_order(self):
        put(self.w, "c")
        self.assertEqual(self.rail(shots.drawn("05")),
                         '<h2 class="ws-j">Sign up</h2><div class="tab ws-row" data-i="0">1</div>'
                         '<div class="tab ws-row" data-i="1">2-1</div><div class="tab ws-row" data-i="2">2-2</div>'
                         '<h2 class="ws-j">Log in</h2><div class="tab ws-row" data-i="3">3</div>')

    def test_a_screenshot_a_case_names_wears_red(self):
        put(self.w, "b")
        self.assertIn('<div class="tab ws-row" data-i="0" style="--c:var(--red)">1</div>', self.rail(shots.drawn("05")))

    def test_the_script_gets_the_screenshots_alone(self):
        put(self.w, "a")
        got = shots.drawn("05")
        data = json.loads(re.search(r'<script type="application/json" id="shots">(.*?)</script>', got, re.S).group(1))
        self.assertEqual([s["name"] for s in data["shots"]], ["1", "2"])
        self.assertNotIn("file", data["shots"][0])
        self.assertEqual(data["pic"], "/p/shots/05/pic")
        for part in ('id="watch"', live.src("live.js"), live.src("walk-shots.js")):
            self.assertIn(part, got)

    def test_no_screenshot_says_so_with_the_same_script(self):
        put(self.w, "d")
        got = shots.drawn("05")
        self.assertIn("No screenshot yet", got)
        self.assertIn(live.src("walk-shots.js"), got)

    def test_a_walk_json_or_a_case_cut_short_at_any_length_still_draws(self):
        put(self.w, "b")
        whole = json.dumps({"main": "04"})
        for cut in range(len(whole) + 1):
            self.w.put("05", "walk.json", whole[:cut])
            self.assertNotIn("failed to draw", shots.drawn("05"), f"walk.json cut at {cut}")
        case = os.path.join(shots.CASES, "05-trial.md")
        with open(case) as f:
            text = f.read()
        for cut in range(len(text) + 1):
            with open(case, "w") as f:
                f.write(text[:cut])
            got = shots.drawn("05")
            self.assertNotIn("failed to draw", got, f"case cut at {cut}")
            self.assertEqual(got.count('class="tab ws-row"'), 3, f"case cut at {cut}")

    def test_its_files_name_every_folder_a_screenshot_lands_in(self):
        put(self.w, "b")
        named, base = shots.files("05"), os.path.join(self.w.work, "05", shots.WALK)
        for f in (os.path.join(self.w.work, "05"), os.path.join(self.w.work, "05", "walk.json"), shots.CASES,
                  base, os.path.join(base, "app"), os.path.join(base, "app", "trial"),
                  os.path.join(base, "app", "trial", "sign-up"), os.path.join(base, "app", "trial", "log-in")):
            self.assertIn(f, named)

    def test_a_walk_coming_later_is_named_by_its_folder(self):
        shutil.rmtree(os.path.join(self.w.work, "05", shots.WALK))
        self.assertIn(os.path.join(self.w.work, "05"), shots.files("05"))


BROWSERS = trial.SERVER + r"""
const url = base + process.env.PAGE;
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       n.style ? n.style.cssText : '', n.disabled === true, [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('aside')), walk(document.querySelector('main'))]);
});
const ROWS = {a: 2, b: 3, c: 4, d: 0, e: 3};
const settled = async (p, rows) => {
  await p.waitForFunction(n => document.querySelectorAll('.ws-row').length === n
    && !('busy' in document.getElementById('watch').dataset), rows, {timeout: 8000, polling: 100});
  await wait(400);
};
const mid = p => p.evaluate(() => (document.getElementById('mid') || {}).textContent || '');

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

    await state('a');
    const b = await open(), c = await open();
    await b.goto(url);
    await settled(b, ROWS.a);
    let same = [];
    for (const name of ['b', 'c', 'd', 'a', 'e', 'b']) {
      await state(name);
      await settled(b, ROWS[name]);
      await c.goto(url);
      await settled(c, ROWS[name]);
      for (const p of [b, c]) if (ROWS[name]) { await p.click('.ws-row'); await wait(200); }
      const x = await snap(b), y = await snap(c);
      let i = 0;
      while (i < x.length && x[i] === y[i]) i++;
      same.push(x === y ? name : `${name} differs, put in place ${x.slice(i - 60, i + 60)}, fresh ${y.slice(i - 60, i + 60)}`);
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    await state('a');
    const a = await open();
    await a.goto(url);
    await settled(a, ROWS.a);
    const first = await mid(a);
    await a.click('#next');
    const nexted = await mid(a);
    await a.keyboard.press('ArrowLeft');
    const lefted = await mid(a);
    await a.click('.ws-row[data-i="1"]');
    await state('e');
    await settled(a, ROWS.e);
    const kept = await mid(a), on = await a.evaluate(() => document.querySelector('.ws-row.on').textContent);
    said('walks', first === '1 · 1 of 2' && nexted === '2 · 2 of 2' && lefted === '1 · 1 of 2'
         && kept === '2 · 3 of 3' && on === '2' && a.loads === 1,
         `opened on "${first}", Next showed "${nexted}", left showed "${lefted}"; a screenshot arrived before mine, and it shows "${kept}", its row "${on}" outlined; ${a.loads} load`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "walks": "Walking the screenshots"}


def serving(tmp: str) -> None:
    """The made-up folder's walk, on the contract, and each screenshot."""
    with made_up() as w:
        put(w, "a")
        table = live.Table([shots.LIVE])

        def old_route(at: str):
            bare = at.partition("?")[0]
            if m := re.fullmatch(r"/p/shots/05(/pic/\d+)", bare):
                return shots.answer("05", m.group(1))
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                put(w, form["name"][0])
                return ""
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1,
                  **table.riding(route=old_route, take=old_take, hears=lambda: []))


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="walk-shots-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "PAGE": serve.address("shots", "05")})
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

    def test_the_screenshots_walk_and_my_place_holds(self):
        self.held("walks")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
