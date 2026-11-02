#!/usr/bin/env python3
"""build.py — make the project's Dock app beside this file, from its source.

The app is a build, kept out of git. It wears the project's name, as
.claude/project.json names it, like My App.app. Run this again when
launcher.applescript changes, or 1100's icon does.

  build.py

Its icon is 1100's, the one my iPhone shows: sessions-dashboard.py's TOUCH,
wearing the rocket page.PATHS["launch"] draws. librsvg draws it at every
size a Mac app icon needs, and iconutil packs them.

osacompile makes the app from launcher.applescript. Its own icon catalog
goes, or it would cover ours. A bundle identifier is set, so macOS can ask
me once whether the app may control iTerm2. The app is signed again last,
so the signature covers every change, and that permission holds.
"""

import importlib.util
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(TOOLS), "lib"))
import project  # noqa: E402

APP = os.path.join(HERE, f"{project.NAME}.app")
SOURCE = os.path.join(HERE, "launcher.applescript")
BUNDLE_ID = "local.{}.sessions-infra".format(re.sub(r"[^a-z0-9]+", "-", project.NAME.lower()).strip("-"))
RSVG = "/opt/homebrew/bin/rsvg-convert"
# Every picture a Mac app icon holds: its name in the iconset, and its side in pixels.
SIZES = [(f"icon_{s}x{s}{'@2x' if k == 2 else ''}.png", s * k)
         for s in (16, 32, 128, 256, 512) for k in (1, 2)]


def icon_svg() -> str:
    """1100's icon, as touch_icon() draws it."""
    spec = importlib.util.spec_from_file_location(
        "sessions_dashboard", os.path.join(TOOLS, "sessions-dashboard.py"))
    dashboard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dashboard)
    return dashboard.TOUCH.format(dashboard.page.PATHS["launch"])


def icns(svg: str, into: str) -> str:
    """The icon at every size, packed into one .icns inside `into`."""
    iconset = os.path.join(into, "icon.iconset")
    os.makedirs(iconset)
    for name, px in SIZES:
        subprocess.run([RSVG, "-w", str(px), "-h", str(px), "-o", os.path.join(iconset, name)],
                       input=svg.encode(), check=True)
    out = os.path.join(into, "icon.icns")
    subprocess.run(["/usr/bin/iconutil", "-c", "icns", iconset, "-o", out], check=True)
    return out


def main() -> None:
    svg = icon_svg()
    with tempfile.TemporaryDirectory(dir=HERE) as scratch:
        icon = icns(svg, scratch)
        if os.path.isdir(APP):
            shutil.rmtree(APP)
        subprocess.run(["/usr/bin/osacompile", "-o", APP, SOURCE], check=True)
        res = os.path.join(APP, "Contents", "Resources")
        car = os.path.join(res, "Assets.car")
        if os.path.exists(car):
            os.remove(car)
        shutil.copyfile(icon, os.path.join(res, "applet.icns"))
    info = os.path.join(APP, "Contents", "Info.plist")
    with open(info, "rb") as f:
        plist = plistlib.load(f)
    plist.pop("CFBundleIconName", None)
    plist["CFBundleIdentifier"] = BUNDLE_ID
    with open(info, "wb") as f:
        plistlib.dump(plist, f)
    subprocess.run(["/usr/bin/codesign", "--force", "--deep", "-s", "-", APP], check=True)
    print(APP)


if __name__ == "__main__":
    main()
