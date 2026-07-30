---
name: 2-ask
description: Writes one question into this session's folder, then stops. Use when the work is blocked on the user and they may be in another window. May arm a waiter that resumes this session when the answer lands.
allowed-tools: Read, Write, Bash, AskUserQuestion, Agent
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

`.claude/playbook/ask-answer-bus.md` holds the design this rests on.

## One question, then stop

A question is one file. Its answer is a second file with the same number.

**Never ask twice without an answer.** Asking ends the turn. Do not work around it.

Anything new is a new question, never a follow-up on an old one.

## Steps

1. **Gate the depth and the waiter.** One `AskUserQuestion` call, two questions.

   Header `Depth`; Question `How deep should this ask go?`
   - `Exact target` — this question only. Nothing added.
   - `Bundled with research` — this question, every coupled question, plus bounded research on the subject.

   Header `Waiter`; Question `Resume this session automatically when the answer lands?`
   - `Arm the waiter` — Step 5 arms it. `/4-inbox` runs itself.
   - `No waiter` — the user runs `/4-inbox` here when they return.

   The user's `/2-ask` line may already settle either. Then do not re-ask it.

2. **Compose the question into a temp file.** Plain text. Fold in whatever the user's `/2-ask` line adds — that line is theirs, and it is trusted.

   Every ask obeys `## The coupled knot` and `## The answer shape` below.

   `Bundled with research` also spawns research, per `## What bundled adds`.

3. **Pick a slug.** Lowercase kebab, from the subject. Three or four words. `retry-backoff`, `timeout-vs-deadline`. It becomes part of the filename, so the subject reads without opening the file.

4. **Write it.**
   ```bash
   python3 .claude/tools/bus.py ask <slug> "$MSG_FILE"
   ```
   It resolves this session, takes the next number, and writes atomically. Read `ASKED=`, `ANSWER=`, `NUMBER=`, and `SESSION=` back from its output.

   `ANSWER=` is the path the answer will take. Nothing derives it by hand.

   `WARN=already open` on stderr → a question was already open. Say so plainly and name both numbers. Never hide it.

5. **Arm the waiter — only if gated on.** Per `## The waiter`.

6. **Confirm, then stop.** End the turn with this shape and nothing after it:

   ```
   ❓ ASKED → <NUMBER> <slug>

   <the ASKED= path, real output, never remembered>

   Next:

   /3-answer <SESSION>

   Waiting — /4-inbox runs itself.
   ```

   The `/3-answer` line is always there. It is how the user answers.
   It stands alone, blank line each side. Nothing shares it.

   The last line appears only when the waiter is armed. The waiter never
   replaces the `/3-answer` line. It governs what happens after the answer
   lands, never how the user writes it.

   Then stop. The turn is over.

## The coupled knot

One file, not one interrogative. The file carries the whole knot.

Two decisions are coupled when ruling one changes the other.

Put every coupled decision in. Number them. Never split a knot across two asks.

Uncoupled and merely nearby? Leave it out. This is not a dumping ground.

## The answer shape

A question that can be answered vaguely will be.

Every ask closes with a section titled `What a complete answer must contain`.

It names, explicitly:

- Every decision that needs ruling. One numbered line each.
- Concrete options where they exist, so the answer can be a pick.
- What this session does with each possible answer.
- What is **not** needed, so no effort is wasted on it.

State your own position on each decision. A question with no position invites one.

## What bundled adds

Two things, and nothing more.

- **Every coupled question already in view.** Anything this session knows it will
  ask next about this subject. Ask it now, in the same file.
- **Bounded research on the subject.** One `researcher` or `web-researcher`,
  read-only, scoped to the questions asked. Never an executor.

Fold findings in as stated facts, with their source. Never a raw dump.

Never widen the subject. Bundled means fuller, never broader.

## The waiter

A detached shell process. It watches for the answer file and exits.

Paste the `ANSWER=` path verbatim. Never edit it, and never build it from `ASKED=`.

```bash
for _ in $(seq 960); do [ -f "<ANSWER= path>" ] && break; sleep 30; done
```

Run it with `run_in_background: true`.

It exits when the answer appears, or after eight hours. Either way this session
wakes once and runs `/4-inbox`. An empty inbox there just stops.

The waiter reads nothing and moves nothing. Manual pull is always the fallback.

## No polling

Never check the inbox in a loop of turns. Never wait inside a turn.

The waiter is a shell process. Zero turns while it waits, one wake when it exits.

## Things NOT to Do

- Never ask a second question while one is open.
- Never read or wait for the answer inside this turn — that is `/4-inbox`.
- Never arm a waiter that was not gated on.
- Never arm more than one waiter.
- Never arm a waiter without a bound. Eight hours is the cap.
- Never type or edit the waiter path. Paste `ANSWER=` verbatim.
- Never drop the `/3-answer` line. The waiter adds, it never replaces.
- Never split coupled decisions across two asks.
- Never ship an ask with no `What a complete answer must contain` section.
- Never research beyond the subject asked, or spawn an executor.
- Never send the whole transcript. The questions, their options, and the findings.
- Never rename or hand-edit a question file.
- Never boot, spawn an executor, write docs, or touch code.

## Output

One `90-NNNN-<slug>-ask.md` in this session's folder, written atomically, and the confirmation block as the last thing in chat. The turn ends.

Waiter armed → one detached background process, and this session resumes itself.
