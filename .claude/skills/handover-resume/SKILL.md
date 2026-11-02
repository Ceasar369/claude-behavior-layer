---
name: handover-resume
description: Hands a prepared session's seat to a fresh successor, from any session, and closes its pane. "Resume the handover" means this skill.
allowed-tools: Read
argument-hint: "NN [account A] [model M] [effort E] — NN is the prepared session; each setting left out takes resume.json, then what NN was named, then its default; system takes System's"
---

# Handover Resume

This skill's work is done before you read this.

`.claude/hooks/handover-resume.py` launches the successor, which takes the
seat.

Reaching this line means the hook did not fire. Report that, and stop.
