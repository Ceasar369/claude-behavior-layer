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


class FinishListTest(unittest.TestCase):
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
        with open(os.path.join(self.seat, "stages.json"), "w") as f:
            json.dump({"kind": "open", "stages": [{"name": "A", "missions": [{"id": "A1", "name": "fix"}]}]}, f)
        with open(os.path.join(self.seat, "drive.json"), "w") as f:
            json.dump({"drive": "plan", "state": "running", "taken": time.strftime(STAMP), "closed": {}}, f)

    def run_tool(self, verb, *keys, words=""):
        out = io.StringIO()
        with patch.object(sys, "argv", ["drive.py", verb, "90", *keys]), \
                patch.object(sys, "stdin", io.StringIO(words)), patch.object(sys, "stdout", out):
            tool.main()
        return out.getvalue()

    def holds(self):
        return tool.holds("90", drive.read("90"))

    def test_no_list_holds_nothing(self):
        self.assertEqual(self.holds(), [])

    def test_a_red_line_holds_a_drive_of_the_plan(self):
        self.run_tool("finish", words="A member signs up on band 00.\nImplemented and verified.\n")
        self.assertEqual(self.holds(), ["Finish line 1 is red: A member signs up on band 00.",
                                        "Finish line 2 is red: Implemented and verified."])

    def test_a_red_line_never_holds_a_drive_of_one_mission(self):
        self.run_tool("finish", words="Implemented and verified.")
        with open(os.path.join(self.seat, "drive.json"), "w") as f:
            json.dump({"drive": "A1", "state": "running", "taken": time.strftime(STAMP), "closed": {}}, f)
        self.assertEqual(self.holds(), [])

    def test_green_and_out_release_the_end_and_the_count_leaves_out_uncounted(self):
        self.run_tool("finish", words="One.\nTwo.\nThree.")
        self.run_tool("green", "1", words="Its screenshot.")
        said = self.run_tool("out", "2", words="Not needed, I said so.")
        self.assertIn("1 · green · One. · Its screenshot.", said)
        self.assertIn("2 · out · Two. · Not needed, I said so.", said)
        self.assertIn("Finish list: 1 of 2 green.", said)
        self.assertEqual(self.holds(), ["Finish line 3 is red: Three."])
        self.run_tool("green", "3", words="Its test output.")
        self.assertEqual(self.holds(), [])

    def test_green_refuses_a_line_that_is_not_there_or_no_proof(self):
        self.run_tool("finish", words="One.")
        with self.assertRaises(SystemExit):
            self.run_tool("green", "2", words="Proof.")
        with self.assertRaises(SystemExit):
            self.run_tool("green", "1")


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
        self.assertIn("1 closed", tool.assistant.drawn("90"))

    def test_a_take_after_an_undriven_close_keeps_it(self):
        self.plan()
        drive.close("90", "A", "A1 never launched.")
        self.assertIn("A", drive.take("90", ["plan"])["closed"])


