# The Layout

Up: [[the-stack-MOC|The Stack]]

Where code sits inside one layer.

## The layer root

Three folders. `backend/`, `frontend/`, `vendors/`.

A backend-only layer has no `frontend/`.

No lockfile. No Biome config. Those live at the root.

## Inside the backend

```
backend/
  package.json
  tsconfig.json
  migrations/          001-*.sql, or .ts where SQL cannot do the work
  src/
    server.ts          the entry
    routes/            the HTTP edge, shaped like the URL
    subjects/          one folder per subject
    base/              db, env, ids, errors, session
    reach/             calls to another of our layers
    run/               migrate, seed, anything typed as a command
```

A backend with tests builds its app in `app.ts`, and listens in `server.ts`.

A test and `pnpm spec` build the app from `app.ts`. Neither listens.

## Transport is separate from the subject

A route validates a body and a query, then calls. It computes nothing. An id
in the address is the subject's to find, or refuse.

A subject holds the work, and the SQL behind it.

The two change for different reasons, so they live apart.

## A subject folder names its own files

`subjects/recipes/recipes-rules.ts` holds the work.

`subjects/recipes/recipes-db.ts` holds its SQL. A file for one job of the
subject may hold that job's own: `recipes-history.ts`.

Each door keeps its password check in one file, named for its people.

Feature first, kind second. Never kind first.

## Inside the frontend

```
frontend/
  index.html
  package.json
  tsconfig.json
  src/
    main.tsx
    routes/            TanStack reads this. The folder is the URL tree.
    parts/             shared components
    base/              api client, session, translations
```
