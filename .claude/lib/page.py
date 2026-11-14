#!/usr/bin/env python3
"""page.py — the look every page in the behaviour band wears.

1100 draws every page but the prototypes, which the app on 1400 draws.
They are read side by side all day, so they share a shell: the same
tokens, the same rails, the same card.

A skill passes a title, a rail and its sections. It never writes CSS for
what the shell already rules.

A part two pages share sits here once: typing into a pane, typing
anywhere, a copy block's Copy button, the find field, the close button,
and the zoom tools a chart wears. So do tool(),
which loads a page tool for 1100 and the views it draws, rules() and
whole(), which borrow one look another page wears, and table(), the
transcript page's table look.

The shell's style and script, each script every page shares, and each
page's own style are files of .claude/pages/, read by shared().

The page fills the glass. No column is centred and nothing is capped, because
every pixel it does not use is one I cannot read.

Every page keeps forty-four rules, and the shell carries each one it can.

  1  No scrollbar shows, bar a chart's own window and the advisor's rows,
     each drawn, and only while it runs past that edge. Wheel and
     trackpad still scroll.
  2  A page's tools sit together, in one place.
  3  A fact shows once per screen. Under 1100's tab, a page's head drops
     its family and its session: the tab names its family, its place the
     session.
  4  Buttons in one group share one width and one order: `.group`.
  5  A session in a stage reads number first, then mission: 23-A3.
  6  A side rail keeps one width, its head's. Nothing drags it.
  7  The page zooms whole, by Cmd+ and Cmd-. A pinch zooms nothing, bar
     a chart's own window. Inside 1100, a page is part of 1100's main.
  8  Finished work folds into one line above what is still live.
  9  A row of tabs too long for its space scrolls sideways.
  10 A screen with nothing to show says so in one large centred line.
  11 A wait is one session's own page. Two sessions waiting alike get
     two pages.
  12 A page picking a session's account, model and effort uses the
     launch page's defaults.
  13 A button that cannot act while its session works is greyed, and
     takes no press, until its turn ends.
  14 A value 1100 uses for every session is set on System.
  15 A page one page opens sits on the right half of 1100's hub, under
     its tab. The page that opened it keeps the left.
  16 A button acting on a session types the line I could type there
     myself, so a press and my words do the same.
  17 A page needing another page opens it whole, drawn by its own code,
     never a copy of its parts.
  18 A page's content scrolls as one. A split view counts as one content,
     each of its panes scrolling apart. Only its tools and the bar I type
     into stay in place.
  19 On a phone, a page follows how it is held. Upright, it shows
     upright; turned, it turns.
  20 On a phone, every control a finger taps is 44 by 44 at least,
     Apple's least touch size.
  21 A place's tabs run, and open, as `.claude/tools/workstation.py`
     orders them.
  22 A chart shows every item's name. None waits on a hover.
  23 A chart bigger than its window pans every way, by a swipe or a drag.
  24 A chart of what waits on what flows one way: left to right, or top
     to bottom, as I flip it.
  25 A chart sets each item between the items it hangs on, and crosses
     as few lines as it can.
  26 A chart never moves on its own.
  27 An item wears its agenda colour on every page.
  28 A family's icon marks its pages alone. Another page never wears it.
  29 On a phone, a page's head takes as few lines as it can.
  30 A control borrows a look another page already wears before a new one
     is made. A new look is mine to rule.
  31 An outcome sits on its item, written as the plan wrote it, in the
     plan's order. Every outcome wears one format.
  32 An outcome shows first. What reached it, and who, stays folded until
     I click.
  33 A vote reads as a count, like 4 of 5 said no. Never a percentage.
  34 A table drawn from a file keeps the file's rows, columns and words.
  35 A row whose state a mark already shows is never tinted for it.
  36 A page about one session is one of that session's tabs, never an icon
     on the main left rail.
  37 A checklist drawn on a page wears Obsidian's table look: a thin border
     round every cell, a sans-serif font, a bold header row, and a table as
     wide as its content.
  38 A page that draws rows from several checklist files names each file's
     path, in dim, above its table.
  39 A side rail is no wider than its widest line needs. The rest of the
     glass is the page's.
  40 A session's words meant to be pasted elsewhere wear a Copy button, on
     every page that shows them. A hand-off, in one of talking.md's shapes,
     wears one group: Copy, Type, then Send, naming its receiver unless it
     is the page's own session, as Send to 12.
  41 A session's square keeps its colour and its size, whatever sits on
     it; what it wears adapts to them. A white dot marks a page waiting on
     me. A role shows as an icon badge, never a word.
  42 A page spanning several sessions is a tab of the session that keeps
     it, never a rail tool. A tab's page wears its hub's frame, and no head
     of its own.
  43 A session's own tab wears its icon, then its word, as Transcript does.
     It wears no badge, no chip and no colour of its own.
  44 A checklist sharing a page with other sections takes the page's own
     background, as they do. Its table keeps rule 37's look.

Imported, never run.
"""

