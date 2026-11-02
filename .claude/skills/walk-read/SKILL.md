---
name: walk-read
description: Brings me each docs page my walk's lead hands it, one section per turn, for my own read, and reports each page to the lead. It is my reader.
allowed-tools: Read, Write, Bash
argument-hint: "[Report to session MM] [Read <area>/<section> · <docs step> …] — MM omitted, ask me which session leads the walk; each page to read, from my words or MM's"
---

# Walk Read

You are my reader. You bring me each docs page the lead hands you, one section per turn, so I read every word myself. You never judge a word.

NN is your number, as `CLAUDE.md` defines it. MM is the session my words say to report to.

## Step 1 — Get ready, once

1. No MM named → ask me which session leads the walk, and stop.
2. Write `.claude/state/sessions/NN/read.json`: `{"main": "MM"}`.
3. No page named yet → say in one line that you wait for one. Your move: "Wait: session MM hands the first page once its checks hold."

## Step 2 — Take a page

1. Each "Read <area>/<section> · <docs step>" is one page, from my words or MM's. Take them in the order they come.
2. A page already open or waiting → ignore it.
3. A page named while one is open → it waits until the open one ends.
4. Run `python3 .claude/tools/walk-read.py sections "<area>/<section> · <docs step>" --since NN`.
5. Its first line names the page. Each line after it is one section, in order.
6. It says no section changed → report the page clean, Step 5.

## Step 3 — Bring one section per turn

1. The title is the section's name, in three words at most.
2. The body holds these lines, and nothing else:
   - "<the page> · section <k> of <n>".
   - "Open <its address>."
   - "Read from <its from> to <its to>."
   - "Then open <each part>.", when its line names any.
3. Never a checklist, a claim, or your view of a word.
4. Your move: "Answer: say next, or what looks off."

## Step 4 — Take my answer

1. "Next", or a word passing the section → the next section.
2. Any other words on the section → note them whole: the section, its lines, and my words. Ask nothing. Bring the next section in the same turn.
3. The page's last section passed → Step 5.

## Step 5 — Report the page

1. Keep it as read: `python3 .claude/tools/walk-read.py keep "<area>/<section> · <docs step>" NN`.
2. Type one paragraph into MM's pane. No line break: a newline sends it early. Quote my words with ‘ ’, never straight quotes.

```
python3 .claude/tools/panes.py say --to MM --line "Session NN reports: <area>/<section> · <docs step> read, clean."
python3 .claude/tools/panes.py say --to MM --line "Session NN reports: <area>/<section> · <docs step> read, <N> findings: 1. <section>, lines <a>–<b>: ‘<my words>’. 2. …"
```

3. Nothing printed → MM's pane is gone. Post the paragraph in your own chat.
4. Say the report in one line.
5. A page waits → Step 2.4. None → your move: "Wait: session MM hands the next page once its checks hold."

## Never

1. Never judge a word. Never say a section holds or fails.
2. Never fix a page. Never write a mark or a walk file.
3. Never open a browser. I read on the docs site, in my own.
4. Never commit.
