# 03 — Download it

My layer into a folder of yours, then your first session, and 1100.

## Your way in

Take `main` from this address:

```
https://github.com/Ceasar369/claude-behavior-layer.git
```

The repository is public, and holds my layer alone. Git takes it with no GitHub account, and no sign-in.

## Into an empty folder

Started from 00's line, your Claude has done this part already.

A trial folder first, if you like: an empty folder you delete after. Your real project takes it as the next part shows.

```
mkdir ~/layer-trial
cd ~/layer-trial
git clone https://github.com/Ceasar369/claude-behavior-layer.git .
```

My layer's files land at the folder's root, with this guide.

Then, in your first session, type `/layer-update`. It answers "Up to date", and renames the clone's remote to `layer`, which only fetches. Your own repository takes the name `origin` when you add it. Every later take is that one command: 20.

## Into your project

In your project's folder:

```
git fetch https://github.com/Ceasar369/claude-behavior-layer.git main
git merge --allow-unrelated-histories FETCH_HEAD
```

Your project may have its own history, unrelated to my layer. That flag lets git join them.

This first take is by hand: your project holds no `/layer-update` yet. Every later take is `/layer-update`: 20.

Git stops once on each file we both hold. In my test project, that was `CLAUDE.md` and `.gitignore`, and nothing else. Join each by hand, then commit:

- `CLAUDE.md`: my sections first, then your project's own.
- `.gitignore`: your lines, then my four: `__pycache__/`, `.claude/settings.local.json`, `.claude/state/`, `node_modules/`.

## Name your project

Type `git branch`. It prints your branch's name, after a `*`. In my walks it printed `main`.

Then copy the sample into `.claude/project.json`:

```
cp .claude/project.example.json .claude/project.json
```

It names the project `Claude Layer Trial`, its branch `main`, and its shift 20000. Change the name and branch for your own project.

Then check the shift. Type:

```
python3 .claude/tools/ports.py free
```

It lists the shift each project on this Mac holds, then the lowest free one: `Free: 20000`. If it prints another, put that one in the file, so no two projects ever share a port.

The name is how 1100 calls your project, on your phone too. The branch is the only one `/8-ship` commits. With no file, `/8-ship` commits only a branch named `work`, and the name is your folder's.

The shift moves every port of this project by 20000, for good. Your 1100 answers on `http://localhost:21100`, and your prototypes app on 21400. So it runs beside another project's 1100, mine included. From here on, read every 1100 in this guide as 21100, and every 1400 as 21400. With a fixed shift, `/00-sessions-dashboard flip` is refused.

Then type:

```
python3 .claude/lib/project.py
```

It prints, as JSON, the nineteen facts my layer reads. `name` and `branch` are yours, and `shift` and `fixed` read 20000. The fifteen others keep their defaults, most of them empty, until you set them: `folders`, `roles` and `sites` for your ports; `band`, `command` and `match` for band 00; `database`, `docs`, `editor` and `workspace`; `color` and `glyph` for 1100's icon; then `home`, `hooks` and `usage`. Document 20 says what each sets.

## Install the zero-turn mod

In an iTerm2 terminal, at this project's root and outside Claude Code, type each line for account 1:

```
claude plugin marketplace add --scope local ./.claude/mods
claude plugin install --scope local zero-turn@layer-mods
```

The marketplace points to this project's `.claude/mods` folder. Keep that folder in place. `.claude/settings.json` already turns `zero-turn@layer-mods` on. Document 04 installs it on each extra account. Restart Claude Code after installation.

## Your first session

Started from 00's line, you are in it already: you started it there.

**Start Claude Code at your project's root.** In iTerm2, in your project's folder, type `claude`. A session started in a subfolder loads none of my hooks.

Plain `claude` starts on your first account, account 1. Document 04 starts the others.

**The trust dialog** (your hands). The first `claude` in a new project asks: "Is this a project you created or one you trust?" It warns that my `.claude/settings.json` pre-approves 70 tool permissions: the browser's. "No, exit" is picked. Press Down, then Return: "Yes, I trust this folder".

It asks once per project, on each account. A trusted folder above it never counts: my walks trusted `~/Projects`, and each new project there still asked. Skipped on an account, every launch there fails after 90 seconds: document 04.

Playwright, each session's own browser, then starts by itself. My settings approve it.

**Your status line.** Two lines under the prompt, drawn by my layer's settings. No setting of yours is needed. Yours read like this:

```
[1] 02 · Opus 5.5 xhigh
ctx:5%  5h:0%(4:20PM)  7d:59%(Mon 6:00PM)  $0.00
```

Line one: your account, your session's number, the model and its effort. Line two: how full the context is, your 5-hour and 7-day limits with when each resets, then what the session has cost so far.

`[1]` is your account's number, until you name it: document 04. A session on an account my layer does not know reads `[?]`. The model and effort are your own settings.

**Claim your number.** Type `/0-session-start 02`. A hook answers:

