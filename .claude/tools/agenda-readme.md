# My agenda

What I want worked on, or set aside, and what waits on what.

It is mine alone. It helps me see my work, and connect it.

1100 draws it, under Agenda on the rail.

## What it is not

It is not truth. It is not a ruling. It is not work.

Nothing in it was decided. Nothing in it is pending.

## Who opens it

You open it only when I mention it.

Asked what to work on next, I did not mention it. You never open it then.

An item never moves you to act. Only my words do.

A search landing here proves nothing. Treat it as no decision.

Handed an item, you look at its subject with me, like any other. The item only reminds me of it. Never talk about the item itself.

## Who writes it

Only my word puts an item on it: I dictate it, or agree to one a session proposes. No proposed item is written before my yes.

You write it only on my word, through `6-agenda`.

How you organise it with me: `knowledge/0010-playbook/0016-agenda/agenda-protocols/protocol-agenda.md`.

Every write goes through `.claude/tools/agenda.py`, never by hand.

New items follow the standard, its note's shape below, from the start.

A quick idea enters with its What alone. Its Why and Done when are written when it's first worked. Nothing is invented to fill a line.

Wording is applied. Meaning comes to me first.

Research leaving a note goes to my references, as `knowledge/0010-playbook/0019-targeted/the-map/outside-the-project.md` says. The Sources line names it.

## An item

One file per item, named for it, like `keys-after-a-wipe.md`:

```
Read README.md first. This item is part of my agenda, and mine alone.

# Reports kept after a crash

Waits on: panes-closed-on-crash
Topics: Behaviour

What: Fix, small: keep a session's report when its pane crashes.
Why: until then, the handover's "Nothing you said is lost." is not true.
Done when: a crashed pane's report reaches its successor, as the handover says.
Sources: .claude/skills/session-report/SKILL.md
```

"Waits on" lists the file names of the items it waits on.

"Topics" names its topics, one or more of those below.

"Phase", under it, names its phase, when the project names phases, as below.

An item never names a session.

Dealt with, an item comes down, with its lines. What waited on it then waits on what it waited on. Partly dealt with, it stays up, its What trimmed to what is left. The trim reaches me first.

Folded into another item, it first hands that item its words, and every wait but that item itself. What waited on it then waits on that item instead. Then it comes down.

A take-down proposal quotes the item's Done when, and the proof it holds: a file, a test, or my words. No proof → it proposes partly done instead, and the item stays up. An item with no Done when comes down on my word.

A loop never enters. Two items waiting on each other share one new item, and both hang on it.

## Its topics

This project names its topics in `topics.json`, beside this file. They are headings, never items, and never come down.

Until it names its own, one topic stands in:

- Behaviour: how our sessions, skills and tools work.

`topics.json` lists the topics in order, each with its colour, then the screens an item may name. The stand-in, written there, reads:

```
{
  "topics": [{"name": "Behaviour", "colour": "#94a3b8"}],
  "screens": []
}
```

Each is a rectangle, down the first column, in that order, wearing its own colour. An item wears no colour of its own.

Every line keeps its meaning: the items most on the left are dealt with first. Out of each rectangle come the items under its topic that wait on nothing.

## Its phases

A project may split its agenda into phases, named in `topics.json` after its screens, in order, as `"phases": ["1", "2"]`. None named, the agenda has none. Each phase's heading is named there too, as `"headings": {"1": "Phase 1: Launch"}`.

Each phase is then its own chart, with its own rectangles, the first on top.

Every item names its phase. An item waits only on items of its own phase. `agenda.py` refuses a wait joining two, and its check names any.

## Its note

A note says up to three things, in order. Only What is needed at first.

- What: its action and its size, then what it applies to, as "Fix, small: …". The action is Look at, Verify, Fix, Do or Decide. The size is small, one session under an hour; medium, one session for a few hours; or large, a team of sessions. An item whose result shows on a screen names it after its size, one of the screens `topics.json` names, as "Fix, small, web app: …". None named, no item names a screen. Never a subject alone.
- Why: what it unblocks, or what breaks without it.
- Done when: the fact that lets the item come down.

An item whose next step is mine carries one line, Mine, naming that ruling or act. Sessions read it, and never take that step. No Mine line: any session may work the item.

The Mine line opens with `Mine:`, then one sentence naming the ruling or the act:

```
Mine: which side moves, the vault or the code.
Mine: putting Jobber's regenerated client secret in my password manager.
```

A note stating a fact names its file, page or reference, in one Sources line. An item holding no fact beyond its own words needs none.

A note holds no research. Research lives in my references, and the Sources line names it. A note stays at 60 words at most.

Each line sits alone, once at most, in this order: What, Why, Done when, Mine, Sources. Only What is needed. `agenda.py` refuses a note breaking it.
