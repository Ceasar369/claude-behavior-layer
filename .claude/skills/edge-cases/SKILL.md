---
name: edge-cases
description: Finds the edge cases my message leaves undecided, before the work starts, and brings me only those no file settles.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "[my message] — omit for my last message"
---

# Edge Cases

## Step 1 — Take the message

An argument → it is the message.

No argument → my last message before this one.

## Step 2 — Read what it touches

Read every file it names, and every file the work would change.

## Step 3 — Ask the five Ws

Ask each W of `knowledge/0010-playbook/0013-thinking/the-thinking-axioms.md`, under "Answer the five Ws", of the work my message asks for.

My words, a file or the code answers it → settled. Follow that answer.

Nothing answers it, and its answer changes what gets built → it is undecided.

## Step 4 — Nothing undecided

Say one line: "Nothing open", then the files that answered each W.

Then start the work, in the same turn.

## Step 5 — Something undecided

Run `clarify-items`, one item per undecided W, each with your recommendation.

Then wait. The work starts once every item is agreed. Nothing else goes first.

## Never

Never run it unless I typed it, or agreed to a move naming it.

Never fill an undecided W with a guess.

Never ask what a file or the code answers.
