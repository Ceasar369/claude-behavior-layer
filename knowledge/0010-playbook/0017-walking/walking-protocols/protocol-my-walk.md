# Protocol — My Walk

Up: [[walking-protocols-MOC|Protocols]]

When I walk an area's section, a subject, or any one thing: who does what, then what happens to each finding.

[[the-walking-axioms|The Walking Axioms]] rule its order: features first, a feature stage by stage, and a whole journey again after every fix.

## Where the walk lives

My walk lives in `walks/`, outside the vault: one folder per area of my app, one folder per section, each with its own checklist. `walks/walks-standard.md` rules every walk file, and each area's `before-you-start.md` holds its facts: where, the logins, the data, the code.

No session's stop deletes it.

A project with no `walks/` takes the layer's standard, `.claude/tools/walks-standard.md`, at its first `walk-write`. From then on the standard is the project's own.

## Four roles, three sessions

**The lead** is the session I talk to. It is the brain. I start it with `7-walk`: "Walk my app with me", a section, a subject, or any one thing. It finds the walk, checks its files with me, launches the walker, reads the case, and fixes with me. It acts on my word, and my yes to its ruling is my word. It then types into the walker or a fixer itself.

**The walker** is a session the lead launches. It runs on Sonnet, at the effort I pick, on the account I pick. It walks in its own hidden Playwright browser, never in my Chrome. It follows each step to the word, and judges nothing. At every check it saves a screenshot of the whole page, top to foot, and the page's text. The text opens with the move just made and the page's address. A docs page saves its text alone: the article, every tab of every code sample, each link with its address. A docs check judging a look keeps its screenshot. It does its own Preps. A move it cannot do, it asks the lead, which brings it to me.

**`walk-analyzer`** is the one judge: an agent the lead sends, `.claude/agents/walk-analyzer.md`. It judges each check against its See line, its screenshot and its page text, blind to anything else. A docs check, from its page text, but for a look. It traces an issue to where it came from: the code, the walk files, the docs. When those disagree, it states each side and picks none. I rule which side is right.

**The reader** is a session the lead launches once a docs page's checks all hold. It runs on Sonnet, at low effort, on the account I pick. It brings me each docs page the lead hands it, one section per turn, and I read every word myself, on the docs site. It judges nothing, fixes nothing, and writes no mark.

One walker, and one reader, carry the whole walk. A fresh one starts only when I ask.

Every turn the lead shows me opens on one line: the journey in hand, as "Journey 1 of 4 · Sign up", and the login the walker walks it as, its own, never mine.

## The walk's list

Every walk is one list in the lead's folder: `walk-list.md`. It names each journey or check it borrows, by section and name, and copies no row. Its marks stay in the checklists. The lead's Walk tab shows it as Obsidian shows a checklist, and the walker reads its rows there, and nowhere else.

My words name a section → the list holds its journeys. A subject, like the email sender → each step that shows it, across sections. A feature `walks/walks-MOC.md` lists → its journeys and steps, stage by stage. Any other words, like "just the Keys page" → the steps already covering its screens. None → `walk-write` writes the thing's journey, in the section its screens sit in.

A check the walk needs that no checklist holds goes into a section's checklist first, through `walk-write`, on my yes.

## Right before each journey

`walk-write` brings the journey's walk files in line with the code on disk, and each other source `walks/walks-standard.md` names, as it rules. A change a file already rules, it makes. Each other change comes to me as an item, and I rule it. Only then does the walker walk it.

A change none of my sessions explains is one I never ruled. It stays a finding. One no check of the journey rests on waits until the journey's case is done.

## The walker walks

The lead writes the walker's row on its own launch page: its name, Sonnet, low effort, and my words as its message. I pick the account, and I press Launch.

The walker makes its own login, as its area's `before-you-start.md` says, and walks as it. It writes `walk.json` in its folder, naming the lead, the area and its login.

It walks one journey: each step, then each lettered detail. Everything it makes sits in its own folder: `walk/<area>/<section>/<journey>/<number>.png`, and the page's text beside it, `<number>.txt`. A docs check saves its `.txt` alone. Before each journey, it keeps its whole `walk/` in the lead's folder, then deletes it, so its Screenshots tab holds this pass of that journey alone.

At the journey's end it types one line into the lead's pane: the journey, how many checks it walked, and any move it could not do. Then it waits. It walks the next journey only when the lead tells it, on my word.

A step marked Real is my hands, where the standard says it walks. There, the walker asks the lead, which brings it to me. I do it in my own Chrome, then paste the code or say what I saw.

## The lead judges, through the analyzer

The walker's line reaches the lead. The lead sends `walk-analyzer` over the journey's checks, in slices of about 25, six at once at most. Each slice comes back with a verdict per check, and each issue with its screenshot's name, or a docs check's page text.

The lead writes the case: `.claude/state/walk-case/<walker>-<area>-<section>-<journey>-<first check>.md`, outside every session's folder. A part walked again after a fix adds `-2`, then `-3`. Its Issues name each screenshot, or a docs check's page text, by its path under the walker's `walk/`. The walker's Screenshots tab marks each one with a red dot, when the case is newer than the screenshot.