import hashlib
import html
import importlib.util
import json
import os
import re
import time
import traceback

import hear
import panes
import plans
import registry
import wake

# What a session's colour means. Two colours, and grey for gone.
#   green  working. Nothing is needed from me. A session whose turn ended
#          on its background wait, its move asking me nothing, works too.
#   red    its turn is over, and it waits on me: for a wave, a gate, a
#          launch, a page, anything.
#   grey   gone, drawn dashed.
# Blue marks no session's state. A count keeps its own two: red waits on
# me, grey only counts.
#
# Claude Code publishes four statuses. Each maps to one of my words.
STATES = {
    "waiting": ("waiting", "red"),
    "busy": ("working", "green"),
    "idle": ("idle", "red"),
    # Its turn is over, and a command it started in the background still
    # runs. Claude Code itself counts it as idle. A dev server stays red;
    # work still running, its move asking me nothing, reads working:
    # live_state.
    "shell": ("idle", "red"),
}


def word(rec) -> str:
    """A session's word from Claude Code's record alone, or gone with no
    record. A page's Send reads it; live_state adds what the registry knows."""
    return STATES.get(rec.get("status"), STATES["idle"])[0] if rec else "gone"


def live_state(rec, mine: dict, open_ids=None) -> tuple:
    """A session's word, colour and look, the same on every page.

    `rec` is Claude Code's record for it, or None once its process is gone.
    `mine` is its record in the registry.
    `open_ids` is every open pane's id, or None when iTerm could not be asked.

    Its pane is panes.pane's: the one holding its terminal while it runs,
    the last one it lived in once it is gone. Its pane closed while it was
    never stopped, I closed it on purpose and keep its folder: closed,
    grey, drawn dashed. Its pane open and its process gone: gone, grey,
    drawn dashed. A browser it opened for me since my last prompt, still
    open, reads waiting. A turn ended on work still running in the
    background, an agent, a command, a browser script or a wait, reads
    working, a bare progress note too. Its move a Ruling, an Action or an
    Answer, it reads idle, though Claude Code reads it busy while an agent
    runs: wake.over's.
    """
    pane = "" if open_ids is None else panes.pane(mine, int(rec["pid"]) if rec else 0, panes.FRESH)
    if pane and pane not in open_ids:
        return "closed", "grey", "dashed"
    if rec is None:
        return "gone", "grey", "dashed"
    status = rec.get("status")
    if status == "busy" and wake.over(rec, mine):
        status = "idle"
    if status in ("busy", "idle", "shell") and any(
            open_ids is None or p in open_ids
            for p in registry.browsers(mine.get("transcript", ""))):
        status = "waiting"
    if status in ("idle", "shell") and wake.waiting(rec, mine):
        status = "busy"
    return (*STATES.get(status, STATES["idle"]), "")


