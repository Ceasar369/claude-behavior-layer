#!/usr/bin/env python3
"""Check library-page.py on a library of its own, never the real one.

Tree, Page, Render, Rail, Graph: how it reads and draws a library.

Drawn: on a made-up library, 1100 draws the book on the contract. A review
record or a word cut short at any length draws every row, never an error.
Its files name the folder, its tree, each word and graph, and the review
record, and a write into another session's folder wakes nothing.

Browser: a server on this session's port, 11NN, draws the made-up library,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  A word added while I type in Find: my words and my cursor hold, and the
  word shows within a second. A review button marks its word in place,
  in one load.

  library-page-test.py [NN] [Tree|Page|Render|Rail|Graph|Drawn|Browser]

NN is this session's number, 15 when none is given.
"""

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
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

# The tool as 1100 and the review record load it, so one patch reaches both.
tool = page.tool("library-page")
review = page.tool("library-review")

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "15")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"library-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

MOC = """# Library

## Rules

A chapter is `##`.

- [[not-a-word|Not a word]]

## Alpha

### Direct

- [[one|One]]
- [[two|Two]]

### Deep

#### Inner

- [[three|Three]]

## Beta

### Only

- [[four|Four]]
"""
PAGE = ("# One\n\nUp: [[library-MOC|Library]]\n\n## What it is\n\nA `thing`.\n\nMore <b>.\n\n"
        "## What it is not\n\nNot two.\n\nSource: https://example.com/one\n")


class Tree(unittest.TestCase):
    def test_a_heading_holding_no_subchapter_is_no_chapter(self):
        self.assertEqual([c["name"] for c in tool.tree(MOC)], ["Alpha", "Beta"])

    def test_each_word_sits_under_its_tiers_with_its_number(self):
        got = {slug: trail for slug, _, trail in tool.spots(tool.tree(MOC))}
        self.assertEqual(got["two"], ["1 Alpha", "1.1 Direct"])
        self.assertEqual(got["three"], ["1 Alpha", "1.2 Deep", "1.2.1 Inner"])
        self.assertEqual(got["four"], ["2 Beta", "2.1 Only"])
        self.assertNotIn("not-a-word", got)


class Page(unittest.TestCase):
    def test_a_page_splits_into_sections_and_its_source(self):
        sections, source = tool.parts(PAGE)
        self.assertEqual([h for h, _ in sections], ["What it is", "What it is not"])
        self.assertEqual(sections[0][1], ["A `thing`.", "More <b>."])
        self.assertEqual(source, "https://example.com/one")

    def test_its_words_are_escaped(self):
        self.assertEqual(tool.inline("A `x` <b>"), "A <code>x</code> &lt;b&gt;")

    def test_a_source_that_is_no_address_is_no_link(self):
        drawn = tool.reading("x", "X", [], "## A\n\nB\n\nSource: javascript:alert(1)\n")
        self.assertNotIn("<a ", drawn)


class Render(unittest.TestCase):
    def library(self, moc):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        with open(os.path.join(folder.name, tool.MOC), "w") as f:
            f.write(moc)
        with open(os.path.join(folder.name, "one.md"), "w") as f:
            f.write(PAGE)
        before = tool.LIBRARY
        tool.LIBRARY = folder.name
        self.addCleanup(setattr, tool, "LIBRARY", before)
        return folder.name

    def test_a_word_with_no_file_says_so(self):
        self.library(MOC)
        drawn = tool.drawn()
        self.assertIn('id="p-one"', drawn)
        self.assertIn("No page for this word.", drawn)

    def test_a_page_added_shows_on_the_next_draw(self):
        folder = self.library(MOC)
        self.assertNotIn("Five", tool.drawn())
        with open(os.path.join(folder, tool.MOC), "a") as f:
            f.write("- [[five|Five]]\n")
        self.assertIn("Five", tool.drawn())

    def test_an_empty_library_says_so(self):
        self.library("# Library\n")
        self.assertIn("No words in the library.", tool.drawn())


