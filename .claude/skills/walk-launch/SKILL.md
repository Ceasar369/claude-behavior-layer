---
name: walk-launch
description: Puts my walk's walker and my reader on this session's launch page, passes the walker my word and the reader each page to read, and keeps the walker's evidence when the walk ends. The walk's lead runs it.
allowed-tools: Read, Write, Bash, Skill
argument-hint: "[an area] · or [walk <a journey> | walk <a journey> again | answer <my words> | read <area>/<section> · <a docs step> | end the walk], once a walker runs — the walk is this session's walk-list.md; the area omitted, ask me which"
---

# Walk Launch

You are my walk's lead. You launch its walker, and pass it my word. You launch my reader, and hand it each page to read. You never drive either.

NN is your number, as `CLAUDE.md` defines it.

## Step 1 — A walker runs already?

1. Read each `.claude/state/sessions/*/walk.json` but your own. One whose `"main"` is NN is your walker, WW. Read each `.claude/state/sessions/*/read.json`. One whose `"main"` is NN is your reader, RR.
2. My words, or `7-walk`'s, read a docs step → Step 5.
3. None, and no area named → ask me which, and stop. None → Step 2. One, and my words name a journey to walk, or answer its question → Step 3. One, and my words end the walk → Step 4.

## Step 2 — Put it on the launch page

1. Read `.claude/state/sessions/NN/walk-list.md`: its title is the walk's name.
2. Read `.claude/state/sessions/NN/launch.json` when it exists. Keep its rows.
3. Add one row, as `launch` Step 4 rules: `{"name": "<the walk's name, three words at most> walker", "model": "sonnet", "effort": "low", "message": "/walk-drive <area>. Report to session NN."}`. No account: I pick it.
4. Say the row in one line. Your move: "Action: pick the walker's account, then press Launch on 1100."

## Step 3 — Pass my word

1. Only my own words in this turn send it. Never on your own.
2. Type it: `python3 .claude/tools/panes.py say --to WW --line "Walk <the journey>."`, or "Walk <the journey> again, whole." A journey split across stages → "Walk <each of its steps already walked> again." My answer to its question → the words I ruled, whole, in one paragraph.
3. Say it in one line.

## Step 4 — End the walk

1. Keep the walker's last journey: `python3 .claude/tools/walk-clear.py WW keep`. It lands in `.claude/state/sessions/NN/walkers/WW-<its start>/`, beside each journey before it: `walk-clear.py` keeps them there before every journey.
2. Then stop it: invoke `reaper` with WW, and RR when a reader runs.

## Step 5 — Hand my reader a page

1. A reader runs → type `python3 .claude/tools/panes.py say --to RR --line "Read <area>/<section> · <the docs step>."`. Say it in one line, and stop.
2. Read `.claude/state/sessions/NN/launch.json` when it exists. Keep its rows.
3. A reader's row stands there → add " Read <area>/<section> · <the docs step>." to its message.
4. None → add one row, as `launch` Step 4 rules: `{"name": "<the walk's name, three words at most> reader", "model": "sonnet", "effort": "low", "message": "/walk-read Report to session NN. Read <area>/<section> · <the docs step>."}`. No account: I pick it.
5. Say the row in one line. Your move: "Action: pick the reader's account, then press Launch on 1100."

## Never

1. Never type into a walker's pane but my word.
2. Never answer a walker for me.
3. Never launch a walker or a reader yourself. I press Launch.
4. Never type into the reader's pane but a page to read.