def shown(nn: str, mine: dict, rec, open_ids=None) -> tuple:
    """A session as every page shows it: (name, word, colour, look, since).

    Its name is Claude Code's for it while it runs, else its title in the
    registry, without its number. Its word, colour and look are
    live_state's. `since` is when its status last moved, in seconds, or 0.
    """
    title = (rec or {}).get("name") or mine.get("title", "")
    since = ((rec or {}).get("statusUpdatedAt") or (rec or {}).get("updatedAt") or 0) // 1000
    return (title[3:] if title.startswith(f"{nn}-") else title or nn,
            *live_state(rec, mine, open_ids), since)


def colours() -> dict:
    """Every session's rail colour and word, as the rail reads them, its pane
    left unasked: a closed pane only greys what is gone anyway."""
    held, live = registry.entries(), registry.claude_records()
    out = {}
    for nn, mine in held.items():
        name, word, colour, _, _ = shown(nn, mine, live.get(mine.get("session_id")))
        out[nn] = (colour, word, name)
    return out


def reddened(acts: list, hold: float = 900, kept: str = "") -> None:
    """Each act(nn, word, name) for each session whose number turns from
    green to red, on a thread of 1100's own, for as long as 1100 runs. The
    buzz and auto-send hang on the one watch. An act that raises is logged,
    and keeps no other act, nor any other session, from its turn.

    It sleeps until a session's record or Claude Code's own records are
    written. `hold` is the safety net: the colours are read again after
    that long, heard or not.

    `kept` is a file the colours are kept in as each is acted on. A 1100
    that starts again takes them up there, remembered(): a session that
    turned red while none ran is still acted on, once.
    """
    was = remembered(kept)
    while True:
        try:
            if was is None:
                was = colours()
                remember(kept, was)
            hear.until(lambda: colours() != was, registry.watched(list(registry.entries())), seconds=hold)
            was = acted(was, acts, kept)
        except Exception:
            time.sleep(60)


def acted(was: dict, acts: list, kept: str = "") -> dict:
    """One look of the colour watch: each act for each session gone from
    green to red since `was`, and the colours as they stand now. A
    session's colour is kept once its acts ran, so a 1100 stopped mid-look
    acts again on the one in hand alone."""
    now = colours()
    for nn, (colour, word, name) in now.items():
        if colour == "red" and was.get(nn, ("",))[0] == "green":
            for act in acts:
                try:
                    act(nn, word, name)
                except Exception:
                    traceback.print_exc()
        if was.get(nn) != now[nn]:
            was = {**was, nn: now[nn]}
            remember(kept, was)
    remember(kept, now)
    return now


def remember(kept: str, held: dict) -> None:
    """The colours, kept whole in `kept`, each beside its session's id."""
    if not kept:
        return
    ids = {nn: mine.get("session_id", "") for nn, mine in registry.entries().items()}
    registry.write_whole(kept, json.dumps({nn: [*held[nn], ids.get(nn, "")] for nn in held}) + "\n")


def remembered(kept: str):
    """The colours a 1100 before this one kept, for each number the same
    session still holds: a number another session took since is left out.
    None with no file to read."""
    if not kept:
        return None
    try:
        with open(kept) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return None
    ids = {nn: mine.get("session_id", "") for nn, mine in registry.entries().items()}
    return {nn: tuple(v[:3]) for nn, v in got.items()
            if isinstance(v, list) and len(v) == 4 and v[3] and v[3] == ids.get(nn)}


