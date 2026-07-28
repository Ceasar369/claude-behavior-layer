#!/bin/bash
# clean.sh — remove the clean file flatten.sh wrote. Nothing else.
#
# Usage: clean.sh <path>
#
# Every other destructive operation in this layer lives inside a script, so the
# Bash guard sees only the invocation and never the delete. These two callers —
# /conclusions and /realign — were the sole outliers typing `rm` directly. This
# script makes them conform, which lets the guard block every directly-typed rm.
#
# It refuses anything that is not a flatten.sh clean file. The refusal is the
# point: a script the guard cannot see must narrow its own blast radius.
#
# Prints REMOVED= or ABSENT=.
# Exit 2 bad arguments · 3 the path is not a clean file.

set -euo pipefail

TARGET="${1:-}"
[ -n "$TARGET" ] || { echo "clean.sh: a path is required" >&2; exit 2; }

# flatten.sh writes to "${TMPDIR:-/tmp}/conclusions-<session>.txt" and nowhere else.
case "$(basename "$TARGET")" in
  conclusions-*.txt) ;;
  *) echo "clean.sh: not a flatten.sh clean file: $TARGET" >&2; exit 3 ;;
esac
case "$TARGET" in
  */*) ;;
  *) echo "clean.sh: an absolute path is required" >&2; exit 3 ;;
esac
case "$TARGET" in
  *"/../"*|*"/..") echo "clean.sh: path traversal refused" >&2; exit 3 ;;
esac

if [ -e "$TARGET" ]; then
  [ -f "$TARGET" ] || { echo "clean.sh: not a regular file: $TARGET" >&2; exit 3; }
  rm -f "$TARGET"
  echo "REMOVED=$TARGET"
else
  echo "ABSENT=$TARGET"
fi
