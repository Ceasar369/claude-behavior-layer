---
name: layer-update
description: Brings the public layer's newest version into this project, and checks it still runs. "Update the layer" means this skill.
allowed-tools: Read, Bash, Skill
argument-hint: "takes no words"
---

# Layer Update

## Step 1 — Update

Run `python3 .claude/tools/layer.py update`.

It refuses → say its line, and stop.

## Step 2 — Rule each clash

It stops on clashes → the merge is left open. Each line names one file, and what clashes.

1. Read both sides of each file: `git diff` shows them.
2. Run `clarify-items`, one item per file. Its `today` quotes this project's lines and the layer's. Its `decision` names the side to keep, or the lines joining both.
3. Settle each file as I rule, with Edit, then `git add` it.
4. Every file settled → `git commit --no-edit`, then run `python3 .claude/tools/layer.py check`.

A file this project changed for itself alone moves to a new file of its own. New files never clash.

## Step 3 — Say the checks

Say each check's line, as the tool printed it.

A failed check is a failing step. Fix what this project holds, then run `python3 .claude/tools/layer.py check` again.

An unfilled stand-in is filled from my words. No words → it is named in chat, for me.

The last line is mine: say it as my move.

## Never

Never settle a clash I have not ruled.

Never edit a shared file to make a check pass. A fix to one goes through `layer-send`.
