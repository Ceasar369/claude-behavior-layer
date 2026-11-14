#!/usr/bin/env python3
"""Check lib/items.py's reading, and both hooks that import it, on a range of items."""

import importlib.util
import os
import sys
import unittest

LAYER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(LAYER, "lib"))
import items  # noqa: E402


def hook(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LAYER, "hooks", f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


plain = hook("plain")
shown = hook("shown")


def laid(*ns) -> str:
    return "".join(f"**{n} · Item {n}'s title**\nIts case.\n\n" for n in ns)


class Items(unittest.TestCase):
    def test_a_range_is_every_item_in_it(self):
        self.assertEqual(items.asked("Ruling: agree items 15 to 21."), list(range(15, 22)))
        self.assertEqual(items.asked("items 7 and 8, item 10"), [7, 8, 10])

    def test_plain_holds_a_range_with_only_its_ends_laid_out(self):
        turn = laid(15, 21) + "Ruling: agree items 15 to 21."
        self.assertEqual(plain.faults(turn)[1], ["items 15 to 21"])

    def test_plain_passes_a_range_laid_out_whole(self):
        turn = laid(*range(15, 22)) + "Ruling: agree items 15 to 21."
        self.assertEqual(plain.faults(turn)[1], [])

    def test_shown_reads_the_same_range(self):
        words = laid(15, 21)
        self.assertEqual([n for n in items.asked("Ruling: agree items 15 to 21.")
                          if not items.laid_out(n, words)], [16, 17, 18, 19, 20])
        self.assertIs(shown.items, items)


if __name__ == "__main__":
    unittest.main()
