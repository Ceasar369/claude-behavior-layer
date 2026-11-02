---
name: blurb-session
description: Writes a file of lines to paste into another of my sessions.
allowed-tools: Read, Glob, Grep
argument-hint: "[what the blurb says] — and which session reads it"
---

# Blurb Session

A few lines I paste into another of my sessions. One file holds them alone.

## Step 1 — Take my line as the instruction

It names what the blurb says, and which session reads it.

Trust it.

## Step 2 — Ground it

Read every file I name before writing about it.

Never state a fact from memory.

Nothing named → write from this session.

## Step 3 — Know the reader

The reader is a session of mine, in another iTerm pane.

It works this repo. It reads the same vault.

Carry what it needs. Carry nothing it already holds.

## Step 4 — Write it as me

`.claude/rules/talking.md` rules the
voice, under "Writing for another reader". Follow it.

## Step 5 — Keep it to one thing

A blurb says one thing. Two things is two blurbs.

Longer than a few lines is a prompt, not a blurb.

## Step 6 — Write the file

My number, as `CLAUDE.md` defines it.

```
python3 .claude/tools/blurb.py NN session <<'EOF'
<the blurb>
EOF
```

The blurb alone goes on stdin. No intro, no markers.

It prints the file's path.

## Step 7 — Name it in chat

One line: the file's path.

## Never

Never put the blurb in chat.

Never write the blurb file with Write or Edit. The tool writes it.

Never write a numbered, phased prompt.

Never commit or push. `/8-ship` owns that.
