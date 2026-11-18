#!/usr/bin/env python3
"""Check library-check.py on pages and a library of its own, never the real one."""

import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("library_check", os.path.join(HERE, "library-check.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def page(line="scrypt is a deliberately slow password scrambler."):
    """A whole page, with the given line under What it is."""
    return (
        "# scrypt\n\nUp: [[library-MOC|Library]]\n\n## What it is\n\n"
        f"{line}\n\n## What it is not\n\nIt is not encryption.\n\n"
        "Source: https://www.rfc-editor.org/rfc/rfc7914\n"
    )


class Faults(unittest.TestCase):
    def test_a_page_true_without_the_code_passes(self):
        self.assertEqual(tool.faults(page()), [])

    def test_words_of_this_project_are_refused(self):
        for line in (
            "We run scrypt.",
            "Our server uses it.",
            "It protects us.",
        ):
            self.assertIn("speaks of this project", tool.faults(page(line))[0], line)

    def test_file_paths_are_refused(self):
        for line in (
            "See code/setup.sh for it.",
            "It sits in password.ts.",
            "Read `.claude/tools/agenda.py`.",
        ):
            self.assertIn("names a file", tool.faults(page(line))[0], line)

    def test_ordinary_words_pass(self):
        for line in (
            "The US standard body published it.",
            "Node.js ships it.",
            "It uses TLS/SSL and/or a certificate.",
            "Read https://www.rfc-editor.org/rfc/rfc7914 for its definition.",
            "A user owes nothing.",
        ):
            self.assertEqual(tool.faults(page(line)), [], line)

    def test_a_page_with_no_source_is_refused(self):
        self.assertTrue(any("Source" in f for f in tool.faults(
            page().replace("Source: https://www.rfc-editor.org/rfc/rfc7914\n", ""))))

    def test_a_missing_part_is_refused(self):
        self.assertTrue(tool.faults("scrypt\n\nUp: [[library-MOC|Library]]\n"))
        self.assertTrue(any("Line 3" in f for f in tool.faults("# scrypt\n\nUp: nothing\n")))
        self.assertTrue(any("What it is not" in f for f in tool.faults(
            "# scrypt\n\nUp: [[library-MOC|Library]]\n\n## What it is\n\nA scrambler.\n")))


class Unlisted(unittest.TestCase):
    def library(self, moc, names):
        folder = tempfile.mkdtemp()
        with open(os.path.join(folder, tool.MOC), "w", encoding="utf-8") as f:
            f.write(moc)
        for name in names:
            with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                f.write(page())
        return folder

    def test_an_empty_library_has_nothing_unlisted(self):
        self.assertEqual(tool.unlisted(self.library("# Library\n", [])), [])

    def test_a_page_the_moc_never_links_is_named(self):
        folder = self.library("# Library\n\n- [[scrypt|scrypt]]\n", ["scrypt.md", "tls.md"])
        self.assertEqual(tool.unlisted(folder), ["tls.md"])


class Misplaced(unittest.TestCase):
    def test_a_word_under_a_subchapter_or_section_passes(self):
        moc = "## Data\n\n### Secrets\n\n- [[tls|TLS]]\n\n#### Hashing\n\n- [[salt|Salt]]\n"
        self.assertEqual(tool.misplaced(moc), [])

    def test_a_word_right_under_a_chapter_is_named(self):
        self.assertEqual(
            tool.misplaced("## Data\n\n- [[tls|TLS]]\n"),
            ["tls: it sits above a subchapter."],
        )

    def test_a_word_linked_twice_is_named(self):
        self.assertEqual(
            tool.misplaced("## Data\n\n### A\n\n- [[tls|TLS]]\n\n### B\n\n- [[tls|TLS]]\n"),
            ["tls: the MOC links it twice."],
        )


def graph(box="1. A sender drops off a parcel [[hub]]"):
    """A whole graph, with the given box."""
    return (
        "# How a Parcel arrives\n\nUp: [[library-MOC|Library]]\n\n## The text\n\nA Parcel is sorted first.\n\n"
        f"## The graph\n\n{box}\n\nSource: https://example.com/parcels.pdf\n"
    )


class Graphs(unittest.TestCase):
    def test_a_whole_graph_passes(self):
        self.assertEqual(tool.graph_faults(graph(), {"hub"}), [])

    def test_a_box_linking_an_unlisted_word_is_named(self):
        self.assertIn("lists nowhere: hub", tool.graph_faults(graph(), set())[0])

    def test_a_graph_with_no_box_or_part_is_refused(self):
        self.assertTrue(any("no box" in f for f in tool.graph_faults(graph("Just words."), set())))
        self.assertTrue(any("## The text" in f for f in tool.graph_faults(graph().replace("## The text", ""), {"hub"})))

    def test_a_graph_speaking_of_this_project_is_refused(self):
        self.assertIn("speaks of this project", tool.graph_faults(graph("1. We sort it [[hub]]"), {"hub"})[0])

    def test_a_graph_sits_once_and_only_under_a_subchapter(self):
        self.assertEqual(tool.misplaced("## A\n\n### B\n\n- Graph: [[g|G]]\n- [[hub|Hub]]\n"), [])
        self.assertEqual(tool.misplaced("## A\n\n- Graph: [[g|G]]\n"), ["g: a graph sits only under a subchapter."])
        self.assertEqual(tool.misplaced("## A\n\n### B\n\n- Graph: [[g|G]]\n\n### C\n\n- Graph: [[g|G]]\n"),
                         ["g: the MOC lists it twice."])

    def test_two_to_four_lanes_pass_and_others_are_refused(self):
        two = "### Truck\n\n1. The depot sorts [[hub]]\n\n### Bike\n\n1. The courier rides"
        self.assertEqual(tool.graph_faults(graph(two), {"hub"}), [])
        one = tool.graph_faults(graph("### Truck\n\n1. The depot sorts [[hub]]"), {"hub"})
        self.assertTrue(any("1 lanes" in f for f in one))
        five = "\n\n".join(f"### L{i}\n\n1. A box" for i in range(5))
        self.assertTrue(any("5 lanes" in f for f in tool.graph_faults(graph(five), set())))
        empty = tool.graph_faults(graph("### A\n\n### B\n\n1. A box"), set())
        self.assertIn("The lane A has no box.", empty)
        loose = tool.graph_faults(graph("1. A box\n\n### A\n\n1. A box\n\n### B\n\n1. A box"), set())
        self.assertTrue(any("outside every lane" in f for f in loose))

    def test_a_series_reads_its_name_then_its_place(self):
        good = graph().replace("## The text\n\n", "## The text\n\nSeries: A login, in order, 1 of 3\n\n")
        self.assertEqual(tool.graph_faults(good, {"hub"}), [])
        bad = graph().replace("## The text\n\n", "## The text\n\nSeries: A login\n\n")
        self.assertTrue(any("series not written" in f for f in tool.graph_faults(bad, {"hub"})))

    def test_a_source_that_is_no_address_is_refused(self):
        bad = graph() + "Source: a search summary\n"
        self.assertTrue(any("no address" in f for f in tool.graph_faults(bad, {"hub"})))

    def test_a_word_two_graphs_link_passes(self):
        moc = "## A\n\n### B\n\n- Graph: [[g|G]]\n- Graph: [[h|H]]\n- [[hub|Hub]]\n"
        self.assertEqual(tool.misplaced(moc), [])
        self.assertEqual(tool.graph_faults(graph(), tool.words(moc)), [])

    def test_a_graph_file_unlisted_or_a_listed_graph_missing_is_named(self):
        folder = tempfile.mkdtemp()
        os.mkdir(os.path.join(folder, tool.GRAPHS))
        with open(os.path.join(folder, tool.GRAPHS, "loose.md"), "w", encoding="utf-8") as f:
            f.write(graph())
        self.assertEqual(tool.homeless(folder, "### B\n\n- Graph: [[gone|Gone]]\n"), [
            "graphs/loose.md: the MOC lists it nowhere.",
            "gone: the MOC lists this graph, but graphs/gone.md is missing.",
        ])


if __name__ == "__main__":
    unittest.main()
