#!/usr/bin/env python3
"""handover-page.py — the page that hands a session over, drawn by 1100 at /p/handover/NN.

A session whose context reaches the threshold set on 1100/system gets
this page, its own, as a launch page is its session's own. It waits in
its team's hub, a tab like any other wait, until the session is handed
over. A session under the threshold has none, nor does one a driver
drives, while it is driven: its driver hands it over. lib/context.py
reads the context and keeps the threshold.

The page says two things. Its session is over the limit: one meter, the
threshold's tick on it. Then its successor's account, model and effort,
on the launch page's own pills, each pre-picked as the successor would
launch now: what lib/handover.py's carried() keeps, else the order's next
account, and the model and effort set on System. A pill picked names its
value, and wins. The pill of System's own value names next or system:
the order's next over a saved account, and System over what the seat was
named. The picks ride in the address, so a reload keeps them.

Hand over sits in the head, where Launch sits on a launch page. One press
types /handover-prepare into the session's pane. Once that hook says it
saved, it types /handover-resume NN with the successor's account, and
each model or effort I picked. Both are hooks, so no model turn runs. An
account left on next takes the order's turn then, and goes in the line.

Nothing is typed into a session working, nor at a dialog, whose Return
would approve its first option, nor into a pane gone, nor into a shell
Claude has left. The page says why. While its session works, Hand over is
greyed, and takes no press. A step failing after the save names the
copy first, so I know my conversation is safe.

The press is lib/handover.py's. A driver runs it too, on the sessions it
drives. Pressed here, it runs as a program of its own, this file's press,
so it keeps running while 1100 restarts. A press names its act,
handover; a post naming none hands nothing over. Each step goes
into the seat's handover.json, which the page draws and 1100 hears.
A press a driver runs shows here too, as it runs. Handed over,
the seat holds a fresh session. After a pause the file goes, and the page
with it. A step whose press died is read as failed, so it never locks the
page, and one handed over as gone.

System's part, both thresholds and a box to set each, is drawn here too.

1100 imports this file. Its server serves LIVE, its home asks waiting,
and System draws system_part. Nothing here runs a server.

  handover-page.py press NN PANE SINCE ACCOUNT MODEL EFFORT
                                  the press Hand over starts, as its own program
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import context  # noqa: E402
import handover  # noqa: E402
import launch  # noqa: E402
import live  # noqa: E402
import models  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402

launcher = page.tool("launch-page")

# Hand over's word while each step runs.
PRESSED = {"saving": "Saving…", "launching": "Launching…", "done": "Handed over"}
WORKING = "Working. Hand over opens once its turn ends."
# Stand-in: the shade of a kept model no pill offers, as opus, a name
# --model takes.
KEPT = "#8a7fb0"


def model_pills(kept: dict) -> list:
    """The launch page's model pills, and one more for a kept model none
    offers, so the page shows what its successor launches on."""
    have, offered = kept.get("model", ""), launcher.offered()
    return offered + ([(have, models.name(have), KEPT)] if have and have not in
                      [v for v, _, _ in offered] else [])


# ---- the press ----------------------------------------------------------------

def take(nn: str, form: dict) -> str:
    """Hand over, pressed. Whatever would type into the wrong place is
    refused, in one sentence. Otherwise the press starts, and the page
    follows its steps."""
    get = lambda k: (form.get(k) or [""])[0]
    pick = {"account": get("account"), "model": get("model"), "effort": get("effort")}
    offered = lambda pills: [v for v, _, _ in pills]
    if (pick["account"] not in ["", handover.NEXT, *offered(launcher.ACCOUNTS)]
            or pick["model"] not in ["", handover.SYSTEM, *offered(model_pills(handover.carried(nn)))]
            or pick["effort"] not in ["", handover.SYSTEM, *offered(launcher.EFFORTS)]):
        return "Pick an account, a model and an effort from the pills. Nothing was typed."
    if handover.progress(nn).get("step") in PRESSED:
        return f"A handover of session {nn} is already under way. Nothing was typed."
    why, mine, pane = page.typable(nn, handover.SAFE)
    if why:
        return why
    since = context.crossed(mine.get("transcript", ""), context.threshold())
    handover.note(nn, step="saving", since=since)
    spawn([*PRESS, nn, pane, str(since), pick["account"], pick["model"], pick["effort"]])
    return ""


# The press runs as a program of its own, so it keeps running while 1100
# restarts: this file's press verb, the pane and the picks after it.
PRESS = [sys.executable, os.path.abspath(__file__), "press"]


def spawn(argv: list) -> None:
    """One program started on its own, outliving whoever started it."""
    subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, cwd=registry.ROOT)


def pressing(nn: str, pane: str, since: int, pick: dict) -> None:
    """The press, in its own program. Its first step names this program,
    so the page reads it as running while 1100 is down. A press that
    raises says so, rather than reading as cut short."""
    handover.note(nn, step="saving", since=since)
    try:
        handover.press(nn, registry.entries().get(nn) or {}, pane, pick, since)
    except Exception as e:
        handover.note(nn, step="failed", said=f"The press failed: {type(e).__name__}: {e}. Nothing more was typed.")


def pressed(nn: str, form: dict) -> str:
    """A press on the page. It names its act, handover; anything else is
    refused, and nothing is handed over."""
    if (form.get("act") or [""])[0] != "handover":
        return "This page takes no such press. Nothing was typed."
    return take(nn, form)


# ---- what waits -----------------------------------------------------------------

def waiting(nn: str, mine: dict, running: dict, limit: int):
    """Whether seat NN's page waits on me, as (label, since), or None.

    It waits while its session's context is at or past `limit`, since the
    moment it rose there, and while its press runs, until the pause after
    Handed over. A session my assistant drives has none while it is
    driven, though a press already running still shows. `running` is
    registry.claude_records().
    """
    press = handover.progress(nn)
    if press.get("step") in PRESSED:
        return PRESSED[press["step"]], press.get("since", 0)
    pct = context.percent(mine, running)
    if pct is None or pct < limit or successor.driven(nn):
        return None
    return f"{pct}%, past {limit}%", context.crossed(mine.get("transcript", ""), limit)


def world(nn: str) -> dict:
    """Everything the page draws for seat NN."""
    held, running = registry.entries(), registry.claude_records()
    mine = held.get(nn) or {}
    rec = running.get(mine.get("session_id"))
    return {"nn": nn, "tag": plans.tag(nn, plans.owners(held)),
            "ctx": context.percent(mine, running), "threshold": context.threshold(),
            "live": page.word(rec),
            "press": handover.progress(nn), "order": accounts.read(), "fallback": accounts.FALLBACK,
            "kept": handover.carried(nn), "system": launch.default()}


# ---- the page -------------------------------------------------------------------

# The launch page's own look draws the pills and their row. This adds the
# meter, and the line that says each step.
CSS = "<style>\n" + page.shared("handover.css") + "</style>"


def say(d: dict, busy: bool) -> str:
    """The line under the pills: each step as it runs, a failure's sentence,
    or why Hand over is greyed."""
    press = d["press"]
    step = press.get("step", "")
    if step == "saving":
        return f"Typed <code>{handover.PREPARE}</code>. Saving its conversation."
    if step == "launching":
        return (f"Saved as {page.esc(press.get('copy', ''))}. "
                f"Typed <code>{page.esc(press.get('typed', ''))}</code>.")
    if step == "done":
        return f"Seat {d['nn']} holds a fresh session now. Its old pane closed."
    if step == "failed":
        return page.esc(press.get("said", ""))
    return WORKING if busy else ""


def draw(d: dict, watch: str) -> str:
    """The page, from what world() reads.

    `watch` is live.watch()'s, and opens the body. The page's own script
    is .claude/pages/scripts/handover.js, the same in every state, and its picks
    go beside it as data."""
    nn, step, ctx, limit = d["nn"], d["press"].get("step", ""), d["ctx"], d["threshold"]
    hot = ctx is not None and ctx >= limit
    if step not in PRESSED and not hot:
        return page.render(f"{nn}-handover", [("", watch + page.blank("No handover waits") + scripts({}))],
                           page.head("handover", d["tag"]), refresh=0)
    off = " disabled" if step in PRESSED else ""
    busy = not off and d["live"] == "working"
    tip = WORKING if busy else f"Types {handover.PREPARE}, then /handover-resume {nn} with these settings, into {nn}'s pane."
    sent = ' class="sent"' if step == "done" else ""
    go = (f'<button id="go"{sent}{" disabled" if off or busy else ""} '
          f'title="{page.esc(tip)}">{page.icon("check", 13) if step == "done" else ""}'
          f'{PRESSED.get(step, "Hand over")}</button>')
    heat = " hot" if hot else ""
    gauge = (f'<div class="gauge"><span class="meter"><span class="fill{heat}" style="width:{ctx or 0}%"></span>'
             f'<span class="tick" style="left:{limit}%"></span><span class="mark" style="left:{limit}%">{limit}%</span>'
             f'</span><span class="pct{heat}">{"–" if ctx is None else f"{ctx}%"}</span></div>')
    o, kept = d["order"], d["kept"]
    turn = o["order"][o["next"]] if o["order"] else d["fallback"]
    # The launch page's own pills. System's own value, now, rides as next
    # or system. Each group pre-picks what the successor launches on: a
    # kept value, else System's. The script marks a pick the address holds.
    now = {"account": turn, "model": d["system"]["model"], "effort": d["system"]["effort"]}
    own = {"account": handover.NEXT, "model": handover.SYSTEM, "effort": handover.SYSTEM}
    pre = {k: kept[k] if kept.get(k) and kept[k] != now[k] else own[k] for k in own}
    groups = [("account", "acct", launcher.ACCOUNTS), ("model", "model", model_pills(kept)),
              ("effort", "effort", launcher.EFFORTS)]
    row = ('<div class="row"><div class="line">' + "".join(
        f'<span class="grp"><span class="lbl {cls}">{k}</span>'
        + launcher.pills(k, [(own[k] if v == now[k] else v, label, shade) for v, label, shade in opts], pre[k], off)
        + '</span>' for k, cls, opts in groups) + '</div></div>')
    line = say(d, busy)
    part = (f'<div class="hp"><h2>Over the limit</h2>{gauge}<h2>Its successor</h2>{row}'
            f'<p class="say" id="say"{"" if line else " hidden"}>{line}</p></div>')
    body = watch + launcher.CSS + CSS + part + scripts(pre)
    return page.render(f"{nn}-handover", [("", body)],
                       page.head("handover", d["tag"], "", f'<span class="group">{go}</span>'), refresh=0)


def data(pre: dict) -> str:
    return json.dumps(pre).replace("</", "<\\/")


# ---- the page on the contract ----------------------------------------------------
#
# 1100 draws the page, and lib/live.py puts each change in place. Its own
# script, .claude/pages/scripts/handover.js, keeps my picks in the address, and
# sends Hand over, naming its act.

def scripts(pre: dict) -> str:
    """The page's scripts on the contract, the same in every state, its
    pre-picks beside them as data."""
    return (page.TABS + f'<script type="application/json" id="picks">{data(pre)}</script>\n'
            f'<script src="{live.src("handover.js")}"></script>\n')


def drawn(nn: str) -> str:
    """Seat NN's page on the contract."""
    mine = (registry.entries().get(nn) or {}).get("session_id", "")
    return draw(world(nn), watch=live.watch(mine))


