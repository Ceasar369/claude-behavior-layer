#!/bin/bash
# guard-destructive.sh — PreToolUse(Bash) guard.
# Registered session-wide in settings.json, AND declared in the frontmatter of
# every executor agent. Session-wide matters because /8-ship runs git in the main
# session rather than in a subagent.
# Blocks destructive / privileged shell deterministically, whatever the prompt says.
# Exit 2 blocks the tool and returns the reason so the agent escalates.
# Reads the hook JSON on stdin.
#
# Backstop, not a sandbox: pattern-based, evadable by a determined command. The
# durable controls are the agent's tool list and permissionMode. Defense-in-depth.

input=$(cat)
cmd=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.command // ""')

# EVERY directly-typed `rm` is blocked — bare, -f, -r, -rf, single file or glob.
#
# Flags are the wrong axis. `rm -f dir/*` carries no `-r`, and the shell expands the
# glob before rm sees it, so a flag-based rule waves through a whole flat directory.
# Not every tree under a repo root is committed, and an uncommitted one has no copy.
#
# Blocking all of it costs almost nothing, because the guard only ever sees the typed
# string. Every legitimate delete in this layer already lives inside a script —
# close.sh, teardown.sh, boot.sh, locks.sh, worktree.sh, flatten.sh, clean.sh — and a
# script's internals are invisible to a hook reading `.tool_input.command`. So the rule
# is simply: deletion goes through a script that bounds its own target.
#
# `git clean` deletes untracked files, which git has no copy of. At a repo root that
# is every uncommitted and every ignored tree, and neither is recoverable. Blocked
# unless it carries `-n` or `--dry-run`, which only lists.
#
# Both `rm` and `git clean` must sit in COMMAND POSITION to match — line start, or after
# `;`, `&`, `|`, `(`. Either name appears in prose constantly, and an echo or a grep
# pattern mentioning one is not a delete. `xargs rm` and `find -exec rm` are matched
# separately: those ARE command position, reached by a route the separator list cannot see.
#
# `git rm` is not `rm`. It removes TRACKED files through the index, so the content
# stays recoverable from history. A package manager's `rm` subcommand removes a
# dependency, never a file. Both are masked before matching, so `git rm -r --cached
# <path>` and `pnpm rm <pkg>` pass while a bare `rm <path>` does not.
scan=$(printf '%s' "$cmd" | sed -E 's/(git|npm|pnpm|yarn|bun|cargo|uv|poetry|pip|brew|apk)[[:space:]]+rm/TOOL_RM/g')

# `git clean` is a delete with no index copy to recover from. A dry run only lists,
# so mask that form out before the match below sees it.
scan=$(printf '%s' "$scan" | sed -E 's/git[[:space:]]+clean[[:space:]][^;&|]*(-[a-z]*n|--dry-run)/GIT_CLEAN_DRYRUN/g')

# Destructive / privileged commands never run unattended.
if printf '%s' "$scan" | grep -Eiq '(^|[;&|(])[[:space:]]*git[[:space:]]+clean([[:space:]]|$)|(^|[;&|(])[[:space:]]*rm([[:space:]]|$)|(xargs|-exec|-execdir)[[:space:]]+rm([[:space:]]|$)|(^|[[:space:]])sudo[[:space:]]|git[[:space:]]+push[[:space:]].*(--force|-f([[:space:]]|$))|(^|[[:space:]])mkfs|(^|[[:space:]])dd[[:space:]].*of=/dev/|>[[:space:]]*/dev/(disk|rdisk|sd|nvme|hd)'; then
  echo "Blocked: destructive command not allowed. For a delete: use \`git rm\` on a tracked file, or a script that bounds its own target. Otherwise stop and ask the user." >&2
  exit 2
fi

exit 0
