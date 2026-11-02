---
name: handover-prepare
description: Saves this session's conversation so a fresh session continues it later, through handover-resume; it launches nothing, and leaves this session running. "Prepare the handover" means this skill.
allowed-tools: Read
argument-hint: "[account A] [model M] [effort E] — the successor's, kept for handover-resume; a bare effort word counts; a model or effort left out keeps what this seat was named, else System's; system takes System's"
---

# Handover Prepare

This skill's work is done before you read this.

`.claude/hooks/handover-prepare.py` copies the conversation into
`handovers/`, and keeps the successor's settings.

Reaching this line means the hook did not fire. Report that, and stop.
