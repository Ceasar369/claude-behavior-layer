#!/usr/bin/env python3
"""layer.py — a project's two roads to the public layer: update, and send.

A project is started from the layer's public repository, and keeps its
history. So an update is a merge of that repository's main branch, read
through the remote `layer`, which only fetches: its push address is
`no-push`, and the one push the public repository takes is the export's,
from the project that builds it. A fresh clone's `origin` becomes it.

  layer.py update        merge the public layer into this project's branch
  layer.py check         the checks an update ends on, alone
  layer.py send          each shared file this project changed since its last update
  layer.py send PATH ... those files' changes, written as one patch for the layer's builder

update refuses a project holding uncommitted changes, and the project
that builds the layer. It fetches, then merges. With nothing new it says
"Up to date". The public repository's own files, project.GITHUB, are put
back as this project held them: one it never held is removed, and a
clash on one is settled so. So is every file under a folder the project
names its own, project.json's "own". Any other clash stops the update with the
merge left open: each file is named, for my ruling. Settle each, then
`git commit`. A clean merge is committed here.

check then says, one line each: that lib/project.py prints the facts,
that the public repository's scripts/check.py passes on this project's
files, that the dashboard draws, each stand-in still unfilled, and
whether CLAUDE.md names the branch project.json names. It ends on the
one step that is mine: the mod's update, on each account.

send reads only what is committed. A shared file is one the public layer
holds, its own files aside. The patch lands in the builder's folder,
project.json's "home", under .claude/state/layer-inbox/, where its
layer-review rules it. With no home on this Mac, it lands in this
project's .claude/state/layer-outbox/, to be sent to the builder by hand.

Standard library only.
"""

import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import project  # noqa: E402

ROOT = project.ROOT
REMOTE = "layer"
REF = f"{REMOTE}/main"
NO_PUSH = "no-push"
STAND_IN = "> **Stand-in.**"
# Where a stand-in is a project's to fill. The guide only shows them.
FILLED = ["CLAUDE.md", "AGENTS.md", "knowledge/", ".claude/skills/", ".claude/app-skills/", ".claude/tools/"]
# What a clash is, by the two letters git status gives it.
CLASH = {"UU": "changed here and in the layer", "AA": "added here and in the layer",
         "UD": "changed here, deleted in the layer", "DU": "deleted here, changed in the layer",
         "AU": "added here, changed in the layer", "UA": "changed here, added in the layer",
         "DD": "deleted here and in the layer"}


class Refused(Exception):
    """One sentence saying why nothing happened."""


