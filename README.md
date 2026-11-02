# My Claude setup

This is how I set up Claude Code.
It works well for me on my own projects.
I also tried it with [Blindfold Chess](https://github.com/Ceasar369/blindfold-chess).
That worked well for me too.

I’m sharing it in case someone else finds it useful.
You can use the parts that help you.
Some parts are specific to my Mac and terminal setup.

[Project page](https://ceasar369.github.io/claude-behavior-layer/) · [Setup](#try-it-locally)

## Rules and tools

The main pieces are:

- My rules for how Claude answers and reasons.
- Workflows for planning, coding, prototypes, and checking an app.
- Local pages for questions, decisions, and session progress.
- Tools for starting sessions and handing work between them.

The full setup uses macOS, iTerm2, and Claude Code.
The rules and workflow files can also be read separately.

<details>
<summary>A screenshot of the local page</summary>

![My local Skills page, filtered for assistant](docs/images/current-layer.jpg)

This screenshot uses empty sample sessions.

</details>

## Blindfold Chess

I wanted a chess trainer for my own practice.
I used this Claude setup while making it.

You can [play it](https://ceasar369.github.io/blindfold-chess/) or [read the code](https://github.com/Ceasar369/blindfold-chess).
You can also download it and run it locally.

## Try it locally

Use a separate trial folder first.
The full environment requires **macOS and iTerm2**.
Install **Python 3.12+**, **Node.js 22+**, **git**, and current **Claude Code**.
A Claude Code account is needed for live conversations.

Check the commands your terminal will use:

```sh
command -v python3 claude node npx git
python3 --version
claude --version
node --version
```

The plugin manifests were validated with Claude Code **2.1.316**.
An older `claude` earlier on PATH needs updating.
Use Anthropic's [installation instructions](https://code.claude.com/docs/en/setup).

Download the public source and prepare its trial configuration:

```sh
git clone https://github.com/Ceasar369/claude-behavior-layer.git
cd claude-behavior-layer
cp .claude/project.example.json .claude/project.json
python3 scripts/check.py
python3 .claude/lib/project.py
```

The sample names the project **Claude Layer Trial**.
Its branch is **main**; its dashboard uses port **21100**.
That keeps the trial separate from another project's port 1100.
Change the sample's name and branch for your own project.

In iTerm2, open **Settings → General → Magic**.
Enable **Python API**, following [iTerm2's documentation](https://iterm2.com/python-api/tutorial/running.html).
The first pane operation installs the `iterm2` Python package.
macOS may request permission for Python to control iTerm2.

Read the [communication rules](.claude/rules/talking.md) and [reasoning rules](.claude/rules/thinking.md).
Review [project settings](.claude/settings.json) before trusting the folder.
They enable hooks and approve the isolated Playwright browser's tools.

From the trial folder, install the included local mod:

```sh
claude plugin marketplace add --scope local ./.claude/mods
claude plugin install --scope local zero-turn@layer-mods
claude
```

Keep this checkout in place while its local marketplace is installed.
Start Claude from the repository root in iTerm2.
Complete Claude's project-trust and MCP prompts yourself.
Playwright may download Chromium on its first browser use.

Inside Claude Code, run these commands separately:

```text
/0-session-start 02
/00-sessions-dashboard restart
```

Open **http://127.0.0.1:21100**.
The dashboard should show your numbered session.
Try `/2-clarify` with one decision you want explained.

The dashboard can control local sessions and inspect their files.
Keep its controller local; the public site is a static preview.

## Checks and limits

```sh
python3 scripts/check.py
```

This parses 101 Python files and five JSON files.
It runs 49 existing tests using isolated temporary fixtures.
The checks passed on macOS with Python 3.12 and 3.14.
The mod and marketplace validate under Claude Code 2.1.316.
Its documented local installation commands also passed an isolated trial.
A fresh folder containing spaces also passed its hook/configuration checks.

These checks do not start real Claude conversations or panes.
Playwright/MCP startup was not exercised in these checks.
Complete first-run iTerm2, macOS, and Claude prompts during setup.
See [release validation](VALIDATION.md) for exact checks and limits.
Optional Dock, phone, and external-provider integrations require separate configuration.
The full environment uses macOS-specific file watchers and terminal tools.

Live conversations, account files, and runtime state stay outside git.
The sample settings are separate from my own working installation.

MIT license. See [LICENSE](LICENSE).
