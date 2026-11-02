---
name: clarify-recap-items
description: Recaps every clarify item I accepted in a session's waves, as its question and final answer, in one file.
allowed-tools: Read, Glob, Grep, Write, Bash
argument-hint: "[NN] [waves, as 5-8] — omit NN to recap this session; omit the waves for every wave"
---

# Clarify Recap Items

## Step 1 — Take the scope

NN names the session to recap. None → this session, its number as `CLAUDE.md` defines it.

A range names the waves. None → every wave.

## Step 2 — Read the waves

Read each wave file in scope, oldest first, from session NN's waves folder. `.claude/tools/clarify-page.py` names it.

Never write a wave file.

## Step 3 — Read what was said

Read every file in session NN's handovers folder, oldest first. `.claude/lib/handover.py` names it.

Run `python3 .claude/tools/transcript.py copy NN --into MM`, MM this session's number. Read the copy it prints.

In both, find each wave's fold table, and each ruling of mine on a wave item in chat.

## Step 4 — Settle each item

Each item in scope takes one of these.

- Agreed outright → its decision, as written.
- Agreed with my words → its decision rewritten whole, my changes inside it. My own words stay wherever they rule.
- Ruled in chat → its fold table, or my chat words, settles it as above.
- Refused, then reworked → it stays out. Its rework shows, under its own number.
- Refused, my words giving the answer → my words are its answer. Its title matches them.
- Parked or held → only the rulings it holds, beside the word parked or held. None → it stays out.
- Never ruled → it stays out.
- An Open questions item → only a ruling it holds on the subject. None → it stays out.

A part of my words that opens a question stays out.

A part that became a new item shows under that item alone.

An answer keeps a table or a tree it needs, from its `show`, my changes in it.

Each answer speaks to me: "your", never "my".

## Step 5 — Write the file

Write `recap-NN-wave-X-wave-Y.md` into this session's folder, X and Y the first and last waves in scope. A run over the same waves replaces it.

Example: session 10 recapping its waves 1 to 8 writes `.claude/state/sessions/10/recap-10-wave-1-wave-8.md`.

Its first line names session NN's title, the waves in scope, and the items shown.

```
# Recap · 10-signing-page · waves 1 to 8 · 30 items
```

Then each item shown, in number order, a blank line between.

```
20 · A person's path starts with the bank
Question: In what order does a person cross the page?
Answer: …
```

A kept table or tree follows its answer, each line indented two spaces.

Plain text. No other heading, no bold.

## Step 6 — Say where it sits

One line in chat: the file's path, and how many items it holds.

1100's Files page shows it, under this session's folder.

## Never

Never reopen an item, or weigh one.

Never add a word I did not rule. Never drop one I did.
