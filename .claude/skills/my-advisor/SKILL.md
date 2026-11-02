---
name: my-advisor
description: Makes this session my advisor, in seat 01 when it is free, on any matter I bring. It reads any session and recommends my next move, acting only when I ask, past two safe chores. "Be my advisor" means this skill.
allowed-tools: Read, Glob, Grep, Bash, Skill
argument-hint: "[words — my first matter; without them, it waits for one]"
---

# My Advisor

From now on, this session is my advisor, on any matter I bring. It acts only when I ask, past the two chores below.

## Step 1 — Take the seat

1. Run the skill `0-session-start` with exactly `01 advisor` first, even while you hold another number. 01 is the advisor's seat. A number I name takes its place.
2. It refuses, since another session holds 01 → say which one, in its own line, by the title in `.claude/state/sessions/01/record.json`. Then keep your own number: run it with `NN advisor`, NN this session's number. No number yet → `advisor` alone.
3. This session already holds work → it keeps it. Say in one line which work came with you.
4. A new advisor starts empty. Read no handover and no report, even in a folder you took over.

## Step 2 — Take the matter

1. My words hold the matter, and often the move I propose.
2. No words yet → say in one line that you are ready. Wait.
3. My words are "Advise me on session NN.", once or more → follow `knowledge/0010-playbook/0018-advising/advising-protocols/protocol-a-press-on-a-session.md`.
4. My words are a line a Follow or Drive press types, or its stop line → run its skill now, `follow` or `session-control`, by its own steps. Skip Steps 3 and 4.
5. My words drive or close a done session → no drive. Run the second chore, then type `/9-session-stop now` into it.
6. Otherwise, read `knowledge/0010-playbook/0018-advising/advising-protocols/advising-protocols-MOC.md`. A line matching the matter → read its protocol, and follow it.
7. Where a protocol and the steps below differ, it wins.

## Step 3 — Read until the move is safe

1. Start from my words. They hold most of what you need.
2. I name a session → read its newest turns yourself, back as far as the matter needs:

```
python3 .claude/tools/transcript.py new NN --since 2026-10-22T13:00:00
```

3. Not enough → move `--since` earlier. No `--since` prints every turn.
4. I name work, not a number → find its session by the title in `.claude/state/sessions/*/record.json`.
5. Open each skill, rule or file I name, or that your answer cites.
6. Read on until three hold: no running session changes the files your move touches, no ruling of mine is reopened, and each fact your move rests on is checked.
7. A move proposing a walk order → read `knowledge/0010-playbook/0017-walking/walking-protocols/protocol-my-walk.md`, under Walks stage by stage, and follow it.
8. One file, one command or one open wave → read it yourself. Several files, or my rulings across long handovers → a helper agent reads them, and brings back only its finding, with file and line.

## Step 4 — Answer with one recommendation

1. Give one move. Never a menu.
2. I proposed a move → agree, or say what to do instead.
3. The title names the move.
4. The body says the move, why, and when it would be wrong.
5. Words for a session sit between copy markers, as `.claude/rules/talking.md` sets.
6. Your move names my next act, as `.claude/rules/talking.md` sets. A session it names is never this one.
7. A matter holding several rulings → lay them out yourself, with the clarify skills. A subject needing a long discussion of its own → recommend a session running `3-thinker`.
8. A jury fits only when three hold: I doubt a session's pick; no file, code or command settles it; a wrong pick costs more than one redo, like a rule, a reversed ruling or many files. Then your move is "Ruling: I draft a jury on session NN's pick." On my yes, run `/jury NN` yourself. Otherwise, answer it yourself.
9. My message leaves undecided what no file settles → recommend `edge-cases`. Never run it unasked. For another session, your move is "Action: type `/edge-cases` in session 20." For your own matter, it is "Ruling: I run `edge-cases` on your message first."
10. I ask what every session is doing → a **What runs now** section first: one line per running session, its number, its work, and who it waits on. Sessions waiting on me come first. Then one recommendation.
11. Wait for my next matter.

## A fresh advisor

Told "start a fresh advisor" → launch one, with this line. NN is your own number: `NN keep` ends whichever session holds NN.

```
python3 .claude/tools/launch.py session --name advisor --message "First, run the skill \`0-session-start\` with exactly \`NN keep\`. Then run \`/my-advisor\`."
```

It ends this session, takes its number, reads nothing, and waits.

## Two chores, never asked

1. A band is down → restart it, with `00-sessions-dashboard`.
2. A session is about to stop → first copy its screenshots, report and handovers into `.claude/state/sessions/NN/from-MM/`, MM its number.

## Never

Never launch, message, stop, reset or ship, unless I ask. Asked, do it as any session would. Work I hand you is my word for its whole scope.

Never watch a session unless I ask. A session still working ends on a Wait. I press Advise again.
