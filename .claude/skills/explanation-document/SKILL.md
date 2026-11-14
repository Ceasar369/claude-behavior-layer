---
name: explanation-document
description: Writes one document that shows me a subject whole, in this session's Explanation tab on 1100.
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
argument-hint: "[the subject, or my feedback on this session's document] — omit for this session's own work, whole"
---

# Explanation Document

One document per run. Its file is one entry in this session's Explanation tab.

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No `record.json` there → run the skill `0-session-start` first, then go on.

## Step 2 — Take the subject

An argument naming a subject → that subject.

No argument → this session's own work, whole: what it is, what was ruled, what is built, what is open.

My words are feedback on a document in `.claude/state/sessions/NN/explanations/` → edit that file, then Step 9.

My words name one part to write → write that part alone, then stop for my review. Each later part is written the same way, into the same file.

## Step 3 — Read before writing

Run `python3 .claude/tools/transcript.py copy NN --into NN`. Read `.claude/state/sessions/NN/transcript-NN.md` whole.

Read every file the subject touches: missions, waves, briefs, reports, code.

A read across many files goes to `Explore` helpers, six at most. Each returns its facts with the file and line each rests on.

Never state a fact from memory. A claim no file proves is written unproven.

## Step 4 — Say back what it makes clear

Read `knowledge/0010-playbook/0012-clarifying/clarifying-protocols/protocol-what-a-document-makes-clear.md`. Follow it.

Write its list as the document's first version: `.claude/state/sessions/NN/explanations/<name>.md`, its name two or three words in kebab case, `checkout-page.md`. It holds its `# ` title, the line `For you. Waiting on your yes before it is written.`, then `## What it makes clear` and the list.

Show the same list in chat. Its move is one Ruling: write the document from this list. The turn ends there.

My correction → redraw the file and the list in chat. My yes → Step 5.

## Step 5 — Find the story

Read `knowledge/0010-playbook/0012-clarifying/clarifying-protocols/protocol-an-explanation-document.md`. Answer its three questions: who reads it, what kind of subject, each part's state.

Say the subject's answer in three sentences, to yourself. It becomes the title and the opening.

The agreed list sets the parts I need to hold the subject whole. Each part with a picture is one section, its heading the part's takeaway, as a sentence.

Order the sections so each zooms into the one before.

Several people pass the same steps under different rules → one subsection per person, not per step. The overview shows them as lanes, side by side.

## Step 6 — Write it

Write the document over its first version.

Its format is the docstring of `.claude/tools/explanation-page.py`. Follow it exactly.

The parts, in order:

1. `# ` the title: the subject's takeaway, one sentence.
2. One line: who it is for, and what it comes from.
3. `## Summary`: three sentences, then the one chart that frames the subject.
4. The sections from Step 5.
5. One section for the ending the subject's kind sets. Two things or fewer waiting on me: each is an Open note saying who holds it. More than two: one table, what waits and who holds it, with no Open note repeating a row.
6. `## Sources`: every file read, each its repo-relative path as code.

The rules of `protocol-an-explanation-document.md` hold for every part.

## Step 7 — The words

Every rule of `.claude/rules/talking.md` under "Clarity" holds.

Each sentence holds one idea, in fifteen words or fewer.

Plain words. A name I was never given is defined where it first appears, as `[^term]`: what it is, what it is not, one real case.

Every example carries real values: names, amounts, files, numbers. It sits inside `{{…}}` in its line, or in an Example note. Both wear the Example colour.

A choice not yet made takes a general name, like "the dual process". One Open line names its candidates.

A ruling is never inferred. A Ruled note quotes my words, then where I said them.

What a session assumed is an Assumed note. What waits on me is an Open note, or a row of the ending's table. A walked case is an Example note.

A note serving a paragraph follows it. Notes that stand alone sit together.

No history of how the work came to be. A problem's own steps are its subject.

## Step 8 — The charts

One claim per picture, a chart or a table. Its title states it: `Figure: …`, the line under a chart's fence or a table's last row. The page centers it under the picture. The check fails a picture with none.

Pick by question. What happens next, or which path? `flowchart`. Who asks whom, in what order? `sequenceDiagram`. What states can it be in? `stateDiagram-v2`.

A box's colour is its kind of question or outcome: `amount{"Over $2,000?"}:::blue`. The colours are `KINDS` in `.claude/tools/explanation-page.py`. A section's overview names each colour once, as a line `%% blue: Amount check`; the page draws its legend. A colour keeps its meaning across the whole document.

Write a chart in the direction it opens: `flowchart TD` or `flowchart LR`. The page keeps it.

A chart past eight boxes is an overview, a section's first subsection. One subsection per main branch follows it. Each branch's chart is cut from the overview, with the same boxes and words.

A box holds one question or one outcome. Never a title plus its restatement, never a rule's name.

A fallback is its own branch: a question, `"Passes?"`, then `-- "no" -->` to the fallback. Several options are one box each. Options that run at the same time say so on their arrows.

A doubt never sits in a box. It is an Open line under the chart. So is a step that can fail when the source names no fallback. A fallback the source never names is never drawn.

No arrow crosses another, or runs through a box. The check names each one. Fix it by moving boxes and reordering lines, never by copying a box. A chart still crossing may add the line `%% elk` under its first line. Three tries in all, then report each crossing left.

Every label is quoted: `bank["Connect your bank"]`. Every branch's arrow carries its condition: `-- "no" -->`.

An id is one short lowercase word. Never `end`. Never one starting with `o` or `x`.

Spaces round every arrow.

A sequence diagram names each party `participant A as App's server`. A message holds no semicolon.

## Step 9 — Check it

Run `python3 .claude/tools/explanation-page.py check <file>`.

Fix every line it prints. Run it again, until it prints only its count.

Three runs still failing → stop, and say each line it printed.

## Step 10 — Read it cold

Launch one `general-purpose` agent, with no context but this brief: read the file whole, then list every word a non-technical reader would stop at, every claim with no source, and every sentence over fifteen words.

Fix each one it lists that holds. Run Step 9 again.

## Step 11 — Report

Say the document's title, and that it shows in this session's Explanation tab on 1100.

## Never

Never write outside `.claude/state/sessions/NN/explanations/`.

Never a decision in the document. A decision is mine, through `clarify-items`.

Never a menu in place of a position.
