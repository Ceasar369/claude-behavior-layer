# 21 — Walks

Your app walked screen by screen, by a walker in its own hidden browser, and judged by the analyzer. Then your marks.

## What it does

A walk checks that your app does what its walk files say. You write the walk you need: one screen, one section, or the whole app.

Four roles, three sessions:

- **The lead** is the session you talk to, through `/7-walk`. It finds the walk, checks its files against your code with you, launches the walker, and reads the case.
- **The walker** is a session the lead puts on its launch page. It does each step to the word, in its own hidden Playwright browser, never in your Chrome. At every check it saves a screenshot and the page's text. It judges nothing.
- **The analyzer**, `.claude/agents/walk-analyzer.md`, is the one judge. The lead sends one for each slice of about 25 checks. Its verdict is the "Tester" mark. Yours is the "You" mark.
- **The reader** is a session the lead launches once a docs page's checks all hold. It brings you that page one section per turn, and you read every word yourself, on your docs site. It judges nothing.

My rules for it sit in `knowledge/0010-playbook/0017-walking/`. `CLAUDE.md` names `walks/`, the folder your walk files live in, outside the vault.

## What it needs

- Your app running on your Mac, at an address the walker can open.
- Playwright, each session's own browser, from my `.mcp.json`: 03.
- A way for the walker to get its own login: a login you make for it, or a command that makes one.

## Start your walks

In session 02:

```
/7-walk
```

With no `walks/` yet, it starts them. It copies my walks standard, `.claude/tools/walks-standard.md`, to `walks/walks-standard.md`. From then on the standard is yours: change it as your app needs. It writes `walks/walks-MOC.md`, then asks your first area, one question at a time.

An area is one part of your app with its own address, like `app/` or `admin/`. Its folder holds `before-you-start.md`, read by every session of a walk:

- **Where** · the address, and each server behind it.
- **Code** · where its screens' routes sit, and the file every quote comes from.
- **Logins** · each login a step names.
- **The walker's login** · how a walker makes its own.
- **Data** · how the test data is filled and reset.
- **Codes and links** · where an email's code or link comes from.
- **Marked** · every marked step.

## Your first walk

Name one screen:

```
/7-walk app the sign-in page
```

No step covers it yet, so `walk-write` writes its journey in the screen's section: its Start, its Prep, its steps, each "See" quoting your code's own words. It shows you each line no file rules, for your yes. `.claude/tools/walk-checklists.py` builds the section's `0-checklist.md`.

The lead then writes the walker's row on its launch page. Your move names it: pick the walker's account, then press Launch on 1100.

The walker walks one journey, then types one line into the lead's pane: how many checks, and any move it could not do. The lead sends the analyzer for each slice, writes the case under `.claude/state/walk-case/`, and brings you each issue, one at a time, with its screenshot on the walker's Screenshots tab.

A walker that cannot proceed asks the lead. The lead brings its question to you, then passes your answer back.

Once the issues are dealt with, it asks your yes on the rest, docs rows aside. Your yes writes ✅ in your column. A docs row's ✅ comes from your own read, through the reader.

An issue you rule becomes a fix. The lead writes the fixer's row on its launch page. On your yes, the lead types into the walker and the fixer itself. Once the fix ends, the lead asks your yes to walk the whole journey again.

At each journey's start, `.claude/tools/walk-clear.py` clears the walker's other journeys' evidence and its Playwright files. Its Screenshots tab then holds the current journey alone.

A section passed whole gets `walked.md`, until a step goes back to ⬜. A step marked "Server only" runs on the deployed server, not your laptop. Its "See" quotes what the laptop shows instead.

End it in the lead's chat: "End the walk." The lead keeps the walker's remaining evidence, then stops it. A dated copy of each area goes to your references, under `walks/`. Your `walks/` stays as it is.

## Make it yours

Everything your app adds lives in your `walks/walks-standard.md`, never in my skills: other roles' views, a languages and widths walk, outside services, a server only some steps walk on. Every walk session reads your standard first.

Docs pages are the exception: my skills walk them, and the reader brings each one to you. The walker reads a docs site built with Zudoku. A site built another way needs its own docs function, in `.claude/skills/walk-drive/SKILL.md`: `.claude/hooks/walker-scripts.py` lets a walker run only the scripts walk-drive names, copied whole.

Updating from an older layer? From your project's root, run this once. It rebuilds every checklist by the new rules:

```
python3 .claude/tools/walk-checklists.py
```

A walker's screenshots now sit one folder deeper, `walk/<area>/<section>/<journey>/`. Ones an older walker saved, one folder higher, no longer show on the Screenshots tab. The walker clears them at its next journey.

## Unproven here

- All of it, in a fresh project. No walk tested it there.
- The updated checklist and old screenshots. No walk tested the update.
- `/7-walk` starting `walks/` from my standard. Nothing ran it.
- `walk-write` writing a new area's folder from your answers. Nothing ran it.

## Check

- `walks/walks-standard.md` and `walks/walks-MOC.md` exist.
- Your first section's `0-checklist.md` lists its journey, with ⬜ for checks not yet passed.
