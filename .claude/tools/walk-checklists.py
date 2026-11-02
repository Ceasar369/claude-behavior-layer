#!/usr/bin/env python3
"""walk-checklists.py — rebuilds every section's two checklists from its walk files, under the project's walks/.

  walk-checklists.py            rebuild every checklist under walks/
  walk-checklists.py FOLDER …   rebuild only the checklists under each folder
  walk-checklists.py --dry      say what would change, write nothing
  walk-checklists.py --missing  list each lettered detail with no title yet
  walk-checklists.py --mark CHECKLIST you|tester NAME=✅|⬜ …   write marks, row by row

A section holds two checklists. 0-checklist.md is the features walk: each
journey's flow, then the steps of its cover files, member.md and docs.md,
when it holds them. looks/looks-checklist.md is the looks walk: the steps
of each sweep in looks/, like french.md or widths.md, when it holds one.
A vendors.md holds no row: it is the analyzer's reference.

A checklist holds one row per check: each step, each lettered detail, and
each row of a sweep, a looks file or member.md: its table rows and its
labelled details. Its first column numbers every row 1, 2, 3, through
the checklist: a letter lives only in a check's name. The walk files
hold the how; the checklist holds the marks. So a row's marks are kept by
its name, and a new row starts not passed: ⬜, or — under a step that is
not mine. A row whose check is gone drops, unless it holds a ✅: then the
checklist stays as it was. A row that moved to the looks checklist, or a
vendor's, drops freely: its marks moved with it, or it holds none now.

A step's name is its heading up to its title, like "Sign up 1". A sweep
step has no title: its whole heading is its name, like "French · Sign up".
A lettered detail's title sits in its bold, "**a · Type the email**".

A cover or looks step whose head's italic line ends naming journey steps,
"*… · Sign up 1, Forgot 1*", is listed under the first journey holding
one. Any other step stays under its own file's heading.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import checklists  # noqa: E402
import registry  # noqa: E402

WALKS = os.path.join(registry.ROOT, "walks")
FEATURES = ("member.md", "docs.md")
# A looks folder's own files, never a sweep.
LOOKS_OWN = ("looks-checklist.md", "looks-MOC.md")
HEAD = "| # | Check | What it checks | You | Tester |\n|---|---|---|:-:|:-:|"

STEP = re.compile(r"^### (.+?)\s*$")
NUMBERED = re.compile(r"^(.+? \d+) · (.+)$")
LETTER = re.compile(r"^> - \*\*([a-z])(?: · (.+?))?\*\* · ")
LABEL = re.compile(r"^> - \*\*([A-Z][^*]*?)\*\* · ")
TABLE = re.compile(r"^\| \*\*(.+?)\*\* \|")
TAIL = re.compile(r"^\*.* · ([^·*]+)\*\s*$")
TITLED = re.compile(r"^# .+ · (.+?)\s*$")


def looks_of(section):
    """The sweeps of a section's looks/, by file name, in order."""
    folder = os.path.join(section, "looks")
    if not os.path.isdir(folder):
        return ()
    return tuple(sorted(f for f in os.listdir(folder) if f.endswith(".md") and f not in LOOKS_OWN))


def read_checklist(path):
    """checklists.read, each journey's rows kept by name: (what, you, tester)."""
    head, journeys = checklists.read(path)
    return head, [{**j, "rows": {r[1]: r[2:] for r in j["rows"]}} for j in journeys]


