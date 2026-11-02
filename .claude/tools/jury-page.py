#!/usr/bin/env python3
"""jury-page.py — the jury tab: a jury's plan before Launch, then its results.

/jury drafts a plan for the session I typed it in, in that session's
newest run folder: jury.py's docstring holds the format. This page draws
it: the typed question, its context, its claims, each with the source it
names, its answer shape, and each jury session, its approach, its model
and its effort, as the launch page's pills. The final session, writing the
conclusion, follows as its own row, its model and effort pills saved under
concluder, jury.py's CONCLUDER until I pick. No account picker: jury
sessions run on the asking session's account. Every word takes an edit in
place and every pill a click, saved into plan.json as I go. Launch types
/jury-run and the run's name into the session's pane, as I could type it
myself. Pressed while the session works, the command waits for its turn's
end, as every command does.

Before Launch, a case's checks read "up to" their facts, one per
advocate. Once results.json lands, the plan locks, and the head names the
step running, how many of its jurors run at once, and how many of the
step's are done. Once it is done, the head says how many claims and
jurors, and when, and the page draws the results instead. The final
session's conclusion leads, one line, then the
claims in the plan's order, each its outcome, its count and its why. On a
case, each fact names the side, the lens and the point resting on it. A
click on a claim opens the jurors of its last round, each its answer,
reason and quote. A quote not found, or none, says what its answer counted
as. A web page's quote that could not be fetched reads "quote unchecked",
beside its link. The run's cost sits at the foot. The plan folds into one
line beneath.

Its looks are borrowed: page.py's shell and the clarify page's items, the
launch page's rows and pills, the transcript page's table.

  jury-page.py try FILE [--port 1112]   the tab, drawn from a fixture file alone

A fixture holds the session's number and tag, then plan.json and
results.json whole, under plan and results.

1100 imports this file for render, take, key, heard and tab: the tab
shows once a plan lands, and waits on me only while its plan waits for
Launch. Only try runs a server.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import models  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

jury = page.tool("jury")
launcher = page.tool("launch-page")

# Picks are counted; ideas and cases are listed, never counted.
COUNTED = jury.SHAPES[:3]
# The launch page's place blue, for the answer shape's pills.
PLACE = "#60a5fa"
# Each answer's colour, on its chip, by its word in lower case. Any other,
# as no answer, stays grey. Stand-in: every one.
COLOUR = {"holds": "var(--green)", "yes": "var(--green)", "broken": "var(--red)", "no": "var(--red)",
          "split": "var(--gold)", "unproven": "var(--gold)", jury.UNSURE: "var(--gold)"}
GAP = "no answer"
# Launch types into a session at its prompt, or while it works: a command
# typed then waits for its turn's end. Never at a dialog.
SAFE = ("idle", "shell", "busy")


# ---- the borrowed looks -----------------------------------------------------

TABLE = page.table()


def model_pills() -> list:
    """The launch page's model pills, each valued by the family --model
    takes, as plan.json holds it."""
    rank = lambda fm: list(launcher.SHADES).index(fm[0]) if fm[0] in launcher.SHADES else len(launcher.SHADES)
    return [(f, models.name(m), launcher.SHADES.get(f, launcher.NEW))
            for f, m in sorted(models.families(), key=rank) if f in jury.MODELS]


# This page's own rules, after the shell's, the launch page's and the table's.
CSS = """<style>
  /* The plan's sessions sit under its item, at its sides. */
  .jt-rows { padding:0 24px 24px; }
  .jt-rows > h2 { margin:0 0 6px; }
  .jt-rows > .row + h2 { margin-top:14px; }
  .jt-rows .row { cursor:default; padding:8px 10px; margin-bottom:8px; }
  .jt-rows .line { font-size:12px; }
  .jt-how { color:var(--dim); }
  .banner { margin:12px 24px 0; }
  /* A word I edit in place looks as it reads, until it holds the cursor. */
  [contenteditable] { cursor:text; border-radius:3px; }
  [contenteditable]:focus { outline:1px solid var(--blue); outline-offset:2px; }
  /* The results: the claims' table fills the width, its claim and why
     cells wrapping. A row opens on a click. */
  .jt-table .grid { display:block; }
  .jt-table table { width:100%; }
  .jt-table td.jt-wrap { white-space:normal; }
  .jt-table td .chip { vertical-align:baseline; }
  .jt-row { cursor:pointer; }
  /* A case's points under the fact they rest on, in line with its text. */
  .jt-point { margin:3px 0 0 44px; }
  /* The last claim keeps the table's last line, its jurors folded under it. */
  .jt-table tbody tr:nth-last-child(2):has(+ tr[hidden]) td { border-bottom:0; }
  /* Each claim's jurors, once unfolded, side by side. */
  .jt-jurors { display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:8px; }
  #items .jt-jurors .prop { margin:0; min-width:0; }
  /* A long name, like a setting's or a file's, breaks where it must. */
  .jt-jurors .prop * { overflow-wrap:anywhere; }
  /* My phone: every pill and button takes a fingertip, 44 by 44 at least,
     Apple's least touch size: page rule 20. */
  @media (hover:none) and (pointer:coarse) {
    .grp, .pills { gap:4px; }
    .pills button, header.top .acts button { min-height:44px; min-width:44px; touch-action:manipulation; }
    .pills button { padding:0 10px; font-size:12px; }
  }
