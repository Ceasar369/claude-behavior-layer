# 17 — Your first night

A plan of missions, driven while you sleep, and what still needs you. Easy tasks, no answer needed from you, simple research and a browser.

## How a drive runs

Your assistant is one session. You give it a goal with `/1-assistant`. It plans the work as stages, A then B. Each stage holds missions, run side by side. Each mission is one session's whole work.

`/1-assistant drive plan` starts the drive. Your assistant then:

- launches each stage's sessions;
- waits in the background, and wakes at each one's finish;
- answers each session from your rulings;
- checks each finish on disk, keeps its work, and stops its session;
- launches each next stage once what it needs has stopped, with no press. A stage whose launch page holds a planned pane move waits for your press of Launch.

My first night, in a trial folder: two missions, about four minutes each. The whole drive, plan to end, took twelve minutes. No session asked anything.

## A night needs every ruling up front

A mission needing one answer of yours waits for it till morning. So your `/1-assistant` line carries everything: the goal, who it is for, when, why, and what each session does when something goes wrong.

Given a bare subject, an assistant plans more than you asked. Mine, in 14, planned discovery, a prototype and two more stages. One line with every ruling cut it to one mission.

In my walks, a session stopped for my answer on a wave of items, a say-back, a thinker's round, a triage's ending, a helper's agree, and the doctor's findings. In a drive, your assistant answers these from your rulings. A question your rulings cannot answer waits for you.

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

**Give it the goal, with every ruling.** The line that ran my first night, less one clause:

```
/1-assistant Plan one stage, A, of two missions, side by side, for a first night drive. A1, python version: with its Playwright browser, it opens https://www.python.org/downloads/ and reads the newest Python 3 release named there, then runs one web search to confirm it, then writes findings/python.md at this project's root, three lines: the version, the page's address, the search's source. A2, iterm version: the same for iTerm2, from https://iterm2.com/downloads.html, the newest stable release, into findings/iterm2.md. Who: one session each, for me to read in the morning. When: now, tonight. Why: to prove a team runs all night on browser and research alone. My rulings, up front: neither mission needs any answer of mine. A page that will not load: the web search alone is enough, and the file says so. Two sources that disagree: write both, name the newer, and go on. The look is settled: plain Markdown, three lines. No discovery mission, no prototype, no later stage. Each mission writes only its one file: no commit, no push, no server, no band 00. Each one's report holds its file's three lines. Once both are checked and stopped, the plan ends.
```

**Read its plan**, in chat and at `http://localhost:1100/p/assistant/10`. Its move asks you to agree.

**Start the drive.** Type:

```
/1-assistant drive plan
```

That line is your agreement. No other word is needed, even when its move asks for others, like "Drive A": mine did, and this line worked. Then leave it.

Your own goals go the same way: one `/1-assistant` line with every ruling, then the drive.

One task alone needs no team: `/self-drive`, 13.

**An open plan.** Name the plan open in your words to `/1-assistant` or `/another-team`. Each mission goes out once you rule it and a seat is free, into the next free seat among the team's ten. The plan page shows an "Open" chip. A stage closes, and the plan ends, only when you say.

## What still needs you

Only these reach you during a drive:

- a question your rulings cannot answer;
- a permission prompt or a dialog, blocking a session;
- a session gone, its process ended with no stop;
- an API error, three times in a row;
- a session failing to launch, three times;
- a failed handover;
- a stage whose planned pane move needs your press of Launch;
- a failed pane arrangement, shown in the launch row's status;
- new work outside your goal. It never stops the drive.

Each reaches you in the assistant's turn. A move asking you something turns the assistant's number red on 1100. It calls a desktop notification.

Only the session it concerns waits. The rest drive on.

## Your limits

Each launch takes the next account in your order: 04. With one account, every session runs on it.

Once an account's 5-hour limit is reached, its sessions wait for the reset. A capped session waits, then its driver types "Go on with your mission."

A launch never passes over a capped account. On its turn, it starts there, and waits too. A handover never moves to another account for a limit.

One login on two Macs shares its limits. Each Mac's 1100 sees the other's use.

## In the morning

- The plan, at `http://localhost:1100/p/assistant/10`.
- Your assistant's last turn. Mine read "Night drive ended · The plan is done".
- Each mission's report, kept by your assistant: `.claude/state/sessions/10/reports/A1/`, `A2/`, and on.
- The stage's summary: `.claude/state/sessions/10/summaries/A.md`.
- What each mission wrote, where it wrote it: `findings/python.md`, in my walk.

## Unproven here

- A whole night. My drive ran twelve minutes.
- The wait's hold keeping a Mac awake on power. My test ran on battery, where it does nothing.
- A limit reached mid-drive, and a Mac asleep at its reset. Nothing reached a limit.
- Every line of "Your limits". They come from my code: nothing capped while my walks ran.
- A notification reaching you. Nothing needed one.
- Playwright's first run on a Mac that never ran it. Mine already held its browser.
- `/drive-chrome` in a drive. My walk used Playwright alone.
- A drive across several accounts. My drive ran on one.
- An open plan, a planned pane move during a drive, and a failed arrangement. No walk tested them.

## Check

The morning after your first night:

- Your assistant's last turn says the plan is done.
- `.claude/state/sessions/10/drive.json` reads `"state": "ended"`.
- `findings/python.md` and `findings/iterm2.md` each hold three lines.
