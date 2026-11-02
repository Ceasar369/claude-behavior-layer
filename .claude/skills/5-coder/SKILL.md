---
name: 5-coder
description: Points this session to what it must know for the code in hand, general first, then its layer's, and codes by the protocol that matches. "Code …" means this skill.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "[the code to write] — omit for the code in hand"
---

# 5 — Coder

A router. It reads what the code in hand needs, then codes by the protocol that matches.

## Step 1 — Read the general knowledge

Read `knowledge/0010-playbook/0015-coding/the-coding-axioms.md`, and `knowledge/0010-playbook/0015-coding/the-stack/the-stack-MOC.md` when it exists.

The axioms hold for all the code in hand. Of the stack's documents, read each one the code touches.

## Step 2 — Read its layer's knowledge

`knowledge/0010-playbook/0019-targeted/the-map/the-repository.md`, when it exists, maps each code folder to its layer's vault folder.

Read that layer's MOC, then each document the code touches. A backend reads its backend's, a frontend its screens'.

Code under `.claude/` reads `knowledge/0010-playbook/0013-thinking/thinking-protocols/behaviour-protocols/the-behaviour-axioms.md`.

Code outside every layer reads no layer folder.

The code changes a page I see, 1100's included, whose look I have not settled, and was asked in words → `4-prototype` first, by What A Person Sees. Code its winner, and mark it built. A look borrowed from another page is settled.

Code building any prototype's winner marks it built, whoever made it: `python3 .claude/tools/prototype.py build NN <subject>`, NN my number. Once its real version is live, take it down through `prototype-remove`, with its name. The stop takes down any left.

## Step 3 — Match a protocol

An edit under `.claude/rules/` or `CLAUDE.md` matches one protocol: read `knowledge/0010-playbook/0013-thinking/thinking-protocols/behaviour-protocols/layer-protocols/protocol-playbook-rule.md`, answer its questions, then edit. Go to Step 4.

Read `knowledge/0010-playbook/0015-coding/coding-protocols/coding-protocols-MOC.md`.

Each line opens with the kind of code it serves.

A folder's line matches → read that folder's MOC. Go down one MOC per tier.

A protocol's line matches → read that protocol, and follow it.

Nothing matches → say so in one line. Then `.claude/rules/thinking.md`'s questions, under "The least that works", and code with no protocol.

## Step 4 — Check it

Once the code is done, run `coder-check`.

The code changed anything 1100 draws → call `00-sessions-dashboard` with `restart`. Until then, 1100 draws the code it started with. A refused restart is a failing step.

## Never

Never read a MOC or a protocol off the matching branch.
