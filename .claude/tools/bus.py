#!/usr/bin/env python3
"""bus.py — the ask/answer bus, stored in the session folders themselves.

A question is one file. Its answer is a second file with the same number.
There is no separate bus root, no counter file, and no pairing state.

    sessions/0037-retry-policy/
      90-0003-backoff-cap-ask.md
      90-0003-backoff-cap-answer.md          <- unread
      90-0002-schema-choice-answer.read.md   <- pulled

State is derived from which files exist. Nothing is stored anywhere else,
so an interrupt can never strand a session in the wrong state.

At most one question is open per session, and that is structural: the /2-ask
skill ends the turn, and a stopped session cannot write a second question. The
script still tolerates several — it takes the highest — but never expects to.

Three writers, three disjoint files: the asker writes the ask, the answerer
writes the answer, the asker renames the answer. No two parties ever write
the same path, so there is no clobber to guard against.

Subcommands:
  ask     <slug> <bodyfile> [--session S]    append the next question
  answer  <session> <bodyfile> [--number N]  answer its open question
  inbox   [--session S]                      list unread answers, as paths
  read    <number> [--session S]             mark one answer pulled
  status  [--json]                           one row per session
  whoami                                     resolve this session's folder
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

# The repo root is three levels above this file (.claude/tools/bus.py).
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATHS_SH = os.path.join(ROOT, ".claude", "lib", "paths.sh")


def _resolve_paths():
    """Ask paths.sh where things live, so bash and Python never disagree.

    paths.sh is the single definition, and it honours paths.local.sh. Falling
    back to the defaults keeps this script working if bash is unavailable.
    """
    default = (os.path.join(ROOT, "sessions"), os.path.join(ROOT, ".claude", "state"))
    if not os.path.isfile(PATHS_SH):
        return default
    try:
        out = subprocess.run(
            ["bash", "-c", 'source "$1"; printf "%s\\n%s\\n" "$SESSIONS" "$STATE"', "_", PATHS_SH],
            capture_output=True, text=True, timeout=5,
        )
        lines = out.stdout.strip().split("\n")
        if out.returncode == 0 and len(lines) == 2 and all(lines):
            return lines[0], lines[1]
    except Exception:
        pass
    return default


SESSIONS, STATE = _resolve_paths()

PREFIX = "90-"
ASK_RE = re.compile(r"^90-(\d{4})-(.+)-ask\.md$")
ANS_RE = re.compile(r"^90-(\d{4})-(.+)-answer\.md$")
READ_RE = re.compile(r"^90-(\d{4})-(.+)-answer\.read\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def die(msg, code=1):
    print(f"bus.py: {msg}", file=sys.stderr)
    sys.exit(code)


def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def whoami(explicit=None):
    """This session's session-folder name."""
    if explicit:
        return explicit
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not sid:
        die("CLAUDE_CODE_SESSION_ID is unset — pass --session <folder>", 2)
    path = os.path.join(STATE, sid)
    if not os.path.isfile(path):
        die(f"no state file for this session ({sid}). Did /0-start run?", 2)
    with open(path) as fh:
        name = fh.read().strip()
    if not name:
        die(f"state file is empty: {path}", 2)
    return name


