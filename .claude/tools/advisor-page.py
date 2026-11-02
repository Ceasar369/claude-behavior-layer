#!/usr/bin/env python3
"""advisor-page.py — the advisor's session panel, atop its Transcript tab.

Only the advisor shows it. A session is the advisor while its name ends in
-advisor: seated(). transcript-page.py draws it inside the advisor's
Transcript tab, pinned over the turns' top left, and routes its presses
here. With no advisor running, nothing shows.

Closed, only a small Advise tab shows, the advisor's icon: the sessions
already sit on 1100's rail. A tap opens it, and a tap closes it. Each
device keeps it as I left it.

Open, it lists every running session but the advisor, one under another,
the newest turns showing under and beside it. Each row is stacked: its
number in its colour, which says its state, and its name; under them,
four presses, one width each. Rows past its height scroll inside it. On a
Mac, and on my phone held sideways, it is only as wide as its rows; on my
phone held upright, it takes the whole width.

Type and Send are the stage page's pair. Type types "Advise me on session
NN. " into the advisor's pane, with no Return. Send types it and presses
Return, or presses Return alone right after its own Type (rule 16). So
Type on 05 and 12, then Send on 20, sends one line naming all three. Sent
while the advisor works, the line waits in line, as any line typed then
does. A row reads Advising in the pair's place once the advisor read a
line naming it in the turn still running, and In line while that line
still waits. Several rows can read Advising at once.

Follow, blue, and Drive, violet, each type one standard line, LINES', with
no Return, as Type does: the follow skill, or session-control on one topic,
the advisor first saying back what it follows or drives, and what ends it.
Drive is Partially drive: its words don't fit the width, so a hover names
them. While the advisor follows a session, lib/follow.py's following(),
its press reads Following, outlined, and types the stop line. While it
drives it, lib/successor.py's drivers(), Drive reads Driving, the same
way. A row flips when the advisor takes or lets go of its session, never
on the press.

  advisor-page.py draw NN    the panel, printed, as the Transcript tab draws it

Imported, or run to draw.
"""

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import follow  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402
import transcripts  # noqa: E402

esc = page.esc

# The line Type and Send type, and each session a line names, read back
# from the transcript: one line can name several.
LINE = "Advise me on session {}."
ASKED = re.compile(r"Advise me on session (\d{2})\.")

# Each line Follow and Drive type, by its press, with no Return. Follow and
# Drive end on a bullet, for my details.
LINES = {
    "follow": "Follow session {}, through the follow skill. Before you start, say back what you follow it for, "
              "and what ends the follow. Here are the details:\n\n-",
    "unfollow": "Stop following session {}.",
    "drive": "Partially drive session {}, through session-control. Before you start, say back the topic you "
             "drive it on, and what ends the drive. Here are the details:\n\n-",
    "undrive": "Stop driving session {}.",
}


def seated(name: str) -> bool:
    """Whether a session, by its whole name, as 01-advisor, is the advisor."""
    return name.endswith("-advisor")


def seat(nn: str) -> bool:
    """Whether session NN is the advisor now, by the name 1100's rail reads."""
    mine = registry.entries().get(nn)
    if not mine:
        return False
    rec = registry.claude_records().get(mine.get("session_id")) or {}
    return seated(rec.get("name") or mine.get("title", ""))


def seen(nn: str) -> list:
    """Every running session but advisor NN, as [number, name, colour],
    lowest first. Each colour is live_state's; a session gone or closed
    runs no more."""
    held, live, open_ids = registry.entries(), registry.claude_records(), panes.ids(panes.FRESH)
    rows = []
    for n, mine in sorted(held.items()):
        shown, _, colour, _, _ = page.shown(n, mine, live.get(mine.get("session_id")), open_ids)
        if n != nn and colour != "grey":
            rows.append([n, shown, colour])
    return rows


def held(nn: str) -> tuple:
    """What advisor NN follows and drives now, each a set of numbers."""
    return (set(follow.following(nn)),
            {n for n, by in successor.drivers().items() if by == nn})


def asked(turns: list) -> list:
    """The sessions my lines among `turns` asked advice on, in order."""
    return [n for t in turns if t["who"] == "you" for n in ASKED.findall(t["text"])]


