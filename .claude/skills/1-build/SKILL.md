---
name: 1-build
description: Opens the code lane. Checks the requested paths against every lock, gates the claim, then one script reuses or cuts the branch worktree and finalizes the lock. Run before the first code write.
allowed-tools: Read, Edit, Bash, AskUserQuestion
argument-hint: "[the code paths this work owns] — e.g. src/api/billing/"
---

# 1 — Build

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Claim the code paths and put the session in a worktree. Nothing else.

## Step 1 — Scope the paths

Name the path prefixes this work owns. Narrow beats broad.

Take them from the user's direction. Never widen a scope they named.

## Step 2 — Check every lock, and see what already exists

```bash
.claude/skills/1-build/locks.sh --paths "<p1>,<p2>"
```

It prints `OVERLAP=yes|no`, then the full body of every colliding lock, each tagged `LIVE` or `CLOSED?`, then every worktree that already exists with its branch, its commits ahead of the integration branch, and its uncommitted count.

**Read every `CLOSED?` body before dismissing it.** A block marked closed in its header can still hold its claim — one may read *"Lock HELD, not cleared; the WORK IS NOT DONE"* and forbid any other build on its branch.

## Step 3 — Continue existing work, or name a new branch

**Match the user's words against the worktree list first.** People name the work, never the branch — "continue the retry policy", "pick the auth rewrite back up", "keep going on that build". A branch on that list whose name or lock plainly matches is the branch. Reuse is the default, not the exception.

Weigh the whole line, not the name alone: commits ahead and an uncommitted count are unfinished work living on that branch.

Uncertain which of two existing branches they mean → ask. Never guess between two, and never cut a new branch to sidestep the question.

Only when nothing on the list matches: name a new one — `fix/<slug>`, `chore/<slug>`, or `feature/<slug>`. The script rejects anything else.

## Step 4 — Gate the claim

`AskUserQuestion` — Header `Claim`; Question `Claim these paths and open the worktree?`

Show the paths, the branch, and — stated plainly — whether this **continues** an existing worktree or **creates** a new one. If it continues, quote that branch's commits ahead and its uncommitted count.

- `OVERLAP=no` → Options `Claim it` / `Adjust the paths` / `Don't claim`.
- `OVERLAP=yes` → Options `Narrow the paths` / `Wait for that lock` / `Fold into that work` / `Claim anyway`.
- **Creating new while a worktree exists** → add `Continue <that branch> instead` as the first option.

Never claim overlapping scope on your own judgment.

## Step 5 — Run `worktree.sh`

```bash
.claude/skills/1-build/worktree.sh --branch <branch> --slug <lock slug> --paths "<p1>,<p2>"
```

`<lock slug>` is this session's lock name — the folder name minus its number. Get the folder name from `python3 .claude/tools/bus.py whoami`.

It prints `ACTION=reuse|attach|create`, `WORKTREE=`, `LOCK_UPDATED=`, then `git worktree list`.

- Exit 2 — bad arguments, or no code checkout configured. Report and stop.
- Exit 6 — git refused. Report the message and stop.
- Exit 7 — the worktree exists but the lock did not update. Report and stop.

## Step 6 — Log it

Append one line to the session's `00-session.md` decision log: the paths, the branch, and the `ACTION`.

## Step 7 — Name the build shape

The claim is open. Say which shape this work is, in one line.

- **Standard** — a fix, a chore, a feature. Plan, then build.
- **Slice** — delivery against a designed plan. No new machinery.
- **Pillar** — a genuinely undesigned subsystem. Seven steps.

Pillar only when nothing designs this subsystem yet. It is rare.
Feature delivery is a slice. Default away from pillar.

Slice → run the six steps in `.claude/playbook/slice-delivery.md`.

Pillar → run the pipeline in `.claude/playbook/pillar-design.md`. Its documents
go in their own subfolder, per that document. Never flat in the session folder.

Naming the shape is all this skill does. It runs none of them.

## Things NOT to Do

- Never cut a second worktree for a branch that has one. `ACTION=reuse` means attach.
- Never write in the primary code checkout. It stays on the integration branch. `guard-infra.sh` blocks it.
- Never give an executor `isolation: worktree` — parallel executors share this one.
- Never claim paths that collide with a live lock without an explicit `Claim anyway`.
- Never dismiss a `CLOSED?` collision without reading its body.
- Never let an executor commit, PR, merge, or ship.
- Never write the lock by hand. `worktree.sh` owns `Branch:` and `Paths:`.
- Never add `disable-model-invocation` — a session runs this itself, before
  its first code write. The claim gate is the control, not the flag.

## Output

The worktree at `.worktrees/<branch>`, `Branch:` and `Paths:` written into the lock, one decision-log line, and the named build shape.

## Files

- `locks.sh` — the collision check. Read-only.
- `worktree.sh` — reuse or cut the worktree, then finalize the lock.