def files(nn: str) -> list:
    """Every file whose write can move seat NN's page: its press, its
    transcript, what its successor launches on, both thresholds, the
    account order, System's model and effort, the models, and what names
    each session. A file that may come later is named by its folder."""
    own = registry.folder(nn)
    out = registry.watched([nn]) + [handover.path(nn), os.path.join(own, handover.RESUME),
                                    os.path.join(own, launch.NAMED), successor.path(nn)]
    mine = registry.entries().get(nn) or {}
    if mine.get("transcript"):
        out.append(mine["transcript"])
    for f in (context.FILE, accounts.FILE, accounts.MODEL, accounts.EFFORT, models.FILE):
        out += [os.path.dirname(f), f]
    for n in registry.entries():
        out += [os.path.join(registry.folder(n), registry.RECORD), os.path.join(registry.folder(n), plans.PLAN)]
    return list(dict.fromkeys(out))


def alive() -> tuple:
    """Each seat whose press runs, by its program alone: a press whose
    program ended writes nothing, yet the page reads it as failed."""
    return tuple(nn for nn in sorted(registry.listing(registry.WORK))
                 if os.path.isfile(handover.path(nn)) and handover.progress(nn).get("step") in PRESSED)


# The page's contract, lib/live.py's: its address, its draw, its files, its
# look, and its take, which names its act.
LIVE = live.Page(serve.address("handover", r"(\d{2})"), drawn, files=files, looks=(alive,), take=pressed)


