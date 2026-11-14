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

It goes out now → Step 2: its stage goes out, or, in an open plan, I ruled it, or a night drive is being prepared.

Otherwise → Step 5.

## Step 2 — Ground it

Read every ruling it carries: my rulings in chat. Read its notes too: each is what a session taught, a claim, never my ruling.

Read every file it will name. Never state a fact from memory.

## Step 3 — Write the mission

Write its `file` with the Write tool. These sections, in order:

1. `# <id> — <name>`, then one paragraph: what you build, and who starts with you.
2. `## Read first, whole` — `CLAUDE.md`, `knowledge/MOC.md`, `.claude/rules/talking.md` and `.claude/rules/thinking.md`, then every ruling and file this work stands on. A mission building from a locked-in prototype names its winner's file. A mission that codes ends it with: "Then run `/5-coder`, before you write any code." A walk mission names `knowledge/0010-playbook/0015-coding/coding-protocols/protocol-walk-and-close.md`.
3. `## Your folder` — the parts you write. Nothing else is yours. A mission whose work spans two parts that never share a file may grant one of them to a helper, in one more line: "A helper may take <part>, through `helper-session`." A mission holding known parallel work grants one line per piece, and names `knowledge/0010-playbook/0011-assisting/assisting-protocols/protocol-swarming.md` in its reads. A walk mission's folder holds its record, and grants its helper: "A helper may take the parts your walk's build lines need, through `helper-session`." A prototype mission's folder holds its subject, and its subject's own rules: The Screen in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/` when it exists, or the page rules atop `.claude/lib/page.py`. A helper is granted only while its stage's missions and helpers stay at nine or fewer.
4. `## Your ports` — your derived ports, from `knowledge/0010-playbook/0019-targeted/the-map/running-locally.md` when it exists.
5. `## The work, in order` — one `###` per step. Each names its edge cases, each with its answer, and ends with its check. A step that removes or ends something ends with two checks, one for the act and one for its reason, each naming where its proof was read. It never restates what `5-coder`'s path holds: a gate, a walk, band 00, a trap. A walk mission's work never restates its protocol. A prototype mission's work is one step: run `/4-prototype` with what it prototypes.
6. `## Objectives` — these words, its objectives file's path filled in: "Your objectives are in `<path>`. Read them before you start. A `Run:` line is yours to prove: run its command. It prints what the line says → turn its `- [ ]` into `- [x]`, and add a `Shown:` line under it, quoting its output. Nothing it did not print. It prints anything else → go back to the work, then run it again. A Run line never needs my judgment: its command decides. A `Yours:` line is mine. Once every Run line is marked, bring me every Yours line together, in one `/2-clarify` wave, then wait. My agree marks it: `- [x]`, and a `Shown:` line naming its wave and item. My feedback asks a proof instead → prove it, then mark it, its `Shown:` naming the wave, the item and that proof. Change only a line's mark, never its words. `/session-report` refuses while any line is unmarked. A mark is never proof: `assistant-check` runs each Run command again."
7. `## Report` — "When every objective is marked, run `/session-report`." Then each part its report holds beyond what changed, and each check with its proof, one line each.
8. `## Rules you keep` — technical choices are yours; one that changes what a person sees comes to me first. Talk to me through `/2-clarify`. Never write outside your folder, but the marks in your objectives file. Never commit. Another session's change outside your folder is ignored, never repaired. When I say you are done, run `/9-session-stop`.

## Step 3b — Write its objectives

Write `missions/<id>-objectives.md` in my folder, beside its `file`, with the Write tool.

```
# <id> — <name> · objectives

- [ ] <an end state>
  Run: `<command>` → <what it prints when the line holds>

- [ ] <an end state>
  Yours: <what I judge, and where I see it>
```

One `- [ ]` line per end state the whole mission reaches. Each takes one proof under it, Run or Yours. A night drive's mission takes Run alone.

**Run** — a terminal command its session runs on this Mac, and what it prints when the line holds. It reads or tests, never writes. What it prints proves the whole claim. A build is the work's step, never a Run command: its Run line reads what the build left. Every line a command can prove is a Run line.

- ✅ `` Run: `grep -rn "No login anywhere" knowledge/` → prints nothing ``

**Yours** — what only I can judge, because no command shows it: what a person sees, what a word means, which hit may stand. A prototype mission's is the winner I locked in. Thinking work's is my agree on its wave.

- ✅ `Yours: each of the 52 hits left standing, named with why, in one wave`

Each line claims only what its proof shows. A word like "every" is part of the claim, so its proof shows every one. A result, never a step: what exists, where it shows.

The session marks a Run line done itself. A Yours line is marked only on my agree.

## Step 4 — Write it as me

`.claude/rules/talking.md` rules the voice, under "Writing for another reader". Follow it.

## Step 5 — Start its notes

Write its `file` with one heading, `# <id> — <name> · notes`, and one line: what it will build.

A finished session adds what this mission must know, one bullet each.

When its stage goes out, the notes become the mission. None of them stays behind as notes.

## Never

Never invent a ruling. A decision not yet made is asked, never written.

Never do the work itself.
