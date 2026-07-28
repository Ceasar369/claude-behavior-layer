#!/bin/bash
# paths.sh — the single definition of where things live.
# Sourced by every lifecycle script and by the hooks that need a path.
# Change a location here, nowhere else.
#
# Definitions only. Sourcing this has no side effects and never exits, so a
# PreToolUse guard can source it safely. A script that genuinely needs the
# directories to exist calls `require_paths` after sourcing.

# The repo root is two levels above this file (.claude/lib/paths.sh). Derived,
# never hardcoded: the layer works wherever it is cloned, under any user.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Machine-local overrides, if any. Git-ignored, and sourced BEFORE the defaults
# below, so anything it sets wins. Copy paths.local.sh.example to start one.
[ -f "$ROOT/.claude/lib/paths.local.sh" ] && source "$ROOT/.claude/lib/paths.local.sh"

# One session folder per session: sessions/NNNN-slug/.
SESSIONS="${SESSIONS:-$ROOT/sessions}"

# The live index. One block per session, under a "## Active Locks" heading.
LOCKFILE="${LOCKFILE:-$SESSIONS/ACTIVE.md}"

# One file per day: archive/YYYY-MM-DD.md. Sessions distil into it and vanish.
ARCHIVE="${ARCHIVE:-$ROOT/archive}"

# The durable documentation tree — the canon a session reads and writes.
DOCS="${DOCS:-$ROOT/docs}"

# Session prompts, written by /7-provide-prompt and claimed by /0-start.
PROMPTS="${PROMPTS:-$ROOT/prompts}"

# Where /1-build cuts a branch worktree of CODE.
WORKTREES="${WORKTREES:-$ROOT/.worktrees}"

# The integration branch every worktree is cut from and merged back into.
MAIN_BRANCH="${MAIN_BRANCH:-main}"

# The primary code checkout. It stays pristine on the default branch — nothing
# writes there, and guard-infra.sh enforces that. Code writes go to a worktree.
# Set it empty in paths.local.sh to switch that guard off entirely.
CODE="${CODE-$ROOT/code}"

# Session id → session folder name. Written once at boot, read by any skill or
# hook that has only a session id. Swept on SessionEnd.
STATE="$ROOT/.claude/state"

# Fail loudly rather than write to a path that does not exist.
# Lifecycle scripts call this. Hooks do not — a guard must not die on a missing
# directory; it must still guard.
require_paths() {
  local d
  for d in "$SESSIONS" "$ARCHIVE"; do
    [ -d "$d" ] || { echo "paths.sh: missing directory: $d" >&2; exit 4; }
  done
  [ -f "$LOCKFILE" ] || { echo "paths.sh: missing lock file: $LOCKFILE" >&2; exit 4; }
}
