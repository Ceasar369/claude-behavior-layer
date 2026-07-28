---
name: challenge
description: Stress-tests an idea, plan, or standing rule by running it past independent agents with deliberately opposed starting stances. Use when the user says "challenge this" or runs /challenge. Read-only.
argument-hint: "[what to challenge] — plus any worries you already have"
allowed-tools: Read, Agent, SendMessage, AskUserQuestion
---

# Challenge

## Anchor

Follow the root `CLAUDE.md`. Truth over agreement.
Read-only. Never write production code or documentation.

## Purpose

Stress-test a conclusion from opposed stances, then report the spread.

## Steps

1. **Absorb the target.** Pin down exactly what is being challenged. Live in the chat → restate it in one tight block. A document → read it. Capture the user's worries verbatim. They are seed angles, never the set.

2. **Build the angle list.** Take their angles, then add the ones they did not name. Push wide: what does it assume, what already exists that kills it, what a hostile expert says, what breaks at scale or under law. Include the premortem angle every time — "assume this failed in six months; why?" Name each angle and its route: code / docs / web / logic / analogy. Compare every target against every route; never narrow the routes by target type.

3. **Assign a stance to every spawn.** Each agent gets exactly one: `IN FAVOUR`, `NEUTRAL`, or `AGAINST`. Cover all three across the set. Never run one stance alone.

4. **Gate the fan-out.** `AskUserQuestion` — Header `Challenge`; Question `Run these <N> angles?`; Options `Run them` (recommended) / `Add angles` / `Redirect`.
   - No spawn until an explicit yes.

5. **Fan out — uncapped, parallel.** One agent per angle. Pick by route:
   - External fact, vendor, tool, regulation, precedent → `web-researcher`.
   - Current code, documentation, what already exists → `researcher`.
   - Pure logic and assumption-breaking → reason in-session, no agent.
   Run independent spawns in parallel. Resume a live agent with `SendMessage`, never a fresh spawn.

6. **Isolate every spawn's context.** Pass exactly three things: the claim, the route, the assigned stance. Never pass the session's own position, the user's preference, which option they favour, or another agent's findings.

7. **Let an agent find nothing.** No quota. An agent with no finding reports none. Never require a concern per agent.

8. **Report by stance.** Group findings under `IN FAVOUR` / `NEUTRAL` / `AGAINST`. Never average them into one verdict. Name every convergence:
   - An `AGAINST` agent that concedes the point → the strongest evidence available. Say so.
   - An `IN FAVOUR` agent that finds a problem anyway → equally strong. Say so.
   - All three stances agreeing → report it as convergence, never as proof.

9. **Classify every finding.** Use these three and nothing else:
   - **Broke** — a specific failure case, traced to real code, a real doc, or a cited external fact. Name the case.
   - **Held** — attacked on that angle and survived. Say what was attacked.
   - **Uncertain** — the angle is real, the evidence is missing. Name what evidence would settle it.

10. **State your own position, labelled as your own.** Keep it separate from the agents' spread. The user decides what survives.

## Things NOT to Do

- Never assert a contradiction you have not verified against the real code or doc.
- Never spawn an executor. `researcher` and `web-researcher` only.
- Never write production code or documentation.
- Never run a single stance. Cover all three.
- Never tell a spawn what the session or the user already believes.
- Never average the stances into one verdict.
- Never soften a finding to agree. Never invent one to look thorough.
- Never call a finding "broke" without naming the failure case.

## Output

- The angle list — the user's worries plus the ones they missed, each with its route and stance.
- Findings grouped by stance, each classified broke / held / uncertain.
- Every convergence named.
- Your own position, labelled as your own. The user decides what survives.
