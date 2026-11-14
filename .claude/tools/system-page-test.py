#!/usr/bin/env python3
"""Check System: its press, what it draws on the contract, and its page in WebKit and Chromium.

Presses: a press System takes none of is refused, and a finding's button
acts on its finding alone.

Drawn: on lib/trial.py's made-up folder, every outside read stood in for,
1100 draws every part, carries no script but its own, starts no program,
saves nothing, draws the same once the clock moves, names the files that
move it, and draws each state file cut short at any length.

Browser: a server on this session's port, 11NN, draws the made-up System
on the contract, as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My place holds while it changes: unsent words, a pill pressed, a finding's End.
  One account reading moved, framed as 9 November's home framed it, and
  alone, reloads nothing.

  system-page-test.py [NN] [Presses|Drawn|Browser]

NN is this session's number, 11 when none is given.
"""

import contextlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import accounts  # noqa: E402
import engines  # noqa: E402
import finish  # noqa: E402
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

dashboard = page.tool("sessions-dashboard")
system = page.tool("system-page")

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "11")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"system-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

# What trial.world() stands in for that System reads for itself, as found
# before any block stands them in.
REAL = {"read": accounts.read, "effort": accounts.effort, "model": accounts.model}
POPEN = subprocess.Popen
# Band 00 and the other ports, as the reader would have read them.
SEEN = ({**{p: p % 200 == 0 for p in system.PORTS}, system.ports.POSTGRES: True},
        [(1105, "Python"), (1207, "node"), (63000, "Chrome")])
# Each state the browser asks for by name: an account's reading and the
# guard's findings. Times are from now, in seconds.
FOUND = {"id": "warn-1", "level": "warn", "title": "Memory is low", "line": "15:00 · 2 GB free.",
         "buttons": [{"verb": "tell", "label": "Tell 05", "note": "Stop."},
                     {"verb": "end", "label": "End", "again": {"question": "End it?", "yes": "End", "no": "Keep"}}],
         "sessions": [{"number": "05", "gb": 1.5, "idle": 12}]}
STATES = {
    "a": {"five": (36.4, 7200), "week": (17.0, 400000), "read": -300, "found": [FOUND]},
    "b": {"five": (52.0, 7000), "week": (17.0, 400000), "read": -120, "found": []},
    "c": {"five": (52.0, -60), "week": (88.0, 90000), "read": -40000, "found": [FOUND, {**FOUND, "id": "warn-2",
                                                                                    "title": "Swap is high"}]},
}


class Stood:
    """System's outside reads, each a file in the made-up folder."""

    def __init__(self, w):
        self.w, self.root = w, os.path.join(w.root, "system")
        for d in ("finish", "accounts", "codex"):
            os.makedirs(os.path.join(self.root, d))
        self.limits = os.path.join(self.root, "finish", "limits-1.json")
        self.findings = os.path.join(self.root, "findings.json")
        self.config = os.path.join(self.root, "outsource.json")
        shutil.copy(engines.CONFIG, self.config)
        if os.path.exists(os.path.join(engines.CODEX, "models_cache.json")):
            shutil.copy(os.path.join(engines.CODEX, "models_cache.json"), os.path.join(self.root, "codex"))
        self.guard = [sys.executable, "-c", "import sys; print(sys.argv[3].capitalize() + 'ed ' + sys.argv[2])"]

    def patches(self) -> list:
        acct = os.path.join(self.root, "accounts")
        return [mock.patch.object(finish, "STATE", os.path.dirname(self.limits)),
                mock.patch.object(engines, "SESSIONS", self.w.work),
                mock.patch.object(engines, "CONFIG", self.config),
                mock.patch.object(engines, "LOCK", os.path.join(self.root, "engines.lock")),
                mock.patch.object(engines, "CODEX", os.path.join(self.root, "codex")),
                mock.patch.object(accounts, "settings_file", lambda a: os.path.join(acct, f"settings-{a}.json")),
                mock.patch.object(accounts, "FILE", os.path.join(acct, "order.json")),
                mock.patch.object(accounts, "EFFORT", os.path.join(acct, "effort.json")),
                mock.patch.object(accounts, "MODEL", os.path.join(acct, "model.json")),
                *(mock.patch.object(accounts, k, fn) for k, fn in REAL.items()),
                mock.patch.object(system, "FINDINGS", self.findings),
                mock.patch.object(system, "GUARD", self.guard),
                mock.patch.object(system, "seen", lambda: SEEN),
                mock.patch.object(system, "looked", lambda: SEEN)]

    def state(self, name: str) -> None:
        """One named state, every file written whole."""
        s, now = STATES[name], time.time()
        windows = {"five_hour": {"used_percentage": s["five"][0], "resets_at": int(now + s["five"][1])},
                   "seven_day": {"used_percentage": s["week"][0], "resets_at": int(now + s["week"][1])}}
        self.write(self.limits, windows)
        os.utime(self.limits, (now + s["read"], now + s["read"]))
        self.write(self.findings, {"findings": s["found"]})

    def read(self, minutes: float) -> None:
        """The account's reading kept again, `minutes` ago, its numbers as they stand."""
        with open(self.limits) as f:
            self.write(self.limits, json.load(f))
        os.utime(self.limits, (time.time() - minutes * 60,) * 2)

    @staticmethod
    def write(path: str, data) -> None:
        with open(path + ".new", "w") as f:
            json.dump(data, f)
        os.replace(path + ".new", path)