# Every family's icon and word. A page's head opens with both, and 1100's
# tabs name a page the same way, so pages are told apart by name, never by
# tint. The strokes are Lucide's.
PATHS = {
    "clarify": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-4.8-4.8"/>',
    "assistant": '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2'
                 'H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/>'
                 '<path d="M8 11h.01"/><path d="M8 16h.01"/>',
    "prototype": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0'
                 'l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/>'
                 '<path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "launch": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>'
              '<path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>'
              '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "system": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94'
             'l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "skills": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "library": '<path d="M12 5v16"/><path d="M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2'
               'H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z"/>',
    "utilities": '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/>'
                 '<rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
    "files": '<path d="M20 10a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1h-2.5a1 1 0 0 1-.8-.4l-.9-1.2A1 1 0 0 0 15 3h-2'
             'a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/><path d="M20 21a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1h-2.9a1 1 0 0 1'
             '-.88-.55l-.42-.85a1 1 0 0 0-.92-.6H13a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/>'
             '<path d="M3 5a2 2 0 0 0 2 2h3"/><path d="M3 3v13a2 2 0 0 0 2 2h3"/>',
    "handover": '<path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/>',
    "agenda": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/>'
              '<rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/>'
              '<path d="M12 12V8"/>',
    "jury": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>'
            '<path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>'
            '<path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "shots": '<path d="M18 22H4a2 2 0 0 1-2-2V6"/><path d="m22 13-1.296-1.296a2.41 2.41 0 0 0-3.408 0L11 18"/>'
             '<circle cx="12" cy="8" r="2"/><rect width="16" height="16" x="6" y="2" rx="2"/>',
    "walk": '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/>'
            '<path d="M13 18h8"/>',
    "advisor": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265'
               'L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"/>',
    # Marks, not families.
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "down": '<path d="m6 9 6 6 6-6"/>',
    "up": '<path d="m18 15-6-6-6 6"/>',
    "back": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "close": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "copy": '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10'
            'c1.1 0 2 .9 2 2"/>',
    "filter": '<path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>',
    "enter": '<path d="M9 10 4 15l5 5"/><path d="M20 4v7a4 4 0 0 1-4 4H4"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "drive": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "pause": '<rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    # A session another session drives.
    "wheel": '<circle cx="12" cy="12" r="8"/><path d="M12 2v7.5"/><path d="m19 5-5.23 5.23"/>'
             '<path d="M22 12h-7.5"/><path d="m19 19-5.23-5.23"/><path d="M12 14.5V22"/>'
             '<path d="M10.23 13.77 5 19"/><path d="M9.5 12H2"/><path d="M10.23 10.23 5 5"/>'
             '<circle cx="12" cy="12" r="2.5"/>',
    # A transcript's steps, by kind.
    "command": '<path d="M12 19h8"/><path d="m4 17 6-6-6-6"/>',
    "read": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12'
            'a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M10 9H8"/><path d="M16 13H8"/>'
            '<path d="M16 17H8"/>',
    "search": '<path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/>',
    "fetch": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>'
             '<path d="M2 12h20"/>',
    "browser": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M10 4v4"/><path d="M2 8h20"/>'
               '<path d="M6 4v4"/>',
    "load": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.106-3.105c.32-.322.863-.22.983.218a6 6 0 0 1'
            '-8.259 7.057l-7.91 7.91a1 1 0 0 1-2.999-3l7.91-7.91a6 6 0 0 1 7.057-8.259c.438.12.54.662.219.984z"/>',
    "agent": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/>'
             '<path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "wrote": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12'
             'a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M9 15h6"/><path d="M12 18v-6"/>',
    "edited": '<path d="M12.659 22H18a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6'
              'a2 2 0 0 0-2 2v9.34"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M10.378 12.622a1 1 0 0 1 3 3.003'
              'L8.36 20.637a2 2 0 0 1-.854.506l-2.867.837a.5.5 0 0 1-.62-.62l.836-2.869a2 2 0 0 1 .506-.853z"/>',
    # The transcript box's attach and more.
    "clip": '<path d="m16 6-8.414 8.586a2 2 0 0 0 2.829 2.829l8.414-8.586a4 4 0 1 0-5.657-5.657l-8.379 8.551a6 6 0 1 0'
            ' 8.485 8.485l8.379-8.551"/>',
    "more": '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    # 1100's home: the transcript's family, a hub's two sides and its one, the
    # buzz's bell, and the rail's zoom in and zoom out.
    "transcript": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
                  '<path d="M13 8H7"/><path d="M17 12H7"/>',
    # A side panel, shown or hidden: an explanation document's contents.
    "panel": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>',
    # A download: an explanation document, exported as one file.
    "download": '<path d="M12 15V3"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/>',
    # An explanation document: an open book.
    "explanation": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4'
                   ' 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "two": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M12 3v18"/>',
    "one": '<rect width="18" height="18" x="3" y="3" rx="2"/>',
    "bell": '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 '
            '.74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
    "zoom-out": '<circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/>'
                '<line x1="8" x2="14" y1="11" y2="11"/>',
    "zoom-in": '<circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/>'
               '<line x1="8" x2="14" y1="11" y2="11"/><line x1="11" x2="11" y1="8" y2="14"/>',
}
# A step of any other kind.
PATHS["other"] = PATHS["load"]
# The advisor's Teams tab wears the Team icon a team's hub wears.
PATHS["teams"] = PATHS["assistant"]
WORDS = {"clarify": "Clarify", "assistant": "Assistant",
         "prototype": "Prototype", "launch": "Launch", "handover": "Handover",
         "system": "System", "skills": "Skills", "files": "Files", "agenda": "Agenda",
         "shots": "Screenshots", "walk": "Walk", "jury": "Jury", "explanation": "Explanation",
         "teams": "Teams"}
