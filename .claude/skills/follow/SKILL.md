---
name: follow
description: Follows a session live, for a task and until its end, waking whenever it speaks. "Follow session 20" means this skill.
allowed-tools: Read
argument-hint: "NN — the session to follow; without it, nothing is followed"
---

# Follow

You follow session NN, live, for one task, until its end. Your work gives you your role. MM is your own number.

## Step 1 — Say it back, then take it

1. You drive NN, in `.claude/state/sessions/MM/driving.json` → say the drive already wakes you on its every turn. Start nothing.
2. Name NN by its title, in `.claude/state/sessions/NN/record.json`.
3. Name what you follow it for, and what ends the follow, from my words or your own Wait.
4. Nothing names a task → ask me for it. Start nothing.
5. Say both back, one line each. Then take it at once, in the same turn, with no yes of mine:

```
python3 .claude/tools/follow.py take MM NN --for "<what you follow it for>" --ends "<what ends the follow>"
```

`Refused` → say its line. Take nothing more.

## Step 2 — Wait on it

One wait covers every session you follow and drive. It hears each take and release while it runs.

Run it with the Bash tool, `run_in_background: true` and `timeout: 7200000`:

```
python3 .claude/tools/transcript.py wait --awake
```

It says a wait already runs → that wait covers NN. Arm nothing.

End your turn. Its move is a Wait naming the session, like "Wait: session 20 answers. I then check its report."

## Step 3 — Its end wakes you

1. Read the wait's output file whole. Its first line names each session that woke it.
2. Each block's head says what you do with that session. One you drive → `session-control` Step 2.
3. One you follow → answer its new turns, in your role. By its `State:`:
   - `asking`, `done` or `idle` → your task goes on.
   - `capped until` or `error, one more try` → nothing. It goes on by itself.
   - `blocked`, `full` or `error, three times in a row` → it reaches me: its session, and what holds it.
   - `gone` → it reaches me: resume it, or reap it. It stays followed. `As told before.` → nothing.
   - `stopped`, or another session holds its number → the wait released it. Tell me the follow ended, and why.
4. Its end holds → `python3 .claude/tools/follow.py release MM NN`. Tell me what it was for, and what holds.
5. Before you wait again, hand yourself over past the threshold, as a driver does: `python3 .claude/tools/successor.py due MM`. Its last line `Hand over` → `session-handover`, with no words, and arm no wait: your successor keeps every follow, and arms the same wait.
6. The last line reads `Wait again.` → Step 2. `Following and driving nothing.` → arm no wait.
7. Nothing new woke you → your turn says "No new turn.", and its move is the same Wait.

## Step 4 — My words reach you while the wait runs

1. Answer me. My ask to clarify runs `2-clarify`, with my words.
2. "Stop following session NN." → `python3 .claude/tools/follow.py release MM NN`. Say the follow ended. The running wait lets NN go.
3. Arm no wait. The one running goes on.

## Never

1. Never type into a session you follow.
2. Never run a second wait.
