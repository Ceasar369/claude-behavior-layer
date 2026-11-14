#!/usr/bin/env python3
"""Check library-review.py, and the marks library-page.py draws from it, on
a library and a record of their own, never the real ones."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import page  # noqa: E402

lib = page.tool("library-page")
rv = page.tool("library-review")

MOC = """# Library

## Alpha

### Direct

- Graph: [[flow|Flow]]
- [[one|One]]
- [[two|Two]]

### Other

- [[three|Three]]
"""
GRAPH = "# Flow\n\nUp: [[library-MOC|Library]]\n\n## The text\n\nIt flows.\n\n## The graph\n\n1. Start [[one]]\n"


class Reviews(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = folder.name
        os.mkdir(os.path.join(self.root, lib.GRAPHS))
        self.write(lib.MOC, MOC)
        for name in ("one", "two", "three"):
            self.write(f"{name}.md", f"# {name}\n\n## What it is\n\nThe {name}.\n")
        self.write(os.path.join(lib.GRAPHS, "flow.md"), GRAPH)
        for module, name, value in ((lib, "LIBRARY", self.root),
                                    (rv, "FOLDER", os.path.join(self.root, "state")),
                                    (rv, "RECORD", os.path.join(self.root, "state", "reviews.json"))):
            self.addCleanup(setattr, module, name, getattr(module, name))
            setattr(module, name, value)

    def write(self, name, text):
        with open(os.path.join(self.root, name), "w") as f:
            f.write(text)

    def states(self):
        with open(os.path.join(self.root, lib.MOC)) as f:
            rows = lib.numbered(lib.tree(f.read()))
        return {k: s for k, (s, _) in rv.states(rows, lambda r: rv.text_of(lib, r)).items()}

    def test_every_item_starts_never_reviewed(self):
        self.assertEqual(self.states(), {"graphs/flow": "new", "one": "new", "two": "new", "three": "new"})

    def test_a_number_a_file_or_a_name_marks_one(self):
        self.assertEqual(rv.marked("1.1.1", "reviewed"), (True, "Word 1.1.1, One, is marked reviewed."))
        self.assertEqual(rv.marked("graphs/flow", "reviewed"), (True, "Graph 1.1.A, Flow, is marked reviewed."))
        self.assertEqual(rv.marked("Three", "reviewed"), (True, "Word 1.2.1, Three, is marked reviewed."))
        self.assertEqual(self.states(), {"graphs/flow": "ok", "one": "ok", "two": "new", "three": "ok"})

    def test_an_edit_or_a_move_shows_as_changed(self):
        rv.marked("one", "reviewed")
        rv.marked("three", "reviewed")
        self.write("one.md", "# one\n\n## What it is\n\nThe one, grown.\n")
        self.write(lib.MOC, MOC.replace("- [[three|Three]]\n", "").replace("- [[two|Two]]\n", "- [[two|Two]]\n- [[three|Three]]\n"))
        got = self.states()
        self.assertEqual((got["one"], got["three"], got["two"]), ("changed", "changed", "new"))
        rv.marked("one", "reviewed")
        self.assertEqual(self.states()["one"], "ok")

    def test_a_new_number_alone_changes_nothing(self):
        rv.marked("three", "reviewed")
        self.write(lib.MOC, MOC.replace("### Direct", "### First\n\n- [[two|Two]]\n\n### Direct").replace(
            "- [[two|Two]]\n\n### Other", "\n### Other"))
        self.assertEqual(self.states()["three"], "ok")

    def test_not_reviewed_unmarks_it(self):
        rv.marked("two", "reviewed")
        self.assertEqual(rv.marked("two", "not-reviewed"), (True, "Word 1.1.2, Two, is marked not reviewed."))
        self.assertEqual(self.states()["two"], "new")

    def test_a_refusal_says_why_and_keeps_nothing(self):
        self.assertEqual(rv.marked("nine", "reviewed"), (False, "The library holds no word or graph nine."))
        self.assertEqual(rv.marked("one", "done"), (False, "'done' is refused. Say reviewed or not-reviewed."))
        self.assertEqual(rv.load(), {})

    def test_the_page_draws_each_mark_its_counts_and_its_button(self):
        rv.marked("one", "reviewed")
        self.write("one.md", "# one\n\n## What it is\n\nThe one, grown.\n")
        rv.marked("two", "reviewed")
        drawn = lib.drawn()
        self.assertIn('id="marks"', drawn)
        self.assertIn('data-w="one"><span class="mk mk-changed"', drawn)
        self.assertIn('data-w="two"><span class="mk mk-ok"', drawn)
        self.assertIn('data-w="three"><span class="mk mk-new"', drawn)
        self.assertIn('<span class="count plain">3</span><span class="count rv"><b class="c-changed">1 changed</b>'
                      ' · <b class="c-new">1 new</b></span>', drawn)
        one = drawn.split('id="p-one"')[1].split("</article>")[0]
        self.assertIn("Changed since you reviewed it, ", one)
        self.assertIn('data-item="one" data-to="reviewed">Mark reviewed</button>', one)
        two = drawn.split('id="p-two"')[1].split("</article>")[0]
        self.assertIn('data-item="two" data-to="not-reviewed">Mark not reviewed</button>', two)
        flow = drawn.split('id="g-flow"')[1].split("</article>")[0]
        self.assertIn('<h1>It flows.</h1><div class="rv-line rv-new">', flow)

    def test_the_page_takes_a_press_and_refuses_in_one_sentence(self):
        self.assertEqual(lib.take({"item": ["two"], "to": ["reviewed"]}), "")
        self.assertEqual(self.states()["two"], "ok")
        self.assertEqual(lib.take({"item": ["nine"], "to": ["reviewed"]}), "The library holds no word or graph nine.")


if __name__ == "__main__":
    unittest.main()
