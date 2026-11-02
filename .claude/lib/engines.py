#!/usr/bin/env python3
"""engines.py — the two engines outsource hands work to, Codex and Grok, as 1100's System shows them.

Codex is ChatGPT's coding agent. Grok Build is xAI's. Each runs on my own
plan with its company, never on a Claude account.

Each engine's model and effort sit in .claude/tools/outsource.json, under
"engines". I set them on its card on 1100/system. Every outsource run
takes them: a brief names its engine alone. "default" names the engine a
brief takes when it names none.

  {"engines": {"codex": {"model": "gpt-6.1-sol", "effort": "medium"},
               "grok": {"model": "grok-4.7", "effort": "medium"}},
   "default": "codex", ...}

What each card shows comes from the engine's own files, so no draw waits
on either:

- Its models and their efforts: its models_cache.json. Codex's desktop app
  shares that file and can leave an older list there. outsource.py asks
  Codex itself before each run.
- Its plan and window: Codex's newest session file holds its plan, its
  weekly window's percent and reset, written whenever Codex runs. Grok's
  log holds its tier, its percent used and its week's end, written only
  when its app opens. Grok's machine mode, `grok agent`, offers no call
  for them. So 1100 opens Grok's app unseen every ten minutes, from a
  folder of its own, sending nothing, and closes it once that line is
  written: asking(), on a thread of its own. Opening it costs no usage,
  and saves no Grok session.
- The sessions running it: each run's lock, `pid engine`, in a session's
  outsource folder, while its process lives.
"""

import calendar
import fcntl
import glob
import json
import os
import pty
import select
import subprocess
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(ROOT, ".claude", "tools", "outsource.json")
SESSIONS = os.path.join(ROOT, ".claude", "state", "sessions")
# Saves take turns on this lock, kept out of the shipped tools folder.
LOCK = os.path.join(ROOT, ".claude", "state", "engines", "save.lock")
NAMES = {"codex": "Codex", "grok": "Grok"}
CODEX = os.path.expanduser("~/.codex")
GROK = os.path.expanduser("~/.grok")
GROK_LOG = os.path.join(GROK, "logs", "unified.jsonl")
# The line Grok's app logs once it has its billing.
BILLED = "fetched credits config"
# The tail of a file read for its newest line: a session file runs to
# megabytes, and its last reading sits near its end.
TAIL = 2_000_000
# Seconds between two asks of Grok, and the longest one ask waits.
ASK_EVERY = 600
ASK_WAIT = 30
ASKED_FROM = os.path.join(tempfile.gettempdir(), "grok-usage-ask")


def config() -> dict:
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def save(engine: str, model: str = "", effort: str = "") -> None:
    """Sets an engine's model or effort, as its card's pills do. A model
    whose efforts lack the one kept takes the model's own default. A model
    or effort its engine does not offer sets nothing. Two saves at once
    take turns, so neither loses the other's."""
    offered = models(engine)
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        c = config()
        mine = c["engines"][engine]
        if model in offered:
            mine["model"] = model
            efforts, own = offered[model]
            if mine.get("effort") not in efforts:
                mine["effort"] = own
        if effort and effort in offered.get(mine["model"], ([], ""))[0]:
            mine["effort"] = effort
        with open(CONFIG + ".tmp", "w", encoding="utf-8") as f:
            f.write(json.dumps(c, indent=2) + "\n")
        os.replace(CONFIG + ".tmp", CONFIG)


def models(engine: str) -> dict:
    """Model -> (its efforts, its default effort), in the engine's own
    order. A model with no efforts has ([], ""). Empty when its cache
    cannot be read."""
    try:
        with open(os.path.join(CODEX if engine == "codex" else GROK, "models_cache.json")) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    if engine == "codex":
        return {m["slug"]: ([x.get("effort") if isinstance(x, dict) else x
                             for x in m.get("supported_reasoning_levels") or []],
                            m.get("default_reasoning_level") or "")
                for m in got.get("models", []) if m.get("visibility") == "list"}
    out = {}
    for name, m in (got.get("models") or {}).items():
        info = m.get("info") or {}
        if info.get("hidden"):
            continue
        efforts = info.get("reasoning_efforts") or [] if info.get("supports_reasoning_effort") else []
        values = [e["value"] for e in reversed(efforts)]
        out[name] = (values, next((e["value"] for e in efforts if e.get("default")), ""))
    return out


