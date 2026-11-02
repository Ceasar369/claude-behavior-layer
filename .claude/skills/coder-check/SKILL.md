---
name: coder-check
description: Checks what this session changed against the vault and the docs, and brings me each line they contradict. "Check the docs" means this skill.
allowed-tools: Read, Glob, Grep, Edit, Write, Skill, Agent
argument-hint: "takes no words; checks every file this session changed since its last check"
---

# Coder Check

## Step 1 — List what changed

My number, as `CLAUDE.md` defines it.

Run `python3 .claude/tools/coder-check.py open NN`.

It prints every file this session wrote, moved or deleted since its last check.

Nothing listed → say "Nothing changed". Go to step 6.

## Step 2 — Read what describes it

`knowledge/0010-playbook/0019-targeted/the-map/the-repository.md`, when it exists, maps each code folder to its layer's vault folder.

Read each listed file as it stands now.

One `Explore` helper does the search. Its brief names each listed file, and each name a listed file added, renamed or removed. It searches:

- each vault document naming what a listed file does, which its layer's MOC finds.
- each document in `knowledge/0010-playbook/0015-coding/the-stack/` naming what a listed file does, when that folder exists.
- `knowledge/`, and the docs folder `.claude/project.json` names under `docs`, for each name.

It brings back only the lines found: each one's path, line number and text.

A listed vault file is read against the code it describes.

## Step 3 — Find each contradiction

A line contradicts when a reader would conclude something the code no longer does.

Inside the code: a comment describing old behaviour, a test asserting it, a word missing in one language.

In the vault and the docs: a line stating what the code no longer does.

A fact the vault never held is no contradiction. An item never adds one.

## Step 4 — Fix the code side

Fix each stale comment, test and word with Edit.

Run each test file it changed.

Done names each fix.

## Step 5 — Bring the vault side

A helper asks me nothing. Its report names each line. The session it reports to brings them.

Each contradicted line in the vault or the docs is one item, through `clarify-items`.

Its `today` quotes the line. A line stating what code decides leaves: its `decision` removes it. Any other line's `decision` writes the new line.

The new line obeys `knowledge/standard.md` and its folder's admission rule.

A line I agree is written with Edit. Done names it.

No contradiction anywhere → say "Nothing found".

## Step 6 — Close the check

Run `python3 .claude/tools/coder-check.py close NN`.

## Never

Never write a vault or docs line I have not agreed.

Never check `.claude/`, or `knowledge/0010-playbook/` outside `knowledge/0010-playbook/0015-coding/the-stack/`. `behaviour-doctor` checks them.
