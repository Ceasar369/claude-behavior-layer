import type { Register } from 'claude-code'

// A zero-turn skill is all hook: its settings hook does the work and answers
// a session's own Skill call by refusing it, its one line the reason, so
// the skill's body never loads. That refusal comes back as an errored
// result, "PreToolUse:Skill hook error: <line>", even when the work
// succeeded. This lets the settings hook run as before, then hands its line
// back as the call's result. 9-session-stop stays out: its answer also ends
// the turn.
//
// Claude Code runs an installed copy, one per account. A change here lands
// once plugin.json's version rises and each account runs
// `claude plugin update zero-turn@layer-mods`.
const ZERO_TURN = new Set([
  '0-session-start', '00-sessions-dashboard', '8-ship',
  'handover-prepare', 'handover-resume', 'prototype-continue', 'prototype-remove',
  'prototype-save', 'reaper',
])
const REFUSED = /^PreToolUse:Skill hook error:\s*([\s\S]*)$/

export const register: Register = on => {
  on('tool.call', { tool: 'Skill' }, async ($, e, next) => {
    if (!ZERO_TURN.has(e.skill)) return next(e)
    const ran = await next(e)
    const line = ran.isError === true && typeof ran.text === 'string' ? REFUSED.exec(ran.text) : null
    if (!line) return ran
    return {
      result: { success: true, commandName: e.skill, status: 'forked', agentId: 'hook', result: line[1] },
    }
  })
}
