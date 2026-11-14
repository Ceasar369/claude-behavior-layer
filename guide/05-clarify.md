# 05 — Clarify

How a session asks you something, and how you answer it, on 1100.

## What clarify is

Clarify is how a session lays something out for you. It has eight shapes, one job each. `/2-clarify` picks the shape your ask needs. Each shape also answers by its own name.

Most other skills end in one of its shapes, so it comes first.

## Your first try

In session 02, type:

```
/2-clarify what is 1100, in this layer?
```

It names the shape it picked: "Your ask is a thing to understand, so this calls `clarify-explain`." Then it answers in three parts: what it is, what it is not, one real case. In my walk: 56 seconds.

## A decision, answered on 1100

Type into 02:

```
I want a short welcome note at this project's root, for whoever opens it next. Two decisions are mine: the file's name, and whether it says this folder is only a trial of the layer. Lay them out for me to rule, then write it.
```

02 lays out two items, in chat and on 1100: a wave. Open `http://localhost:1100/p/clarify/02`.

On each item, press Agree, or type your own words. Then press Send. Send types your answers into 02's pane, and 02 writes the note, `README.md`.

Every decision a session needs from you waits on 1100 like this, under the session's number. Answers typed in chat count too.

## Each shape, by its own name

Each ran in my walk with these words, each in under a minute and a half.

**Understood** says back each instruction, then acts only on your word:

```
/clarify-understood Add a last line to README.md naming the commit this folder was walked on, from git log, and keep the file under twelve lines.
```

It said back two items. I typed `Agree both.`, and it added the line.

**Summary** says what is agreed, what is left to do, and what is still open:

```
/clarify-summary the README at this folder's root
```

**Steps** says what happens next, in order, each step with its owner:

```
/clarify-steps saving this folder's README in git, with /8-ship
```

**Green light** answers "can I do this now?", with every prerequisite, met, not met, or unproven:

```
/clarify-green-light launch a second session in this folder now, with /launch
```

**Full picture** steps back in three sections, each zooming into the one before:

```
/clarify-full-picture I'm lost in this folder's work so far
```

**Explain** and **items** are the two you met above.

**Recap** is the eighth. `/clarify-recap-items` writes every item you agreed in a session's waves into one file, each as its question and final answer.

A move like "say go, and I run `/8-ship`" waits for your go. Say nothing, and nothing runs.

## Unproven here

- macOS asking to let Python control iTerm2, at your first Send. My Mac allowed it long ago.
- `/clarify-recap-items`. No walk ran it here.

## Check

- `README.md` sits at your project's root.
- `http://localhost:1100/p/clarify/02` reads "This wave is sent."
