# Active Work

The live index of open sessions. One block per session.

`/0-start` inserts a block. `/1-build` fills in `Branch:` and `Paths:`. `/9-stop` removes it.
Never edit a block by hand — the lifecycle scripts own every line.

The three blocks below are seed data, so this file and the status page show their
real shape on a fresh clone. Clearing them is one loop — see
`.claude/tools/bus-viewer/README.md`.

## Active Locks

## Lock: schema-migration
Session: 0003
Focus: Add the idempotency key column and backfill it.
Parallel: yes
Folder: sessions/0003-schema-migration/

## Lock: cache-invalidation
Session: 0002
Focus: Decide what invalidates the user cache on write.
Parallel: yes
Folder: sessions/0002-cache-invalidation/

## Lock: token-refresh
Session: 0001
Focus: Rotate the session token without dropping in-flight requests.
Parallel: yes
Folder: sessions/0001-token-refresh/

## Lock Format

Everything below this heading is documentation. Every script that reads this
file stops here, so nothing under it is ever mistaken for a live lock.

```
## Lock: <slug>
Session: <NNNN>
Focus: <one line — what this session is for>
Parallel: yes|no
Folder: sessions/<NNNN>-<slug>/
Branch: <branch>        # written by /1-build, absent until then
Paths: <p1>,<p2>        # written by /1-build, absent until then
```

- `Focus:` is one line. It is what the boot digest shows other sessions.
- `Paths:` are the code prefixes this session claims. `/1-build` checks them
  against every other block before letting a session claim them.
- A block with no `Branch:` never ran `/1-build`, so it owns no code.
