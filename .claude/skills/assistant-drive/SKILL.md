---
name: assistant-drive
description: Steers what I hand my assistant, from its take to its end.
allowed-tools: Skill, Read
argument-hint: "plan · a stage's letter · mission ids · pause · resume — what I hand you, or what I say of the drive"
---

# Assistant Drive

My number, NN, as `CLAUDE.md` defines it.

`drive plan` hands you my whole plan, from where it stands. A stage's letter hands you each session of that stage not stopped. A mission id hands you its session.

The protocols under Driving, in the assisting protocols' MOC, rule each moment. These are their commands.

## Step 1 — Take it

```
python3 .claude/tools/drive.py take NN <plan, letters or ids>
```

Its last line, `Next:`, is your next step. Follow it, and each `Next:` line `drive.py` prints after.

A mission with no session yet → name it in one line, and leave it.

At every take, a successor's too, your turn shows each thing still waiting on me, whole, and your move names it: a session the states call blocked or gone, an item the handover copies show I never answered.

## Step 2 — Wait

`session-control` Step 1, with every session you drive not stopped: take each, then arm the one wait. It keeps each session's bookmark itself.

A session I hand you while you drive joins the same wait: take it. The running wait hears it.

## Step 3 — Each finish

`1-assistant` Step 8 routes it, by its state. Then go on here, at Step 5.

## Step 4 — What reaches me

Only these: an item my rulings cannot answer, a wave holding my drafts or no answer of yours, a blocked session, a gone session, an error three times in a row, a launch row failing three times, a failed handover, new work that does not fit my goal.

Reach me three ways at once, at every such moment:

1. Your turn shows it whole, and your move names it, with its session and item: `Answer needed: …` or `Ruling: …`. A wave waiting for my Send: `Action: on 1100, rule session NN's wave K, then Send.` A move asking me anything turns you red on 1100.
2. Call the PushNotification tool, `status: "proactive"`, with one line naming it. Your tools may hold it deferred: load it first through ToolSearch, `select:PushNotification`. Call it each time, even after one came back "Not sent".
3. Drive on for every other session.

Until I answer, every turn you end shows each thing still waiting on me, whole, and its move names it.

My answer comes in your chat. Type it into its session yourself, through `session-control` Step 2.

## Step 5 — After each moment, before you wait again

`session-control` Step 3, with every session you drive not stopped. It hands over each one past the threshold, then you, when you are.

Your own `Hand over` → your successor takes your seat, and drives on.

## Step 6 — A stage stopped

In an open plan, a stage closes only when I close it: then this step runs for it.

Say its short summary in your chat: what each session did, and what it taught. Name who answered each thing: you, or me.

Then keep the same words:

```
python3 .claude/tools/drive.py close NN <letter> <<'EOF'
<the same words>
EOF
```

## Step 7 — The next stage

While a stage runs, prepare the next stage's launch page through `launch` Step 4, scheduled. Its rows are mine to change until it fires. Once the stage closes → `1-assistant` Step 7.

In an open plan, no launch page. Each mission I rule goes out at once, and each waiting for a seat once one frees: `1-assistant` Step 7.

## Step 8 — Pause and resume

"Pause the drive." → end the step you are on. Run `python3 .claude/tools/drive.py pause NN`, then TaskStop the wait. Your move is "Ruling: resume the drive when you choose. Say 'Resume the drive.'" While paused, arm no wait, and act on no session.

"Resume the drive." → run `python3 .claude/tools/drive.py resume NN`. Then arm the one wait, unless one runs: it returns at once on every finish that came while paused. Its `Next:` line says the rest.

## Step 9 — The end

Every session the drive holds has stopped. In an open plan, only once I end it, and each stage that went out is closed by Step 6:

```
python3 .claude/tools/drive.py end NN
```

It ends → say so in one line, with no merged report. Your move is "Action: stop this session. Type `/9-session-stop`.", unless the plan holds more. Arm no wait.

It names what holds the end → settle each, then run it again.
