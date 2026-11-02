#!/usr/bin/env python3
"""walk-read.py — my reader's sections of one docs page, and what changed since my read.

A docs step lives in a section's docs.md, under walks/. Its italic line
opens with the page's address, then its source: a guide page under
code/app/docs/pages/, or the published spec for an API tab page.

  walk-read.py sections STEP [--since NN]   each section of the step's page, in order
  walk-read.py keep STEP NN                 keep the page's source as read, in NN's folder

STEP names the step as a walk list does: "app/training · Docs 1".

A guide page's sections are its top, from its title to its first "## "
heading, then each "## " heading to the next. An API tab page's sections
are its calls, one per operation of the tag its address names, in the
order the site draws them: path by path, GET before POST.

--since NN prints only the sections changed since NN kept the page: a
guide section by its lines, a call by its operation with every $ref
filled in. Nothing kept yet prints every section.

The first line names the page and counts its sections, or those changed.
Each section then prints one line: its place, its name, its address with
the anchor the site gives it, its source lines for a guide, where it
starts and ends, and each part to open.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHODS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]


def slug(words):
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", words.strip().lower()))


def find_step(step):
    folder, _, name = step.partition(" · ")
    docs = ROOT / "walks" / folder.strip() / "docs.md"
    if not name or not docs.is_file():
        sys.exit(f"No docs.md for {step!r}.")
    lines = docs.read_text().splitlines()
    for i, line in enumerate(lines):
        head = re.match(rf"### {re.escape(name.strip())} · (.+)", line)
        if head:
            italic = next((l for l in lines[i + 1:i + 4] if l.startswith("*")), "")
            parts = [p.strip() for p in italic.strip("*").split(" · ")]
            if len(parts) >= 2:
                return head.group(1).strip(), parts[0], ROOT / parts[1]
    sys.exit(f"No step {name.strip()!r} with an address and a source in {docs}.")


def kept_path(step, nn, source):
    return ROOT / ".claude" / "state" / "sessions" / nn / "read" / (slug(step.replace("/", " ")) + source.suffix)


def plain(line):
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line)
    return line.replace("`", "").replace("**", "").strip(" |>")


def last_words(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return sentences[-1] if sentences[-1] else text


def guide_sections(text):
    lines = text.splitlines()
    body = 0
    if lines and lines[0] == "---":
        body = lines.index("---", 1) + 1
    title = next((l[7:].strip() for l in lines[1:body] if l.startswith("title:")), "")
    heads, fenced = [], False
    for i in range(body, len(lines)):
        if lines[i].startswith("```"):
            fenced = not fenced
        elif not fenced and lines[i].startswith("## "):
            heads.append(i)
    starts = [body] + heads
    sections = []
    for k, start in enumerate(starts):
        end = (starts[k + 1] if k + 1 < len(starts) else len(lines)) - 1
        head = lines[start][3:].strip() if lines[start].startswith("## ") else title
        tabs, fenced, last = [], False, ""
        for line in lines[start:end + 1]:
            fence = re.match(r"^```(\S*)(?:.*title=\"([^\"]+)\")?", line)
            if fence:
                if not fenced:
                    tabs.append(fence.group(2) or fence.group(1) or "code")
                    last = "the end of its code sample"
                fenced = not fenced
            elif fenced or not line.strip() or line.lstrip().startswith("<"):
                continue
            elif line.lstrip().startswith("|"):
                if not re.match(r"^\s*\|[\s:|-]+\|\s*$", line):
                    last = f'the table row "{plain(line)}"'
            else:
                last = f'"{last_words(plain(line))}"'
        while end > start and not lines[end].strip():
            end -= 1
        open_parts = []
        if tabs:
            open_parts.append("its code sample's tabs: " + ", ".join(tabs))
        sections.append({
            "name": head, "anchor": slug(head) if lines[start].startswith("## ") else "",
            "lines": (start + 1, end + 1), "from": f'"{head}"', "to": last or f'"{head}"',
            "open": open_parts, "body": "\n".join(lines[start:end + 1]),
        })
    return sections


def resolve(node, spec, seen=()):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if ref and ref not in seen:
            target = spec
            for key in ref.lstrip("#/").split("/"):
                target = target.get(key, {})
            return resolve(target, spec, seen + (ref,))
        return {k: resolve(v, spec, seen) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve(v, spec, seen) for v in node]
    return node


def api_sections(text, address):
    spec = json.loads(text)
    page = address.rstrip("/").split("/")[-1]
    tag = next((t["name"] for t in spec.get("tags", []) if slug(t["name"]) == page), None)
    if tag is None:
        sys.exit(f"No tag in the spec draws {address}.")
    calls = []
    for path, item in spec.get("paths", {}).items():
        for method in METHODS:
            op = item.get(method)
            if isinstance(op, dict) and tag in op.get("tags", []):
                calls.append(op)
    sections = []
    for k, op in enumerate(calls):
        where = {p.get("in") for p in resolve(op.get("parameters", []), spec)}
        parts = [f"its {w} parameters" for w in ("path", "query") if w in where]
        if "requestBody" in op:
            parts.append("its request body")
        parts.append("its responses: " + ", ".join(op.get("responses", {})))
        parts.append("the samples on the right")
        after = calls[k + 1]["summary"] if k + 1 < len(calls) else None
        sections.append({
            "name": op["summary"], "anchor": slug(op["summary"]), "lines": None,
            "from": f'"{op["summary"]}"', "to": f'just above "{after}"' if after else "the page's end",
            "open": parts, "body": json.dumps(resolve(op, spec), sort_keys=True),
        })
    return sections


def page_sections(address, source, text):
    return api_sections(text, address) if source.suffix == ".json" else guide_sections(text)


def sections(step, since):
    title, address, source = find_step(step)
    now = page_sections(address, source, source.read_text())
    shown, count = now, f"{len(now)} sections."
    kept = kept_path(step, since, source) if since else None
    if kept and kept.is_file():
        before = {s["name"]: s["body"] for s in page_sections(address, source, kept.read_text())}
        shown = [s for s in now if before.get(s["name"]) != s["body"]]
        count = f"{len(shown) or 'no'} section{'' if len(shown) == 1 else 's'} changed since your read."
    print(f"{title}: {count}")
    for k, s in enumerate(shown, 1):
        where = f"{address}#{s['anchor']}" if s["anchor"] else address
        lines = f" · lines {s['lines'][0]}–{s['lines'][1]}" if s["lines"] else ""
        opens = " · open " + "; ".join(s["open"]) if s["open"] else ""
        print(f"{k}/{len(shown)} · {s['name']} · {where}{lines} · from {s['from']} to {s['to']}{opens}")


def keep(step, nn):
    _, _, source = find_step(step)
    kept = kept_path(step, nn, source)
    kept.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, kept)
    print(kept.relative_to(ROOT))


def main(args):
    if len(args) >= 2 and args[0] == "sections":
        since = args[args.index("--since") + 1] if "--since" in args else None
        sections(args[1], since)
    elif len(args) == 3 and args[0] == "keep":
        keep(args[1], args[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