def checks(path, known):
    """Each check of one walk file, in order: (name, what, step's name)."""
    sweep = os.path.basename(path) == "member.md" or os.path.basename(os.path.dirname(path)) == "looks"
    out, step = [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        m = STEP.match(line)
        if m:
            heading = m.group(1)
            step = next((k for k in sorted(known, key=len, reverse=True)
                         if heading == k or heading.startswith(k + " · ")), None)
            if step is None:
                n = NUMBERED.match(heading)
                step = n.group(1) if n and not sweep else heading
            title = heading[len(step) + 3:] if heading != step else ""
            if not title and " · " in step:
                title = step.split(" · ", 1)[1]
            out.append((step, title, step))
            continue
        if step is None:
            continue
        m = LETTER.match(line)
        if m:
            name = step + m.group(1) if step[-1].isdigit() else f"{step} · {m.group(1)}"
            out.append((name, m.group(2) or "", step))
            continue
        if not sweep:
            continue
        m = LABEL.match(line) or TABLE.match(line)
        if m:
            out.append((f"{step} · {m.group(1)}", m.group(1), step))
    return out


def covers(path):
    """Each step of a phase file, by its heading, and the names its head's
    italic line ends on: the journey steps it covers, when they are ones."""
    out, heading = {}, None
    for line in open(path, encoding="utf-8").read().splitlines():
        m = STEP.match(line)
        if m:
            heading = m.group(1)
        elif heading and heading not in out and line.strip():
            t = TAIL.match(line)
            out[heading] = [s.strip() for s in t.group(1).split(",")] if t else []
    return out


def groups(path, journeys, phases, flow):
    """Each heading's rows: each journey its flow, when `flow`, then each
    phase step covering one of its steps, in the phases' order. A phase file
    the checklist never named joins at the end, from the checklist's folder."""
    folder = os.path.dirname(path)
    links = [j["link"] for j in journeys]
    for f in phases:
        link = os.path.relpath(os.path.join(folder, f), WALKS)[:-3]
        if os.path.isfile(os.path.join(folder, f)) and link not in links:
            t = TITLED.match(open(os.path.join(folder, f), encoding="utf-8").readline())
            journeys.append({"link": link, "name": t.group(1) if t else f[:-3].capitalize(), "rows": {}})
            links.append(link)
    old = {k: v for j in journeys for k, v in j["rows"].items()}
    rows = {j["link"]: checks(os.path.join(WALKS, j["link"] + ".md"), old) for j in journeys}
    phase = {j["link"] for j in journeys if os.path.basename(j["link"]) + ".md" in phases}
    home = {step: j["link"] for j in journeys if j["link"] not in phase for _, _, step in rows[j["link"]]}
    out = {link: ([] if link in phase or not flow else list(rows[link])) for link in links}
    for f in phases:
        link = next((p for p in phase if os.path.basename(p) + ".md" == f), None)
        if link is None:
            continue
        tags = covers(os.path.join(WALKS, link + ".md"))
        for row in rows[link]:
            named = next((v for k, v in tags.items() if k == row[2] or k.startswith(row[2] + " · ")), [])
            owners = [home[s] for s in named if s in home]
            to = min(owners, key=links.index) if named and len(owners) == len(named) else link
            out[to].append(row)
    kept = [(j, out[j["link"]]) for j in journeys if out[j["link"]] or (flow and j["link"] not in phase)]
    return kept, old


def journeys_of(features):
    """A features checklist's journey headings: none a looks or vendors file,
    none whose file is gone."""
    head, journeys = read_checklist(features)
    gone = {"vendors"} | {f[:-3] for f in looks_of(os.path.dirname(features))}
    keep = [j for j in journeys if os.path.basename(j["link"]) not in gone and "/looks/" not in j["link"]
            and os.path.isfile(os.path.join(WALKS, j["link"] + ".md"))]
    return head, journeys, keep


def lines_of(head, grouped, old):
    lines, added, missing = list(head), 0, []
    number = 0
    for j, rows in grouped:
        lines += [f"## [[{j['link']}|{j['name']}]]", "", HEAD]
        for name, what, step in rows:
            if name in old:
                kept_what, you, tester = old[name]
                what = kept_what or what
            else:
                added += 1
                you = "—" if old.get(step, ("", "", ""))[1] == "—" else "⬜"
                tester = "⬜"
            if not what:
                missing.append(name)
            number += 1
            lines.append(f"| {number} | {name} | {what} | {you} | {tester} |")
        lines.append("")
    text = "\n".join(lines).rstrip("\n") + "\n"
    return text.replace(" step, your mark", " check, your mark", 1), added, missing


def looks_head(features, looks):
    """A new looks checklist's head: its title, its Up, its purpose."""
    title = open(features, encoding="utf-8").readline().strip()
    section = title[2:].split(" · ")[0] if title.startswith("# ") else "Section"
    up = os.path.relpath(os.path.join(os.path.dirname(looks), "looks-MOC"), WALKS)
    return [f"# {section} · looks checklist", "", f"Up: [[{up}|Looks]]", "",
            "Every looks check, your mark and the tester's.", ""]


def build_looks(features, write):
    """The section's looks checklist, from looks/ and the section's journeys.
    A row new here keeps the marks the features checklist held for it."""
    looks = os.path.join(os.path.dirname(features), "looks", "looks-checklist.md")
    sweeps = looks_of(os.path.dirname(features))
    if not sweeps:
        return None
    _, every, keep = journeys_of(features)
    carried = {k: v for j in every for k, v in j["rows"].items()}
    if os.path.isfile(looks):
        head, own = read_checklist(looks)
        mine = {k: v for j in own for k, v in j["rows"].items()}
    else:
        head, mine = looks_head(features, looks), {}
    flows = [{"link": j["link"], "name": j["name"], "rows": {}} for j in keep
             if os.path.basename(j["link"]) not in ("live", "member", "docs")]
    grouped, _ = groups(looks, flows, sweeps, False)
    old = {**carried, **mine}
    text, added, missing = lines_of(head, grouped, old)
    names = {r[0] for _, rows in grouped for r in rows}
    dropped = [k for k in mine if k not in names and "✅" in mine[k][1:]]
    return finish(looks, text, write, added, dropped, missing)


def build(path, write, moved):
    """The features checklist. `moved` names the rows its looks checklist holds."""
    head, _, keep = journeys_of(path)
    grouped, old = groups(path, keep, FEATURES, True)
    _, every = read_checklist(path)
    held = {k: v for j in every for k, v in j["rows"].items()}
    text, added, missing = lines_of(head, grouped, {**held, **old})
    names = {r[0] for _, rows in grouped for r in rows}
    dropped = [k for k in held if k not in names and "✅" in held[k][1:]
               and k not in moved and not k.startswith("Vendors ")]
    return finish(path, text, write, added, dropped, missing)


def finish(path, text, write, added, dropped, missing):
    changed = not os.path.isfile(path) or text != open(path, encoding="utf-8").read()
    if write and changed and not dropped:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)
    return changed, added, dropped, missing


