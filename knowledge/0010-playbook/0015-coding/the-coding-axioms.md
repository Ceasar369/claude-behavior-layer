# The Coding Axioms

Up: [[coding-MOC|Coding]]

What a session always respects when it codes, on top of `.claude/rules/`.

## 1. Code is written with Write and Edit

The shell only copies, moves and deletes files.

Write and Edit refuse a file not read first. A heredoc or `sed -i` writes blind, in a tree several sessions write at once.

## 2. Band 00 runs the working tree

A save that breaks a layer breaks it for every session.

A session may start or restart band 00 when its work needs it, without abusing it.

A booted session derives its own ports and starts its own servers. [[running-locally|Running Locally]] states how a port is derived.

It stops each by its own port or pid, never by a name pattern.

A session binds its derived port, and no other.

No server falls back to a spare port or band.

A port that will not bind is a failing step.

A session may point one reach address at its own band.

## 3. A build another session broke holds only the gate step

It runs again, after a pause. The rest of the work goes on.

## 4. The vault and the docs take proposals

A line either should hold, outside the session's folder, goes into its report as a proposal.

## 5. Tests, builds and type checks start under `taskpolicy -b`

The type check runs as `taskpolicy -b` and its command, never its command alone.

A test run starts one worker per core, and slows every session's typing until it ends.

## 6. A session works in one layer's folder

> **Stand-in.** One of this project's layers, and the one folder under `code/` its session touches.

They never open the same file.

## 7. A comment agrees with what it comments on, and is written well

It says what the vault, the code and the pages actually say and do.

It is never verbose, and needs the least maintenance possible.

## 8. A session runs the tests it changed, never a whole suite

While building, a session runs only the test files it changed, as [[the-tools|The Tools]] runs one.

Its type check, lint and build run once, at its end.

No session runs or recommends a whole suite.

## 9. A step that needs no browser may go to the cloud

Propose it as one item, through `cloud-step`.
