#!/usr/bin/env python3
"""Check Files: what it draws on the contract, and its page in WebKit and Chromium.

Drawn: on lib/trial.py's made-up folder, 1100 draws every session's
folder, carries no script but its own, starts no program, draws the same
once the clock moves, names the files that move it, marks a picked file
gone once it is, and draws a record cut short at any length, its folder
still shown.

Browser: a server on this session's port, 11NN, draws the made-up Files
on the contract, as a program of its own. Each engine checks, in order:

  A changed page, put in place, equals the page drawn fresh, state by state.
  My place holds while it changes: a picked file rewritten draws again
  where I scrolled, a file removed says so in its place, a file written
  into an open folder shows as its row by itself within a second, and
  Refresh fills an open folder again, in one load.

  files-page-test.py [NN] [Drawn|Browser]

NN is this session's number, 11 when none is given.
"""

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

files = page.tool("files-page")
dashboard = page.tool("sessions-dashboard")

NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "11")
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"files-page-test-{NN}"
SERVING = "serve" in sys.argv[1:]

PICKED = "05/notes/long.md"
LONG = "".join(f"Line {i} of a long note.\n" for i in range(400))


def state(w, name: str) -> None:
    """One named state of the made-up folder.

    a: a long note in 05's notes. b: a file added at 05's top, and 10's
    title changed. c: the long note rewritten. d: the long note gone."""
    note = os.path.join(w.work, "05", "notes", "long.md")
    if name == "a":
        w.put("05", "notes/long.md", LONG)
        for extra in ("05/added.md",):
            with contextlib.suppress(OSError):
                os.remove(os.path.join(w.work, extra))
        registry.write_whole(os.path.join(w.work, "10", registry.RECORD), json.dumps(w.held["10"], indent=2) + "\n")
        # Every file an hour old, so how long ago reads alike on two pages a second apart.
        for d, _, names in os.walk(w.work):
            for n in names:
                os.utime(os.path.join(d, n), (time.time() - 3600,) * 2)
    elif name == "b":
        w.put("05", "added.md", "# Added\n")
        registry.write_whole(os.path.join(w.work, "10", registry.RECORD),
                             json.dumps({**w.held["10"], "title": "10-renamed-team"}, indent=2) + "\n")
    elif name == "c":
        registry.write_whole(note, LONG.replace("Line 3 ", "Line three "))
    elif name == "d":
        with contextlib.suppress(OSError):
            os.remove(note)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        state(self.w, "a")

    def test_every_session_folder_draws(self):
        got = files.drawn("")
        for nn in ("05", "10", "11", "12"):
            self.assertIn(f'<details data-k="{nn}" id="d-{nn}">', got, nn)
        for part in ('id="watch"', live.src("files.js"), '<script type="application/json" id="picked">{"mark": "none"}',
                     "Team 10 · ", 'id="again"', 'id="fview"'):
            self.assertIn(part, got, part)
        self.assertNotIn("failed to draw", got)

    def test_it_carries_no_script_but_its_own(self):
        got = files.drawn("")
        inline = [s for s in re.findall(r"<script([^>]*)>(.*?)</script>", got, re.S)
                  if "src=" not in s[0] and "application/json" not in s[0]]
        self.assertEqual(len(inline), len(re.findall(r"<script>", page.render("x", [("", "")]))))

    def test_it_starts_no_program_logs_no_error_and_draws_the_same_once_the_clock_moves(self):
        logged = io.StringIO()
        with contextlib.redirect_stderr(logged):
            first = files.drawn("f=" + PICKED)
            files.files("f=" + PICKED)
            with trial.clock():
                trial.forget()
                again = files.drawn("f=" + PICKED)
        self.assertEqual(self.w.started, [])
        self.assertNotIn("Traceback", logged.getvalue())
        self.assertEqual(first, again, "what ticks is drawn in the browser, never by 1100")

    def test_a_picked_file_is_marked_and_named_until_gone(self):
        note = os.path.join(self.w.work, *PICKED.split("/"))
        got = files.drawn("f=" + PICKED)
        self.assertIn(json.dumps({"mark": files.mark(os.path.realpath(note))}), got)
        self.assertIn(os.path.realpath(note), files.files("f=" + PICKED))
        state(self.w, "d")
        self.assertIn('{"mark": "none"}', files.drawn("f=" + PICKED))
        self.assertIn(os.path.realpath(note), files.files("f=" + PICKED))

    def test_a_query_outside_a_session_folder_names_nothing(self):
        for query in ("f=05/../../etc/passwd", "f=../x", "f=5/x", ""):
            self.assertEqual(files.named(query), "", query)
            self.assertIn('{"mark": "none"}', files.drawn(query))

    def test_a_record_cut_short_at_any_length_keeps_its_folder(self):
        path = os.path.join(self.w.work, "11", registry.RECORD)
        with open(path) as f:
            whole = f.read()
        for cut in range(len(whole)):
            with open(path, "w") as f:
                f.write(whole[:cut])
            got = files.drawn("")
            self.assertNotIn("failed to draw", got, f"cut at {cut}")
            self.assertIn('id="d-11"', got, f"cut at {cut}: its folder lost")
            # Cut of its last newline alone, the record still reads whole.
            if whole[:cut].strip() != whole.strip():
                self.assertIn("sessions/11/ · its record is unreadable", got, f"cut at {cut}")
            self.assertIn(path, files.files(""), f"cut at {cut}")

    def test_1100_still_answers_each_name_another_file_calls(self):
        for name in ("size", "count", "listed", "inside", "tree", "text", "raw"):
            self.assertTrue(hasattr(dashboard, name), name)


