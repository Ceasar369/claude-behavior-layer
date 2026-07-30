# Cold Audit

How consequential work gets proved before it ships.

**Trigger** — a consequential build is finished and proven by its builder.

**Done** — the audit returns clean, and build and audit close as a pair.

Built is not shipped. The builder's word is not proof.

A fresh, independent session audits the work cold.

## When it applies

- Any consequential build. Auth, permissions, schema, a whole phase.
- Anything non-trivial, at any scope. The loop is phase-agnostic.
- A trivial fix or chore skips it. That is the user's judgment.

## Who does what

- **Build session** — built the work and proved it. Later applies the fixes.
- **Audit session** — fresh, cold, independent. Forms its verdict from
  ground truth. Re-audits the fixes. Keeps its context across rounds.
- **The user** — writes the audit prompt, judges the findings,
  routes fixes, decides ship. They sit between the two sessions.

## The loop

1. **Build, proven.** The build session finishes and proves its work.
2. **Write the audit prompt.** The user writes it themselves.
   They oversaw the build, so they name exactly what to audit.
3. **Audit cold.** A fresh session boots with that prompt.
   It fans the audit across parallel researchers, immediately.
   It does not re-plan. The scope is already named in the prompt.
   It forms its verdict from ground truth — committed code and the docs.
   It reads the builder's self-report only after its verdict.
   That report is context. It is never truth.
   Findings go in an audit file, not a research file.
4. **Judge.** Vetted on proofs, not claims. Clean ships. Gaps route back.
5. **Fix.** The findings return to the build session. It applies them.
6. **Re-audit.** The same audit session re-checks. It kept its context.
   It fans out again, every round. Never a single-threaded re-check.
   It re-verifies from the code. Never "confirm it is fixed" —
   that phrasing invites a rubber-stamp.
   The re-check goes in a reaudit file.
7. **Loop if needed.** A complex fix takes several rounds. Expect that.
8. **Close together.** When clean, close the build and audit as a pair.
   The close names what landed. Findings did not go unnoticed.

## Writing the audit prompt

Nail these before writing:

- **Who does what.** The audit audits. The build fixes. The user ships.
- **Where.** Ground truth — committed code and the docs. Name the exact scope.
- **What to reference.** The precise docs and code paths.
- **Tempo.** Tell it not to re-plan. Tell it to fan out immediately.

The prompt is read-only in scope. It is the user's to write.

## The roles are declared once

The user names both roles when the loop starts. Once, not per hop.

Each session knows its role because they said so. Never by guessing.

If it does not know, it asks. Once.

They carry every message between them. No session reaches another.

## Steer whoever has the next move

One steer per real event. Two events per round: the verdict, and the fixes.

- **Verdict sound** → the move is the build's. Route the fixes there.
  Confirm with the user first on a correctness-critical path. Write nothing
  to the audit. The audit goes idle. It is never told to stand by.
- **Verdict thin, or it contradicts the code** → the move is the audit's.
  Write the dig there, and nothing to the build.
- **Both have real moves** → write to both.
- **The fixes land** → the move is the audit's. Send the re-audit.

The build's "fixes applied" is a doorbell, not a payload.
The audit re-verifies from code, never from the builder's report.

## Honest deferrals

- Some findings are fairly deferred to a later phase.
- State each deferral plainly. Never leave it to memory.
- Home each one with an explicit trigger.
- Let the auditor judge the deferral too.

## Two things this is not

- Not the builder's own verify. That check is internal to the build session.
  This audit is independent. It does not replace that one.
- Not a review of a skill or an agent. Cold audit means the built code.
