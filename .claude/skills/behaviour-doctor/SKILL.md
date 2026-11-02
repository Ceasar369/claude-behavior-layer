---
name: behaviour-doctor
description: Finds what my latest behaviour changes missed, against my own rules. "Run the doctor" means this skill.
allowed-tools: Read, Glob, Grep, Agent, Skill
argument-hint: "[NN ...] — only what those sessions wrote; omit for everything changed since the last checkup"
---

# Behaviour Doctor

## Step 1 — Know my number

My number, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No number → run `0-session-start` first, then go on.

## Step 2 — Open the checkup

```
python3 .claude/tools/behaviour-doctor.py open NN [SS ...]
```

NN is my number. SS are the sessions I named, if any.

It writes `.claude/state/sessions/NN/doctor/`, and prints the window and its writers.

No file changed → go to step 5.

## Step 3 — Send the checkers

Ten window files or fewer → one `general-purpose` agent runs every slice.

More → one `general-purpose` agent per slice, in the background, six at most at once. As one finishes, the next goes.

- Rulings and Unheeded, over at most three transcript copies each.
- Repeats.
- Protocol.
- Ripple and Conflict.

No transcript copy → no Rulings and Unheeded checker.

Each prompt says: read `.claude/state/sessions/NN/doctor/brief.md` first and follow it, then names its slices and its copies. Nothing else.

## Step 4 — Refute the batch

Write every finding returned into `.claude/state/sessions/NN/doctor/candidates.md`, each under an id.

None → go to step 5.

Send one `general-purpose` agent. Its prompt says: you are the refuter, read `.claude/state/sessions/NN/doctor/brief.md` and follow its refuter section.

Drop every finding it disproves.

## Step 5 — Close the checkup

```
python3 .claude/tools/behaviour-doctor.py close NN
```

## Step 6 — Bring me the findings

None survives → say "Nothing found".

Otherwise, run `clarify-items`, one item per finding, five at most per round. The rest wait, in order.

Each finding takes three parts, in plain words, each under its bold label.

- **What's wrong.** The rule, quoted, and what breaks it.
- **In practice.** What goes wrong today, or that nothing does yet.
- **My fix.** The exact change, with the words it writes.

What's wrong and In practice fill `today`. My fix fills `decision`.

A protocol gap adds its question, and where it goes.

Name the files. Line numbers only where they help me find a line.

Then one line: what it cost, each agent's tokens and the total.

Each one I agree goes into `.claude/state/sessions/NN/doctor/agreed.md`, with its fix.

## Never

Never edit a file the checkup read. The doctor writes only in `.claude/state/sessions/NN/doctor/` and `.claude/state/behaviour-doctor/`, and its rounds through `.claude/tools/clarify-page.py`.

Never show a finding the refuter disproved.

Never build an agreed finding. They go through `3-thinker` together, when I name them.
