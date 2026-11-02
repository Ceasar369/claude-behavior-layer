#!/usr/bin/env python3
"""hook.py — the contract every skill's hook honours.

A skill is a UserPromptSubmit hook. The hook does all the work, and blocks
the prompt before Claude Code loads the skill body, so the skill costs no
model turn and no tokens.

A session may call a skill itself, through its Skill tool. That call is no
prompt. A hook registered under PreToolUse, matcher Skill, hears it through
the same words(), and done() refuses the call with the same sentence. The
zero-turn mod, .claude/mods/zero-turn, hands that sentence back as the
call's result, so it never reads as a hook error.

Some hooks answer a write instead of a prompt, and have no skill behind
them. written() is their door, as words() is a skill's. Others refuse a
tool outright through done(): SendMessage, and a command guard.py judges.

A skill whose whole work is one verb of one tool hands it to tool(), and
the tool's last line is the sentence shown.

The floor every file here sits on is
knowledge/0010-playbook/0013-thinking/thinking-protocols/behaviour-protocols/the-behaviour-axioms.md.

Imported, never run.
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The event words() is answering. done() replies in that event's shape.
answering = "UserPromptSubmit"


def words(trigger: str) -> list:
    """The words typed after the trigger, or nothing at all.

    A prompt that does not start with the trigger belongs to another hook or
    to the model, so this exits 0 and says nothing. Every prompt in every
    session runs this, so it is the first thing and it is cheap.

    A Skill call naming the trigger's skill counts as typing it. Its args
    are the words. Any other tool call exits 0 the same way.

    The event is kept on the returned list, as `.event`, because a caller
    that needs the session id or the transcript should not read stdin twice.
    """
    global answering
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("hook_event_name") == "PreToolUse":
        call = event.get("tool_input") or {}
        if event.get("tool_name") != "Skill" \
                or call.get("skill") != trigger.lstrip("/"):
            sys.exit(0)
        answering = "PreToolUse"
        said = call.get("args") or ""
    else:
        prompt = (event.get("prompt") or "").strip()
        if not prompt.startswith(trigger):
            sys.exit(0)
        said = prompt[len(trigger):]
    rest = Words(said.split())
    rest.event = event
    return rest


def written(pattern: str) -> tuple:
    """The file a Write or Edit just wrote, matched, or nothing at all.

    A write that is not to a matching path belongs to nobody here, so this
    exits 0 and says nothing. Returns the match, then the event.
    """
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if event.get("tool_name") not in ("Write", "Edit"):
        sys.exit(0)
    found = re.search(pattern, (event.get("tool_input") or {}).get("file_path") or "")
    if not found:
        sys.exit(0)
    return found, event


class Words(list):
    """A word list carrying the event it came from."""
    event: dict = {}

    def first(self) -> str:
        return self[0].lower() if self else ""


def done(line: str, end: bool = False) -> None:
    """Report one sentence and stop the prompt. A second line may follow it,
    a newline apart.

    A blocked prompt always renders as a hook warning, whatever fields are
    set. Blocking is what keeps a skill at zero tokens, so the colour is the
    price and the words carry the meaning.

    Success always says "successfully". Nothing else in this layer does.

    A Skill call is refused instead, so its body never loads. The session
    reads the words as the call's answer, the zero-turn mod's result. With end,
    the session's turn ends there instead, and it writes nothing after.
    """
    if answering == "PreToolUse":
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": line,
            },
        }
        if end:
            out.update({"continue": False, "stopReason": line})
        print(json.dumps(out))
        sys.exit(0)
    print(json.dumps({
        "decision": "block",
        "reason": line,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "suppressOriginalPrompt": True,
        },
    }))
    sys.exit(0)


def tool(trigger: str, path: str, verb: str, silent: str, passes: int = 0) -> None:
    """A skill whose whole work is one verb of one tool: the trigger's
    words(), the first `passes` of them handed on, the tool run, then done()
    with its last line, or `silent` when it printed nothing. The tool's own
    line says whether it succeeded."""
    said = words(trigger)
    r = subprocess.run([sys.executable, path, verb, *said[:passes]], capture_output=True, text=True)
    lines = (r.stdout + r.stderr).strip().splitlines()
    done(lines[-1] if lines else silent)

