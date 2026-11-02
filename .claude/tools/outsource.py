#!/usr/bin/env python3
"""outsource.py — one brief, run on Codex or Grok, checked, and answered in JSON.

A session hands a task to an engine, Codex, ChatGPT's coding agent, or
Grok Build, xAI's, as a folder inside its own session folder:

  .claude/state/sessions/NN/outsource/<slug>/
    task.md      the brief. The engine reads it and cannot write it.
    out/         the engine's working folder, and the only place it can write.
    runs/        each run's events, reply and errors.
    state.json   the thread, the tries and the last answer.

  outsource.py new    NN slug            scaffold the folder and its brief
  outsource.py check  FOLDER             is the brief ready to run
  outsource.py run    FOLDER             the first run, then the checks
  outsource.py resume FOLDER  < words    the same thread again, then the checks

run and resume take minutes. The session that wrote the brief starts each
in the background itself, and reads its JSON once told it ended. One
session holds atOnce runs at most, outsource.json's: one more is refused.

The engine works inside out/. The checks run from the folder itself, so
they name its files out/<name>, and a file beside task.md is ../<name> to
it. The brief's paths start from the repository's root.

Every verb prints one JSON object, and exits 0. Its "status" is one of:

  ok        check: the brief is ready.
  refused   nothing ran. "problems" says why.
  passed    the engine answered done, and every check held.
  question  the engine stopped to ask. "question" holds it. resume answers it.
  failed    the engine answered done, but a check did not hold, or it broke.
            "problems" holds each. resume with no words sends them back.

Codex runs with my user config and rules ignored, in a workspace-write
sandbox rooted at out/. Grok runs on a copy of the folder outside the
repository, so no project file of Claude's or Cursor's loads, and its
user-level ones are switched off. Its wall is the custom profile WALL,
which refuses to start rather than run unwalled; a run whose wall Grok's
log does not show going up fails. It approves its own steps inside that
wall: a headless Grok skips any step awaiting approval, and still ends well.
Each runs with its engine's model and effort, the web the brief sets, and
no keyboard input. What it may touch, and what it must stop and ask, are
fixed here. The brief names its engine alone: each engine's model and
effort are outsource.json's, set on its card on 1100/system, as
lib/engines.py says. So are the caps.

A misuse prints one line on stderr and exits 1.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import engines  # noqa: E402
import registry  # noqa: E402

ROOT = registry.ROOT
SESSIONS = os.path.realpath(registry.WORK)
NAMES = engines.NAMES
GROK_HOME = os.path.expanduser("~/.grok")
WALL = "outsource"
GROK_OFF = {**{f"GROK_{v}_{s}_ENABLED": "0" for v in ("CLAUDE", "CURSOR")
               for s in ("AGENTS", "HOOKS", "MCPS", "RULES", "SKILLS")}, "GROK_MEMORY": "0"}

PARTS = ("Run settings", "Goal", "Read", "Write", "Hand back", "Checks", "Calls that stay mine")
KEYS = ("engine", "web")

TEMPLATE = """# Task: TODO: the task, in a few words

## Run settings

- engine: codex
- web: off

## Goal

TODO: what is built, and for whom, in a few lines.

## Read

- `TODO: a path` — why the engine reads it.

## Write

Only inside `out/`, your working folder. Nothing else is writable. This
brief's own folder is one level up: a file beside task.md is `../<name>`.

## Hand back

- `out/TODO: a file`

## Checks

- `TODO: a command` — what it proves. It runs from this brief's folder, so it names `out/<file>`. It reads the engine's files. It never runs them.

## Calls that stay mine

