---
name: 7-walk
description: Leads my walk of an area of my app, a section, a subject, or any one thing, as its lead. "Walk my app with me" means this skill.
allowed-tools: Read, Skill
argument-hint: "[an area] [a section, a subject like the email sender, words naming one thing, or looks and a section] · or a walker's report, a walker's question, my answer to it, a reader's report, a fix that ended, my yes to walk a journey, my words ending the walk — the area omitted, the only one walks/walks-MOC.md lists, or ask me which; the rest omitted, the first section I have not walked whole"
---

# 7 — Walk

A router. It reads the walking folder, then calls its children in order, each given what the last returned. This session is the walk's lead.

My yes to your ruling is my word. You carry it out yourself, the same turn, typing into the walker or a fixer included. Never hand me words to type.

While your walker walks, or an analyzer you sent judges, no step here and no child brings me a ruling. The protocol's "How each one reaches me" says what comes once they end.

An area is one folder of `walks/`, one part of my app, as `walks/walks-MOC.md` lists them.

## Step 1 — Read the walking folder

1. Read `knowledge/0010-playbook/0017-walking/walking-MOC.md`, `knowledge/0010-playbook/0017-walking/the-walking-axioms.md` and `knowledge/0010-playbook/0017-walking/walking-protocols/protocol-my-walk.md`.

The axioms and the protocol hold for this whole turn, and for each child it calls.

## Step 2 — Pick what my words are

1. A reader's report, "Session RR reports: <a docs step> read, …" → invoke `walk-case` with the report, whole. Stop.
2. A walker's report, "Session WW reports: …" → Step 6.
3. A walker's question, "Session WW asks: …" → Step 8.
4. My answer to a walker's question → invoke `walk-launch` with "answer", then my words, whole. Stop.
5. A fixer's last report, its fix done → Step 7.
6. My yes to walk a journey, or to walk one again → invoke `walk-launch` with "walk <the journey>", or "walk <the journey> again". A first walk → then invoke `walk-write` with the journey after it. Stop.
7. My words end the walk → invoke `walk-launch` with "end the walk". Stop.
8. A start → Step 3.

## Step 3 — Find it

1. No `walks/walks-MOC.md` → invoke `walk-write` with "start the walks". Stop.
2. No area named → the only one `walks/walks-MOC.md` lists. Several → ask me which, and stop.
3. Invoke `walk-find` with the area and my words. The area is walked whole → stop.

## Step 4 — Check the first journey

Invoke `walk-write`, with the area and what `walk-find` returned. It writes the walk's list, adds what the walk lacks, then checks its first journey with me.

## Step 5 — Launch the walker

1. Invoke `walk-launch` with the area.
2. Once it has put the walker on the page, invoke `walk-write` with the walk's second journey.

## Step 6 — Judge a journey

1. Invoke `walk-case` with the report, whole.
2. Each docs step it names ready for my read → invoke `walk-launch` with "read <area>/<section> · <the step>".
3. Then invoke `walk-write` with the next journey to check.

## Step 7 — A fix ended

1. Invoke `walk-write` with the fix that ended.
2. Your move: "Ruling: walk <the journey> again, whole." A journey split across stages → "Ruling: walk <each of its steps already walked> again."

## Step 8 — A walker asks

1. Read what its question names: the journey file, the line it stopped on, its evidence.
2. Bring it to me: where it stands, what it did, its question, then your recommendation and its case.
3. Your move: "Ruling: session WW <what it does>." A step needing my hands → an Action, naming what I do and where.
4. Never answer it yourself. Only my answer reaches it.

## Never

Never do a child's work here.