# ---- System's part ----------------------------------------------------------------

# System draws it without its script: .claude/pages/scripts/system.js sends each
# save, and nothing reloads.
SYSTEM = r"""<style>
  #limit, #wrapup { margin-top:6px; }
  #limit input, #wrapup input { flex:none; width:7ch; text-align:right; font-weight:700; }
</style>
<div class="pair"><div>
<div class="lbl">Handover threshold</div>
<form class="set" id="limit"><input id="threshold" value="%LEVEL%" inputmode="numeric" autocomplete="off"
  aria-label="The context a session hands over at"><span class="dim">%</span><button class="btn go">Save</button></form>
<p class="hint">A session whose context passes it gets its own Handover page, until it is handed over.</p>
</div><div>
<div class="lbl">Wrap-up threshold</div>
<form class="set" id="wrapup"><input id="wrap" value="%WRAP%" inputmode="numeric" autocomplete="off"
  aria-label="The context a working session wraps up at"><span class="dim">%</span><button class="btn go">Save</button></form>
<p class="hint">A session still working past it is told to finish its step and end its turn, so it is handed over. It never sits under the handover threshold.</p>
</div></div>
<script>
(() => {
  const ok = v => /^\d{1,2}$/.test(v.trim()) && +v > 0;
  [['limit', 'threshold', 'threshold'], ['wrapup', 'wrap', 'wrapup']].forEach(([form, id, name]) => {
    const box = document.getElementById(id);
    box.addEventListener('input', () => box.classList.toggle('bad', !ok(box.value)));
    document.getElementById(form).onsubmit = async e => {
      e.preventDefault();
      if (!ok(box.value)) return;
      await fetch('/', {method: 'POST', redirect: 'manual', body: new URLSearchParams({[name]: box.value.trim()})});
      location.reload();
    };
  });
})();
</script>
"""


def system_part() -> str:
    """System's part, under the accounts: both thresholds side by side,
    each with a box to set it."""
    return SYSTEM.replace("%LEVEL%", str(context.threshold())).replace("%WRAP%", str(context.wrapup()))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    run = sub.add_parser("press")
    for name in ("nn", "pane", "since", "account", "model", "effort"):
        run.add_argument(name)
    args = ap.parse_args()
    pressing(args.nn, args.pane, int(args.since or 0),
             {"account": args.account, "model": args.model, "effort": args.effort})


if __name__ == "__main__":
    main()
