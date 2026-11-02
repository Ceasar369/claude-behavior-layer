# Protocol — Sizing A Stage

Up: [[assisting-protocols-MOC|Protocols]]

When you group a plan's missions into stages, and how many each holds.

## The steps, in order

Every step's skill is `assistant-stages`.

In an open plan, [[the-stages|The Stages]] places each mission. Step 3 still holds at each launch.

1. **Put what can start now in stage A.** A later mission starts once what it needs has stopped.
2. **Hold back a mission calling a part still being built.** It waits for it. It shares that stage only when it finishes without it, on fixtures. A mission whose last check needs that part's output waits a stage.
3. **Split two missions meeting through their whole work.** Two missions writing one part are read file by file. Meeting through their whole work, they never share a stage. Meeting at one step, they share it. The wait holds that step alone. Each mission names that step, and who goes first.
4. **Put each mission in the earliest stage it can join.** Only steps 2, 3 and 5 hold it back.
5. **Stop at the ceiling.** [[the-stages|The Stages]] names it.

## What reaches me

The plan, one line per stage, in chat and on your page.
