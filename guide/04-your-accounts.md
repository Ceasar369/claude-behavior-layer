# 04 — Your accounts

One, two or three Claude accounts, joined to my layer. Do this before any step launches a second session.

## What an account is

An account is one Claude login, kept in one folder on your Mac.

| Account | Its folder | How a session starts on it |
|---|---|---|
| 1 | `~/.claude` | `claude` |
| 2 | `~/.claude-acct2` | `CLAUDE_CONFIG_DIR=~/.claude-acct2 claude` |
| 3 | `~/.claude-acct3` | `CLAUDE_CONFIG_DIR=~/.claude-acct3 claude` |

My layer launches each session on one of them. `~/.claude-accounts.json` names them for it: one file per Mac, for every project. With no file, there is one account, 1, in `~/.claude`.

## One account

Nothing more is needed. Documents 02 and 03 did it all.

Your status line opens `[1]`, your account's number. To show your name and plan instead, write `~/.claude-accounts.json`. Type this line, with your name in place of `<your name>`, and your plan, like `20x`:

```
printf '%s\n' '{"accounts": {"1": {"folder": "~/.claude", "plan": "20x", "name": "<your name>"}}}' > ~/.claude-accounts.json
```

Its name starts with a dot, so Finder hides it. `cat ~/.claude-accounts.json` shows it.

The status line then opens with your name. 1100's System page shows your plan after `/00-sessions-dashboard restart`: 1100 reads the list once, as it starts.

## Each extra account: four acts

Account 2 is the example. A third is the same, with `3`.

**1. Its login, in its own folder** (your hands). In iTerm2, type:

```
CLAUDE_CONFIG_DIR=~/.claude-acct2 claude
```

The first time, it shows "Welcome to Claude Code", then a choice of text style, then its login. Log in with that account. Then type `/exit`.

Never move or rename that folder after its login. Claude Code keys the login's Keychain entry to the folder.

Never start account 1 with `CLAUDE_CONFIG_DIR=~/.claude`. Claude Code would then read another file, `~/.claude/.claude.json`, with a trust list of its own. Account 1 starts with plain `claude`.

**2. Its zero-turn mod** (your hands). Outside Claude Code, in an iTerm2 terminal at your project's root, type each line:

```
CLAUDE_CONFIG_DIR=~/.claude-acct2 claude plugin marketplace add --scope local ./.claude/mods
CLAUDE_CONFIG_DIR=~/.claude-acct2 claude plugin install --scope local zero-turn@layer-mods
```

Use account 3's folder for account 3. The marketplace points to this project's `.claude/mods` folder: keep it in place. New sessions load the mod after installation.

**3. Its trust, in each project** (your hands). In your project's folder, type the same line:

```
CLAUDE_CONFIG_DIR=~/.claude-acct2 claude
```

The trust dialog of 03 shows again, though account 1 trusts the project. Each account keeps its own trust list. Press Down, then Return. Then type `/exit`.

Skipped, every launch on that account stops at the dialog, and never claims its number. After 90 seconds, the launch page says: "failed: 05 never claimed its number."

**4. Its line in the list.** Write both accounts into `~/.claude-accounts.json`. This line replaces the whole file, the one-account line included:

```
printf '%s\n' '{"accounts": {"1": {"folder": "~/.claude", "plan": "20x", "name": "<your name>"}, "2": {"folder": "~/.claude-acct2", "plan": "20x", "name": "<its name>"}}}' > ~/.claude-accounts.json
```

A number is one digit, 1 to 9. A folder starts with `~` or `/`. Two accounts never share a folder.

Skipped, my layer never uses that account. A session you start on it by hand reads `[?]`, and my layer never sees it run.

## Then, on 1100

Type `/00-sessions-dashboard restart`. Each account then shows on 1100: a pill on the launch and handover pages, `claude-1`, `claude-2`, and a card on System, at `http://localhost:1100/system`.

On System, set an order: type `1 2` in its order box, then Save. Each launch naming no account takes the next turn. With no order, every launch takes account 1.

The box shows `1` in grey. It is only an example. A number your list lacks turns red.

Three accounts take an order such as `3 2 1 3 2`. Each account's share of the turns is its share of the launches.

## Auto mode, on each account

From Claude Code 2.1.283, nothing to set: 02.

## Chrome, with several accounts

One account drives your Chrome: the list's `chrome`, else account 1. To move it, add `"chrome": "2"` beside `"accounts"`. Then sign the Claude in Chrome extension, in each profile, into that account's login. Document 15 uses it.

## Removing an account

Take its line out of the list, then restart 1100. Its turns stay in the order, and are passed over.

## On my own Mac

My list already holds my three accounts. It is one file per Mac, so a new project of mine sees all three. I never type this document's list lines: each replaces the whole list.

Each project keeps its own order, in its own `.claude/state/accounts/order.json`. A new project starts with none: every launch takes account 1. I set its order on its own System page.

Each of my accounts trusts the new project once: act 3, on accounts 2 and 3.

## Unproven here

- Logging an account in, and `/exit` after it. My walk logged nothing in.
- Installing the zero-turn mod on an extra account. No walk tested it.
- Yes at the trust dialog on a second account. My walk only saw the dialog show.
- A launch failing on an account that never trusted the project. The 90 seconds come from my code.
- Typing the order, and pressing Save. My walk set it through the same code.
- 1100's restart showing a new account. My walk drew it on a fresh copy of 1100.
- Moving Chrome to another account.
- Writing the list with these lines. My Mac's list was written long ago.

## Check

- 1100's System page shows one card per account in your list.
- Its launch page, behind Launch under the utilities button, shows one pill per account.
- On each extra account, `CLAUDE_CONFIG_DIR=~/.claude-acct2 claude` at your project's root opens with no trust dialog. Type `/exit`.

Opening the launch page the first time installs iTerm2's Python package into `.claude/state/iterm/venv`: 20 MB, over the network, once per project. The page reads, splits and rearranges your panes through it. It needs version 1.14 or newer.
