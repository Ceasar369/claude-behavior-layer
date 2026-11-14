#!/usr/bin/env python3
"""explanation-page.py — a session's explanation documents, in its Explanation tab.

A session writes each document as one Markdown file in its own folder,
explanations/<name>.md, its name in kebab case. While it holds one, it
shows one Explanation tab, after its Transcript. The tab lists every
document, highest number first, each its number before its title, the
line under it, and when it was written and last updated. A document's
number and first written time are kept for good in numbers.json, beside
it, from the first time the page sees it, so a rewrite whole keeps both.
A press opens one, whole, with All documents above its numbered title,
back to the list, and its number of the whole and its times under its
line. A file gone leaves the list; the last gone closes the tab.

Above the list, two pills flip its order, and each device keeps which.
Every download is HTML, each document the file its Export saves, drawn in
a headless browser, its number first. Each card's button saves its one.
Download all, on this Mac, makes NN-name-documents, a plain folder holding
them all, in Downloads, and Download as zip beside it saves
NN-name-documents.zip, which opens into that folder. Elsewhere, as on a
phone, a browser cannot save a folder, so Download all alone shows, and
saves the zip.

A document draws on the whole glass: one reading column of 680px, about eighty characters, its
notes in the margin beside it, widening with the glass up to 600px, the
contents rail on the left. A picture, a chart or a table, spans the glass,
its title centered under it. A chart draws at its own size, never past
the glass, centered in its frame, and its frame's bottom edge drags down
to enlarge it. A chart too tall for the glass keeps a size its labels
read at, and the page scrolls past it. Narrower
than column and margin together, every note folds under what it serves.
The advisor's Advise tab, hung at the top left, hides the rail and shows
it again; each device keeps which. Back to all documents tops the rail.
Export, a second tab beside it, saves the document as one HTML file
anyone can open, its charts drawn in, with no script.

A file holds, in order:
  # its title, a takeaway
  one line under it: who it is for, and what it comes from
  ## each section, its heading a takeaway
     paragraphs, lists, ### a sub-heading, a copy block
     a list whose every item is "**Key** — value": key facts, as rows
     a ```mermaid fence, or a table: a picture; "Figure: …", the line
       under it, its title
     "> **Ruled** …", Assumed, Open or Example: a note, its chip its kind
     [^term] inside a line, with "[^term]: …" on a line of its own: a
       definition, beside the line that first names it
     {{…}} inside a line: an example, in the Example colour
The page numbers each section, 1, each sub-heading, 3.1, each chart,
Figure 1, and each table, Table 1, the two counted on their own. A number
typed before a heading or a title is dropped. A note after a paragraph or
a list sits in the margin beside it. A note after a picture sits under its
title. A note after anything else stays in the column. An Example note
wears the Example colour.

A chart is the shared one, .claude/pages/scripts/charts.js: its strip, its zoom, its
legend. Each box wears its kind's colour, :::green or another of KINDS, and
the chart's line "%% green: Paid outcome" names it in the legend. A box
of a document written before kinds wears its part's state, :::built,
:::ruled, :::assumed, :::open or :::outside. A note's chip wears its kind's
colour. A chart opens in the direction it was written in, and still flips.
A flowchart holding the line %% elk is placed by ELK, which keeps arrows
from crossing.

1100 imports this file for its LIVE pages, the list at /p/explanation/NN
and a document at /p/explanation/NN/NAME, and for tab, answer and heard.
Only check runs on its own.

  explanation-page.py check FILE   every chart drawn headless, every picture's title
                                   checked, every crossing arrow named; each failure printed
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import zipfile

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import serve  # noqa: E402

TP = page.tool("transcript-page")

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*([\w-]*)")
DEFINED = re.compile(r"^\[\^([\w-]+)\]:\s*(.*)$")
REF = re.compile(r"\[\^([\w-]+)\]")
FACT = re.compile(r"^\*\*([^*\n]+)\*\*\s+[—–]\s+([\s\S]+)$")
KIND = re.compile(r"^\*\*(Ruled|Assumed|Open|Example)[.:]?\*\*[.:]?\s*(?:[—–-]\s*)?")
CHIP = {"Ruled": "blue", "Assumed": "gold", "Open": "red", "Example": "example"}
# A part's state, as a box wears it: the clarify page's mark whose colour it
# takes, and the word its legend says. Documents written before kinds.
STATES = {"built": ("done", "Built"), "ruled": ("session", "Ruled"), "assumed": ("assumed", "Assumed"),
          "open": ("you", "Open"), "outside": ("today", "Outside")}
# A box's kind of question or outcome, as a colour: a box wears :::green, and
# the chart's line "%% green: Paid outcome" names it in its legend.
KINDS = {"blue": "#60a5fa", "violet": "#a78bfa", "cyan": "#22d3ee", "yellow": "#facc15",
         "green": "#4ade80", "pink": "#f472b6", "orange": "#fb923c", "red": "#f87171",
         "teal": "#2dd4bf", "lime": "#a3e635", "indigo": "#818cf8", "magenta": "#e879f9",
         "slate": "#94a3b8", "rose": "#fb7185", "white": "#f1f5f9"}
# An example inside a line, {{a $10,000 milestone, debited}}, wears the
# Example colour. A chart's source never reaches it.
EXAMPLE = re.compile(r"\{\{(.+?)\}\}")
HELD = re.compile("^\x00chart(\\d+)\x00$")
# A number typed before a heading, "3. " or "3.1 ", or a picture's title,
# "Figure 2 — ": the page numbers each itself, so it drops the typed one.
TYPED = re.compile(r"^(?:\d+(?:\.\d+)*\.\s+|\d+(?:\.\d+)+\s+|(?:Figure|Fig\.|Table)\s+\d+\s*[—–:-]\s*)")
# A table's title, held as a paragraph of its own until it joins its table.
TITLED = "\x00title\x00"
# A note after one of these joins it: beside a paragraph or a list, under a
# picture. A chart holds its place as a paragraph.
TEXT = ("p", "ul", "ol", "fig")


# ---- reading a document ----------------------------------------------------------

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "part"


def read(text: str) -> dict:
    """A document: its title, its lede, its definitions, its charts, each
    {src, caption}, and its sections, each {id, title, blocks}. A chart
    holds its place among its section's blocks as a paragraph of its own,
    \\x00chartN\\x00. A table with its title is one block, ("fig", (rows,
    caption)). Its blocks are the transcript page's."""
    doc = {"title": "", "lede": "", "notes": {}, "charts": [], "sections": []}
    lede, body = [], None
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if m := FENCE.match(line):
            mark = m.group(1)
            shut = re.compile(rf"^ {{0,3}}{re.escape(mark[0])}{{{len(mark)},}}\s*$")
            j = i + 1
            while j < len(lines) and not shut.match(lines[j]):
                j += 1
            if m.group(2).lower() == "mermaid":
                k = j + 1
                caption = (TYPED.sub("", lines[k][7:].strip())
                           if k < len(lines) and lines[k].startswith("Figure:") else "")
                doc["charts"].append({"src": "\n".join(lines[i + 1:j]), "caption": caption})
                if body is not None:
                    body += ["", f"\x00chart{len(doc['charts']) - 1}\x00", ""]
                i = k + (1 if caption else 0)
                continue
            if body is not None:
                body += lines[i:j + 1]
            i = j + 1
            continue
        if d := DEFINED.match(line):
            doc["notes"][d.group(1)] = d.group(2).strip()
        elif line.startswith("# ") and not doc["title"]:
            doc["title"] = line[2:].strip()
        elif line.startswith("## "):
            body = []
            doc["sections"].append({"title": TYPED.sub("", line[3:].strip()), "lines": body})
        elif body is None:
            if line.strip():
                lede.append(line.strip())
        elif line.startswith("Figure:") and body and body[-1].lstrip().startswith("|"):
            body += ["", TITLED + TYPED.sub("", line[7:].strip()), ""]
        else:
            body.append(line)
        i += 1
    doc["lede"] = " ".join(lede)
    seen = set()
    for s in doc["sections"]:
        sid = slug(s["title"])
        while sid in seen:
            sid += "-2"
        seen.add(sid)
        s["id"] = sid
        s["blocks"] = []
        for b in TP.blocks("\n".join(s.pop("lines")), False):
            if b[0] == "p" and b[1].startswith(TITLED) and s["blocks"] and s["blocks"][-1][0] == "table":
                s["blocks"][-1] = ("fig", (s["blocks"][-1][1], b[1][len(TITLED):]))
            elif b[0] != "hand":
                s["blocks"].append(b)
    return doc