The analyzer's verdict is each row's "Tester" mark. The lead writes it.

A check after a failed one, on the same screen, reads "not reached", and stays ⬜.

Each issue whose cause is unknown gets one more analyzer run, to trace it.

## How each one reaches me

While the walker walks, or an analyzer the lead sent still judges, the lead brings me nothing to rule. A walker's question waits for the analyzers too.

Once the last one reports, one turn lists every journey judged since my last ruling: its checks that hold, and each issue, in one line. Each page I read since follows, with its findings.

The lead then brings each issue first, one at a time, without asking my opinion: the check, what it should show, what shows instead, its screenshot or a docs check's page text, and the analyzer's trace. What the standard adds to an issue comes with it.

Once the issues are dealt with, the lead asks my yes on the rest, docs rows aside. My yes writes "You" ✅ on each row that holds. A docs row's "You" comes from my read alone.

Nothing else is written. The checklist keeps marks alone. The case, the transcript and git keep the rest.

## My read of the docs

A docs page reaches my read once every tester check on it holds. The lead hands it to the reader. The walk goes on while I read.

The reader brings one section per turn, one call in the API tab, with no checklist and none of the tester's claims. I answer "next", or say what looks off.

At each page's end, the reader tells the lead. A clean page's rows take "You" ✅. Each thing I flagged is a finding of mine, and reaches me as an issue does.

A fix changes a page I read: I read again only the sections it changed.

## A fix for each failure

A failure I rule, or a finding of mine, is built now. Nothing new goes on my agenda.

The lead clarifies the fix with me first, as much as it needs, until it can write the brief without guessing: the screen and its address, what shows against what should, which side is right, what must not change, and the journey to walk again.

It then writes the fixer's row on its launch page. One session by default. A team, through `another-team`, only when the fix crosses layers. I pick the account, and I press Launch. Nobody drives the fixer. I may also talk to it in its own pane.

The fixer's message carries the brief, and two default steps.

- **Before it codes**, once everything is ready, it writes `/session-report`. With my yes, it sends it to the lead with `message`: what matches what the lead and I clarified, and why anything differs. Then it waits, and codes only once I say: green light, code it. The lead checks the report first. With my yes, it types those words into the fixer with `message`.
- **When it is done**, it writes `/session-report` again. With my yes, it sends it to the lead the same way: what it changed, and its tests.

Then, with the lead, I close the fixer or give it more.

A fixer keeps the checks its coding protocol rules, on its own ports. Band 00 shows the change once the file saves.

Two fixers never open the same file. The lead names each one's files.

A change from a session outside the walk that breaks a step holds that journey, like a fix. The lead names that session and its file to me, and touches neither.

## When a fix ends

`walk-write` rewrites each line the fix made wrong, as `walks/walks-standard.md` rules, and names each change.

On my word, the lead tells the walker to walk the whole journey again. A journey split across stages walks again each of its steps already walked, whatever stage it sat in, right after the fix. So does a counter step already walked: once later steps have added rows, its count is judged against the test data plus the rows this walk added, which the lead names before that walk. The analyzer judges it again.

## A finding with nothing to fix here

A Hidden thing that shows: I say which side is right. "Hide it" is a failure like any other. "Keep it" changes the vault line, through a fixer too.

A Not built or Not designed step is a missing piece. My words on one are built now, like any finding.

A finding inside a part no session works on gets no fixer. It comes to me.

## Walks stage by stage

`walks/walks-MOC.md` lists the features, one after the other, and the order of the places each stage walks in.

A feature walks its subject's life one stage after the other. Each stage walks in the first place of that order showing it, then in each other place showing it. Only then does the next stage start. A place that never shows a stage is skipped.

A journey opening a stage passes whole. Another place's journey splits: each of its steps walks at the stage it shows.

One walker walks the feature, line by line, on its own login. A counter walks before the first stage: a step counting rows a later step of its feature adds, or reading their view empty. The rest of its journey walks at its stage.

Any session proposing a walk order follows this one: the lead, my assistant, my advisor.

Only a session that is not a walker resets the test data, and never while another walk's `walk.json` stands. A walker on its own login never resets, and its Preps act on its own login and company. A Prep, Start or End that needs a reset, names a seeded login, or relies on a login or record an earlier feature made, is a line `walk-write` rewrites.

## A walk's end

I end the walk in the lead's chat. The lead keeps the walker's evidence, then stops the walker and the reader.

The lead keeps the walker's `walk/` folder and its `walk.json` in its own folder, `walkers/<walker>-<its start>/`, for reference only. Each walker keeps apart, and each journey its last pass alone. No tab shows them.

My code changes stay on disk until I rule a ship.

I may hand the lead over at any time, with `session-handover`. Any session I start finds where I stopped, from each checklist's marks and the cases in `.claude/state/walk-case/`.