class PausePointTest(unittest.TestCase):
    """A plan run in order on stand-ins: A1 and A2 in stage A, B1 in stage B,
    a pause point after A1 and after stage A. Each mission stops when the
    test says, never through a session."""

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.seat = os.path.join(self.work.name, "90")
        os.makedirs(self.seat)
        self.gone = set()
        for p in (patch.object(registry, "WORK", self.work.name), patch.object(registry, "entries", return_value={}),
                  patch.object(registry, "claude_records", return_value={}),
                  patch.object(panes, "ids", return_value=set()),
                  patch.object(tool, "stages", self.stages)):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.work.cleanup)
        self.put("stages.json", {"stages": [
            {"name": "A", "missions": [{"id": "A1", "name": "one", "session": "91"},
                                       {"id": "A2", "name": "two", "session": "92"}]},
            {"name": "B", "missions": [{"id": "B1", "name": "three"}]}]})
        self.put("drive.json", {"drive": "plan", "state": "running", "taken": time.strftime(STAMP), "closed": {}})

    def stages(self, nn):
        with open(os.path.join(self.seat, "stages.json")) as f:
            got = json.load(f)["stages"]
        return [(chr(65 + i), [(m, m["id"] in self.gone) for m in s["missions"]]) for i, s in enumerate(got)]

    def put(self, name, got):
        with open(os.path.join(self.seat, name), "w") as f:
            json.dump(got, f)

    def kept(self, mid, number):
        os.makedirs(os.path.join(self.seat, "reports", mid), exist_ok=True)
        open(os.path.join(self.seat, "reports", mid, f"transcript-{number}.md"), "w").close()

    def run_tool(self, verb, *keys, words=""):
        """What the verb printed. Its exit code lands in self.code: 0 when it
        returned, PAUSED once it reached a pause point."""
        out, self.code = io.StringIO(), 0
        with patch.object(sys, "argv", ["drive.py", verb, "90", *keys]), \
                patch.object(sys, "stdin", io.StringIO(words)), patch.object(sys, "stdout", out):
            try:
                tool.main()
            except SystemExit as e:
                if not isinstance(e.code, int):
                    raise
                self.code = e.code
        return out.getvalue()

    def test_a_drive_pauses_at_each_point_and_resumes_exactly_there(self):
        self.assertIn("Pause points: after stage A, after A1.", self.run_tool("point", "A", "A1"))
        said = self.run_tool("show")
        self.assertNotIn("Pause point reached", said)
        self.assertEqual(self.code, 0)
        # A1's work is kept: the drive pauses there, and launches nothing.
        self.kept("A1", "91")
        said = self.run_tool("show")
        self.assertEqual(self.code, drive.PAUSED)
        self.assertIn("Pause point reached: after A1. Nothing new launches.", said)
        self.assertIn("Finished: A1. Look at", said)
        self.assertIn('Next: nothing launches or stops until "Resume the drive."', said)
        self.assertEqual(drive.read("90")["state"], "paused")
        self.assertNotIn("kick off", self.run_tool("show"))
        self.assertEqual(self.code, 0)
        # Resumed, it goes on from there: A1 stopped, A2 still runs, and A1 never pauses it again.
        self.gone.add("A1")
        said = self.run_tool("resume")
        self.assertNotIn("Pause point reached", said)
        self.assertEqual(self.code, 0)
        self.assertIn("Stage A runs", said)
        self.assertIn("then wait on 92.", said)
        # Stage A stops and closes: the drive pauses before stage B.
        self.gone |= {"A1", "A2"}
        self.kept("A2", "92")
        said = self.run_tool("close", "A", words="A1 and A2 wrote their files.")
        self.assertEqual(self.code, drive.PAUSED)
        self.assertIn("Pause point reached: after stage A. Nothing new launches.", said)
        self.assertIn("Finished: A1, A2.", said)
        self.assertNotIn("kick off stage B", said)
        said = self.run_tool("resume")
        self.assertIn("Next: kick off stage B.", said)
        self.assertEqual(drive.read("90")["passed"], ["A1", "A"])

    def test_a_point_on_a_kept_mission_pauses_at_its_keep(self):
        self.run_tool("point", "A1")
        os.makedirs(registry.folder("91"))
        with patch.object(drive, "keep", lambda nn, k, n: self.kept(k, n) or []):
            said = self.run_tool("keep", "A1")
        self.assertEqual(self.code, drive.PAUSED)
        self.assertIn("Pause point reached: after A1.", said)
        self.assertIn('Next: stop 91-A1, as its finish asks.', said)
        self.assertEqual(drive.read("90")["state"], "paused")

    def test_a_mission_point_holds_in_a_drive_of_its_stage(self):
        self.run_tool("point", "A1")
        self.put("drive.json", {"drive": "A", "state": "running", "taken": time.strftime(STAMP), "closed": {}})
        self.kept("A1", "91")
        self.assertIn("Pause point reached: after A1.", self.run_tool("show"))
        self.assertEqual(drive.read("90")["state"], "paused")

    def test_a_point_names_only_what_the_plan_holds(self):
        with self.assertRaises(SystemExit) as refused:
            self.run_tool("point", "C9")
        self.assertNotEqual(refused.exception.code, drive.PAUSED)


if __name__ == "__main__":
    unittest.main()
