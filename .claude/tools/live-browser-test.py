#!/usr/bin/env python3
"""Check what .claude/pages/scripts/live.js promises, in WebKit and in Chromium.

A server on this session's port, 11NN, draws one made-up page on the
contract, from a state file this test rewrites. It runs as a program of
its own, so the test can kill it mid-word and start it again. Each engine
opens the page and checks, in order:

  A changed page, put in place, equals the page drawn fresh.
  I type in a box, and every part of the page changes: my words, my
  cursor, my place and what I opened hold, and the page loaded once.
  My unsent words return after a reload, and after the server died. They
  belong to their session, never to its number.
  The server silent for five seconds, the page says so in one line, and
  goes on once it is back, with no reload.
  A hidden page asks nothing. Shown again, it is current within a second.
  The page reloads once when its own code changed, after I stop typing,
  and my words come back.
  Words I edit in place, a contenteditable's, keep my words and my cursor
  through a change. Untouched under my cursor, they take the server's
  words once it leaves, and so does a field.
  A press shows it was taken, lands once across a short silence, and a
  refused one says why along the foot.

  live-browser-test.py [NN]

NN is this session's number, 02 when none is given.
"""

import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402

NN = sys.argv[1] if len(sys.argv) > 1 else "02"
PORT = 1100 + int(NN) + serve.ports.SHIFT
SKILL = f"live-browser-test-{NN}"
SERVING = len(sys.argv) > 3 and sys.argv[2] == "serve"
TMP = sys.argv[3] if SERVING else tempfile.mkdtemp(prefix="live-browser-test-")
STATE, ACTED = (os.path.join(TMP, n) for n in ("state.json", "acted.log"))
PAGE = serve.address("trial", NN)

# The page's own script. It touches the screen only from live.ready: it
# adds one node of its own, and sends each button's press.
OWN = """<script>
window.CODE = %d;
live.ready(() => {
  const made = document.createElement('span');
  made.id = 'made';
  made.textContent = 'Made by the page.';
  document.getElementById('list').after(made);
  document.addEventListener('click', e => {
    const b = e.target.closest('#mark, #refuse');
    if (b) live.pressed(b, {act: b.id});
  });
});
live.drawn(() => { window.DRAWN = (window.DRAWN || 0) + 1; });
</script>"""


def draw(nn: str) -> str:
    with open(STATE) as f:
        s = json.load(f)
    items = "".join(f'<li id="i-{page.esc(i["k"])}" class="{page.esc(i["c"])}">{page.esc(i["t"])}</li>' for i in s["items"])
    return page.render(f"{nn}-trial", [("", (
        live.watch(s["session"]) + f'<style>#title {{ color:{s["color"]}; }}</style>'
        f'<h1 id="title">{page.esc(s["title"])}</h1><ul id="list">{items}</ul>'
        f'<details id="more"><summary>More</summary><p>{page.esc(s["more"])}</p></details>'
        f'<p id="word" contenteditable="true">{page.esc(s["word"])}</p>'
        f'<div id="tall" style="height:{int(s["tall"])}px">{page.esc(s["spacer"])}</div>'
        f'<textarea id="box" rows="3">{page.esc(s["saved"])}</textarea><input id="line" value="{page.esc(s["line"])}">'
        '<button class="btn" id="mark">Mark</button><button class="btn" id="refuse">Refuse</button>'
        f'<p id="foot">{page.esc(s["foot"])}</p>'
        f'<script type="application/json" id="data">{json.dumps(s["data"])}</script>' + OWN % int(s["code"])))], refresh=0)


def pressed(nn: str, form: dict) -> str:
    if (form.get("act") or [""])[0] != "mark":
        return "This press is refused. Nothing was done."
    with open(ACTED, "a") as f:
        f.write("mark\n")
    return ""


def old_route(path: str):
    if path.partition("?")[0] == "/trial/acted":
        try:
            with open(ACTED) as f:
                return json.dumps(len(f.readlines())).encode(), "application/json"
        except OSError:
            return b"0", "application/json"
    return b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404


def old_take(form: dict, path: str) -> str:
    """The test's own two presses: the state written whole, and the server
    dying at once, for the seconds the press names."""
    if path == "/trial/set":
        hidden = STATE + ".tmp"
        with open(hidden, "w") as f:
            f.write(form["state"][0])
        os.replace(hidden, STATE)
        return ""
    if path == "/trial/die":
        trial.die(TMP, form["down"][0])
    return "Nothing at this address takes a press."


if SERVING:
    table = live.Table([live.Page(serve.address("trial", r"(\d{2})"), draw, files=lambda nn: [STATE], take=pressed)])
    serve.run(SKILL, PORT, lambda: "home", recheck=1,
              **table.riding(route=old_route, take=old_take, hears=lambda: []))
    sys.exit(0)


