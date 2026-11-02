#!/usr/bin/env python3
"""8-ship.py — the hook behind /8-ship.

    /8-ship         commit everything
    /8-ship push    commit everything, then push

Everything means everything tracked or untracked, .claude/ included, minus
what .gitignore already refuses.

The project's branch is the only branch: the one .claude/project.json
names, work when it names none. Anything else is refused.

A project holding .claude/tools/export.py, the tool copying its layer out,
hears one line more after a commit: how many layer files changed since
the last export, as the export's changes() counts them, or the sentence
it refuses with. A project without it hears nothing more.

A push then waits, WAIT seconds at most, for GitHub's checks on the commit
it pushed, and names each step that failed, with its first error line.
Unread, a failed check went unseen for weeks. A project with no
.github/workflows/ waits for nothing.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import hook  # noqa: E402
import project  # noqa: E402

TRIGGER = "/8-ship"
BRANCH = project.BRANCH
TRAILER = project.TRAILER
WAIT, EVERY = 600, 10  # seconds: the longest wait for the checks, and each look
# A line naming why a step failed: a thrown error, a leak, an audit's count.
CAUSE = re.compile(r"^\s*Error\b|leaks found|vulnerabilities found|error TS\d+|ERR_")
TIMESTAMP = re.compile(r"^\S+Z ")
COLOUR = re.compile(r"\x1b\[[0-9;]*m")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", hook.ROOT, *args],
                          capture_output=True, text=True)


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], cwd=hook.ROOT,
                          capture_output=True, text=True)


def causes(log: str) -> list:
    """Each failed step's first line naming its error, in the run's order.

    The log names no step, so each "##[error]" line, which closes a failed
    step, cuts it: the cause is the first CAUSE line since the cut before.
    No such line → the last line before the cut."""
    found, block = [], []
    for raw in log.splitlines():
        text = COLOUR.sub("", TIMESTAMP.sub("", raw.split("\t", 2)[-1])).strip()
        if text.startswith("##[error]"):
            named = [x for x in block if CAUSE.search(x)]
            found.append(named[0] if named else (block[-1] if block else text))
            block = []
        elif text:
            block.append(text)
    return found


def checks(sha: str) -> str:
    """What GitHub's checks said of `sha`, or why they were not read."""
    if not os.path.isdir(os.path.join(hook.ROOT, ".github", "workflows")):
        return ""
    end = time.monotonic() + WAIT
    while True:
        try:
            r = gh("run", "list", "--commit", sha, "--limit", "1",
                   "--json", "databaseId,status,conclusion,url")
        except FileNotFoundError:
            return "GitHub's checks were not read: gh is not installed."
        if r.returncode != 0:
            return f"GitHub's checks were not read: {last_line(r)}"
        runs = json.loads(r.stdout or "[]")
        if runs and runs[0]["status"] == "completed":
            break
        if time.monotonic() + EVERY > end:
            if not runs:
                return f"GitHub started no check on it within {WAIT // 60} minutes."
            return f"GitHub's checks still run after {WAIT // 60} minutes: {runs[0]['url']}"
        time.sleep(EVERY)
    run = runs[0]
    if run["conclusion"] == "success":
        return "GitHub's checks successfully passed."
    jobs = json.loads(gh("run", "view", str(run["databaseId"]), "--json", "jobs").stdout or "{}")
    failed = [s["name"] for j in jobs.get("jobs", []) for s in j["steps"]
              if s["conclusion"] == "failure"]
    lines = causes(gh("run", "view", str(run["databaseId"]), "--log-failed").stdout)
    named = [f"- {step}: {lines[i]}" if i < len(lines) else f"- {step}"
             for i, step in enumerate(failed)]
    return "\n".join([f"GitHub's checks failed: {run['url']}", *named])


def message(lines: list) -> str:
    """A commit message built from the change itself.

    No model reads this diff, so the message states what moved rather than
    what it means. Areas are the top folder of each path, in the order git
    reports them.
    """
    areas, added, changed, deleted = [], 0, 0, 0
    for line in lines:
        code, path = line[:2], line[3:].strip().strip('"')
        top = path.split("/")[0]
        if top not in areas:
            areas.append(top)
        if "D" in code:
            deleted += 1
        elif "?" in code or "A" in code:
            added += 1
        else:
            changed += 1

    where = ", ".join(areas[:3]) + (" and more" if len(areas) > 3 else "")
    counts = [f"{n} {w}" for n, w in
              ((added, "added"), (changed, "changed"), (deleted, "deleted")) if n]
    return f"Ship {where}\n\n{', '.join(counts)}.\n\n{TRAILER}\n"


def count(n: int, thing: str) -> str:
    """`1 path`, `2 paths`. A sentence reads wrong with the plural always on."""
    return f"{n} {thing}" if n == 1 else f"{n} {thing}s"


def last_line(r: subprocess.CompletedProcess) -> str:
    text = (r.stderr or r.stdout).strip().splitlines()
    return text[-1] if text else "no reason given"


def since_export() -> str:
    """How many layer files changed since the last export, the export's
    refusal, or "" where nothing can count them."""
    path = os.path.join(hook.ROOT, ".claude", "tools", "export.py")
    if not os.path.isfile(path):
        return ""
    try:
        spec = importlib.util.spec_from_file_location("export", path)
        export = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(export)
        n = len(export.changes()[1])
    except Exception as e:
        return str(e) if type(e).__name__ == "Refused" else ""
    return f"{count(n, 'layer file')} changed since the last export." if n else \
        "No layer file changed since the last export."


def main() -> None:
    args = hook.words(TRIGGER)
    word = args.first()
    if word not in ("", "push"):
        hook.done("Say `/8-ship` or `/8-ship push`. Nothing else.")

    here = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if here != BRANCH:
        hook.done(f"On branch {here}, not {BRANCH}. Nothing was committed.")

    lines = [x for x in git("status", "--porcelain").stdout.splitlines() if x]
    dirty = len(lines)

    # A clean tree still has commits to push. Committing is what is optional
    # here, not pushing, so nothing returns early on an empty status.
    if lines:
        git("add", "-A")
        fd, path = tempfile.mkstemp(suffix=".gitmsg")
        with os.fdopen(fd, "w") as f:
            f.write(message(lines))
        r = git("commit", "-F", path)
        os.remove(path)
        if r.returncode != 0:
            hook.done(f"Commit refused: {last_line(r)}")

    if word != "push":
        if not dirty:
            hook.done("Nothing to ship.")
        layer = since_export()
        hook.done(f"{count(dirty, 'path')} successfully committed to {BRANCH}." + (f"\n{layer}" if layer else ""))

    ahead = [x for x in git("log", "--oneline", "@{u}..HEAD").stdout.splitlines() if x]
    if not ahead:
        hook.done("Nothing to push.")

    r = git("push")
    if r.returncode != 0:
        hook.done(f"The push was refused: {last_line(r)}")

    said = checks(git("rev-parse", "HEAD").stdout.strip())
    hook.done(f"{count(len(ahead), 'commit')} successfully pushed to {BRANCH}." + (f"\n{said}" if said else ""))


if __name__ == "__main__":
    main()
