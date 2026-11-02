# Protocol — Hearing Me Mid-Drive

Up: [[driving-protocols-MOC|Driving Protocols]]

When you wait between finishes, and a finish or my words arrive.

## The steps, in order

1. **Wait idle, never inside a turn.** Skill: `session-control`.
2. **A finish wakes you.** Any kind ends the wait: done, asking, capped, an error, blocked or gone. Claude Code then starts your turn. Follow [[protocol-a-session-finishes|A Session Finishes]]. Skill: `session-control`.
3. **Arm the wait again.** Skill: `session-control`.
4. **My words reach you at once.** Skill: `1-assistant`.
5. **A session joining the drive joins the wait.** Skill: `session-control`.

## What reaches me

Nothing, between finishes. While your wait runs and your last move asks me nothing, you read green, as working. A move asking me anything turns you red, wait or not. This holds for every session waiting in the background, on every page and every card.
