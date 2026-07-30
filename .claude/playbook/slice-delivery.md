# Slice Delivery

Delivering one phase against a plan that is already designed.

**Trigger** — the build gate named the shape slice.

**Done** — every officially-works claim is verified, and the cold audit is clean.

A slice invents no new machinery. The plan tree holds the spec.
Each step file states what officially works when done.

## The six steps

1. Claim the next open phase from the frontier.
2. Build by phase. One branch, one worktree, disjoint executor files.
3. Integration smokes run at each phase exit. Never batch them to the end.
4. Walk each named human gate.
5. Verify every officially-works claim, doc against code.
6. Cold audit. A slice is always consequential.
