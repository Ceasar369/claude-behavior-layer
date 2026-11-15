# The Formats

Up: [[the-stack-MOC|The Stack]]

How an id, an amount, a rate and a time are held, everywhere.

## The identifiers

### A prefix, an underscore, then base58

An id is random bits, written in base58. A record never kept, read again on
every read, takes bits hashed from its source: the same source, the same id.

Base58 drops the characters people confuse. Zero and O. Capital I and l.

`<prefix>_7Fh2kQ...`

### The prefix names the kind

It is never decoration. Read an id and you know what it is.

### The id is the primary key

A counting number may sit beside it, to keep rows in the order they came.

### An id is never sequential

It leaks how much business we do, and lets someone walk our rows by counting.

A short number a person reads may count up. It is never its id.

### A time-ordered id is not used

UUIDv7 sorts by time, which keeps an index tidy.

It also carries the moment of creation inside it.

## The money

### Integer minor units

Money is an integer number of minor units. Never a float.

Postgres stores it as `bigint`.

### The currency sits in its own column

> **Stand-in.** This project's currencies.

The column exists even for one, held to it by a check. Adding a currency changes
that check, never a column.

### The Postgres money type is never used

It carries no currency, and it shifts with the machine's locale.

### A rate is basis points

A rate is an integer number of basis points.

2.9% is `290`. Postgres stores it as `bigint`, never `numeric`.

### Rounding happens once

Amount times rate, divided by 10,000, then rounded once.

Half up, to the minor unit.

### A rate is stamped when it is applied

It is never looked up again afterwards.

A rate that changes must not rewrite what already happened.

## The time

### An instant is stored in UTC

The column is `timestamptz`.

It travels as ISO 8601, ending in `Z`.

### A calendar date is not an instant

A payment due on 1 March is a calendar date.

Held as a timestamp, it reads as 28 February west of UTC.

So a calendar date is `date`. Never `timestamptz`.

### Display converts. Storage never does

A screen shows the viewer's own clock, from their device.

A period that cuts rows by our days reads one fixed clock, never the viewer's.
