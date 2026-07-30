#!/bin/bash
# guard-write.sh — the write-scope fence for executor subagents.
# Declared in the frontmatter of executor on PreToolUse(Write|Edit|MultiEdit).
# Confines it to its tree.
#
# IDENTITY: the agent name comes from $1, passed in the agent's own hook
# declaration. It is NEVER read from stdin agent fields — those are unreliable
# in PreToolUse hooks.
#
# FLOOR per agent — the only writable places:
#   executor          → .worktrees/<branch>/ + sessions/
#   unknown           → block
#
# The primary code checkout is blocked here by default-deny, and blocked again
# session-wide by guard-infra.sh. Two independent controls, deliberately.
#
# The sessions/ allowance is the executor's own work summary, and nothing else.
# Documentation is not an executor's to write: a researcher analyses the deltas
# and the session writes them, which is what the executor file already says.
#
# There is NO lane fence, and that is deliberate. An earlier version split
# backend/ from frontend/ inside ONE tree, while two same-lane spawns always
# passed the identical check — so the common collision was never covered.
# What separates two live executors is the spawn contract: explicit target
# paths, and an executor that STOPS without them. Worktree-root files (lint
# config, formatter config, compose files, CI workflows) are shared ground —
# they serialise through plan-agents sequencing, one owner per phase step.
#
# ADDING A LANE: if your repo genuinely needs one executor fenced out of a
# subtree, three things change together — a case branch below that sets
# OTHER_LANE, a new agent file carrying its own `guard-write.sh <name>` hook
# declaration, and a row in .claude/agents/README.md. A table row with no case
# branch has no fence at all.
#
# Exit 0 = allow. Exit 2 = block.

set -euo pipefail

AGENT="${1:-}"
if [[ -z "$AGENT" ]]; then
  echo "guard-write: missing agent argument (\$1). Block all writes." >&2
  exit 2
fi

# Fail closed. A guard that cannot resolve its own paths blocks, never allows.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh" 2>/dev/null || {
  echo "guard-write [${AGENT}]: cannot source paths.sh — blocking every write." >&2
  exit 2
}

JQ="/usr/bin/jq"

input=$(cat)
file_path=$(printf '%s' "$input" | "$JQ" -r '.tool_input.file_path // ""' 2>/dev/null || true)

# Reject empty path.
if [[ -z "$file_path" ]]; then
  echo "guard-write [${AGENT}]: file_path is empty — outside write floor — stop and report." >&2
  exit 2
fi

# Normalize: collapse /./, then reject any /../ (target may not exist yet, so no realpath).
# sed, not bash substitution: in ${var//p/r} the replacement is literal, so an escaped
# slash inserts a backslash and corrupts the path. The :a/ta loop catches /././ too.
normalized=$(printf '%s' "$file_path" | sed -e ':a' -e 's|/\./|/|g;ta')
if [[ "$normalized" == *"/../"* ]] || [[ "$normalized" == *"/.." ]]; then
  echo "guard-write [${AGENT}]: path traversal in '${file_path}' — stop and report." >&2
  exit 2
fi
# Reject anything outside the repo root.
if [[ "$normalized" != "${ROOT}/"* ]] && [[ "$normalized" != "${ROOT}" ]]; then
  echo "guard-write [${AGENT}]: '${file_path}' is outside the repo root — stop and report." >&2
  exit 2
fi

floor_pass=0
case "$AGENT" in
  executor) ;;
  *)
    echo "guard-write: unknown agent '${AGENT}' — block." >&2
    exit 2
    ;;
esac

# Allow: the worktree, and its own work summary in the session folder.
if [[ "$normalized" == "${WORKTREES}/"* ]]; then
  floor_pass=1
elif [[ "$normalized" == "${SESSIONS}/"* ]]; then
  floor_pass=1
fi

if [[ "$floor_pass" -ne 1 ]]; then
  echo "guard-write [${AGENT}]: '${file_path}' outside write floor — stop and report." >&2
  exit 2
fi

exit 0
