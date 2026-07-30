#!/bin/bash
# attach.sh — point THIS terminal at an existing live session. One file write.
#
# Usage:
#   attach.sh --target <NNNN | slug | NNNN-slug>
#
# Invoked by a handoff prompt's first step, in the fresh terminal.
#
# Writes .claude/state/<session_id>, holding the folder name. It creates no
# folder, no lock, and no marker, and it deletes nothing. session-markers.sh
# clears the identity file on SessionEnd.
#
# Prints, for the model to read:
#   FOLDER= PATH= ATTACHED= BRANCH= then the folder listing between FILES markers.
#
# Exit 2 bad arguments · 3 no match or ambiguous · 4 missing path
#      · 5 the folder exists but is not live · 6 no harness session id
#      · 7 this terminal already belongs to a session.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    *) echo "attach.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

[ -n "$TARGET" ] || { echo "attach.sh: --target is required" >&2; exit 2; }

SID="${CLAUDE_CODE_SESSION_ID:-}"
[ -n "$SID" ] || {
  echo "attach.sh: CLAUDE_CODE_SESSION_ID is unset — cannot record identity" >&2
  exit 6
}

# ---- Refuse to hijack an attached terminal ------------------------------
# Repointing would orphan the first session's identity, unnoticed.
if [ -f "$STATE/$SID" ]; then
  echo "attach.sh: this terminal already belongs to $(cat "$STATE/$SID")" >&2
  echo "attach.sh: park there and attach from a fresh terminal" >&2
  exit 7
fi

# ---- Resolve the target -------------------------------------------------
# Three spellings: the number, the slug, or the whole folder name. Ambiguity
# refuses. An all-digit target is zero-padded, so "4" finds "0004"; anything
# else is compared literally.
WANT_NUM=""
case "$TARGET" in
  ""|*[^0-9]*) ;;
  *) WANT_NUM=$(printf '%04d' "$((10#$TARGET))") ;;
esac

matches=()
for d in "$SESSIONS"/[0-9][0-9][0-9][0-9]-*; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  num="${name%%-*}"
  slug="${name#*-}"
  if [ "$name" = "$TARGET" ] || [ "$slug" = "$TARGET" ] \
     || { [ -n "$WANT_NUM" ] && [ "$num" = "$WANT_NUM" ]; }; then
    matches+=("$name")
  fi
done

if [ "${#matches[@]}" -eq 0 ]; then
  echo "attach.sh: no session folder matches '$TARGET'" >&2
  echo "attach.sh: live sessions:" >&2
  for d in "$SESSIONS"/[0-9][0-9][0-9][0-9]-*; do
    [ -d "$d" ] && [ -f "$d/.session-live" ] && echo "  $(basename "$d")" >&2
  done
  exit 3
fi

if [ "${#matches[@]}" -gt 1 ]; then
  echo "attach.sh: '$TARGET' matches ${#matches[@]} sessions — name one exactly:" >&2
  printf '  %s\n' "${matches[@]}" >&2
  exit 3
fi

FOLDER="${matches[0]}"
DIR="$SESSIONS/$FOLDER"

# ---- Refuse a closed session -------------------------------------------
# No marker means the lock is gone. Attaching would claim what nobody registered.
[ -f "$DIR/.session-live" ] || {
  echo "attach.sh: $FOLDER is not live — no .session-live marker" >&2
  echo "attach.sh: a closed session cannot be resumed. Boot a new one." >&2
  exit 5
}

# ---- Write the identity file -------------------------------------------
mkdir -p "$STATE"
printf '%s\n' "$FOLDER" > "$STATE/$SID"

# ---- Output ------------------------------------------------------------
echo "FOLDER=$FOLDER"
echo "PATH=$DIR"
echo "ATTACHED=yes"

# The branch, off this session's lock block. Empty means /1-build never ran.
SLUG="${FOLDER#*-}"
BRANCH=$(awk -v slug="$SLUG" '
  $0 == "## Lock: " slug { inblock = 1; next }
  /^## Lock:/ { inblock = 0 }
  inblock && /^Branch:/ { print substr($0, 9); exit }
' "$LOCKFILE" 2>/dev/null || true)
echo "BRANCH=$BRANCH"

# Every file the session left behind, newest last.
echo "FILES_START"
ls -1rt "$DIR" 2>/dev/null | grep -v '^\.' || true
echo "FILES_END"
