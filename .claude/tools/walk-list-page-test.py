#!/usr/bin/env python3
"""Check the Walk tab: what it draws on the contract, and its page in WebKit and Chromium.

Drawn: on lib/trial.py's made-up folder, with a made-up walks/ of its
own, 1100 draws each journey and check, escapes what a file holds, names
the files that move it, and draws a walk file cut short at any length.
`rows` reads as it did.

Browser: a server on this session's port, 11NN, draws the made-up walk,
as a program of its own. Each engine checks:

  A changed page, put in place, equals the page drawn fresh, state by
  state, in one load.

  walk-list-page-test.py [NN] [Drawn|Browser]

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
spec = importlib.util.spec_from_file_location("walk_list_page_test", os.path.join(HERE, "walk-list-page.py"))
walk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(walk)
import live  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "16")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"walk-list-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

CHECKLIST = """# Trial checklist

## [[app/trial/sign-up|Sign up]]

| # | Check | What it checks | You | Tester |
|---|---|---|---|---|
| 1 | Sign up 1 | The form opens. | ⬜ | ⬜ |
| 2 | Sign up 2 | The email is <checked>. | ⬜ | ✅ |
| 4 | Sign up 2a | A wrong email is refused. | ⬜ | ⬜ |

## [[app/trial/log-in|Log in]]

| # | Check | What it checks | You | Tester |
|---|---|---|---|---|
| 3 | Log in 1 | The password is asked. | ⬜ | ⬜ |
"""
# Each state the browser asks for by name: the walk's file.
STATES = {
    "a": "# A trial walk\n\n- app/trial · Sign up\n",
    "b": "# A trial walk\n\n- app/trial · Sign up\n- app/trial · Log in 1\n",
    "c": "# A renamed walk\n\n- app/trial · Sign up 2 alone\n- app/trial · Nowhere\n- app/trial · Log in\n",
    "d": "",
}


@contextlib.contextmanager
def walks():
    """A made-up walks/ folder in WALKS's place, holding one section."""
    root = tempfile.mkdtemp(prefix="walks-")
    os.makedirs(os.path.join(root, "app", "trial"))
    with open(os.path.join(root, "app", "trial", "0-checklist.md"), "w") as f:
        f.write(CHECKLIST)
    try:
        with patch.object(walk, "WALKS", root):
            yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world, folder = trial.world(), walks()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.walks = folder.__enter__()
        self.addCleanup(folder.__exit__, None, None, None)

    def put(self, text: str) -> None:
        self.w.put("05", walk.FILE, text)

    def test_every_journey_and_check_draws(self):
        self.put(STATES["c"])
        got = walk.drawn("05")
        for part in ("A renamed walk · 3 checks", '<span class="ob-link">Sign up</span>', "Sign up 2",
                     "The email is &lt;checked&gt;.", "not found", "Log in 1", 'id="watch"', live.src("live.js")):
            self.assertIn(part, got, part)
        self.assertNotIn("Sign up 2a", got)
        self.assertNotIn("failed to draw", got)

    def test_no_walk_says_so(self):
        self.put("")
        self.assertIn("No walk", walk.drawn("05"))

    def test_a_walk_cut_short_at_any_length_still_draws(self):
        whole = STATES["c"]
        for cut in range(len(whole) + 1):
            self.put(whole[:cut])
            got = walk.drawn("05")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertIn('id="watch"', got, f"cut at {cut}")

    def test_a_checklist_cut_short_at_any_length_still_draws(self):
        self.put(STATES["b"])
        path = os.path.join(self.walks, "app", "trial", "0-checklist.md")
        for cut in range(0, len(CHECKLIST) + 1, 7):
            with open(path, "w") as f:
                f.write(CHECKLIST[:cut])
            self.assertNotIn("failed to draw", walk.drawn("05"), f"cut at {cut}")

    def test_its_files_name_the_walk_and_each_checklist(self):
        self.put(STATES["b"])
        named = walk.files("05")
        for f in (os.path.join(self.w.work, "05"), os.path.join(self.w.work, "05", walk.FILE),
                  os.path.join(self.walks, "app", "trial", "0-checklist.md"), os.path.join(self.walks, "app", "trial"),
                  os.path.join(self.w.work, "10", "stages.json")):
            self.assertIn(f, named)

    def test_a_walk_coming_later_is_named_by_its_folder(self):
        os.remove(os.path.join(self.w.work, "05", walk.FILE))
        self.assertIn(os.path.join(self.w.work, "05"), walk.files("05"))

    def test_rows_reads_as_before(self):
        self.assertEqual(walk.rows(STATES["b"]), "\n".join([
            "A trial walk", "", "Sign up · walks/app/trial/0-checklist.md",
            "  1 · Sign up 1 · The form opens.", "  2 · Sign up 2 · The email is <checked>.",
            "  4 · Sign up 2a · A wrong email is refused.",
            "  Also read: walks/app/trial/sign-up.md · Start, Prep · walks/app/before-you-start.md · Logins", "",
            "Log in · walks/app/trial/0-checklist.md", "  3 · Log in 1 · The password is asked.",
            "  Also read: walks/app/trial/log-in.md · Start, Prep · walks/app/before-you-start.md · Logins"]))


BROWSERS = trial.SERVER + r"""
const url = base + process.env.PAGE;
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('main'))]);
});
const settled = async (p, title) => {
  await p.waitForFunction(t => document.body.textContent.includes(t)
    && !('busy' in document.getElementById('watch').dataset), title, {timeout: 8000, polling: 100});
  await wait(300);
};
const TITLES = {a: 'A trial walk · 3 checks', b: 'A trial walk · 4 checks', c: 'A renamed walk · 3 checks', d: 'No walk'};

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
    await settled(b, TITLES.a);
    let same = [];
    for (const name of ['b', 'c', 'a', 'd', 'b']) {
      await state(name);
      await settled(b, TITLES[name]);
      await c.goto(url);
      await settled(c, TITLES[name]);
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh"}


def serving(tmp: str) -> None:
    """The made-up folder's walk, on the contract."""
    with trial.world() as w, walks():
        path = os.path.join(w.work, "05", walk.FILE)
        table = live.Table([walk.LIVE])

        def old_route(at: str):
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                registry.rewrite(path, STATES[form["name"][0]])
                return ""
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1,
                  **table.riding(route=old_route, take=old_take, hears=lambda: []))


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="walk-list-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "PAGE": serve.address("walk", "05")})
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


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
