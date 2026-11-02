---
name: prototype-brainstorm
description: Brainstorms with me, in chat, which axes my prototype's next generation could change, before it is built. "Let's brainstorm" means this skill.
allowed-tools: Read, Glob, Grep
argument-hint: "[my words on the newest generation] — omit to find its axes from its files alone"
---

# Prototype Brainstorm

An axis is one way the design could differ. Shape, what opens on a click, its look.

The brainstorm lives in chat, over as many turns as I want. It ends when I say build.

Every axis is a proposal. My "build" is the one ruling.

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it.

`python3 .claude/tools/prototype.py status NN` prints my subject.

No subject, or no `code/prototypes/<subject>/g<N>.json` yet → say so in one line, and stop.

Your table of axes already sits in this chat → my words answer it. Build → Step 6. Anything else → Step 5.

## Step 2 — Read what it starts from

The newest `code/prototypes/<subject>/g<N>.json`: its unknowns, and each variation's direction and answers.

Each of its variations, `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`.

Its subject's own rules. A product screen: The Screen, every document in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`, and `knowledge/0010-playbook/0015-coding/the-stack/the-look.md` beside it, whole. A page 1100 draws: the page rules, atop `.claude/lib/page.py`, and nothing more of it.

My words in this subject's rounds, and my words now. A compacted chat → run `python3 .claude/tools/transcript.py copy NN --into NN`, and read `.claude/state/sessions/NN/transcript-NN.md`.

## Step 3 — Find the axes

Each unknown the generation answered is an axis.

Each choice a variation made that no unknown asked is an axis too: its layout, what it shows first, its look, a stand-in.

An axis my words already ruled stays out.

## Step 4 — Say them

One text fence. One line per axis: its name, its value in g<N>, then two or three new values.

A new value carries the subject's real data: its names, its numbers, its states.

An axis g<N> already tried several ways says so.

A value that breaks the subject's own rules names the rule.

## Step 5 — Fold my answers

Each answer moves an axis to values I pick, holds it, drops it, or adds one.

Fold them. Say the table again, each axis marked moved or held.

Back and forth, until I say build.

## Step 6 — Hand it on

I say build → hand my picks on, and the level I named, if any.

My picks: each axis moved, with the values to try. Each held axis, as held.

## Never

Never build, edit or delete a variation.

Never pick for me.

Never end the brainstorm. I say build.
