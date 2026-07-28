# Own execution

Read this only after the DAG was presented and the user answered `Spawn now`.

## 1 — Record the plan

Write the execution plan to this session's folder (`sessions/<NNNN>-<slug>/`), tiers included.

## 2 — Spawn

- Pass each executor's approved tier as the spawn's `model`. It overrides the agent file. Omit it and the file's own model stands — never cheaper than approved, only dearer.
- Ensure the worktree exists before the first code write. `/1-build` creates it; if absent, run `/1-build` first. Never cut a second — a branch lives in one worktree.
- **Parallel executors SHARE the session worktree.** Never add agent-level `isolation: worktree`.
- Spawn independent executors in one message so they run concurrently.
- Resume a live agent via `SendMessage`, never a fresh spawn.

## 3 — Checkpoint at each phase boundary

Every finished agent has written its work summary to the session folder. Log "phase N done" to `00-session.md`.

Then gate the checkpoint, routed the same way as the spawn gate:
`AskUserQuestion` — Header `Checkpoint`; Question `Phase done — commit before the next agents?`; Options `Commit + continue` (runs `/8-ship` commit-only on the branch) / `Continue, no commit` / **Other = type mid-build steering**.

Steer before the next phase spawns.

## 4 — Human gate (work-phase, not stop)

Mark any phase whose output needs a manual check — UI, browser, device. After such a phase, pause and present the gate before the next phase spawns. Executors are single-shot and cannot gate on a human; the orchestration owns it.

## 5 — Verify after all phases complete

- Spawn a `researcher` for correctness and doc-vs-code.
- On auth, permissions, or data integrity: verify security on the merits.
- Evidence, never assertion. Never rubber-stamp. Code is ground truth for state, not for correctness.

## Things NOT to Do

- Never spawn before an explicit `Spawn now`.
- Never cut a second worktree for a branch that already has one.
- Never add `isolation: worktree` to a parallel executor.
- Never skip the checkpoint gate to keep momentum.
- Never let an executor gate on a human — it cannot.
- Never accept a claimed pass. Read the actual output.
