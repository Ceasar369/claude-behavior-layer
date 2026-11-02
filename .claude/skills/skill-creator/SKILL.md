---
name: skill-creator
description: Writes a new skill to this layer's standard.
allowed-tools: Read, Write, Edit, Glob, Grep
argument-hint: "[the behaviour to repeat]"
---

# Skill Creator

A skill is a behaviour I want repeated. This writes one.

## Step 1 — Read the standard

Read
`knowledge/0010-playbook/0013-thinking/thinking-protocols/behaviour-protocols/the-behaviour-axioms.md`.

It is the floor. Follow it, never restate it.

## Step 2 — Say the behaviour in one sentence

Write what happens, when I run it, in one sentence.

Unclear → ask one question, in prose.

Two sentences → it is two skills. Say so and stop.

## Step 3 — Choose the kind

**Deterministic** — the same input always gives the same result, and no
judgment is needed. It is a hook. It costs nothing.

**Judgment** — it reads, decides, or writes prose. It is a model skill.
Its `SKILL.md` body carries the instructions.

Say which, and why in one line, before writing anything.

## Step 4 — Choose the name

The name says what the skill does, in words I already say.

A leading digit is for a skill I type all day. A rare one takes none.

Ask me for the digit. Never assign one.

Run `ls .claude/skills/` first. A name already taken is refused.

Every name Claude Code owns is a word. A leading digit clears them all.

A plain name is cleared in a fresh pane, by typing `/` and reading the
menu. A built-in answering to it refuses the name.

## Step 5 — Write the files

A hook skill takes three:

```
.claude/hooks/<name>.py        all of the work
.claude/skills/<name>/SKILL.md so the command resolves
.claude/settings.json          two entries: UserPromptSubmit, and PreToolUse on Skill
```

A model skill takes one:

```
.claude/skills/<name>/SKILL.md
```

Work that outlives the prompt goes in `.claude/tools/<name>.py`.

State goes in `.claude/state/<name>/`.

The description is one line of menu text.

It says what the skill does. A quoted phrase joins once I use one. Never a list.

A second phrase enters only after a real misfire.

Never a word another description already claims.

One word of mine covering two acts → I pick a new word for one.

`argument-hint` names every word the skill takes, and what leaving it out does.

A hook calls `hook.words(TRIGGER)` first, and `hook.done()` last.
`.claude/lib/hook.py` rules both.

## Step 6 — Write the body

Imperative. Numbered steps. One instruction a line.

State the rule. Never the reason, the history, or the source.

Every path is repo-relative and whole.

A rule never carries a real value: a default, a place, a name a tool prints. It names the file holding the value. An example may carry one.

A shell comment may hold one.

## Step 7 — Prove it

Open a fresh pane.

Run it. Paste the output back to me, verbatim.

Untested → say "unproven", in that word.

## Step 8 — Report

Name every file written. Name what it costs per run.

Then stop.
