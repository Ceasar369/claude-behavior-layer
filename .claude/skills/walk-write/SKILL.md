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
3. A feature whose section has docs pages naming its screens, and no `docs.md` → write its `docs.md`, one step per page, as the standard's "A section's folder" rules, then list its steps. Step 10 searches each page before it walks.
4. A section walked whole → its list needs no yes. Otherwise, show the list, and ask my yes.

## Step 4 — Write a new journey

1. Write one journey file in the screens' section, as the standard's "A journey file" rules: its Start, its Prep, its End, then its steps. Every quote comes from the file the area's `before-you-start.md` names under Code, word for word.
2. Add its link to the section's MOC, and its heading to the section's `0-checklist.md`, `## [[<its link>|<its name>]]`, in its screens' rail order.

## Step 5 — Check a journey before it is walked

1. Read the journey's file, and each file its checklist heading's rows come from.
2. Check each line against the code on disk: each quote against its words' file, each address against its route, and each line the standard gives another source, against it.
3. A Prep, Start or End naming a reset of the test data → rewrite it so a walker on its own login needs none: the rows to change, or the login to make. A Prep writing the database → rewrite it as its call to the dev door the area's `before-you-start.md` names, when it names one. One no route takes → a move on the screen that does it. No screen does it → it stays my hands. A Prep naming a password inside a settings file → rewrite it to name "your login's password". A Prep naming a key inside a settings file → rewrite it to write the key itself: `local-test-key`. A Prep naming a seeded login, or its company → rewrite it to act on the walker's own login and company, as the standard's "A journey file" rules. A Prep or Start relying on a login or record an earlier feature made → rewrite it so this feature makes it again. A step starting on the screen the step before it left, like "Go back", that the walk's list puts apart from that step → its Do first opens the screen its head names.
4. A step that tests the real channel itself, as the standard's Real mark says, wearing no mark → add Real after its title. Each other check the standard asks before a walk → as it rules, with 9's items.
5. Search the journey, as Step 9, and each docs step its checklist heading holds, as Step 10. An Angles line naming a letter that moved, or a detail gone → rewrite it to the details as they stand.
6. Asked while the journey before it is walked → check now, and write nothing yet. Once that journey ends, recheck only the lines whose screens use a file a fix changed since, as each fix's report names. Then go on.
7. A line the code makes wrong, its change made by a session of this walk → rewrite it to the code. A step that changes goes back to ⬜, both marks, its details' Tester marks too.
8. A change no session of this walk explains → do not rewrite it. It is a finding: quote both sides. A finding no check of this journey rests on waits. It comes alone, once the journey's case is done.
9. A change a file already rules, as 3 and 5 do, is made, and named in Done, one line each. Each other change is one `clarify-items` item: its line before and its line after, word for word, the code line that settles it in its sources. Then each search's one item. Then each finding a check of this journey rests on, one item each. Nothing to change → "<the journey>'s files match the code."
10. Each item I agree → keep it. My other words → change it as they say.

## Step 6 — Rewrite what a fix made wrong

1. Read the fix's report: each file it changed.
2. Each line of the journey those files make wrong: its "See" takes the screen as it is now, and its step goes back to ⬜, both marks, its details' Tester marks too. A Stand-in mark goes once my words replace it.
3. An angle I designed, or a docs page's line I agreed, that this fix built → write its detail now, as I agreed it. Then the Angles line, as Step 5's 5.
4. Show and confirm, as Step 5's 9 and 10.
5. Return the journey: it walks again, whole. A journey split across stages → each of its steps already walked, whatever its stage.

## Step 7 — Rebuild the checklists

1. Run `python3 .claude/tools/walk-checklists.py walks/<area>/<the section>`. It rebuilds that section's two checklists alone.
2. Return the section, and each journey heading holding a step I have not passed.

## Step 8 — Start the walks

