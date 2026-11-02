---
name: prototype-variations
description: Turns my words into the next generation's variations, first naming a new subject and its unknowns.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "my words — a new subject, or feedback on this session's prototype · omit after Send, to fold my answers"
---

# Prototype Variations

Each direction opens with what its variation shows, by "3. It shows only what my unknowns need", in `knowledge/0010-playbook/0014-prototyping/the-prototyping-axioms.md`. Then it says how the variation answers the unknowns.

"The badge alone: a column per status the service provider sees, a numbered row per look" opens one.

A direction naming numbered things says which they are: looks, which compete in groups, or sections of one design, which never do. It names each group's looks, as "looks 1 and 2 compete, 3 and 4 compete, 5 and 6 are only shown". `knowledge/0010-playbook/0014-prototyping/prototyping-protocols/protocol-glance.md` defines all three.

That axiom never sets how many variations a round holds. Its level's protocol does. At Full, each look I ask for is its own variation.

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it.

`python3 .claude/tools/prototype.py status NN` prints my subject, or none.

## Step 2 — Know which round this is

`python3 .claude/tools/clarify-page.py answers NN` says `sent` → fold it through `clarify-items`.

- A new round opens → stop.
- Every item settled → the unknowns and the variations I confirmed are the round. Go to Step 5.

A subject → Step 4. None → Step 3.

## Step 3 — Start a subject

Read everything my words name: the screen, its parts, its fixtures, my references.

Name the subject in one to three words, kebab-case. No folder in `code/prototypes/` holds that name.

The level's protocol names what comes before generation 1.

It asks my unknowns first → invoke `clarify-items`, with the `then:` line I was given. Its items: the unknowns my words name, each one question, then generation 1's variations, as many as the protocol says, each with its direction. Stop. Nothing is built before I confirm them.

It asks nothing → my words are the round. Turn them into generation 1's variations, as many as the protocol says, each with its direction. A value they leave out takes a marked stand-in. Go to Step 5.

## Step 4 — Take my feedback

Read the subject's newest `code/prototypes/<subject>/g<N>.json`.

Turn my words into the next round: each new variation, as many as the level's protocol says, its direction, and the variation it grows from, as `1/v3`, or none.

One round may take variations from several sources.

My words pick looks in groups, like `g1/v1 · A: look 1 · B: open` → the new variation keeps each look I picked, as a look with no group. Each open group is asked again, as new looks in the same group.

A word you cannot place → ask me one line, and stop. Never guess a direction.

## Step 5 — Say the round

The round is the subject, its unknowns, and each variation: its direction, and its source, as `1/v3`, or none.

Say it in chat, in one line opening "G<N>'s round:", naming each variation's direction and source: "G2's round: the head under the title, from 1/v3. The head beside the total, from 1/v1."

## Step 6 — Hand the round on

Hand it on at once.

## Never

Never build a variation.

Never hand a round on before its line is said in chat.

Never write a file. The round lives in chat and in its wave.
