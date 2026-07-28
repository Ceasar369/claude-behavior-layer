---
name: skill-creator
description: Creates a new Claude Code skill to the authoring standard. Use when asked to create a skill or codify a repeatable workflow. Creates only — never reviews or edits an existing one.
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
---

# Skill Creator

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Produce a `SKILL.md` that Claude discovers, triggers, and executes reliably.

## Target

All skills live in `.claude/skills/<name>/`. Infer the name from context; ask only if genuinely unclear.

Every skill anchors to the root `CLAUDE.md`. A skill written for an executor also names the docs that govern that lane — point at an index, never restate one.

## Frontmatter

Verify every limit and value set at `https://code.claude.com/docs/en/skills.md` before stating it.

**Required:**
- `name` — lowercase, numbers, hyphens. Defaults to the directory name.
- `description` — third person. States WHAT the skill does AND WHEN to use it.

**Optional:**
- `allowed-tools` — grants the listed tools without a permission prompt, for the invoking turn only. Does not restrict the toolset.
- `disallowed-tools` — removes tools from the pool while the skill is active. Use this to take a tool away.
- `argument-hint` — short hint shown beside the slash command.
- `arguments` — named positional arguments, substituted as `$name` in the body.
- `when_to_use` — extra trigger context. Appended to `description`; shares its character budget.
- `model` — the same values `/model` accepts. Omit to inherit.
- `effort` — low / medium / high / xhigh / max. Omit to inherit.
- `user-invocable` — `false` hides the skill from the `/` menu. Menu visibility only: the description stays in context, and the `Skill` tool still reaches it.
- `disable-model-invocation` — `true` so only the user's `/command` invokes it. Claude cannot invoke it, and its description stays out of context entirely. Check who calls the skill first; never set it on a skill another skill invokes. Whether it also blocks this skill's own outward `Skill` calls is undocumented — never rely on either reading. Protect an irreversible action with an `AskUserQuestion` gate, not this flag.
- `context` — `fork` runs the skill in a forked subagent.
- `background` — `false` waits for the forked subagent's result in the invoking turn.
- `agent` — delegate to a named custom agent.
- `hooks` — hooks scoped to this skill's lifecycle.
- `paths` — glob list; the skill loads only for matching files.
- `shell` — `bash` (default) or `powershell`, for `!` command blocks.

## The description

Ceiling: 1,536 characters, `description` and `when_to_use` combined.
It loads into every session — unless the skill carries `disable-model-invocation: true`, which keeps it out of context entirely.

Write one or two sentences, under 40 words. Third person. Lead with the use case.
Pack WHAT and WHEN. Add an anti-case only when a sibling skill could be confused for this one.

✅ `Extracts text from PDFs and fills forms. Use when working with PDF files.`
❌ `Helps with documents.`
❌ A paragraph of conditions, lifecycle notes, and caveats.

## Naming

The name says what the skill is, read alone. Never vague — no `helper`, no `utils`.

**A numeric prefix is reserved for a genuine sequence.** Ten skills carry one,
`0` through `9`, because they run in a fixed order: `0-start`, `1-build`,
`2-ask`, `3-answer`, `4-inbox`, `5-repeat`, `6-clarify`, `7-provide-prompt`,
`8-ship`, `9-stop`. The digit is the position, and it buys a one-keystroke reach
in the `/` menu.

Every other skill is a plain name — `prove`, `challenge`, `realign`. A skill with
no position in a sequence never takes a digit, because a number that means
nothing is a number a reader tries to decode.

All ten digits are taken. Writing a new skill means a plain name, unless the user
explicitly renumbers the sequence to make room.

## Supporting files

Put depth the body does not need every run into a file beside `SKILL.md` — templates, examples, scripts, reference data. Reference it by relative path.

```
.claude/skills/<name>/
├── SKILL.md          ← required
├── template.md       ← optional supporting file
└── example.sh        ← optional supporting file
```

## Body template

```
---
name: <slug>
description: <third-person what + when, under 40 words>
allowed-tools: <tools the body actually exercises>
---

# <Title>

## Anchor
<Which CLAUDE.md applies.>

## Purpose
<One imperative sentence.>

## Steps
1. <First action.>
2. <Second action.>

## Things NOT to Do
- <Constraints and anti-patterns.>

## Output
<What gets written, where, in what shape.>
```

`Anchor`, `Purpose`, `Steps`, `Things NOT to Do`, and `Output` are required. Rename `Steps`
to fit the skill's shape and add sections freely. Never drop a required one. `Things to Do`
is optional — add it only when the required actions do not already live in `Steps`.

## Rules

Every one holds on the draft before it is written. Read them with the conventions above.

- Cap the description at 40 words.
- Cap every skill at 200 lines total.
- Instruct, never explain. No rationale, no justification, no background.
- Use imperative voice throughout.
- Use timeless language — no dates, no "currently", no "planned".
- Pick one default approach. Never present multiple equivalent options.
- Use forward slashes in all paths.
- `allowed-tools` names the tools the body actually exercises.
- Every path the skill names must actually exist.
- Any skill that verifies must require the runnable check's actual output, never a claim of success.

## Question gates

Find the skill's decision points. When a decision is a small set of known options (2–4) asked in the main session, design it as an `AskUserQuestion` gate — header, question, options with a recommended first — and add `AskUserQuestion` to `allowed-tools`. When the answer needs prose, ask in chat. Gates cannot fire inside a subagent — keep those paths self-deciding.

## Steps

1. Infer target, purpose, trigger, argument, and output from context. Ask only what is genuinely unclear — one question, never an interview, via `AskUserQuestion`.
2. Identify decision points; design known-option ones as `AskUserQuestion` gates.
3. Draft `SKILL.md` using the body template with the correct anchor.
4. Move depth the body does not need every run into a supporting file.
5. Glob or grep every path the draft names. A path that does not resolve is a defect.
6. Confirm every rule in `## Rules` holds. Count the description's words.
7. Write to `.claude/skills/<name>/SKILL.md`.

## Things NOT to Do

- Never explain why a rule exists — state the rule.
- Never name a path without verifying it resolves.
- Never write a description longer than 40 words.
- Never present multiple equivalent options.
- Never omit the description's anti-case when a sibling skill could be confused for this one.
- Never grant a tool the body never exercises.
- Never review, audit, or edit an existing skill here. This skill creates.
- Never write an agent. Agents follow their own standard, in `.claude/agents/README.md`.

## Output

The new `SKILL.md` at `.claude/skills/<name>/SKILL.md`, plus any supporting files in that directory. Reply with the absolute path.