</style>"""

SCRIPT = r"""<script>
const PLAN = %PLAN%;
let timer = 0;
const flush = () => { clearTimeout(timer); timer = 0; return post({act: 'plan', plan: JSON.stringify(PLAN)}); };
const save = () => { clearTimeout(timer); timer = setTimeout(flush, 300); };
const put = (path, v) => {
  const ks = path.split('.'), last = ks.pop();
  ks.reduce((o, k) => o[k], PLAN)[last] = v;
};
document.querySelectorAll('[data-f]').forEach(el => {
  el.addEventListener('input', () => { put(el.dataset.f, el.textContent.trim()); save(); });
  el.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); el.blur(); } });
});
document.querySelectorAll('.pills[data-k] button').forEach(b => b.addEventListener('click', () => {
  const k = b.parentNode.dataset.k;
  b.parentNode.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  put(k, b.dataset.v);
  if (k === 'shape') document.querySelectorAll('.jt-shape').forEach(e => { e.textContent = b.dataset.v; });
  save();
}));
async function launch(b) {
  if (timer) await flush();
  pressed(b, {act: 'launch'});
}
</script>"""

# A claim's row opens its jurors under it, and folds them again.
UNFOLD = r"""<script>
document.querySelectorAll('tr.jt-row').forEach(tr => tr.addEventListener('click', () => {
  const box = tr.nextElementSibling, shut = box.hidden;
  box.hidden = !shut;
  tr.querySelector('.jt-arrow').textContent = shut ? '▾' : '▸';
}));
</script>"""


# ---- the parts ----------------------------------------------------------------

esc = page.esc


def chip(word: str) -> str:
    """An answer or an outcome, in lower case, on its colour."""
    word = word.lower()
    style = f' style="--c:{COLOUR[word]}"' if word in COLOUR else ""
    return f'<span class="chip"{style}>{esc(word)}</span>'


def place(at: str) -> str:
    return (f'<a class="link" href="{esc(at)}" target="_blank" rel="noopener">{esc(at)}</a>'
            if at.startswith("http") else esc(at))


def clock(stamp: str) -> str:
    """An ISO time as my clock reads it, 16:20."""
    try:
        return datetime.datetime.fromisoformat(stamp).strftime("%H:%M")
    except (TypeError, ValueError):
        return ""


def edit(path: str, text: str, live: bool, tag: str = "span", cls: str = "") -> str:
    """A word I edit in place, saved under `path` in the plan. Once
    launched, it is only text."""
    attrs = f' class="{cls}"' if cls else ""
    if live:
        attrs += f' data-f="{path}" contenteditable="plaintext-only" spellcheck="false"'
    return f"<{tag}{attrs}>{esc(text)}</{tag}>"


def sizes(plan: dict) -> tuple:
    """How many claims or lenses, and how many jurors in all. A case's
    claims are its facts, one per advocate at most."""
    lenses = len(plan["lenses"])
    claims = (lenses * sum(s["per"] == "lens" for s in plan["sessions"]) if plan["shape"] == "a case"
              else len(plan["claims"]))
    items = {"claim": claims, "lens": lenses}
    return items, sum(items[s["per"]] for s in plan["sessions"])


def jurors_said(plan: dict) -> str:
    """The plan's jurors, an upper bound on a case."""
    return f"{'up to ' if plan['shape'] == 'a case' else ''}{page.count(sizes(plan)[1], 'juror')}"


def weighs(plan: dict) -> str:
    """What a plan weighs: its claims, else its lenses."""
    if plan["claims"]:
        return page.count(len(plan["claims"]), "claim")
    return page.count(len(plan["lenses"]), "lens", "lenses")


