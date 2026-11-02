#!/usr/bin/env python3
"""walk-shots-page.py — a session's Screenshots tab: every screenshot its walk keeps, in order.

A walker saves each check's screenshots beside the page's text, in its
own folder: walk/<area>/<section>/<journey>/<number>.png, the number its
checklist's # column, like 14. A check saved more than once ends each
save -1, -2, and on. Its time is the file's own. The tab shows the
session's own walk/ alone. A walker clears its walk/ before it walks a
journey, so the tab holds that journey alone.

The rail names each journey by its file's title, then holds one box per
screenshot, one under the other, in walked order, by time, each reading
its file's name: 19, or 40-1, 40-2. It is as wide as the widest name a
walk makes, 190-21. The box in view wears an outline. A screenshot the
lead's case names under its Issues, the case written after it, wears red,
the page's only colour. Back, Play, Next and Speed walk them; left and
right step, space plays. The screenshot fills the width beside the rail,
its shape kept, and a taller one scrolls down, from its top on each new
one. On my phone held upright, it takes three quarters of the glass under
the top rail, and the journeys the rest, each scrolling on its own. Its
name and place show in the top rail.

The lead's cases are .claude/state/walk-case/<walker>-….md, outside every
session's folder. The lead is walk.json's "main".

1100 imports this file for render, key, answer, tab and heard: the tab
shows once a session holds a screenshot, and never waits on me. Only try
runs a server.

  walk-shots-page.py try FILE [--port 1113]   the tab, drawn from a fixture file alone

A fixture holds nn, tag and shots, each {j, journey, name, time, at, file,
rep}: j its folder under walk/, journey that journey's title, name the
file's without .png, file an absolute path.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

WALK = "walk"
CASES = os.path.join(registry.ROOT, ".claude", "state", "walk-case")
SHOT = re.compile(r"\d+(?:-[\w-]+)?\.png")
# A screenshot a case names, its path under the walker's walk/ folder.
NAMED = re.compile(r"[\w-]+/[\w-]+/[\w-]+/\d+(?:-[\w-]+)?\.png")
SPEEDS = [1, 1.5, 2, 3]
BASE = 1500


# ---- what the walk left -----------------------------------------------------------

def read(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def sources(nn: str) -> list:
    """The walk session NN's tab draws, as [(walker, its walk folder, its
    main)], or [] with none."""
    mine = registry.folder(nn)
    if not os.path.isdir(os.path.join(mine, WALK)):
        return []
    return [(nn, os.path.join(mine, WALK), read(os.path.join(mine, "walk.json")).get("main", ""))]


def reported(walker: str) -> dict:
    """Each screenshot the cases about this walker name under Issues, with
    the newest such case's time: a case older than a screenshot judged an
    earlier pass, and dots nothing."""
    out = {}
    for name in registry.listing(CASES):
        if not (name.startswith(f"{walker}-") and name.endswith(".md")):
            continue
        path = os.path.join(CASES, name)
        try:
            at = os.path.getmtime(path)
            with open(path) as f:
                text = f.read()
        except OSError:
            continue
        for part in re.split(r"(?m)^## ", text):
            if part.startswith("Issues"):
                for shot in NAMED.findall(part):
                    out[shot] = max(at, out.get(shot, 0))
    return out


def title(area: str, section: str, journey: str) -> str:
    """A journey's title, its file's first line, walks/<area>/<section>/<journey>.md.
    No such file, its folder's name."""
    try:
        with open(os.path.join(registry.ROOT, "walks", area, section, journey + ".md")) as f:
            first = f.readline()
    except OSError:
        first = ""
    return first[2:].strip() if first.startswith("# ") else journey.replace("-", " ").capitalize()


def shots(nn: str) -> list:
    """Every screenshot session NN's tab draws, journey by journey, each
    journey's in walked order, journeys by their first screenshot."""
    out = []
    for walker, base, main in sources(nn):
        dots = reported(walker) if main else {}
        for here in glob.glob(os.path.join(base, "*", "*", "*", "")):
            j = os.path.relpath(here, base)
            journey, got = title(*j.split(os.sep)), []
            for name in registry.listing(here):
                if SHOT.fullmatch(name):
                    file = os.path.join(here, name)
                    try:
                        at = os.path.getmtime(file)
                    except OSError:
                        continue
                    got.append({"j": j, "journey": journey, "name": name[:-4],
                                "time": time.strftime("%H:%M:%S", time.localtime(at)),
                                "at": at, "file": file,
                                "rep": dots.get(os.path.relpath(file, base), 0) > at})
            got.sort(key=lambda s: (s["at"], s["file"]))
            if got:
                out.append(got)
    out.sort(key=lambda g: g[0]["at"])
    return [s for g in out for s in g]


def world(nn: str) -> dict:
    """Everything the tab draws for session NN, in a fixture's shape."""
    return {"nn": nn, "tag": plans.tag(nn, plans.owners(registry.entries())), "shots": shots(nn)}


