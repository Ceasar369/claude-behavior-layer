# Protocol — Handing Over What You Drive

Up: [[driving-protocols-MOC|Driving Protocols]]

When a session you drive passes System's handover threshold.

## The steps, in order

1. **Read each session you drive after each moment.** Its context against System's handover threshold, the same % its Handover page reads. Skill: `session-control`.
2. **Past the threshold, decide as if no handover came.** Skill: `session-control`.
3. **Otherwise, hand it over and answer at once.** The handover runs in the background, on the account saved for that handover, else the order's next, and the model and effort its seat was named, else System's. Skill: `session-control`.
4. **Its successor reads the copies, then ends its turn.** Skill: `session-control`.
5. **Past the wrap-up threshold, a working session wraps up.** A hook tells it so, after each tool call. `.claude/rules/thinking.md` lists every stop, under "Finish what was asked". Its finish comes to you. Skill: none, the hook.
6. **A full window is a finish too.** Skill: `session-control`.
7. **A failed handover leaves it in its seat.**

## Held throughout

Whoever drives a session hands it over. A driver nobody drives hands itself over: [[protocol-handing-itself-over|Handing Itself Over]].

A session you drive gets no Handover page.

A session whose driver is capped waits for the driver's reset.

## What reaches me

Nothing. Only a failed handover, through [[protocol-stuck|Stuck]].
