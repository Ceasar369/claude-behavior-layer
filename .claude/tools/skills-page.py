#!/usr/bin/env python3
"""skills-page.py — every skill, as a cheat sheet, on 1100/skills.

Each skill's name, description and arguments already sit in the head of
its SKILL.md. The page reads every head each time it draws, so it is
always current, stores nothing, and never spends a token.

Skills group by family. A family is its router, D-name, then its
children, name-*, in the order of their digits. Every other skill sits
first, under No family, laid left to right across the page. The numbered
families follow in as many columns as the width holds.

A row leads with its command, copied on a click. Under it, its
arguments, one choice a line. Under them, its intent, the description's
first sentence, across the column. A small filter narrows every family
to the rows holding each word typed; Enter copies the first.

The dashboard's server serves it. Imported, never run.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402

SKILLS = os.path.join(registry.ROOT, ".claude", "skills")
ROUTER = re.compile(r"(\d+)-(.+)")
# The families whose pages wear an icon, beside their digit.
ICONED = ("assistant", "clarify", "prototype", "agenda")


def value(raw: str) -> str:
    """A head's value as it reads: a double-quoted one drops its quotes, and
    its \\" and \\\\ read as a quote and a backslash."""
    raw = raw.strip()
    if len(raw) > 1 and raw[0] == raw[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", raw[1:-1])
    return raw.strip('"')


def heads() -> list:
    """Every SKILL.md's head, as (name, description, arguments), by name."""
    out = []
    for name in sorted(registry.listing(SKILLS)):
        try:
            with open(os.path.join(SKILLS, name, "SKILL.md"), encoding="utf-8", errors="replace") as f:
                text = f.read(4000)
        except OSError:
            continue
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        field = lambda k: next((value(line.split(":", 1)[1]) for line in head.splitlines()
                                if line.startswith(f"{k}:")), "")
        out.append((field("name") or name, field("description"), field("argument-hint")))
    return out


def families(found: list) -> list:
    """(digit, family, [skills]) for every router, by digit, then No family."""
    routers = sorted(((m.group(1), m.group(2), s) for s in found if (m := ROUTER.fullmatch(s[0]))),
                     key=lambda r: (int(r[0]), len(r[0])))
    taken = {r[2][0] for r in routers}
    groups = []
    for digit, fam, router in routers:
        kids = [s for s in found if s[0] not in taken and s[0].startswith(f"{fam}-")]
        taken |= {s[0] for s in kids}
        groups.append((digit, fam, [router] + kids))
    return groups + [("", "no family", [s for s in found if s[0] not in taken])]


def args(hint: str) -> str:
    """A skill's arguments, one choice a line. What each means dims."""
    return '<div class="args">' + "".join(
        f'<div>{page.esc(form)}' + (f' <span class="mn">— {page.esc(means)}</span>' if means else "") + '</div>'
        for form, _, means in (choice.partition(" — ") for choice in hint.split(" · "))) + '</div>'


def line(skill: tuple) -> str:
    name, description, arguments = skill
    intent = (re.match(r".*?[.!?](?=\s|$)", description) or [description])[0]
    return (f'<div class="sr"><button class="cmd" title="Copy /{page.esc(name)}" data-c="/{page.esc(name)}">'
            f'<span class="t">/{page.esc(name)}</span>{page.icon("copy", 13)}</button>'
            + (args(arguments) if arguments else "")
            + f'<p class="int">{page.esc(intent)}</p></div>')


STYLE = "<style>\n" + page.shared("skills.css") + "</style>\n"


def sections(found: list) -> tuple:
    """The No family section, and every numbered family's, as the page draws them."""
    primary, groups = "", []
    for digit, fam, skills in families(found):
        if not skills:
            continue
        mark = ((f'<span class="dg">{digit}</span>' if digit else "")
                + (page.icon(fam, 14) if fam in ICONED else ""))
        title = fam.replace("-", " ").capitalize() if digit else "No family"
        rows = "".join(line(s) for s in skills)
        section = (f'<section class="skf"><div class="skh">{mark}<b>{page.esc(title)}</b></div>'
                   + (f'<div class="across">{rows}</div>' if not digit else rows) + '</section>')
        if digit:
            groups.append(section)
        else:
            primary = section
    return primary, groups


FIND = (f'<label class="find">{page.icon("filter", 14)}<input id="q" spellcheck="false" '
        'aria-label="Filter the skills" placeholder="Filter: a command, what it does"></label>')
NO_MATCH = '<p class="nomatch">No skill\'s command or intent holds that.</p>'


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws every skill. The page's own script, .claude/pages/scripts/skills.js,
# copies and filters: lib/live.py.

def drawn() -> str:
    """The skills page, every skill drawn, its filter keeping no words past
    a reload but its own."""
    found = heads()
    primary, groups = sections(found)
    body = (live.watch() + STYLE + f'<div class="first">{primary}</div><div class="sk">{"".join(groups)}</div>'
            + NO_MATCH + f'<script src="{live.src("skills.js")}"></script>\n')
    return page.render("00-skills", [("", body)],
                       page.head("skills", "", FIND.replace('<input id="q"', '<input id="q" data-draft="no"', 1),
                                 f'<span class="hm" id="hm">{len(found)} skills</span>'),
                       refresh=0)


def files() -> list:
    """The skills folder, each skill's folder, and each SKILL.md: a skill
    added later is heard by the folder."""
    names = registry.listing(SKILLS)
    return [SKILLS, *(os.path.join(SKILLS, n) for n in names), *(os.path.join(SKILLS, n, "SKILL.md") for n in names)]


# The page's contract, lib/live.py's: its address, its draw, its files.
LIVE = live.Page(r"/skills", drawn, files=files)