def running() -> dict:
    """Engine -> the sessions running it now, by number, each once."""
    out = {e: [] for e in NAMES}
    for lock in glob.glob(os.path.join(SESSIONS, "*", "outsource", "*", "runs", ".lock")):
        try:
            with open(lock) as f:
                pid, engine = (f.read().split() + ["codex"])[:2]
            os.kill(int(pid), 0)
        except (OSError, ValueError):
            continue
        nn = lock.split(os.sep)[-5]
        if engine in out and nn not in out[engine]:
            out[engine].append(nn)
    return {e: sorted(v) for e, v in out.items()}


def tail(path: str) -> list:
    """The file's last lines, newest first."""
    with open(path, "rb") as f:
        f.seek(max(0, os.path.getsize(path) - TAIL))
        return f.read().decode("utf-8", "replace").splitlines()[::-1]


def codex_use() -> dict:
    """Codex's plan and window from its newest session file: {"plan":
    "prolite", "pct": 12.0, "reset": 1793629053, "days": 7, "read":
    1793024000}. Empty when no session file holds one."""
    files = sorted(glob.glob(os.path.join(CODEX, "sessions", "*", "*", "*", "*.jsonl")), key=os.path.getmtime)
    for path in files[::-1][:5]:
        try:
            lines = tail(path)
        except OSError:
            continue
        for line in lines:
            if '"rate_limits"' not in line:
                continue
            try:
                got = json.loads(line)
            except ValueError:
                continue
            rl = (got.get("payload") or {}).get("rate_limits") or {}
            w = rl.get("primary") or {}
            if not w:
                continue
            return {"plan": rl.get("plan_type") or "", "pct": float(w.get("used_percent") or 0),
                    "reset": int(w.get("resets_at") or 0), "days": round((w.get("window_minutes") or 0) / 1440),
                    "read": int(os.path.getmtime(path))}
    return {}


def grok_use() -> dict:
    """Grok's tier, its percent used and its week's end, from its log's
    newest billing line: {"plan": "SuperGrok", "pct": 1.0, "reset":
    1793232000, "read": 1793024000}. A line with no percent, as Free's,
    leaves pct out. Empty when its log holds none."""
    try:
        lines = tail(GROK_LOG)
    except OSError:
        return {}
    for line in lines:
        if BILLED not in line:
            continue
        try:
            got = json.loads(line)
            ctx = got["ctx"]
            end = ctx["config"]["currentPeriod"]["end"]
            read = calendar.timegm(time.strptime(got["ts"][:19], "%Y-%m-%dT%H:%M:%S"))
            reset = calendar.timegm(time.strptime(end[:19], "%Y-%m-%dT%H:%M:%S"))
        except (ValueError, KeyError, TypeError):
            continue
        pct = ctx["config"].get("creditUsagePercent")
        return {"plan": ctx.get("subscriptionTier") or "", "reset": int(reset), "read": int(read),
                **({"pct": float(pct)} if isinstance(pct, (int, float)) else {})}
    return {}


def ask_grok() -> bool:
    """Open Grok's app unseen, in a terminal of its own, until it logs its
    billing, then close it. True once a new billing line is written."""
    try:
        before = os.path.getsize(GROK_LOG)
    except OSError:
        before = 0
    os.makedirs(ASKED_FROM, exist_ok=True)
    mine, its = pty.openpty()
    try:
        proc = subprocess.Popen(["grok", "--no-alt-screen"], cwd=ASKED_FROM, stdin=its, stdout=its, stderr=its,
                                start_new_session=True)
    except OSError:
        os.close(mine)
        os.close(its)
        return False
    os.close(its)
    got, end = False, time.time() + ASK_WAIT
    try:
        while time.time() < end and not got:
            # Its screen is drained, so it never blocks on a full terminal.
            if select.select([mine], [], [], 1)[0]:
                try:
                    os.read(mine, 65536)
                except OSError:
                    break
            try:
                with open(GROK_LOG, "rb") as f:
                    f.seek(before)
                    got = BILLED.encode() in f.read()
            except OSError:
                pass
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        os.close(mine)
    return got


def asking() -> None:
    """1100's asking of Grok, on a thread of its own, for as long as 1100
    runs: at once on start, then every ten minutes. A billing line Grok's
    own app wrote within those ten minutes is fresh already, and Grok is
    not asked. With no outsource here, or no Grok, it never asks."""
    while True:
        try:
            config()
            fresh = time.time() - grok_use().get("read", 0) < ASK_EVERY
            if not fresh:
                ask_grok()
        except Exception:
            pass
        time.sleep(ASK_EVERY)
