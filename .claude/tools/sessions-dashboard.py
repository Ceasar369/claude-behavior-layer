#!/usr/bin/env python3
"""sessions-dashboard.py — 1100, the one page server.

One page, open all day. Band 00 belongs to no session, and 1100 is the
behaviour layer's own front door: every page is drawn here. A session may
serve its own copy on 11NN to try new code: session 08 tries 1100 on 1108.

Home is the workstation: what waits on me, and the team it belongs to.
workstation.py draws it. The pages it opens for a session are 1100's own:

  /p/clarify/NN     a wave, clarify-page.py's
  /p/assistant/NN   a plan, assistant-page.py's
  /p/launch/NN      a launch, launch-page.py's
  /p/handover/NN    a handover, handover-page.py's
  /p/jury/NN        a jury's plan, then its results, jury-page.py's
  /p/walk/NN        a walk's checklist, walk-list-page.py's
  /p/shots/NN       a walk's screenshots, walk-shots-page.py's, and each one
  /p/transcript/NN  a session's whole transcript, transcript-page.py's,
                    and the parts it asks for as I read it; the advisor's
                    wears its panel, advisor-page.py's

A prototype's page is 1100's own, prototype-page.py's, at /proto/; every
other address under /proto/ 1100 passes through whole to 1400. Every page
is on the contract, lib/live.py's: each page tool states its LIVE, and
TABLE gathers them. Each page's posts come back to its own address, and
its own take answers them. An address named nowhere here answers not
found, and a post there takes nothing.

The rail opens more pages, each at its own address.

  /p/launch/00  my own launch page, behind Launch. launch-page.py draws it.
  /agenda  my agenda, as one chart. agenda-page.py draws it, and takes
           Start.
  /system  usage, the outsource engine, defaults, thresholds, the rail's
           size, band 00, other ports and the memory guard. system-page.py
           draws it, and takes a finding's button.
  /files   every session's folder as a tree, and the file I pick, at
           /tree, /text and /raw. files-page.py draws it.
  /skills  every skill, by family. skills-page.py draws it.
  /library the library as a book, read from library/ each draw, each item
           wearing its review mark. library-page.py draws it, and takes a
           review button's press.

/apple-touch-icon.png is 1100's icon on my iPhone's home screen, and
/manifest.webmanifest names it there as an app of its own, by the
project's name. /sw.js is its service worker, which shows the buzz:
lib/push.py's, posted to /push once I allow it, and sent once a session
is done, from the colour watch below.

/project names the project this 1100 serves, by name and folder. One
project runs at a time: while another project's 1100 answers, band, stop
and restart refuse, naming it. lib/project.py holds both halves.

1100 also types drive.RESUME into a driving assistant capped on its own
account, once the cap resets: lib/finish.py's watch, on a thread of its
own for as long as 1100 runs. On another, a session whose number turns
from green to red buzzes my phone, and an assistant is handed its
mission's sessions waiting on me, as assistant-page.py's auto-send rules:
lib/page.py's colour watch, reddened. On another, it asks every account
for its two windows: lib/finish.py's asking. On another, it reads iTerm's
pane list while pages ask for it, so no draw ever waits on iTerm:
lib/panes.py's freshen. Each page tool's own readers, READERS, run on
threads of their own too, as System's ports and database.

Nothing is stored here. Every request reads what it shows.

The shell, the colours and the server are shared. See .claude/lib/.
It keeps the page rules atop .claude/lib/page.py.

  sessions-dashboard.py serve  [--port 1100]
  sessions-dashboard.py band
  sessions-dashboard.py status
  sessions-dashboard.py stop      band 00 and 1100, never a session's
  sessions-dashboard.py check     the code on disk draws, and its scripts parse, or it raises
  sessions-dashboard.py restart   1100 alone, on the code on disk
"""

import argparse
import ast
import contextlib
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import context  # noqa: E402
import engines  # noqa: E402
import finish  # noqa: E402
import live  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import push  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import show  # noqa: E402
import appwake  # noqa: E402
import trial  # noqa: E402
import wake  # noqa: E402

SKILL = "sessions-dashboard"
PORT = serve.PORT
HERE =os.path.dirname(os.path.abspath(__file__))

