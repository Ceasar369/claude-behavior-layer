---
name: session-handover
description: Hands this session's seat to a fresh session, which takes its number, name and folder, and closes this pane. "Hand over" means this skill.
allowed-tools: Read, Skill
argument-hint: "[account A] [model M] [effort E] — the successor's; a model or effort left out keeps what this seat was named, else System's; system takes System's"
---

# Session Handover

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No `record.json` there → run the skill `0-session-start` first, then go on.

## Step 2 — Let my work end

An agent or a background task of mine still running → wait until it ends.

## Step 3 — Save, then hand over

Invoke `handover-prepare` with the `Skill` tool, and no args.

Then invoke `handover-resume` with the `Skill` tool. Its args are NN, then the words I typed after `/session-handover`, if any. Nothing else.

Each answers in one line. A line without "successfully" → say that line, and stop. Step 4 never runs then.

## Step 4 — Say it

One line: "My successor takes my seat now. This pane closes."

## Never

Never run `/9-session-stop` or `/reaper`.

Never write in my folder.
