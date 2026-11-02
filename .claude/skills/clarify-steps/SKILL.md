---
name: clarify-steps
description: Lays out what happens next, in order, every step with its owner. "Next steps" means this skill.
allowed-tools: Read, Glob, Grep
argument-hint: "[the scope] — omit for the work in hand"
---

# Clarify Steps

Every step answers what, who, when, how and why. You decide them. Only the step shows.

## Step 1 — Ground it

Read the state the steps come from. The conversation, my folder, the code.

Never list from memory.

## Step 2 — Find every step

A step is one action someone takes. Never a choice.

One subject per turn. The rest wait, in order.

An item I have not ruled on is a step of mine: "Rule on item 2, Cap every job at three tries."

## Step 3 — Give each step one owner

Four owners, labelled as you speak to me. Never a fifth.

- **You** — me. An act only I can take.
- **Me** — this session, and every agent it spawns.
- **Session NN** — another running session, by its number.
- **New session** — one not started yet.

Me only when this holds: "This seat did the work with me, uncompacted since." Otherwise a new session.

Never "we". Never blank. An agent is never an owner.

A session's number comes from its record, `.claude/state/sessions/NN/record.json`. Never invent one.

## Step 4 — Say why, or say how it is checked

A step of mine says why it is mine.

A ruling, a fact only I hold, or an act only my hands can take.

None applies → the step is not mine.

Every other step says how it is checked. "Done when the test passes."

Never "done when it works".

## Step 5 — Order by real dependency

A step sits after what it needs. Never invent an order.

A step waiting on another session, or on something missing, is checked now, as `.claude/rules/thinking.md` says, under "A neighbour is not a block".

A step that can wait for my choice is marked later.

## Step 6 — How follows who and when

Never ask me how. It follows from the owner.

- **Me** → you do it. Nothing to type.
- **Session NN** → yours to send. Its blurb, from `blurb-session`, when you ask.
- **New session**, now → offer to kick it off with `launch`. "Say go."
- **New session**, later → its blurb file, from `blurb-session`, named below its step.
- **You** → a ruling, or an act for my hands. Nothing to type.

## Step 7 — Render one list

One line per step, plus its why or its check.

```
1. **You** — Rule how slice one splits.
   A ruling is yours alone.
2. **Me** — Think the building blocks through with you.
   Done when every block has agreed items.
3. **New session**, now — Write the agreed vault changes. Say go.
   Done when a search finds no stale line.
```

Nothing is on me → one line above the list: "Nothing is on you."

A change that reaches other sessions ends on one step of mine: "**You** — tell the sessions you choose. A blurb, if you ask." It names the sessions it reaches. It never sends a word.

What nobody can move sits below the list, under **Blocked**, with why.

Nothing blocked → no **Blocked**.

## Never

Never show the five questions. Only their answers, inside the step.

Never hand me a line to run in this session. You run it.

Never explain a subject here. That is `clarify-explain`.

Never open a new decision here. That is `clarify-items`.

Never split the list by owner. One list, always.

Never give yourself a step that messages another session.

Never invent a step to fill the list.
