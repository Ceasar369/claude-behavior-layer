# Pillar Design

The seven-step pipeline that takes an undesigned subsystem to shipped.

**Trigger** — the build gate named the shape pillar. Nothing designs this yet.

**Done** — verify passes, the distillation is in the docs, and the ship gate opens.

Only for a genuinely undesigned subsystem. Feature delivery is a slice.
A pillar invents no new machinery. It reuses the existing skills and agents.

**Adapt this before adopting it.** It assumes a client/server split behind a
versioned contract, and several host contexts sharing one bundle. One service
with no client collapses to steps 1, 2, 6 and 7.

## Where the documents live

Every pillar document sits in one folder, inside the session folder.

`<NNNN>-<slug>/<pillar-slug>/` — named for the pillar, never the step.

The step number prefixes the file. Four primary documents.

- `1-macro.md`
- `2-contract.md`
- `3-client-book.md`
- `4-micro.md`

A step may add lettered supplements: `4a-state-model.md`. One topic each.
Never a fifth primary document.

Steps 5 through 7 produce code and baselines. No document.

The session's own files stay flat, with their own numbering.
Pillar numbering never touches them.

## The documents are scaffolding

Closing the session deletes the folder. Every pillar document dies with it.

`docs/` receives one distillation, written before the close. The macro and
the locked contract are what the docs keep.

## The seven steps

| Step | What it answers | Gate |
|---|---|---|
| 1 · Macro | What this is, and how big | The user reviews the macro |
| 2 · Contract | The shape, spec-first | The user reviews the draft |
| 3 · Prototype | What is missing | A round surfaces nothing new |
| 4 · Micro | How, and prove it | The user reviews; the contract locks |
| 5 · Component book | How it looks | Visual and accessibility pass |
| 6 · Build | Both sides, to the contract | Each side verified on the merits |
| 7 · Verify | Does it hold | Verify passes, then the ship gate |

A server-only pillar skips prototype, the component book, and the host steps.

## Rigor calibration

Every macro carries a rigor value: light, standard, or full.

Set once, at macro time. Every later step reads it.

Justify it on four axes. Each yes adds weight.

| Axis | Question |
|---|---|
| Novelty | No prior pillar covers this pattern? |
| Regulatory | Touches personal data, or law? |
| Agent count | Three or more agents in the build? |
| Reversibility | Hard to undo in production? |

- **Light** — read-only interface, no regulatory exposure, one agent, reversible.
- **Standard** — one or two axes. Full spec.
- **Full** — anything correctness-critical, or three or more axes. Deep verify.

Auth and permissions always get full. Rigor scales depth, never skipping a step.

## 2 · Contract

The contract is the seam between the two sides. Both build against it, in
parallel. Tests prove conformance.

A pillar declares whichever contracts it touches. Mark the rest not applicable.

- **The API** — the request and response shape.
- **Events** — what this pillar emits to subscribers.
- **The embed protocol** — the handshake and shared types, when a host embeds it.

### Standing contract rules

- Versioned together. Consumers pin a version.
- Cross-origin messaging uses a strict origin allowlist. Never a wildcard.
- Emitted events are signed, retried, and versioned.
- Exact quantities are integers in their smallest unit. Never floats.
- Idempotency keys are declared end to end, from day one.
- Route-out flows carry no token in the URL.
- Every user-facing surface ships in every supported locale.

The draft is enough to prototype and to start both sides.
The prototype exposes what it is missing. It locks at the micro.

## 3 · Prototype

A discovery loop, not a deliverable. Build the thinnest walkthrough that
exercises the contract end to end, and record only what it revealed.

Run rounds until one surfaces nothing new. Completeness is the bar here.
Appearance is the component book's job.

Classify every gap it finds: missing from the contract, missing from the macro,
or a genuine redesign. The third one stops and re-gates.

## 5 · Component book

Each component in isolation, to production grade. All states, every supported
locale. A committed visual baseline per component. An accessibility pass with
no violations. Design tokens drive theming.

One canonical home per component. One file. No exceptions.

## 6 · Build — one host at a time, pausable

The server builds to the locked contract. Nothing invented beyond it.
Correctness-critical code is maximal, never minimal.

The client assembles the component-book atoms into the flow.

One bundle serves every host context. Each is a complete, shippable
increment. Pause or ship between them. The order is the user's.

## 7 · Verify

Two depths: hard is a behavioral walk plus a visual snapshot; light is
a smoke test. The primary hosts get hard. Secondary ones get light.

Two tiers: browser-grade first, then a real device where one applies.

Test order: component visuals, the flow on mocks, the flow on the real API,
the primary host hard, each embedded host hard, a smoke test on the rest.

### The three checks

- **Function** — the done-signal walks pass.
- **Fidelity** — the code matches the macro's intent.
- **Safety** — security verified on the merits for auth and permissions.

### Correctness assertions

For any action that must not double-apply, assert three layers.

- The interface shows the exact value.
- One network call on replay, with the idempotency key present.
- The store holds exactly one record. No duplicate on replay.

Verify passes before any ship gate opens. The ship gate is the user's
choice, never automatic.

## The design queue

Pillars are designed in a decided order. A new undesigned subsystem
joins the queue by decision, never by drift.

The feature frontier is separate. It lives with the plan, not here.
