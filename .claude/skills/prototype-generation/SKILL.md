---
name: prototype-generation
description: Builds one generation of a prototype, at the level its protocol sets.
allowed-tools: Read, Glob, Grep, Write, Agent, mcp__playwright__browser_navigate, mcp__playwright__browser_resize, mcp__playwright__browser_console_messages, mcp__playwright__browser_evaluate, mcp__playwright__browser_close
argument-hint: "the subject, its level, its unknowns, then each variation's direction and the variation it grows from"
---

# Prototype Generation

## Step 1 — Know my number

My number, as `CLAUDE.md` defines it. My page is the prototypes app, on the port `python3 .claude/tools/prototype.py status NN` prints. 1100 frames it in my hub while I hold a subject not locked in.

## Step 2 — Take the round

The subject, its level, its unknowns, and each variation: its direction, and its source, as `1/v3`, or none.

A line opening "G<N>'s round:" is in chat before anything is built. None yet → say it now.

Read its level's protocol, `knowledge/0010-playbook/0014-prototyping/prototyping-protocols/protocol-<level>.md`. No level → Glance. It says who writes each variation, and where each is checked.

The generation's number is one past the newest `code/prototypes/<subject>/g<N>.json`. The first is 1.

Its variations are `v1`, `v2`, and on.

## Step 3 — Name what it builds on

Whoever writes a variation reads every file it builds on. Name each one by path. An agent writing → read none whole.

- Each source's file, `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`.
- The real parts, styles and fixtures each variation reuses, under `code/`. Glob and Grep find them.
- A page 1100 draws: `.claude/lib/page.py`'s shell, `SHELL`, and the CSS of each page it borrows from.

Each variation names every look it uses: borrowed, with its page, or new. A new look is my item before the build.

## Step 4 — Write each variation

The protocol says the session writes it → write it yourself, by the brief below.

Otherwise launch one `general-purpose` agent per variation, six at most at once, each with `model: sonnet`. As one finishes, the next goes.

Each brief holds:

1. The one file it writes: `code/prototypes/src/routes/<subject>/g<N>/v<M>.tsx`. It writes nothing else.
2. Its route: `createFileRoute("/<subject>/g<N>/v<M>")`.
3. The unknowns, and its direction. It draws what its direction shows, and nothing more, by "3. It shows only what my unknowns need", in `knowledge/0010-playbook/0014-prototyping/the-prototyping-axioms.md`.
4. Its source file, when it has one: a variation of this subject. It starts from that file.
5. The parts, styles and fixtures to import, by relative path, from any frontend under `code/`. Its frontend's look file, `src/base/styles.css`, comes whole, as text: `import look from "<relative path>/src/base/styles.css?inline"`. The route draws it as `<style>{look}</style>`, so it lives only while the route is on screen. The variation's own new rules follow it, and nothing else is copied. A source file's copied rules leave. A real rule it changes is rewritten among its own.
6. Its data is typed in. No backend call, no login, no database.
7. It never edits a file it imports.
8. Its subject's own rules. A product screen's are The Screen, in `knowledge/0010-playbook/0015-coding/the-stack/the-screen/`. A variation that draws a whole screen obeys The Screen and the frame, in `knowledge/0010-playbook/0015-coding/the-stack/the-look.md`. A page 1100 draws obeys the page rules, atop `.claude/lib/page.py`. Its direction outranks them.
9. Its opening comment names its direction, numbers and stand-ins, and every look it uses: borrowed, with its page, or new. Each stand-in is also marked where it sits.

## Step 5 — Check the files

Each variation's file exists.

Each agent's report names only its own file. Another file written → name it in chat, and stop. The session wrote it → nothing to check.

## Step 6 — Write the generation

Write `code/prototypes/<subject>/g<N>.json` with the Write tool.

```json
{"subject": "proposal-header", "generation": 2,
 "unknowns": [{"id": "u1", "text": "How the state reads at a glance."}],
 "variations": [
   {"id": "v1", "direction": "A full-width band: both parties agreed.",
    "from": "1/v3", "route": "/proposal-header/g2/v1",
    "looks": [{"n": "1", "title": "Inside a card", "group": "A"},
              {"n": "2", "title": "Outline only", "group": "A"},
              {"n": "3", "title": "The pending state"}],
    "answers": {"u1": "Agreed, from the first line."}}]}
```

`from` is `""` for a variation with no source.

`looks` lists the numbered things the variation draws, one entry each: its number, as its route wears it, its title in a few words, and for a look that competes, its group, one letter. Looks in one group compete, and I pick one. An entry with no group is only shown, as a section is. A variation with no numbered things has no `looks`.

Writing it holds this subject for me, through `.claude/hooks/prototype-hold.py`, and 1100 counts it.

## Step 7 — Check each renders

Open each variation's route on the port `prototype.py status NN` prints, with Playwright. Read its console errors, at each width the protocol names: resize first, then read them again.

A phone width emulates touch, so its touch rules apply. Before it, pass this to `browser_run_code_unsafe`. After it, the same with `enabled: false`.

```js
async (page) => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
}
```

A favicon's 404 is no error.

Then measure each screen it shows at 1500 wide, against The Screen's Width, `knowledge/0010-playbook/0015-coding/the-stack/the-screen/width.md`. Resize, then pass this to `browser_evaluate`. It lists every part narrower than the column:

```js
() => {
  const column = document.querySelector(".page-column");
  if (!column) return "No column: nothing to measure.";
  const box = column.getBoundingClientRect();
  const pad = getComputedStyle(column);
  const left = box.left + parseFloat(pad.paddingLeft);
  const right = box.right - parseFloat(pad.paddingRight);
  const narrow = [];
  for (const part of column.querySelectorAll("*")) {
    const cap = getComputedStyle(part).maxWidth;
    if (cap === "none" || cap === "100%") continue;
    const rect = part.getBoundingClientRect();
    if (rect.width < 200) continue;
    if (rect.width >= part.parentElement.getBoundingClientRect().width - 4) continue;
    narrow.push(`${part.getAttribute("class")}: ${Math.round(rect.width)} wide, white ${Math.round(rect.left - left)} left, ${Math.round(right - rect.right)} right`);
  }
  return narrow.length ? narrow : "Nothing stops short of the column.";
}
```

Each part listed holds only fields or prose, or it centres: its white left equals its white right. Anything else is an error. A narrow part its direction asks for stays, named in chat.

An error → as the protocol says: the session fixes its own file, it is named in chat, or one agent, with `model: sonnet`, fixes that variation's file, briefed with its path, its route and the error. A fix is checked again.

Never take a screenshot. A look is an agent's to see.

Close the Playwright page when every variation renders.

## Step 8 — Show me

1100 frames the generation from the prototypes app, under my number on its rail.

Say one line: "G2 is built." Then one line per variation: its id, its source, its direction.

A button a variation invents, one no real page has, takes one line under it: what a press does.

Several looks or sections share one variation → one line each under it: its number, then what it shows. A group's looks sit together, under its letter.

A picture inside a section takes its own line, after its section's: its number, like 3.1, then what it shows.

```
G1 is built.
v1, from none: the badge alone, in each status, three looks. 1 and 2 compete.
A · 1 — inside a card.
A · 2 — outline only.
3 — dot only, shown beside them.
```

## Never

Never write outside `code/prototypes/`.

Never delete a variation. Only a lock-in does.

Never add your pick.
