# 13 — Self-drive

One task taken to its end, checked, then the session stops itself.

## What it does

`/self-drive` takes the task you hand it to its end, verified and visible. Then it stops its own session. One task alone needs no team: this is it.

## Your first try

In session 04, from 12:

```
/self-drive write code/guide-lines.txt, holding exactly what python3 code/guide-lines.py prints, then check it matches a fresh run.
```

In my walk: two minutes and thirty-five seconds. It wrote the file, and checked it against a fresh run with `cmp`, byte for byte. It ran its own code check. Then it stopped its session, and the pane closed.

It should end on a short report: what changed, what it checked. Mine stopped without one.

In my walk, the follower woke on the stop, checked the file, and ended its follow.

## Unproven here

- A task longer than a few minutes.
- A self-drive in a fresh session. Mine ran in a session that had already worked.

## Check

```
python3 code/guide-lines.py > /tmp/fresh.txt
cmp /tmp/fresh.txt code/guide-lines.txt
```

`cmp` prints nothing when the two match. 04's pane is gone.
