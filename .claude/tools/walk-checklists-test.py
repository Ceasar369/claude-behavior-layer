#!/usr/bin/env python3
"""Check walk-checklists.py on a section of its own, in a walks/ of its own, never the real one."""

import importlib.util
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("walk_checklists_test", os.path.join(HERE, "walk-checklists.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

ANGLES = ("**Angles** · Empty: 1a · Wrong shape: 1a · Limits: 1b · Twice: none, one press sends once"
          " · Cut short: 1b · Someone else: none, nobody is signed in · Time: Not designed")

CHECKLIST = """# Sign · checklist

Up: [[app/sign/sign-MOC|Sign]]

Every sign check, your mark and the tester's: ✅ passed, ⬜ not passed yet, — not yours.

## [[app/sign/sign-up|Sign up]]

| # | Check | What it checks | You | Tester |
|---|---|---|:-:|:-:|
| 1 | Sign up 1 | Type the email | ✅ | ✅ |
| 2 | Sign up 1a | A wrong email is refused | — | ✅ |
| 3 | Sign up 1b | A long email is cut | — | ⬜ |
"""


def journey(angles=None):
    """Sign up, its Angles line after its End when given."""
    lines = ["# Sign up", "", "Up: [[app/sign/sign-MOC|Sign]]", "", "Signing up.", "",
             "**Start** · Signed out.", "", "**Prep** · None.", "", "**End** · Signed in.", ""]
    if angles:
        lines += [angles, ""]
    lines += ["### Sign up 1 · Type the email", "", "*Sign up · /signup · nobody*", "",
              "**Do** · Type walk@seed.test.", "", '**See** · "Welcome".', "",
              "> [!note]- Details the tester checks (2)",
              '> - **a · A wrong email is refused** · walk → "Enter an email."',
              '> - **b · A long email is cut** · 300 letters → the field holds 254.', ""]
    return "\n".join(lines)


DOCS_ANGLES = ("**Angles** · Error codes: a · Limits: none, it takes no value · Retry: none, it moves nothing"
               " · Events: none, it writes none · Sandbox and live: none, both read alike · Wrong key: none, its link to Calls")


def docs(covers):
    """One docs step, Docs 1, its italic line ending on `covers`, its Angles line after it."""
    return "\n".join([
        "# Sign · Docs", "", "Up: [[app/sign/sign-MOC|Sign]]", "", "Its pages.", "",
        "**Start** · The docs site.", "", "**Prep** · None.", "", "**End** · Nothing to reset.", "",
        "### Docs 1 · Sign up", "", f"*localhost:3000/sign-up · pages/sign-up.md · {covers}*", "",
        DOCS_ANGLES, "", '**See** · "Sign up".', "",
        "> [!note]- Details the tester checks (1)", "> - **a · Every link lands** · Each link opens its page.", ""])


class WalkChecklistsTest(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        p = patch.object(tool, "WALKS", self.work.name)
        p.start()
        self.addCleanup(p.stop)
        self.section = os.path.join(self.work.name, "app", "sign")
        os.makedirs(self.section)
        self.write("0-checklist.md", CHECKLIST)

    def write(self, name, text):
        path = os.path.join(self.section, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, name="0-checklist.md"):
        with open(os.path.join(self.section, name), encoding="utf-8") as f:
            return f.read()

    def build(self):
        with patch.object(sys, "argv", ["walk-checklists.py", self.section]), patch("builtins.print"):
            tool.main()
        return self.read()

    def test_an_angles_line_shows_under_its_journeys_heading(self):
        self.write("sign-up.md", journey(ANGLES))
        text = self.build()
        self.assertIn(f"## [[app/sign/sign-up|Sign up]]\n\n{ANGLES}\n\n| # | Check |", text)
        self.assertEqual(text.count("**Angles**"), 1)

    def test_a_rebuild_keeps_every_mark(self):
        self.write("sign-up.md", journey(ANGLES))
        text = self.build()
        self.assertIn("| 1 | Sign up 1 | Type the email | ✅ | ✅ |", text)
        self.assertIn("| 2 | Sign up 1a | A wrong email is refused | — | ✅ |", text)
        self.assertIn("| 3 | Sign up 1b | A long email is cut | — | ⬜ |", text)

    def test_a_journey_detail_is_the_testers_alone_and_a_passed_one_stays(self):
        held = self.read("0-checklist.md").replace("| 2 | Sign up 1a | A wrong email is refused | — | ✅ |", "| 2 | Sign up 1a | A wrong email is refused | ✅ | ✅ |")
        self.write("0-checklist.md", held.replace("| 3 | Sign up 1b | A long email is cut | — | ⬜ |", "| 3 | Sign up 1b | A long email is cut | ⬜ | ⬜ |"))
        self.write("sign-up.md", journey(ANGLES))
        text = self.build()
        self.assertIn("| 2 | Sign up 1a | A wrong email is refused | ✅ | ✅ |", text)
        self.assertIn("| 3 | Sign up 1b | A long email is cut | — | ⬜ |", text)

    def test_a_renamed_detail_takes_its_new_title_and_keeps_its_mark(self):
        self.write("sign-up.md", journey(ANGLES).replace("A wrong email is refused", "A bad email is refused"))
        text = self.build()
        self.assertIn("| 2 | Sign up 1a | A bad email is refused | — | ✅ |", text)
        self.assertNotIn("A wrong email is refused", text)

    def test_a_renamed_step_takes_its_new_title_and_keeps_its_marks(self):
        self.write("sign-up.md", journey(ANGLES).replace("Sign up 1 · Type the email", "Sign up 1 · Enter the email"))
        self.assertIn("| 1 | Sign up 1 | Enter the email | ✅ | ✅ |", self.build())

    def test_a_detail_with_no_title_keeps_the_one_its_row_holds(self):
        self.write("sign-up.md", journey(ANGLES).replace("**a · A wrong email is refused**", "**a**"))
        self.assertIn("| 2 | Sign up 1a | A wrong email is refused | — | ✅ |", self.build())

    def test_a_sweep_step_with_no_title_keeps_the_one_its_row_holds(self):
        self.write("sign-up.md", journey(ANGLES))
        self.write("looks/french.md", "# French\n\nUp: [[app/sign/looks/looks-MOC|Looks]]\n\nIts French.\n\n"
                   "### French · Sign up\n\n*Each word in French · Sign up 1*\n\n### French · Login\n\n*Each word · Login*\n")
        self.build()
        self.assertIn("| French · Login | Login | ⬜ | ⬜ |", self.read("looks/looks-checklist.md"))
        held = self.read("looks/looks-checklist.md").replace("| French · Sign up | Sign up | ⬜ | ⬜ |",
                                                             "| French · Sign up | The signup's words | ✅ | ⬜ |")
        self.write("looks/looks-checklist.md", held)
        self.build()
        self.assertIn("| French · Sign up | The signup's words | ✅ | ⬜ |", self.read("looks/looks-checklist.md"))

    def test_a_detail_lettered_past_z_gets_its_own_row(self):
        self.write("sign-up.md", journey(ANGLES) + '> - **aa · A spaced email is trimmed** · " walk@seed.test" → "Welcome".\n')
        text = self.build()
        self.assertIn("| 3 | Sign up 1b | A long email is cut | — | ⬜ |\n| 4 | Sign up 1aa | A spaced email is trimmed | — | ⬜ |", text)

    def test_a_journey_with_no_angles_line_builds_as_before(self):
        self.write("sign-up.md", journey())
        self.assertEqual(self.build(), CHECKLIST)

    def test_a_second_build_changes_nothing(self):
        self.write("sign-up.md", journey(ANGLES))
        first = self.build()
        self.assertEqual(self.build(), first)

    def test_a_rewritten_angles_line_replaces_the_old_one(self):
        self.write("sign-up.md", journey(ANGLES))
        self.build()
        moved = ANGLES.replace("Limits: 1b", "Limits: 1c")
        self.write("sign-up.md", journey(moved))
        text = self.build()
        self.assertIn(moved, text)
        self.assertNotIn(ANGLES, text)
        self.assertEqual(text.count("**Angles**"), 1)

    def test_an_angles_line_after_a_step_is_no_journeys(self):
        self.write("sign-up.md", journey() + "\n" + ANGLES + "\n")
        self.assertNotIn("**Angles**", self.build())

    def test_a_docs_steps_angles_line_follows_its_journeys(self):
        self.write("sign-up.md", journey(ANGLES))
        self.write("docs.md", docs("Sign up 1"))
        text = self.build()
        shown = "**Docs 1 · Angles** · " + DOCS_ANGLES[len("**Angles** · "):]
        self.assertIn(f"## [[app/sign/sign-up|Sign up]]\n\n{ANGLES}\n\n{shown}\n\n| # | Check |", text)
        self.assertIn("| Docs 1a | Every link lands | ⬜ | ⬜ |", text)

    def test_a_docs_step_covering_no_journey_shows_its_line_under_docs(self):
        self.write("sign-up.md", journey(ANGLES))
        self.write("docs.md", docs("Sign up"))
        text = self.build()
        shown = "**Docs 1 · Angles** · " + DOCS_ANGLES[len("**Angles** · "):]
        self.assertIn(f"## [[app/sign/docs|Docs]]\n\n{shown}\n\n| # | Check |", text)
        self.assertEqual(text.count("**Docs 1 · Angles**"), 1)

    def test_the_looks_checklist_holds_no_angles_line(self):
        self.write("sign-up.md", journey(ANGLES))
        self.write("looks/french.md", "# French\n\nUp: [[app/sign/looks/looks-MOC|Looks]]\n\nIts French.\n\n"
                   "### French · Sign up\n\n*Each word in French · Sign up 1*\n\n"
                   "| **Welcome** | Bienvenue |\n")
        self.build()
        self.assertIn("French · Sign up", self.read("looks/looks-checklist.md"))
        self.assertNotIn("**Angles**", self.read("looks/looks-checklist.md"))


if __name__ == "__main__":
    unittest.main()
