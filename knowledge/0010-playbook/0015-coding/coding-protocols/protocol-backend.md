# Protocol — Backend

Up: [[coding-protocols-MOC|Protocols]]

Backend code, in any layer: a route, a subject, a migration, or their tests.

## The parts it touches

One layer's `backend/`, as [[the-layout|The Layout]] places its folders.

Its spec too, when it has one, which only `pnpm spec` writes.

## The steps, in order

1. Place each change where The Layout puts it.
2. A schema change is a new migration, as [[the-tools|The Tools]] rules. Band 00 reads the same database, as [[running-locally|Running Locally]] rules. So the change stays additive. A later migration drops the old shape, once every server has moved off it.
3. Each new block gets its own test, beside it.
4. Run it on your own port, from Running Locally.
5. While building, run only the test files you changed, as [[the-coding-axioms|The Coding Axioms]] rule.
6. At the end, pass the gate once, under `taskpolicy -b`: `pnpm typecheck` and `pnpm lint`. A backend with a `spec` script adds `pnpm spec --check`.
7. Prove each door with `curl` and a cookie jar, on your own port.

## The lessons

Nothing sits here.