# Every kind of tab a session shows, once: its word, and the tool that
# draws its page, in the order a session's tabs run: those that can wait
# on me first, then those I read. Its icon is PATHS' of its own name.
# Home's model orders a hub's tabs by it, home draws them as the model hands
# them, and 1100 loads each kind's tool from it.
TAB_KINDS = {"clarify": ("Clarify", "clarify-page"), "jury": ("Jury", "jury-page"),
             "handover": ("Handover", "handover-page"), "launch": ("Launch", "launch-page"),
             "prototype": ("Prototype", "prototype-page"), "transcript": ("Transcript", "transcript-page"),
             "explanation": ("Explanation", "explanation-page"),
             "walk": ("Walk", "walk-list-page"), "shots": ("Screenshots", "walk-shots-page"),
             "teams": ("Teams", "teams-page")}


def icon(name: str, size: int = 14, cls: str = "i") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{PATHS[name]}</svg>')


def family(name: str) -> str:
    """A family as a page's head names it: its icon, then its word."""
    return f'<span class="fam">{icon(name)}<b>{WORDS[name]}</b></span>'


def head(name: str, tag: str = "", mid: str = "", acts: str = "", driven: str = "") -> str:
    """A page's top rail. Its family and its session's tag on the left, what
    it shows in the middle, its tools together on the right. A page of a
    session another drives wears `driven`, the line naming its driver, on
    a thin band under it, the wheel first.

    Under 1100's tab, the family and the tag go: the tab names both.
    """
    who = family(name) + (f'<span class="dim">·</span><b>{esc(tag)}</b>' if tag else "")
    band = f'<div class="by">{icon("wheel", 13)}{esc(driven)}</div>' if driven else ""
    return (f'<header class="top fam {name}"><span class="who">{who}</span>'
            f'<span class="mid">{mid}</span><span class="acts">{acts}</span>{band}</header>\n')


def blank(line: str) -> str:
    """A screen with nothing to show: one large line, centred."""
    return f'<div class="empty"><p>{esc(line)}</p></div>'


# The steps 1100's two zooms take, one a press: the page's, by the rail's
# foot buttons, and the rail's, by Rail size on System.
ZOOMS = [0.5, 0.67, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2]


# Every style and script the pages share or own, one file each. lib/live.py
# serves the ones a page loads by address.
PAGES = os.path.join(registry.ROOT, ".claude", "pages")
STYLES = os.path.join(PAGES, "styles")
SCRIPTS = os.path.join(PAGES, "scripts")
# Each one already read here, as text.
SHARED: dict = {}


def where(name: str) -> str:
    """Where one such file sits, by its kind: a script in SCRIPTS, a style in STYLES."""
    return os.path.join(SCRIPTS if name.endswith(".js") else STYLES, name)