# Every check, in each engine: its name, whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const PICKED = process.env.PICKED;
const url = base + '/files';
const state = name => post('/trial/state', {name});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy', 'id'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('details') ? n.open : null,
       // How long ago ticks on its own, a second apart on two pages.
       'since' in n.dataset ? [] : [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify(walk(document.querySelector('main')));
});
const settled = async p => {
  await p.waitForFunction(() => document.getElementById('watch') && !('busy' in document.getElementById('watch').dataset)
    && !/Loading/.test(document.getElementById('fview').textContent), null, {timeout: 6000});
  await wait(500);
};

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true, args: ENGINE === 'chromium' ? ['--disable-partial-raster'] : []});
    // 05's folder and its notes open, as I left them on this device.
    const context = await browser.newContext({viewport: {width: 1200, height: 800}});
    await context.addInitScript(() => { if (!localStorage.getItem('files-open')) localStorage.setItem('files-open', JSON.stringify({'05': true, '05/notes': true})); });
    const open = async () => {
      const p = await context.newPage();
      p.loads = 0;
      p.on('request', r => { if (r.isNavigationRequest() && r.frame() === p.mainFrame()) p.loads++; });
      return p;
    };

    // A changed page, put in place, equals the page drawn fresh, state by state.
    await state('a');
    const b = await open(), c = await open();
    await b.goto(url + '?f=' + encodeURIComponent(PICKED));
    await settled(b);
    let same = [];
    for (const name of ['b', 'c', 'd', 'a']) {
      await state(name);
      await wait(1500);
      await settled(b);
      // A file added deep in a folder is filled by Refresh, on both.
      await b.click('#again');
      await wait(800);
      await settled(b);
      await c.goto(url + '?f=' + encodeURIComponent(PICKED));
      await settled(c);
      const x = await snap(b), y = await snap(c);
      let i = 0;
      while (i < x.length && x[i] === y[i]) i++;
      same.push(x === y ? name : `${name} differs: ${x.slice(i - 100, i + 80)} | ${y.slice(i - 100, i + 80)}`);
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // My place holds while it changes.
    await state('a');
    const a = await open();
    await a.goto(url + '?f=' + encodeURIComponent(PICKED));
    await settled(a);
    await a.evaluate(() => { document.getElementById('fview').scrollTop = 300; });
    await state('c');
    const redrawn = await a.waitForFunction(() => document.getElementById('fview').textContent.includes('Line three'), null, {timeout: 6000}).then(() => true, () => false);
    const top = await a.evaluate(() => document.getElementById('fview').scrollTop);
    await state('d');
    const gone = await a.waitForFunction(() => document.getElementById('fview').textContent.includes('This file is gone.'), null, {timeout: 6000}).then(() => true, () => false);
    await state('a');
    await a.waitForFunction(() => document.getElementById('fview').textContent.includes('Line 3 '), null, {timeout: 6000}).catch(() => {});
    // A file written into an open folder shows as its row by itself, within a second.
    const wrote = Date.now();
    await state('b');
    const itself = await a.waitForSelector('[data-f="05/added.md"]', {timeout: 6000}).then(() => Date.now() - wrote, () => -1);
    await a.click('#again');
    await wait(800);
    const filled = await a.$('[data-f="05/added.md"]').then(e => !!e);
    said('place', redrawn && top === 300 && gone && itself >= 0 && itself <= 1000 && filled && a.loads === 1,
         `the picked file rewritten drew again: ${redrawn}, scrolled at ${top}; removed, it says so: ${gone}; a file written into 05's open folder showed by itself ${itself} ms on; Refresh filled it again: ${filled}; ${a.loads} load`);
    await a.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "place": "My place holds while it changes"}


def serving(tmp: str) -> None:
    """The made-up Files on the contract, its folders and files, and the
    test's own presses."""
    with trial.world() as w:
        state(w, "a")
        table = live.Table([files.LIVE])

        def old_route(at: str):
            bare, _, query = at.partition("?")
            if m := re.fullmatch(r"/tree/(\d{2})/?(.*)", bare):
                return files.tree(m.group(1), urllib.parse.unquote(m.group(2)))
            if m := re.fullmatch(r"/text/(\d{2})/(.+)", bare):
                return files.text(m.group(1), urllib.parse.unquote(m.group(2)))
            return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404

        def old_take(form: dict, at: str) -> str:
            if at == "/trial/state":
                state(w, form["name"][0])
                return ""
            if at == "/trial/die":
                trial.die(tmp, form["down"][0])
            return "Nothing at this address takes a press."

        serve.run(SKILL, PORT, lambda: "home", recheck=1, raw=files.raw,
                  **table.riding(route=old_route, take=old_take, hears=lambda: files.files("")))


class Browser(unittest.TestCase):
    """The page itself, in each engine: one run, then each check read."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.mkdtemp(prefix="files-page-test-")
        try:
            with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", tmp], PORT, tmp):
                r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "PICKED": PICKED})
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


if __name__ == "__main__":
    if SERVING:
        serving(sys.argv[sys.argv.index("serve") + 1])
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