```
UserPromptSubmit operation blocked by hook: Session successfully renamed to 02.
```

Your session is now 02. The top edge of your prompt box shows `02` at once. A bare `/0-session-start` takes a free number from 02 up. No launch hands out 01: it is the advisor’s seat.

The status line shows it only after the session's first model turn: the claim spent none. Until then, line one holds no number, and line two shows `?` for each limit. Your first model turn comes in 05.

**Start 1100.** Type `/00-sessions-dashboard restart`. Then open `http://localhost:21100`. It opens on its Skills tab, with session 02 in its rail.

**Without the shift.** One project runs 1100 at a time. While another project answers on 1100, this start is refused, naming it:

```
Refused: <that project> already answers on 1100, from <its folder>. One project runs at a time: type /00-sessions-dashboard stop there first.
```

Do what it says, when you choose. That stop takes down that project's 1100 and its band 00.

## The app door, optional

The door lets a Claude desktop app chat, your app chat, read and act on your sessions. It is `.claude/tools/app-door.py`. It speaks MCP, the language the Claude app's connectors speak.

The app runs it on this Mac, through your project's own desktop extension, named for it: "Claude Layer Trial sessions" for this trial. It talks over a pipe only the app holds: no tunnel, no port, no key. Each project has its own extension.

In an iTerm2 terminal, at your project's root, type this. It packs the extension:

```
python3 .claude/tools/app-door.py extension
```

It prints the file's path, `.claude/state/door/claude-layer-trial-sessions.mcpb`, under your project's folder. Double-click it, and the Claude app installs it. Its tool permissions sit on its own page in the app.

The app chat cannot restart 1100. To keep 1100 up, hand that to launchd, the Mac's service manager. It needs a `python3` of 3.12 or newer, the one your shell finds:

```
python3 .claude/tools/app-door.py install
```

Killed or frozen, 1100 is back within ten seconds. Stopped on purpose, it comes back a minute later. Either way, without band 00. It starts again at each login.

Its label is `com.behaviour-layer.app-door.` followed by your project's name in lowercase. Each run of characters outside `a` to `z` and `0` to `9` becomes a dash. Leading and trailing dashes are dropped. For `Claude Layer Trial`, it is `com.behaviour-layer.app-door.claude-layer-trial`.

The door has a switch. `python3 .claude/tools/app-door.py shut` refuses every call, until `python3 .claude/tools/app-door.py open`. A new project's door starts open.

**Each chat's view.** Each app chat has its own view of 1100, and a view follows only its own chat. View 1 is `localhost:1100/?app`, view 2 is `?app=2`. For this trial, with its shift, they are `http://localhost:21100/?app` and `http://localhost:21100/?app=2`. The chat opens its view in the app's side panel.

**The app skill.** A new app chat starts its link through one app skill, `.claude/app-skills/start-app-link/SKILL.md`. Say "start app" for view 1, or "start app 2" for view 2.

Its line 14 is a stand-in: each of your project's names, its extension and its 1100, one step each. Fill it first: document 20 lists it. A ZIP built before then carries the stand-in unfilled.

Then type `/app-skill` in a session, naming that change. It writes the skill, and zips it as `.claude/app-skills/start-app-link.zip`. A fresh download holds no ZIP.

In the Claude app, upload that ZIP: Customize, then Skills, then **+**, **+ Create skill**, then **Upload a skill**. `/app-skill` hands you these steps, with the ZIP's whole path. Where the app shows Plugins in place of Customize, the way to upload is not found.

To stop an installed keep for good, replace `<its label>` with its label, then type these lines in Terminal:

```
launchctl bootout gui/$(id -u)/<its label>
rm ~/Library/LaunchAgents/<its label>.plist
```

## Unproven here

- `/layer-update` in a fresh clone, through this guide. My trial ran its tool in a scratch folder.
- Taking `main` with no GitHub account. My walk's Mac was signed in to GitHub.
- `git clone` into the folder. My walk ran `git init`, then `git pull`.
- A branch named other than `main`. My Mac's git takes `main` from Xcode's own settings.
- Joining the two files, and finishing the merge. My test proved only where git stops.
- A project already holding its own `.claude/` settings, skills or hooks.
- Copying the sample. My walk wrote the file by hand, named Newcomer Trial.
- 1100 starting on 21100 for a new project, through this guide. Another project of mine fixes the same shift, set by hand. No walk of this guide ran it.
- Without the shift: stopping my other project's 1100, so this one's starts. No walk stopped mine.
- Installing the zero-turn mod, and its answer to a session's Skill call. No walk tested either.
- Reusing its marketplace across projects, or moving its source folder. No walk tested either.
- The app door: its extension, its keep under launchd, open and shut, each chat's view, and the app skill's upload. No walk tested them.

## Check

- The top edge of your prompt box shows `02`. Your status line shows it too, once 05's first line has run.
- `http://localhost:21100` shows session 02.
- `python3 .claude/lib/project.py` prints your project's name and your branch.
