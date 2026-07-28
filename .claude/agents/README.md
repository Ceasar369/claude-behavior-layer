# Agents Index

Every agent is one file: `.claude/agents/<name>.md`. Read the existing ones before
writing a new one.

The roster is the write-fence map. Each writer agent maps to one hook-fenced
directory — that is what makes an agent a separate agent, not its topic.

**Executors are for scale, never for permission.** The session may write code in the
worktree itself. Delegate for parallelism, for scope one context cannot hold, or for
isolation with an independent verifier. Never because code needs an agent — it does not.

Nobody writes the primary code checkout. `guard-infra.sh` blocks it session-wide.

| Agent | Writes | Fence |
|---|---|---|
| `backend-executor` | `.worktrees/<branch>/` minus `frontend/`, plus `sessions/` | `guard-write.sh backend-executor` |
| `frontend-executor` | `.worktrees/<branch>/` minus `backend/`, plus `sessions/` | `guard-write.sh frontend-executor` |
| `researcher` | nothing | `Read, Glob, Grep` only |
| `web-researcher` | nothing | tools only |

The `sessions/` allowance is the executor's own work summary, and nothing else.
The documentation is never an executor's to write. A researcher analyses the deltas;
the session writes them.

Shipping is not an agent. `/8-ship` runs git in the session the user is watching.

## Adding or renaming a lane

The two executor lanes are `backend/` and `frontend/` — directory names inside the
worktree, not stack names. To rename them, or to add a third:

1. Add or rename the `case` branch in `.claude/hooks/guard-write.sh`.
2. Add or rename the agent file, including its own `guard-write.sh <name>` hook.
3. Update the table above.

All three change together. A lane in the table with no `case` branch has no fence;
a `case` branch with no table row is invisible to whoever staffs the work.

## The Agent Standard

### Frontmatter

**Required:**
- `name` — lowercase, hyphens only, ≤64 chars. Cannot contain "anthropic" or "claude".
- `description` — the delegation trigger: WHEN to use this agent, AND the anti-case.
  Third person, ≤1024 characters. **This is a character cap, not the 40-word cap that
  governs skills.**
- `tools` — explicit minimal allowlist. Never a wildcard. Only what the agent exercises.

**Model:**
- `sonnet` — the default. Write it unless there is a reason not to.
- `haiku` — purely mechanical work only: format, rename, sort, count. Never an
  irreversible action.
- Always write the field. Omitting it inherits the caller's model — a silent tier.
- **Executors are tiered per spawn** by `plan-agents`. Their frontmatter names the
  dearest tier they take, so a forgotten tier costs tokens, never correctness.

**Other fields:**
- `permissionMode: acceptEdits` — an agent holding `Write` or `Edit`.
- `permissionMode: default` — everything else. This includes an agent that writes only
  through `Bash`: `acceptEdits` governs `Write` and `Edit` prompts and nothing else, so
  it would be inert.
- `maxTurns` — set it on open-ended explorers. Count the worst-case tool calls first;
  leave real headroom for retries and the return.
- `memory` — never set it. Memory is disabled layer-wide; `guard-memory.sh` blocks
  every memory write.
- `hooks` — a write-capable agent declares `guard-write.sh <its own name>` on
  `Write|Edit|MultiEdit`. **An agent that does not declare it has no write fence.**

### Why some hooks are declared twice

`guard-destructive.sh` is registered in `settings.json` AND redeclared in each
executor's frontmatter. That is deliberate, and it is not the same as `guard-write.sh`.

`guard-write.sh` takes the agent's identity as `$1`, from the agent's own declaration.
It cannot be registered session-wide, because session-wide has no agent name to pass —
and the name is never read from stdin, since those fields are unreliable in a
`PreToolUse` hook. So each agent declares its own, and that declaration IS the fence.

`guard-destructive.sh` takes no argument, so both registrations are identical in
effect. It is declared twice because the two registrations cover different callers,
and neither covers both: the session-wide one covers `/8-ship` running git in the main
session, and the frontmatter one is the agent's own guarantee, independent of whatever
`settings.json` happens to say. A guard you can lose by editing one file is not a guard.

Duplicating a no-argument guard costs one extra process per call. Losing it costs a
repository.

### Body structure

1. **Role** — one imperative sentence.
2. **Where you operate** — every directory listed. For code: the worktree at
   `.worktrees/<branch>/`, never the primary checkout — that stays pristine on the
   integration branch and `guard-write.sh` blocks writes to it.
3. **Read first** — the exact paths to read before acting. Point at an index and let
   the agent follow it; never restate an index inline.
4. **How you work** — single-shot: read everything, act, return. Sentences ≤10 words.
   Verify before claiming done. Evidence over assertion — return the command and its
   output, never "it passed." Never ask mid-task; make the reasonable call and continue.
5. **Truth over agreement** — an agent that reviews or returns findings judges on the
   merits. Never rubber-stamp the spawning prompt's framing or a green result. Code is
   ground truth for state, not for correctness.
6. **Return format** — structured. What it reports, in what shape.
7. **Things NOT to do** — one line each.

**Cap: 200 lines.**

### Hard rules

- No wildcard in `tools`.
- No path that needs an unstated working directory. Repo-root-relative is fine —
  `docs/…`, `sessions/…`. A worktree path names its branch, because the branch varies.
- Never set `memory`.
- **A subagent cannot gate.** There is no user inside it. Never couple an agent to a
  skill that gates — the spawning session pre-decides and passes the answer in the prompt.
- **Never require the user's own message.** An executor hears only the spawning session;
  that relayed go IS the authorized channel. Demanding the user's direct words deadlocks
  the agent.
- An agent never spawns another agent. Orchestration stays in the main session.
