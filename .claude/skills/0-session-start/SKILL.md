---
name: 0-session-start
description: Claims this session's number and names its tab. "Start this session" means this skill, with or without a number. Pass one to three words naming the work I asked for.
allowed-tools: Read
argument-hint: "[NN] [one to three words naming the work, or keep] — omit NN for the lowest free side number; NN keep takes seat NN over: ends its session, keeps its folder and name"
---

# 0 — Session Start

This skill's work is done before you read this.

`.claude/hooks/0-session-start.py` claims the number, writes its record,
and sets the title.

Reaching this line means the hook did not fire. Report that, and stop.
