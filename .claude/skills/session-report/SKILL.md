---
name: session-report
description: Writes where this session's work stands into its folder, and says it in chat. "Write your report" means this skill.
allowed-tools: Read, Glob, Grep, Write
argument-hint: "takes no words"
---

# Session Report

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No `record.json` there → run the skill `0-session-start` first, then go on.

## Step 2 — Take the time

Run `date "+%Y-%m-%dT%H:%M:%S"`. Its line is the report's bookmark.

## Step 3 — Read the work

Run `python3 .claude/tools/transcript.py copy NN --into NN`. Read `.claude/state/sessions/NN/transcript-NN.md` whole.

Read every file in `.claude/state/sessions/NN/handovers/`, whole, oldest first.

Find my mission: `grep -l '"title": "<my name>"' .claude/state/sessions/*/stages.json`. A match is my plan, in my assistant's folder. Its mission with my name as `title` names my mission's `file`. Read it whole.

Read every file the work names. Never state a fact from memory.

## Step 4 — Write the report

Write `.claude/state/sessions/NN/report.md` with the Write tool. It replaces any report before it.

```
# <the work, in a few words> · read to <the bookmark>

Stale once `python3 .claude/tools/transcript.py new NN --since <the bookmark>` prints a `User` turn.
```

Then these sections, in order, each a `##`:

- **Agreed** — what I ruled, or agreed to. Each quotes my words, with its turn in the transcript copy.
- **Done** — what changed on disk, one line each, then each check with its proof. A check not run says "unproven".
- **To do** — what is left, and who does it.
- **Still open** — each question I still rule on. A question a file the work names answers is not open: the work follows the file.

A mission's Report section names more → each part goes under Done.

An empty section → one line saying so.

`.claude/rules/talking.md` rules its voice, under "Writing for another reader". This session's own work names its number, never "I".

## Step 5 — Say it

Say the report's Agreed, To do and Still open in chat, in `clarify-summary`'s shape. Name the report under Done. Then wait.

A mission → the turn's Done line reads "`.claude/state/sessions/NN/report.md`: my final report. <id> is complete." Its move reads "Action: tell session MM <id> is complete. Its report: `.claude/state/sessions/NN/report.md`.", MM being my plan's folder.

No mission → its move follows `.claude/rules/talking.md`.

## Never

Never write outside my folder.

Never report a ruling I did not make.
