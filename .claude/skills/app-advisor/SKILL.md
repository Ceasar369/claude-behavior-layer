---
name: app-advisor
description: Readies this Claude desktop chat to run my-advisor, with 1100 open beside it and driven through its own code.
allowed-tools: Read, Glob, Grep, Bash, Skill
argument-hint: "[words — my first matter; without them, it waits for one]"
---

# App Advisor

This chat sits in Claude's desktop window, beside my sessions, never inside one.

## Step 1 — Check where you run

1. Run `echo $CLAUDE_CODE_ENTRYPOINT`.
2. It is not `claude-desktop` → say "app-advisor runs only in Claude's desktop window. Here, type /my-advisor." Stop.

## Step 2 — Open 1100 beside you

1. Run `python3 .claude/tools/sessions-dashboard.py status`.
2. It is not up → say "1100 is down. Type /00-sessions-dashboard." Stop.
3. Open the address it prints in the browser pane, with `preview_start`.
4. Read the docstring of `.claude/tools/sessions-dashboard.py`. It names every page, and the tool that draws and takes it.

## Step 3 — Know what differs here

1. This chat holds no number, no pane and no record. Never claim one.
2. No session can type into this chat. Read a session's answer in its transcript.
3. This chat's account is `account()`'s answer, in `.claude/lib/registry.py`.
4. Read a session's state with `colours()`, in `.claude/lib/page.py`.
5. Read any other page through the tool that draws it, as the docstring names.
6. Act as a page's button acts: through that tool's own code.
7. A launch goes through my own launch page, `/p/launch/00`, as `.claude/tools/launch-page.py` takes it. Never `launch.py`.
8. No code reaches it → open the page at its own address, never through 1100's home, and press it there.
9. A screenshot only looks. Read and press through scripts.
10. An act that needs a session number → ask me first.
11. `/my-advisor`'s fresh advisor needs a number and `launch.py`, and its second chore copies into its own folder. This chat skips both. Told "start a fresh advisor" → say "Here, a fresh advisor is a new chat. Open one, and type /app-advisor." Its first chore needs neither: run it as it says.

## Step 4 — Be my advisor

1. Read `.claude/skills/my-advisor/SKILL.md`. Follow it from its Step 2, with my words. Its Step 1 takes a seat, and this chat holds none.
2. Where it says this session, it means this chat.
