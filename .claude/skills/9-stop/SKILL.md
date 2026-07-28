---
name: 9-stop
disable-model-invocation: true
description: Closes a session. Verifies only if `/1-build` ran, reports what would be lost, composes the archive prose, then one gate prunes the folder and clears the lock. Never commits — that is `/8-ship`.
allowed-tools: Read, Write, Bash, AskUserQuestion
argument-hint: "[optional NNNN-slug] — omit it when this session booted itself"
---

# 9 — Stop

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Report what closing loses, record what happened in prose, then remove the session.

## Step 1 — Probe

Resolve the folder name — `NNNN-slug`:

```bash
python3 .claude/tools/bus.py whoami
```

It fails → read this session's `00-session.md`. Both fail → ask the user. Never guess it.

```bash
.claude/skills/9-stop/probe.sh --folder <NNNN-slug>
```

Read `BRANCH=`, `WORKTREE=`, `WT_DIRTY=`, `WT_UNPUSHED=`, `REPO_DIRTY=`, `OPEN_ASK=`, `UNREAD_ANSWER=`.

`BRANCH=` empty means `/1-build` never ran. Skip Step 2 entirely.

**Closing another session from this one:** output these steps as a copy-paste blurb for that session. Execute nothing.

## Step 2 — Verify — only when `BRANCH=` is set

Run the build and test commands for what this session changed. Read the actual output.

Red → report it and stop. Do not close over a red tree.

Never re-verify prior sessions' committed work. Never accept a claimed pass.

## Step 3 — Loss report — read-only

List what closing would lose. Group it:

- **Durable conclusions** — decisions or findings not in the docs. Say where each belongs.
- **Uncommitted work** — quote `WT_DIRTY`, `WT_UNPUSHED`, and `REPO_DIRTY` with the branch. State plainly: run `/8-ship` before pruning, or it is gone.
- **Doc-sync** — name `/doc-check`. Never guess which docs drifted; that skill proves it.
- **Open question** — `OPEN_ASK` or `UNREAD_ANSWER` above zero. Both files live in the folder and die with it. Name the question, and say the answer is lost unread.
- **Carried threads** — deferrals, unresolved items, follow-ups.

One line each: what it is, where it sits, what is lost if ignored. Say plainly when nothing durable exists.

Promote nothing. The user decides per item, and any keep is a separate write before the prune.

## Step 4 — Compose the archive prose

Write one block for today's day file to `<session folder>/.archive-block.md`.

**Pure prose. No paths, no filenames, no links, no PR numbers, no SHAs.** Name things in words. `close.sh` rejects a block that breaks this.

State what changed and why, in short sentences. Show the block in chat — it freezes once written.

## Step 5 — Gate the close

`AskUserQuestion` — Header `Close`; Question `Write this archive block and prune the folder? Everything above is gone after.`; Options `Do it` / `Not yet`.

`Not yet` → stop here. Nothing written, nothing deleted.

## Step 6 — Close

```bash
.claude/skills/9-stop/close.sh --folder <NNNN-slug> --archive-block <folder>/.archive-block.md
```

It archives, then removes the folder, the lock block, and the identity file. Read every `=` line back and report what it did.

Exit 8 — the archive block was rejected or the append failed. Nothing was removed. Fix the block and re-run.

## Things NOT to Do

- Never commit, PR, merge, or tear down a worktree. All of that is `/8-ship`.
- Never prune before the loss report is presented.
- Never prune while `WT_DIRTY` or `WT_UNPUSHED` is non-zero without saying so at the gate.
- Never put a path, filename, link, PR number, or SHA in the archive block.
- Never promote or doc-sync automatically.
- Never delete a session folder by hand. `close.sh` owns the order.
- Never close over a red build.

## Output

The verification result when `/1-build` ran, the loss report, the archive block as written, and every line `close.sh` printed.

## Files

- `probe.sh` — the closing state, from disk and git. Read-only.
- `close.sh` — archive, then remove the folder, the lock, the identity file.
