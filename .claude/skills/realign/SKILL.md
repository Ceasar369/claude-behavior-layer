---
name: realign
description: Realigns a stuck session with what the user actually wants, diagnosed from the on-disk transcript. Use when the session is not understanding or not doing what was asked. Anti-case: a failed explanation is `6-clarify`.
argument-hint: "[what it is getting wrong] — optional"
allowed-tools: Bash, Read, AskUserQuestion
---

# Realign

## Anchor

Follow the root `CLAUDE.md`. Truth over agreement.
This runs IN the stuck session and keeps it. Nothing closes. Nothing is handed anywhere.

## Purpose

Find where this session diverged from the user's intent, correct it, and hold the correction.

## Steps

1. **Flatten the transcript.** Run `.claude/skills/conclusions/flatten.sh` with no argument. Read every `KEY=VALUE` line it prints. Non-zero exit → report its `FAIL:` line verbatim and STOP.

2. **Diagnose from the transcript, never from memory.** Read the clean file. Every finding cites a `@@TURN@@` number and quotes the turn. A turn marked `SYSTEM-NOT-USER` is harness output — never the user's instruction.

3. **Check every ruling.** For each `[GATE ANSWERED]` line, compare what the user chose against what the session did next. A divergence from a ruling is a defect. Name it and quote both sides.

4. **Restate the goal, quoted.** What the user actually asked for, in their words, from the transcript. Never the session's paraphrase of it.

5. **List what went wrong.** One specific line each, every line carrying its quoted turn. Never a characterisation without its evidence. No self-flattery. No minimising.

6. **Gate the list.** `AskUserQuestion` — Header `Diagnosis`; Question `Agree with this list?`; Options `Agree` (recommended) / `Revise`.
   - `Revise` → fold in the corrections, re-present, gate again.
   - Hold nothing until they agree.

7. **Delete the clean file.** `.claude/skills/conclusions/clean.sh "$CLEAN"`. Do this on every exit path, including every STOP above.

8. **Hold the correction.** Apply the agreed list for the rest of the session. Run this skill again when it slips.

9. **Continue in place.** Same session, same context. Then wait for the user's instruction.

## Things NOT to Do

- Never diagnose from memory. The transcript is the record; the stuck context is not.
- Never state a failure without its quoted turn.
- Never attribute a `SYSTEM-NOT-USER` turn to the user.
- Never write a fresh-session prompt. That is `/7-provide-prompt`, and the user runs it.
- Never commit, ship, PR, merge, or mark anything done.
- Never clear the lock or edit the live index.
- Never run `/9-stop`. This skill does not close.
- Never soften the list to save face.
- Never treat this as a one-turn reset.
- Never leave the clean file behind.

## Output

Chat only. The goal in the user's own words, the divergences with their turn numbers, the
what-went-wrong list, then the correction held for the rest of the session.
No files written. Nothing committed, closed, or cleared.
