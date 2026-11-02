---
name: session-successor
description: Takes the seat of a session handed over to this one, reads where its work stands, lays out the next steps, then works on them.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "takes no words; run it once this session holds the handed-over number"
---

# Session Successor

## Step 1 — Take the seat

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

Every file in `.claude/state/sessions/NN/handovers/` is read, whole, oldest first. One not read yet → read it now.

## Step 2 — Read where the work stands

Read each one that exists.

- My mission. `grep -l '"title": "<my name>"' .claude/state/sessions/*/stages.json` finds my plan. Its mission with my name as `title` names my mission's `file`. Read it whole.
- My newest wave, the highest K in `.claude/state/sessions/NN/waves/wave-K.md`, whole.
- My prototype: `python3 .claude/tools/prototype.py status NN`.

## Step 3 — Say where the work stands

One line: my work, and where it stands.

## Step 4 — Lay out the next steps

Invoke `clarify-steps`, with my work as its scope.

## Step 5 — Work on them

Carry out each step this seat owns. `.claude/rules/thinking.md` says what stops you, under "Finish what was asked".
