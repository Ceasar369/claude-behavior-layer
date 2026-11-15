# 20 — Make it yours

My layer, turned into yours, one step after the other. Take any step, or none.

## 1. Who you are

Your `~/.claude/CLAUDE.md` loads in every project you start inside your home folder, on every account. Put there who you are, and how you want to be spoken to.

Mine says I am barely tech-savvy, so my sessions explain in plain words. That line sits in my own file, never in my layer. Your sessions talk at your level.

Each account may keep its own file too: account 2's is `~/.claude-acct2/CLAUDE.md`.

## 2. Your project's name, and your branch

`CLAUDE.md` opens on a stand-in: your project's name, as the title, then what it is, in a few lines.

`CLAUDE.md` also says your sessions work together on the `work` branch. Name yours there: the one `git branch` printed in 03. In my walk, the doctor caught this line: 19.

One line to any session does both. Mine, in my trial's words:

```
In CLAUDE.md, put this project's own name and words where the stand-in is: the title Claude Layer Trial, then one line, a throwaway trial of the layer, deleted after the walk. Then name main as the branch my sessions share, where it says work.
```

Put your own name, words and branch in place of mine. It wrote both, then marked the doctor's finding built in `agreed.md`: 19. It left the two examples in `thinking.md` that name `work`: they are only examples.

`AGENTS.md` is Codex's copy of `CLAUDE.md`, with one extra line telling it to read `.claude/rules/` first. Keep both files in step.

## 3. Your project's facts: the other stand-ins

A line opening `> **Stand-in.**` waits for your project's facts. Find them:

```
git grep -n "Stand-in"
```

The twenty-three lines opening `> **Stand-in.**` are yours. The others belong to my code and skills, or to this guide: leave them. On a fresh download, they are these:

| File | What goes there |
|---|---|
| `.claude/app-skills/start-app-link/SKILL.md:14` | Each of your project's names, its extension and its 1100, one step each |
| `.claude/skills/walk-drive/SKILL.md:86` | Each Prep your walks name, and the browser function it runs |
| `AGENTS.md:3` | Your project's name and what it is |
| `CLAUDE.md:3` | Your project's name and what it is |
| `knowledge/0010-playbook/0013-thinking/the-parts.md:15` | Your project's parts that run nowhere, beside Behaviour |
| `knowledge/0010-playbook/0015-coding/the-coding-axioms.md:47` | One layer of your project, and the one `code/` folder its session touches |
| `knowledge/0010-playbook/0015-coding/the-stack/the-formats.md:48` | Your project's currencies |
| `knowledge/0010-playbook/0015-coding/the-stack/the-screen/a-records-page.md:11` | What each of your records adds to its page |
| `knowledge/0010-playbook/0015-coding/the-stack/the-screen/the-screen-MOC.md:16` | Your own kinds of screen, one document each |
| `knowledge/0010-playbook/0015-coding/the-stack/the-stack-MOC.md:12` | `the-look.md`, once you write it: what every frontend looks like, and its token file |
| `knowledge/0010-playbook/0015-coding/the-stack/the-tools.md:90` | The languages every frontend carries |
| `knowledge/0010-playbook/0019-targeted/the-map/outside-the-project.md:9` | The folder your archives and references sit in, by its full path |
| `knowledge/0010-playbook/0019-targeted/the-map/outside-the-project.md:15` | Your archives, each folder and the trial it was |
| `knowledge/0010-playbook/0019-targeted/the-map/outside-the-project.md:21` | Your references folder, by its full path |
| `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md:34` | Your port digits: each one, its folder, and what it is |
| `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md:49` | Any folder taking site digits in place of roles |
| `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md:69` | A session's port, from your project's digits |
| `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md:85` | One backend's port, and the band 00 address it calls |
| `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md:105` | Your database, when you have one: its port, and what writes to it |
| `knowledge/0010-playbook/0019-targeted/the-map/the-browser.md:30` | Each Chrome profile on your Mac: its directory, and its Chrome label |
| `knowledge/0010-playbook/0019-targeted/the-map/the-browser.md:36` | Each site you sign into, its address, and the profile holding its login |
| `knowledge/0010-playbook/0019-targeted/the-map/the-repository.md:17` | Your folders under `code/`, each one and its layer |
| `knowledge/MOC.md:12` | Your own vault areas, `0020` to `0090`, one line each |

A project with no servers can leave the server lines as they are.

Before any new research, `thinking.md` sends a session to your references folder, and files new research there. Fill that line first, if you keep research.

Two links lead nowhere. One names a document your project writes under `walks/`. The other is a placeholder.

`the-stack/` holds my own stack's choices: its tools, its layout, its formats, its screens. Keep what fits your project, and rewrite the rest.

## 4. Your servers, in `.claude/project.json`

Document 03 set its name and branch. Every other key is optional too.

| Key | What it sets | With none |
|---|---|---|
| `ports` | `folders` and `roles`: the first and second digits your servers' ports may take; `sites`: a folder's own second digits, in place of the roles | 1100 alone; roles `1` backend, `2` frontend; no sites |
| `shift` | A shift every port always takes: 20000 puts 1100 on 21100. `flip` is then refused | The shift `flip` last wrote; else none |
| `band` | `servers`, `command` and `match`: what `/00-sessions-dashboard` starts as band 00, the one command it runs, and how the memory guard knows it | 1100 runs alone |
| `database` | `port`, `name` and `pg_isready`: the one database 1100's System page shows a dot for | No dot |
| `docs` | The docs folder `/coder-check` counts | None |
| `color` | The square of 1100's icon on your phone, as `#rrggbb` | Orange |
| `glyph` | What that icon draws: SVG markup, in Lucide's 24 by 24 stroke style | A rocket |
| `home` | The folder of the project that builds my layer, when it sits on your Mac. `/layer-send` leaves a fix there | The fix lands in your own project, to send by hand |
| `hooks` | Your own hooks, by event: section 6 | None |
| `own` | Folders an update leaves as you hold them: section 6 | None |
| `usage` | A shared usage reader on this Mac: a program's path, `~` for your home. `.claude/lib/accounts.py` reads through it | None |

