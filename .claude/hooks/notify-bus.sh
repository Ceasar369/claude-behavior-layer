#!/bin/bash
# notify-bus.sh — PostToolUse(Bash) alert for ask/answer traffic.
# Fires a desktop notification when /2-ask writes a question, or /3-answer writes
# one back, so a session blocked in another window does not go unnoticed.
#
# ALERT-ONLY, turn-based safe: it inspects the command string to decide WHETHER
# to alert. It never reads message contents, never pulls anything, never
# delivers across sessions, never runs /4-inbox. You still control the tempo.
# Hooks are session-isolated — this cannot move a message; it only surfaces
# that one was written.
#
# It matches the bus.py subcommand rather than a file path, because bus.py takes
# the session and slug as arguments and builds the path itself. The read
# subcommand renames an answer already seen, so it deliberately does not alert.
#
# Reads the hook JSON on stdin. Always exits 0 — PostToolUse cannot block.

source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh" 2>/dev/null || exit 0

input=$(cat)
cmd=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.command // ""' 2>/dev/null || true)

case "$cmd" in
  *bus.py*" ask "*)    kind=ask ;;
  *bus.py*" answer "*) kind=answer ;;
  *) exit 0 ;;
esac

if [ "$kind" = ask ]; then
  msg="A session has a question — /3-answer it"
else
  slug=$(printf '%s' "$cmd" | sed -n 's/.*bus\.py[[:space:]][[:space:]]*answer[[:space:]][[:space:]]*\([A-Za-z0-9._-]*\).*/\1/p' | head -n1)
  if [ -n "$slug" ]; then msg="Answered — run /4-inbox in ${slug}";
  else msg="Answered — run /4-inbox in that session"; fi
fi

title="$(basename "$ROOT")"

# Best effort, on whatever the machine has. Silence is an acceptable outcome —
# this hook must never fail a tool call.
if [ -x /usr/bin/osascript ]; then
  /usr/bin/osascript -e "display notification \"${msg}\" with title \"${title}\"" >/dev/null 2>&1 || true
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "$title" "$msg" >/dev/null 2>&1 || true
fi

exit 0
