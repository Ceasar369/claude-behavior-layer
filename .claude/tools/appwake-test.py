#!/usr/bin/env python3
"""Check lib/appwake.py: nothing in it can type into the Claude app.
No pane, no app."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import appwake  # noqa: E402


class NeverTypes(unittest.TestCase):
    """Session 99 once told my app chat it was done, typed into the Claude app."""

    def test_no_way_to_type_or_watch(self):
        for gone in ("wake", "watch", "KEYS", "FRONT", "AX", "_jxa"):
            self.assertFalse(hasattr(appwake, gone), gone)

    def test_no_script_runner_or_keystroke(self):
        with open(appwake.__file__) as f:
            src = f.read()
        for word in ("osascript", "subprocess", "keystroke", "System Events"):
            self.assertNotIn(word, src)


if __name__ == "__main__":
    unittest.main(verbosity=1)
