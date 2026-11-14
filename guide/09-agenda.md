# 09 — Agenda

Your agenda: what you want worked on, under topics, and what waits on what.

## What it does

`/6-agenda` keeps the items you dictate, each under a topic. 1100 draws them, under Agenda. Agenda sits under the utilities button on its rail, closed until you open it. Your agenda never enters git: it stays on your Mac, in `.claude/state/agenda/`.

## Your first try

In session 02:

```
/6-agenda add three items under Behaviour. One: the README names the line a newcomer types first. Two: code/guide-lines.py gets a test. Three: this trial folder is deleted once the walk ends, after the other two.
```

The agenda starts on its first command: `.claude/state/agenda/README.md` appears. It wrote each item as "Do, small": one session, under an hour, since my words named no size. In my walk: one minute.

It may propose one line more. Mine proposed a "Mine" line for item 3: an item only I can act on. I said yes.

Open `http://localhost:1100/agenda`. It draws the three under Behaviour, the first two arrowing into the third.

## Triage one item

```
/6-agenda triage the item guide-lines.py gets a test
```

It says what exists today, then recommends an ending: here, a new session writing the test. Rule its ending in words:

```
Keep it. Launch nothing.
```

It keeps the item, then says the triage stays open until you say close. Leave it open, as I did: 02 takes your next lines as before. Saying `close` ends it: 02 writes its report, then stops itself.

## Your own topics

Until you name your topics, one stands in: Behaviour. Document 20 names yours.

## Unproven here

- Your own topics. My walk kept Behaviour.
- An ending that launches a session. I kept the item.
- Saying `close` to a triage. Mine stayed open.

## Check

- `.claude/state/agenda/` holds `README.md`, and one file per item.
- 1100's Agenda page shows the three items under Behaviour.
