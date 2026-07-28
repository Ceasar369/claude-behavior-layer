#!/bin/bash
# session-markers.sh — SessionEnd hook. Clears this session's identity file.
#
# boot.sh writes .claude/state/<session_id>, holding this session's folder name.
# It is the one place a skill or a hook can learn that name from a session id
# alone, so it must not outlive the session that owns it.
#
# A crash never reaches SessionEnd, so a sweep backstops the targeted delete:
# a file older than one day belongs to a session that is certainly gone.
#
# SessionEnd is side-effects only — its exit code and output are ignored.
# Always exits 0. Never blocks anything.

source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh" 2>/dev/null || exit 0

input=$(cat 2>/dev/null || true)
sid=$(printf '%s' "$input" | /usr/bin/jq -r '.session_id // ""' 2>/dev/null || true)

[ -n "$sid" ] && rm -f "$STATE/$sid"

[ -d "$STATE" ] && find "$STATE" -type f -mtime +1 ! -name '.gitkeep' -delete 2>/dev/null

exit 0