def progress(plan: dict, res: dict) -> str:
    """The head once launched: the step, how many run at once, and how many
    of the step's are done. Once done, the claims, the jurors and when."""
    noun = "fact" if plan["shape"] == "a case" else "claim"
    if res.get("state") == "done":
        n = len(res["claims"])
        return (f"Done · {n} {noun}{'s' if n != 1 else ''} · {res['jurors']['asked']} jurors · "
                f"{clock(res.get('launched'))} to {clock(res.get('done'))}")
    st = res.get("step") or {}
    line = f"Step {st['n']} of {st['steps']} · {st['what']}" if st else "Starting"
    if st.get("asked"):
        line += f" · {st['at_once']} at once · {st['answered']} of {st['asked']} done"
    return f"Failed · {line}" if res.get("state") == "failed" else line


def session_row(i: int, s: dict, plan: dict, live: bool) -> str:
    n = sizes(plan)[0][s["per"]]
    count = (f"up to {n} facts · 1 subagent each" if plan["shape"] == "a case" and s["per"] == "claim"
             else f"{n} subagents · 1 per {s['per']}")
    off = "" if live else " disabled"
    pills = lambda key, options: (f'<span class="grp"><span class="lbl {key}">{key}</span>'
                                  + launcher.pills(f"sessions.{i}.{key}", options, s[key], off) + "</span>")
    return (f'<div class="row"><div class="line"><span class="chip g">{esc(s["letter"])}</span>'
            f'{edit(f"sessions.{i}.approach", s["approach"], live, "b")}'
            f'<span class="lbl">{count} · {min(n, jury.AT_ONCE)} at once</span></div>'
            f'{edit(f"sessions.{i}.how", s["how"], live, "div", "line jt-how")}'
            f'<div class="line">{pills("model", model_pills())}{pills("effort", launcher.EFFORTS)}'
            '<span class="grp"><span class="lbl">returns</span>each juror\'s answer, unchanged. '
            'It never merges them.</span></div>'
            f'<div class="line"><span class="lbl">its subagents differ</span>by {s["per"]}, one each'
            f'<span class="grp"><span class="lbl">answers</span><span><span class="jt-shape">{esc(plan["shape"])}'
            '</span> · why, in one line · its quote, with file and line</span></span></div></div>')


def concluder_row(plan: dict, live: bool) -> str:
    """The final session, once every jury session ends: its model and its
    effort as pills, saved under concluder in the plan."""
    s, off = plan["concluder"], "" if live else " disabled"
    letters = [x["letter"] for x in plan["sessions"]]
    # A plan with no jury session still draws: its conclusion is the first.
    after = ("the jury" if not letters else letters[0] if len(letters) == 1
             else ", ".join(letters[:-1]) + " and " + letters[-1])
    own = chr(ord(letters[-1]) + 1) if letters else "A"
    pills = lambda key, options: (f'<span class="grp"><span class="lbl {key}">{key}</span>'
                                  + launcher.pills(f"concluder.{key}", options, s[key], off) + "</span>")
    return (f'<h2>Then the conclusion · 1 session</h2><div class="row"><div class="line">'
            f'<span class="chip g">{own}</span><b>Writes the conclusion</b>'
            f'<span class="lbl">no subagents · starts once {after} end</span></div>'
            '<div class="line jt-how">Reads the question and the results alone, never your conversation. '
            'Each sentence names its claim.</div>'
            f'<div class="line">{pills("model", model_pills())}{pills("effort", launcher.EFFORTS)}'
            '<span class="grp"><span class="lbl">returns</span>one line, then each claim\'s outcome, count and why.'
            '</span></div></div>')


def kick(plan: dict) -> str:
    at = plan["from"].get("at", "")
    return f'<p class="kick">{esc(plan["from"].get("label", ""))}{" · " + place(at) if at else ""}</p>'


