---
name: 4-prototype
description: Prototypes what I cannot yet picture, one generation of variations at a time. "Prototype …" means this skill.
allowed-tools: Skill, Read, Glob, Grep
argument-hint: "[words — what to prototype, or my feedback on it, with glance, compare or full to set its level · brainstorm · your pick · what to look at · lock in g2/v3, or g2/v3 · A: look 1 · B: open · save it for later · continue sign-in-form · remove] — omit to go on with this session's prototype"
---

# 4 — Prototype

A router. It prototypes what I am unsure of, in generations, until I lock one in.

Only this router combines the children. A child never calls another.

## Step 1 — Know my number

My number, as `CLAUDE.md` defines it. My page is the prototypes app, on the port `python3 .claude/tools/prototype.py status NN` prints. 1100 frames it in my hub while I hold a subject not locked in. Every other one shows on the app's library, at `/`.

No number → run the skill `0-session-start` first.

## Step 2 — Read the prototyping folder

Read `knowledge/0010-playbook/0014-prototyping/prototyping-MOC.md` and `knowledge/0010-playbook/0014-prototyping/the-prototyping-axioms.md`.

The axioms hold for every run.

Read `knowledge/0010-playbook/0014-prototyping/prototyping-protocols/prototyping-protocols-MOC.md`.

The level my words name picks its protocol: Glance, Compare or Full. None named → Glance. Read that protocol, and follow it.

## Step 3 — Route

`python3 .claude/tools/prototype.py status NN` prints this session's subject.

- It prints that this project has no prototypes app → say that line, and stop.
- My words keep this prototype for later → Step 10.
- My words continue a prototype by its name, or name none → Step 11.
- No subject, and my words name something to prototype → Step 4.
- My words name a variation, like `g2/v3` or `g2/v3 · A: look 1 · B: open`, with or without a note after a dash → Step 5.
- My words delete this prototype → Step 6.
- My words ask for your pick → Step 7.
- My words ask what to look at → Step 8.
- My words ask to brainstorm, or a brainstorm runs in this chat → Step 9.
- My words ask you to understand something → say it back, through `clarify-understood`. Build nothing.
- Otherwise my words are feedback on this session's subject → Step 4.

## Step 4 — Make the next generation

Invoke `prototype-variations` with my words, the level, and `then: /4-prototype`.

It hands on a round: the subject, its unknowns, and each variation's direction and source. It stopped for me instead → stop.

Invoke `prototype-generation` with that round and its level.

## Step 5 — Lock one in, or ask again

My words name a variation. A variation with groups of looks comes with each group's pick: `g2/v3 · A: look 1 · B: look 4`. A group with no pick reads `B: open`.

- A note after the dash asks for a change → Step 4, with the variation as its source and the note as my words.
- The variation holds no groups, or every group names its look → invoke `prototype-lock-in` with the variation and the looks I named. A note that asks for nothing rides on the lock-in. Then invoke `prototype-rules`.
- A group reads `open` → Step 4, with the variation as its source. The looks I picked stay. Each open group's looks are asked again.

## Step 6 — Delete the prototype

Invoke `prototype-remove` with this session's subject.

## Step 7 — Give your pick

Invoke `prototype-pick`, with the generation I name, or none.

## Step 8 — Give the checklist

Invoke `prototype-checklist`, with the generation I name, or none.

## Step 9 — Brainstorm

Invoke `prototype-brainstorm` with my words.

It hands on my picks → Step 4, with them as my words, at the level they name. It stopped for me instead → stop.

## Step 10 — Save it for later

Invoke `prototype-save`. Say what it printed.

## Step 11 — Continue one

Invoke `prototype-continue` with the prototype's exact kebab name, or none when my words name none. Say what it printed.

It took the prototype → go on with my words' rest, if any, as feedback: Step 4.

## Never

Never keep a variation on your own.

Never offer your pick unasked.

Never give the checklist unasked.

Never brainstorm unasked.

Never write a prototype outside `code/prototypes/`.