Your prototypes app writes its own `band` entry: 16.

A port is four digits: folder, role, session. Session 05 on a frontend in folder 7 takes 7205. No two sessions collide. The shift adds to each: 20000 makes 7205 27205.

A running 1100 keeps the name it started with. `/00-sessions-dashboard restart` takes a new one.

## 5. Your agenda's topics

Until you name your topics, one stands in: Behaviour. Name yours in `.claude/state/agenda/topics.json`, beside the agenda's `README.md`: each topic's name and colour, then the screens an item may name. The README shows the shape. 1100 draws new topics after its next start.

## 6. Your own pieces beside mine

- **Your own facts.** `.claude/project.json` is yours alone. My updates never touch it.
- **Your own files.** Your own skills under new names, your own rules file in `.claude/rules/`, your own vault areas. New files never clash with my updates.
- **Your own hooks.** `.claude/settings.json` is mine, the same in every project. Leave it as it is. Name each hook of yours in `.claude/project.json`, under `hooks`, by its event:

```
"hooks": {
  "UserPromptSubmit": [{"file": ".claude/hooks/my-skill.py", "timeout": 60}],
  "PreToolUse": [{"file": ".claude/hooks/my-skill.py", "timeout": 60}]
}
```

My `.claude/hooks/own-hooks.py` runs them, on a session's start, a prompt, a Skill call, a Write or an Edit, and a stop. A skill of yours that answers as a hook takes the two lines above.

One more event is my layer's own: `AfterShip`. `/8-ship` runs each hook you name under it after a commit, and hands it the commit and its paths. Its last line joins the ship's answer. A project that publishes after a ship starts its publish there.
- **Your own folders.** `the-stack/` holds my stack's documents. Yours may sit in the same folder. Name it in `.claude/project.json`, and an update leaves it as you hold it:

```
"own": ["knowledge/0010-playbook/0015-coding/the-stack/"]
```
- **Your edits to my files.** Avoid them: every update then stops on that file. A fix to one of mine goes back to me instead, in section 8.
- **Your version of one of my skills.** A skill of the same name in your account's own folder beats the project's: `~/.claude/skills/` for account 1, `~/.claude-acct2/skills/` for account 2. It holds in all your projects, so use it rarely.

`/behaviour-doctor` checks what you change against my rules: 19.

## 7. The memory guard, if you want it

It freezes, then ends, a program eating memory before your Mac runs out. `.claude/tools/memory-guard.py` holds it. It is optional.

Its name is the same in every project. Installing it in a second project replaces the first's.

## 8. My updates

Once I push an update, take it in a session. Commit your own work first, with `/8-ship`. Then type:

```
/layer-update
```

It merges my newest `main` into your branch. When nothing is new, it answers "Up to date".

GitHub's own files, this guide, the README and the website among them, are never added to your project by an update. One you already hold stays as you hold it.

It stops on a file we both changed, and names each one. Your session lays each out, and you choose.

It ends on its checks, one line each: your facts print, my own checks pass on your files, 1100 draws, each stand-in still unfilled, and whether `CLAUDE.md` names your branch.

**A fix of yours, back to me.** You fixed one of my files, and every project should have it. Type:

```
/layer-send
```

It lists each file of mine your project changed since its last update. You pick. It writes one patch file. With `home` set in `.claude/project.json`, the patch lands in my project's inbox. With none, it lands in your `.claude/state/layer-outbox/`: send me that file.

Your project never pushes to my repository. Its remote `layer` only fetches, and my layer's guard refuses any push aimed there.

A change to the zero-turn mod lands once its `.claude/mods/zero-turn/.claude-plugin/plugin.json` version rises. Run this line in a terminal, from your project's folder, on each account:

```
claude plugin update zero-turn@layer-mods
```

For an extra account, start the line with its `CLAUDE_CONFIG_DIR`, as in 04.

## 9. Tell me what broke

Each break you meet is a fix for my layer too.

## Unproven here

- Your own servers on band 00, and the memory guard. My walks ran neither.
- 1100 taking a new name at its restart. My walks restarted no 1100.
- Your own agenda topics.
- A skill of yours beating mine of the same name, and `~/.claude/skills/` reaching your other accounts.
- `~/.claude/CLAUDE.md` for a project outside your home folder.
- `/layer-update` and `/layer-send` in a real project, from GitHub. My trial ran their tool in a scratch folder: an update with new commits, a clash, and a patch.
- A hook of your own, run by `own-hooks.py` inside a real session. My trial ran it in a scratch folder.
- An `AfterShip` hook, and a folder named under `own`, in a real project.
- Updating the zero-turn mod on each account. No walk tested it.
- `git grep -n "Stand-in"` in a real project of yours. My walk ran it on a fresh trial.

## Check

```
git grep -n "Stand-in"
```

Each line opening `> **Stand-in.**` that it still prints is one you chose to leave.
