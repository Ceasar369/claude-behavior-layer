---
name: 6-agenda
description: Calls the one agenda skill my words need, once my agenda's rules are read. "My agenda …" means this skill.
allowed-tools: Read, Skill
argument-hint: "[what I dictate, an item, a topic or items to triage] — omit to see the order"
---

# 6 — Agenda

A router. Only it combines its children. A child never calls another.

## Step 1 — Only when I name it

Run only when I name my agenda.

Asked what to work on next, I did not name it. Open nothing in `.claude/state/agenda/`, and stop here.

## Step 2 — Read the agenda folder

Read `knowledge/0010-playbook/0016-agenda/agenda-MOC.md` and `knowledge/0010-playbook/0016-agenda/the-agenda-axioms.md`.

The axioms hold for this whole turn.

Read `knowledge/0010-playbook/0016-agenda/agenda-protocols/agenda-protocols-MOC.md`.

A line matching my words → read that protocol, and follow it.

## Step 3 — Call one child

I take a topic, triage one, or name items to triage → `agenda-triage`.

Otherwise → `agenda-write`: what I dictate, the order, or where an item stands.

Invoke it with the `Skill` tool, passing my words.

## Never

Never write my agenda here.
