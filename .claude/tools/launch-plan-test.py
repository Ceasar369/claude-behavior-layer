#!/usr/bin/env python3
"""Check launch plans without opening or moving real sessions."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
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
# No test touches a real page's file or launch log. This folder holds neither.
NOWHERE = os.path.join(tempfile.mkdtemp(), "none")
page.path = page.launch.path = lambda nn: os.path.join(NOWHERE, nn, "launch.json")
# Nor holds a real page's launch lock.
page.launch.held_at = lambda nn: os.path.join(NOWHERE, "launches", f"{nn}.lock")
# Nor takes a turn from my real account order.
page.accounts.take = lambda: page.accounts.FALLBACK

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

    def test_a_fire_exits_launched_only_once_every_row_launched(self):
        for every, code in ((True, schedule.drive.LAUNCHED), (False, 1)):
            with patch.object(sys, "argv", ["schedule.py", "fire", "01"]), patch("builtins.print"), \
                    patch.object(schedule.signal, "signal"), patch.object(schedule.page, "tool"), \
                    patch.object(schedule, "fire", return_value=(["01-one launched"], every)):
                with self.assertRaises(SystemExit) as ended:
                    schedule.main()
            self.assertEqual(ended.exception.code, code)

    def test_planning_saves_without_moving_sessions(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "launch.json")
            rows = [{k: v for k, v in ROWS[0].items() if k != "status"}]
            with patch.object(page.launch, "path", return_value=target), patch.object(page, "placed"), \
                    patch.object(page.iterm, "apply_layout") as apply:
                said = page.take_for("01", [""])({"act": ["save"], "rows": [json.dumps(rows)],
                    "seen": ["[1]"], "moves": [json.dumps([MOVE])], "layouts": [json.dumps([SHAPE])]})
                self.assertEqual(said, "")
                self.assertEqual(page.moves("01"), [MOVE])
                self.assertEqual(page.layouts("01"), [SHAPE])
                apply.assert_not_called()

    def test_a_press_that_saves_nothing_answers_its_refusal(self):
        with patch.object(page, "save") as save, patch.object(page, "load", return_value=ROWS):
            self.assertEqual(page.take_for("01", [""])({"act": ["save"], "rows": ["[]"]}),
                             "A launch is booting on this page, so nothing was saved.")
            self.assertEqual(page.take_for("01", [""])({"act": ["save"], "rows": ["{not json"]}),
                             "The page's rows could not be read, so nothing was saved.")
            save.assert_not_called()

    def test_a_refused_launch_answers_the_banner_words(self):
        banner = [""]
        with patch.object(page, "save"), patch.object(page, "load", return_value=[]), \
                patch.object(page, "placed"), patch.object(page, "scheduled", return_value=""), \
                patch.object(page.launch, "problems", return_value=["Row 1 has no number."]), \
                patch.dict(page.KEPT, {"01": (TREE, "", [])}), patch.object(page.launch, "begin") as thread:
            said = page.take_for("01", banner)({"act": ["launch"], "rows": [json.dumps([{"uid": 1}])], "seen": ["[1]"]})
        self.assertEqual(said, "Nothing launched. Row 1 has no number.")
        self.assertEqual(banner[0], said)
        thread.assert_not_called()

    def test_missing_or_moved_panes_refuse_launch(self):
        self.assertEqual(page.move_problems([MOVE], ROWS, TREE), [])
        self.assertTrue(page.move_problems([dict(MOVE, source="p:gone")], ROWS, TREE))
        self.assertTrue(page.move_problems([dict(MOVE, anchor="r:2")], ROWS, TREE))
        self.assertEqual(page.shape_problems([MOVE], [SHAPE], ROWS, TREE), [])
        self.assertTrue(page.shape_problems([MOVE], [], ROWS, TREE))

    def test_changed_layout_stops_before_opening_panes(self):
        with patch.object(page.launch, "load", return_value=ROWS), patch.object(page.launch, "moves", return_value=[MOVE]), \
                patch.object(page.launch, "layouts", return_value=[SHAPE]), patch.object(page.iterm, "tree", return_value=[]), \
                patch.object(page.launch, "launcher", return_value=""), patch.object(page.launch, "place") as place, \
                patch.object(page.launch, "mark") as mark, patch.object(page.registry, "release"), patch.object(page.launch, "save"):
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
        with patch.object(page.launch, "load", return_value=ROWS), patch.object(page.launch, "moves", return_value=[MOVE]), \
                patch.object(page.launch, "layouts", return_value=[SHAPE]), patch.object(page.iterm, "tree", side_effect=[TREE, OPENED, OPENED]), \
                patch.object(page.launch, "launcher", return_value=""), patch.object(page.launch, "place", side_effect=place), \
                patch.object(page.iterm, "apply_layout", side_effect=arrange), patch.object(page.iterm, "close", side_effect=close), \
                patch.object(page.registry, "release"), patch.object(page.launch, "save"), \
                patch.object(page.launch, "mark", side_effect=mark), patch.object(page.launch, "start", side_effect=start), \
                patch.object(page.launch, "follow"):
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


def osa(code=0, out="1"):
    return SimpleNamespace(returncode=code, stdout=out, stderr="refused" if code else "")


class WrittenRowTest(unittest.TestCase):
    """Session 90's walker row: "n": 91, "model": "sonnet", "effort": "low"."""

    ROW = {"uid": 1, "n": 91, "name": "Site walker", "message": "/walk-drive site.",
           "model": "sonnet", "effort": "low"}

    def test_a_number_written_as_a_number_launches_as_two_digits(self):
        with patch.object(page, "save") as save, patch.object(page, "load", return_value=[]), \
                patch.object(page, "scheduled", return_value=""), patch.object(page.registry, "entries", return_value={}), \
                patch.object(page.iterm, "tree", return_value=TREE), patch.object(page.launch, "problems", return_value=[]), \
                patch.object(page.registry, "reserve", return_value=True) as reserve, \
                patch.object(page.launch, "claim", side_effect=lambda nn: os.open(os.devnull, os.O_RDONLY)), patch.object(page.launch, "begin"):
            said = page.take_for("90", [""])({"act": ["launch"], "rows": [json.dumps([self.ROW])], "seen": ["[1]"]})
        row = save.call_args.args[1][0]
        self.assertEqual((said, row["n"], reserve.call_args.args[0]), ("", "91", "91"))
        self.assertEqual((row["model"], row["effort"]), ("sonnet", "low"))

    def test_its_claim_is_seen_and_its_message_typed(self):
        row = dict(self.ROW)
        page.launch.fill([row], lambda _name: [], ("L:w", "L:t"), [], "90")
        rec = {"session_id": "s", "title": "91-site-walker", "pid": 1}
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(page.launch.registry, "folder", return_value=folder), \
                patch.object(page.launch.registry, "entries", return_value={"91": rec}), \
                patch.object(page.launch.registry, "claude_records", return_value={}), \
                patch.object(page.launch.registry, "pid_of", return_value=1), \
                patch.object(page.launch.registry, "watched", return_value=[]), \
                patch.object(page.launch.panes, "pane", return_value="p"), \
                patch.object(page.launch, "renamed", return_value=True), \
                patch.object(page.launch.time, "sleep"), \
                patch.object(page.launch.panes, "say", return_value=True) as say:
            self.assertTrue(page.launch.arrive(row, "p"))
            with open(os.path.join(folder, page.launch.NAMED)) as f:
                named = json.load(f)
        say.assert_called_once_with("p", "/walk-drive site.")
        self.assertEqual(named, {"model": "sonnet", "effort": "low"})

    def test_its_low_effort_rides_the_boot_line(self):
        line = page.launch.line({**self.ROW, "n": "91", "account": "1"})
        self.assertIn("--effort low", line)
        self.assertIn('"/0-session-start 91 Site walker"', line)

    def test_a_haiku_row_forces_haiku_subagents(self):
        with patch.object(page.launch.panes.accounts, "pinned", return_value=""):
            haiku = page.launch.line({**self.ROW, "n": "91", "account": "1", "model": "haiku"})
            sonnet = page.launch.line({**self.ROW, "n": "91", "account": "1"})
        self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 claude", haiku)
        self.assertNotIn("SUBAGENT", sonnet)


