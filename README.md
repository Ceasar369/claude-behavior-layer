# A behavior layer for Claude Code

A working `.claude/` — 19 skills, 3 agents, 8 hooks, and a session convention that
ties them together. Not a starter template. This is a layer that has been run,
broken, and hardened, then lifted out of the project it grew in.

Clone it, point three variables at your repo, and it runs.

Two things in here you probably haven't seen elsewhere. They come first.

## 1. Ten skills, ten digits

A keyboard has exactly ten digits. This layer spends all ten.

The ten skills reached most often carry one, `0` through `9`, so each costs a
single keystroke. `/0` boots a session. `/9` closes it — alpha and omega, the two
run more than any other.

```
0  start      1  build                                  8  ship    9  stop
      2  ask   3  answer   4  inbox
      5  repeat   6  clarify   7  provide-prompt
```

`0`, `1`, `8`, `9` are the spine — once each, in that order. `2` through `7` are
the middle, reached repeatedly, in whatever order the work needs.

The digit is a position, never a ranking. The other eight skills hold no position
in that sequence, so they keep plain names. There is no eleventh digit, which is
the point: a new skill earns one only by displacing an existing one on frequency.

## 2. A file-based bus for questions across windows

A session gets blocked on a decision. You're in another window. Normally it stalls.

Here it writes the question into its own folder and stops. Any other window
answers it. The blocked session pulls the answer and carries on.

```
sessions/0041-refactor-auth/
  90-0003-token-expiry-ask.md
  90-0003-token-expiry-answer.md        ← unread
  90-0002-schema-choice-answer.read.md  ← already pulled
```

**There is no state anywhere else.** No pairing table, no counter, no daemon.
Three writers touch three disjoint filenames — the asker writes the ask, the
answerer writes the answer, the asker renames it once read. Nothing can clobber
anything, and an interrupt cannot strand a session in a wrong state, because the
state *is* which files exist.

`/2-ask` writes and stops. `/3-answer` replies from anywhere. `/4-inbox` pulls it
back. One question open at a time, and that is structural rather than a rule —
asking ends the turn, and a stopped session cannot ask twice.

**The blocked session can wake itself.** `/2-ask` optionally leaves one detached
shell process watching for its own answer file — bounded at eight hours, spending
zero model turns while it waits. The answer lands, the process exits, and the
session resumes into `/4-inbox` on its own. That waiter is the only piece of state
outside the files, and it is deliberately worthless: it reads nothing and moves
nothing. Lose it and the answer file still stands, because pulling by hand is
always the fallback.

A local page shows the whole board:

```bash
python3 .claude/tools/bus-viewer/server.py    # http://127.0.0.1:8787
```

Orange, a session is waiting on you. Green, it owes itself an `/4-inbox`. The page
imports the same `bus.py` the skills call, so it derives every state at read time
and can never disagree with them. One dependency: `python3`.

On macOS, `./build-app.sh` makes it a double-clickable boot button — engine up,
workspace open, page on screen. The icon is drawn from code, not checked in as art.

## The three ideas

**A session is an object on disk, not a chat window.** It has a number, a folder, a
lock block, and a live marker. `/0-start` creates all four; `/9-stop` distils the session
into one prose paragraph in a dated archive file and removes them. What survives is
what was written down on purpose. Nothing survives by accident.

**A rule a model can drift past is not a control.** Every rule that must hold is a
hook with an exit code, not a sentence in `CLAUDE.md`. Five guards block destructive
shell, writes to the pristine checkout, an executor leaving its lane, built-in
subagent types, and memory writes. They fire for the main session and for every
subagent, and they are all probeable from a terminal.

**An agent is defined by its write fence, not its topic.** `executor` is not "the
agent that writes code" — it is the agent that can write `.worktrees/<branch>/`
and its own session folder, and nothing else on disk. The fence is a directory
check in `guard-write.sh`, keyed off the name the agent passes in its own hook
declaration. Change the fence and you have changed the agent. Pass a name the
`case` does not know and every write is blocked, which is how a retired agent
fails closed.

One fence, not one per topic. Parallel executors are separated by their assigned
target paths instead — an executor spawned without them stops rather than guessing
its scope. If you want a hard fence between two subtrees, adding one is three edits
that must land together: a `case` branch in `guard-write.sh`, an agent file carrying
its own `guard-write.sh <name>` declaration, and a row in `.claude/agents/README.md`.
A table row with no `case` branch has no fence at all.

## What's in the box

### Skills

All nineteen, by what they are for.

