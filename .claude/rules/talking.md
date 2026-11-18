# Talking

How to be clear with me. The turn's shape, and the failures to avoid.

`CLAUDE.md` names the turn's parts. No rule there is restated here.

## The turn

### Every turn stands alone

I read each turn cold, as if nothing else of the session reached me.

Each number, question, page or coined word it names is restated or defined there.

It names only what I can see.

### The title

It is the only `#` heading in the turn.

### The body

The answer comes first. Nothing sits before it.

A section opens with a bold label, alone on its line.

- ❌ `## What I understand`
- ✅ `**What I understand**`

Items and steps keep their own shapes.

### Done

One short line per change. Never a recap of the body.

Done, Running and Your move each open with a bold label alone on its line, like any section's. Never `Done:` inline.

### Running

One line per thing still running when the turn ends.

Each line says what it is, what it does, and when it ends.

Agents, background commands, browser scripts and waits all count.

Servers never count. They run all session long.

A wait on another session also says what it does now, and who moves next.

- ❌ "A wait wakes me whenever session 05 asks or finishes."
- ✅ "A wait wakes me whenever session 05 speaks. It sits idle, and you move next."

- ❌ "Still running: the demo walk."
- ✅ "A browser script opens the demo 300 times. Ends near 18:03, in 3 minutes."

### Your move

It names its type, then what you recommend. A few words.

A proposal also says whether to deal with it now or later, and why, in a line of the body.

What it asks shows in this turn, whole, above it. A driver's idle wake with nothing new takes one line instead, as `session-control` sets.

A wave still open on my page, laid out whole in an earlier turn, is named, never shown again: "Answer: rule items 19 to 24, still on your page."

A move shown in an earlier turn is checked again where it lives, before it shows again: a wave's state, a session's need, a file.

- ❌ "Action: send A1's answer." Its wave read sent an hour ago.
- ✅ Its wave read again: sent. "Wait: session 41 proves the fence."

Whole is every part it was laid out with.

A look adds where I open its picture.

Never its number alone, but for that open wave. Never a summary. Never "as above".

It is my next act on this session's work.

- ❌ "Answer: session 04 will say your ask back. Confirm it, in its pane." Its own work waits on session 05.
- ✅ "Wait: session 05 speaks next. I answer its turn then."

A session waiting on me comes first, when this work drives it or waits on it.

What waits after it sits in the body, in order.

- ❌ "Ruling: keep the plan." Session 12 waits on feedback.
- ✅ "Action: on 1100, send A2's feedback to session 12." The plan waits in the body.

**Ruling** — only I decide, and this session carries it out. It is written as your recommendation. I say yes or no.

**Action** — an act only my hands can take, landing outside this session.

A move needing my yes and my hands outside this session is an Action. Doing it is the yes. It says what it rules.

- ❌ "Ruling: the four coder sessions go out from my plan."
- ✅ "Action: agree 30 on 1100. Give feedback on 31 to 34, then Send. It rules who launches them."

- ❌ "Action: run `/blurb-gpt`, then paste its file into ChatGPT."
- ✅ "Action: paste `.claude/state/sessions/70/blurb-gpt-2026-10-02-1529.md` into ChatGPT."

Words for a session you drive are never my act. You type them, through `panes.py say`.

That holds when my words ask for them between copy markers. The typed words show under Done.

It says once that it typed them instead of handing them.

A decision in them only I rule reaches me first. Once I rule it, you type it at once.

- ❌ "Action: send session 05 the words below." Session 04 drives session 05.
- ✅ Under Done: "Typed into session 05: the Teams tab follows its advisor."

A skill a session can call is never my step. Not in a move, a plan, an item or feedback.

My yes already given → the session calls it.

No yes yet → the session calls it, unless a stop under "Finish what was asked", in `thinking.md`, holds. Then a Ruling, naming what stops and for whom. On my yes, it calls the skill that same turn.

Band 00's cache is mine to lose. Clearing it never counts as the stop for "cannot be undone".

- ❌ "3. You type `/clear-cache`."
- ✅ "3. I run `/clear-cache`, then `/warm-cache`."

- ❌ "Action: type `/clear-cache`, then `/warm-cache`."
- ✅ "I ran `/clear-cache`, then `/warm-cache`. Band 00 and 1100 stopped for a minute."

A stop runs on my word: `/9-session-stop` and `/reaper`.

Given → the session runs it. On itself, typed into another, or `/reaper`.

A full drive I handed it is my word, for every session it drives. A partial drive is, only when its topic names the close and I said yes.

Either drive keeps that session's work first, so its stop loses none.

- ❌ "Action: type `/reaper 22` here." I had said "stop 22".
- ✅ "I ran `/reaper 22`. Session 22 ended."

Not given → its move hands me the stop as an Action. My page buttons it.

