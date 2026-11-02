#!/usr/bin/env python3
"""page.py — the look every page in the behaviour band wears.

1100 draws every page but the prototypes, which the app on 1400 draws.
They are read side by side all day, so they share a shell: the same
tokens, the same rails, the same card.

A skill passes a title, a rail and its sections. It never writes CSS for
what the shell already rules.

A part two pages share sits here once: the watch, a page's own save,
typing into a pane, typing anywhere, a copy block's Copy button, the find
field, the close button, and the zoom tools a chart wears. So do tool(),
which loads a page tool for 1100 and the views it draws, rules() and
whole(), which borrow one look another page wears, and table(), the
transcript page's table look.

The page fills the glass. No column is centred and nothing is capped, because
every pixel it does not use is one I cannot read.

Every page keeps forty-one rules, and the shell carries each one it can.

  1  No scrollbar shows, bar a chart's own window, and only while the
     chart runs past that edge. Wheel and trackpad still scroll.
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


def reddened(acts: list, hold: float = 900) -> None:
    """Each act(nn, word, name) for each session whose number turns from
    green to red, on a thread of 1100's own, for as long as 1100 runs. The
    buzz and auto-send hang on the one watch. An act that raises is logged,
    and keeps no other act, nor any other session, from its turn.

    It sleeps until a session's record or Claude Code's own records are
    written. `hold` is the safety net: the colours are read again after
    that long, heard or not.
    """
    was = None
    while True:
        try:
            was = colours() if was is None else was
            hear.until(lambda: colours() != was, registry.watched(list(registry.entries())), seconds=hold)
            now = colours()
            for nn, (colour, word, name) in now.items():
                if colour == "red" and was.get(nn, ("",))[0] == "green":
                    for act in acts:
                        try:
                            act(nn, word, name)
                        except Exception:
                            traceback.print_exc()
            was = now
        except Exception:
            time.sleep(60)


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
WORDS = {"clarify": "Clarify", "assistant": "Assistant",
         "prototype": "Prototype", "launch": "Launch", "handover": "Handover",
         "system": "System", "skills": "Skills", "files": "Files", "agenda": "Agenda",
         "shots": "Screenshots", "walk": "Walk", "jury": "Jury"}
# Every kind of tab a session shows, once: its word, and the tool that
# draws its page, in the order a session's tabs run: those that can wait
# on me first, then those I read. Its icon is PATHS' of its own name.
# Home's model orders a hub's tabs by it, home draws them as the model hands
# them, and 1100 loads each kind's tool from it.
TAB_KINDS = {"clarify": ("Clarify", "clarify-page"), "jury": ("Jury", "jury-page"),
             "handover": ("Handover", "handover-page"), "launch": ("Launch", "launch-page"),
             "prototype": ("Prototype", "prototype-page"), "transcript": ("Transcript", "transcript-page"),
             "walk": ("Walk", "walk-list-page"), "shots": ("Screenshots", "walk-shots-page")}


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
  :root {{
    --bg:#0f1115; --panel:#161922; --line:#242835;
    --text:#e6e8ee; --dim:#8b91a3;
    --red:#f87171; --blue:#60a5fa; --green:#4ade80; --grey:#4b5162;
    --raised:#262b39; --hover:#30364a; --gold:#fbbf24;
  }}
  /* Every page paints dark from its first moment. No color-scheme: a frame
     whose scheme differs from the blank page it holds while loading paints
     that page white, the flash itself. */
  :root {{ background:var(--bg); }}
  * {{ box-sizing:border-box; }}
  /* No scrollbar shows, either way, bar a chart window's own: .chart .sb.
     Wheel and trackpad still scroll. */
  * {{ scrollbar-width:none; }}
  *::-webkit-scrollbar {{ display:none; width:0; height:0; }}
  html,body {{ height:100%; }}
  /* My phone never enlarges a block of text on its own, as it does once
     turned sideways: a page inside home zooms only by the rail's buttons. */
  html {{ -webkit-text-size-adjust:100%; text-size-adjust:100%; }}
  /* Only main scrolls. The rail is always open, so it never scrolls away. */
  body {{ margin:0; display:flex; overflow:hidden;
    background:var(--bg); color:var(--text);
    font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
  main {{ flex:1; min-width:0; overflow-y:auto; padding:6px; }}
  svg.i {{ flex:none; display:inline-block; vertical-align:middle; }}

  /* A side rail keeps one width, its head's. Nothing drags it. */
  aside {{ width:280px; flex:none; height:100%; overflow-y:auto;
    background:var(--panel); border-right:1px solid var(--line);
    padding:6px 8px; }}
  h2 {{ font-size:10px; text-transform:uppercase; letter-spacing:.08em;
    color:var(--dim); margin:0 0 5px; font-weight:600; }}
  main h2 {{ margin:8px 0 5px; }}
  main h2:first-child {{ margin-top:0; }}

  .state {{ color:var(--c); font-size:11px; font-weight:600; }}
  .dim {{ color:var(--dim); }}

  pre.doc {{ margin:0; padding:10px 14px; background:var(--panel);
    border:1px solid var(--line); border-radius:5px;
    white-space:pre-wrap; word-break:break-word; font:inherit; }}
  /* A screen with nothing to show: one large line, centred. */
  .empty {{ display:flex; align-items:center; justify-content:center; min-height:100%;
    padding:24px; text-align:center; font-size:clamp(20px, 4vw, 34px); font-weight:700;
    color:var(--dim); }}
  .empty p {{ margin:0; }}
  /* A note inside a page, when a part has nothing to show. */
  .note {{ color:var(--dim); padding:10px 8px; background:var(--panel);
    border:1px solid var(--line); border-radius:5px; }}

  /* Buttons in one group: one width, the widest's, in one order. */
  .group {{ display:inline-grid; grid-auto-flow:column; grid-auto-columns:1fr; gap:6px;
    align-items:center; }}
  .group > button, .group > a {{ justify-content:center; text-align:center; }}
  /* The pages' buttons, coloured by their receiver. Outline sends nothing
     yet: Type and Copy. White sends to a working session, gold to one
     steering others, the assistant or the advisor: into(). Green says it
     is done, red that it was refused. */
  .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; height:27px;
    padding:0 10px; border-radius:4px; cursor:pointer; white-space:nowrap; font:inherit;
    font-size:12px; font-weight:700; background:none; color:var(--text); border:1px solid var(--dim); }}
  .btn.go {{ background:#fff; color:#000; border-color:#fff; }}
  .btn.ask, [data-steers] .btn.go.own:not(.done, .gone) {{ background:var(--gold); color:#000;
    border-color:var(--gold); }}
  .btn.done, .btn.taken {{ background:var(--green); color:var(--bg); border-color:var(--green); }}
  .btn.gone {{ background:var(--red); color:var(--bg); border-color:var(--red); }}
  .btn:disabled {{ opacity:.45; cursor:default; }}
  /* CP, a hand-off's Copy: its copy icon, then a check once copied. */
  .cp .ok, .cp.done .no {{ display:none; }}
  .cp.done .ok {{ display:inline-block; }}
  /* A press that typed nothing says why, along the page's foot, in the
     launch page's banner look: TYPING's refusal(). */
  .refusal {{ position:fixed; left:12px; right:12px; bottom:12px; z-index:20; margin:0; padding:6px 9px;
    background:var(--panel); border:1px solid var(--red); border-radius:5px; color:var(--red); }}
  .refusal[hidden] {{ display:none; }}
  /* A close button: its cross alone, dim until hovered. A touch screen
     makes it a fingertip. */
  .close {{ flex:none; display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px;
    padding:0; color:var(--dim); background:none; border:1px solid var(--line); border-radius:4px; cursor:pointer; }}
  .close:hover {{ color:var(--text); background:var(--hover); border-color:var(--dim); }}
  @media (hover:none) and (pointer:coarse) {{
    .close {{ width:44px; height:44px; }}
  }}

  /* A rail row I click. It shows one thing in main, and wears .on while
     it does. Its dot and its status word say where that thing stands. */
  .tab {{ margin:0 -4px 6px; padding:1px 4px; border-radius:4px;
    cursor:pointer; }}
  .tab:hover, .tab.on {{ background:var(--bg); }}

  /* One item, alone in main. Two sizes only: the title, and the rest.
     Nothing opens or closes. */
  .item {{ display:none; background:var(--panel); border:1px solid var(--line);
    border-left:4px solid var(--c); border-radius:6px;
    padding:18px 22px; margin:12px 16px; }}
  .item.on {{ display:block; }}
  .item p, .item li {{ font-size:17px; line-height:1.55; margin:0 0 10px; }}
  .item h3 {{ font-size:28px; line-height:1.25; margin:0 0 20px; }}
  .part {{ display:flex; gap:14px; }}
  .part .k {{ flex:none; width:18ch; color:var(--dim); }}
  .part.rec .v {{ color:var(--green); }}
  .agree {{ display:inline-block; margin-top:14px; font:inherit; font-size:17px;
    font-weight:700; padding:10px 20px; border-radius:6px; cursor:pointer;
    background:var(--bg); color:var(--green); border:2px solid var(--green); }}
  .agree:hover {{ background:color-mix(in srgb, var(--green) 14%, var(--bg)); }}
  .agree.on {{ background:var(--green); color:var(--bg); }}
  .agree.locked, .agree:disabled {{ cursor:default; }}
  .agree:disabled {{ opacity:.45; }}
  .item p.hint {{ color:var(--dim); margin:8px 0 0; }}
  .field {{ display:block; width:100%; margin-top:18px; font:inherit; font-size:17px;
    padding:12px 14px; border-radius:6px; background:var(--bg); color:var(--text);
    border:2px solid var(--line); }}
  .field:focus {{ outline:none; border-color:var(--blue); }}

  /* A field that finds as I type: its icon, then the words. Each page
     sizes it where it sits. */
  .find {{ display:flex; align-items:center; gap:7px; height:28px; padding:0 3px 0 8px;
    background:var(--bg); border:1px solid var(--dim); border-radius:5px; color:var(--dim); }}
  .find:focus-within {{ border-color:var(--blue); }}
  .find input {{ flex:1; min-width:0; height:100%; padding:0; border:0; outline:0; background:none;
    color:var(--text); font:inherit; font-size:13px; }}
  .find input::placeholder {{ color:var(--dim); }}
  /* A touch screen: the field takes a fingertip, and 16px text, WebKit's
     standard size. Smaller, a tap into it zooms the page. */
  @media (hover:none) and (pointer:coarse) {{
    .find {{ height:auto; }}
    .find input {{ height:44px; font-size:16px; }}
  }}

  /* The zoom tools a chart wears: −, + and Fit, one group, then the
     percent it shows at. ZOOM wires them; where they sit sizes them. */
  .zt {{ display:inline-flex; align-items:center; gap:4px; }}
  .zt .group {{ gap:4px; }}
  .zt .group button {{ width:100%; }}
  .zt .pct {{ min-width:5ch; margin-left:4px; text-align:right; font-variant-numeric:tabular-nums; }}

  /* Two rails, both as thin as they go, for a page that draws a
     header.top. The top one spans the glass and holds the page's tools.
     The left one holds only numbers, each wearing its colour. */
  body:has(> header.top) {{ display:grid; grid-template-columns:auto 1fr;
    grid-template-rows:auto 1fr; }}
  body:has(> header.top) > main {{ min-height:0; grid-column:2 / 3; }}
  header.top {{ grid-column:1 / -1; display:grid;
    grid-template-columns:1fr auto 1fr; align-items:center; gap:12px;
    padding:6px 12px; background:var(--panel);
    border-bottom:1px solid var(--line); }}
  header.top b {{ font-size:18px; }}
  header.top .wave {{ font-size:16px; font-weight:700; color:var(--blue); }}
  /* A head's own buttons. A .btn or a pill borrowed into a head keeps its
     own look. */
  header.top button:not(:where(.btn, .pills button)) {{ justify-self:end; font:inherit; font-size:18px;
    font-weight:700; padding:8px 32px; border-radius:6px; cursor:pointer;
    background:#fff; color:#000; border:0; }}
  header.top button:not(:where(.btn, .pills button)):disabled {{ background:var(--grey); color:var(--text);
    cursor:not-allowed; }}
  header.top button.sent:not(:where(.btn, .pills button)) {{ background:var(--green); color:var(--bg);
    cursor:default; }}
  header.top button.gone:not(:where(.btn, .pills button)) {{ background:var(--red); color:var(--bg); }}

  /* A head naming its family: the icon and the word, then the session's
     tag, on the left. What the page shows sits in the middle. Its tools
     sit together on the right, one group. */
  header.top.fam {{ grid-template-columns:auto minmax(0,1fr) auto; min-height:40px;
    padding:6px 10px; min-width:0; }}
  header.top.fam .who {{ display:inline-flex; align-items:center; gap:8px; white-space:nowrap; min-width:0;
    overflow:hidden; }}
  header.top.fam .who b {{ font-size:13px; }}
  .fam {{ display:inline-flex; align-items:center; gap:6px; color:var(--text); white-space:nowrap; }}
  .fam b, header.top.fam .who .fam b {{ font-size:12px; letter-spacing:.02em; }}
  header.top.fam .mid {{ justify-self:center; min-width:0; overflow:hidden; text-overflow:ellipsis;
    white-space:nowrap; font-size:14px; font-weight:700; color:var(--blue); }}
  header.top.fam .acts {{ justify-self:end; display:flex; align-items:center; gap:6px; }}
  header.top.fam button:not(:where(.btn, .pills button)) {{ justify-self:auto; font-size:13px; padding:5px 14px; }}
  /* A driven session's band: edge to edge under the head's row. */
  header.top.fam .by {{ grid-column:1 / -1; display:flex; align-items:center; gap:6px; margin:-6px -10px -6px;
    padding:5px 10px; font-size:12px; color:var(--dim); background:var(--raised); border-top:1px solid var(--line); }}
  /* Under 1100's tab: the tab names the family and the session. */
  html.slim header.top.fam {{ grid-template-columns:minmax(0,1fr) auto; }}
  html.slim header.top.fam .who {{ display:none; }}
  html.slim header.top.fam .mid {{ justify-self:start; }}
  html.slim header.top:not(.fam) > b:first-child {{ visibility:hidden; }}
  @media (max-width:520px) {{
    header.top.fam {{ grid-template-columns:minmax(0,1fr) auto; gap:8px; }}
    header.top.fam .mid {{ display:none; }}
    header.top.fam button:not(:where(.btn, .pills button)) {{ padding:5px 10px; }}
  }}

  nav.nums {{ min-height:0; overflow-y:auto; padding:6px 4px;
    background:var(--panel); border-right:1px solid var(--line); }}
  nav.nums .tab {{ display:block; width:26px; margin:0 0 4px; padding:2px 0;
    text-align:center; font-weight:700; border-radius:4px;
    background:var(--c); color:var(--bg); }}
  nav.nums .tab.g {{ color:var(--text); }}
  nav.nums .tab.on {{ outline:2px solid var(--text); outline-offset:1px; }}
  nav.nums .tab.hint {{ box-shadow:inset 0 0 0 2px var(--h); }}

  /* The clarify page. Every item stacks in main, each with its own
     feedback box. */
  header.top.fam button.agree {{ margin:0; padding:4px 16px; background:var(--bg);
    color:var(--green); border:2px solid var(--green); font-size:13px; }}
  header.top.fam button.agree.on {{ background:var(--green); color:var(--bg); opacity:1; }}
  header.top.fam button.agree:disabled:not(.on) {{ background:var(--grey);
    color:var(--text); border-color:var(--grey); opacity:1; }}
  header.top.fam button#send {{ border:2px solid #fff; }}
  header.top.fam button#send:disabled {{ border-color:var(--grey); }}
  header.top.fam button#send.sent {{ border-color:var(--green); }}
  header.top.fam button#send.gone {{ border-color:var(--red); }}
  /* While its line types, Send's word gives way to a spinner. */
  header.top.fam button#send.busy {{ position:relative; background:#fff; color:transparent;
    border-color:#fff; cursor:progress; }}
  header.top.fam button#send.busy::after {{ content:""; position:absolute; inset:0; margin:auto;
    width:14px; height:14px; border-radius:50%; border:2px solid transparent;
    border-top-color:#000; border-right-color:#000; animation:spin .7s linear infinite; }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
  body:has(> header.top.clarify) > main {{ padding:0; }}
  #items {{ flex:1 0 auto; padding:22px 32px 28px; }}
  #items .item {{ background:none; border:0; border-radius:0; padding:0; margin:0; }}
  #items .item p, #items .item li {{ font-size:16px; line-height:1.55; margin:0 0 6px; }}
  #items .item p.kick {{ color:var(--dim); font-size:13px; margin-bottom:8px; }}
  #items .kick b {{ color:var(--c); }}
  #items .item h1.q {{ font-size:28px; line-height:1.25; margin:0 0 14px; }}
  #items .item p.dec {{ font-size:16px; line-height:1.45; font-weight:700; }}
  #items .dec .arr {{ color:var(--dim); margin-right:6px; }}
  #items .why .k, #items .from .k {{ color:var(--dim); margin-right:8px; }}
  #items .link {{ color:var(--blue); cursor:pointer; text-decoration:underline; }}
  #items h2.sec {{ font-size:11px; letter-spacing:.09em; text-transform:uppercase;
    color:var(--dim); margin:28px 0 10px; padding-top:14px;
    border-top:1px solid var(--line); font-weight:700; }}
  #items h3.sub {{ font-size:13px; color:var(--dim); margin:16px 0 6px; font-weight:700; }}
  #items ul.b {{ margin:0 0 6px; padding-left:20px; }}
  #items ul.split li .out {{ color:var(--blue); white-space:nowrap; }}
  #items .row {{ display:grid; grid-template-columns:10ch 1fr; gap:16px; margin-bottom:10px; }}
  #items .row .k {{ color:var(--dim); font-size:15px; padding-top:2px; }}
  #items .row.src .v {{ color:var(--dim); font-size:14px; }}
  /* The feedback bar is one line at rest. It opens while I type in it, or
     while it holds my answer, and grows with the text up to a third of
     the glass. */
  .bar {{ position:sticky; bottom:0; flex:none; padding:6px 24px 8px;
    background:var(--panel); border-top:1px solid var(--line);
    display:flex; flex-direction:column; gap:6px; }}
  .bar.open {{ padding:8px 24px 12px; }}
  .bar .lab {{ font-size:11px; letter-spacing:.09em; text-transform:uppercase;
    color:var(--dim); font-weight:700; display:none; }}
  .bar.open .lab {{ display:flex; }}
  .bar .lab .st {{ margin-left:auto; text-transform:none; letter-spacing:0;
    font-weight:400; }}
  .bar textarea {{ flex:none; height:40px; max-height:calc(30 * var(--vh, 1vh) - 44px); overflow-y:auto;
    resize:none; font:inherit; font-size:14px; line-height:1.5;
    padding:8px 14px; border-radius:6px; background:var(--bg); color:var(--text);
    border:2px solid var(--line); }}
  .bar textarea:focus {{ outline:none; border-color:var(--blue); }}
  .bar.hide {{ display:none; }}

  /* The clarify page's text is small enough that a whole item fits the
     pane. The assistant page shares #items, so these reach only the page
     whose head is clarify's. */
  header.top.clarify ~ main #items {{ padding:0 0 20px; }}
  /* Every item shows, one under the other. Its own padding carries main's
     sides, so the rectangle between two items runs edge to edge. */
  header.top.clarify ~ main #items .item {{ display:block; padding:20px 24px 28px; }}
  header.top.clarify ~ main #items .item + .item {{ border-top:36px solid var(--hover); }}
  /* The item's number, the rail's chip, before its question. */
  header.top.clarify ~ main #items .item h1.q .chip {{ font-size:16px; line-height:26px; min-width:34px;
    margin-right:12px; vertical-align:2px; }}
  /* Each item's own feedback box, at its foot. One line at rest, it opens
     while I type in it, or while it holds my answer, and grows with the
     text. */
  header.top.clarify ~ main .fbx {{ margin-top:22px; display:flex; flex-direction:column; gap:6px; }}
  header.top.clarify ~ main .fbx .lab {{ display:flex; font-size:11px; letter-spacing:.09em;
    text-transform:uppercase; color:var(--dim); font-weight:700; }}
  header.top.clarify ~ main .fbx .lab .st {{ margin-left:auto; text-transform:none; letter-spacing:0;
    font-weight:400; }}
  header.top.clarify ~ main .fbx textarea {{ height:40px; overflow-y:hidden; resize:none; font:inherit;
    font-size:14px; line-height:1.5; padding:8px 14px; border-radius:6px; background:var(--panel);
    color:var(--text); border:2px solid var(--line); }}
  header.top.clarify ~ main .fbx textarea:focus {{ outline:none; border-color:var(--blue); }}
  header.top.clarify ~ main #items .item p,
  header.top.clarify ~ main #items .item li {{ font-size:14px; line-height:1.5; margin:0 0 5px; }}
  header.top.clarify ~ main #items .item h1.q {{ font-size:20px; margin:0 0 8px; }}
  header.top.clarify ~ main #items .item p.dec {{ font-size:16px; line-height:1.45; margin:0 0 6px; }}
  header.top.clarify ~ main #items h2.sec {{ margin:18px 0 8px; padding-top:10px; }}
  header.top.clarify ~ main #items .item p.srcs {{ color:var(--dim); font-size:12px; margin:18px 0 0; }}
  header.top.clarify ~ main #items .item .chart p {{ font-size:inherit; line-height:inherit; margin:0; }}

  /* The clarify page's pictures, always under the decision. A text fence
     is a pre. A chart is a frame: a strip that zooms, fits and flips it,
     then a window holding the SVG Mermaid draws, then the legend the page
     adds under it. */
  #items pre.pre, #items pre.mmd {{ margin:4px 0 6px; padding:8px 12px;
    background:var(--panel); border:1px solid var(--line); border-radius:5px;
    font-size:13px; line-height:1.4; white-space:pre; overflow-x:auto; }}
  #items pre .dim, #items .legend b.dim {{ color:var(--dim); font-weight:400; }}
  #items .chart {{ margin:4px 0 6px; }}
  #items .chart .cf {{ border:1px solid var(--line); border-radius:5px; overflow:hidden; }}
  #items .chart .strip {{ display:flex; align-items:center; gap:4px; padding:3px 6px;
    background:var(--panel); border-bottom:1px solid var(--line); color:var(--dim); font-size:11px; }}
  #items .chart .strip button {{ font:inherit; font-size:12px; font-weight:700; line-height:1;
    min-width:24px; height:20px; padding:0 7px; border-radius:4px; cursor:pointer;
    background:var(--bg); color:var(--text); border:1px solid var(--line); }}
  #items .chart .strip button:hover:not(:disabled) {{ border-color:var(--dim); }}
  #items .chart .strip button:disabled {{ color:var(--dim); cursor:default; opacity:.5; }}
  #items .chart .strip button.flip {{ margin-left:8px; }}
  #items .chart .strip .tip {{ margin-left:auto; }}
  #items .chart .cv {{ position:relative; height:0; overflow:hidden;
    user-select:none; -webkit-user-select:none; }}
  #items .chart .cv.away {{ cursor:grab; touch-action:none; }}
  #items .chart .cv.drag {{ cursor:grabbing; }}
  /* The window's bottom edge, a bar to drag down: the window grows, and
     the chart zooms with it. */
  #items .chart .grip {{ position:relative; height:12px; cursor:ns-resize; touch-action:none;
    background:var(--panel); border-top:1px solid var(--line); }}
  #items .chart .grip::after {{ content:''; position:absolute; left:50%; top:4px; width:40px;
    margin-left:-20px; height:3px; border-radius:2px; background:var(--dim); opacity:.5; }}
  #items .chart .grip:hover::after, #items .chart .grip.drag::after {{ opacity:1; }}
  /* The window's scroll bars, over the chart, each shown only while the
     chart runs past that edge. */
  #items .chart .sb {{ position:absolute; z-index:1; display:none; touch-action:none;
    background:rgba(139,145,163,.08); border-radius:4px; }}
  #items .chart .sb.on {{ display:block; }}
  #items .chart .sb.x {{ left:2px; right:14px; bottom:2px; height:8px; }}
  #items .chart .sb.y {{ top:2px; bottom:14px; right:2px; width:8px; }}
  #items .chart .sb i {{ position:absolute; border-radius:4px; background:var(--dim); opacity:.55; }}
  #items .chart .sb.x i {{ top:0; bottom:0; }}
  #items .chart .sb.y i {{ left:0; right:0; }}
  #items .chart .sb:hover i, #items .chart .sb.drag i {{ opacity:.95; }}
  #items .chart .cz {{ transform-origin:0 0; }}
  #items .chart .cz svg {{ display:block; width:100%; height:100%; }}
  #items .legend {{ display:flex; flex-wrap:wrap; gap:4px 16px; margin:2px 0 10px;
    color:var(--dim); font-size:12px; }}
  #items .lg {{ display:inline-flex; align-items:center; gap:6px; }}
  #items .lg b {{ color:var(--text); }}
  #items .lg .sw {{ width:13px; height:9px; border:2px solid var(--c); border-radius:2px; }}
  #items .lg .sh {{ border:1.5px solid var(--dim); }}
  #items .lg .dia {{ width:8px; height:8px; transform:rotate(45deg); margin:0 2px; }}
  #items .lg .cyl {{ width:11px; height:12px; border-radius:6px / 3px; }}
  #items .lg .ar {{ width:20px; border-top:2px solid var(--dim); }}
  #items .lg .ar.dash {{ border-top-style:dashed; }}

  /* An assistant's proposal, under the decision and above its why, across
     the whole width. Blue, because a session wrote it. Take it turns green
     once taken. */
  #items .prop {{ margin:4px 0 14px; padding:10px 14px; background:var(--panel);
    border:1px solid var(--line); border-left:3px solid var(--blue); border-radius:5px; }}
  #items .prop .ph {{ font-size:11px; letter-spacing:.09em; text-transform:uppercase;
    color:var(--blue); font-weight:700; margin-bottom:6px; }}
  header.top.clarify ~ main #items .item .prop p.pw {{ color:var(--dim); font-size:13px; margin:0 0 6px; }}
  #items .prop blockquote.pq {{ margin:0 0 8px; padding:6px 10px; background:var(--bg);
    border-left:2px solid var(--dim); white-space:pre-wrap; font-size:14px; line-height:1.5; }}
  #items .prop button.take {{ font:inherit; font-size:13px; font-weight:700; padding:4px 14px;
    border-radius:4px; cursor:pointer; background:#fff; color:#000; border:0; }}
  #items .prop button.take:disabled {{ background:var(--green); color:var(--bg); cursor:default; }}

  /* The assistant page. Its rail and main are clarify's: mission ids,
     each stage's letter above its own, a thin line between stages, and
     no frame around main. */
  nav.nums .gap {{ height:1px; margin:8px 2px 10px; background:var(--line); }}
  nav.nums .tab.stg {{ background:none; color:var(--dim); font-size:11px;
    margin:0 0 3px; padding:0; }}
  nav.nums .tab.stg:hover, nav.nums .tab.stg.on {{ color:var(--text); }}
  nav.nums .tab.stg.on {{ outline:1px solid var(--dim); }}
  #items h3.sub.go {{ cursor:pointer; }}
  #items h3.sub.go:hover {{ color:var(--text); text-decoration:underline; }}
  .chip {{ flex:none; display:inline-block; min-width:26px; padding:0 4px;
    text-align:center; border-radius:4px; font-weight:700;
    background:var(--c, var(--grey)); color:var(--bg); }}
  .chip.g {{ color:var(--text); }}
  .chip.dashed {{ background:none; color:var(--c, var(--grey));
    box-shadow:inset 0 0 0 1px var(--c, var(--grey)); }}
  nav.nums .tab.done {{ background:none; color:var(--dim);
    box-shadow:inset 0 0 0 1px var(--grey); }}
  nav.nums .tab.dashed {{ background:none; color:var(--c);
    box-shadow:inset 0 0 0 2px var(--c); }}
  .paste {{ position:relative; margin:6px 0 12px; padding:10px 96px 10px 14px;
    background:var(--panel); border-left:3px solid var(--blue); }}
  .paste .txt {{ white-space:pre-wrap; font-size:15px; line-height:1.55; }}
  .paste > button {{ position:absolute; top:8px; right:8px; font:inherit;
    font-size:12px; font-weight:700; padding:4px 14px; border-radius:4px;
    cursor:pointer; background:none; color:var(--text); border:1px solid var(--dim); }}
  .paste > button.done {{ background:var(--green); color:var(--bg); border-color:var(--green); }}
  /* A move's paste also types into its session: Copy, Type and the send
     button sit above its words, on the right, and the words take the
     whole width. */
  .paste.to {{ padding-right:14px; }}
  .paste .acts {{ display:flex; justify-content:flex-end; margin-bottom:8px; }}

  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. A
     field's text is 16px, WebKit's standard size: smaller, a tap into it
     zooms the page. Only the clarify page's parts sit here. The assistant
     and handover pages carry their own. */
  @media (hover:none) and (pointer:coarse) {{
    header.top.clarify button {{ min-height:44px; }}
    header.top.clarify ~ nav.nums .tab {{ width:44px; padding:0; line-height:44px; }}
    header.top.clarify ~ main #items .link {{ padding:14px 0; }}
    header.top.clarify ~ main #items .prop button.take {{ min-height:44px; }}
    /* The chart's strip wraps whole, its tip last, never over itself. */
    header.top.clarify ~ main #items .chart .strip {{ flex-wrap:wrap; }}
    header.top.clarify ~ main #items .chart .strip button {{ min-width:44px; height:44px;
      white-space:nowrap; }}
    /* At rest, the feedback box keeps its hint to one line. */
    header.top.clarify ~ main .fbx textarea {{ min-height:44px; font-size:16px; }}
    header.top.clarify ~ main .fbx:not(.open) textarea,
    header.top.clarify ~ main .fbx:not(.open) textarea::placeholder {{ white-space:nowrap;
      overflow:hidden; text-overflow:ellipsis; }}
    /* Half my phone: the sides tighten, so the strip's tools share a line. */
    @media (max-width:520px) {{
      header.top.clarify ~ main #items .item {{ padding-left:12px; padding-right:12px; }}
    }}
  }}
</style>
<script>
/* Framed by 1100's home, a page wears home's zoom from its first draw, so
   nothing it lays out moves once home applies it. FRAME follows it after. */
try {{ if (parent !== window) {{ const z = +localStorage.getItem('home-zoom');
  if (z && z !== 1) document.documentElement.style.zoom = String(z); }} }} catch (e) {{}}
/* When I last typed into a field here: a page never reloads within three
   seconds of it, so a reload never takes a box away mid-word. WATCH and
   home's watch both wait on it. */
addEventListener('input', () => {{ window.typedAt = Date.now(); }}, true);
addEventListener('wheel', e => {{ if (e.ctrlKey) e.preventDefault(); }}, {{passive: false}});
addEventListener('gesturestart', e => e.preventDefault());
addEventListener('gesturechange', e => e.preventDefault());
(() => {{
  let settle = 0;
  addEventListener('resize', () => {{
    clearTimeout(settle);
    settle = setTimeout(() => {{
      const s = document.body.style;
      s.transform = 'translateZ(0)';
      requestAnimationFrame(() => requestAnimationFrame(() => {{ s.transform = ''; }}));
    }}, 150);
  }});
}})();
</script>
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
FRAME = """<script>
(() => {
  if (parent === window) return;
  const root = document.documentElement;
  root.classList.add('framed');
  const zoom = () => parseFloat(root.style.zoom) || 1;
  const glass = () => root.style.setProperty('--vh', innerHeight / zoom() / 100 + 'px');
  let was = zoom();
  glass();
  addEventListener('resize', glass);
  new MutationObserver(() => {
    if (zoom() === was) return;
    was = zoom();
    glass();
    dispatchEvent(new Event('ws-zoom'));
  }).observe(root, {attributes: true, attributeFilter: ['style']});
  addEventListener('message', e => {
    const d = e.data || {};
    if (e.source !== parent || !d.ws) return;
    if ('slim' in d) root.classList.toggle('slim', !!d.slim);
    if ('zoom' in d) root.style.zoom = d.zoom === 1 ? '' : String(d.zoom);
    if (d.go) dispatchEvent(new Event('ws-' + d.go));
  });
  parent.postMessage({ws: 1, hello: 1}, '*');
})();
</script>
"""

# Shows the item a tab names, and keeps it in the address, so a reload
# lands on the same one. Only an item or a tab carries these ids.
TABS = """<script>
function tab(k) {
  k = String(k);
  document.querySelectorAll('.item').forEach(e => e.classList.toggle('on', e.id === 't-' + k));
  document.querySelectorAll('.tab').forEach(e => e.classList.toggle('on', e.dataset.k === k));
  history.replaceState(null, '', '#' + encodeURIComponent(k));
}
</script>
"""

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
TYPING = """<script>
const NOT_TYPED = 'Not typed', UNANSWERED = '1100 did not answer. Nothing was typed.';
async function typePost(data, to = location.pathname) {
  try {
    const r = await fetch(to, {method: 'POST', redirect: 'manual', body: new URLSearchParams(data)});
    if (r.status === 409) return await r.text();
    return r.ok || r.type === 'opaqueredirect' ? '' : null;
  } catch (e) { return null; }
}
// The sentence a refused press says, until the next press or eight seconds on.
let refusalTimer = 0;
function refusal(said) {
  let p = document.getElementById('refusal');
  if (!p && !said) return;
  if (!p) {
    p = document.createElement('p');
    p.id = 'refusal';
    p.className = 'refusal';
    p.setAttribute('role', 'status');
    document.body.appendChild(p);
  }
  clearTimeout(refusalTimer);
  p.textContent = said;
  p.hidden = !said;
  if (said) refusalTimer = setTimeout(() => { p.hidden = true; }, 8000);
}
async function pressed(b, data, unsent) {
  if ('was' in b.dataset) { b.innerHTML = b.dataset.was; b.title = b.dataset.tip; delete b.dataset.was; }
  b.classList.remove('gone');
  refusal('');
  b.disabled = true;
  const said = await typePost(data);
  b.disabled = false;
  if (said === '') {
    const was = b.innerHTML;
    if (unsent) b.textContent = 'Typed';
    b.classList.add('done');
    setTimeout(() => { b.innerHTML = was; b.classList.remove('done'); }, 1500);
    return said;
  }
  const why = said || UNANSWERED;
  b.dataset.was = b.innerHTML;
  b.dataset.tip = b.title;
  b.textContent = NOT_TYPED;
  b.title = why;
  b.classList.add('gone');
  refusal(why);
  return said;
}
</script>
"""

# A copy block's Copy button, pressed: the block's words go onto the
# clipboard, and the button reads Copied, green, for a moment. The words
# are the nearest .txt above it, so a Copy inside a group finds its
# block's. Each page showing a session's reply calls copied() from its own
# click.
COPY = """<script>
function copied(b) {
  let box = b.parentNode;
  while (box && !box.querySelector('.txt')) box = box.parentNode;
  const text = box.querySelector('.txt').textContent, word = b.querySelector('span'), was = word.textContent;
  navigator.clipboard?.writeText(text).then(() => {
    b.classList.add('done');
    word.textContent = 'Copied';
    setTimeout(() => { b.classList.remove('done'); word.textContent = was; }, 1500);
  }, () => {});
}
</script>
"""

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
ANYWHERE = """<script>
function anywhere(typeIn, tabIn) {
  if (matchMedia('(hover: none) and (pointer: coarse)').matches) return;
  const field = e => e.target.closest && e.target.closest('input, textarea, [contenteditable]');
  const chrome = /(?:Chrome|Chromium)\\//.test(navigator.userAgent);
  window.typeIn = typeIn;
  if (tabIn) window.tabIn = tabIn;
  addEventListener('keydown', e => {
    if (field(e) || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === 'Tab' && !e.shiftKey) { if (tabIn && tabIn()) e.preventDefault(); return; }
    if (e.key.length === 1 && e.key !== ' ' && typeIn(e.key)) e.preventDefault();
  });
  addEventListener('paste', e => {
    const t = field(e), clip = e.clipboardData;
    if (!e.defaultPrevented && chrome && t && t.matches('textarea:not(:disabled):not([readonly])')
        && clip && !clip.files.length) {
      const text = clip.getData('text/plain');
      if (text && document.execCommand('insertText', false, text)) { e.preventDefault(); return; }
    }
    if (!e.defaultPrevented && !field(e) && typeIn(e.clipboardData.getData('text'))) e.preventDefault();
  });
}
</script>
"""

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
ZOOM = """<script>
const ZOOM_TOOLS = %TOOLS%;
function zoomer(tools, win, chart) {
  const STEP = 1.25, z = k => tools.querySelector('[data-z=' + k + ']'), pct = tools.querySelector('.pct');
  const paint = () => {
    const s = chart.scale(), [lo, hi] = s ? chart.bounds() : [0, 0];
    z('out').disabled = !s || s <= lo;
    z('in').disabled = !s || s >= hi;
    z('fit').disabled = !s || chart.fitted();
    pct.textContent = s ? Math.round(s * 100) + '%' : '';
  };
  // A size a hair from a bound lands on it, so a step back out ends fitted.
  const go = (s, at) => {
    const [lo, hi] = chart.bounds();
    chart.to(s <= lo * (1 + 1e-9) ? lo : s >= hi * (1 - 1e-9) ? hi : s, at);
    paint();
  };
  const point = e => { const r = win.getBoundingClientRect(); return {x: e.clientX - r.left, y: e.clientY - r.top}; };
  z('out').onclick = () => { if (chart.scale()) go(chart.scale() / STEP, null); };
  z('in').onclick = () => { if (chart.scale()) go(chart.scale() * STEP, null); };
  z('fit').onclick = () => { if (chart.scale()) { chart.fit(); paint(); } };
  // While a gesture runs, its Ctrl wheel is ignored, so nothing zooms twice.
  let pinch = 0;
  win.addEventListener('wheel', e => {
    if (!e.ctrlKey) return;
    e.preventDefault();
    if (pinch || !chart.scale()) return;
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? win.clientHeight : 1;
    go(chart.scale() * Math.exp(-Math.max(-50, Math.min(50, e.deltaY * unit)) * 0.01), point(e));
  }, {passive: false});
  win.addEventListener('gesturestart', e => { e.preventDefault(); pinch = chart.scale(); });
  win.addEventListener('gesturechange', e => { e.preventDefault(); if (pinch) go(pinch * e.scale, point(e)); });
  win.addEventListener('gestureend', e => { e.preventDefault(); pinch = 0; });
  return paint;
}
</script>
""".replace("%TOOLS%", json.dumps(ZOOM_TOOLS).replace("</", "<\\/"))

# A page I type into never refreshes itself, because a reload takes the box
# away mid-word. It reloads only once its key moves, and never within three
# seconds of my typing, the shell's typedAt. It is told: /heard holds
# the question until the key has changed, then it asks again. 1100 and the
# prototypes app both hold it, and mark a held answer with the X-Heard
# header. A server gone, as on a restart, or one answering without it, is
# asked again a few seconds later. The watch taken away, it never reloads.
#
# A page that draws itself again in place, as a transcript does, defines
# told(now). Its key moved, it is handed the new one, and never reloads.
#
# A browser holds six requests to one host at once, and each held watch is
# one. A page framed by a page of its own server that watches for its
# frames, as 1100's home does, hands its watch up instead of holding one.
#
# The watch asks about the page's whole address, its query too, as it
# stands at each ask: Files names its picked file there.
#
# A page with no box I type into builds no key: it wears a hash of its whole
# draw, so anything it draws moving reloads it. A hand-picked key drifts
# from the draw, and what it forgets shows only on a reload of my own.
WATCH = """<div id="watch" data-key="{key}" hidden></div>
<script>
(async () => {{
  const here = () => document.getElementById('watch');
  try {{ if (parent !== window && parent.watchFor) return parent.watchFor(window); }} catch (e) {{}}
  const nap = ms => new Promise(f => setTimeout(f, ms));
  const settled = async () => {{ while (here() && 'busy' in here().dataset) await nap(50); return here(); }};
  for (;;) {{
    try {{
      if (!here()) return;
      const r = await fetch('/heard?key=' + encodeURIComponent(here().dataset.key)
                            + '&path=' + encodeURIComponent(location.pathname + location.search));
      if (r.headers.get('X-Heard')) {{
        const now = await r.text(), w = await settled();
        if (!w) return;
        if (now !== w.dataset.key) {{
          if (typeof window.told === 'function') {{ await window.told(now); continue; }}
          while (Date.now() - (window.typedAt || 0) < 3000) await nap(500);
          return location.reload();
        }}
        continue;
      }}
    }} catch (e) {{}}
    await nap(3000);
  }}
}})();
</script>
"""

# A page that saves its own file saves through post(body): it posts the body
# to its own path, its watch marked busy until every save lands, then sets
# the watch's key to the one its save left. Its own save never reloads it,
# framed or alone. It answers whether the save landed, so a page never says
# saved when 1100 did not answer.
POST = """<script>
let saving = 0;
async function post(body) {
  const w = document.getElementById('watch');
  let landed = false;
  saving++;
  if (w) w.dataset.busy = '';
  try {
    const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual', body: new URLSearchParams(body)});
    landed = r.ok || r.type === 'opaqueredirect';
    if (w) w.dataset.key = await (await fetch(location.pathname + '/key')).text();
  } catch (e) {}
  if (!--saving && w) delete w.dataset.busy;
  return landed;
}
</script>
"""


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


# The key a watch wears until render() puts the hash of the whole draw in.
WHOLE = 'data-key="whole"'


def watch(key: str = "") -> str:
    """Reload the page when its key changes, or hand a page defining
    told(now) the new key. The key names the file's state. A page with no
    box I type into passes none, and render() hashes its whole draw."""
    return TABS + (WATCH.replace('data-key="{key}"', WHOLE).format() if not key
                   else WATCH.format(key=esc(key)))


def render(title: str, sections: list, rail: str = "",
           refresh: int = 0, frame: bool = True) -> str:
    """Sections are (heading, html) pairs, in the order they are read.

    A heading of "" draws the section bare. An empty rail draws no rail, so
    a page that wants the whole glass still gets it. A page running its own
    frames, as 1100's home does, passes frame=False.

    A refresh of 0 draws no refresh tag at all. content="0" is not "never",
    it is "now", and the page reloads itself without pause. A page I type
    into asks for 0, because a reload takes the box away mid-word.

    A watch with no key of its own wears the hash of the whole page drawn.
    """
    body = "".join((f"  <h2>{esc(h)}</h2>\n" if h else "") + f"  {b}\n"
                   for h, b in sections)
    tag = f'<meta http-equiv="refresh" content="{int(refresh)}">\n' if refresh else ""
    out = SHELL.format(title=esc(title), rail=rail, body=body, refresh=tag,
                       tail=FRAME if frame else "")
    if WHOLE not in out:
        return out
    return out.replace(WHOLE, f'data-key="{hashlib.sha1(out.encode()).hexdigest()[:12]}"', 1)
