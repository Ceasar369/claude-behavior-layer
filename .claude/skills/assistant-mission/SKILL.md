---
name: assistant-mission
description: Writes the one file a launched session reads first, its mission, from my rulings.
allowed-tools: Read, Glob, Grep, Write, Edit
argument-hint: "A1 — the mission to write; one whose stage is not next gets its notes"
---

# Assistant Mission

## Step 1 — Take the mission

My number, NN, as `CLAUDE.md` defines it. My folder is `.claude/state/sessions/NN/`.

The id finds its entry in `.claude/state/sessions/NN/stages.json`: its name, its stage, its `file`.

It goes out now → Step 2: its stage goes out, or, in an open plan, I ruled it.

Otherwise → Step 5.

## Step 2 — Ground it

Read every ruling it carries: my rulings in chat. Read its notes too: each is what a session taught, a claim, never my ruling.

Read every file it will name. Never state a fact from memory.

## Step 3 — Write the mission

Write its `file` with the Write tool. These sections, in order:

1. `# <id> — <name>`, then one paragraph: what you build, and who starts with you.
2. `## Read first, whole` — `CLAUDE.md`, `knowledge/MOC.md`, `.claude/rules/talking.md` and `.claude/rules/thinking.md`, then every ruling and file this work stands on. A mission building from a locked-in prototype names its winner's file. A mission that codes ends it with: "Then run `/5-coder`, before you write any code." A walk mission names `knowledge/0010-playbook/0015-coding/coding-protocols/protocol-walk-and-close.md`.
3. `## Your folder` — the parts you write. Nothing else is yours. A mission whose work spans two parts that never share a file may grant one of them to a helper, in one more line: "A helper may take <part>, through `helper-session`." A walk mission's folder holds its record, and grants its helper: "A helper may take the parts your walk's build lines need, through `helper-session`." A prototype mission's folder holds its subject, and its subject's own rules: The Screen in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/` when it exists, or the page rules atop `.claude/lib/page.py`. A helper is granted only while its stage's missions and helpers stay at nine or fewer.
4. `## Your ports` — your derived ports, from `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md` when it exists.
5. `## The work, in order` — one `###` per step. Each names its edge cases, each with its answer, and ends with its check. A step that removes or ends something ends with two checks, one for the act and one for its reason, each naming where its proof was read. A step two missions meet at names the other mission, and who goes first. It never restates what `5-coder`'s path holds: a gate, a walk, band 00, a trap. A walk mission's work never restates its protocol. A prototype mission's work is one step: run `/4-prototype` with what it prototypes.
6. `## Report` — "When the work is done, run `/session-report`." Then each part its report holds beyond what changed and each check with its proof, one line each.
7. `## Rules you keep` — technical choices are yours; one that changes what a person sees comes to me first. Talk to me through `/2-clarify`. Never write outside your folder. Never commit. Another session's change outside your folder is ignored, never repaired. When I say you are done, run `/9-session-stop`.

## Step 4 — Write it as me

`.claude/rules/talking.md` rules the voice, under "Writing for another reader". Follow it.

## Step 5 — Start its notes

Write its `file` with one heading, `# <id> — <name> · notes`, and one line: what it will build.

A finished session adds what this mission must know, one bullet each.

When its stage goes out, the notes become the mission. None of them stays behind as notes.

## Never

Never invent a ruling. A decision not yet made is asked, never written.

Never do the work itself.
