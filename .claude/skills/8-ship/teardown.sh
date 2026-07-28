#!/bin/bash
# teardown.sh — remove a merged branch's worktree, then update the primary checkout.
#
# Usage: teardown.sh --branch <name> [--keep-remote]
#
# Run ONLY after the branch is merged. Removing a worktree whose branch is not
# merged destroys work.
#
# `git worktree remove` reports success at the git-metadata level even when the
# directory survives on disk — a running dev server holds open file handles. So
# every step is verified against the disk, never against git's own answer.
#
# Exit 2 bad arguments · 3 the branch is not merged · 9 the directory survived.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"

BRANCH="" KEEP_REMOTE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --branch)      BRANCH="${2:-}"; shift 2 ;;
    --keep-remote) KEEP_REMOTE=1;   shift   ;;
    *) echo "teardown.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
[ -n "$BRANCH" ] || { echo "teardown.sh: --branch is required" >&2; exit 2; }
[ -d "${CODE:-}" ] || { echo "teardown.sh: no code checkout at '${CODE:-}'" >&2; exit 2; }

WT="$WORKTREES/$BRANCH"

# ---- Refuse unless the branch is genuinely merged ------------------------
git -C "$CODE" fetch origin "$MAIN_BRANCH" --quiet 2>/dev/null
if ! git -C "$CODE" merge-base --is-ancestor "$BRANCH" "origin/$MAIN_BRANCH" 2>/dev/null; then
  echo "teardown.sh: '$BRANCH' is NOT an ancestor of origin/$MAIN_BRANCH — not merged." >&2
  echo "teardown.sh: refusing. Removing it now would destroy the work." >&2
  exit 3
fi
echo "MERGED=yes"

# ---- 1. Stop anything holding the directory open ------------------------
if [ -d "$WT" ] && [ -x /usr/sbin/lsof ]; then
  holders=$(/usr/sbin/lsof +D "$WT" -t 2>/dev/null | sort -u)
  if [ -n "$holders" ]; then
    echo "HOLDERS=$(printf '%s' "$holders" | tr '\n' ' ')"
    for pid in $holders; do kill "$pid" 2>/dev/null; done
    for pid in $holders; do kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null; done
  else
    echo "HOLDERS=none"
  fi
fi

# ---- 2. Remove, then prune ---------------------------------------------
git -C "$CODE" worktree remove --force "$WT" 2>/dev/null
git -C "$CODE" worktree prune 2>/dev/null

# ---- 3. Trust the disk, never git's answer -----------------------------
if [ -d "$WT" ]; then
  rm -rf "$WT"
fi
if [ -d "$WT" ]; then
  echo "WORKTREE_REMOVED=no"
  echo "teardown.sh: '$WT' still exists after a forced remove and an rm -rf." >&2
  exit 9
fi
echo "WORKTREE_REMOVED=yes"

# ---- 4. The branch, local then remote ----------------------------------
git -C "$CODE" branch -D "$BRANCH" >/dev/null 2>&1 \
  && echo "LOCAL_BRANCH_DELETED=yes" || echo "LOCAL_BRANCH_DELETED=no"

if [ "$KEEP_REMOTE" -eq 0 ]; then
  if git -C "$CODE" push origin --delete "$BRANCH" >/dev/null 2>&1; then
    echo "REMOTE_BRANCH_DELETED=yes"
  else
    echo "REMOTE_BRANCH_DELETED=no — branch protection or already gone. Left as is."
  fi
else
  echo "REMOTE_BRANCH_DELETED=skipped"
fi

# ---- 5. Fast-forward the primary checkout ------------------------------
# Never force. A checkout that cannot fast-forward is dirty or diverged, and
# that is the user's to resolve.
if git -C "$CODE" pull --ff-only --quiet 2>/dev/null; then
  echo "PRIMARY_${MAIN_BRANCH}=fast-forwarded to $(git -C "$CODE" rev-parse --short HEAD)"
else
  echo "PRIMARY_${MAIN_BRANCH}=could not fast-forward — dirty or diverged. Left untouched."
fi
