---
name: another-team
description: Starts one new team on my subject, led by its own assistant, with this session's work when there is some. "Start a team" or "kick off a team" means this skill.
allowed-tools: Read, Glob, Grep, Write
argument-hint: "[my words: the subject, or several subjects] — omit for my last message"
---

# Another Team

A team is one assistant on a free ten, and the sessions it launches there.

## Step 1 — Take my words

An argument → it is my words.

No argument → my last message before this one.

Two or more subjects → one team each.

## Step 2 — Find the seat

```
python3 .claude/tools/launch.py seat
```

It prints SS, the lowest free ten's seat.

It says "No ten is free for an assistant." → say so in one line. Launch nothing. Stop.

Two or more teams → each takes a free ten, as `launch.py seat` judges one. Too few free → say how many fit, launch nothing, and stop.

## Step 3 — Name the subject

The subject is my words, never an agenda item.

Find the code or vault path my words point to. Name it. Read nothing else for it.

An agenda item I named → its path goes in the message.

## Step 4 — Find the neighbours

Read each `.claude/state/sessions/*0/stages.json`, and the `record.json` beside it.

Its title and its missions' names give that team's subject.

`knowledge/0010-playbook/0013-thinking/the-parts.md`, when it exists, names the parts.

A team whose subject touches a part this subject touches is a neighbour.

## Step 5 — Weigh what goes with my words

This session holds my rulings, research or a thinking on the subject → a brief goes with it. Go to Step 7.

My words alone → Step 6.

## Step 6 — Write the message, and launch

One paragraph, as me. `.claude/rules/talking.md` rules its voice, under "Writing for another reader".

Its parts, in order, each only when it applies:

1. An agenda item I named: "Read the README in `<the item's folder>`, then `<the item's path>`: it only reminds me of this work, so look at the subject with me, never at the item."
2. The subject, in my words, with its path.
3. Each neighbour: "Session `<its seat>` leads a team on `<its subject>`, in `<the part>`, so read what your sessions would write before they write a file both could touch."
4. "Be my assistant for it, with the skill 1-assistant: you lead a team of sessions that covers everything it needs, from clarification and prototyping to implementation and testing."
5. A discovery I asked for: "Your first stage is discovery: one session finds out what I want and clarifies it with me."
6. My words name the team's plan open: "Your plan is open, as `knowledge/0010-playbook/0011-assisting/the-stages.md` says, under "Two kinds of plan". Start by planning the first stage with me." Otherwise: "Start by planning the first stage with me. Once it ends, we refine the plan together."

One team:

```
python3 .claude/tools/launch.py session --number SS --name "<subject> team" --message "<the message>"
```

Its name is one to three words, ending in "team".

Two or more teams → rows in `.claude/state/sessions/NN/launch.json`, as the skill `launch` Step 4 writes them. Each row takes `n`, its seat. A row carries no brief.

Go to Step 9.

## Step 7 — Launch it, then write its brief

```
python3 .claude/tools/launch.py session --number SS --name "<subject> team"
```

Never pass `--message` here.

It prints the pane, then SS once the session holds it. Write nothing in its folder before SS prints.

Write its brief as `another-session` writes one, in `.claude/state/sessions/SS/brief/`, with `01-the-subject.md` as its first idea.

Every fact comes from a file opened this session, or from my words.

## Step 8 — Hand it the brief

The message is Step 6's parts, opening with: "Read .claude/state/sessions/SS/brief/ whole, 00-read-me.md first." It ends: "Before planning, say back what you understood, with /clarify-understood. Plan once I confirm."

```
python3 .claude/tools/panes.py say --to SS --line "<the message>"
```

It prints the pane id. Empty means nothing was typed: the pane is gone, or Claude is gone from it. Say which, and stop.

## Step 9 — Say it, and stop

One team: one line. "Team SS started, below me."

Rows: list them, one line each, its name and seat. Your move is "Action: press Launch on 1100."

## Never

Never type into a team after its first message.

Never research the subject. The team does.

Never decide discovery for it. Name one only when I asked for it.

Never add a finding, a fix or a plan to my words.