class CloneTest(unittest.TestCase):
    """Row 91 clones session 01, whose record says account 2, session id 34c5-abcd."""

    ROW = {"uid": 1, "n": "91", "name": "Site walker", "message": "/clone-session", "account": "3",
           "model": "sonnet", "effort": "low"}
    PROJECT = "-Users-me-Projects-my-project"

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.folders = {a: os.path.join(self.root, f"acct{a}") for a in ("2", "3")}
        self.src = os.path.join(self.folders["2"], "projects", self.PROJECT, "34c5-abcd.jsonl")
        os.makedirs(os.path.dirname(self.src))
        with open(self.src, "w") as f:
            f.write('{"type": "user"}\n')
        os.makedirs(os.path.join(self.root, "sessions", "01"))
        with open(os.path.join(self.root, "sessions", "01", "record.json"), "w") as f:
            json.dump({"session_id": "34c5-abcd", "account": "2", "transcript": self.src}, f)
        folder = lambda nn: os.path.join(self.root, "sessions", f"{int(nn):02d}")
        self.patch = patch.object(page.launch.registry, "folder", side_effect=folder)
        self.patch.start()
        # Accounts 2 and 3 are the test's own, never this Mac's list.
        self.known = patch.dict(page.launch.panes.CONFIG,
                                {a: f"CLAUDE_CONFIG_DIR={f} " for a, f in self.folders.items()})
        self.known.start()

    def tearDown(self):
        self.known.stop()
        self.patch.stop()

    def test_a_clone_row_resumes_its_target_forked(self):
        line = page.launch.line({**self.ROW, "clone": "01"})
        self.assertTrue(line.endswith(" --resume 34c5-abcd --fork-session"), line)
        self.assertIn('"/0-session-start 91 Site walker" --model', line)

    def test_a_row_without_clone_is_unchanged(self):
        line = page.launch.line(self.ROW)
        r = self.ROW
        self.assertEqual(line, page.launch.panes.boot_line(r["name"], r["account"], r["model"], r["effort"], r["n"]))
        self.assertNotIn("--resume", line)

    def test_a_clone_with_no_record_is_refused_in_one_sentence(self):
        self.assertEqual(page.launch.line({**self.ROW, "clone": "77"}), "")
        with patch.object(page.launch, "live", return_value=set()), \
                patch.object(page.launch.registry, "files", return_value=[]):
            said = page.launch.problems([{**self.ROW, "clone": "77"}])
        self.assertEqual(said, ["Row 1: Session 77 has no conversation to clone."])

    def test_another_accounts_clone_copies_its_transcript_and_keeps_the_original(self):
        target = page.launch.cloned("01")
        got = page.launch.carry(target, "3", self.folders)
        dest = os.path.join(self.folders["3"], "projects", self.PROJECT, "34c5-abcd.jsonl")
        self.assertEqual(got, dest)
        with open(dest) as a, open(self.src) as b:
            self.assertEqual((a.read(), b.read()), ('{"type": "user"}\n', '{"type": "user"}\n'))
        self.assertEqual(page.launch.carry(target, "2", self.folders), self.src)
        self.assertEqual(os.listdir(os.path.dirname(dest)), ["34c5-abcd.jsonl"])