| | |
|---|---|
| **Lifecycle** | `0-start` `1-build` `8-ship` `9-stop` `handoff` |
| **Messages** | `2-ask` `3-answer` `4-inbox` |
| **Input and delivery** | `5-repeat` `6-clarify` `7-provide-prompt` `snippet` |
| **Analysis** | `conclusions` `realign` `prove` `challenge` `doc-check` |
| **Authoring** | `plan-agents` `skill-creator` |

A few worth naming:

- **`handoff`** — moves a live session to a fresh terminal without closing it.
  The number, the folder, the lock and the branch all stay; only the pane changes.
  It updates the session's own folder first, then writes a prompt whose first line
  re-attaches the new terminal to the same session identity.

- **`prove`** — someone claims the docs say X. It splits the claim, fans out cold
  collectors that are forbidden from concluding anything, hands every quote to a
  separate judge, then greps each returned quote to confirm the line number. A claim
  that cannot be quoted is reported as invented.
- **`conclusions` / `realign`** — both read the session's own on-disk transcript
  rather than its context. They flatten it into a gate-aware file where a formal
  `AskUserQuestion` answer is marked as the highest-authority evidence, and harness
  notifications are tagged so they can never be mistaken for the user.
- **`challenge`** — spawns agents with deliberately opposed assigned stances, and
  never tells any of them what the session already believes.

### Agents

| Agent | Writes | Fence |
|---|---|---|
| `executor` | `.worktrees/<branch>/`, plus `sessions/` | `guard-write.sh executor` |
| `researcher` | nothing | `Read, Glob, Grep` only |
| `web-researcher` | nothing | tools only |

### Hooks

| Hook | Event | Effect |
|---|---|---|
| `guard-destructive.sh` | PreToolUse(Bash) | Blocks every directly-typed `rm`, `git clean`, `sudo`, force-push. |
| `guard-infra.sh` | PreToolUse(Write) | Blocks any write to the primary code checkout. |
| `guard-write.sh` | PreToolUse(Write) | Confines an executor to its lane. Fails closed. |
| `guard-spawn.sh` | PreToolUse(Task) | Blocks built-in subagent types. |
| `guard-memory.sh` | PreToolUse(Write) | Blocks every write to a Claude memory store. |
| `archive-init.sh` | SessionStart | Creates today's archive file. |
| `session-markers.sh` | SessionEnd | Clears the session's identity file, sweeps stale ones. |
| `notify-bus.sh` | PostToolUse(Bash) | Desktop notification when a question is asked or answered. |

### The status page

Covered above. `.claude/tools/bus-viewer/` — one command, any OS, any browser.

If you have iTerm2 and its Browser Plugin, the macOS boot button gives you a
dedicated window with a terminal on the left and the page live on the right.
Without them it opens your browser, which needs no setup.

## The session convention

Nine of the nineteen skills depend on this. It is the one thing to understand
before adopting.

```
sessions/
  ACTIVE.md                             the live index — lock blocks
  0001-token-refresh/
    00-session.md                       intent, mode, decision log
    .session-live                       the live marker
    90-0001-refresh-trigger-ask.md      asked, unanswered      → orange
  0002-cache-invalidation/
    90-0001-delete-or-write-ask.md
    90-0001-delete-or-write-answer.md   answered, not pulled   → green
  0003-schema-migration/
    90-0001-backfill-shape-ask.md
    90-0001-backfill-shape-answer.read.md   pulled             → grey
archive/
  2026-01-14.md                         one file per day, pure prose
```

Those three are seed data, shipped so a fresh clone shows the real shape rather
than an empty tree. Clearing them is one loop — see the viewer README.

A lock block claims path prefixes. `/1-build` refuses to open a worktree on paths a
live lock already claims, and prints the colliding block in full so the collision is
judged on its own terms rather than by a rule. That is what lets several sessions run
at once against one repository.

`/1-build` cuts a worktree per branch under `.worktrees/`, so the primary checkout never
moves off the integration branch and several branches are live simultaneously. `/8-ship`
tears the worktree down only after verifying on disk that the branch really merged.

## Install

```bash
git clone <this repo> my-project
cd my-project
cp .claude/lib/paths.local.sh.example .claude/lib/paths.local.sh
```

`paths.local.sh` holds overrides only — it is sourced before the defaults, so anything
it sets wins. Never copy `paths.sh` itself.