1. Copy `.claude/tools/walks-standard.md` to `walks/walks-standard.md`. From then on it is the project's own.
2. Write `walks/walks-MOC.md`, as the standard's "Every file" rules: its title, Walks, then its link to the standard.
3. Ask me my first area: its name, and each fact its `before-you-start.md` holds, as the standard lists them. One question at a time.
4. Write the area's folder, as the standard's "An area's folder" rules, and link it from `walks/walks-MOC.md`.

## Step 9 — Search a journey

1. A journey whose search I already ruled, its Angles line written or its cases listed in an item of mine → that item is its search. Search again only each screen whose code, or a server rule it reads or its presses reach, changed since that ruling, as git shows. Nothing changed → no item, and its Angles line, as 8.
2. Read the code behind each of the journey's screens: its route, the words file the area's `before-you-start.md` names under Code, and each server rule it reads or its presses reach.
3. List each case that code checks, in a state the journey's screens hold, that no step or detail walks, in this journey or another: each value it refuses, each limit it holds, each state it answers, each place a press leads. A detail walking the same value on another screen, or in another state, like a list holding rows, leaves it unwalked. A screen a step hands to another journey is that journey's. Values the code answers in the same words share one case, across screens too. The same words answering at a second address → that address joins the same line, two on one, as "/orders/new/cart, /orders/new/quick as the buyer → /orders". It never counts as walked.
4. Ask each screen each angle the standard's "The search" names. One a detail walks → its letters. One another journey walks, or that cannot happen here → "none", with why. One the code decides that no detail walks → a case of 3. One no code decides → undecided.
5. Each case → its proposed detail, under the first step showing it, lettered on from that step's last: what to do → what shows, quoted from the code. A case a new Prep reaches → its detail, and that Prep. A case no Prep can reach today → said so, never a detail. A detail the code leaves in doubt → marked unproven, to prove first.
6. One `clarify-items` item for the journey, titled with its counts, as "From scratch: 10 cases to add, 6 angles undecided". Its show, in order: Add, In doubt, No Prep reaches today, Not designed, each head left out when empty. Then the journey's Angles line, as it will read.
7. I agree or correct the whole list in one go, never case by case. Each detail I agree → write it under its step. An angle I design is a build, never a line first: a fixer builds it, and Step 6 writes its detail once the fix ends. Each angle I list Not designed → a line under Marked in the area's `before-you-start.md`.
8. Write the Angles line after the End, as the standard's "The search" rules.

## Step 10 — Search a docs page

1. A page whose search I already ruled → as Step 9's 1, its calls' code in place of its screens'.
2. Read the code behind each call the page names: its route, its rules, its refusals, its events, and the API reference.
3. List each case that code checks that the page never states: each refusal, each limit, a retry, each event. Each → the line the page gains, and its detail, lettered on from the step's last.
4. A code every call shares, like a wrong key's, is never proposed. It sits on one page alone, as the standard names it, and the page links it instead.
5. Ask the page each angle the standard's "The search" names. One the page answers → its letters. One it cannot answer → a line of 3, or undecided when no code decides it.
6. A page line the code contradicts → both sides, the page's line number beside it. A claim the page makes that no detail walks → its proposed detail.
7. One `clarify-items` item for the page, titled with its counts, as "Create an order: 6 lines, 3 conflicts, 2 unwalked claims". Its show, in order: Page gains, Fixed to the code, Walk, unwalked today, Not designed, each head left out when empty. Then the step's Angles line, as it will read.
8. I agree or correct the page's list in one go. Each line I agree goes to a docs fixer, and Step 6 writes its detail once the fix ends. Each other detail I agree → write it now. Each angle I list Not designed → a line under Marked in the area's `before-you-start.md`.
9. Write the step's Angles line after its italic line, as the standard's "The search" rules.

## Never

1. Never make a change no file rules without my yes.
2. Never write a mark, but a changed step's going back to ⬜.
3. Never remove a step, a detail or a row I passed.
4. Never commit.