def marks(nn: str) -> tuple:
    """The sessions advisor NN reads in the turn still running, and those
    still in line. A turn starts at a line of mine it read at rest; one it
    read mid-turn joins the turn running."""
    transcript = page.tool("transcript-page")
    path = transcript.located(nn, look=True)
    th = transcripts.thread(path) if path else None
    if not th:
        return set(), set()
    turns = [t for _, t, _ in th.numbered(transcript.status(nn) == "idle")]
    reading = set()
    if transcript.state(nn) == "working":
        opens = [i for i, t in enumerate(turns) if t["who"] == "you" and t["counted"] and not t.get("mid")]
        reading = set(asked(turns[opens[-1]:])) if opens else set()
    return reading, {n for s in th.waiting() for n in ASKED.findall(s)}


def row(n: str, name: str, colour: str, mark: str, on: tuple) -> str:
    """One session, stacked: its number in its colour and its name, then
    Type and Send, or what its line already became, then Follow and Drive."""
    pair = (f'<button type="button" class="btn mark" disabled>{mark}</button>' if mark
            else '<span class="group pair"><button type="button" class="btn" data-act="type">Type</button>'
                 f'<button type="button" class="btn ask" data-act="send">{page.icon("send", 11)}Send</button></span>')
    fo = (f'<button type="button" class="btn fo on" data-act="unfollow" title="Stop following session {esc(n)}">'
          'Following</button>' if n in on[0]
          else f'<button type="button" class="btn fo" data-act="follow" title="Follow session {esc(n)}">Follow</button>')
    dr = (f'<button type="button" class="btn dr on" data-act="undrive" title="Stop driving session {esc(n)}">'
          'Driving</button>' if n in on[1]
          else f'<button type="button" class="btn dr" data-act="drive" title="Partially drive session {esc(n)}">'
               'Drive</button>')
    return (f'<div class="row" data-nn="{esc(n)}"><span class="sq" style="background:var(--{colour})">{esc(n)}</span>'
            f'<span class="nm">{esc(name)}</span><span class="acts">{pair}'
            f'<span class="group pair hold">{fo}{dr}</span></span></div>')


def rows(nn: str) -> str:
    """The panel's rows, as a told page draws them again."""
    reading, waiting = marks(nn)
    on = held(nn)
    listing = "".join(row(n, s, c, "Advising" if n in reading else "In line" if n in waiting else "", on)
                      for n, s, c in seen(nn))
    return f'<div class="rows" id="advrows">{listing or "<p class=note>No other session runs.</p>"}</div>'


def key(nn: str) -> str:
    """What moves the panel apart from the advisor's transcript: each
    session's colour and name, and what it follows and drives."""
    on = held(nn)
    got = [seen(nn), sorted(on[0]), sorted(on[1])]
    return hashlib.sha1(json.dumps(got).encode()).hexdigest()[:8]


def panel(nn: str) -> str:
    """The Advise tab and the rows it opens, with their look and script."""
    return (STYLE + '<div class="adv" id="adv"><button type="button" class="b0 atab" id="atab" aria-expanded="false"'
            f' aria-label="Sessions to advise on" title="Advise">{page.icon("advisor", 16)}</button>'
            + rows(nn) + "</div>" + SCRIPT)


def take(nn: str, form: dict) -> str:
    """A press on session SS's row, into advisor NN's pane. Type leaves
    "Advise me on session SS. " in its prompt, no Return. Send types the
    line and presses Return, or presses Return alone right after its own
    Type: the line already sits there, with any typed before it. Follow,
    Drive and their stops type their line, no Return, as Type does.
    Working, it reads a sent line once it can. Whatever would type into the
    wrong place is refused, in one sentence, and nothing is typed."""
    get = lambda k: (form.get(k) or [""])[0]
    how, ss = get("how"), get("nn")
    if how not in ("type", "send", *LINES) or not re.fullmatch(r"\d{2}", ss) or ss == nn:
        return ""
    if ss not in registry.entries():
        return f"There is no session {ss}. Nothing was typed."
    why, _, pane = page.typable(nn, ("idle", "shell", "busy"))
    if why:
        return why
    enter = how == "send"
    text = "" if enter and get("only") == "return" else LINES.get(how, LINE).format(ss) + ("" if enter else " ")
    return serve.Typing(lambda: "" if panes.say(pane, text, enter=enter) else page.gone(nn))


