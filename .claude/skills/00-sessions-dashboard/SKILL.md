---
name: 00-sessions-dashboard
description: Starts, reports or stops the sessions dashboard.
allowed-tools: Read
argument-hint: "status | restart | stop | flip — omit to start the dashboard and the project's band 00, restarting whatever answers; restart swaps 1100 onto the code on disk; stop takes down 1100 and band 00; flip moves both to the shifted ports, 21100 for 1100, or back, and is refused where project.json fixes the shift"
---

# 00 — Sessions Dashboard

This skill's work is done before you read this.

`.claude/hooks/00-sessions-dashboard.py` does it.

Reaching this line means the hook did not fire. Report that, and stop.
