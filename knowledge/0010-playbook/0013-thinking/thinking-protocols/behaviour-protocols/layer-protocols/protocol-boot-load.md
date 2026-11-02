# Protocol — Boot Load

Up: [[layer-protocols-MOC|Layer Protocols]]

When the subject is what every session loads before its first word.

## The parts it touches

Behaviour. Every `CLAUDE.md` a session loads, every rule in `.claude/rules/`, each skill's description, the settings, auto-memory.

[[the-behaviour-axioms|The Behaviour Axioms]] hold the floor.

## The questions, in order

1. What loads today? Start a fresh session at the root, and read `/context`.
2. Where does each piece come from? The project, the user, the account, or a parent folder.
3. Does every session need it, on every turn?
4. Could it load only when a skill runs? Then it moves into that skill.
5. What did the change save? Measure again, in a fresh session.

## The lessons

- A description is menu text. The shortest line that still picks the right skill.
- The proof is a fresh session.
