#!/usr/bin/env python3
"""Check launch plans without opening or moving real sessions."""

import importlib.util
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch-page.py")
spec = importlib.util.spec_from_file_location("launch_page_test", path)
page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page)
schedule_spec = importlib.util.spec_from_file_location("schedule_test", os.path.join(os.path.dirname(path), "schedule.py"))
schedule = importlib.util.module_from_spec(schedule_spec)
schedule_spec.loader.exec_module(schedule)

ROWS = [{"uid": 1, "n": "02", "win": "L:w", "tab": "L:t", "status": "booting"}]
TREE = [{"window": "w", "tabs": [{"tab": "t", "root": {"pane": "live"}}]}]
MOVE = {"win": "L:w", "tab": "L:t", "source": "p:live", "anchor": "r:1", "side": "right"}
SHAPE = {"win": "L:w", "tab": "L:t", "root": {"split": "columns", "children": [
    {"ref": "r:1"}, {"ref": "p:live"}]}}
OPENED = [{"window": "w", "tabs": [{"tab": "t", "root": {"split": "columns", "children": [
    {"pane": "new"}, {"pane": "live"}]}}]}]


class PlanTest(unittest.TestCase):
    def test_scheduled_fire_never_applies_planned_moves(self):
        lp = SimpleNamespace(moves=lambda _nn: [MOVE])
        with patch.object(schedule, "unschedule"), patch.object(schedule, "press") as press:
            lines, success = schedule.fire("01", lp)
            self.assertFalse(success)
            self.assertIn("your press of Launch", lines[0])
            press.assert_not_called()

    def test_planning_saves_without_moving_sessions(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "launch.json")
            rows = [{k: v for k, v in ROWS[0].items() if k != "status"}]
            with patch.object(page, "path", return_value=target), patch.object(page, "placed"), \
                    patch.object(page.iterm, "apply_layout") as apply:
                page.take_for("01", [""])({"act": ["save"], "rows": [json.dumps(rows)],
                    "seen": ["[1]"], "moves": [json.dumps([MOVE])], "layouts": [json.dumps([SHAPE])]})
                self.assertEqual(page.moves("01"), [MOVE])
                self.assertEqual(page.layouts("01"), [SHAPE])
                apply.assert_not_called()

    def test_missing_or_moved_panes_refuse_launch(self):
        self.assertEqual(page.move_problems([MOVE], ROWS, TREE), [])
        self.assertTrue(page.move_problems([dict(MOVE, source="p:gone")], ROWS, TREE))
        self.assertTrue(page.move_problems([dict(MOVE, anchor="r:2")], ROWS, TREE))
        self.assertEqual(page.shape_problems([MOVE], [SHAPE], ROWS, TREE), [])
        self.assertTrue(page.shape_problems([MOVE], [], ROWS, TREE))

    def test_changed_layout_stops_before_opening_panes(self):
        with patch.object(page, "load", return_value=ROWS), patch.object(page, "moves", return_value=[MOVE]), \
                patch.object(page, "layouts", return_value=[SHAPE]), patch.object(page.iterm, "tree", return_value=[]), \
                patch.object(page, "launcher", return_value=""), patch.object(page.launch, "place") as place, \
                patch.object(page, "mark") as mark, patch.object(page.registry, "release"):
            page.go("00")
            place.assert_not_called()
            self.assertEqual(mark.call_args.args[2], "failed: arrangement changed before launch.")

    def run_plan(self, succeeds):
        events = []
        def place(*_):
            events.append("open")
            return "new"
        def arrange(spec):
            events.append(("arrange", spec))
            return succeeds
        def close(pane):
            events.append(("close", pane))
            return True
        def mark(_nn, _uid, status):
            events.append(("status", status))
        def start(*_):
            events.append("start")
        with patch.object(page, "load", return_value=ROWS), patch.object(page, "moves", return_value=[MOVE]), \
                patch.object(page, "layouts", return_value=[SHAPE]), patch.object(page.iterm, "tree", side_effect=[TREE, OPENED, OPENED]), \
                patch.object(page, "launcher", return_value=""), patch.object(page.launch, "place", side_effect=place), \
                patch.object(page.iterm, "apply_layout", side_effect=arrange), patch.object(page.iterm, "close", side_effect=close), \
                patch.object(page.registry, "release"), patch.object(page, "save"), \
                patch.object(page, "mark", side_effect=mark), patch.object(page.launch, "start", side_effect=start), \
                patch.object(page, "follow"):
            page.go("00")
        return events

    def test_move_runs_after_opening_before_starting(self):
        events = self.run_plan(True)
        spec = {"tabs": [{"tab_id": "t", "root": {"vertical": True, "children": [
            {"session_id": "new"}, {"session_id": "live"}]}}]}
        self.assertEqual(events[:3], ["open", ("arrange", spec), "start"])

    def test_failed_move_closes_only_new_unstarted_panes(self):
        events = self.run_plan(False)
        self.assertEqual(events[0], "open")
        self.assertEqual(events[1][0], "arrange")
        self.assertEqual(events[2], ("close", "new"))
        self.assertNotIn("start", events)
        self.assertTrue(events[3][1].startswith("failed: arrangement"))


if __name__ == "__main__":
    unittest.main()
