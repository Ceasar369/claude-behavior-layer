#!/bin/bash
# close.sh — the close, in one call. Archive first, then remove.
#
# Usage: close.sh --folder <NNNN-slug> [--archive-block <file>] [--prompt <basename>]
#
# In order:
#   1. Append the archive block to archive/YYYY-MM-DD.md
#   2. Delete the session folder, marker included — skipped when it is already
#      gone and a lock block still names it. That is the stale-lock case: the
#      block is the only thing left, and clearing it is the whole job.
#   3. Delete the lock block whose Folder: names that folder
#   4. Clear this session's identity file (.claude/state/<session_id>)
#   5. Delete the claimed prompt file, if one is named. Prompts come and go.
#
# The archive append happens FIRST. A failure after it leaves the record written
# and the folder intact — recoverable. The reverse order is not.
#
# Exit 2 bad arguments · 3 folder not found and no lock names it
#      · 8 the archive append failed.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/paths.sh"
require_paths

FOLDER="" BLOCK="" PROMPT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --folder)        FOLDER="${2:-}"; shift 2 ;;
    --archive-block) BLOCK="${2:-}";  shift 2 ;;
    --prompt)        PROMPT="${2:-}"; shift 2 ;;
    *) echo "close.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done
[ -n "$FOLDER" ] || { echo "close.sh: --folder is required" >&2; exit 2; }

# A bare folder name only. This guards the rm -rf below: no slashes, no dots,
# no empty value can reach it, so the target is always one child of SESSIONS.
case "$FOLDER" in */*|"."|".."|"") echo "close.sh: --folder must be a bare folder name" >&2; exit 2 ;; esac

# A folder already gone is not an error when a lock still names it. That is the
# stale-lock case, and clearing the block is the whole job. Refusing here would
# leave the block with no sanctioned route to remove it.
D="$SESSIONS/$FOLDER"
FOLDER_GONE=0
if [ ! -d "$D" ]; then
  if grep -q "sessions/$FOLDER/" "$LOCKFILE" 2>/dev/null; then
    FOLDER_GONE=1
  else
    echo "close.sh: $D not found, and no lock block names it" >&2
    exit 3
  fi
fi

# ---- 1. Archive ---------------------------------------------------------
if [ -n "$BLOCK" ]; then
  [ -f "$BLOCK" ] || { echo "close.sh: archive block file not found: $BLOCK" >&2; exit 8; }
  DAY="$ARCHIVE/$(date +%F).md"
  [ -f "$DAY" ] || printf '# %s\n' "$(date +%F)" > "$DAY"
  # Reject a block carrying paths, links, filenames, PR numbers, or SHAs — the
  # archive forbids them. Both patterns below are deliberately narrow: a false
  # reject is worse than a miss, because its message names a cause the writer
  # cannot find. "he/she" is not a path, and "1234567" is not a SHA.
  reject=""
  # A slash counts as a path only when a segment beside it carries a digit,
  # dot, underscore or hyphen. Prose alternatives never do.
  if grep -qE '\[\[|\]\]|\.(md|sh|py|json|ya?ml|ts|tsx|js)\b|\bPR #|[a-zA-Z0-9_.-]*[0-9._-][a-zA-Z0-9_.-]*/|/[a-zA-Z0-9_.-]*[0-9._-]' "$BLOCK"; then
    reject="a path, link, filename, or PR number"
  # A SHA is 7-40 hex characters carrying at least one letter. A plain number
  # of any length is a figure, and figures belong in the archive.
  elif grep -oE '\b[0-9a-f]{7,40}\b' "$BLOCK" | grep -q '[a-f]'; then
    reject="a commit SHA"
  fi
  if [ -n "$reject" ]; then
    echo "close.sh: the archive block contains $reject." >&2
    echo "close.sh: the archive is pure prose. Rewrite it in words, then re-run." >&2
    exit 8
  fi
  { printf '\n'; cat "$BLOCK"; printf '\n'; } >> "$DAY"
  echo "ARCHIVED=$DAY"
else
  echo "ARCHIVED=none"
fi

# ---- 2. The session folder ---------------------------------------------
if [ "$FOLDER_GONE" -eq 1 ]; then
  echo "FOLDER_REMOVED=no — already gone; clearing the lock only"
else
  rm -rf "$D"
  echo "FOLDER_REMOVED=$D"
fi

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

# ---- 5. The claimed prompt ----------------------------------------------
# A bare basename only, resolved inside PROMPTS. The same guard shape as the
# folder: no slashes, no dots, so the target is always one child of PROMPTS.
if [ -n "$PROMPT" ]; then
  case "$PROMPT" in */*|"."|".."|"") echo "PROMPT_REMOVED=no — --prompt must be a bare filename" ;; *)
    P="$PROMPTS/$PROMPT"
    if [ -f "$P" ]; then
      if git -C "$PROMPTS" ls-files --error-unmatch "$PROMPT" >/dev/null 2>&1; then
        git -C "$PROMPTS" rm -q -- "$PROMPT"
      else
        rm -f "$P"
      fi
      echo "PROMPT_REMOVED=$P"
    else
      echo "PROMPT_REMOVED=no — $P not found"
    fi
  esac
fi
