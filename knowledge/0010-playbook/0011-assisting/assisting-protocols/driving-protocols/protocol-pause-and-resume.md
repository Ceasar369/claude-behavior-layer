# Protocol — Pause And Resume

Up: [[driving-protocols-MOC|Driving Protocols]]

When I pause your drive, when it reaches a pause point, or when I resume it.

## The steps, in order

1. **"Pause the drive." pauses it.** I type it, or pause it on the whole plan. End the step you are on, then wait: nothing launches or stops. Skill: `1-assistant`.
   - A pause point I named in the plan pauses it too, once the drive reaches it: after a stage, after a mission, or before a team launches. End the step you are on, then tell me in one turn what finished, and where to look. Skill: `assistant-drive`.
2. **Hold still while paused.** Skill: `assistant-drive`.
3. **Stay my assistant.** My words reach you at once, and you answer as always. Skill: `1-assistant`.
4. **"Resume the drive." resumes it.** I type it, or resume it on the whole plan. Read each session's need, handle every finish that came while paused, then arm your wait again. Skills: `1-assistant` and `assistant-drive`.
5. **Let the scheduled launch go.** In a plan run in order, a stage that ended while paused closes now, and the next one fires: [[protocol-closing-a-stage|Closing A Stage]]. Skill: `1-assistant`.

## What reaches me

Nothing. While paused, the whole plan shows the drive paused.