# ---- drawing it ----------------------------------------------------------------

class Refs:
    """The definitions a document names, numbered in the order it first
    names them. Each block hands over the ones it names first."""

    def __init__(self, notes: dict):
        self.notes, self.order = notes, []

    def mark(self, html: str) -> tuple:
        """Its [^term] marks drawn as numbers, its {{examples}} in their
        colour, outside a chart's source, and the terms it named first."""
        fresh = []

        def sup(m) -> str:
            t = m.group(1)
            if t not in self.order:
                self.order.append(t)
                fresh.append(t)
            return f'<sup class="ed-ref">{self.order.index(t) + 1}</sup>'

        parts = re.split(r"(<pre[\s\S]*?</pre>)", REF.sub(sup, html))
        return "".join(p if i % 2 else EXAMPLE.sub(r'<span class="ed-ex">\1</span>', p)
                       for i, p in enumerate(parts)), fresh

    def note(self, t: str) -> str:
        body, _ = self.mark(TP.inline(self.notes.get(t, "")))
        return f'<div class="ed-def"><sup class="ed-ref">{self.order.index(t) + 1}</sup>{body}</div>'


def inner(blocks: list) -> str:
    return "".join(f"<p>{TP.inline(t)}</p>" if k == "p" else TP.block(k, t) for k, t in blocks)


def note(got: list) -> str:
    """A quote: a note, its chip its kind when its first words name one."""
    chip, ex = "", ""
    if got and got[0][0] == "p" and (m := KIND.match(got[0][1])):
        chip = f'<span class="ed-chip" style="--c:var(--{CHIP[m.group(1)]})">{m.group(1)}</span>'
        ex = " ed-ex" if m.group(1) == "Example" else ""
        got = [("p", got[0][1][m.end():])] + got[1:]
    return f'<div class="ed-note">{chip}<div class="{ex.strip()}">{inner(got)}</div></div>'


def facts(got) -> list:
    """A list whose every item is "**Key** — value", as its rows, or []."""
    rows = []
    for b in got:
        if len(b) != 1 or b[0][0] != "p" or not (m := FACT.match(b[0][1])):
            return []
        rows.append((m.group(1), m.group(2)))
    return rows