def shared(name: str) -> str:
    """One file of .claude/pages/ as text, read once per process: the
    shell's style, a page's own, or a script every page shares, put
    whole into a page.
    Read here, never through lib/live.py: a hook that loads this module
    must not load the server with it."""
    if name not in SHARED:
        with open(where(name), "rb") as f:
            SHARED[name] = f.read().decode()
    return SHARED[name]


# Every page zooms whole, by Cmd+ and Cmd-, which iTerm's browser owns.
# A pinch, or a wheel it sends with Ctrl, zooms nothing, so Cmd+ and Cmd-
# stay the one zoom. A chart's window hears its own pinch first.
#
# WebKit can keep showing the picture a page drew before its pane grew,
# white where it grew, until a zoom draws it again. So once a resize
# settles, the page draws itself whole again, as a zoom would.
#
# My phone draws every page at its own width, never 980 wide and shrunk.
# A framed page obeys only the line of the page around it, the home's.
# A Mac ignores the line.
SHELL = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{refresh}<style>
{style}</style>
<script>
{script}</script>
{rail}<main>
{body}</main>
{tail}"""


# Inside 1100, a page is part of 1100's main. It drops its head's family
# and session when told the page around it already names them, and goes
# back to where it opens when told to: it hears "ws-home".
#
# Home zooms a page by its root's zoom: it sets it itself, or posts it to a
# page on another port. A zoom reflows the page under the same scrollTop
# and fires no resize, so the page hears "ws-zoom" once it moves, before
# anything is drawn at the new size. --vh holds a hundredth of the glass, in
# the page's own pixels, at any zoom: a vh would grow with the zoom.
FRAME = "<script>\n" + shared("frame.js") + "</script>\n"

# Shows the item a tab names, and keeps it in the address, so a reload
# lands on the same one. Only an item or a tab carries these ids.
TABS = "<script>\n" + shared("tabs.js") + "</script>\n"

# The session a paste is for, named by the line above it: "Send to session
# 12." The stage page's moves and the Transcript tab's copy blocks read it
# alike.
SEND_TO = re.compile(r"\bsend (?:it |this )?to session (\d{2})\b", re.I)


def into(nn: str) -> str:
    """A send button's class, by its receiver: gold into a session steering
    others, an assistant with a plan or the advisor; white into any other."""
    title = (registry.entries().get(nn) or {}).get("title", "")
    return "btn ask" if title.endswith("-advisor") or plans.plan(nn).get("stages") else "btn go"


# A hand-off's Copy, the same on every page: COPY's copied() presses it.
CP = (f'<button class="btn cp">{icon("copy", 14, "i no")}{icon("check", 14, "i ok")}'
      '<span>Copy</span></button>')

# A press that types into a pane waits for the typing, since only the
# server knows whether it typed. typePost() posts it, to the page's own
# path or the address it is given, and answers "" once it typed, the
# server's sentence when it typed nothing, and null when the server never
# answered or failed. pressed() is one button's whole press: it greys
# while it types, then flashes green, reading Typed when the line was left
# unsent. Nothing typed, it turns red and reads Not typed until it is
# pressed again, and refusal() says why along the page's foot. It answers
# what typePost answered.
TYPING = "<script>\n" + shared("typing.js") + "</script>\n"

# A copy block's Copy button, pressed: the block's words go onto the
# clipboard, and the button reads Copied, green, for a moment. The words
# are the nearest .txt above it, so a Copy inside a group finds its
# block's. Each page showing a session's reply calls copied() from its own
# click.
COPY = "<script>\n" + shared("copy.js") + "</script>\n"

# On my Mac, a letter or a paste landing anywhere on a page, never in a
# field, goes to the page's box, with no click. Space still scrolls, and a
# shortcut stays a shortcut. My phone types only where I tap.
#
# A page names its own box, and when it takes typing, in the typeIn it
# hands anywhere(): typeIn(text) answers true once its box took the text.
# A page whose Tab does something hands a tabIn too, true once it acted.
# Both stay on its window, so 1100's home hands them what lands on home.
# A paste the page already took, as a transcript takes a picture, is left.
# Chrome can receive a paste's text, then lose it before inserting it.
# In a textarea, insert that text during the paste, keeping undo available.
ANYWHERE = "<script>\n" + shared("anywhere.js") + "</script>\n"

# The zoom tools a chart wears, defined once for every chart. They zoom the
# chart alone, never the page around it: 1100's zoom stays the page's. A
# press never takes the cursor from the box I type in. A pinch on the
# chart's own window zooms it too, around the pointer. It arrives as a
# wheel sent with Ctrl, or in Safari as gesture events.
#
# ZOOM_TOOLS is their markup. zoomer(tools, win, chart) wires one set: the
# element holding them, the chart's window, and the chart. A chart's size
# counts from its natural size, 1, and the chart answers five things.
#   scale()    its size now, or 0 while it shows nothing
#   bounds()   [its fitted size, the furthest it zooms in]
#   to(s, at)  go to size s, holding still the point `at` of the window,
#              from its top left as the screen measures it: the pointer's
#              under a pinch, null for the middle of what shows
#   fit()      back to its fitted size
#   fitted()   whether it shows fitted now
# zoomer answers paint(), which the chart calls whenever it moves: the
# percent then reads its size, and a tool that cannot act greys.
ZOOM_TOOLS = ('<span class="zt"><span class="group">'
              '<button type="button" data-z="out" title="Zoom out" aria-label="Zoom out"'
              ' onmousedown="event.preventDefault()">−</button>'
              '<button type="button" data-z="in" title="Zoom in" aria-label="Zoom in"'
              ' onmousedown="event.preventDefault()">+</button>'
              '<button type="button" data-z="fit" title="Back to the fitted size"'
              ' onmousedown="event.preventDefault()">Fit</button>'
              '</span><span class="pct"></span></span>')
ZOOM = ("<script>\nconst ZOOM_TOOLS = " + json.dumps(ZOOM_TOOLS).replace("</", "<\\/") + ";\n"
        + shared("zoom.js") + "</script>\n")


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def count(n: int, one: str, many: str = "") -> str:
    """A count as it reads: 1 claim, 2 claims. `many` when the word takes
    more than an s: 1 lens, 2 lenses."""
    return f"{n} {one if n == 1 else many or one + 's'}"


# Each page tool loaded, by name: one module per tool in a process, so its
# lock and what it keeps are one, whoever asks.
LOADED: dict = {}


def tool(name: str):
    """A page tool in .claude/tools/, loaded whole, once per process. Its
    file name holds a dash, so no import statement can name it."""
    if name in LOADED:
        return LOADED[name]
    here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", f"{name}.py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), here)
    found = importlib.util.module_from_spec(spec)
    LOADED[name] = found
    try:
        spec.loader.exec_module(found)
    except BaseException:
        del LOADED[name]
        raise
    return found


def rules(css: str, part: str) -> str:
    """A look another page wears, borrowed: the rules of its `css` whose
    selector names `part`, as .pills, as one style tag. A selector list
    keeps only what names it, and a rule inside an @media block stays the
    page's own."""
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", re.sub(r"/\*.*?\*/", "", css, flags=re.S))
    out = []
    for chosen, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        mine = [s.strip() for s in chosen.split(",") if part in s]
        if mine:
            out.append(f"  {', '.join(mine)} {{ {body.strip()} }}")
    return "<style>\n" + "\n".join(out) + "\n</style>"


