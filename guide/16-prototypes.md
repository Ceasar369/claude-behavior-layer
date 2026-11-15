# 16 — Prototypes

Your prototypes app, built once, then one generation of a prototype, picked and locked in.

## What it does

`/4-prototype` prototypes what you cannot yet picture, one generation of variations at a time. Each variation is a page you look at. 1100 draws the prototype page around it, at `/proto/`. Your project's own prototypes app, on 1400, only serves the variations.

My layer brings the family without an app. Your first prototype mission builds yours.

## Without its app

In session 02:

```
/4-prototype a welcome card
```

It answers in one line, and stops:

```
This project has no prototypes app in code/prototypes/. Its first prototype mission builds one.
```

Nothing is written. In my walk: 50 seconds.

## Build the app

Type into 02:

```
Then run this project's first prototype mission: build its prototypes app in code/prototypes/.
```

It ran `/5-coder` itself. No assistant, no mission file. In my last walk: twenty-one minutes. An agent of its own first mapped what my layer expects of the app, for eight and a half of them.

My walk's app ran on Vite, React and TanStack Router, installed by pnpm: 84 packages, over the network, once. Its `node_modules/` holds 89 MB.

My last walk's build picked that stack from my layer's own files, and took its packages from the network. It did look at which processes held my 1100 and 1400.

**Its config, as a template.** The app's `code/prototypes/vite.config.ts` sets two things my layer needs: the port, read from `PORT`, and the base, `/proto/`. Mine reads:

```
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// The whole app sits here, prototypes.py's BASE. 1100 passes every address
// under it through to this port, so 1100 frames the app from its own
// origin: the Claude app's browser panel refuses a frame from another port.
const BASE = "/proto/";

// Every prototype is a route here. None calls a backend, so the environment
// gives only the port.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const port = Number(env.PORT);
  if (!Number.isInteger(port)) throw new Error("PORT is not set.");
  return {
    base: BASE,
    plugins: [
      tanstackRouter({ target: "react", autoCodeSplitting: true }),
      react(),
    ],
    server: { port, strictPort: true, allowedHosts: [".ts.net"] },
  };
});
```

If your session's build writes another, hold it to those two.

**`node_modules/` stays out of git.** My layer's `.gitignore` holds it, among its four lines: `__pycache__/`, `.claude/settings.local.json`, `.claude/state/`, `node_modules/`. No `/8-ship` carries the app's 89 MB.

**Its band entry.** The build also wrote a `band` into `.claude/project.json`, so `/00-sessions-dashboard` serves the app on 1400. In my walk, the file then read:

```
{"name": "Newcomer Trial", "branch": "main", "band": {"servers": {"Prototypes": {"1400": "Prototypes"}}, "command": "pnpm --dir code/prototypes dev"}}
```

Then type `/00-sessions-dashboard`. With no word after it, it starts 1100 and your band 00, the app with it. `restart` swaps 1100 alone.

## One generation

Type `/4-prototype a welcome card` again, unless the session goes on by itself. Mine did.

With no level named, it builds at Glance: one variation, v1. In my walk: under three minutes. Its page is `http://localhost:1100/proto/?subject=welcome-card&session=02`. If the session names another address for it, open the page there. On 1100's home, the session's tile opens it too, in its Prototype tab.

Then, in 02:

- `/prototype-pick` gives the session's own pick, with what speaks for and against it. 42 seconds.
- `/prototype-checklist` lists what you look at and decide, line by line. 33 seconds.

## Lock it in

On the page, press the Pick bar under v1. Send then reads "Send · lock in". Press it.

Send types `g1/v1` into 02's pane. 02 locks the card in, then looks for rules the round teaches. In my walk: 55 seconds. 1100's `/proto/`, with no subject named, now draws the library: every winner under Locked, then every saved prototype under Saved.

If Send turns red and reads "Try again", type `g1/v1` into 02 yourself, as Send would. In my last walk, Send refused twice. Its tooltip said a dialog waited in the session's pane, though none did.

`/prototype-rules`, typed after, found nothing to write: "No new rules". On a fresh layer it has nowhere to write a rule for a product's screens until you make that place.

`/prototype-remove` keeps a locked winner. A hook answers:

```
UserPromptSubmit operation blocked by hook: welcome-card keeps its winner, g1/v1, until the session building it removes it. Nothing was removed.
```

**With the shift from 03.** Your app takes 21400, beside another project's 1400. Nothing waits on the other project.

**Without the shift.** One project at a time. While my band 00 runs, 1400 is my other project's app: this project's app cannot take the port, and its prototypes never reach 1400. `/00-sessions-dashboard`, bare, is refused there, as `restart` is in 03.

My last walk's build then served its own copy, on 1481, and named that port in every move: "Until it stops, this project's prototypes show only on 1481."

To give 1400 to this project, stop my band 00 in my other project first, with `/00-sessions-dashboard stop`. Then start this project's.

## Unproven here

- The app on npm alone, with no pnpm.
- `/00-sessions-dashboard` serving the app on 1400. My walks served it on other ports, beside my own band 00.
- `/prototype-brainstorm`. Nothing ran it.
- The app on 21400, under the shift. No walk ran it.
- Without the shift: stopping my band 00, so this project's app takes 1400. No walk stopped mine.
- Removing a winner: `python3 .claude/tools/prototype.py remove welcome-card --winner`.

## Check

- The welcome card shows on its page.
- `code/prototypes/welcome-card/g1.json` holds `"locked": true`.
- `git status` lists no `node_modules/`.