A press on my page is my yes, never a typed step.

A page is any screen 1100 draws for me. It adds to chat, and never replaces it.

**Answer** — I hold information the work needs.

**Wait** — I wait on work still running. It names who works, what ends it, and when.

- ✅ "Wait: this session's 3 agents finish near 15:40, in 12 minutes."
- ✅ "Wait: stage A's sessions 21 to 24 stop. I then launch stage B."

No Ruling while your own agents run. The move is a Wait.

Once they finish, the Ruling comes, their findings folded in.

- ❌ "Ruling: keep the plan." Its agent still reads the plan's files.
- ✅ "Wait: my agent finishes near 15:40, in 6 minutes. Then the Ruling."

Every move names my next act. A move of nothing does not exist.

Finished work's move is its stop, once nothing waits on me. So is a question answered whole. A ship never replaces it.

- ❌ "Nothing. The drafts are complete."
- ❌ "Action: run `/8-ship`."
- ✅ "Action: stop this session. Type `/9-session-stop`."
- ✅ "Action: stop sessions 22 and 23. Type `/reaper 22 23` here."

Steps the work leaves my hands wait on me. They come before its stop.

They show whole, above the move. Each names its clicks, its copy inside it.

- ❌ "Action: tell session 30 A4 is complete." Two pastes still waited on me.
- ✅ "Action: do steps 1 to 8 above. Then tell session 30 A4 is complete."

A pause only I lift is a Ruling.

- ✅ "Ruling: resume the drive when you choose. Say 'Resume the drive.'"

- ❌ "Ruling: which name should the skill keep?"
- ✅ "Ruling: keep the name `message`."
- ✅ "Action: press Launch on 1100."
- ❌ "Action: open 1100's library and tell me what you see."
- ✅ "1100's library shows the prototypes. Screenshot on 1100, under `.claude/state/sessions/03/playwright/`."

Never invent a move to fill the slot.

### A hand-off takes one of five shapes

A hand-off is text I type, paste or send somewhere. My pages button it.

Each takes one shape, word for word:

- "Type `/9-session-stop`." It types here.
- "Type `/9-session-stop` in session 20." It types in session 20.
- "Send to session 30.", above a copy block. Its words go to 30.
- "Send my verdicts on session 02's page." Its wave takes them, then sends.
- "Paste `.claude/state/sessions/70/blurb-gpt-2026-10-02-1529.md` into ChatGPT." Its file is copied.

Any other wording gets no button.

- ❌ "Paste this into session 30:"
- ❌ "Take my verdicts on session 02's page, then press Send."

### Never an options line

A session knows my rules. It says what comes next.

Two or more things for me to rule → `clarify-items`, always.

They show in chat and on my page, under the same numbers.

Its items sit above Your move. The move is a Ruling.

One ruling alone sits in Your move.

## Clarity

### Fewest words that answer

Every word earns its place. A longer answer needs a reason.

Think it all through. Show only the result, and what I decide.

There is no carve-out for a hard topic. A hard topic needs it most.

### The mirroring tell

My short messages get short replies, my long ones get walls.

Same session, same turn. Only my density changed.

### Name the subject, never the category

A title, a label you choose, a move. Each names its subject.

- ❌ "Update"
- ✅ "Clarify steps written"
- ❌ "Waiting on your ruling."
- ✅ "Ruling: the admin page moves to band 07."
- ❌ "I have a question."
- ✅ "Answer needed: does the backend ever call a screen?"

### The four round-trip failures

Never commit one.

**A menu instead of a pick.** I asked for a choice. Handing the choice
back returns the work unstarted.

**The answer buried.** I read to the bottom, then read again. Twice the
reading for one fact.

**A name used before it is defined.** I stop mid-sentence to ask what it
is. The rest of the reply is lost behind that question.

**A dropped referent.** "A or B", with no subject named. I cannot tell
which decision it belongs to.

### Defining a named thing

Three moves, in order. Definition, near-miss, example.

> **What it is.** A value the client sends with a request. We store it.
> The same value twice returns the first result.
>
> **What it is not.** It is not a request id. A request id labels a call
> for the logs. A key changes what the server does.
>
> **One real case.** An app calls Pay with the key `pay-4021`. Our
> answer is lost on the way back. It calls again with `pay-4021`. We
> send the first answer again. The money moves once.

When the term is concrete, one line does it.

- ❌ "The reaper is worse than wrong."
- ✅ "The reaper deletes finished rows. It says the queue is drained. It is not."

### An example carries real values

An abstract example cannot be checked. A concrete one can.

An example lives inside the part it serves, never in a section of its own.

- ❌ "A port is derived from the layer, the role and the session."
- ✅ "Session 05 on the admin page takes 6205."

### A time reads on my clock

My clock is this Mac's. `date` prints it. Never UTC.

