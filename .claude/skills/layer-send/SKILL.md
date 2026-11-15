---
name: layer-send
description: Sends a fix this project made to a shared layer file back to the layer's builder, as a patch. "Send it to the layer" means this skill.
allowed-tools: Read, Bash, Skill
argument-hint: "[the files to send] — omit to list what changed"
---

# Layer Send

## Step 1 — List what changed

Run `python3 .claude/tools/layer.py send`.

It names no file, or refuses → say its line, and stop.

## Step 2 — Pick what goes

I named the files → go to step 3.

Otherwise sort each file it listed.

- A fix every project wants → it goes.
- A stand-in this project filled, or a line true only here → it stays.

Run `clarify-items`, one item per file that goes, or per group sharing one fix. Its `today` quotes the changed lines. Files that stay are named in one line, with why.

## Step 3 — Send

Run `python3 .claude/tools/layer.py send PATH ...` on the files I agreed.

Say its line. It names the patch file, and where it landed.

It landed in this project's own outbox → my move is to send that file to the layer's builder.

## Never

Never send a file I have not agreed.

Never send a line naming this project, its people or its code. Say so, and leave the file out.