class PillTest(unittest.TestCase):
    """A batch drafted on my page: System picks each pill once, then my press is final."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.file = os.path.join(self.folder, "launch.json")
        self.turns = iter(["1", "2", "3"] * 10)
        self.taken = []
        def take():
            self.taken.append(next(self.turns))
            return self.taken[-1]
        for p in (patch.object(page.launch, "path", return_value=self.file),
                  patch.object(page.accounts, "take", side_effect=take),
                  patch.object(page.launch, "default", return_value={"model": "claude-opus-5-5", "effort": "medium"}),
                  patch.object(page, "placed"), patch.object(page, "scheduled", return_value="")):
            p.start()
            self.addCleanup(p.stop)

    def press(self, rows, seen=None):
        said = page.take_for("77", [""])({"act": ["save"], "rows": [json.dumps(rows)],
                                          "seen": [json.dumps(seen or [r["uid"] for r in rows])]})
        self.assertEqual(said, "")
        return page.load("77")

    def test_a_row_written_naming_nothing_takes_system_once(self):
        with open(self.file, "w") as f:
            json.dump({"rows": [{"name": "a", "message": "Go."}, {"name": "b", "model": "sonnet", "message": "Go."}]}, f)
        first = page.load("77")
        self.assertEqual([(r["account"], r["model"], r["effort"]) for r in first],
                         [("1", "claude-opus-5-5", "medium"), ("2", "sonnet", "medium")])
        self.assertEqual(page.load("77"), first)
        self.assertEqual(self.taken, ["1", "2"])

    def test_my_account_on_a_later_row_of_ten_stays_as_i_set_it(self):
        rows = self.press([{"uid": u, "name": f"row {u}", "message": "Go."} for u in range(1, 11)])
        self.assertEqual([r["account"] for r in rows], ["1", "2", "3"] * 3 + ["1"])
        rows[6]["account"] = "2"
        rows = self.press(rows)
        # The order moves on, and the page saves a row it never saw filled.
        page.accounts.take()
        rows = self.press([{k: v for k, v in r.items() if k != "account"} if r["uid"] == 1 else r for r in rows])
        self.assertEqual(rows[6]["account"], "2")
        self.assertEqual([r["account"] for r in rows], ["1", "2", "3", "1", "2", "3", "2", "2", "3", "1"])
        self.assertEqual(len(self.taken), 11)

    def test_system_said_by_the_app_chat_is_systems_now_and_chromes_for_drive_chrome(self):
        row = {"uid": 1, "by": "app", "message": "Go.", "account": "2", "effort": "high"}
        self.assertEqual(page.system(row, "effort"), "medium")
        self.assertEqual(page.system({**row, "message": "/drive-chrome a"}, "account"), page.accounts.CHROME)


class LostLineTest(unittest.TestCase):
    """Session 17's boot line: iTerm refused the search while its window went full screen."""

    def test_a_refused_search_is_tried_again(self):
        with patch.object(page.panes.subprocess, "run", side_effect=[osa(1, ""), osa(0, ""), osa()]) as run, \
                patch.object(page.panes.time, "sleep"):
            self.assertTrue(page.panes.write("p", "x"))
            self.assertEqual(run.call_count, 3)

    def test_a_pane_never_found_reports_the_miss(self):
        with patch.object(page.panes.subprocess, "run", return_value=osa(0, "")) as run, \
                patch.object(page.panes.time, "sleep"):
            self.assertFalse(page.panes.say("p", "hello"))
            self.assertEqual(run.call_count, page.panes.TRIES)

    def test_a_timeout_is_never_typed_twice(self):
        late = page.panes.subprocess.TimeoutExpired("osascript", 20)
        with patch.object(page.panes.subprocess, "run", side_effect=late) as run, \
                patch.object(page.panes.time, "sleep"):
            self.assertFalse(page.panes.write("p", "x"))
            self.assertEqual(run.call_count, 1)

    def test_text_and_return_are_two_scripts(self):
        with patch.object(page.panes.subprocess, "run", return_value=osa()) as run, \
                patch.object(page.panes.time, "sleep"):
            self.assertTrue(page.panes.say("p", "hello"))
        scripts = [c.args[0][2] for c in run.call_args_list]
        self.assertEqual(len(scripts), 2)
        self.assertIn('"hello"', scripts[0])
        self.assertNotIn("character id 13", scripts[0])
        self.assertIn("character id 13", scripts[1])

    def arrive(self, programs):
        row = {"n": "99", "name": "t"}
        with patch.object(page.launch.hear, "until", return_value=False), \
                patch.object(page.launch.registry, "entries", return_value={}), \
                patch.object(page.launch.registry, "watched", return_value=[]), \
                patch.object(page.launch, "STARTED", 0), patch.object(page.launch.registry, "CLAIM", 0.2), \
                patch.object(page.launch, "line", return_value="boot"), \
                patch.object(page.launch.panes, "settle"), \
                patch.object(page.launch.panes, "programs", side_effect=programs), \
                patch.object(page.launch.panes, "say", return_value=True) as say:
            got = page.launch.arrive(row, "p")
        return got, row, say.call_count

    def test_no_claude_types_again_then_fails_saying_why(self):
        got, row, typed = self.arrive(lambda _pane: [])
        self.assertFalse(got)
        self.assertEqual(typed, page.launch.RETYPES)
        self.assertEqual(row["why"], "Claude never started in its pane.")

    def test_claude_running_is_left_to_claim(self):
        got, row, typed = self.arrive(lambda _pane: ["claude /0-session-start 99 t --model m"])
        self.assertFalse(got)
        self.assertEqual(typed, 0)
        self.assertEqual(row["why"], "99 never claimed its number.")


class LogTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.file = os.path.join(self.folder, "launch.json")
        self.log = os.path.join(self.folder, page.launch.LOG)
        self.row = {"uid": 1, "n": "17", "log": self.log}

    def lines(self):
        with open(self.log) as f:
            return [json.loads(line) for line in f]

    def test_a_step_is_one_line_with_its_answer(self):
        page.launch.note(self.row, "p", "boot line typed", False)
        got = self.lines()[0]
        self.assertEqual((got["n"], got["pane"], got["step"], got["answer"]), ("17", "p", "boot line typed", False))

    def test_a_row_with_no_log_writes_nothing(self):
        page.launch.note({"n": "17"}, "p", "step")
        self.assertEqual(os.listdir(self.folder), [])

    def test_a_refused_write_is_logged_with_iterm_words(self):
        with patch.dict(page.launch.WATCHED, {"p": self.row}), \
                patch.object(page.panes.subprocess, "run", side_effect=[osa(1, ""), osa()]), \
                patch.object(page.panes.time, "sleep"):
            self.assertTrue(page.panes.write("p", "x"))
        got = self.lines()
        self.assertEqual([(x["pane"], x["step"], x["answer"]) for x in got], [("p", "iTerm refused a write", "refused")])

    def test_a_log_that_cannot_be_written_stops_nothing(self):
        page.launch.note({"n": "17", "log": os.path.join(self.folder, "gone", "log")}, "p", "step")

    def test_last_row_launched_deletes_the_log(self):
        with patch.object(page.launch, "path", return_value=self.file):
            page.save("10", [{"uid": 1}, {"uid": 2}])
            page.launch.note(self.row, "p", "step")
            page.mark("10", 1, None)
            self.assertTrue(os.path.exists(self.log))
            page.mark("10", 2, None)
        self.assertEqual(os.listdir(self.folder), [])

    def test_a_failed_row_keeps_the_log(self):
        with patch.object(page.launch, "path", return_value=self.file):
            page.save("10", [{"uid": 1}])
            page.launch.note(self.row, "p", "step")
            page.mark("10", 1, "failed: no.")
        self.assertTrue(os.path.exists(self.log))

    def test_a_wait_ending_stops_watching_its_pane(self):
        with patch.dict(page.launch.WATCHED, {"p": self.row}), patch.object(page.launch, "arrive", return_value=True), \
                patch.object(page.launch, "mark"):
            page.follow("10", self.row, "p", "", {})
            self.assertNotIn("p", page.launch.WATCHED)