def plan_part(plan: dict, live: bool) -> str:
    """The plan, before Launch: the typed question, then its jury sessions."""
    claims = "".join(f'<p><span class="chip g">{c["n"]}</span> {edit(f"claims.{k}.text", c["text"], live)} '
                     f'<span class="dim">· names: {edit(f"claims.{k}.source", c["source"] or "none", live)}</span></p>'
                     for k, c in enumerate(plan["claims"]))
    lenses = "".join(f'<p><span class="chip g">{k + 1}</span> {edit(f"lenses.{k}", w, live)}</p>'
                     for k, w in enumerate(plan["lenses"]))
    shapes = launcher.pills("shape", [(s, s, PLACE) for s in jury.SHAPES], plan["shape"], "" if live else " disabled")
    rule = ("Each claim gets a count, like 4 of 5 said no. Never a percentage." if plan["shape"] in COUNTED
            else "Ideas and cases are listed, never counted.")
    rows = "".join(session_row(i, s, plan, live) for i, s in enumerate(plan["sessions"]))
    return ('<div id="items"><div class="item">'
            f'{kick(plan)}{edit("question", plan["question"], live, "h1", "q")}'
            + ('<h2 class="sec">Context</h2>' if plan["context"] else "")
            + "".join(edit(f"context.{k}", line, live, "p") for k, line in enumerate(plan["context"]))
            + (f'<h2 class="sec">Claims · {len(plan["claims"])}</h2>{claims}' if plan["claims"] else "")
            + (f'<h2 class="sec">Lenses · {len(plan["lenses"])}</h2>{lenses}' if plan["lenses"] else "")
            + f'<h2 class="sec">Answer shape</h2>{shapes}<p class="srcs">{rule}</p></div></div>'
            f'<div class="jt-rows"><h2>Jury sessions · {len(plan["sessions"])} · {jurors_said(plan)}</h2>'
            f'{rows}{concluder_row(plan, live)}</div>')


def juror(a: dict, sessions: dict) -> str:
    """One juror's answer, its reason and its quote, named by its session."""
    head = (f'<div class="ph">{chip(a["answer"])} {esc(a["juror"])} · '
            f'{esc(sessions.get(a["session"], {}).get("approach", ""))} · {esc(models.name(a.get("model", "")))}</div>')
    if a["answer"] == GAP:
        return f'<div class="prop">{head}<p class="pw">No answer, after one retry.</p></div>'
    check, counted = a.get("check", ""), a.get("counted", "")
    where = {"unchecked": f"{place(a.get('place', ''))} · quote unchecked",
             "not found": f"{place(a.get('place', ''))} · quote not found, counted {esc(counted)}",
             "none": f"No quote · counted {esc(counted)}"}.get(check, place(a.get("place", "")))
    quote = f'<blockquote class="pq">{esc(a["quote"])}</blockquote>' if a.get("quote") else ""
    return f'<div class="prop">{head}<p>{esc(a.get("why", ""))}</p>{quote}<p class="pw">{where}</p></div>'


def results_part(plan: dict, res: dict) -> str:
    """The conclusion, the claims each with its outcome, the cost, then
    the plan, folded."""
    sessions = {s["letter"]: s for s in plan["sessions"]}
    argued = {}
    for p in res.get("points") or []:
        argued.setdefault(p["fact"], []).append(p)
    rows = ""
    for c in res["claims"]:
        last = [a for a in c["answers"] if a.get("round", 1) == c.get("rounds", 1)]
        points = "".join(f'<div class="dim jt-point">{esc(p["side"])} · {esc(p["lens"])} · {esc(p["point"])}</div>'
                         for p in argued.get(c["n"], []))
        rows += (f'<tr class="jt-row"><td class="jt-wrap"><span class="dim jt-arrow">▸</span> '
                 f'<span class="chip g">{c["n"]}</span> {esc(c["text"])}{points}</td>'
                 f'<td>{chip(c["outcome"])}</td><td>{esc(c["count"])}</td>'
                 f'<td class="jt-wrap">{esc(c["why"])}</td></tr>'
                 f'<tr hidden><td colspan="4" class="jt-wrap"><div class="jt-jurors">'
                 + "".join(juror(a, sessions) for a in last) + "</div></td></tr>")
    conclusion, cost = res.get("conclusion") or {}, (res.get("cost") or {}).get("line", "")
    return ('<div id="items"><div class="item">'
            f'<p class="kick">Conclusion · the final session · {esc(models.name(conclusion.get("model", "")))}'
            ' · from the results alone</p>'
            f'<h1 class="q">{esc(conclusion.get("lead", ""))}</h1><div class="nt jt-table"><div class="grid"><table>'
            '<thead><tr><th>Claim</th><th>Outcome</th><th>Count</th><th>Why</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></div>'
            + (f'<p class="srcs">{esc(cost)}</p>' if cost else "")
            + '</div><div class="item"><div class="note">'
            f'Plan · {page.count(len(plan["sessions"]) + 1, "session")} · {jurors_said(plan)} · '
            f'launched {clock(res.get("launched"))}, done {clock(res.get("done"))}</div></div></div>')


