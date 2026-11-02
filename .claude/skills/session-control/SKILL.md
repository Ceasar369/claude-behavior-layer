---
name: session-control
description: Drives sessions for me, answering them as me, in full or partially on one topic. "Partially drive 22 on …" means this skill.
allowed-tools: Read, Glob, Grep
argument-hint: "NN [MM …] [on <topic>] — the sessions you drive, and a partial drive's topic"
---

# Session Control

It types with my authority. Every word you send arrives as mine.

A full drive runs all five steps, until each session closes. A partial drive runs Steps 1 to 4, on one topic I name, and Step 5 only when that topic names the close and I said yes.

## Who uses it

These sessions, and no other.

- A session testing a new behaviour, on the throwaway sessions it launched for that test.
- A stage session, on the helper it started through `helper-session`.
- An assistant, on the sessions I hand it.
- A session, on the session it launched through `drive-chrome`, on the account that drives my Chrome.
- Any session I ask to partially drive another, on one topic.

Each NN is one of yours, or you stop here.

## Step 1 — Watch

A partial drive first says back its topic and what ends it, one line each, by the session's title in `.claude/state/sessions/NN/record.json`. Nothing in my words names a topic → ask me for it, and start nothing. My advisor then takes nothing until my yes to that say-back: it types into that session as me. Any driver's topic naming the session's close takes that yes before the close. Your move asks it, as a Ruling, like "Ruling: I drive session 22 on its typos, and close it once they are fixed." My advisor's one yes covers its drive and that close. My words before the say-back are never that yes, even when they name the drive or the close.

Then take them, once, before your first wait. A partial drive names its topic, in my words:

```
python3 .claude/tools/successor.py take MM NN …
python3 .claude/tools/successor.py take MM NN --topic "<the topic>"
```

MM is your own number. 1100's wheel and the Handover page read only this, never your wait. Your seat keeps it across a handover. A session you followed is driven now: its follow ends.

`Refused NN` → another session drives it. Nothing is taken: arm no wait. It reaches me.

Then arm your one wait, in the background. Run it with the Bash tool, `run_in_background: true` and `timeout: 7200000`:

```
python3 .claude/tools/transcript.py wait --awake
```

It covers every session you drive and follow, each on the bookmark its record keeps. It hears each take and release while it runs. It says a wait already runs → that wait covers them. Arm nothing.

Then end your turn. Its move is a Wait naming the sessions, like "Wait: sessions 22 and 31 answer. I reply to them as you.", unless something still waits on me. A turn you end while you drive sessions and no wait covers them is held once, by `.claude/hooks/unwatched.py`.

Claude Code starts your turn the moment the wait ends. Read its output file whole.

- Its first line names each session that woke it: by its finish, or idle. Act on those alone, by Step 2. One you follow → the `follow` skill's Step 3.
- Each block's head says what you do with that session. It ends on its `State:`.
- It woke at its limit → no session finished.
- Claude Code stopped it, status `killed` → nothing finished either.

Then arm it again. Its last line reads `Following and driving nothing.` → arm no wait.

One wait runs at a time. A session joining → take it. The running wait hears it.

My words reach you while the wait runs. Answer me, and leave it running. My ask to clarify runs `2-clarify`, with my words.

## Step 2 — Answer

Answer only from my rulings: this conversation, your mission, the agreed items.

In a partial drive, answer only on its topic. An item outside it is one my rulings cannot answer.

By its `State:`:

- `asking` → answer it.
- `done` → its work is reported done. Check it on disk. Holds → Step 4.
- `capped until HH:MM` → its account hit a usage limit. Type nothing. The wait returns at the reset.
- `capped until HH:MM, due now` → type "Go on with your mission." into it, once.
- `error, one more try at HH:MM` → an API error, not a usage limit. Type nothing. The wait returns then.
- `error, one more try at HH:MM, due now` → type "Go on with your mission." into it, once.
- `error, three times in a row` → it reaches me.
- `full` → its context filled its window. Type nothing: Step 3 hands it over.
- `blocked` → a dialog holds it. Type nothing into it, ever: a Return there picks option 1. It reaches me.
- `gone` → its process ended with no stop. Keep its work, as Step 4 does. It reaches me. The wait wakes on it this once, then says `As told before.` I rule: resume it, or end it. Ended → the skill `reaper`, with its number: its folder and pane go, and the wait releases it. Resumed → the wait hears it.
- `stopped`, or another session holds its number → the wait released it. Tell me.
- `idle since HH:MM, N minutes` → it waits on you. A full drive sends it its next work now, or its stop. A partial drive sends it its next work on its topic, or nothing: it waits on me.

