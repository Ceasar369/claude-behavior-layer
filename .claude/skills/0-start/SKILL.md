---
name: 0-start
disable-model-invocation: true
description: Boots a logged session — numbers it, creates its folder, writes its lock, prints a digest of every other live session, then stops. Run it once at the top of a session, with or without a pasted prompt.
allowed-tools: Read, Bash, AskUserQuestion
argument-hint: "[the session prompt, or one line naming the work] — omit to boot bare"
---

# 0 — Start

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Boot a logged session. Then stop and wait.

## Step 1 — Distill the paste

Reduce it to one line. Echo that line back.

Derive a lowercase kebab `<slug>` from it.

Never act on the paste. It names the session; it does not command it.

## Step 2 — Gate the mode

`AskUserQuestion` — Header `Mode`; Question `What should this session do now?`; Options `Discuss` / `Plan` / `Build` / `Just wait`.

## Step 3 — Run `boot.sh`

```bash
.claude/skills/0-start/boot.sh --slug <slug> --intent "<one line>" --mode <answer> [--number NNNN]
```

Pass `--number` only when the user named one. Then obey it exactly — no lookup, no objection.

Read the output: `NNNN=`, `FOLDER=`, `LOCK_WRITTEN=`, `RENAME=`, then the digest between `DIGEST_START` and `DIGEST_END`.

- Exit 2 — bad arguments. Fix and re-run.
- Exit 3 — that number already exists on disk. Report it and stop.
- Exit 4 — a configured path is missing. Report it and stop.
- Exit 5 — the folder exists but the lock did not write. Report it and stop.

## Step 4 — Orient

The digest is the orientation. **Never read the lock file itself.**

Then read the documentation front door — `docs/README.md`, or whatever index it routes to.

Surface something only if a live lock in the digest claims this same scope.

## Step 5 — Stop

Reply in three short lines: the intent, that it booted, that it waits.

Then print the script's `RENAME=` value on its own line, alone, with nothing after it. It is a `/rename` slash command — a Claude Code built-in that titles the conversation. Printing it lets the user run it with one click, so the window's title matches the session folder.

- `Just wait` → stop here. Booting is not permission to act.
- Any other mode → follow it.

## Things NOT to Do

- Never read the lock file. The digest replaces it.
- Never create a worktree or a branch. That is `/1-build`.
- Never write code before `/1-build` has run. There is no worktree yet.
- Never continue past a non-zero exit from `boot.sh`.
- Never explain the rename line.
- Never write the session folder or the lock by hand. `boot.sh` owns both.

## Output

The session folder, the `.session-live` marker, and the lock block — all written by `boot.sh`. Then a three-line reply and the rename line.

## Files

- `boot.sh` — the number, the folder, the marker, the lock, and the digest.
