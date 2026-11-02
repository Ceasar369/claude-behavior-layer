# Release validation

This public snapshot starts from committed source `289c5586`.
The existing export rules omit project code and live state.
Six additional redactions replace private examples and test-fixture paths.
No original working installation was changed.

## Candidate fixes

- Run all 33 configured Python hooks through `python3`.
- Quote their project paths, including folders containing spaces.
- Provide `.claude/project.example.json` for a separate trial.
- Add `scripts/check.py` and a macOS source-check workflow.
- Document setup, permissions, sample ports, and tested limits.
- Add the local mod's README, author, and MIT metadata.

The trial sample uses branch `main` and fixed shift `20000`.
Its dashboard address is `http://127.0.0.1:21100`.
The runtime controller remains bound to the loopback interface.

## Checks performed

| Check | Result |
| --- | --- |
| Export contents plus documented redactions | 271 source files matched |
| Known credential, JWT, and private-key pattern scan | No matches |
| Personal absolute paths | Generic documentation examples only |
| Python syntax | All 101 layer Python files parsed |
| JSON syntax | Five configuration/manifest files parsed |
| `walk-clear-test.py` | 7 passed |
| `drive-test.py` | 5 passed |
| `follow-test.py` | 31 passed |
| `launch-plan-test.py` | 6 passed |
| Full isolated check runner | Passed on macOS, Python 3.12 and 3.14 |
| Quoted hook inside a fresh folder containing spaces | Passed |
| Sample project facts, branch and fixed port shift | Passed |
| Local marketplace and mod manifests | Validated using Claude Code 2.1.316 |
| Documented marketplace add and plugin install commands | Both succeeded at local scope |
| Installed plugin listing | Enabled, local scope, version 0.1.0 |
| Installation paths and symlinks | Entirely inside isolated trial |

Run the same isolated checks with:

```sh
python3 scripts/check.py
```

Manifest validation used the existing native Claude Code installation.
A separate temporary `CLAUDE_CONFIG_DIR` isolated its settings.
The documented commands installed only into that isolated trial.
No plugin was installed into the user's existing configuration.
No login, trust, or macOS permission prompt occurred.
The trial also used a project folder containing spaces.
The native executable was invoked directly to verify version 2.1.316.
A PATH-selected older Homebrew binary was also detected.
The README therefore asks readers to check their CLI version.

## Scope of these results

The test suites use temporary fixtures and mocked session operations.
They do not open, rearrange, or type into real panes.
No new-machine macOS permission flow was completed.
No live Claude model conversation was started.
The bundled Playwright/MCP launch configuration remains runtime-unverified here.
No optional Dock, phone, or external-provider integration was exercised.
A pattern scan cannot prove the absence of every secret.

The complete controller targets macOS, iTerm2, and Claude Code.
Its file watcher uses macOS kqueue APIs.
CI runs the isolated tests on macOS for that reason.
The public website is separate static content under `docs/`.
