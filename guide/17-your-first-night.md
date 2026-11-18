# 17 — Your first night

A plan of missions, driven while you sleep, with nothing waiting on your press or your ruling. Easy tasks, simple research and a browser.

## How an autonomous drive runs

You prepare the drive whole with one session, through `/autonomous-drive`. Then it runs to its end. Only what your hands alone may do waits for you.

Your assistant is one session. It plans the work as stages, A then B. Each stage holds missions, run side by side. Each mission is one session's whole work. One session alone is a plan of one mission. Work across several teams makes your session their advisor, each team led by its own assistant.

**Preparing, with you.** Your assistant:

- writes every plan, and every mission whole;
- makes each objective a `Run:` line: a command, and what it prints once the work is done;
- keeps out any mission that needs you: thinking, a prototype, discovery, or a walk with you;
- sets each launch's account, model and effort, each on the account with the most left;
- keeps each pause point you name: after a stage, after a mission, or before a team;
- sends its wave of items, so each ruling it can see coming reaches you before the start;
- runs its check, `python3 .claude/tools/autonomous-drive.py check 10`. A failing line names its fix. Every line holding, its move asks you to start.

**Running, without you.** Your assistant:

- launches each stage's sessions, with no press;
- waits in the background, and wakes at each one's finish;
- answers each session from your rulings;
- takes a ruling of yours the work needs as its own recommendation, carries it, and records it in a wave, for your review at the end;
- checks each finish on disk, keeps its work, and stops its session;
- launches each next stage once what it needs has stopped.

A drive that stops for your rulings is a regular drive: `/1-assistant`, then `/1-assistant drive plan`.

## A night needs every ruling up front

A ruling your words leave open, your assistant takes for you. It waits in a wave till morning, already carried. So your `/autonomous-drive` line carries everything: the goal, who it is for, when, why, and what each session does when something goes wrong.

Given a bare subject, an assistant plans more than you asked. Mine, in 14, planned discovery, a prototype and two more stages. One line with every ruling cut it to one mission.

In my walks, a session stopped for my answer on a wave of items, a say-back, a thinker's round, a triage's ending, a helper's agree, and the doctor's findings. In a drive, your assistant answers these from your rulings, or takes its own recommendation.

**Research and a browser.** Each session has its own hidden browser, Playwright, and Claude Code's own web search and fetch. Both run with nobody watching. Playwright holds no login: a page behind one shows signed out. Your own Chrome, through `/drive-chrome`, holds your logins: 15. Sign each site in before you sleep.

## Before you leave

**Keep your Mac awake** (your hands). While your assistant waits in the background, its wait holds your Mac awake, on power alone. The hold lets go once the wait ends. A working session holds it too, then lets go within two minutes of its turn's end. In my walk, each wait took its hold, through macOS's own `caffeinate`.

So keep it on power, lid open. On battery, the wait's hold does nothing.

**Auto mode on.** From Claude Code 2.1.283 it is on by itself: 02. A permission prompt would hold a session until your hand answers it. My walks met none.

**1100 stays up.** If your assistant reaches your limit, 1100 types "Resume the drive." into it at the reset.

**Size a stage to your Mac.** Each open browser holds about half a gigabyte.

## Your first night

**Start your assistant.** A fresh session, at your project's root: `claude`, then:

```
/0-session-start 10
```

10 is an assistant's seat. Its missions take 11 to 19.

**Give it the goal, with every ruling.** My first night's line, written for this skill:

```
/autonomous-drive Plan one stage, A, of two missions, side by side, for a first autonomous drive. A1, python version: with its Playwright browser, it opens https://www.python.org/downloads/ and reads the newest Python 3 release named there, then runs one web search to confirm it, then writes findings/python.md at this project's root, three lines: the version, the page's address, the search's source. A2, iterm version: the same for iTerm2, from https://iterm2.com/downloads.html, the newest stable release, into findings/iterm2.md. Who: one session each, for me to read in the morning. When: now, tonight. Why: to prove a team runs all night on browser and research alone. My rulings, up front: neither mission needs any answer of mine. A page that will not load: the web search alone is enough, and the file says so. Two sources that disagree: write both, name the newer, and go on. The look is settled: plain Markdown, three lines. No discovery mission, no prototype, no later stage. Each mission writes only its one file: no commit, no push, no server, no band 00. Each is done when `wc -l < findings/python.md`, or `findings/iterm2.md`, prints 3. Once both are checked and stopped, the plan ends.
```

