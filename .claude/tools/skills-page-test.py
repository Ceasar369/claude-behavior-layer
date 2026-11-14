#!/usr/bin/env python3
"""Check the skills page: what it draws on the contract, and its page in WebKit and Chromium.

Drawn: on a made-up skills folder, 1100 draws every skill, escaped. A
SKILL.md cut short at any length still draws its row, never an error.
Its files name the folder, each skill's folder and each SKILL.md, and a
write into another session's folder wakes nothing.

Browser: a server on this session's port, 11NN, draws the made-up skills,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  A skill changed while I type in the filter: my words and my cursor hold,
  the filter takes in the change, and Enter copies its command, in one load.

  skills-page-test.py [NN] [Drawn|Browser]

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
spec = importlib.util.spec_from_file_location("skills_page_test", os.path.join(HERE, "skills-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import live  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "15")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"skills-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

# Each skill: its description, and its arguments.
CLARIFY = ("Calls the one clarify shape that answers my ask. More after.", "")
ITEMS = ("Lays out every item I must rule on, in chat and on my page.", "now — at once · later")
ANOTHER = ("Hands my words to one new session.", "")
AGENDA = ("Writes my agenda as I dictate it — its order too.", "")
# Each state the browser asks for by name: its skills, by name.
STATES = {
    "a": {"2-clarify": CLARIFY, "clarify-items": ITEMS, "another-session": ANOTHER},
    "b": {"2-clarify": CLARIFY, "clarify-items": ITEMS, "another-session": ANOTHER, "agenda-write": AGENDA},
    "c": {"2-clarify": CLARIFY, "clarify-items": ("Lays out each ruling item, whole.", ""), "another-session": ANOTHER,
          "agenda-write": AGENDA},
    "d": {"2-clarify": CLARIFY, "clarify-items": ITEMS},
}


def head(name: str, description: str, arguments: str) -> str:
    """A SKILL.md, its head first."""
    return (f'---\nname: {name}\ndescription: "{description}"\n'
            + (f"argument-hint: {arguments}\n" if arguments else "") + "---\n\n# A made-up skill\n")


def state(folder: str, name: str) -> None:
    """The folder holding state `name`'s skills alone, each SKILL.md swapped in whole."""
    os.makedirs(folder, exist_ok=True)
    want = STATES[name]
    for n in os.listdir(folder):
        if n not in want:
            shutil.rmtree(os.path.join(folder, n))
    for n, (description, arguments) in want.items():
        path, text = os.path.join(folder, n, "SKILL.md"), head(n, description, arguments)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path) as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        registry.rewrite(path, text)