def key(nn: str) -> str:
    """What the tab reloads on: every screenshot's name, and every case
    file's state."""
    words = []
    for walker, base, main in sources(nn):
        for root, _, names in os.walk(base):
            words += [os.path.join(root, n) for n in sorted(names) if n.endswith(".png")]
        for name in registry.listing(CASES) if main else []:
            if not name.startswith(f"{walker}-"):
                continue
            try:
                words.append(f"{name}:{os.path.getmtime(os.path.join(CASES, name))}")
            except OSError:
                pass
    return hashlib.sha1("\0".join(words).encode()).hexdigest()[:12]


# ---- the page -----------------------------------------------------------------------

# The prototype's own rules, after the shell's: screenshots-tab g5/v1.
CSS = """<style>
  /* The journeys' rail: as wide as the widest name a walk makes, 190-21,
     six characters, then the box's padding and its own. A journey's title
     wraps to it, a word too long breaking where it must. Each box borrows
     the clarify page's number rail, nav.nums. */
  body:has(> header.top) > aside { width:calc(6ch + 32px); }
  .ws-j { margin:14px 0 8px; text-transform:none; letter-spacing:0; overflow-wrap:anywhere; }
  .ws-j:first-child { margin-top:0; }
  .tab.ws-row, .tab.ws-row:hover, .tab.ws-row.on { display:block; margin:0 0 6px; padding:3px 6px;
    text-align:center; font-weight:700; border-radius:4px;
    background:var(--c, var(--grey)); color:var(--text); }
  .tab.ws-row.on { outline:2px solid var(--text); outline-offset:1px; }
  /* The screenshot fills main's width, its shape kept, and a taller one
     scrolls down inside main. */
  body:has(> header.top) > main { display:flex; overflow:hidden; padding:8px; }
  .ws-view { flex:1; min-width:0; min-height:0; overflow-y:auto; }
  .ws-shot { display:block; width:100%; height:auto; border:1px solid var(--line); border-radius:5px; }
  /* A touch screen: each box a fingertip tall. */
  @media (hover:none) and (pointer:coarse) {
    .tab.ws-row, .tab.ws-row:hover, .tab.ws-row.on { padding:0 6px; line-height:44px; }
  }
  /* My phone, upright: the screenshot takes three quarters of the glass
     under the top rail, and the journeys the rest, each scrolling on its
     own: shots-upright g1/v1's look 2. */
  @media (hover:none) and (pointer:coarse) and (orientation:portrait) {
    body:has(> header.top) { grid-template-columns:minmax(0, 1fr); grid-template-rows:auto minmax(0, 3fr) minmax(0, 1fr); }
    body:has(> header.top) > main { grid-column:1 / -1; grid-row:2; }
    body:has(> header.top) > aside { grid-column:1 / -1; grid-row:3; width:auto; border-right:0;
      border-top:1px solid var(--line); }
  }
</style>"""

SCRIPT = r"""<script>
const S = %DATA%, SPEEDS = %SPEEDS%, BASE = %BASE%;
let at = 0, playing = 0, speed = 0, timer = 0;
const last = S.length - 1;
const $ = id => document.getElementById(id);
const view = $('view'), shot = $('shot');
function rail() {
  let h = '';
  S.forEach((s, i) => {
    const prev = S[i - 1];
    if (!prev || prev.j !== s.j) h += `<h2 class="ws-j">${s.journey}</h2>`;
    h += `<div class="tab ws-row" data-i="${i}" onclick="go(${i})"`
       + (s.rep ? ' style="--c:var(--red)"' : '') + `>${s.name}</div>`;
  });
  $('rail').innerHTML = h;
}
function show() {
  const s = S[at];
  document.querySelectorAll('.ws-row').forEach(r => {
    const on = +r.dataset.i === at;
    r.classList.toggle('on', on);
    if (on) r.scrollIntoView({block: 'nearest'});
  });
  // A new screenshot starts at its top.
  if (shot.dataset.at !== String(at)) { shot.dataset.at = at; view.scrollTop = 0; }
  shot.src = '%PIC%/' + at;
  shot.alt = s.name;
  $('mid').textContent = `${s.name} · ${at + 1} of ${S.length}`;
  $('back').disabled = at === 0;
  $('next').disabled = at === last;
  $('play').textContent = playing ? 'Pause' : 'Play';
  $('speed').textContent = SPEEDS[speed] + '×';
  keep();
}
// My place, my speed and whether it plays outlive a reload, as a new
// screenshot brings one. The place is kept by the screenshot itself, its
// journey, name and time, never by where it sat in the list.
const KEPT = 'shots:' + location.pathname, idOf = s => s.j + '|' + s.name + '|' + s.time;
const keep = () => sessionStorage.setItem(KEPT, JSON.stringify({id: idOf(S[at]), playing, speed}));
function go(i) { at = Math.max(0, Math.min(i, last)); show(); }
function stop() { playing = 0; clearInterval(timer); show(); }
function play() {
  if (playing) return stop();
  playing = 1; clearInterval(timer);
  timer = setInterval(() => { if (at >= last) return stop(); at++; show(); }, BASE / SPEEDS[speed]);
  show();
}
function faster() { speed = (speed + 1) % SPEEDS.length; if (playing) { playing = 0; play(); } else show(); }
addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') go(at + 1);
  if (e.key === 'ArrowLeft') go(at - 1);
  if (e.key === ' ') { e.preventDefault(); play(); }
});
let was = null;
try { was = JSON.parse(sessionStorage.getItem(KEPT) || 'null'); } catch (e) {}
if (was) { at = Math.max(0, S.findIndex(s => idOf(s) === was.id)); speed = SPEEDS[was.speed] ? was.speed : 0; }
rail(); show();
if (was && was.playing) play();
</script>"""


