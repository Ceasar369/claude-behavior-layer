---
name: assistant-successor
description: Makes this session the assistant of a plan already running, lays out the next steps, then works on them.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "takes no words; run it once this session holds the plan's number"
---

# Assistant Successor

## Step 1 — Take the role

Read `.claude/skills/1-assistant/SKILL.md` whole. It is your role from now on.

Run its Steps 1 to 3.

## Step 2 — Read the plan's state

My folder is `.claude/state/sessions/NN/`.

Read `.claude/state/sessions/NN/stages.json`, every mission file of the latest stage that went out, and every file in `.claude/state/sessions/NN/answers/`. In an open plan, every mission file whose session has not stopped, whatever its stage.

For each launched session of that stage, run `python3 .claude/tools/clarify-page.py answers SS`.

## Step 3 — Say where the plan stands

One line: which stage went out last, and whether every mission in it has stopped. In an open plan: which sessions run, by stage.

## Step 4 — Lay out the next steps

Invoke `clarify-steps`, with the plan as its scope.

## Step 5 — Work on them

Carry out each step this seat owns, by `1-assistant`'s steps. `.claude/rules/thinking.md` says what stops you, under "Finish what was asked".
