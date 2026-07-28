#!/bin/bash
# guard-memory.sh — PreToolUse(Write|Edit|MultiEdit) guard. Registered globally
# in settings.json, so it fires for the main session AND every subagent.
#
# Memory is disabled in this layer. The repo is the durable home: CLAUDE.md, the
# skills, the agents, the archive. A fact worth keeping belongs in a file under
# version control, where it can be read, reviewed, and reverted.
# This blocks every write to a Claude memory store. When blocked, the agent must
# surface the memory to the user and route it — never persist it silently.
# Reads the hook JSON on stdin. Exit 2 blocks; exit 0 allows.

input=$(cat)
file_path=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.file_path // ""')

# Normalize: collapse /./ so a memory path cannot hide behind it.
# sed, not bash substitution: in ${var//p/r} the replacement is literal, so an escaped
# slash inserts a backslash and corrupts the path. The :a/ta loop catches /././ too.
normalized=$(printf '%s' "$file_path" | sed -e ':a' -e 's|/\./|/|g;ta')

# Any Claude account dir's memory store:  …/.claude*/projects/*/memory/…
if printf '%s' "$normalized" | grep -Eq '/\.claude[^/]*/projects/[^/]+/memory(/|$)'; then
  echo "Blocked: memory writes are disabled. Do not persist this. Surface the memory to the user and discuss where it belongs — a doc, the code, CLAUDE.md, or a skill or agent file. Wait for the decision." >&2
  exit 2
fi

exit 0
