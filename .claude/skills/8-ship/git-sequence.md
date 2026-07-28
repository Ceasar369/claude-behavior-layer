# The git sequence

Read this at Step 7, after approval. Run the sections in order. Stop at the first failure and report it — never skip forward.

`<root>` is the repo root resolved in Step 1. For code that is `.worktrees/<branch>/`. For the layer repo it is the repo root itself.

`<main>` is the integration branch — `MAIN_BRANCH` in `.claude/lib/paths.sh`.

## 1 — Commit

In `<root>`:

1. `git add -- <file1> <file2> …` — only the listed files.
2. `git status --short` — the staged set must match the list exactly.
   **Empty staged set → you are in the wrong directory. Stop.** The primary code checkout is always clean; a worktree has its own index.
3. `git commit` with the authored message, appending:
   `Co-Authored-By: Claude <noreply@anthropic.com>`
4. `git push origin <branch>`. Add `-u` on a first push.

Never commit to `<main>` in a remoted repo. Never stage a file not listed.

Commit-only depth stops here.

## 2 — PR

In `<root>`:

1. `git log <main>..HEAD --oneline` — empty means nothing to PR. Stop and say so.
2. Title: the newest commit title on this branch, max 70 characters.
3. Body: `git log <main>..HEAD --pretty=format:"- %s"`
4. `gh pr create --base <main> --head <branch> --title "<title>" --body "<body>"`
5. Report the PR URL.

`merge: no` stops here. The PR stays open.

## 3 — Merge

`gh pr merge <branch> --merge`

Never pass `--delete-branch`. Never force. Report the merge status before doing anything else — this is the step nothing undoes.

## 4 — After the merge — code only

**Never run `git checkout <main>` inside a worktree.** `<main>` is checked out in the primary checkout, and a branch lives in one worktree only. The command fails with `fatal: '<main>' is already used by worktree at …`, and because it is usually chained with `&&`, everything after it silently does not run.

Instead:

```bash
.claude/skills/8-ship/teardown.sh --branch <branch>
```

It verifies the branch really is merged, kills anything holding the directory open, removes the worktree, confirms on disk that it is gone, deletes the branch local and remote, and fast-forwards the primary checkout.

Read every `=` line back. Report each one.

- Exit 2 — bad arguments, or no code checkout configured. Stop and report.
- Exit 3 — the branch is not merged. Nothing was removed. Stop and report.
- Exit 9 — the directory survived. Stop and report; do not retry blindly.
- `REMOTE_BRANCH_DELETED=no` — branch protection refused. Say so; leave it.
- `PRIMARY_<main>=could not fast-forward` — dirty or diverged. Say so; never force.

**The next branch is not cut here.** `/1-build` cuts it, so a worktree's path always matches its branch.

## 5 — Report

- **Code:** branch committed, PR URL, merge status, every teardown line.
- **The layer repo:** branch committed, and the merge result if one ran.
- **Blockers:** anything that failed, quoted.

Never report a step as done without its actual output.
