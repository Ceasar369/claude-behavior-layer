---
name: doc-check
description: Finds where the docs contradict the actual code. Gathers what changed, fans out researchers by subject, returns each contradiction with its paths. Read-only — it never fixes.
allowed-tools: Read, Bash, Agent, AskUserQuestion
argument-hint: "[optional scope] — a subject, a path, or nothing for everything that changed"
---

# Doc Check

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Name every place a doc claims something the code contradicts. Evidence, never recollection.

## Step 1 — Gather what changed

```bash
.claude/skills/doc-check/changed.sh [--folder <NNNN-slug>]
```

It prints this repo's working tree, every worktree's diff against the integration branch, the claimed `Paths:` from each lock, and any doc-sync flags in the session's work summaries.

A scope was given → narrow to it. No scope → everything the script returned.

## Step 2 — Split by subject

Group the changed files by subject, never by file. One subject per researcher.

A subject is a thing a doc describes — the job queue, the auth seam, the boot skills. Not a directory.

Two to six subjects. More than six means the scope is too wide — say so and narrow it.

## Step 3 — Fan out

Spawn one `researcher` per subject, all in one message so they run concurrently.

Each spawn carries:
- **Purpose** — one line: find where the docs contradict reality on this subject.
- **Read first** — the exact changed files, and the exact docs that describe them.
- **Return** — one row per contradiction: the doc path and line, what it claims, what reality is, and the file and line proving it.
- **Never** — propose a fix, judge severity, or report a doc as stale without the proving path.

Return nothing found when nothing is found. A quota invents findings.

## Step 4 — Merge inline

Merge the returns yourself. Never spawn an agent to merge another agent's output.

Drop any row whose proving path you cannot confirm by reading it. An unproven row is not a finding.

## Step 5 — Sweep for what nobody was assigned

A researcher reads the paths its spawn named. A stale file nobody named stays unread.

So grep the whole doc surface for every dead name the merge surfaced — a retired skill, a removed flag, a renamed path. Every hit outside a researcher's read list is a finding the fan-out missed.

Exclude the archive and past session prompts. Those record history.

## Step 6 — Present

One row per contradiction: the doc path, what it claims, what is true, the proof.

Order by consequence — auth, permissions, and data integrity first. Then say plainly what was checked and found clean.

## Step 7 — Gate the fixes

`AskUserQuestion` — Header `Fixes`; Question `Which of these to fix now?`; `multiSelect: true`.

The tool takes four options at most. Three findings or fewer → one option each, plus `Fix none`. More → group them by subject into three, and say in chat which findings each option carries.

Doc and behavior fixes: the session writes them. Code fixes: an executor.

## Things NOT to Do

- Never write a doc in this skill. Reviewing and fixing are two actions.
- Never report a contradiction without the path and line that proves it.
- Never split by file. One concern per researcher.
- Never trust the fan-out for coverage. It reads only what its spawns named.
- Never let a researcher merge another researcher's output.
- Never spawn `web-researcher` — this is local docs against local reality.
- Never claim a doc is current because nobody flagged it. Read it.
- Never pad the list to look thorough.

## Output

A row per contradiction — doc path, its claim, the truth, the proof — then the gate result. No files written.

## Files

- `changed.sh` — what changed, across the docs, the worktrees, and the locks.
