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

The nineteen lines opening `> **Stand-in.**` are yours. The others belong to my code and skills, or to this guide: leave them. On a fresh download, they are these:

| File | What goes there |
|---|---|
| `.claude/app-skills/start-app-link/SKILL.md:14` | Each of your project's names, its extension and its 1100, one step each |
| `.claude/skills/walk-drive/SKILL.md:86` | Each Prep your walks name, and the browser function it runs |
| `AGENTS.md:3` | Your project's name and what it is |
| `CLAUDE.md:3` | Your project's name and what it is |
| `knowledge/0010-playbook/0013-thinking/the-parts.md:15` | Your project's parts that run nowhere, beside Behaviour |
| `knowledge/0010-playbook/0015-coding/coding-MOC.md:12` | `the-stack/`, once you write it: what your code is built with |
| `knowledge/0010-playbook/0015-coding/the-coding-axioms.md:47` | One layer of your project, and the one `code/` folder its session touches |
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

Five links lead nowhere. They name documents your project writes under `the-stack/` or `walks/`, or a placeholder.

## 4. Your servers, in `.claude/project.json`

Document 03 set its name and branch. Every other key is optional too.

| Key | What it sets | With none |
|---|---|---|
| `ports` | `folders` and `roles`: the first and second digits your servers' ports may take; `sites`: a folder's own second digits, in place of the roles | 1100 alone; roles `1` backend, `2` frontend; no sites |
| `shift` | A shift every port always takes: 20000 puts 1100 on 21100. `flip` is then refused | The shift `flip` last wrote; else none |
| `band` | `servers`, `command` and `match`: what `/00-sessions-dashboard` starts as band 00, the one command it runs, and how the memory guard knows it | 1100 runs alone |
| `database` | `port`, `name` and `pg_isready`: the one database 1100's System page shows a dot for | No dot |
| `docs` | The docs folder `/coder-check` counts | None |
| `dock` | `editor` and `workspace`: what a click on the Dock app opens | No editor opens |
| `usage` | A shared usage reader on this Mac: a program's path, `~` for your home. `.claude/lib/accounts.py` reads through it | None |

Your prototypes app writes its own `band` entry: 16.

A port is four digits: folder, role, session. Session 05 on a frontend in folder 7 takes 7205. No two sessions collide. The shift adds to each: 20000 makes 7205 27205.

A running 1100 keeps the name it started with. `/00-sessions-dashboard restart` takes a new one.

## 5. Your agenda's topics

Until you name your topics, one stands in: Behaviour. Name yours in `.claude/state/agenda/topics.json`, beside the agenda's `README.md`: each topic's name and colour, then the screens an item may name. The README shows the shape. 1100 draws new topics after its next start.

## 6. Your own pieces beside mine

- **Your edits to my files.** Each merge keeps them. Git stops on a line we both changed, and you choose.
- **Your own files.** Your own skills under new names, your own rules file in `.claude/rules/`, your own vault areas. My updates never touch them.
- **Your version of one of my skills.** A skill of the same name in your account's own folder beats the project's: `~/.claude/skills/` for account 1, `~/.claude-acct2/skills/` for account 2. It holds in all your projects, so use it rarely.

`/behaviour-doctor` checks what you change against my rules: 19.

## 7. The memory guard, if you want it

It freezes, then ends, a program eating memory before your Mac runs out. `.claude/tools/memory-guard.py` holds it. It is optional.

Its name is the same in every project. Installing it in a second project replaces the first's.

## 8. My updates

Once I push an update, take it from GitHub:

```
git fetch https://github.com/Ceasar369/claude-behavior-layer.git main
git merge --allow-unrelated-histories FETCH_HEAD
```

When nothing is new, the merge answers "Already up to date." My walk's did, from GitHub.

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
- An update that brings new commits from GitHub. My walk's update found nothing new.
- Updating the zero-turn mod on each account. No walk tested it.
- `git grep -n "Stand-in"` in a real project of yours. My walk ran it on a fresh trial.

## Check

```
git grep -n "Stand-in"
```

Each line opening `> **Stand-in.**` that it still prints is one you chose to leave.
