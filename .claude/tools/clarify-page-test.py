#!/usr/bin/env python3
"""Check the clarify page: its presses, what it draws on the contract, and its page in WebKit and Chromium.

Presses: a press it cannot take is refused, on a wave of its own.

Drawn: on lib/trial.py's made-up folder, 1100 draws every kind of field,
escapes what a session wrote, hands the page's script the answers alone,
names the files that move it, and draws a wave cut short at any length.

Browser: a server on this session's port, 11NN, draws the made-up wave,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My words save as I type, Return moves on, Agree agrees, Send sends, and
  Take it takes a proposal, in one load.
  A chart draws beside its source, and again once its source changes.

  clarify-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 02 when none is given.
"""

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
spec = importlib.util.spec_from_file_location("clarify_page_test", os.path.join(HERE, "clarify-page.py"))
clarify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clarify)
import live  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "02")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"clarify-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

WAVE = "# Wave 3\nsent:\n\n## 1 · Port\nquestion: Which port?\n"

CHART = "```mermaid\nflowchart TB\n  a[\"Ask\"]:::you --> b[\"Answer\"]:::session\n```\nFigure: one ask, one answer"
# Each state the browser asks for by name: a wave's head, and its items.
FIRST = {"n": "1", "title": "Port", "question": "Which port?", "decision": "1100.",
         "why": "It is the one page server. See item 2.", "show": CHART}
SECOND = {"n": "2", "title": "Name", "question": "Which name?", "decision": "trial."}
THIRD = {"n": "3", "title": "Tree", "question": "Which files?", "decision": "Two.", "wrong": "A third exists.",
         "show": "```\nlib/\n  live.py  + new\n  serve.py  ~ changes\n  old.py\n```", "today": "One file.",
         "instead": "- Keep one\n- Split in three"}
STATES = {
    "a": ({}, [FIRST, SECOND]),
    "b": ({}, [{**FIRST, "feedback": "Use 1104."}, {**SECOND, "proposed": "agree\nby: 10\nwhy: It is settled."}]),
    "c": ({}, [{**FIRST, "agree": "yes", "show": CHART.replace("Answer", "Reply")},
               {**SECOND, "proposed": "feedback\nby: 10\n> Call it live."}, THIRD]),
    "d": ({"sent": "yes"}, [{**FIRST, "agree": "yes"}, {**SECOND, "feedback": "Call it live."}, THIRD]),
    "p": ({}, [{**FIRST, "proposed": "feedback\nby: 10\n> Take these words."}, SECOND]),
}


def wave(name: str) -> str:
    head, items = STATES[name]
    return clarify.dump(1, {"sent": "", "then": "", **head}, [dict(it) for it in items])


