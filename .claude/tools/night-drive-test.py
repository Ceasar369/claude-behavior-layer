#!/usr/bin/env python3
"""Check the night drive's readiness check, its take and its accounts, on a
made-up repository of its own, never a real seat."""

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
import accounts  # noqa: E402
import drive  # noqa: E402
import finish  # noqa: E402
import registry  # noqa: E402

spec = importlib.util.spec_from_file_location("night_drive_tool_test", os.path.join(HERE, "night-drive.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

RUN = "  Run: `test -f out.txt` → prints nothing, exit 0\n"
CHOSEN = {"account": "1", "model": "haiku", "effort": "low"}


class NightDriveTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        work = os.path.join(self.root.name, ".claude", "state", "sessions")
        state = os.path.join(self.root.name, ".claude", "state", "finish")
        os.makedirs(os.path.join(work, "05"))
        os.makedirs(state)
        soon = int(time.time()) + 3600
        for a, pct in (("1", 40), ("2", 100), ("3", 10)):
            with open(os.path.join(state, f"limits-{a}.json"), "w") as f:
                json.dump({"five_hour": {"used_percentage": pct, "resets_at": soon},
                           "seven_day": {"used_percentage": pct // 2, "resets_at": soon},
                           "seven_day_opus": {"used_percentage": 5, "resets_at": soon}}, f)
        for p in (patch.object(registry, "ROOT", self.root.name), patch.object(registry, "WORK", work),
                  patch.object(finish, "STATE", state), patch.object(accounts, "KNOWN", ["1", "2", "3"]),
                  patch.object(accounts, "read", lambda: {"order": ["2", "1"], "next": 0}),
                  patch.object(accounts, "pinned", lambda a: "sonnet" if a == "3" else ""),
                  patch.object(accounts, "model", lambda: "haiku")):
            p.start()
            self.addCleanup(p.stop)

    def put(self, rel: str, body) -> None:
        p = os.path.join(self.root.name, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body if isinstance(body, str) else json.dumps(body))

    def mission(self, at: str, mid: str, name: str, body: str = "", objectives: str = "- [ ] out.txt exists\n" + RUN,
                **choices) -> dict:
        folder = f"{at}/missions"
        self.put(f"{folder}/{mid}-{name}.md", body or f"# {mid} — {name}\n\nWrite out.txt.\n")
        if objectives is not None:
            self.put(f"{folder}/{mid}-objectives.md", f"# {mid} — {name} · objectives\n\n{objectives}")
        return {"id": mid, "name": name, "file": f"{folder}/{mid}-{name}.md", **(choices or CHOSEN)}

    def plan(self, at: str, stages: list, finish_lines=("Done. Run: `test -f out.txt` → exit 0",), **extra) -> None:
        self.put(f"{at}/stages.json", {**extra, "stages": [{"name": f"Stage {chr(65 + i)}", "missions": ms}
                                                           for i, ms in enumerate(stages)],
                                       "finish": [{"line": l, "state": "red"} for l in finish_lines]})

    def run_tool(self, *argv):
        out = io.StringIO()
        code = 0
        with patch.object(sys, "argv", ["night-drive.py", *argv]), patch.object(sys, "stdout", out):
            try:
                tool.main()
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
                out.write(str(e.code) if not isinstance(e.code, int) else "")
        return out.getvalue(), code

    def test_a_complete_plan_passes(self):
        at = ".claude/state/sessions/05"
        self.plan(at, [[self.mission(at, "A1", "one")], [self.mission(at, "B1", "two")]])
        said, code = self.run_tool("check", "05")
        self.assertEqual(code, 0, said)
        self.assertIn("Ready: every line holds.", said)
        self.assertNotIn("fails", said)
        # Only the windows that apply: no Opus runs, so its own window stays out.
        self.assertIn("Account 1, 2 launches: five_hour 40% used", said)
        self.assertNotIn("seven_day_opus", said)
        self.assertIn("System's default, for extra work.", said)

    def test_a_plan_with_one_gap_of_each_kind_is_refused(self):
        at = ".claude/state/sessions/05"
        self.plan(at, [[
            self.mission(at, "A1", "notes", body="# A1 — notes · notes\n\nIt will write out.txt.\n"),
            self.mission(at, "A2", "bare", objectives=None),
            self.mission(at, "A3", "look", objectives="- [ ] The page reads well\n  Yours: the page, on 1100\n"),
            self.mission(at, "A4", "think", body="# A4 — think\n\nRun `/3-thinker` with me.\n"),
            self.mission(at, "A5", "unset", account="1", model="haiku"),
            self.mission(at, "A6", "pinned", account="3", model="opus", effort="high"),
        ]], finish_lines=("The page reads well.",), kind="open")
        self.put(f"{at}/teams.json", {"teams": [
            {"seat": "50", "name": "late team", "waits": ["60"], "launch": [], **CHOSEN},
            {"seat": "60", "name": "first team", "launch": [{"line": "The trunk stands.", "state": "red"}]}]})
        self.put(f"{at}/waves/wave-1.md", "# Wave 1\nsent: no\n\n## An item\nquestion: Which?\n")
        said, code = self.run_tool("check", "05")
        self.assertEqual(code, 1)
        for gap in ("Session 05's plan is open: its stages close on my word alone.",
                    "Team 50's plan is not written: .claude/state/sessions/05/night-drive/50/stages.json holds no mission.",
                    "Team 50 waits on teams 60, with no launch list",
                    "A1's mission is still notes",
                    "A2 has no objectives file",
                    "A3's objective on line 3 is a Yours line",
                    "finish line 1 has no Run command: The page reads well.",
                    "Team 60: launch-list line 1 has no Run command: The trunk stands.",
                    "A4 needs me while it runs (/3-thinker)",
                    "A5 names no effort.",
                    "A6 runs opus on account 3, pinned to sonnet.",
                    "Team 60's row names no account and no model and no effort.",
                    "Session 05's wave 1 is open: send it, or close it."):
            self.assertIn(gap, said)
        self.assertIn("Not ready", said)
        # Opus runs now, so its own window shows.
        self.assertIn("seven_day_opus 5% used", said)

    def test_no_plan_at_all_is_refused(self):
        said, code = self.run_tool("check", "05")
        self.assertEqual(code, 1)
        self.assertIn("Session 05 holds no plan", said)

    def test_start_runs_only_once_ready(self):
        _, code = self.run_tool("start", "05")
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(registry.folder("05"), "night-drive", "drive.json")))
        at = ".claude/state/sessions/05"
        self.plan(at, [[self.mission(at, "A1", "one")]])
        said, code = self.run_tool("start", "05")
        self.assertEqual(code, 0, said)
        self.assertTrue(os.path.isfile(os.path.join(registry.folder("05"), "night-drive", "drive.json")))
        said, code = self.run_tool("end", "05")
        self.assertIn("Session 05's night drive ended.", said)
        self.assertFalse(os.path.exists(os.path.join(registry.folder("05"), "night-drive")))

    def test_an_unread_window_shows_as_unread(self):
        os.remove(os.path.join(finish.STATE, "limits-1.json"))
        at = ".claude/state/sessions/05"
        self.plan(at, [[self.mission(at, "A1", "one")]])
        said, code = self.run_tool("check", "05")
        self.assertEqual(code, 0, said)
        self.assertIn("Account 1, 1 launch: five_hour unread; seven_day unread.", said)

    def test_extra_work_leaves_a_capped_default(self):
        # Account 2 is the order's next, and capped: account 1 has the most left
        # that runs haiku, since account 3 is pinned to sonnet.
        self.assertEqual(self.run_tool("account", "05")[0].strip(), "1")
        with patch.object(accounts, "pinned", lambda a: ""):
            self.assertEqual(self.run_tool("account", "05")[0].strip(), "3")
        with patch.object(accounts, "read", lambda: {"order": ["2", "1"], "next": 1}):
            self.assertEqual(self.run_tool("account", "05")[0].strip(), "1")

    def test_a_team_takes_its_plan_whole(self):
        at = ".claude/state/sessions/05/night-drive/50"
        m = self.mission(at, "A1", "one", body=f"# A1 — one\n\nYour objectives are in `{at}/missions/A1-objectives.md`.\n")
        self.plan(at, [[{**m, "queued": "2026-11-13T20:00:00", "session": "51"}]])
        self.put(".claude/state/sessions/05/teams.json", {"teams": [{"seat": "50", "name": "late team", **CHOSEN}]})
        said, code = self.run_tool("take", "50", "05")
        self.assertEqual(code, 1)
        self.assertIn("Session 50 has no folder.", said)
        os.makedirs(registry.folder("50"))
        said, code = self.run_tool("take", "50", "05")
        self.assertEqual(code, 1)
        self.assertIn("Seat 50 is not claimed yet.", said)
        self.put(".claude/state/sessions/50/record.json", {"number": "50"})
        said, code = self.run_tool("take", "50", "05")
        self.assertEqual(code, 0, said)
        self.assertIn("Team 50 holds its plan: 1 stages, 1 missions.", said)
        with open(os.path.join(registry.folder("50"), "stages.json")) as f:
            got = json.load(f)["stages"][0]["missions"][0]
        self.assertEqual(got["file"], ".claude/state/sessions/50/missions/A1-one.md")
        self.assertNotIn("session", got)
        with open(os.path.join(registry.folder("50"), "missions", "A1-one.md")) as f:
            self.assertIn(".claude/state/sessions/50/missions/A1-objectives.md", f.read())
        self.assertFalse(os.path.exists(os.path.join(self.root.name, at)))
        self.assertTrue(os.path.isfile(os.path.join(registry.folder("50"), "night-drive", "drive.json")))
        said, code = self.run_tool("take", "50", "05")
        self.assertEqual(code, 1)

    def test_a_team_row_stands_alone_on_the_page(self):
        at = ".claude/state/sessions/05/night-drive/50"
        self.plan(at, [[self.mission(at, "A1", "one")]])
        self.put(".claude/state/sessions/05/teams.json", {"teams": [{"seat": "50", "name": "late team", **CHOSEN}]})
        said, code = self.run_tool("row", "05", "50")
        self.assertEqual(code, 0, said)
        with open(os.path.join(registry.folder("05"), "launch.json")) as f:
            rows = json.load(f)["rows"]
        self.assertEqual(rows, [{"n": "50", "name": "late team", "message": "/night-drive take 05", **CHOSEN}])
        said, code = self.run_tool("row", "05", "50")
        self.assertEqual(code, 1)
        self.assertIn("launch page holds rows", said)

    def test_the_check_lists_each_pause_point(self):
        at = ".claude/state/sessions/05"
        self.plan(at, [[{**self.mission(at, "A1", "one"), "pause": True}], [self.mission(at, "B1", "two")]])
        with open(os.path.join(self.root.name, at, "stages.json")) as f:
            p = json.load(f)
        p["stages"][0]["pause"] = True
        self.put(f"{at}/stages.json", p)
        said, code = self.run_tool("check", "05")
        self.assertEqual(code, 0, said)
        self.assertIn("Pause points:\n  Session 05's plan: after A1.\n  Session 05's plan: after stage A.\n", said)

    def test_a_night_plan_pauses_at_its_point_and_resumes_there(self):
        # A night drive over one team drives its plan through drive.py: its
        # pause point fires there, the drive started by the check.
        spec = importlib.util.spec_from_file_location("drive_tool_night_test", os.path.join(HERE, "drive.py"))
        drive_tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drive_tool)
        at = ".claude/state/sessions/05"
        self.plan(at, [[self.mission(at, "A1", "one")], [self.mission(at, "B1", "two")]])
        with open(os.path.join(self.root.name, at, "stages.json")) as f:
            p = json.load(f)
        p["stages"][0]["pause"] = True
        self.put(f"{at}/stages.json", p)
        self.assertEqual(self.run_tool("start", "05")[1], 0)
        self.put(f"{at}/drive.json", {"drive": "plan", "state": "running", "taken": "2026-11-13T20:00:00",
                                      "closed": {}})
        gone = [("A", [({"id": "A1", "name": "one", "session": "06"}, True)]), ("B", [({"id": "B1", "name": "two"}, False)])]

        def tool_run(verb, words=""):
            out, code = io.StringIO(), 0
            with patch.object(sys, "argv", ["drive.py", verb, "05", *(["A"] if verb == "close" else [])]), \
                    patch.object(sys, "stdin", io.StringIO(words)), patch.object(sys, "stdout", out), \
                    patch.object(drive_tool, "stages", lambda nn: gone), \
                    patch.object(registry, "entries", return_value={}), \
                    patch.object(registry, "claude_records", return_value={}):
                try:
                    drive_tool.main()
                except SystemExit as e:
                    code = e.code
            return out.getvalue(), code

        said, code = tool_run("close", "A1 wrote its file.")
        self.assertEqual(code, drive.PAUSED, said)
        self.assertIn("Pause point reached: after stage A. Nothing new launches.", said)
        self.assertNotIn("kick off stage B", said)
        said, code = tool_run("resume")
        self.assertEqual(code, 0, said)
        self.assertIn("Next: kick off stage B.", said)

    def test_a_pause_before_a_team_holds_its_launch_until_resumed(self):
        at = ".claude/state/sessions/05/night-drive/50"
        self.plan(at, [[self.mission(at, "A1", "one")]])
        self.put(".claude/state/sessions/05/night-drive/drive.json", {"started": "2026-11-13T20:00:00",
                                                                      "state": "running"})
        self.put(".claude/state/sessions/05/teams.json", {"teams": [
            {"seat": "40", "name": "trunk team", **CHOSEN},
            {"seat": "50", "name": "late team", "pause": True, **CHOSEN}]})
        self.put(".claude/state/sessions/40/drive.json", {"drive": "plan", "state": "ended"})
        said, code = self.run_tool("check", "05")
        self.assertIn("  Before team 50 launches.", said)
        page = os.path.join(registry.folder("05"), "launch.json")
        said, code = self.run_tool("row", "05", "50")
        self.assertEqual(code, drive.PAUSED, said)
        self.assertIn("Pause point reached: before team 50 launches. Nothing new launches.", said)
        self.assertIn("Finished: team 40.", said)
        self.assertFalse(os.path.exists(page))
        said, code = self.run_tool("row", "05", "50")
        self.assertEqual(code, 1)
        self.assertIn("The night drive is paused before team 50", said)
        self.assertFalse(os.path.exists(page))
        said, code = self.run_tool("resume", "05")
        self.assertIn("Resumed. Next: `python3 .claude/tools/night-drive.py row 05 50`", said)
        said, code = self.run_tool("row", "05", "50")
        self.assertEqual(code, 0, said)
        self.assertIn("Team 50's row is on session 05's launch page.", said)
        self.assertTrue(os.path.isfile(page))


if __name__ == "__main__":
    unittest.main()
