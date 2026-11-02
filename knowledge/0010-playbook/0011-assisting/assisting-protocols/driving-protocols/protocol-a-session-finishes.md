# Protocol — A Session Finishes

Up: [[driving-protocols-MOC|Driving Protocols]]

When a session you drive answers, asks, or stops working.

## The steps, in order

1. **Read each session's need.** Skill: `1-assistant`.
2. **Give every answer it needs, and send it yourself.** My clarify items are no blocker: you answer them. Skill: `assistant-answer` writes it, and `session-control` sends it.
3. **Only a real blocker stops you.** `.claude/rules/thinking.md` lists every stop, under "Finish what was asked". Bring me what blocks you: [[protocol-stuck|Stuck]]. Skill: `session-control`.
4. **Check it.** Skill: `assistant-check`, then `session-control`.
5. **Keep its work.** Copy the session's folder, without its screenshots, and its transcript, into your folder. One folder per mission, so a number used again never overwrites one. Skill: `session-control`.
6. **Stop it.** Skill: `session-control`.
7. **Capped: wait for its reset.** When the capped account is your own, "Resume the drive." is typed into you at the reset, and you go on from step 1. A drive I paused stays paused. Skill: `session-control`.
8. **Error: three tries, each after a pause.** Skill: `session-control`.
9. **Blocked: type nothing into it.** A permission prompt or a dialog holds it, and a Return there picks option 1. Only my hand answers it. Bring it to me: [[protocol-stuck|Stuck]]. Skill: `1-assistant`.
10. **Gone: keep its work, then bring it to me.** Skill: `session-control`.
11. **Past System's threshold: hand it over, and answer at once.** [[protocol-handing-over-what-you-drive|Handing Over What You Drive]]. Skill: `session-control`.
12. **Move on.** Every session of a stage stopped, in a plan run in order → [[protocol-closing-a-stage|Closing A Stage]]. A mission I ruled waits for a seat → launch it now. Every session of a drive of one session or one stage stopped → [[protocol-ending-the-plan|Ending The Plan]]. Otherwise, arm your wait again: [[protocol-hearing-me-mid-drive|Hearing Me Mid-Drive]], step 3. Skill: `assistant-drive`.

## What reaches me

Only what reaches me through [[protocol-stuck|Stuck]]. You settle everything else, and every other session goes on.