TODO: each choice the engine must stop and ask about, or "None."
"""

INSTRUCTIONS = """You were given one brief, a file named task.md. Do what it says and nothing else.
Read only the files its Read part names, and the brief itself. Do not read CLAUDE.md, AGENTS.md or any other project file unless the brief names it.
Write only in your current folder. A refused write is final: do not look for a way around it.
Never commit, push, install packages or change git.
If the brief does not answer something you need, or the choice is listed under 'Calls that stay mine', stop and reply with status question. Never guess.
Your last message must follow the reply schema: status done, or status question. List each file as a path relative to your current folder."""

GROK_REPLY = """The reply schema is one JSON object, alone in your last message, with no code fence: {"status": "done" or "question", "summary": a string, "question": a string, "files": [each a path relative to your current folder]}."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "summary", "question", "files"],
    "properties": {
        "status": {"type": "string", "enum": ["done", "question"]},
        "summary": {"type": "string"},
        "question": {"type": "string"},
        "files": {"type": "array", "items": {"type": "string"}},
    },
}


config = engines.config


def say(result: dict) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def resolve(folder: str) -> str:
    """The hand-off folder, whole. Refused outside the sessions' folders, so
    no engine ever gets write access to code."""
    path = os.path.realpath(folder if os.path.isabs(folder) else os.path.join(ROOT, folder))
    if not path.startswith(SESSIONS + os.sep):
        sys.exit(f"Refused: {path} is not under {SESSIONS}.")
    return path


def offered(engine: str) -> dict:
    """Model -> its efforts, for each model the engine lists. Grok lists no
    efforts: None. Codex is asked itself: its cache file is shared with
    Codex's desktop app, whose older list overwrites it. Empty when the
    engine will not answer."""
    if engine == "grok":
        try:
            got = subprocess.run(["grok", "models"], capture_output=True, text=True,
                                 timeout=60, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired):
            return {}
        return {m: None for m in re.findall(r"^\s+[*-] (\S+)", got.stdout, re.M)}
    try:
        got = subprocess.run(["codex", "debug", "models"], capture_output=True, text=True,
                             timeout=60, stdin=subprocess.DEVNULL)
        models = json.loads(got.stdout).get("models", [])
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}
    return {m["slug"]: [x.get("effort") if isinstance(x, dict) else x
                        for x in m.get("supported_reasoning_levels", [])]
            for m in models if m.get("visibility") == "list"}


def sections(text: str) -> dict:
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"## (.+?)\s*$", line)
        if m:
            name = m.group(1)
            out[name] = []
        elif name is not None:
            out[name].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def bullets(text: str) -> list:
    """The first backticked span of each bullet line."""
    out = []
    for line in text.splitlines():
        m = re.search(r"`([^`]+)`", line) if line.lstrip().startswith("-") else None
        if m:
            out.append(m.group(1).strip())
    return out


def settings(sec: dict, c: dict) -> tuple:
    """The engine and web the brief asks for, its engine's model and effort,
    and what is wrong with them."""
    problems, kv = [], {}
    for line in sec.get("Run settings", "").splitlines():
        m = re.match(r"-\s*([a-z]+):\s*(.*?)\s*$", line.strip())
        if not m:
            continue
        if m.group(1) in ("model", "effort", "preset"):
            problems.append(f"Run settings sets no {m.group(1)}: each engine's is set on its card on 1100/system.")
        elif m.group(1) not in KEYS:
            problems.append(f"Run settings holds an unknown key: {m.group(1)}.")
        elif m.group(2):
            kv[m.group(1)] = m.group(2)
    engine = kv.get("engine") or c["default"]
    if engine not in c["engines"]:
        problems.append(f"engine must be one of {', '.join(c['engines'])}, not {engine}.")
        engine = c["default"]
    model, effort = c["engines"][engine]["model"], c["engines"][engine].get("effort") or ""
    web = kv.get("web", "off")
    if web not in c["webs"]:
        problems.append(f"web must be one of {', '.join(c['webs'])}, not {web}.")
    elif engine == "grok" and web == "cached":
        problems.append("Grok has no cached web: off or live.")
    have = offered(engine)
    if have and model and model not in have:
        problems.append(f"Model {model}, set on 1100/system, is not offered on this account. It offers: {', '.join(have)}.")
    elif have and model and have[model] is not None and effort not in have[model]:
        problems.append(f"Effort {effort} is not offered for {model}. It offers: {', '.join(have[model])}.")
    return {"engine": engine, "model": model, "effort": effort, "web": c["webs"].get(web, "disabled")}, problems


