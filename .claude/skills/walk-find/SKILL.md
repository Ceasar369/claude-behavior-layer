---
name: walk-find
description: Finds what a walk covers: the section where I stopped, a section I name, the steps a subject shows in, a feature's steps stage by stage, or the screens, code and walk steps behind one thing I name.
allowed-tools: Read, Glob, Grep
argument-hint: "[an area] [nothing, a section, looks and a section, a subject like the email sender, or words naming one thing] · or a feature walks/walks-MOC.md lists — the area omitted, and no feature named, ask me which"
---

# Walk Find

You find what my walk covers. You read only.

An area is one folder of `walks/`, as `walks/walks-MOC.md` lists them.

## Step 1 — Know what my words name

1. No area named, and no feature `walks/walks-MOC.md` lists → ask me which, and stop.
2. Read `walks/walks-standard.md` whole, the area's MOC, `walks/<area>/<area>-MOC.md`, and its `before-you-start.md`. A feature → the MOC and `before-you-start.md` of each area its line names, and `knowledge/0010-playbook/0017-walking/walking-protocols/protocol-my-walk.md`, under Walks stage by stage.
3. Nothing, a section the MOC lists, or "looks" and a section → Step 2. A subject, like the email sender, or a feature → Step 3. Any other words → Step 4.

## Step 2 — A section

1. A step I have not passed is one with a "You" mark reading ⬜ on any of its rows: its own, its details', its cover files' rows. A — is the tester's alone. A step the standard walks elsewhere never counts here.
2. The checklist is the section's `0-checklist.md`, or its `looks/looks-checklist.md` for looks.
3. A section named → that section. Otherwise, read the `0-checklist.md` of each section the MOC lists under "Sections", then "Across sections", in its order. The first one holding a step I have not passed is the walk's.
4. Every step passed → say the area is walked whole, and stop.
5. Return the section, and each journey heading of its checklist holding a step I have not passed, in order. Name the first such step, its screen and its address, from its head.

## Step 3 — A subject

1. A subject the standard gives its own file, like a vendor's → that file. Its "Walked" line names each step that shows it.
2. A feature → each journey and step of the places its line names.
3. Any other subject → search the journey files of `walks/<area>/*/` for its words, and each cover step's head naming it.
4. Return each step: its section's folder, then its name, like `app/authentication · Sign up 2`, in the sections' order. A feature's → its counters first, then stage by stage, as Walks stage by stage rules: each journey opening a stage whole, then each other place's step showing that stage.

## Step 4 — One thing

1. Find its screens: search the area's code, where its `before-you-start.md`'s Code names it: its routes, and the file its words come from.
2. Each screen's section is the one whose rail row, or menu entry, opens it.
3. Search the journey files of `walks/<area>/*/` for each screen's address and its words.
4. Steps cover it → return their section, and each step's name.
5. None → return "none", with each screen: its address, its route file, its words' keys, and its section.

## Never

Never write a file.
