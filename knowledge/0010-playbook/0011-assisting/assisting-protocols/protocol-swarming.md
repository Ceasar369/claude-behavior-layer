# Protocol — Swarming

Up: [[assisting-protocols-MOC|Protocols]]

Known parallel work: when one big task holds no thinking left, and splits into pieces.

## When it applies

Every ruling the work needs is made. Work still holding a choice is never swarmed.

## Why sessions, not subagents

Subagents share their session's number, so its ports. Their browser tests run one at a time.

Each session takes its own number and ports. Their tests run side by side.

## The steps, in order

1. **Split the work into pieces.** No two pieces write one file. Two that must, run one after the other.
2. **Brief each piece.** One target, the files it writes, and its `Done when:`. The brief lists each subagent's exact edits.
3. **Launch through the skill that already launches.** A helper through `helper-session`, a mission through its stage. Each session runs Haiku, at high effort.
4. **Each session spreads its piece over subagents.** Each subagent takes one exact list.
5. **Rerun every proof a session reports.** Haiku sometimes reports work done without checking it.
6. **Stop each session once its proof holds.**