def draw(d: dict, tail: str = "") -> str:
    """The tab, from what world() reads or what a fixture holds. `tail` is its watch."""
    nn, s = d["nn"], d["shots"]
    if not s:
        top = page.head("shots", d["tag"], "0 of 0")
        return page.render(f"{nn}-shots", [("", page.blank("No screenshot yet") + tail)],
                           top + "<aside></aside>\n", refresh=0)
    acts = ('<span class="group"><button class="btn" id="back" onclick="go(at - 1)">Back</button>'
            '<button class="btn" id="play" onclick="play()">Play</button>'
            '<button class="btn" id="next" onclick="go(at + 1)">Next</button>'
            '<button class="btn" id="speed" title="Speed" onclick="faster()">1×</button></span>')
    top = page.head("shots", d["tag"], '<span id="mid"></span>', acts)
    body = '<div class="ws-view" id="view"><img class="ws-shot" id="shot" alt=""></div>'
    data = [{k: v for k, v in x.items() if k != "file"} for x in s]
    script = (SCRIPT.replace("%DATA%", json.dumps(data).replace("</", "<\\/"))
              .replace("%SPEEDS%", json.dumps(SPEEDS)).replace("%BASE%", str(BASE))
              .replace("%PIC%", serve.address("shots", nn) + "/pic"))
    return page.render(f"{nn}-shots", [("", CSS + body + tail + script)],
                       top + '<aside id="rail"></aside>\n', refresh=0)


def render(nn: str) -> str:
    return draw(world(nn), page.watch(key(nn)))


def picture(d: dict, k: str):
    """Screenshot K of the tab, as its bytes and their type."""
    s = d["shots"]
    if not k.isdigit() or int(k) >= len(s):
        return b"", "text/plain; charset=utf-8"
    try:
        with open(s[int(k)]["file"], "rb") as f:
            return f.read(), "image/png"
    except OSError:
        return b"", "text/plain; charset=utf-8"


def answer(nn: str, rest: str):
    """The tab, or one screenshot: /pic/K."""
    if not rest:
        return render(nn)
    if m := re.fullmatch(r"/pic/(\d+)", rest):
        return picture(world(nn), m.group(1))
    return None


def tab(nn: str):
    """Session NN's tab, as (its line, the file it began with), or None
    with no screenshot. Its line is the newest journey and the count."""
    s = shots(nn)
    if not s:
        return None
    first = min(s, key=lambda x: os.path.getmtime(x["file"]) if os.path.exists(x["file"]) else 0)
    return f"{s[-1]['journey']} · {len(s)}", first["file"]


def heard() -> list:
    """What 1100 hears for every session's tab: each walk folder, down to
    its journeys, and the cases folder once a walk names its main."""
    out, mains = [], False
    for nn in registry.listing(registry.WORK):
        if not re.fullmatch(r"\d{2}", nn):
            continue
        for _, base, main in sources(nn):
            out.append(base)
            for section in registry.listing(base):
                out.append(os.path.join(base, section))
                out += [os.path.join(base, section, j) for j in registry.listing(os.path.join(base, section))]
            mains = mains or bool(main)
    return out + [CASES] if mains else out


# ---- tried alone ----------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    tried = sub.add_parser("try")
    tried.add_argument("file")
    tried.add_argument("--port", type=int, default=1113)
    args = ap.parse_args()
    path = os.path.abspath(args.file)
    load, mark = serve.fixture(path)

    def route(p: str):
        bare = p.partition("?")[0]
        if m := re.search(r"/pic/(\d+)$", bare):
            return picture(load(), m.group(1))
        return None

    serve.run(f"walk-shots-page-{args.port % 100:02d}", args.port, lambda: draw(load(), page.watch(mark())),
              route=route, keyof=mark, hears=lambda: [path])


if __name__ == "__main__":
    main()
