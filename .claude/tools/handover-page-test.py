#!/usr/bin/env python3
"""Check the handover page: its presses, what it draws on the contract, its press as its own program, and its page in WebKit and Chromium.

Presses: a press under way is refused and starts nothing; on the
contract, a post naming no act hands nothing over.

Drawn: on lib/trial.py's made-up folder, the page on the contract opens
with its watch, names the files that move it, and draws its state files
cut short at any length.

Own program: a server on this session's port, 11NN, serves the made-up
seat. An empty post is refused with 409. Hand over, pressed, starts its
press through handover-page.py's own spawn(): the real `handover-page.py
press` program, standing on the made-up folder, with only its typing
stood in. The server is then killed, and the handover finishes without
it, each line typed once.

Browser: the same server draws the made-up seat. Each engine checks, in
order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  A pill I pick holds while the page changes, and Hand over names its act.

  handover-page-test.py [NN] [Presses|Drawn|OwnProgram|Browser]

NN is this session's number, 14 when none is given.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("handover_page_test", os.path.join(HERE, "handover-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import accounts  # noqa: E402
import context  # noqa: E402
import handover  # noqa: E402
import live  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "14")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"handover-page-test-{NN}"
# The one program a made-up press reads as still running.
RUNNING = 4242
# Popen as it stands before a made-up folder refuses it.
POPEN = subprocess.Popen


def note(step: str, **more) -> str:
    return json.dumps({"step": step, "pid": RUNNING, **more}) + "\n"


# Each state the browser asks for by name: seat 05's press file, and the threshold.
STATES = {
    "hot": (None, 70),
    "tick": (None, 60),
    "saving": (note("saving", since=0), 70),
    "launching": (note("launching", since=0, copy="handovers/1.md",
                       typed="/handover-resume 05 account 1 model opus"), 70),
    "done": (note("done", since=0, copy="handovers/1.md", typed="/handover-resume 05 account 1"), 70),
    "failed": (json.dumps({"step": "failed", "said": "Saved as handovers/1.md. Then <b>it</b> stopped."}), 70),
    "cool": (None, 90),
}


def stand(w, name: str) -> None:
    """Seat 05 in state NAME: its press file, and the threshold."""
    press, limit = STATES[name]
    path = handover.path("05")
    if press is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        registry.write_whole(path, press)
    registry.write_whole(context.FILE, json.dumps({"threshold": limit}) + "\n")


class Presses(unittest.TestCase):
    def press(self, step: str, form: dict, take=None):
        with patch.object(tool.handover, "progress", return_value={"step": step}), \
                patch.object(tool.page, "typable", return_value=("Session 05 has no pane.", {}, "")) as typable, \
                patch.object(tool, "spawn") as spawn:
            said = (take or tool.take)("05", form)
        return said, typable.called, spawn.called

    def test_a_press_under_way_is_refused(self):
        for step in tool.PRESSED:
            self.assertEqual(self.press(step, {}),
                             ("A handover of session 05 is already under way. Nothing was typed.", False, False))

    def test_a_first_press_goes_on_to_the_pane_check(self):
        self.assertEqual(self.press("", {}), ("Session 05 has no pane.", True, False))

    def test_a_post_naming_no_act_hands_nothing_over(self):
        for form in ({}, {"account": ["1"]}, {"act": ["launch"]}):
            self.assertEqual(self.press("", form, tool.pressed),
                             ("This page takes no such press. Nothing was typed.", False, False), form)

    def test_a_press_naming_its_act_goes_on(self):
        self.assertEqual(self.press("", {"act": ["handover"]}, tool.pressed), ("Session 05 has no pane.", True, False))

    def test_a_press_that_raises_says_so(self):
        work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, work, True)
        with patch.object(registry, "WORK", work), \
                patch.object(handover, "press", side_effect=RuntimeError("no iTerm")):
            tool.pressing("05", "P", 0, {"account": "", "model": "", "effort": ""})
            got = handover.progress("05")
        self.assertEqual(got["step"], "failed")
        self.assertIn("RuntimeError: no iTerm", got["said"])


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def test_the_page_opens_with_its_watch_and_its_own_script(self):
        got = tool.drawn("05")
        for part in ('id="watch"', live.src("handover.js"), '<script type="application/json" id="picks">',
                     'id="go"', 'class="pills" data-k="model"'):
            self.assertIn(part, got, part)
        self.assertNotIn("onclick=", got)
        self.assertNotIn("typePost", got)

    def test_every_state_draws_with_the_same_scripts(self):
        code = lambda page: re.findall(r"<script(?! type=\"application/json\")[^>]*>", page)
        first = code(tool.drawn("05"))
        with patch.object(ports, "alive", lambda pid: pid == RUNNING):
            for name in STATES:
                stand(self.w, name)
                got = tool.drawn("05")
                self.assertNotIn("failed to draw", got, name)
                self.assertEqual(code(got), first, name)

    def test_its_files_name_its_press_its_transcript_and_the_threshold(self):
        named = tool.files("05")
        for f in (handover.path("05"), self.w.held["05"]["transcript"], context.FILE, os.path.dirname(context.FILE),
                  accounts.FILE, os.path.join(registry.folder("05"), handover.RESUME)):
            self.assertIn(f, named, f)

    def test_its_state_files_cut_short_at_any_length_still_draw(self):
        whole = {handover.path("05"): STATES["launching"][0], context.FILE: '{"threshold": 70}\n',
                 os.path.join(registry.folder("05"), handover.RESUME): '{"account": "2", "model": "opus"}\n',
                 os.path.join(registry.folder("05"), "named.json"): '{"model": "opus", "effort": "high"}'}
        for path, text in whole.items():
            for cut in range(len(text) + 1):
                registry.write_whole(path, text[:cut])
                got = tool.drawn("05")
                self.assertNotIn("failed to draw", got, f"{os.path.basename(path)} cut at {cut}")
            registry.write_whole(path, text)

    def test_a_press_whose_program_ended_reads_failed_by_its_look(self):
        stand(self.w, "saving")
        with patch.object(ports, "alive", lambda pid: pid == RUNNING):
            self.assertEqual(tool.alive(), ("05",))
            self.assertIn("Saving…", tool.drawn("05"))
        self.assertEqual(tool.alive(), ())
        self.assertIn("cut short", tool.drawn("05"))


# ---- the made-up seat, served ------------------------------------------------------

def hooks(root: str, transcript: str, record: str):
    """panes.say, for a child press: each line typed is kept, and each hook
    answers as its own would, the successor taking the seat."""
    def say(pane, line, **more) -> bool:
        with open(os.path.join(root, "typed.txt"), "a") as f:
            f.write(line + "\n")
        time.sleep(0.5)
        word = (f"Saved successfully into handovers/1.md." if line == handover.PREPARE
                else "Launched successfully.")
        with open(transcript, "a") as f:
            f.write(json.dumps({"type": "system", "content": f"{handover.BLOCKED} {word}"}) + "\n")
        if line.startswith("/handover-resume"):
            with open(record) as f:
                held = json.load(f)
            registry.write_whole(record, json.dumps({**held, "session_id": "successor"}))
        return True
    return say


# Set to the test's folder, the press program the server starts stands on
# the made-up folder that folder's root.txt names.
TRIAL = "HANDOVER_PAGE_TEST_FOLDER"
# Written into the test's folder, never the tree, and put on PYTHONPATH:
# Python runs it before every program it starts. It acts only in
# `handover-page.py press` with TRIAL set, and a stand-in that fails ends
# that program before it types anything.
SITE = """import os, sys
if os.environ.get({trial!r}) and os.path.basename(sys.argv[0]) == "handover-page.py" and sys.argv[1:2] == ["press"]:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("handover_page_trial", {test!r})
        test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test)
        test.stand_in(os.environ[{trial!r}], sys.argv[2])
    except BaseException as e:
        sys.exit(f"The press could not stand on the made-up folder: {{e!r}}")
