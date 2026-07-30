#!/bin/bash
# boot.sh — create the session folder, the live marker, and the lock. Print the digest.
#
# Usage:
#   boot.sh --slug <kebab> --intent "<one line>" [--number NNNN]
#
# The mode is not recorded here. /0-start gates it after the boot returns.
#
# Prints, for the model to read:
#   NNNN= FOLDER= LOCK_WRITTEN= RENAME= then a live-lock digest between DIGEST markers.
#
# Exit 2 bad arguments · 3 number collides with an existing folder · 4 missing path
#      · 5 the folder was created but the lock did not write.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

SLUG="" INTENT="" NUMBER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --slug)   SLUG="${2:-}";   shift 2 ;;
    --intent) INTENT="${2:-}"; shift 2 ;;
    --number) NUMBER="${2:-}"; shift 2 ;;
    *) echo "boot.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

for pair in "slug:$SLUG" "intent:$INTENT"; do
  [ -n "${pair#*:}" ] || { echo "boot.sh: --${pair%%:*} is required" >&2; exit 2; }
done

# The slug must be kebab — it becomes a folder name and a lock key.
case "$SLUG" in
  *[^a-z0-9-]*|-*|*-|"") echo "boot.sh: slug must be lowercase kebab: '$SLUG'" >&2; exit 2 ;;
esac

# ---- The number ----------------------------------------------------------
# Named number wins outright. Otherwise: one above the highest folder that
# EXISTS. Basing it on existing folders rather than on live markers means a
# new session can never collide with a folder still on disk.
highest=0
for d in "$SESSIONS"/[0-9][0-9][0-9][0-9]-*; do
  [ -d "$d" ] || continue
  n=$(basename "$d"); n="${n%%-*}"; n=$((10#$n))
  [ "$n" -gt "$highest" ] && highest="$n"
done

if [ -n "$NUMBER" ]; then
  case "$NUMBER" in *[^0-9]*|"") echo "boot.sh: --number must be digits" >&2; exit 2 ;; esac
  NNNN=$(printf '%04d' "$((10#$NUMBER))")
  existing=$(find "$SESSIONS" -maxdepth 1 -type d -name "${NNNN}-*" 2>/dev/null | head -n1)
  if [ -n "$existing" ]; then
    echo "boot.sh: $NNNN already exists on disk: $(basename "$existing")" >&2
    exit 3
  fi
else
  NNNN=$(printf '%04d' "$((highest + 1))")
fi

FOLDER="$SESSIONS/$NNNN-$SLUG"
[ -e "$FOLDER" ] && { echo "boot.sh: $FOLDER already exists" >&2; exit 3; }

TODAY=$(date +%F)

# ---- The session folder --------------------------------------------------
mkdir -p "$FOLDER"

{
  printf '# Session %s — %s\n\n' "$NNNN" "$SLUG"
  printf 'Intent: %s\n' "$INTENT"
  printf 'Started: %s\n\n' "$TODAY"
  printf '## Decision log\n\n'
  printf -- '- %s — %s\n' "$TODAY" "$INTENT"
} > "$FOLDER/00-session.md"

: > "$FOLDER/.session-live"

# ---- The identity map ---------------------------------------------------
# Every later skill needs this session's folder name — /1-build, /9-stop, /2-ask,
# /4-inbox. Boot is the one place that already knows it, so it records it once
# here instead of four skills each re-deriving it by reading the lock file.
# Keyed by the harness session id, which is also all a hook ever receives.
# session-markers.sh sweeps it on SessionEnd.
if [ -n "${CLAUDE_CODE_SESSION_ID:-}" ]; then
  mkdir -p "$STATE"
  printf '%s\n' "$NNNN-$SLUG" > "$STATE/$CLAUDE_CODE_SESSION_ID"
fi

# ---- The lock -----------------------------------------------------------
# Inserted immediately after the "## Active Locks" heading. Written atomically
# so a failure mid-write cannot leave the live index truncated.
LOCK_TMP=$(mktemp)
trap 'rm -f "$LOCK_TMP"' EXIT

awk -v slug="$SLUG" -v nnnn="$NNNN" -v focus="$INTENT" -v folder="sessions/$NNNN-$SLUG/" '
  { print }
  !done && /^## Active Locks[[:space:]]*$/ {
    print ""
    print "## Lock: " slug
    print "Session: " nnnn
    print "Focus: " focus
    print "Parallel: yes"
    print "Folder: " folder
    done = 1
  }
' "$LOCKFILE" > "$LOCK_TMP"

grep -q "^## Lock: $SLUG\$" "$LOCK_TMP" || {
  echo "boot.sh: could not find '## Active Locks' in $LOCKFILE — lock NOT written" >&2
  echo "NNNN=$NNNN"
  echo "FOLDER=$FOLDER"
  echo "LOCK_WRITTEN=no"
  exit 5
}
cat "$LOCK_TMP" > "$LOCKFILE"

# ---- Output ------------------------------------------------------------
echo "NNNN=$NNNN"
echo "FOLDER=$FOLDER"
echo "LOCK_WRITTEN=yes"
echo "RENAME=/rename $NNNN-$SLUG"

# The digest replaces reading the lock file. Name, session, branch, and a
# truncated focus, for LIVE locks only.
#
# A closed lock marks itself either on its "## Lock:" header or on its
# "Session:" line — both spellings occur. So each block is buffered and the
# live/closed decision is made only once the whole block has been read.
echo "DIGEST_START"
awk '
  function trunc(s, n) { return (length(s) > n) ? substr(s, 1, n - 3) "..." : s }
  function flush() {
    if (name != "" && live) {
      printf "· %s", name
      if (sess  != "") printf "  [%s]", trunc(sess, 12)
      if (brnch != "") printf "  branch=%s", trunc(brnch, 40)
      printf "\n    %s\n", trunc(focus, 90)
    }
    name = ""; sess = ""; brnch = ""; focus = ""; live = 1
  }
  BEGIN { live = 1 }
  /^## Lock Format/ { flush(); exit }
  /^## Lock:/ {
    flush()
    name = $0; sub(/^## Lock: /, "", name)
    if ($0 ~ /CLOSED/) live = 0
    next
  }
  name == "" { next }
  /^Session:/ { sess  = substr($0, 10); if ($0 ~ /CLOSED/) live = 0 }
  /^Branch:/  { brnch = substr($0, 9) }
  /^Focus:/   { if (focus == "") focus = substr($0, 8) }
  END { flush() }
' "$LOCKFILE"
echo "DIGEST_END"
