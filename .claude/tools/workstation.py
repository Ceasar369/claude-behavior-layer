#!/usr/bin/env python3
"""workstation.py — 1100's home: what waits on me, and the team it belongs to.

1100 is the only page server. Home opens on the Skills page. Its address
keeps where I am, so a reload lands back there. An assistant's page
always shows while its session holds a plan, and waits on me while one of
its missions needs my hand: assistant-page.py's due. A jury
tab shows from its plan landing, for its session's newest run, and waits
on me only while that plan waits for Launch: jury-page.py's tab(). A
Walk tab shows while a session holds walk-list.md, and a Screenshots tab
once its own walk holds a screenshot:
walk-list-page.py's and walk-shots-page.py's tab(). Neither waits on
me. Every other page shows only while it waits on me: a clarify wave not sent, a
launch with rows, a prototype a running session holds, not locked in, or
a handover once a session's context passes System's threshold. A launch a
drive scheduled shows too, and so does a handover once pressed, until its
page clears, but none waits on me, so none wears a dot. Nor does any
page while its session works or is gone, its number green or grey: a page
waits on me from its session's turn ending. The team tab alone waits while
its assistant works: what its missions need of me waits on me, not on it. Nor
does any page of a session another fully drives: its driver answers it,
so it wears no dot and never opens itself. A partial drive answers only
its topic, and its pages wait as any other's.
While home shows Skills, a
new wait opens its hub by itself, on its own tab; of several, a handover
first, then the rail's order. Anywhere else, only the rail moves.

An assistant page's Launch page opens that assistant's launch page under
its own tab, on the right. While my assistant drives, whatever it drives,
a session, a stage or the whole plan, the launch page it scheduled for
the next stage has no tab until I press that Launch page. It hides again
once I pick any other tab, hub or page.

A team is an assistant and its sessions, read from disk, never guessed. An
assistant on a zero seat with a plan leads its ten: 10 leads 11 to 19. A
session running a plan's mission sits under that plan. Every other session
stands alone. Who launched a session makes no team.

Every team opens as one hub, and so does every session standing alone. A
team's Team icon opens its hub on its team tab: its assistant's page, at
its current stage, the one running, else the next not started. Each press
of the icon or the Team tab brings it back there. The whole plan, a stage and a mission all show inside it. Nothing
else is ever a team tab, so a session standing alone has none. The code
calls the team tab the hub's overview. A hub's tabs follow, session by
session, its head first, then each member, lowest number first, as the
rail runs, on my Mac and my phone alike. Each session's run by kind:
those that can wait on me first, then those I read: its clarify, jury,
handover, launch and prototype, then its transcript, transcript-page.py's,
its walk and its screenshots: page.TAB_KINDS.
A number on the rail opens its
hub on its own session's first tab waiting on me, of any kind: a fully
driven session has none. Otherwise its Clarify, while it holds a wave
not sent, its session working or driven. Otherwise a number opens its own session's last tab
on show, while it stands, never another session's, though a team's
sessions share one hub. With none, it opens its transcript. A head's
number opens its own tabs as a member's does, never the team tab: only
the Team icon opens that. On a wide screen, the
team tab keeps the left, and the tab opens on the right. A tab whose page goes, as a wave once sent, hands its
place to its own session's next tab, never another session's. A session
joining a team takes me along into the team's hub. While I stay, a
handover beginning to wait on me opens itself, on every screen.

Every chip leading a session's tabs names it: its tag, then its name, as
02 sign-in-fix, once per strip, and its tabs wear no number of their
own. A number I point at on the rail names its session at once, on a
bubble beside it, with what waits on me there. The Team icon names its
team the same way.

A hub holding two sessions or more groups its tabs by session, as Chrome
groups its own: the session's chip once, then its tabs, each its icon and
word. A chip of a session another drives wears the wheel after its tag,
lib/successor.py's driver named on a hover, with a partial drive's topic. A tap on the chip folds them into it, and the chip then wears their
icons, and a red dot while one waits on me. Every group starts unfolded,
and a tab opening unfolds its group. Each device keeps what I folded. The
group holding the tab on show wears the white line under its chip too,
folded or not, so I always see whose tab I am on.

The rail is one column. Skills, white, is pinned on top, and opens the
Skills page. Then System, Agenda, Launch, which opens my own launch page,
Prototypes, which opens 1400's library, and Files, then the hubs,
team by team, a thin line
before each. A session standing alone is its own number. A team is one grey band, edge
to edge: its Team icon, the team tab's icon on a dark square, then its
head's number, then each member's, lowest first, its number over its
mission. A hub with a team tab is a team, before any member joins. Each
number's square wears its session's colour, at one size, page rule 41's.
Its number sits on the left; what it wears stacks in a black column on
its right, inside the square: a white dot while a page of its own waits
on me; the wheel and its driver's number while another session drives
it, under the dot only while a partial drive leaves a page waiting on me;
then its role's icon, the lead's Walk, the walker's Screenshots or the
advisor's Advise. The Team icon wears the
dot on its corner while the team tab waits on me, and its head's number
never does for it. The outline sits on the session
on show: the one whose tab shows on the right, or the Team icon while its
team tab shows alone. A number opens its hub, a session standing alone as a
team's right side does. Zoom in and zoom out sit right under Files.
What runs out of room scrolls under Skills, with a fade and an arrow at
each edge more numbers sit past, the arrow wearing a red dot while one
hidden that way waits on me. My Mac and my phone draw it alike, the
phone's at a fingertip's size.

On my phone's home screen, a bell sits pinned at the rail's foot, under a
thin line, until I allow the buzz. One tap asks, and once allowed it hides: lib/push.py tells my
phone each time a session is done. A tap on a buzz opens that session's
transcript, in its hub.

1100 zooms whole, by Cmd+ and Cmd-. Inside it, two zooms move apart, one
step a press, each kept on each device. The rail's two zoom buttons zoom
the page: the strip and every page home frames, on my Mac and my phone
alike. The rail has its own, set by Rail size on System, so it grows
while the page stays as it is. A press leaves the cursor where it was,
and each page holds what I was reading. A pinch zooms nothing, bar a
chart's own window. A page under a tab drops its head's family and
session, since the tab names both.

Below 1100 pixels, and on my phone held upright, a hub shows one pane at a
time, its team tab the first. My phone held sideways is wide.

My phone, and never a Mac however narrow its pane, draws the home on the
whole glass, every control 44 by 44. There, a tab half under the strip's
arrow opens at my tap, and a swipe scrolls the strip.

Wide, on my Mac or my phone held sideways, a small glyph at the tabs'
right end turns a hub with a team tab to one side, one pane at a time,
and back. Each device keeps my pick, for every hub.

Nothing is stored here. /model reads the registry, Claude Code's records,
and each session's files, the way 1100's views read them. Home asks it
again each time a file it hears moves, and reloads itself once 1100
restarts on new code. Of the pages it keeps, only those on show are
watched; one hidden is told what moved once it shows again.

The dashboard's server serves it. Imported, never run.
"""

import json
import os
import sys
import traceback
import urllib.parse

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import context  # noqa: E402
import drive  # noqa: E402
import launch  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import plans  # noqa: E402
import ports  # noqa: E402
import project  # noqa: E402
import push  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import successor  # noqa: E402

views = page.tool("dashboard-views")
clarify, assistant, launcher, jury = views.clarify, views.assistant, views.launcher, views.jury


# ---- the model ---------------------------------------------------------------

def teams_of(held: dict, owned: dict) -> list:
    """Every team, as (head, members), lowest head first.

    An assistant leading a ten always heads it. Any other session sits in
    its assistant's ten first, then under the plan whose mission it is. A
    head sitting under another joins that one's team. Its launcher counts
    for nothing.
    """
    tens = launch.teams(held)
    over = {nn: f"{nn[0]}0" for nn in held if nn[1] != "0" and nn[0] in tens and f"{nn[0]}0" in held}
    lead_ten = lambda nn: nn[1] == "0" and nn[0] in tens
    for nn, (lead, _) in owned.items():
        if nn not in over and not lead_ten(nn) and lead in held:
            over[nn] = lead

    def root(nn: str) -> str:
        seen = [nn]
        while nn in over and over[nn] not in seen:
            nn = over[nn]
            seen.append(nn)
        # Sessions each under another make a ring, and its lowest heads it,
        # so none of them leaves the rail.
        if nn in over:
            return min(seen[seen.index(over[nn]):], key=int)
        return nn

    heads = sorted((nn for nn in held if root(nn) == nn), key=int)
    return [(h, sorted(n for n in held if n != h and root(n) == h)) for h in heads]


def born(path: str) -> int:
    try:
        return int(os.stat(path).st_birthtime)
    except OSError:
        return 0


def since_prototype(nn: str, subject: str) -> int:
    """When a prototype began waiting: its newest generation's birth, else
    the hold's."""
    gens = views.prototypes.generations(os.path.join(views.APP, subject))
    return born(gens[-1][1]) if gens else born(views.prototypes.subject_file(nn))


# Each failure already in 1100's log, so one failing on every draw is
# logged once.
FAILED: set = set()


def failed(what: str) -> None:
    """The error being handled, into 1100's log, once per what and its kind."""
    if (what, sys.exc_info()[0]) not in FAILED:
        FAILED.add((what, sys.exc_info()[0]))
        traceback.print_exc()