def draw(d: dict, tail: str = "") -> str:
    """The tab, from a run: d holds the session's nn and tag, and the
    run's plan and results, None until launched. `tail` is its
    watch."""
    plan, res = d["plan"], d.get("results")
    if not plan:
        return page.render(f"{d['nn']}-jury", [("", page.blank("No jury waits") + tail)],
                           page.head("jury", d["tag"]), refresh=0)
    plan = {**plan, "concluder": jury.concluder(plan)}
    # The jury sessions, then the final session.
    started = len(plan["sessions"]) + 1
    script, banner = "", ""
    if res and res.get("state") == "done":
        mid = progress(plan, res)
        go = '<button class="sent" disabled>Done</button>'
        body = results_part(plan, res)
        script = UNFOLD
    else:
        live = not res
        tip = f"Types /jury-run {plan['run']} into session {d['nn']}'s pane."
        mid = (f"Plan · {weighs(plan)} · {page.count(started, 'session')} · {jurors_said(plan)}" if live
               else progress(plan, res))
        go = (f'<button id="launch" title="{esc(tip)}"{"" if live else " disabled"} '
              f'onclick="launch(this)">{"Launch" if live else "Launched"} · {started}</button>')
        banner = f'<div class="banner">{esc(res["error"])}</div>' if res and res.get("error") else ""
        body = plan_part(plan, live)
        if live:
            script = page.POST + page.TYPING + SCRIPT.replace("%PLAN%", json.dumps(plan).replace("</", "<\\/"))
    # The clarify page's head, so its phone sizes hold, with the jury's own family.
    rail = (f'<header class="top fam clarify"><span class="who">{page.family("jury")}<span class="dim">·</span>'
            f'<b>{esc(d["tag"])}</b></span><span class="mid">{esc(mid)}</span>'
            f'<span class="acts"><span class="group">{go}</span></span></header>\n')
    return page.render(f"{d['nn']}-jury", [("", launcher.CSS + TABLE + CSS + banner + body + tail + script)],
                       rail, refresh=0)


# ---- my edits -----------------------------------------------------------------

def merged(plan: dict, sent: dict) -> dict:
    """The plan with my edits from the page: only its words, its shape, and
    each session's model and effort, the final session's too, each from
    what its pills offer. Its picks follow its shape."""
    out = json.loads(json.dumps(plan))
    words = lambda v, was: v if isinstance(v, str) and v.strip() else was
    each = lambda got, was: [words(got[k] if k < len(got) else None, w) for k, w in enumerate(was)]
    out["question"] = words(sent.get("question"), plan["question"])
    out["context"] = each(sent.get("context", []), plan["context"])
    out["lenses"] = each(sent.get("lenses", []), plan["lenses"])
    for c, got in zip(out["claims"], sent.get("claims", [])):
        c["text"] = words(got.get("text"), c["text"])
        source = got.get("source")
        c["source"] = "" if source == "none" else words(source, c["source"])
    for s, got in zip(out["sessions"], sent.get("sessions", [])):
        s["approach"], s["how"] = words(got.get("approach"), s["approach"]), words(got.get("how"), s["how"])
        s["model"] = got["model"] if got.get("model") in jury.MODELS else s["model"]
        s["effort"] = got["effort"] if got.get("effort") in panes.EFFORTS else s["effort"]
    end, got = jury.concluder(plan), sent.get("concluder") or {}
    end["model"] = got["model"] if got.get("model") in jury.MODELS else end["model"]
    end["effort"] = got["effort"] if got.get("effort") in panes.EFFORTS else end["effort"]
    out["concluder"] = end
    if sent.get("shape") in jury.SHAPES and sent["shape"] != plan["shape"]:
        out["shape"] = sent["shape"]
        out["picks"] = (jury.PICKS.get(out["shape"]) or plan["picks"]) if out["shape"] in COUNTED else []
    return out


# ---- a session's run ------------------------------------------------------------

def newest(nn: str) -> str:
    """Session NN's newest run folder holding a plan, or ""."""
    base = jury.folder(nn)
    names = [n for n in registry.listing(base) if os.path.isfile(os.path.join(base, n, "plan.json"))]
    return os.path.join(base, max(names)) if names else ""


def read(path: str):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def world(nn: str) -> dict:
    """Everything the tab draws for session NN, in a fixture's shape."""
    run, held = newest(nn), registry.entries()
    return {"nn": nn, "tag": plans.tag(nn, plans.owners(held)),
            "plan": read(os.path.join(run, "plan.json")) if run else None,
            "results": read(os.path.join(run, "results.json")) if run else None}