GRAPH = """# Flow

Up: [[library-MOC|Library]]

## The text

The headline.

A paragraph.

- **Who starts it** — the member

## The graph

1. First box [[one]]
2. Is it so?
   - yes: A branch [[two]]
3. Last box [[nowhere]]

Figure: the caption.

Unproven: the order.

Source: https://example.com/flow
"""


class Rail(unittest.TestCase):
    def test_words_sort_alphabetically_and_number_by_place(self):
        drawn = tool.contents(tool.tree(MOC.replace("- [[one|One]]\n- [[two|Two]]", "- [[two|Two]]\n- [[one|One]]")))
        self.assertLess(drawn.index('<span class="n">1.1.1</span> One'), drawn.index('<span class="n">1.1.2</span> Two'))
        self.assertIn('<span class="n">1.2.1.1</span> Three', drawn)

    def test_graphs_come_first_lettered_then_a_line_and_counts_add_up(self):
        moc = MOC.replace("### Direct\n\n", "### Direct\n\n- Graph: [[flow|Flow]]\n- Graph: [[also|Also]]\n")
        drawn = tool.contents(tool.tree(moc))
        a, b = drawn.index('<span class="n">A</span> Flow'), drawn.index('<span class="n">B</span> Also')
        self.assertTrue(a < b < drawn.index('<hr class="t-sep">') < drawn.index("1.1.1"))
        self.assertEqual(drawn.count('<hr class="t-sep">'), 1)
        self.assertIn('Direct<span class="count plain">4</span>', drawn)
        self.assertIn('Deep<span class="count plain">1</span>', drawn)
        self.assertIn('Alpha<span class="count plain">5</span>', drawn)


