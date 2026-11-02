---
name: assistant-checkpoint
description: Reads what my running sessions said since the last checkpoint, and brings me what they raised. "Checkpoint" means this skill.
allowed-tools: Read, Write, Skill
argument-hint: "[NN ...] — the sessions to read; without them, every session of my current stage"
---

# Assistant Checkpoint

## Step 1 — Know my number

My number, MM, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/MM/`.

## Step 2 — Take the sessions

Numbers I give → those sessions.

None → run `python3 .claude/tools/assistant-page.py states MM`, and read `.claude/state/sessions/MM/stages.json`.

The current stage is the first with a mission not stopped; in an open plan, every stage with one. Read each of its missions' sessions, and each helper.

No number and no plan → say a checkpoint needs sessions to read, and stop.

## Step 3 — Read what each said since the last checkpoint

`.claude/state/sessions/MM/checkpoint.json` holds one mark per session.

For each session SS, run `python3 .claude/tools/transcript.py new SS --since T`, T being its mark.

No mark → run it without `--since`.

Read the output whole, in parts.

A User turn is me. A User turn opening "Session NN reports:" is that session's report, never mine.

What I said in a session's pane is a ruling. What a session said is its claim.

Write each session's new mark, the output's last line, into `checkpoint.json`.

## Step 4 — Sort what you read

For each session, find:

- each thing I said there, and each ruling;
- each thing it did: a line written, a step closed, a check run;
- each thing it raised: an answer, a criticism, a related thing;
- what it waits on.

A thing a session raised that I never took up is open.

A thing two sessions say differently is open. Name both.

Each thing names its session and its turn.

Read a file a session names only where a thing turns on it.

## Step 5 — Where we stand

Run `2-clarify` with: where we stand on what I said in these sessions.

## Step 6 — What they raised

My next message → carry any ruling in it first. Then run `2-clarify` with: what these sessions raised that I never took up.

## Step 7 — Think it through

I name a thing to think through → run `3-thinker` with it, naming its session and turn.

## Step 8 — Carry my rulings

A ruling of mine a session must carry → my move names that session's mission, for `/1-assistant`.

## Never

Never type into a session.

Never state what a session did without its turn.
