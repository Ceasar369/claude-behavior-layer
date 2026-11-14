#!/usr/bin/env python3
"""Check the launch page: its presses, what it draws on the contract, a launch outliving its server, and its page in WebKit and Chromium.

Presses: a press it cannot take is refused, and a file it cannot read is
never written over.

Drawn: on lib/trial.py's made-up folder, 1100 draws every kind of row,
escapes what a session wrote, hands the page's script its data, names the
files that move it, never writes as it draws, and draws a file cut short
at any length as unreadable.

Launch: a server on this session's port, 11NN, takes a Launch press. The
launch runs as a program of its own. The server is killed mid-launch and
comes back, as a fresh 1100 does; the launch finishes all the same, and
types its first message once.

Browser: the same server draws the made-up page. Each engine checks, in
order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My typing holds while a session writes a row, and saves, and a pill
  press saves, in one load.

  launch-page-test.py [NN] [Presses|Drawn|Launch|Browser]

NN is this session's number, 11 when none is given.
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
import types
import unittest
import urllib.parse
import urllib.request
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("launch_page_test", os.path.join(HERE, "launch-page.py"))
lp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lp)
import accounts  # noqa: E402
import launch  # noqa: E402
import live  # noqa: E402
import ports  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "11")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"launch-page-test-{NN}"
# The one way a program is started here, kept before a made-up folder refuses it.
POPEN = subprocess.Popen

ROW = {"uid": 1, "n": "07", "name": "trial", "message": "Hello.", "account": "1", "model": trial.MODEL, "effort": "high"}
WEB = {"uid": 2, "kind": "browser", "site": "1100"}
# Each state the browser asks for by name: session 05's launch.json.
STATES = {
    "a": {"rows": [ROW, WEB]},
    "s": {"after": "B", "rows": [ROW, {"uid": 3, "name": "walker", "message": "Go <b>now</b>.", "drive": True,
                                       "status": "failed: it stopped."}]},
    "b": {"rows": [{**ROW, "status": "booting", "pane": "05000000-0000-0000-0000-000000000000"}, WEB]},
    "e": {"rows": []},
    "c": {"rows": [ROW, {**WEB, "at": {"anchor": "r:1", "side": "right"}}, {"name": "later", "message": "New."}]},
    "one": {"rows": [ROW]},
}


def text(d: dict) -> str:
    return json.dumps(d, indent=2) + "\n"


class Presses(unittest.TestCase):
    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.path = lp.path("05")

    def test_an_unknown_act_is_refused_and_nothing_changes(self):
        with open(self.path) as f:
            was = f.read()
        self.assertEqual(lp.pressed("05", {"act": ["shout"]}), "This page takes no such press. Nothing was saved.")
        with open(self.path) as f:
            self.assertEqual(f.read(), was)

    def test_a_file_it_cannot_read_is_never_written_over(self):
        self.w.put("05", "launch.json", '{"rows": [')
        self.assertEqual(lp.pressed("05", {"act": ["save"], "rows": ["[]"], "seen": ["[]"]}),
                         "This page's file cannot be read, so nothing was saved.")
        with open(self.path) as f:
            self.assertEqual(f.read(), '{"rows": [')

    def test_a_save_writes_the_rows(self):
        rows = [dict(ROW, name="renamed"), WEB]
        self.assertEqual(lp.pressed("05", {"act": ["save"], "rows": [json.dumps(rows)], "seen": ["[1, 2]"]}), "")
        self.assertEqual([r.get("name") for r in lp.read("05")][0], "renamed")


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def put(self, name: str) -> None:
        self.w.put("05", "launch.json", text(STATES[name]))

    def data(self, got: str) -> dict:
        return json.loads(re.search(r'<script type="application/json" id="launch-data">(.*?)</script>', got, re.S).group(1))

    def test_every_kind_of_row_draws(self):
        self.put("a")
        got = lp.drawn("05")
        for part in ('id="row-1"', 'id="row-2"', 'id="n-1"', 'id="name-1" data-f="name" value="trial"', 'id="msg-1"',
                     'id="site-2" data-f="site" value="1100"', 'data-pill="effort" data-v="high"', 'class="on"',
                     'data-pill="drive">self-drive</button>', 'data-win=""', 'data-tab=""', 'data-d="left"',
                     'data-drop=""', "Launch · 2", 'id="watch"', live.src("launch.js"), page_tabs()):
            self.assertIn(part, got, part)
        self.assertNotIn("failed to draw", got)
        self.assertEqual([r["uid"] for r in self.data(got)["rows"]], [1, 2])

    def test_a_clone_row_shows_what_it_clones(self):
        self.w.put("05", "launch.json", text({"rows": [{**ROW, "clone": "01"}, WEB]}))
        got = lp.drawn("05")
        self.assertIn('<span class="lbl drive">clone of 01</span>', got)
        self.assertEqual(got.count("clone of"), 1)
        self.assertEqual(self.data(got)["rows"][0]["clone"], "01")

    def test_a_scheduled_page_with_a_failed_row_draws(self):
        self.put("s")
        got = lp.drawn("05")
        self.assertIn("Schedule · 2", got)
        self.assertIn('title="Launches once stage B closes"', got)
        self.assertIn('<span class="state">failed: it stopped.</span>', got)
        self.assertIn('class="row failed"', got)

    def test_a_booting_page_takes_no_press(self):
        self.put("b")
        got = lp.drawn("05")
        self.assertIn("Launching…", got)
        self.assertIn("booting…", got)
        self.assertEqual(got.count("<textarea"), got.count('data-f="message" disabled'))
        self.assertIn('id="add" disabled', got)

    def test_what_a_session_wrote_is_escaped(self):
        self.put("s")
        got = lp.drawn("05")
        self.assertNotIn("<b>now</b>", got)
        self.assertIn("Go &lt;b&gt;now&lt;/b&gt;.", got)
        self.assertEqual(self.data(got)["rows"][1]["message"], "Go <b>now</b>.")

    def test_a_row_the_session_wrote_shows_its_uid_and_the_file_stays_as_written(self):
        self.put("c")
        with open(lp.path("05")) as f:
            was = f.read()
        got = lp.drawn("05")
        self.assertIn('id="row-3"', got)
        with open(lp.path("05")) as f:
            self.assertEqual(f.read(), was)

    def test_no_row_says_so_and_my_own_page_waits_with_one(self):
        self.put("e")
        self.assertIn("No row waits", lp.drawn("05"))
        self.assertIn('id="row-1"', lp.drawn("00"))

    def test_a_file_cut_short_at_any_length_draws_as_unreadable(self):
        whole = text(STATES["c"])
        # A file read half-written is read again for a fifth of a second: no wait here.
        with patch.object(launch.time, "sleep"):
            for cut in range(len(whole) + 1):
                self.w.put("05", "launch.json", whole[:cut])
                got = lp.drawn("05")
                self.assertNotIn("failed to draw", got, f"cut at {cut}")
                self.assertEqual(lp.page.esc(lp.UNREAD) in got, cut < len(whole.rstrip()), f"cut at {cut}")

    def test_its_files_name_its_file_by_its_folder(self):
        named = lp.files("00")
        self.assertIn(registry.folder("00"), named)
        self.assertIn(lp.path("00"), named)
        self.assertIn(accounts.FILE, named)

    def test_a_draw_starts_no_program(self):
        self.put("a")
        lp.drawn("05")
        self.assertEqual(self.w.started, [])


def page_tabs() -> str:
    return lp.page.TABS.strip()[:40]


# ---- the server a browser and a launch reach ------------------------------------

def serving(tmp: str) -> None:
    """The made-up folder's page, on a sessions folder that
    outlives this server: tmp/work. A launch starts the stand-in program
    below, as a press starts tools/launch.py page NN. Started again, the
    server first does what a fresh 1100 does: resume."""
    with trial.world() as w:
        work = os.path.join(tmp, "work")
        if not os.path.isdir(work):
            shutil.copytree(w.work, work)
        program = [sys.executable, os.path.abspath(__file__), NN, "launcher", tmp]
        with patch.object(registry, "WORK", work), patch.object(launch, "PROGRAM", program), \
                patch.object(launch, "subprocess", types.SimpleNamespace(Popen=POPEN, DEVNULL=subprocess.DEVNULL)):
            path = lp.path("05")
            lp.resume("05")
            table = live.Table([lp.LIVE])

            def old_take(form: dict, at: str) -> str:
                if at == "/trial/state":
                    registry.rewrite(path, text(STATES[form["name"][0]]))
                    return ""
                if at == "/trial/add":
                    with lp.LOCK:
                        d = lp.whole("05")
                        d["rows"].append({"name": "later", "message": "Written by the session."})
                        lp.put("05", d)
                    return ""
                if at == "/trial/die":
                    trial.die(tmp, form["down"][0])
                return "Nothing at this address takes a press."

            serve.run(SKILL, PORT, lambda: "home", recheck=1,
                      **table.riding(take=old_take, hears=lambda: []))


def launcher(tmp: str, nn: str, fd: int) -> None:
    """The stand-in for tools/launch.py page NN: lib/launch.py's run, on the
    server's sessions folder, with iTerm and the session stood in. A pane
    opens at once. Its session claims once tmp/claimed is written, and
    each first message typed is a line in tmp/typed."""
    registry.WORK = os.path.join(tmp, "work")
    accounts.take = lambda: accounts.FALLBACK
    launch.place = lambda r, made, windows: f"pane-{r['uid']}"
    launch.start = lambda r, pane: launch.note(r, pane, "boot line typed", True)

    def arrive(row: dict, pane: str, by: str = "") -> bool:
        while not os.path.exists(os.path.join(tmp, "claimed")):
            time.sleep(0.05)
        with open(os.path.join(tmp, "typed"), "a") as f:
            f.write(row["n"] + "\n")
        launch.note(row, pane, "first message typed", True)
        return True

    launch.arrive = arrive
    launch.run(nn, fd)


class Unfollowed(urllib.request.HTTPRedirectHandler):
    """A press's 303 is its answer, never an address to go on to."""

    def redirect_request(self, *given):
        return None


