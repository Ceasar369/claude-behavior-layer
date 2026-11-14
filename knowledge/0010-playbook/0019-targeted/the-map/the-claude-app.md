# The Claude App

Up: [[the-map-MOC|The Map]]

Where my Claude app's pieces live: its skills, its settings, its extension, and the pages about them.

## Its skills

Every skill I upload to the app sits in `.claude/app-skills/`, in a folder named as the skill, its ZIP beside it.

The skill that starts my app link, a chat that runs my sessions and 1100, is `.claude/app-skills/start-app-link/SKILL.md`.

The Claude Code skill `app-skill` writes each one, and its ZIP.

## Its settings

`.claude/app-settings/` holds the text of the app's settings. `set-a-memory-import.txt` is its memory import, and `set-b-instructions.txt` its Instructions.

## Its extension

Each project reaches the desktop app through its own desktop extension, named for it, like "My project sessions". The app runs it on my Mac.

The extension runs the door, `.claude/tools/app-door.py`. `app-door.py extension` packs it. Its tools, and three of the app's own, show_widget, send_later and SendUserMessage, are everything the app chat can do. Its browser panel keeps 1100 open.

The app chat's rules are `.claude/tools/app-rules.md`. It reads them through the door's `read_rules`, fresh each chat.

The extension's tool permissions sit on its own page in the app.

## What shapes it

No door tool waits.

Nothing types into the Claude app. The app chat reads a session when I ask, and again when a reminder it set with send_later comes back.

Each app chat has its own view of 1100: `localhost:1100/?app` is view 1, `?app=2` is view 2. A view follows only its own chat. The chat opens it in the app's side panel.

`.claude/tools/app-door-test.py` fails when 1100 gains a button no door tool covers.

## The pages about it

Anthropic's own pages about the app are captured in the references, each set listed in its MOC.