# The tab hangs from the transcript's top left. Open, the panel is pinned
# over the turns, only as wide as its rows, each row stacked. A narrow
# transcript, as my phone held upright, gives it the whole width. Follow is
# blue, Drive a violet of its own, each outlined in its colour while on.
STYLE = """<style>
  .tp { position:relative; flex:1; min-height:0; display:flex; flex-direction:column; container-type:inline-size; }
  .tp > .scroll { padding-top:40px; }
  .adv { --violet:#a78bfa; position:absolute; top:0; left:0; z-index:3; display:flex; flex-direction:column;
    gap:6px; }
  .atab { flex:none; align-self:flex-start; display:inline-flex; align-items:center; justify-content:center;
    width:34px; height:30px; margin-left:8px; color:var(--text); background:var(--raised);
    border:1px solid var(--grey); border-top:0; border-radius:0 0 6px 6px; box-shadow:0 4px 12px rgba(0,0,0,.4);
    text-align:center; }
  .atab:hover { background:var(--hover); }
  .adv:not(.open) > .rows { display:none; }
  .adv.open { max-height:calc(100% - 24px); padding:0 14px 10px; background:var(--bg);
    border-bottom:1px solid var(--grey); border-right:1px solid var(--grey); border-radius:0 0 6px 0;
    box-shadow:0 10px 24px rgba(0,0,0,.55); }
  .adv.open > .atab { margin-left:-6px; color:#000; background:#fff; border-color:#fff; box-shadow:none; }
  .adv .rows { flex:1 1 auto; min-height:0; overflow-y:auto; overscroll-behavior:contain; display:flex;
    flex-direction:column; gap:4px; }
  .adv .note { margin:0; }
  .adv .row { display:grid; grid-template-columns:auto minmax(0,1fr); align-items:center; gap:6px 10px;
    padding:5px 8px; background:var(--panel); border:1px solid var(--line); border-radius:5px; }
  .adv .sq { display:inline-flex; align-items:center; justify-content:center; width:28px; height:22px;
    border-radius:4px; color:var(--bg); font-size:12px; font-weight:700; }
  .adv .nm { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; contain:inline-size; }
  .adv .acts { grid-column:1 / -1; display:grid; grid-template-columns:1fr 1fr; gap:6px; }
  .adv .pair { width:22ch; }
  .adv .acts > .mark { width:auto; }
  .adv .hold .btn { padding:0 4px; }
  .adv .btn.fo { background:var(--blue); color:#000; border-color:var(--blue); }
  .adv .btn.dr { background:var(--violet); color:#000; border-color:var(--violet); }
  .adv .btn.fo.on { background:none; color:var(--blue); }
  .adv .btn.dr.on { background:none; color:var(--violet); }
  .adv .btn.done { background:var(--green); color:var(--bg); border-color:var(--green); }
  @container (max-width: 560px) {
    .adv.open { right:0; border-right:0; border-radius:0; }
    .adv .pair { width:auto; }
  }
  /* My phone: every control takes a fingertip (rule 20). */
  @media (hover:none) and (pointer:coarse) {
    .tp > .scroll { padding-top:54px; }
    .atab { width:48px; height:44px; }
    .atab svg { width:20px; height:20px; }
    .adv.open { padding:0 10px 10px; }
    .adv.open > .atab { margin-left:-2px; }
    .adv .row .btn { height:44px; }
  }
</style>
"""

# The tab opens and closes the panel, and each device keeps which. A row's
# Type leaves its line in the advisor's prompt, and its Send then presses
# Return alone. A told page draws the rows again, and a Type pressed stays
# pressed.
SCRIPT = """<script>
(() => {
  const adv = document.getElementById('adv'), tab = document.getElementById('atab'), typed = new Set();
  const show = open => {
    adv.classList.toggle('open', open);
    tab.setAttribute('aria-expanded', open);
    try { localStorage.setItem('advise-open', open ? '1' : ''); } catch (e) {}
  };
  let was = '1';
  try { was = localStorage.getItem('advise-open') ?? '1'; } catch (e) {}
  show(!!was);
  tab.addEventListener('click', () => show(!adv.classList.contains('open')));
  adv.addEventListener('click', async e => {
    const b = e.target.closest('.row button[data-act]');
    if (!b || b.disabled) return;
    const nn = b.closest('.row').dataset.nn, how = b.dataset.act;
    const only = how === 'send' && typed.has(nn) ? 'return' : '';
    if (await pressed(b, {act: 'advise', how, nn, only}, how !== 'send') !== '') return;
    if (how === 'type') typed.add(nn);
    else if (how === 'send') typed.clear();
  });
  window.advRows = got => {
    const now = document.getElementById('advrows');
    if (got && now) now.replaceWith(got);
  };
})();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["draw"])
    ap.add_argument("number")
    args = ap.parse_args()
    print(panel(f"{int(args.number):02d}"))


if __name__ == "__main__":
    main()
