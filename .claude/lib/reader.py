#!/usr/bin/env python3
"""reader.py — what only a program can tell, read on a thread of its own.

iTerm's layout, the process list and the ports each take a program to
read, and a draw that starts one makes every other draw wait behind it.
A Reader reads for the draws: 1100 starts it, it asks every few seconds
while a draw asked within the last minute, and a draw takes its answer
at once. An answer unlike the one before is told at once, moved(), so
the page showing it never waits for a recheck.

Nobody asking, it stops reading, and its answer ages. A draw is never
handed that: the first ask after an idle spell wakes the thread, and
waits for what stands now, `patience` seconds at most. Only a program
that does not answer in that time leaves a draw the older answer, and
aged() says so.

A tool run alone starts none. There, last() reads for itself each time,
as before.

Imported, never run.
"""

import sys
import threading
import time
import traceback

# How long after a draw's last ask a reader keeps reading.
WANTED = 60
# Each is called once a read answers differently from the one before. A
# server hands its pulse's renew() here, so a page whose look reads that
# answer is asked about at once, never a recheck later.
MOVED: list = []


def moved() -> None:
    """Tell whoever waits that an answer read in the background moved."""
    for tell in list(MOVED):
        tell()


class Reader:
    """One thing read in the background: `read` is the program's answer,
    asked every `every` seconds once start()ed."""

    def __init__(self, read, every: float = 3, patience: float = 2):
        self.read, self.every, self.patience = read, every, patience
        self.got, self.at, self.asked, self.started, self.said = None, 0.0, 0.0, False, 0.0
        # When a read was last tried, each read done, counted, and the one
        # a draw last gave up waiting on.
        self.tried, self.reads, self.given_up = 0.0, 0, -1
        self.turn = threading.Condition()

    def start(self) -> None:
        """Read on a thread of its own from now on, for as long as the
        caller runs. A second start changes nothing."""
        if self.started:
            return
        self.started = True
        threading.Thread(target=self.run, daemon=True).start()

    def run(self) -> None:
        while True:
            if not self.at or self.wanted():
                self.once()
            # Its nap ends early when a draw asks after an idle spell.
            with self.turn:
                self.turn.wait(self.every)

    def once(self) -> None:
        """One read. A read that raises keeps the last answer, and is
        logged, once a minute at most. An answer unlike the one before is
        told: moved()."""
        try:
            got = self.read()
            news = bool(self.at) and got != self.got
            self.got, self.at = got, time.time()
            if news:
                moved()
        except Exception:
            if time.time() - self.said >= 60:
                self.said = time.time()
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} reader: a read failed", file=sys.stderr)
                traceback.print_exc()
        with self.turn:
            self.tried, self.reads = time.time(), self.reads + 1
            self.turn.notify_all()

    def running(self) -> bool:
        """Whether a thread reads for the draws, and has an answer in hand."""
        return self.started and bool(self.at)

    def aged(self) -> bool:
        """Whether no read was tried lately: the thread went idle, or its
        program has not answered yet."""
        return time.time() - self.tried > self.every * 2

    def wanted(self) -> bool:
        """Whether a draw asked within the last WANTED seconds."""
        return time.time() - self.asked < WANTED

    def want(self) -> None:
        """Keep the thread reading, with no answer taken: for a read that
        starts a job, which no draw waits on."""
        self.asked = time.time()

    def last(self):
        """The answer as it stands, at once while the thread reads. With no
        thread reading, it is read now. After an idle spell, the thread
        reads at once and the ask waits for it, `patience` seconds at
        most, once per read: a program that will not answer never holds
        the draws up."""
        self.asked = time.time()
        if not self.running():
            self.once()
            return self.got
        if self.aged():
            with self.turn:
                seen = self.reads
                if seen != self.given_up:
                    self.turn.notify_all()
                    if not self.turn.wait_for(lambda: self.reads != seen, self.patience):
                        self.given_up = seen
        return self.got
