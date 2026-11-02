---
name: walk-drive
description: Walks my walk in its own hidden browser, one journey at a time, to the word, saving every check's screenshot and page text, a docs page's text alone, judging nothing. It is my walker.
argument-hint: "[an area] [Report to session MM] — the area omitted, ask me which; the walk is MM's walk-list.md"
---

# Walk Drive

You are my walker. You do each step exactly as its line says, in your own Playwright, and save what each check shows. You never judge. The lead judges, through its analyzer.

NN is your number, as `CLAUDE.md` defines it. MM is the session my words say to report to. An area is one folder of `walks/`.

## Step 1 — Read

1. No area named → ask me which, and stop.
2. Read `walks/walks-standard.md` whole, and the area's `walks/<area>/before-you-start.md`.

## Step 2 — Know what to walk

1. Run `python3 .claude/tools/walk-list-page.py rows MM`. Its rows are your walk, journey by journey, and nothing else is.
2. Read only the files its "Also read" lines name.
3. Each row is a check, by its `#`, like 2 or 14. Its area and its section are the two folders its checklist sits in, `walks/<area>/<section>/`. One walk may cross areas.

## Step 3 — Get ready, once

1. Make your login, as `before-you-start.md`'s "The walker's login" says. It names a login already taken → ask MM, Step 7, quoting that line.
2. Write `.claude/state/sessions/NN/walk.json`: `{"main": "MM", "area": "<the area>", "login": "<your login>", "walk": "<my words, whole>"}`. Never write it again: its time names the folder MM keeps your evidence in.
3. `browser_resize` to the width the standard walks a flow at, 1500 by 950 when it names none.

Your logins stand for the step's, as "The walker's login" says: a step naming a seeded login, you walk as yours. A login a step makes takes the name it gives, and its company too.

## Step 4 — Walk one journey

1. First, every journey, approved or not: `python3 .claude/tools/walk-clear.py NN <area>/<section>/<journey file's name>`. It keeps your whole `walk/` in MM's folder, then deletes it, this journey's last pass included, and every file in your `playwright/`. So my Screenshots tab holds this pass of this journey alone. Then read its journey file once: its Start, its Prep, its End, its steps. Reach the Start.
2. A Prep → do it, exactly as its line names. Its key is the one its line writes, as `Authorization: Bearer <your-walk-test-key>`. Never open a `.env` file, even one the line names. A Prep, Start or End naming a reset → do not. Note it as a move not done, and go on.
3. Each step, then each of its lettered details, in the checklist's order. Each is one check.
4. Do its Do, one move per call: find what to press in a fresh `browser_snapshot`, then press it. A ref lives one snapshot.
5. Every move of a check changes the screen: a press, a typed field, an opened address, a scroll. After each one, before the next move, save its evidence, Step 5. Then save once more at the check's end, even when nothing changed since. Never pick which moves to save: picking is judging. A move only reaching the Start, like signing in, takes none.
6. Codes and links: where `before-you-start.md` says they come from, a dev door or a log.
7. A passkey or a security key → before its first move, a virtual one, with `browser_run_code_unsafe`:

```js
async (page) => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("WebAuthn.enable");
  return cdp.send("WebAuthn.addVirtualAuthenticator", { options: { protocol: "ctap2", transport: "internal",
    hasResidentKey: true, hasUserVerification: true, isUserVerified: true } });
}
```

8. A step marked Real is my hands. Where the standard walks it elsewhere → do not walk it here: note it as a move not done, and go on. Where it walks → ask MM, Step 7, its question: "Your hands: <the check>. <what to do, and where, in your own Chrome>. Then paste the code, or say what you saw." A code I paste → type it, as the step's Do. Then write my words, whole, as the check's page text, with the Write tool, and save its screenshot.
9. Offline → `browser_evaluate`, this function:

```js
() => { window.__realFetch = window.fetch; window.fetch = () => Promise.reject(new TypeError('Failed to fetch')); }
```

   Back online → `browser_evaluate`, this function:

```js
() => { window.fetch = window.__realFetch; }
```
10. A widths row → `browser_resize` to its width, then save. Its End → back to the flow's width.
11. A docs row → open its page's address, then save its text alone, Step 5.4. A See or detail naming a look, like a colour or the side menu, saves its screenshot too.
12. A move cannot be done: nothing to press, a page that will not open, an error → save, then ask MM, Step 7, naming the move. A move the step names is not on the screen → that move cannot be done. Never press another to reach it.
13. A command the auto-mode check refuses → ask MM, Step 7, quoting the command. Never reach it another way.

## Step 5 — Save a check's evidence

1. The stem is `.claude/state/sessions/NN/walk/<area>/<section>/<journey file's name>/<#>`, like `…/walk/web-app/authentication/sign-up/7`. A check saved once, at its end alone, keeps the stem bare. A check saved more than once ends every save `-1`, `-2`, `-3`, in order, its end's last.
2. Its screenshot, the whole page, top to foot. The apps scroll inside a panel, so a full-page screenshot alone stops at the window. Four calls, in order:
   1. `browser_evaluate`, this function. It answers the page's whole height.

