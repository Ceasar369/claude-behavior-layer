---
name: jury-run
description: Runs a drafted jury to its conclusion and counts.
allowed-tools: Read, Bash
argument-hint: "[a run, like 2026-10-21-1612] — omit for this session's newest plan not yet run"
---

# Jury Run

## Step 1 — Only on my word

Run only when I typed it, or the jury tab's Launch typed it.

## Step 2 — Read the jury axioms

Read `knowledge/0010-playbook/0019-targeted/jury/the-jury-axioms.md`. They hold for this whole turn.

## Step 3 — Start it

My number, NN, as `CLAUDE.md` defines it.

Run `python3 .claude/tools/jury.py run NN RUN` with the Bash tool, `run_in_background` true. Bare → leave RUN out.

Say it runs, then end the turn. Running names it.

## Step 4 — Say the conclusion

When it ends, read its output whole.

The body is its output, word for word: the conclusion, its count line, each claim that does not hold, and the jury tab's address.

It failed → its last lines, and the results file.

## Never

Never change a count or an outcome.

Never add a fact the output lacks.