# Every check, in each engine. Each line it prints is one check: its name,
# whether it held, and what was seen.
BROWSERS = trial.SERVER + r"""
const url = base + process.env.LIVE_PAGE;
const set = s => post('/trial/set', {state: JSON.stringify(s)});
const acted = async () => (await fetch(base + '/trial/acted')).json();
const S1 ={session: 's-one', code: 1, color: 'rgb(230, 232, 238)', title: 'First title', tall: 1500, spacer: 'Spacer one.',
            items: [{k: 'a', c: 'x', t: 'Item A'}, {k: 'b', c: 'x', t: 'Item B'}, {k: 'c', c: 'x', t: 'Item C'}],
            more: 'More, first.', word: 'alpha', saved: '', line: 'line one', foot: 'Foot one.', data: {n: 1}};
const S2 = {...S1, color: 'rgb(74, 222, 128)', title: 'Second title', tall: 1800, spacer: 'Spacer two.',
            items: [{k: 'd', c: 'x', t: 'Item D'}, {k: 'c', c: 'y', t: 'Item C, changed'}, {k: 'a', c: 'x', t: 'Item A'}],
            more: 'More, second.', word: 'beta', saved: 'Words 1100 drew.', line: 'line two', foot: 'Foot two.', data: {n: 2}};
const S3 = {...S2, title: 'Third title', tall: 900, items: [{k: 'a', c: 'z w', t: 'Item A, alone'}], more: 'More, third.',
            word: 'gamma', line: '', foot: 'Foot three.', data: {n: 3}};
// A page as it stands, node by node: what a fresh draw and a changed one must agree on.
const snap = p => p.evaluate(() => {
  const walk = n => n.nodeType === 3 ? n.data : n.nodeType !== 1 ? null
    : [n.tagName, [...n.attributes].filter(a => !['style', 'class', 'data-busy'].includes(a.name)).map(a => a.name + '=' + a.value).sort(),
       [...n.classList].sort(), n.style ? n.style.cssText : '', n.matches('input, textarea') ? n.value : null,
       [...n.childNodes].map(walk).filter(x => x !== null)];
  return JSON.stringify(walk(document.querySelector('main')));
});
const title = (p, t, ms = 5000) => p.waitForFunction(t => document.getElementById('title').textContent === t
  && !('busy' in document.getElementById('watch').dataset), t, {timeout: ms});
const said = (name, held, seen) => console.log(JSON.stringify({engine: ENGINE, name, held: !!held, seen}));
let ENGINE = '';

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 900, height: 600}});
    const open = async () => {
      const p = await context.newPage();
      p.loads = 0;
      p.on('request', r => { if (r.isNavigationRequest() && r.frame() === p.mainFrame()) p.loads++; });
      return p;
    };

    // A changed page, put in place, equals the page drawn fresh.
    await set(S1);
    const b = await open(), c = await open();
    await b.goto(url);
    let same = [];
    for (const s of [S2, S3, S1, S3]) {
      await set(s);
      await title(b, s.title);
      await c.goto(url);
      same.push(await snap(b) === await snap(c));
    }
    said('fresh', same.every(Boolean) && b.loads === 1, `${same.filter(Boolean).length} of ${same.length} changed pages equal the fresh draw, in ${b.loads} load`);
    await b.close();
    await c.close();

    // I type in a box, and every part of the page changes.
    await set(S1);
    const a = await open();
    await a.goto(url);
    await a.click('#more summary');
    await a.locator('#box').scrollIntoViewIfNeeded();
    await a.click('#box');
    await a.keyboard.type('hello wor');
    const look = () => a.evaluate(() => {
      const box = document.getElementById('box'), $ = id => document.getElementById(id);
      return {title: $('title').textContent, items: [...document.querySelectorAll('#list li')].map(li => li.id + ':' + li.className + ':' + li.textContent).join('|'),
              more: $('more').querySelector('p').textContent, foot: $('foot').textContent, color: getComputedStyle($('title')).color,
              line: $('line').value, box: box.value, active: document.activeElement.id, at: box.selectionStart,
              top: Math.round(box.getBoundingClientRect().top), open: $('more').open, made: !!$('made'),
              data: JSON.parse($('data').textContent).n, tall: $('tall').offsetHeight, drawn: window.DRAWN || 0};
    });
    const was = await look();
    let began = Date.now();
    await set(S2);
    await title(a, S2.title);
    const took = Date.now() - began;
    const now = await look();
    await a.keyboard.type('ld');
    const typed = (await look()).box;
    const changed = now.items === 'i-d:x:Item D|i-c:y:Item C, changed|i-a:x:Item A' && now.more === S2.more && now.foot === S2.foot
      && now.color === S2.color && now.line === 'line two' && now.data === 2 && now.tall === 1800 && now.drawn >= 1;
    const held = now.box === 'hello wor' && now.active === 'box' && now.at === was.at && Math.abs(now.top - was.top) <= 2
      && now.open && now.made && typed === 'hello world';
    said('typing', changed && held && took < 1500 && a.loads === 1,
         `every part changed ${took} ms on: ${changed}; my words "${typed}", cursor at ${now.at} of ${was.at}, box ${now.top - was.top} px off, `
         + `details ${now.open ? 'open' : 'shut'}, the page's own node ${now.made ? 'kept' : 'lost'}, ${a.loads} load`);

    // My unsent words return after a reload, and after the server died. They belong to their session.
    await a.reload();
    const reloaded = (await look()).box;
    await die(1);
    await a.reload().catch(() => {});
    await up();
    await a.goto(url);
    const crashed = (await look()).box;
    await set({...S2, session: 's-two'});
    await a.waitForFunction(() => document.getElementById('watch').dataset.session === 's-two', null, {timeout: 5000});
    await wait(300);
    const other = (await look()).box;
    await a.reload();
    const others = (await look()).box;
    await set(S2);
    await a.waitForFunction(() => document.getElementById('watch').dataset.session === 's-one', null, {timeout: 5000});
    await wait(300);
    const back = (await look()).box;
    said('words', reloaded === 'hello world' && crashed === 'hello world' && other === S2.saved && others === S2.saved && back === 'hello world',
         `after a reload "${reloaded}", after the server died "${crashed}", under another session "${other}" then "${others}", back under their own "${back}"`);

    // The server silent for five seconds, the page says so in one line, and goes on, with no reload.
    await a.click('#box');
    const loads = a.loads;
    const line = () => a.evaluate(() => { const p = document.getElementById('away'); return p && !p.hidden ? p.textContent : ''; });
    began = Date.now();
    await die(8);
    await wait(3500);
    const early = await line();
    await a.waitForFunction(() => { const p = document.getElementById('away'); return p && !p.hidden; }, null, {timeout: 9000});
    const shown = Date.now() - began, words = await line();
    await up();
    await a.waitForFunction(() => { const p = document.getElementById('away'); return p && p.hidden; }, null, {timeout: 8000});
    await set({...S2, title: 'After the silence'});
    await title(a, 'After the silence');
    const after = await look();
    said('silent', !early && shown >= 4500 && /is not answering/.test(words) && a.loads === loads && after.box === 'hello world' && after.active === 'box',
         `the line showed ${shown} ms on: "${words}"; it went once the server was back, ${a.loads - loads} reloads, my words "${after.box}"`);

    // A hidden page asks nothing. Shown again, it is current within a second.
    const hide = hidden => a.evaluate(hidden => {
      Object.defineProperty(document, 'hidden', {configurable: true, get: () => hidden});
      document.dispatchEvent(new Event('visibilitychange'));
    }, hidden);
    await hide(true);
    await wait(300);
    await set({...S2, title: 'While hidden'});
    await wait(1500);
    const unseen = (await look()).title;
    began = Date.now();
    await hide(false);
    await title(a, 'While hidden');
    const current = Date.now() - began;
    said('hidden', unseen === 'After the silence' && current < 1000, `hidden, it kept "${unseen}"; shown again, it was current ${current} ms on`);

    // The page reloads once when its own code changed, after I stop typing, and my words come back.
    await a.click('#box');
    const before = a.loads;
    await set({...S2, title: 'While hidden', code: 2});
    for (let i = 0; i < 10; i++) { await a.keyboard.type('x'); await wait(400); }
    const during = a.loads - before, mine = (await look()).box;
    await a.waitForFunction(() => window.CODE === 2, null, {timeout: 12000});
    await wait(4000);
    const kept = (await look()).box;
    said('code', during === 0 && a.loads === before + 1 && kept === mine && /x{10}$/.test(kept),
         `${during} reloads while I typed, ${a.loads - before} once I stopped, and my words came back: ${kept === mine}`);

    // Words I edit in place keep my words and my cursor through a change.
    // Untouched under my cursor, they take the server's words once it
    // leaves, and so does a field.
    {
    await set(S1);
    const e = await open();
    await e.goto(url);
    const word = () => e.evaluate(() => { const w = document.getElementById('word'), s = getSelection();
      return {text: w.textContent, active: document.activeElement.id, at: s.focusOffset, inside: w.contains(s.focusNode),
              line: document.getElementById('line').value}; });
    const into = id => e.evaluate(id => { const w = document.getElementById(id), r = document.createRange();
      w.focus(); r.selectNodeContents(w); r.collapse(false); getSelection().removeAllRanges(); getSelection().addRange(r); }, id);
    await into('word');
    await e.keyboard.type('XY');
    const mine = await word();
    await set(S2);
    await title(e, S2.title);
    const through = await word();
    await e.keyboard.type('Z');
    const more = await word();
    await e.reload();
    await into('word');
    await set({...S2, word: 'delta', title: 'Fourth title'});
    await title(e, 'Fourth title');
    const under = await word();
    await e.click('#title');
    await e.waitForFunction(() => document.getElementById('word').textContent === 'delta', null, {timeout: 4000}).catch(() => {});
    const left = await word();
    await set({...S2, word: 'epsilon', title: 'Fifth title'});
    await title(e, 'Fifth title');
    const apart = await word();
    await e.click('#line');
    await set({...S2, word: 'epsilon', line: 'line three', title: 'Sixth title'});
    await title(e, 'Sixth title');
    const field = await word();
    await e.click('#title');
    await e.waitForFunction(() => document.getElementById('line').value === 'line three', null, {timeout: 4000}).catch(() => {});
    const after = await word();
    said('editing', mine.text === 'alphaXY' && through.text === 'alphaXY' && through.active === 'word' && through.inside && through.at === mine.at
         && more.text === 'alphaXYZ' && under.text === 'beta' && under.active === 'word' && left.text === 'delta' && apart.text === 'epsilon'
         && field.line === 'line two' && field.active === 'line' && after.line === 'line three' && e.loads === 2,
         `through a change my words read "${through.text}", my cursor at ${through.at} of ${mine.at}, then "${more.text}"; untouched under my cursor `
         + `they stayed "${under.text}", and read "${left.text}" once it left, then "${apart.text}"; a field stayed "${field.line}", then read "${after.line}"`);
    await e.close();
    }

    // A press shows it was taken, lands once across a short silence, and a refused one says why.
    let count = await acted();
    await a.click('#mark');
    const taken = await a.evaluate(() => document.getElementById('mark').disabled || document.getElementById('mark').classList.contains('done'));
    await a.waitForFunction(() => document.getElementById('mark').classList.contains('done'), null, {timeout: 5000});
    const once = await acted() - count;
    await a.click('#refuse');
    await a.waitForFunction(() => { const p = document.getElementById('refusal'); return p && !p.hidden; }, null, {timeout: 5000});
    const why = await a.evaluate(() => document.getElementById('refusal').textContent);
    const red = await a.evaluate(() => document.getElementById('refuse').classList.contains('gone'));
    await wait(1600);
    count = await acted();
    await die(0.3);
    await a.click('#mark');
    await up();
    await a.waitForFunction(() => document.getElementById('mark').classList.contains('done'), null, {timeout: 8000});
    const across = await acted() - count;
    said('press', taken && once === 1 && /refused/.test(why) && red && across === 1,
         `a press was taken at once and acted ${once} time; a refused one said "${why}"; one sent across a silence acted ${across} time`);

    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

# What each check says, by its name.
NAMES = {"fresh": "A changed page, put in place, equals the page drawn fresh",
         "typing": "I typed in a box while every part changed",
         "words": "My unsent words",
         "silent": "The server silent",
         "hidden": "A hidden page",
         "code": "The page's own code changed",
         "editing": "Words I edit in place",
         "press": "A press"}


with open(STATE, "w") as f:
    f.write("{}")
try:
    with trial.kept_up([sys.executable, os.path.abspath(__file__), NN, "serve", TMP], PORT, TMP):
        r = trial.browsers(BROWSERS, {"TRIAL_BASE": f"http://127.0.0.1:{PORT}", "LIVE_PAGE": PAGE})
finally:
    with open(os.path.join(TMP, "server.log"), errors="replace") as f:
        logged = f.read()
    shutil.rmtree(os.path.dirname(serve.pidfile(SKILL)), ignore_errors=True)
    shutil.rmtree(TMP, ignore_errors=True)

seen = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
for engine in missing:
    print(f"FAILED: {engine} was not run: its build is not installed.")
for s in seen:
    print(("" if s["held"] else "FAILED: ") + f"{NAMES[s['name']]}, in {s['engine']}: {s['seen']}.")
ran = {s["engine"] for s in seen}
whole = ran == {"webkit", "chromium"} and all(len([s for s in seen if s["engine"] == e]) == len(NAMES) for e in ran)
if r.returncode or not whole:
    print(f"FAILED: the browsers ended early. {r.stderr.strip()[-1500:]}")
    if "Traceback" in logged:
        print(logged.strip()[-1500:])
sys.exit(0 if whole and not r.returncode and all(s["held"] for s in seen) else 1)
