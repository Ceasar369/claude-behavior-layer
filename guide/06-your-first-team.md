# 06 — Your first team

Launch a session, message it, end it, hand over, save, stop. Each step ran in my walk, with session 80 where yours is 02, and 81 where yours is 03.

## Launch a session

Type into session 02:

```
/launch one session: it writes today's date, from the date command, into date.txt at this project's root, then waits for my next message.
```

Session 03 opens in a pane below yours, and does it.

iTerm2's Python package came with 04's launch page: 20 MB, over the network, once per project. Whatever reads your panes first installs it: the launch page, a launch, or a session's Transcript tab on 1100.

On a launch page, drag any pane, including one already open. The moves apply only when you press Launch. Undo move takes back a planned move. The page may show Retry save, or "Launch could not be confirmed".

## Message it

```
/message 03 add a second line to date.txt that says: written by session 03.
```

It reaches 03 as if you had typed it there.

On a session's Transcript tab, a copy block has Copy. A hand-off has Copy, Type and Send. "Send my verdicts on session 03's page." has Send answers to 03. A hand-off to paste a file into ChatGPT has Copy file.

## End it

```
/reaper 03
```

A hook answers like this:

```
UserPromptSubmit operation blocked by hook: 1 successfully ended: 03. Its folder was deleted.
```

03's process, pane and folder are gone. What it wrote elsewhere, like `date.txt`, stays.

02 never sees that answer: a hook gave it, not 02. If 02 later says 03 still runs, it is wrong.

## Hand over

```
/session-handover
```

A fresh session opens where 02's pane was. It shows another number, then takes 02. It reads what 02 saved. The old pane closes. In my walk, the seat took about thirteen seconds.

This is how a session goes on once its context runs full. A drive hands its sessions over by itself. Document 11 shows the slower way: prepare now, resume later.

## Save the work

```
/8-ship
```

In my walk, it answered:

```
UserPromptSubmit operation blocked by hook: 3 paths successfully committed to main.
```

It commits every change in your project, on the branch your `.claude/project.json` names: tracked or not, `.claude/` included, minus what `.gitignore` refuses. Your own unsaved changes go in too.

`/8-ship push` also pushes.

## Stop

```
/9-session-stop
```

Typed bare, it goes through the session's model first. The model checks that nothing you asked for still holds the session, then stops it. `/9-session-stop now` stops at once, with no check.

The stop ends the session's ports, deletes its folder, and closes its pane. The pane closes at once, so its answer shows only in the session's transcript. Its answer reads like this:

```
Session 02 successfully stopped. No port was running. 1 dropped. Exiting.
```

"1 dropped" counts the work files its folder held. What sat in its folder goes with it: its waves, its blurbs, its handover copies.

Each next document starts in a session at your project's root. Start one as in 03: `claude`, then `/0-session-start 02`.

## Unproven here

- `/8-ship push`. My walks had no remote.
- The launch page moves, its Undo move and its two banners.
- The Transcript buttons.

## Check

- `date.txt` holds two lines.
- `git status` shows nothing to commit.
- `git log` shows your ship on top.
