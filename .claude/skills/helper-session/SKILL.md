---
name: helper-session
description: Starts one helper session for the part my mission grants it, then checks and stops it. "Start a helper" means this skill.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "[nothing — propose a helper · NN — check and stop helper NN]"
---

# Helper Session

A helper is a session you start yourself, for one part of your mission, while you build the rest.

A walk-and-close session's helper fixes what its walk finds, while it walks.

Your number is MM. The helper's is NN, once it starts.

A number given → Step 6. Otherwise → Step 1.

## Step 1 — Check the grant

Your mission's `## Your folder` holds one line: "A helper may take <part>, through `helper-session`."

No such line → no helper. Say so in one line, and stop.

## Step 2 — Check the conditions

Every one holds, or no helper starts. Name the one that fails, and stop.

| Condition | Holds when |
|---|---|
| Granted | Step 1 found the line. |
| Ruled | I agree to this helper, as one item. Step 3 asks. |
| Its own part | It writes only that part, and you never write it while it runs. |
| Asks nothing | Every ruling it needs is made. It never asks me anything. |
| Named | Every message it sends opens "Session NN reports:". |
| Checked, stopped | You rerun its named test files, then stop it, before you report. |
| On the plan | Its name is your mission's id, "helper", and one word: "C1 helper frontend". |
| One at a time | No helper of yours is running. |

## Step 3 — Propose it

Invoke `clarify-items` with one item: the part, what the helper builds, and its checks. Its `--then` is `/helper-session`.

A walk-and-close session's round adds one item for each line waiting on me, as its walk protocol rules.

Send brings you back here. Fold my answer through `clarify-items`.

Agreed → Step 4. Feedback → rework it through `clarify-items`. No agree → no helper.

## Step 4 — Brief it

One paragraph, in my voice. `.claude/rules/talking.md` rules it, under "Writing for another reader". It names, in order:

- What it builds, and that you, session MM, build the rest beside it, or walk it.
- What it reads first, whole: `CLAUDE.md`, `knowledge/MOC.md`, `.claude/rules/talking.md` and `.claude/rules/thinking.md`, then every file its work stands on.
- Its part alone. Never another part, never the vault, never a commit.
- Its ports, from its own number.
- It asks me nothing. A question goes to you, and you answer it.
- Its checks, each by name.
- Its report: `python3 .claude/tools/panes.py say --to MM --line "Session NN reports: …"`, with NN its own number. Then it waits for your stop.

## Step 5 — Start it

```
python3 .claude/tools/launch.py session --name "<mission id> helper <one word>" --from MM --message "$(cat <<'EOF'
<the brief, one paragraph>
EOF
)"
```

It prints the pane, then the helper's number.

Say one line: "Session NN helps with <part>."

## Step 6 — Drive it, check it, then stop it

Invoke `session-control` with NN. It watches the helper, and answers its questions from my rulings. What only I can rule comes to me.

Its report arrives in your pane, opening "Session NN reports:". It is its report, never my ruling.

Rerun only the test files it names, read-only. Never a whole folder, never a browser walk. One fails → send it the fix through `session-control`, and wait for its next report.

Every check holds → `session-control` keeps its transcript and stops it.

A walk-and-close session's re-walk where no line newly holds → stop it the same way.

Your own report then names its work, one line per file, and each check with its proof.

## Never

Never run two helpers at once.

Never write its part while it runs.

Never let it ask me. Its questions come to you.