def figure(pic: str, caption: str, n: dict, word: str, kind: str = "") -> str:
    """A picture, its title centered under it, the two one block, numbered
    `word` N: charts and tables each counted on their own, in `n`."""
    n[word] += 1
    cap = (f'<figcaption><span class="ed-fn">{word} {n[word]}</span>{TP.inline(caption)}</figcaption>'
           if caption else "")
    return f'<figure class="ed-fig{kind}"><div class="ed-pic">{pic}{cap}</div></figure>'


def drawn(kind: str, got, doc: dict, n: dict) -> str:
    """One block, drawn."""
    if kind == "p" and (m := HELD.match(got)):
        chart = doc["charts"][int(m.group(1))]
        return figure(f'<pre class="wait">{page.esc(chart["src"])}</pre>', chart["caption"], n, "Figure")
    if kind == "fig":
        return figure(TP.block("table", got[0]), got[1], n, "Table", " ed-tab")
    if kind == "p":
        return f"<p>{TP.inline(got)}</p>"
    if kind == "h":
        n["sub"] += 1
        return f'<h3>{n["sec"]}.{n["sub"]} {TP.inline(TYPED.sub("", got))}</h3>'
    if kind == "quote":
        return note(got)
    if kind == "ul" and (rows := facts(got)):
        return '<dl class="ed-facts">' + "".join(f"<dt>{page.esc(k)}</dt><dd>{TP.inline(v)}</dd>"
                                                for k, v in rows) + "</dl>"
    return TP.block(kind, got)


def section(s: dict, doc: dict, refs: Refs, n: dict, lead: bool) -> str:
    """One section: its numbered heading, then its column. Each block's
    margin notes float level with it: the definitions it names first, and
    the notes after it. A figure carries its own, under its caption."""
    n["sec"], n["sub"] = n["sec"] + 1, 0
    pieces = []
    for kind, got in s["blocks"]:
        html, fresh = refs.mark(drawn(kind, got, doc, n))
        side = [refs.note(t) for t in fresh]
        if kind == "quote" and pieces and pieces[-1][0] in TEXT:
            pieces[-1][2].extend([html] + side)
            continue
        pieces.append((kind, html, side))
    out = []
    for kind, html, side in pieces:
        notes = "".join(f'<aside class="ed-mn">{x}</aside>' for x in side)
        out.append(html.replace("</figure>", notes + "</figure>") if html.startswith("<figure") else notes + html)
    title, _ = refs.mark(TP.inline(s["title"]))
    return (f'<section class="ed-sec{" lead" if lead else ""}" id="s-{s["id"]}"><h2>{n["sec"]}. {title}</h2>'
            f'<div class="ed-flow">{"".join(out)}</div></section>')


def back(home: str, words: str) -> str:
    """The way back to the list at `home`, saying `words`."""
    return (f'<button class="back" onclick="location.href=\'{home}\'">'
            f'{page.icon("back", 12)}{words}</button>')


def draw(doc: dict, name: str, home: str = "", at: tuple = (0, ""), file: str = "", watch: str = "") -> str:
    """The page, from a document, its title `name`. `home` is its list's
    address: its way back, above its title and atop its rail. `at` is its
    number, before its title, and its place and times, under its line:
    place()'s. Its tabs, hung top left: the rail's, then Export, which saves
    `file`.html, or `name`.html.

    On the contract, `watch` is live.watch()'s, and opens the body. The
    page's scripts are then scripted()'s, the same on the list. With no
    watch, as check draws it, the page carries its scripts inline."""
    if not doc["title"] and not doc["sections"]:
        return page.render(name, [("", watch + page.blank("This document is empty")
                                   + (scripted() if watch else ""))], refresh=0)
    refs, n = Refs(doc["notes"]), {"sec": 0, "sub": 0, "Figure": 0, "Table": 0}
    lede, _ = refs.mark(TP.inline(doc["lede"])) if doc["lede"] else ("", [])
    number = f'<span class="ed-n">{at[0]} ·</span>' if at[0] else ""
    head = (f'<header class="ed-title">{back(home, "All documents") if home else ""}'
            f'<h1>{number}{page.esc(doc["title"])}</h1>'
            + (f'<p class="ed-lede">{lede}</p>' if lede else "")
            + (f'<p class="ed-when">{page.esc(at[1])}</p>' if at[1] else "") + "</header>")
    body = "".join(section(s, doc, refs, n, i == 0) for i, s in enumerate(doc["sections"]))
    rail = ('<aside class="ed-rail">' + (back(home, "Back to all documents") if home else "")
            + "".join(f'<a href="#s-{s["id"]}" data-id="s-{s["id"]}">{i}. {page.esc(s["title"])}</a>'
                      for i, s in enumerate(doc["sections"], 1))
            + "</aside>\n") if len(doc["sections"]) >= 4 else ""
    tabs = ('<div class="ed-toggle">'
            + ('<div class="adv open" id="adv"><button type="button" class="atab" id="atab" aria-expanded="true"'
               f' aria-label="Contents" title="Contents">{page.icon("panel", 16)}</button></div>' if rail else "")
            + f'<button type="button" class="atab" id="export" data-file="{page.esc(file or name)}.html"'
            f' aria-label="Export" title="Export as one HTML file">{page.icon("download", 16)}</button></div>')
    scripts = (scripted() if watch else page.COPY + page.ZOOM
               + "<script>\n" + page.shared("charts.js") + "</script>\n" + MARKS + OWN)
    return page.render(name, [("", watch + CSS + tabs + f'<div id="items" class="ed">{head}{body}</div>' + scripts)],
                       rail, refresh=0)


