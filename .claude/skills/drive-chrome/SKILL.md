---
name: drive-chrome
description: Drives my Chrome through a clicking session on Chrome's account, while you stay the thinker, in each profile the work needs. "Drive my Chrome …" means this skill.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: "[a profile or a site, then the work] — neither drives Default"
---

# Drive Chrome

Screen work takes two sessions. The thinker decides, and talks to me. A clicking session on Chrome's account browses and clicks as the thinker says, and saves what it captures.

Your number is NN, as `CLAUDE.md` defines it.

## Step 1 — Know your role

Your message names a session to report to → you are the clicking session. Step 3.

Otherwise → you are the thinker. Step 2.

## Step 2 — Research the route, then launch the clicking session

Before any click, research the route on each site the work touches: every page, in order, and every choice on it. Read the site's own help pages, the references first, as `.claude/rules/thinking.md` says under "Read before reasoning".

A route that forks, like a standard or an advanced sign-up, is settled here. The clicking session never picks one.

Run `python3 .claude/tools/chrome.py account`. It prints C, the account that drives my Chrome.

```
python3 .claude/tools/launch.py session --account C --model opus --effort low --name "<one to three words>" --message "/drive-chrome <my words, whole>. The route: <each page's address and each choice, in order>. Report to session NN."
```

It prints the pane, then the clicking session's number, MM.

Say one line: "Session MM clicks in your Chrome."

Invoke `session-control` with MM. Tell it each next step. Check every file its report names.

You drive it whole, never through me. Every step it can take goes to it, at once.

A step needing an inbox goes to it too: a code, a link, an email's source.

My hands come in only for a password, a card, an agreement in my name, or a delete.

It reports a page the route never named → research it before its next step.

It reports a wait for my hands → end your turn on its Action, whole. My word goes on to MM.

The work I asked is done → stop it. Undone → keep it in your wait, and tell me.

Nothing below is yours.

## Step 3 — Pick the profiles

A profile named → that one.

Each site the work touches → its row in `knowledge/0010-playbook/0019-targeted/the-map/the-browser.md`. An inbox is a site.

Nothing named → `Default`.

## Step 4 — Read each browser ID

Once per profile Step 3 picked.

```
python3 .claude/tools/chrome.py profile "<directory or label>"
```

It prints the profile's line, its browser ID third, then the line that opens its window.

Refused, no profile by that name → its reason, in one line, is your whole report. Go to Step 9.

Refused otherwise → wait for my hands.

## Step 5 — Select that browser

Load every Chrome tool the work needs in one ToolSearch call. Include `list_connected_browsers` and `select_browser`.

Call `list_connected_browsers`.

Its browser ID is missing → run the printed `open -na` line. A new window connects within seconds. List again until it shows.

Missing after several lists → wait for my hands.

Call `select_browser` with the browser ID of the site in hand. Each site switches to its own.

## Step 6 — Work in your own tabs

Call `tabs_context_mcp` with `createIfEmpty: true`. Its tab is yours.

My own tabs stay out of your reach.

Batch your steps in `browser_batch`.

Follow the route your message names, page by page. A page it never named → report it to the thinker, and wait.

A page asks me to sign in → wait for my hands.

A page waits on an emailed code or link → open that inbox in its profile, in a tab of your own. Type the code, or open the link. Then back to the route.

## Step 7 — Save what you capture

Take each screenshot with `save_to_disk: true`. It returns a path.

Copy each file into the folder my words name. Its name says what it shows.

No folder named → the references. `knowledge/0010-playbook/0019-targeted/the-map/outside-the-project.md` names its folder, and how a capture joins it.

## Step 8 — Close your tabs

Close every tab you opened, with `tabs_close_mcp`.

## Step 9 — Report

Your message names the thinker, MM:

```
python3 .claude/tools/panes.py say --to MM --line "Session NN reports: <what you did, and every file saved, by path>"
```

Then wait for its next step, or its stop.

## Wait for my hands

Only my hands clear a login page, a refused profile, or a window that never connects.

A login page → first reach every other site the work needs. Each login page keeps its own tab.

Then report to the thinker one Action naming every fix, and nothing else:

```
python3 .claude/tools/panes.py say --to MM --line "Session NN reports: waiting for your hands. Action: <every fix>"
```

- Login pages → "Action: sign into GitHub and Google in my tabs. Then type signed in."
- A refusal → the fix its reason names.
- A missing window → "Action: open the Work window, then type open."

Close no tab.

The thinker's word resumes the step that waited. Still blocked → wait again.

## Never

Never sign into a site. Never type a password or a card.

Never pay, accept an agreement, delete, or send from my inbox.

Never drive a profile Step 3 did not pick.

Never touch a tab you did not open.

Never talk to me. Your words go to the thinker.
