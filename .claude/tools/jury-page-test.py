#!/usr/bin/env python3
"""Check the jury tab: its presses, what it draws on the contract, and its page in WebKit and Chromium.

Presses: an edit it cannot read, a run it does not hold and a launched
run are each refused, on a run of their own.

Drawn: on lib/trial.py's made-up folder, the tab on the contract opens
with its watch, names the files that move it, and draws its plan and
results cut short at any length, saying which cannot be read.

Browser: a server on this session's port, 11NN, draws the made-up run,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My words hold while the page changes, and save as I type, and Launch
  types /jury-run.

  jury-page-test.py [NN] [PlanEdits|Drawn|Browser]

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
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("jury_page_test", os.path.join(HERE, "jury-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import live  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "14")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"jury-page-test-{NN}"

REFUSED = "The edit was not a plan this page can read. Nothing was saved."


class PlanEdits(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.work = work.name
        with open(os.path.join(work.name, "plan.json"), "w") as f:
            json.dump({"run": "r1", "question": "Which port?"}, f)
        self.saves = []
        for p in (patch.object(tool, "named", return_value=work.name),
                  patch.object(tool, "merged", side_effect=lambda plan, sent: {**plan, **sent}),
                  patch.object(tool.jury, "save", side_effect=lambda path, plan: self.saves.append(plan))):
            p.start()
            self.addCleanup(p.stop)

    def edit(self, sent: str) -> str:
        return tool.take("05", {"act": ["plan"], "plan": [sent]})

    def test_bad_json_is_refused(self):
        self.assertEqual(self.edit("{not json"), REFUSED)
        self.assertEqual(self.saves, [])

    def test_json_that_is_no_plan_is_refused(self):
        self.assertEqual(self.edit("[1, 2]"), REFUSED)
        self.assertEqual(self.saves, [])

    def test_no_such_run_is_refused(self):
        self.assertEqual(tool.take("05", {"act": ["launch"], "run": ["r9"]}),
                         "Session 05 has no jury run r9. Nothing was typed.")
        self.assertEqual(self.saves, [])

    def test_launching_a_launched_run_is_refused(self):
        with open(os.path.join(self.work, "results.json"), "w") as f:
            json.dump({"run": "r1", "state": "running"}, f)
        self.assertEqual(tool.take("05", {"act": ["launch"]}), "Jury run r1 was already launched. Nothing was typed.")

    def test_a_good_edit_still_saves(self):
        self.assertEqual(self.edit('{"question": "Which band?"}'), "")
        self.assertEqual(self.saves[0]["question"], "Which band?")


# ---- the made-up run, in each state ----------------------------------------------

RUNNING = {"state": "running", "launched": "2026-11-01T09:00:00",
           "step": {"n": 1, "steps": 2, "what": "Jurors answer", "asked": 3, "answered": 1, "at_once": 3}}
DONE = {"state": "done", "launched": "2026-11-01T09:00:00", "done": "2026-11-01T09:20:00", "jurors": {"asked": 3},
        "conclusion": {"lead": "It holds, <b>3 of 3</b>.", "model": "claude-opus-5-5"}, "cost": {"line": "Cost · $1.20"},
        "claims": [{"n": 1, "text": "Port is 1100.", "outcome": "holds", "count": "3 of 3", "why": "Every juror read it.",
                    "rounds": 1, "answers": [{"juror": "A1", "session": "A", "answer": "holds", "why": "It reads 1100.",
                                              "quote": "PORT = 1100", "place": "lib/ports.py:12", "model": "opus"},
                                             {"juror": "A2", "session": "A", "answer": "no answer"}]}]}
# Each state: what the plan changes, the results, and whether an earlier run stands beside it.
STATES = {
    "plan": ({}, None, False),
    "edited": ({"question": "Does it still hold?", "context": ["Made up.", "A second line."]}, None, False),
    "shape": ({"shape": "yes or no"}, None, False),
    "two": ({}, None, True),
    "running": ({}, RUNNING, False),
    "done": ({}, DONE, False),
    "bad": ({}, '{"state": "do', False),
}
EARLIER = "0000-earlier"


class Run:
    """Session 05's made-up run, put in each state whole."""

    def __init__(self):
        self.run = tool.newest("05")
        with open(os.path.join(self.run, "plan.json")) as f:
            self.plan = json.load(f)

    def stand(self, name: str) -> None:
        change, results, earlier = STATES[name]
        registry.write_whole(os.path.join(self.run, "plan.json"), json.dumps({**self.plan, **change}, indent=1))
        self.results(results)
        self.earlier(earlier)

    def results(self, got) -> None:
        path = os.path.join(self.run, "results.json")
        if got is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            registry.write_whole(path, got if isinstance(got, str) else json.dumps({"run": self.plan["run"], **got}))

    def earlier(self, on: bool) -> None:
        there = os.path.join(os.path.dirname(self.run), EARLIER)
        if on:
            os.makedirs(there, exist_ok=True)
            registry.write_whole(os.path.join(there, "plan.json"),
                                 json.dumps({**self.plan, "run": EARLIER, "question": "An earlier question?"}))
        else:
            shutil.rmtree(there, ignore_errors=True)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.r = Run()

    def test_the_tab_opens_with_its_watch_and_its_own_script(self):
        got = tool.drawn("05")
        for part in ('id="watch"', live.src("jury.js"), '<script type="application/json" id="plan">', 'id="launch"',
                     'contenteditable="plaintext-only"'):
            self.assertIn(part, got, part)
        self.assertNotIn("onclick=", got)

    def test_every_state_draws_with_the_same_scripts(self):
        code = lambda page: re.findall(r"<script(?! type=\"application/json\")[^>]*>", page)
        first = code(tool.drawn("05"))
        for name in STATES:
            self.r.stand(name)
            got = tool.drawn("05")
            self.assertNotIn("failed to draw", got, name)
            self.assertEqual(code(got), first, name)

    def test_what_a_session_wrote_is_escaped(self):
        self.r.stand("done")
        got = tool.drawn("05")
        self.assertNotIn("<b>3 of 3</b>", got)
        self.r.plan["question"] = "</script><b>out</b>"
        self.r.stand("plan")
        got = tool.drawn("05")
        data = json.loads(re.search(r'<script type="application/json" id="plan">(.*?)</script>', got, re.S).group(1))
        self.assertEqual(data["question"], "</script><b>out</b>")
        self.assertNotIn("</script><b>out</b>", got)

    def test_its_files_name_each_run_and_its_two_files(self):
        self.r.stand("two")
        named = tool.files("05")
        for f in (tool.jury.folder("05"), self.r.run, os.path.join(self.r.run, "results.json"),
                  os.path.join(os.path.dirname(self.r.run), EARLIER, "plan.json")):
            self.assertIn(f, named, f)

    def test_its_files_cut_short_at_any_length_still_draw_and_say_so(self):
        self.r.stand("two")
        for name, text in (("results.json", json.dumps({"run": self.r.plan["run"], **DONE})),
                           ("plan.json", json.dumps(self.r.plan))):
            path = os.path.join(self.r.run, name)
            for cut in range(len(text)):
                registry.write_whole(path, text[:cut])
                got = tool.drawn("05")
                self.assertNotIn("failed to draw", got, f"{name} cut at {cut}")
                self.assertIn(f"its {name} is unreadable", got, f"{name} cut at {cut}")
                self.assertIn("An earlier question?", got, f"{name} cut at {cut}: a row was lost")
            registry.write_whole(path, text)
        self.assertNotIn("unreadable", tool.drawn("05"))