Dropping the layer into an existing repo takes six paths: `.claude/`, `CLAUDE.md`,
`sessions/`, `archive/`, `docs/`, `prompts/`. Only the first four are load-bearing —
`require_paths` hard-fails without `sessions/` and `archive/`. Skip `docs/` and
`prompts/` and nothing errors, but `/prove`, `/doc-check`, `/7-provide-prompt`, and
`researcher` all lose the tree they navigate, silently. Point `DOCS` and `PROMPTS` at
your real ones instead.

Requires `bash`, `jq`, `python3`, and `git`. `gh` only if you use `/8-ship` to open PRs.

Probe the guards before trusting them:

```bash
printf '{"tool_input":{"command":"rm -rf build/"}}' | .claude/hooks/guard-destructive.sh
# → exit 2, with the block reason on stderr
```

## What you must change first

1. **`.claude/lib/paths.local.sh`** — set `CODE` to your real code checkout. It
   defaults to `./code`. Set `CODE=""` to switch `guard-infra.sh` off entirely if your
   repo has no separate checkout. Set `MAIN_BRANCH` if yours is not `main`.

2. **Nothing, if one executor suits you.** `executor` writes the whole worktree, and
   parallel spawns are separated by their assigned target paths rather than by a hook.
   Want a hard fence between two subtrees anyway? Add it in three places at once — a
   `case` branch in `guard-write.sh`, an agent file with its own `guard-write.sh <name>`
   declaration, and a row in `.claude/agents/README.md`. A row with no `case` branch
   has no fence.

3. **`docs/`** — replace the placeholder with your real documentation, and give it a
   front door. `prove`, `doc-check`, and `researcher` all start there and navigate by
   discovery, so any structure works as long as there is an index to follow.

4. **`CLAUDE.md`** — the communication section is opinionated on purpose: eight words
   per sentence, answer first, no preamble, pick one option rather than listing three.
   Keep it or cut it, but decide deliberately. The rest of the file is the routing and
   delegation doctrine the skills assume, and that part is load-bearing.

5. **Nothing else is machine-specific.** No absolute path appears anywhere in the
   layer. Every script derives the repo root from its own location; every hook command
   uses `$CLAUDE_PROJECT_DIR`.

## What it assumes

- One repository, several concurrent sessions, one human directing them.
- Code lives in a checkout that is never written directly, and changes land in branch
  worktrees.
- Documentation is a tracked tree in the repo, not a wiki.
- Claude Code is the runtime: `SKILL.md` frontmatter, `.claude/agents/`, hook events,
  and `AskUserQuestion` all behave as documented.
- Branch names start `fix/`, `chore/`, or `feature/`. `worktree.sh` rejects anything else.

If the second assumption does not hold, drop `guard-infra.sh` and simplify `/1-build`.
Everything else stands on its own.

### One dependency worth knowing about

Session identity — the map from a Claude Code session to its folder — is keyed on
`CLAUDE_CODE_SESSION_ID`. That variable is not a documented contract, so the layer
never trusts it alone. `boot.sh` writes the map only when it is set; `bus.py` says
plainly which session it could not resolve; `close.sh` clears the map immediately and
the `SessionEnd` hook clears it again; and a sweep deletes any file older than a day,
because a crashed session never reaches `SessionEnd`.

If the variable disappears, `/2-ask`, `/4-inbox`, and `/9-stop` lose the ability to name
their own session — every one of them then asks rather than guessing. Nothing corrupts.
That is the intended failure mode, not an oversight.

## Extending it

`/skill-creator` writes new skills to the authoring standard — 200-line cap,
40-word description cap, required sections, every named path verified to resolve.
`.claude/agents/README.md` is the equivalent standard for agents, including the rule
that a write-capable agent without a declared `guard-write.sh` hook has no fence at all.

`.claude/playbook/` holds the layer's own method documents — how to pace a prompt,
how a slice differs from a pillar, how consequential work gets audited cold, how a
change is traced through its dependents. They ship inside `.claude/` rather than in
`docs/` on purpose: `DOCS` is yours to repoint anywhere, and a skill that referenced
"the Writing a Prompt document" would dangle the moment you did. Every one of them is
opinionated and every one is yours to cut.

All ten digits are taken, so a new skill takes a plain name — `handoff` is the most
recent. A digit marks a position in a sequence; a skill with no position never gets one.

## Seed data

Three session folders, one archive day file, and three lock blocks ship with the
repo. They are real output from the real scripts, not mocks — the fastest way to
see the shape a session takes on disk, and what it leaves behind when it closes.

Clearing them is one loop, in `.claude/tools/bus-viewer/README.md`.

## License

MIT. See `LICENSE`.
