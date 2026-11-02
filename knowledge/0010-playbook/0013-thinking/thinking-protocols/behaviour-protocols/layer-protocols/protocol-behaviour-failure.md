# Protocol — Behaviour Failure

Up: [[layer-protocols-MOC|Layer Protocols]]

When the subject is a skill or hook that failed when it ran.

## The parts it touches

Behaviour. `skill-creator` holds the contract every skill and its hook honours. `.claude/lib/hook.py` holds a hook's with no skill.

[[the-behaviour-axioms|The Behaviour Axioms]] hold the floor.

## The questions, in order

1. Where did it fail? Read the transcript at that exact call.
2. Which event did that call raise? Which event does the hook answer?
3. Which path do sessions already take? The fix serves that path.
4. Does a throwaway project in `/tmp` prove the fix?
5. Which vault lines stop being true?

## The lessons

- Read the transcript before any code.
- Prove the fix before asking for a ruling.
