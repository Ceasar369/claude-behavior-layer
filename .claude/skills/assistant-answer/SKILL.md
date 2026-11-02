---
name: assistant-answer
description: Tells me what to reply to another session's clarify items or open questions, and puts each agree or feedback on its page. "Help me answer session 05" means this skill, in any session.
allowed-tools: Read, Glob, Grep, Write
argument-hint: "A1 or 21 — the mission, or its session"
---

# Assistant Answer

## Step 1 — Take the session

My number, MM, as `CLAUDE.md` defines it.

A mission id finds its session: `python3 .claude/tools/assistant-page.py states MM`. A number is the session.

Its mission is its entry in `.claude/state/sessions/MM/stages.json`.

No such file or entry → it has no mission. Its id is its number, and my rulings alone judge it.

## Step 2 — Read what is new since your last answer

Your old `.claude/state/sessions/MM/answers/<id>.md` names, in its headline, the wave it answered and its bookmark. Call them wave K and T.

```
python3 .claude/tools/clarify-page.py answers NN --since K
python3 .claude/tools/transcript.py new NN --since T
```

The first prints what I sent on wave K and every later wave. The second prints every turn after T, then the next bookmark.

What I sent there, and what I said in its pane, are rulings. Your old answer was a proposal.

A mark of mine on a wave still `waiting on you` is my draft. It is mine, only not sent yet.

In a drive, you sent there yourself. Only my words in your chat are rulings.

A turn marked `Session NN · report` is a helper's report, never my ruling.

Compare my sent answers on wave K with your old answer, item by item. I answered every later sent wave alone.

No old answer → `answers NN --since 1`, and `new NN` with no `--since`. Nothing is compared.

## Step 3 — Read what it asks

Its newest `.claude/state/sessions/NN/waves/wave-N.md` whose `sent:` is empty, whole.

No such wave → its questions and its move, in the turns Step 2 printed.

## Step 4 — Weigh each point

Read every file behind it. Run what can be run.

Judge it against my rulings and its mission. Never against its phrasing.

Right and complete → agree. Anything else → the exact feedback.

An item holding my draft → weigh my draft, never the item afresh.

- It holds → holds.
- It asks a question, or says Explain → answer it, in plain words.
- Anything else → feedback: sharper words, my meaning kept whole.

In a session I handed you, an item my rulings cannot answer takes this feedback, word for word: "This one moves to chat. My answer comes there. Go on with everything else." It reaches me, as `assistant-drive` Step 4 says.

## Step 5 — Reach every session it touches

An answer carrying words for another session reads that session first, as Steps 2 and 3 do. Then it goes by that session's state, from `assistant-page.py states`:

- `answer`, `send` or `waiting on you`, with a wave open → its words go in as proposals, on its own page.
- `answer` with no wave open, `check` or `idle` → its answer too, under its own mission, in this same pass.
- `working`, capped, or an error with one more try → my move reads "Once session NN is idle, send to session NN."
- `blocked`, `gone`, or an error three times in a row → nothing goes in. It reaches me, with its state.

## Step 6 — Put it on the page, then write it down

First, put each verdict under its item, on the session's own page. A feedback's words to send come on stdin.

```
python3 .claude/tools/clarify-page.py propose NN --item 1 --agree --by MM
python3 .claude/tools/clarify-page.py propose NN --item 3 --feedback --by MM --why "Only the machine's backend has app.ts today." <<'EOF'
Agreed, worded so it holds for every backend as it stands.
EOF
```

A session with no wave waiting takes no proposal. Nor does a session I handed you whose wave Step 7 sends. An item moved to chat takes none either.

Only a feedback on my draft takes a proposal. Taking it replaces my words, so it carries my meaning whole.

Then write `.claude/state/sessions/MM/answers/<id>.md` with the Write tool.

```
# Wave 4 · Four agree, two feedback · read to 2026-09-24T14:16:05
## Your moves
1. Send my verdicts on session 21's page.
Since my answer to wave 2:
- Item 5: I proposed agree. You sent feedback.
- You answered wave 3 alone.
## Item 1 · agree
## Item 3 · feedback
Only the machine's backend has `app.ts` today.
> Agreed, worded so it holds for every backend as it stands.
```

The headline names the wave it answers and its count, then `read to` and the bookmark `new` printed. A chat answer names no wave.

`## Your moves` comes first: each move in order, naming its session. A wave's move is "Send my verdicts on session NN's page." A wave waiting for my Send, with nothing to take: "On 1100, rule session NN's wave K, then Send." A chat move is "Send to session NN.", then its `> ` lines.

Under it, one bullet per change of meaning since your old answer. A verdict I flipped, feedback I rewrote, a wave I answered alone. A wording change stays silent. None → no lines.

One `##` per item, in its order. Its last word is agree or feedback. On my draft, it is holds, answered or feedback.

A feedback carries one line of why, then the words to send, as `> ` lines.

An answered item carries its answer as plain lines, never `> `.

A question outside a wave takes one `##` each, the same way.

A `> ` line goes to the session word for word, the same words its proposal carries. I never paste it: the page's Send types it, or you do, in a session I handed you. `.claude/rules/talking.md` rules its voice, under "Writing for another reader".

## Step 7 — Say it

Lay the answer out in chat: its moves, and each item's verdict with its words. Its headline stays in the file. The page carries the same.

In chat, a chat move's words sit in a copy block, under its "Send to session NN.", as `.claude/rules/talking.md` shapes a hand-off.

I asked for your help, never your hands. Outside a drive, I send each answer myself, from 1100.

Your move is an Action naming each send, in order: "Action: on 1100, send A1's answer, then A2's. It rules each verdict." With no mission, it is the wave's own move: "Action: send my verdicts on session 02's page."

A session I handed you through `1-assistant` drive is yours to send only when its wave holds an answer of yours, and no draft of mine. Moving an item to chat answers nothing. Send it yourself, the whole wave at once, through `session-control` Step 2, with no yes of mine.

Any other wave waits for my Send, drive or not. You send nothing.

## Never

Never agree to what breaks a ruling of mine.

Never type into a pane I did not hand you. Outside a drive, my press of Send is the ruling.

Never write a change yourself. Name who writes it: one session, or split in two, with why.
