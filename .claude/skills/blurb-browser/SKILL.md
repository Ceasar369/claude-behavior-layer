---
name: blurb-browser
description: Writes a file of lines to paste into a session holding my Chrome.
allowed-tools: Read, Glob, Grep
argument-hint: "[what the session does in Chrome] — and which pages it visits"
---

# Blurb Browser

A few lines I paste into a session holding my Chrome. One file holds them alone.

## Step 1 — Take my line as the instruction

It names what the session does in Chrome, and which pages.

Trust it.

## Step 2 — Ground every address

Read the file holding a route or a port before naming it.

Never write an address from memory.

A local address is derived, never chosen. The scheme sits in
`knowledge/0010-playbook/0019-targeted/the-map/running-locally.md`.

## Step 3 — Know the reader

The reader holds my Chrome, and nothing of this repo.

It reads no vault. It has not seen this session.

The blurb carries every fact the work needs.

## Step 4 — Name the sites first

The extension asks me for a site before it acts there.

List every site the work touches, one per line.

A site I have not granted stops the work.

## Step 5 — Name the stops in order

One line per stop. Its address, then what happens there.

A stop that only looks says look.

A stop that types names the field and the value.

## Step 6 — Name what comes back

Say what the session reports, and in what shape.

A screenshot, a console line, a page's text. Name which.

## Step 7 — Write it as me

`.claude/rules/talking.md` rules the
voice, under "Writing for another reader". Follow it.

## Step 8 — Write the file

My number, as `CLAUDE.md` defines it.

```
python3 .claude/tools/blurb.py NN browser <<'EOF'
<the blurb>
EOF
```

The blurb alone goes on stdin. No intro, no markers.

The tool puts my rule files above it: this repo's `CLAUDE.md`, its Communication section alone, then every other `CLAUDE.md` Claude Code loads and `.claude/rules/`, each in full.

It prints the file's path.

## Step 9 — Name it in chat

One line: the file's path.

## Never

Never put the blurb in chat.

Never write the blurb file with Write or Edit. The tool writes it.

Never name an address I have not read.

Never send the session at an element that opens a dialog. A dialog blocks
the extension, and nothing reaches it afterwards.
