# The Change Policy

Up: [[securing-MOC|Securing]]

How a change reaches a server.

## From git alone

Every change reaches a server from git, through the deploy tool.

The owner approves each live deploy.

## The gates

A deploy passes its checks first: secrets, dependencies, specs, types, lint, tests.

A deploy refuses an edited old migration.

A deploy runs a quick live test. On failure, it rolls back.

## GitHub's checks

Every push runs the checks on GitHub.

A failed check is fixed before the next deploy.
