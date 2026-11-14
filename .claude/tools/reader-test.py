#!/usr/bin/env python3
"""Check lib/reader.py, and the process list 1100 reads through it.

A Reader run alone reads at each ask. Started, it reads on a thread of its
own, and an ask takes its last answer and starts nothing. A read that
raises keeps the last answer. Nobody asking, it stops reading.

The process list read in the background must say what ps itself says: when
each process started, which terminal it sits on, and every process there
is. `fresh` still asks ps.

With the readers 1100 starts, a draw of the handover page on the real
sessions folder starts no program: which sessions run, and a seat's own
claude line, both come from the process list read in the background.
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import threading
import time
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import handover as handover_lib  # noqa: E402
import live  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import ports  # noqa: E402
import reader  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402
import trial  # noqa: E402
import wake  # noqa: E402


def until(check, seconds: float = 5) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        if check():
            return True
        time.sleep(0.02)
    return check()


class Readers(unittest.TestCase):
    def test_alone_it_reads_at_each_ask(self):
        reads = []
        r = reader.Reader(lambda: reads.append(1) or len(reads))
        self.assertEqual([r.last(), r.last()], [1, 2])

    def test_started_an_ask_takes_the_last_answer_and_reads_nothing(self):
        reads = []
        r = reader.Reader(lambda: reads.append(1) or len(reads), every=0.05)
        r.start()
        self.assertTrue(until(r.running))
        count = len(reads)
        got = [r.last() for _ in range(50)]
        self.assertLessEqual(len(reads), count + 1)
        self.assertTrue(all(count <= g <= count + 1 for g in got))
        self.assertTrue(until(lambda: len(reads) > count + 2), "it reads on, while a draw asks")

    def test_a_read_that_raises_keeps_the_last_answer(self):
        state = {"n": 0}

        def read():
            state["n"] += 1
            if state["n"] > 1:
                raise OSError("the program failed")
            return "first"
        r = reader.Reader(read, every=0.02)
        with contextlib.redirect_stderr(io.StringIO()):
            r.start()
            self.assertTrue(until(r.running))
            self.assertEqual(r.last(), "first")
            self.assertTrue(until(lambda: state["n"] > 3))
            self.assertEqual(r.last(), "first")

    def test_nobody_asking_it_stops_reading(self):
        reads = []
        r = reader.Reader(lambda: reads.append(1) or len(reads), every=0.02)
        with mock.patch.object(reader, "WANTED", 0.5):
            r.start()
            r.last()
            time.sleep(1.5)
            count = len(reads)
            time.sleep(0.5)
            self.assertEqual(len(reads), count)
            r.last()
            self.assertTrue(until(lambda: len(reads) > count))


class Idle(unittest.TestCase):
    """A reader gone idle never hands a draw what it read before."""

    def test_the_first_ask_after_an_idle_spell_gets_what_stands_now(self):
        state = {"map": "two panes"}
        r = reader.Reader(lambda: state["map"], every=0.05)
        with mock.patch.object(reader, "WANTED", 0.3):
            r.start()
            self.assertTrue(until(r.running))
            self.assertEqual(r.last(), "two panes")
            time.sleep(1.2)
            state["map"] = "three panes"
            self.assertEqual(r.last(), "three panes")

    def test_a_draw_after_an_idle_spell_shows_what_stands_now(self):
        state = {"map": "two panes"}
        kept = reader.Reader(lambda: state["map"], every=0.05)
        table = live.Table([live.Page(r"/p/map/(\d{2})", lambda nn: f"<p>{kept.last()}</p>", looks=[kept.last])])
        with mock.patch.object(reader, "WANTED", 0.3):
            kept.start()
            self.assertTrue(until(kept.running))
            self.assertIn("two panes", table.route("/p/map/05"))
            time.sleep(1.2)
            state["map"] = "three panes"
            self.assertIn("three panes", table.route("/p/map/05"))

    def test_a_program_that_will_not_answer_never_holds_the_draws_up(self):
        state = {"slow": 0.0}

        def read():
            time.sleep(state["slow"])
            return "an answer"
        r = reader.Reader(read, every=0.05, patience=0.2)
        with mock.patch.object(reader, "WANTED", 0.3):
            r.start()
            self.assertTrue(until(r.running))
            r.last()
            time.sleep(1.0)
            state["slow"] = 2.0
            began = time.time()
            self.assertEqual(r.last(), "an answer")
            first = time.time() - began
            began = time.time()
            r.last()
            self.assertLess(first, 1.0)
            self.assertLess(time.time() - began, 0.1)
            self.assertTrue(r.aged())


class Processes(unittest.TestCase):
    """The process list, read through a Reader of its own, against ps itself."""

    def setUp(self):
        # A process that ended before the list was read: a pid gone.
        ended = subprocess.Popen(["/usr/bin/true"])
        ended.wait()
        self.kept = reader.Reader(ports.everything)
        self.kept.once()
        self.kept.started = True
        self.mine = [os.getpid(), os.getppid(), 1, ended.pid]

    def test_it_says_what_ps_says(self):
        real = ports.started(self.mine)
        self.assertEqual(len(real), 3)
        ttys = {pid: panes.tty_of(pid) for pid in [int(d["pid"]) for d in registry.claude_records(fresh=True).values()]}
        table = dict((pid, (parent, command)) for pid, parent, command in wake.table())
        with mock.patch.object(ports, "PROCESSES", self.kept), mock.patch.object(subprocess, "run") as ran:
            self.assertEqual(ports.started(self.mine), real)
            self.assertEqual({pid: panes.tty_of(pid) for pid in ttys}, ttys)
            seen = dict((pid, (parent, command)) for pid, parent, command in wake.table())
            self.assertEqual(seen[1], table[1])
            self.assertEqual(seen[os.getpid()][0], table[os.getpid()][0])
            ran.assert_not_called()

    def test_fresh_still_asks_ps(self):
        with mock.patch.object(ports, "PROCESSES", self.kept), \
                mock.patch.object(subprocess, "run", wraps=subprocess.run) as ran:
            self.assertIn(os.getpid(), ports.started([os.getpid()], fresh=True))
            self.assertEqual(ran.call_count, 1)

    def test_a_process_too_new_for_the_list_is_asked_of_ps(self):
        with subprocess.Popen(["/bin/sleep", "5"]) as born:
            with mock.patch.object(ports, "PROCESSES", self.kept):
                panes.TTYS[:] = [0.0, {}]
                self.assertNotIn(born.pid, self.kept.last())
                self.assertEqual(panes.tty_of(born.pid), panes.tty_of(os.getpid()))
            born.kill()


class Records(unittest.TestCase):
    """Claude Code's records, on lib/trial.py's made-up folder: inside 1100,
    a status that just moved is read at once."""

    def ends(self, w) -> None:
        path = os.path.join(w.account, "sessions", "40011.json")
        with open(path) as f:
            record = json.load(f)
        with open(path, "w") as f:
            json.dump({**record, "status": "idle"}, f)

    def status(self) -> str:
        return registry.claude_records()["00000000-0000-4000-8000-000000000011"]["status"]

    def test_alone_an_answer_is_kept_a_second(self):
        with trial.world() as w:
            self.assertEqual(self.status(), "busy")
            self.ends(w)
            self.assertEqual(self.status(), "busy")

    def test_inside_1100_a_status_that_moved_is_read_at_once(self):
        kept = reader.Reader(dict)
        kept.once()
        kept.started = True
        with trial.world() as w, mock.patch.object(ports, "PROCESSES", kept):
            self.assertEqual(self.status(), "busy")
            self.assertIs(registry.claude_records(), registry.claude_records())
            self.ends(w)
            self.assertEqual(self.status(), "idle")


class Draws(unittest.TestCase):
    """A draw of the handover page on the real sessions folder, with the
    readers 1100 starts: the process list's, and iTerm's panes'."""

    def test_the_handover_page_draws_and_starts_no_program(self):
        table = live.Table([page.tool("handover-page").LIVE])
        kept = reader.Reader(ports.everything)
        kept.once()
        kept.started = True
        asked, last = [], kept.last
        kept.last = lambda: asked.append(1) or last()
        seen = panes.terminals()
        me, begun, real = threading.get_ident(), [], subprocess.Popen.__init__

        def counted(popen, args, *more, **named):
            if threading.get_ident() == me:
                begun.append(args if isinstance(args, str) else " ".join(map(str, args)))
            return real(popen, args, *more, **named)

        held = sorted(registry.entries())
        with mock.patch.object(ports, "PROCESSES", kept), mock.patch.object(panes, "REFRESHING", [True]), \
                mock.patch.object(panes, "LAST", [time.time(), seen]), \
                mock.patch.object(subprocess.Popen, "__init__", counted):
            for nn in held:
                registry.PUBLISHED[:] = [0.0, None]
                panes.TTYS[:] = [0.0, {}]
                with wake.once():
                    drawn = table.route(serve.address("handover", nn))
                self.assertIsInstance(drawn, str, nn)
                self.assertNotIn("failed to draw", drawn, nn)
            # A seat's own claude line, as lib/handover.py reads it when the
            # seat has no named.json: each seat's, then one running session's.
            running = {int(r["pid"]) for r in registry.claude_records().values()}
            for nn in held:
                handover_lib.named(nn)
            lines = {pid: handover_lib.own(pid) for pid in sorted(running)}
        print(f"The handover page, drawn for {len(held)} real sessions, and {len(lines)} running sessions' own claude "
              f"lines read: {len(begun)} programs started, and the background reader asked {len(asked)} times "
              "for the process list.")
        self.assertEqual(begun, [])
        self.assertGreater(len(asked), len(held))
        # What the reader says is what ps itself says.
        self.assertEqual(lines, {pid: handover_lib.own(pid) for pid in lines})


if __name__ == "__main__":
    unittest.main()
