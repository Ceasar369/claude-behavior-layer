#!/bin/bash
# archive-init.sh — SessionStart hook.
# Creates today's archive file (archive/YYYY-MM-DD.md) if it is absent.
# Idempotent: never overwrites an existing file. Always exits 0.
#
# Paths come from paths.sh, never from CLAUDE_PROJECT_DIR. That variable
# resolves against the session's working directory, so a session started in a
# subfolder once wrote the archive one level deep. paths.sh derives the root
# from this file's own location, which no working directory can shift.
set -e

source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh"

TODAY="$(date +%F)"
ARCHIVE_FILE="$ARCHIVE/$TODAY.md"

mkdir -p "$ARCHIVE"
[ -f "$ARCHIVE_FILE" ] || printf '# %s\n' "$TODAY" > "$ARCHIVE_FILE"

exit 0
