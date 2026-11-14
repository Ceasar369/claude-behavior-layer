# 01 — How it thinks

Sessions, skills, hooks and 1100, through one real case. Then my three rule files.

## The words

**A session.** One Claude Code conversation, in one iTerm2 pane.

**A number.** Two digits a session claims, like `01`. Its folder is `.claude/state/sessions/01/`. `01` is the advisor's seat. `02` to `09` are side sessions. `10`, `20` and on are assistants' seats: assistant `10` leads `11` to `19`.

**The advisor.** `/my-advisor` takes seat 01 when it is free. It restarts a band that is down. Before a session stops, it copies that session's screenshots, report and handovers into its own `from-MM/`, MM the stopping session's number.

A session whose name ends in `-advisor` shows an Advise panel, atop its Transcript tab. Closed, it is a small Advise tab. Open, it lists every running session: Type and Send ask the advisor about one, and Follow and Drive hand it one to follow or drive. `/app-advisor` runs the advisor in Claude's desktop app, with 1100 beside it. In any session, `/assistant-answer` helps you answer another session: say "Help me answer session 05".

**A skill.** A command a session runs, like `/launch`. Each is one `SKILL.md` in `.claude/skills/`. Only its one-line description loads at start. Its body loads when it runs.

**A hook.** A script Claude Code runs on an event, with no model involved. Some skills are a hook alone: their work is done before the model reads a word, so they cost no turn.

**1100.** A page on your Mac, at `http://localhost:1100`. It draws every page waiting on you: a wave of decisions, a launch, a handover, a plan, a jury.

**A wave.** One round of decisions a session lays out for you. You answer on 1100, then press Send.

**A plan.** An assistant's work, in stages A, B, C. A stage holds missions, run side by side, nine sessions at most. A mission is one session's whole work, written in one file. In a plan in order, a stage goes out whole, once what it needs has stopped. An open plan sends each mission out once you rule it.

## Two kinds of answer

**A hook skill answers at once.** Its answer opens "UserPromptSubmit operation blocked by hook:". That is its normal answer, never an error. In my walk, `/0-session-start 80` answered:

```
UserPromptSubmit operation blocked by hook: Session successfully renamed to 80.
```

`/0-session-start`, `/00-sessions-dashboard`, `/reaper`, `/8-ship`, `/handover-prepare`, `/handover-resume`, `/prototype-save`, `/prototype-continue` and `/prototype-remove` answer this way.

**A model skill takes a turn.** The session reads the skill, works, then answers. In my walk, `/2-clarify what is 1100, in this layer?` took 56 seconds.

A hook's answer to a line you typed reaches your screen alone. The session's model never reads it. A session's own Skill call gets the hook's line as `PreToolUse:Skill hook error`. The zero-turn mod makes it a plain result for those nine skills. It never changes `/9-session-stop`.

## One real case

A session of mine brought my layer into an empty folder, then ran a small team there. Every line below happened.

1. It typed `claude` in the folder, then `/0-session-start 80`. A hook answered at once: "Session successfully renamed to 80." No model turn was spent.
2. It asked 80 for a welcome note, holding two decisions: the file's name, and whether the note says the folder is only a trial. 80 laid them out as a wave of two items.
3. The wave showed on 1100, on session 80's clarify page. It answered as I would: Agree on item 1, a few words on item 2, then Send. Send typed the answers into 80's pane. 80 wrote `README.md`.
4. `/launch`, with one small task, opened session 81 in a pane below 80's. 81 wrote today's date into `date.txt`, and waited.
5. `/message 81 …` typed one line into 81's pane, as if by hand. 81 added a line.
6. `/reaper 81` ended 81: its process, its pane and its folder. A hook did it.
7. `/session-handover` gave 80's seat to a fresh session. It took number 80, read what the first had saved, and went on. The old pane closed.
8. `/1-assistant`, with a goal, made 80 an assistant. It planned stage A: two missions, each reading one web page with its own browser.
9. `/1-assistant drive plan` started the drive. 80 launched 81 and 82, side by side. Each finished in about four minutes, and asked nothing. 80 checked each one's file, kept each one's work, and stopped each. The whole drive took twelve minutes.

Documents 05, 06 and 17 give you each of those lines.

## How the files are organised

Seven kinds of file. Each has one job, and costs what its job needs.

- **`CLAUDE.md`.** Every session loads it before its first word: every turn's shape, the front door, who holds authority. Every word is paid on every turn, so it stays short.
- **`.claude/rules/`.** Loaded by every session too. `talking.md`: how a session speaks to you. `thinking.md`: how it reasons. Each rule is stated once.
- **`.claude/skills/`.** A menu. A family shares one digit: 1 assistant, 2 clarify, 3 thinker, 4 prototype, 5 coder, 6 agenda, 7 walk. Its router, like `/1-assistant`, is the one you type. It calls the rest. Three more digits stand alone: 0 starts, 8 saves, 9 stops.
- **`.claude/hooks/`.** What never needs judgment. Some answer a skill, like `/8-ship`. Others guard every session: `guard.py` runs before every shell command, and refuses `pkill`.
- **`.claude/lib/` and `.claude/tools/`.** The code, in Python. A thing two files need lives once, in `lib/`.
- **`.claude/mods/`.** The zero-turn mod, written in TypeScript.
- **`.claude/state/`.** What sessions write as they run, one folder per session. Git never carries it.

The playbook sits apart, in `knowledge/0010-playbook/`. A family's router reads its own folder there, only when it runs. A session pays for the doctrine its work needs, and no more.

`CLAUDE.md` then sends every session to `knowledge/MOC.md`, before any other file. It is the front door of `knowledge/`, the vault: notes I chose to keep, for me and my sessions.

## Every turn takes one shape

`CLAUDE.md` sets it. A title of three words or fewer. The answer, in short sentences. Done: what changed on disk. Running: what still runs. Your move, always last: a ruling, an action, an answer, or a wait.

## Your step

Read `CLAUDE.md`, `.claude/rules/talking.md` and `.claude/rules/thinking.md`, whole.

Note what you would keep, and what you would change. Document 20 is where you change it.

## Unproven here

- A session's own Skill call, with and without the zero-turn mod. No walk tested either.
- The advisor, its two chores, its panel and its desktop app. No walk tested them.
- `/assistant-answer` in any session. No walk tested it here.

## Check

Answer these from the files alone, with your Claude:

1. Which file does every session load before its first word?
2. What answers `/reaper`: the model, or a hook?
3. Where does a decision a session needs from you wait?