class Presses(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.path = os.path.join(work.name, "wave-3.md")
        with open(self.path, "w") as f:
            f.write(WAVE)
        # The wave file's own reading is lib/waves.py's, which the tool put in reach.
        p = patch.object(sys.modules["waves"], "waves", return_value=[(3, self.path)])
        p.start()
        self.addCleanup(p.stop)

    def press(self, **form):
        return clarify.take("05", {k: [v] for k, v in form.items()})

    def saved(self):
        with open(self.path) as f:
            return f.read()

    def test_an_unknown_item_is_refused(self):
        self.assertEqual(self.press(act="agree", n="9", on="yes"), "Wave 3 has no item 9. Nothing was saved.")
        self.assertEqual(self.saved(), WAVE)

    def test_an_unknown_act_is_refused(self):
        self.assertEqual(self.press(act="shout", n="1"), "This page takes no such press. Nothing was saved.")
        self.assertEqual(self.saved(), WAVE)

    def test_no_wave_waiting_is_refused(self):
        with open(self.path, "w") as f:
            f.write(WAVE.replace("sent:", "sent: yes"))
        self.assertEqual(self.press(act="agree", n="1", on="yes"),
                         "Session 05 has no wave waiting on you. Nothing was saved.")
        self.assertEqual(self.press(act="send"), "Session 05 has no wave waiting on you. Nothing was typed.")

    def test_sending_a_wave_with_no_items_is_refused(self):
        with open(self.path, "w") as f:
            f.write("# Wave 3\nsent:\n")
        self.assertEqual(self.press(act="send"), "Wave 3 holds no items. Nothing was typed.")

    def test_a_known_press_still_saves(self):
        self.assertEqual(self.press(act="agree", n="1", on="yes"), "")
        self.assertIn("agree: yes", self.saved())

    def test_a_fix_replaces_an_unanswered_item_under_its_number(self):
        block = "## Use port 1104\nquestion: Which port?\ndecision: 1104.\n"
        self.assertEqual(self.press(act="fix", n="1", text=block), "")
        _, items = clarify.parse(self.saved())
        self.assertEqual((items[0]["n"], items[0]["title"], items[0]["decision"]), ("1", "Use port 1104", "1104."))
        self.press(act="agree", n="1", on="yes")
        self.assertEqual(self.press(act="fix", n="1", text=block), "Item 1 holds an answer. Nothing was changed.")

    def test_a_save_swaps_the_wave_whole_and_keeps_its_birth(self):
        was = os.stat(self.path)
        self.assertEqual(self.press(act="feedback", n="1", text="Use 1104."), "")
        now = os.stat(self.path)
        self.assertNotEqual(now.st_ino, was.st_ino)
        self.assertEqual(now.st_birthtime, was.st_birthtime)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def put(self, text: str) -> None:
        self.w.put("05", "waves/wave-1.md", text)

    def test_every_kind_of_field_draws(self):
        self.put(wave("c"))
        got = clarify.drawn("05")
        for part in ('id="t-1"', 'id="t-3"', '<pre class="mmd">flowchart TB', "<figcaption>one ask, one answer</figcaption>",
                     '<a class="link" data-go="2">item 2</a>', '<span class="k">Wrong if</span>',
                     '<span class="lg"><b>+</b>New</span>', '<span class="dim">  old.py</span>',
                     '<h2 class="sec">Today</h2><p>One file.</p>', '<ul class="b "><li>Keep one</li><li>Split in three</li></ul>',
                     "Session 10, your assistant, proposes · Feedback", '<blockquote class="pq">Call it live.</blockquote>',
                     'data-take="2"', '<textarea id="fb-1" data-n="1"', 'id="r-3"', 'id="watch"', live.src("clarify.js")):
            self.assertIn(part, got, part)
        self.assertNotIn("failed to draw", got)

    def test_what_a_session_wrote_is_escaped(self):
        self.put(clarify.dump(1, {"sent": ""}, [{"n": "1", "title": "x", "question": "<script>alert(1)</script>",
                                                 "decision": "ok", "feedback": "</script><b>out</b>"}]))
        got = clarify.drawn("05")
        self.assertNotIn("<script>alert(1)", got)
        self.assertNotIn("</script><b>out</b>", got)
        data = json.loads(re.search(r'<script type="application/json" id="wave">(.*?)</script>', got, re.S).group(1))
        self.assertEqual(data["items"], [{"n": "1", "agree": "", "feedback": "</script><b>out</b>", "status": "", "proposed": ""}])
        self.assertEqual(data["key"], clarify.key("05"))

    def test_a_sent_wave_takes_no_typing(self):
        self.put(wave("d"))
        got = clarify.drawn("05")
        self.assertEqual(got.count("<textarea"), got.count(" disabled>"))

    def test_no_wave_says_so_with_the_same_scripts(self):
        shutil.rmtree(os.path.join(self.w.work, "05", "waves"))
        got = clarify.drawn("05")
        self.assertIn("No items wait", got)
        self.assertIn(live.src("clarify.js"), got)

    def test_a_wave_cut_short_at_any_length_still_draws(self):
        whole = wave("c")
        for cut in range(len(whole) + 1):
            self.put(whole[:cut])
            self.assertNotIn("failed to draw", clarify.drawn("05"), f"cut at {cut}")

    def test_its_files_name_its_wave(self):
        self.put(wave("a"))
        named = clarify.files("05")
        self.assertIn(os.path.join(self.w.work, "05", "waves"), named)
        self.assertIn(os.path.join(self.w.work, "05", "waves", "wave-1.md"), named)


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + process.env.CLARIFY_PAGE;
const state = name => post('/trial/state', {name});
const file = async () => (await fetch(base + '/trial/wave')).text();
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('nav.nums')), walk(document.querySelector('main'))]);
});
const settled = async (p, items) => {
  await p.waitForFunction(n => document.querySelectorAll('#items .item').length === n
    && !('busy' in document.getElementById('watch').dataset), items, {timeout: 6000});
  await wait(400);
};

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1200, height: 800}});
    // The charts' library comes from the network. These pages go without, so each draws its source.
    await context.route('**/cdn.jsdelivr.net/**', r => r.abort());
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
    let same = [];
    for (const [name, items] of [['b', 2], ['c', 3], ['d', 3], ['a', 2], ['p', 2], ['c', 3]]) {
      await state(name);
      await settled(b, items);
      await c.goto(url);
      await settled(c, items);
      for (const p of [b, c]) { await p.click('nav.nums .tab'); await wait(200); }
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My words save as I type, Return moves on, Agree agrees, Send sends, and Take it takes a proposal.
    await state('a');
    const a = await open();
    await a.goto(url);
    await settled(a, 2);
    await a.click('#fb-1');
    await a.keyboard.type('Use 1104.');
    for (let i = 0; i < 40 && !(await file()).includes('feedback: Use 1104.'); i++) await wait(100);
    const saved = (await file()).includes('feedback: Use 1104.');
    await wait(600);
    const typed = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('fb-1').value,
      red: document.getElementById('r-1').style.getPropertyValue('--c'), line: document.querySelector('#t-1 .st').textContent}));
    await a.keyboard.press('Enter');
    const moved = await a.evaluate(() => document.activeElement.id);
    await a.click('#agree');
    for (let i = 0; i < 40 && !/## 2 [^#]*agree: yes/.test(await file()); i++) await wait(100);
    const agreed = /## 2 [^#]*agree: yes/.test(await file());
    await a.waitForFunction(() => document.getElementById('send').textContent === 'Send' && !document.getElementById('send').disabled, null, {timeout: 4000});
    await a.click('#send');
    await a.waitForFunction(() => document.getElementById('send').textContent === 'Sent', null, {timeout: 6000});
    const sent = /^sent: yes$/m.test(await file()), line = await (await fetch(base + '/trial/said')).text();
    await a.waitForFunction(() => [...document.querySelectorAll('.fbx textarea')].every(t => t.disabled), null, {timeout: 4000});
    await state('p');
    await a.waitForSelector('[data-take="1"]:not([disabled])', {timeout: 6000});
    await a.click('[data-take="1"]');
    for (let i = 0; i < 40 && !(await file()).includes('feedback: Take these words.'); i++) await wait(100);
    const took = (await file()).includes('feedback: Take these words.');
    await a.waitForFunction(() => document.querySelector('[data-take="1"]').textContent === '✓ Taken', null, {timeout: 4000});
    said('answers', saved && typed.active === 'fb-1' && typed.words === 'Use 1104.' && typed.red === 'var(--red)' && /^Saved/.test(typed.line)
         && moved === 'fb-2' && agreed && sent && line === '/clarify-items' && took && a.loads === 1,
         `typed words saved: ${saved}, my cursor stayed in ${typed.active}; Return moved it to ${moved}; Agree agreed: ${agreed}; `
         + `Send typed "${line}" and marked the wave sent: ${sent}; Take it took the proposal: ${took}; ${a.loads} load`);

    // With the charts' library in reach: a chart draws beside its source,
    // and draws again once its source changes. The library is asked first,
    // so a chart that fails to draw never passes as unreachable.
    await state('a');
    const reached = await fetch('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs').then(r => r.ok, () => false);
    const net = await browser.newContext({viewport: {width: 1200, height: 800}});
    const now = await net.newPage();
    await now.goto(url);
    if (!reached) {
      said('charts', true, 'unproven here: the charts\' library could not be reached, so no chart drew');
    } else {
      const drew = await now.waitForFunction(() => document.querySelector('#items .chart svg'), null, {timeout: 12000}).then(() => true, () => false);
      await wait(1200);
      const kept = await now.evaluate(() => { const pre = document.querySelector('#t-1 pre.mmd');
        return !!pre && pre.hidden && pre.nextElementSibling.classList.contains('chart'); });
      await state('c');
      const again = await now.waitForFunction(() => { const c = document.querySelectorAll('#t-1 .chart');
        return c.length === 1 && c[0].textContent.includes('Reply'); }, null, {timeout: 12000}).then(() => true, () => false);
      said('charts', drew && kept && again,
           `a chart drew: ${drew}, beside its hidden source: ${kept}; its source changed, and it drew again: ${again}`);
    }
    await net.close();

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "answers": "My answers", "charts": "The charts"}


