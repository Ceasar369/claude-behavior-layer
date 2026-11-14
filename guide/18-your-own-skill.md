# 18 — Your own skill

A skill of your own, written to my layer's standard, then proven in a fresh session.

## What it does

`/skill-creator` writes a new skill to my layer's standard. When no judgment is needed, it writes a hook: the skill then answers at once, and costs no turn.

A skill's leading digit names its family, as 01 shows. Name the digit in your line, or say it takes none. Mine took none.

## Your first try

In session 02:

```
/skill-creator when I type /guide-count, it prints each guide document's line count and word count side by side, then both totals. It takes no leading digit. Prove it in a fresh session, launched for it, then stop that session through its own /9-session-stop.
```

It chose a hook, "no judgment is needed", and wrote three things:

- `.claude/hooks/guide-count.py`, the hook;
- `.claude/skills/guide-count/SKILL.md`, the skill's body;
- two entries in `.claude/settings.json`, so the hook runs.

Then it proved it. It launched a fresh session, typed `/guide-count` there, and read the hook's answer:

```
UserPromptSubmit operation blocked by hook: Guide successfully counted.
```

A table followed: each document's lines and words, then both totals. Then it stopped that session. In my walk: eight minutes, its proof included.

A hook skill costs no tokens. Every prompt and skill call in the project then takes a little longer: the hook reads each one. My walk's session put it at about 37 milliseconds.

## Unproven here

- `/skill-creator` with no digit named. My line named it, so its question never showed.
- The 37 milliseconds. Nothing measured them.

## Check

In a session started after it, type:

```
/guide-count
```

It answers at once, with no turn. Its totals match the last lines of `wc -l guide/*.md` and `wc -w guide/*.md`.