@contextlib.contextmanager
def made_up():
    """The made-up folder, System's reads stood in for, in state a."""
    with trial.world() as w, contextlib.ExitStack() as stack:
        s = Stood(w)
        for p in s.patches():
            stack.enter_context(p)
        s.state("a")
        yield w, s


class Presses(unittest.TestCase):
    def setUp(self):
        world = made_up()
        self.w, self.s = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def test_a_press_it_takes_none_of_is_refused(self):
        self.assertEqual(system.pressed({"order": ["1"]}), system.NO_SUCH)

    def test_a_closed_finding_and_an_unoffered_button_are_refused(self):
        self.assertEqual(system.pressed({"act": ["end"], "finding": ["warn-9"]}),
                         "This finding is already closed. Nothing was done.")
        self.assertEqual(system.pressed({"act": ["kill"], "finding": ["warn-1"]}),
                         "This finding offers no such button. Nothing was done.")

    def test_a_button_acts_on_its_finding_alone(self):
        # The guard stood in for is the one program a press may start.
        with mock.patch.object(subprocess, "Popen", POPEN):
            got = system.pressed({"act": ["end"], "finding": ["warn-1"]}).outside()
        self.assertIsInstance(got, serve.Said)
        self.assertEqual(str(got), "Ended warn-1")

    def test_1100_still_answers_each_name_another_file_calls(self):
        for name in ("BAND", "DATABASE", "PLANS", "LEVELS", "seen", "other", "usage", "engines_seen", "findings",
                     "clock", "band_state"):
            self.assertTrue(hasattr(dashboard, name), name)
        self.assertIs(dashboard.engines, engines)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = made_up()
        self.w, self.s = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)

    def test_every_part_draws(self):
        got = system.drawn()
        for part in ('id="watch"', live.src("system.js"), "claude-1", 'data-window="', 'data-reset="', 'data-at="',
                     'id="order"', 'id="effort"', 'id="model"', 'id="threshold"',
                     'id="rail"', '<div class="lbl">Band 00</div>', "Other ports · 2", "1 more port", 'id="f-warn-1"',
                     '<script type="application/json" id="system">'):
            self.assertIn(part, got, part)
        self.assertNotIn("failed to draw", got)

    def test_the_app_views_open_now_draw_and_one_open_twice_reads_amber(self):
        self.assertIn('<div class="lbl">App views · 0</div>', system.drawn())
        self.assertIn("No app view is open.", system.drawn())
        now = time.time()
        with mock.patch.object(system.show, "HOMES", {("12", "a"): now, ("2", "b"): now, ("2", "c"): now,
                                                     ("5", "gone"): now - system.show.OPEN - 1}):
            self.assertEqual(system.opened(), ((2, 2), (12, 1)))
            got = system.drawn()
        self.assertIn('<div class="lbl">App views · 2</div>', got)
        self.assertIn('<b>View 2</b></span><span class="c" style="color:#a8741c">2 panels</span>', got)
        self.assertIn('<b>View 12</b></span><span class="c dim">1 panel</span>', got)
        self.assertLess(got.index("View 2<"), got.index("View 12<"))
        self.assertNotIn("View 5<", got)
        self.assertNotIn("No app view is open.", got)
        self.assertIn(system.opened, system.LIVE.looks)

    def test_it_carries_no_script_but_its_own(self):
        got = system.drawn()
        inline = [s for s in re.findall(r"<script([^>]*)>(.*?)</script>", got, re.S)
                  if "src=" not in s[0] and "application/json" not in s[0]]
        shell = page.render("x", [("", "")])
        self.assertEqual(len(inline), len(re.findall(r"<script>", shell)), "an inline script beyond the shell's")

    def test_it_starts_no_program_and_logs_no_error(self):
        logged = io.StringIO()
        with contextlib.redirect_stderr(logged):
            system.drawn()
            system.files()
        self.assertEqual(self.w.started, [])
        self.assertNotIn("Traceback", logged.getvalue())

    def test_it_saves_nothing(self):
        stamps = lambda: {os.path.join(d, f): os.stat(os.path.join(d, f)).st_mtime_ns
                          for d, _, fs in os.walk(self.s.root) for f in fs}
        before = stamps()
        system.drawn()
        self.assertEqual(stamps(), before)

    def test_it_draws_the_same_once_the_clock_moves(self):
        for name in STATES:
            self.s.state(name)
            first = system.drawn()
            with trial.clock():
                trial.forget()
                again = system.drawn()
            self.assertEqual(first, again, f"state {name}: what ticks is drawn in the browser, never by 1100")

    def test_its_files_name_each_file_it_reads(self):
        named = system.files()
        for f in (self.s.limits, self.s.findings, self.s.config, accounts.EFFORT, accounts.MODEL,
                  accounts.FILE, accounts.settings_file("1"), os.path.join(self.w.work, "05", "record.json")):
            self.assertIn(f, named, f)

    def test_each_state_file_cut_short_at_any_length_still_draws(self):
        cases = {self.s.limits: "This account's reading is unreadable", self.s.findings: "cannot be read",
                 self.s.config: "outsource settings are unreadable"}
        logged = io.StringIO()
        for path, says in cases.items():
            with open(path) as f:
                whole = f.read()
            for cut in range(len(whole)):
                with open(path, "w") as f:
                    f.write(whole[:cut])
                with contextlib.redirect_stderr(logged):
                    got = system.drawn()
                self.assertNotIn("failed to draw", got, f"{path} cut at {cut}")
                for a in accounts.KNOWN:
                    self.assertIn(f"claude-{a}", got, f"{path} cut at {cut}: a row lost")
                if cut == 1:
                    self.assertIn(says, got, f"{path} cut at {cut}")
            with open(path, "w") as f:
                f.write(whole)
        self.assertNotIn("Traceback", logged.getvalue())


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + '/system';
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
const settled = async p => {
  await p.waitForFunction(() => document.getElementById('watch') && !('busy' in document.getElementById('watch').dataset), null, {timeout: 6000});
  await wait(500);
};

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true, args: ENGINE === 'chromium' ? ['--disable-partial-raster'] : []});
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
    await settled(b);
    let same = [];
    for (const name of ['b', 'c', 'a', 'c', 'b']) {
      await state(name);
      await b.waitForFunction(() => true);
      await wait(1200);
      await settled(b);
      await c.goto(url);
      await settled(c);
      const x = await snap(b), y = await snap(c);
      let i = 0;
      while (i < x.length && x[i] === y[i]) i++;
      same.push(x === y ? name : `${name} differs: ${x.slice(i - 120, i + 80)} | ${y.slice(i - 120, i + 80)}`);
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My place holds while it changes: unsent words, a pill pressed, a finding's End.
    await state('a');
    const a = await open();
    await a.goto(url);
    await settled(a);
    await a.click('#order');
    await a.keyboard.type('2 1');
    await state('b');
    await a.waitForFunction(() => !document.getElementById('f-warn-1'), null, {timeout: 6000});
    await settled(a);
    const kept = await a.evaluate(() => ({active: document.activeElement.id, words: document.getElementById('order').value}));
    const pill = await a.evaluate(() => [...document.querySelectorAll('#effort button')].find(b => !b.classList.contains('on')).dataset.v);
    await a.click(`#effort button[data-v="${pill}"]`);
    const pilled = await a.waitForFunction(v => document.querySelector(`#effort button[data-v="${v}"]`).classList.contains('on'), pill, {timeout: 6000}).then(() => true, () => false);
    await state('a');
    await a.waitForSelector('#f-warn-1 [data-verb="end"]', {timeout: 6000});
    await settled(a);
    await a.click('#f-warn-1 > .bs [data-verb="end"]');
    const asked = await a.evaluate(() => !document.querySelector('#f-warn-1 > .q').hidden);
    await a.click('#f-warn-1 [data-sure]');
    const ended = await a.waitForFunction(() => (document.querySelector('#f-warn-1 .said') || {}).textContent === 'Ended warn-1', null, {timeout: 6000}).then(() => true, () => false);
    said('place', kept.active === 'order' && kept.words === '2 1' && pilled && asked && ended && a.loads === 1,
         `my cursor stayed in ${kept.active}, its words "${kept.words}"; the ${pill} pill took: ${pilled}; End asked first: ${asked}, then ended: ${ended}; ${a.loads} load`);
    await a.close();

    // One account reading moved, framed as 9 November's home framed it, and alone: no reload.
    const storm = {};
    for (const [name, to, framed] of [['contract, framed', '/system', true], ['contract, alone', '/system', false]]) {
      await state('a');
      const p = await open();
      // Every load of the page, its own or its frame's, kept or given up.
      let n = 0;
      p.on('request', r => { if (r.isNavigationRequest() && new URL(r.url()).pathname === to) n++; });
      await p.goto(base + (framed ? '/trial/home?to=' + encodeURIComponent(to) : to));
      const frame = () => framed ? p.frames().find(f => f.url().includes(to)) : p.mainFrame();
      await wait(1500);
      await frame().waitForSelector('#watch', {state: 'attached', timeout: 6000});
      await wait(1500);
      const before = n;
      await post('/trial/read', {minutes: '3'});
      await wait(10000);
      storm[name] = n - before;
      storm[name + ' shows it'] = await frame().evaluate(() => [...document.querySelectorAll('[data-at]')].map(e => e.textContent).join(' ')).catch(() => '');
      await p.close();
    }
    said('storm', storm['contract, framed'] === 0 && storm['contract, alone'] === 0
                  && /Last read/.test(storm['contract, framed shows it']) && /Last read/.test(storm['contract, alone shows it']),
         JSON.stringify(storm));

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

# 9 November's home, as commit daed2096 drew its frame watch: each framed
# page hands its watch up, and a page told it moved is reloaded at once,
# with no wait for the reload to land. Only the lines that watch frames.
HOME = r"""<!doctype html><meta charset="utf-8"><style>body{margin:0}iframe{border:0;width:1200px;height:780px}</style>
<iframe class="on" src="%TO%"></iframe>
<script>
const watched = new Set();
let asking = null, soon = 0;
const rewatch = () => { clearTimeout(soon); soon = setTimeout(() => asking && asking.abort(), 50); };
window.watchFor = w => { watched.add(w); rewatch(); };
const shown = w => w.frameElement.classList.contains('on');
function watchOf(w) {
  try {
    if (w.closed || !w.frameElement || !w.frameElement.isConnected) return null;
    const e = w.document.getElementById('watch');
    return e ? {w, path: w.location.pathname + w.location.search, key: e.dataset.key,
                busy: 'busy' in e.dataset, typing: Date.now() - (w.typedAt || 0) < 3000} : null;
  } catch (e) { return null; }
}
(async () => {
  const nap = ms => new Promise(f => setTimeout(f, ms));
  for (;;) {
    const marks = [];
    for (const w of watched) { const m = watchOf(w); if (!m) watched.delete(w); else if (shown(w)) marks.push(m); }
    if (!marks.length) { await nap(100); continue; }
    const q = marks.map(m => 'path=' + encodeURIComponent(m.path) + '&key=' + encodeURIComponent(m.key)).join('&');
    const ask = asking = new AbortController();
    try {
      const r = await fetch('/heard?' + q, {signal: ask.signal});
      if (r.headers.get('X-Heard')) {
        const got = (await r.text()).split('\n');
        let moved = false;
        marks.forEach((m, i) => {
          const now = got[i], still = watchOf(m.w);
          if (now !== undefined && now !== m.key && still && !still.busy && still.key === m.key) {
            if (typeof m.w.told === 'function') { m.w.told(now); moved = true; }
            else if (!still.typing) { m.w.location.reload(); moved = true; }
          }
        });
        if (!moved) await nap(1000);
        continue;
      }
    } catch (e) { if (ask.signal.aborted) continue; }
    await nap(3000);
  }
})();
</script>
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "place": "My place holds while it changes",
         "storm": "One account reading moved"}


def serving(tmp: str) -> None:
    """The made-up System on the contract, with the test's own presses. The
    guard stood in for is the one program a press may start."""
    with made_up() as (w, s), mock.patch.object(subprocess, "Popen", POPEN):
        table = live.Table([system.LIVE])

        def old_route(at: str):
            bare, _, query = at.partition("?")
            if bare == "/trial/home":
                to = urllib.parse.parse_qs(query).get("to", ["/system"])[0]
                return HOME.replace("%TO%", html.escape(to)).encode(), "text/html; charset=utf-8"
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str):
            if at == "/trial/state":
                s.state(form["name"][0])
                return ""
            if at == "/trial/read":
                s.read(float(form["minutes"][0]))
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return dashboard.take(form, at)

        serve.run(SKILL, PORT, lambda: "home", recheck=1,
                  **table.riding(route=old_route, take=old_take, hears=system.files))


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="system-page-test-")
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

    def test_my_place_holds_while_it_changes(self):
        self.held("place")

    def test_one_reading_moved_reloads_nothing_on_the_contract(self):
        self.held("storm")


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
