#!/usr/bin/env bash
# Lists this project's session transcripts, newest first, with their renamed titles.
# Usage: list-sessions.sh [count]   (default 15)
set -uo pipefail

N="${1:-15}"
BASE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
case "$BASE" in /*) ;; *) BASE="$HOME/$BASE";; esac
D="$BASE/projects/$(echo "$PWD" | sed 's|/|-|g')"

[ -d "$D" ] || { echo "FAIL: no project transcript dir at $D" >&2; exit 1; }

printf '%-16s  %-8s  %8s  %s\n' "MODIFIED" "ID" "SIZE" "TITLE"
ls -t "$D"/*.jsonl 2>/dev/null | head -"$N" | while read -r f; do
  id=$(basename "$f" .jsonl)
  title=$(jq -rn 'last(inputs | select(.type=="custom-title") | .customTitle) // ""' "$f" 2>/dev/null)
  [ -z "$title" ] && title="(untitled)"
  printf '%-16s  %-8s  %7sK  %s\n' \
    "$(date -r "$f" '+%Y-%m-%d %H:%M')" \
    "${id:0:8}" \
    "$(( $(wc -c <"$f") / 1024 ))" \
    "$title"
done
