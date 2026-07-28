#!/bin/bash
# probe.sh — report the closing state from disk and git. Read-only.
#
# Usage: probe.sh --folder <NNNN-slug>
#
# Prints:
#   FOLDER= EXISTS= MARKER= LOCK_SLUG= BRANCH= WORKTREE= WT_DIRTY= WT_UNPUSHED=
#   REPO_DIRTY= OPEN_ASK= UNREAD_ANSWER= ARCHIVE_FILE=
#
# BRANCH empty means this session never ran /1-build — so there is nothing to
# verify and nothing to ship.
#
# Exit 2 bad arguments · 3 the folder does not exist.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

FOLDER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --folder) FOLDER="${2:-}"; shift 2 ;;
    *) echo "probe.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
[ -n "$FOLDER" ] || { echo "probe.sh: --folder is required (NNNN-slug)" >&2; exit 2; }
case "$FOLDER" in */*|"."|".."|"") echo "probe.sh: --folder must be a bare folder name" >&2; exit 2 ;; esac

D="$SESSIONS/$FOLDER"
echo "FOLDER=$D"
if [ -d "$D" ]; then echo "EXISTS=yes"; else echo "EXISTS=no"; echo "probe.sh: $D not found" >&2; exit 3; fi
[ -f "$D/.session-live" ] && echo "MARKER=present" || echo "MARKER=absent"

# The lock block is the one whose Folder: names this folder.
SLUG=$(awk -v want="sessions/$FOLDER/" '
  /^## Lock Format/ { exit }
  /^## Lock:/ { name = $0; sub(/^## Lock: /, "", name); sub(/ —.*$/, "", name); next }
  name != "" && /^Folder:/ { if (index($0, want)) { print name; exit } }
' "$LOCKFILE")
echo "LOCK_SLUG=${SLUG:-}"

BRANCH=""
if [ -n "$SLUG" ]; then
  BRANCH=$(awk -v slug="$SLUG" '
    /^## Lock:/ { inb = ($0 == "## Lock: " slug) }
    inb && /^Branch:/ { b = substr($0, 9); sub(/ .*$/, "", b); print b; exit }
  ' "$LOCKFILE")
fi
echo "BRANCH=${BRANCH:-}"

if [ -n "$BRANCH" ] && [ -d "$WORKTREES/$BRANCH" ]; then
  WT="$WORKTREES/$BRANCH"
  echo "WORKTREE=$WT"
  echo "WT_DIRTY=$(git -C "$WT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  up=$(git -C "$WT" rev-list --count "@{u}..HEAD" 2>/dev/null || echo "no-upstream")
  echo "WT_UNPUSHED=$up"
  echo "--- uncommitted in the worktree, first 20 ---"
  git -C "$WT" status --short 2>/dev/null | head -20 | sed 's/^/  /' || true
else
  echo "WORKTREE="
  echo "WT_DIRTY=0"
  echo "WT_UNPUSHED=0"
fi

# Docs and behavior-layer changes live in this repo, not in the worktree.
echo "REPO_DIRTY=$(git -C "$ROOT" status --porcelain -- docs .claude CLAUDE.md 2>/dev/null | wc -l | tr -d ' ')"

# An unanswered question left behind. It dies with the folder, so name it first.
echo "OPEN_ASK=$(ls -1 "$D" 2>/dev/null | grep -c -- '-ask\.md$' || true)"
echo "UNREAD_ANSWER=$(ls -1 "$D" 2>/dev/null | grep -c -- '\-answer\.md$' || true)"
echo "ARCHIVE_FILE=$ARCHIVE/$(date +%F).md"
echo "--- files in the session folder ---"
ls -1A "$D" | sed 's/^/  /'
