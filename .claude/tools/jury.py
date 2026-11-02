#!/usr/bin/env python3
"""jury.py — starts jury sessions, matches their quotes, and counts their answers.

A jury checks words against their sources with many small agents. A jury
session is one approach: its model, its stance, what it reads. Its jurors
are Claude Code's built-in subagent, one per claim, or one per lens on a
case. Jurors get only the typed question, never the asking session's
conversation.

  jury.py draft NN < draft.json   a plan into session NN's folder; prints its path
  jury.py run NN [RUN]            runs plan RUN, else NN's newest plan not yet run
  jury.py words NN                session NN's last words, as /jury reads them

draft.json is what /jury drafted: from, context, question, shape, and
claims, each {"text", "source"}; picks and lenses when it sets its own.
draft fills the rest: the run, the defaults below, each claim's number.

The run folder
--------------

Each run sits in the asking session's own folder,
.claude/state/sessions/NN/jury/RUN/. RUN is the minute draft made it,
2026-10-21-1612, with -2 added when that minute is taken.

  plan.json      draft writes it. The jury tab draws it, and saves my edits into it before Launch.
  results.json   run writes it as jurors answer, and again once the conclusion lands.
  streams/       each headless session's raw stream, for proof. No page reads it.

Each write replaces a file whole: written beside it, then swapped in. A
plan with results.json beside it is launched, and never changes again.

plan.json, what the tab draws before Launch:

  {"run": "2026-10-21-1612", "session": "10", "drafted": "2026-10-21T16:12:03",
   "from": {"label": "Session 10's last turn · 14:23", "at": ""},
   "context": ["Session 10 sent a research agent to study small agents checking claims."],
   "question": "Does each claim in the report hold against its source?",
   "shape": "one pick", "picks": ["Holds", "Broken", "Unproven"],
   "claims": [{"n": 1, "text": "Your rules say Claude Code refuses a seventh agent.",
               "source": ".claude/rules/thinking.md:285"}],
   "lenses": [],
   "sessions": [{"letter": "A", "approach": "Reads the cited source",
                 "how": "Reads the source each claim names, else the file it is about. Nothing else.",
                 "reads": "cited", "model": "haiku", "effort": "medium", "per": "claim"}]}

  from      where the words came from. label is the tab's kick line. at is
            the file or link, "" for a turn or my own words.
  context   the typed question's context, one line each.
  question  its one question.
  shape     one of SHAPES.
  picks     the answers a pick shape counts: PICKS for yes or no and one
            pick, the options for several picks, [] for an idea or a case.
            Every shape also allows UNSURE, never listed.
  claims    numbered from 1, each with its source: a file:line, a file or a
            link, "" when none is named. An idea with no claims asks the
            question itself. A case holds none: each advocate gives one point,
            and the fact it rests on becomes a claim, in results.json.
  lenses    a case's lenses, my five axes by default, read from AXES. [] otherwise.
  sessions  each jury session, in order: CHECKS, or a case's ADVOCATES then CHECKS.
              letter    its chip.
              approach  its name.
              how       its stance: what its jurors are told to try.
              reads     a key of READS: cited, own or any.
              model     a family --model takes: one of MODELS.
              effort    one of panes.EFFORTS.
              per       claim: one juror per claim. lens: one per lens, a case's advocates.
  concluder the session that writes the conclusion: {"model": "sonnet",
            "effort": "high"}, each as a jury session's. The tab saves it.
            Left out, or a key of it, CONCLUDER's holds.

The account is never in it. A run takes the asking session's own.

Launch: the tab saves my edits into plan.json, then types into the asking
session's pane the line I could type there myself:

  /jury-run 2026-10-21-1612

results.json, what the tab draws once Launch ran:

  {"run": "2026-10-21-1612", "session": "10",
   "launched": "2026-10-21T16:20:11", "done": "", "state": "running", "error": "",
   "jurors": {"answered": 12, "asked": 18},
   "step": {"n": 1, "steps": 2, "what": "Checking 6 claims", "at_once": 18, "answered": 12, "asked": 18},
   "claims": [{"n": 4, "text": "A rule of yours is wrong.", "source": "",
               "outcome": "Broken", "count": "2 of 2 said Broken · C gave no answer",
               "rounds": 1, "why": ".claude/settings.json:93 sets six.",
               "answers": [{"juror": "A·4", "session": "A", "round": 1,
                            "model": "claude-haiku-5-5", "answer": "Broken",
                            "why": "The rule says six, as this Mac sets.",
                            "quote": "Six agents run at once, at most.",
                            "place": ".claude/rules/thinking.md:285",
                            "check": "matched", "counted": "Broken"}]}],
   "points": [],
   "conclusion": {"lead": "Act on one claim.", "model": "claude-sonnet-5-5"},
   "cost": {"sessions": [{"letter": "A", "tokens": 48210, "usd": 0.0121}],
            "conclusion": {"tokens": 12400, "usd": 0.031},
            "total": {"tokens": 151489, "usd": 0.092},
            "line": "A 48,210 tokens · B 51,003 · C 39,876 · conclusion 12,400 · total 151,489 tokens, $0.09 at list price"}}

  state       running, concluding, done, or failed with its error.
  jurors      jurors through, of jurors asked so far. A re-check adds to asked.
  step        the step running, else the last one: its number, of a case's 3
              or another shape's 2, what it does, how many of its jurors run
              at once, and how many are through of its own. A juror is
              through once answered, or given up on. Each batch moves it.
  claims      in the plan's order, each as the plan wrote it. A case's facts.
    outcome   the answer every counted answer in the last round gave: a pick,
              or several joined by ", ". split, when two re-checks left them
              apart. listed, for an idea. no answer, when no juror answered.
              "" while it runs.
    count     the last round's count, never a percentage, each gap named:
              "3 of 3 said Holds", "2 of 2 said Holds · C gave no answer",
              "2 said Holds · 1 said Broken" on a split. "" for an idea.
    rounds    1, or 2 and 3 after re-checks.
    why       the conclusion's one line for it. "" until it lands.
    answers   every juror's answer, every round.
      juror   its session's letter and its claim's number.
      session its session's letter.
      round   the round it answered in.
      model   the model the stream says ran it.
      answer  as the juror gave it, or no answer.
      why     its one-line reason.
      quote   its words from the source, as it wrote them.
      place   the file:line, or the page's link, it quoted.
      check   matched; not found; unchecked, a page that could not be
              fetched, its link in place; none, no quote given.
      counted what it counted as: its answer, or the unsure answer when its
              quote is not found or none. "" when never counted: no answer,
              or an idea.
  points      a case's points, else []: {"side": "For", "session": "A",
              "lens": "It is fast.", "point", "fact": 3}. side is its
              session's approach. fact is the claim it rests on.
  conclusion  {} until it lands. lead is its one lead line.
  cost        each jury session's tokens, the conclusion's, and the total.
              Tokens add input, output and cache, from each headless run's
              result event. usd adds its total_cost_usd, at list price.

How a run goes
--------------

Each jury session starts headless in --safe-mode, on the asking session's
account: no CLAUDE.md, no hook, no skill, no custom agent. Sign-in and
subagents still work. The headless session only dispatches. It reads
nothing, and starts at most AT_ONCE jurors, the cap the command line also
passes, so a seventh is never refused. More jurors wait for the next
batch. Every juror runs in the foreground: one result, no resumes. Its
answer comes back in the stream, and this file writes it. The headless
session writes nothing.

A quote is matched word for word, after evening out spaces, a line
number's tab or colon, curly quotes, backticks, quotes around it, and a
note after them. A page is fetched and its markup stripped first.

A juror with no answer is asked once more. A claim whose counted answers
differ runs again in every check session, by fresh jurors who see every
quote and no verdict, RECHECKS times at most. Then one fresh session
writes the conclusion, from the question and the results alone.
"""