# The states and the kinds, added to the clarify page's marks before any
# chart draws. A kind has no word of its own: its chart's line names it.
MARKS = ("<script>\nfor (const [k, [like, word]] of Object.entries(" + json.dumps(STATES) + ")) {\n"
         "  const s = STD[like], h = HUE[like]; delete STD[k]; STD[k] = s; WORD[k] = word; HUE[k] = h; }\n"
         "for (const [k, c] of Object.entries(" + json.dumps(KINDS) + ")) {\n"
         "  STD[k] = `fill:${c}26,stroke:${c},stroke-width:2px,color:#e6e8ee`; HUE[k] = c; }\n"
         "</script>\n")

# This page's own, after the clarify page's charts: the direction a chart
# was written in, the rail lighting the section in view, its tab, and
# Export.
OWN = r"""<script>
/* A chart shrinks to the glass's height only while its labels, 13px,
   stay 10px or more. A taller chart keeps its width's size, and the page
   scrolls past it.
   A flowchart opens in the direction it was written in: LR or RL left to
   right, any other top to bottom. Its strip still flips it. A chart waits
   as pre.wait, out of the charts' sight, until its direction is known. A
   page in a hidden frame has no width, so nothing draws until it shows. */
READ = 10 / 13;
async function directions() {
  if (!innerWidth) return;
  for (const el of [...document.querySelectorAll('pre.wait')]) {
    const src = el.textContent, way = src.match(/^\s*(?:flowchart|graph)\s+(TB|TD|BT|LR|RL)\b/m);
    if (flow(src) && !DIR[src]) DIR[src] = way && /LR|RL/.test(way[1]) ? 'LR' : 'TB';
    el.className = 'mmd';
  }
}
const drawAll = () => directions().then(charts);
drawAll();
addEventListener('resize', () => setTimeout(drawAll, 60));

/* The rail lights the last section whose top has passed the upper fifth
   of main. */
(() => {
  const main = document.querySelector('main'), links = [...document.querySelectorAll('.ed-rail a')];
  if (!main || !links.length) return;
  const light = () => {
    const top = main.getBoundingClientRect().top + main.clientHeight * 0.2;
    const secs = [...document.querySelectorAll('.ed-sec')];
    const at = secs.filter(s => s.getBoundingClientRect().top < top).pop() || secs[0];
    links.forEach(a => a.classList.toggle('on', a.dataset.id === at.id));
  };
  links.forEach(a => a.onclick = e => { e.preventDefault();
    document.getElementById(a.dataset.id).scrollIntoView({block: 'start'}); });
  main.addEventListener('scroll', light, {passive: true});
  light();
})();

/* The rail's tab, the advisor's: it hides the rail and shows it again, and
   each device keeps which. The document then has the glass, and its
   charts and margin measure again. */
(() => {
  const adv = document.getElementById('adv'), tab = document.getElementById('atab');
  if (!adv) return;
  const show = (open, moved) => {
    adv.classList.toggle('open', open);
    document.body.classList.toggle('rail-shut', !open);
    tab.setAttribute('aria-expanded', open);
    try { localStorage.setItem('explanation-rail', open ? '1' : ''); } catch (e) {}
    if (moved) dispatchEvent(new Event('resize'));
  };
  let was = '1';
  try { was = localStorage.getItem('explanation-rail') ?? '1'; } catch (e) {}
  show(!!was, false);
  tab.addEventListener('click', () => show(!adv.classList.contains('open'), true));
})();

/* Export saves the document as one HTML file, for anyone, in any browser.
   It keeps the page's look, and each chart as it draws now: a still
   picture as wide as it draws, never past the glass, its legend and its
   title, and no script. The way back, the copy buttons and each chart's
   strip stay behind. */
(() => {
  const b = document.getElementById('export');
  if (!b) return;
  const STILL = 'html, body { height:auto; overflow:visible; } body { display:block; } main { overflow:visible; }'
    + ' .ed-still svg { display:block; margin:0 auto; height:auto; }';
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  b.addEventListener('click', () => {
    const items = document.getElementById('items'), out = items.cloneNode(true);
    const live = [...items.querySelectorAll('.chart')];
    out.querySelectorAll('.chart').forEach((d, i) => {
      const c = live[i] && live[i].chart, svg = d.querySelector('.cz svg'), still = document.createElement('div');
      still.className = 'ed-still';
      if (svg && c) {
        svg.removeAttribute('height');
        svg.setAttribute('width', '100%');
        svg.style.cssText = `max-width:${Math.ceil(c.nat.w)}px; aspect-ratio:${c.nat.w} / ${c.nat.h};`;
        still.append(svg);
      }
      const lg = d.querySelector('.legend');
      if (lg) still.append(lg);
      d.replaceWith(still);
    });
    out.querySelectorAll('.back, .cp').forEach(e => e.remove());
    const css = [...document.querySelectorAll('style')].filter(s => !s.closest('svg'))
      .map(s => s.textContent).join('\n') + STILL;
    const h = out.querySelector('h1'), title = h && h.lastChild ? h.lastChild.textContent : '';
    const html = '<!doctype html>\n<meta charset="utf-8">\n'
      + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      + `<title>${esc(title)}</title>\n<style>${css}</style>\n<main>${out.outerHTML}</main>\n`;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
    a.download = b.dataset.file;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
  });
})();
</script>"""

# The prototype's look, on the shell's tokens. A chart wears the shell's
# own #items .chart rules.
CSS = "<style>\n" + page.shared("explanation.css") + "</style>\n"
# The way back to the list, above the title and atop the rail: the assistant
# page's back, borrowed. The rail's tab and Export's: the advisor's Advise
# tab, borrowed, the rail's white while its rail is open.
BACK = page.rules(page.tool("assistant-page").STYLE, ".back")
CSS += (BACK + BACK.replace("#items .back", "aside.ed-rail .back")
        + page.whole(page.tool("advisor-page").STYLE, r"\.atab"))

