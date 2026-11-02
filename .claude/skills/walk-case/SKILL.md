---
name: walk-case
description: Judges one journey my walker walked, through walk-analyzer, writes its case and its marks, brings me each issue, and readies the fix I rule. The walk's lead runs it.
allowed-tools: Read, Write, Edit, Bash, Agent
argument-hint: "[the walker's report line, whole] · or [a reader's report line, whole] · or [a fix: my ruling on one issue] — omitted, ask me for the walker's report"
---

# Walk Case

You are my walk's lead: its brain. The analyzer judges; you read its case, and decide with me.

NN is your number, as `CLAUDE.md` defines it.

## Step 1 — Read the report

1. No words → ask me for the walker's report, and stop.
2. A fix, my ruling on one issue → Step 6.
3. A reader's report, "Session RR reports: <a docs step> read, …" → Step 7.
4. The line names the walker, WW, the journey, and its evidence folder. Read `.claude/state/sessions/WW/walk.json`, and `walks/walks-standard.md` whole: each extra it gives a case, an issue or a journey's end holds here too.
5. Read the journey's rows: `python3 .claude/tools/walk-list-page.py rows NN`, each row's `#` and name under that journey.

## Step 2 — Send the analyzer

1. Cut the rows into slices of about 25, in order.
2. Send one `walk-analyzer` agent per slice, six at once at most, in the background: "Judge. Walker folder: `.claude/state/sessions/WW/`. Journey file: `<its path>`. Checks: `<each # · name>`."
3. Wait for each. Never judge a screenshot or page text yourself.

## Step 3 — Write the case

1. Write `.claude/state/walk-case/WW-<area>-<section>-<journey file's name>-<its first check's #>.md`, like `11-app-training-coordinate-19.md`. The first check is the first this pass walked: a journey split across stages gets one case per part. The same part walked again after a fix adds `-2`, then `-3`. Never overwrite a case.

```text
# <the journey> · walker WW · <date, time>

<N> checks: <h> hold, <i> issues, <r> not reached, <w> not walked.

## Verdicts

<each analyzer line, in the checklist's order>

## Issues

- **<#> · <name>** · `<area>/<section>/<journey>/<the screenshot>.png`, or a docs check's `.txt` · should: "<…>" · shows: "<…>"
```

Then each section the standard adds to a case, from the analyzers' answers.

2. Each issue whose cause the analyzer did not name → one more `walk-analyzer`: "Trace. Walker folder: … Check: … Screenshot or page text: … Differs: …". Its answer goes under that issue.
3. Write the "Tester" marks, ✅ for holds and ⬜ otherwise: `python3 .claude/tools/walk-checklists.py --mark <the checklist> tester "<name>=✅" "<name>=⬜" …`.
4. Name each docs step of the checklist now ready for my read: every row of it ✅ for the tester, its own and each detail's, and its own "You" ⬜.

## Step 4 — Bring each issue

1. Your walker walks, or an analyzer you sent still judges → say what came back. Your move: "Wait: <each one still running> reports here." Bring nothing to rule, and stop.
2. Once the last one reports, list first every journey judged since my last ruling: its checks that hold, and each issue, in one line. Then each page I read since, and each of its findings, in one line.
3. Each issue, one per turn, first: the check, what it should show, what shows instead, its screenshot on WW's Screenshots tab, or a docs check's page text, quoted, the trace, and what the standard adds to an issue. Ask nothing about it.
4. My ruling on it → Step 6. My word to move on → the next issue.
5. No issue left → what the standard brings once the issues are dealt with. Then ask, alone on the last line: "Approve the <h> checks that hold? Type yes, or say which you don't." Its <h> leaves out docs rows: my read marks them, Step 7.
6. My yes → `--mark <the checklist> you` with each holding row ✅. Then each line the standard's "Keeping it current" gives the lead at a journey's end.

## Step 5 — The next journey

1. A finding `walk-write` held for this journey → bring it now, alone.
2. Your move names the next journey: "Ruling: walk <the next journey>." `7-walk` carries my yes.

## Step 6 — Ready a fix

1. Clarify with me until you can write the brief without guessing: the screen and its address, what shows against what should, which side is right, what must not change, and the journey to walk again. One question at a time.
2. Read `.claude/state/sessions/NN/launch.json` when it exists. Keep its rows. Add one, as `launch` Step 4 rules: `{"name": "<the screen> fix", "message": "<the message>"}`. No account, model or effort: I pick them.
3. The message, one paragraph, in my voice: the brief, then "Before you code, once everything is ready, write /session-report. Then, with my yes, send it to session NN with /message: what matches what session NN and I clarified, and why anything differs. Then wait. Code only once I say: green light, code it. When you are done, write /session-report again, and with my yes send it to session NN the same way: what you changed, and your tests."
4. A fix crossing layers → `another-team`, with the same brief and steps, in place of the row.
5. Your move: "Action: pick the fixer's account, model and effort, then press Launch on 1100."
6. Its report reaches you, before it codes → check it against what we clarified. Say what differs, or that it matches. With my yes, type "green light, code it." into the fixer with `message`.

## Step 7 — My read of a page

1. The line names the reader, RR, the docs step, then "clean" or each finding.
2. Clean → `python3 .claude/tools/walk-checklists.py --mark <its checklist> you "<name>=✅" …`, on every row of the step: its own and each detail's. Say it in one line.
3. Each finding is mine. It reaches me as Step 4 brings an issue, after the same wait and the same list: the docs step, the section and its lines, my words, then those lines of the page, quoted. Ask nothing about it.
4. My ruling on it → Step 6. My word to move on → the next finding.
5. Every finding of the page dealt with, and no fix changing the page → mark its rows as 2 does.

## Never

1. Never judge a check yourself. The analyzer's verdict is the mark.
2. Never type into the walker's or a fixer's pane but on my word.
3. Never write a walk file's line. `walk-write` does.
4. Never commit.
