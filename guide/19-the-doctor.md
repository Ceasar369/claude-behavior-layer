# 19 — The doctor

What you changed in my layer, checked against my rules.

## What it does

`/behaviour-doctor` finds what your latest behaviour changes missed, against my own rules. Its first checkup reads your last commit, and every change not yet saved. Its findings come to you as a wave on 1100.

Run it after your first skill, 18: it then has something to read.

## Your first try

In session 02:

```
/behaviour-doctor
```

Its turn ends at once: "Checkup running". One checker agent reads your changes in the background. A second agent then tries to disprove each finding.

In my last walk, the checkup read four files: the new skill's three, and `.claude/project.json`. It took twenty-one minutes, and 299,539 tokens. It found two real gaps:

1. `CLAUDE.md` still named `work` as the branch my sessions share, where the trial's branch was `main`.
2. The new skill's menu line, `.claude/skills/guide-count/SKILL.md:3`, held no quoted phrase. `/skill-creator` asks for one: words you say that mean the skill, like `/reaper`'s "Kill sessions 3, 4 and 5".

The findings showed as a wave. Yours shows at `http://localhost:1100/p/clarify/02`. On item 1, I pressed Agree. Item 2 asks for your phrase, so I typed: Agree, with the phrase "count the guide". Then I pressed Send.

An agreed finding waits, unbuilt, in `.claude/state/sessions/02/doctor/agreed.md`, until you ask for its fix. A fix you already know needs only your words: 20's step 2 fixed my item 1, and the session marked it built there. The next checkup starts from the commit this one ended on.

## Unproven here

- More than ten files, with several checkers at once. My four files took one.
- A fix through `/3-thinker`, the doctor's own road for findings that need thinking through. My fix needed none.

## Check

`.claude/state/sessions/02/doctor/agreed.md` holds what you agreed.
