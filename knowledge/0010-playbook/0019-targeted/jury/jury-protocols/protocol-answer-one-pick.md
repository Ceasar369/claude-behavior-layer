# Protocol — Answer One Pick

Up: [[jury-protocols-MOC|Jury Protocols]]

When the answer is one pick, most often whether a claim holds against its source.

## The parts it touches

`.claude/tools/jury.py`: the picks, the jury sessions, and the lines a juror answers in.

[[the-jury-axioms|The Jury Axioms]] hold the floor.

## What a juror gets and returns

It gets the context, the question, and one claim. It is told the claim's source, unless its session finds its own.

It returns one pick, its reason, and its quote with its place.

## The questions, in order

1. What are the claims? Each is one fact, in the words' own wording, in their order.
2. Which source does each claim name? Else the file it is about. None found leaves it empty.
3. Does every counted answer agree? Apart, the claim is checked again, then shown split.
