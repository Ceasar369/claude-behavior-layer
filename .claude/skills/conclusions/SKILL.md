---
name: conclusions
description: Reconstructs what a session decided, from its on-disk transcript. Use when the user runs /conclusions or asks what was concluded — in this session or an earlier one.
argument-hint: "[session id, prefix, or title] — omit for this session"
allowed-tools: Bash, Read, Agent, AskUserQuestion, Write
---

# Conclusions

## Anchor

Follow the root `CLAUDE.md`. Truth over agreement.
Read the on-disk transcript. Never summarize from memory.

## Purpose

Pull every agreed conclusion of one session into a structured ledger.

## Steps

1. **Resolve the target.** No argument → the current session. An argument, or any ask
   about an earlier session → run `list-sessions.sh 15`, show the table, and gate the
   pick. Titles come from `/rename`, so the user picks by name.
   Gate it with `AskUserQuestion`.

2. **Flatten.** Run `flatten.sh [target]`. It prints `KEY=VALUE` lines. Read every one.
   Non-zero exit → report the `FAIL:` line verbatim and STOP. Never continue without a
   clean file.

3. **Check the size.** `APPROX_TOKENS` over 150000 → report the number, name the session,
   and STOP. Recommend narrowing to a shorter session instead. Never truncate silently.

4. **Report the numbers before extracting.** State `TITLE`, `TURNS`, `QUESTIONS_ASKED`,
   `GATES_ANSWERED`, `NON_USER_TURNS`.

   Those two counts measure different things. One gate call carries several questions, so
   `QUESTIONS_ASKED` normally exceeds `GATES_ANSWERED`. Never read that gap as withdrawal.
   A withdrawal is a `[GATE ASKED]` with no `[GATE ANSWERED]` after it. Find it by reading.

5. **Spawn one `researcher`** on the clean file, with the brief below. One agent.
   Extraction, not judgment.

6. **Reconcile.** Apply `## Reconcile stance` to its ledger.

7. **Present.** `Locked` / `Moved out` / `Still open` / `Next`.

8. **Offer to keep it.** Header `Keep it`, Question `File this ledger in the session folder?`.
   Options: `Chat only` (recommended) / `File it`. On the second, `Write` it
   to the live session folder as `NN-conclusions.md`, numbered after the highest existing
   file.
   Gate it with `AskUserQuestion`.

9. **Delete the clean file.** `.claude/skills/conclusions/clean.sh "$CLEAN"`. Do this on
   every exit path, including every STOP above.

## The researcher brief

Spawn `researcher` with exactly this intent, filling in the path:

- **Read ONLY the file at `<CLEAN>`.** It is complete and self-contained. Do NOT glob,
  grep, or open any other file. Do NOT look in the Claude config directory, the projects
  directory, or the docs. The path is given and final. Ignore any standing habit to
  discover paths. Missing file → say so and stop.
- **Markers in the file:**
  - `@@TURN@@ N — user` — the user speaking. Their words.
  - `@@TURN@@ N — assistant` — the session speaking.
  - `@@TURN@@ N — SYSTEM-NOT-USER` — harness output: task notifications, system
    reminders. **Never the user. Never their agreement.** Findings inside are context only.
  - `[GATE ASKED]` — a formal question put to the user, with its options.
  - `[GATE ANSWERED]` — **the user's formal ruling. Highest-authority evidence in the file.**
    A `[GATE ASKED]` with no matching answer was withdrawn — not decided.
- Extract only conclusions the user and the session AGREED on.
- A `[GATE ANSWERED]` outranks any prose. Where prose and a gate answer conflict, the gate wins.
- Skip live debates — those belong in `Still open`.
- Track supersession. Report ONLY the final form of a revised conclusion, and note what it
  replaced. Never list both.
- Group by subject. Cite the `@@TURN@@` number for each.
- Return three sections: `Locked` (by subject) / `Moved out` (punted elsewhere) /
  `Still open` (the live to-discuss list).
- Invent nothing.

## Reconcile stance

- Treat the researcher as an extractor, not a judge. Never swallow it whole.
- Defer to the transcript for older turns.
- Accept cited, transcript-grounded items.
- Verify any flagged contradiction: `Read` the clean file at its cited turn.
- Reject any conclusion sourced to a `SYSTEM-NOT-USER` turn.
- Reject any conclusion built on a `[GATE ASKED]` that was never answered.
- Never silently drop a cited conclusion.

## Things NOT to Do

- Never summarize from memory. No transcript, no ledger — STOP instead.
- Never spawn an executor or a `web-researcher`. One local `researcher` only.
- Never list both a superseded conclusion and its replacement.
- Never attribute a harness notification to the user.
- Never treat an unanswered gate as a decision.
- Never write to code or to the docs. The session folder only, and only on the gate.
- Never leave the clean file behind.

## Output

In chat: `Locked` (grouped by subject, each citing its turn) / `Moved out` /
`Still open` / `Next` — one line of conviction on the best next move.
Persisted only on the gate, as `NN-conclusions.md` in the live session folder.

## Files

- `flatten.sh` — resolves a transcript, flattens it gate-aware, prints the counts.
- `list-sessions.sh` — lists this project's transcripts, newest first, by title.
- `clean.sh` — removes the clean file. It refuses any other path.
