# 08 — Coder

A session writes code, then checks it against the vault and your docs.

## What it does

`/5-coder` points the session to what it must know for the code in hand, then codes by the protocol that matches. Once done, it runs `/coder-check` itself. Each line of the vault or of your docs that the change contradicts comes to you.

## Your first try

In session 02:

```
/5-coder a tiny script, code/guide-lines.py: it prints each guide document's name and its line count, then the total.
```

In my walk it took under a minute. It wrote the script, ran it, and checked it against `wc -l guide/*.md`. Then it ran `/coder-check` itself: nothing contradicted.

Typed by hand right after, `/coder-check` finds nothing new: "Nothing changed".

## Your stack

A coder finds no word on your languages, versions or folders until you write it. For one small script, it needed none. Document 20 names where your own stack documents go.

## Another coding hand

`/outsource` hands a coding piece to Codex, then audits what comes back. Install and sign in to `codex` first. 1100's System page shows its card.

Codex sessions in your project read `AGENTS.md`. Keep it in step with `CLAUDE.md`. An outsourced Codex reads the files its brief names.

## Unproven here

- A protocol's gate. Walk And Close names none.
- `/outsource` with Codex. My walk did not run it.
- A docs folder. `docs` in `.claude/project.json` names none, so `/coder-check` searched the vault alone.

## Check

```
python3 code/guide-lines.py
wc -l guide/*.md
```

Both print the same count for each document, and the same total.
