# Protocol — Answer Yes Or No

Up: [[jury-protocols-MOC|Jury Protocols]]

When the answer is yes or no.

## The parts it touches

`.claude/tools/jury.py`: the jury sessions, and the lines a juror answers in.

[[the-jury-axioms|The Jury Axioms]] hold the floor.

## What a juror gets and returns

It gets the context and one question. A question asked of several things gets one juror per thing, each a claim.

It returns yes, no or can't tell, its reason, and its quote with its place.

## The questions, in order

1. Is it one question, answered yes or no? Two questions are two juries.
2. Does every counted answer agree? Apart, it is asked again, then shown split.
