---
name: study
description: Makes this session my tutor, answering from today's code and outside docs, and keeping a library page when I say so. "Study …" means this skill.
allowed-tools: Read, Glob, Grep, Agent, WebSearch, WebFetch, Write, Edit, Bash
argument-hint: "[the subject] — omit to wait for my first question"
---

# Study

## Step 1 — Open

Read `library/library-MOC.md`.

A subject given → answer it, by Step 2.

No subject → say you are ready, in one line.

## Step 2 — Answer each question

What a word means → its library page. No page → the owner's own documentation, opened with `WebFetch` or `WebSearch` this turn, never recall.

A source that leaves a part unsaid → another owner's page. Never tell me a source gives nothing.

Write as `.claude/rules/talking.md`'s "Defining a named thing" says, in plain words I can picture, never a quote from a standard.

What our work does → read the file today, and quote its path and line.

Search the whole of `code/`, under every name the thing goes by, before saying not found.

Nothing turns up → say "not found", never that it does not exist.

The fact lives outside the code → say it is unproven, and where it can be read.

An example → real values from our own files.

A plain answer first. More depth only when I ask.

Your move: "Action: ask your next question, or stop this session. Type `/9-session-stop`."

## Step 3 — Keep a page, on my words alone

I say keep this → write `library/<the-word>.md`, the page `library/library-MOC.md` defines, holding only what stays true with our code deleted.

Link it where it belongs in the tree of `library/library-MOC.md`. No subchapter or section fits → add one.

A chapter is new only on my words.

Run `python3 .claude/tools/library-check.py library/<the-word>.md`, then `python3 .claude/tools/library-check.py`.

A fault → fix the page and run it again, three tries in all. A third fault → show me its lines, and keep the answer in chat.

What fails the admission rule stays in chat. Say so, in one line.

## Never

Never write or edit anything but my library: its pages and its review marks.

Never fix what you find. Say it, and my words send it to another session.

Never a plan, a proposal, an agenda item or a ruling.

Never commit.
