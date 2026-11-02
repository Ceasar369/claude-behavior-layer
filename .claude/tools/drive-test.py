#!/usr/bin/env python3
"""Check an open plan's drive on a plan in a folder of its own, never a real seat."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import drive  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402

spec = importlib.util.spec_from_file_location("drive_tool_test", os.path.join(HERE, "drive.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

STAMP = "%Y-%m-%dT%H:%M:%S"


class OpenPlanTest(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.seat = os.path.join(self.work.name, "90")
        os.makedirs(self.seat)
        for p in (patch.object(registry, "WORK", self.work.name), patch.object(registry, "entries", return_value={}),
                  patch.object(registry, "claude_records", return_value={}),
                  patch.object(panes, "ids", return_value=set())):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.work.cleanup)

    def plan(self, queued=None):
        mission = {"id": "A1", "name": "layer fix", **({"queued": queued} if queued else {})}
        self.put("stages.json", {"kind": "open", "stages": [{"name": "Fixes", "missions": [mission]},
                                                            {"name": "More", "missions": [{"id": "B1", "name": "more"}]}]})

    def put(self, name, got):
        with open(os.path.join(self.seat, name), "w") as f:
            json.dump(got, f)

    def stands(self):
        self.put("drive.json", {"drive": "plan", "state": "running", "taken": time.strftime(STAMP), "closed": {}})
        return tool.stands("90", drive.read("90"))

    def test_a_mission_queued_seconds_ago_is_never_next(self):
        self.plan(time.strftime(STAMP))
        said = self.stands()
        self.assertNotIn("Next: launch A1 while a seat is free.", said)
        self.assertIn("Next: wait for A1 to claim a number.", said)

    def test_a_row_booting_on_the_launch_page_is_never_next(self):
        self.plan(time.strftime(STAMP, time.localtime(time.time() - 600)))
        self.put("launch.json", {"rows": [{"uid": 1, "n": "91", "name": "layer fix", "status": "booting"}]})
        self.assertIn("Next: wait for A1 to claim a number.", self.stands())

    def test_a_mission_queued_long_ago_with_no_launch_is_next(self):
        self.plan(time.strftime(STAMP, time.localtime(time.time() - 600)))
        self.assertIn("Next: launch A1 while a seat is free.", self.stands())

    def test_an_undriven_open_plan_closes_a_stage_that_folds(self):
        self.plan()
        with patch.object(sys, "argv", ["drive.py", "close", "90", "A"]), \
                patch.object(sys, "stdin", io.StringIO("A1 never launched.")), \
                patch("builtins.print"):
            tool.main()
        self.assertIn("A", drive.read("90")["closed"])
        self.assertFalse(drive.driving(drive.read("90")))
        self.assertIn("1 closed", tool.assistant.render("90"))

    def test_a_take_after_an_undriven_close_keeps_it(self):
        self.plan()
        drive.close("90", "A", "A1 never launched.")
        self.assertIn("A", drive.take("90", ["plan"])["closed"])


if __name__ == "__main__":
    unittest.main()
