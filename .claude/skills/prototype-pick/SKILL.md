---
name: prototype-pick
description: Gives this session's preference among its prototype's newest variations, with the reasons for and against each.
allowed-tools: Read, Glob, Grep, Agent
argument-hint: "[g2 — the generation to weigh] — omit for the newest"
---

# Prototype Pick

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it. My page is the prototypes app, on the port `python3 .claude/tools/prototype.py status NN` prints. 1100 frames it in my hub while I hold a subject not locked in.

`python3 .claude/tools/prototype.py status NN` prints the app's port, my subject, and whether the app is up.

No subject → say so in one line, and stop. The app down → `/00-sessions-dashboard` brings band 00 up.

## Step 2 — Read what it weighs

The generation I name, or the newest `code/prototypes/<subject>/g<N>.json`.

It holds one variation, its numbers all sections → say "Nothing to pick: g<N> holds one variation, in sections." Stop. Sections are never picked among, by `knowledge/0010-playbook/0014-prototyping/prototyping-protocols/protocol-glance.md`.

Each of its variations, `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`.

Its subject's own rules. A product screen: The Screen, every document in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`, and `knowledge/0010-playbook/0015-coding/the-stack/the-look.md` beside it, whole. A page 1100 draws: the page rules, atop `.claude/lib/page.py`, and nothing more of it.

My words in this subject's rounds. A compacted chat → run `python3 .claude/tools/transcript.py copy NN --into NN`, and read `.claude/state/sessions/NN/transcript-NN.md`.

## Step 3 — Weigh each variation

Weigh in this order. A higher one outranks a lower one.

1. My words in this subject's rounds. A decision in chat is final.
2. Its subject's own rules. A product screen: The Screen, in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`, then the frame and the tokens, in `knowledge/0010-playbook/0015-coding/the-stack/the-look.md`. A page 1100 draws: the page rules.
3. A precedent in a real frontend under `code/`, named as a precedent.

A choice none of them covers is a gap.

## Step 4 — See each claim

One agent sees every claim about a width, at that width, with Playwright. Its brief lists each claim, its route, `/<subject>/g<N>/v<M>`, on the port `prototype.py status NN` prints, and its width. It answers in text: what it saw, claim by claim.

Never take a screenshot yourself.

## Step 5 — Say it

`knowledge/0010-playbook/0014-prototyping/the-prototyping-axioms.md` rules it, under "11. My taste is written down".

The pick comes first: one variation, or a blend for the next generation.

Several looks share one variation → the pick may be one look in each group, by its number, shown alone in the next generation.

Then each variation, or each look when several share one: its For and its Against, each naming the word, rule or precedent behind it.

Then each gap, one line each.

## Never

Never build, edit or delete a variation.

Never pick from a variation you did not read.