def soft_whoami():
    """Same lookup, but never fatal. Answering does not require a state file."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    path = os.path.join(STATE, sid) if sid else ""
    if path and os.path.isfile(path):
        with open(path) as fh:
            return fh.read().strip() or "unknown"
    return "unknown"


def session_dir(name):
    d = os.path.join(SESSIONS, name)
    if not os.path.isdir(d):
        die(f"no such session folder: {d}", 3)
    return d


def scan(d):
    """(asks, answers, reads) as {number: filename}."""
    asks, answers, reads = {}, {}, {}
    for fn in os.listdir(d):
        if not fn.startswith(PREFIX):
            continue
        for rx, bucket in ((READ_RE, reads), (ANS_RE, answers), (ASK_RE, asks)):
            m = rx.match(fn)
            if m:
                bucket[int(m.group(1))] = fn
                break
    return asks, answers, reads


def state_of(d):
    """open | answered | idle, plus the number it refers to.

    Open beats answered — a session that owes nothing still waits on nobody.
    """
    asks, answers, reads = scan(d)
    unanswered = sorted(n for n in asks if n not in answers and n not in reads)
    if unanswered:
        return "open", unanswered[-1], len(unanswered)
    unread = sorted(answers)
    if unread:
        return "answered", unread[-1], len(unread)
    return "idle", 0, 0


def subject(d, number):
    asks, answers, reads = scan(d)
    for bucket, rx in ((asks, ASK_RE), (answers, ANS_RE), (reads, READ_RE)):
        fn = bucket.get(number)
        if fn:
            return rx.match(fn).group(2)
    return ""


def write_atomic(path, header, bodyfile):
    if not os.path.isfile(bodyfile):
        die(f"no such body file: {bodyfile}", 4)
    with open(bodyfile) as fh:
        body = fh.read()
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(header + "\n" + body.rstrip("\n") + "\n")
    os.replace(tmp, path)


# ---- subcommands ---------------------------------------------------------

def cmd_ask(a):
    me = whoami(a.session)
    d = session_dir(me)
    if not SLUG_RE.match(a.slug):
        die(f"slug must be lowercase kebab: '{a.slug}'", 5)

    asks, answers, reads = scan(d)
    high = max(list(asks) + list(answers) + list(reads) + [0])
    n = high + 1
    name = f"{PREFIX}{n:04d}-{a.slug}-ask.md"
    path = os.path.join(d, name)
    write_atomic(path, f"<!-- ask {n:04d} | from {me} | {now()} -->", a.bodyfile)

    still_open = [x for x in asks if x not in answers and x not in reads]
    print(f"ASKED={path}")
    print(f"NUMBER={n:04d}")
    print(f"SESSION={me}")
    if still_open:
        others = ", ".join(f"{x:04d}" for x in sorted(still_open))
        print(f"WARN=already open: {others}", file=sys.stderr)


def cmd_answer(a):
    d = session_dir(a.session)
    asks, answers, reads = scan(d)

    if a.number:
        n = int(a.number)
        if n not in asks:
            die(f"{a.session} has no question {n:04d}", 6)
    else:
        unanswered = sorted(x for x in asks if x not in answers and x not in reads)
        if not unanswered:
            die(f"{a.session} has no open question", 6)
        n = unanswered[-1]

    if n in answers or n in reads:
        die(f"question {n:04d} is already answered", 7)

    slug = ASK_RE.match(asks[n]).group(2)
    me = a.me or soft_whoami()  # the answerer need not have booted via /0-start
    name = f"{PREFIX}{n:04d}-{slug}-answer.md"
    path = os.path.join(d, name)
    write_atomic(path, f"<!-- answer {n:04d} | from {me} | {now()} -->", a.bodyfile)

    print(f"ANSWERED={path}")
    print(f"NUMBER={n:04d}")
    print(f"ASK={os.path.join(d, asks[n])}")


def cmd_inbox(a):
    me = whoami(a.session)
    d = session_dir(me)
    _, answers, _ = scan(d)
    if not answers:
        print("INBOX=empty")
        return
    for n in sorted(answers):
        print(f"UNREAD={n:04d} {os.path.join(d, answers[n])}")


def cmd_read(a):
    me = whoami(a.session)
    d = session_dir(me)
    _, answers, _ = scan(d)
    n = int(a.number)
    if n not in answers:
        die(f"no unread answer {n:04d} in {me}", 8)
    src = os.path.join(d, answers[n])
    dst = src[: -len("-answer.md")] + "-answer.read.md"
    os.replace(src, dst)
    print(f"READ={dst}")


def cmd_status(a):
    rows = []
    if os.path.isdir(SESSIONS):
        for name in sorted(os.listdir(SESSIONS)):
            d = os.path.join(SESSIONS, name)
            if not os.path.isdir(d) or name.startswith("."):
                continue
            st, n, count = state_of(d)
            rows.append({
                "session": name,
                "state": st,
                "number": f"{n:04d}" if n else "",
                "subject": subject(d, n) if n else "",
                "count": count,
                "live": os.path.exists(os.path.join(d, ".session-live")),
            })
    if a.json:
        import json
        print(json.dumps(rows, indent=2))
        return
    action = {"open": "answer it", "answered": "run /4-inbox there", "idle": "idle"}
    for r in rows:
        if r["state"] == "idle" and not r["live"]:
            continue
        extra = f" ({r['count']} open)" if r["count"] > 1 else ""
        label = f"{r['number']}-{r['subject']}" if r["subject"] else "-"
        print(f"{r['session']}\t{r['state']}\t{label}\t{action[r['state']]}{extra}")


def cmd_whoami(a):
    print(whoami(a.session))


def main():
    p = argparse.ArgumentParser(prog="bus.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("ask")
    q.add_argument("slug")
    q.add_argument("bodyfile")
    q.add_argument("--session")
    q.set_defaults(fn=cmd_ask)

    w = sub.add_parser("answer")
    w.add_argument("session")
    w.add_argument("bodyfile")
    w.add_argument("--number")
    w.add_argument("--me")
    w.set_defaults(fn=cmd_answer)

    i = sub.add_parser("inbox")
    i.add_argument("--session")
    i.set_defaults(fn=cmd_inbox)

    r = sub.add_parser("read")
    r.add_argument("number")
    r.add_argument("--session")
    r.set_defaults(fn=cmd_read)

    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    m = sub.add_parser("whoami")
    m.add_argument("--session")
    m.set_defaults(fn=cmd_whoami)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