class LaunchAgainTest(unittest.TestCase):
    def test_only_a_pane_with_nothing_running_is_reused(self):
        with patch.object(page.launch.panes, "terminals", return_value={"p": "/dev/ttys1"}), \
                patch.object(page.launch.panes, "programs", return_value=[]):
            self.assertTrue(page.launch.reusable({"pane": "p"}))
            self.assertFalse(page.launch.reusable({"pane": "gone"}))
            self.assertFalse(page.launch.reusable({}))
        with patch.object(page.launch.panes, "terminals", return_value={"p": "/dev/ttys1"}), \
                patch.object(page.launch.panes, "programs", return_value=["vim"]):
            self.assertFalse(page.launch.reusable({"pane": "p"}))

    def test_a_failed_row_keeps_its_pane_and_its_neighbour(self):
        tree = [{"window": "w", "tabs": [{"tab": "t", "root": {"split": "columns", "children": [
            {"pane": "mine"}, {"pane": "next"}]}}]}]
        row = {"at": {"anchor": "r:8", "side": "left"}, "win": "N1", "tab": "N1"}
        with patch.object(page.launch.iterm, "tree", return_value=tree):
            keep = page.launch.kept(row, "mine", {"8": "next"})
        self.assertEqual(keep, {"pane": "mine", "win": "L:w", "tab": "L:t",
                                "at": {"anchor": "p:next", "side": "left"}})
        page.launch.settle([{**row, **keep, "uid": 7}], tree, "")

    def test_a_kept_pane_is_retyped_with_no_new_pane(self):
        row = {"uid": 7, "n": "17", "pane": "mine", "status": "booting"}
        with patch.object(page.launch, "load", return_value=[row]), patch.object(page.launch, "moves", return_value=[]), \
                patch.object(page.launch, "layouts", return_value=[]), patch.object(page.launch, "launcher", return_value=""), \
                patch.object(page.launch, "reusable", return_value=True), \
                patch.object(page.launch, "place") as place, patch.object(page.launch, "start") as start, \
                patch.object(page.launch, "follow"), patch.object(page.launch, "save"), patch.object(page.registry, "release"):
            page.go("10")
        place.assert_not_called()
        self.assertEqual(start.call_args.args[1], "mine")


