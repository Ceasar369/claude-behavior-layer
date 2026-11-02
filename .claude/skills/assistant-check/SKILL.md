---
name: assistant-check
description: Verifies one session's reported work on disk, and says in chat, and on the page, whether it holds.
allowed-tools: Read, Glob, Grep, Write, Edit
argument-hint: "A1 or 21 — the mission, or its session"
---

# Assistant Check

## Step 1 — Take the session

My number, MM, as `CLAUDE.md` defines it.

A mission id finds its session: `python3 .claude/tools/assistant-page.py states MM`. A number is the session.

Its mission is its entry in `.claude/state/sessions/MM/stages.json`.

## Step 2 — Read its report

Your old `.claude/state/sessions/MM/answers/<id>.md` names its bookmark in its headline, after `read to`. Call it T.

```
python3 .claude/tools/transcript.py new NN --since T
```

It prints every turn after T, then the next bookmark. Its last session turn is its report, or names the report file holding it. Read that file whole. No old answer → no `--since`.

A turn marked `Session NN · report` is its helper's report, never my ruling.

Read its mission file.

## Step 3 — Re-run its test files

Re-run only the test files its report names, read-only. Never a whole folder, never a browser walk.

Every other claim its report makes is read on disk: its files, and the output it pastes.

A session that ran a helper holds only once its helper's checks pass too, and the helper is stopped.

A prototype mission holds once `code/prototypes/<subject>/` keeps one generation with one variation, and its route renders on the prototypes app, on the port `python3 .claude/tools/prototype.py status NN` prints.

Never write in its folder.

## Step 4 — Write the answer

Write `.claude/state/sessions/MM/answers/<id>.md` with the Write tool.

```
# Holds: stop session 21 · read to 2026-09-24T15:02:11
## Your moves
1. Send to session 21.
> /9-session-stop now
- 43 of 43 tests pass.
- The spec check passes, in its pasted output.
```

Line one is the verdict, "Holds: stop session 21" or "Not done: " and what is missing, then `read to` and the bookmark `new` printed.

`## Your moves` comes first. It holds → its one move types `/9-session-stop now` into its pane. Not done → its move sends the exact fixes to its session, as `> ` lines.

One bullet per check, with its proof. A check not run says "unproven".

Not done → one `##` per fix after the checks, with its why.

A `> ` line goes to the session word for word. I never paste it. `.claude/rules/talking.md` rules its voice, under "Writing for another reader".

## Step 5 — Carry what it taught

Its report hands a later mission something → add it to that mission's notes, one bullet.

## Step 6 — Say it

Lay the answer out in chat: its verdict, each check with its proof, and its moves. The page carries the same.

I asked for your help, never your hands. Outside a drive, I send each move myself, from 1100.

Your move is "Action: on 1100, send session NN its stop." when it holds, or "Action: on 1100, send session NN the fixes." when it does not. It rules the verdict.

In a drive, your verdict returns to `1-assistant` Step 8. It stops the session, or sends the fixes. Never ask my yes.

## Never

Never clear a stop on its word alone.

Never fix its work.
