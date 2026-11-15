# The Tools

Up: [[the-stack-MOC|The Stack]]

Every tool choice, binding every layer, the one workspace holding every package, and the walk's traps.

## The choices

### Language

TypeScript, strict. Every layer, frontend and backend.

### Runtime

Node. It runs TypeScript with no flag: it strips the types, and refuses syntax that emits code.

`tsc --noEmit` is the type gate. An enum fails it.

Every import names its `.ts` extension. The type gate accepts it.

### Server

Fastify. One framework, every backend.

A server reads its port from the environment, never from code.

Its route schemas validate at the edge.

### Database

Postgres. Homebrew installs it on a laptop.

One server. One database per layer with a backend.

Each database takes its layer's name.

No cross-layer join is possible. Postgres cannot join two databases.

One role per database. A layer's credentials open its own, and no other.

One pool per process.

There is no Docker.

### Driver

`pg`, with nothing above it.

No ORM. No query builder.

### Money in the driver

`pg` returns `bigint` as a string, deliberately.

One type parser, registered at boot, turns it back into a number, for amounts and rates alike.

How each is held is [[the-formats|The Formats]]'s.

### Migrations

Plain SQL files. Applied in name order, once, forward only.

A file that has applied never changes.

### Linter and formatter

Biome. It replaces eslint and prettier both.

### Tests

`node:test`, run by Node itself. No test dependency enters a package. The
deploy's smoke runs on k6, on the server.

Each test sits beside its code, as `*.test.ts`. One named for a source file
tests it. Another names what it tests: `recipes-edges.test.ts`.

A test program `pnpm test` must not run takes another name.

One test file runs alone, from its package's folder: `node --env-file-if-exists=.env --test --test-force-exit --test-timeout=120000 <file>`. The two flags end the run once its tests finish, and fail a test past two minutes.

A test never leaves a row behind. It works in its own schema of its layer's
sandbox database, dropped after, or makes its own rows, then drops them.

`curl` and a cookie jar prove a door's backend alone. It answers on its own port. A browser walk proves the pair, through the frontend's port.

### Frontend

React, built by Vite, routed by TanStack Router.

> **Stand-in.** The languages every frontend carries.

## The workspace

### One workspace

pnpm.

Every package under `code/` belongs to it.

### What is installed once

What every package uses lives at the root.

A catalog pins each version in one place.

### What one package holds

Its own runtime packages, and nothing shared.

A backend holds Fastify and `pg`.

A frontend holds React and its router.

### Every package we ship answers the same commands

- `pnpm dev` — it runs.
- `pnpm typecheck` — `tsc --noEmit`.
- `pnpm lint` — `biome check .`.
- `pnpm test` — `node:test` runs.
- `pnpm migrate` — a backend applies its own migrations.
- `pnpm seed` — a backend loads its seeded people.

A package answers `test` even with nothing to run.

A backend has no `build`.

A frontend has `build`.

### Several packages at once

pnpm's own recursion does this, never a runner script.

- `pnpm -r typecheck` — every package that has one. The prototypes run none.
- `pnpm -r lint` — every package.
- `pnpm -r --parallel dev` — every server.
- `pnpm --filter <package> dev` — one package.

### One release carries every backend

`pnpm deploy` writes one package with its own dependencies.

One deploy writes each backend so, into one release, out of one workspace.

## The walk's traps

### An open browser holds half a gigabyte

It holds it until its session ends. A walk ends with `browser_close`.

### A ref lives one snapshot

A Playwright click names a ref from the newest snapshot. Once the page changes, an older ref fails: "Ref e21 not found in the current page snapshot".

### The run-code tool lacks `URL` and `require`

`browser_run_code_unsafe` runs without `URL`, `URLSearchParams` or `require`.

### The upload tool takes files inside the repository

A file outside it is refused: "outside allowed roots". A walk keeps its document beside its screenshots.
