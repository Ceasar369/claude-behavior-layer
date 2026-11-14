#!/usr/bin/env python3
"""Check the assistant page: its presses, what it draws on the contract, and its page in WebKit and Chromium.

Presses: each act types its own line into the right pane, a press it
cannot take is refused in a sentence, and Auto-send keeps its switch.

Drawn: on lib/trial.py's made-up folder, the page on the contract draws
drawing()'s parts, names every file it reads, draws each state file cut
short at any length, and a gone session's time stands still. states
prints each mission's need.

Browser: a server on this session's port, 11NN, draws the made-up plan,
as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  The view, a fold and the scroll I left stay while the page changes, in one load.
  Type types, Send after it presses Return alone, and Auto-send keeps its switch.

  assistant-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 13 when none is given. Its port must be
free: this session's own copy of 1100 serves there too.
"""

import builtins
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("assistant_page_test", os.path.join(HERE, "assistant-page.py"))
assistant = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assistant)
import drive  # noqa: E402
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "13")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"assistant-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

# The made-up plan's missions, as lib/trial.py's world holds them, and a
# second stage some states add.
A1 = {"id": "A1", "name": "trial work", "session": "11", "title": "11-trial-work", "queued": "2026-11-01T08:59:00"}
A2 = {"id": "A2", "name": "later work"}
A3 = {"id": "A3", "name": "gone work", "session": "12", "title": "12-gone-work", "queued": "2026-11-01T08:58:00"}
B1 = {"id": "B1", "name": "next work"}
MOVES = ("# Wave 1 answered · read to 2026-11-01T09:00:00\n\n## Your moves\n1. Send the words below.\n\n"
         "Send to session 05.\n> Hello, session 05.\n\n## Item 1 · agree\n> It holds.\n\n## Item 2 · feedback\n> Not yet.\n")
# Each state the browser asks for by name: the plan, A1's answer, and Auto-send's switch.
STATES = {
    "a": ([("Stage A", [A1, A2, A3])], "# Holds\n\nIt holds.\n", None),
    "b": ([("Stage A", [A1, A2, A3])], MOVES, None),
    "c": ([("Stage A", [A1, {**A2, "name": "renamed work"}, A3]), ("Stage B", [B1])], MOVES, False),
    "d": ([("Stage A", [A1, A2, A3]), ("Stage B", [B1])], "# Holds again\n\nStill holds.\n", True),
}


def put(w, name: str) -> None:
    """State `name`, written into the made-up folder, each file swapped whole."""
    stages, said, on = STATES[name]
    folder = os.path.join(w.work, "10")
    mission = os.path.join(folder, "missions", "A1-trial-work.md")
    stages = [{"name": s, "missions": [{**m, "file": mission} if m["id"] == "A1" else m for m in ms]}
              for s, ms in stages]
    registry.rewrite(os.path.join(folder, plans.PLAN), json.dumps({"stages": stages}, indent=1) + "\n")
    registry.rewrite(os.path.join(folder, "answers", "A1.md"), said)
    auto = os.path.join(folder, assistant.AUTO)
    if on is None:
        if os.path.exists(auto):
            os.remove(auto)
    else:
        registry.rewrite(auto, json.dumps({"on": on}) + "\n")


def set_up(w) -> None:
    """The made-up folder, ready for the page: A1's mission long enough to scroll."""
    w.put("10", "missions/A1-trial-work.md", "# A1 — trial work\n\n" + "".join(f"Line {i} of the mission.\n"
                                                                              for i in range(200)))
    w.put("10", "missions/A1-objectives.md", "# A1 · objectives\n\n- [ ] It holds.\n")
    put(w, "a")