def mark(path, column, pairs):
    """Write each NAME=MARK into the column, You or Tester, of one checklist."""
    at = {"you": 3, "tester": 4}[column]
    want = dict(p.split("=", 1) for p in pairs)
    lines, done = open(path, encoding="utf-8").read().split("\n"), set()
    for i, line in enumerate(lines):
        cells = line.split(" | ")
        if line.startswith("| ") and len(cells) == 5 and cells[1] in want:
            cells[at] = want[cells[1]] + (" |" if at == 4 else "")
            lines[i] = " | ".join(cells)
            done.add(cells[1])
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    missed = [n for n in want if n not in done]
    print(f"{len(done)} marks written" + (f", not found: {', '.join(missed)}" if missed else "") + ".")


def say(rel, result, only_missing):
    if result is None:
        return
    changed, added, dropped, missing = result
    if only_missing:
        for name in missing:
            print(f"{rel}: {name}")
    elif dropped:
        print(f"{rel}: kept as it was, passed rows with no check behind them: {', '.join(dropped)}")
    elif changed:
        print(f"{rel}: {added} rows added" + (f", {len(missing)} with no title yet" if missing else ""))


def main():
    if sys.argv[1:2] == ["--mark"]:
        mark(os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4:])
        return
    dry = "--dry" in sys.argv
    only_missing = "--missing" in sys.argv
    write = not (dry or only_missing)
    roots = [os.path.abspath(a) for a in sys.argv[1:] if not a.startswith("--")] or [WALKS]
    paths = sorted(os.path.join(d, f) for root in roots for d, _, fs in os.walk(root)
                   for f in fs if f == "0-checklist.md")
    for path in paths:
        looks = build_looks(path, write)
        say(os.path.relpath(os.path.join(os.path.dirname(path), "looks", "looks-checklist.md"), WALKS),
            looks, only_missing)
        lp = os.path.join(os.path.dirname(path), "looks", "looks-checklist.md")
        moved = set()
        if os.path.isfile(lp):
            moved = {k for j in read_checklist(lp)[1] for k in j["rows"]}
        if looks and not write:
            heads = tuple(f[:-3].capitalize() for f in looks_of(os.path.dirname(path)))
            moved |= {k for j in read_checklist(path)[1] for k in j["rows"] if k.startswith(heads)}
        say(os.path.relpath(path, WALKS), build(path, write, moved), only_missing)


if __name__ == "__main__":
    main()
