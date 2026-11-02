# The Browser

Up: [[the-map-MOC|The Map]]

Where my logins live. Which Chrome profile holds which site, and which session reaches it.

## Two browsers

Playwright is a session's own hidden browser. `.mcp.json` starts one for each session.

It holds no login. A page behind one shows signed out.
My Chrome holds my logins. A session reaches it through the Claude in Chrome extension.

## The listed account reaches my Chrome

Each Chrome profile holds its own copy of the extension.

A copy is signed into one Claude account. A session reaches only the copies signed into its own.

Only the account the list names drives my Chrome: `~/.claude-accounts.json`, under `chrome`.

A profile is reachable when its extension is signed into the account the list names, and its window is open.

Each reachable profile is a browser of its own, with its own browser ID.

`.claude/tools/chrome.py` reads each profile's browser ID, and the account it is signed into.

## The profiles

> **Stand-in.** Each Chrome profile on this Mac: its directory, and its Chrome label.

The directory is the identity. The label is what Chrome shows.

## Sites, by profile

> **Stand-in.** Each site I sign into, and the profile holding its login.

A site holds its login in its profile alone.
