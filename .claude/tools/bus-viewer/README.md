# Ask / Answer Viewer

A local status page showing which session has a question out and which has an
answer waiting. Each session with traffic gets a card: orange when someone owes
it an answer, green when it owes itself an `/4-inbox`, grey when nobody owes
anybody a move. Cards sort by state, longest wait first.

It reads the session folders directly. There is no separate bus root and no
counter file — the state derivation lives in `../bus.py`, which the page
imports, so the page and the skills can never disagree.

Read-only. It never writes.

## Run it

```bash
python3 server.py                  # then open http://127.0.0.1:8787
BUS_PORT=8788 python3 server.py    # a second engine, for a second repo
```

That is the whole dependency list: `python3`. Works on any OS with any browser.

Everything below is the optional macOS convenience layer.

## The boot button

```bash
./build-app.sh
```

That produces `Bus.app`. Double-click it, or drag it to the Dock. One click:

1. **The engine** — started only when the port is dead.
2. **Your workspace** — only if you supplied `open-workspace.sh`.
3. **One window** — holding the status page.

Every step **ensures**, never adds. Click it five times and you still have one
engine and one window. That is the whole design rule: the button is a state the
machine converges on, not a sequence it replays.

### Step 3 has two paths

**The browser path** needs no setup. The page opens in your default browser.
This is what happens unless you have gone out of your way to set up the other.

**The iTerm2 path** gives you a dedicated window: a terminal on the left, the
status page live on the right. It needs three things, and falls back to the
browser silently if any is missing:

- iTerm2 in `/Applications`.
- Its Browser Plugin (drop the plugin in `/Applications`).
- A profile named `Bus` — Profile Type = Web Browser, Initial URL =
  `http://127.0.0.1:8787`.

The window is identified by its `Bus` pane, so a second click focuses it rather
than opening a second one.

Controlling iTerm needs macOS Automation permission. The first click after a
build prompts once. Rebuilding changes the bundle signature, so the prompt can
return: System Settings → Privacy & Security → Automation.

## Files

| File | What it is |
|---|---|
| `server.py` | The engine. Serves the page and `/status`. Debug it directly. |
| `../bus.py` | The ask/answer mechanics, imported for the state scan. |
| `launcher.applescript` | The boot button's source. |
| `build-app.sh` | Builds `Bus.app` from that source. |
| `make-icon.py` | Draws `icon.png` from code. No dependencies, no binary art. |
| `launcher.conf.example` | Port, iTerm profile name, app name. |
| `open-workspace.sh.example` | Optional: what step 2 opens. |

`Bus.app` and `icon.icns` are build artifacts and are git-ignored. `icon.png` is
committed and authoritative — supply your own to replace it. `make-icon.py` only
fills a gap when no `icon.png` exists.

## Settings

```bash
cp launcher.conf.example launcher.conf     # port, profile name, app name
cp open-workspace.sh.example open-workspace.sh && chmod +x open-workspace.sh
```

Both are git-ignored. Both are optional.

Running two repos at once? Give each a different `PORT`, and a different
`APP_NAME` so the two Dock icons are distinguishable. The page header shows
which repository each engine is watching.

## Seed sessions

The repository ships with three sessions in `sessions/`, one per state, so the
page shows something the first time you run it rather than "No sessions." They
are real session folders written by the real scripts — nothing about them is
mocked. Read them to see the shape a session actually takes on disk.

Clear them whenever you want the repo empty:

```bash
for s in 0001-token-refresh 0002-cache-invalidation 0003-schema-migration; do
  .claude/skills/9-stop/close.sh --folder "$s"
done
```

That removes each folder and its lock block, the same way `/9-stop` does. It writes
nothing to `archive/`, because no archive block is passed.

## What the states mean

Three values, named by whose turn it is. Each is derived at read time from which
files exist — nothing is stored, so nothing can get stuck.

- **Open** (orange) — an `-ask.md` file with no `-answer.md` beside it. Run `/3-answer <session>` from any window.
- **Answered** (green) — an `-answer.md` not yet renamed `-answer.read.md`. Run `/4-inbox` in that session.
- **Idle** (grey) — nothing pending either way.

Open beats answered, so a session showing orange may also have an answer waiting.

A session that has never asked anything gets no card — questions are the subject
of this page. A closed session whose questions were all answered and pulled drops
off too.

Idle is not "done". It means nobody owes anybody a move right now.

## The round marker

Numbers run contiguously per session, so how many exist is how deep the thread ran.

A card shows that count beside the session name once it passes one. At four or
more it turns orange.

One question is the norm and shows no marker.

A session can only have one question open at a time: asking ends its turn, so a
stopped session cannot ask again. If a second ever appears, the card shows an
`N open` badge and names the highest.

The page refreshes every 5 seconds.

## Editing the engine

`server.py` holds the page inline, so a running engine serves the code it started
with. Editing the file changes nothing until the old process dies — and the app
only starts one when the port is **dead**, so clicking it will not reload an edit.

Kill it by port, never by name — `pkill -f` misses it:

```bash
kill $(lsof -nP -tiTCP:8787 -sTCP:LISTEN)
python3 server.py &
```

Then reload. Skip this and the page serves stale code and looks broken.

The engine is a local process, not a daemon. It runs while your machine session
is up. A restart kills it, and the pinned tab then shows a connection error until
you click the app again. The error is honest; the fix is one click.