A `say` the permission check refuses leaves that step unproven. Say so in the turn. It never reaches me as an Action.

A session you drive never sits idle on work you hold. Each finish gets, at once, every piece of work it can do now, or its stop. Work waiting on another session goes the moment that session reports done. Its stop alone waits for its check.

A wave is yours to send only when it holds an answer of yours, and no draft of mine. Moving an item to chat answers nothing. Any other wave: mark nothing, send nothing. It reaches me.

Yours waits on its page. Mark every item:

```
python3 .claude/tools/clarify-page.py rule NN --item 3 --agree
python3 .claude/tools/clarify-page.py rule NN --item 4 --feedback <<'EOF'
The words I would type, in my voice.
EOF
```

An item my rulings cannot answer takes this feedback, word for word: "This one moves to chat. My answer comes there. Go on with everything else." It reaches me.

Then send the whole wave at once, with no yes of mine:

```
python3 .claude/tools/clarify-page.py send NN
```

My ask for your recommendations covers the wave it names.

A question in chat, or my answer to what reached me:

```
python3 .claude/tools/panes.py say --to NN --line "<one paragraph, in my voice>"
```

`.claude/rules/talking.md` rules the voice, under "Writing for another reader".

`say` prints the pane it typed into. It prints nothing, or a sentence → nothing was typed. Say it again, three tries in all. A third with no pane reaches me.

What reaches me shows whole in every turn you end, and your move names it, with its session and item, until I answer. The others go on.

## Step 3 — Hand over, before you wait again

Whoever drives a session hands it over. A driver nobody drives hands itself over.

Once each finish is handled by Step 2, before you arm the wait again:

```
python3 .claude/tools/successor.py due MM NN …
```

MM is your own number, then every session you drive not stopped. One line each, yours last:

- `Hand over NN` → decide first what Step 2 does with its finish, as if no handover came. Its work holds → Step 4, then Step 5 in a full drive, and no handover. Otherwise run `python3 .claude/tools/successor.py hand NN --by MM` with the Bash tool, `run_in_background: true`. Meanwhile write that answer, or those fixes. Send nothing yet.
- `Wait for NN` → it still works. Its wrap-up hook turns it to you.
- `Drive on NN` → nothing.
- `Hand over` → TaskStop your wait, if one runs. Then `session-handover`, with no words. Arm no wait: your successor waits on the same sessions.
- `Driven by KK` → nothing. KK hands you over.
- `Drive on` → arm the wait again.

`hand` ends:

- With "successfully" → send it what you wrote, by Step 2, at once, until `say` prints its pane. It is its first work, and reaches it once it has read the copies. Its own first turn ends on a Wait, which wakes nothing, so an answer never sent leaves it waiting for good. Then arm the wait again.
- Without "successfully" → NN keeps its seat. Send it what you wrote. The failure reaches me.

Your own `session-handover` fails → you keep the seat. It reaches me. Arm the wait again. At the next moment, `due` decides again, without asking me.

Mid-turn, the wrap-up hook may tell you to hand yourself over. `.claude/rules/thinking.md` says when, under "Finish what was asked". Do it by this step.

## Step 4 — Save

A session's work is done → keep what you need. In a partial drive, its work is the topic, done once it holds on disk.

An assistant keeps a mission's folder, without its screenshots, and its transcript, in its own `reports/<id>/`:

```
python3 .claude/tools/drive.py keep MM <id>
```

Any other session keeps the transcript:

```
python3 .claude/tools/transcript.py copy NN --into MM
```

MM is your own number.

A partial drive ends here. Its topic names its close, and I said yes → Step 5. Otherwise let it go:

```
python3 .claude/tools/successor.py release MM NN
```

The running wait lets it go. Tell me in your turn: the topic, what holds, and that NN is mine again.

My line "Stop driving session NN." ends its drive at once, with no save and no close. Let it go, as above. Tell me where its topic stands, and that NN is mine again.

## Step 5 — Close

A full drive, or a partial drive whose topic names the close, once I said yes. Stop it, then let it go:

```
python3 .claude/tools/panes.py say --to NN --line "/9-session-stop now"
python3 .claude/tools/successor.py release MM NN
```

Its folder and panes go when it stops.

A gone session has no Claude to stop, and `say` types nothing into its pane. Step 2 ends it.

## Never

Never drive any other session.

Never answer what only I rule.

Never run two waits.

Never leave a session a full drive holds running.

Never leave a session you drive idle on work you hold.

Never answer outside a partial drive's topic, nor close its session without my yes to a topic naming the close.
