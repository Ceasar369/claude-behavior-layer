#!/bin/bash
# guard-spawn.sh — PreToolUse(Task|Agent) guard: block built-in subagent types.
#
# The doctrine: every research, exploration, or execution task goes to a NAMED
# custom agent from .claude/agents/.
# Built-in types (general-purpose, Explore, Plan, claude, …) carry no project
# context, no communication standard, and no hooks — so no write fence.
# Smaller and faster models default to them; this blocks that deterministically.
# A text rule alone did not hold.
# Exit 2 blocks the tool and returns the reason to the agent. Reads hook JSON on stdin.
#
# Backstop, not a sandbox. The durable control is the orchestration doctrine;
# this enforces the one line models keep dropping.

input=$(cat)
agent=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.subagent_type // ""')

case "$agent" in
  general-purpose|claude|Explore|Plan|statusline-setup|output-style-setup)
    echo "Blocked: '$agent' is a built-in agent type. Use a named custom agent — 'researcher' for exploration, the matching executor for work. See CLAUDE.md (Spawn discipline) and .claude/agents/." >&2
    exit 2
    ;;
esac

exit 0
