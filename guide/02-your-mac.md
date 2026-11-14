# 02 — Your Mac

What your Mac needs before my layer runs, and three settings.

## What it needs

| What | Why my layer needs it | Where it expects it |
|---|---|---|
| macOS | Typing into panes, waiting on files, background jobs | Any recent macOS |
| iTerm2 | Every pane: opening it, typing into it, naming it, splitting it | `/Applications/iTerm.app` |
| Claude Code | Every session. From 2.1.283, auto mode starts by itself | `claude` on your PATH, or `~/.local/bin/claude` |
| Python 3.10 or newer | Every hook, library module and tool | The first `python3` on your PATH |
| Node, with `npx` | Each session's own browser, Playwright | The PATH Claude Code sees |
| git | `/8-ship`, the behaviour doctor, and taking my layer | Your PATH |
| zsh | Every pane's shell | macOS's default shell |

Your PATH is the list of folders your shell searches for a command.

Your Mac is a recent Apple-silicon one. Homebrew's place there is `/opt/homebrew`, where my layer expects it. Homebrew first, then Python and Node through it, is the short way.

No `jq` is needed: my status line runs on Python alone.

Optional, each for one comfort:

| What | For |
|---|---|
| Google Chrome, with the Claude in Chrome extension | `/drive-chrome`: a session driving your own Chrome, with your logins. Document 15 |
| pnpm | The prototypes app my walk built. Document 16 |
| Tailscale, and librsvg | 1100 on your phone, with its icon |

The Chrome extension signs into one of your Claude accounts: the one that drives your Chrome. That is account 1, unless document 04 names another.

Install what is missing, your own way.

## Three settings

**iTerm2's Python API** (your hands). In iTerm2: Settings, General, Magic, "Enable Python API". My layer reads iTerm2's layout, splits panes and rearranges them through it. The Python package must be version 1.14 or newer.

**Python first on your PATH.** Every hook starts with `#!/usr/bin/env python3`. macOS's own Python is 3.9.6, and my hooks fail under it. The first `python3` your PATH finds must be 3.10 or newer.

**Auto mode.** From Claude Code 2.1.283, a session in a terminal starts in auto mode by itself. Nothing to set. My walks met no permission prompt.

An older Claude Code needs one line in each account's own settings file:

```
"permissions": {"defaultMode": "auto"}
```

Account 1's file is `~/.claude/settings.json`. A second account's sits in its own folder: document 04. If the file already holds a `"permissions"` entry, add `"defaultMode": "auto"` inside it.

Without it, on an older Claude Code, each permission prompt holds its session until your hand answers it.

Your project's `.claude/settings.json` can never set it. Claude Code ignores auto mode there.

## Unproven here

- Installing any of these. My walks ran on a Mac that already held them all.
- Rearranging panes, and the Python package version it needs. No walk tested either.
- Auto mode with no line at all. Every account in my walks also held the line.

## Check

In a new iTerm2 pane, type:

```
which python3 claude node npx; python3 --version; claude --version
```

- Each name prints a path.
- Python prints 3.10 or newer.
- Claude Code prints its version. Below 2.1.283, auto mode needs its line.

Then, in iTerm2's Settings, "Enable Python API" shows on. Document 04 installs the Python package when you first open a launch page.
