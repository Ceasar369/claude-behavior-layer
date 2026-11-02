#!/usr/bin/env python3
"""open.py — what one click on the project's app, in my Dock, does.

The launcher is optional. Its editor and workspace file are the project's,
as .claude/project.json names them under dock, and the app wears the
project's name.

1100 comes up first when it is down, and alone. serve.start is the half
of /00-sessions-dashboard that starts 1100. The band is its other half,
and nothing here calls it. A 1100 already answering is left alone. One
project runs at a time: another project's 1100 answering refuses the
click, naming it.

The editor opens the workspace, or the project's folder when none is
named, behind. Naming no editor, the click opens none. Naming Cursor,
a Cursor already showing the workspace only shows it again, and
opens no second window. Cursor's own launcher does it: a plain open of the
workspace lands in Cursor's Agents window, and --classic sends it to the
editor instead.

Then iTerm2 shows my workspace: one window, full screen, 1100 in a
browser pane on the left, a terminal in this repository on the right.
iTerm2 starts first when it is not running.

A window already open comes forward, and no second one opens. Its browser
pane wears user.dock, set when it opened. That is how it is found. Here it
becomes iTerm2's front window. launcher.applescript then brings iTerm2
itself forward.

launcher.applescript runs this with Homebrew's python3, the one 1100 runs
on. The window half needs the iterm2 package, so it runs again, in the
venv lib/iterm.py keeps.

  open.py           the click
  open.py window    the window half, in iTerm2's venv
"""

import os
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import iterm  # noqa: E402
import project  # noqa: E402
import serve  # noqa: E402

DASHBOARD = os.path.join(ROOT, ".claude", "tools", "sessions-dashboard.py")
# 1100's own name for its pid and log, the one the hook starts it under.
SKILL = "sessions-dashboard"
URL = f"http://localhost:{serve.PORT}"
WORKSPACE = project.WORKSPACE
# The command that opens a file in the editor, its flags included.
EDITOR = project.EDITOR
ITERM = "com.googlecode.iterm2"
MARK, NAME = "user.dock", project.NAME
# A window half still waiting after this long is stuck, and gives up:
# iTerm2 never came up, or it was refused the permission it asks for.
WAIT = 60


def running() -> bool:
    """Whether iTerm2 is up. The question reaches no app, so it asks no permission."""
    r = subprocess.run(["/usr/bin/osascript", "-e", f'application id "{ITERM}" is running'],
                       capture_output=True, text=True)
    return r.stdout.strip() == "true"


def click() -> None:
    problem = project.refusal(serve.PORT) or serve.start(SKILL, serve.PORT, DASHBOARD)
    if problem:
        sys.exit(problem)
    # The editor starts behind: iTerm2 comes forward last.
    if EDITOR:
        subprocess.run([*EDITOR, WORKSPACE])
    if not running():
        subprocess.run(["/usr/bin/open", "-b", ITERM])
    if not iterm.ready():
        sys.exit("iTerm2's venv could not be made.")
    sys.exit(subprocess.run([iterm.PYTHON, os.path.abspath(__file__), "window"]).returncode)


def window() -> None:
    import iterm2

    async def mine(app):
        """The window this app opened, or None."""
        for w in app.terminal_windows:
            for t in w.tabs:
                for s in t.sessions:
                    if await s.async_get_variable(MARK) == NAME:
                        return w
        return None

    async def opened(connection, app):
        """A new window, full screen: 1100 on the left, a terminal in this repository on the right."""
        page = iterm2.LocalWriteOnlyProfile({"Custom Command": "Browser", "Initial URL": URL})
        made = await iterm2.Window.async_create(connection, profile_customizations=page)
        # A new window comes back before iTerm has told the app about its
        # tab, so the app is read again before the tab is asked for.
        await app.async_refresh()
        win = app.get_window_by_id(made.window_id)
        left = win.tabs[0].sessions[0]
        await left.async_set_variable(MARK, NAME)
        shell = iterm2.LocalWriteOnlyProfile({"Custom Directory": "Yes", "Working Directory": ROOT})
        await left.async_split_pane(vertical=True, profile_customizations=shell)
        await win.async_set_fullscreen(True)
        return win

    async def run(connection):
        app = await iterm2.async_get_app(connection)
        win = await mine(app) or await opened(connection, app)
        await win.async_activate()

    signal.alarm(WAIT)
    iterm2.run_until_complete(run, retry=True)


if __name__ == "__main__":
    window() if sys.argv[1:] == ["window"] else click()
