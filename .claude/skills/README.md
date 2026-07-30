# Skills Index

Each folder is one invokable skill. The entry point is always `SKILL.md`.
Depth a skill does not need every run sits beside it as a supporting file.

## Naming convention

The name says what the skill is, read alone. A digit is added to that, never
a replacement for it.

A keyboard has exactly ten digits. Ten skills carry one, `0` through `9` — the
ten reached most often. `/0` is one key. `/start` is six. The digit marks a
position in one session, and it buys a keystroke.

The digits are spent deliberately, never handed out. `0` boots a session and `9`
closes it: alpha and omega, the two run more than any other. The eight between
them fill the middle of a session.

Every other skill takes a plain name. A plain name has no position. `prove` does
not come after `challenge`; `realign` is not step four of anything. Numbering
them would invent an order a reader then tries to decode.

All ten digits are taken, and there is no eleventh. A new skill takes a plain
name, unless it displaces one on frequency of use.

## The order

The digits trace one session, start to finish.

```
0  start            boot it
1  build            open the code lane
      2  ask        hand a question out
      3  answer     answer another session
      4  inbox      pull the answer back
      5  repeat     distill what was asked
      6  clarify    fix a reply that missed
      7  provide-prompt   write the next session's prompt
8  ship             commit, PR, merge
9  stop             close it
```

`0`, `1`, `8`, `9` are the session's spine — they happen once, in that order.
`2` through `7` are the middle: reached repeatedly, in whatever order the work
needs, but always between opening the lane and shipping it.

## The roster

**Lifecycle** — the spine. Every one depends on the session-folder and lock
convention described in `CLAUDE.md`.

| Skill | What it does |
|---|---|
| `0-start` | Numbers and boots a session; writes its folder and its lock. |
| `1-build` | Claims code paths against every lock; opens the branch worktree. |
| `8-ship` | Commits, pushes, PRs, merges, tears the worktree down. |
| `9-stop` | Reports what closing loses, archives it in prose, prunes the folder. |
| `handoff` | Hands a live session to a fresh terminal, with its instructions. |

`handoff` runs as often as the work needs, so it carries no digit. It claims
nothing and closes nothing. A handed session still ends at `9-stop`.

**Messages** — one question at a time, across windows.

| Skill | What it does |
|---|---|
| `2-ask` | Writes one question into this session's folder, then stops. |
| `3-answer` | Answers another session's open question, on the merits. |
| `4-inbox` | Pulls the answer left here, applies it, continues. |

**Input and delivery** — what to do when a message did not land cleanly, in
either direction.

| Skill | What it does |
|---|---|
| `5-repeat` | Distills a long or dictated message, then gates confirmation. |
| `6-clarify` | Re-delivers a reply the user could not use, diagnosed and fixed. |
| `7-provide-prompt` | Writes a session prompt — numbered, or a handoff. |
| `snippet` | Marks a paste as another session's output; re-anchors its referents. |

**Analysis** — read-only. None of them writes code or documentation.

| Skill | What it does |
|---|---|
| `conclusions` | Reconstructs what a session decided, from its transcript. |
| `realign` | Finds where a stuck session diverged, from its transcript. |
| `prove` | Proves a claim is written somewhere, or reports it invented. |
| `challenge` | Stress-tests an idea from three opposed stances. |
| `doc-check` | Finds where the docs contradict the code. |

**Authoring** — the layer extending itself.

| Skill | What it does |
|---|---|
| `plan-agents` | Staffs a scope into an agent DAG, then renders or executes it. |
| `skill-creator` | Creates a new skill to the authoring standard. |

## Two shared scripts

`realign` calls `conclusions/flatten.sh` and `conclusions/clean.sh`. Neither is
private to `conclusions/`.

## Adding a skill

Run `/skill-creator`. It carries the frontmatter reference, the body template, and
the rules — including the 200-line cap, the 40-word description cap, and the rule
that a new skill takes a plain name rather than a digit.
