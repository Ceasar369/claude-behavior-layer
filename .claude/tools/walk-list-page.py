#!/usr/bin/env python3
"""walk-list-page.py — a walk lead's Walk tab, and its walker's list.

Every walk the lead runs is one file in its folder: walk-list.md. Its
title names the walk. Each line under it names a whole journey, or one
check, borrowed from a section's checklist. A section ending /looks
borrows from its looks checklist:

    # The email sender

    - app/authentication · Sign up
    - app/settings · Team 2
    - app/settings · Team 3 alone
    - app/authentication/looks · French · Signup

The file holds names only. Each row, its words and its marks, is read
from that checklist, so a check lives in one place. A step brings its
lettered details, unless its line ends "alone": then its own row comes
alone. A journey brings every row under its heading. A name no
checklist holds shows as "not found", never hidden.

The tab draws one block per journey, as Obsidian draws a checklist: a
thin border round every cell, a sans-serif font, a bold header row, and a
table as wide as its content. Each block's heading is the journey, then
its file's path in dim. Under each, what the walker also reads.

The walker reads the same rows here, through `rows`, and nothing else:

  walk-list-page.py rows NN        the walk's rows and reading list, as text
  walk-list-page.py try FILE [--port 1114]   the tab, drawn from a fixture file alone

A fixture holds nn, tag and walk, the file's text.

1100 imports this file for render, key, tab and heard: the tab shows
while a session holds walk-list.md, and never waits on me.
"""

import argparse
import hashlib
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import checklists  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

FILE = "walk-list.md"
WALKS = os.path.join(registry.ROOT, "walks")
LINE = re.compile(r"^- ([\w/-]+) · (.+?)\s*$")


def own(section: str, check: str) -> str:
    """A row's own file, when its check's first word names one in its
    section: Member · … reads member.md, Docs 1 docs.md, French · … looks/french.md."""
    name = re.split(r"[ ·]", check, 1)[0].lower() + ".md"
    return name if os.path.isfile(os.path.join(WALKS, section, name)) else ""


def path(nn: str) -> str:
    return os.path.join(registry.folder(nn), FILE)


def listed(section: str) -> str:
    """The checklist a line's section names, from walks/."""
    return f"{section}/looks-checklist.md" if section.endswith("/looks") else f"{section}/0-checklist.md"


def checklist(section: str) -> list:
    """A section's checklist, as (journey link, journey name, rows), each
    row (#, check, what, you, tester)."""
    try:
        _, journeys = checklists.read(os.path.join(WALKS, listed(section)))
    except OSError:
        return []
    return [(j["link"], j["name"], [r for r in j["rows"] if r[0]]) for j in journeys]


def blocks(text: str) -> tuple:
    """The walk's name, and its blocks in its own order: one per journey
    in a row, each {journey, file, rows, reads}. A name no checklist holds
    is a row of its own, "not found"."""
    lines = text.splitlines()
    name = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "Walk")
    out = []
    for ln in lines:
        m = LINE.match(ln)
        if not m:
            continue
        section, check = m.groups()
        alone = check.endswith(" alone")
        if alone:
            check = check[: -len(" alone")]
        found = None
        for link, journey, rows in checklist(section):
            if journey == check:
                found = (link, journey, list(rows))
                break
            for i, r in enumerate(rows):
                if r[1] == check:
                    # A step's details follow it, each named for it:
                    # Sign up 2a, or French · Sign up · Phone.
                    detail = re.compile(re.escape(check) + r"(?:[a-z]| · .+)")
                    found = (link, journey, [r] + ([] if alone else list(itertools.takewhile(
                        lambda x: detail.fullmatch(x[1]), rows[i + 1:]))))
                    break
            if found:
                break
        file = f"walks/{listed(section)}"
        if not found:
            out.append({"journey": check, "file": file, "rows": [("", check, "not found", "", "")], "reads": []})
            continue
        link, journey, rows = found
        if out and out[-1]["file"] == file and out[-1]["journey"] == journey:
            out[-1]["rows"] += rows
        else:
            out.append({"journey": journey, "file": file, "rows": rows, "reads": [f"walks/{link}.md · Start, Prep"]})
        for r in rows:
            mine = own(section, r[1])
            extra = f"walks/{section}/{mine} · Start, Prep" if mine and f"{section}/{mine}" != f"{link}.md" else ""
            if extra and extra not in out[-1]["reads"]:
                out[-1]["reads"].append(extra)
    for b in out:
        if b["reads"]:
            area = b["file"].split("/")[1]
            b["reads"].append(f"walks/{area}/before-you-start.md · Logins")
    return name, out


def world(nn: str) -> dict:
    try:
        with open(path(nn)) as f:
            text = f.read()
    except OSError:
        text = ""
    return {"nn": nn, "tag": plans.tag(nn, plans.owners(registry.entries())), "walk": text}


