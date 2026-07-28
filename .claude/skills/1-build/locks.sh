#!/bin/bash
# locks.sh — check requested code paths against every live lock. Read-only.
#
# Usage: locks.sh --paths "src/api/,src/web/"
#
# Prints OVERLAP=yes|no. On overlap, prints the FULL body of each colliding lock
# so the collision can be judged on its own terms — that is the only place the
# full lock bodies are ever needed.
#
# Exit 2 bad arguments.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

PATHS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --paths) PATHS="${2:-}"; shift 2 ;;
    *) echo "locks.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
[ -n "$PATHS" ] || { echo "locks.sh: --paths is required" >&2; exit 2; }

REQ=$(mktemp); COLLIDE=$(mktemp)
trap 'rm -f "$REQ" "$COLLIDE"' EXIT
printf '%s' "$PATHS" | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$' > "$REQ"

# Walk the lock file block by block. A block collides when its Paths: value and
# a requested path are prefixes of one another in either direction.
#
# EVERY collision is reported, closed blocks included, tagged LIVE or CLOSED?.
# This is a safety control, so it fails loud. A block marked closed in its header
# can still hold its claim in its body — one may read "Lock HELD, not cleared"
# and forbid any other build on its branch. Filtering on the header would hide
# exactly that. The caller judges; the script never decides.
awk -v reqfile="$REQ" '
  BEGIN { n = 0; while ((getline line < reqfile) > 0) req[++n] = line; live = 1 }
  function collides(lockpaths,   i, j, m, parts, p, r) {
    m = split(lockpaths, parts, /[, ]+/)
    for (j = 1; j <= m; j++) {
      p = parts[j]
      gsub(/[`"()]/, "", p)
      if (p == "" || p == "TBD" || p ~ /^n\/a/) continue
      for (i = 1; i <= n; i++) {
        r = req[i]
        if (index(p, r) == 1 || index(r, p) == 1) return 1
      }
    }
    return 0
  }
  function flush() {
    if (name != "" && hit) {
      print (live ? "=== LIVE — " : "=== CLOSED? — read the body, a closed header can still hold its claim — ") name
      print body
    }
    name = ""; body = ""; hit = 0; live = 1
  }
  /^## Lock Format/ { flush(); exit }
  /^## Lock:/ {
    flush()
    name = $0; sub(/^## Lock: /, "", name)
    if ($0 ~ /CLOSED/) live = 0
    body = $0 "\n"
    next
  }
  name == "" { next }
  {
    body = body $0 "\n"
    if (/^Session:/ && $0 ~ /CLOSED/) live = 0
    if (/^Paths:/ && collides(substr($0, 8))) hit = 1
  }
  END { flush() }
' "$LOCKFILE" > "$COLLIDE"

if [ -s "$COLLIDE" ]; then
  echo "OVERLAP=yes"
  echo "--- colliding locks, in full ---"
  cat "$COLLIDE"
else
  echo "OVERLAP=no"
fi

# Existing worktrees, so REUSE is visible before a branch is named. A branch lives
# in one worktree; work continues in the one it already has. The user names the
# work, not the branch — this list is what those words get matched against.
echo
echo "--- worktrees that already exist ---"
found=0
if [ -n "${CODE:-}" ] && [ -d "$CODE" ]; then
  while IFS= read -r wt; do
    case "$wt" in "$WORKTREES"/*) ;; *) continue ;; esac
    br=$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
    ahead=$(git -C "$wt" rev-list --count "$MAIN_BRANCH..HEAD" 2>/dev/null || echo "?")
    dirty=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    printf "  branch=%s  commits_ahead_of_%s=%s  uncommitted=%s\n" "$br" "$MAIN_BRANCH" "$ahead" "$dirty"
    found=1
  done < <(git -C "$CODE" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')
fi
[ "$found" -eq 0 ] && echo "  (none — any branch named here will be created)"