# The tab's list alone, so no document's Export carries it. Its order wears
# the launch page's pills, and its downloads the shell's .btn.
LIST = (page.rules(page.tool("launch-page").CSS, ".pills")
        + "<style>\n" + page.shared("explanation-list.css") + "</style>\n")


# ---- one session's documents, for 1100 -------------------------------------------

FOLDER = "explanations"


def folder(nn: str) -> str:
    return os.path.join(page.registry.folder(nn), FOLDER)


def born(path: str) -> float:
    """A file's birth. A rewrite whole is a new file, born anew."""
    st = os.stat(path)
    return getattr(st, "st_birthtime", st.st_mtime)


# Each document's number and first written time, kept beside them.
NUMBERS = "numbers.json"


def numbered(nn: str) -> list:
    """Session NN's documents, as (n, name, path, written), highest number
    first. The first time the page sees a document, numbers.json keeps its
    number, the next one, oldest first, and its file's birth as when it was
    written. A rewrite whole then keeps both. A name gone keeps its entry,
    so its number is never given again. A book that stands but cannot be
    read is never written over: its documents number afresh, unkept."""
    base = folder(nn)
    try:
        here = [(f[:-3], os.path.join(base, f)) for f in os.listdir(base) if re.fullmatch(r"[a-z0-9-]+\.md", f)]
    except OSError:
        return []
    book, whole = os.path.join(base, NUMBERS), True
    try:
        with open(book, encoding="utf-8") as f:
            kept = json.load(f)
        if not isinstance(kept, dict) or not all(isinstance(v, list) and len(v) == 2 for v in kept.values()):
            raise ValueError(NUMBERS)
    except OSError:
        kept = {}
    except (ValueError, UnicodeDecodeError):
        kept, whole = {}, False
    here = [(name, p) for name, p in here if os.path.isfile(p)]
    new = sorted((born(p), name) for name, p in here if name not in kept)
    if new and not whole:
        kept.update({name: [i + 1, made] for i, (made, name) in enumerate(new)})
    elif new:
        top = max((v[0] for v in kept.values()), default=0)
        kept.update({name: [top + i + 1, made] for i, (made, name) in enumerate(new)})
        fd, tmp = tempfile.mkstemp(dir=base)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(kept, f, indent=1)
        os.replace(tmp, book)
    return sorted(((kept[name][0], name, p, kept[name][1]) for name, p in here), reverse=True)


def files(nn: str) -> list:
    """Session NN's documents, as (name, path), highest number first."""
    return [(name, path) for _, name, path, _ in numbered(nn)]


def when(path: str, made: float = 0) -> str:
    """When a document was written, `made` or its file's birth, and last
    updated a minute or more after, on this Mac's clock: "Written Nov 3,
    14:41 · updated 14:49". An update on another day names its day."""
    try:
        made, moved = made or born(path), os.path.getmtime(path)
    except OSError:
        return ""
    w, u = time.localtime(made), time.localtime(moved)
    day = lambda t: f"{time.strftime('%b', t)} {t.tm_mday}, "
    out = f"Written {day(w)}{time.strftime('%H:%M', w)}"
    if moved - made >= 60:
        out += f" · updated {'' if u[:3] == w[:3] else day(u)}{time.strftime('%H:%M', u)}"
    return out


def place(nn: str, name: str) -> tuple:
    """A document's number, and the line under its lede: "Document 2 of 2 ·
    Written …", of the highest number there. (0, "") for none."""
    found = numbered(nn)
    for n, f, path, made in found:
        if f == name:
            return n, f"Document {n} of {found[0][0]} · {when(path, made)}"
    return 0, ""


def tab(nn: str):
    """Session NN's one Explanation tab, as (its line, its oldest document),
    or None with no document."""
    found = files(nn)
    return (page.count(len(found), "document"), found[-1][1]) if found else None


def text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def heading(path: str) -> tuple:
    """A document's title and lede, read from its head alone."""
    title, lede = "", []
    for line in text(path).split("\n"):
        if line.startswith("## "):
            break
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif title and line.strip():
            lede.append(line.strip())
    return title, REF.sub("", " ".join(lede))


def saved(n: int, name: str, top: int) -> str:
    """A document's name once saved, its number first, as wide as the
    session's highest, `top`, so a folder sorts them in order."""
    return f"{n:0{max(2, len(str(top)))}d}-{name}.html"


def bundle(nn: str) -> str:
    """The folder Download all saves: the session's name while it runs, else
    its title, its number first."""
    mine = page.registry.entries().get(nn) or {}
    rec = page.registry.claude_records().get(mine.get("session_id")) or {}
    title = rec.get("name") or mine.get("title", "")
    name = slug(title[3:] if title.startswith(f"{nn}-") else title) if title else ""
    return "-".join(([nn, name] if name else [nn]) + ["documents"])


def stills(nn: str, only: str = "") -> list:
    """Session NN's documents, or its one named `only`, each as its Export
    saves it, as (its saved name, its HTML), highest number first. One
    headless browser draws them all. [] when it cannot."""
    found = [d for d in numbered(nn) if not only or d[1] == only]
    if not found:
        return []
    top = numbered(nn)[0][0] if only else found[0][0]
    drawn = {name: draw(read(text(path)), f"{nn}-{name}", at=place(nn, name), file=name)
             for _, name, path, _ in found}
    try:
        ran = headless(STILLS, json.dumps(drawn), capture=True)
        got = json.loads(ran.stdout) if ran.returncode == 0 else {}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        got = {}
    return [(saved(n, name, top), got[name]) for n, name, _, _ in found if name in got]