def check_brief(folder: str, c: dict) -> tuple:
    """Everything wrong with the brief before a run spends anything."""
    try:
        with open(os.path.join(folder, "task.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return {}, ["task.md is missing."]
    problems = ["task.md still holds TODO: lines."] if "TODO:" in text else []
    sec = sections(text)
    problems += [f"The part '{p}' is missing or empty." for p in PARTS if not sec.get(p)]
    run, more = settings(sec, c)
    problems += more
    reads = bullets(sec.get("Read", ""))
    for p in reads:
        full = os.path.expanduser(p)
        full = full if os.path.isabs(full) else os.path.join(ROOT, full)
        if os.path.basename(full).startswith(".env"):
            problems.append(f"Read names a .env file: {p}")
        elif not os.path.exists(full):
            problems.append(f"Read names a path that does not exist: {p}")
    back = bullets(sec.get("Hand back", ""))
    if not back:
        problems.append("Hand back names no file.")
    for p in back:
        norm = os.path.normpath(p)
        if os.path.isabs(p) or norm == "out" or not norm.startswith("out" + os.sep):
            problems.append(f"Hand back must name a file inside out/: {p}")
    checks = bullets(sec.get("Checks", ""))
    if not checks:
        problems.append("Checks names no command.")
    run.update({"checks": checks, "back": [os.path.normpath(p) for p in back]})
    return run, problems


def load_state(folder: str) -> dict:
    try:
        with open(os.path.join(folder, "state.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"runs": 0, "failures": 0, "thread": "", "last": {}}


def save_state(folder: str, st: dict) -> None:
    path = os.path.join(folder, "state.json")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)
    os.replace(path + ".tmp", path)


def digest(folder: str) -> str:
    with open(os.path.join(folder, "task.md"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def events(path: str) -> dict:
    """What a run's event stream says: the thread, the usage, the commands, the error."""
    out = {"thread": "", "usage": {}, "commands": 0, "error": ""}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            kind, item = e.get("type"), e.get("item") or {}
            if kind == "thread.started":
                out["thread"] = e.get("thread_id", "")
            elif kind == "turn.completed":
                out["usage"] = e.get("usage", {})
            elif kind == "item.completed" and item.get("type") == "command_execution":
                out["commands"] += 1
            elif kind == "turn.failed":
                out["error"] = str((e.get("error") or {}).get("message") or kind)
    return out


def grok_events(path: str) -> dict:
    """What a Grok run's event stream says, and its reply: the JSON object
    its last message holds. A usage line closes each message."""
    out = {"thread": "", "usage": {}, "commands": 0, "error": "", "reply": None}
    said, last = "", ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            kind = e.get("type")
            if kind == "text":
                said += str(e.get("data", ""))
            elif kind == "usage":
                last, said = said or last, ""
            elif kind == "tool_call" and str(e.get("toolName", "")).startswith("run_terminal"):
                out["commands"] += 1
            elif kind == "error":
                out["error"] = str(e.get("message") or kind)
            elif kind == "end":
                out.update({"thread": e.get("sessionId", ""), "usage": e.get("usage", {})})
                if e.get("stopReason") != "end_turn" and not out["error"]:
                    out["error"] = f"it stopped on {e.get('stopReason')}"
    last = said or last
    try:
        reply = json.JSONDecoder().raw_decode(last[last.index("{"):])[0]
        out["reply"] = reply if isinstance(reply, dict) else None
    except ValueError:
        pass
    return out


def outside(folder: str) -> str:
    """Grok's copy of a hand-off folder, outside the repository."""
    session = os.path.basename(os.path.dirname(os.path.dirname(folder)))
    return os.path.join(tempfile.gettempdir(), "outsource", f"{session}-{os.path.basename(folder)}")


def mirror(src: str, dst: str, skip: tuple = ()) -> None:
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns(*skip))


def wall() -> None:
    """Writes the WALL profile into Grok's sandbox.toml, when missing. Grok
    write-protects that file inside the wall."""
    path = os.path.join(GROK_HOME, "sandbox.toml")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    if f"[profiles.{WALL}]" not in text:
        with open(path, "a", encoding="utf-8") as f:
            f.write(("\n" if text and not text.endswith("\n") else "") + f'[profiles.{WALL}]\nextends = "workspace"\n')


def walled(work: str, since: int) -> bool:
    """Whether Grok's sandbox log, past byte since, shows the wall enforced on work."""
    try:
        with open(os.path.join(GROK_HOME, "sessions", "sandbox-events.jsonl"), encoding="utf-8", errors="replace") as f:
            f.seek(since)
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if (e.get("event_type") == "ProfileApplied" and e.get("profile") == WALL and e.get("enforced") is True
                        and os.path.realpath(e.get("workspace", "")) == os.path.realpath(work)):
                    return True
    except OSError:
        pass
    return False


def invoke(folder: str, c: dict, run: dict, st: dict, prompt: str) -> dict:
    """One run, a new thread or the same one. Returns what it left behind."""
    n = st["runs"] + 1
    stem = os.path.join(folder, "runs", f"{n:02d}")
    grok, env = run["engine"] == "grok", None
    if grok:
        wall()
        copy = outside(folder)
        mirror(folder, copy, ("runs", "state.json"))
        work, env = os.path.join(copy, "out"), {**os.environ, **GROK_OFF}
        cmd = ["grok", "-p", prompt, "--output-format", "streaming-json", "--rules", INSTRUCTIONS + "\n" + GROK_REPLY,
               "-m", run["model"], "--sandbox", WALL, "--always-approve", "--no-subagents", "--no-auto-update"]
        cmd += (["--reasoning-effort", run["effort"]] if run["effort"] else []) + (
            ["--disable-web-search"] if run["web"] == "disabled" else []) + (["-r", st["thread"]] if st["thread"] else [])
        log = os.path.join(GROK_HOME, "sessions", "sandbox-events.jsonl")
        since = os.path.getsize(log) if os.path.exists(log) else 0
    else:
        work = os.path.join(folder, "out")
        schema = os.path.join(folder, "runs", "reply.schema.json")
        with open(schema, "w", encoding="utf-8") as f:
            json.dump(SCHEMA, f)
        cmd = ["codex", "exec"] + (["resume"] if st["thread"] else []) + [
            "--ignore-user-config", "--ignore-rules", "--json",
            "-m", run["model"],
            "-c", f'model_reasoning_effort="{run["effort"]}"',
            "-c", f'web_search="{run["web"]}"',
            "-c", 'shell_environment_policy.inherit="core"',
            "-c", "developer_instructions=" + json.dumps(INSTRUCTIONS),
            "--output-schema", schema, "-o", stem + "-reply.json"]
        cmd += (["-c", 'sandbox_mode="workspace-write"', st["thread"]] if st["thread"]
                else ["--sandbox", "workspace-write"]) + [prompt]
    began, timed_out = time.time(), False
    with open(stem + "-events.jsonl", "w") as out, open(stem + "-stderr.txt", "w") as err:
        proc = subprocess.Popen(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=err, start_new_session=True)
        try:
            proc.wait(timeout=c["timeoutSeconds"])
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            timed_out = True
    if grok:
        got = grok_events(stem + "-events.jsonl")
        mirror(work, os.path.join(folder, "out"))
        if not walled(work, since):
            got["error"] = "its wall did not show as up in its log"
    else:
        got = events(stem + "-events.jsonl")
        got["reply"] = None
        try:
            with open(stem + "-reply.json", encoding="utf-8") as f:
                got["reply"] = json.loads(f.read())
        except (OSError, ValueError):
            pass
    got.update({"n": n, "seconds": round(time.time() - began), "code": proc.returncode, "timed_out": timed_out})
    return got


def verify(folder: str, c: dict, run: dict, reply: dict, sha: str) -> tuple:
    """The files the engine left, and what is wrong with them or with its checks."""
    out, files, problems = os.path.join(folder, "out"), [], []
    for dirpath, dirs, names in os.walk(out, followlinks=False):
        for name in dirs + names:
            if os.path.islink(os.path.join(dirpath, name)):
                problems.append(f"{os.path.relpath(os.path.join(dirpath, name), folder)} is a symbolic link.")
        for name in names:
            p = os.path.join(dirpath, name)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            size = os.path.getsize(p)
            files.append({"path": os.path.relpath(p, folder), "bytes": size})
            if size > c["fileBytes"]:
                problems.append(f"{files[-1]['path']} is {size} bytes, over the {c['fileBytes']} cap.")
    if len(files) > c["fileCount"]:
        problems.append(f"out/ holds {len(files)} files, over the {c['fileCount']} cap.")
    have = {f["path"] for f in files}
    problems += [f"Hand back names {p}, which {NAMES[run['engine']]} did not write." for p in run["back"] if p not in have]
    for p in reply.get("files", []):
        rel = os.path.relpath(p, folder) if os.path.isabs(p) else os.path.normpath(p)
        if rel not in have and os.path.normpath(os.path.join("out", rel)) not in have:
            problems.append(f"The reply lists {p}, which is not in out/.")
    if digest(folder) != sha:
        problems.append("task.md changed during the run.")
    for cmd in run["checks"]:
        try:
            r = subprocess.run(["bash", "-c", cmd], cwd=folder, capture_output=True, text=True,
                               timeout=c["checkSeconds"], stdin=subprocess.DEVNULL)
            if r.returncode:
                tail = (r.stdout + r.stderr).strip()[-300:]
                problems.append(f"Check failed (exit {r.returncode}): {cmd}" + (f" — {tail}" if tail else ""))
        except subprocess.TimeoutExpired:
            problems.append(f"Check timed out: {cmd}")
    return files, problems


def going(folder: str) -> int:
    """How many runs go now in this session's hand-off folders: each lock
    whose process lives."""
    pieces, n = os.path.dirname(folder), 0
    for name in os.listdir(pieces):
        try:
            with open(os.path.join(pieces, name, "runs", ".lock")) as f:
                os.kill(int(f.read().split()[0]), 0)
            n += 1
        except (OSError, ValueError):
            pass
    return n


def lock(folder: str, engine: str) -> str:
    """One run per folder at a time. A lock left by a dead process is
    cleared. It holds `pid engine`, which 1100's System reads."""
    path = os.path.join(folder, "runs", ".lock")
    try:
        os.kill(int(open(path).read().split()[0]), 0)
        sys.exit("Refused: a run is already going in this folder.")
    except (OSError, ValueError):
        pass
    with open(path, "w") as f:
        f.write(f"{os.getpid()} {engine}")
    return path


def go(folder: str, words: str, resume: bool) -> dict:
    c, st = config(), load_state(folder)
    result = {"status": "refused", "folder": folder, "problems": []}
    run, problems = check_brief(folder, c)
    if problems:
        return {**result, "problems": problems}
    if resume != bool(st["thread"]):
        return {**result, "problems": ["resume needs a first run." if resume else "A run exists here: use resume."]}
    if st["failures"] >= c["maxFailures"] or st["runs"] >= c["maxRuns"]:
        return {**result, "problems": [f"{st['failures']} failed tries and {st['runs']} runs are used: the cap is reached."]}
    name = NAMES[run["engine"]]
    if run["engine"] == "codex":
        try:
            login = subprocess.run(["codex", "login", "status"], capture_output=True, text=True)
            signed_in = not login.returncode and "Logged in" in login.stdout + login.stderr
        except OSError:
            signed_in = False
        if not signed_in:
            return {**result, "problems": ["Codex is not installed or not signed in: npm install -g @openai/codex, then codex login."]}
    last = st["last"].get("status", "")
    if going(folder) >= c["atOnce"]:
        return {**result, "problems": [f"{c['atOnce']} runs already go in this session: start this one once one ends."]}
    if not resume:
        prompt = f"Do the task in {os.path.join(folder, 'task.md')}. Its paths start from {ROOT}."
    elif last == "question" and not words:
        return {**result, "problems": [f"{name} asked a question: resume needs the answer on stdin."]}
    elif last == "question":
        prompt = f"The owner answers your question:\n{words}\nContinue the task in {os.path.join(folder, 'task.md')} and reply again."
    elif last == "failed":
        prompt = "The checks did not hold. Fix only what they name, then reply again.\n" + "\n".join(st["last"]["problems"]) + (f"\n{words}" if words else "")
    elif words:
        prompt = f"The owner asks for a change:\n{words}\nReply again when it is done."
    else:
        return {**result, "problems": ["The last run passed: resume needs the change asked, on stdin."]}
    sha, path = digest(folder), lock(folder, run["engine"])
    try:
        got = invoke(folder, c, run, st, prompt)
        reply, files, problems = got["reply"] or {}, [], []
        why = ("timed out" if got["timed_out"] else f"exit {got['code']} {got['error']}".strip() if got["code"]
               else got["error"] or ("" if reply.get("status") in ("done", "question")
                                     else "its last message was not the reply shape"))
        if why:
            status, problems = "failed", [f"{name} stopped: {why}."]
        elif reply["status"] == "question":
            status = "question"
        else:
            files, problems = verify(folder, c, run, reply, sha)
            status = "failed" if problems else "passed"
        st.update({"runs": st["runs"] + 1, "failures": st["failures"] + (status == "failed"),
                   "thread": got["thread"] or st["thread"],
                   "last": {"status": status, "problems": problems, "question": reply.get("question", "")}})
        save_state(folder, st)
        return {"status": status, "folder": folder, "run": got["n"], "runs": st["runs"], "failures": st["failures"],
                "seconds": got["seconds"], "engine": run["engine"], "model": run["model"], "effort": run["effort"],
                "usage": got["usage"], "commands": got["commands"], "summary": reply.get("summary", ""),
                "question": reply.get("question", "") if status == "question" else "",
                "files": files, "problems": problems}
    finally:
        os.remove(path)


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="verb", required=True)
    n = sub.add_parser("new")
    n.add_argument("number")
    n.add_argument("slug")
    for verb in ("check", "run", "resume"):
        sub.add_parser(verb).add_argument("folder")
    a = p.parse_args()

    if a.verb == "new":
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
            sys.exit("Refused: the slug is lowercase words joined by hyphens.")
        folder = os.path.join(registry.folder(a.number), "outsource", a.slug)
        if os.path.exists(folder):
            sys.exit(f"Refused: {folder} exists.")
        for sub_dir in ("out", "runs"):
            os.makedirs(os.path.join(folder, sub_dir))
        with open(os.path.join(folder, "task.md"), "w", encoding="utf-8") as f:
            f.write(TEMPLATE)
        print(folder)
        return

    folder = resolve(a.folder)
    if not os.path.isfile(os.path.join(folder, "task.md")):
        sys.exit(f"Refused: {folder} holds no task.md.")
    for sub_dir in ("out", "runs"):
        os.makedirs(os.path.join(folder, sub_dir), exist_ok=True)
    if a.verb == "check":
        run, problems = check_brief(folder, config())
        say({"status": "refused", "problems": problems} if problems else
            {"status": "ok", "engine": run["engine"], "model": run["model"], "effort": run["effort"], "web": run["web"],
             "checks": len(run["checks"]), "hand_back": run["back"]})
    else:
        say(go(folder, sys.stdin.read().strip() if a.verb == "resume" else "", a.verb == "resume"))


if __name__ == "__main__":
    main()