# ---- served --------------------------------------------------------------------------

BROWSERS = trial.SERVER + r"""
const url = base + process.env.PAGE;
const state = name => post('/trial/state', {name});
const file = async () => (await fetch(base + '/trial/plan')).text();
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('main'))]);
});
const key = p => p.evaluate(() => { const w = document.getElementById('watch'); return w && !('busy' in w.dataset) ? w.dataset.key : ''; });
const caught = async (p, fresh) => {
  const want = await key(fresh);
  for (let i = 0; i < 80 && await key(p) !== want; i++) await wait(100);
  await wait(300);
  return await key(p) === want;
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
    await state('plan');
    const b = await open(), c = await open();
    await b.goto(url);
    await wait(500);
    let same = [];
    for (const name of ['edited', 'shape', 'two', 'running', 'done', 'bad', 'plan', 'done', 'plan']) {
      await state(name);
      await wait(200);
      await c.goto(url);
      await wait(300);
      const on = await caught(b, c);
      same.push(on && await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My words hold while the page changes, and save as I type, and Launch types /jury-run.
    await state('plan');
    const a = await open();
    await a.goto(url);
    await wait(500);
    await a.click('h1.q');
    await a.keyboard.press('End');
    await a.keyboard.type(' Really?');
    for (let i = 0; i < 40 && !(await file()).includes('Really?'); i++) await wait(100);
    const saved = (await file()).includes('Really?');
    await post('/trial/earlier', {});
    await a.waitForSelector('.jt-plans a.row', {timeout: 6000}).catch(() => {});
    await a.keyboard.type(' Yes.');
    await wait(200);
    const held = await a.evaluate(() => ({rows: document.querySelectorAll('.jt-plans a.row').length,
      words: document.querySelector('h1.q').textContent, mine: document.activeElement.matches('h1.q')}));
    await a.click('.pills[data-k="sessions.0.effort"] button[data-v="max"]').catch(() => {});
    for (let i = 0; i < 40 && !/"effort": "max"/.test(await file()); i++) await wait(100);
    const picked = /"effort": "max"/.test(await file()) && (await file()).includes('Really? Yes.');
    await a.click('#launch');
    let line = '';
    for (let i = 0; i < 40 && !(line = await (await fetch(base + '/trial/said')).text()); i++) await wait(100);
    said('words', saved && held.rows === 2 && held.words.endsWith('Really? Yes.') && held.mine && picked
         && /^\/jury-run \S+$/.test(line) && a.loads === 1,
         `typed words saved: ${saved}; a run landed beside it (${held.rows} rows), and my words held: "${held.words}", my cursor in them: ${held.mine}; `
         + `a pill and my words saved: ${picked}; Launch typed "${line}"; ${a.loads} load`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "words": "My words hold, save, and Launch types"}


def serving(tmp: str) -> None:
    """The made-up run, drawn, with the test's own presses."""
    typed = []
    with trial.world(), patch.object(panes, "say", lambda pane, line, **more: typed.append(line) or True):
        r = Run()
        table = live.Table([tool.LIVE])

        def old_route(at: str):
            bare = at.partition("?")[0]
            if bare == "/trial/plan":
                with open(os.path.join(r.run, "plan.json")) as f:
                    return f.read().encode(), "text/plain; charset=utf-8"
            if bare == "/trial/said":
                return (typed[-1] if typed else "").encode(), "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                r.stand(form["name"][0])
                return ""
            if at == "/trial/earlier":
                r.earlier(True)
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
        tmp = tempfile.mkdtemp(prefix="jury-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "PAGE": serve.address("jury", "05")})
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

    def test_my_words_hold_save_and_launch_types(self):
        self.held("words")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "serve" in args:
        serving(args[args.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in args if a != NN])
