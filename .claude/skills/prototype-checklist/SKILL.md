---
name: prototype-checklist
description: Lists what I look at and decide in my prototype's newest generation, number by number. "What do I look at?" means this skill.
allowed-tools: Read, Glob, Grep
argument-hint: "[g2 — the generation to check] — omit for the newest"
---

# Prototype Checklist

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it.

`python3 .claude/tools/prototype.py status NN` prints my subject.

No subject → say so in one line, and stop.

## Step 2 — Read what it lists

The generation I name, or the newest `code/prototypes/<subject>/g<N>.json`: its unknowns, and each variation's direction and answers.

Each of its variations, `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`. Its stand-ins sit in its opening comment, and where each is marked.

`knowledge/0010-playbook/0014-prototyping/prototyping-protocols/protocol-glance.md` defines looks and sections.

## Step 3 — Place each item

An item is one unknown's answer, or one stand-in.

Each sits under the number that first shows it: a look, a section, or a picture inside a section, like 3.1. A variation with no number → under the variation.

An item shown alike in several sits under the first, once. One that differs sits under each, saying how.

## Step 4 — Say it

The whole checklist sits in one text fence.

One block per variation: its id, then what it shows.

Under it, every number it draws, in screen order: its number, then what it shows, as `1 — the client, Marie Tremblay`. A picture inside a section follows its section, as `2.1 — under Acme Projects' settings`.

Under each, one short line per item: `[ ] `, then where to look and what it shows, in plain words. A stand-in's line ends with "Stand-in."

## Never

Never build, edit or delete a variation.

Never give your pick. That is `prototype-pick`.
