# The Behaviour Axioms

Up: [[behaviour-protocols-MOC|Behaviour Protocols]]

The floor every file in `.claude/` sits on. Every behaviour protocol points here.

## Cost

Choosing which skill to run is a tax, paid before any work.

Every boot load earns its place. What every session loads, every session pays.

A skill that does two things is two skills. One file beats three.

A skill never grows into a tree of ifs. A branch that grows becomes its own skill.

The bare command does my common case. A skill takes a small, closed set of words.

A change is heard, never polled. A write tells 1100, and an open page redraws.

A timer only rechecks what no file carries: a pane closing, a port going down.

A small fix never redesigns. It builds on what is proven.

## Reach

A skill stands alone. No router stands before it.

A thing two skills need moves to `lib/` when the second needs it.
One module defines it. Never a copy. Its docstring says what it holds, and why.

## Families

Every skill family sits on one digit, D.
Its router is `D-name`, its children `name-*`, its playbook folder `001D`.

A page is 1100's, never a family's.

The thinking family has no page.

Every family folder holds three pieces, named for the family: its MOC, `the-<family>-axioms.md`, and `<family>-protocols/` with its own MOC.
Other documents sit beside them.

A family's router does three things.
It reads its family's folder, and what picks a child. Every child it calls in that turn holds the folder's law.
It calls children in order, passing each what the last returned.
It keeps its family's state file, when it has one.
Any other work is a child's.

## Proof

The session proves it, never me. A fresh pane, Playwright, the transcript.

What a session can run, it runs. When only my hands can, it gives me an exact matrix.

A running session is never borrowed. A pane opened for a test closes when the test ends, with its record.

The session drives its test sessions itself, through `session-control`. I am never asked to.

## Order

A change starts from what I mean. The session clarifies until it understands.

It prototypes only what changes what I see. Otherwise it skips the prototype.

It clarifies again when a prototype or a discussion needs it.

It then summarizes what was agreed, and plans two steps: build, then test it whole, each with its skill.

A fix first reads its failure in its transcript or log. No test session runs before the build.

Testing is never mine to ask for. The plan always holds it.

A build moves in order: try it, write it, test it whole, wire it.

A page is tried first. Its tool draws a fixture file, alone, until I lock it.
It reuses what exists, and changes none of it.

The documents, skills and hooks are then written around what was tried.

One full run tests the whole.

Wiring comes last: only then does what running sessions use change.

## Writing

Editing means deleting. Read the whole file. Delete what nothing reads.
A comment describing changed behaviour is worse than none. An import nothing uses is a defect.

A permission rule never approves code that runs on the machine. A hook needs none, nor a tool a hook calls.
Never widen one. `Bash(python3 *)` allows every script on the machine.

Each folder in `.claude/state/` is named for what owns it. Nothing sits loose.

A folder in `.claude/` whose layout is ours stays flat until it passes nine files. Only then does it take subfolders. `.claude/skills/` is Claude Code's: one folder per skill. So is `.claude/agents/`: one file per agent a session sends, its model, effort and tools fixed in it. So is `.claude/mods/`: one plugin per mod.

Python 3 and its standard library, and two packages.

AppleScript writes the dock launcher. TypeScript writes a mod, and a mod only calls Python.
