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

Read `BRANCH=`, `WORKTREE=`, `WT_DIRTY=`, `WT_UNPUSHED=`, `REPO_DIRTY=`, `DOCS_DIRTY=`, `OPEN_ASK=`, `UNREAD_ANSWER=`.

`BRANCH=` empty means `/1-build` never ran. Skip Step 2 entirely.

- Exit 2 — bad arguments. Fix and re-run.
- Exit 3 — no such folder, and no lock names it. Report and stop.

**A stale lock — the folder is gone but its block remains.** Probe exits 3.
Skip to Step 6 and run `close.sh --folder <NNNN-slug>` with no archive block.
It clears the block alone and prints `FOLDER_REMOVED=no — already gone`.
Never hand-edit the lock file.

**Closing another session from this one:** output these steps as a copy-paste blurb for that session. Execute nothing.

## Step 2 — Verify — only when `BRANCH=` is set

Run the build and test commands for what this session changed. Read the actual output.

Red → report it and stop. Do not close over a red tree.

Never re-verify prior sessions' committed work. Never accept a claimed pass.

## Step 3 — Loss report — read-only

Report ONLY what closing actually loses. An empty section is omitted, header included. Silence is the default.

- **Durable conclusions** — a decision or finding not yet in a doc. One line: the fact, its destination.
- **Uncommitted work** — non-zero counters only, one line, with the branch. This session's own folder and lock never count. Pre-existing dirt from other work: one word, no story.
- **Doc drift** — only when certain a named doc needs a named change. The doc, the gap, one line each. Not certain → say nothing. Suspicion is `/doc-check`'s job, the user's to invoke — never parked in a close.
- **Open question** — only when `OPEN_ASK` or `UNREAD_ANSWER` is above zero. Name the question; its answer dies unread.
- **Carried threads** — deferrals and follow-ups, one line each.

Every section empty → exactly one line: "Nothing lost by closing." The gate then skips (Step 5).

Promote nothing. The user decides per item, and any keep is a separate write before the prune.

## Step 4 — Compose the archive prose

Write one block for today's day file to `<session folder>/.archive-block.md`.

**Pure prose. No paths, no filenames, no links, no PR numbers, no SHAs.** Name things in words. `close.sh` rejects a block that breaks this.

State what changed and why, in short sentences. Show the block in chat — it freezes once written.

## Step 5 — Gate the close

**Skip this gate only when the loss report is empty.** Empty means every one of these holds:

- `BRANCH=` is empty — no build ran.
- `WT_DIRTY`, `WT_UNPUSHED`, `OPEN_ASK`, `UNREAD_ANSWER` are all zero.
- Zero durable conclusions and zero carried threads in the report.
- The only uncommitted repo changes are this session's own folder and the lock. They die at close by design. Anything else counts as loss.

All hold → say "loss report empty — closing without the gate" and go to Step 6. Any one fails → gate:

`AskUserQuestion` — Header `Close`; Question `Write this archive block and prune the folder? Everything above is gone after.`; Options `Do it` / `Not yet`.

`Not yet` → stop here. Nothing written, nothing deleted.

## Step 6 — Close

```bash
.claude/skills/9-stop/close.sh --folder <NNNN-slug> --archive-block <folder>/.archive-block.md [--prompt <N-slug.md>]
```

This session ran a numbered prompt → pass its bare filename as `--prompt`. The prompt dies with the session. Prompts come and go; none is kept. Unsure which file → omit the flag; never guess-delete.

It archives, then removes the folder, the lock block, the identity file, and the named prompt. Read every `=` line back and report what it did.

Exit 8 — the archive block was rejected or the append failed. Nothing was removed. Fix the block and re-run.

## Things NOT to Do

- Never commit, PR, merge, or tear down a worktree. All of that is `/8-ship`.
- Never prune before the loss report is presented.
- Never prune while `WT_DIRTY` or `WT_UNPUSHED` is non-zero without saying so at the gate.
- Never put a path, filename, link, PR number, or SHA in the archive block.
- Never promote or doc-sync automatically.
- Never delete a session folder by hand. `close.sh` owns the order.
- Never close over a red build.
- Never skip the gate while any loss-report section is non-empty.

## Output

The verification result when `/1-build` ran, the loss report, the archive block as written, and every line `close.sh` printed.

## Files

- `probe.sh` — the closing state, from disk and git. Read-only.
- `close.sh` — archive, then remove the folder, the lock, the identity file.