def model() -> dict:
    """Everything home draws, as one answer. Every team and every session
    standing alone gets its hub, every session its transcript, and every
    assistant its page; every other page exists only while it waits on me.
    It carries no clock of its own, so it only changes when something did."""
    held, live, open_ids = registry.entries(), registry.claude_records(), panes.ids(panes.FRESH)
    owned = plans.owners(held)
    drivers, topics = successor.driven_all(held), successor.topics(held)
    limit = context.threshold()
    sessions, pages, own = {}, {}, {}
    app_up = None
    for nn, mine in sorted(held.items()):
        name = mine.get("title", nn)
        try:
            name, _, colour, look, _ = page.shown(nn, mine, live.get(mine.get("session_id")), open_ids)
            sessions[nn] = {"name": name, "colour": colour, "dashed": bool(look), "tag": plans.tag(nn, owned),
                            "by": drivers.get(nn, ""), "topic": topics.get(nn, "")}
            own[nn] = []

            def add(kind: str, label: str, since: int, path: str, port: int = 0, up: bool = True,
                    waits: bool = True) -> None:
                key = f"{kind}:{nn}"
                own[nn].append(key)
                pages[key] = {"kind": kind, "nn": nn, "label": label, "waits": waits, "since": since,
                              "port": port, "path": path, "up": up}

            # Its role, the badge its square wears: the advisor; a walk's lead,
            # which holds the walk's list; or a walker, which holds walk.json.
            if views.advisor.seated((live.get(mine.get("session_id")) or {}).get("name") or mine.get("title", "")):
                sessions[nn]["role"] = "advisor"
            wave, path, head, items = clarify.newest(nn)
            if wave and not head.get("sent"):
                add("clarify", f"Wave {wave} · {sum(1 for it in items if clarify.answered(it))} of {len(items)}",
                    born(path), serve.address("clarify", nn))
            if got := jury.tab(nn):
                label, began, waits = got
                add("jury", label, born(began), serve.address("jury", nn), waits=waits)
            if got := views.walk_list.tab(nn):
                sessions[nn].setdefault("role", "lead")
                add("walk", got[0], born(got[1]), serve.address("walk", nn), waits=False)
            elif os.path.isfile(os.path.join(registry.folder(nn), "walk.json")):
                sessions[nn].setdefault("role", "walker")
            if got := views.shots.tab(nn):
                add("shots", got[0], born(got[1]), serve.address("shots", nn), waits=False)
            if launcher.read(nn):
                add("launch", views.launch_line(nn), born(launcher.path(nn)), serve.address("launch", nn),
                    waits=not launcher.scheduled(nn))
            if subject := views.prototypes.on_hub(nn, live.get(mine.get("session_id"))):
                if app_up is None:
                    app_up = ports.answering(views.prototypes.PORT)
                add("prototype", views.proto_line(subject), since_prototype(nn, subject),
                    "/?" + urllib.parse.urlencode({"subject": subject, "session": nn}),
                    views.prototypes.PORT, app_up)
            if got := views.handover.waiting(nn, mine, live, limit):
                label, since = got
                add("handover", label, since, serve.address("handover", nn),
                    waits=label not in views.handover.PRESSED.values())
        except Exception:
            # A session whose files fail to read draws grey, with its
            # transcript alone, and every other session draws on: one bad
            # file never freezes home. Each failure is logged once.
            failed(f"session {nn}")
            for k in [k for k, p in pages.items() if p["nn"] == nn]:
                del pages[k]
            sessions[nn] = {"name": name, "colour": "grey", "dashed": True, "tag": nn, "by": "", "topic": ""}
            own[nn] = []
        pages[f"transcript:{nn}"] = {"kind": "transcript", "nn": nn, "label": name, "waits": False,
                                     "since": 0, "port": 0, "path": serve.address("transcript", nn), "up": True}

    def first(keys: list) -> list:
        return sorted(keys, key=lambda k: pages[k]["since"])

    order = list(page.TAB_KINDS)

    def ranked(keys: list) -> list:
        """One session's tabs, in page.TAB_KINDS' order. A kind it lacks goes last."""
        kind = lambda k: pages[k]["kind"]
        return sorted(keys, key=lambda k: order.index(kind(k)) if kind(k) in order else len(order))

    hubs = {}
    for h, members in teams_of(held, owned):
        # The head first, then each member, lowest number first, as the rail.
        team = [h] + members
        waiting = [k for nn in team for k in first(own[nn])]
        assisting = bool(plans.plan(h).get("stages"))
        if assisting:
            # A plan that fails to read still opens its team tab: the page
            # draws the error, and every other hub draws on.
            overview, owed, line = f"assistant:{h}", [], "Plan"
            try:
                at = views.stage_at(h, held, live)
                owed, line = assistant.due(h, held, live, open_ids), views.plan_line(h, at)
            except Exception:
                failed(f"plan {h}")
            pages[overview] = {"kind": "assistant", "nn": h, "label": line, "waits": bool(owed),
                               "since": min((t for _, _, t in owed), default=0), "port": 0,
                               "path": serve.address("assistant", h), "up": True, "hub": h}
            # The next stage's scheduled launch page has no tab, until I press
            # its Launch page. It is the one page home hides this way. Whatever
            # the drive holds, a session, a stage or the whole plan.
            mine, k = drive.read(h), f"launch:{h}"
            if k in pages and drive.driving(mine) and launcher.scheduled(h):
                pages[k]["hidden"] = True
        else:
            # Only a team's plan is an overview. A session standing alone
            # keeps each of its pages under its own tab.
            overview = ""
        # A hub is its head's number, so a first member joining keeps it.
        # Its tabs go session by session, each one's by kind, and home draws
        # them in this order.
        hub = h
        tabs = [k for nn in team for k in ranked(own[nn] + [f"transcript:{nn}"]) if k != overview]
        hubs[hub] = {"overview": overview, "tabs": tabs, "nn": h, "members": [n for n in team if n != h]}
        for k in waiting:
            pages[k]["hub"] = hub
    # Nothing waits on me while its session works, or once it is gone, bar
    # the team tab: words waiting for my send wait on me while the
    # assistant works. Nor while another session fully drives it: its
    # driver answers. A partial drive answers only its topic.
    for p in pages.values():
        s = sessions[p["nn"]]
        if (s["colour"] == "grey" or s["colour"] == "green" and p["kind"] != "assistant"
                or s["by"] and not s["topic"]):
            p["waits"] = False
    left = {hub["overview"] for hub in hubs.values()}
    for k in pages:
        pages[k]["side"] = "l" if k in left else "r"
    waits = first([k for k in pages if pages[k]["waits"]])
    # The rail's numbers, team by team.
    return {"sessions": sessions, "pages": pages, "hubs": hubs, "waits": waits, "rail": list(hubs),
            "pid": os.getpid()}


# ---- home ---------------------------------------------------------------------

# Home's icons: every tab kind's, by page.TAB_KINDS, then the team tab's,
# the advisor's badge and the rail's own.
ICONS = [*page.TAB_KINDS, "assistant", "advisor", "agenda", "system", "skills", "files", "zoom-in", "zoom-out",
         "left", "right"]

FOOT = ('<div class="foot"><div class="cut"></div>'
        '<button class="b0 rb" id="bell" onclick="nav.bell()" aria-label="Buzz me when a session is done" '
        'title="Buzz me when a session is done" hidden>' + page.icon("bell", 15) + '</button></div>')

# My phone draws the home on the whole glass, under the notch and the home
# bar. Opened from its home screen, the home runs alone, with no Safari
# around it, under a status bar it shows through, and is named for the
# project there, as an app of its own, which a buzz needs. A tap into a field,
# in home or any page it frames, never zooms the glass, whatever the
# field's text size or my zoom. A Mac ignores all six, and its tab keeps
# the page's title.
WIDTH = '<meta name="viewport" content="width=device-width, initial-scale=1">'
GLASS = ('<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, '
         'viewport-fit=cover">\n'
         '<meta name="apple-mobile-web-app-capable" content="yes">\n'
         '<meta name="mobile-web-app-capable" content="yes">\n'
         '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
         f'<meta name="apple-mobile-web-app-title" content="{page.esc(project.NAME)}">\n'
         '<link rel="manifest" href="/manifest.webmanifest">')


def home() -> str:
    """The workstation. It draws itself from /model, and reloads only when
    1100 restarts. Its watch starts from the key of the model drawn in, so
    a change landing while it loads is told at once."""
    drawn = json.dumps(model())
    shell = (HOME.replace("%MODEL%", drawn.replace("</", "<\\/"))
             .replace("%SEEN%", serve.hashed(drawn))
             .replace("%PUSH%", json.dumps(push.public()))
             .replace("%PROTOTYPES%", str(views.prototypes.PORT))
             .replace("%ZOOMS%", json.dumps(page.ZOOMS))
             .replace("%WORDS%", json.dumps({**{k: w for k, (w, _) in page.TAB_KINDS.items()}, "assistant": "Team"}))
             .replace("%ORDER%", json.dumps(list(page.TAB_KINDS)))
             .replace("%ICONS%", json.dumps({**{k: page.icon(k, 15) for k in ICONS},
                                             "two": page.icon("two", 14), "one": page.icon("one", 14),
                                             "wheel": page.icon("wheel", 11)})))
    edge = lambda d, glyph: (f'<button class="b0 rarr" id="r{d}" onclick="nav.rail({-1 if d == "up" else 1})" '
                             f'aria-label="More sessions" title="More sessions">{page.icon(glyph, 13)}</button>')
    rail = (f'<aside class="rail"><div class="pin" id="pin"></div>{edge("up", "left")}<div class="list" id="tools"></div>'
            f'{edge("dn", "right")}{FOOT}</aside>')
    body = ('<div class="region" id="region"><div class="strip" id="strip"><div class="tabs" id="tabs" '
            'role="tablist"></div><button class="arr al" id="al" aria-label="Scroll the tabs left" '
            f'title="More tabs">{page.icon("left", 15)}</button><button class="arr ar" id="ar" '
            f'aria-label="Scroll the tabs right" title="More tabs">{page.icon("right", 15)}</button>'
            '<button class="b0 sides" id="sides" onclick="nav.sides()" hidden></button></div>'
            '<div class="pane l" id="L"></div><div class="pane r" id="R"></div><div class="tool" id="T"></div>'
            '<div class="empty" id="none"><p>Nothing waits on you.</p></div></div>' + page.ANYWHERE + shell)
    return page.render("00-home", [("", body)], rail, refresh=0, frame=False).replace(WIDTH, GLASS, 1)


