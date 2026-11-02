---
name: agenda-write
description: Writes my agenda as I dictate it, and says its order or where an item stands.
allowed-tools: Read
argument-hint: "[what I dictate, or an item] — omit to say the order"
---

# Agenda Write

My agenda is `.claude/state/agenda/`. It holds what I dictate, and what waits on what.

## Step 1 — Read it

Run `python3 .claude/tools/agenda.py list`. It is the agenda whole.

Read `.claude/state/agenda/README.md`. Its note's shape is the standard.

## Step 2 — Do what my words ask

**I dictate.** A new item, a change, a link, a rename, or an item dealt with.

Write it at once, in my words, with the verbs below. Its What takes the README's shape: pick its action and size from my words, and say them in your turn.

Anything beyond my words, a link I did not name or a Why, comes to me first.

**I ask the order.** Say it in plain words, topic by topic. First what can start now, then what waits on what.

**I ask where an item stands.** Run `python3 .claude/tools/agenda.py where ITEM`, and say its answer in plain words.

## The verbs

- `add NAME --topics TOPIC ... --phase PHASE --note TEXT [--after ITEM ...]`, the note holding its What at least
- `under ITEM TOPIC ...`, its topics replaced
- `phase ITEM PHASE`, it moves to that phase
- `link ITEM PARENT` and `unlink ITEM PARENT`
- `rename ITEM NAME`
- `note ITEM`, the note on stdin, in the README's shape
- `down ITEM`, once dealt with

Each runs as `python3 .claude/tools/agenda.py <verb> …`.

A refused write goes to me, its sentence whole.

Once written, name each item the tool says moved.

