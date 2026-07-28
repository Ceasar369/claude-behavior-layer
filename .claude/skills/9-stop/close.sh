#!/bin/bash
# close.sh — the close, in one call. Archive first, then remove.
#
# Usage: close.sh --folder <NNNN-slug> [--archive-block <file>]
#
# In order:
#   1. Append the archive block to archive/YYYY-MM-DD.md
#   2. Delete the session folder, marker included
#   3. Delete the lock block whose Folder: names that folder
#   4. Clear this session's identity file (.claude/state/<session_id>)
#
# The archive append happens FIRST. A failure after it leaves the record written
# and the folder intact — recoverable. The reverse order is not.
#
# Exit 2 bad arguments · 3 folder not found · 8 the archive append failed.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

FOLDER="" BLOCK=""
while [ $# -gt 0 ]; do
  case "$1" in
    --folder)        FOLDER="${2:-}"; shift 2 ;;
    --archive-block) BLOCK="${2:-}";  shift 2 ;;
    *) echo "close.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
[ -n "$FOLDER" ] || { echo "close.sh: --folder is required" >&2; exit 2; }

# A bare folder name only. This guards the rm -rf below: no slashes, no dots,
# no empty value can reach it, so the target is always one child of SESSIONS.
case "$FOLDER" in */*|"."|".."|"") echo "close.sh: --folder must be a bare folder name" >&2; exit 2 ;; esac

D="$SESSIONS/$FOLDER"
[ -d "$D" ] || { echo "close.sh: $D not found" >&2; exit 3; }

# ---- 1. Archive ---------------------------------------------------------
if [ -n "$BLOCK" ]; then
  [ -f "$BLOCK" ] || { echo "close.sh: archive block file not found: $BLOCK" >&2; exit 8; }
  DAY="$ARCHIVE/$(date +%F).md"
  [ -f "$DAY" ] || printf '# %s\n' "$(date +%F)" > "$DAY"
  # Reject a block carrying paths, links, or SHAs — the archive forbids them.
  if grep -qE '\[\[|\]\]|/[a-zA-Z0-9_.-]+/|\.md\b|\bPR #|\b[0-9a-f]{7,40}\b' "$BLOCK"; then
    echo "close.sh: the archive block contains a path, link, filename, PR number, or SHA." >&2
    echo "close.sh: the archive is pure prose. Rewrite it in words, then re-run." >&2
    exit 8
  fi
  { printf '\n'; cat "$BLOCK"; printf '\n'; } >> "$DAY"
  echo "ARCHIVED=$DAY"
else
  echo "ARCHIVED=none"
fi

# ---- 2. The session folder ---------------------------------------------
rm -rf "$D"
echo "FOLDER_REMOVED=$D"

# ---- 3. The lock block --------------------------------------------------
# Drop the whole block whose Folder: line names this folder. Buffered, so the
# decision is made only after the block has been read in full.
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
awk -v want="sessions/$FOLDER/" '
  function flush() { if (name != "" && !drop) printf "%s", body; name = ""; body = ""; drop = 0 }
  /^## Lock Format/ { flush(); infmt = 1 }
  infmt { print; next }
  /^## Lock:/ { flush(); name = $0; body = $0 "\n"; next }
  name == "" { print; next }
  { body = body $0 "\n"; if (/^Folder:/ && index($0, want)) drop = 1 }
  END { flush() }
' "$LOCKFILE" > "$TMP"
cat "$TMP" > "$LOCKFILE"
if grep -q "sessions/$FOLDER/" "$LOCKFILE"; then
  echo "LOCK_REMOVED=no — a reference to $FOLDER remains in the lock file"
else
  echo "LOCK_REMOVED=yes"
fi

# ---- 4. The identity file -----------------------------------------------
# Any ask/answer files went with the folder in step 2 — they live inside it.
# All that remains is the session-id → folder map boot.sh wrote.
# CLAUDE_CODE_SESSION_ID is undocumented; the SessionEnd hook is the guaranteed
# clear. This is the immediate one, and it is allowed to find nothing.
if [ -n "${CLAUDE_CODE_SESSION_ID:-}" ]; then
  rm -f "$STATE/$CLAUDE_CODE_SESSION_ID"
  echo "STATE_CLEARED=yes"
else
  echo "STATE_CLEARED=no — session id unavailable; the SessionEnd hook will clear it"
fi
