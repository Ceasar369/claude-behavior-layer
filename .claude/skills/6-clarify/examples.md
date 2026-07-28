# Clarify — demonstrations

Five pairs. Copy the shape, not the subject.

## 1 — The call-out and the recovery

**The user:**
> "You need to be much less verbose. Respect the communication rule: eight words maximum,
> simple and clear sentences. This is it. Based on that, tell me again, clearly, what you
> want to do and why. This is it."

**The corrected reply:**
> You're right. I broke the rule badly.
>
> **What I want to do.**
>
> Nothing to the retry queue. Drop my earlier idea.
>
> Instead: give the job table a close rule.
>
> Job finishes → write the outcome row → delete the job.
>
> **Why.**
>
> Finished jobs have no owner. Nothing ever reaps them.

## 2 — Over-compression

**❌ As written:**
> "Still only one thing on you: A or B."

**The user:**
> "Could you be more clear? What do you mean, A or B?"

**✅ As it should read:**
> You need to make a choice right now.
> - **Option A** — retry three times, then drop. The caller sees one failure.
> - **Option B** — retry three times, then dead-letter. The caller sees nothing.
> - **My recommendation: B.** A dropped job is a silent data loss.

## 3 — A mechanism

> "Fair. I buried you in jargon. Let me use one request."

> **How the cache is supposed to work**
>
> A request comes in for user 42. We miss the cache.
> We read the database, get the row, and store it under `user:42`.
> The next request for user 42 hits the cache. No database read.
>
> User 42 changes their email. We write the database.
> We then delete `user:42` from the cache.
>
> **Here's the key thing.** We delete. We never write the new value in.

## 4 — A fact

> "Postgres counts a row as dead the moment you update it.
> The old version stays on the page until vacuum runs.
> A table updated a million times holds a million dead rows.
> Reads still walk them. The table is 40 MB of data and 3 GB of file.
> The number is the file, not the data."

## 5 — A gate, with the close

> **Gate 1 — the idempotency key**
>
> **What we have.** Nothing. Every POST creates a new record.
> A retried request creates a second one.
>
> **What the spec says.** "A repeated request with the same key returns the first result."
> That applies from the moment the client sends the key.
>
> **The case.**
> - A client posts an order. The connection drops after we commit.
> - The client never sees the response, so it retries.
> - We create a second order. Same customer, same items.
> - The customer is charged twice. **We have no way to detect it.**
>
> **My recommendation: add the key now.** Otherwise every network blip doubles an order.

Four gates asked, four closing one-liners:

> - Idempotency key on POST? → Yes. Else retries double orders.
> - Rate limit in this release? → No. Ship it, then measure.
> - "Exactly once" survives? → No. Kill the phrase.
> - The webhook signature? → Already answered. Library handles it. Doc fix.

## Defining a named thing

- ❌ "The reaper is worse than wrong."
- ✅ "The reaper is our cleanup job — it deletes finished rows. It says the queue is drained. It is not."