class ErrorTest(unittest.TestCase):
    def test_an_error_opening_a_row_ends_only_that_row(self):
        rows = [{"uid": 1, "n": "02", "account": "1", "status": "booting"},
                {"uid": 2, "n": "03", "account": "1", "status": "booting"}]
        def place(r, *_):
            if r["uid"] == 1:
                raise RuntimeError("boom")
            return "new"
        with patch.object(page.launch, "load", return_value=rows), patch.object(page.launch, "moves", return_value=[]), \
                patch.object(page.launch, "layouts", return_value=[]), patch.object(page.launch, "launcher", return_value=""), \
                patch.object(page.launch, "place", side_effect=place), patch.object(page.launch, "start") as start, \
                patch.object(page.launch, "follow"), patch.object(page.launch, "mark") as mark, patch.object(page.launch, "save"), \
                patch.object(page.registry, "release"), patch.object(page.traceback, "print_exc"):
            page.go("10")
        marks = {c.args[1]: c.args[2] for c in mark.call_args_list}
        self.assertIn("boom", marks[1])
        self.assertEqual(marks[2], "booting")
        self.assertEqual(start.call_count, 1)

    def test_a_row_left_booting_never_locks_the_page(self):
        rows = [{"uid": 1, "n": "02", "status": "booting"}]
        with patch.object(page.launch, "load", return_value=rows), patch.object(page.launch, "opening", side_effect=RuntimeError), \
                patch.object(page.launch, "save") as save, patch.object(page.registry, "release") as release, \
                patch.object(page.traceback, "print_exc"):
            page.go("10")
        release.assert_called_once_with("02")
        self.assertTrue(save.call_args.args[1][0]["status"].startswith("failed: its launch stopped on an error"))

    def test_an_error_while_waiting_fails_the_row_with_its_words(self):
        row = {"uid": 1, "n": "02"}
        with patch.object(page.launch, "arrive", side_effect=KeyError("gone")), \
                patch.object(page.launch, "kept", return_value={"pane": "p"}), patch.object(page.launch, "mark") as mark, \
                patch.object(page.registry, "release") as release, patch.object(page.traceback, "print_exc"):
            page.follow("10", row, "p", "", {})
        release.assert_called_once_with("02")
        self.assertIn("gone", mark.call_args.args[2])
        self.assertEqual(mark.call_args.args[3], {"pane": "p"})


class OnlyTest(unittest.TestCase):
    """The app door's Launch names its own rows: only those launch."""

    ROWS = [{"uid": 1, "n": "04", "name": "mine", "status": "failed: it stopped."},
            {"uid": 2, "n": "05", "name": "cache", "by": "app"}]

    def press(self, form):
        with patch.object(page, "save") as save, patch.object(page, "load", return_value=[]), \
                patch.object(page, "placed"), patch.object(page, "scheduled", return_value=""), \
                patch.object(page.launch, "problems", return_value=[]), \
                patch.object(page.registry, "reserve", return_value=True) as reserve, \
                patch.dict(page.KEPT, {"00": (TREE, "", [])}), patch.object(page.launch, "claim", side_effect=lambda nn: os.open(os.devnull, os.O_RDONLY)), \
                patch.object(page.launch, "begin") as thread:
            said = page.take_for("00", [""])(form)
        return said, save.call_args.args[1], [c.args[0] for c in reserve.call_args_list], thread.called

    def test_a_launch_naming_rows_boots_only_those(self):
        said, rows, reserved, started = self.press({"act": ["launch"], "rows": [json.dumps(self.ROWS)],
                                                    "seen": ["[1, 2]"], "only": ["[2]"]})
        self.assertEqual((said, reserved, started), ("", ["05"], True))
        self.assertEqual(rows[0]["status"], "failed: it stopped.")
        self.assertEqual(rows[1]["status"], "booting")
        self.assertEqual(rows[1]["by"], "app")

    def test_a_launch_naming_rows_waits_on_planned_moves(self):
        said, rows, reserved, started = self.press({"act": ["launch"], "rows": [json.dumps(self.ROWS)],
                                                    "seen": ["[1, 2]"], "only": ["[2]"], "moves": [json.dumps([MOVE])]})
        self.assertEqual(said, "Nothing launched. This page plans pane moves, which wait for its own Launch.")
        self.assertEqual((reserved, started), ([], False))
        self.assertNotIn("status", rows[1])

    def test_a_fault_names_its_row_on_the_whole_page(self):
        rows = [dict(r) for r in self.ROWS]
        with patch.object(page.launch, "problems", return_value=["Row 1: a number is 01 to 99.",
                                                                 "Row 2: 05 is on another row too."]):
            self.assertEqual(page.faults(rows, [rows[1]]), ["Row 2: 05 is on another row too."])


