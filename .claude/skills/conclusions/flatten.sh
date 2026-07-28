#!/usr/bin/env bash
# Flattens one Claude Code session transcript into a numbered, gate-aware clean file.
# Usage: flatten.sh [session-id-or-prefix]   (omit to use the current session)
#
# Captures, per turn: prose text, every AskUserQuestion gate asked, and every gate
# answer correlated by tool_use_id. Tags harness notifications so they are never
# mistaken for the user. Turn markers use @@TURN@@ so prose headings cannot forge one.
#
# Prints KEY=VALUE lines the caller must read. Exits non-zero on every failure.
set -uo pipefail

SID="${1:-${CLAUDE_CODE_SESSION_ID:-}}"
[ -n "$SID" ] || { echo "FAIL: no session id given and CLAUDE_CODE_SESSION_ID is unset" >&2; exit 2; }

BASE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
case "$BASE" in /*) ;; *) BASE="$HOME/$BASE";; esac
D="$BASE/projects/$(echo "$PWD" | sed 's|/|-|g')"

T="$D/$SID.jsonl"
if [ ! -f "$T" ]; then
  n=$(ls "$D"/"$SID"*.jsonl 2>/dev/null | wc -l | tr -d ' ')
  case "$n" in
    1) T=$(ls "$D"/"$SID"*.jsonl) ;;
    0) echo "FAIL: no transcript matching '$SID' in $D" >&2; exit 3 ;;
    *) echo "FAIL: '$SID' matches $n transcripts — give more characters" >&2; exit 3 ;;
  esac
fi

CLEAN="${TMPDIR:-/tmp}/conclusions-$(basename "$T" .jsonl).txt"
trap 'rm -f "$CLEAN.part"' EXIT

jq -rn '
  [inputs]
  | map(select((.type=="user" or .type=="assistant") and (.isMeta != true) and (.isSidechain != true)))
  | . as $all
  | ([ $all[] | (.message.content) as $c
       | (if ($c|type)=="string" then [] else ($c // []) end)
       | .[] | select(.type=="tool_use" and .name=="AskUserQuestion") | .id ]) as $gateids
  | $all
  | map(
      (.message.content) as $c
      | (if ($c|type)=="string" then [{type:"text",text:$c}] else ($c // []) end) as $b
      | ($b | map(select(.type=="text") | .text) | join("\n")) as $txt
      | {
          role: (if .type=="user"
                   and ($txt|test("SYSTEM NOTIFICATION|<task-notification>|^<system-reminder>"))
                 then "SYSTEM-NOT-USER" else .type end),
          txt: $txt,
          asked: ($b | map(select(.type=="tool_use" and .name=="AskUserQuestion")
                    | (.input.questions // [])
                    | map("[GATE ASKED] \(.header): \(.question) :: \((.options//[])|map(.label)|join(" | "))"))
                  | flatten),
          answered: ($b | map(select(.type=="tool_result" and ([.tool_use_id] | inside($gateids)))
                       | "[GATE ANSWERED] " + (.content|tostring)))
        })
  | map(select((.txt|gsub("\\s";"")) != "" or (.asked|length)>0 or (.answered|length)>0))
  | to_entries
  | map("@@TURN@@ \(.key+1) — \(.value.role)\n"
        + (if (.value.txt|gsub("\\s";"")) != "" then .value.txt+"\n" else "" end)
        + (if (.value.asked|length)>0    then (.value.asked|join("\n"))+"\n" else "" end)
        + (if (.value.answered|length)>0 then (.value.answered|join("\n"))+"\n" else "" end))
  | .[]' "$T" > "$CLEAN.part" || { echo "FAIL: jq could not parse $T" >&2; exit 4; }

mv "$CLEAN.part" "$CLEAN"

turns=$(grep -c '^@@TURN@@' "$CLEAN" || true)
if [ "${turns:-0}" -lt 1 ]; then
  rm -f "$CLEAN"
  echo "FAIL: 0 turns extracted from $T" >&2
  exit 5
fi

echo "CLEAN=$CLEAN"
echo "SOURCE=$T"
echo "TITLE=$(jq -rn 'last(inputs | select(.type=="custom-title") | .customTitle) // "(untitled)"' "$T" 2>/dev/null)"
echo "TURNS=$turns"
# Two different units, deliberately named apart. One gate call can carry several
# questions, so QUESTIONS_ASKED routinely exceeds GATES_ANSWERED with nothing wrong.
# A withdrawal is an unanswered gate, found by reading — never by comparing these.
echo "QUESTIONS_ASKED=$(grep -c 'GATE ASKED' "$CLEAN" || true)"
echo "GATES_ANSWERED=$(grep -c 'GATE ANSWERED' "$CLEAN" || true)"
echo "NON_USER_TURNS=$(grep -c 'SYSTEM-NOT-USER' "$CLEAN" || true)"
echo "APPROX_TOKENS=$(( $(wc -w <"$CLEAN") * 4 / 3 ))"