def key(nn: str) -> str:
    """What the tab reloads on: its run's two files. My own save takes the
    key it left, through page.py's post(), so it never reloads the page."""
    run, words = newest(nn), []
    for name in ("plan.json", "results.json"):
        try:
            with open(os.path.join(run, name), "rb") as f:
                words.append(f.read())
        except OSError:
            words.append(b"")
    return hashlib.sha1(b"\0".join([run.encode()] + words)).hexdigest()[:12]


def render(nn: str) -> str:
    return draw(world(nn), page.watch(key(nn)))


def take(nn: str, form: dict) -> str:
    """My edits, saved into plan.json, or Launch. A launched plan takes
    neither. Launch types at the session's prompt, or while it works; a
    dialog waiting, or a pane gone, is refused in one sentence."""
    run, act = newest(nn), (form.get("act") or [""])[0]
    if not run or os.path.exists(os.path.join(run, "results.json")):
        return ""
    plan = read(os.path.join(run, "plan.json"))
    if not plan:
        return ""
    if act == "plan":
        try:
            jury.save(os.path.join(run, "plan.json"), merged(plan, json.loads((form.get("plan") or ["{}"])[0])))
        except (ValueError, AttributeError, TypeError):
            pass
        return ""
    if act != "launch":
        return ""
    why, _, pane = page.typable(nn, SAFE)
    if why:
        return why
    line = f"/jury-run {plan['run']}"
    return serve.Typing(lambda: "" if panes.say(pane, line) else page.gone(nn))


def tab(nn: str):
    """Session NN's tab on 1100, as (its line, the file it began with,
    whether it waits on me), or None with no plan. It shows from a plan
    landing, for the newest run, and waits on me only while its plan waits
    for Launch."""
    run = newest(nn)
    plan = read(os.path.join(run, "plan.json")) if run else None
    if not plan:
        return None
    res = read(os.path.join(run, "results.json"))
    if not res:
        return f"Plan · {weighs(plan)}", os.path.join(run, "plan.json"), True
    st, state = res.get("step") or {}, res.get("state")
    label = (f"Step {st['n']} of {st['steps']}" + (f" · {st['answered']} of {st['asked']} done" if st.get("asked") else "")
             if st else "Starting")
    label = "Done" if state == "done" else f"Failed · {label}" if state == "failed" else label
    return label, os.path.join(run, "plan.json"), False


def heard() -> list:
    """What 1100 hears for every session's tab: its jury folder, where a
    run lands, and its newest run's folder, where each file is swapped in."""
    out = []
    for nn in registry.listing(registry.WORK):
        if re.fullmatch(r"\d{2}", nn) and os.path.isdir(jury.folder(nn)):
            out += [jury.folder(nn), newest(nn)]
    return [p for p in out if p]


# ---- tried alone ----------------------------------------------------------------

def fixture(path: str):
    """A server's render, take, route and key for one fixture file. /plan
    draws it with its results set aside. Launch types nothing: it prints
    the line it would type."""
    load, mark = serve.fixture(path)

    def shown(bare: bool) -> str:
        d = load()
        if bare:
            d["results"] = None
        return draw(d, page.watch(mark()))

    def pressed(form: dict, _path: str) -> str:
        d, act = load(), (form.get("act") or [""])[0]
        if act == "launch":
            print(f"Launch would type into session {d['nn']}'s pane: /jury-run {d['plan']['run']}", flush=True)
        elif act == "plan":
            try:
                d["plan"] = merged(d["plan"], json.loads((form.get("plan") or ["{}"])[0]))
            except (ValueError, AttributeError, TypeError):
                return ""
            jury.save(path, d)
        return ""

    def route(p: str):
        bare = p.partition("?")[0]
        if bare.endswith("/key"):
            return mark()
        return shown(True) if bare == "/plan" else None

    return (lambda: shown(False)), pressed, route, mark


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    tried = sub.add_parser("try")
    tried.add_argument("file")
    tried.add_argument("--port", type=int, default=1112)
    args = ap.parse_args()
    path = os.path.abspath(args.file)
    shown, pressed, route, mark = fixture(path)
    serve.run(f"jury-page-{args.port % 100:02d}", args.port, shown, take=pressed, route=route,
              keyof=mark, hears=lambda: [path])


if __name__ == "__main__":
    main()