def key(nn: str) -> str:
    """What the tab reloads on: the walk's file, and each checklist it
    borrows from."""
    d, words = world(nn), []
    words.append(d["walk"])
    for section in sorted({m.group(1) for ln in d["walk"].splitlines() if (m := LINE.match(ln))}):
        try:
            words.append(str(os.path.getmtime(os.path.join(WALKS, listed(section)))))
        except OSError:
            pass
    return hashlib.sha1("\0".join(words).encode()).hexdigest()[:12]


# ---- the tab ---------------------------------------------------------------------

# Obsidian's look, its default dark theme: the locked prototype custom-walk g3/v1. Page rule 37.
CSS = """<style>
  .ob { background:#1e1e1e; color:#dadada; padding:18px 22px; min-height:100%;
    font:14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif; }
  main:has(> .ob) { padding:0; }
  .ob-block { width:fit-content; max-width:100%; margin:0 0 22px; }
  .ob-block:last-child { margin-bottom:0; }
  .ob-h { display:flex; align-items:baseline; flex-wrap:wrap; gap:12px; margin:0 0 8px; text-transform:none;
    letter-spacing:0; font-size:16px; font-weight:700; color:#dadada; }
  .ob-link { color:#a78bfa; text-decoration:underline; }
  .ob-path { font:12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; font-weight:400; }
  .ob table { border-collapse:collapse; width:fit-content; max-width:100%; }
  .ob th, .ob td { border:1px solid #363636; padding:4px 10px; text-align:left; vertical-align:top; }
  .ob th { font-weight:600; }
  .ob td.ob-what { max-width:56ch; }
  .ob .ob-mark { text-align:center; }
  .ob-reads { margin:8px 0 0; }
</style>"""


def table(rows: list) -> str:
    e = page.esc
    head = ('<tr><th>#</th><th>Check</th><th>What it checks</th><th class="ob-mark">You</th>'
            '<th class="ob-mark">Tester</th></tr>')
    body = "".join(f'<tr><td>{e(n)}</td><td>{e(c)}</td><td class="ob-what">{e(w)}</td>'
                   f'<td class="ob-mark">{e(y)}</td><td class="ob-mark">{e(t)}</td></tr>' for n, c, w, y, t in rows)
    return f"<table><thead>{head}</thead><tbody>{body}</tbody></table>"


def draw(d: dict, tail: str = "") -> str:
    nn = d["nn"]
    name, got = blocks(d["walk"])
    if not got:
        return page.render(f"{nn}-walk", [("", page.blank("No walk") + tail)],
                           page.head("walk", d["tag"]), refresh=0)
    count = sum(len(b["rows"]) for b in got)
    e = page.esc
    body = "".join(
        f'<div class="ob-block"><h2 class="ob-h"><span class="ob-link">{e(b["journey"])}</span>'
        f'<span class="dim ob-path">{e(b["file"])}</span></h2>{table(b["rows"])}'
        + (f'<p class="dim ob-reads">Walker also reads: {e(" · ".join(b["reads"]))}</p>' if b["reads"] else "")
        + '</div>' for b in got)
    top = page.head("walk", d["tag"], f"{e(name)} · {count} check{'' if count == 1 else 's'}")
    return page.render(f"{nn}-walk", [("", CSS + f'<div class="ob">{body}</div>' + tail)], top, refresh=0)


def render(nn: str) -> str:
    return draw(world(nn), page.watch(key(nn)))


def tab(nn: str):
    """Session NN's tab, as (its line, its file), or None with no walk."""
    d = world(nn)
    if not d["walk"].strip():
        return None
    name, got = blocks(d["walk"])
    return f"{name} · {sum(len(b['rows']) for b in got)}", path(nn)


def heard() -> list:
    """Each session's walk-list.md, and each checklist it borrows from."""
    out = []
    for nn in registry.listing(registry.WORK):
        if re.fullmatch(r"\d{2}", nn) and os.path.isfile(path(nn)):
            out.append(path(nn))
            for ln in world(nn)["walk"].splitlines():
                if m := LINE.match(ln):
                    out.append(os.path.join(WALKS, listed(m.group(1))))
    return sorted(set(out))


def rows(text: str) -> str:
    """The walk as the walker reads it: each journey, its checks, and what
    it also reads."""
    name, got = blocks(text)
    out = [name]
    for b in got:
        out.append(f"\n{b['journey']} · {b['file']}")
        out += [f"  {n} · {c} · {w}" for n, c, w, _, _ in b["rows"]]
        if b["reads"]:
            out.append("  Also read: " + " · ".join(b["reads"]))
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("rows").add_argument("nn")
    tried = sub.add_parser("try")
    tried.add_argument("file")
    tried.add_argument("--port", type=int, default=1114)
    args = ap.parse_args()
    if args.verb == "rows":
        try:
            with open(path(args.nn)) as f:
                print(rows(f.read()))
        except OSError:
            sys.exit(f"Session {args.nn} holds no {FILE}.")
        return
    file = os.path.abspath(args.file)
    load, mark = serve.fixture(file)
    serve.run(f"walk-list-page-{args.port % 100:02d}", args.port, lambda: draw(load(), page.watch(mark())),
              keyof=mark, hears=lambda: [file])


if __name__ == "__main__":
    main()
