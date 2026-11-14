#!/usr/bin/env python3
"""library-check.py — refuses a library page or graph that leans on this project.

A page says what one word means, so it stays true whatever the code does. A
graph, in graphs/, draws how several words meet, under the same test.

  library-check.py                        every page and graph, and that the MOC links each
  library-check.py library/tls.md         that page alone
  library-check.py library/graphs/x.md    that graph alone

Each fault prints one line, and it exits 1. No fault prints what was checked.
It catches the words and paths below. A value with neither is the tutor's to
catch.
"""

import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIBRARY = os.path.join(ROOT, "library")
GRAPHS = "graphs"
MOC = "library-MOC.md"
UP = "Up: [[library-MOC|Library]]"
SECTIONS = ("## What it is", "## What it is not")
PARTS = ("## The text", "## The graph")
SOURCE = "Source: https://"
GRAPH = re.compile(r"- Graph: \[\[([\w-]+)")
WORD = re.compile(r"\[\[([\w-]+)\]\]\s*$")
STEP = re.compile(r"\d+\. ")
SERIES = re.compile(r"Series: .+, \d+ of \d+")

OURS = re.compile(r"\b(?:[Ww]e|[Oo]urs?|us)\b")
NAME = re.compile(r"contract-?it", re.IGNORECASE)
PATH = re.compile(
    r"(?:^|[\s`(\"'])(?:code|knowledge|walks|library|\.claude)/"
    r"|\b[\w-]+\.(?:tsx?|py|sql|sh|json|md|txt|ya?ml|toml|conf|env)\b"
)


def common(lines: list, needed: tuple) -> list[str]:
    """The faults a page and a graph share: title, Up, sections, source,
    and words of this project."""
    found = []
    if not lines[0].startswith("# "):
        found.append("Line 1 is not a title.")
    if len(lines) < 3 or lines[2] != UP:
        found.append(f"Line 3 is not: {UP}")
    for section in needed:
        if section not in lines:
            found.append(f"No section: {section}")
    if not any(line.startswith(SOURCE) for line in lines):
        found.append(f"No line opening: {SOURCE}")
    for n, line in enumerate(lines, 1):
        if OURS.search(line) or NAME.search(line):
            found.append(f"Line {n} speaks of this project: {line}")
        if PATH.search(line):
            found.append(f"Line {n} names a file: {line}")
    return found


def faults(text: str) -> list[str]:
    """Every fault one page holds, each naming its line."""
    return common(text.split("\n"), SECTIONS)


def graph_faults(text: str, words: set) -> list[str]:
    """Every fault one graph holds: a page's, no box, a box linking a word
    the MOC lists nowhere, lanes not two to four, a lane with no box or a
    box outside every lane, and a source that is no address."""
    lines = text.split("\n")
    found = common(lines, PARTS)
    found += [f"Line {n} is a source that is no address: {line}" for n, line in enumerate(lines, 1)
              if line.startswith("Source:") and not line.startswith(SOURCE)]
    found += [f"Line {n} is a series not written as Series: <its name>, 1 of 3: {line}"
              for n, line in enumerate(lines, 1) if line.startswith("Series:") and not SERIES.fullmatch(line)]
    if PARTS[1] in lines:
        after = lines[lines.index(PARTS[1]) + 1:]
        if not any(STEP.match(line) for line in after):
            found.append("The graph has no box: no line opening 1. under ## The graph.")
        lanes, boxes, loose = [], 0, False
        for n, line in enumerate(after, lines.index(PARTS[1]) + 2):
            if (m := WORD.search(line)) and m.group(1) not in words:
                found.append(f"Line {n} links a word the MOC lists nowhere: {m.group(1)}")
            if line.startswith("### "):
                if lanes and not boxes:
                    found.append(f"The lane {lanes[-1]} has no box.")
                lanes.append(line[4:].strip())
                boxes = 0
            elif STEP.match(line):
                boxes += 1
                loose = loose or not lanes
        if lanes and not boxes:
            found.append(f"The lane {lanes[-1]} has no box.")
        if lanes and not 2 <= len(lanes) <= 4:
            found.append(f"The graph holds {len(lanes)} lanes. A graph holds one path, or two to four lanes.")
        if lanes and loose:
            found.append("A box sits outside every lane: under ## The graph, before its first ###.")
    return found


def unlisted(library: str) -> list[str]:
    """Every page the MOC links nowhere."""
    with open(os.path.join(library, MOC), encoding="utf-8") as f:
        moc = f.read()
    return [
        os.path.basename(page)
        for page in pages(library)
        if f"[[{os.path.basename(page)[:-3]}" not in moc
    ]


def homeless(library: str, moc: str) -> list[str]:
    """Every graph file the MOC lists nowhere, and every graph it lists
    with no file."""
    listed = {m.group(1) for line in moc.split("\n") if (m := GRAPH.match(line))}
    held = {os.path.basename(g)[:-3] for g in graphs(library)}
    return ([f"{GRAPHS}/{g}.md: the MOC lists it nowhere." for g in sorted(held - listed)]
            + [f"{g}: the MOC lists this graph, but {GRAPHS}/{g}.md is missing." for g in sorted(listed - held)])


def words(moc: str) -> set:
    """Every word the MOC lists."""
    return {m.group(1) for line in moc.split("\n") if (m := re.match(r"- \[\[([^|\]]+)", line))}


def misplaced(moc: str) -> list[str]:
    """Every link the tree holds wrongly: a word above a subchapter, a graph
    anywhere but a subchapter, or either twice."""
    found = []
    seen = set()
    depth = 0
    for line in moc.split("\n"):
        heading = re.match(r"(#{2,4}) ", line)
        if heading:
            depth = len(heading.group(1))
        if graph := GRAPH.match(line):
            name = graph.group(1)
            if depth != 3:
                found.append(f"{name}: a graph sits only under a subchapter.")
            if name in seen:
                found.append(f"{name}: the MOC lists it twice.")
            seen.add(name)
            continue
        link = re.match(r"- \[\[([^|\]]+)", line)
        if not link:
            continue
        name = link.group(1)
        if depth < 3:
            found.append(f"{name}: it sits above a subchapter.")
        if name in seen:
            found.append(f"{name}: the MOC links it twice.")
        seen.add(name)
    return found


def pages(library: str) -> list[str]:
    """Every page, the MOC aside."""
    return sorted(
        page
        for page in glob.glob(os.path.join(library, "*.md"))
        if os.path.basename(page) != MOC
    )


def graphs(library: str) -> list[str]:
    """Every graph."""
    return sorted(glob.glob(os.path.join(library, GRAPHS, "*.md")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("page", nargs="?")
    args = ap.parse_args()
    with open(os.path.join(LIBRARY, MOC), encoding="utf-8") as f:
        moc = f.read()
    chosen = [args.page] if args.page else pages(LIBRARY) + graphs(LIBRARY)
    said = []
    for page in chosen:
        with open(page, encoding="utf-8") as f:
            text = f.read()
        is_graph = os.path.basename(os.path.dirname(os.path.abspath(page))) == GRAPHS
        name = f"{GRAPHS}/{os.path.basename(page)}" if is_graph else os.path.basename(page)
        got = graph_faults(text, words(moc)) if is_graph else faults(text)
        said += [f"{name}: {fault}" for fault in got]
    if not args.page:
        said += [f"{name}: the MOC does not link it." for name in unlisted(LIBRARY)]
        said += homeless(LIBRARY, moc)
        said += misplaced(moc)
    if said:
        print("\n".join(said))
        sys.exit(1)
    print(f"Checked {len(chosen)} pages.")


if __name__ == "__main__":
    main()
