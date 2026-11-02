# Running Locally

Up: [[the-map-MOC|The Map]]

How a port is derived, and how a session reaches another layer.

## A port is derived, never chosen

Every port is four digits, before the shift. Three things make it.

```
<folder><role><session>
    7      2      05    →  7205
```

Nothing is registered. No two sessions collide.

## The shift

While `.claude/state/ports/shift.json` holds a shift, these ports add it: `1100`, `1400`, each session's derived ports, and every port band 00's command names. 20000 moves `1100` to `21100`, and session 05's derived `7205` to `27205`.

It keeps this project clear of another project's ports on the same Mac.

`/00-sessions-dashboard flip` sets it, and clears it.

A project can fix its shift in `.claude/project.json`. `flip` then refuses.

A server started before a flip keeps the port it bound.

## Each server folder holds one first digit

Each folder under `code/` that runs a server holds one first digit.

A layer's is its vault folder's: the third digit of its vault number.

> **Stand-in.** This project's digits: each one, its vault folder, and what it is.

Digit `0` is unassigned.

## The role digit

| Digit | Role |
|---|---|
| `1` | Backend |
| `2` | Frontend |

Digit `0` is never a role. Nothing binds it.

> **Stand-in.** Any folder taking site digits in place of roles.

## The session digits

A session is two digits, `01` through `99`.

`/0-session-start` gives a session its digits. Without it, a session holds no ports.

`01` is my advisor's seat. `02` to `09` are my side sessions, for tests and quick work.

`10`, `20` … `90` are assistant seats. Each leads its ten: `10` leads `11` to `19`.

Past `09`, side sessions take the next free numbers, around every assistant's ten.

An assistant takes the lowest ten no session holds.

Only missions and helpers take a team's ten. A mission takes its team's number ending in its own, as [[the-assisting-axioms|The Assisting Axioms]] axiom 7 rules. A helper takes the lowest free one.

Every other launch takes a side number, whoever launches it.

> **Stand-in.** A session's port, from this project's digits.

## Band 00 is what `/00-sessions-dashboard` brings up

`/00-sessions-dashboard` starts every server `.claude/project.json` names, on band 00.

It runs the command `.claude/project.json` names, so I never type it.

Band 00 belongs to no session. It is mine, to look at what exists.

Every band runs the same commands, so a name matches every band's servers.

## Reaching another layer

A session's backend reaches every other layer on band 00.

> **Stand-in.** One backend's port, and the band-00 address it calls.

Every reach address comes from the environment.

The code never changes. Only the environment does.

## The behaviour band

Layer `1` is the behaviour layer. It holds band `00`, and each session's copy of a band-00 server: session 08 tries `1100` on `1108`.

`1100` is the one page server, `00-sessions-dashboard`'s. It draws every session's clarify, assistant, launch, handover and jury page itself.

## Blocked ports

Browsers, AirPlay and adb hold `4045`, `5000`, `5037`, `5060`, `5061`, `6000`, `7000`.

Each has `0` as its second digit. No derived port does.

## The database

> **Stand-in.** This project's database, when it has one: its port, and what writes to it.

## A port that answers is somebody working

Something already answering means another session has it.
