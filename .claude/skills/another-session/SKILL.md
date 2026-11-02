---
name: another-session
description: Hands my words, and this session's work when there is some, to one new session, which says them back before it works. "This is for another session" means this skill.
allowed-tools: Read, Glob, Grep, Write, Skill
argument-hint: "[my words for it] — omit for my last message"
---

# Another Session

## Step 1 — Take my words

An argument → it is my words.

No argument → my last message before this one.

## Step 2 — Weigh what goes with them

My words alone → Step 3.

My words hand over this session's work too, its findings or its files → Step 5.

## Step 3 — Write its message

One paragraph, as me. `.claude/rules/talking.md` rules its voice, under "Writing for another reader".

It holds my words, whole, and what you understood from me, with the context I gave.

Its facts are my words. Nothing is read for them.

It ends: "Before any work, say back what you understood, with /clarify-understood. Work once I confirm."

## Step 4 — Launch it

```
python3 .claude/tools/launch.py session --name "<one to three words>" --message "<its message>"
```

Add a flag only for what I named: `--number`, `--account`, `--model`, `--effort` or `--where`.

It prints the pane, then the number once the session holds its message. Go to Step 8.

## Step 5 — Clarify until I agree

Invoke `clarify-summary` on what goes with my words: the session's name, then what is agreed, to do, and still open.

Ask in the body what I would add. The move is a Ruling: agree, and you launch it.

My feedback → rework it, and invoke `clarify-summary` again. Only my agree goes on.

## Step 6 — Launch it, then write its folder

```
python3 .claude/tools/launch.py session --name "<one to three words>"
```

Add a flag only for what I named. Never pass `--message` here.

It prints the pane, then NN once the session holds it. Write nothing in its folder before NN prints.

Its folder is `.claude/state/sessions/NN/brief/`. `00-read-me.md` comes first. It says:

- What the folder is.
- The reading order, one line per file.
- "Nothing in this folder is a ruling unless it quotes one of mine. What I say in chat outranks it."

Then one short file per idea, numbered in reading order: `01-your-role.md`.

A file from any folder in `.claude/state/sessions/` is copied into `brief/sources/`. A vault or code file is named by its path, and never copied.

`.claude/rules/talking.md` rules the voice, under "Writing for another reader". Every fact comes from a file opened this session, or from my words.

## Step 7 — Hand it the folder

```
python3 .claude/tools/panes.py say --to NN --line "Read .claude/state/sessions/NN/brief/ whole, 00-read-me.md first. Before any work, say back what you understood, with /clarify-understood. Work once I confirm."
```

It prints the pane id. Empty means nothing was typed: the pane is gone, or Claude is gone from it. Say which, and stop.

## Step 8 — Say it, and stop

One line: "Session 15 started."

## Never

Never research the problem. The new session does.

With my words alone, never read a file they name.

Never add a finding, a fix or a plan to my words.

Never write outside the new session's `brief/`.
