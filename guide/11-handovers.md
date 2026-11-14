# 11 — Handovers

A session's conversation saved, resumed in a fresh session, then reported.

## What they do

A session's context fills as it works. A handover gives its seat to a fresh session, which reads what the first saved, and goes on.

- `/session-handover`, from 06, does it at once, in one line.
- `/handover-prepare` saves the conversation now. `/handover-resume NN`, typed later in any other session, hands the seat over.
- `/session-report` writes where the work stands into one file, for another session to read.

## A second session, waiting

Type into 02:

```
/launch one session: it waits for my next message.
```

Session 03 opens below 02, and waits.

## Prepare, then resume

In 02:

```
/handover-prepare
```

A hook answers at once, saying it saved session 02 as `handovers/1.md` and to run `handover-resume 02` from a fresh session. The copy holds 02's whole conversation, turn by turn.

Its answer also says "Name what still runs in your reply". 02 never reads it: a hook gave it, not 02's model.

In 03:

```
/handover-resume 02
```

A hook answers that session 02's successor launched and takes its seat. The old pane closes.

The successor opens under another number for about fifteen seconds, then takes 02. It reads the copy, then lays out the next steps. In my walk: twenty-two seconds to the seat, almost seven minutes to its first turn. The old pane closes.

## Report

In 02, now the successor:

```
/session-report
```

It writes `.claude/state/sessions/02/report.md`: what you agreed, what is done with its proof, what is left to do, what is still open. Each ruling cites its turn. It also lays out Agreed, To do and Still open in chat, then waits. In my walk: four minutes.

## Unproven here

- A resume long after its prepare. Mine came within a minute.
- The report laid out in chat. My walk preceded that change.

## Check

- `.claude/state/sessions/02/handovers/1.md` exists.
- The successor's status line shows `02`.
- `.claude/state/sessions/02/report.md` exists.

Session 03 still waits. Document 12 uses it.