def archive(nn: str):
    """Every document as HTML, in one folder, in one zip. None when none
    could be drawn."""
    found, out = stills(nn), io.BytesIO()
    if not found:
        return None
    inside = bundle(nn)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.mkdir(inside)
        for file, html in reversed(found):
            z.writestr(f"{inside}/{file}", html)
    return out.getvalue()


def unpacked(nn: str) -> str:
    """Every document as HTML, in one new folder in this Mac's Downloads.
    A folder of that name already there stays, and this one takes the next
    number, as a browser's download does. Says why when there is none."""
    if not numbered(nn):
        return "This session holds no document."
    found = stills(nn)
    if not found:
        return "The documents could not be drawn as HTML."
    base = os.path.join(os.path.expanduser("~/Downloads"), bundle(nn))
    target, i = base, 2
    while os.path.exists(target):
        target, i = f"{base} {i}", i + 1
    os.mkdir(target)
    for file, html in found:
        with open(os.path.join(target, file), "w", encoding="utf-8") as f:
            f.write(html)
    return ""


def listing(nn: str, watch: str) -> str:
    """The tab: its order and Download all, then every document, highest
    number first, each its number, title, lede and times. A press opens it.
    Its button saves it. `watch` is live.watch()'s."""
    found, home = numbered(nn), serve.address("explanation", nn)
    if not found:
        return page.render(f"{nn}-explanation", [("", watch + CSS + page.blank("No explanation document yet")
                                                  + scripted())], refresh=0)
    top = found[0][0]
    rows = "".join(f'<div class="ed-card"><a class="ed-row" href="{home}/{name}">'
                   f'<b><span class="ed-n">{n} ·</span>{page.esc(title or name)}</b>'
                   + (f'<span>{TP.inline(lede)}</span>' if lede else "")
                   + f'<em class="ed-when">{page.esc(when(path, made))}</em></a>'
                   f'<a class="btn ed-one" href="{home}/{name}.html" download="{saved(n, name, top)}"'
                   f' aria-label="Download {saved(n, name, top)}" title="Download {saved(n, name, top)}">'
                   f'{page.icon("download", 16)}</a></div>'
                   for n, name, path, made in found for title, lede in [heading(path)])
    # One document has no order to flip.
    order = (f'<span class="pills" id="order"><button type="button" data-o="up" aria-pressed="false">'
             f'{found[-1][0]} first</button><button type="button" class="on" data-o="down" aria-pressed="true">'
             f'{top} first</button></span>') if len(found) > 1 else "<span></span>"
    zipped = f'href="{home}/documents.zip" download="{bundle(nn)}.zip"'
    whole = (f'<span class="ed-saves"><a class="btn ed-zip" {zipped}>{page.icon("download", 16)}Download as zip</a>'
             f'<a class="btn go ed-all" {zipped}>{page.icon("download", 16)}<span>Download all</span></a></span>')
    body = (f'<div id="items" class="ed"><div class="ed-top">{order}{whole}</div>'
            f'<div class="ed-list" data-order="down">{rows}</div></div>')
    return page.render(f"{nn}-explanation", [("", watch + CSS + LIST + body + scripted())], refresh=0)


def answer(nn: str, rest: str):
    """A document as HTML at /NAME.html, or all of them at /documents.zip.
    A file gone, or one that could not be drawn, answers not found, and so
    does any other address: the list and each document are the contract's."""
    if rest == "/documents.zip":
        return (got, "application/zip") if (got := archive(nn)) else None
    if file := re.fullmatch(r"/([a-z0-9-]+)\.html", rest or ""):
        got = stills(nn, file.group(1))
        return (got[0][1].encode(), "text/html; charset=utf-8") if got else None
    return None


def heard() -> list:
    """What 1100 hears: each session's explanations folder, so a document
    new or gone moves its tabs, and each document, so a write redraws it."""
    reg, out = page.registry, []
    for nn in reg.listing(reg.WORK):
        if re.fullmatch(r"\d{2}", nn) and os.path.isdir(folder(nn)):
            out += [folder(nn)] + [path for _, path in files(nn)]
    return out


# ---- the page on the contract ----------------------------------------------------
#
# 1100 draws the list, as listing() does, and each document, as draw() does,
# and lib/live.py puts each change in place. Their own script is one file,
# .claude/pages/scripts/explanation.js, after the shell's copy and zoom and the
# shared charts. Both carry the same scripts, so a document gone, which
# shows the list at its address, reloads nothing. Its names differ from the
# contract's drawn() and files(): this file's own drawn() and files() are
# older, and other names call them.

def scripted() -> str:
    """The scripts of the list and of each document, on the contract: the
    states and the kinds a chart's box wears go beside them as data."""
    return (page.TABS + page.COPY + page.ZOOM + f'<script type="application/json" id="states">{json.dumps(STATES)}'
            f'</script>\n<script type="application/json" id="kinds">{json.dumps(KINDS)}</script>\n'
            f'<script src="{live.src("charts.js")}"></script>\n'
            f'<script src="{live.src("explanation.js")}"></script>\n')


def owner(nn: str) -> str:
    return (page.registry.entries().get(nn) or {}).get("session_id", "")


