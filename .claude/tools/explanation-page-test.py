#!/usr/bin/env python3
"""Check the Explanation tab: what it draws on the contract, and its list and documents in WebKit and Chromium.

Drawn: on lib/trial.py's made-up folder, the list and a document on the
contract open with their watch, carry the same scripts, name the files
that move them, draw a document or its numbers cut short at any length,
and never write over numbers that cannot be read.

Browser: a server on this session's port, 11NN, draws the made-up
documents, as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  The order I picked and the rail I shut hold while the page changes.

  explanation-page-test.py [NN] [Drawn|Browser]

NN is this session's number, 14 when none is given.
"""

import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("explanation_page_test", os.path.join(HERE, "explanation-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import live  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "14")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"explanation-page-test-{NN}"

SHORT = "# A trial document\nFor a test, from made-up state.\n\n## One section\nA paragraph.\n"
LONG = """# A trial document
For a test, from made-up state.

## One section
A paragraph names a term[^term].

[^term]: A definition, beside it.

> **Ruled** — it holds.

## Two
- **Port** — 1100
- **Band** — 00

## Three
```mermaid
flowchart LR
  a["Ask"]:::ruled --> b["Answer"]:::built
```
Figure: one ask, one answer

## Four
| Name | Port |
|---|---|
| 1100 | 1100 |
Figure: a table
"""
SECOND = "# A second document\nIts line.\n\n## Its section\nWords.\n"
THIRD = "# A third document\nIts own line.\n\n## Its section\nMore words.\n"
# Each state: the documents of session 05, by name, or None for one gone.
STATES = {
    "one": {"trial": SHORT, "second": None, "third": None},
    "two": {"trial": SHORT, "second": SECOND, "third": None},
    "three": {"trial": SHORT, "second": SECOND, "third": THIRD},
    "long": {"trial": LONG, "second": SECOND, "third": None},
    "edited": {"trial": LONG.replace("A trial document", "An edited document").replace("Words.", "Other words."),
               "second": SECOND.replace("Its line.", "Its new line."), "third": None},
    "gone": {"trial": None, "second": SECOND, "third": None},
}


def stand(name: str) -> None:
    """Session 05's documents in state NAME, each written whole, its birth kept."""
    base = tool.folder("05")
    for doc, text in STATES[name].items():
        path = os.path.join(base, f"{doc}.md")
        if text is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            try:
                with open(path) as f:
                    if f.read() == text:
                        continue
            except OSError:
                pass
            registry.rewrite(path, text)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def test_the_list_and_a_document_open_with_their_watch_and_the_same_scripts(self):
        stand("long")
        code = lambda page: re.findall(r"<script(?! type=\"application/json\")[^>]*>", page)
        listed, doc = tool.pictured("05"), tool.pictured("05", "trial")
        for got in (listed, doc):
            for part in ('id="watch"', live.src("explanation.js"), live.src("charts.js"), '<script type="application/json" id="states">'):
                self.assertIn(part, got, part)
            # The way back, the shell's, alone keeps its own click: it only goes to the list.
            self.assertEqual(set(re.findall(r'onclick="([^"]*)"', got)) - {"location.href='/p/explanation/05'"}, set())
        self.assertEqual(code(listed), code(doc))
        self.assertIn('class="ed-list"', listed)
        self.assertIn('<pre class="wait">flowchart LR', doc)
        self.assertIn('id="atab"', doc)

    def test_a_document_gone_shows_the_list_and_every_state_draws(self):
        for name in STATES:
            stand(name)
            for got in (tool.pictured("05"), tool.pictured("05", "trial"), tool.pictured("05", "second")):
                self.assertNotIn("failed to draw", got, name)
        stand("gone")
        self.assertIn('class="ed-list"', tool.pictured("05", "trial"))

    def test_its_files_name_the_folder_each_document_and_the_numbers(self):
        stand("two")
        named = tool.watched("05", "trial")
        base = tool.folder("05")
        for f in (registry.folder("05"), base, os.path.join(base, tool.NUMBERS),
                  os.path.join(base, "trial.md"), os.path.join(base, "second.md")):
            self.assertIn(f, named, f)

    def test_a_document_cut_short_at_any_length_still_draws(self):
        path = os.path.join(tool.folder("05"), "trial.md")
        whole = ("é " + LONG).encode()
        for cut in range(len(whole) + 1):
            with open(path, "wb") as f:
                f.write(whole[:cut])
            for got in (tool.pictured("05"), tool.pictured("05", "trial")):
                self.assertNotIn("failed to draw", got, f"cut at {cut}")

    def test_numbers_cut_short_are_never_written_over_and_lose_no_row(self):
        stand("two")
        tool.numbered("05")
        book = os.path.join(tool.folder("05"), tool.NUMBERS)
        with open(book) as f:
            text = f.read()
        for cut in range(len(text)):
            with open(book, "w") as f:
                f.write(text[:cut])
            got = tool.pictured("05")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertIn("A trial document", got, f"cut at {cut}: a row was lost")
            self.assertIn("A second document", got, f"cut at {cut}: a row was lost")
            if cut:
                with open(book) as f:
                    self.assertEqual(f.read(), text[:cut], f"cut at {cut}: the numbers were written over")


# ---- served --------------------------------------------------------------------------

BROWSERS = trial.SERVER + r"""
const list = base + process.env.PAGE, doc = list + '/trial';
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 || ['SCRIPT', 'STYLE'].includes(n.tagName) || n.id === 'refusal' ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([[...document.body.classList].sort(), walk(document.body)]);
});
const key = p => p.evaluate(() => { const w = document.getElementById('watch'); return w && !('busy' in w.dataset) ? w.dataset.key : ''; });
const caught = async (p, fresh) => {
  const want = await key(fresh);
  for (let i = 0; i < 80 && await key(p) !== want; i++) await wait(100);
  await wait(400);
  return await key(p) === want;
};

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1400, height: 900}});
    // The charts' library comes from the network. Both pages go without, so each draws its source.
    await context.route('**/cdn.jsdelivr.net/**', r => r.abort());
    const open = async () => {
      const p = await context.newPage();
      p.loads = 0;
      p.on('request', r => { if (r.isNavigationRequest() && r.frame() === p.mainFrame()) p.loads++; });
      return p;
    };

    // A changed page, put in place, equals the page drawn fresh, state by state.
    let same = [], loads = [];
    for (const [at, names] of [[list, ['two', 'three', 'edited', 'gone', 'one']], [doc, ['long', 'edited', 'one', 'long', 'gone', 'two']]]) {
      await state('one');
      const b = await open(), c = await open();
      await b.goto(at);
      await wait(600);
      for (const name of names) {
        await state(name);
        await wait(200);
        await c.goto(at);
        await wait(600);
        const on = await caught(b, c);
        same.push(on && await snap(b) === await snap(c) ? name : name + ' differs');
      }
      loads.push(b.loads);
      await b.close();
      await c.close();
    }
    said('fresh', same.every(s => !s.includes('differs')) && loads.every(n => n === 1),
         `put in place, then drawn fresh: ${same.join(', ')}; loads ${loads.join(', ')}`);

    // The order I picked and the rail I shut hold while the page changes.
    await state('two');
    const a = await open();
    await a.goto(list);
    await wait(500);
    await a.click('#order button[data-o="up"]');
    await state('three');
    await a.waitForFunction(() => document.querySelectorAll('.ed-card').length === 3, null, {timeout: 6000}).catch(() => {});
    await wait(300);
    const order = await a.evaluate(() => [...document.querySelectorAll('.ed-card .ed-n')].map(n => parseInt(n.textContent, 10)).join(','));
    await state('long');
    await a.goto(doc);
    await wait(600);
    await a.click('#atab');
    await state('edited');
    await a.waitForFunction(() => document.querySelector('.ed h1').textContent.includes('An edited document'), null, {timeout: 6000}).catch(() => {});
    const shut = await a.evaluate(() => ({shut: document.body.classList.contains('rail-shut'), title: document.querySelector('.ed h1').textContent}));
    said('kept', order === '1,2,3' && shut.shut && shut.title.includes('An edited document') && a.loads === 2,
         `the list I put oldest first reads ${order} once a third landed; the rail stayed shut: ${shut.shut} as the document became "${shut.title}"; ${a.loads} loads, one per address`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "kept": "My order and my rail hold"}


def serving(tmp: str) -> None:
    """The made-up documents, drawn, with the test's own presses."""
    with trial.world():
        table = live.Table(tool.LIVE)

        def old_route(at: str):
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                stand(form["name"][0])
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1,
                  **table.riding(route=old_route, take=old_take, hears=lambda: []))


class Browser(unittest.TestCase):
    """The tab itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="explanation-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "PAGE": serve.address("explanation", "05")})
            with open(os.path.join(tmp, "server.log"), errors="replace") as f:
                cls.logged = f.read()
        finally:
            shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
            shutil.rmtree(tmp, ignore_errors=True)
        cls.seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
        cls.ended = r.stderr.strip()[-1500:] if r.returncode else ""
        cls.missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
        for s in cls.seen:
            print(("" if s["held"] else "FAILED: ") + f"{NAMES[s['name']]}, in {s['engine']}: {s['seen']}.",
                  file=sys.stderr)

    def held(self, name: str) -> None:
        self.assertEqual(self.missing, [], "an engine's build is not installed")
        mine = [s for s in self.seen if s["name"] == name]
        self.assertEqual(sorted(s["engine"] for s in mine), ["chromium", "webkit"],
                         f"the browsers ended early. {self.ended} {self.logged[-800:] if 'Traceback' in self.logged else ''}")
        for s in mine:
            self.assertTrue(s["held"], f"{NAMES[name]}, in {s['engine']}: {s['seen']}")

    def test_a_changed_page_put_in_place_equals_the_page_drawn_fresh(self):
        self.held("fresh")

    def test_my_order_and_my_rail_hold_while_the_page_changes(self):
        self.held("kept")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "serve" in args:
        serving(args[args.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in args if a != NN])
