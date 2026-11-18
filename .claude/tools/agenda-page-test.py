#!/usr/bin/env python3
"""Check the agenda page: its presses, what it draws on the contract, and its page in WebKit and Chromium.

Presses: Start is handed on, and any other press is refused in a sentence.

Drawn: on a made-up agenda folder, 1100 draws the frame and hands the
agenda over as data, escaped. An item cut short at any length draws as
one it could not read, never as an error, never lost. Its files name the
folder and each item, and a write into another session's folder wakes
nothing.

Browser: a server on this session's port, 11NN, draws the made-up agenda,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  A note written while I type in the search: my words and my cursor hold,
  and the hits move with it, in one load. Start sends its item.

  agenda-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 15 when none is given.
"""

import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("agenda_page_test", os.path.join(HERE, "agenda-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import agenda  # noqa: E402
import live  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "15")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"agenda-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

TOPIC = [name for name, _ in agenda.TOPICS]
PHASE = list(agenda.PHASES) or [""]
WHAT = "What: Do, small: an item the test draws."
# Each item: its title, what it waits on, its topics, its phase, its note.
SIGN_IN = ("Sign in", [], [TOPIC[0]], PHASE[0], WHAT)
SIGN_UP = ("Sign up", [], [TOPIC[0]], PHASE[0], WHAT)
INVITES = ("Team invites", ["sign-up"], [TOPIC[0]], PHASE[0], WHAT)
CALENDAR = ("Shared calendar", [], [TOPIC[-1], TOPIC[0]], PHASE[-1], WHAT + "\nMine: read the calendar.")
# Each state the browser asks for by name: its items, by file name.
STATES = {
    "a": {"sign-in": SIGN_IN, "sign-up": SIGN_UP},
    "b": {"sign-in": SIGN_IN, "sign-up": SIGN_UP, "team-invites": INVITES},
    "c": {"sign-in": SIGN_IN, "sign-up": SIGN_UP, "team-invites": INVITES, "shared-calendar": CALENDAR},
    "d": {"sign-in": (*SIGN_IN[:4], WHAT + "\nWhy: the calendar needs it."), "shared-calendar": CALENDAR},
}


def state(folder: str, name: str) -> None:
    """The folder holding state `name`'s items alone, each swapped in whole,
    and its README, as a first read leaves it."""
    agenda.start(folder)
    want = STATES[name]
    for f in os.listdir(folder):
        if f.endswith(".md") and f != agenda.README and f[:-3] not in want:
            os.remove(os.path.join(folder, f))
    for i, (title, after, topics, phase, note) in want.items():
        text = agenda.text_of({"title": title, "after": after, "topics": topics, "phase": phase, "note": note})
        path = os.path.join(folder, f"{i}.md")
        try:
            with open(path) as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        registry.rewrite(path, text)


class Made(unittest.TestCase):
    """A made-up agenda folder, in the tool's place, inside lib/trial.py's made-up sessions folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.folder = os.path.join(self.w.root, "agenda")
        state(self.folder, "c")
        p = patch.object(tool, "FOLDER", self.folder)
        p.start()
        self.addCleanup(p.stop)


class Presses(Made):
    def test_a_press_naming_no_act_is_refused(self):
        self.assertEqual(tool.pressed({"act": ["no such act"]}), "This page takes no such press. Nothing was started.")

    def test_start_is_handed_on(self):
        got = tool.pressed({"start": ["sign-in"]})
        self.assertIsInstance(got, serve.Typing)

    def test_start_on_no_such_item_is_refused(self):
        self.assertEqual(tool.pressed({"start": ["nowhere"]}).outside(), "No item is named 'nowhere'.")
        self.assertEqual(self.w.started, [])


class Drawn(Made):
    def data(self, got: str) -> dict:
        return json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', got, re.S).group(1))

    def test_it_draws_its_frame_and_hands_the_agenda_over(self):
        got = tool.drawn()
        for part in ('id="watch"', live.src("live.js"), live.src("agenda.js"), 'id="sc"', 'id="note"', 'id="icons"',
                     '<input id="q" data-draft="no"'):
            self.assertIn(part, got, part)
        self.assertEqual(sorted(it["id"] for it in self.data(got)["items"]),
                         ["shared-calendar", "sign-in", "sign-up", "team-invites"])
        self.assertEqual(next(it for it in self.data(got)["items"] if it["id"] == "shared-calendar")["mine"],
                         "read the calendar.")

    def test_what_a_note_holds_is_escaped(self):
        registry.rewrite(os.path.join(self.folder, "sign-in.md"), agenda.text_of(
            {"title": "Sign in", "after": [], "topics": [TOPIC[0]], "phase": PHASE[0],
             "note": "What: </script><b>out</b>"}))
        got = tool.drawn()
        self.assertNotIn("</script><b>out</b>", got)
        self.assertIn("What: </script><b>out</b>", [it["note"] for it in self.data(got)["items"]])

    def test_an_item_cut_short_at_any_length_is_never_lost(self):
        path = os.path.join(self.folder, "sign-up.md")
        with open(path, "rb") as f:
            whole = f.read()
        for cut in range(len(whole) + 1):
            with open(path, "wb") as f:
                f.write(whole[:cut])
            got = tool.drawn()
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            d = self.data(got)
            self.assertTrue("sign-up" in [it["id"] for it in d["items"]] or "sign-up.md" in d["broken"], f"cut at {cut}")

    def test_its_files_name_the_folder_and_each_item(self):
        named = tool.files()
        self.assertIn(self.folder, named)
        for i in STATES["c"]:
            self.assertIn(os.path.join(self.folder, f"{i}.md"), named)

    def test_a_write_into_another_sessions_folder_wakes_nothing(self):
        table = live.Table([tool.LIVE])
        first = table.picture("/agenda")
        self.w.put("11", "notes.md", "Another session's file.")
        self.w.put("05", "waves/wave-2.md", "# Wave 2\nsent:\n")
        # A picture younger than live.YOUNG is answered unread.
        time.sleep(live.YOUNG)
        self.assertIs(table.picture("/agenda"), first)
        state(self.folder, "d")
        time.sleep(live.YOUNG)
        self.assertIsNot(table.picture("/agenda"), first)


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + '/agenda';
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy', 'data-ms'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('main'))]);
});
const settled = async (p, n) => {
  await p.waitForFunction(n => document.querySelectorAll('#sc .node').length === n
    && !('busy' in document.getElementById('watch').dataset), n, {timeout: 6000});
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

    // A changed page, put in place, equals the page drawn fresh, state by state.
    await state('a');
    const b = await open(), c = await open();
    await b.goto(url);
    await settled(b, 2);
    let same = [];
    for (const [name, n] of [['b', 3], ['c', 4], ['d', 2], ['a', 2], ['c', 4]]) {
      await state(name);
      await settled(b, n);
      await c.goto(url);
      await settled(c, n);
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // A note written while I type in the search: my words and cursor hold,
    // and the hits move with it.
    await state('c');
    const a = await open();
    await a.goto(url);
    await settled(a, 4);
    await a.click('#q');
    await a.keyboard.type('calendar need');
    const before = await a.evaluate(() => document.querySelectorAll('#note .rows button').length);
    await state('d');
    await settled(a, 2);
    await a.keyboard.type('s');
    const typed = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('q').value,
      hits: [...document.querySelectorAll('#note .rows button')].map(b => b.dataset.id).sort().join(' ')}));
    // Start sends its item: the test's own stand-in for a session's start.
    await a.keyboard.press('Escape');
    await a.click('#sc .node[data-id="sign-in"]');
    await a.click('#start');
    let started = '';
    for (let i = 0; i < 40 && !started; i++) { started = await (await fetch(base + '/trial/started')).text(); if (!started) await wait(100); }
    said('typing', typed.active === 'q' && typed.words === 'calendar needs' && before === 0 && typed.hits === 'sign-in'
         && started === 'sign-in' && a.loads === 1,
         `my cursor stayed in ${typed.active}, my words read "${typed.words}"; hits before the write: ${before}, after: ${typed.hits}; `
         + `Start sent ${started || 'nothing'}; ${a.loads} load`);
    await a.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "My typing, while a note is written, and Start"}


def serving(tmp: str) -> None:
    """The made-up agenda, drawn, with the test's own presses."""
    started = []
    with trial.world() as w:
        folder = os.path.join(w.root, "agenda")
        state(folder, "a")
        tool.FOLDER = folder
        tool.start = lambda item: started.append(item) or ""
        table = live.Table([tool.LIVE])

        def old_route(at: str):
            if at.partition("?")[0] == "/trial/started":
                return (started[-1] if started else "").encode(), "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                state(folder, form["name"][0])
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
        tmp = tempfile.mkdtemp(prefix="agenda-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}"})
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

    def test_my_typing_holds_while_a_note_is_written_and_start_sends(self):
        self.held("typing")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