def pictured(nn: str, name: str = "") -> str:
    """Session NN's list, or its document NAME, on the contract. A document
    gone shows the list."""
    path = os.path.join(folder(nn), f"{name}.md")
    if not name or not os.path.isfile(path):
        return listing(nn, live.watch(owner(nn)))
    return draw(read(text(path)), f"{nn}-{name}", home=serve.address("explanation", nn), at=place(nn, name),
                file=name, watch=live.watch(owner(nn)))


def watched(nn: str, name: str = "") -> list:
    """Every file whose write can move the list or a document: the
    session's folder, where its explanations folder comes later, that
    folder, where a document comes or goes, its numbers, and each document,
    since the list shows each one's title and times."""
    base = folder(nn)
    return [page.registry.folder(nn), base, os.path.join(base, NUMBERS)] + [path for _, path in files(nn)]


# The pages' contract, lib/live.py's: the list, and each document.
LIVE = [live.Page(serve.address("explanation", r"(\d{2})"), pictured, files=watched),
        live.Page(serve.address("explanation", r"(\d{2})") + r"/([a-z0-9-]+)", pictured, files=watched)]


# ---- checked ---------------------------------------------------------------------

CHECK = r"""
const path = require('path');
const bin = process.env.PATH.split(':').find(p => p.includes('_npx') && p.endsWith(path.join('node_modules', '.bin')));
const {chromium} = require(path.join(bin, '..', 'playwright'));
const fs = require('fs');
const html = fs.readFileSync(0, 'utf8');
(async () => {
  const browser = await chromium.launch({headless: true});
  const p = await (await browser.newContext({viewport: {width: 1500, height: 950}})).newPage();
  const errors = [];
  p.on('pageerror', e => errors.push('The page: ' + e.message));
  await p.route('http://explanation.test/', r => r.fulfill({contentType: 'text/html', body: html}));
  await p.goto('http://explanation.test/');
  // A drawn chart's source stays in place, hidden.
  await p.waitForFunction(() => !document.querySelector('pre.mmd:not([hidden]), pre.wait'), null, {timeout: 30000}).catch(() => {});
  const out = await p.evaluate(async () => {
    const failed = [...document.querySelectorAll('#items pre.pre')].map(el => el.textContent);
    const left = document.querySelectorAll('pre.mmd:not([hidden]), pre.wait').length;
    const why = [];
    const m = typeof M !== 'undefined' && M ? await M : null;
    for (const src of failed) {
      let reason = 'it did not draw';
      try { if (m) await m.parse(src); } catch (e) { reason = String(e.message || e).split('\n').slice(0, 3).join(' '); }
      why.push({first: src.trim().split('\n')[0], reason});
    }
    return {charts: document.querySelectorAll('#items .chart').length, why, left};
  });
  // No arrow crosses another, or runs through a box it does not join. Each
  // arrow is walked every 5px; its first and last 12px, where arrows meet
  // at a box, never count. Its ends name it, by the boxes nearest them.
  const crossed = await p.evaluate(() => {
    const out = [], words = g => ([...g.querySelectorAll('text > tspan')].map(t => t.textContent.trim()).join(' ')
      || g.textContent).replace(/\s+/g, ' ').trim().slice(0, 40);
    const turn = (a, b, c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    const cut = (a, b, c, d) => turn(a, b, c) * turn(a, b, d) < 0 && turn(c, d, a) * turn(c, d, b) < 0;
    const within = (q, r) => q.x > r.left + 2 && q.x < r.right - 2 && q.y > r.top + 2 && q.y < r.bottom - 2;
    for (const svg of document.querySelectorAll('#items .chart svg')) {
      const fig = svg.closest('figure')?.querySelector('.ed-fn')?.textContent || 'A chart';
      const boxes = [...svg.querySelectorAll('g.node')].map(g => ({r: g.getBoundingClientRect(), t: words(g)}));
      const nearest = q => boxes.reduce((best, b) => {
        const d = Math.hypot(Math.max(b.r.left - q.x, 0, q.x - b.r.right), Math.max(b.r.top - q.y, 0, q.y - b.r.bottom));
        return d < best.d ? {d, b} : best; }, {d: Infinity, b: {t: '?'}}).b;
      const arrows = [...new Set(svg.querySelectorAll('path.flowchart-link, .edgePaths path'))].map(path => {
        const all = path.getTotalLength(), m = path.getScreenCTM();
        const at = s => { const q = path.getPointAtLength(s); return new DOMPoint(q.x, q.y).matrixTransform(m); };
        const pts = [];
        for (let s = 12; s <= all - 12; s += 5) pts.push(at(s));
        const ends = [at(0), at(all)].map(nearest);
        return {pts, ends, name: `"${ends[0].t}" → "${ends[1].t}"`};
      });
      arrows.forEach((a, i) => {
        for (const b of boxes) if (!a.ends.includes(b) && a.pts.some(q => within(q, b.r)))
          out.push(`${fig}: the arrow ${a.name} runs through "${b.t}".`);
        for (const z of arrows.slice(i + 1))
          if (a.pts.some((q, k) => k && z.pts.some((w, l) => l && cut(a.pts[k - 1], q, z.pts[l - 1], w))))
            out.push(`${fig}: the arrow ${a.name} crosses ${z.name}.`);
      });
    }
    return out;
  });
  // The first screen holds the title, the answer, and its picture's first
  // 120px, on a Mac's glass under 1100's tabs, the way back's line left
  // room. The answer's definitions may push the rest below.
  await p.setViewportSize({width: 1500, height: 900});
  await p.waitForTimeout(400);
  const below = await p.evaluate(() => {
    const fig = document.querySelector('.ed-sec.lead .ed-fig');
    return fig ? Math.round(fig.getBoundingClientRect().top + 120 - innerHeight) : 0;
  });
  // Nothing may cover anything, at a wide glass and a narrow one: every
  // block of the column, every margin note, every picture and its title.
  const covered = (below > 0 ? [`The answer's picture needs its first 120px on the first screen; ${below}px fall below it.`] : []).concat(crossed);
  for (const width of [2560, 1500, 1100, 800]) {
    await p.setViewportSize({width, height: 950});
    await p.waitForTimeout(400);
    covered.push(...await p.evaluate(width => {
      const els = [...document.querySelectorAll('.ed-flow > :not(.ed-fig), .ed-mn, .ed-pic > *')];
      const words = e => (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
      const out = [];
      for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
        if (els[i].contains(els[j]) || els[j].contains(els[i])) continue;
        const a = els[i].getBoundingClientRect(), b = els[j].getBoundingClientRect();
        const x = Math.min(a.right, b.right) - Math.max(a.left, b.left), y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (x > 2 && y > 2) out.push(`At ${width} wide, "${words(els[i])}" covers "${words(els[j])}".`);
      }
      return out;
    }, width));
  }
  await browser.close();
  for (const e of errors) console.log(e);
  for (const w of out.why) console.log(`A chart failed, the one opening "${w.first}": ${w.reason}`);
  if (out.left) console.log(`${out.left} chart(s) never drew: Mermaid did not load. Offline, every chart stays its source.`);
  for (const c of covered) console.log(c);
  console.log(`${out.charts} chart(s) drew.`);
  process.exit(errors.length || out.why.length || out.left || covered.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
"""

