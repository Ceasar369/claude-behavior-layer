---
name: clarify-green-light
description: Answers my "can I do this now?" with every prerequisite, met or not.
allowed-tools: Read, Glob, Grep
argument-hint: "[the action I want to take] — omit for the one my last message names"
---

# Clarify Green Light

## Step 1 — Name my action

An argument → it is the action.

No argument → the action my last message names.

One action per turn. The rest wait, in order.

## Step 2 — List every prerequisite

A prerequisite is something done before the action can go ahead.

Read every file the action touches. Never state a fact from memory.

Number them, in the order they must be done.

## Step 3 — Check each one

Each is met, not met, or unproven. A met one names the file proving it. A live fact no file proves is unproven.

## Step 4 — All met

Answer in one line: "Green light: <the action> can go ahead."

## Step 5 — Some unmet

List every prerequisite, met or not, in its order.

Each unmet one says how to clear it.

A fix → name the fix, and the files it touches.

It needs thinking through → offer to run `3-thinker` on it. "Say go."

Another skill clears it → name that skill, and offer to run it.

`.claude/rules/thinking.md`, under "A neighbour is not a block", rules what goes on meanwhile.

## Never

Never give a green light while a prerequisite is unmet.

Never take the action yourself unless I ask.
