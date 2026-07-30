---
name: handoff
disable-model-invocation: true
description: Hands this live session to a fresh terminal. Updates its own folder, gates the mode, then writes a prompt through /7-provide-prompt. Paste that prompt in the new window and close this pane. Never boots and never closes.
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, Skill
argument-hint: "[what the fresh terminal should do next]"
---

# Handoff

## Anchor

Follow the root `CLAUDE.md`.

## Purpose

Hand this session's work and its instructions to a fresh terminal. Then stop.

## What changes, and what does not

This runs **in the session being handed over**. The fresh terminal runs nothing
but the paste. There is no second skill.

The number, the folder, the lock, the marker and the branch all stay. Only the
terminal changes. No number is consumed, and no new lock is written.

Session identity is one file — `.claude/state/<harness session id>`, holding the
folder name. The prompt's first step writes it in the new terminal.

## Steps

1. **Resolve this session.**
   ```bash
   python3 .claude/tools/bus.py whoami
   ```
   It fails → this terminal owns no session. Say so and stop. Nothing to hand over.

2. **Update this session's own folder first.** Before writing any prompt.

   The folder is the record. The prompt only points at it.

   - `00-session.md` — append the decisions this stretch reached. One line each.
   - Any working document this stretch changed. Now, never deferred.
   - A `## State` section in `00-session.md`: what is settled, what is in flight,
     and the exact next action.

   **Never let the prompt carry a fact the folder does not hold.** The prompt is
   pasted once and dies. The folder is what the next stretch reads.

3. **Check for an unread answer.**
   ```bash
   python3 .claude/tools/bus.py inbox
   ```
   Anything unread → name it in the prompt. `/4-inbox` is owed before new work.

4. **Gate the mode.** `AskUserQuestion` — Header `Mode`; Question `What should the fresh terminal do?`

   - `Implement now` — it attaches, orients, and builds.
   - `Plan` — it attaches, orients, plans, then waits.
   - `Discuss` — it attaches, orients, discusses. No writes.
   - `Orient and wait` — it attaches, reports, stops.

   The `/handoff` line may already name it. Then do not re-ask.

5. **Write the prompt.** Run `/7-provide-prompt` and pass this as the intent:

   - **Handoff variant** — say so explicitly, so it uses the right sentinel and
     puts the attach command first. See its `## Handoff prompts` section.
   - **The session** — the folder name, exactly. The branch, when `/1-build` ran.
   - **Read first** — this session's own folder, in the order that makes sense.
     Real paths. The `## State` section first.
   - **Where the work stands** — settled, in flight, the next action.
   - **Any unread answer** — by number, and that `/4-inbox` is owed.
   - **The mode** — from step 4. It sets how the prompt opens.
   - **What not to do** — anything this stretch already ruled out.

   Never hand-roll the prompt. That skill owns the format and the guardrails.

6. **Print the move block.** End the turn with this and nothing after it:

   ```
   ➡️ HANDED OFF → <NNNN-slug>

   <the prompt path, from provide-prompt's output>

   Paste that file in the fresh terminal. Nothing else.
   Do not continue here. Close this pane.
   ```

7. **Stop.** The turn is over. Handing over ends the work in this window.

## The fresh terminal

It pastes the prompt. Its first step is the attach:

```bash
.claude/skills/handoff/attach.sh --target <NNNN-slug>
```

- Exit 2 — bad arguments. Fix the target and re-run.
- Exit 3 — no match, or several. It lists them.
- Exit 4 — a configured path is missing. Report and stop.
- Exit 5 — that session is closed. It cannot be resumed. `/0-start` instead.
- Exit 6 — no harness session id. This terminal cannot hold an identity, so the
  bus, the lock and the closer will all fail here. Report it and stop.
- Exit 7 — that pane already owns a session. Hand that one off first.

Then it reads the folder, reports what it holds, and follows the mode.

## After the move

Closing the old pane is the cleanup. `session-markers.sh` clears its identity
file on `SessionEnd`. Until then both panes resolve to the same session.

A session still ends at `/9-stop`. Hand it over as often as the work needs.

An unclosed session holds its lock, and every later `/1-build` re-checks it.

## Things NOT to Do

- Never run this in a terminal that owns no session.
- Never write a prompt before the folder is updated. The folder is the record.
- Never put a fact in the prompt that the folder does not hold.
- Never hand-roll the prompt body. `/7-provide-prompt` owns the format.
- Never tell the fresh terminal to run `/0-start`. That boots a new session.
- Never create a folder, a lock block, or a live marker. The session has all three.
- Never keep working after printing the move block. The turn ends there.
- Never write the identity file by hand. `attach.sh` owns it.
- Never delete an identity file. `SessionEnd` owns that.
- Never hand off a session in order to avoid closing it.

## Output

The session's own folder updated, one prompt written by `/7-provide-prompt`, and
the move block as the last thing in chat. The turn ends.

## Files

- `attach.sh` — resolves the target, refuses a closed or already-owned session, writes the identity file, prints the folder's real shape. Invoked by the prompt, never by this skill.
