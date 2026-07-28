#!/bin/bash
# guard-infra.sh — PreToolUse(Write|Edit|MultiEdit) guard. Registered session-wide
# in settings.json, so it fires for the main session AND every subagent.
#
# The primary code checkout stays pristine on the default branch. Nothing writes
# there — not an executor, not the session, not the user through a session. Code
# writes go to the worktree at .worktrees/<branch>/, which /1-build creates.
#
# This exists because the rule was text only. CLAUDE.md said the session never
# writes the primary checkout, and no hook enforced it. A sentence a model can
# drift past is not a control. guard-write.sh fences the executors; nothing
# fenced the session.
#
# The worktree is deliberately NOT blocked. A session may write code there
# directly when the work fits one pass. Executors are for scale, not permission.
#
# CODE is defined in .claude/lib/paths.sh. Set it empty in paths.local.sh to
# switch this guard off — a repo with no separate code checkout does not need it.
#
# Reads the hook JSON on stdin. Exit 2 blocks; exit 0 allows.

source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh" 2>/dev/null || exit 0

[ -n "${CODE:-}" ] || exit 0

input=$(cat)
file_path=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.file_path // ""' 2>/dev/null || true)

[ -n "$file_path" ] || exit 0

# Normalize: collapse /./ so the path cannot hide behind it.
# sed, not bash substitution: in ${var//p/r} the replacement is literal, so an
# escaped slash inserts a backslash and corrupts the path instead of cleaning it.
# The :a/ta loop re-runs until no /./ remains, catching /././ too.
normalized=$(printf '%s' "$file_path" | sed -e ':a' -e 's|/\./|/|g;ta')

if [[ "$normalized" == "${CODE}/"* ]] || [[ "$normalized" == "${CODE}" ]]; then
  echo "Blocked: the primary code checkout at ${CODE} is never written. It stays pristine on the default branch. Write in the worktree at .worktrees/<branch>/ — run /1-build if none exists." >&2
  exit 2
fi

exit 0