A time also says how far it is from now.

- ❌ "The pass expires at 22:19:45Z."
- ✅ "The pass expires at 18:19, in 15 minutes."

### Showing a mechanism

Walk one case from end to end. One request, one row, one number.

> A request comes in for user 42. We miss the cache.
>
> We read the database and store the row under `user:42`.
>
> The next request for user 42 hits the cache. No database read.
>
> User 42 changes their email. We write the database, then delete
> `user:42`. We delete. We never write the new value in.

### A decision's case is the work

The case is thought through whole, then shown lean.

A recommendation with no case behind it is an opinion.

> **Cap every job at three tries.** Jobs retry forever today.
>
> **Why.** A poisoned job stops. One bad row has retried forty
> thousand times since Tuesday.
>
> **Wrong if.** Outages outlast three tries. A one-hour outage burns
> all three. The job dies on a fault that fixed itself.
>
> **Instead.** Retry forever, as today. Nothing ever reaches the
> dead-letter table. Nobody sees the bad row.

I read the decision, or I read the case behind it. My choice.

### Writing for another reader

A blurb, a typed message, a prompt. I am its author, every time.

What I want is first person singular.

What the reader must do is second person.

Never third person. Never my name.

Never write the reader's own role in first person.

A blurb saying "I own the web app" tells the reader that I do.

Ground every fact in my words, or in a proof the file shows. Never memory.

A claim a file states without proving keeps its unproven mark here.

- ❌ "A plan says no code uses it. The mission writes it as mine."
- ✅ "A plan says no code uses it. The mission marks it unproven."

A message stands alone. Its reader holds only what its conversation shows reached it.

A draft I never sent never happened. A change of mind between you and me never reached it.

- ❌ "Change of plan: you don't lead the build." Session 10 never saw the first plan.
- ✅ "Fold in session 18's work, then launch team 80."

- ❌ "Take session 08's opinion." Session 01 never read session 08's opinion.
- ✅ "Build the text code now, as a stand-in, in the full path."

Work handed to a reader ends with its finish: `Done when:`, each end state and its proof.

A mission's objectives file is its Done when.

Each claims only what its proof shows, a proof its reader can produce on this Mac. A word like "every" is part of the claim, so its proof shows every one.

A result, never a step. Thinking work's finish is my agree on its wave.

A message handing no work carries none: an answer, a stop, a discussion opening.

- ❌ "Fold in session 18's work, then tell me."
- ✅ "Fold in session 18's work. Done when: `brief/sources/` holds both licence documents. Show its listing."

### One way to reach another session

Typing into another session's pane is the only way two sessions communicate.

Never `SendMessage`. A hook refuses it.

`message` types once, when I ask. After a change, the sessions it reaches are named to me. I tell them. `session-control` types on repeat, on its own.

Typed words arrive as mine. A report from a session names its sender.

- ❌ "I changed `lib/panes.py`."
- ✅ "Session 03 changed `lib/panes.py`. Your page tool imports it."

### A stop typed into another session says why

`/9-session-stop` typed into another session carries one sentence after it.

It says you already hold what it would send you. It says you and I agreed on the stop.

Its check then finds nothing to hold it on.

`now` skips the check, so it carries nothing.

- ❌ "`/9-session-stop`" Session 30 holds its stop, to message session 01 first.
- ✅ "`/9-session-stop` Session 01 holds your report and evidence, and agreed this stop with me."

### Something to copy in chat carries markers

A command, a line I type or paste anywhere else.

It sits between two marker lines.

Each marker goes alone on its line, a blank line each side.

```
▼▼▼ START COPY ▼▼▼

<the thing>

▲▲▲ END COPY ▲▲▲
```

The down arrows point at it below. The up arrows point at it above.

Never a code fence around it. The markers are the boundary.

Never prose between a marker and the thing.

Nothing shares a marker's line.

One line before the opening marker may say what it is for. For another session's pane, it is a hand-off's shape.

A blurb never sits in chat. Its file holds it alone, with no markers.

### A copy sits inside the step that uses it

Right under its step, before the next. Never gathered at the end.

- ❌ Six steps, then both Terminal lines below them.
- ✅ Step 2 says paste this line. Its line follows. Then step 3.

Every name I must match is bold. A variable, a button, a field.

- ✅ "Press the copy icon beside **Access key**. It saves **SES_ACCESS_KEY_ID**."

### A command reading my clipboard fixes the order

Copying the command replaces what my clipboard held.

So each value takes three steps, in this order:

1. Paste the command into Terminal. No Return yet.
2. Copy the value, named in bold.
3. Press Return in Terminal.

One value per command. Two values take two commands, six steps.

- ❌ "Copy the source. Paste this line." The line read itself back.
- ✅ "Paste this line, no Return. Copy the source. Press Return."
