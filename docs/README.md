# docs/

Your durable documentation. The canon.

This is the tree the layer treats as source of truth for everything that is not
code. Product decisions, architecture, doctrine, conventions — whatever your
project needs to state once and rely on.

Three skills read it directly:

- `/prove` searches it for the source of a claim.
- `/doc-check` compares it against what the code actually does.
- `/plan-agents` names the parts of it an agent must read before acting.

Structure it however you like. The layer never assumes a folder tree — it
discovers one. Give it a front door (`docs/README.md`, an index, a map) and every
skill and agent finds the rest by following links.

Two rules the layer does assume:

- **Code wins on every conflict.** A doc that disagrees with running code is a
  doc bug. `/doc-check` reports it as one.
- **A doc is timeless.** No dates, no "currently", no session numbers. Dated
  narrative belongs in `archive/`, which is exactly what it is for.

Point `DOCS` somewhere else in `.claude/lib/paths.local.sh` if your docs live
outside this repo.

This tree is yours alone. The layer's own method documents — how to pace a prompt,
how work gets audited before it ships — live in `.claude/playbook/` instead, so they
still resolve when you repoint `DOCS`.
