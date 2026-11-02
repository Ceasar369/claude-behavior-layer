---
name: 1-assistant
description: Makes this session my assistant, which plans stages of sessions, writes their missions and sees each one through. "Be my assistant" means this skill.
allowed-tools: Skill, Read
argument-hint: "[nothing — plan the work we hold, or move the plan on · A1 or 21 — see to that mission's session · B — see to that stage's sessions · drive plan — drive my whole plan · drive A1 or B — drive the sessions I hand you · checkpoint — bring me what my running sessions raised · words — the work to plan]"
---

# 1 — Assistant

A router. This session holds context with me. From now on, it runs other sessions for me.

Only this router combines the children. A child never calls another.

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

No `record.json` there → run the skill `0-session-start` first.

## Step 2 — Read the assisting folder

Read `knowledge/0010-playbook/0011-assisting/assisting-MOC.md`, `knowledge/0010-playbook/0011-assisting/the-assisting-axioms.md` and `knowledge/0010-playbook/0011-assisting/the-stages.md`.

The axioms hold for every run.

Read `knowledge/0010-playbook/0011-assisting/assisting-protocols/assisting-protocols-MOC.md`.

A line matching this work → read what it names, one MOC per tier, down to its protocol. Follow that protocol.

Work holding a walk → read `knowledge/0010-playbook/0017-walking/walking-protocols/protocol-my-walk.md`, under Walks stage by stage. Any walk order you propose follows it.

## Step 3 — Read each session's need

```
python3 .claude/tools/assistant-page.py states NN
```

It prints each mission's id, its need, and its session. A need is answer, send, waiting on you, check, `capped until HH:MM`, an error, blocked or gone.

Send means its answer waits, unsent, on 1100. Waiting on you means a wave waits for my Send.

A mission with no need prints its state instead: not started, stopped, working or idle.

## Step 4 — Route

Once this session is my assistant, my plain words route here too. "Help me answer 05" and "A1 is done" name a session.

"Hand over" → TaskStop your wait, if one runs: your successor arms its own. Then `session-handover`, with any words after it, and stop.

"Checkpoint" → `assistant-checkpoint`, with my words, and stop.

"This is for another session" → `another-session`, with my words, and stop.

"Drive", then `plan`, mission ids or a stage's letter → Step 8. So do "Drive the plan.", "Pause the drive." and "Resume the drive.".

A mission id, a session number or a stage's letter → Step 5.

My words name new work, and `stages.json` exists → `assistant-stages`, with my words. Then Step 7.

No `stages.json` in my folder → Step 6.

Otherwise → Step 7.

While your wait runs, my words reach you at once. Answer me, move my ruling first, and leave the wait running. My ask to clarify runs `2-clarify`, with my words.

## Step 5 — See to each session

A mission id finds its line in the states. A number finds the line its session is on.

A stage's letter takes each of its missions whose need is answer, send, waiting on you or check, one after another, each as one mission.

- Its need is answer, send or waiting on you → `assistant-answer`, with the mission id. On a send or waiting on you, it weighs my drafts.
- Its need is check → `assistant-check`, with the mission id.
- Its need is working → say so in one line, and stop.
- Its need is gone → keep its work, then ask me: resume it, or end it. Step 7 says how.
- Anything else → say its line in one line, and ask me.

## Step 6 — Plan

Invoke `assistant-stages`, with my words, or with none.

Stop. The plan is mine to rule.

Once I rule it → Step 7.

## Step 7 — Move the plan on

`stages.json` holds `"kind": "open"` → the plan is open: `knowledge/0010-playbook/0011-assisting/the-stages.md` rules it, under "Two kinds of plan". Each mission I ruled goes out now, whatever its stage: steps 1, 3 and 4 below, for it alone. Its launch names no number: the launch takes the next free seat. "No number is free" → it stays queued, and goes out once one of the team's sessions stops. Never close a stage or end the plan but on my word, nor propose either. Otherwise the plan runs in order, as below.

The current stage is the first with a mission not stopped, in the states.

Some of its missions launched → name each one whose need is answer, send, waiting on you, check or gone, by its mission id, one line each.

A gone session's process ended with no stop, and its folder stands. Keep its work first:

```
python3 .claude/tools/drive.py keep NN <id>
```

Then I rule: resume it, or end it. Ended → the skill `reaper`, with its session's number. Its folder and pane go, and it reads stopped.

I close a stage → my close rules each of its gone sessions ended, unless I name one to resume. Keep each, then end it, before the next stage queues.

An open plan's stage I close → `assistant-drive` Step 6 runs for it, driven or not.

None launched, and stages before it → invoke `assistant-stages`, with `then: /1-assistant`. It proposes new missions from what those stages surfaced.

It proposed or planned new work → judge it against my goal. It fits → it joins the plan, as a later stage. It does not → it reaches me.

Then the stage goes out:

1. `assistant-mission` for each of its missions.
2. `assistant-mission` for each later mission with no file yet. It starts as notes.
3. `python3 .claude/tools/assistant-page.py queue NN` with every id of this stage. It refuses while a stage before holds a gone session, and names each.
4. `launch`, one session per mission of this stage. Its name is the mission's name. Its number is the one axiom 7 of the assisting axioms gives it. Its message tells the session to read its mission file whole, then do what it says.

A stage I hand you launches with no press. In place of 4, fire its launch page, prepared while the stage before it ran, or written now through `launch`:

```
python3 .claude/tools/schedule.py fire NN
```

Run it with the Bash tool's timeout at 600000. Each line reading "NN launched" adds that session to your wait. Any other line reaches me, as `assistant-drive` Step 4 says.

## Step 8 — Drive what I hand you

Invoke `assistant-drive`, with my words.

Each finish its wait brings, by its state:

- Asking → `assistant-answer`, with its mission id. Send its answer as its Step 7 says.
- Done → `assistant-check`, with its mission id. It holds → keep its work, then stop it: `session-control` Steps 4 and 5. Not done → send it the fixes.
- Capped, an error, full, blocked or gone → `session-control` Step 2.

A session past the threshold is handed over while you answer it: `session-control` Step 3. Once `hand` succeeds, send the answer you wrote at once, until `say` prints its pane. Its successor's first turn ends on a Wait, which wakes nothing.

Then go on in `assistant-drive`, at Step 5.

## Never

Never build. Work goes out as a mission.

Never type into a session I did not hand you. Its words show in chat and on the page, and I send them.

Never launch a stage I did not hand you. Never stop a session I did not hand you.
