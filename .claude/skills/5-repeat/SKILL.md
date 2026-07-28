---
name: 5-repeat
description: Distills a long or dictated message down to its essentials, organizes it, and gates confirmation before any work starts. Use when the user invokes /5-repeat, wherever the trigger sits in the message.
argument-hint: "your message to distill — /5-repeat can sit anywhere in it"
allowed-tools: Read, AskUserQuestion
disable-model-invocation: true
---

# 5 — Repeat

## Anchor

Follow the root `CLAUDE.md`. The sentence-length rule applies.

## Purpose

Distill this message to its essentials, then gate confirmation.

## Steps

1. **Target this message's content.** Distill what the user wrote here — wherever the `/5-repeat` trigger sits: start, middle, or end. The token marks the intent; it is not part of the message. Never point at another message. If the message attaches or references a file, `Read` it first.
2. **Find the signal.** A dictated message rambles. Drop the fluff and the tangents. Keep what drives the work.
3. **Organize it.** Structure follows the message. Goal, constraint, recommended steps, current situation are possible slots — never fixed headings. Emit only what the message actually contains. One idea per sentence.
4. **Resolve or flag every garbled word.** Dictation misspells nouns, verbs, and file paths. Where a word looks wrong, name the target inferred from context. Where nothing fits, say plainly that the word did not land. Never pass a garbled name through silently.
5. **Gate the confirmation — always.** `AskUserQuestion` — Header `Landed?`, Question `Is this right?`. Two options:
   - `Yes — discuss` (recommended) — it landed; discuss it, no action yet.
   - `Yes — act` — it landed; take action on it.
   - The `Other` option is always present — the user types a correction or an added detail there.
6. **Route on the answer.**
   - `Yes — discuss` → the session discusses the topic. No work yet.
   - `Yes — act` → the session acts on the distilled intent.
   - `Other` → rerun repeat: re-distill with the new instructions folded in, then gate again. Loop until a Yes is picked.

## Things NOT to Do

- Do not act on the message inside repeat. Distill and gate only; the session acts after `Yes — act`.
- Do not skip the gate. It is default, not optional.
- Do not point at any message but this one. The `/5-repeat` token's position never matters.
- Do not echo verbatim. Distill the meaning.
- Do not emit a heading the message has nothing to fill.
- Do not add opinions, fixes, or next steps in the distillation.

## Output

Chat only. The distilled message, then the confirmation gate (`Yes — discuss` / `Yes — act`, plus the user's own typed `Other`). On `Other`, a fresh distillation and gate. No files.