# Home, and every view, through it.
workstation = page.tool("workstation")
views = workstation.views
skills = page.tool("skills-page")
library = page.tool("library-page")
agenda = page.tool("agenda-page")
transcript = page.tool("transcript-page")

# The one command that starts every band-00 server, the project's own.
# It goes through a login shell, so it finds what my shell finds, which a
# hook's own PATH does not carry. A project naming none runs 1100 alone.
DEV = ["/bin/zsh", "-lc", project.COMMAND] if project.COMMAND else None

# ---- System and Files -------------------------------------------------------------

# Each is a page tool of its own: system-page.py and files-page.py. Every
# name another file calls here still answers, from there: tools/app-door.py
# reads System and Files through this file.
system = page.tool("system-page")
files = page.tool("files-page")
BAND, PORTS, DATABASE, LEVELS, PLANS = system.BAND, system.PORTS, system.DATABASE, system.LEVELS, system.PLANS
band_state, seen, other, clock, usage = system.band_state, system.seen, system.other, system.clock, system.usage
engines_seen, findings = system.engines_seen, system.findings
size, count, listed, inside, tree, text, raw = (files.size, files.count, files.listed, files.inside, files.tree,
                                                files.text, files.raw)


def gathered(name: str) -> list:
    """What each page tool states under `name`, one or several: its
    contract, LIVE, or its readers, READERS. A page joining the contract
    states both in its own file, and changes no other."""
    out = []
    for tool in dict.fromkeys([*views.tools.values(), views.assistant, views.advisor, skills, library, agenda,
                               transcript, workstation, system, files]):
        found = getattr(tool, name, None)
        out += found if isinstance(found, (list, tuple)) else [found] if found else []
    return out


# Every page that states a contract, lib/live.py's: every page 1100 draws.
# 1100 asks this table before route(), and every address that is no page
# rides on.
TABLE = live.Table(gathered("LIVE"))


def served() -> live.Table:
    """A fresh table of every page TABLE holds, no picture kept: for the
    gate, whose every draw is drawn now."""
    return live.Table(TABLE.pages)


# Every address the rail opens, for the gate to walk.
RAIL = ["/system", "/files", "/skills", "/library", "/agenda", views.prototypes.BASE]
# Each part a session's transcript asks for as I read it: transcript-page.py's answer().
TRANSCRIPT = re.compile(serve.address("transcript", r"(\d{2})") + r"(/pane|/step/[\w-]+|/pic/\d+/\d+)")
# Each of a walk's screenshots: walk-shots-page.py's answer().
SHOTS = re.compile(serve.address("shots", r"(\d{2})") + r"(/pic/\d+)")
# A session's explanation documents, each one as HTML, and all of them
# saved: explanation-page.py's answer().
EXPLANATION = re.compile(serve.address("explanation", r"(\d{2})") + r"/([a-z0-9-]+\.html|documents\.zip)")
# What an address nothing lives at answers, and a press there.
NOT_FOUND = (b"Nothing lives at this address.\n", "text/plain; charset=utf-8", 404)
# The type data goes as: show's order, the app home's wake line.
JSON = "application/json"
NO_PRESS = "Nothing at this address takes a press."


def view_of(query: str) -> str:
    """The view /show's address names, as ?view=2. None named is view 1."""
    return (urllib.parse.parse_qs(query).get("view") or ["1"])[0]


def keyof(path: str):
    """The key of /show's order, for the view its address names, and of
    /app's wake line, or None for every other address no page holds."""
    try:
        if path.partition("?")[0] == "/show":
            # An app home names itself, so 1100 knows which panels are open now.
            show.asked(view_of(path.partition("?")[2]),
                       (urllib.parse.parse_qs(path.partition("?")[2]).get("home") or [""])[0])
            return show.key(view_of(path.partition("?")[2]))
        if path.partition("?")[0] == "/app":
            return hashlib.sha1(appwake.panel()["line"].encode()).hexdigest()[:12]
        return None
    except Exception:
        live.logged(f"key {path}", f"the key of {path}")
        return None


def either(words) -> str:
    """Words as a choice reads: low, medium or high."""
    words = [str(w) for w in words]
    return ", ".join(words[:-1]) + " or " + words[-1] if len(words) > 1 else "".join(words)


