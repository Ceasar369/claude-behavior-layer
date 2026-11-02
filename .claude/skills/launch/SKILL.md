---
name: launch
description: Launches other Claude Code sessions or browser panes for me, each in its own iTerm pane. "Launch a session" means this skill. Never a subagent.
argument-hint: "[the sessions or sites to open, and what each does]"
allowed-tools: Read, Write
---

# Launch

## Step 1 — Know my number

My number, NN, as `CLAUDE.md` defines it.

Read `.claude/state/sessions/NN/record.json`.

No record → run the skill `0-session-start`, then go on.

## Step 2 — Decide the panes

I may be precise, or vague. Vague → decide the sessions the work needs.

One session is one pane. One site I want shown is one pane.

One pane → step 3. Two or more → step 4.

## Step 3 — One pane opens at once

A session:

```
python3 .claude/tools/launch.py session --name "<one to three words>" --message "<its first message>"
```

A site: `python3 .claude/tools/launch.py browser --site <site>`. Add `--name` only for a name I gave.

A page of this layer names itself.

Add a flag only for what I named. Every other value keeps its default.

- `--number` — two digits. Only missions and helpers take a team's ten.
- `--account` — one of this Mac's accounts, by its number.
- `--model` — any model id Claude Code knows, as `claude-opus-5-5`.
- `--effort` — `low`, `medium`, `high`, `xhigh` or `max`.
- `--from` — a session number.
- `--where` — `right`, `left`, `down`, `up`, `tab` or `window`.

A site is a port on this machine, or any address.

A session prints its pane, then its number once it holds its message.

Say one line: "Session 07 started, below me." Stop.

## Step 4 — Two or more wait on my page

The file is `.claude/state/sessions/NN/launch.json`. Write it with the Write tool.

It exists → read it first. Keep every key it holds, as it is, not only `rows`: the page keeps my planned pane moves in `moves` and `layouts`. Keep every row, as it is. Add mine after them.

```json
{"rows": [
  {"name": "docs skeleton",
   "message": "Read CLAUDE.md, then build the skeleton I describe below."},
  {"kind": "browser", "site": 7204}
]}
```

A session row takes `name` and `message`. Add `n`, `account`, `model` or `effort` only when I named it. A calling skill may also set `n`, the row's seat, as `another-team` does. A mission's row in a plan run in order always sets it, and an open plan's never does: the launch takes the next free seat. Axiom 7 of `knowledge/0010-playbook/0011-assisting/the-assisting-axioms.md` rules both. Add `"drive": true` only when I asked it to self-drive.

A browser row takes `site`. Add `name` only when I named it. The page proposes `NN-browser-K`.

The page fills the rest: the order's next account, the model and effort set on 1100/system, each pane below the one before.

1100 hears the file. The page shows in my hub, with a white dot on its number once this session's turn ends, until the rows are gone.

List the rows in chat, one line each: its name, and its number or account when I named one. Your move is "Action: press Launch on 1100."

A stage I handed you, as my assistant, adds one key, `"after"`, naming the stage before it: `{"after": "B", "rows": [...]}`. Its button reads Schedule, and a press launches nothing. You fire it once that stage closes, as `1-assistant` Step 7 says, so nothing waits on my press. Its rows are mine to change until then. Your move is a Wait, like "Wait: stage B's sessions stop. I then launch stage C."

A page found not ready before my press comes down at once, scheduled or not. Delete `.claude/state/sessions/NN/launch.json`. My edits on it go with it. Your move is a Wait naming what brings it back, like "Wait: the three helpers report. I then put stage D's page back." Once it is ready, write it again, as this step does. Its move comes back with it.

## Every message

`.claude/rules/talking.md` rules its voice,
under "Writing for another reader". Follow it.

One paragraph, no line break.

Read every file it names. Never state a fact from memory.

## Never

Never boot two or more panes yourself. The page launches them, when I press Launch, or when you fire a stage I handed you.

Never write where a row lands. I place each row on the page.
