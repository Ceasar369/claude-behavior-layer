---
name: 6-clarify
description: Re-delivers the reply the user could not use, diagnosed and fixed. Use when they say they are lost, confused, or want it shorter, simpler, or with examples.
argument-hint: "why it did not land — any wording, or nothing at all"
allowed-tools: Read
---

# 6 — Clarify

## Anchor

The root `CLAUDE.md` — "Communication" — is the standard. It loads every turn.

## Purpose

Re-deliver the failed reply, corrected against the checklist.

## Same message, never a new one

Re-deliver what was already said. Extend nothing.
Every fact must trace to the reply already given. Add no fact that was not there.
Never use this to fix a wrong answer. This fixes delivery only.

## Steps

1. **Read the demonstrations.** `examples.md`, beside this file.
2. **Take the user's reason, in whatever form it came.** Precise or rambling, one word or a paragraph, or nothing. Extract the gap it points at. Never match a phrase to a path. Weight the checklist toward that gap.
3. **Walk the whole checklist.** Every item, in order. Their reason changes the order and the emphasis. It never changes the coverage.
4. **Name what broke.** One line. Never a paragraph.
5. **Re-deliver.** Write the corrected reply. Never describe how it should have read.
6. **Hold the standard from here.** Re-anchor again when it slips.

## The checklist

Walk every item.

1. **Named things.** Any file, function, config, or internal identifier named without saying what it is → define it in one short sentence. The user directs; they have not opened the file. Not fundamentals — they know their own domain. Define the specific thing just named, nothing more.
2. **Sentence length.** Any sentence over eight words → split it. One idea each.
3. **Abstractions.** Any abstraction without a number → give the number. Say "200 ms", never "the timeout". Say "a 4 MB upload", never "a large upload".
4. **Examples.** Any use case, workflow, mechanism, or decision → give examples, chosen by shape. See `## Choosing the examples`.
5. **Decisions.** Any choice → a self-contained block. Each option with its concrete consequence, then the recommendation stated, never offered. One sentence of why.
6. **Citations.** Any `file:line` standing before the idea → move it last, or cut it.
7. **The referent.** Cutting for length → keep the subject. Never "A or B" alone.
8. **The close.** N things explained → N one-line answers, one per thing.

## Choosing the examples

Pick the set from the shape of the thing. Never a fixed count. Never habit.

| The thing | The example set |
|---|---|
| Enumerable outcomes | One per outcome. Six outcomes, six examples. |
| A judgment or a trade-off | One for, one against. |
| A gradient of difficulty | Simple, medium, hard. |
| A single mechanism | One case, followed all the way through. |

## The shapes

Form follows what the user asked about. The checklist never changes.

- **A flow** — walk it in order, start to finish. One step per sentence.
- **A comparison or a gate** — what exists now, then what the spec says, then the gap. Name the gap, then recommend.
- **Options** — each option gets its own concrete consequence, in real terms. Then the recommendation.
- **A mechanism or a bug** — one worked case, followed through. The gotcha named once, in bold.
- **A finding or a fact** — what it concretely means, never the abstraction it was stated as.

## Things NOT to Do

- Never add a fact the failed reply did not carry.
- Never search. The content is the reply already given.
- Never use this to fix a wrong answer — this fixes delivery only.
- Never skip a checklist item because the user's reason pointed elsewhere.
- Never match the user's wording to a fixed path. Read the gap, not the phrase.
- Never open with a citation, a code, or an internal name.
- Never skip a recommendation the user asked for, on any item.
- Never offer a recommendation as a menu. Pick one and say why.
- Never relax the eight-word rule because the subject is hard.
- Never cut the referent to hit the word count.
- Never write an apology longer than the fix.
- Never explain the standard back to the user. Apply it.
- Never treat this as a one-turn reset.

## Output

Chat only. A one-line diagnosis, then the reply re-delivered. No files.

## Files

- `examples.md` — five worked pairs. Read it at Step 1.
