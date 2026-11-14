#!/usr/bin/env python3
"""library-page.py — the library, as a book, on 1100/library.

The page reads library/ each time it draws, so it stores nothing, and a page
added there shows on the next draw. Its tree is library-MOC.md's: a ## holding
a ### is a chapter, a ### a subchapter, a #### a section, a link a word. A
chapter, a subchapter and a section are numbered by their place in that file.
Inside each, the rail sorts its words alphabetically and numbers them by that
place, as 8.1.1 or 3.2.1.1, its graphs first, lettered A, B, C, then a line.
Each chapter and subchapter shows its count, graphs counted, so they add up.

A numbered rail that folds sits beside the page of the word opened. Find
narrows the words to those holding what is typed. The address's hash names
the word, and what I folded and typed outlives a reload. So do the rail's
width, which its edge drags, and whether it is shut, by its tab top left:
page rules 6 and 39 bend here, by my ruling.

A graph, library/graphs/<name>.md, sits first in its one home subchapter, a
small icon then its name. Opened, its text is on the left and its graph on
the right, as one path or two to four lanes side by side, each its own path. A divider drags the width, the graph's bottom edge its length, and
no text changes size: each box is a page box, never a scaled picture. A box
linking a word wears that word's number in the rail, then its name. A
press on a box swaps the left side to that box's word; the graph stays. Every
word a box links says "Explained in" and the graph's name.

Each word and graph wears its review mark, as library-review.py keeps it:
a grey ring, never reviewed; a green check, reviewed; an orange dot,
changed since. Each chapter and subchapter counts what changed and what
is new in place of its total. One switch atop the rail hides every mark,
its counts back to totals, and outlives a reload. An opened word or graph
says its state under its title, with the button that sets it.

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

LIBRARY = os.path.join(registry.ROOT, "library")
GRAPHS = "graphs"
MOC = "library-MOC.md"
HEADING = re.compile(r"(#{2,4}) +(.+?)\s*$")
LINK = re.compile(r"\[\[([\w-]+)(?:\|([^\]]+))?\]\]")
GRAPH = re.compile(r"- Graph: \[\[([\w-]+)(?:\|([^\]]+))?\]\]\s*$")
SOURCE = re.compile(r"Source: *(\S+)\s*$")
STEP = re.compile(r"\d+\. +(.+?)\s*$")
BRANCH = re.compile(r"\s+- +(yes|no): +(.+?)\s*$")
BOX = re.compile(r"(.*?)\s*\[\[([\w-]+)\]\]\s*$")
FACT = re.compile(r"- \*\*([^*]+)\*\* +[—–] +(.+?)\s*$")
UNPROVEN = "Unproven:"
SERIES = "Series:"
# Lucide's chart-network, the prototype's graph icon.
ICON = ('<svg class="i" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="m13.11 7.664 1.78 2.672"/><path d="m14.162 12.788-3.324 1.424"/>'
        '<path d="m20 4-6.06 1.515"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/><circle cx="12" cy="6" r="2"/>'
        '<circle cx="16" cy="12" r="2"/><circle cx="9" cy="15" r="2"/></svg>')


def tree(text: str) -> list:
    """The file's chapters. A subchapter holds `words` or `sections`, each
    word a (slug, name), and its `graphs`, each a (slug, name)."""
    chapters, heading, chapter, sub, section = [], "", None, None, None
    for line in text.splitlines():
        if m := HEADING.fullmatch(line):
            tier, name = len(m.group(1)), m.group(2)
            if tier == 2:
                heading, chapter, sub, section = name, None, None, None
            elif tier == 3:
                if chapter is None:
                    chapter = {"name": heading, "subs": []}
                    chapters.append(chapter)
                sub, section = {"name": name, "words": [], "sections": [], "graphs": []}, None
                chapter["subs"].append(sub)
            elif sub:
                section = {"name": name, "words": []}
                sub["sections"].append(section)
        elif sub and (m := GRAPH.fullmatch(line)):
            sub["graphs"].append((m.group(1), m.group(2) or m.group(1)))
        elif sub and line.startswith("- "):
            (section or sub)["words"].extend((s, n or s) for s, n in LINK.findall(line))
    return chapters


def spots(chapters: list) -> list:
    """Every word, in the file's order, as (slug, name, its trail of tiers)."""
    out = []
    for c, chapter in enumerate(chapters, 1):
        for s, sub in enumerate(chapter["subs"], 1):
            up = [f"{c} {chapter['name']}", f"{c}.{s} {sub['name']}"]
            out += [(slug, name, up) for slug, name in sub["words"]]
            for x, section in enumerate(sub["sections"], 1):
                out += [(slug, name, [*up, f"{c}.{s}.{x} {section['name']}"]) for slug, name in section["words"]]
    return out


