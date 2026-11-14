---
name: transcript
description: Writes this whole chat as one clean transcript file. Use when I say "give me the transcript", "transcript", or ask for this chat written out.
---

# Transcript

When I ask for the transcript, write one `.md` file of this whole chat, and give it to me to download.

## The file holds only this, in order

1. Its file name, as the one `#` heading. Example: `# transcript-2026-11-05.md`.
2. The date, on its own line. Example: `Thu 2026-11-05`.
3. Every exchange of this chat, from the first message.

The file name is `transcript-` then today's date, `YYYY-MM-DD`, then `.md`.

## Each exchange

Each exchange is my message, then yours.

Each message sits under its speaker, as a `###` heading: `### Me` for mine, `### Claude` for yours.

Every message is kept whole, word for word, in the order it was sent.

Never shorten, fix, reword or summarize a message. Code blocks, lists and links stay as they were.

Write only what was said in the chat. Never your tool calls, their results, or your thinking.

Stop at the message just before I asked for the transcript.

## Never in the file

- No parts, sections or headings beyond the file name and the speakers. No "Part 1".
- No opening paragraph. No line about setup, skills or tools run.
- No summary, note or comment, anywhere.
- No line between messages, like `---`.

## Edge cases

A message you cannot reproduce, like a picture or a file I sent, gets one line where it sat:

`[Picture not reproduced]`, or `[File not reproduced: name.pdf]`.

The rest of that message is still kept whole around it.

A message I typed among spoken ones is still my message. It stays under `### Me`, with no mark.

A chat too long for one write is still one file. Write it in pieces, appending in order, until every message is in.

## Then

Give me the file. Say nothing else but its name.