def refused(form: dict) -> str:
    """The one sentence a system setting's bad value is refused with, or ""
    when every value posted would save. Each check is its save's own rule,
    so a valid value saves exactly as before."""
    get = lambda k: form.get(k, [""])[0]
    if "order" in form and accounts.parse(get("order")) is None:
        return f"Order '{get('order')}' is refused. Use only accounts {either(accounts.KNOWN)}."
    if "effort" in form and get("effort") not in panes.EFFORTS:
        return f"Effort '{get('effort')}' is refused. Choose {either(panes.EFFORTS)}."
    if "model" in form and not re.fullmatch(r"[A-Za-z0-9.-]+", get("model")):
        return f"Model '{get('model')}' is refused. A model's name holds only letters, digits, dots and dashes."
    if "own" in form:
        a, family, effort = get("own"), get("own_model"), get("own_effort")
        if a not in accounts.KNOWN:
            return f"Account '{a}' is refused. Choose {either(accounts.KNOWN)}."
        if accounts.settings(a) is None:
            return f"claude-{a}'s settings.json is not a JSON object, so nothing was saved."
        families = [f for f, _ in models.families()]
        if family and family not in families:
            return f"Model '{family}' is refused for claude-{a}. Choose {either(families)}."
        if effort and effort not in accounts.SAVED:
            return f"Effort '{effort}' is refused for claude-{a}. Choose {either(accounts.SAVED)}."
        if effort and not accounts.own(a)["model"]:
            return f"claude-{a} has no model saved. Pick its model first, then its effort."
    if "engine" in form:
        seen, e = engines_seen(), get("engine")
        if e not in seen:
            return (f"Engine '{e}' is refused. Choose {either(seen)}." if seen
                    else f"Engine '{e}' is refused. No outsource engine is set up.")
        offered, model, effort = seen[e]["models"], get("engine_model"), get("engine_effort")
        if model and model not in offered:
            return f"Model '{model}' is refused for {e}. Choose {either(offered) or 'none: its models cannot be read'}."
        target = model or seen[e]["set"]["model"]
        efforts = offered.get(target, ([], ""))[0]
        if effort and effort not in efforts:
            return (f"Effort '{effort}' is refused for {e}'s {target}. Choose {either(efforts)}." if efforts
                    else f"Effort '{effort}' is refused. {e}'s {target} takes no effort.")
    for k, word in (("threshold", "Threshold"), ("wrapup", "Wrap-up")):
        s = get(k).strip()
        if k in form and not (s.isdigit() and 1 <= int(s) <= 99):
            return f"{word} '{get(k)}' is refused. Choose a whole percent from 1 to 99."
    return ""


def app_home(form: dict) -> str:
    """The app home's own posts: whether it holds my cursor, or my Copy
    taking the wake line it shows. lib/appwake.py waits on both."""
    if "held" in form:
        appwake.held(form["held"][0] == "1")
    if "taken" in form:
        appwake.waiting("")
    return ""


def take(form: dict, path: str = "/") -> str:
    """A post to an address no page holds: a phone's buzz handed over, the
    explanation documents saved, the app home's own, or a setting on the
    system page, which posts to /. A setting refused is said. A post
    anywhere else takes nothing."""
    if path == "/push":
        return push.keep(form)
    # Download all, pressed on this Mac: the zip's address, posted to.
    if (e := EXPLANATION.fullmatch(path)) and e.group(2) == "documents.zip":
        return views.explanation.unpacked(e.group(1))
    if path == "/app":
        return app_home(form)
    if path != "/":
        return NO_PRESS
    if why := refused(form):
        return why
    if "order" in form:
        accounts.save(accounts.parse(form["order"][0]))
    if "effort" in form:
        accounts.save_effort(form["effort"][0])
    if "model" in form:
        accounts.save_model(form["model"][0])
    if "own" in form:
        accounts.save_own(form["own"][0], form.get("own_model", [""])[0], form.get("own_effort", [""])[0])
    if "engine" in form:
        engines.save(form["engine"][0], form.get("engine_model", [""])[0], form.get("engine_effort", [""])[0])
    if "threshold" in form:
        context.save("threshold", form["threshold"][0])
    if "wrapup" in form:
        context.save("wrapup", form["wrapup"][0])
    return ""


# ---- my iPhone's icon -----------------------------------------------------------------------

