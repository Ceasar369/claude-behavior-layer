#!/usr/bin/env python3
"""Check hooks/handed.py holds words handed for a driven session, under any move."""

import importlib.util
import os
import unittest

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks", "handed.py")
spec = importlib.util.spec_from_file_location("handed", HOOK)
handed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handed)

BLOCK = "\n▼▼▼ START COPY ▼▼▼\n\nFold in the fixes.\n\n▲▲▲ END COPY ▲▲▲\n"


class Handed(unittest.TestCase):
    def test_a_copy_block_under_a_ruling_is_held(self):
        said = "**Your move**\nRuling: I type the words below into session 05." + BLOCK
        self.assertEqual(handed.handed(said), {"05"})

    def test_a_copy_block_under_an_answer_is_held(self):
        said = "Session 05 asks which port.\n" + BLOCK + "\n**Your move**\nAnswer: say if 7205 is right."
        self.assertEqual(handed.handed(said), {"05"})

    def test_the_send_shape_is_still_held(self):
        self.assertEqual(handed.handed("Send to session 05." + BLOCK), {"05"})

    def test_a_copy_block_naming_no_session_passes(self):
        said = "Paste this line into Terminal." + BLOCK + "\n**Your move**\nRuling: I build it now."
        self.assertEqual(handed.handed(said), set())

    def test_a_session_named_with_no_copy_block_passes(self):
        said = "Session 05 finished its build.\n**Your move**\nRuling: I check session 05's work."
        self.assertEqual(handed.handed(said), set())

    def test_a_stop_is_mine(self):
        self.assertEqual(handed.handed("Action: type `/9-session-stop` in session 05."), set())


if __name__ == "__main__":
    unittest.main()
