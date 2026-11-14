# Release validation

This public copy starts from committed source `d7c5a941`.
The export rules omit project code and live state.
They cut or replace each private example on the way.
No original working installation was changed.

## Before each push

Three checks stand before every push to this repository.

- The export refuses a file naming a private project, a person, or the author's home folder.
- A second pass reads every file of the branch for the same words, an email address, a home folder, or a key's shape.
- gitleaks then scans the folder for secrets.

The push runs only when all three are clean. It is never forced.

## Checks performed on this copy

| Check | Result |
| --- | --- |
| Whole-branch read: private words, emails, home folders, key shapes | 404 files read, none found |
| gitleaks secret scan | No findings |
| Python syntax | All 158 layer Python files parsed |
| JSON syntax | Five configuration/manifest files parsed |
| Configured hooks | All 36 run through `python3`, each path quoted |
| `walk-clear-test.py` | 7 passed |
| `drive-test.py` | 14 passed |
| `follow-test.py` | 41 passed |
| `launch-plan-test.py` | 48 passed |
| Full isolated check runner | Passed on macOS, Python 3.12 and 3.14, with an empty home folder |

Run the same isolated checks with:

```sh
python3 scripts/check.py
```

## Checks from v1.0.0, not repeated

These ran on the v1.0.0 snapshot, from committed source `289c5586`.
They were not run again on this copy.

| Check | Result at v1.0.0 |
| --- | --- |
| Quoted hook inside a fresh folder containing spaces | Passed |
| Sample project facts, branch and fixed port shift | Passed |
| Local marketplace and mod manifests | Validated using Claude Code 2.1.316 |
| Documented marketplace add and plugin install commands | Both succeeded at local scope |
| Installed plugin listing | Enabled, local scope, version 0.1.0 |
| Installation paths and symlinks | Entirely inside isolated trial |

Manifest validation used the existing native Claude Code installation.
A separate temporary `CLAUDE_CONFIG_DIR` isolated its settings.
The documented commands installed only into that isolated trial.
No plugin was installed into the user's existing configuration.
No login, trust, or macOS permission prompt occurred.
The trial also used a project folder containing spaces.

The trial sample uses branch `main` and fixed shift `20000`.
Its dashboard address is `http://127.0.0.1:21100`.
The runtime controller remains bound to the loopback interface.

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
