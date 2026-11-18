# Protocol — Ending An Autonomous Drive

Up: [[autonomous-driving-protocols-MOC|Autonomous Driving Protocols]]

When the last plan of an autonomous drive ends.

## The steps, in order

1. **End each plan as a regular drive does.** [[protocol-ending-the-plan|Ending The Plan]]. Skill: `assistant-drive`.
2. **Over several teams, wait for every team's drive to end.** Each team's assistant ends its own, then hands me its stop. Skill: `autonomous-drive`.
3. **Mark the autonomous drive ended.** Skill: `autonomous-drive`.
4. **List the drive in your last turn.** What waits on me, what you ruled for me, by its wave, what finished, and what stopped. Skill: `autonomous-drive`.
5. **Hand me what waits first.** Your move is the first thing waiting on me: a ruling, or a team's stop. Your own stop comes once nothing waits. You never stop yourself. Skill: `autonomous-drive`.

## What reaches me

The list, whole, then the first thing waiting on me as your move. Your stop, once nothing waits.
