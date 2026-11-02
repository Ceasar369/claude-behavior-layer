---
name: prototype-rules
description: Proposes what my rounds on this prototype teach every screen like it, and writes what I agree into its subject's own rules: The Screen, or the page rules.
allowed-tools: Skill, Read, Glob, Grep, Edit, Write
argument-hint: "omit — after a lock-in, or to fold my answers after Send"
---

# Prototype Rules

## Step 1 — Know my subject

My number, as `CLAUDE.md` defines it.

`python3 .claude/tools/prototype.py status NN` prints my subject.

## Step 2 — Know which round this is

Run `python3 .claude/tools/clarify-page.py answers NN`. It says `sent` → invoke `clarify-items` to fold it, then go to step 6.

Otherwise → step 3.

## Step 3 — Read the rounds

Run `python3 .claude/tools/transcript.py copy NN --into NN`. Read `.claude/state/sessions/NN/transcript-NN.md` whole.

My words about this subject are the rounds.

Read the winner, the one `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx` left.

Read its subject's own rules. A product screen: The Screen, every document in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`. A page 1100 draws: the page rules, atop `.claude/lib/page.py`.

## Step 4 — Find the rules

A rule is one thing my words ruled about how any screen under the same rules looks, beyond this subject.

The winner obeys it. A rule the winner breaks is no rule.

A page or screen live today that breaks it → reword the rule until it holds there too. Never write the exception.

What its rules already hold is no new rule.

Each rule is one fact, in its rules' voice. A product screen's names its kind: a document in The Screen, or a new one. A page's takes the next number.

A rule clashing with one already there → one item naming both.

No rule found → say so in one line, and stop.

## Step 5 — Propose them

Invoke `clarify-items`, with `then: /prototype-rules`.

One item per rule: "Does this rule join The Screen, under <kind>?", or "Does this rule join the page rules, as rule <N>?"

Its `from` quotes my words, with their turn in the transcript copy.

## Step 6 — Write what I agree

Read `knowledge/standard.md`.

Each agreed rule goes into its kind's document, in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`, with the Edit tool.

A new kind takes its own document there, with the Write tool, and one line in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/the-screen-MOC.md`.

A page's agreed rule joins the page rules, atop `.claude/lib/page.py`, under the next number, with the Edit tool. The line above the list keeps its count true.

Say each rule written, one line each.

## Never

Never write a rule I did not agree.

Never edit the vault outside `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`.

Never edit `.claude/lib/page.py` outside the page rules.

A rule names no subject, no turn and no session.
