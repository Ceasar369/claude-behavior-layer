#!/usr/bin/env python3
"""test-chat.py — one fresh app chat for a test, on stand-ins only.

A test never reaches a real session. This chat holds no tool of Claude
Code's own, so it cannot message, list or type into any session on this
Mac. Its only tools are the app door's, run as `app-door.py trial`: the
made-up sessions of lib/trial.py, 05, 10, 11 and 12, with every press,
draft and stop kept in a folder, never done. The app's own tools are
stand-ins there too, each call kept: those my rules allow, and those
they took away, so a call to one shows. It runs
outside the project, under my app's own Instructions, like my app chat.

  test-chat.py "<my words>" ["<my next words>" ...]
                                each a turn of mine, in one chat; prints each reply,
                                then each act it made and the draft it left
  ... --sent NN "<my message>" ...
                                between two turns, I send stand-in NN my message
                                myself, unsaid, and it answers "On it."
  TRIAL_TAP=Feedback ...        what my tap on AskUserQuestion answers, Agree by default
  TRIAL_WAVE=items.json ...     stand-in 05's wave, as a JSON list of items, in place of the made-up one

hooks/guard.py refuses any other headless `claude` a session starts.
"""

import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOOR = os.path.join(HERE, "app-door.py")
INSTRUCTIONS = os.path.join(ROOT, ".claude", "app-settings", "set-b-instructions.txt")
# Claude Code's own tools that reach another session, refused on top of --tools "".
REACHING = ["SendMessage", "ListAgents", "Agent", "Bash"]


def steps(args: list) -> list:
    """My turns and my unsaid sends, in order: ("say", words) or ("sent", NN, words)."""
    out, i = [], 0
    while i < len(args):
        if args[i] == "--sent" and i + 2 < len(args):
            out.append(("sent", f"{int(args[i + 1]):02d}", args[i + 2]))
            i += 3
        else:
            out.append(("say", args[i]))
            i += 1
    return out


def sent(record: str, nn: str, words: str) -> None:
    """My message in stand-in NN's transcript, as if I had typed it in its
    pane, and its answer after it."""
    with open(os.path.join(record, "world.json")) as f:
        heard = json.load(f)[nn]
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    sid = os.path.basename(heard).removesuffix(".jsonl")
    with open(heard, "a") as f:
        f.write(json.dumps({"type": "user", "sessionId": sid, "timestamp": stamp, "uuid": "sent-1",
                            "origin": {"kind": "human"}, "message": {"role": "user", "content": words}}) + "\n")
        f.write(json.dumps({"type": "assistant", "sessionId": sid, "timestamp": stamp, "uuid": "sent-2",
                            "parentUuid": "sent-1", "message": {"role": "assistant", "content": [
                                {"type": "text", "text": "On it."}]}}) + "\n")


def main() -> None:
    plan = steps(sys.argv[1:])
    if not any(s[0] == "say" and s[1].strip() for s in plan):
        sys.exit('Usage: test-chat.py "<my words>" [--sent NN "<my message>"] ["<my next words>"]')
    folder = tempfile.mkdtemp(prefix="test-chat-")
    record = os.path.join(folder, "record")
    with open(os.path.join(folder, "mcp.json"), "w") as f:
        json.dump({"mcpServers": {"door": {"command": sys.executable, "args": [DOOR, "trial", record],
                                           "env": {"TRIAL_TAP": os.environ.get("TRIAL_TAP", "Agree"),
                                                   "TRIAL_WAVE": os.environ.get("TRIAL_WAVE", "")}}}}, f)
    with open(os.path.join(folder, "settings.json"), "w") as f:
        json.dump({"permissions": {"deny": REACHING}}, f)
    with open(INSTRUCTIONS) as f:
        instructions = f.read()
    chat = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json",
                             "--verbose", "--tools", "", "--strict-mcp-config",
                             "--mcp-config", os.path.join(folder, "mcp.json"),
                             "--settings", os.path.join(folder, "settings.json"),
                             "--allowedTools", "mcp__door", "--disallowedTools", ",".join(REACHING),
                             "--append-system-prompt", instructions],
                            cwd=folder, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        for step in plan:
            if step[0] == "sent":
                sent(record, step[1], step[2])
                print(f"--- Unsaid: I sent stand-in {step[1]}: {step[2]}\n")
                continue
            print(f"--- Me: {step[1]}")
            chat.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": step[1]}}) + "\n")
            chat.stdin.flush()
            for line in chat.stdout:
                event = json.loads(line)
                if event.get("type") == "result":
                    print(f"--- Chat: {(event.get('result') or '').strip()}\n")
                    break
    finally:
        chat.stdin.close()
        chat.wait(timeout=60)
    print(f"--- Its acts, kept in {record}, none done:")
    shown = False
    for name in ("acts.jsonl", "order.json"):
        path = os.path.join(record, name)
        if os.path.exists(path):
            with open(path) as f:
                print(f"{name}: {f.read().strip()}")
            shown = True
    print("" if shown else "none")


if __name__ == "__main__":
    main()
