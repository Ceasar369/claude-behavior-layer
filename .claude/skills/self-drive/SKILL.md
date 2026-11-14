---
name: self-drive
description: Takes the work I hand it to its end, verified and visible, then stops this session. "Self-drive …" means this skill.
allowed-tools: Skill, Read, Write, Edit, Glob, Grep
argument-hint: "[the work] — omit to self-drive the work in hand"
---

# Self-Drive

The drive is on from this call. Once off, it stays off until this session stops.

## Step 1 — Do the work by its protocol

Code, anywhere → `5-coder`.

A document under `knowledge/` → `knowledge/standard.md`, then its folder's admission rule. Write only the facts my words rule.

## Step 2 — What turns the drive off

- A skill whose work waits on me: `3-thinker`, `4-prototype`, `2-clarify`, `clarify-items`, `6-agenda`, a launch page.
- A question I type.
- A permission I deny.

Every other stop is in `.claude/rules/thinking.md`, under Finish what was asked.

Off → end your turn in its shape, showing what you need, whole. Never call `9-session-stop` after.

A team's assistant keeps it on: my words make this session my assistant through `1-assistant`.

1. Its plan goes out as one `clarify-items` wave, with no `--then`: my Send folds it first.
2. Its first item, What I understood, says my words back. A say-back my words ask for is that item, never a stop of its own.
3. Its next items are the plan's stages with their missions, then its finish list.
4. My agree on every item → keep the finish list, as `1-assistant` Step 6 says. Then invoke `1-assistant` with `drive plan`. The plan's drive runs from here, to its report and its stop as my move: `assistant-drive` Step 9. Never call `9-session-stop`.
5. My feedback on any item → fold it, then bring the reworked items in one wave the same way.

## Step 3 — My words mid-run

Words I type or paste join the work. The drive stays on.

An interrupt with no words → wait for mine.

A permission prompt → wait for my click. Approved, drive on.

## Step 4 — Verify it

Run what the protocol's gate names. Its walk runs in step 5, not here.

## Step 5 — Make it visible

It must run on a server that outlives you: 1100 or band 00. Never your own ports.

- 1100's code changed → `5-coder` already restarted 1100.
- Band 00's code changed, and it does not reload alone → call `00-sessions-dashboard`.
- Nothing serves it → nothing.

A refused restart is a failing step.

Walk it there once through Playwright, at its address, as its protocol rules.

## Step 6 — Stop

Every step held → write one short report as this turn's text: what changed, what was checked, any stand-in left. Then call `9-session-stop`.
