---
name: plan-agents
description: Staffs any scope into an agent DAG — units, parallel or sequential, which agent, which model tier, a prompt each. Renders it, or owns execution. It never decides whether the work is worth doing.
argument-hint: "[the scope] — a plan, a named target, or just \"delegate this\""
allowed-tools: Read, Glob, Write, Edit, AskUserQuestion, Agent, Skill, SendMessage
---

# Plan Agents

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Turn any scope into a correct agent DAG: units, parallel/sequential, agents, tiers, a prompt each, verification.

## Inputs

Take a scope from anywhere — `7-provide-prompt`, an audit loop, plan mode, or the user saying "delegate this to agents." There is no approved-caller list. Whatever arrives is the scope.

When the caller already named the units and the parallel/sequential split, consume it. Never re-decompose.

## Know the live roster — read it every run

Never assume which agents exist. Glob `.claude/agents/*.md` and read frontmatter. Skip any file with no `name:` field — `README.md` is the Agent Standard, not an agent. Staff only real agents.

## Step 0 — Should this be delegated at all?

Answer before staffing anything. Executors are for scale, never for permission.

The session may write code in the worktree itself. So delegation must earn its cost — an agent rebuilds context the session already holds.

**Say so and stop** when the work fits one context and one pass: a few coupled files, a bounded change, verifiable in one go. Name it as the session's own work. Staff nothing.

**Staff it** when any one holds:
- The work splits into genuinely parallel units. Two agents run at once.
- The scope exceeds what one context holds.
- The work wants isolation and an independent verifier.

The user asked for staffing explicitly → staff it, and say plainly if you would have done it inline.

## Step 1 — Ground (when code is involved)

For build or code-touching work, spawn a `researcher` to verify the scope against the CURRENT code and docs: read the exact files and governing docs, surface conflicts, return grounding paths and deltas. Code and docs outrank the scope. For pure research staffing, skip this.

## Step 2 — Decompose into units

Break the work into the smallest real units. Tag each **parallel** or **sequential**, one-line reason:
- Sequential — needs another unit's output, or touches the same files.
- Parallel — fully independent: different files or areas, no shared state.

Order by dependency: schema before the code that reads it, the API before its client, a migration verified before the next unit builds on it.

**Disjoint files are necessary, never sufficient.** Parallel executors share one worktree, so check for couplings that are not files anyone writes: concurrent builds racing on the same output directory, `git` index lock contention, dev-server port conflicts, and one agent holding a stale view after another's write. Sequence anything that collides on those.

## Step 3 — Assign agents (units ≠ agents)

- Coupled units (shared files, sequential dependency) → one agent, one responsibility.
- Independent units (disjoint files, no shared build or port) → parallel agents.
- After a fan-out, the orchestrating session merges the parallel outputs itself — inline, never a spawned agent. No builder integrates another builder's output.

**Avoid the God Agent.** Split at the concern boundary, not the file boundary. Three levers, in order:
1. **Single-responsibility ceiling** — one concern per agent.
2. **Independence seam** — parallelize only genuinely disjoint work; never split a coupled sequential chain just to shrink it.
3. **Incremental phasing** — if one concern is still too large, phase it: one feature at a time.

**Split test** per proposed agent: verifiable in isolation? would one failure cascade? Disjoint → parallel; coupled and sequential → keep together, phase if large. The signal is "single concern, verifiable in isolation" — never a file count.

Verification is a separate control (Step 5). Right-sizing the build never removes the verifier.

**Set each executor's model tier** — the model rides the spawn, never the agent file. An agent without a tier is not yet assigned.
- `sonnet` — the default. Known pattern, bounded change, an existing shape to follow.
- `opus` — the unit touches auth, permissions, data integrity, or anything irreversible. Or the design is novel with no pattern to follow.
- **Unsure → `opus`.**
- Researchers are never tiered here — their agent file fixes their model.
- Treat this tier as the opening bid. The Step 5 gate sets the verdict.

## Step 4 — Per-agent prompt

Each agent gets five parts plus two blocks:
- **Purpose** — one imperative line.
- **Context** — 2–3 grounding sentences.
- **Read first** — the exact paths the agent reads before acting. Name the docs that govern this change, not the whole tree. Point at an index and let the agent follow it; never restate an index inline.
- **Target paths** — the exact absolute path prefixes the agent may write.
- **Steps / Things to do / Things NOT to do.**
- **Update after** — for an executor: write its work summary into the session folder and flag doc-sync; never sync the docs inline.
- **Verification** — the SPECIFIC tests for its changed files. Not "run the suite." Full suite only for broad, shared, migration, or security changes. "No tests needed" only when no behavior changed — never on auth, permissions, or data integrity.

## Step 5 — Render, or own execution

**Decide the mode from the scope, before presenting.** Three tests, in order:

1. The scope says not to build — "just staff it", "do not spawn", "show me the DAG" → **render only**.
2. The scope is hypothetical, invented, or a test → **render only**.
3. Otherwise, and the user is present and ready → **you own execution**.

Unsure → render only. Presenting costs a turn. Spawning writes code.

**Render only** → present the staffed DAG and stop. No gate — a gate offering `Spawn now` contradicts the mode. Say plainly that nothing will spawn.

**You own execution** → present the DAG, gate it, then follow `own-execution.md` beside this file.

Present the DAG in full before any spawn: each agent, its job, its **model tier** with a one-line reason, which run **parallel** vs **sequential** with a one-line reason, the order, the branch, and each agent's scoped tests. An executor shown without a tier is a malformed DAG — fix it before gating. Never skip this display, even when the build was already approved.

Gate the spawn — owning execution only:
`AskUserQuestion` — Header `Spawn`; `Spawn now` (recommended) / `Adjust first` / `Don't spawn`.
- No spawn until an explicit `Spawn now`.

## Things NOT to Do

- Never decide whether the work is worth doing. That is the user's. You decide only whether it needs agents.
- Never staff work that fits one pass. Say so and stop.
- Never re-decompose a split the caller already made.
- Never put two agents on the same files at once.
- Never parallelize units that collide on a build directory, the `git` index, or a port.
- Never collapse concerns into a God Agent, nor split a coupled sequential chain just to shrink it.
- Never let splitting replace the verification agent — two controls, not a trade.
- Never spawn a builder before an explicit, DAG-level approval. A prior build-level "go" does not count. Never spawn at all in render-only mode.
- Never gate in render-only mode. Offering `Spawn now` there contradicts the mode.
- Never skip the DAG display, even when the build was pre-approved.
- Never tier an auth, permissions, or data-integrity unit to `sonnet` to save budget.
- Never skip tests on those same paths.
- Never let a spawned agent integrate another agent's output.

## Output

- **Render only:** the staffed DAG — units, parallel/sequential, agents, tiers, per-agent prompts, scoped tests. Then the turn ends.
- **Owning execution:** the DAG presented and gated, then executed per `own-execution.md`.

## Files

- `own-execution.md` — the spawn, checkpoint, human-gate, and verify procedure. Read it only when owning execution.