class Graph(unittest.TestCase):
    def test_a_graph_reads_its_boxes_branches_and_marks(self):
        got = tool.chart(GRAPH)
        self.assertEqual([s["box"] for s in got["steps"]],
                         [("First box", "one"), ("Is it so?", ""), ("Last box", "nowhere")])
        self.assertEqual(got["steps"][1]["branch"], ("yes", ("A branch", "two")))
        self.assertEqual(got["text"][2], ("fact", ("Who starts it", "the member")))
        self.assertEqual((got["caption"], got["unproven"], got["sources"]),
                         ("the caption.", ["Unproven: the order."], ["https://example.com/flow"]))
        self.assertEqual(tool.linked(GRAPH), ["one", "nowhere", "two"])

    def test_lanes_each_hold_their_own_path_and_marks(self):
        lanes = GRAPH.replace("1. First box [[one]]\n2. Is it so?\n   - yes: A branch [[two]]\n3. Last box [[nowhere]]",
                              "### Left\n\n1. First box [[one]]\n2. Next\n\nUnproven: the left.\n\n"
                              "### Right\n\n1. Other [[two]]")
        got = tool.chart(lanes)
        self.assertEqual([(lane["name"], len(lane["steps"])) for lane in got["lanes"]], [("Left", 2), ("Right", 1)])
        self.assertEqual(got["lanes"][0]["unproven"], ["Unproven: the left."])
        self.assertEqual(got["unproven"], ["Unproven: the order."])
        self.assertEqual(tool.linked(lanes), ["one", "two"])
        drawn = tool.lane(got["lanes"][0], {"one": "One"}, True)
        self.assertTrue(drawn.startswith('<div class="gx-lane plain"><h3 class="gx-name">Left</h3><div class="gx-chart">'))
        self.assertIn('<p class="stand">Unproven: the left.</p>', drawn)

    def test_a_series_shows_in_one_line_above_the_headline(self):
        got = tool.chart(GRAPH.replace("## The text\n\n", "## The text\n\nSeries: A login, in order, 1 of 3\n\n"))
        self.assertEqual(got["series"], "A login, in order, 1 of 3")
        self.assertEqual(got["text"][0], ("p", "The headline."))
        drawn = tool.graphing("flow", "Flow", GRAPH.replace("## The text\n\n", "## The text\n\nSeries: S, 1 of 2\n\n"), {})
        self.assertIn('<p class="gx-series">Series: S, 1 of 2</p><h1>The headline.</h1>', drawn)
        self.assertNotIn("gx-series", tool.graphing("flow", "Flow", GRAPH, {}))

    def test_one_path_is_one_unnamed_lane(self):
        got = tool.chart(GRAPH)
        self.assertEqual([lane["name"] for lane in got["lanes"]], [""])
        self.assertNotIn("gx-name", tool.lane(got["lanes"][0], {}, False))

    def test_a_graph_sits_in_its_home_subchapter_alone(self):
        chapters = tool.tree(MOC.replace("### Direct\n\n", "### Direct\n\n- Graph: [[flow|Flow]]\n"))
        self.assertEqual(chapters[0]["subs"][0]["graphs"], [("flow", "Flow")])
        self.assertNotIn("flow", [s for s, _, _ in tool.spots(chapters)])

    def test_a_box_is_a_page_box_and_its_word_links_back(self):
        folder = Render.library(self, MOC.replace("### Direct\n\n", "### Direct\n\n- Graph: [[flow|Flow]]\n"))
        os.mkdir(os.path.join(folder, tool.GRAPHS))
        with open(os.path.join(folder, tool.GRAPHS, "flow.md"), "w") as f:
            f.write(GRAPH)
        drawn = tool.drawn()
        self.assertIn('class="t-word t-graph" data-g="flow"', drawn)
        # A box's word wears its number in the rail, then its name.
        self.assertIn('<button class="gx-box" data-w="one">First box<small>1.1.1 One</small></button>', drawn)
        self.assertIn('<button class="gx-box bad" data-w="two">', drawn)
        self.assertIn('<div class="gx-box">Last box</div>', drawn)
        self.assertIn('<em>no</em>', drawn)
        self.assertEqual(drawn.count("Explained in: Flow"), 2)

    def test_a_word_in_two_graphs_shows_both_lines(self):
        moc = MOC.replace("### Direct\n\n", "### Direct\n\n- Graph: [[flow|Flow]]\n- Graph: [[also|Also]]\n")
        folder = Render.library(self, moc)
        os.mkdir(os.path.join(folder, tool.GRAPHS))
        for name in ("flow", "also"):
            with open(os.path.join(folder, tool.GRAPHS, f"{name}.md"), "w") as f:
                f.write(GRAPH)
        one = tool.drawn().split('id="p-one"')[1].split("</article>")[0]
        self.assertIn('data-g="flow">', one)
        self.assertIn("Explained in: Flow", one)
        self.assertIn('data-g="also">', one)
        self.assertIn("Explained in: Also", one)


FLOWED = MOC.replace("### Direct\n\n", "### Direct\n\n- Graph: [[flow|Flow]]\n")
FIVE = FLOWED.replace("- [[four|Four]]\n", "- [[four|Four]]\n- [[five|Five]]\n")
CHANGED = PAGE.replace("Not two.", "Not three.")
# Each state the browser asks for by name: each file, by its place in the
# library, and the words reviewed, as (word, its file then).
STATES = {
    "a": ({tool.MOC: MOC, "one.md": PAGE}, []),
    "b": ({tool.MOC: FLOWED, "one.md": PAGE, "graphs/flow.md": GRAPH}, []),
    "c": ({tool.MOC: FLOWED, "one.md": CHANGED, "graphs/flow.md": GRAPH}, [("one", PAGE)]),
    "d": ({tool.MOC: FIVE, "one.md": CHANGED, "graphs/flow.md": GRAPH, "five.md": "# Five\n\n## What it is\n\nFive.\n"},
          [("one", PAGE)]),
}


