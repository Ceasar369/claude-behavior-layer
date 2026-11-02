#!/usr/bin/env python3
"""Check the transcript page's hand-offs: Copy file, and Send's receiver."""

import importlib.util
import os
import re
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("transcript_page_test", os.path.join(HERE, "transcript-page.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

SAID = ("Action: stop this session. Type `/9-session-stop` in session 05.\n\n"
        "Send to session 05.\n\n▼▼▼ START COPY ▼▼▼\n\nHello\n\n▲▲▲ END COPY ▲▲▲\n\n"
        "Then type `/9-session-stop` in session 12.")


def sends(html: str) -> list:
    return re.findall(r"(Send(?: to \d\d)?)</button>", html)


class CopyFileTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        p = patch.object(tool.registry, "ROOT", self.root.name)
        p.start()
        self.addCleanup(p.stop)
        os.makedirs(os.path.join(self.root.name, "code"))
        for name in ("code/.env", "code/.env.example", "code/notes.md"):
            with open(os.path.join(self.root.name, name), "w") as f:
                f.write("words")

    def test_a_env_file_is_refused(self):
        for name in ("code/.env", "code/.env.example"):
            self.assertIsNone(tool.filed(name))
            self.assertNotIn("Copy file", tool.handoff("file", "", name))

    def test_a_link_to_a_env_file_is_refused(self):
        os.symlink(os.path.join(self.root.name, "code/.env"), os.path.join(self.root.name, "code/plain.txt"))
        self.assertIsNone(tool.filed("code/plain.txt"))

    def test_a_plain_file_still_copies(self):
        self.assertEqual(tool.filed("code/notes.md"), "words")
        self.assertIn("Copy file", tool.handoff("file", "", "code/notes.md"))


class SendTest(unittest.TestCase):
    def test_its_own_page_reads_send(self):
        self.assertEqual(sends(tool.reply(SAID, "05")), ["Send", "Send", "Send to 12"])
        self.assertEqual(sends("".join(tool.stretch([{"k": "text", "t": SAID}], "05"))),
                         ["Send", "Send", "Send to 12"])

    def test_another_page_names_the_receiver(self):
        self.assertEqual(sends(tool.reply(SAID, "12")), ["Send to 05", "Send to 05", "Send"])

    def test_the_key_never_changes_with_the_page(self):
        keys = lambda own: re.findall(r'data-hand="(\w+)"', tool.reply(SAID, own))
        self.assertEqual(keys("05"), keys("12"))


if __name__ == "__main__":
    unittest.main()
