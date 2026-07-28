# code/

Your primary code checkout goes here.

It stays pristine on the default branch. Nothing writes to it — not an executor,
not the session, not you through a session. `guard-infra.sh` blocks every write.

Code changes go to a branch worktree at `.worktrees/<branch>/`, which `/1-build`
cuts from this checkout. That is why a session can hold several branches at once
without a single `git checkout`.

Point it wherever your code actually lives by setting `CODE` in
`.claude/lib/paths.local.sh`. Set `CODE=""` there to switch the guard off if your
repo has no separate code checkout.