def serving(tmp: str) -> None:
    """The made-up folder's wave, with the test's own presses."""
    typed = []
    with trial.world() as w, patch.object(panes, "say", lambda pane, line, **more: typed.append(line) or True):
        path = os.path.join(w.work, "05", "waves", "wave-1.md")
        table = live.Table([clarify.LIVE])

        def old_route(at: str):
            bare = at.partition("?")[0]
            if bare == "/trial/wave":
                with open(path) as f:
                    return f.read().encode(), "text/plain; charset=utf-8"
            if bare == "/trial/said":
                return (typed[-1] if typed else "").encode(), "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                registry.rewrite(path, wave(form["name"][0]))
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
        tmp = tempfile.mkdtemp(prefix="clarify-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "CLARIFY_PAGE": serve.address("clarify", "05")})
            with open(os.path.join(tmp, "server.log"), errors="replace") as f:
                cls.logged = f.read()
        finally:
            shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
            shutil.rmtree(tmp, ignore_errors=True)
        cls.seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
        cls.ended = r.stderr.strip()[-1500:] if r.returncode else ""
        cls.missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
        for s in cls.seen:
            print(("" if s["held"] else "FAILED: ") + f"{NAMES[s['name']]}, in {s['engine']}: {s['seen']}.")

    def held(self, name: str) -> None:
        self.assertEqual(self.missing, [], "an engine's build is not installed")
        mine = [s for s in self.seen if s["name"] == name]
        self.assertEqual(sorted(s["engine"] for s in mine), ["chromium", "webkit"],
                         f"the browsers ended early. {self.ended} {self.logged[-800:] if 'Traceback' in self.logged else ''}")
        for s in mine:
            self.assertTrue(s["held"], f"{NAMES[name]}, in {s['engine']}: {s['seen']}")

    def test_a_changed_page_put_in_place_equals_the_page_drawn_fresh(self):
        self.held("fresh")

    def test_my_answers_save_move_on_agree_send_and_take(self):
        self.held("answers")

    def test_a_chart_draws_beside_its_source_and_again_once_it_changes(self):
        self.held("charts")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
