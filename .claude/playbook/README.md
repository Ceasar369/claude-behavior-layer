# The playbook

The layer's own method documents. How the work is run.

These are **not** your project's documentation. That is `docs/`, and this layer
never writes there.

## Why they live inside `.claude/`

`docs/` is yours. `paths.local.sh` can repoint `DOCS` anywhere — a sibling repo,
an external wiki, a folder outside the tree entirely. A skill that said "read the
Writing a Prompt document" would dangle the moment you did.

These ship with the layer instead, so every reference resolves on a fresh clone
with no configuration at all.

## What is here

| Document | What it holds | Who reads it |
|---|---|---|
| `ask-answer-bus.md` | The design behind the cross-window question bus. | `2-ask` |
| `writing-a-prompt.md` | How to pace work for a fresh session, with a worked example. | `7-provide-prompt` |
| `slice-delivery.md` | Delivering one phase against a plan already designed. | `1-build` |
| `pillar-design.md` | The seven-step pipeline for an undesigned subsystem. | `1-build` |
| `cold-audit.md` | How consequential work gets proved before it ships. | `7-provide-prompt` |
| `impact-check.md` | Tracing a change through everything that depends on it. | `CLAUDE.md` |
| `communication.md` | The depth behind the communication rules in `CLAUDE.md`. | `CLAUDE.md` |

## Adapting them

Every one is opinionated, and every one is yours to change. They describe a way
of working, not a constraint the scripts enforce — no hook reads them and no
script parses them.

Two are worth a look before you adopt them wholesale:

- **`pillar-design.md`** assumes a client/server split behind a versioned
  contract, and several host contexts sharing one bundle. If your project is one
  service with no client, most of it collapses to steps 1, 2, 6 and 7.
- **`cold-audit.md`** assumes you are willing to run a second, independent
  session to audit the first. That costs real tokens. Decide deliberately.

Cut what does not fit. A method document nobody follows is worse than none.
