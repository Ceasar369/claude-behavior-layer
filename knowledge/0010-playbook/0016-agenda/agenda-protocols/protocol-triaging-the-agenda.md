# Protocol — Triaging the Agenda

Up: [[agenda-protocols-MOC|Agenda Protocols]]

When the subject is triaging my agenda: a topic's items, brought to me one at a time, simplest first, each ending one of five ways I rule.

## The parts it touches

Behaviour. My agenda, `.claude/state/agenda/`. Its `README.md` rules an item's take-down and its fold.

[[protocol-agenda|Agenda]] holds the questions every change to my agenda answers. This protocol adds the loop.

A ruling that changes what a person sees follows [[protocol-what-a-person-sees|What A Person Sees]].

`agenda-triage` runs each ending.

[[the-behaviour-axioms|The Behaviour Axioms]] hold the floor.

## The questions, in order

1. Which items are the topic's? Read the whole live agenda once. Take every item under the topic, as `agenda.py topics` lists them. An item waiting on one is taken too.
2. Which are left alone? An item a running session works, and an item on a running triage's agreed list. Each partial drive's topic, which `successor.py take --topic` records, names what its session works. A running triage writes its agreed list in `.claude/state/sessions/<the triage's number>/triage.md`. Each shows on the list, marked. A session that stopped holds nothing, whatever its list said.
3. Do I agree the list? It is the first ruling, before any item. Agreed, I may ask to split it across sessions.
4. Which item comes next? The simplest to settle: a behaviour item, a small fix, an item a bigger item holds, a stale item. Large items, and items only my hands can do, come last.
5. What does it hold? Read its note, and the files its note names, before bringing it.
   - Explain the item whole, in plain words, layer by layer.
   - Its decisions come as clarify items, five a round. Mine is what changes the use I want, or touches my standards. Anything else, the session decides and names.
6. How does it reach me? One item per turn, its case shaped as `talking.md` shapes a decision's.
7. How does it end? One of five. I rule which, live or through the lessons below.
   - Take it down, as the README says.
   - Fold it into another item, as the README says.
   - Act now. A fix session self-drives it. The ruling names its account, model and effort. Partially drive it on its item, through `session-control`: this protocol is my ask. Its work done, propose its take-down. A look I can't picture yet is prototyped first, at Compare, then stop. The item takes a Mine line naming the lock-in.
   - Keep it. Say in one line what it waits on. An item I want to think through first stays, its What a Decide, for a session of its own.
   - Mine. It stays, with its Mine line.
8. How does it close? Once I say close, nothing new starts: no item, no drawing, no round. Fixes already running finish. Then `session-report`, its Agreed listing every item's ending in my words, and the triage stops.

## The lessons

- An item's turn says what exists today, in plain words. An act-now proposal also says what its fix session will do, step by step, and what I gain.
- With me in the triage, a running fix holds the next item. Once it closes, ask me before the next.
- Driven while I'm away, only a fix whose files meet a running fix's waits. A ruling or a drawing never waits.
- Driven while I'm away: an item only I can act on or rule stays up, as Mine. A fix that changes how a screen looks waits for my eye. A small, clear fix runs now, checked on disk before its item comes down.