def post(path: str, **form) -> int:
    """One press on the test's server: its answer's code, 0 when it never answered."""
    try:
        with urllib.request.build_opener(Unfollowed).open(urllib.request.Request(
                f"http://127.0.0.1:{PORT}{path}", urllib.parse.urlencode(form).encode()), timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code
    except OSError:
        return 0


def until(fn, seconds: float = 15) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        if fn():
            return True
        time.sleep(0.05)
    return False


class Launch(unittest.TestCase):
    """A Launch press, its server killed mid-launch, and the launch finishing."""

    def test_a_launch_outlives_its_server_and_types_its_first_message_once(self):
        tmp = tempfile.mkdtemp(prefix="launch-page-test-")
        self.addCleanup(shutil.rmtree, tmp, True)
        self.addCleanup(shutil.rmtree, os.path.dirname(serve.pidfile(SKILL)), True)
        file = os.path.join(tmp, "work", "05", "launch.json")

        def rows() -> list:
            try:
                with open(file) as f:
                    return json.load(f)["rows"]
            except (OSError, ValueError, KeyError):
                return []

        with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
            self.assertIn(post("/trial/state", name="one"), (200, 303))
            said = post(serve.address("launch", "05"), act="launch", rows=json.dumps([ROW]), seen="[1]", press="p1")
            self.assertIn(said, (200, 303), self.log(tmp))
            booted = until(lambda: any(r.get("status") == "booting" and r.get("pane") for r in rows()))
            self.assertTrue(booted, f"the row never booted: {rows()} {self.log(tmp)}")
            self.assertEqual(post("/trial/die", down="1"), 0)
            # Back, the server has resumed as a fresh 1100 does, and left the launch alone.
            self.assertTrue(until(lambda: ports.answering(PORT), 20), "the server never came back")
            time.sleep(0.5)
            still = rows()
            with open(os.path.join(tmp, "claimed"), "w"):
                pass
            finished = until(lambda: not os.path.exists(file), 20)
            with patch.object(registry, "WORK", os.path.join(tmp, "work")):
                running = launch.running("05")
        with open(os.path.join(tmp, "typed")) if os.path.exists(os.path.join(tmp, "typed")) else open(os.devnull) as f:
            typed = f.read().split()
        print(f"Launched, its server killed mid-launch and back: the row stood {still[0].get('status')} meanwhile; "
              f"the launch finished: {finished}; first messages typed: {typed}; still running: {running}.", flush=True)
        self.assertEqual(still[0].get("status"), "booting")
        self.assertTrue(finished, self.log(tmp))
        self.assertEqual(typed, ["07"])
        self.assertFalse(running)

    @staticmethod
    def log(tmp: str) -> str:
        out = ""
        for name in ("server.log", os.path.join("launches", "05.log")):
            try:
                with open(os.path.join(tmp, name), errors="replace") as f:
                    out += f.read()[-800:]
            except OSError:
                pass
        return out


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + process.env.LAUNCH_PAGE;
const state = name => post('/trial/state', {name});
const file = () => { try { return fs.readFileSync(process.env.LAUNCH_FILE, 'utf8'); } catch (e) { return ''; } };
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       n.matches('button, input, textarea') ? n.disabled : null, [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify([walk(document.querySelector('header.top')), walk(document.querySelector('main'))]);
});
const settled = async (p, rows) => {
  await p.waitForFunction(n => document.querySelectorAll('#rows .row').length === n && document.querySelector('#map .tabmap, #map .note')
    && !('busy' in document.getElementById('watch').dataset), rows, {timeout: 8000});
  await wait(400);
};
const first = p => p.evaluate(() => { const c = document.querySelector('#rows .row'); if (c) c.click(); });

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1200, height: 900}});
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
    for (const [name, rows] of [['s', 2], ['b', 2], ['a', 2], ['e', 0], ['c', 3], ['a', 2]]) {
      await state(name);
      await settled(b, rows);
      await c.goto(url);
      await settled(c, rows);
      for (const p of [b, c]) { await first(p); await wait(200); }
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My typing holds while a session writes a row, and saves; a pill press saves.
    await state('a');
    const a = await open();
    await a.goto(url);
    await settled(a, 2);
    await a.click('#name-1');
    await a.keyboard.press('End');
    await a.keyboard.type(' typed');
    for (let i = 0; i < 40 && !file().includes('"name": "trial typed"'); i++) await wait(100);
    const saved = file().includes('"name": "trial typed"');
    await post('/trial/add', {});
    await a.waitForFunction(() => document.querySelectorAll('#rows .row').length === 3, null, {timeout: 8000});
    await a.keyboard.type('!');
    const held = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('name-1').value}));
    for (let i = 0; i < 40 && !file().includes('"name": "trial typed!"'); i++) await wait(100);
    const kept = file().includes('"name": "trial typed!"') && file().includes('Written by the session.');
    await a.click('#row-1 [data-pill="effort"][data-v="max"]');
    for (let i = 0; i < 40 && !file().includes('"effort": "max"'); i++) await wait(100);
    const pill = file().includes('"effort": "max"');
    await wait(600);
    const on = await a.evaluate(() => document.querySelector('#row-1 [data-pill="effort"][data-v="max"]').classList.contains('on'));
    said('typing', saved && held.active === 'name-1' && held.words === 'trial typed!' && kept && pill && on && a.loads === 1,
         `typed words saved: ${saved}; a session wrote a row while I typed, and my cursor stayed in ${held.active}, `
         + `holding "${held.words}"; both saved: ${kept}; a pill press saved: ${pill}, and shows picked: ${on}; ${a.loads} load`);

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "My typing, a session's write and a pill"}


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="launch-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}",
                                              "LAUNCH_PAGE": serve.address("launch", "05"),
                                              "LAUNCH_FILE": os.path.join(tmp, "work", "05", "launch.json")})
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

    def test_my_typing_holds_while_a_session_writes_and_a_pill_saves(self):
        self.held("typing")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "serve" in args:
        serving(args[args.index("serve") + 1])
    elif "launcher" in args:
        at = args.index("launcher")
        launcher(args[at + 1], args[at + 2], int(args[args.index("--held") + 1]))
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in args if a != NN])
