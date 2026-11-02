#!/usr/bin/env python3
"""cloud-step.py — one coding step in a cloud session: start it, wait for its branch, bring its work home.

  cloud-step.py start [--account 1] --branch cloud/<step> --brief FILE
  cloud-step.py wait --branch cloud/<step> [--minutes 60]
  cloud-step.py bring --branch cloud/<step> --part PATH [--part PATH ...]

start runs `claude --cloud` under the account's folder, in a terminal of its
own, since --cloud refuses one without. It runs the model a launch on that
account takes: lib/accounts.py's pinned(), else model(). The brief's file
is the session's task, and TAIL is added to it. It prints the session's
link and id.

wait asks GitHub for the branch every POLL seconds, and exits 0 once it is
there, 1 when the minutes run out.

bring reads the branch's last commit message, its report, and the files it
changed since the branch left this branch's GitHub copy. A file outside
every --part refuses it, and nothing changes. Otherwise git apply writes
the changes into the working tree, unshipped, all or nothing, and the
branch is deleted on GitHub. A clash leaves the tree and the branch as
they were. It exits 1 on any refusal.
"""

from __future__ import annotations

import argparse
import os
import pty
import re
import select
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402
import models  # noqa: E402

# The accounts I ruled may run cloud sessions. The first goes when start
# names none: a stand-in, until I rule which goes first.
CLOUD = ("1", "2")
# What ties a child claude to the session that runs this; the cloud
# session's starter must not carry them.
SESSION_VARS = ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_BRIDGE_SESSION_ID",
                "CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_MESSAGING_SOCKET",
                "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_PID")
LINK = re.compile(r"https://claude\.ai/code/(session_\w+)")
ANSI = re.compile(r"\x1b\[[0-9;?<>]*[a-zA-Z]|\x1b\][^\x07]*\x07")
POLL = 30
STARTING = 180
TAIL = """

When the step is done: commit only the files of your part, on the branch you are on. \
The commit message is your report: what you built, one line per file, and each check you ran \
with its result, or why it could not run here. Push it once, with `git push origin HEAD:{branch}`, \
then stop. \
You can reach nobody, so you ask nothing: a question you cannot settle from the files goes in \
the report instead."""


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def start(account: str, branch: str, brief: str) -> int:
    if account not in CLOUD or account not in accounts.ACCOUNTS:
        print(f"Account {account} may not run cloud sessions. Only {' or '.join(CLOUD)}.")
        return 1
    with open(brief) as f:
        task = f.read().strip() + TAIL.format(branch=branch)
    env = {k: v for k, v in os.environ.items() if k not in SESSION_VARS}
    if (folder := accounts.ACCOUNTS[account]["folder"]) != accounts.DEFAULT:
        env["CLAUDE_CONFIG_DIR"] = folder
    model = accounts.pinned(account) or accounts.model()
    master, slave = pty.openpty()
    # --model goes first: after --cloud, the flag is read as its description.
    proc = subprocess.Popen([models.binary() or "claude", "--model", model, "--cloud", task],
                            stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True)
    os.close(slave)
    seen, deadline = "", time.time() + STARTING
    while time.time() < deadline and not LINK.search(seen):
        ready, _, _ = select.select([master], [], [], 1)
        if ready:
            try:
                seen += ANSI.sub("", os.read(master, 4096).decode(errors="replace"))
            except OSError:
                break
        elif proc.poll() is not None:
            break
    if proc.poll() is None:
        proc.terminate()
    os.close(master)
    if not (m := LINK.search(seen)):
        print("No cloud session started. Its terminal said:")
        print(seen.strip()[-1500:])
        return 1
    print(f"Started on account {account}, on {model}: https://claude.ai/code/{m.group(1)}")
    print(f"Session id: {m.group(1)}")
    return 0


def wait(branch: str, minutes: int) -> int:
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        if (got := git("ls-remote", "--heads", "origin", branch).stdout.strip()):
            print(f"{branch} is on GitHub at {got.split()[0][:8]}.")
            return 0
        time.sleep(POLL)
    print(f"{branch} did not reach GitHub in {minutes} minutes.")
    return 1


def bring(branch: str, parts: list) -> int:
    here = git("branch", "--show-current").stdout.strip()
    for ref in (branch, here):
        if (r := git("fetch", "-q", "origin", ref)).returncode:
            print(f"Could not fetch {ref}: {r.stderr.strip()}")
            return 1
    tip = git("rev-parse", f"origin/{branch}").stdout.strip()
    base = git("merge-base", f"origin/{here}", tip).stdout.strip()
    files = git("diff", "--name-only", base, tip).stdout.split()
    print("Its report:")
    print(git("log", "-1", "--format=%B", tip).stdout.strip())
    print()
    outside = [f for f in files if not any(f.startswith(p.rstrip("/") + "/") or f == p for p in parts)]
    if outside:
        print("Refused, nothing changed. Files outside its part:")
        print("\n".join(outside))
        return 1
    patch = git("diff", "--binary", base, tip).stdout
    r = subprocess.run(["git", "apply"], input=patch, capture_output=True, text=True)
    if r.returncode:
        print("Refused, nothing changed. Its changes clash with the working tree:")
        print(r.stderr.strip())
        return 1
    git("push", "-q", "origin", "--delete", branch)
    print(f"Brought into {here}, unshipped. {branch} deleted on GitHub.")
    print("\n".join(files))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--account", default=CLOUD[0])
    s.add_argument("--branch", required=True)
    s.add_argument("--brief", required=True)
    w = sub.add_parser("wait")
    w.add_argument("--branch", required=True)
    w.add_argument("--minutes", type=int, default=60)
    b = sub.add_parser("bring")
    b.add_argument("--branch", required=True)
    b.add_argument("--part", action="append", required=True)
    a = p.parse_args()
    if a.cmd == "start":
        return start(a.account, a.branch, a.brief)
    if a.cmd == "wait":
        return wait(a.branch, a.minutes)
    return bring(a.branch, a.part)


if __name__ == "__main__":
    sys.exit(main())
