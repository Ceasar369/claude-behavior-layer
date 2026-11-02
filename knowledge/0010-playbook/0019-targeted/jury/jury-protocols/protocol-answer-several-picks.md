# Protocol — Answer Several Picks

Up: [[jury-protocols-MOC|Jury Protocols]]

When the answer is every pick that applies, among named options.

## The parts it touches

`.claude/tools/jury.py`: the jury sessions, and the lines a juror answers in.

[[the-jury-axioms|The Jury Axioms]] hold the floor.

## What a juror gets and returns

It gets the context, one question, and the options.

It returns every option that applies, or can't tell, its reason, and its quote with its place.

## The questions, in order

1. Are the options a known set? A file names them, or I do.
2. Does every counted answer name the same picks? Apart, it is asked again, then shown split.