"""


def stand_in(tmp: str, nn: str) -> None:
    """The press program, handover-page.py's own, standing on the made-up
    folder the server that started it left behind as it died: its seat's
    files there, and each line it types kept and answered as each hook
    would. It notes itself in TMP/programs.txt: its argv, and whether it
    runs in a session of its own."""
    with open(os.path.join(tmp, "root.txt")) as f:
        root = f.read()
    work = os.path.join(root, "sessions")
    record = os.path.join(work, nn, registry.RECORD)
    with open(record) as f:
        held = json.load(f)
    with open(os.path.join(tmp, "programs.txt"), "a") as f:
        f.write(json.dumps({"argv": sys.argv, "own": os.getsid(0) == os.getpid()}) + "\n")
    for stood in (patch.object(registry, "WORK", work), patch.object(registry, "LIVE", [os.path.join(root, "account")]),
                  patch.object(ports, "started", lambda pids, *more, **named: {int(p): "" for p in pids}),
                  patch.object(accounts, "take", lambda: accounts.FALLBACK),
                  patch.object(panes, "say", hooks(root, held["transcript"], record))):
        stood.start()


def serving(tmp: str, running: bool) -> None:
    """The made-up seat, drawn, with the test's own presses. When
    `running`, a press goes through the page's own spawn(), and the one
    program the made-up folder lets it start is the press. When not, a
    press is only kept."""
    with trial.world() as w:
        with open(os.path.join(tmp, "root.txt"), "w") as f:
            f.write(w.root)
        table = live.Table([tool.LIVE])
        spawned = os.path.join(tmp, "spawned.txt")
        refused = subprocess.Popen

        def popen(argv, *given, **named):
            if list(argv[:len(tool.PRESS)]) == tool.PRESS:
                return POPEN(argv, *given, **named)
            return refused(argv, *given, **named)

        def spawn(argv: list) -> None:
            with open(spawned, "w") as f:
                f.write(json.dumps(argv[len(tool.PRESS):]))

        def old_route(at: str):
            bare = at.partition("?")[0]
            if bare == "/trial/spawned":
                return (open(spawned).read() if os.path.exists(spawned) else "").encode(), "text/plain; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                stand(w, form["name"][0])
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return "Nothing at this address takes a press."

        # A made-up press runs while its pid is RUNNING's, or, pressed for real, while its program does.
        alive = lambda pid: pid == RUNNING or (running and alive_pid(pid))
        with patch.object(subprocess, "Popen", popen) if running else patch.object(tool, "spawn", spawn), \
                patch.object(ports, "alive", alive):
            serve.run(SKILL, PORT, lambda: "home", recheck=1,
                      **table.riding(route=old_route, take=old_take, hears=lambda: []))


def alive_pid(pid) -> bool:
    """Whether a real process runs, as ports.alive reads it outside a made-up folder."""
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def post(path: str, form: dict):
    """One press at the test's server: its code and its words."""
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=urllib.parse.urlencode(form).encode())
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        with e:
            return e.code, e.read().decode()
    except OSError as e:
        return 0, str(e)