HOME = r"""<style>
  body:has(> aside.rail) > main { padding:0; overflow:hidden; display:flex; flex-direction:column; }
  button { font:inherit; color:inherit; }
  .b0 { background:none; border:0; margin:0; padding:0; border-radius:4px; cursor:pointer; text-align:left; }
  .b0:focus-visible { outline:2px solid var(--blue); outline-offset:1px; }
  .count { display:inline-block; min-width:17px; height:17px; padding:0 4px; border-radius:9px;
    background:var(--red); color:var(--bg); font:700 10px/17px ui-monospace,Menlo,monospace; text-align:center; }
  .count.g { background:var(--grey); color:var(--text); }
  .dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--c, var(--grey)); }
  .nm { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

  /* The rail: one column, 44px, overriding the shell's 280. Skills stays
     pinned on top. System, Agenda, Launch, Prototypes, Files, zoom in and
     out, and every hub's number scroll under it once they run out of room. */
  aside.rail { width:44px; padding:6px 0; display:flex; flex-direction:column; align-items:center; overflow:hidden; }
  .pin { flex:none; display:flex; justify-content:center; width:100%; padding-bottom:6px; }
  .list { flex:1; min-height:0; width:100%; overflow-y:auto; display:flex; flex-direction:column; align-items:center;
    gap:6px; padding:2px 0 8px; }
  /* A thin line before each team. */
  .cut { flex:none; width:20px; height:1px; margin:2px 0; background:var(--line); }
  /* Numbers past the rail's edge: a fade and an arrow there, as the strip
     wears them, the arrow a red dot while a session hidden that way waits
     on me. */
  .list.ft { -webkit-mask-image:linear-gradient(to bottom, transparent 0, #000 24px);
    mask-image:linear-gradient(to bottom, transparent 0, #000 24px); }
  .list.fb { -webkit-mask-image:linear-gradient(to top, transparent 0, #000 24px);
    mask-image:linear-gradient(to top, transparent 0, #000 24px); }
  .list.ft.fb { -webkit-mask-image:linear-gradient(to bottom, transparent 0, #000 24px, #000 calc(100% - 24px), transparent 100%);
    mask-image:linear-gradient(to bottom, transparent 0, #000 24px, #000 calc(100% - 24px), transparent 100%); }
  .rarr { flex:none; position:relative; display:none; align-items:center; justify-content:center; width:32px; height:18px;
    color:var(--dim); }
  .rarr.on { display:inline-flex; }
  .rarr:hover { color:var(--text); background:var(--hover); }
  .rarr svg { transform:rotate(90deg); }
  .rarr.waits::after { content:""; position:absolute; top:1px; right:3px; width:8px; height:8px; border-radius:50%;
    background:var(--red); }
  /* The foot: the bell, pinned under a thin line, both gone once it hides. */
  .foot { flex:none; display:flex; flex-direction:column; align-items:center; gap:6px; width:100%; }
  .foot:has(> #bell[hidden]) > .cut { display:none; }
  .rb:disabled { opacity:.4; cursor:default; }
  .rb[hidden] { display:none; }
  /* Zoomed: the rail by its own zoom; the strip and the lines home writes
     by the page's. Each framed page zooms itself, so nothing zooms twice. */
  aside.rail { zoom:var(--rail, 1); }
  .strip, .empty, .down { zoom:var(--zoom, 1); }
  .rb { flex:none; position:relative; display:inline-flex; align-items:center; justify-content:center; width:32px;
    height:32px; color:var(--dim); border:1px solid transparent; text-align:center; }
  .rb:hover { color:var(--text); background:var(--hover); }
  .rb.on { color:var(--text); background:var(--raised); border-color:var(--grey); }
  /* Skills, pinned on top: white. */
  .rb.go, .rb.go:hover { color:#000; background:#fff; border-color:#fff; }
  .rb.go.on { outline:2px solid var(--blue); outline-offset:2px; }
  /* A hub: its number, in its session's colour, on the left, a member's
     mission under it. What it wears stacks in a black column on its right,
     inside the square: the white dot while a page waits on me, the wheel
     and its driver's number while another session drives it, then its role.
     The square never grows, and its colour never changes. Gone is outlined. */
  .rb.num, .rb.num:hover { overflow:hidden; color:var(--bg); background:var(--c); border:0; line-height:1; }
  .rb.num:hover { filter:brightness(1.12); }
  .rb.num.gone { color:var(--dim); background:none; border:1px solid var(--grey); }
  .rb.num.on { outline:2px solid var(--text); outline-offset:2px; }
  .rb.num .nm { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
    justify-content:center; gap:2px; font-size:13px; font-weight:800; letter-spacing:-.6px; }
  .rb.num.has .nm { right:12px; }
  .rb.num .m { font-size:9px; font-weight:700; letter-spacing:-.3px; }
  .rb.num .bs { position:absolute; top:0; right:0; bottom:0; width:12px; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:2px; background:var(--bg); color:#fff; }
  .rb.num .bs i { display:inline-flex; align-items:center; justify-content:center; font-style:normal; }
  .rb.num .bs svg { width:9px; height:9px; stroke-width:2.6; }
  .rb.num .wt::before { content:""; width:7px; height:7px; border-radius:50%; background:#fff; }
  .rb.num .dv { margin-bottom:-1px; }
  .rb.num .dd { font-size:8px; font-weight:800; letter-spacing:-.6px; }
  /* A team: one grey band, edge to edge, behind its Team icon, its head's
     number and each member's. */
  .team { flex:none; width:100%; display:flex; flex-direction:column; align-items:center; gap:6px; padding:4px 0;
    background:var(--grey); }
  /* The Team icon: the team tab's icon on a dark square. */
  .rb.tm, .rb.tm:hover { color:var(--text); background:var(--bg); border-color:var(--bg); }
  .rb.tm:hover { background:var(--panel); }
  .rb.tm.on { outline:2px solid var(--text); outline-offset:2px; }
  /* The team tab waits on me: a white dot on the Team icon's corner, ringed
     in the band's grey. */
  .rb.tm .wt { position:absolute; top:-4px; right:-4px; width:10px; height:10px; border-radius:50%; background:#fff;
    box-shadow:0 0 0 2px var(--grey); }
  /* On the band, gone keeps the rail's dark inside its outline. */
  .team .rb.num.gone { background:var(--panel); }

  /* Main: the strip over the right pane, the overview left. */
  .region { position:relative; flex:1; min-width:0; min-height:0; display:grid;
    grid-template-columns:minmax(0,1fr) minmax(0,1fr); grid-template-rows:auto minmax(0,1fr);
    grid-template-areas:"l tabs" "l r"; }
  /* A hub with no overview: its strip over its one pane. */
  .region[data-mode="one"] { grid-template-columns:minmax(0,1fr); grid-template-areas:"tabs" "r"; }
  .region[data-mode="one"] > .l { display:none; }
  .region[data-mode="tool"], .region[data-mode="none"] { grid-template-columns:minmax(0,1fr);
    grid-template-rows:minmax(0,1fr); grid-template-areas:"t"; }
  .region[data-mode="tool"] > :not(.tool), .region[data-mode="none"] > :not(.empty) { display:none; }
  .region:not([data-mode="tool"]) .tool, .region:not([data-mode="none"]) .empty { display:none; }
  .strip { grid-area:tabs; position:relative; min-width:0; background:var(--panel); border-bottom:1px solid var(--line); }
  .l { grid-area:l; border-right:1px solid var(--line); }
  .r { grid-area:r; }
  .tool, .empty { grid-area:t; }
  .pane, .tool { min-width:0; min-height:0; display:flex; flex-direction:column; }
  .pane > *, .tool > * { flex:1; min-width:0; min-height:0; border:0; width:100%; display:none; }
  .pane > .on, .tool > .on { display:block; }
  /* A frame paints dark before its page arrives: never a white flash. */
  .pane > iframe, .tool > iframe { background:var(--bg); }
  .down { padding:24px; color:var(--dim); }
  /* The strip: one row that scrolls sideways, an arrow and a fade at each end that hides more. */
  .tabs { position:relative; display:flex; flex-wrap:nowrap; min-width:0; min-height:40px; overflow-x:auto;
    overflow-y:hidden; overscroll-behavior-x:contain; }
  .tabs.fl { -webkit-mask-image:linear-gradient(to right, transparent 0, transparent 20px, #000 52px);
    mask-image:linear-gradient(to right, transparent 0, transparent 20px, #000 52px); }
  .tabs.fr { -webkit-mask-image:linear-gradient(to left, transparent 0, transparent 20px, #000 52px);
    mask-image:linear-gradient(to left, transparent 0, transparent 20px, #000 52px); }
  .tabs.fl.fr { -webkit-mask-image:linear-gradient(to right, transparent 0, transparent 20px, #000 52px, #000 calc(100% - 52px), transparent calc(100% - 20px), transparent 100%);
    mask-image:linear-gradient(to right, transparent 0, transparent 20px, #000 52px, #000 calc(100% - 52px), transparent calc(100% - 20px), transparent 100%); }
  .arr { position:absolute; top:0; bottom:0; z-index:2; width:24px; display:none; align-items:center;
    justify-content:center; color:var(--dim); background:none; border:0; cursor:pointer; }
  .arr:hover { color:var(--text); background:var(--hover); }
  .arr.on { display:inline-flex; }
  .al { left:0; }
  .ar { right:0; }
  .wtab { flex:none; display:inline-flex; align-items:center; gap:6px; min-height:39px; padding:0 12px;
    border-radius:0; color:var(--dim); border-right:1px solid var(--line); box-shadow:inset 0 -2px 0 transparent;
    white-space:nowrap; }
  .wtab:hover { color:var(--text); background:var(--hover); }
  .wtab.on { color:var(--text); box-shadow:inset 0 -2px 0 var(--text); }
  .wtab b { font-size:12px; }
  .wtab.ov { display:none; }
  /* A team's group: its session's chip, then its tabs, a line under them in
     the chip's colour. Folded, the chip wears its tabs' icons. */
  .grp { flex:none; display:flex; }
  .ghead { flex:none; display:inline-flex; align-items:center; justify-content:center; gap:5px; min-height:39px;
    padding:0 8px; border-radius:0; border-right:1px solid var(--line); }
  .ghead:hover { background:var(--hover); }
  /* One session's strip: its chip, with its name, leads its tabs once. */
  .ghead.lead { cursor:default; }
  .ghead.lead:hover { background:none; }
  /* A number pointed at: its session's tag and name, then what waits on
     me, on a bubble beside it, its arrow pointing at the number. */
  .nb { position:fixed; z-index:30; display:flex; flex-direction:column; gap:2px; max-width:360px; padding:5px 9px;
    color:var(--text); font-size:12px; background:var(--raised); border:1px solid var(--grey); border-radius:6px;
    box-shadow:0 4px 14px rgba(0,0,0,.45); pointer-events:none; transform:translateY(-50%); }
  .nb::before { content:""; position:absolute; left:-6px; top:50%; transform:translateY(-50%);
    border:6px solid transparent; border-left:0; border-right-color:var(--grey); }
  .nb[hidden] { display:none; }
  .nb .w { color:var(--dim); font-size:11px; }
  .ghead .chip { display:inline-flex; align-items:center; gap:4px; padding:1px 6px; }
  .ghead .chip svg { width:11px; height:11px; }
  /* A driven session's chip: the wheel after its tag. */
  .chip.dr { display:inline-flex; align-items:center; justify-content:center; gap:4px; }
  .chip.dr svg { width:11px; height:11px; stroke-width:2.6; }
  .grp.open .wtab { box-shadow:inset 0 -2px 0 var(--c); }
  .grp.open .wtab.on { box-shadow:inset 0 -2px 0 var(--text); }
  .grp.here .ghead { box-shadow:inset 0 -2px 0 var(--text); }
  .empty p { font-size:clamp(20px, 4vw, 34px); }
  /* Wide, one side or two: a small glyph at the tabs' right end. */
  .strip { display:flex; }
  .strip > .tabs { flex:1; }
  .sides { flex:none; display:inline-flex; align-items:center; justify-content:center; width:40px;
    border-radius:0; color:var(--dim); border-left:1px solid var(--line); }
  .sides:hover { color:var(--text); background:var(--hover); }
  .sides[hidden] { display:none; }
  .strip:has(> .sides:not([hidden])) .ar { right:40px; }
  /* One side: one pane at a time, as half a screen shows it. */
  .region[data-sides="1"], .region[data-sides="1"][data-mode="one"] { grid-template-columns:minmax(0,1fr);
    grid-template-areas:"tabs" "p"; }
  .region[data-sides="1"] > .l, .region[data-sides="1"] > .r { grid-area:p; border-right:0; }
  .region[data-sides="1"][data-pane="overview"] > .r, .region[data-sides="1"][data-pane="right"] > .l {
    display:none; }
  .region[data-sides="1"] .wtab.ov { display:inline-flex; }

  /* Half a screen, or my phone held upright: the same rail, one pane at a
     time. My phone held sideways is wide, whatever its width. */
  @media (max-width: 1100px) and (hover: hover), (hover: none) and (pointer: coarse) and (orientation: portrait) {
    .region, .region[data-mode="one"] { grid-template-columns:minmax(0,1fr); grid-template-areas:"tabs" "p"; }
    .region > .l, .region > .r { grid-area:p; border-right:0; }
    .region[data-pane="overview"] > .r, .region[data-pane="right"] > .l { display:none; }
    .wtab.ov { display:inline-flex; }
  }

  /* My phone, and never a Mac, however narrow its pane. The home fills the
     glass: the rail's panel runs under the notch, and only the notch's side
     is kept clear. Held sideways, iOS insets both sides alike, so the side
     comes from how the phone is turned; unknown, both stay clear. Upright,
     the status bar's band stays clear. Every control takes a fingertip: 44
     by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    html { overflow:hidden; overscroll-behavior:none; -webkit-text-size-adjust:100%; text-size-adjust:100%;
      -webkit-tap-highlight-color:transparent;
      --il:env(safe-area-inset-left, 0px); --ir:env(safe-area-inset-right, 0px); }
    html.nl { --ir:0px; }
    html.nr { --il:0px; }
    body { padding-top:env(safe-area-inset-top, 0px); }
    .b0 { touch-action:manipulation; }
    /* The rail and the strip zoom, but the glass's insets never do. */
    aside.rail { width:calc(56px + var(--il) / var(--rail, 1)); padding:8px 0 0 calc(var(--il) / var(--rail, 1)); }
    .pin { padding-bottom:4px; }
    .list { gap:4px; padding-bottom:8px; }
    .foot { gap:4px; padding-bottom:calc(8px + env(safe-area-inset-bottom, 0px) / var(--rail, 1)); }
    .cut { width:30px; margin:4px 0; background:var(--grey); }
    .rb { width:44px; height:44px; border-radius:6px; }
    .rb svg.i { width:20px; height:20px; }
    .team { gap:4px; }
    /* The phone's 44px square: look 1's every size, times 44 over 32. */
    .rb.num .nm { gap:3px; font-size:18px; }
    .rb.num.has .nm { right:16px; }
    .rb.num .m { font-size:12px; }
    .rb.num .bs { width:16px; gap:3px; }
    .rb.num .bs svg { width:12px; height:12px; }
    .rb.num .wt::before { width:10px; height:10px; }
    .rb.num .dd { font-size:11px; }
    .rb.tm .wt { width:12px; height:12px; }
    body:has(> aside.rail) > main { padding-right:var(--ir); }
    /* The strip's panel runs under the notch too. */
    .strip { margin-right:calc(-1 * var(--ir) / var(--zoom, 1)); padding-right:calc(var(--ir) / var(--zoom, 1)); }
    .ar { right:calc(var(--ir) / var(--zoom, 1)); }
    .tabs { min-height:44px; }
    .wtab { min-height:44px; padding:0 14px; }
    .ghead { min-height:44px; min-width:44px; }
    /* The strip's arrows only show that more sits there: a tap reaches the
       tab under one, and a swipe scrolls. */
    .arr { width:44px; pointer-events:none; }
    .sides { width:44px; }
    .strip:has(> .sides:not([hidden])) .ar { right:calc(44px + var(--ir) / var(--zoom, 1)); }
  }
  /* iOS blurs below its status bar in a home-screen app. Keep controls
     below that edge while upright, regardless of the page's zoom. */
  @media (hover:none) and (pointer:coarse) and (orientation:portrait) {
    html.ios-app body { padding-top:calc(env(safe-area-inset-top, 0px) + 24px); }
  }
</style>
<script id="model" type="application/json">%MODEL%</script>
<script>
const ICONS = %ICONS%;
let M = JSON.parse(document.getElementById('model').textContent);
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
// Each tab's word, and the order a session's tabs run in: page.TAB_KINDS.
const WORD = %WORDS%, ORDER = %ORDER%;
// Half a screen, or my phone held upright: one pane at a time.
const NARROW = '(max-width: 1100px) and (hover: hover), (hover: none) and (pointer: coarse) and (orientation: portrait)';
// Wide, my Mac or my phone held sideways shows one side or two: my pick,
// kept on each device, for every hub.
const wide = () => !matchMedia(NARROW).matches;
let sides = localStorage.getItem('home-sides') === '1' ? 1 : 2;
const oneAtATime = () => !wide() || sides === 1;
const ago = t => { const d = Math.max(0, Math.floor(Date.now() / 1000 - t));
  return d < 60 ? d + 's' : d < 3600 ? Math.floor(d / 60) + 'm' : Math.floor(d / 3600) + 'h'; };
// The rail's pages, each in main. Launch opens my own launch page,
// Prototypes the library on the prototypes app's own port.
const TOOLS = ['skills', 'system', 'agenda', 'launch', 'prototypes', 'files'], LAUNCH = '/p/launch/00';
const PROTOTYPES = `${location.protocol}//${location.hostname}:%PROTOTYPES%/`;
let view = {kind: 'skills'}, back = {kind: 'skills'};
// lastOf is each session's own last tab on show, so its number brings it
// back: never another session's, though a team's sessions share one hub.
const picks = {}, frames = {}, lastRight = {}, lastOf = {};
// The groups I folded, kept on each device: a hub, then a session's tag, as
// 10:11-B1. A tag names its mission, so the next mission's starts unfolded.
const folded = new Set(JSON.parse(localStorage.getItem('home-folded') || '[]'));
function fold(key, shut) {
  if (shut) folded.add(key); else folded.delete(key);
  const live = new Set(Object.entries(M.hubs).flatMap(([id, h]) => h.tabs.map(k => id + ':' + M.sessions[M.pages[k].nn].tag)));
  for (const k of folded) if (!live.has(k)) folded.delete(k);
  localStorage.setItem('home-folded', JSON.stringify([...folded]));
}

// ---- what is on show --------------------------------------------------------

const hubOn = () => view.kind === 'hub' ? view.id : '';
// A hub's tabs, in the model's order: its head's, then each member's, each
// session's by kind, on my Mac and my phone alike.
const tabsOf = hub => hub.tabs;
// A hidden page has no tab while I am elsewhere: it shows only as my pick,
// and any other pick, hub or page drops it.
const hidden = k => !!(M.pages[k] || {}).hidden;
const drop = id => { if (M.hubs[id] && hidden(pickOf(id).right)) keep(id, {...pickOf(id), right: firstTab(M.hubs[id])}); };
// A hub's right side opens on its leftmost tab.
const firstTab = hub => tabsOf(hub).find(k => !hidden(k)) || '';
// One session's own tabs in a hub, hidden ones aside.
const ownTabs = (hub, nn) => tabsOf(hub).filter(k => M.pages[k].nn === nn && !hidden(k));
// A session's first tab waiting on me, of any kind. A fully driven one has none.
const waiting = (hub, nn) => ownTabs(hub, nn).find(k => M.pages[k].waits) || '';
// A session's Clarify: it shows only while it holds a wave not sent.
const unsent = (hub, nn) => ownTabs(hub, nn).find(k => M.pages[k].kind === 'clarify') || '';
// A click on a session opens its first tab waiting on me; else its
// Clarify, working or driven; else its own last tab on show, while it
// stands; else its transcript.
const entry = (hub, nn) => {
  const last = lastOf[nn] && lastOf[nn].right;
  return waiting(hub, nn) || unsent(hub, nn)
    || (ownTabs(hub, nn).includes(last) && last) || 'transcript:' + nn;
};
// The tab on show on a hub's right: my pick while its page stands. Once the
// page is gone, as a wave once sent, its own session's next tab takes its
// place, never another session's.
function rightOf(id) {
  const hub = M.hubs[id], p = pickOf(id);
  if (hub.tabs.includes(p.right)) return p.right;
  const [kind, nn] = String(p.right || '').split(':'), mine = nn ? ownTabs(hub, nn) : [];
  return mine.find(k => ORDER.indexOf(M.pages[k].kind) > ORDER.indexOf(kind)) || mine[mine.length - 1] || firstTab(hub);
}
// The handovers waiting on me in a hub.
const handovers = id => M.hubs[id]
  ? tabsOf(M.hubs[id]).filter(k => M.pages[k].waits && M.pages[k].kind === 'handover') : [];
// My pick in a hub holds, unless a handover began waiting since I made it:
// it then shows on the right, on every screen.
const pickOf = id => {
  const p = picks[id], fresh = p && handovers(id).find(k => !p.seen.includes(k));
  return fresh ? {...p, right: fresh, pane: 'right'} : p || {right: firstTab(M.hubs[id]), pane: 'overview'};
};
// A pick keeps the handovers it saw, and is its session's last tab on show.
// The team tab is no session's: only the Team icon opens it.
const keep = (id, p) => {
  picks[id] = {...p, seen: handovers(id)};
  const nn = p.right && M.pages[p.right] && M.pages[p.right].nn;
  if (nn && !(p.pane === 'overview' && M.hubs[id] && M.hubs[id].overview)) lastOf[nn] = {right: p.right, pane: 'right'};
};

// Where I am rides in the address, so a reload lands back there: #agenda,
// #skills, #system, #files, #launch, #prototypes, or a hub's number, then the tab I picked, as
// #90/clarify:95. A hub with no team tab never reads overview.
function mark() {
  const id = hubOn(), hub = id && M.hubs[id], p = hub && picks[id] && pickOf(id);
  const tab = p && (p.pane === 'overview' && hub.overview ? 'overview' : rightOf(id));
  const at = id ? id + (tab ? '/' + tab : '') : view.kind;
  if (location.hash !== '#' + at) history.replaceState(null, '', '#' + at);
}
function landed() {
  const [at, k] = decodeURIComponent(location.hash.slice(1)).split('/');
  if (TOOLS.includes(at)) return {kind: at};
  if (!at) return {kind: 'skills'};
  if (k) keep(at, k === 'overview' ? {right: '', pane: 'overview'} : {right: k, pane: 'right'});
  return {kind: 'hub', id: at};
}

// ---- small parts ----------------------------------------------------------------

// A session another drives wears the wheel after its tag.
// A chip leading a session's tabs wears its name too, once per strip.
function chip(nn, more = '', named = false) {
  const s = M.sessions[nn];
  return `<span class="chip${s.colour === 'grey' ? ' g' : ''}${s.dashed ? ' dashed' : ''}${s.by ? ' dr' : ''}" style="--c:var(--${s.colour})">${esc(s.tag)}${named ? ' ' + esc(s.name) : ''}${s.by ? ICONS.wheel : ''}${more}</span>`;
}
const onTopic = s => s.topic ? `, on ${s.topic}` : '';
const drivenBy = nn => M.sessions[nn].by ? ` · driven by ${M.sessions[nn].by}${onTopic(M.sessions[nn])}` : '';
const word = k => WORD[M.pages[k].kind];

// ---- the rail -------------------------------------------------------------------

// The session on show in a hub: the one whose tab shows on the right, or
// its head while its team tab shows alone.
function hereOf(id) {
  if (view.kind !== 'hub' || view.id !== id || !M.hubs[id]) return '';
  const hub = M.hubs[id], p = pickOf(id), right = rightOf(id);
  return (hub.overview && p.pane === 'overview' && oneAtATime()) || !right ? hub.nn : M.pages[right].nn;
}
// The team tab shows alone in a hub on show: the Team icon wears the
// outline, never its head.
const teamOn = id => view.kind === 'hub' && view.id === id && !!(M.hubs[id] || {}).overview
  && pickOf(id).pane === 'overview' && oneAtATime();

// What waits on me under one page, for a square's bubble.
const told = k => `\n${WORD[M.pages[k].kind]} · ${M.pages[k].label}, waiting ${ago(M.pages[k].since)}`;

// One hub on the rail. A session standing alone is its own number, in its
// colour. A team is one grey band: its Team icon, which opens the team
// tab, then its head's number, then each member's, its number over its
// mission, each in its own colour. A hub with a team tab is a team before
// any member joins. Every number opens its own session's tab, by entry().
// What a square wears stacks in its black column: a white dot while its
// page waits on me, and its bubble names each one; the wheel and its
// driver's number while another session drives it, the dot under them
// only while a partial drive leaves a page waiting on me; then its role's
// icon: the lead's Walk, the walker's Screenshots, the advisor's Advise.
// The outline sits on the session on
// show, or on the Team icon while the team tab shows alone.
const ROLE = {lead: 'walk', walker: 'shots', advisor: 'advisor'};
function number(id) {
  const hub = M.hubs[id], members = hub.members || [], here = hereOf(id), team = teamOn(id);
  const one = (nn, member) => {
    const s = M.sessions[nn], keys = hub.tabs.filter(k => M.pages[k].waits && M.pages[k].nn === nn);
    const what = (s.by ? `\nDriven by ${s.by}${onTopic(s)}` : '') + keys.map(told).join('');
    const mission = member && s.tag.startsWith(nn + '-') ? s.tag.slice(nn.length + 1) : '';
    const mark = (s.by ? `<i class="dv">${ICONS.wheel}</i><i class="dd">${esc(s.by)}</i>` : '')
      + (keys.length ? '<i class="wt"></i>' : '')
      + (s.role ? `<i class="rl">${ICONS[ROLE[s.role]]}</i>` : '');
    return `<button class="b0 rb num${s.colour === 'grey' ? ' gone' : ''}${mark ? ' has' : ''}${here === nn && !team ? ' on' : ''}" style="--c:var(--${s.colour})" onclick="nav.session('${nn}')" aria-label="${esc(s.tag)} ${esc(s.name)}${esc(what)}" data-nn="${esc(nn)}" data-what="${esc(what)}"><span class="nm"><span>${esc(nn)}</span>${mission ? `<span class="m">${esc(mission)}</span>` : ''}</span>${mark ? `<span class="bs">${mark}</span>` : ''}</button>`;
  };
  if (!hub.overview && !members.length) return one(id, false);
  const ov = hub.overview && M.pages[hub.overview], what = ov && ov.waits ? told(hub.overview) : '';
  const icon = ov ? `<button class="b0 rb tm${team ? ' on' : ''}" onclick="nav.team('${id}')" aria-label="Team · ${esc(M.sessions[id].tag)} ${esc(M.sessions[id].name)}${esc(what)}" data-nn="${esc(id)}" data-team="1" data-what="${esc(what)}">${ICONS.assistant}${what ? '<i class="wt"></i>' : ''}</button>` : '';
  return `<div class="team">${icon}${[id, ...members].map((nn, i) => one(nn, i > 0)).join('')}</div>`;
}

// A number I point at names its session at once, beside it: its tag and
// name, then what waits on me, on one bubble over the page. The Team icon
// names its team the same way. A pointer alone shows it; my phone's hub
// names its session in the strip instead.
const nb = Object.assign(document.createElement('div'), {className: 'nb', hidden: true});
document.body.appendChild(nb);
const SQUARE = '.rb.num, .rb.tm';
function pointAt(b) {
  const s = M.sessions[b.dataset.nn];
  if (!s || !matchMedia('(hover: hover)').matches) return;
  nb.innerHTML = `<span>${b.dataset.team ? '<b>Team</b> · ' : ''}<b>${esc(s.tag)}</b> ${esc(s.name)}</span>`
    + b.dataset.what.split('\n').filter(Boolean).map(w => `<span class="w">${esc(w)}</span>`).join('');
  const r = b.getBoundingClientRect();
  nb.style.left = r.right + 8 + 'px';
  nb.style.top = (r.top + r.bottom) / 2 + 'px';
  nb.hidden = false;
}
$('tools').addEventListener('mouseover', e => { const b = e.target.closest(SQUARE); if (b) pointAt(b); });
$('tools').addEventListener('mouseout', e => {
  const b = e.target.closest(SQUARE);
  if (b && !b.contains(e.relatedTarget)) nb.hidden = true;
});
$('tools').addEventListener('scroll', () => { nb.hidden = true; }, {passive: true});

// The page's zoom, one way, wearing the zoom it shows at.
function zoomTool(step) {
  const way = step > 0 ? 'in' : 'out', end = zoom === (step > 0 ? ZOOMS[ZOOMS.length - 1] : ZOOMS[0]);
  return `<button class="b0 rb" onclick="nav.zoom(${step})" onmousedown="event.preventDefault()" aria-label="Zoom the page ${way}" `
    + `title="Zoom the page ${way} · ${Math.round(zoom * 100)}% now"${end ? ' disabled' : ''}>${ICONS['zoom-' + way]}</button>`;
}

// System, Agenda, Launch, Prototypes and Files, then zoom in and out, then
// every hub, team by team.
function tools() {
  const on = k => view.kind === k ? ' on' : '';
  return `<button data-tool="system" class="b0 rb${on('system')}" title="System: the account order, band 00 and every other port" onclick="nav.tool('system')">${ICONS.system}</button>`
    + `<button data-tool="agenda" class="b0 rb${on('agenda')}" title="Agenda: what I want worked on, and what waits on what" onclick="nav.tool('agenda')">${ICONS.agenda}</button>`
    + `<button data-tool="launch" class="b0 rb${on('launch')}" title="Launch: a new session" onclick="nav.tool('launch')">${ICONS.launch}</button>`
    + `<button data-tool="prototypes" class="b0 rb${on('prototypes')}" title="Prototypes: every one locked in, and every one saved" onclick="nav.tool('prototypes')">${ICONS.prototype}</button>`
    + `<button data-tool="files" class="b0 rb${on('files')}" title="Files: every session's folder, lowest number first" onclick="nav.tool('files')">${ICONS.files}</button>`
    + zoomTool(1) + zoomTool(-1)
    + M.rail.map(id => '<div class="cut"></div>' + number(id)).join('');
}

// Skills stays pinned. The rest keeps where it was scrolled to.
function drawRail() {
  const list = $('tools'), focused = document.activeElement;
  const inList = list.contains(focused), inPin = $('pin').contains(focused);
  const before = [...list.querySelectorAll('button')], at = before.indexOf(focused);
  const nn = inList && focused.dataset.nn, team = inList && focused.dataset.team;
  const tool = inList && focused.dataset.tool;
  $('pin').innerHTML = `<button class="b0 rb go${view.kind === 'skills' ? ' on' : ''}" title="Skills: every skill, by family" onclick="nav.tool('skills')">${ICONS.skills}</button>`;
  const top = list.scrollTop;
  nb.hidden = true;
  list.innerHTML = tools();
  if (inPin) $('pin').querySelector('button')?.focus({preventScroll:true});
  if (inList) {
    const buttons = [...list.querySelectorAll('button')];
    const same = buttons.find(b => nn ? b.dataset.nn === nn && b.dataset.team === team : tool && b.dataset.tool === tool);
    (same || buttons[Math.min(at, buttons.length - 1)])?.focus({preventScroll:true});
  }
  list.scrollTop = top;
  edges();
}

// Numbers past the rail's edge, either way: its fade and its arrow show,
// and the arrow's red dot while a session hidden that way waits on me.
function edges() {
  const l = $('tools'), r = l.getBoundingClientRect();
  const up = l.scrollTop > 1, down = l.scrollTop + l.clientHeight < l.scrollHeight - 1;
  let waitsUp = false, waitsDown = false;
  l.querySelectorAll(SQUARE).forEach(b => {
    if (!b.querySelector('.wt')) return;
    const at = b.getBoundingClientRect();
    if (at.bottom <= r.top + 2) waitsUp = true;
    if (at.top >= r.bottom - 2) waitsDown = true;
  });
  l.classList.toggle('ft', up);
  l.classList.toggle('fb', down);
  $('rup').classList.toggle('on', up);
  $('rdn').classList.toggle('on', down);
  $('rup').classList.toggle('waits', waitsUp);
  $('rdn').classList.toggle('waits', waitsDown);
}
$('tools').addEventListener('scroll', edges, {passive: true});
addEventListener('resize', edges);

// ---- main -------------------------------------------------------------------------

function src(k) {
  const p = M.pages[k];
  return p.port ? `${location.protocol}//${location.hostname}:${p.port}${p.path || '/'}` : p.path;
}

// Each page is drawn once, in its side's pane, and kept, so what I typed
// in it survives a tab, a team, or a trip home.
function frame(k) {
  const p = M.pages[k], box = p.side === 'l' ? $('L') : $('R');
  let f = frames[k];
  if (f && (f.dataset.up === 'true') !== p.up) { f.remove(); f = null; }
  if (!f) {
    f = document.createElement(p.up ? 'iframe' : 'div');
    f.dataset.k = k;
    f.dataset.up = p.up;
    if (p.up) {
      f.src = src(k);
      f.title = `${WORD[p.kind]} · ${M.sessions[p.nn].tag}`;
      f.addEventListener('load', () => zoomed(f));
    } else {
      f.className = 'down';
      f.textContent = `${p.port} is not answering, so this ${WORD[p.kind].toLowerCase()} cannot show.`;
    }
    frames[k] = f;
  }
  if (f.parentNode !== box) box.appendChild(f);
  return f;
}

function tell(f, slim) {
  if (f.contentWindow) f.contentWindow.postMessage({ws: 1, slim}, '*');
}

// A team opened, by its number or its Team tab, brings its page back to its
// current stage: the one running, else the next not started. A page just
// made opens there anyway.
function home(id) {
  const f = M.hubs[id] && frames[M.hubs[id].overview];
  if (f && f.contentWindow) f.contentWindow.postMessage({ws: 1, go: 'home'}, '*');
}

const RED = '<span class="dot" style="--c:var(--red)"></span>';
// A tab inside a group drops its chip, since the group's names its session.
function tab(k, label, cls, on, grouped = false) {
  const p = M.pages[k];
  return `<button class="b0 wtab${cls}${on ? ' on' : ''}" role="tab" aria-selected="${on}" data-k="${k}" onclick="nav.pick('${k}')" title="${WORD[p.kind]} · ${esc(M.sessions[p.nn].tag)} · ${esc(p.label)}${p.waits ? ' · waits on you' : ''}${esc(drivenBy(p.nn))}">${p.waits ? RED : ''}${ICONS[p.kind]}${grouped ? '' : chip(p.nn)}<b>${label}</b></button>`;
}

// A hub holding two sessions or more groups its tabs by session, as Chrome
// groups its own: the session's chip once, then its tabs. A tap on the chip
// folds them into it; folded, it wears their icons, and a red dot while one
// waits on me. Every group starts unfolded. The group holding the tab on
// show wears the white line under its chip too.
function group(id, nn, ks, on) {
  const key = id + ':' + M.sessions[nn].tag, shut = folded.has(key), here = ks.some(on);
  const head = `<button class="b0 ghead" onclick="nav.fold('${esc(key)}')" title="${shut ? 'Unfold' : 'Fold'} ${esc(M.sessions[nn].tag)}'s tabs${esc(drivenBy(nn))}">`
    + `${shut && ks.some(k => M.pages[k].waits) ? RED : ''}${chip(nn, shut ? ks.map(k => ICONS[M.pages[k].kind]).join('') : '', true)}</button>`;
  return `<div class="grp${shut ? '' : ' open'}${here ? ' here' : ''}" style="--c:var(--${M.sessions[nn].colour})">${head}`
    + `${shut ? '' : ks.map(k => tab(k, word(k), '', on(k), true)).join('')}</div>`;
}

function drawMain() {
  mark();
  const region = $('region');
  document.querySelectorAll('.pane > *, .tool > *').forEach(f => f.classList.remove('on'));
  if (TOOLS.includes(view.kind)) {
    region.dataset.mode = 'tool';
    delete region.dataset.sides;
    const want = view.kind === 'launch' ? LAUNCH : view.kind === 'prototypes' ? PROTOTYPES : '/' + view.kind;
    let f = frames['tool:' + view.kind];
    if (!f) {
      f = frames['tool:' + view.kind] = document.createElement('iframe');
      f.addEventListener('load', () => zoomed(f));
      $('T').appendChild(f);
    }
    if (f.dataset.src !== want) f.src = f.dataset.src = want;
    f.classList.add('on');
    tell(f, false);
    return onShow();
  }
  const id = hubOn();
  if (!id || !M.hubs[id]) { region.dataset.mode = 'none'; return onShow(); }
  // A hub opens on its overview. With none, its tabs show alone.
  const hub = M.hubs[id], ov = hub.overview, p = pickOf(id);
  const pane = ov ? p.pane : 'right', right = rightOf(id);
  // A pick whose page is gone moves to the tab that took its place, so the
  // page coming back later never pulls me away from where I went.
  if (p.right && right !== p.right && !hub.tabs.includes(p.right)) keep(id, {...p, right});
  region.dataset.mode = ov ? 'hub' : 'one';
  // Half a screen hides the overview under a right pick.
  region.dataset.pane = pane;
  // Wide, a hub with an overview shows one side or two.
  const glyph = $('sides');
  region.dataset.sides = sides;
  glyph.hidden = !(wide() && ov);
  glyph.innerHTML = sides === 1 ? ICONS.one : ICONS.two;
  glyph.title = sides === 1 ? 'Show both sides' : 'Show one side';
  // A tab newly opened unfolds its group, so what opened always shows.
  if (right && right !== lastRight[id]) fold(id + ':' + M.sessions[M.pages[right].nn].tag, false);
  lastRight[id] = right;
  const ts = tabsOf(hub).filter(k => !hidden(k) || k === right), nns = [...new Set(ts.map(k => M.pages[k].nn))];
  const lit = k => k === right && !(oneAtATime() && pane === 'overview');
  $('tabs').innerHTML = (ov ? tab(ov, word(ov), ' ov', pane === 'overview' && oneAtATime()) : '')
    + (nns.length > 1 ? nns.map(nn => group(id, nn, ts.filter(k => M.pages[k].nn === nn), lit))
      : [nns.length ? `<span class="ghead lead">${chip(nns[0], '', true)}</span>` : '',
         ...ts.map(k => tab(k, word(k), '', lit(k), true))]).join('');
  if (ov) {
    const f = frame(ov);
    f.classList.add('on');
    tell(f, oneAtATime());
  }
  const r = frame(right);
  r.classList.add('on');
  tell(r, true);
  strip();
  const on = document.querySelector('.wtab.on');
  if (on) on.scrollIntoView({block: 'nearest', inline: 'nearest'});
  warm(id);
  onShow();
}

// The hub on show opens its other tabs ahead, hidden, one at a time: each
// once the one before has loaded and home has sat still a moment. A first
// click on one is then instant. Only 1100's own pages open ahead: a
// prototype, on its own port, waits for its click. Leaving the hub stops it.
let warming = '';
function warm(id) {
  if (warming === id) return;
  warming = id;
  const next = () => {
    const hub = M.hubs[id];
    if (warming !== id || hubOn() !== id || !hub) { if (warming === id) warming = ''; return; }
    const k = tabsOf(hub).find(k => !hidden(k) && !frames[k] && M.pages[k].up && !M.pages[k].port);
    if (!k) { warming = ''; return; }
    frame(k).addEventListener('load', () => setTimeout(next, 300), {once: true});
  };
  setTimeout(next, 800);
}

// The strip shows an arrow and a fade at each end that hides more. A
// vertical wheel over it scrolls it sideways.
function strip() {
  const t = $('tabs'), l = t.scrollLeft > 1, r = t.scrollLeft + t.clientWidth < t.scrollWidth - 1;
  t.classList.toggle('fl', l);
  t.classList.toggle('fr', r);
  $('al').classList.toggle('on', l);
  $('ar').classList.toggle('on', r);
}
$('tabs').addEventListener('scroll', strip, {passive: true});
$('tabs').addEventListener('wheel', e => {
  const t = $('tabs');
  if (e.ctrlKey || e.metaKey || t.scrollWidth <= t.clientWidth || Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
  e.preventDefault();
  t.scrollLeft += e.deltaY;
}, {passive: false});
$('al').onclick = () => $('tabs').scrollBy({left: -Math.max(120, $('tabs').clientWidth * 0.7), behavior: 'smooth'});
$('ar').onclick = () => $('tabs').scrollBy({left: Math.max(120, $('tabs').clientWidth * 0.7), behavior: 'smooth'});
new ResizeObserver(strip).observe($('tabs'));

function draw() {
  drawRail();
  drawMain();
}

// ---- zoom --------------------------------------------------------------------------

// One step a press, as a browser zooms. Two zooms move apart, each kept on
// each device. The page's, by the rail's buttons under Files: the strip and every
// page home frames, each by its own root, so nothing zooms twice. A page on
// another port, as the prototypes app's, is told by a message. A press
// never takes the cursor from the page I type in. The rail's own, by Rail
// size on System, which keeps it as rail-zoom: home hears it change.
const ZOOMS = %ZOOMS%;
const kept = key => ZOOMS.includes(+localStorage.getItem(key)) ? +localStorage.getItem(key) : 1;
let zoom = kept('home-zoom');
function zoomed(f) {
  try { f.contentDocument.documentElement.style.zoom = zoom === 1 ? '' : String(zoom); }
  catch (e) { if (f.contentWindow) f.contentWindow.postMessage({ws: 1, zoom}, '*'); }
}
function zoomAll() {
  document.documentElement.style.setProperty('--zoom', zoom);
  Object.values(frames).forEach(zoomed);
  requestAnimationFrame(edges);
}
function zoomRail() {
  document.documentElement.style.setProperty('--rail', kept('rail-zoom'));
  requestAnimationFrame(edges);
}
zoomRail();
addEventListener('storage', e => { if (e.key === 'rail-zoom') zoomRail(); });

// ---- where a click goes ----------------------------------------------------------

function go(v) {
  // The system page asks lsof while it is open, so it closes once I leave it.
  if (v.kind !== 'system' && frames['tool:system']) { frames['tool:system'].remove(); delete frames['tool:system']; }
  // Leaving a hub drops its hidden tab, so coming back finds it gone.
  if (view.kind === 'hub' && !(v.kind === 'hub' && v.id === view.id)) drop(view.id);
  // A hub gone meanwhile has nothing left to show.
  view = v.kind === 'hub' && !M.hubs[v.id] ? {kind: 'skills'} : v;
  draw();
}
function open(id, k) {
  if (k) keep(id, M.hubs[id].tabs.includes(k) ? {right: k, pane: 'right'} : {...pickOf(id), pane: 'overview'});
  go({kind: 'hub', id});
}
const nav = {
  pick: k => {
    const id = hubOn();
    if (k === M.hubs[id].overview) {
      keep(id, {...pickOf(id), pane: 'overview'});
      drop(id);
    } else keep(id, {right: k, pane: 'right'});
    draw();
    if (k === M.hubs[id].overview) home(id);
  },
  // The Team icon opens its hub on the team tab, back at its current stage,
  // as a press of the Team tab does.
  team: id => {
    if (!M.hubs[id]) return;
    keep(id, {...pickOf(id), pane: 'overview'});
    drop(id);
    go({kind: 'hub', id});
    home(id);
  },
  // A number, on the rail or on System, opens its hub, its right side on
  // its own session's tab, by entry(): a head's as a member's.
  session: nn => {
    const id = Object.keys(M.hubs).find(h => M.hubs[h].tabs.includes('transcript:' + nn));
    if (id) open(id, entry(M.hubs[id], nn));
  },
  // A rail arrow scrolls the numbers most of the rail's height that way.
  rail: way => { const l = $('tools'); l.scrollBy({top: way * l.clientHeight * 0.8, behavior: 'smooth'}); },
  fold: key => {
    fold(key, !folded.has(key));
    drawMain();
  },
  zoom: step => {
    zoom = ZOOMS[Math.max(0, Math.min(ZOOMS.length - 1, ZOOMS.indexOf(zoom) + step))];
    localStorage.setItem('home-zoom', zoom);
    zoomAll();
    drawRail();
  },
  // One side or two. One side shows what the right side showed.
  sides: () => {
    sides = sides === 1 ? 2 : 1;
    localStorage.setItem('home-sides', sides);
    const id = hubOn();
    if (sides === 1 && id) keep(id, {...pickOf(id), pane: 'right'});
    draw();
  },
  // Skills, System, Agenda, Launch, Prototypes and Files open their page in main;
  // picked again, they return.
  tool: kind => {
    if (view.kind === kind) return go(back);
    if (view.kind === 'hub') back = view;
    go({kind});
  },
};

// A page inside main says hello, and home tells it whether to drop its
// head's names. An assistant page's Launch page asks for that assistant's
// launch page, which opens under its own tab, on the right. A session of
// its whose wave waits on me asks for its Clarify tab. A session's number
// on System opens it as the rail does: its hub, on its own tab, by
// entry().
addEventListener('message', e => {
  const d = e.data || {};
  const f = Object.values(frames).find(x => x.contentWindow === e.source);
  if (!f || !d.ws) return;
  if (d.hello) {
    zoomed(f);
    const left = f.parentNode === $('L');
    tell(f, left ? oneAtATime() && !!(M.hubs[hubOn()] || {tabs: []}).tabs.length : f.parentNode === $('R'));
  }
  if (d.open === 'launch') {
    const id = Object.keys(M.hubs).find(h => M.hubs[h].overview === f.dataset.k);
    const k = id && 'launch:' + M.hubs[id].nn;
    if (k && M.hubs[id].tabs.includes(k)) open(id, k);
  }
  if (d.open === 'clarify') {
    const k = 'clarify:' + d.nn, id = M.pages[k] && M.pages[k].hub;
    if (id && M.hubs[id]) open(id, k);
  }
  if (d.open === 'session') nav.session(d.nn);
});

// ---- typing on home ---------------------------------------------------------------

// On my Mac, a letter or a paste landing on home itself, never in a field,
// goes to the page on show that takes typing, through its typeIn: the
// right side's first, then the team tab's, then a rail page's. A Tab goes
// the same way, through its tabIn, so a transcript fills its suggestion. A
// key shortcut stays a shortcut, and space still scrolls.
function hand(name, ...args) {
  for (const f of ['R', 'L', 'T'].flatMap(id => [...$(id).querySelectorAll(':scope > .on')])) {
    try { if (f.getClientRects().length && f.contentWindow[name] && f.contentWindow[name](...args)) return true; }
    catch (e) {}
  }
  return false;
}
anywhere(text => hand('typeIn', text), () => hand('tabIn'));
// A click on home itself, never into a field, hands the cursor back to the
// page on show that holds it, through its holdCursor: a transcript's box.
// So does a page newly on show, in onShow.
addEventListener('click', e => {
  if (!e.target.closest('input, textarea, select, [contenteditable]')) setTimeout(() => hand('holdCursor'));
});

// ---- told when something moves ------------------------------------------------------

// Home asks /model again, and redraws around the pages it keeps. A new 1100
// may draw a new home, so a new pid reloads it whole.
function apply(next) {
  if (next.pid !== M.pid) return location.reload();
  const had = new Set(M.waits);
  // The session on show and its tab: a hub that goes, as when its session
  // joins a team, takes me along into the hub holding that session now.
  const was = view.kind === 'hub' ? hereOf(view.id) : '', tab = was && rightOf(view.id);
  M = next;
  for (const k of Object.keys(frames)) {
    if (!k.startsWith('tool:') && !M.pages[k]) { frames[k].remove(); delete frames[k]; }
  }
  if (view.kind === 'hub' && !M.hubs[view.id]) {
    const to = was && Object.keys(M.hubs).find(h => h === was || M.hubs[h].members.includes(was));
    if (to) keep(to, {right: M.hubs[to].tabs.includes(tab) ? tab : entry(M.hubs[to], was), pane: 'right'});
    view = to ? {kind: 'hub', id: to} : {kind: 'skills'};
  }
  // On Skills, a new wait opens its hub by itself, on its own tab. Of
  // several, the ruled order picks: a handover first, then the rail's
  // order, then the hub's tabs'. Anywhere else, only the rail moves.
  const fresh = M.waits.filter(k => !had.has(k) && M.hubs[M.pages[k].hub]);
  if (view.kind === 'skills' && fresh.length) {
    const kind = k => M.pages[k].kind, at = k => M.rail.indexOf(M.pages[k].hub);
    const hub = M.pages[fresh.find(k => kind(k) === 'handover') || fresh.sort((a, b) => at(a) - at(b))[0]].hub;
    const tabs = tabsOf(M.hubs[hub]).filter(k => fresh.includes(k));
    const k = tabs.find(k => kind(k) === 'handover') || tabs[0];
    keep(hub, k ? {right: k, pane: 'right'} : {...pickOf(hub), pane: 'overview'});
    view = {kind: 'hub', id: hub};
  }
  draw();
}

// A browser holds six requests to one host at once, and each held watch is
// one. So home holds one, for itself and for every page of 1100's own it
// frames: each hands its watch up, through watchFor. The prototype page,
// from 1400, asks its own server.
const watched = new Set();
let asking = null, soon = 0, showing = '';
const rewatch = () => { clearTimeout(soon); soon = setTimeout(() => asking && asking.abort(), 50); };
window.watchFor = w => {
  watched.add(w);
  rewatch();
};
// Only a page on show is asked about. A hidden one moves nothing I see, and
// each page asked about is drawn again on every write 1100 hears. Shown
// again, it is asked with the key it last wore, so one that moved while
// hidden is told at once.
const shown = w => w.frameElement.classList.contains('on');
function onShow() {
  const now = Object.keys(frames).filter(k => frames[k].classList.contains('on')).join();
  if (now !== showing) { showing = now; rewatch(); setTimeout(() => hand('holdCursor')); }
}
// A framed page's watch as it stands: its address, its key, and whether it
// is saving. Nothing once its frame is gone, or its page took its watch
// away. A removed frame's window still reads its last page, so the frame
// itself is asked first. A page saving its own file is never reloaded, nor
// one typed into in the last three seconds: it is, once I pause. A page
// that draws its own news, as a transcript does, is told, never reloaded.
// A reload put off while I type is owed: it comes once I pause, whatever
// the page's key reads by then, since the page's own save takes up the key
// the outside change left.
function owe(w) {
  if (w.owedReload) return;
  w.owedReload = setInterval(() => {
    const s = watchOf(w);
    if (s && (s.typing || s.busy)) return;
    clearInterval(w.owedReload);
    if (s) w.location.reload();
  }, 500);
}
function watchOf(w) {
  try {
    if (w.closed || !w.frameElement || !w.frameElement.isConnected) return null;
    const e = w.document.getElementById('watch');
    return e ? {w, path: w.location.pathname + w.location.search, key: e.dataset.key,
                busy: 'busy' in e.dataset, typing: Date.now() - (w.typedAt || 0) < 3000} : null;
  } catch (e) { return null; }
}
(async () => {
  const nap = ms => new Promise(f => setTimeout(f, ms));
  let seen = '%SEEN%';
  for (;;) {
    const marks = [];
    for (const w of watched) { const m = watchOf(w); if (!m) watched.delete(w); else if (shown(w)) marks.push(m); }
    const q = [['/model', seen], ...marks.map(m => [m.path, m.key])]
      .map(([p, k]) => 'path=' + encodeURIComponent(p) + '&key=' + encodeURIComponent(k)).join('&');
    const ask = asking = new AbortController();
    try {
      const r = await fetch('/heard?' + q, {signal: ask.signal});
      if (r.headers.get('X-Heard')) {
        const got = (await r.text()).split('\n');
        let moved = got[0] !== seen;
        if (moved) { seen = got[0]; apply(await (await fetch('/model')).json()); }
        marks.forEach((m, i) => {
          const now = got[i + 1], still = watchOf(m.w);
          if (now !== undefined && now !== m.key && still && !still.busy && still.key === m.key) {
            if (typeof m.w.told === 'function') { m.w.told(now); moved = true; }
            else if (!still.typing) { m.w.location.reload(); moved = true; }
            else owe(m.w);
          }
        });
        // An answer that moved nothing here waits a second before the next
        // ask, so nothing is ever asked about without pause.
        if (!moved) await nap(1000);
        continue;
      }
    } catch (e) { if (ask.signal.aborted) continue; }
    await nap(3000);
  }
})();

// ---- my phone ------------------------------------------------------------------------

// Held sideways, iOS insets both sides alike, though only one holds the
// notch: how the phone is turned says which. Opened from the home screen
// and held upright, iOS lays the page out short by its status bar, 47 on
// an iPhone 13, though it draws the whole glass: the rest showed as a band.
// There the home takes the screen's own size, and sits in the page instead
// of filling the window.
function fit() {
  const o = window.orientation, root = document.documentElement.classList;
  root.toggle('nl', o === 90);
  root.toggle('nr', o === -90);
  root.toggle('ios-app', navigator.standalone === true);
  if (navigator.standalone !== true) return;
  const long = Math.max(screen.width, screen.height), short = Math.min(screen.width, screen.height);
  const wide = innerWidth >= innerHeight;
  Object.assign(document.body.style, {position: 'absolute', top: '0', left: '0',
    width: (wide ? long : short) + 'px', height: (wide ? short : long) + 'px'});
}
addEventListener('resize', fit);
addEventListener('orientationchange', fit);
fit();

// ---- the buzz ---------------------------------------------------------------------------

// Only my phone's home screen can be buzzed. Its bell asks, from my tap, as
// iOS requires; once allowed, it hides, and each load hands the phone's
// subscription to 1100 again. A tap on a buzz opens what it names.
const PUSH = %PUSH%;
const buzzable = navigator.standalone === true && 'serviceWorker' in navigator && 'PushManager' in window
  && 'Notification' in window;
let worker = null;
const raw = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - s.length % 4) % 4)),
  c => c.charCodeAt(0));
const handed = sub => fetch('/push', {method: 'POST', redirect: 'manual',
  body: new URLSearchParams({sub: JSON.stringify(sub), origin: location.origin})});
nav.bell = async () => {
  if (!worker) return;
  const said = await Notification.requestPermission();
  if (said !== 'granted') { $('bell').hidden = said === 'denied'; return; }
  const ready = await navigator.serviceWorker.ready;
  await handed(await ready.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: raw(PUSH)}));
  $('bell').hidden = true;
};
(async () => {
  if (!buzzable) return;
  navigator.serviceWorker.addEventListener('message', e => {
    const to = e.data && e.data.open;
    if (!to) return;
    history.replaceState(null, '', new URL(to, location.href).hash || '#');
    go(landed());
  });
  await navigator.serviceWorker.register('/sw.js');
  worker = await navigator.serviceWorker.ready;
  const sub = await worker.pushManager.getSubscription();
  if (sub && Notification.permission === 'granted') return handed(sub);
  $('bell').hidden = Notification.permission === 'denied';
})().catch(() => {});

matchMedia(NARROW).addEventListener('change', draw);
setInterval(drawRail, 30000);
zoomAll();
go(landed());
</script>
"""
