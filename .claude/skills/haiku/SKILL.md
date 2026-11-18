---
name: haiku
description: Puts what I ask to Haiku agents at once, then answers from the findings it verified.
allowed-tools: Agent, Read, Grep, Glob, Bash
argument-hint: "[what I ask, or a file of items] — omit for the question in my message before this command"
---

# Haiku

## Step 1 — Find the questions

My words → each question in them.

A file I name → each item in it, read whole.

Bare → the question in my message before this command.

No question there → ask for it, in one line. Then stop.

## Step 2 — Send three per question

Each question takes three agents. Two questions go at once. `.claude/rules/thinking.md` caps how many run.

Send each pair's six agents in one message, through the Agent tool, each with `subagent_type` haiku-lens and `run_in_background` false. `.claude/agents/haiku-lens.md` fixes their model, effort, tools and report.

Each question takes one agent per lens: proof, challenge, missing.

Each brief holds the question word for word, what a fresh reader needs to find its places, and its lens.

The missing lens's brief also holds a list to check, one entry at a time: the rulings or changes the question answers, and the sections of each source it rests on.

Never put my leaning or this conversation in a brief.

## Step 3 — Verify

Open the source of every claim the answer rests on. Read the whole section, never the quote alone.

A claim most agents make is read at its source too.

A commit an agent names → read it with `git show`.

Agents disagree → the source settles it.

A claim its source does not hold → dropped.

A claim left unread → unproven, in that word.

## Step 4 — Answer

Answer each pair's questions once all six agents return. Then send the next pair.

One answer per question, in the turn's shape `CLAUDE.md` sets.

Each claim names its source.

Never a list of what each agent said.

## Step 5 — A session's wave: place each opinion

The questions are items of a session's wave waiting on me → place each answer on its page yourself, as its proposal, once the item's pair is answered:

```
python3 .claude/tools/clarify-page.py propose NN --item N --agree --by MM
python3 .claude/tools/clarify-page.py propose NN --item N --feedback --by MM --why "<one line>" <<'EOF'
<the feedback, in my words>
EOF
```

NN is that session's number, MM your own. Never ask me first.

Never send the wave, and never mark an answer of mine: I take a proposal, then Send.

## Never

Never edit a file. A proposal on a wave's page, by Step 5, is no edit.

Never send an agent but haiku-lens.
