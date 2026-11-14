# 00 — Read me first

## Start here

On your Mac, in iTerm2, make an empty folder and start Claude Code in it. For a folder named `layer-trial`, in your home folder:

```
mkdir ~/layer-trial
cd ~/layer-trial
claude
```

If it asks whether you trust this folder, press Down, then Return: "Yes, I trust this folder".

Then give your Claude this one line, word for word:

```
Download the main branch of the public GitHub repository https://github.com/Ceasar369/claude-behavior-layer into this folder. It needs no GitHub account. Check that python3 is 3.12 or newer, and help me install it if not. Then tell me to restart Claude Code here. After the restart, read guide/00-read-me.md and walk me through every document in guide/, in order, one step at a time: explain each step, wait for me wherever it needs my hands, and run each document's check with me.
```

When it tells you to restart, type `/exit`. Then, in the same folder:

```
claude --continue
```

A plain `claude` would open a new conversation, without your line.

The trust dialog may ask again: press Down, then Return. Then type `Go on.` Your Claude reads this guide, and walks you through it, from here to 21.

## What my layer is

My layer is everything that shapes how my Claude Code sessions behave. It is three things:

- `CLAUDE.md`, at the root: what every session reads before its first word.
- `.claude/`: my rules, my skills, my hooks, and the code behind them.
- `knowledge/`: its front door, `MOC.md`, and the playbook, `knowledge/0010-playbook/`: how the work is run.

It holds my layer alone.

## Who this guide is for

Two readers, each on a Mac:

- You, in a project of yours.
- Me, in another project of mine.

Where my own path differs, a document says so, under "On my own Mac".

## What it gives you

- **A team.** Several Claude Code sessions, each in its own iTerm2 pane, each under a two-digit number.
- **Skills to run it.** One line launches a session, messages it, hands it over, or ends it.
- **An assistant.** One session plans the work as stages of sessions, writes each one's mission, and drives them to the end. It can run all night.
- **1100.** A page on your Mac, at `http://localhost:1100`. Every decision a session needs from you waits there.
- **My rules.** How a session talks to you, and how it reasons.

## How to take this guide

Twenty-two documents, one step each, in order. Each ends with a check you run with your Claude.

| Document | Its step |
|---|---|
| `00-read-me.md` | This one: your start, what my layer gives you, and how to take it |
| `01-how-it-thinks.md` | Sessions, skills, hooks and 1100, then my three rule files |
| `02-your-mac.md` | What your Mac needs, and three settings |
| `03-download-it.md` | My layer into your folder, your first session, and 1100 |
| `04-your-accounts.md` | One, two or three Claude accounts |
| `05-clarify.md` | A decision answered on 1100, then every clarify shape |
| `06-your-first-team.md` | Launch, message, end, hand over, save, stop |
| `07-thinker.md` | One subject thought through, round by round |
| `08-coder.md` | A small script, checked against the vault |
| `09-agenda.md` | Items for your agenda, then one triaged |
| `10-blurbs.md` | Files for ChatGPT, your Chrome, or another session |
| `11-handovers.md` | A session saved, resumed in a fresh one, then reported |
| `12-more-hands.md` | Work handed to a new session, followed, and read |
| `13-self-drive.md` | One task to its end, then the session stops itself |
| `14-teams.md` | A team of one mission, with a helper |
| `15-chrome.md` | A session in your own Chrome |
| `16-prototypes.md` | Your prototypes app, one generation, a lock-in |
| `17-your-first-night.md` | A plan of missions, driven while you sleep |
| `18-your-own-skill.md` | A skill of your own, proven in a fresh session |
| `19-the-doctor.md` | What you changed, checked against my rules |
| `20-make-it-yours.md` | Your own facts, settings and pieces, then my updates |
| `21-walks.md` | Your app walked by a walker, judged by one analyzer, then your marks |

Every step is an offer. Take what serves you, in your own time. Skip the rest.

A team that runs all night, on easy tasks, is document 17. Its own steps need only 02 to 04 before it.

Your Claude walks you through them in order, from the line above. You may also take any step yourself, or hand one document to any session in one line, the way each mission of mine starts:

```
Read guide/04-your-accounts.md whole, then do what it says.
```

A few steps need your own hands: a setting on your Mac, a dialog, a login. Each says so.

Each step here first ran in a throwaway project of mine, typed into a session of mine. What no walk ran is listed in its document, under "Unproven here".

My last walk followed this guide whole, start to end, as a newcomer would: on my Mac, on one account. Typed by hand, it takes about three hours. 16 is the longest, at an hour.

## Unproven here

- The start above: that line, given to a fresh Claude in an empty folder, and the restart after it. Nobody walked it yet.
- This guide on your own Mac. My walk ran on mine, beside my own 1100 and accounts.

## Check

Your computer is a Mac, and you work in iTerm2. Then every document applies.

On Windows or Linux, no pane opens and no wait wakes. Only my words travel there: `CLAUDE.md`, the rules and the playbook.