def homes(chapters: list) -> list:
    """Every graph, in the file's order, as (slug, name)."""
    return [g for chapter in chapters for sub in chapter["subs"] for g in sub["graphs"]]


def parts(text: str) -> tuple:
    """A page's sections, as (heading, [paragraph]), and its source."""
    sections, source = [], ""
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split("\n")).strip()
        if m := SOURCE.fullmatch(block):
            source = m.group(1)
        elif block.startswith("## "):
            sections.append((block[3:], []))
        elif sections and block:
            sections[-1][1].append(block)
    return sections, source


def boxed(text: str) -> tuple:
    """A box's words and the word it links, or ""."""
    m = BOX.fullmatch(text)
    return (m.group(1), m.group(2)) if m else (text, "")


def chart(text: str) -> dict:
    """A graph's file: its series, as "A login, in order, 1 of 3" or "",
    its text, as ("p" | "fact" | "unproven", …) lines,
    its lanes, each {name, steps, unproven}, every step, each {box, branch},
    its caption, the unproven lines under its graph, and its sources. A
    graph with no ### is one lane, named "". An Unproven line sits where it
    is written: in a lane until the caption, under the graph after it."""
    out = {"series": "", "text": [], "lanes": [], "steps": [], "caption": "", "unproven": [], "sources": []}
    part = ""
    for line in text.splitlines():
        if m := SOURCE.fullmatch(line):
            out["sources"].append(m.group(1))
        elif line.startswith("## "):
            part = line[3:].strip()
        elif part == "The text" and (m := FACT.fullmatch(line)):
            out["text"].append(("fact", (m.group(1), m.group(2))))
        elif part == "The text" and line.startswith(SERIES):
            out["series"] = line[len(SERIES):].strip()
        elif part == "The text" and line.strip():
            out["text"].append(("unproven" if line.startswith(UNPROVEN) else "p", line.strip()))
        elif part == "The graph":
            if line.startswith("### "):
                out["lanes"].append({"name": line[4:].strip(), "steps": [], "unproven": []})
            elif m := STEP.fullmatch(line):
                if not out["lanes"]:
                    out["lanes"].append({"name": "", "steps": [], "unproven": []})
                out["lanes"][-1]["steps"].append({"box": boxed(m.group(1)), "branch": None})
                out["steps"].append(out["lanes"][-1]["steps"][-1])
            elif (m := BRANCH.fullmatch(line)) and out["steps"]:
                out["steps"][-1]["branch"] = (m.group(1), boxed(m.group(2)))
            elif line.startswith("Figure:"):
                out["caption"] = line[7:].strip()
            elif line.startswith(UNPROVEN):
                lane = out["lanes"][-1] if out["lanes"] and not out["caption"] else None
                (lane["unproven"] if lane else out["unproven"]).append(line.strip())
    if len(out["lanes"]) == 1:
        out["unproven"][:0] = out["lanes"][0]["unproven"]
        out["lanes"][0]["unproven"] = []
    return out


def linked(text) -> list:
    """Every word a graph's boxes link, once each, in order."""
    got = chart(text or "")
    out = [s["box"][1] for s in got["steps"]] + [s["branch"][1][1] for s in got["steps"] if s["branch"]]
    return list(dict.fromkeys(w for w in out if w))


def inline(text: str) -> str:
    """A paragraph's words, its backticks as code."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", page.esc(text))


def explained(slug: str, graphs: list) -> str:
    """The lines linking a word to each graph whose boxes link it."""
    return "".join(f'<button class="explained" data-g="{g}">{ICON} Explained in: {page.esc(n)}</button>'
                   for g, n, words in graphs if slug in words)


def mark(state: str) -> str:
    """An item's review mark: new, ok or changed."""
    if state == "ok":
        return f'<span class="mk mk-ok" title="Reviewed">{page.icon("check", 12)}</span>'
    return f'<span class="mk mk-{state}" title="{"Changed since review" if state == "changed" else "Never reviewed"}"></span>'


MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def reviewed(key: str, marks: dict) -> str:
    """The line under an item's title: its state, when, and its button."""
    state, at = marks.get(key, ("new", ""))
    when = ""
    if at:
        day, clock = at.split(" ")
        _, month, d = day.split("-")
        when = f", {MONTHS[int(month) - 1]} {int(d)} at {clock}"
    said = {"new": "Never reviewed", "ok": f"Reviewed{when}",
            "changed": f"Changed since you reviewed it{when}"}[state]
    to, press = ("not-reviewed", "Mark not reviewed") if state == "ok" else ("reviewed", "Mark reviewed")
    return (f'<div class="rv-line rv-{state}">{mark(state)}<span>{said}</span>'
            f'<button type="button" class="btn rv-set" data-item="{page.esc(key)}" data-to="{to}">{press}</button></div>')


def reading(slug: str, name: str, trail: list, text, graphs: list = (), marks: dict = None) -> str:
    """One word's page, hidden until opened. No file: it says so. `graphs`
    are (slug, name, words) each."""
    steps = "".join(f"<span>{page.esc(t)}</span><i>›</i>" for t in trail)
    back = f'<button class="close back" aria-label="Back to the contents">{page.icon("back")}</button>'
    head = f'<nav class="trail">{back}{steps}</nav><h1>{page.esc(name)}</h1>{reviewed(slug, marks or {})}'
    if text is None:
        return f'<article class="reading" id="p-{slug}" hidden>{head}<p class="dim">No page for this word.</p>{explained(slug, graphs)}</article>'
    sections, source = parts(text)
    said = "".join(f"<h2>{page.esc(h)}</h2>" + "".join(f"<p>{inline(p)}</p>" for p in ps) for h, ps in sections)
    link = ""
    if source:
        src = page.esc(source)
        link = (f'<a class="source" href="{src}" target="_blank" rel="noreferrer">{src}</a>'
                if source.startswith(("https://", "http://")) else f'<p class="source">{src}</p>')
    return f'<article class="reading" id="p-{slug}" hidden>{head}{said}{explained(slug, graphs)}{link}</article>'


def source(src: str) -> str:
    s = page.esc(src)
    return (f'<a class="source" href="{s}" target="_blank" rel="noreferrer">{s}</a>'
            if src.startswith(("https://", "http://")) else f'<p class="source">{s}</p>')


def box(text: str, slug: str, names: dict, kind: str = "") -> str:
    """One box. Linking a word the library holds, it is a button naming it."""
    cls = f"gx-box{' ask' if text.endswith('?') else ''}{kind}"
    if slug in names:
        return (f'<button class="{cls}" data-w="{slug}">{page.esc(text)}'
                f'<small>{page.esc(names[slug])}</small></button>')
    return f'<div class="{cls}">{page.esc(text)}</div>'


def lane(each: dict, names: dict, named: bool) -> str:
    """One lane: its own path of boxes, top to bottom, its name above it
    and its unproven lines under it when the graph holds several."""
    flow, label = [], ""
    for i, step in enumerate(each["steps"]):
        if i:
            flow.append(f'<div class="gx-arrow"><i></i><span>↓</span>{f"<em>{label}</em>" if label else ""}</div>')
        side, branch, label = "", "<span></span>", ""
        if step["branch"]:
            said_as, (words, w) = step["branch"]
            side, branch = f"{said_as} →", box(words, w, names, " bad")
            label = "no" if said_as == "yes" else "yes"
        flow.append(f'<div class="gx-step">{box(*step["box"], names)}<span class="gx-side">{side}</span>{branch}</div>')
    head = f'<h3 class="gx-name">{inline(each["name"])}</h3>' if named else ""
    marks = "".join(f'<p class="stand">{inline(u)}</p>' for u in each["unproven"])
    plain = " plain" if named and not any(step["branch"] for step in each["steps"]) else ""
    return f'<div class="gx-lane{plain}">{head}<div class="gx-chart">{"".join(flow)}</div>{marks}</div>'


