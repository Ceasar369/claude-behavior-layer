---
name: prototype-lock-in
description: Keeps the variation I name as the winner, and deletes every other one.
allowed-tools: Read, Edit, mcp__playwright__browser_navigate, mcp__playwright__browser_console_messages, mcp__playwright__browser_close
argument-hint: "g2/v3, or g2/v3 · A: look 1 · B: look 4 — the variation to keep, and one look in each group it holds"
---

# Prototype Lock-in

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it.

`python3 .claude/tools/prototype.py status NN` prints the app's port, and my subject.

## Step 2 — Lock it in

Run `python3 .claude/tools/prototype.py lock-in <subject> g<N>/v<M>`, with the variation I named.

A variation with groups of looks takes one look in each: add `--looks 1,4`, the numbers I named. A group with no look refuses.

Say what it printed.

## Step 3 — Cut the losing looks

It printed looks that left the record → open the variation's file. Delete each such look's scene, and every picture inside it, like 2.1. Keep every other. The numbers stay as they are.

Open its route on the port `prototype.py status NN` prints, with Playwright, and read its console errors. A favicon's 404 is no error. Close the page.

## Step 4 — Name the winner

Say its route and its file: `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`.

A later mission names that file under "Read first".

## Never

Never lock in a variation I did not name.
