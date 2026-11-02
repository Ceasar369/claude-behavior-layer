---
name: walk-write
description: Writes my walk files: starts a project's walks, writes each walk's list, adds what a walk lacks, and brings each journey's lines in line with the code right before it is walked.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[start the walks] · [an area] [a section and its journeys · the steps walk-find found · none, and the screens walk-find found · a journey to check · a fix that ended] — the area omitted, ask me which; the rest omitted, ask me what to write"
---

# Walk Write

You write my walk files. Every change no file rules, I confirm first. Marks are the lead's.

NN is your number, as `CLAUDE.md` defines it. An area is one folder of `walks/`, as `walks/walks-MOC.md` lists them.

## Step 1 — Read the standard

1. No `walks/walks-standard.md` → Step 8 first.
2. Read `walks/walks-standard.md` whole, and the area's `before-you-start.md`. They rule every line you write.
3. No area named → ask me which, and stop. Nothing else named → ask me what to write, and stop.
4. A section and its journeys → Step 2, then Step 3, then Step 5 for its first journey.
5. The steps `walk-find` found → Step 3, then Step 5 for its first journey.
6. "none", and the screens `walk-find` found → Step 4, then Step 2, then Step 3, then Step 5 for the new journey.
7. A journey to check → Step 5.
8. A fix that ended → Step 6.
9. Each ends with Step 7.

## Step 2 — Name what each step covers

1. In each of the section's cover and looks files, read each step's head and its italic line.
2. Its italic line ends naming journey steps, as a vendor's does → leave it.
3. Otherwise, find each journey step of the section whose screen it checks: the same address, or the screen its docs page describes.
4. Found → add them at its italic line's end, before the closing `*`: ` · Sign up 1, Forgot 1`. None → leave it.
5. A docs step whose italic line names no address → add its page's address first, as the standard rules it.
6. Show them with Step 5's changes, for my yes.

## Step 3 — Write the walk's list

1. Write `.claude/state/sessions/NN/walk-list.md`, as `.claude/tools/walk-list-page.py`'s docstring rules: its title, the walk's name in my words, then one line per journey or step, `- <area>/<section> · <its name>`, in the order `walk-find` returned. A whole journey takes one line. A looks walk's section ends `/looks`.
2. A check my words want that no checklist holds → write it as a step of the journey that first shows it, as Step 4 rules, then list it.
3. A section walked whole → its list needs no yes. Otherwise, show the list, and ask my yes.

## Step 4 — Write a new journey

1. Write one journey file in the screens' section, as the standard's "A journey file" rules: its Start, its Prep, its End, then its steps. Every quote comes from the file the area's `before-you-start.md` names under Code, word for word.
2. Add its link to the section's MOC, and its heading to the section's `0-checklist.md`, `## [[<its link>|<its name>]]`, in its screens' rail order.

## Step 5 — Check a journey before it is walked

1. Read the journey's file, and each file its checklist heading's rows come from.
2. Check each line against the code on disk: each quote against its words' file, each address against its route, and each line the standard gives another source, against it.
3. A Prep, Start or End naming a reset of the test data → rewrite it so a walker on its own login needs none: the rows to change, or the login to make. A Prep writing the database → rewrite it as its call to the dev door the area's `before-you-start.md` names, when it names one. One no route takes → a move on the screen that does it. No screen does it → it stays my hands. A Prep naming a seeded login, or its company → rewrite it to act on the walker's own login and company, as the standard's "A journey file" rules. A Prep or Start relying on a login or record an earlier feature made → rewrite it so this feature makes it again. A step starting on the screen the step before it left, like "Go back", that the walk's list puts apart from that step → its Do first opens the screen its head names.
4. A step that tests the real channel itself, as the standard's Real mark says, wearing no mark → add Real after its title. Each other check the standard asks before a walk → as it rules, with 8's items.
5. Asked while the journey before it is walked → check now, and write nothing yet. Once that journey ends, recheck only the lines whose screens use a file a fix changed since, as each fix's report names. Then go on.
6. A line the code makes wrong, its change made by a session of this walk → rewrite it to the code. A step that changes goes back to ⬜, both marks, its details' too.
7. A change no session of this walk explains → do not rewrite it. It is a finding: quote both sides. A finding no check of this journey rests on waits. It comes alone, once the journey's case is done.
8. A change a file already rules, as 3 does, is made, and named in Done, one line each. Each other change is one `clarify-items` item: its line before and its line after, word for word, the code line that settles it in its sources. Then each finding a check of this journey rests on, one item each. Nothing to change → "<the journey>'s files match the code."
9. Each item I agree → keep it. My other words → change it as they say.

## Step 6 — Rewrite what a fix made wrong

1. Read the fix's report: each file it changed.
2. Each line of the journey those files make wrong: its "See" takes the screen as it is now, and its step goes back to ⬜, both marks, its details' too. A Stand-in mark goes once my words replace it.
3. Show and confirm, as Step 5's 8 and 9.
4. Return the journey: it walks again, whole. A journey split across stages → each of its steps already walked, whatever its stage.

## Step 7 — Rebuild the checklists

1. Run `python3 .claude/tools/walk-checklists.py walks/<area>/<the section>`. It rebuilds that section's two checklists alone.
2. Return the section, and each journey heading holding a step I have not passed.

## Step 8 — Start the walks

1. Copy `.claude/tools/walks-standard.md` to `walks/walks-standard.md`. From then on it is the project's own.
2. Write `walks/walks-MOC.md`, as the standard's "Every file" rules: its title, Walks, then its link to the standard.
3. Ask me my first area: its name, and each fact its `before-you-start.md` holds, as the standard lists them. One question at a time.
4. Write the area's folder, as the standard's "An area's folder" rules, and link it from `walks/walks-MOC.md`.

## Never

1. Never make a change no file rules without my yes.
2. Never write a mark, but a changed step's going back to ⬜.
3. Never remove a step, a detail or a row I passed.
4. Never commit.
