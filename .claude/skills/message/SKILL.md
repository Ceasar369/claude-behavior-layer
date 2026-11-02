---
name: message
description: Types one paragraph into another session's pane, as me. "Message session 2 to …" means this skill, never SendMessage.
allowed-tools: Read, Glob, Grep
argument-hint: "NN [what to say] — NN is the session number"
---

# Message

It arrives where my own typing arrives, so it carries my authority.

## Step 1 — Take the target

The first word is a session number.

The rest is what I want said.

## Step 2 — Write it

`.claude/rules/talking.md` rules the
voice, under "Writing for another reader". Follow it.

One paragraph, no line break. A newline submits and splits the message.

Carry no copy markers. Those are for my hand, not a pane.

Name what the reader does first, then what it needs to know.

## Step 3 — Ground it

Read every file the message names. Never state a fact from memory.

## Step 4 — Type it in

```
.claude/tools/panes.py say --to NN --line "<the paragraph>"
```

It types the paragraph and presses return. It sends.

It prints the pane id. Empty means nothing was typed: the pane is gone, or Claude is gone from it.

## Step 5 — Report

Read the target's transcript. Its record names the file.

The paragraph shows there once → it landed.

Not there, and the target is working → say it is queued, unproven.

Say which session it reached, and quote nothing back.

Gone → say so, and offer `blurb-session` instead.

## Never

Never leave it unsent. I run this to send, not to draft.

A message I want to read first is `blurb-session`.

Never send to my own number.

Never claim it landed before the target's transcript shows it.