class Drawn(unittest.TestCase):
    """A made-up skills folder, in the tool's place, inside lib/trial.py's made-up sessions folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.folder = os.path.join(self.w.root, "skills")
        state(self.folder, "b")
        p = patch.object(tool, "SKILLS", self.folder)
        p.start()
        self.addCleanup(p.stop)

    def test_it_draws_every_skill(self):
        got = tool.drawn()
        for part in ('id="watch"', live.src("live.js"), live.src("skills.js"), '<input id="q" data-draft="no"',
                     'data-c="/2-clarify"', 'data-c="/clarify-items"', 'data-c="/agenda-write"', '4 skills',
                     '<span class="mn">— at once</span>'):
            self.assertIn(part, got, part)

    def test_what_a_skill_says_is_escaped(self):
        registry.rewrite(os.path.join(self.folder, "agenda-write", "SKILL.md"),
                         head("agenda-write", "</script><b>out</b>.", ""))
        got = tool.drawn()
        self.assertNotIn("</script><b>out</b>", got)
        self.assertIn("&lt;/script&gt;&lt;b&gt;out&lt;/b&gt;.", got)

    def test_a_skill_cut_short_at_any_length_still_draws_its_row(self):
        path = os.path.join(self.folder, "clarify-items", "SKILL.md")
        whole = head("clarify-items", "Lays out é every item.", "now").encode()
        for cut in range(len(whole) + 1):
            with open(path, "wb") as f:
                f.write(whole[:cut])
            got = tool.drawn()
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertEqual(got.count('<div class="sr">'), 4, f"cut at {cut}")

    def test_its_files_name_the_folder_each_skill_and_its_head(self):
        named = tool.files()
        self.assertIn(self.folder, named)
        for n in STATES["b"]:
            self.assertIn(os.path.join(self.folder, n), named)
            self.assertIn(os.path.join(self.folder, n, "SKILL.md"), named)

    def test_a_write_into_another_sessions_folder_wakes_nothing(self):
        table = live.Table([tool.LIVE])
        first = table.picture("/skills")
        self.w.put("11", "notes.md", "Another session's file.")
        self.w.put("05", "waves/wave-2.md", "# Wave 2\nsent:\n")
        # A picture younger than live.YOUNG is answered unread.
        time.sleep(live.YOUNG)
        self.assertIs(table.picture("/skills"), first)
        state(self.folder, "c")
        time.sleep(live.YOUNG)
        self.assertIsNot(table.picture("/skills"), first)


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + '/skills';
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('main'))]);
});
const settled = async (p, n) => {
  await p.waitForFunction(n => document.querySelectorAll('.sr').length === n
    && !('busy' in document.getElementById('watch').dataset), n, {timeout: 6000});
  await wait(400);
};
// The filter, typed as I would, from a click into it.
const filter = async (p, words) => { await p.click('#q'); await p.keyboard.type(words); await wait(200); };

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
    await settled(b, 3);
    let same = [];
    for (const [name, n] of [['b', 4], ['c', 4], ['d', 2], ['a', 3], ['c', 4]]) {
      await state(name);
      await settled(b, n);
      await c.goto(url);
      await settled(c, n);
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // A skill changed while I type in the filter: my words and cursor hold,
    // and the filter takes in the change.
    await state('b');
    const a = await open();
    await a.goto(url);
    await settled(a, 4);
    await a.evaluate(() => { navigator.clipboard.writeText = async t => { window.copied = t; }; });
    await filter(a, 'each rul');
    const before = await a.evaluate(() => document.querySelectorAll('.sr:not(.none)').length);
    await state('c');
    await a.waitForFunction(() => document.querySelector('.sr:not(.none)'), null, {timeout: 6000}).catch(() => {});
    await wait(400);
    await a.keyboard.type('ing');
    const typed = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('q').value,
      shown: [...document.querySelectorAll('.sr:not(.none) .cmd')].map(b => b.dataset.c).join(' '),
      marked: [...document.querySelectorAll('.sr:not(.none) mark')].map(m => m.textContent).join(' '),
      hint: document.getElementById('hm').textContent}));
    await a.keyboard.press('Enter');
    await wait(200);
    const copied = await a.evaluate(() => window.copied || '');
    said('typing', typed.active === 'q' && typed.words === 'each ruling' && before === 0 && typed.shown === '/clarify-items'
         && typed.marked === 'each ruling' && typed.hint === '↵ copies /clarify-items' && copied === '/clarify-items' && a.loads === 1,
         `my cursor stayed in ${typed.active}, my words read "${typed.words}"; rows before the write: ${before}, after: ${typed.shown}, `
         + `marked "${typed.marked}", the hint reads "${typed.hint}"; Enter copied ${copied || 'nothing'}; ${a.loads} load`);
    await a.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "My filter, while a skill changes, and Enter's copy"}


def serving(tmp: str) -> None:
    """The made-up skills, drawn, with the test's own presses."""
    with trial.world() as w:
        folder = os.path.join(w.root, "skills")
        state(folder, "a")
        tool.SKILLS = folder
        table = live.Table([tool.LIVE])

        def old_route(at: str):
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
        tmp = tempfile.mkdtemp(prefix="skills-page-test-")
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

    def test_my_filter_holds_while_a_skill_changes_and_enter_copies(self):
        self.held("typing")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
