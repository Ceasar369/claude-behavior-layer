#!/usr/bin/env python3
"""Check the transcript page: its presses, what it draws on the contract, and its page in WebKit and Chromium.

Presses: a hand-off's Copy file and Send's receiver, a dialog's Send, and
a press it cannot take.

Drawn: on lib/trial.py's made-up folder, 1100 draws every kind of turn,
hands the page's script its data alone, names the files that move it, and
draws each state file it reads cut short at any length, no turn lost.

Browser: a server on this session's port, 11NN, draws the made-up
transcript on the contract, as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My typing holds while the page changes, in one load.
  My unsent words come back after 1100 dies mid-word, show under no other
  session on the same number, and are gone once sent.

  transcript-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 12 when none is given. advisor-page-test.py
serves its own page through this file's server.
"""

import html
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
spec = importlib.util.spec_from_file_location("transcript_page_test", os.path.join(HERE, "transcript-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import follow  # noqa: E402
import live  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "12")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"transcript-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

SAID = ("Action: stop this session. Type `/9-session-stop` in session 05.\n\n"
        "Send to session 05.\n\n▼▼▼ START COPY ▼▼▼\n\nHello\n\n▲▲▲ END COPY ▲▲▲\n\n"
        "Then type `/9-session-stop` in session 12.")


def sends(html: str) -> list:
    return re.findall(r"(Send(?: to \d\d)?)</button>", html)


class CopyFileTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        p = patch.object(tool.registry, "ROOT", self.root.name)
        p.start()
        self.addCleanup(p.stop)
        os.makedirs(os.path.join(self.root.name, "code"))
        for name in ("code/.env", "code/.env.example", "code/notes.md"):
            with open(os.path.join(self.root.name, name), "w") as f:
                f.write("words")

    def test_a_env_file_is_refused(self):
        for name in ("code/.env", "code/.env.example"):
            self.assertIsNone(tool.filed(name))
            self.assertNotIn("Copy file", tool.handoff("file", "", name))

    def test_a_link_to_a_env_file_is_refused(self):
        os.symlink(os.path.join(self.root.name, "code/.env"), os.path.join(self.root.name, "code/plain.txt"))
        self.assertIsNone(tool.filed("code/plain.txt"))

    def test_a_plain_file_still_copies(self):
        self.assertEqual(tool.filed("code/notes.md"), "words")
        self.assertIn("Copy file", tool.handoff("file", "", "code/notes.md"))


class SendTest(unittest.TestCase):
    def test_its_own_page_reads_send(self):
        self.assertEqual(sends(tool.reply(SAID, "05")), ["Send", "Send", "Send to 12"])
        self.assertEqual(sends("".join(tool.stretch([{"k": "text", "t": SAID}], "05"))),
                         ["Send", "Send", "Send to 12"])

    def test_another_page_names_the_receiver(self):
        self.assertEqual(sends(tool.reply(SAID, "12")), ["Send to 05", "Send to 05", "Send"])

    def test_its_copy_takes_the_reply_whole(self):
        got = re.match(r'<div class="reply"><div class="whole"><div class="txt" hidden>(.*?)</div>'
                       r'<button class="btn cp">', tool.reply(SAID, "05"), re.S)
        self.assertEqual(html.unescape(got.group(1)), SAID)

    def test_the_key_never_changes_with_the_page(self):
        keys = lambda own: re.findall(r'data-hand="(\w+)"', tool.reply(SAID, own))
        self.assertEqual(keys("05"), keys("12"))


class DialogTest(unittest.TestCase):
    """Send while a dialog waits: the page types into it, plain=yes is refused."""

    def send(self, **extra):
        form = {"act": ["send"], "text": ["Go on"], **{k: [v] for k, v in extra.items()}}
        with patch.object(tool, "status", return_value="waiting"), \
                patch.object(tool.page, "typable", return_value=("", {}, "pane-5")) as typable, \
                patch.object(tool.serve, "Typing", side_effect=lambda f: f) as typing, \
                patch.object(tool, "amend", return_value="") as amend:
            said = tool.take("05", form)
            if callable(said):
                said = said()
        return said, typable.called, typing.called, amend.called

    def test_plain_is_refused_and_types_nothing(self):
        self.assertEqual(self.send(plain="yes"),
                         ("Session 05 has a question open; answer it first.", False, False, False))

    def test_the_page_still_types_into_the_dialog(self):
        self.assertEqual(self.send(), ("", True, True, True))


class RefusedTest(unittest.TestCase):
    def press(self, form):
        with patch.object(tool.page, "typable") as typable:
            said = tool.take("05", {k: [v] for k, v in form.items()})
        self.assertFalse(typable.called)
        return said

    def test_an_empty_send_is_refused(self):
        self.assertEqual(self.press({"act": "send", "text": "  "}),
                         "There were no words or files to send. Nothing was typed.")

    def test_an_unknown_act_is_refused(self):
        self.assertEqual(self.press({"act": "shout"}), "This page takes no shout press. Nothing was typed.")


# ---- the made-up states, one name each ------------------------------------------

# The second session on 05's number, after the first stopped.
OTHER = "00000000-0000-4000-8000-000000000095"
# How many lines of trial.spoken() state "a" keeps: its first turns only.
EARLY = 12


def lines(sid: str, title: str, working: bool = False, cut: int = 0) -> str:
    said = trial.spoken(sid, title, working)
    return "".join(json.dumps(x) + "\n" for x in (said[:cut] if cut else said))


def stand(w, name: str) -> None:
    """Session 05, and the advisor 01, as state `name` holds them.

    a: its first turns; b: its whole transcript; c: working again, a line
    of mine unanswered; d: whole, with its status line; n: another session
    on its number, newly started. Then the advisor's own: f, 01 follows 05;
    g, 01 also drives 11; l, 01's list names 05 alone."""
    if name == "n":
        rec = w.session("05", "trial")
        heard = os.path.join(os.path.dirname(rec["transcript"]), OTHER + ".jsonl")
        registry.rewrite(heard, lines(OTHER, "05-fresh", cut=2))
        w.held["05"] = {**rec, "session_id": OTHER, "title": "05-fresh", "transcript": heard}
        registry.rewrite(os.path.join(w.work, "05", registry.RECORD), json.dumps(w.held["05"], indent=2) + "\n")
        with open(os.path.join(w.account, "sessions", "40005.json")) as f:
            d = json.load(f)
        registry.rewrite(os.path.join(w.account, "sessions", "40005.json"),
                         json.dumps({**d, "sessionId": OTHER, "name": "05-fresh"}))
        return
    if name in "abcd":
        rec = w.session("05", "trial", "busy" if name == "c" else "idle")
        registry.rewrite(rec["transcript"], lines(rec["session_id"], rec["title"], name == "c",
                                                  EARLY if name == "a" else 0))
        status = os.path.join(w.work, "05", registry.STATUSLINE)
        if name == "d":
            registry.rewrite(status, "Opus 5.5 · 40% context\nwork · 3 files changed\n")
        elif os.path.exists(status):
            os.remove(status)
        return
    if name == "f":
        follow.take("01", "05", "its report", "it stops")
    elif name == "g":
        successor.take("01", ["11"], "the port")
    elif name == "l":
        tool.advisor.keep_list("01", ["05"])
    elif name == "0":
        for p in (follow.path("01"), successor.path("01"), os.path.join(w.work, "01", tool.advisor.LIST)):
            if os.path.exists(p):
                os.remove(p)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        tool.ENDED.clear()
        self.addCleanup(tool.ENDED.clear)

    def test_every_kind_of_turn_draws(self):
        got = tool.drawn("05")
        for part in ('id="watch"', f'data-session="{self.w.held["05"]["session_id"]}"', live.src("live.js"),
                     live.src("transcript.js"), live.src("advisor.js"), 'class="turn you mine"', 'class="turn ses"',
                     "Ran /clarify-items", '<span class="what">Command</span>', '<span class="what">Agent</span>',
                     'class="wake"', 'class="reply"', '<div class="move">', '<textarea id="words"',
                     'id="tx" data-state="idle" data-claude="idle"', '<script type="application/json" id="tdata">'):
            self.assertIn(part, got, part)
        self.assertNotIn("failed to draw", got)
        self.assertNotIn('id="adv"', got)
        self.assertEqual(self.w.started, [])

    def test_its_data_goes_as_data(self):
        data = json.loads(re.search(r'<script type="application/json" id="tdata">(.*?)</script>',
                                    tool.drawn("05"), re.S).group(1))
        self.assertEqual(data["base"], "/p/transcript/05")
        self.assertIn(["context", "Visualize current context usage as a colored grid."], data["skills"])
        self.assertEqual(sorted(data["icons"]), ["file", "x"])

    def test_the_advisor_wears_its_panel(self):
        self.w.session("01", "advisor")
        got = tool.drawn("01")
        self.assertIn('id="adv"', got)
        self.assertEqual(re.findall(r'class="row" data-nn="(\d\d)"', got), ["05", "10", "11"])
        self.assertNotIn("advRows", got)

    def test_its_files_name_what_moves_it(self):
        named = tool.files("05")
        own = os.path.join(self.w.work, "05")
        for f in (self.w.held["05"]["transcript"], os.path.join(own, registry.RECORD),
                  os.path.join(own, registry.STATUSLINE), os.path.join(self.w.work, "10", "stages.json"),
                  os.path.join(self.w.account, "sessions"), tool.skills_page.SKILLS):
            self.assertIn(os.path.realpath(f) if "account" in f else f, named, f)

    def test_a_transcript_still_to_come_is_named_by_its_folder(self):
        os.remove(self.w.held["05"]["transcript"])
        self.assertIn(os.path.dirname(self.w.held["05"]["transcript"]), tool.files("05"))

    def test_the_advisors_files_name_its_list_follows_and_drives(self):
        self.w.session("01", "advisor")
        named = tool.files("01")
        for f in (os.path.join(self.w.work, "01", tool.advisor.LIST), follow.path("01"), successor.path("01")):
            self.assertIn(f, named)

    def quick(self) -> None:
        """Every skill's head, read once: a cut test draws thousands of times."""
        p = patch.object(tool.skills_page, "heads", return_value=tool.skills_page.heads())
        p.start()
        self.addCleanup(p.stop)

    def test_a_transcript_cut_short_at_any_length_loses_no_turn(self):
        self.quick()
        path = self.w.held["05"]["transcript"]
        with open(path) as f:
            whole = f.read()
        drawn = tool.drawn("05").count('<section class="turn')
        seen = 0
        for cut in range(len(whole) + 1):
            with open(path, "w") as f:
                f.write(whole[:cut])
            got = tool.drawn("05")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            turns = got.count('<section class="turn')
            self.assertGreaterEqual(turns, seen, f"a turn was lost at {cut}")
            seen = turns
        self.assertEqual(seen, drawn)

    def test_every_other_file_it_reads_cut_short_at_any_length_still_draws(self):
        self.quick()
        self.w.session("01", "advisor")
        stand(self.w, "d")
        for n in ("f", "g", "l"):
            stand(self.w, n)
        own = os.path.join(self.w.work, "01")
        # The advisor's tab reads every one of them, bar 05's status line.
        for nn, path in (("05", os.path.join(self.w.work, "05", registry.STATUSLINE)),
                         ("01", os.path.join(own, registry.RECORD)), ("01", os.path.join(self.w.work, "05", registry.RECORD)),
                         ("01", os.path.join(self.w.work, "10", "stages.json")),
                         ("01", os.path.join(self.w.account, "sessions", "40001.json")), ("01", follow.path("01")),
                         ("01", successor.path("01")), ("01", os.path.join(own, tool.advisor.LIST))):
            with open(path) as f:
                whole = f.read()
            for cut in range(len(whole) + 1):
                with open(path, "w") as f:
                    f.write(whole[:cut])
                registry.PUBLISHED[:] = [0.0, None]
                self.assertNotIn("failed to draw", tool.drawn(nn), f"{path} cut at {cut}")
            with open(path, "w") as f:
                f.write(whole)


# ---- the page in both engines ----------------------------------------------------

# A page as it stands, node by node: what a fresh draw and a changed one must agree on.
SNAP = r"""
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy', 'data-got'].includes(a.name))
         .map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify(walk(document.getElementById('tx')));
});
const state = name => post('/trial/state', {name});
const typedLine = async () => (await fetch(base + '/trial/said')).text();
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// The page stands: 1100's last picture in place, nothing fetched.
const settled = async (p, check) => {
  await p.waitForFunction(c => !!document.getElementById('tx') && !('busy' in (document.getElementById('watch') || {dataset: {}}).dataset)
    && (!c || document.querySelector(c)), check || '', {timeout: 8000});
  await wait(500);
};
const opener = context => async () => {
  const p = await context.newPage();
  p.loads = 0;
  p.on('request', r => { if (r.isNavigationRequest() && r.frame() === p.mainFrame()) p.loads++; });
  return p;
};
"""

BROWSERS = trial.SERVER + SNAP + r"""
const url = base + '/p/transcript/05';

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1000, height: 760}});
    const open = opener(context);

    // A changed page, put in place, equals the page drawn fresh, state by state.
    await state('a');
    const b = await open(), c = await open();
    await b.goto(url);
    await settled(b);
    let same = [];
    for (const name of ['b', 'c', 'd', 'a', 'n', 'b']) {
      await state(name);
      await b.waitForFunction(() => !('busy' in document.getElementById('watch').dataset), null, {timeout: 8000});
      await wait(1800);
      await settled(b);
      await c.goto(url);
      await settled(c);
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My typing holds while the page changes: the words, the cursor, and a
    // call I unfolded, in one load.
    await state('a');
    const t = await open();
    await t.goto(url);
    await settled(t);
    await t.click('button.row');
    await t.click('#words');
    await t.keyboard.type('Half a thou');
    await state('c');
    await t.waitForSelector('#tx[data-claude="busy"]', {timeout: 8000});
    await t.keyboard.type('ght.');
    await state('d');
    await t.waitForFunction(() => document.querySelector('#meter div'), null, {timeout: 8000});
    await settled(t);
    const held = await t.evaluate(() => ({words: document.getElementById('words').value, at: document.activeElement.id,
      open: document.querySelectorAll('button.row[aria-expanded="true"]').length}));
    said('typing', held.words === 'Half a thought.' && held.at === 'words' && held.open === 1 && t.loads === 1,
         `the box read "${held.words}", the cursor in #${held.at}, ${held.open} call unfolded, through two changes; ${t.loads} load`);
    await t.close();

    // My unsent words, on a device of their own: back after 1100 dies
    // mid-word, shown under no other session on the same number, back
    // under their own, and gone once sent.
    const own = await browser.newContext({viewport: {width: 1000, height: 760}});
    await state('b');
    const d = await opener(own)();
    await d.goto(url);
    await settled(d);
    await d.click('#words');
    await d.keyboard.type('Keep these words');
    await die(1);
    await up();
    await d.reload();
    await settled(d);
    const back = await d.evaluate(() => document.getElementById('words').value);
    await state('n');
    await d.waitForFunction(() => document.getElementById('tx').dataset.t.startsWith('00000000-0000-4000-8000-000000000095'), null, {timeout: 8000});
    await settled(d);
    const other = await d.evaluate(() => document.getElementById('words').value);
    await state('b');
    await d.waitForFunction(() => !document.getElementById('tx').dataset.t.startsWith('00000000-0000-4000-8000-000000000095'), null, {timeout: 8000});
    await d.reload();
    await settled(d);
    const again = await d.evaluate(() => document.getElementById('words').value);
    await d.focus('#words');
    await d.keyboard.press('Enter');
    await d.waitForFunction(() => document.getElementById('words').value === '', null, {timeout: 8000}).catch(() => {});
    await wait(300);
    const line = await typedLine();
    const left = await d.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith('draft:') && k.endsWith(':words')).length);
    await d.reload();
    await settled(d);
    const after = await d.evaluate(() => document.getElementById('words').value);
    said('drafts', back === 'Keep these words' && other === '' && again === 'Keep these words' && line === 'Keep these words'
         && left === 0 && after === '',
         `after 1100 died: "${back}"; another session on 05: "${other}"; the first one again: "${again}"; `
         + `Return typed "${line}", ${left} draft left, and a reload shows "${after}"`);
    await own.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "My typing holds while it changes", "drafts": "My unsent words",
         "panel": "The panel"}


def serving(tmp: str) -> None:
    """The made-up folder on the contract, its parts, and the test's own
    presses. An advisor, 01, sits beside session 05. Each line typed into a
    pane is kept for /trial/said."""
    typed = []
    with trial.world() as w, patch.object(panes, "say", lambda pane, line, **more: typed.append(line) or True):
        tool.ENDED.clear()
        w.session("01", "advisor")
        table = live.Table([tool.LIVE])
        sub = re.compile(serve.address("transcript", r"(\d{2})") + r"(/[\w/-]+)")

        def old_route(at: str):
            bare, _, query = at.partition("?")
            if m := sub.fullmatch(bare):
                got = tool.answer(m.group(1), m.group(2), query)
                if got is not None:
                    return got
            if bare == "/trial/said":
                return (typed[-1] if typed else "").encode(), "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                stand(w, form["name"][0])
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1, **table.riding(route=old_route, take=old_take))


def run_browsers(script: str, here: str, names: dict) -> tuple:
    """`script` in both engines against this file's server, as a program of
    its own: each check seen, how the run ended, any engine missing, and the
    server's log."""
    tmp = tempfile.mkdtemp(prefix="transcript-page-test-")
    try:
        with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
            r = trial.browsers(script, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}"})
        with open(os.path.join(tmp, "server.log"), errors="replace") as f:
            logged = f.read()
    finally:
        shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
    for s in seen:
        print(("" if s["held"] else "FAILED: ") + f"{names[s['name']]}, in {s['engine']}: {s['seen']}.", flush=True)
    missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
    return seen, r.stderr.strip()[-1500:] if r.returncode else "", missing, logged


class Engines(unittest.TestCase):
    """A page in each engine: one run, then each check read."""
    SCRIPT = BROWSERS

    @classmethod
    def setUpClass(cls):
        cls.seen, cls.ended, cls.missing, cls.logged = run_browsers(cls.SCRIPT, HERE, NAMES)

    def held(self, name: str) -> None:
        self.assertEqual(self.missing, [], "an engine's build is not installed")
        mine = [s for s in self.seen if s["name"] == name]
        self.assertEqual(sorted(s["engine"] for s in mine), ["chromium", "webkit"],
                         f"the browsers ended early. {self.ended} {self.logged[-800:] if 'Traceback' in self.logged else ''}")
        for s in mine:
            self.assertTrue(s["held"], f"{NAMES[name]}, in {s['engine']}: {s['seen']}")


class Browser(Engines):
    def test_a_changed_page_put_in_place_equals_the_page_drawn_fresh(self):
        self.held("fresh")

    def test_my_typing_holds_while_the_page_changes(self):
        self.held("typing")

    def test_my_unsent_words_wait_on_my_device(self):
        self.held("drafts")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