# Each document's page, {name: html} on stdin, drawn and pressed Export,
# its file printed back as {name: html}. A document with no Export, an
# empty one, is left out.
STILLS = r"""
const path = require('path');
const bin = process.env.PATH.split(':').find(p => p.includes('_npx') && p.endsWith(path.join('node_modules', '.bin')));
const {chromium} = require(path.join(bin, '..', 'playwright'));
const fs = require('fs');
const pages = JSON.parse(fs.readFileSync(0, 'utf8'));
(async () => {
  const browser = await chromium.launch({headless: true});
  const ctx = await browser.newContext({viewport: {width: 1500, height: 950}, acceptDownloads: true});
  const out = {};
  for (const [name, html] of Object.entries(pages)) {
    const p = await ctx.newPage();
    await p.route('http://explanation.test/', r => r.fulfill({contentType: 'text/html', body: html}));
    await p.goto('http://explanation.test/');
    if (await p.$('#export')) {
      await p.waitForFunction(() => !document.querySelector('pre.mmd:not([hidden]), pre.wait'), null, {timeout: 30000}).catch(() => {});
      await p.waitForTimeout(300);
      const [d] = await Promise.all([p.waitForEvent('download'), p.click('#export')]);
      out[name] = fs.readFileSync(await d.path(), 'utf8');
    }
    await p.close();
  }
  await browser.close();
  process.stdout.write(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def headless(script: str, given: str, capture: bool = False) -> subprocess.CompletedProcess:
    """Node runs `script` beside the project's own Playwright, `given` on
    its stdin, within two minutes."""
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           ".mcp.json")) as f:
        mcp = re.search(r"@playwright/mcp@[\w.-]+", f.read()).group()
    return subprocess.run(["npx", "-y", "-p", mcp, "-c", 'node -e "$EXPLANATION_SCRIPT"'], input=given, text=True,
                          capture_output=capture, timeout=120, env={**os.environ, "EXPLANATION_SCRIPT": script})


def lint(doc: dict) -> list:
    """What a document names but never defines, or defines but never names,
    each box mark that is no state, and each picture with no title."""
    whole = json.dumps(doc["sections"]) + doc["lede"] + json.dumps(doc["charts"])
    used = set(REF.findall(whole))
    out = [f"[^{t}] is named, but never defined." for t in sorted(used - set(doc["notes"]))]
    out += [f"[^{t}] is defined, but never named." for t in sorted(set(doc["notes"]) - used)]
    out += [f'The chart opening "{c["src"].strip().splitlines()[0] if c["src"].strip() else ""}" has no title.'
            " Its title is the line under its fence: Figure: …" for c in doc["charts"] if not c["caption"]]
    out += [f'The table headed "{" | ".join(got[0])}" has no title.'
            " Its title is the line under its last row: Figure: …"
            for s in doc["sections"] for kind, got in s["blocks"] if kind == "table"]
    marks = {m for c in doc["charts"] for m in re.findall(r":::(\w+)", c["src"])}
    out += [f"A chart wears :::{m}. A box wears its kind's colour: "
            + ", ".join(f":::{k}" for k in KINDS) + "." for m in sorted(marks - set(STATES) - set(KINDS))]
    if not doc["title"]:
        out.append("The document has no # title.")
    return out


def check(path: str) -> int:
    doc = read(text(path))
    problems = lint(doc)
    for p in problems:
        print(p, flush=True)
    ran = headless(CHECK, draw(doc, "check", at=(1, f"Document 1 of 1 · {when(path)}")))
    return 1 if problems or ran.returncode else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    checked = sub.add_parser("check")
    checked.add_argument("file")
    args = ap.parse_args()
    sys.exit(check(os.path.abspath(args.file)))


if __name__ == "__main__":
    main()
