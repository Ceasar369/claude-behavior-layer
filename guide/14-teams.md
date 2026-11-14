# 14 — Teams

A team of its own: an assistant, one mission, and a helper.

## What it does

`/another-team` starts a new team on your subject, led by its own assistant. The assistant plans with you, writes each mission, and launches it. A mission holds one grant line per helper, each for one part, through `/helper-session`. Swarmed work starts several Haiku helpers at once: `knowledge/0010-playbook/0011-assisting/assisting-protocols/protocol-swarming.md` says how.

Here the team runs without a drive: you carry each step by hand. Document 17 drives one.

## Start the team

In 02:

```
/another-team a word count for the guide: code/guide-words.py prints each guide document's word count, then the total, with a test beside it.
```

Team 10 opens below. A team takes the lowest free ten, with no word to name another.

Its first plan, from a bare subject, held far more than I asked: discovery, a prototype, and two more stages. It took eight minutes.

## Every ruling, in one line

So your line to an assistant carries every ruling: what each mission does, who it is for, when, why, and what it may not do. Type into 10:

```
No. Plan one stage, A, of one mission alone, A1 word counter: it writes code/guide-words.py, which prints each guide document's name and word count, then the total, a word being what wc -w counts; and code/test_guide_words.py beside it, which checks every count against wc -w. Its mission's Your folder holds this line: A helper may take the test, code/test_guide_words.py, through helper-session. A1 builds the script, and starts that helper for the test. My rulings, up front: who, me; when, now; why, to try a team of one. The output is plain text, a name then its count, as code/guide-lines.py prints. No discovery, no prototype, no later stage. No commit, no push, no server, no band 00. Once I agree, launch A1 without a drive.
```

It planned A1 alone. Its plan shows at `http://localhost:1100/p/assistant/10`.

A helper needs its grant in the mission: "A helper may take <part>, through `helper-session`." `/helper-session` runs only inside a mission that holds it. The assistant writes the line when your words ask for it, as mine did.

## Launch the mission

Type into 10:

```
Agree. Launch A1 now, without a drive.
```

10 writes A1's mission, and launches it as session 11.

The first time I typed that line, it never reached 10. Typed again, it landed. If 10's prompt stays empty, type it again.

## The helper

11 builds the script, then starts a helper, 12, for the test. My last walk's 11 asked nothing first: "Your mission says "start one helper", so I didn't ask you first." If yours lays out one item first, a helper writing the test, type into 11:

```
Agree item 1.
```

12 writes the test, and reports to 11. 11 checks it, then stops 12.

11 then writes its report. Its move tells you to tell session 10 that A1 is complete.

## Close it

Type into 10:

```
A1 is complete. Its report: .claude/state/sessions/11/report.md.
```

10 reruns the test files 11's report names, never a browser walk, and keeps its verdict. With no drive, it asks: "Type `/9-session-stop` in session 11." Its plan page, `http://localhost:1100/p/assistant/10`, offers Send to 11. Or type the stop into 11 yourself:

```
/9-session-stop
```

That ends the plan. Then type `/9-session-stop` into 10.

End to end, my team took 37 minutes.

A jury can weigh a question you give `/jury`. Its Jury tab's Launch works while its session is busy.

## Unproven here

- A drive in this team. A drive may push to your phone, so I left it out.
- A mission with no grant line, asking for a helper.
- The plan page's Send to 11. I typed the stop myself.
- Jury Launch while its session is busy.

## Check

```
python3 code/guide-words.py
wc -w guide/*.md
```

Both print the same count for each document, and the same total.

```
taskpolicy -b python3 code/test_guide_words.py
```

The test passes. `taskpolicy -b` runs it at low priority.