class Presses(unittest.TestCase):
    """Each press on the made-up plan, its pane stood in for."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        set_up(self.w)
        self.typed = []
        for p in (patch.object(panes, "say", lambda pane, line, **more: self.typed.append((pane, line, more)) or True),
                  patch.object(page, "typable", lambda nn, ok: ("", self.w.held.get(nn, {}), f"pane-{nn}"))):
            p.start()
            self.addCleanup(p.stop)

    def press(self, **form):
        got = assistant.take("10", {k: [v] for k, v in form.items()})
        return got.outside() if isinstance(got, serve.Typing) else got

    def test_type_leaves_the_line_unsent_in_the_assistants_pane(self):
        self.assertEqual(self.press(act="type", id="A1"), "")
        self.assertEqual(self.typed, [("pane-10", "/assistant-answer A1 11-trial-work ", {"enter": False})])

    def test_send_sends_the_line_and_after_type_presses_return_alone(self):
        self.assertEqual(self.press(act="type", id="A1", send="yes"), "")
        self.assertEqual(self.press(act="type", id="A1", send="yes", only="return"), "")
        self.assertEqual(self.typed, [("pane-10", "/assistant-answer A1 11-trial-work", {"enter": True}),
                                      ("pane-10", "", {"enter": True})])

    def test_drive_and_send_this_stage_type_their_lines(self):
        self.assertEqual(self.press(act="drive", id="A1", send="yes"), "")
        self.assertEqual(self.press(act="stage", id="A", send="yes"), "")
        self.assertEqual([line for _, line, _ in self.typed], [drive.handed("10", "A1").rstrip(), "/1-assistant A"])

    def test_a_paste_types_into_the_pane_its_move_names(self):
        put(self.w, "b")
        key = assistant.sign("Hello, session 05.")
        self.assertEqual(self.press(act="paste", id="A1", key=key, send="yes"), "")
        self.assertEqual(self.typed, [("pane-05", "Hello, session 05.", {"enter": True})])

    def test_what_names_nothing_the_plan_holds_types_nothing(self):
        for form in ({"act": "type", "id": "Z9"}, {"act": "drive", "id": "Z9"}, {"act": "stage", "id": "Q"},
                     {"act": "paste", "id": "A1", "key": "no-such-key"}):
            self.assertRegex(self.press(**form), r"^Nothing to type for .*Reload the page\.$", form)
        self.assertEqual(self.typed, [])

    def test_an_unknown_act_is_refused(self):
        self.assertEqual(self.press(act="shout"), "This button does nothing here: shout. Nothing was typed.")
        self.assertEqual(self.press(), "This button does nothing here: no act. Nothing was typed.")

    def test_a_pane_that_cannot_take_typing_is_said(self):
        with patch.object(page, "typable", lambda nn, ok: (f"Session {nn} shows a dialog. Nothing was typed.", {}, "")):
            self.assertEqual(self.press(act="type", id="A1"), "Session 10 shows a dialog. Nothing was typed.")
        self.assertEqual(self.typed, [])

    def test_auto_send_keeps_its_switch(self):
        self.assertTrue(assistant.auto_on("10"))
        self.assertEqual(self.press(act="auto", id="off"), "")
        self.assertFalse(assistant.auto_on("10"))
        self.assertEqual(self.press(act="auto", id="on"), "")
        self.assertTrue(assistant.auto_on("10"))

    def test_the_contract_takes_a_press_once(self):
        table = live.Table([assistant.LIVE])
        form = {"act": ["auto"], "id": ["off"], "press": ["p-1"]}
        self.assertEqual(table.take(form, serve.address("assistant", "10")), "")
        os.remove(os.path.join(self.w.work, "10", assistant.AUTO))
        self.assertEqual(table.take(form, serve.address("assistant", "10")), "")
        self.assertTrue(assistant.auto_on("10"), "the same press, sent again, acted twice")


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        assistant.KEPT.clear()
        self.addCleanup(assistant.KEPT.clear)
        set_up(self.w)

    def test_it_draws_its_parts_opened_by_its_watch(self):
        got = assistant.drawn("10")
        parts = assistant.drawing("10", plans.plan("10"))
        for part in (parts["items"], parts["rail"], parts["head"]):
            self.assertIn(part, got)
        self.assertTrue(got.index('id="watch"') < got.index('id="items"'))
        self.assertIn(f'data-session="{self.w.held["10"]["session_id"]}"', got)
        self.assertIn(live.src("assistant.js"), got)
        self.assertNotIn("failed to draw", got)
        self.assertNotIn("typePost", got, "an inline press script was drawn")

    def test_it_draws_the_same_once_the_clock_moves(self):
        first = assistant.drawn("10")
        with trial.clock():
            trial.forget()
            self.assertEqual(assistant.drawn("10"), first)

    def test_a_gone_sessions_time_stands_still(self):
        held = registry.entries()
        self.assertFalse(os.path.exists(self.w.held["12"]["transcript"]))
        at = assistant.quiet(A3, held)
        self.assertEqual(at, int(__import__("time").mktime(__import__("time").strptime(A3["queued"], assistant.STAMP))))
        with trial.clock():
            self.assertEqual(assistant.quiet(A3, held), at)
            self.assertEqual(assistant.quiet({**A3, "queued": ""}, held), 0)

    def test_no_plan_says_so_with_the_same_scripts(self):
        os.remove(os.path.join(self.w.work, "10", plans.PLAN))
        got = assistant.drawn("10")
        self.assertIn("No plan yet", got)
        self.assertIn(live.src("assistant.js"), got)
        self.assertNotIn(assistant.UNREADABLE, got)

    def test_the_plan_cut_short_at_any_length_says_unreadable_and_keeps_every_row(self):
        path = os.path.join(self.w.work, "10", plans.PLAN)
        with open(path, "rb") as f:
            whole = f.read()
        assistant.drawn("10")
        for cut in range(len(whole)):
            registry.rewrite(path, whole[:cut].decode(errors="ignore"))
            got = assistant.drawn("10")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            # Cut only of its last line's end, the plan is still whole.
            if whole[:cut].strip() != whole.strip():
                self.assertIn(assistant.UNREADABLE + assistant.KEPT_ROWS, got, f"cut at {cut}")
            for k in ("A1", "A2", "A3"):
                self.assertIn(f'data-k="{k}"', got, f"cut at {cut}, row {k} lost")
        assistant.KEPT.clear()
        registry.rewrite(path, whole[:len(whole) // 2].decode(errors="ignore"))
        got = assistant.drawn("10")
        self.assertIn(assistant.UNREADABLE, got)
        self.assertNotIn(assistant.KEPT_ROWS, got)
        self.assertNotIn("failed to draw", got)

    def test_each_other_state_file_cut_short_at_any_length_still_draws(self):
        folder = os.path.join(self.w.work, "10")
        files = {os.path.join(folder, "answers", "A1.md"): MOVES,
                 drive.path("10"): json.dumps({"drive": "A", "state": "running", "words": ["A"]}) + "\n",
                 os.path.join(folder, assistant.AUTO): json.dumps({"on": False}) + "\n",
                 os.path.join(folder, "launch.json"): json.dumps({"rows": [{"uid": 1, "n": "07"}]}) + "\n",
                 os.path.join(folder, registry.RECORD): json.dumps(self.w.held["10"], indent=2) + "\n"}
        logged = io.StringIO()
        with contextlib.redirect_stderr(logged):
            for path, whole in files.items():
                name = os.path.basename(path)
                for cut in range(len(whole) + 1):
                    registry.rewrite(path, whole[:cut])
                    got = assistant.drawn("10")
                    self.assertNotIn("failed to draw", got, f"{name} cut at {cut}")
                    # The assistant's own JSON files, cut short, say so.
                    if name in assistant.OTHERS and whole[:cut].strip() != whole.strip():
                        self.assertIn(f"{name}, is unreadable now.", got, f"{name} cut at {cut}")
                registry.rewrite(path, whole)
            self.assertNotIn("unreadable now", assistant.drawn("10"))
        self.assertNotIn("Traceback", logged.getvalue())

    def test_its_files_name_every_file_it_reads(self):
        put(self.w, "b")
        # registry.entries() follows each session into the transcript it
        # continued in, as every page's draw does: those reads are its own.
        seen, real_open, real_stat = [], builtins.open, os.stat

        def watching(fn):
            seen.clear()
            with patch.object(builtins, "open", lambda f, *a, **k: seen.append(str(f)) or real_open(f, *a, **k)), \
                    patch.object(os, "stat", lambda f, *a, **k: seen.append(str(f)) or real_stat(f, *a, **k)):
                fn()
            return {os.path.realpath(f) for f in seen if os.path.realpath(f).startswith(os.path.realpath(self.w.root))}

        shared = watching(registry.entries)
        read = watching(lambda: assistant.drawn("10")) - shared
        named = {os.path.realpath(f) for f in assistant.files("10")}
        missed = sorted(os.path.relpath(f, self.w.root) for f in read if f not in named and os.path.dirname(f) not in named)
        self.assertEqual(missed, [])
        for part in (os.path.join("10", plans.PLAN), os.path.join("10", "answers", "A1.md"),
                     os.path.join("10", "missions", "A1-objectives.md"), os.path.join("10", drive.FILE)):
            self.assertIn(os.path.realpath(os.path.join(self.w.work, part)), named, part)
        # The session a move names: its transcript tells whether it heard the words.
        self.assertIn(os.path.realpath(self.w.held["05"]["transcript"]), named)

    def test_states_prints_each_missions_need(self):
        out = io.StringIO()
        with patch.object(sys, "argv", ["assistant-page.py", "states", "10"]), contextlib.redirect_stdout(out):
            assistant.main()
        lines = out.getvalue().splitlines()
        self.assertEqual([line.split(" · ")[0] for line in lines], ["A1", "A2", "A3"])
        self.assertEqual(lines[1], "A2 · not started · later work")


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + process.env.ASSISTANT_PAGE;
const state = name => post('/trial/state', {name});
const read = async what => (await fetch(base + '/trial/' + what)).text();
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
// The engine now running.
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy', 'data-typed'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('nav.nums')), walk(document.querySelector('main'))]);
});
const settled = async (p, rows) => {
  await p.waitForFunction(n => document.querySelectorAll('nav.nums .tab:not(.stg)').length === n
    && !('busy' in document.getElementById('watch').dataset), rows, {timeout: 6000});
  await wait(400);
};
const view = (p, k) => p.evaluate(k => tab(k), k);

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
    for (const [name, rows] of [['b', 3], ['c', 4], ['d', 4], ['a', 3], ['c', 4]]) {
      await state(name);
      await settled(b, rows);
      await c.goto(url);
      await settled(c, rows);
      for (const p of [b, c]) { await view(p, 'all'); await wait(200); }
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // The view, a fold and the scroll I left stay while the page changes.
    await state('a');
    const k = await open();
    await k.goto(url);
    await settled(k, 3);
    await k.click('nav.nums .tab[data-k="A1"]');
    await k.click('#m-A1');
    await k.evaluate(() => { document.querySelector('main').scrollTop = 600; });
    const top = await k.evaluate(() => document.querySelector('main').scrollTop);
    for (const name of ['d', 'a', 'd']) { await state(name); await settled(k, name === 'd' ? 4 : 3); }
    const kept = await k.evaluate(() => ({view: location.hash, on: document.querySelector('#t-A1').classList.contains('on'),
      fold: document.getElementById('m-A1').getAttribute('aria-expanded'), top: document.querySelector('main').scrollTop,
      moved: document.querySelector('#t-A1 .ans').textContent}));
    // Words newly waiting for my send open their stage, once.
    await state('b');
    await k.waitForFunction(() => location.hash === '#A', null, {timeout: 6000}).catch(() => {});
    const due = await k.evaluate(() => location.hash + ' ' + document.querySelector('#t-A').classList.contains('on'));
    said('place', kept.view === '#A1' && kept.on && kept.fold === 'true' && kept.top === top && top > 0
         && kept.moved.includes('Still holds.') && due === '#A true' && k.loads === 1,
         `view ${kept.view}, shown: ${kept.on}; the mission's fold open: ${kept.fold}; scrolled ${kept.top} of ${top}; `
         + `its answer moved in: ${kept.moved.includes('Still holds.')}; words waiting for my send opened ${due}; ${k.loads} load`);
    await view(k, 'A1');

    // Type types, Send after it presses Return alone, and Auto-send keeps its switch.
    const before = (await read('said')).split('\n').filter(Boolean).length;
    await k.click('#t-A1 .acts3 .btn:nth-child(1)');
    await k.waitForFunction(() => document.querySelector('#t-A1 .acts3 .btn').textContent === 'Typed', null, {timeout: 4000});
    await k.click('#t-A1 .acts3 .btn:nth-child(2)');
    for (let i = 0; i < 40 && (await read('said')).split('\n').filter(Boolean).length < before + 2; i++) await wait(100);
    const lines = (await read('said')).split('\n').filter(Boolean).slice(before);
    await view(k, 'all');
    await k.click('#auto button[data-v="off"]');
    for (let i = 0; i < 40 && !(await read('auto')).includes('false'); i++) await wait(100);
    const auto = await read('auto');
    await k.waitForFunction(() => !('busy' in document.getElementById('watch').dataset), null, {timeout: 4000});
    await wait(1500);
    const pill = await k.evaluate(() => document.querySelector('#auto button.on').dataset.v);
    said('presses', lines.length === 2 && lines[0] === 'type /assistant-answer A1 11-trial-work ' && lines[1] === 'send ' && auto.includes('false')
         && pill === 'off' && k.loads === 1,
         `typed: ${JSON.stringify(lines)}; Auto-send's file: ${auto.trim()}, its pill: ${pill}; ${k.loads} load`);
    await k.close();
    await state('a');

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "place": "My view, fold and scroll", "presses": "Type, Send and Auto-send"}


def serving(tmp: str) -> None:
    """The made-up plan, drawn, with the test's own presses."""
    typed = []
    with trial.world() as w, \
            patch.object(panes, "say", lambda pane, line, enter=True, **more:
                         typed.append(("send " if enter else "type ") + line) or True), \
            patch.object(page, "typable", lambda nn, ok: ("", w.held.get(nn, {}), f"pane-{nn}")):
        set_up(w)
        table = live.Table([assistant.LIVE])

        def old_route(at: str):
            bare = at.partition("?")[0]
            if bare == "/trial/said":
                return "\n".join(typed).encode(), "text/plain; charset=utf-8"
            if bare == "/trial/auto":
                try:
                    with open(os.path.join(w.work, "10", assistant.AUTO), "rb") as f:
                        return f.read(), "text/plain; charset=utf-8"
                except OSError:
                    return b"none", "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                put(w, form["name"][0])
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
        # A server already there, as this session's copy of 1100, would be
        # drawn and pressed in the made-up server's place.
        if serve.ports.answering(PORT):
            raise RuntimeError(f"Port {PORT} already answers. Stop session {NN}'s copy of 1100 there first.")
        tmp = tempfile.mkdtemp(prefix="assistant-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "ASSISTANT_PAGE": serve.address("assistant", "10")})
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

    def test_my_view_fold_and_scroll_stay_while_the_page_changes(self):
        self.held("place")

    def test_type_send_and_auto_send(self):
        self.held("presses")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