**Read its plan and its check**, in chat and at `http://localhost:1100/p/assistant/10`. Answer its wave, if it sends one.

**Start the drive.** Its move reads "Ruling: I start the autonomous drive now." Say yes. Then leave it.

Your own goals go the same way: one `/autonomous-drive` line with every ruling, the check, then your yes.

One task alone needs no team: `/self-drive`, 13.

**An open plan.** Name the plan open in your words to `/1-assistant` or `/another-team`. Each mission goes out once you rule it and a seat is free, into the next free seat among the team's ten. The plan page shows an "Open" chip. A stage closes, and the plan ends, only when you say. So an open plan is a regular drive's, never an autonomous one's.

## What still needs you

Only these wait for you during an autonomous drive:

- anything shipped, committed, pushed or deployed;
- anything deleted;
- any money moved;
- any step only your hands can take;
- each pause point you named, with what finished and where to look. "Resume the drive." goes on.

A session in trouble reaches you too:

- a permission prompt or a dialog, blocking a session;
- a session gone, its process ended with no stop;
- an API error, three times in a row;
- a session failing to launch, three times;
- a failed handover;
- a failed pane arrangement, shown in the launch row's status.

Each reaches you in the assistant's turn. A move asking you something turns the assistant's number red on 1100. It calls a desktop notification.

Only the session it concerns waits. The rest drive on.

New work outside your goal never stops the drive. Your assistant writes its mission from your rulings, and launches it on System's account, model and effort.

## Your limits

Each mission runs on the account its preparation set: the one with the most left, then. Extra work takes the next account in your order, 04, or the one with the most left when that one is capped. With one account, every session runs on it.

Once an account's 5-hour limit is reached, its sessions wait for the reset. A capped session waits, then its driver types "Go on with your mission."

A handover never moves to another account for a limit.

One login on two Macs shares its limits. Each Mac's 1100 sees the other's use.

## In the morning

- The plan, at `http://localhost:1100/p/assistant/10`.
- Your assistant's last turn, under four labels: what waits on you, what it ruled for you, by its wave, what finished, and what stopped. Its move is the first thing waiting on you.
- Each ruling it took for you, in its wave, to agree or change.
- Each mission's report, kept by your assistant: `.claude/state/sessions/10/reports/A1/`, `A2/`, and on.
- The stage's summary: `.claude/state/sessions/10/summaries/A.md`.
- What each mission wrote, where it wrote it: `findings/python.md`, in my walk.

## Unproven here

- A whole night. My first night ran twelve minutes, as a regular drive, before `/autonomous-drive` existed. No walk has run this skill.
- A ruling taken for you, and its wave in the morning. No walk tested it.
- The wait's hold keeping a Mac awake on power. My test ran on battery, where it does nothing.
- A limit reached mid-drive, and a Mac asleep at its reset. Nothing reached a limit.
- Every line of "Your limits". They come from my code: nothing capped while my walks ran.
- A notification reaching you. Nothing needed one.
- Playwright's first run on a Mac that never ran it. Mine already held its browser.
- `/drive-chrome` in a drive. My walk used Playwright alone.
- A drive across several accounts, or several teams. My drive ran on one account, as one team.
- A pause point, and a failed arrangement. No walk tested them.

## Check

The morning after your first night:

- Your assistant's last turn lists what finished, and nothing waits on you but its stop.
- `.claude/state/sessions/10/drive.json` reads `"state": "ended"`.
- `python3 .claude/tools/autonomous-drive.py end 10` was run: `.claude/state/sessions/10/autonomous-drive/drive.json` is gone.
- `findings/python.md` and `findings/iterm2.md` each hold three lines.
