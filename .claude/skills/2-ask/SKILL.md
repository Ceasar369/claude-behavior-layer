---
name: 2-ask
description: Writes one question into this session's own folder, then stops. Use when the work is blocked on the user and they may be in another window. They answer from anywhere with /3-answer.
allowed-tools: Write, Bash
argument-hint: "[the question, or detail to fold into it]"
---

# 2 — Ask

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Hand one question to the user, wherever they are. Then stop.

## When to use it

The work cannot continue without them, and they may not be watching this window.

Otherwise gate here normally with `AskUserQuestion`. Most questions are that.

## One question, then stop

A question is one file. Its answer is a second file with the same number.

**Never ask twice without an answer.** Asking ends the turn, so this holds on its own. Do not work around it.

Anything new is a new question, never a follow-up on an old one.

## Steps

1. **Compose the question into a temp file.** The question and its options, as plain text. Fold in whatever the user's `/2-ask` line adds — that line is theirs, and it is trusted.

2. **Pick a slug.** Lowercase kebab, from the subject. Three or four words. `retry-backoff`, `timeout-vs-deadline`. It becomes part of the filename, so the subject reads without opening the file.

3. **Write it.**
   ```bash
   python3 .claude/tools/bus.py ask <slug> "$MSG_FILE"
   ```
   It resolves this session, takes the next number, and writes atomically. Read `ASKED=`, `NUMBER=`, and `SESSION=` back from its output.

   `WARN=already open` on stderr → a question was already open. Say so plainly and name both numbers. Never hide it.

4. **Confirm, then stop.** End the turn with this shape and nothing after it:
   - `❓ ASKED → <NUMBER> <slug>`
   - The path, from the `ASKED=` line. Real output, never remembered.
   - `Next: /3-answer <SESSION> from any window.`

   Then stop. The turn is over.

## No loops — ever

Never poll for the answer. Never wait. The user answers when they get to it, and runs `/4-inbox` here.

## Things NOT to Do

- Never ask a second question while one is open.
- Never read or wait for the answer — that is `/4-inbox`.
- Never send the whole transcript. The question and its options only.
- Never rename or hand-edit a question file.
- Never boot, spawn, write docs, or touch code.

## Output

One `90-NNNN-<slug>-ask.md` in this session's folder, written atomically, and the confirmation block as the last thing in chat. The turn ends.