def whole(css: str, parts: str) -> str:
    """A look another page wears, borrowed: each whole rule of its `css`
    whose selector matches the pattern `parts`, as one style tag. rules()
    would split an :is() selector apart. A rule inside an @media block
    stays the page's own."""
    css = re.sub(r"</?style>|/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    return "<style>\n" + "\n".join(f"  {s.strip()} {{ {b.strip()} }}" for s, b in
                                   re.findall(r"([^{}]+)\{([^{}]*)\}", css)
                                   if re.search(parts, s)) + "\n</style>"


def table() -> str:
    """The transcript page's table look: each whole rule of its style naming
    a table's part."""
    return whole(tool("transcript-page").STYLE, r"\.grid|table|\bth\b|\btd\b|tbody")


def gone(nn: str) -> str:
    """What a page says when session NN's pane, the one it types into, is gone."""
    return f"Session {nn}'s pane is gone. Nothing was typed."


def left(nn: str) -> str:
    """What a page says when Claude is gone from session NN's pane."""
    return f"Claude is gone from session {nn}'s pane. Nothing was typed."


def absent(nn: str) -> str:
    """left(nn) when Claude is gone from session NN's pane, else "".

    Its process ended with no stop, and its folder stands. The shell left
    in its pane runs a typed line as a command, so a path typing into a
    session asks here, or through typable(), first. A number with no
    folder is no session: "", and the caller's own pane check speaks.
    """
    mine = registry.entries().get(nn)
    if mine and registry.claude_records(fresh=True).get(mine.get("session_id")) is None:
        return left(nn)
    return ""