import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import transcripts  # noqa: E402

ROOT = registry.ROOT
# The references sit beside the project, its folder's name and "-references".
# Jurors that search read them too.
REFERENCES = ROOT + "-references"
AXES = os.path.join(ROOT, "knowledge", "0010-playbook", "0013-thinking", "the-thinking-axioms.md")
STAMP = "%Y-%m-%dT%H:%M:%S"

SHAPES = ("yes or no", "one pick", "several picks", "an idea", "a case")
PICKS = {"yes or no": ["Yes", "No"], "one pick": ["Holds", "Broken", "Unproven"]}
UNSURE = "can't tell"
MODELS = ("opus", "sonnet", "fable", "haiku")

# A juror's reach, by its session's reads, and the tools that give it.
READS = {
    "cited": "Read the claim's cited source, and nothing else.",
    "own": f"Find your own source: this project, the folder {REFERENCES}, or the web.",
    "any": f"Search anywhere: this project, the folder {REFERENCES}, or the web.",
}
TOOLS = {"cited": ["Read", "WebFetch"],
         "own": ["Read", "Grep", "Glob", "WebFetch", "WebSearch"],
         "any": ["Read", "Grep", "Glob", "WebFetch", "WebSearch"]}

CHECKS = [
    {"approach": "Reads the cited source",
     "how": "Reads the source each claim names, else the file it is about. Nothing else.",
     "reads": "cited", "model": "haiku", "effort": "medium", "per": "claim"},
    {"approach": "Finds its own source",
     "how": "Never told where a claim came from. Searches until one line settles it.",
     "reads": "own", "model": "haiku", "effort": "medium", "per": "claim"},
    {"approach": "Tries to break it",
     "how": "Hunts for one line against each claim. Finding none, it says so.",
     "reads": "any", "model": "sonnet", "effort": "medium", "per": "claim"},
]
ADVOCATES = [
    {"approach": "For", "how": "Argues for it, through its lens. Each point names its fact and source.",
     "reads": "any", "model": "sonnet", "effort": "medium", "per": "lens"},
    {"approach": "Against", "how": "Argues against it, through its lens. Each point names its fact and source.",
     "reads": "any", "model": "sonnet", "effort": "medium", "per": "lens"},
]
CONCLUDER = {"model": "sonnet", "effort": "medium"}

# Jurors one headless session starts at once. Claude Code refuses one past its cap.
AT_ONCE = 6
RECHECKS = 2
# Seconds one headless session may run before it is stopped.
WATCHDOG = 900


def now() -> str:
    return datetime.datetime.now().strftime(STAMP)


def concluder(plan: dict) -> dict:
    """The model and effort the conclusion runs on: the plan's, else CONCLUDER's."""
    own = plan.get("concluder")
    return {**CONCLUDER, **(own if isinstance(own, dict) else {})}


def folder(nn: str) -> str:
    return os.path.join(registry.folder(nn), "jury")


