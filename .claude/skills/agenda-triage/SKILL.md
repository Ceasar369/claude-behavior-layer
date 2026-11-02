---
name: agenda-triage
description: Triages a topic of my agenda with me, one item per turn, and carries out each ending I rule.
allowed-tools: Read, Glob, Grep, Write, Skill
argument-hint: "[a topic, or the items to triage] — omit for the topic in hand"
---

# Agenda Triage

`knowledge/0010-playbook/0016-agenda/agenda-protocols/protocol-triaging-the-agenda.md` rules every step. This runs it.

## Step 1 — The list

Run `python3 .claude/tools/agenda.py list`. Read `.claude/state/agenda/README.md`.

My words name the items → they are the list, agreed. Step 3.

Otherwise build the topic's list, as the protocol's questions 1 and 2 say. Question 2 reads two things:

- each partial drive's topic, which `successor.py take --topic` records in its driver's `.claude/state/sessions/MM/driving.json`.
- each running triage's agreed list, `.claude/state/sessions/MM/triage.md`.

Show it, one line per item. Your move is the ruling on it.

I agree it → write it, one item's file name per line, into `.claude/state/sessions/NN/triage.md`. NN is my number, as `CLAUDE.md` defines it.

## Step 2 — A split, when I ask

I ask to split the agreed list → invoke `1-assistant` with the `Skill` tool, passing: "Split this agreed triage list across missions, by area, no item shared. Each mission's first step: Run `6-agenda`: triage these items: <its items>." Then the list: every item's file name.

Stop here. The assistant carries it.

## Step 3 — The next item

Pick it, as the protocol's question 4 says.

Read its note, and every file it names.

Bring the item, as the protocol's questions 5 and 6 say. Its decisions that are mine go through `clarify-items`.

## Step 4 — Carry out the ending I rule

Each write runs as `python3 .claude/tools/agenda.py <verb> …`. A trim, a fold's words or a new What reaches me first.

- Take it down: quote its Done when and the proof it holds, then `down ITEM`.
- Fold it: hand its words to the other item with `note`, its waits with `link`, as the README says. Then `down ITEM`.
- Act now → Step 5.
- Keep it: one line on what it waits on. Thought through first → `note ITEM`, its What a Decide.
- Mine: `note ITEM`, with its Mine line.

An item I agree to add → `add`, in the README's shape.

## Step 5 — A fix session

Launch it through `launch`, on the account, model and effort I ruled. Its message names the item and its Done when, then:

- A fix: "Run `self-drive`. Test on your own ports. Save every picture under `.claude/state/playwright-mcp/<your name>/`."
- A look I can't picture yet: "Run `4-prototype` at Compare, then stop. Build nothing." The item then takes a Mine line naming the lock-in.

Take it, and drive it partially on its item, through `session-control`.

Its work done, check it on disk. Quote the item's Done when, and propose the take-down.

The item down, a fix session still running is named to me.

## Step 6 — Close

I say close → start nothing new: no item, no drawing, no round.

Each fix still running finishes, and is named to me.

Run `session-report`. Then invoke `9-session-stop`.

## Never

Never bring an item a running session works.
