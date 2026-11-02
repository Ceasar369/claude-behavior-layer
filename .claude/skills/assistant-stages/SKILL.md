---
name: assistant-stages
description: Plans the work in hand as stages A, B, C, each holding missions that run side by side.
allowed-tools: Read, Glob, Grep, Write, Skill
argument-hint: "[the work to plan] — omit for the work this session holds"
---

# Assistant Stages

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No `stages.json` there, and NN does not end in 0 → I sit off an assistant's seat. `python3 .claude/tools/launch.py seat` prints the seat, SS. Run the skill `0-session-start` with `SS <my title's words>`: my folder and my pages move to SS. Say so in one line, and go on as SS.

My title's words are my name without its number: `07-proposal-thinking` gives `proposal thinking`.

## Step 2 — Take the work

An argument → it is the work.

None → the work this session holds with me: my rulings in chat, its research.

`.claude/state/sessions/NN/stages.json` exists → this session's own research adds only missions I ruled.

Read every file the work names. Never plan from memory.

## Step 3 — Propose what stopped stages surfaced

No `stages.json` → Step 4.

`python3 .claude/tools/assistant-page.py states NN` prints each mission's state. A stage whose missions all read stopped has stopped.

No stage stopped → Step 4.

`python3 .claude/tools/clarify-page.py answers NN` says `sent` → fold it through `clarify-items`. A new round opens → stop. Every item settled → the missions I agreed are the work. Go to Step 4.

Otherwise, read what each stopped stage surfaced:

- Each of its missions' `.claude/state/sessions/NN/answers/<id>.md`.
- Each of its sessions' last turn: `python3 .claude/tools/transcript.py copy SS --into NN`, then only the copy's last session turn.
- Each of its missions' kept report, `.claude/state/sessions/NN/reports/<id>/report.md`, when one exists.

New work I have not ruled → judge it against my goal. It fits → it is the work: go to Step 4. It does not → propose it through `clarify-items`, with the `then:` line I was given. Stop.

- One item per proposed mission. It shows its name, what it builds, the parts it writes and calls, and where it came from: "session 12, wave 7, item 32".

Nothing new → say so in one line, and stop.

## Step 4 — Read the rules

Read `knowledge/0010-playbook/0011-assisting/the-stages.md` and `knowledge/0010-playbook/0011-assisting/assisting-protocols/protocol-sizing-a-stage.md`.

Read `knowledge/0010-playbook/0013-thinking/the-parts.md` and `knowledge/0010-playbook/0019-targeted/the-map/the-repository.md`, each when it exists.

## Step 5 — Cut the missions

A mission is one session's work, whole.

Name the parts each one writes, as `knowledge/0010-playbook/0013-thinking/the-parts.md` names them.

Work whose want I have not stated gets a discovery mission first, in stage A. It writes no part.

My want is stated when my words answer who, what, when, where and why. Discovery asks me each one they leave open.

I ask for discovery → it comes first, stated or not.

A mission building something I will look at, whose look I have not settled, gets a prototype mission in an earlier stage. Its part is its subject.

A mission's name is one to three words, unique in the plan. Its session takes that name.

## Step 6 — Group them into stages

Follow `knowledge/0010-playbook/0011-assisting/assisting-protocols/protocol-sizing-a-stage.md`, step by step. It applies the one test in `knowledge/0010-playbook/0011-assisting/the-stages.md`.

An open plan places each new mission as `the-stages.md` says, under "Two kinds of plan": the stage I name, or else the stage filling. A mission joining a stage takes its next number there: A2 after A1.

## Step 7 — Write the plan

Write `.claude/state/sessions/NN/stages.json` with the Write tool.

```json
{"stages": [
  {"name": "Stage A", "missions": [
    {"id": "A1", "name": "vault and docs",
     "file": ".claude/state/sessions/NN/missions/A1-vault-and-docs.md"}]}]}
```

A mission takes `id`, `name` and `file`. The tool adds the rest.

I named the plan open, when the team started or since → `"kind": "open"` before `"stages"`. Never otherwise.

`file` is `missions/<id>-<name, dashed>.md` in my folder. It need not exist yet.

The file exists → read it first. Keep every mission already queued or launched, exactly as it is.

## Step 8 — Say it

Lay the plan out in chat: one line per stage, its letter, then each mission's id and name.

The page carries the same.

## Never

Never write a wait into the plan. A mission names the step it meets another at, through `assistant-mission`.

Never give two missions one name.
