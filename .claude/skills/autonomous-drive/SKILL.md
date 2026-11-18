---
name: autonomous-drive
description: Prepares a drive whole with me, over one session, one team or several, then runs it to its end so nothing waits on my press or my ruling. Every team my advisor launches drives this way, unless I ask for a regular drive.
allowed-tools: Skill, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[the work] — omit for the work in hand · take MM — a team takes the plan session MM wrote for it, and drives"
---

# Autonomous Drive

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

Read `knowledge/0010-playbook/0011-assisting/assisting-protocols/autonomous-driving-protocols/autonomous-driving-protocols-MOC.md` and its three protocols. They rule each moment. These are their commands.

My words ask for a regular drive → this skill does not run. `1-assistant` drives it, by `assistant-drive`.

## Step 1 — A team launched inside an autonomous drive

My words are `take MM` → you are a team's assistant, launched by the autonomous drive session MM runs:

```
python3 .claude/tools/autonomous-drive.py take NN MM
```

Then invoke `1-assistant` with `drive plan`. No plan wave: the plan is agreed. Steps 5 and 6 rule the drive from here.

Session MM follows no session. It hears only what you type into its pane, with `message`:

- a ruling of mine your plan needs: the question, your recommendation, its case, and what waits on it.
- each stage's close, and your plan's end. `drive.py`'s `Next:` line names both.

MM's answer is mine: carry it. Bring me nothing until your team's end, but what Step 5 says waits for me.

## Step 2 — Where it runs

Count the teams the work spans, from my words.

- One session, or one team → it runs here. Go to Step 3.
- Several teams, with an advisor already holding them in its `.claude/state/sessions/MM/teams.json`, or on its list → say which, in one line. Launch nothing. Your move is "Type `/autonomous-drive` in session MM."
- Several teams, with none → give each team a free ten's seat. Invoke `my-advisor` with "Advise sessions SS and TT.", naming each seat. Keep this whole conversation. Then go on here, as the advisor.

## Step 3 — Prepare it with me

Follow Preparing An Autonomous Drive, step by step.

- One session → a plan of one mission, through `assistant-stages`.
- One team → your own plan, through `assistant-stages`.
- Several teams → your plan of teams, by `knowledge/0010-playbook/0018-advising/advising-protocols/protocol-planning-teams.md`, through `teams.py`. Each team not launched yet: write its plan as `assistant-stages` and `assistant-mission` write one, in `.claude/state/sessions/NN/autonomous-drive/SS/` in place of your folder, SS its seat.

Each mission's entry in its `stages.json` names its launch's `account`, `model` and `effort`. Each team's row names them: `python3 .claude/tools/teams.py set NN SS account=… model=… effort=…`. Each account is the one the check shows with the most left.

Every objective, finish line and launch-list line carries `` Run: `<command>` → <what it prints> ``.

Each pause point I name: after a stage or a mission → `python3 .claude/tools/drive.py point NN <letters and ids>`, or in a waiting team's `stages.json`, `"pause": true` on its stage or mission; before a team launches → `python3 .claude/tools/teams.py pause NN SS`.

## Step 4 — The check

```
python3 .claude/tools/autonomous-drive.py check NN
```

Show it whole. A line fails → fix what it names, then run it again.

Every line holds → your move is "Ruling: I start the autonomous drive now." On my yes:

```
python3 .claude/tools/autonomous-drive.py start NN
```

## Step 5 — It runs

Follow An Autonomous Drive Runs.

One session or one team → invoke `1-assistant` with `drive plan`. Each stage's launch rows take their missions' account, model and effort.

Several teams → for each team waiting on nothing, one at a time:

```
python3 .claude/tools/autonomous-drive.py row NN SS
python3 .claude/tools/schedule.py fire NN
```

`row` exits with `lib/drive.py`'s PAUSED code → fire nothing. Your turn says what finished, and where to look, as it printed. Your move is "Ruling: resume the drive when you choose. Say 'Resume the drive.'" "Resume the drive." → `python3 .claude/tools/autonomous-drive.py resume NN`, then that team's row and fire.

Run the fire with the Bash tool's timeout at 600000. It exits with `lib/drive.py`'s LAUNCHED code → the team joins your list: `python3 .claude/tools/advisor-page.py list NN`, with every team launched. Any other exit reaches me, with what it printed.

Follow no team. Each lead types into your pane at a ruling, a stage's close and its plan's end. Each time, run each red line's command of each waiting team. It prints what the line says → `python3 .claude/tools/teams.py green NN SS K`, the output on stdin. A team's every line green → launch it, as above.

Extra work → write its mission from rulings you hold, `Run:` objectives only. Its account:

```
python3 .claude/tools/autonomous-drive.py account NN
```

Its model and effort are System's: name neither.

A ruling of mine that blocks work, typed into your pane by a lead, or met in your own plan → take your own recommendation, carry it, and record it in one wave per team, for my review at that team's end, through `clarify-items`. A lead's ruling: type your answer into its pane, with `message`.

Only these wait for me, in chat: anything shipped, committed, pushed or deployed, anything deleted, any money moved, and any step only my hands can take. Drive on for everything else.

## Step 6 — Its end

Follow Ending An Autonomous Drive.

Your own plan → `assistant-drive` Step 9 ends it. Several teams → once `python3 .claude/tools/drive.py show SS` reads ended for every team.

```
python3 .claude/tools/autonomous-drive.py end NN
```

Your last turn lists, under four labels: what waits on me, what you ruled for me, by its wave, what finished, and what stopped. Your move is the first thing waiting on me: a ruling, or a team's stop. Once nothing waits, your move is "Action: stop this session. Type `/9-session-stop`."

## Never

Never start before every line of the check holds.

Never launch a team or a stage for my press while it runs: fire it.
