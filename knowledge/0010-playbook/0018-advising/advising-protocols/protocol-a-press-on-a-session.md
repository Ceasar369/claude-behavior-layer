# Protocol — A Press On A Session

Up: [[advising-protocols-MOC|Protocols]]

When Send on your Transcript tab's Advise panel, or my words, send you to a session.

## The steps, in order

1. **Know the session by its record.** Its title, account and mission, in `.claude/state/sessions/NN/record.json`. Never by its number alone: numbers are reused.
2. **Name its situation first.** The reply's first line names which situation below it is in.
3. **An open wave runs `assistant-answer`.** Its newest `.claude/state/sessions/NN/waves/wave-K.md` whose `sent:` is empty.
4. **Several sessions read in one turn get one reply.** A part each, under its number.

## The situations

One line each: how it shows, and the move it ends on.

- **A wave waits.** Its newest wave is not sent. Step 3.
- **Done, waiting to stop.** It says its work is finished. Run the second chore, then end on its stop.
- **I need to understand it.** Its newest turns explain work or a choice, and nothing new waits on me. An Answer, or a Wait.
- **Stuck or failing.** Errors, refused steps, failed proof, or a wait repeating. An Action to recover, or a Ruling on a repair.
- **A proposal to judge.** A plan or a prototype puts a choice to me. A Ruling on that choice.
- **Sessions to order.** Two sessions meet on a file, or one waits on another. A Ruling on who goes first, or a Wait.
- **A ruling asked in prose.** Its reply asks me to decide, with no wave open. A Ruling, or an Action with the exact words.
- **Waiting on work.** A helper, a command, a report or another session holds its next step. A Wait, naming who works and what ends it.
- **A walk asks me.** Its lead or its walker asks at a check. Follow [[protocol-a-walk-asks-me|A Walk Asks Me]].
- **Finished work to check.** A result, a report or a research claim stands against its assignment and its proof. A Ruling, or an Action for a handoff.
- **My hands are needed.** A login, a phone step, a clipboard, a dashboard press or an email remains. An Action naming its place, its control and its order.
- **Every session at once.** I ask about several sessions. One Action, sessions waiting on me first.
- **A page disagrees with its session.** A tab, a colour or a receipt differs from its transcript. A Ruling, or an Action.
- **An answer only I hold.** It lacks a fact about me, a requirement, or an outside answer. An Answer.
