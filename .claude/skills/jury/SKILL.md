---
name: jury
description: Sends a turn, a file or my question to a jury of agents, each answer quoted from its source.
allowed-tools: Read, Bash
argument-hint: "[a session number, a path, a link, or my own words] — omit for this session's last turn"
---

# Jury

Drafts one jury plan into this session's folder. The docstring of `.claude/tools/jury.py` rules the plan, and every field in it.

## Step 1 — Only on my word

Run only when I typed it, or asked for a jury in words.

## Step 2 — Read the jury folder

Read `knowledge/0010-playbook/0019-targeted/jury/jury-MOC.md` and `knowledge/0010-playbook/0019-targeted/jury/the-jury-axioms.md`.

The axioms hold for this whole turn.

## Step 3 — Find the words

My number, NN, as `CLAUDE.md` defines it.

Bare → this session's last turn before this command.

A session number → run `python3 .claude/tools/jury.py words NN`. Its words name a report file → that file, read whole. Else its words.

A path → that file, read whole.

A link → that page, fetched whole.

Any other words → my own words, or my question.

## Step 4 — Pick the shape

Read `knowledge/0010-playbook/0019-targeted/jury/jury-protocols/jury-protocols-MOC.md`.

Pick the one shape the words ask for. Read its protocol, and follow it.

Words stating facts take one pick, each fact a claim.

## Step 5 — Write the typed question

The context: what a juror needs to read the words, in a few lines.

Never this conversation. Never my leaning.

The question: one question, asked neutrally.

## Step 6 — Draft it

Pipe one JSON object into `python3 .claude/tools/jury.py draft NN`: from, context, question, shape and claims, as its docstring names them.

`from` holds a label, like "Session 21's last turn · 14:23", and the file or link, else empty.

The tool fills the jury sessions, a case's lenses, and each claim's number. It prints the plan's path.

## Step 7 — Say it

Say the question, its shape, and each claim with its source.

Name the plan's path.

The move is an Action: press Launch in this session's jury tab, once the plan reads right.

## Never

Never run the jury. Launch in the jury tab runs it.