def typable(nn: str, ok: tuple) -> tuple:
    """Whether a page may type into session NN's pane now, as (why, mine, pane).

    `why` is the one sentence a refusal says, "" when typing is safe. `ok`
    holds the statuses the page types into; any other refuses, in its own
    sentence. iTerm is asked afresh, once: the pane list it answers names
    both the open panes and the session's. `mine` is the session's record,
    `pane` its pane, both empty on a refusal.
    """
    mine = registry.entries().get(nn)
    if not mine:
        return f"There is no session {nn}. Nothing was typed.", {}, ""
    rec = registry.claude_records(fresh=True).get(mine.get("session_id"))
    if rec is None:
        return left(nn), {}, ""
    status = rec.get("status")
    if status not in ok:
        why = {"waiting": f"A dialog waits in session {nn}'s pane.",
               "busy": f"Session {nn} is working.",
               "idle": f"Session {nn} sits idle at its prompt.",
               "shell": f"Session {nn} sits idle at its prompt, with a background shell running.",
               }.get(status, f"Session {nn}'s status reads {status}." if status else f"Session {nn} has no status.")
        return f"{why} Nothing was typed.", {}, ""
    open_ids = panes.ids()
    pane = panes.pane(mine, int(rec["pid"]), panes.FRESH)
    if not pane or (open_ids is not None and pane not in open_ids):
        return gone(nn), {}, ""
    return "", mine, pane


# The key live.watch() wears until render() puts the hash of the whole draw in.
WHOLE = 'data-key="whole"'


def render(title: str, sections: list, rail: str = "",
           refresh: int = 0, frame: bool = True) -> str:
    """Sections are (heading, html) pairs, in the order they are read.

    A heading of "" draws the section bare. An empty rail draws no rail, so
    a page that wants the whole glass still gets it. A page running its own
    frames, as 1100's home does, passes frame=False.

    A refresh of 0 draws no refresh tag at all. content="0" is not "never",
    it is "now", and the page reloads itself without pause. A page I type
    into asks for 0, because a reload takes the box away mid-word.

    A page's watch, as live.watch() writes it, wears the hash of the whole
    page drawn.
    """
    body = "".join((f"  <h2>{esc(h)}</h2>\n" if h else "") + f"  {b}\n"
                   for h, b in sections)
    tag = f'<meta http-equiv="refresh" content="{int(refresh)}">\n' if refresh else ""
    out = SHELL.format(title=esc(title), rail=rail, body=body, refresh=tag,
                       style=shared("shell.css"), script=shared("shell.js"),
                       tail=FRAME if frame else "")
    if WHOLE not in out:
        return out
    return out.replace(WHOLE, f'data-key="{hashlib.sha1(out.encode()).hexdigest()[:12]}"', 1)
