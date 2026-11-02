#!/usr/bin/env python3
"""Check walk-clear.py on a walker and a lead in a folder of their own, never a real seat."""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import registry  # noqa: E402

spec = importlib.util.spec_from_file_location("walk_clear_test", os.path.join(HERE, "walk-clear.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class WalkClearTest(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        p = patch.object(registry, "WORK", self.work.name)
        p.start()
        self.addCleanup(p.stop)
        os.makedirs(os.path.join(self.work.name, "90"))
        os.makedirs(os.path.join(self.work.name, "91", "playwright"))
        self.start(1761767880)

    def start(self, at):
        """A walker in seat 91 gets ready: it writes walk.json, once, at `at`."""
        card = os.path.join(self.work.name, "91", "walk.json")
        with open(card, "w") as f:
            json.dump({"main": "90", "area": "web-app"}, f)
        os.utime(card, (at, at))

    def run_tool(self, what):
        with patch.object(sys, "argv", ["walk-clear.py", "91", what]), patch("builtins.print"):
            tool.main()

    def walk(self, journey, *checks, mark=""):
        self.run_tool(journey)
        folder = os.path.join(self.work.name, "91", "walk", journey)
        os.makedirs(folder, exist_ok=True)
        for c in checks:
            with open(os.path.join(folder, f"{c}.png"), "w") as f:
                f.write(mark or journey)

    def files(self, *at):
        root = os.path.join(self.work.name, *at)
        return sorted(os.path.relpath(os.path.join(b, n), root) for b, _, ns in os.walk(root) for n in ns)

    def kept(self):
        return os.listdir(os.path.join(self.work.name, "90", "walkers"))

    def test_a_whole_second_pass_starts_with_no_file_from_the_first(self):
        self.walk("web-app/proposals/member", 7, 8, 9)
        self.walk("web-app/proposals/member")
        self.assertEqual(self.files("91", "walk"), [])

    def test_a_walk_of_two_journeys_keeps_both_at_its_end(self):
        self.walk("web-app/proposals/member", 7, 8)
        self.walk("web-app/proposals/live", 1)
        self.run_tool("keep")
        [to] = self.kept()
        self.assertEqual(self.files("90", "walkers", to, "walk"),
                         ["web-app/proposals/live/1.png", "web-app/proposals/member/7.png",
                          "web-app/proposals/member/8.png"])

    def test_two_areas_keep_one_journey_name_apart(self):
        self.walk("web-app/proposals/member", 7)
        self.walk("app/training/member", 7)
        self.run_tool("keep")
        [to] = self.kept()
        self.assertEqual(self.files("90", "walkers", to, "walk"),
                         ["app/training/member/7.png", "web-app/proposals/member/7.png"])

    def test_a_journey_kept_again_holds_its_last_pass_alone(self):
        self.walk("web-app/proposals/proposal", 20, "20-2", "20-3")
        self.walk("web-app/proposals/proposal", 20, "20-2", mark="again")
        self.run_tool("keep")
        [to] = self.kept()
        folder = os.path.join(self.work.name, "90", "walkers", to, "walk", "web-app", "proposals", "proposal")
        self.assertEqual(sorted(os.listdir(folder)), ["20-2.png", "20.png"])
        with open(os.path.join(folder, "20.png")) as f:
            self.assertEqual(f.read(), "again")

    def test_a_new_walker_in_the_seat_keeps_apart(self):
        self.walk("web-app/proposals/member", 7)
        self.run_tool("keep")
        # The walker is stopped; a new one claims the seat, its folder fresh.
        shutil.rmtree(os.path.join(self.work.name, "91", "walk"))
        self.start(1761771480)
        self.walk("web-app/proposals/live", 1)
        self.run_tool("keep")
        first, second = sorted(self.kept())
        self.assertRegex(first, r"^91-\d\d-\d\d-\d{4}$")
        self.assertEqual(self.files("90", "walkers", first, "walk"), ["web-app/proposals/member/7.png"])
        self.assertEqual(self.files("90", "walkers", second, "walk"), ["web-app/proposals/live/1.png"])

    def test_a_lead_gone_gets_no_folder(self):
        os.rmdir(os.path.join(self.work.name, "90"))
        self.walk("web-app/proposals/member", 7)
        self.walk("web-app/proposals/live")
        self.assertFalse(os.path.exists(os.path.join(self.work.name, "90")))
        self.assertEqual(self.files("91", "walk"), [])

    def test_a_journey_without_its_area_is_refused(self):
        with self.assertRaises(SystemExit):
            self.run_tool("proposals/member")


if __name__ == "__main__":
    unittest.main()
