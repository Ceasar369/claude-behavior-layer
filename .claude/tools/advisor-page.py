#!/usr/bin/env python3
"""advisor-page.py — the advisor's session panel, atop its Transcript tab.

Only the advisor shows it. A session is the advisor while its name ends in
-advisor: seated(). transcript-page.py draws it inside the advisor's
Transcript tab, pinned over the turns' top left, and routes its presses
here. With no advisor running, nothing shows.

Closed, only a small Advise tab shows, the advisor's icon: the sessions
already sit on 1100's rail. A tap opens it, and a tap closes it. Each
device keeps it as I left it.

An advisor's list names the sessions it advises on, LIST in its folder, so
a handover of its seat keeps it. With no list, the advisor is general, and
sees every running session. A listed session stopped, or another on its
number, drops out, and an empty list stays a list, never general.

Open, it lists the running sessions it sees, itself never among them, one
under another, the newest turns showing under and beside it. Each row is stacked: its
number in its colour, which says its state, and its name; under them,
four presses, one width each. Rows past its height scroll inside it, and a
bar of its own beside them shows where they sit, rule 1's exception. On a
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

The Transcript tab draws the panel through drawn(), its script
.claude/pages/scripts/advisor.js, and names files() among its own.

  advisor-page.py list NN 02 04 05   advisor NN's list, replaced whole
  advisor-page.py list NN            advisor NN's list gone: it is general

Imported, or run.
"""

import argparse
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

LIST = "advising.json"

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


def listing(nn: str) -> dict:
    """Advisor NN's list as kept, by number. Empty → it is general."""
    return follow.records(os.path.join(registry.folder(nn), LIST))


def listed(nn: str, held: dict) -> list:
    """The sessions on advisor NN's list still holding their numbers, lowest
    first: a session stopped, or another on its number, drops out."""
    kept = listing(nn)
    return [n for n in sorted(kept) if n in held and follow.same(kept[n], held[n], n)]


def keep_list(nn: str, numbers: list) -> None:
    """Advisor NN's list, replaced whole. Each session is kept by its
    identity, so a reused number never passes for it."""
    kept = {n: follow.identity(n) for n in numbers}
    follow.update(nn, os.path.join(registry.folder(nn), LIST), lambda d: (d.clear(), d.update(kept)))


def seen(nn: str) -> list:
    """The running sessions advisor NN sees, as [number, name, colour],
    lowest first: its list's, or with no list every one but itself. Each
    colour is live_state's; a session gone or closed runs no more."""
    held, live, open_ids = registry.entries(), registry.claude_records(), panes.ids(panes.FRESH)
    has_list, on_list = bool(listing(nn)), listed(nn, held)
    rows = []
    for n, mine in sorted(held.items()):
        if has_list and n not in on_list:
            continue
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
    Type and Send, or what its line already became, then Follow and Drive.
    Its colour is a longhand: live.js redraws a style property by property,
    and a shorthand holding var() reads back empty, losing the colour."""
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
    return (f'<div class="row" data-nn="{esc(n)}"><span class="sq" style="background-color:var(--{colour})">{esc(n)}</span>'
            f'<span class="nm">{esc(name)}</span><span class="acts">{pair}'
            f'<span class="group pair hold">{fo}{dr}</span></span></div>')


def rows(nn: str) -> str:
    """The panel's rows."""
    reading, waiting = marks(nn)
    on = held(nn)
    drawn = "".join(row(n, s, c, "Advising" if n in reading else "In line" if n in waiting else "", on)
                    for n, s, c in seen(nn))
    empty = "No session on this advisor's list runs." if listing(nn) else "No other session runs."
    return f'<div class="rows" id="advrows">{drawn or f"<p class=note>{empty}</p>"}</div>'


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
    if how not in ("type", "send", *LINES):
        return f"This page has no {how or 'unnamed'} button. Nothing was typed."
    if not re.fullmatch(r"\d{2}", ss):
        return f"{ss or 'A blank'} is not a session number. Nothing was typed."
    if ss == nn:
        return f"Session {nn} cannot advise on itself. Nothing was typed."
    if ss not in registry.entries():
        return f"There is no session {ss}. Nothing was typed."
    why, _, pane = page.typable(nn, ("idle", "shell", "busy"))
    if why:
        return why
    enter = how == "send"
    text = "" if enter and get("only") == "return" else LINES.get(how, LINE).format(ss) + ("" if enter else " ")
    return serve.Typing(lambda: "" if panes.say(pane, text, enter=enter) else page.gone(nn))


# The tab hangs from the transcript's top left. Open, the panel is pinned
# over the turns, only as wide as its rows, each row stacked and never
# squeezed: past the panel's height, the rows scroll, their bar drawn in
# the panel's right margin, as a chart's own window draws its. A narrow
# transcript, as my phone held upright, gives it the whole width. Follow is
# blue, Drive a violet of its own, each outlined in its colour while on.
STYLE = "<style>\n" + page.shared("advisor.css") + "</style>\n"


# ---- the panel on the contract --------------------------------------------------
#
# The panel has no address of its own: it draws inside the advisor's
# Transcript tab, transcript-page.py's drawn(), which names files() among
# its own. 1100 draws its rows; .claude/pages/scripts/advisor.js opens and closes
# it and sends each press.

def drawn(nn: str) -> str:
    """The Advise tab and the rows it opens, with their look, no script."""
    return (STYLE + '<div class="adv" id="adv"><button type="button" class="b0 atab" id="atab" aria-expanded="false"'
            f' aria-label="Sessions to advise on" title="Advise">{page.icon("advisor", 16)}</button>'
            + rows(nn) + '<div class="sb" id="advsb" aria-hidden="true"><i></i></div></div>')


def files(nn: str) -> list:
    """Every file whose write can move advisor NN's panel: its list, and
    each session's record, follows and drives, and Claude Code's records,
    where a state moves."""
    held = registry.entries()
    out = registry.watched(list(held)) + [os.path.join(registry.folder(nn), LIST)]
    for n in held:
        out += [follow.path(n), successor.path(n)]
    return out


# Its contract is the Transcript tab's: no Page of its own.
LIVE: list = []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["list"])
    ap.add_argument("number")
    ap.add_argument("sessions", nargs="*")
    args = ap.parse_args()
    nn = f"{int(args.number):02d}"
    them = [f"{int(s):02d}" for s in args.sessions]
    held = registry.entries()
    if bad := [s for s in them if s == nn or s not in held]:
        sys.exit(f"Refused {', '.join(bad)}: this advisor itself, or no session holds it. Nothing changed.")
    keep_list(nn, them)
    print(f"Advisor {nn} advises on: {', '.join(held[s].get('title', s) for s in them)}." if them
          else f"Advisor {nn} has no list. It is general.")


if __name__ == "__main__":
    main()
