---
name: blurb-gpt
description: Writes a file I paste into ChatGPT, carrying my rules in full. "Blurb GPT …" means this skill.
allowed-tools: Read, Glob, Grep
argument-hint: "[what GPT does] — and the files it needs; none named → the session picks them"
---

# Blurb GPT

One file I paste into ChatGPT. It holds the blurb alone.

## Step 1 — Take my line as the instruction

It names what GPT does, and may name the files it needs.

Trust it.

## Step 2 — Know the reader

The reader is GPT, in ChatGPT.

It holds nothing of this machine. It opens no path.

So the file carries every file the work needs, in full.

## Step 3 — Pick the files

My rules always go first. The tool adds them: every `CLAUDE.md` Claude Code loads, `.claude/rules/`, and `knowledge/MOC.md`.

Add every file the work touches: vault documents, code, session files.

Your files follow my rules, in the order you give them. Files I named lead.

Pick through the vault's MOCs and the code's tree. Read only what picking needs.

A `.env` file never goes. The tool refuses one.

## Step 4 — Write the ask as me

`.claude/rules/talking.md` rules the
voice, under "Writing for another reader". Follow it.

Ground every fact in a file opened this session, or in my words.

Say what GPT does, and what it hands back.

Name a file by its absolute path, as its header shows it. Never its bare name, never its place in the file.

## Step 5 — Write the file

My number, as `CLAUDE.md` defines it.

```
python3 .claude/tools/blurb.py NN gpt <file> <file> <<'EOF'
<the ask>
EOF
```

Each file is repo-relative. The ask alone goes on stdin.

It prints the file's path, then its code word.

## Step 6 — Name it in chat

One line: the file's path, and the code word GPT's reply takes as its Title.

## Never

Never put the blurb in chat.

Never write the blurb file with Write or Edit. The tool writes it.

Never commit or push. `/8-ship` owns that.
