# Ask · Answer Bus

How a blocked session reaches the user in another window.

**Trigger** — a session cannot continue without the user, and they are elsewhere.

**Done** — the answer is pulled, weighed, and the work has resumed.

The operating steps live in the ask, answer, and inbox skills. This is the
design they rest on.

## State is which files exist

A question is one file. Its answer is a second file, same number.

Both live inside the asking session's own folder. There is no bus root, no
counter, and no pairing record.

Nothing is stored, so an interrupt cannot strand a session in a wrong state.

## Three writers, three files

The asker writes the question. The answerer writes the answer. The asker
renames the answer once read.

No two parties ever write the same path. So there is no clobber to guard against.

## Three states, all derived

- **Open** — a question exists with no answer beside it.
- **Answered** — an answer exists and has not been pulled.
- **Idle** — nothing is waiting on anyone.

Idle is not done. It means nobody owes a move right now.

## Fewest rounds, never smallest question

A round trip re-sends both contexts. The question itself is nearly free.

Coupled decisions travel in one file. Ruling one changes the other.

Every question states what a complete answer must contain.

The back and forth is never automated. The user drives every round.

## No session polls

A blocked session may leave one detached shell process watching for its
answer file. It spends no model turns. Bounded at eight hours.

That waiter is the one piece of state outside the files. It reads nothing and
moves nothing. Lose it and the answer file still stands.

Manual pull is always the fallback.

## The answer is advice

The asking session weighs it, then reports the resulting action.

It never reprints the answer. The user wrote it and already read it.
