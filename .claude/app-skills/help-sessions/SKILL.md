---
name: help-sessions
description: Helps with the sessions named, and keeps them for the chat. Use for "help me with session 01", "help me with 40 and 50", "help me with all idle sessions", or "help me" alone.
---

# Help sessions

You help me answer the sessions I name. My app rules still hold whole, their six-line limit too.

## Keep my sessions

1. "Help me with 01 and 70" → keep 01 and 70 for this chat.
2. "Help me" alone → the sessions you keep.
3. "Add 80", "drop 70" → change the kept set. A new list replaces it.
4. "All idle sessions" → call `list_sessions`. Take every session waiting on me.
5. A session I name but you never kept → help with it once. The kept set stays.

## Read each one

1. Call `read_session` on each, fresh, every time. Never answer from your last read.
2. Call `read_wave` on each. Note whether a wave waits on me.

## Say each one in one line

1. One line per session: where it stands, and my next act. "Session 01: wave 54 waits on you, four items."
2. A session still working → "Session 40 is still working." Nothing more on it.
3. Several sessions → one last line: the one I answer first. What unblocks the most, then what has waited longest.

## Its wave

1. One session alone, with a wave waiting on me → skip its line. Bring its wave, as my app rules' Waves say.
2. Several sessions → bring no wave until I name one.
