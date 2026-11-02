#!/usr/bin/env python3
"""dashboard-views.py — what 1100 finds in each session, and the tools it draws with.

1100 is the only page server. It draws every page itself, bar the
prototype page, which it frames from the one prototypes app on 1400.
Home, the workstation, reads each session's pages here, so every page is
found one way:

  a wave not sent           clarify-page.py
  rows in launch.json       launch-page.py
  a subject held, unlocked  lib/prototypes.py
  a context past System's   handover-page.py
  a plan, stages.json       assistant-page.py
  a jury's plan, jury/      jury-page.py
  a walk's screenshots      walk-shots-page.py
  walk-list.md              walk-list-page.py

The advisor wears its role's badge, by its name: advisor-page.py's
seated(). Its panel sits on its Transcript tab, no tab of its own.

Which page waits on me is workstation.py's model(). The lines under the
launch, prototype and assistant tabs, and every file whose write can move
a page, live here too. Imported, never run.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import drive  # noqa: E402
import follow  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import prototypes  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402
from prototypes import APP  # noqa: E402

# Each page tool, loaded whole, so 1100 reads each file the page's own way:
# every tab kind's, by page.TAB_KINDS, the team tab's, and the advisor's
# panel's.
tools = {kind: page.tool(name) for kind, (_, name) in page.TAB_KINDS.items()}
clarify, gallery, launcher, handover, jury, shots, walk_list = (
    tools[k] for k in ("clarify", "prototype", "launch", "handover", "jury", "shots", "walk"))
assistant = page.tool("assistant-page")
advisor = page.tool("advisor-page")


# ---- the line under each -----------------------------------------------------

def stage_at(nn: str, held: dict, live: dict) -> int:
    """The current stage, the first holding a mission not stopped, as the
    assistant page opens on it. Its place in the plan, from 0."""
    stages = plans.plan(nn)["stages"]
    stopped = [all(assistant.state({**m, **plans.found(m, held, nn)}, held, live, None)[2] == " done"
                   for m in s.get("missions", [])) for s in stages]
    return stopped.index(False) if False in stopped else len(stages) - 1


def plan_line(nn: str, at: int) -> str:
    return f"Stage {chr(65 + at)} of {len(plans.plan(nn)['stages'])}"


def proto_line(subject: str) -> str:
    gens = prototypes.generations(os.path.join(APP, subject))
    if not gens:
        return subject
    newest = gallery.load(gens[-1][1])
    many = len(newest.get("variations", []))
    return f"{subject} · G{newest.get('generation', gens[-1][0])} · {many} variation{'' if many == 1 else 's'}"


def launch_line(nn: str) -> str:
    rows = launcher.read(nn)
    web = sum(1 for r in rows if r.get("kind") == "browser")
    count = lambda k, word: f"{k} {word}{'' if k == 1 else 's'}" if k else ""
    return " · ".join(x for x in (count(len(rows) - web, "session"), count(web, "browser")) if x)


def heard() -> list:
    """Every file whose write can move home or a page 1100 draws: each
    session's own, its plan's answers and drive, what it took to drive and
    to follow, the subject it holds, and its jury runs. The numbers come
    from the folder's listing: a tick reads no record."""
    held = [n for n in registry.listing(registry.WORK) if re.fullmatch(r"\d{2}", n)]
    out = registry.watched(held)
    for nn in held:
        answers = os.path.join(registry.folder(nn), "answers")
        out += [launcher.path(nn), os.path.join(registry.folder(nn), "stages.json"),
                drive.path(nn), os.path.join(registry.folder(nn), successor.FILE),
                follow.path(nn), prototypes.subject_file(nn), answers]
        out += [os.path.join(answers, n) for n in registry.listing(answers)]
        if subject := prototypes.subject_of(nn):
            out.append(os.path.join(APP, subject))
    return out + jury.heard() + shots.heard() + walk_list.heard()