def git(*args: str, data: str = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", ROOT, *args], input=data, capture_output=True, text=True)


def out(*args: str) -> str:
    r = git(*args)
    return r.stdout.strip() if r.returncode == 0 else ""


def github(path: str) -> bool:
    """Whether an update leaves a path as this project holds it: one of
    the public repository's own files, or one under a folder the project
    names its own."""
    return any(path == p or (p.endswith("/") and path.startswith(p)) for p in project.GITHUB + project.OWN)


def remote() -> None:
    """The remote `layer` made to read the public repository, and to push
    nowhere. A project cloned from it holds it as `origin`: that remote is
    renamed, so `origin` is free for the project's own repository."""
    if not out("remote", "get-url", REMOTE) and project.LAYER in out("remote", "get-url", "origin"):
        git("remote", "rename", "origin", REMOTE)
    url = out("remote", "get-url", REMOTE)
    if not url:
        git("remote", "add", REMOTE, project.LAYER_URL)
    elif project.LAYER not in url:
        git("remote", "set-url", REMOTE, project.LAYER_URL)
    git("remote", "set-url", "--push", REMOTE, NO_PUSH)
    if project.LAYER not in out("remote", "get-url", REMOTE) or out("remote", "get-url", "--push", REMOTE) != NO_PUSH:
        raise Refused(f"Refused: the remote {REMOTE} could not be set to the public layer, fetch-only. Nothing was merged.")


def clashes() -> list:
    """Each file the open merge clashes on: (letters, path)."""
    return [(x[:2], x[3:]) for x in git("status", "--porcelain", "-z").stdout.split("\0") if x[:2] in CLASH]


def settle(before: set) -> list:
    """The public repository's own files put back as this project held them
    before the merge. Returns each one removed or put back."""
    now = {p for p in git("ls-files", "-z").stdout.split("\0") if p}
    now |= {p for _, p in clashes()}
    settled = []
    for path in sorted(p for p in now | before if github(p)):
        if path in before:
            if git("diff", "--quiet", "HEAD", "--", path).returncode or any(p == path for _, p in clashes()):
                git("checkout", "HEAD", "--", path)
                settled.append(path)
        else:
            git("rm", "-q", "-f", "--cached", "--", path)
            full = os.path.join(ROOT, path)
            if os.path.exists(full):
                os.remove(full)
            settled.append(path)
    for top in project.GITHUB:
        full = os.path.join(ROOT, top)
        if top.endswith("/") and os.path.isdir(full):
            for folder, _, _ in os.walk(full, topdown=False):
                if not os.listdir(folder):
                    os.rmdir(folder)
    return settled


def update() -> str:
    if os.path.exists(os.path.join(ROOT, ".claude", "tools", "export.py")):
        raise Refused("Refused: this project builds the layer. It sends through export.py, and takes no update.")
    if git("status", "--porcelain").stdout.strip():
        raise Refused("Refused: this project holds uncommitted changes. Commit them first, with /8-ship. Nothing was merged.")
    remote()
    r = git("fetch", REMOTE, "main")
    if r.returncode:
        raise Refused(f"Refused: the public layer could not be fetched. {r.stderr.strip()[-300:]} Nothing was merged.")
    sha = out("rev-parse", "--short=8", REF)
    if git("merge-base", "--is-ancestor", REF, "HEAD").returncode == 0:
        return f"Up to date: this project already holds the layer's {sha}.\n" + check()
    before = {p for p in git("ls-tree", "-r", "-z", "--name-only", "HEAD").stdout.split("\0") if p}
    shared = bool(out("merge-base", "HEAD", REF))
    git("merge", "--no-commit", "--no-ff", *([] if shared else ["--allow-unrelated-histories"]), REF)
    if not out("rev-parse", "-q", "--verify", "MERGE_HEAD"):
        raise Refused("Refused: git started no merge. Nothing was merged.")
    settled = settle(before)
    left = clashes()
    if left:
        raise Refused(f"Stopped: the layer's {sha} clashes with this project on {len(left)} file"
                      f"{'s' if len(left) > 1 else ''}. The merge is left open. Rule each one, "
                      "settle it, then commit.\n" + "\n".join(f"  {path}: {CLASH[code]}" for code, path in left))
    r = git("commit", "-q", "-F", "-", data=f"Update the layer to {sha}\n\n{project.TRAILER}\n")
    if r.returncode:
        raise Refused(f"Refused: the merge did not commit. {(r.stderr or r.stdout).strip()[-300:]}")
    said = f"Updated: this project now holds the layer's {sha}."
    if settled:
        said += f" {len(settled)} of the public repository's own files were kept out, or kept as they were."
    return said + "\n" + check()


def run(*command: str) -> tuple:
    r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def check() -> str:
    """Each check an update ends on, one line each, passed or failed."""
    lines = []

    def say(ok: bool, passed: str, failed: str) -> None:
        lines.append(("  pass  " + passed) if ok else ("  FAIL  " + failed))

    ok, last = run(sys.executable, os.path.join(".claude", "lib", "project.py"))
    say(ok, "lib/project.py prints this project's facts.", f"lib/project.py failed: {last[0]}")

    source = out("show", f"{REF}:scripts/check.py")
    if not source:
        say(False, "", f"scripts/check.py could not be read from {REF}. Run layer.py update first.")
    else:
        # The script finds the project from its own path, so it is told the
        # path it would have here.
        shim = ("import sys; src = sys.stdin.read(); "
                f"exec(compile(src, 'scripts/check.py', 'exec'), {{'__file__': {os.path.join(ROOT, 'scripts', 'check.py')!r}, "
                "'__name__': '__main__'})")
        r = subprocess.run([sys.executable, "-c", shim], input=source, cwd=ROOT, capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
        say(r.returncode == 0, "the public repository's scripts/check.py passes here.", f"scripts/check.py failed: {tail[0]}")

    ok, last = run(sys.executable, os.path.join(".claude", "tools", "sessions-dashboard.py"), "check")
    say(ok, "the dashboard draws.", f"the dashboard does not draw: {last[0]}")

    unfilled = []
    for path in (p for p in git("ls-files", "-z", "--", *FILLED).stdout.split("\0") if p and p != ".claude/tools/layer.py"):
        try:
            with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                unfilled += [f"{path}:{n}" for n, line in enumerate(f, 1) if line.startswith(STAND_IN)]
        except (OSError, UnicodeDecodeError):
            continue
    say(not unfilled, "no stand-in is left unfilled.",
        f"{len(unfilled)} stand-in{'s' if len(unfilled) > 1 else ''} left unfilled: " + ", ".join(unfilled))

    try:
        with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as f:
            named = f"`{project.BRANCH}` branch" in f.read()
    except OSError:
        named = False
    say(named, f"CLAUDE.md names the branch `{project.BRANCH}`, as project.json does.",
        f"CLAUDE.md never says \"`{project.BRANCH}` branch\", the branch project.json names.")

    lines.append("  mine  run `claude plugin update zero-turn@layer-mods` on each account.")
    return "\n".join(lines)


def base() -> str:
    """The layer commit this project last took."""
    if not out("rev-parse", "-q", "--verify", REF):
        raise Refused("Refused: this project has never fetched the layer. Run layer.py update first.")
    found = out("merge-base", "HEAD", REF)
    if not found:
        raise Refused("Refused: this project shares no history with the public layer. Run layer.py update first.")
    return found


def changed(since: str) -> list:
    """Each shared file this project's commits changed since SINCE: (letter, path)."""
    shared = {p for p in git("ls-tree", "-r", "-z", "--name-only", since).stdout.split("\0") if p and not github(p)}
    rows = [x for x in git("diff", "--name-status", "-z", "--no-renames", since, "HEAD").stdout.split("\0") if x]
    return [(code, path) for code, path in zip(rows[::2], rows[1::2]) if path in shared]


def send(paths: list) -> str:
    since = base()
    moved = changed(since)
    if not paths:
        if not moved:
            return f"No shared file changed since this project's last update, the layer's {since[:8]}."
        word = {"M": "changed", "D": "deleted"}
        return (f"{len(moved)} shared file{'s' if len(moved) > 1 else ''} changed since this project's last update, "
                f"the layer's {since[:8]}. Name the ones to send: layer.py send PATH ...\n"
                + "\n".join(f"  {word.get(code, 'changed'):8} {path}" for code, path in moved))
    stray = [p for p in paths if p not in {path for _, path in moved}]
    if stray:
        raise Refused(f"Refused: {', '.join(stray)} is no shared file this project changed. Nothing was written.")
    patch = git("diff", "--no-renames", since, "HEAD", "--", *paths).stdout
    home = project.HOME if project.HOME and os.path.isdir(os.path.join(project.HOME, ".claude")) else ""
    folder = os.path.join(home or ROOT, ".claude", "state", "layer-inbox" if home else "layer-outbox")
    os.makedirs(folder, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", project.NAME.lower()).strip("-") or "project"
    full = os.path.join(folder, f"{slug}-{time.strftime('%Y-%m-%d-%H%M%S')}.patch")
    with open(full, "w", encoding="utf-8") as f:
        f.write(f"# From {project.NAME}, against the layer's {since[:8]}.\n# {len(paths)} file"
                f"{'s' if len(paths) > 1 else ''}: {', '.join(paths)}\n" + patch)
    if home:
        return f"Sent: {full}. The builder's layer-review rules it."
    return f"Written: {full}. This Mac holds no builder's folder, so send that file to the layer's builder."


def main() -> None:
    verbs = {"update": update, "check": check, "send": lambda: send(sys.argv[2:])}
    verb = sys.argv[1] if sys.argv[1:] else ""
    if verb not in verbs or (verb != "send" and sys.argv[2:]):
        print("Say layer.py update, layer.py check, layer.py send or layer.py send PATH ... Nothing else.")
        sys.exit(1)
    try:
        print(verbs[verb]())
    except Refused as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
