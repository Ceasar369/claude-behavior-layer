---
name: prove
description: Proves whether a claim a session made is actually written anywhere, using cold collectors and one judge. Use when the user demands a source — "prove it". Anti-case: attacking a conclusion on the merits is `challenge`.
argument-hint: "[the claim] — or point at what the session just said"
allowed-tools: Bash, Agent, SendMessage, AskUserQuestion
---

# Prove

## Anchor

Follow the root `CLAUDE.md`. Evidence over assertion, truth over agreement.
A claim that cannot be quoted was invented. Say so plainly, even when the session is this one.

## Purpose

Establish whether a claim is written anywhere, and quote it or report it invented.

## Steps

1. **State the claim.** Quote what the session actually said. Verbatim, never a summary.
2. **Split it.** "We agreed X, per rule Y" is two claims. One claim, one proof.
3. **Take the pointer, if there is one.** If the session named a source, record it. Check it first. Never treat it as the boundary. If the session cannot name one, record that — it is already evidence.
4. **Name the homes.** Use the table below as a starting order, never a boundary. Sweep past it always.
5. **Name the angles — both directions.**
   - **Confirming:** the claim's own words, synonyms, the concept, any code identifier.
   - **Falsifying:** the competing option, the decision *not* to do it, the negation, the term that would appear if the opposite were true.
   One term is a false negative waiting to happen. Confirming terms alone find only support.
6. **Gate the spawn.** `AskUserQuestion` — Header `Prove`; Question `Run these <N> collectors?`; Options `Run them` (recommended) / `Add angles` / `Redirect`.
   - No spawn until an explicit yes.
7. **Spawn the collectors — parallel, one per home.** `researcher` for the docs, the code, and the behavior layer. `web-researcher` when the claim cites an external source. Put the collectors' rule below into every prompt. Resume a live agent with `SendMessage`, never a fresh spawn.
8. **Spawn one judge after every collector returns.** A `researcher`, given every quote at once. Put the judge's rule below into its prompt.
9. **Verify every quote mechanically.** For each quote the judge returns, grep a distinctive fragment of it in the named file. Take the line number from the grep, never from the judge.

   A miss is unverified, not yet fabricated. Prose wraps, so a quote spanning two lines never matches as one string. Re-grep the longest fragment that sits on a single line. Still nothing → report it fabricated.
10. **Report the verdict.** Never soften it. Never overturn it on disagreement.

## The homes — a search order, never a boundary

| Claim type | Sweep first |
|---|---|
| A standing rule or convention | `docs/` |
| A decision was made | `archive/` — the dated day files |
| Product, architecture, or an open question | `docs/` |
| Code exists, or behaves a way | the worktree, or the code checkout — grep the code, never a doc |
| The behavior layer itself | `.claude/`, `CLAUDE.md` |

## The collectors' rule — put this in every collector prompt

Collectors find. They never conclude.

- Return every occurrence. Never stop at the first hit.
- Quote verbatim, with path and line. Never paraphrase.
- No verdict, no opinion, no "this proves it".
- **Your `Findings` field is the raw list of occurrences and nothing else.** It is not a
  direct answer. You have no answer to give.
- Report the search itself: every path walked, every term tried, confirming and falsifying.

## The judge's rule — put this in the judge's prompt

Read every collector's quotes at once. Rule once.

Six verdicts:

- **Found, once, consistent** — quote it.
- **Found many times, consistent** — quote them all.
- **Found many times, contradictory** — quote every side.
- **Found, but it says something different** — drift. Quote the claim and the source together.
- **Not found** — only with the full search log, every path and every term. `Not found` means
  not found by these terms in these homes. It never means nowhere. State the bound.
- **Search incomplete** — the log skips an angle the premise named, or the angle list carried
  no falsifying terms. Name what is missing. The claim stays unproven either way.

**Rule on the angle list too.** It was written by the session whose claim is on trial.
A thin list buys a clean `not found`. Judge whether the angles were sufficient, and return
`search incomplete` when they were not.

## Things NOT to Do

- Never search for evidence inside this skill. Collectors search.
- Never grep except to confirm a quote the judge already returned.
- Never rule on the claim yourself. The judge rules.
- Never rule on whether your own angle list was sufficient. The judge rules.
- Never spawn an executor. `researcher` and `web-researcher` only.
- Never accept a paraphrase as proof. "It basically says" is where a hallucination hides.
- Never let one collector both find and judge.
- Never stop a sweep at the first hit. A contradiction is only visible in the full set.
- Never treat the session's pointer as the boundary of the search.
- Never trust a line number the judge reports. Grep it.
- Never soften a `not found`. An invented claim is reported as invented.
- Never overturn a verdict because you disagree. Escalate merit disputes to the user.

## Output

Chat only. The premise — split claims, pointer, homes, angles both directions.
Then the verdict, its quotes, and the grep result for each. No files.
