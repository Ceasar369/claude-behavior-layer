#!/usr/bin/env python3
"""Check the plan of teams on a folder of its own, never a real seat."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import registry  # noqa: E402

spec = importlib.util.spec_from_file_location("teams_tool_test", os.path.join(HERE, "teams.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class TeamsTest(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.work.name, "01"))
        p = patch.object(registry, "WORK", self.work.name)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.work.cleanup)

    def run_tool(self, *argv, stdin=""):
        out = io.StringIO()
        with patch.object(sys, "argv", ["teams.py", *argv]), patch.object(sys, "stdin", io.StringIO(stdin)), \
                patch.object(sys, "stdout", out):
            tool.main()
        return out.getvalue()

    def saved(self):
        with open(os.path.join(self.work.name, "01", "teams.json")) as f:
            return json.load(f)

    def test_a_team_launches_once_every_line_is_green(self):
        self.run_tool("team", "01", "40", "backend team")
        self.run_tool("team", "01", "50", "screens team")
        said = self.run_tool("wait", "01", "50", stdin="The trunk stands on band 00.\nThe backend's tests pass.\n")
        self.assertIn("Team 40, backend team: waits on nothing.", said)
        self.assertIn("Team 50, screens team: launch list 0 of 2 green.", said)
        self.run_tool("green", "01", "50", "1", stdin="A project starts and ends on band 00.")
        said = self.run_tool("out", "01", "50", "2", stdin="Not needed.")
        self.assertIn("Team 50, screens team: every line green: its row goes on the launch page.", said)
        lines = self.saved()["teams"][1]["launch"]
        self.assertEqual([l["state"] for l in lines], ["green", "out"])
        self.assertEqual(lines[0]["said"], "A project starts and ends on band 00.")

    def test_a_shared_place_names_its_owner(self):
        self.run_tool("team", "01", "40", "backend team")
        said = self.run_tool("share", "01", "40", "the launch page")
        self.assertIn("Shared: the launch page, owned by team 40.", said)

    def test_waits_choices_and_drive(self):
        for seat, name in (("40", "backend team"), ("50", "screens team"), ("60", "pages team")):
            self.run_tool("team", "01", seat, name)
        self.run_tool("after", "01", "50", "40", "60")
        self.run_tool("set", "01", "50", "account=2", "model=opus", "effort=high", "self=on")
        self.run_tool("set", "01", "50", "self=")
        said = self.run_tool("drive", "01", "50", "plan", stdin="Its plan holds no thinking left.")
        self.assertIn("  Waits on teams 40, 60.", said)
        self.assertIn("  Launches with account 2, model opus, effort high.", said)
        self.assertIn("  Drive: plan. Its plan holds no thinking left.", said)
        t = self.saved()["teams"][1]
        self.assertEqual((t["waits"], t["account"], "self" in t, t["drive"]), (["40", "60"], "2", False, "plan"))

    def test_a_pause_point_before_a_team(self):
        self.run_tool("team", "01", "50", "screens team")
        self.assertIn("  A pause point before its launch.", self.run_tool("pause", "01", "50"))
        self.assertTrue(self.saved()["teams"][0]["pause"])

    def test_refusals(self):
        self.run_tool("team", "01", "40", "backend team")
        for argv, stdin in ((("team", "01", "40", "again"), ""), (("wait", "01", "60"), "x"),
                            (("green", "01", "40", "1"), "proof"), (("wait", "01", "40"), ""),
                            (("after", "01", "40", "40"), ""), (("after", "01", "40", "70"), ""),
                            (("set", "01", "40", "colour=red"), ""), (("drive", "01", "40", "fast"), "why"),
                            (("drive", "01", "40", "plan"), "")):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                self.run_tool(*argv, stdin=stdin)

    def test_show_with_no_plan(self):
        self.assertIn("No plan of teams yet.", self.run_tool("show", "01"))


if __name__ == "__main__":
    unittest.main()
