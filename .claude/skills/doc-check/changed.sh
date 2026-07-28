#!/bin/bash
# changed.sh — gather everything that changed, so docs can be checked against it.
# Read-only. Runs no git command that writes.
#
# Usage: changed.sh [--folder <NNNN-slug>]
#
# Prints, in labelled sections: the docs and behavior-layer working tree, every
# worktree's diff against the integration branch, this session's claimed Paths,
# and its work-summary files.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

FOLDER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --folder) FOLDER="${2:-}"; shift 2 ;;
    *) echo "changed.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

echo "=== DOCS + BEHAVIOR LAYER — uncommitted in this repo ==="
git -C "$ROOT" status --short -- docs .claude CLAUDE.md 2>/dev/null | head -100 || true
echo

echo "=== CODE — every worktree, committed against $MAIN_BRANCH and uncommitted ==="
if [ -d "$WORKTREES" ]; then
  while IFS= read -r wt; do
    [ -d "$wt" ] || continue
    br=$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
    echo "--- $br  ($wt)"
    echo "  committed vs $MAIN_BRANCH:"
    git -C "$wt" diff --name-only "$MAIN_BRANCH...HEAD" 2>/dev/null | sed 's/^/    /' | head -60 || echo "    (cannot diff against $MAIN_BRANCH)"
    echo "  uncommitted:"
    git -C "$wt" status --short 2>/dev/null | sed 's/^/    /' | head -40 || true
  done < <(find "$WORKTREES" -mindepth 1 -maxdepth 3 -name ".git" -exec dirname {} \; 2>/dev/null)
else
  echo "(no worktrees)"
fi
echo

echo "=== CODE — uncommitted in the primary checkout (should be empty) ==="
if [ -n "${CODE:-}" ] && [ -d "$CODE" ]; then
  git -C "$CODE" status --short 2>/dev/null | head -40 || true
else
  echo "(no code checkout configured)"
fi
echo

echo "=== CLAIMED PATHS — from every lock carrying one ==="
awk '
  /^## Lock Format/ { exit }
  /^## Lock:/ { name = $0; sub(/^## Lock: /, "", name); next }
  name != "" && /^Paths:/ { print "  " name " → " substr($0, 8) }
' "$LOCKFILE"
echo

if [ -n "$FOLDER" ]; then
  D="$SESSIONS/$FOLDER"
  echo "=== SESSION WORK SUMMARIES — $FOLDER ==="
  if [ -d "$D" ]; then
    for f in "$D"/*work*.md "$D"/*research*.md; do
      [ -f "$f" ] || continue
      echo "--- $(basename "$f")"
      grep -nEi 'doc-sync|stale|contradict|out of date|needs updating' "$f" | head -20 | sed 's/^/    /' || true
    done
  else
    echo "(folder not found: $D)"
  fi
fi
