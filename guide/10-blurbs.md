# 10 — Blurbs

A file of words for a reader outside your session: ChatGPT, a session holding your Chrome, or another session.

## What they do

A blurb is one file, written for one reader. You paste it there yourself.

- `/blurb-gpt` carries my rules in full, so ChatGPT answers as my sessions would.
- `/blurb-browser` carries my rule files in full, and the Communication section of this project's `CLAUDE.md`, for a session that holds your Chrome.
- `/blurb-session` carries your words alone. Its reader is a session of your project, which loads my rules itself.

## Your first try

In session 02, one after the other:

```
/blurb-gpt GPT reads guide/00-read-me.md and hands back every word a newcomer may not know, each with a plain replacement
```

```
/blurb-browser the session opens https://example.com in my Chrome, reads the page's heading and its one link's address, and reports both as text
```

```
/blurb-session for a second session in this folder: run python3 code/guide-lines.py, and tell me its total line
```

Each wrote one file in the session's folder, in under 35 seconds: `.claude/state/sessions/02/blurb-gpt-<date>-<time>.md`, and the same for browser and session. Each turn's move names where to paste it.

The GPT and browser files carry your own `~/.claude/CLAUDE.md`, once. What you write there in 20 reaches ChatGPT too.

The GPT file also carries the line of `CLAUDE.md` naming `work` as the branch your sessions share. Name yours there: 20.

A session's stop deletes its folder, its blurbs with it. Paste them first.

## Unproven here

- Pasting any of them. My walk pasted nothing anywhere.

## Check

`.claude/state/sessions/02/` holds three files: one opening `blurb-gpt-`, one `blurb-browser-`, one `blurb-session-`.