# 1100 on my iPhone's home screen: the project's color filling the square, and
# its glyph, white, centred. A project naming neither gets orange and the
# rocket Launch wears. With no icon tag, iOS asks the site's root for it.
# librsvg draws it.
TOUCH = ('<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">'
         '<rect width="180" height="180" fill="{}"/><g transform="translate(36 36) scale(4.5)" fill="none" '
         'stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{}</g></svg>')


def touch_icon() -> bytes:
    """The icon, 180 by 180, as a PNG."""
    svg = TOUCH.format(project.COLOR, project.GLYPH or page.PATHS["launch"])
    return subprocess.run(["/opt/homebrew/bin/rsvg-convert"], input=svg.encode(),
                          capture_output=True, check=True).stdout


# 1100 as an app of its own on my phone: its name, its icon, and no Safari
# around it. A phone's buzz needs one.
MANIFEST = json.dumps({"name": project.NAME, "short_name": project.NAME, "id": "/", "start_url": "/",
                       "scope": "/", "display": "standalone", "background_color": "#0f1115",
                       "theme_color": "#0f1115",
                       "icons": [{"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}]})


def opened(nn: str) -> str:
    """Home's address that opens session NN's transcript, in its hub."""
    held = registry.entries()
    return "/#{}/transcript:{}".format(next((h for h, members in workstation.teams_of(held, plans.owners(held))
                                            if nn == h or nn in members), nn), nn)


# ---- the server -------------------------------------------------------------------------

def one_list(fn):
    """`fn`, asking the Mac for its process table once per draw, however
    many sessions it shows: wake.once()."""
    def run(*args):
        with wake.once():
            return fn(*args)
    return run


def contained(fn):
    """`fn`, its error kept to the page that raised it. That page shows the
    error's last line, lib/live.py's failed(), so every other page goes on
    being told."""
    def run(*args):
        try:
            return fn(*args)
        except Exception as e:
            line = f"{type(e).__name__}: {e}"
            live.logged(hashlib.sha1(f"{args}{line}".encode()).hexdigest()[:12],
                        f"the draw of {args[0] if args else '/'}")
            return live.failed(line)
    return run


def route(path: str):
    """Home is /. Every page is the table's. Every other address is named
    here, and one named nowhere answers not found."""
    bare, _, query = path.partition("?")
    bare = bare.split("#")[0]
    if bare == "/":
        return None
    # The last order show.py wrote for one view: what its home switches to.
    if bare == "/show":
        return json.dumps(show.read(view_of(query))).encode(), JSON
    # How many app homes hold each view right now, as the app door asks.
    if bare == "/views":
        return json.dumps(show.homes()).encode(), JSON
    # The wake line waiting on the app home's panel, or "".
    if bare == "/app":
        return json.dumps({"line": appwake.panel()["line"]}).encode(), JSON
    if m := TRANSCRIPT.fullmatch(bare):
        got = transcript.answer(m.group(1), m.group(2), query)
        return NOT_FOUND if got is None else got
    if m := SHOTS.fullmatch(bare):
        got = views.shots.answer(m.group(1), m.group(2))
        return NOT_FOUND if got is None else got
    if m := EXPLANATION.fullmatch(bare):
        got = views.explanation.answer(m.group(1), "/" + m.group(2))
        return NOT_FOUND if got is None else got
    if m := re.fullmatch(r"/tree/(\d{2})/?(.*)", bare):
        return tree(m.group(1), urllib.parse.unquote(m.group(2)))
    if m := re.fullmatch(r"/text/(\d{2})/(.+)", bare):
        return text(m.group(1), urllib.parse.unquote(m.group(2)))
    if bare == "/apple-touch-icon.png":
        return touch_icon(), "image/png"
    if bare == "/manifest.webmanifest":
        return MANIFEST.encode(), "application/manifest+json"
    if bare == project.ASKED:
        return project.identity().encode(), "application/json"
    if bare == "/sw.js":
        return push.WORKER.encode(), "text/javascript; charset=utf-8"
    return NOT_FOUND


def start_band() -> str:
    """Bring up every band-00 server that is not already answering.

    Nothing is waited for. A dev server takes far longer to bind than a
    prompt should block, and the system page turns each port green on its
    own, which is what it is for.

    The command is left detached, so it outlives the hook that started it,
    and its pid is recorded. A live launcher is the reason not to start a second
    one: a port that never binds, because its package is not written yet,
    would otherwise relaunch the whole band on every call.

    A project naming no band 00 starts none.
    """
    if not DEV or not PORTS:
        return "This project names no band 00, so 1100 runs alone."
    pidfile = serve.pidfile("band-00")
    if ports.alive(serve.kept("band-00")):
        return "Band 00 is already running."
    down = sorted(p for p, up in band_state().items() if not up)
    if not down:
        return "Band 00 was already up."
    log = serve.logfile("band-00")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "ab") as f:
        started = subprocess.Popen(DEV, cwd=serve.ROOT, stdout=f, stderr=f,
                                   start_new_session=True)
    with open(pidfile, "w") as f:
        f.write(str(started.pid))
    return f"Band 00 starting, {len(down)} to come up."


def stop_everything() -> str:
    """Take down band 00 and this page, and wait until they are gone.

    Every session's own servers stay up: each session stops its own. This
    page goes last, so it is watching until the end.
    """
    running = ports.held("00")
    running.pop(PORT, 0)
    killed = ports.stop(running)
    # The command that started the band outlives the servers under it. Left
    # alive, it would tell the next start that band 00 is still running.
    band = serve.kept("band-00")
    serve.stop("band-00", 0)
    page = serve.holder(PORT)
    if serve.stop(SKILL, PORT):
        killed.append(str(PORT))
    ports.gone([p for p in (*running.values(), band, page) if p], 10)
    if not killed:
        return "Nothing was running."
    return f"{len(killed)} successfully stopped: {', '.join(sorted(killed))}."


# A page's own scripts: each script tag but a JSON one.
SCRIPTS = re.compile(r"<script(?![^>]*application/json)[^>]*>(.*?)</script>", re.S)
# Node compiles each script file it is handed, as node --check would, and
# prints each one failing: its file, its line, and why.
PARSE = r"""
const fs = require('fs'), vm = require('vm');
for (const f of process.argv.slice(1)) {
  try { new vm.Script('(function(){' + fs.readFileSync(f, 'utf8') + '\n})', {filename: f}); }
  catch (e) { console.log(f + '\t' + ((String(e.stack).split('\n')[0].match(/:(\d+)$/) || [])[1] || '?') + '\t' + e.message); }
}
"""


def node() -> str:
    """Node, as this Mac holds it: on the PATH, else nvm's newest. "" with none."""
    found = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/node")))
    return shutil.which("node") or (found[-1] if found else "")


def parsed(drawn: dict) -> None:
    """Every script each drawn page carries, compiled by Node, so a slip
    inside a Python string never blanks a page, and every script the pages
    on the contract share, .claude/pages/scripts/'s. One failing raises, naming its
    page, its script and its line. A Mac with no Node checks nothing."""
    runner = node()
    if not runner:
        return
    with tempfile.TemporaryDirectory() as tmp:
        files = {f: os.path.relpath(f, serve.ROOT) for f in sorted(glob.glob(os.path.join(live.SCRIPTS, "*.js")))}
        for path, html in drawn.items():
            for i, src in enumerate(SCRIPTS.findall(html)):
                f = os.path.join(tmp, f"{len(files)}.js")
                with open(f, "w") as out:
                    out.write(src)
                files[f] = f"{path} script {i + 1}"
        r = subprocess.run([runner, "-e", PARSE, *files], capture_output=True, text=True, timeout=60)
    bad = [line.split("\t") for line in r.stdout.splitlines() if line.count("\t") == 2]
    if bad:
        f, line, why = bad[0]
        raise SyntaxError(f"{files.get(f, f)}, line {line}: {why}"
                          + (f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""))


def bound(node) -> list:
    """The names one top-level statement binds, an import's aside."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [n.id for t in node.targets for n in ast.walk(t)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


def twice() -> None:
    """Every file under lib, tools and hooks, read for a name bound twice
    at its top level: the second binding takes the first's place for every
    reader. On 9 November `USED` held a table where lib/transcripts.py
    meant a pattern, and every transcript holding a task notice failed to
    draw. One found raises, naming its file and both lines."""
    root = os.path.dirname(HERE)
    for f in sorted(glob.glob(os.path.join(root, "lib", "*.py")) + glob.glob(os.path.join(root, "tools", "*.py"))
                    + glob.glob(os.path.join(root, "hooks", "*.py"))):
        with open(f, encoding="utf-8") as src:
            tree = ast.parse(src.read(), f)
        seen = {}
        for node in tree.body:
            for name in bound(node):
                if name in seen:
                    raise SyntaxError(f"{os.path.relpath(f, serve.ROOT)} binds {name} twice, "
                                      f"at lines {seen[name]} and {node.lineno}")
                seen[name] = node.lineno


# A press every page must refuse in a sentence: one naming no act it knows.
# A page with one act is also handed that act with a value it never
# offered, by the start of its address.
REFUSED = {"act": ["no such act"]}
OFFERED = {serve.address("launch", ""): {"act": ["save"], "rows": ["{"]},
           serve.address("handover", ""): {"act": ["handover"], "model": ["no such model"]}}


def stood(path: str):
    """One address, drawn now as 1100 draws it: home, or its page on the
    contract, its HTML or its bytes. A draw that raises raises here, and an
    address no page holds is refused."""
    if path == "/":
        return workstation.home()
    found = TABLE.find(path)
    if found is None:
        raise LookupError(f"home opens {path}, which no page on the contract answers")
    held, args = found
    return held.draw(*args)


def made_up() -> dict:
    """Home and every page of lib/trial.py's made-up folder, drawn twice
    through the table, the clock moved between: a wave, a plan, launch rows
    and every other kind, whether or not one shows on my real 1100 now.
    Each page drawn, by its address. A draw that raises, logs an error,
    starts a program or differs once the clock moved, a page that opens
    without its watch, a session home cannot read, and a press that is not
    refused in a sentence, each raise here. On 10 November the assistant
    page drew the current second, and reloaded 28 times in ten."""
    drawn, logged = {}, io.StringIO()
    with trial.world() as w, contextlib.redirect_stderr(logged):
        workstation.FAILED.clear()
        live.LOGGED.clear()
        pages = workstation.model()["pages"]
        if workstation.FAILED:
            raise RuntimeError("home could not read the made-up " + ", ".join(sorted(f[0] for f in workstation.FAILED)))
        def steady(draw, path: str):
            first = draw(path)
            with trial.clock():
                trial.forget()
                again = draw(path)
            if first != again:
                raise RuntimeError(f"the made-up {path} draws differently once the clock moves: "
                                   "what ticks is drawn in the browser, never by 1100")
            return first

        drawn["made-up /"] = steady(stood, "/")
        # Each page as the table draws it and takes its press: a page opens
        # with its watch, and loads the shared script. Home's model is data.
        table = served()
        for path in sorted({p["path"] for p in pages.values()}) + RAIL + ["/model"]:
            if not table.find(path):
                raise RuntimeError(f"home opens {path}, which no page on the contract answers")
            first = steady(table.route, path)
            if isinstance(first, str):
                if 'id="watch"' not in first or live.src("live.js") not in first:
                    raise RuntimeError(f"the made-up {path} draws without live.watch()")
                drawn[f"made-up {path}"] = first
            for form in [REFUSED, *(f for at, f in OFFERED.items() if path.startswith(at))]:
                said = table.take(form, path)
                if type(said) is not str or not said.strip():
                    raise RuntimeError(f"the page at {path} took a press it must refuse: {said!r}")
        if w.started:
            raise RuntimeError(f"a draw of the made-up folder started a program: {w.started[0][:120]}")
    # The made-up folder holds nothing a page cannot read, so an error
    # logged while drawing it is the code's.
    if "Traceback" in logged.getvalue():
        raise RuntimeError("a draw of the made-up folder logged an error: "
                           + [line for line in logged.getvalue().splitlines() if line.strip()][-1])
    return drawn


def check() -> None:
    """No file binds a name twice. Home and every page of a made-up folder
    draw: made_up(). Then draw home once, as a fresh 1100 would, then one
    page of each kind home shows now, my own launch page, and every rail
    page 1100 draws, and parse every script they all carry. Raises when the
    code on disk cannot."""
    twice()
    drawn = made_up()
    first = {}
    for p in workstation.model()["pages"].values():
        first.setdefault(p["kind"], p["path"])
    drawn["/"] = workstation.home()
    for path in [*first.values(), serve.address("launch", "00"), "/system", "/files", "/skills", "/library", "/agenda"]:
        got = stood(path)
        if isinstance(got, str):
            drawn[path] = got
    parsed(drawn)


def restart() -> str:
    """1100 alone, stopped and started on the code on disk. Band 00 and
    every session's servers stay up.

    The new code draws in a child first, and its pages' scripts parse.
    When it cannot, the running 1100 is never touched, so a broken edit
    never leaves me with no page.
    """
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "check"],
                       capture_output=True, text=True)
    if r.returncode:
        last = (r.stderr.strip().splitlines() or ["it printed nothing"])[-1]
        return f"1100 kept its old code. The new code fails to draw: {last}"
    pid = serve.holder(PORT)
    serve.stop(SKILL, PORT)
    if pid:
        ports.gone([pid], 5)
    if ports.answering(PORT):
        return "1100 did not stop, so nothing changed."
    problem = serve.start(SKILL, PORT, os.path.abspath(__file__))
    return problem or "1100 successfully restarted on the new code."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["serve", "status", "stop", "band", "check", "restart"])
    ap.add_argument("--port", type=int, default=PORT)
    args = ap.parse_args()

    # One project at a time: another project's 1100 and band are never
    # stopped, started over or joined from here.
    refused = project.refusal(PORT) if args.verb in ("band", "stop", "restart") else ""
    if refused:
        print(refused)
    elif args.verb == "check":
        check()
        print("1100's code draws.")
    elif args.verb == "restart":
        print(restart())
    elif args.verb == "serve":
        # A copy tried on a session's own port keeps its pid in that
        # session's server folder, which its stop deletes.
        skill = SKILL if args.port == PORT else f"{SKILL}-{args.port % 100:02d}"
        # A launch is a program of its own, which 1100 stopping never stops.
        # One whose program died left rows booting: resume hands them to a
        # new one. My own launch page's rows are 00's, and 00 is no session.
        # A copy on a session's port picks none up. A driving assistant capped on its own
        # account goes on at the reset, a session done buzzes my phone, a
        # mission's session waiting on me is handed to its assistant, every
        # account is asked for its windows, and band 00's log is kept short.
        # Only 1100 does any.
        if args.port == PORT:
            for nn in [*registry.entries(), "00"]:
                views.launcher.resume(nn)
            threading.Thread(target=finish.watch, daemon=True).start()
            threading.Thread(target=finish.asking, daemon=True).start()
            threading.Thread(target=page.reddened, args=([push.buzz(opened), views.assistant.sent],),
                             kwargs={"kept": os.path.join(serve.SERVERS, SKILL, "colours.json")},
                             daemon=True).start()
            threading.Thread(target=serve.keep_short, args=("band-00",), daemon=True).start()
        # iTerm's pane list is read on a thread of its own, so no draw ever
        # waits on iTerm: lib/panes.py's refresher. A copy runs it too.
        threading.Thread(target=panes.freshen, daemon=True).start()
        # So is the process list, lib/reader.py's way: no draw starts ps. And
        # so is what each page tool states as its own readers, READERS.
        ports.PROCESSES.start()
        for kept in gathered("READERS"):
            kept.start()
        # The table is asked first, and hears each open page's files. What
        # rides on is heard here: the app chat's panel, and show's
        # folder, made now so its first order is heard. Home reloads when
        # its own code moves, never on a restart alone.
        os.makedirs(show.FOLDER, exist_ok=True)
        workstation.CODE[0] = workstation.code()
        riding = TABLE.riding(take=take, route=contained(one_list(route)), keyof=keyof,
                              hears=lambda: [appwake.PANEL, show.FOLDER])
        riding.update(route=one_list(riding["route"]), keyof=one_list(riding["keyof"]))
        # The prototype page is 1100's own: its address is never passed
        # through to 1400, every other under its prefix is.
        through = (views.prototypes.BASE, views.prototypes.PORT, lambda path: TABLE.find(path) is not None)
        serve.run(skill, args.port, contained(one_list(workstation.home)), raw=raw, through=through, **riding)
    elif args.verb == "band":
        print(start_band())
    elif args.verb == "stop":
        print(stop_everything())
    else:
        print(f"http://127.0.0.1:{args.port} — "
              + ("up" if ports.answering(args.port) else "down"))


if __name__ == "__main__":
    main()
