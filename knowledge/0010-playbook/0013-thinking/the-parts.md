# The Parts

Up: [[thinking-MOC|Thinking]]

Which parts there are: what one change can touch.

## A part is one server, or one place nothing runs

Every server `.claude/project.json` lists is one part.

Its two digits name it. `32` is the app's frontend, in `code/app/frontend/`.

A part carries its layer's vault folder. `0030-app` goes with both 31 and 32.

> **Stand-in.** This project's parts that run nowhere, beside Behaviour, one line each.

- **Behaviour.** The root's `CLAUDE.md`, `.claude/`, and `knowledge/0010-playbook/` except `0015-coding/the-stack/`.

Nothing is smaller than a part.

## A prototype subject is a part

Each subject in `code/prototypes/` is one part, named by the subject.

`prototypes · <subject>` is `code/prototypes/<subject>/` and `code/prototypes/src/routes/<subject>/`.

Two subjects never share a file. The app they share, and its port, belong to no part.

## A call belongs to the part that answers it

Sign-up's frontend calls a backend route. The route is thought through in 31, once.

32 only uses it.
