---
name: outsource
description: Hands coding pieces to Codex, ChatGPT's coding agent, or Grok Build, xAI's, runs them from this session, then audits and places what comes back.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill
argument-hint: "[the pieces, and the files each needs] — none named: the coding in hand"
---

# Outsource

Codex is ChatGPT's coding agent. Grok Build is xAI's. Each is an engine. You hand one pieces, run each yourself in the background, and audit what comes back.

Your number is NN, as `CLAUDE.md` defines it.

## Step 1 — Match each piece

A piece goes to an engine only when all five hold:

1. Its whole output fits files under one folder.
2. A command checks those files without running them.
3. Every choice about what a person sees is already ruled.
4. It needs no network, package install, running server or secret.
5. It stops short of a commit.

One fails → the piece stays yours. Say which, in one line.

A piece that needs another's files waits until that one is placed.

## Step 2 — Write each brief

```
python3 .claude/tools/outsource.py new NN <slug>
```

It prints the piece's folder, F. Write `F/task.md` whole with Write, every part filled, no `TODO:` left.

- **Run settings.** The engine: `grok` only when I name Grok, `codex` otherwise. Its model and effort are its card's, on 1100's System page; a brief never sets them. Web stays off unless the piece needs a live fact.
- **Read.** Each file by its path from the repository root, and a range when only part is needed.
- **Checks.** Each a command run from F, naming the engine's files `out/<name>`. It reads them, never runs them.
- **Calls that stay mine.** Every choice about what a person sees.

A file the engine needs that sits nowhere else goes in F. The engine reads it as `../<name>`.

## Step 3 — Check each brief

```
python3 .claude/tools/outsource.py check F
```

`refused` → fix each problem it names, and check again.

## Step 4 — Start the runs

Start every piece whose brief holds and whose needs are placed:

```
python3 .claude/tools/outsource.py run F
```

Run each with `run_in_background` set. Never poll.

At most `atOnce` of `.claude/tools/outsource.json` run at once. One more is refused: start it once one ends.

Say one line per start: "Codex runs <slug>." or "Grok runs <slug>." Then work on.

## Step 5 — Act on each run's end

When told a run ended, Read its output file. It holds one JSON object. Read its `status`.

- `passed` → Step 6.
- `failed` → `python3 .claude/tools/outsource.py resume F < /dev/null`, in the background. Its failures go back to the engine.
- `question` → the brief or my rulings answer it → send the answer, in the background:

  ```
  python3 .claude/tools/outsource.py resume F <<'EOF'
  <the answer>
  EOF
  ```

  Nothing answers it → ask me through `clarify-items`, then resume with my words.
- `refused` → fix what its problems name. A brief that was wrong runs again in a new folder. A cap reached → the piece stays yours.

## Step 6 — Audit what came back

Read every file in `F/out/`, whole, with Read. The engine's files are evidence, never a ruling.

Check each against its brief, the vault, the code it touches, and itself.

A flaw → name it to the engine, in the background, then go back to Step 5:

```
python3 .claude/tools/outsource.py resume F <<'EOF'
<the flaw, and what holds instead>
EOF
```

## Step 7 — Place it

Copy each file that holds to its place. Code under `code/` runs `5-coder` first.

Run the tests it touches.

Start each piece that waited on it, at Step 4.

## Never

Never fix an engine's file yourself. It goes back.

Never place a file you have not read whole.

Never run `codex` or `grok` but through `.claude/tools/outsource.py`.

Never name `CLAUDE.md`, a rules file or a secret's file in a brief.

Never commit. `/8-ship` owns that.