def graphing(slug: str, name: str, text, names: dict, marks: dict = None) -> str:
    """One graph, hidden until opened: its text left, its graph right, its
    review line under its headline."""
    back = f'<button class="close back" aria-label="Back to the contents">{page.icon("back")}</button>'
    if text is None:
        return (f'<article class="graph" id="g-{slug}" hidden><div class="gx-col">{back}'
                f'<h1>{page.esc(name)}</h1><p class="dim">No file for this graph.</p></div></article>')
    got, said, facts = chart(text), [], []
    for kind, line in got["text"]:
        if kind == "fact":
            facts.append(f"<li><b>{page.esc(line[0])}</b> — {inline(line[1])}</li>")
            continue
        if facts:
            said.append('<h2>At a glance</h2><ul class="gx-keys">' + "".join(facts) + "</ul>")
            facts = []
        said.append(f'<p class="stand">{inline(line)}</p>' if kind == "unproven"
                    else (f"<h1>{inline(line)}</h1>" if not said else f"<p>{inline(line)}</p>"))
    if facts:
        said.append('<h2>At a glance</h2><ul class="gx-keys">' + "".join(facts) + "</ul>")
    said.insert(1 if said and said[0].startswith("<h1>") else 0, reviewed(f"graphs/{slug}", marks or {}))
    lanes ="".join(lane(each, names, len(got["lanes"]) > 1) for each in got["lanes"])
    picture = (f'<div class="gx-lanes">{lanes}</div>'
               '<div class="gx-edge" title="Drag to change the graph\'s length">═</div>'
               + (f'<p class="gx-fig">Figure: {inline(got["caption"])}</p>' if got["caption"] else "")
               + "".join(f'<p class="stand">{inline(u)}</p>' for u in got["unproven"])
               + "".join(source(src) for src in got["sources"]))
    return (f'<article class="graph" id="g-{slug}" data-g="{slug}" hidden>'
            f'<div class="gx-col"><div class="gx-text">{back}'
            + (f'<p class="gx-series">Series: {inline(got["series"])}</p>' if got["series"] else "")
            + f'{"".join(said)}</div>'
            f'<div class="gx-word" hidden><button class="gx-return">← Back to {page.esc(name)}</button>'
            '<div class="gx-slot"></div></div></div>'
            '<div class="gx-bar" title="Drag to change the width">‖</div>'
            f'<div class="gx-graph">{picture}</div></article>')


def word(slug: str, name: str, at: str = "", marks: dict = None) -> str:
    """A word's button, its mark, then its number `at` in the tree."""
    number = f'<span class="n">{at}</span> ' if at else ""
    return (f'<button class="t-word" data-w="{slug}">{mark(marks.get(slug, ("new",))[0]) if marks is not None else ""}'
            f'{number}{page.esc(name)}</button>')


def entry(slug: str, name: str, letter: str, marks: dict = None) -> str:
    worn = mark(marks.get(f"graphs/{slug}", ("new",))[0]) if marks is not None else ""
    return (f'<button class="t-word t-graph" data-g="{slug}">{worn}{ICON}<span class="n">{letter}</span> '
            f'{page.esc(name)}</button>')


def alphabetical(words: list) -> list:
    return sorted(words, key=lambda w: w[1].casefold())


def counted(sub: dict) -> int:
    """A subchapter's count: its words, its sections' words, its graphs."""
    return len(sub["words"]) + sum(len(x["words"]) for x in sub["sections"]) + len(sub["graphs"])


def numbered(chapters: list) -> list:
    """Every row of the rail, in its order, as the rail numbers it: each
    {n, kind, name, slug, up, count}. A graph is n "2.1.A", under its
    subchapter. The app door reads the library by these numbers."""
    out = []
    row = lambda n, kind, name, slug="", up="", count=0: out.append(
        {"n": n, "kind": kind, "name": name, "slug": slug, "up": up, "count": count})
    for c, chapter in enumerate(chapters, 1):
        row(f"{c}", "chapter", chapter["name"], count=sum(counted(sub) for sub in chapter["subs"]))
        for s, sub in enumerate(chapter["subs"], 1):
            at = f"{c}.{s}"
            row(at, "subchapter", sub["name"], up=f"{c}", count=counted(sub))
            for i, (slug, name) in enumerate(sub["graphs"]):
                row(f"{at}.{chr(65 + i)}", "graph", name, slug, at)
            for n, (slug, name) in enumerate(alphabetical(sub["words"]), 1):
                row(f"{at}.{n}", "word", name, slug, at)
            for x, section in enumerate(sub["sections"], 1):
                row(f"{at}.{x}", "section", section["name"], up=at, count=len(section["words"]))
                for n, (slug, name) in enumerate(alphabetical(section["words"]), 1):
                    row(f"{at}.{x}.{n}", "word", name, slug, f"{at}.{x}")
    return out