def save(path: str, data: dict) -> None:
    """A file replaced whole."""
    registry.write_whole(path, json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def axes() -> list:
    """My five axes, as the thinking axioms list them."""
    try:
        text = open(AXES).read()
    except OSError:
        return []
    part = re.search(r"^## [^\n]*five axes[^\n]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return re.findall(r"^- (.+)$", part.group(1), re.M) if part else []


# ---- draft ------------------------------------------------------------------

def draft(nn: str, got: dict) -> str:
    """Write session NN's new plan from what /jury drafted. Its path."""
    shape = got.get("shape")
    if shape not in SHAPES:
        sys.exit(f"shape must be one of: {', '.join(SHAPES)}.")
    case = shape == "a case"
    claims = [] if case else [
        {"n": i, "text": c["text"].strip(), "source": str(c.get("source") or "").strip()}
        for i, c in enumerate([c for c in got.get("claims") or [] if str(c.get("text") or "").strip()], 1)]
    picks = got.get("picks") or PICKS.get(shape, [])
    if shape == "several picks" and not picks:
        sys.exit("several picks needs its picks.")
    sessions = [dict(s) for s in (ADVOCATES + CHECKS if case else CHECKS)]
    for i, s in enumerate(sessions):
        s["letter"] = chr(ord("A") + i)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    run, k = stamp, 1
    while os.path.exists(os.path.join(folder(nn), run)):
        k += 1
        run = f"{stamp}-{k}"
    plan = {"run": run, "session": nn, "drafted": now(),
            "from": {"label": str((got.get("from") or {}).get("label") or ""),
                     "at": str((got.get("from") or {}).get("at") or "")},
            "context": [str(x) for x in got.get("context") or []],
            "question": str(got.get("question") or "").strip(),
            "shape": shape,
            "picks": [] if shape in ("an idea", "a case") else [str(p) for p in picks],
            "claims": claims,
            "lenses": [str(x) for x in got.get("lenses") or axes()] if case else [],
            "sessions": [{k: s[k] for k in ("letter", "approach", "how", "reads", "model", "effort", "per")}
                         for s in sessions]}
    path = os.path.join(folder(nn), run, "plan.json")
    save(path, plan)
    return path


# ---- words ------------------------------------------------------------------

def words(nn: str) -> str:
    """Session NN's last words since my turn, under its title and their time."""
    path, title = transcripts.find(nn)
    if not path:
        sys.exit(f"No transcript for session {nn}.")
    said, at, _ = transcripts.last_said(path)
    if not said:
        sys.exit(f"Session {nn} has said nothing since its last prompt.")
    return f"# {title} · {transcripts.clock(at)}\n\n{said}"


# ---- the quote match --------------------------------------------------------

CURLY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', " ": " "})


def even(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(CURLY)).strip()


def forms(quote: str) -> list:
    """The quote as a juror may have dressed it: a line number's tab or colon
    on each line, backticks or quotes around it, a note after them. Each
    form, evened out."""
    raw = quote.strip().translate(CURLY)
    bare = "\n".join(re.sub(r"^\s*\d+\s*(?:\t|:|→|\|)", "", line) for line in raw.splitlines())
    bare = re.sub(r"^\s*\d+\s+(?=`)", "", bare)
    inside = re.search(r"([\"`])(.{8,})\1", raw, re.S)
    out = []
    for f in (raw, bare) + ((inside.group(2),) if inside else ()):
        f = f.strip()
        out.append(f)
        while len(f) > 1 and f[0] == f[-1] and f[0] in "`'\"":
            f = f.strip(f[0]).strip()
            if len(f) >= 8:
                out.append(f)
    return list(dict.fromkeys(even(f) for f in out if f))


def holds(quote: str, text: str) -> bool:
    """Whether a form of QUOTE sits in TEXT word for word, its backticks, a
    word's code marks, aside. A quote cut with an ellipsis holds when each
    piece does, in order."""
    hay = even(text.replace("`", ""))
    for f in (even(f.replace("`", "")) for f in forms(quote)):
        if f in hay:
            return True
        at, pieces = 0, [p for p in re.split(r"\s*(?:…|\.\.\.)\s*", f) if p]
        for p in pieces:
            at = hay.find(p, at)
            if at < 0:
                break
            at += len(p)
        else:
            if len(pieces) > 1:
                return True
    return False


class Text(HTMLParser):
    """A page's words, its markup and scripts stripped."""

    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        self.hidden += tag in self.SKIP

    def handle_endtag(self, tag):
        self.hidden -= tag in self.SKIP and self.hidden > 0

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


PAGES: dict = {}
PAGES_LOCK = threading.Lock()


def page(url: str) -> str | None:
    """A page's text, fetched once per run. None when it cannot be fetched."""
    with PAGES_LOCK:
        if url in PAGES:
            return PAGES[url]
    try:
        ask = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh) jury.py"})
        with urllib.request.urlopen(ask, timeout=20) as r:
            kind = r.headers.get_content_type()
            body = r.read(5_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
        if kind == "text/html" or kind == "application/xhtml+xml":
            p = Text()
            p.feed(body)
            body = " ".join(p.parts)
        elif not kind.startswith("text/"):
            body = None
    except Exception:
        body = None
    with PAGES_LOCK:
        PAGES[url] = body
    return body


LINK = re.compile(r"https?://[^\s<>()\"'`]+")
PATH = re.compile(r"[~\w./@+-]*/[\w.@+-]+|[\w@+-][\w.@+-]*\.\w+")


def source_text(place: str) -> tuple:
    """The text a place names, as (text, link). text is None when no file or
    page answers; link is set when the place is a page."""
    url = LINK.search(place or "")
    if url:
        link = url.group(0).rstrip(".,;:)]")
        return page(link), link
    m = PATH.search(place or "")
    if not m:
        return None, ""
    name = os.path.expanduser(m.group(0))
    for base in ("", ROOT, REFERENCES):
        path = os.path.join(base, name) if base else name
        if os.path.isabs(path) and os.path.isfile(path):
            try:
                return open(path, errors="replace").read(), ""
            except OSError:
                return None, ""
    return None, ""


def check(quote: str, place: str) -> str:
    """matched, not found, unchecked, or none."""
    if not quote.strip() or even(quote).lower() in ("none", "n/a", "-", "—"):
        return "none"
    text, link = source_text(place)
    if text is None:
        return "unchecked" if link else "not found"
    return "matched" if holds(quote, text) else "not found"


# ---- what a juror is asked, and what it answers ---------------------------

def unsure(plan: dict) -> str:
    """The answer an unsettled claim counts as."""
    return "Unproven" if plan["shape"] == "one pick" and "Unproven" in plan["picks"] else UNSURE


def answer_lines(plan: dict, shape: str) -> list:
    if shape == "an idea":
        first = "Answer: your idea, in one line"
    elif shape == "several picks":
        first = f"Answer: every pick that applies, from {', '.join(plan['picks'])}, joined by commas; or {UNSURE}"
    else:
        picks = plan["picks"] + ([] if unsure(plan) in plan["picks"] else [UNSURE])
        first = f"Answer: one of {', '.join(picks)}"
    out = ["Answer in exactly four lines, nothing else:", first, "Why: one line",
           "Quote: the source's words alone, copied exactly, on one line", "Place: file:line, or the page's link"]
    if plan["picks"] == PICKS["one pick"]:
        out.append("Holds: the source says so. Broken: it says otherwise. Unproven: it settles nothing, "
                   "or you can't tell.")
    return out


def typed(plan: dict, s: dict, claim: dict | None, quotes: list) -> str:
    """The typed question one juror gets: the context, one question, the answer's shape."""
    lines = ["Context:"] + plan["context"] + ["", f"Question: {plan['question']}"]
    if claim and claim["text"]:
        lines.append(f"Claim: {claim['text']}")
        if s["reads"] != "own":
            lines.append(f"Its cited source: {claim['source'] or 'none named'}")
    lines += ["", f"Your approach: {s['how']}", READS[s["reads"]]]
    if quotes:
        lines += ["", "Quotes other jurors gave, with no verdict. Check each against its source yourself:"]
        lines += [f"- {q} ({p})" for q, p in quotes]
    return "\n".join(lines + [""] + answer_lines(plan, plan["shape"]))


def advocate(plan: dict, s: dict, lens: str) -> str:
    """The typed question one advocate gets, for one lens of a case."""
    lines = ["Context:"] + plan["context"] + ["", f"Question: {plan['question']}",
                                              f"Your side: {s['approach']}. Your lens: {lens}",
                                              "", f"Your approach: {s['how']}", READS[s["reads"]], "",
                                              "Give only your one strongest point, in exactly four lines, "
                                              "nothing else:",
                                              "Point: one line", "Fact: the fact it rests on, in one line",
                                              "Quote: the source's words alone, copied exactly, on one line",
                                              "Place: file:line, or the page's link"]
    return "\n".join(lines)


FIELD = re.compile(r"^[\s>*_`#-]*(answer|verdict|why|quote|place|point|fact)[*_`]*\s*:[*_]*\s*(.*)$", re.I)


def fields(text: str) -> list:
    """Each block of NAME: value lines, a value running on until the next name."""
    blocks, last = [{}], None
    for line in text.splitlines():
        m = FIELD.match(line)
        if m:
            name = {"verdict": "answer"}.get(m.group(1).lower(), m.group(1).lower())
            if name in blocks[-1] and name in ("answer", "point"):
                blocks.append({})
            blocks[-1][name] = m.group(2).strip()
            last = name
        elif last and line.strip() and last == "quote":
            blocks[-1][last] += "\n" + line
    return [b for b in blocks if b]


def picked(plan: dict, said: str) -> str | None:
    """A juror's answer as a count takes it. None when it is no pick."""
    plain = said.strip().strip("*_`.").strip()
    low = plain.lower()
    if re.match(r"(can'?t|cannot|can not) tell", low):
        return unsure(plan)
    if plan["shape"] == "several picks":
        chosen = [p for p in plan["picks"] if re.search(rf"\b{re.escape(p.lower())}\b", low)]
        return ", ".join(chosen) or None
    for p in plan["picks"]:
        if re.match(rf"{re.escape(p.lower())}\b", low):
            return p
    return None


# ---- the headless sessions ------------------------------------------------

def environment(nn: str) -> dict:
    """A headless session's environment: no Claude session's markers, no
    iTerm pane's, the asking session's account, and the cap on the line."""
    try:
        with open(os.path.join(registry.folder(nn), registry.RECORD)) as f:
            acct = json.load(f).get("account", "")
    except (OSError, ValueError, AttributeError):
        acct = ""
    acct = acct if acct in accounts.ACCOUNTS else registry.account()
    env = {k: v for k, v in panes.clean().items() if k not in ("ITERM_SESSION_ID", "TERM_SESSION_ID")}
    where = accounts.ACCOUNTS.get(acct, {}).get("folder", accounts.DEFAULT)
    if where != accounts.DEFAULT:
        env["CLAUDE_CONFIG_DIR"] = where
    env["CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS"] = str(AT_ONCE)
    return env


def command(prompt: str, model: str, tools: list, effort: str = "") -> list:
    """The exact command a headless session runs."""
    line = ["claude", "-p", prompt, "--safe-mode", "--model", model,
            "--tools", ",".join(tools),
            "--permission-mode", "dontAsk", "--strict-mcp-config", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose"]
    if os.path.isdir(REFERENCES):
        line += ["--add-dir", REFERENCES]
    web = [t for t in ("WebFetch", "WebSearch") if t in tools]
    if web:
        line += ["--allowedTools", ",".join(web)]
    if effort:
        line += ["--effort", effort]
    return line


def headless(cmd: list, env: dict, stream: str) -> int:
    """Run one headless session, its stream into STREAM. Its exit code; -1 when stopped."""
    os.makedirs(os.path.dirname(stream), exist_ok=True)
    with open(stream, "w") as out, open(stream[:-len(".jsonl")] + ".err", "w") as err:
        try:
            return subprocess.run(cmd, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                  stdout=out, stderr=err, timeout=WATCHDOG).returncode
        except subprocess.TimeoutExpired:
            return -1


def report(event: dict, item: dict) -> str:
    """A foreground juror's report, from the user event carrying its result."""
    r = event.get("tool_use_result")
    if isinstance(r, dict) and isinstance(r.get("content"), list):
        parts = r["content"][r.get("harnessNoteCount", 0): len(r["content"]) - r.get("harnessTailCount", 0)]
        return "\n".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
    c = item.get("content")
    text = c if isinstance(c, str) else "\n".join(p.get("text", "") for p in c or [] if isinstance(p, dict))
    text = text.split("The report follows:\n", 1)[-1].split("\nagentId:", 1)[0]
    return "\n".join(line[2:] if line.startswith("  ") else line for line in text.splitlines()).strip()


def tag(description: str) -> str:
    """A juror's tag, A·4, from the description its call carried."""
    m = re.search(r"([A-Z])\s*[·.\-_ ]?\s*(\d+)\s*$", description or "")
    return f"{m.group(1)}·{m.group(2)}" if m else ""


def heard(stream: str) -> dict:
    """What one headless session's stream holds: each juror's report, model
    and prompt as asked, by its tag; the session's last words; its usage."""
    calls, got, models = {}, {}, {}
    out = {"jurors": got, "said": "", "usage": {"models": {}, "usd": 0.0}}
    try:
        lines = open(stream).read().splitlines()
    except OSError:
        lines = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        kind, parent = e.get("type"), e.get("parent_tool_use_id")
        message = e.get("message") if isinstance(e.get("message"), dict) else {}
        content = message.get("content")
        if kind == "assistant" and parent:
            models.setdefault(parent, message.get("model", ""))
        elif kind == "assistant":
            for c in content or []:
                if c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                    calls[c["id"]] = c.get("input") or {}
        elif kind == "user" and not parent and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in calls and not c.get("is_error"):
                    r = e.get("tool_use_result") if isinstance(e.get("tool_use_result"), dict) else {}
                    ask = calls[c["tool_use_id"]]
                    got[tag(ask.get("description", ""))] = {
                        "text": report(e, c), "prompt": ask.get("prompt", ""),
                        "model": r.get("resolvedModel") or models.get(c["tool_use_id"], "")}
        elif kind == "result":
            out["said"] = e.get("result") or ""
            out["usage"] = {"models": e.get("modelUsage") or {}, "usd": e.get("total_cost_usd") or 0.0}
    return out


def tokens(usage: dict) -> int:
    return sum(m.get("inputTokens", 0) + m.get("outputTokens", 0) + m.get("cacheReadInputTokens", 0)
               + m.get("cacheCreationInputTokens", 0) for m in usage["models"].values())


def dispatch(jobs: list, s: dict) -> str:
    """The dispatcher's prompt: start these jurors at once, pass each prompt unchanged, reply DONE."""
    head = (f"You only dispatch jurors. Never read, search or answer anything yourself.\n"
            f"In one single message, call the Agent tool {len(jobs)} times at once. Every call: "
            f"subagent_type general-purpose, run_in_background false, model {s['model']}, "
            f"effort {s['effort']}. Each call takes the description and the prompt given below. "
            f"Pass each prompt exactly as written, every line, unchanged.\n"
            f"When every call has returned, reply only DONE.")
    return head + "".join(f"\n\n<<<description: juror {tag}>>>\n{prompt}\n<<<end>>>" for tag, prompt in jobs)


# ---- a run ------------------------------------------------------------------

class Run:
    """One launched plan: its jury sessions, its rounds, its results."""

    def __init__(self, nn: str, name: str):
        self.nn, self.name = nn, name
        self.dir = os.path.join(folder(nn), name)
        self.plan = json.load(open(os.path.join(self.dir, "plan.json")))
        # What the check rounds ask. A case's facts are claims, each asked as one pick.
        self.asks = self.plan if self.plan["shape"] != "a case" else {
            **self.plan, "shape": "one pick", "picks": PICKS["one pick"],
            "question": "Does the claim hold against its source?"}
        self.concluder = concluder(self.plan)
        self.env = environment(nn)
        self.lock = threading.Lock()
        self.usage = collections.defaultdict(lambda: {"models": {}, "usd": 0.0, "tokens": 0})
        self.batches = collections.Counter()
        self.res = {"run": name, "session": nn, "launched": now(), "done": "", "state": "running",
                    "error": "", "jurors": {"answered": 0, "asked": 0}, "step": {},
                    "claims": [], "points": [], "conclusion": {}, "cost": {}}

    def write(self) -> None:
        with self.lock:
            self.res["cost"] = self.cost()
            save(os.path.join(self.dir, "results.json"), self.res)

    def cost(self) -> dict:
        own = [{"letter": s["letter"], "tokens": self.usage[s["letter"]]["tokens"],
                "usd": round(self.usage[s["letter"]]["usd"], 4)} for s in self.plan["sessions"]]
        end = {"tokens": self.usage["conclusion"]["tokens"], "usd": round(self.usage["conclusion"]["usd"], 4)}
        total = {"tokens": sum(x["tokens"] for x in own) + end["tokens"],
                 "usd": round(sum(x["usd"] for x in own) + end["usd"], 4)}
        bits = [f"{x['letter']} {x['tokens']:,}" + (" tokens" if i == 0 else "") for i, x in enumerate(own)]
        line = " · ".join(bits + [f"conclusion {end['tokens']:,}",
                                  f"total {total['tokens']:,} tokens, ${total['usd']:.2f} at list price"])
        return {"sessions": own, "conclusion": end, "total": total, "line": line}

    def spend(self, key: str, usage: dict) -> None:
        with self.lock:
            u = self.usage[key]
            u["usd"] += usage["usd"]
            u["tokens"] += tokens(usage)

    def begin(self, n: int, what: str, sessions: int = 0, each: int = 0) -> None:
        """Step N starts: SESSIONS jury sessions, EACH jurors apiece."""
        with self.lock:
            self.res["step"] = {"n": n, "steps": 3 if self.plan["shape"] == "a case" else 2, "what": what,
                                "at_once": sessions * min(each, AT_ONCE), "answered": 0, "asked": sessions * each}
            self.res["jurors"]["asked"] += sessions * each
        self.write()

    def tick(self, k: int) -> None:
        """K more jurors of the step are through: answered, or given up on."""
        with self.lock:
            self.res["step"]["answered"] += k
            self.res["jurors"]["answered"] += k
        self.write()

    def ask(self, s: dict, jobs: list, label: str, valid) -> dict:
        """Ask session S's jurors, AT_ONCE per headless session. A juror whose
        report VALID refuses, or whose prompt came changed, is asked once
        more. Each juror's (report, model), None for no answer."""
        out, left = {}, list(jobs)
        for attempt in ("", "-again"):
            batches = [left[i:i + AT_ONCE] for i in range(0, len(left), AT_ONCE)]
            left = []
            for k, batch in enumerate(batches, 1):
                stream = os.path.join(self.dir, "streams", f"{s['letter']}-{label}{attempt}-{k}.jsonl")
                headless(command(dispatch(batch, s), "haiku", ["Agent"] + TOOLS[s["reads"]]), self.env, stream)
                got = heard(stream)
                self.spend(s["letter"], got["usage"])
                missed = len(left)
                for t, prompt in batch:
                    g = got["jurors"].get(t)
                    if g and even(g["prompt"]) == even(prompt) and valid(g["text"]):
                        out[t] = (g["text"], g["model"])
                    else:
                        left.append((t, prompt))
                # A juror asked again is through only once its second try ends.
                self.tick(len(batch) if attempt else len(batch) - (len(left) - missed))
            if not left:
                break
        for t, _ in left:
            out[t] = None
        return out

    def readable(self, text: str) -> bool:
        """Whether a check juror's report holds an answer a count can take."""
        said = (fields(text) or [{}])[0].get("answer", "")
        return bool(said) if self.asks["shape"] == "an idea" else picked(self.asks, said) is not None

    def answer(self, s: dict, n: int, rnd: int, got) -> dict:
        """One juror's answer as results.json keeps it."""
        a = {"juror": f"{s['letter']}·{n}", "session": s["letter"], "round": rnd, "model": "",
             "answer": "no answer", "why": "", "quote": "", "place": "", "check": "none", "counted": ""}
        if got is None:
            return a
        text, model = got
        b = (fields(text) or [{}])[0]
        a.update(model=model, why=b.get("why", ""), quote=b.get("quote", ""), place=b.get("place", ""))
        a["check"] = check(a["quote"], a["place"])
        if self.asks["shape"] == "an idea":
            a["answer"] = b.get("answer", "") or "no answer"
            return a
        pick = picked(self.asks, b.get("answer", ""))
        if pick is None:
            return a
        a["answer"] = b.get("answer", "").strip().strip("*_`").strip()
        a["counted"] = pick if a["check"] in ("matched", "unchecked") else unsure(self.asks)
        return a

    def round(self, claims: list, rnd: int) -> None:
        """Every check session answers every claim in CLAIMS once, side by side."""
        checks = [s for s in self.plan["sessions"] if s["per"] == "claim"]
        seen = {c["n"]: [] if rnd == 1 else list(dict.fromkeys(
            (a["quote"], a["place"]) for a in c["answers"] if a["quote"] and a["check"] != "none"))
            for c in claims}

        def one(s):
            jobs = [(f"{s['letter']}·{c['n']}", typed(self.asks, s, c, seen[c["n"]])) for c in claims]
            got = self.ask(s, jobs, f"r{rnd}", self.readable)
            with self.lock:
                for c in claims:
                    c["answers"].append(self.answer(s, c["n"], rnd, got[f"{s['letter']}·{c['n']}"]))
            self.write()

        case = self.plan["shape"] == "a case"
        self.begin(2 if case else 1, f"{'Checking' if rnd == 1 else 'Re-checking'} {len(claims)} "
                                     f"{'fact' if case else 'claim'}{'s' if len(claims) > 1 else ''}",
                   len(checks), len(claims))
        with ThreadPoolExecutor(len(checks) or 1) as pool:
            list(pool.map(one, checks))

    def settle(self, c: dict, last: bool) -> bool:
        """Set a claim's outcome from its newest round. Whether it is settled."""
        rnd = max(a["round"] for a in c["answers"])
        latest = [a for a in c["answers"] if a["round"] == rnd]
        said = [a["counted"] for a in latest if a["counted"]]
        gaps = "".join(f" · {a['session']} gave no answer" for a in latest if a["answer"] == "no answer")
        c["rounds"] = rnd
        if self.asks["shape"] == "an idea":
            c["outcome"], c["count"] = "listed", ""
            return True
        if not said:
            c["outcome"], c["count"] = "no answer", "no juror answered"
            return True
        tally = collections.Counter(said)
        if len(tally) == 1:
            c["outcome"], c["count"] = said[0], f"{len(said)} of {len(said)} said {said[0]}{gaps}"
            return True
        if not last:
            return False
        c["outcome"] = "split"
        c["count"] = " · ".join(f"{k} said {v}" for v, k in tally.most_common()) + gaps
        return True

    def checks(self) -> None:
        """Rounds over every claim: the first, then re-checks of claims still apart."""
        open_ = list(self.res["claims"])
        for rnd in range(1, RECHECKS + 2):
            if not open_:
                break
            self.round(open_, rnd)
            with self.lock:
                open_ = [c for c in open_ if not self.settle(c, rnd == RECHECKS + 1 or self.asks["shape"] == "an idea")]
            self.write()

    def advocates(self) -> None:
        """A case's For and Against: one juror per lens, one point each. Each fact becomes a claim."""
        sides = [s for s in self.plan["sessions"] if s["per"] == "lens"]
        lenses = self.plan["lenses"]
        self.begin(1, "Arguing", len(sides), len(lenses))

        def argued(text: str) -> bool:
            return any(b.get("point") and b.get("fact") for b in fields(text))

        def one(s):
            got = self.ask(s, [(f"{s['letter']}·{i}", advocate(self.plan, s, lens))
                               for i, lens in enumerate(lenses, 1)], "case", argued)
            return s, got

        with ThreadPoolExecutor(len(sides) or 1) as pool:
            done = list(pool.map(one, sides))
        facts = {}
        for s, got in done:
            for i, lens in enumerate(lenses, 1):
                g = got[f"{s['letter']}·{i}"]
                b = next((b for b in fields(g[0]) if b.get("point") and b.get("fact")), None) if g else None
                if not b:
                    continue
                key = even(b["fact"]).lower()
                if key not in facts:
                    facts[key] = {"n": len(facts) + 1, "text": b["fact"], "source": b.get("place", ""),
                                  "outcome": "", "count": "", "rounds": 0, "why": "", "answers": []}
                self.res["points"].append({"side": s["approach"], "session": s["letter"], "lens": lens,
                                           "point": b["point"], "fact": facts[key]["n"]})
        with self.lock:
            self.res["claims"] = list(facts.values())
        self.write()

    def conclude(self) -> None:
        """One fresh session writes the lead line and each claim's why, from the question and results alone."""
        case = self.plan["shape"] == "a case"
        item = "fact" if case else "claim"
        lines = [f"Question: {self.plan['question']}", f"Answer shape: {self.plan['shape']}", "", "Results:"]
        for c in self.res["claims"]:
            lines.append(f"{item.title()} {c['n']}: {c['text']}")
            lines.append(f"  Outcome: {c['outcome']} · {c['count']}" if c["count"] else f"  Outcome: {c['outcome']}")
            for a in [a for a in c["answers"] if a["round"] == c["rounds"]]:
                lines.append(f"  {a['juror']}: {a['answer']} · {a['why']} · quote {a['check']}: "
                             f"{even(a['quote'])} ({a['place']})")
        if case:
            lines += ["", "Points:"] + [f"  {p['side']} · {p['lens']} · {p['point']} · rests on fact {p['fact']}"
                                        for p in self.res["points"]]
        ask = ("You write a jury run's conclusion, from the question and the results below alone.\n"
               'Reply with one JSON object and nothing else: {"lead": "...", "why": {"1": "...", "2": "..."}}.\n'
               "lead: one short line. What the reader needs to care about, and what they do, like "
               f'"Act on one claim." or "Nothing needs you." It names each {item} it rests on.\n'
               f"why: one line per {item}, by its number: what settled its outcome, from its quotes, "
               "naming the file or page it rests on.\n"
               + ("On this case, the lead names the facts that decide it. Never say to do it, or not.\n" if case else "")
               + ("Each idea is one juror's answer. Name it by its juror, like A·1.\n"
                  if self.plan["shape"] == "an idea" else "")
               + "Add no fact the results do not hold. Never a percentage. Ten words at most per sentence.\n\n"
               + "\n".join(lines))
        stream = os.path.join(self.dir, "streams", "conclusion.jsonl")
        for _ in range(2):
            headless(command(ask, self.concluder["model"], [], self.concluder["effort"]), self.env, stream)
            got = heard(stream)
            self.spend("conclusion", got["usage"])
            m = re.search(r"\{.*\}", got["said"], re.S)
            try:
                said = json.loads(m.group(0)) if m else None
            except ValueError:
                said = None
            if isinstance(said, dict) and said.get("lead"):
                whys = said.get("why") if isinstance(said.get("why"), dict) else {}
                with self.lock:
                    self.res["conclusion"] = {"lead": str(said["lead"]).strip(),
                                              "model": next(iter(got["usage"]["models"]), "")}
                    for c in self.res["claims"]:
                        c["why"] = str(whys.get(str(c["n"]), "")).strip()
                return
        with self.lock:
            self.res["error"] = "The conclusion came back empty, twice."

    def go(self) -> None:
        if self.plan["shape"] == "a case":
            self.advocates()
        else:
            items = self.plan["claims"] or [{"n": 1, "text": "", "source": ""}]
            self.res["claims"] = [{**c, "outcome": "", "count": "", "rounds": 0, "why": "", "answers": []}
                                  for c in items]
            self.write()
        if self.res["claims"]:
            self.checks()
        with self.lock:
            self.res["state"] = "concluding"
        self.begin(3 if self.plan["shape"] == "a case" else 2, "Writing the conclusion")
        self.conclude()
        with self.lock:
            self.res["state"], self.res["done"] = "done", now()
        self.write()


def chat(res: dict, plan: dict) -> str:
    """What a run hands the asking session to say: the conclusion, one count
    line, each claim that does not hold, one line each, then the jury tab's
    address. Every quote stays on the tab."""
    noun, claims = "fact" if plan["shape"] == "a case" else "claim", res["claims"]
    out = [res["conclusion"].get("lead") or "No conclusion came back.", ""]
    if claims:
        tally = collections.Counter(c["outcome"] for c in claims)
        out.append(f"{len(claims)} {noun}{'s' if len(claims) > 1 else ''}: "
                   + ", ".join(f"{k} {'hold' if v == 'Holds' else v.lower()}" for v, k in tally.most_common()) + ".")
    for c in claims:
        if c["outcome"] == "Holds":
            continue
        out.append(" · ".join(x for x in (str(c["n"]), c["outcome"], c["count"], c["text"]) if x))
        if plan["shape"] == "an idea":
            out += [f"  {a['juror']}: {a['answer']} — {a['why']}" for a in c["answers"]
                    if a["round"] == c["rounds"] and a["answer"] != "no answer"]
    if res["error"]:
        out += ["", f"Error: {res['error']}"]
    out += ["", f"Every {noun} and quote: localhost:{serve.PORT}{serve.address('jury', res['session'])}"]
    return "\n".join(out)


def newest(nn: str) -> str:
    """Session NN's newest plan with no results beside it."""
    base = folder(nn)
    names = sorted((n for n in os.listdir(base) if os.path.isfile(os.path.join(base, n, "plan.json"))
                    and not os.path.exists(os.path.join(base, n, "results.json"))), reverse=True) \
        if os.path.isdir(base) else []
    return names[0] if names else ""


def refused(plan: dict) -> str:
    """Why a plan cannot run, or empty."""
    if plan.get("shape") not in SHAPES:
        return f"Its shape is not one of: {', '.join(SHAPES)}."
    letters = [s.get("letter") for s in plan.get("sessions", [])]
    if len(set(letters)) != len(letters) or not letters:
        return "Its sessions need one letter each."
    for s in plan["sessions"]:
        if s.get("model") not in MODELS or s.get("effort") not in panes.EFFORTS \
                or s.get("reads") not in READS or s.get("per") not in ("claim", "lens"):
            return f"Session {s.get('letter')} holds a model, effort, reads or per it cannot take."
    if plan["shape"] == "a case" and not (plan.get("lenses") and any(s["per"] == "lens" for s in plan["sessions"])):
        return "A case needs its lenses, and a session per lens."
    if not any(s["per"] == "claim" for s in plan["sessions"]):
        return "It needs a session per claim."
    end = concluder(plan)
    if end["model"] not in MODELS or end["effort"] not in panes.EFFORTS:
        return "Its concluder holds a model or effort it cannot take."
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["draft", "run", "words"])
    ap.add_argument("nn")
    ap.add_argument("run", nargs="?", default="")
    args = ap.parse_args()
    nn = f"{int(args.nn):02d}"
    if args.verb == "draft":
        print(os.path.relpath(draft(nn, json.load(sys.stdin)), ROOT))
        return
    if args.verb == "words":
        print(words(nn))
        return
    name = args.run or newest(nn)
    if not name or not os.path.isfile(os.path.join(folder(nn), name, "plan.json")):
        sys.exit(f"No plan to run in {os.path.relpath(folder(nn), ROOT)}.")
    if os.path.exists(os.path.join(folder(nn), name, "results.json")):
        sys.exit(f"Run {name} was already launched.")
    run = Run(nn, name)
    why = refused(run.plan)
    if why:
        sys.exit(f"Run {name} cannot run. {why}")
    try:
        run.go()
    except Exception as e:
        run.res["state"], run.res["error"] = "failed", f"{type(e).__name__}: {e}"
        run.write()
        raise
    print(chat(run.res, run.plan))


if __name__ == "__main__":
    main()
