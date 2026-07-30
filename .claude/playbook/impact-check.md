# Impact Check

Tracing a change through everything that depends on it.

**Trigger** — a change is about to ripple beyond the file in hand.

**Done** — every dependent is repointed, and a re-grep returns zero live hits.

Two cases. A name changed. Or a meaning changed.

The second is much harder, and it is the one that gets missed.

## Case one — a name or path changed

### What counts as a reference

Any place that names the changed thing.

Documents, the behavior layer, and code. Not just links —
prose, paths, and display text too.

### The change decides the fix

- **Rename.** Replace the old token with the new. Everywhere.
- **Deletion.** Remove or repoint every citation.
- **Move or split.** Repoint every inbound link and path.
- **Behavior layer.** The same hunt across `.claude` and `CLAUDE.md`.

### The hunt

- Grep the exact token across the whole scope.
- Then grep the partial forms. References hide there.
- Link display text — the display half too.
- The bare basename, with and without extension.
- Path fragments in prose, not only in links.
- Index child lists, parent links, back-links.

### Name every surface — never sweep from the root alone

A docs tree that is its own git checkout, or one the outer `.gitignore` covers,
is invisible to a grep that honours ignore files. The sweep reports clean and
the tree was never read.

Name each surface explicitly, every time: `CLAUDE.md`, `.claude/`, `docs/`,
`prompts/`, and each worktree.

### The trap — do not fool your grep

Never filter grep on a string that holds the changed path.

An inverted match on the old path hides lines mentioning it.
Those hidden lines can be live references.

Filter by file, or read every hit by hand.

Exclude the archive and session logs by file only. Then read those
hits and confirm they are history.

### Verify clean

- Re-grep the old token across the full scope.
- Expect zero live hits. Any drift means not done.
- Confirm every index and back-link still resolves.
- Return the grep command and its output.

## Case two — a meaning changed

The hard case. The concept's meaning shifted, not its name.

Grep finds the name. It cannot find an assumption.

### Why grep is not enough

A meaning change breaks documents that never name the thing.

They reason from the old meaning. The word is simply absent.

### The hunt

- Start at the naming document. Update the definition first.
- That document is the concept's one canonical home.
- Then find the dependents. Who assumes the old meaning?
- Trace by concept, not by string.
- Ask: who behaves as if the old meaning still held?
- Check downstream behavior — flows, rules, gates.
- A researcher reads for assumptions, not for mentions.

### Verify

You cannot grep a meaning clean.

Re-read each dependent. Confirm it fits the new meaning.

A dependent still assuming the old meaning is a miss.

## What escalates

Some edits never auto-apply. Recognize them, stop, and ask.

### The four triggers

- **Meaning.** The edit changes what a concept means.
- **Correctness-critical.** Auth, permissions, an amount, a limit, a rule
  that money or safety depends on.
- **Legal or regulatory.** An obligation, a compliance gate, a retention rule.
- **Deletion.** Removing a document or a concept.

### Meaning versus wording

- Wording: clearer phrasing, same claim. Apply it.
- Meaning: the claim, scope, or rule shifts. Escalate it.
- The test: would a reader now conclude something different?
- A different conclusion means meaning. Meaning means escalate.

### Why these stop

- Correctness-critical and legal fail closed. A wrong fact costs real damage.
- Meaning propagates silently across many documents.
- Deletion cannot be un-rung.

### How to escalate

- Name the specific item. Old form, new form.
- State which trigger it trips, and why.
- One item at a time. Never a bundle.