def fold(tier: str, key: str, label: str, count: str, kids: str) -> str:
    """A row that folds what sits under it, folded at first."""
    arrows = page.icon("right", 13, "i shut") + page.icon("down", 13, "i open")
    return (f'<div class="fold" data-k="{key}"><button class="{tier}">{arrows}{label}{count}</button>'
            f'<div class="kids">{kids}</div></div>')


def items(subs: list) -> list:
    """Every word's and graph's item under these subchapters, as
    library-review.py names them."""
    return [k for sub in subs for k in [*(f"graphs/{g}" for g, _ in sub["graphs"]),
                                        *(w for w, _ in sub["words"]),
                                        *(w for x in sub["sections"] for w, _ in x["words"])]]


def waiting(keys: list, marks: dict) -> str:
    """What still asks for review, as a count reads it: 3 changed · 1 new,
    or "" when nothing does."""
    states = [marks.get(k, ("new",))[0] for k in keys]
    said = [f"{states.count(s)} {s}" for s in ("changed", "new") if states.count(s)]
    return " · ".join(said)


def counts(total: int, keys: list, marks: dict) -> str:
    """A row's plain total, then its review count, which the switch shows
    in its place."""
    left = waiting(keys, marks)
    rv = (" · ".join(f'<b class="c-{part.split()[1]}">{part}</b>' for part in left.split(" · ")) if left
          else mark("ok"))
    return f'<span class="count plain">{total}</span><span class="count rv">{rv}</span>'


def contents(chapters: list, marks: dict = None) -> str:
    out, marks = [], marks or {}
    for c, chapter in enumerate(chapters, 1):
        subs = []
        for s, sub in enumerate(chapter["subs"], 1):
            kids = "".join(entry(*g, chr(65 + i), marks) for i, g in enumerate(sub["graphs"]))
            kids += '<hr class="t-sep">' if sub["graphs"] else ""
            kids += "".join(word(*w, f"{c}.{s}.{n}", marks) for n, w in enumerate(alphabetical(sub["words"]), 1))
            for x, section in enumerate(sub["sections"], 1):
                kids += (f'<div class="t-3"><span class="n">{c}.{s}.{x}</span> {page.esc(section["name"])}</div>'
                         '<div class="deep">' + "".join(word(*w, f"{c}.{s}.{x}.{n}", marks) for n, w in
                                                        enumerate(alphabetical(section["words"]), 1)) + '</div>')
            subs.append(fold("t-2", f"{c}.{s}", f'<span class="n">{c}.{s}</span> {page.esc(sub["name"])}',
                             counts(counted(sub), items([sub]), marks), kids))
        total = sum(counted(sub) for sub in chapter["subs"])
        out.append(fold("t-1", f"{c}", f'<span class="n">{c}</span> {page.esc(chapter["name"])}',
                        counts(total, items(chapter["subs"]), marks), "".join(subs)))
    return "".join(out)


def width(chapters: list, marks: dict = None) -> str:
    """The rail's width until I drag it, its widest line's with every fold
    open. A graph's line counts its icon as two characters. A row's mark
    adds its width, and a count its review count's, when that is longer."""
    lines, marks = {38: 0, 56: 0, 40: 0}, marks or {}
    tally = lambda subs: max(3, len(waiting(items(subs), marks)))
    for c, chapter in enumerate(chapters, 1):
        lines[40] = max(lines[40], len(f'{c} {chapter["name"]} ') + tally(chapter["subs"]))
        for s, sub in enumerate(chapter["subs"], 1):
            lines[40] = max(lines[40], len(f'{c}.{s} {sub["name"]} ') + tally([sub]))
            lines[38] = max([lines[38], *(len(f"{c}.{s}.00 {n}") for _, n in sub["words"]),
                             *(len(n) + 4 for _, n in sub["graphs"])])
            for x, section in enumerate(sub["sections"], 1):
                lines[38] = max(lines[38], len(f'{c}.{s}.{x} {section["name"]}'))
                lines[56] = max([lines[56], *(len(f"{c}.{s}.{x}.00 {n}") for _, n in section["words"])])
    # A word's or a graph's mark, and its gap, add 18px.
    widest = ", ".join(f"calc({n}ch + {px + 24 + (18 if px != 40 else 0)}px)" for px, n in lines.items())
    return f"max({widest})"


STYLE = "<style>\n" + page.shared("library.css") + "</style>\n"

# The rail's tab: the advisor's Advise tab, borrowed, as the explanation page
# borrows it.
TAB = page.whole(page.tool("advisor-page").STYLE, r"\.atab")


