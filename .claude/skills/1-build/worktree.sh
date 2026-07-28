#!/bin/bash
# worktree.sh — reuse or cut the branch's worktree, then finalize the lock.
#
# Usage: worktree.sh --branch <name> --slug <lock slug> --paths "p1,p2"
#
# A branch lives in exactly one worktree. If one exists, it is attached, never
# duplicated. The primary code checkout is never touched.
#
# Prints ACTION=reuse|attach|create · WORKTREE= · LOCK_UPDATED=
# Exit 2 bad arguments · 6 git refused · 7 the lock block was not found.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

BRANCH="" SLUG="" PATHS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --slug)   SLUG="${2:-}";   shift 2 ;;
    --paths)  PATHS="${2:-}";  shift 2 ;;
    *) echo "worktree.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
for pair in "branch:$BRANCH" "slug:$SLUG" "paths:$PATHS"; do
  [ -n "${pair#*:}" ] || { echo "worktree.sh: --${pair%%:*} is required" >&2; exit 2; }
done

case "$BRANCH" in
  fix/*|chore/*|feature/*) ;;
  *) echo "worktree.sh: branch must start fix/ chore/ or feature/ — got '$BRANCH'" >&2; exit 2 ;;
esac

[ -d "${CODE:-}" ] || { echo "worktree.sh: no code checkout at '${CODE:-}' — set CODE in .claude/lib/paths.local.sh" >&2; exit 2; }

WT="$WORKTREES/$BRANCH"

# ---- Reuse, attach, or create -------------------------------------------
if [ -d "$WT" ]; then
  ACTION=reuse
elif git -C "$CODE" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  # The branch exists but has no worktree — check it out, never re-create it.
  git -C "$CODE" worktree add "$WT" "$BRANCH" >/dev/null 2>&1 || { echo "worktree.sh: git worktree add failed for existing branch '$BRANCH'" >&2; exit 6; }
  ACTION=attach
else
  git -C "$CODE" worktree add "$WT" -b "$BRANCH" >/dev/null 2>&1 || { echo "worktree.sh: git worktree add -b failed for '$BRANCH'" >&2; exit 6; }
  ACTION=create
fi

# A fresh worktree usually needs dependencies before anything runs in it. The
# commands are yours, not the layer's — put them in this optional hook and it is
# called with the worktree path. Absent, nothing happens.
# See .claude/lib/worktree-setup.sh.example for the contract and examples.
if [ "$ACTION" != "reuse" ] && [ -x "$ROOT/.claude/lib/worktree-setup.sh" ]; then
  "$ROOT/.claude/lib/worktree-setup.sh" "$WT" || echo "worktree.sh: worktree-setup.sh failed — the worktree still exists" >&2
fi

# ---- Finalize the lock --------------------------------------------------
# Branch: and Paths: are inserted after Focus: in this slug's block only.
# An existing Branch:/Paths: line is replaced, never duplicated.
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT

awk -v slug="$SLUG" -v br="$BRANCH" -v pths="$PATHS" '
  BEGIN { found = 0 }
  /^## Lock:/ { inblock = ($0 == "## Lock: " slug); if (inblock) found = 1 }
  inblock && /^Branch:/ { next }
  inblock && /^Paths:/  { next }
  { print }
  inblock && /^Focus:/ {
    print "Branch: " br
    print "Paths: " pths
  }
  END { exit (found ? 0 : 1) }
' "$LOCKFILE" > "$TMP" || {
  echo "ACTION=$ACTION"; echo "WORKTREE=$WT"; echo "LOCK_UPDATED=no"
  echo "worktree.sh: no lock block '## Lock: $SLUG' in $LOCKFILE" >&2
  exit 7
}
cat "$TMP" > "$LOCKFILE"

echo "ACTION=$ACTION"
echo "WORKTREE=$WT"
echo "LOCK_UPDATED=yes"
git -C "$CODE" worktree list | sed 's/^/  /'
