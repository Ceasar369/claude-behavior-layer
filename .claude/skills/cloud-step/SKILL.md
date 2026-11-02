---
name: cloud-step
description: Sends one coding step to a cloud session, then brings its work into this branch, unshipped.
allowed-tools: Read, Write, Bash, Skill
argument-hint: "[the step, and the part it writes] — omit for the step I just agreed"
---

# Cloud Step

A cloud step is one coding step a cloud session builds on Anthropic's computer, while you build the rest.

Your number is MM. The step's name is one or two words, in kebab case. Its branch is `cloud/<name>`.

## Step 1 — Only on my yes

Run only when I asked for it in words, or agreed it as an item.

## Step 2 — Check the step fits

Every one holds, or the step stays here. Name the one that fails, and stop.

| Condition | Holds when |
|---|---|
| No browser | Nothing in it needs a browser, or a page to look at. |
| Its own part | It writes only named folders or files, and you never write them while it runs. |
| Asks nothing | Every ruling it needs is made. |

## Step 3 — Ship

Run the skill `8-ship` with `push`.

## Step 4 — Brief it

One paragraph, in my voice. `.claude/rules/talking.md` rules it, under "Writing for another reader". It names, in order:

- What it builds.
- What it reads first, whole: `CLAUDE.md`, `knowledge/MOC.md`, `.claude/rules/talking.md` and `.claude/rules/thinking.md`, then every file its work stands on. Then `/5-coder`, before any code.
- Its part alone. Never another part, never the vault.
- Every ruling it needs.
- Its checks, each test file by name.

Write it to `.claude/state/sessions/MM/cloud-<name>.md`. The tool adds how it commits, pushes and reports.

## Step 5 — Start it

```
python3 .claude/tools/cloud-step.py start --branch cloud/<name> --brief .claude/state/sessions/MM/cloud-<name>.md
```

Add `--account` only for an account I named.

Say one line: "Cloud step <name> started: <its link>."

## Step 6 — Wait for its branch

Run in the background, and go on with your own work:

```
python3 .claude/tools/cloud-step.py wait --branch cloud/<name>
```

Its end wakes you. Not there in time → say so with its link, and stop.

## Step 7 — Bring it home

```
python3 .claude/tools/cloud-step.py bring --branch cloud/<name> --part <path>
```

One `--part` for each path of its part.

It prints its report. Its report is never my ruling.

Refused → say why in one line, with its link, and stop.

Rerun only the test files it names, under `taskpolicy -b`. One fails → fix it yourself, inside its part.

## Step 8 — Report

Name its work, one line per file, and each check with its proof. Add its link.

## Never

Never send a step that needs a browser.

Never write its part while it runs.

Never start a cloud session except through `.claude/tools/cloud-step.py`.