def read(path: str):
    """A file's words, or None when it cannot be read. A file cut short
    mid-letter reads to where it was cut."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


FIND = (f'<label class="find">{page.icon("search", 14)}<input id="q" spellcheck="false" '
        'aria-label="Find a word" placeholder="Find a word"></label>')
EMPTY = "No words in the library."


def book(find: str):
    """The library as the page draws it: {rail, front, pages}, its rail
    wearing `find`, or None when it holds no word."""
    moc = read(os.path.join(LIBRARY, MOC)) or ""
    chapters = tree(moc)
    every = spots(chapters)
    texts = {slug: read(os.path.join(LIBRARY, f"{slug}.md")) for slug, _, _ in every}
    drawn = {slug: read(os.path.join(LIBRARY, GRAPHS, f"{slug}.md")) for slug, _ in homes(chapters)}
    if not every:
        return None
    # A box linking a word names it by its number in the rail, then its name.
    names = {r["slug"]: f'{r["n"]} {r["name"]}' for r in reversed(numbered(chapters)) if r["kind"] == "word"}
    graphs = [(g, n, linked(drawn[g])) for g, n in homes(chapters)]
    marks = page.tool("library-review").states(
        numbered(chapters), lambda r: (drawn if r["kind"] == "graph" else texts).get(r["slug"]))
    switch = ('<button type="button" class="sw-row" id="marks" aria-pressed="true">'
              '<span class="sw-name">Review marks</span><span class="sw"><span class="sw-knob"></span></span></button>')
    rail = (f'<aside style="width:{width(chapters, marks)}">{find}{switch}<div id="tree">{contents(chapters, marks)}</div>'
            '<div id="found" hidden>' + "".join(word(s, n, "", marks) for s, n, _ in every)
            + '<p class="dim" id="none" hidden>No word found.</p></div></aside><div class="t-bar"></div>\n')
    toggle = ('<div class="t-toggle"><div class="adv open" id="adv"><button type="button" class="atab" id="atab"'
              f' aria-expanded="true" aria-label="Contents" title="Contents">{page.icon("panel", 16)}</button></div></div>')
    pages = "".join(reading(s, n, t, texts[s], graphs, marks) for s, n, t in every)
    pages += "".join(graphing(g, n, drawn[g], names, marks) for g, n in homes(chapters))
    front = (STYLE + TAB + toggle
             + page.blank("Pick a word.").replace('class="empty"', 'class="empty" id="blank"', 1))
    return {"rail": rail, "front": front, "pages": pages}


def heard() -> list:
    """The folder, its tree, its graphs and the review record's folder: a
    write into any moves the page."""
    folder = os.path.join(LIBRARY, GRAPHS)
    try:
        each = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".md")]
    except OSError:
        each = []
    return [LIBRARY, os.path.join(LIBRARY, MOC), folder, *each, page.tool("library-review").FOLDER]


def take(form: dict) -> str:
    """A review button's press: its item, marked as it says. A refusal
    comes back in one sentence."""
    ok, said = page.tool("library-review").marked(form.get("item", [""])[0], form.get("to", [""])[0])
    return "" if ok else said


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws the whole book. The page's own script, .claude/pages/scripts/library.js,
# opens, folds, finds and drags: lib/live.py.

def drawn() -> str:
    """The library page, its Find keeping no words past a reload but its own."""
    got = book(FIND.replace('<input id="q"', '<input id="q" data-draft="no"', 1))
    if got is None:
        return page.render("00-library", [("", live.watch() + page.blank(EMPTY))], refresh=0)
    body = (live.watch() + got["front"] + got["pages"] + f'<script src="{live.src("library.js")}"></script>\n')
    return page.render("00-library", [("", body)], rail=got["rail"], refresh=0)


def files() -> list:
    """The folder, its tree, each word's file, its graphs and the review
    record: a write into any moves the page. A word or graph added later is
    heard by its folder."""
    chapters = tree(read(os.path.join(LIBRARY, MOC)) or "")
    review = page.tool("library-review")
    return [*heard(), review.RECORD, *(os.path.join(LIBRARY, f"{slug}.md") for slug, _, _ in spots(chapters)),
            *(os.path.join(LIBRARY, GRAPHS, f"{slug}.md") for slug, _ in homes(chapters))]


# The page's contract, lib/live.py's: its address, its draw, its files, its take.
LIVE = live.Page(r"/library", drawn, files=files, take=take)
