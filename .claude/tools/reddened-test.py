#!/usr/bin/env python3
"""Check lib/page.py's colour watch keeps its place across a restart of 1100.

On lib/trial.py's made-up folder, session 11 works, so it reads green. A
1100 keeps the colours, stops, and session 11's turn ends meanwhile. The
1100 that starts next acts on it once, and the one after acts on nothing.
A number another session took since is acted on by neither.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "lib"))
import page  # noqa: E402
import trial  # noqa: E402


class Kept(unittest.TestCase):
    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.kept = os.path.join(folder.name, "colours.json")
        self.told = []
        self.acts = [lambda nn, word, name: self.told.append((nn, word, name))]

    def ends(self, nn: str) -> None:
        """Session NN's turn, ended: Claude Code's own record of it reads idle."""
        path = os.path.join(self.w.account, "sessions", f"{40000 + int(nn)}.json")
        with open(path) as f:
            record = json.load(f)
        with open(path, "w") as f:
            json.dump({**record, "status": "idle"}, f)
        trial.forget()

    def start(self) -> dict:
        """A 1100 starting: the colours it takes up, and its first look."""
        was = page.remembered(self.kept)
        return page.acted(page.colours() if was is None else was, self.acts, self.kept)

    def test_a_session_gone_red_while_1100_was_down_is_acted_on_once(self):
        self.assertEqual(page.colours()["11"][0], "green")
        self.start()
        self.assertEqual(self.told, [])
        self.ends("11")
        self.start()
        self.assertEqual(self.told, [("11", "idle", "trial-work")])
        self.start()
        self.assertEqual(len(self.told), 1)

    def test_with_no_colours_kept_a_start_acts_on_nothing(self):
        self.ends("11")
        self.start()
        self.assertEqual(self.told, [])

    def test_a_number_another_session_took_is_left_out(self):
        self.start()
        with open(self.kept) as f:
            kept = json.load(f)
        kept["11"][3] = "another-session"
        with open(self.kept, "w") as f:
            json.dump(kept, f)
        self.ends("11")
        self.assertNotIn("11", page.remembered(self.kept))
        self.start()
        self.assertEqual(self.told, [])

    def test_an_act_that_raises_keeps_no_other_from_its_turn(self):
        def broken(nn, word, name):
            raise ValueError("this act fails")
        self.acts.insert(0, broken)
        self.start()
        self.ends("11")
        with contextlib.redirect_stderr(io.StringIO()):
            self.start()
        self.assertEqual([t[0] for t in self.told], ["11"])


if __name__ == "__main__":
    unittest.main()