# One process marking one row of a page's file, 150 times over. With the
# lock of one process alone, two of them lost a mark in one run of three.
MARKER = """
import importlib.util, sys
spec = importlib.util.spec_from_file_location("launch_page_marker", sys.argv[1])
page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page)
page.path = page.launch.path = lambda nn: sys.argv[2]
# The lock sits on the sessions folder, which a fresh copy of the layer lacks.
page.launch.registry.WORK = page.launch.os.path.dirname(sys.argv[2])
for step in range(150):
    page.mark("77", int(sys.argv[3]), f"step {step}")
"""


class FileTest(unittest.TestCase):
    """The page's file: read whole, written whole, and never written over unread."""

    def setUp(self):
        self.file = os.path.join(tempfile.mkdtemp(), "launch.json")
        p = patch.object(page.launch, "path", return_value=self.file)
        p.start()
        self.addCleanup(p.stop)

    def test_a_file_caught_half_written_is_read_again(self):
        with open(self.file, "w") as f:
            f.write('{"rows": [{"uid": 1, "na')

        def finish():
            time.sleep(0.05)
            with open(self.file, "w") as f:
                json.dump({"rows": [{"uid": 1, "name": "a"}]}, f)
        threading.Thread(target=finish).start()
        self.assertEqual(page.read("77"), [{"uid": 1, "name": "a"}])

    def test_a_file_that_never_reads_shows_no_row_and_is_never_written_over(self):
        with open(self.file, "w") as f:
            f.write('{"rows": [')
        self.assertEqual(page.read("77"), [])
        with self.assertRaises(page.Unreadable):
            page.save("77", [])
        with self.assertRaises(page.Unreadable):
            page.mark("77", 1, None)
        with open(self.file) as f:
            self.assertEqual(f.read(), '{"rows": [')

    def test_a_save_keeps_the_files_birth(self):
        page.save("77", [{"uid": 1, "name": "a"}])
        an_hour_ago = time.time() - 3600
        os.utime(self.file, (an_hour_ago, an_hour_ago))
        born = os.stat(self.file).st_birthtime
        page.save("77", [{"uid": 1, "name": "b"}])
        self.assertEqual(os.stat(self.file).st_birthtime, born)
        self.assertGreater(os.stat(self.file).st_mtime, an_hour_ago + 3000)
        self.assertEqual(page.read("77")[0]["name"], "b")

    def test_four_processes_marking_rows_lose_none(self):
        page.save("77", [{"uid": uid, "name": f"row {uid}"} for uid in (1, 2, 3, 4)])
        four = [subprocess.Popen([sys.executable, "-B", "-c", MARKER, path, self.file, str(uid)]) for uid in (1, 2, 3, 4)]
        self.assertEqual([p.wait(timeout=120) for p in four], [0, 0, 0, 0])
        self.assertEqual([r["status"] for r in page.read("77")], ["step 149"] * 4)


class RunTest(unittest.TestCase):
    """One launch of a page at a time: its lock, held across processes."""

    def test_a_held_lock_refuses_a_second_launch_until_it_is_let_go(self):
        fd = page.launch.claim("78")
        self.assertGreaterEqual(fd, 0)
        self.assertEqual(page.launch.claim("78"), -1)
        held = subprocess.run([sys.executable, "-B", "-c", HOLDS, page.launch.held_at("78")], capture_output=True, text=True)
        self.assertEqual(held.stdout.strip(), "held")
        os.close(fd)
        self.assertFalse(page.launch.running("78"))

    def test_a_launch_whose_lock_is_held_elsewhere_runs_nothing(self):
        fd = page.launch.claim("79")
        try:
            with patch.object(page.launch, "go") as go:
                page.launch.run("79")
            go.assert_not_called()
        finally:
            os.close(fd)


# Another process, asking whether a page's launch lock is held.
HOLDS = """
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDWR)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    print("free")
except OSError:
    print("held")
"""


if __name__ == "__main__":
    unittest.main()