def state(folder: str, name: str) -> None:
    """The library holding state `name`'s files alone, each swapped in
    whole, and its review record holding its words reviewed on 1 November."""
    files, reviewed = STATES[name]
    os.makedirs(os.path.join(folder, tool.GRAPHS), exist_ok=True)
    for at, _, names in list(os.walk(folder)):
        for n in names:
            if os.path.relpath(os.path.join(at, n), folder) not in files:
                os.remove(os.path.join(at, n))
    for at, text in files.items():
        path = os.path.join(folder, at)
        try:
            with open(path) as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        registry.rewrite(path, text)
    rows = tool.numbered(tool.tree(files[tool.MOC]))
    record = {w: {"text": text, "home": review.home(rows, next(r for r in rows if r["slug"] == w)),
                  "at": "2026-11-01 09:00"} for w, text in reviewed}
    if record != review.load():
        os.makedirs(review.FOLDER, exist_ok=True)
        registry.rewrite(review.RECORD, json.dumps(record))


class Drawn(unittest.TestCase):
    """A made-up library and review record, in the tool's place, inside
    lib/trial.py's made-up sessions folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.folder = os.path.join(self.w.root, "library")
        for p in (patch.object(tool, "LIBRARY", self.folder),
                  patch.object(review, "FOLDER", os.path.join(self.w.root, "review")),
                  patch.object(review, "RECORD", os.path.join(self.w.root, "review", "reviews.json"))):
            p.start()
            self.addCleanup(p.stop)
        state(self.folder, "c")

    def test_it_draws_the_book_on_the_contract(self):
        got = tool.drawn()
        for part in ('id="watch"', live.src("live.js"), live.src("library.js"), '<input id="q" data-draft="no"',
                     'id="p-one"', 'id="g-flow"', 'class="t-word t-graph" data-g="flow"', "Not three.",
                     'class="rv-line rv-changed"'):
            self.assertIn(part, got, part)
        self.assertNotIn("typePost", got)

    def test_an_empty_library_says_so_and_still_wears_its_watch(self):
        registry.rewrite(os.path.join(self.folder, tool.MOC), "# Library\n")
        got = tool.drawn()
        self.assertIn(tool.EMPTY, got)
        self.assertIn('id="watch"', got)

    def test_a_review_record_cut_short_at_any_length_keeps_every_row(self):
        with open(review.RECORD, "rb") as f:
            whole = f.read()
        rows = tool.drawn().count('class="t-word')
        for cut in range(len(whole) + 1):
            with open(review.RECORD, "wb") as f:
                f.write(whole[:cut])
            got = tool.drawn()
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertEqual(got.count('class="t-word'), rows, f"cut at {cut}")

    def test_a_word_or_a_graph_cut_short_at_any_length_keeps_every_row(self):
        rows = tool.drawn().count('class="t-word')
        for at, whole in (("one.md", CHANGED.replace("thing", "thé").encode()), ("graphs/flow.md", GRAPH.encode())):
            path = os.path.join(self.folder, at)
            for cut in range(len(whole) + 1):
                with open(path, "wb") as f:
                    f.write(whole[:cut])
                got = tool.drawn()
                self.assertNotIn("failed to draw", got, f"{at} cut at {cut}")
                self.assertEqual(got.count('class="t-word'), rows, f"{at} cut at {cut}")

    def test_its_files_name_its_tree_each_word_and_graph_and_the_review_record(self):
        named = tool.files()
        for at in (self.folder, os.path.join(self.folder, tool.MOC), os.path.join(self.folder, "one.md"),
                   os.path.join(self.folder, "two.md"), os.path.join(self.folder, tool.GRAPHS),
                   os.path.join(self.folder, tool.GRAPHS, "flow.md"), review.FOLDER, review.RECORD):
            self.assertIn(at, named)

    def test_a_write_into_another_sessions_folder_wakes_nothing(self):
        table = live.Table([tool.LIVE])
        first = table.picture("/library")
        self.w.put("11", "notes.md", "Another session's file.")
        self.w.put("05", "waves/wave-2.md", "# Wave 2\nsent:\n")
        # A picture younger than live.YOUNG is answered unread.
        time.sleep(live.YOUNG)
        self.assertIs(table.picture("/library"), first)
        state(self.folder, "d")
        time.sleep(live.YOUNG)
        self.assertIsNot(table.picture("/library"), first)

    def test_a_press_naming_nothing_is_refused(self):
        self.assertEqual(tool.take({"act": ["no such act"]}), "'' is refused. Say reviewed or not-reviewed.")


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + '/library';
const state = name => post('/trial/state', {name});
const record = async () => (await fetch(base + '/trial/record')).text();
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('aside')), walk(document.querySelector('main'))]);
});
// What shows each state has arrived.
const SHOWS = {
  a: () => !document.querySelector('.t-graph') && document.body.innerHTML.includes('Not two.'),
  b: () => !!document.querySelector('.t-graph') && document.body.innerHTML.includes('Not two.'),
  c: () => document.body.innerHTML.includes('Not three.') && !document.querySelector('[data-w="five"]'),
  d: () => !!document.querySelector('#found [data-w="five"]'),
};
const settled = async (p, name) => {
  await p.waitForFunction(([name, shows]) => new Function('return (' + shows[name] + ')()')()
    && !('busy' in document.getElementById('watch').dataset), [name, Object.fromEntries(Object.entries(SHOWS).map(([k, f]) => [k, f.toString()]))], {timeout: 6000});
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
    await b.goto(url + '#one');
    await settled(b, 'a');
    let same = [];
    for (const name of ['b', 'c', 'd', 'a', 'c']) {
      await state(name);
      await settled(b, name);
      await c.goto(url + '#one');
      await settled(c, name);
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // A word added while I type in Find: my words and cursor hold, and the
    // word shows within a second. Then a review button marks its word in place.
    await state('c');
    const a = await open();
    await a.goto(url);
    await settled(a, 'c');
    // The page has held its watch a while, as an open page has.
    await wait(4000);
    await a.click('#q');
    await a.keyboard.type('fi');
    const t0 = Date.now();
    await state('d');
    const shown = await a.waitForSelector('#found [data-w="five"]:not([hidden])', {timeout: 6000}).then(() => Date.now() - t0, () => -1);
    await a.keyboard.type('ve');
    const typed = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('q').value,
      found: [...document.querySelectorAll('#found .t-word:not([hidden])')].map(b => b.dataset.w).join(' ')}));
    await a.keyboard.press('Escape');
    await a.evaluate(() => { location.hash = 'two'; });
    await a.click('#p-two .rv-set');
    const marked = await a.waitForSelector('#p-two .rv-line.rv-ok', {timeout: 6000}).then(() => true, () => false);
    const kept = (await record()).includes('"two"');
    said('typing', typed.active === 'q' && typed.words === 'five' && typed.found === 'five' && shown >= 0 && shown <= 1000
         && marked && kept && a.loads === 1,
         `my cursor stayed in ${typed.active}, my words read "${typed.words}", found: ${typed.found}; the word added showed in ${shown} ms; `
         + `the review button marked its word in place: ${marked}, and kept it: ${kept}; ${a.loads} load`);
    await a.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "My typing, while a word is added, and a review"}


def serving(tmp: str) -> None:
    """The made-up library, drawn, with the test's own presses."""
    with trial.world() as w:
        folder = os.path.join(w.root, "library")
        tool.LIBRARY = folder
        review.FOLDER = os.path.join(w.root, "review")
        review.RECORD = os.path.join(review.FOLDER, "reviews.json")
        state(folder, "a")
        table = live.Table([tool.LIVE])

        def old_route(at: str):
            if at.partition("?")[0] == "/trial/record":
                return json.dumps(review.load()).encode(), "text/plain; charset=utf-8"
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
        tmp = tempfile.mkdtemp(prefix="library-page-test-")
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

    def test_my_typing_holds_while_a_word_is_added_and_a_review_marks_in_place(self):
        self.held("typing")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