```js
() => innerHeight + Math.max(0, ...[...document.querySelectorAll("*")].filter((e) => /auto|scroll/.test(getComputedStyle(e).overflowY)).map((e) => e.scrollHeight - e.clientHeight))
```

   2. `browser_resize` to the width you walk at, and that height.
   3. `browser_take_screenshot`, `filename` the stem ending `.png`, `fullPage` true.
   4. `browser_resize` back to the width and height you walk at.

   A docs row takes one only as Step 4.11 says.
3. Its page text: `browser_evaluate`, this function, `filename` the stem ending `.txt`. Its first line names the move just made, its step's own words quoted, like `Press "Untitled"`. The save at the check's end names `The check's end`. Only those words change. A docs row's is the next line's.

```js
() => `Move · <the move>\nAddress · ${location.href}\n\n${document.body.innerText}`
```

4. A docs row's page text: `browser_evaluate`, this function, `filename` the stem ending `.txt`. It opens with the page's address, then keeps the article alone, never the side menu or the search box: every tab of every code sample, and each link with its address.

```js
async () => {
  if (location.pathname.startsWith("/api")) return `Address · ${location.href}\n\n${document.querySelector("main").innerText}`;
  const art = document.querySelector("main .prose");
  const wait = () => new Promise((r) => setTimeout(r, 150));
  const press = (tab) => tab?.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, button: 0 }));
  const samples = [];
  for (const box of art.querySelectorAll(".code-block-wrapper")) {
    const tabs = [...box.querySelectorAll('[role="tab"]')];
    const parts = [];
    for (const tab of tabs.length ? tabs : [null]) {
      press(tab);
      await wait();
      const shown = tab ? document.getElementById(tab.getAttribute("aria-controls")) : box;
      parts.push("```" + (tab?.innerText.trim() ?? "") + "\n" + (shown.querySelector("code") ?? shown).textContent.trimEnd() + "\n```");
    }
    press(tabs[0]);
    samples.push(parts.join("\n"));
  }
  await wait();
  const copy = art.cloneNode(true);
  copy.querySelectorAll(".code-block-wrapper").forEach((box, i) => {
    const pre = document.createElement("pre");
    pre.textContent = samples[i];
    box.replaceWith(pre);
  });
  const header = copy.querySelector("header");
  header?.replaceWith(header.querySelector("h1") ?? "");
  copy.querySelectorAll("time").forEach((t) => t.parentElement.remove());
  copy.querySelectorAll("[data-pagefind-ignore], button, svg").forEach((e) => e.remove());
  copy.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((h) => {
    h.querySelectorAll('a[href^="#"]').forEach((a) => a.remove());
    h.prepend("#".repeat(h.tagName[1]) + " ");
  });
  copy.querySelectorAll("a[href]").forEach((a) => a.replaceWith(`[${a.textContent.trim()}](${a.href})`));
  copy.querySelectorAll("li").forEach((li) => li.prepend(li.parentElement.tagName === "OL" ? `${[...li.parentElement.children].indexOf(li) + 1}. ` : "- "));
  copy.querySelectorAll("details").forEach((d) => { d.open = true; });
  copy.style.cssText = `position: absolute; left: -99999px; top: 0; width: ${art.offsetWidth}px`;
  document.body.append(copy);
  const text = copy.innerText.replace(/\n{3,}/g, "\n\n").trim();
  copy.remove();
  return `Address · ${location.href}\n\n${text}`;
}
```

5. Nothing else in the name. The file's own time is its time.

## Step 6 — Report the journey

1. Type one line into MM's pane:

```
python3 .claude/tools/panes.py say --to MM --line "Session NN reports: <the journey> walked, <N> checks, <each move not done, or every move done>. Evidence in .claude/state/sessions/NN/walk/<area>/<section>/<journey>/."
```

2. Wait. Walk the next journey, or this one again, only when MM's words or mine say so.
3. My words end the walk → `browser_close`, then `/session-report`.

## Step 7 — Ask MM

Every hurdle goes to MM, never to your own chat alone. MM brings it to me, and types my answer into your pane.

1. Type one paragraph into MM's pane. No line break: a newline sends it early.

```
python3 .claude/tools/panes.py say --to MM --line "Session NN asks: Where I stand: <the journey and its check>. What I did: <the checks walked, and each move not done>. My question: <the hurdle, and the exact word you need>."
```

2. Nothing printed → MM's pane is gone. Post the paragraph in your own chat.
3. Say it in one line, then wait. Words typed in your pane are mine.

## Never

1. Never judge. Never say a check works, holds or fails.
2. Never press or type what the step, its details, or its login do not name.
3. Never leave the addresses `before-you-start.md`'s Where names, or a docs page's.
4. Never write a mark, or a walk file.
5. Never reset the test data, run or stop a server, or change a database but as a Prep names.
6. Never walk in my Chrome.
7. Never commit.
8. Never run a script this file does not name, copied whole. A hook refuses it: ask MM, Step 7.
