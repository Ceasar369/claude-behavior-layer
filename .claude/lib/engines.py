#!/usr/bin/env python3
"""engines.py — the engine outsource hands work to, Codex, as 1100's System shows it.

Codex is ChatGPT's coding agent. It runs on my own plan with its company,
never on a Claude account.

Its model and effort sit in .claude/tools/outsource.json, under
"engines". I set them on its card on 1100/system. Every outsource run
takes them: a brief names its engine alone. "default" names the engine a
brief takes when it names none.

  {"engines": {"codex": {"model": "gpt-6.1-sol", "effort": "medium"}},
   "default": "codex", ...}

What its card shows comes from Codex's own files, so no draw waits on it:

- Its models and their efforts: its models_cache.json. Codex's desktop app
  shares that file and can leave an older list there. outsource.py asks
  Codex itself before each run.
- Its plan and window: Codex's newest session file holds its plan, its
  weekly window's percent and reset, written whenever Codex runs.
- The sessions running it: each run's lock, `pid engine`, in a session's
  outsource folder, while its process lives.
"""

import fcntl
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(ROOT, ".claude", "tools", "outsource.json")
SESSIONS = os.path.join(ROOT, ".claude", "state", "sessions")
# Saves take turns on this lock, kept out of the shipped tools folder.
LOCK = os.path.join(ROOT, ".claude", "state", "engines", "save.lock")
NAMES = {"codex": "Codex"}
CODEX = os.path.expanduser("~/.codex")
# The tail of a file read for its newest line: a session file runs to
# megabytes, and its last reading sits near its end.
TAIL = 2_000_000


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
    """Model -> (its efforts, its default effort), in Codex's own order. A
    model with no efforts has ([], ""). Empty when its cache cannot be read."""
    try:
        with open(os.path.join(CODEX, "models_cache.json")) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return {m["slug"]: ([x.get("effort") if isinstance(x, dict) else x
                         for x in m.get("supported_reasoning_levels") or []],
                        m.get("default_reasoning_level") or "")
            for m in got.get("models", []) if m.get("visibility") == "list"}


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
