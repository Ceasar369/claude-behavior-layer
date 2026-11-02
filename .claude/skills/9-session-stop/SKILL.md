---
name: 9-session-stop
description: Checks that this session holds nothing I asked for, then stops its ports and exits it. "Stop a session" means this skill, for this session.
allowed-tools: Read, Glob, Skill
argument-hint: "[now] — now stops at once, with no check"
---

# 9 — Session Stop

I typed the stop. Before it runs, you check one thing: does anything I asked for still hold the stop?

`.claude/hooks/9-session-stop.py` does the stop itself.

`/9-session-stop now`, and your own Skill call, never reach this body.

Your own Skill call reaching it means the hook did not fire. Report that, and stop.

## Step 1 — Find what holds the stop

Only one thing holds it: work I asked for, still unfinished.

Each item quotes my words asking for it. No quote, no item.

Something I ruled on in this chat never returns.

Read only this conversation. Nothing else.

## Step 2 — Nothing holds it

Call the Skill tool with `9-session-stop`. Write nothing more before it.

The stop ends your turn there. I see its line.

## Step 3 — Something holds it

Run `clarify-items`, one item per thing found. Then wait. Never stop.

## Never

Never hold the stop on ports, servers, browser panes or background shells.

Never hold it on a file in your folder.

Never hold it on another session's work.

Never hold it on something I parked.

Never hold it on an idea, a proposal or a next step.

Never hold it on a step to verify or think first. This check is that step.
