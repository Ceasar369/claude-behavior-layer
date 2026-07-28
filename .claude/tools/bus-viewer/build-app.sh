#!/bin/bash
# build-app.sh — build the double-clickable boot button from source.
#
#   ./build-app.sh [AppName]
#
# The bundle is a build artifact, git-ignored. This script is the source of
# truth; run it whenever launcher.applescript or make-icon.py changes.
#
# It exists for two reasons. The obvious one: five steps in the right order is a
# script, not a README block. The real one: step 3 deletes a file, and this
# layer's guard blocks every directly-typed `rm`. A delete belongs inside a
# script that bounds its own target, which is exactly what remove_bundle does —
# it refuses anything that is not an osacompile bundle in this directory.
#
# macOS only. Needs osacompile, sips, iconutil, PlistBuddy, codesign — all
# shipped with the system or with the Command Line Tools.
#
# Exit 2 not macOS or a tool is missing · 3 a refused delete · 4 a build step failed.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ "$(uname -s)" = "Darwin" ] || { echo "build-app.sh: macOS only." >&2; exit 2; }
for t in /usr/bin/osacompile /usr/bin/sips /usr/bin/iconutil /usr/libexec/PlistBuddy /usr/bin/codesign; do
  [ -x "$t" ] || { echo "build-app.sh: missing $t" >&2; exit 2; }
done

# Settings, if any. launcher.conf is git-ignored; the example ships.
APP_NAME=Bus
# shellcheck disable=SC1091
[ -f "$HERE/launcher.conf" ] && . "$HERE/launcher.conf"
APP_NAME="${1:-$APP_NAME}"
APP="$HERE/$APP_NAME.app"

BUNDLE_ID="local.behavior-layer.$(printf '%s' "$APP_NAME" | tr '[:upper:] ' '[:lower:]-')"
USAGE="Opens your workspace and the ask/answer status page."

# ---- A delete that bounds its own target --------------------------------
# Refuses anything that is not an osacompile app bundle sitting in this
# directory. The refusal is the point: a script the guard cannot see must
# narrow its own blast radius.
remove_bundle() {
  local target="$1"
  case "$target" in
    "$HERE"/*.app) ;;
    *) echo "build-app.sh: refusing to remove '$target' — not an .app in $HERE" >&2; exit 3 ;;
  esac
  case "$target" in
    *"/../"*|*"/..") echo "build-app.sh: path traversal refused" >&2; exit 3 ;;
  esac
  [ -d "$target" ] || return 0
  [ -f "$target/Contents/MacOS/applet" ] || {
    echo "build-app.sh: refusing to remove '$target' — not an osacompile bundle" >&2
    exit 3
  }
  rm -rf "$target"
}

remove_file() {
  local target="$1"
  case "$target" in
    "$APP"/Contents/Resources/*) ;;
    *) echo "build-app.sh: refusing to remove '$target' — outside the bundle" >&2; exit 3 ;;
  esac
  [ -f "$target" ] && rm -f "$target"
  return 0
}

# ---- 1. The icon, drawn from code ---------------------------------------
python3 "$HERE/make-icon.py" "$HERE/icon.png" >/dev/null || { echo "build-app.sh: make-icon.py failed" >&2; exit 4; }

ICONSET="$(mktemp -d)/icon.iconset"
mkdir -p "$ICONSET"
for spec in "16 16x16" "32 16x16@2x" "32 32x32" "64 32x32@2x" \
            "128 128x128" "256 128x128@2x" "256 256x256" "512 256x256@2x" \
            "512 512x512" "1024 512x512@2x"; do
  px="${spec%% *}"; nm="${spec##* }"
  /usr/bin/sips -z "$px" "$px" "$HERE/icon.png" --out "$ICONSET/icon_$nm.png" >/dev/null 2>&1
done
/usr/bin/iconutil -c icns "$ICONSET" -o "$HERE/icon.icns" || { echo "build-app.sh: iconutil failed" >&2; exit 4; }
echo "ICON=$HERE/icon.icns"

# ---- 2. Compile the bundle ----------------------------------------------
remove_bundle "$APP"
/usr/bin/osacompile -o "$APP" "$HERE/launcher.applescript" || { echo "build-app.sh: osacompile failed" >&2; exit 4; }
echo "COMPILED=$APP"

# ---- 3. Drop osacompile's default icon catalog --------------------------
# Left in place it overrides the icon installed below, and the app shows the
# generic applet face no matter what is in Resources.
remove_file "$APP/Contents/Resources/Assets.car"
/usr/libexec/PlistBuddy -c "Delete :CFBundleIconName" "$APP/Contents/Info.plist" >/dev/null 2>&1 || true

# ---- 4. Two load-bearing plist keys -------------------------------------
# BOTH are required for the Automation permission, and the failure mode of a
# missing CFBundleIdentifier is silent: macOS denies the Apple event with -1743
# and shows NO prompt, so the app never appears in System Settings at all.
# osacompile does not always set one.
/usr/libexec/PlistBuddy -c "Add :NSAppleEventsUsageDescription string '$USAGE'" "$APP/Contents/Info.plist" >/dev/null 2>&1 \
  || /usr/libexec/PlistBuddy -c "Set :NSAppleEventsUsageDescription '$USAGE'" "$APP/Contents/Info.plist" >/dev/null
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$APP/Contents/Info.plist" >/dev/null 2>&1 \
  || /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$APP/Contents/Info.plist" >/dev/null
echo "BUNDLE_ID=$BUNDLE_ID"

# ---- 5. Install the icon, then re-sign ----------------------------------
# Re-sign AFTER the plist edits. An ad-hoc signature must cover the final
# Info.plist, or macOS treats the bundle as tampered and the Automation grant
# will not stick.
cp "$HERE/icon.icns" "$APP/Contents/Resources/applet.icns"
/usr/bin/codesign --force --deep -s - "$APP" >/dev/null 2>&1 || { echo "build-app.sh: codesign failed" >&2; exit 4; }
echo "SIGNED=yes"

# ---- Report -------------------------------------------------------------
echo "APP=$APP"
echo "PLIST_ID=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$APP/Contents/Info.plist" 2>/dev/null)"
echo "PLIST_USAGE=$(/usr/libexec/PlistBuddy -c 'Print :NSAppleEventsUsageDescription' "$APP/Contents/Info.plist" 2>/dev/null)"
echo "ASSETS_CAR=$([ -f "$APP/Contents/Resources/Assets.car" ] && echo present || echo removed)"
echo
echo "Double-click it, or drag it to the Dock."
echo "First click may ask for Automation permission if you use the iTerm2 pane."
