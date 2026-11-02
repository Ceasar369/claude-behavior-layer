---
name: clarify-items
description: Lays out every item I must rule on, thought through whole and shown lean, in chat and on my page.
allowed-tools: Read, Glob, Grep
argument-hint: "[the scope] — omit for the work in hand, or to fold my answers after Send"
---

# Clarify Items

An item is one thing I rule on. Every item a wave shows is new.

`python3 .claude/tools/clarify-page.py` keeps the wave file. Never Read, Write or Edit one.

## Step 1 — Know which round this is

My number, as `CLAUDE.md` defines it.

Run `clarify-page.py answers NN`. It says `sent` → go to step 5.

It says `waiting on you`, and I wrote in chat since the wave → judge my message against it.

- It answers some items, or all → go to step 5. Only what I answered folds.
- It asks about an item → answer it in chat. The wave stays open.
- It moves on, to another subject or a discussion first → close the wave with `--chat`, marking nothing, then answer my message. Its items come back as a new wave when I return to them.

It says `waiting on you`, and I said nothing in chat → say the wave still waits on me, and stop.

It says `closed`, and you folded that wave last turn → my Send came late. Say it is already folded, and stop.

Otherwise, a new round starts at step 2.

## Step 2 — Find the items, and order them

Foundations first. An item that exists only if another passes waits for the next round.

One that builds on another sits after it, with `after: item N`.

The rest go weightiest first. Five at most. The rest wait, in order.

A round fills its five. An edge case or a later decision with room becomes an item of its own.

What finds no room gathers in one last item, after the five. Its title is Open questions; each takes one line. Its decision recommends which to explore now. One I explore becomes an item next round. The rest wait for later.

## Step 3 — Think each one through

Six questions. Each answer is one field.

1. **Frame.** What exactly is ruled? A file already rules it → no item. Quote it, and follow it. Mine, or not? Mine is what changes the use I want, or touches my standards, technical or not. Not mine → no item. Do it, and say so. → `question`
2. **Today.** What is true now? Read the file. Never memory. → `today`
3. **Instead.** What else could we do, today included? First, can something that exists do it: a setting, a tool or a skill? → `instead`
4. **Weigh.** My five axes, in `knowledge/0010-playbook/0013-thinking/the-thinking-axioms.md`. → `why`
5. **Follow.** What breaks, what it costs, who pays? Which one fact flips it? A fact a file already settles is checked, never left as the flip. → `wrong`
6. **Commit.** What exactly does agree build? → `decision`

## Step 4 — Show only what the item needs

Always `question`, `decision`, `why`, `wrong` and `sources`. One line each.

A name I have not been given is defined where it first appears.

Each condition met adds its one field. Nothing else shows.

| When it | Add |
|---|---|
| turns on steps in order | a chart in `show` |
| turns on where things live | a tree in `show` |
| compares things on the same points | a table in `show` |
| changes what exists | `today`, in the same picture |
| has a real alternative | `instead`, one line each, and why not |
| comes from my feedback | `from`, the words of mine it came from |

A picture is a fence inside its field. ` ```mermaid ` is a chart. Any other fence is text.

A chart is `flowchart TB`. The page draws it under the decision, and I can flip it. It tags each node `:::you`, `:::session`, `:::done` or `:::today`. `{}` is a condition, `[()]` a file. `-->` means then, `-.->` reads. Labels stay short.

A tree marks each changed line after its name, past two spaces: `+` new, `~` changes, `-` goes. `└── retry.ts   + new`.

The page draws the legend. Never write a style.

In chat, the same fields take bold labels: **Question**, **Decision**, **Why**, **Wrong if**, and so on. A tree or a table sits in a text fence. A chart becomes its flow in a text fence, one arrow per step: `a try fails → third try? → dead_letters`. Never a Mermaid fence.

## Step 5 — Fold my answers

`clarify-page.py answers NN` prints only my answers, under the wave's state. My chat answers count too. On one item, my chat words win over a page draft: Return sent them, and a draft waits for Send.

It reads `waiting on you` → mark each one on the page before the round closes: `clarify-page.py rule NN --item N --agree`, or `--feedback` with my words on stdin. An agree in my own words is `--agree`.

It reads `sent` → mark nothing. A sent wave is my record. A mark refused means my Send just closed it: mark no more.

Split each feedback into its parts. Each part gets one outcome.

- `agreed`
- `settled` — the rework says exactly my words.
- `new item N` — anything else it opens or changes.
- `answered` — a question, answered in chat before any rework.
- `moved to chat` — a subject that needs a discussion. It comes back as a new item, unless I rule it in chat.

"Explain", on an item, gets its subject explained, never a new proposal.

Show the fold in chat, as one text table: item, by number and title, my words in brief, what it became. A settled part shows its settled line. A new item shows its title beside its number.

An item I left unanswered comes back as it was, under a new number.

Close the round: `clarify-page.py close NN`. Closed in chat, never Send → add `--chat`, whatever the reason. No new item → say it closed, and how many were agreed.

## Step 6 — Lay the round out

Check first: each name I was never given is defined in its item. One is not → the round waits until it is.

Every round goes on my page and in chat: the same items, the same numbers. No number → run `0-session-start` first, then go on.

### On the page

```
python3 .claude/tools/clarify-page.py wave NN <<'EOF'
## Cap every job at three tries
question: Does a job stop retrying?
decision: Yes, after three tries. The fourth goes to the dead-letter table.
why: One bad row has retried forty thousand times since Tuesday.
wrong: Outages outlast three tries. Jobs die on faults that fixed themselves.
show: ```mermaid
  flowchart TB
    F[A try fails]:::session --> T{Third try?}
    T -- yes --> D[(dead_letters)]:::done
    T -- no --> F
  ```
sources: jobs/retry.ts
EOF
```

Each item opens with `## ` and its title. The tool numbers it.

A field's first line sits after its name. Every further line is indented two spaces, a fence's lines too.

`--then` is what Send types into my pane. My caller names it, for this wave alone.

The tool writes the wave. 1100 draws it in my hub, with a white dot on its number once this session's turn ends, until I send it or it closes in chat.

A wave found wrong before I answer → close it with `--chat`, say why in one line, and lay out the fixed one.

### In chat

Lay the same items out, with the same fields, under the wave's numbers. Head each item `N · its title`, as the page does.

Never ask which to start with. I rule in prose, in my own order.

## Never

Never explain a subject here. That is `clarify-explain`.

Never open a gate. The round is the gate.
