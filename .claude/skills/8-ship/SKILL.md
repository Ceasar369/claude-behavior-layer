---
name: 8-ship
description: Commits, pushes, opens a PR, and merges. Reads the diff, authors the message, gates in the terminal, then runs git itself. Use for "ship it" or "commit this". Never called by /9-stop.
allowed-tools: Bash, Read, AskUserQuestion, Agent
argument-hint: "[what to ship] — omit it and the current branch's changes are the scope"
---

# 8 — Ship

## Anchor

Follow the root `CLAUDE.md`. Never log a secret, a credential, or personal data.

## Purpose

Decide what ships and how far, gate it with the user, then run the git sequence.

## Run it silently

Steps 1–5 are mechanics. Do them without narration — never announce reading git state, reading the diff, or setting a marker. Surface three things only: the ship plan at the gate, a detected conflict, and the result.

## Approval already in hand — one caller only

A full ship — PR or merge — always gates. Never skip it.

Commit-only depth skips Step 6 in exactly one case: `plan-agents`' phase checkpoint (`own-execution.md`) where the user chose `Commit + continue`, this turn.

- `/9-stop` never supplies approval. It does not ship and has no ship gate.
- An answer pulled by `/4-inbox` never supplies it. That confirms the work, not the commit. Gate here.

In that one case: show the plan briefly and go to Step 7. No gate. Never infer approval loosely.

## Steps

1. **Resolve the repo and its root.** Two repos exist, with different roots.

   | Repo | Root | Remote |
   |---|---|---|
   | Code | `.worktrees/<branch>/` | yes |
   | This layer repo | the repo root | maybe |

   **Code lives in a worktree, never in the primary checkout.** Resolve it:
   ```bash
   git -C "$CODE" worktree list
   ```
   Take the `.worktrees/<branch>/` entry for this session's work — the lock's `Branch:` names it. The primary checkout stays pristine on the integration branch and has nothing to commit; point git there and it stages nothing and reports success.

   Then in that root: `git branch --show-current`, `git status --short`, `git remote`.

   Remoted and on the integration branch → stop. Never commit to a remoted integration branch.
   No remote → see `## A repo with no remote`.

2. **Decide the files.** From `git status --short`, list every path explicitly. Never "all". Unrelated changes mixed in → stage only what this ship is about, and say what you left out.

3. **Author the message.** Read the diff first — `git diff -- <files>` and `git diff --staged -- <files>`. Write from what you see, never a guess. Follow `## Commit Message Standard`.

4. **Decide the depth.**
   - **Commit-only** — commit and push the branch. No PR, no merge.
   - **Full ship** — commit, push, PR, merge.

5. **Conflict pre-check — full ship only.** Run the merge dry-run in the worktree before the gate. See `## Conflict handling`. Only a clean or resolved tree proceeds.

6. **Gate it.** Present the plan: repo, root, the explicit file list, the message, the depth, and — for a full ship of code — that the worktree will be torn down.

   `AskUserQuestion` — Header `Ship`; Question `Ship this? <repo + depth>`; Options `Ship it` (recommended) / `Adjust` / `Cancel`.

   `Adjust` → revise and re-present. `Cancel` → stop.

7. **Run it.** Read `git-sequence.md` beside this file and follow it exactly. Stop at the first failure and report it. Never skip forward.

## A repo with no remote

A repo with no remote has no push, no PR, and no `gh`. It may carry a working branch beside the integration branch.

**Committing.** Steps 4, 5, and 7 collapse to: decide the files, author the message, gate as in Step 6 (Question `Commit on <branch>? <recap>`), then run `git-sequence.md` section 1, stopping before the push.

Committing to the integration branch here is correct — no remote means the never-commit rule does not apply.

**Folding a working branch back.** A local merge is the only route. Never `gh`.

```bash
git -C <root> checkout <main> && git -C <root> merge --no-ff <branch>
```

Gate it first — Header `Merge`; Question `Fold <branch> in? Local, no remote, no undo.`; Options `Merge it` / `Stay on the branch`.

Report the merge output. Never delete the branch unless the user asks.

## Conflict handling

Never auto-resolve a merge conflict.

1. **Detect.** Fetch the integration branch, then in the worktree: `git merge --no-commit --no-ff origin/<main>`, and `git merge --abort` after reading the result. Clean → the gate. Conflict → step 2.

2. **Present it here, gate here.** A merge decision stays with the user in the terminal. Never hand it to another skill.

   Present it yourself: which files conflict, what the resolution changes, and any **destructive repercussion** — a dropped hunk, an overwrite of another session's change.

   `AskUserQuestion` — Header `Conflict`; Question `Resolve this conflict and continue the ship?`; Options `Resolve it` / `Stop the ship`.

   `Stop the ship` → stop. Nothing committed, nothing merged, no executor spawned.

3. **Resolve — only on approval.** The executor owning that lane applies the resolution in the worktree, then re-verifies green.

4. **Re-check.** Re-run the dry-run. Clean → back to Step 6.

## Commit Message Standard

Read from the diff, never invented. Every claim maps to a real change.

**Title.**
- Ideally ≤5 words. Hard cap ~50 characters — readable at a glance in a list.
- Imperative: "Add", "Fix", "Refactor", "Remove". Never "Added" or "Adds".
- Capitalized, no trailing period. Names the ONE main change.
- Cannot say it in five words → the commit does too much. Flag that.
- `Add token refresh endpoint` · `Fix tenant row-level leak`

**Body.**
- One blank line after the title, then 1–4 short lines.
- What changed and WHY. The diff shows the how.
- Wrap near 72 characters, one idea per line.
- Omit only for a truly trivial change.

**Always.** No secrets, no credentials, no personal data. One commit, one coherent change.

## Things NOT to Do

- Never commit to the integration branch in a remoted repo. A repo with no remote is the exception.
- Never run git in the primary code checkout. It is pristine; a commit there stages nothing.
- Never run `git checkout <main>` inside a worktree. It fails, and an `&&` chain then skips everything after it.
- Never tear down a worktree whose branch is not merged. `teardown.sh` refuses; do not work around it.
- Never ship without approval — from the gate, or in hand this turn. No approval → never ship.
- Never skip the gate for a full ship. Only a commit-only checkpoint skips.
- Never stage a file you did not list.
- Never pass `--delete-branch` to `gh pr merge`. Never force-push.
- Never author a vague message. Title says what; body says why.
- Never treat a `/9-stop` this turn as approval. `/9-stop` does not ship.
- Never route a conflict decision to another skill or session. It gates here.
- Never add `disable-model-invocation` — it severs `plan-agents`' checkpoint call.
- Never report a step done without its actual output.

## Output

The plan as shown at the gate, then every line the sequence produced — commit, push, PR URL, merge status, teardown result, or the failure that stopped it.

## Files

- `git-sequence.md` — the exact command order. Read it at Step 7.
- `teardown.sh` — removes a merged branch's worktree and updates the primary checkout.