class OwnProgram(unittest.TestCase):
    """Hand over, pressed, runs on once its server is killed."""

    def test_the_handover_finishes_once_the_server_is_killed(self):
        tmp = tempfile.mkdtemp(prefix="handover-page-test-")
        root = ""
        site = os.path.join(tmp, "site")
        os.makedirs(site)
        # usercustomize, since Homebrew's Python finds its own packages through its sitecustomize.
        with open(os.path.join(site, "usercustomize.py"), "w") as f:
            f.write(SITE.format(trial=TRIAL, test=os.path.abspath(__file__)))
        searched = os.pathsep.join(p for p in (site, os.environ.get("PYTHONPATH", "")) if p)
        try:
            with patch.dict(os.environ, {"PYTHONPATH": searched, TRIAL: tmp}), \
                    trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp, "running"], PORT, tmp):
                with open(os.path.join(tmp, "root.txt")) as f:
                    root = f.read()
                press = os.path.join(root, "sessions", "05", handover.FILE)
                address = serve.address("handover", "05")
                code, said = post(address, {})
                self.assertEqual((code, said), (409, "This page takes no such press. Nothing was typed."))
                self.assertFalse(os.path.exists(press), "an empty post started a handover")
                code, said = post(address, {"act": "handover", "account": "", "model": "", "effort": ""})
                self.assertIn(code, (200, 303), said)
                post("/trial/die", {"down": "120"})
                for _ in range(50):
                    if not ports.answering(PORT):
                        break
                    time.sleep(0.1)
                self.assertFalse(ports.answering(PORT), "the server never died")
                steps, deadline = [], time.time() + 40
                while time.time() < deadline:
                    try:
                        with open(press) as f:
                            got = json.load(f)
                        step = got.get("step")
                        if step == "failed":
                            step = f"failed: {got.get('said')}"
                    except (OSError, ValueError):
                        step = "gone" if steps and not os.path.exists(press) else None
                    if step and (not steps or steps[-1] != step):
                        steps.append(step)
                    if step == "gone":
                        break
                    time.sleep(0.1)
                down = not ports.answering(PORT)
                with open(os.path.join(root, "typed.txt")) as f:
                    typed = f.read().splitlines()
                try:
                    with open(os.path.join(tmp, "programs.txt")) as f:
                        programs = [json.loads(line) for line in f]
                except OSError:
                    programs = []
            print(f"With its server killed, the press went {' → '.join(steps)}, and typed {typed}, "
                  f"in {len(programs)} program: {[' '.join(map(os.path.basename, p['argv'][:3])) for p in programs]}.",
                  file=sys.stderr)
            self.assertTrue(down, "the server came back before the handover ended")
            self.assertEqual(steps[-3:], ["launching", "done", "gone"], steps)
            self.assertEqual(typed, [handover.PREPARE, "/handover-resume 05 account 1"])
            # One program, the page's own press, started by its own spawn() in a session of its own.
            self.assertEqual([(p["argv"][:3], p["own"]) for p in programs], [([tool.PRESS[1], "press", "05"], True)])
        finally:
            shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
            shutil.rmtree(tmp, ignore_errors=True)
            if root:
                shutil.rmtree(root, ignore_errors=True)


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + process.env.PAGE;
const state = name => post('/trial/state', {name});
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
// A page brought in line with a fresh one: its picture wears the fresh one's key.
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
    await state('hot');
    const b = await open(), c = await open();
    await b.goto(url);
    await wait(500);
    let same = [];
    for (const name of ['tick', 'saving', 'launching', 'done', 'failed', 'cool', 'hot']) {
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

    // A pill I pick holds while the page changes, and Hand over names its act.
    await state('hot');
    const a = await open();
    await a.goto(url);
    await wait(500);
    await a.click('.pills[data-k="effort"] button[data-v="max"]');
    await state('tick');
    for (let i = 0; i < 60 && !(await a.evaluate(() => document.querySelector('.meter .mark').textContent === '60%')); i++) await wait(100);
    const held = await a.evaluate(() => ({moved: document.querySelector('.meter .mark').textContent,
      on: [...document.querySelectorAll('.pills[data-k="effort"] button.on')].map(b => b.dataset.v), hash: location.hash}));
    await a.click('#go');
    let spawned = '';
    for (let i = 0; i < 40 && !(spawned = await (await fetch(base + '/trial/spawned')).text()); i++) await wait(100);
    const word = await a.waitForFunction(() => document.getElementById('go').textContent === 'Saving…', null, {timeout: 4000})
      .then(() => 'Saving…', () => a.evaluate(() => document.getElementById('go').textContent));
    said('press', held.moved === '60%' && held.on.join() === 'max' && held.hash === '#effort=max'
         && /"max"\]$/.test(spawned) && word === 'Saving…' && a.loads === 1,
         `the page moved to ${held.moved} and kept my pick ${held.on} (${held.hash}); Hand over started ${spawned || 'nothing'}, and reads ${word}; ${a.loads} load`);
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "press": "My pick holds, and Hand over names its act"}


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="handover-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp, "kept"], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "PAGE": serve.address("handover", "05")})
            with open(os.path.join(tmp, "server.log"), errors="replace") as f:
                cls.logged = f.read()
            with open(os.path.join(tmp, "root.txt")) as f:
                shutil.rmtree(f.read(), ignore_errors=True)
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

    def test_my_pick_holds_and_hand_over_names_its_act(self):
        self.held("press")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "serve" in args:
        at = args.index("serve")
        serving(args[at + 1], args[at + 2] == "running")
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in args if a != NN])
