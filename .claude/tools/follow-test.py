#!/usr/bin/env python3
"""Check follows, drives and their one wait on seats in a folder of their own, never a real seat."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import drive  # noqa: E402
import finish  # noqa: E402
import follow  # noqa: E402
import handover  # noqa: E402
import hear  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402
import transcripts  # noqa: E402


def tool(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wait_tool = tool("transcript_tool_test", os.path.join(HERE, "transcript.py"))
follow_tool = tool("follow_tool_test", os.path.join(HERE, "follow.py"))
clarify = tool("clarify_page_test", os.path.join(HERE, "clarify-page.py"))
unwatched = tool("unwatched_test", os.path.join(os.path.dirname(HERE), "hooks", "unwatched.py"))

SID = {"01": "aaaaaaaa-0000-0000-0000-000000000001", "10": "aaaaaaaa-0000-0000-0000-000000000010",
       "11": "aaaaaaaa-0000-0000-0000-000000000011", "12": "aaaaaaaa-0000-0000-0000-000000000012"}
NEW = "bbbbbbbb-0000-0000-0000-000000000010"
TURNS = [("User", "17:00", ["go"], "2026-10-29T17:00:00"),
         ("Session 10", "17:01", ["asked"], "2026-10-29T17:01:00"),
         ("User", "17:02", ["yes"], "2026-10-29T17:02:00"),
         ("Session 10", "17:03", ["done it"], "2026-10-29T17:03:00")]


class Seats(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.held = {n: {"number": n, "title": f"{n}-test", "session_id": SID[n],
                         "transcript": os.path.join(self.work.name, f"{SID[n]}.jsonl"), "claimed": "2026-10-29T16:00:00"}
                     for n in SID}
        for n, rec in self.held.items():
            os.makedirs(os.path.join(self.work.name, n), exist_ok=True)
            with open(rec["transcript"], "w") as f:
                f.write("{}\n")
        for p in (patch.object(registry, "WORK", self.work.name),
                  patch.object(registry, "entries", side_effect=lambda: self.held),
                  patch.object(registry, "claude_records", return_value={}),
                  patch.object(transcripts, "turns", return_value=TURNS),
                  patch.object(drive, "state", return_value="")):
            p.start()
            self.addCleanup(p.stop)
        for n, rec in self.held.items():
            with open(os.path.join(registry.folder(n), registry.RECORD), "w") as f:
                json.dump(rec, f)

    def claim(self, nn, sid, title=""):
        """Another session claims NN: its record, written as a claim writes it."""
        self.held[nn] = {**self.held[nn], "session_id": sid, "title": title or self.held[nn]["title"]}
        with open(os.path.join(registry.folder(nn), registry.RECORD), "w") as f:
            json.dump(self.held[nn], f)

    def handed(self, nn, old_sid, new_sid):
        """Seat NN handed over: its successor holds it, its copy names the old session."""
        os.makedirs(os.path.join(registry.folder(nn), handover.HANDOVERS), exist_ok=True)
        with open(os.path.join(registry.folder(nn), handover.HANDOVERS, "1.md"), "w") as f:
            f.write(f"# {nn}-test\n\nTranscript: /x/{old_sid}.jsonl\nTurns: 4.\n")
        self.claim(nn, new_sid)


class RecordsTest(Seats):
    def test_a_follow_reads_only_what_comes_after_its_newest_turn(self):
        got = follow.take("01", "10", "approve checks", "10 reports")
        self.assertEqual(got["bookmark"], "2026-10-29T17:03:00")
        self.assertEqual(got["session"], SID["10"])
        self.assertEqual(set(follow.following("01")), {"10"})

    def test_a_follow_taken_again_keeps_its_place_and_takes_the_new_words(self):
        follow.take("01", "10", "a", "b")
        follow.update("01", follow.path("01"), lambda d: d["10"].update({"bookmark": "2026-10-29T17:05:00"}))
        got = follow.take("01", "10", "c", "d")
        self.assertEqual((got["for"], got["bookmark"]), ("c", "2026-10-29T17:05:00"))

    def test_a_handover_successor_is_the_same_session(self):
        follow.take("01", "10", "a", "b")
        self.handed("10", SID["10"], NEW)
        self.assertEqual(set(follow.following("01")), {"10"})

    def test_a_reused_number_is_another_session_even_with_the_same_title(self):
        follow.take("01", "10", "a", "b")
        self.claim("10", NEW)
        self.assertEqual(follow.following("01"), {})

    def test_a_stopped_session_drops_out(self):
        follow.take("01", "10", "a", "b")
        del self.held["10"]
        self.assertEqual(follow.following("01"), {})

    def test_what_the_same_session_read_moves_its_bookmark_on_its_next_arming(self):
        follow.take("01", "10", "a", "b")
        follow.read("01", follow.path("01"), {"10": "2026-10-29T17:09:00"}, SID["01"])
        self.assertEqual(follow.records(follow.path("01"))["10"]["bookmark"], "2026-10-29T17:03:00")
        follow.armed("01", follow.path("01"), SID["01"])
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["bookmark"], "2026-10-29T17:09:00")
        self.assertNotIn("read", got)

    def test_a_successor_reads_again_what_its_predecessor_read(self):
        follow.take("01", "10", "a", "b")
        follow.read("01", follow.path("01"), {"10": "2026-10-29T17:09:00"}, SID["01"])
        follow.armed("01", follow.path("01"), NEW)
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["bookmark"], "2026-10-29T17:03:00")
        self.assertNotIn("read", got)


class DriveTest(Seats):
    def test_a_drive_reads_from_the_newest_turn_and_replaces_the_follow(self):
        follow.take("01", "11", "a", "b")
        self.assertEqual(successor.take("01", ["11"], "fix the typos"), [])
        self.assertEqual(follow.following("01"), {})
        got = successor.taken("01")["11"]
        self.assertEqual((got["topic"], got["bookmark"], got["session"]),
                         ("fix the typos", "2026-10-29T17:02:00", SID["11"]))

    def test_a_reused_number_is_never_shown_driven(self):
        successor.take("01", ["11"], "t")
        self.assertEqual(successor.drivers(), {"11": "01"})
        self.claim("11", NEW)
        self.assertEqual(successor.drivers(), {})

    def test_a_take_from_before_identities_were_kept_still_drives(self):
        with open(successor.path("01"), "w") as f:
            json.dump({"11": {"topic": "", "taken": "2026-10-29T16:52:13"}}, f)
        self.assertEqual(successor.drivers(), {"11": "01"})

    def test_a_follow_of_a_driven_session_is_refused(self):
        successor.take("01", ["11"], "t")
        self.assertIn("you drive it", follow_tool.refused("01", "11"))
        self.assertIn("this seat", follow_tool.refused("01", "01"))
        self.assertIn("no session", follow_tool.refused("01", "44"))
        self.assertEqual(follow_tool.refused("01", "12"), "")

    def test_a_seat_that_only_follows_hands_itself_over(self):
        self.assertFalse(successor.driving("01"))
        follow.take("01", "10", "a", "b")
        self.assertTrue(successor.driving("01"))
        wrap = tool("wrap_up_test", os.path.join(os.path.dirname(HERE), "hooks", "wrap-up.py"))
        out = io.StringIO()
        with patch.object(wrap.context, "last", return_value=(1, 1)), \
                patch.object(wrap.context, "share", return_value=90), patch.object(wrap.context, "wrapup", return_value=80), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"], "transcript_path": "x"}))), \
                redirect_stdout(out):
            wrap.main()
        self.assertIn("hand yourself over", json.loads(out.getvalue())["hookSpecificOutput"]["additionalContext"])

    def test_the_successor_arms_the_one_wait(self):
        follow.take("01", "10", "a", "b")
        self.assertIn(successor.WAIT, handover.message("01"))

    def test_a_partial_drive_band_names_its_topic(self):
        self.assertEqual(clarify.band("01", "fix the typos"),
                         "01 drives this session on fix the typos. Items off it are yours.")
        self.assertEqual(clarify.band("01", ""), "01 drives this session, and answers this wave.")
        self.assertEqual(clarify.band("", "x"), "")


class CapTest(Seats):
    def test_a_seat_that_follows_is_resumed_with_its_own_line(self):
        follow.take("01", "10", "a", "b")
        with patch.object(registry, "tail", return_value=[]):
            self.assertEqual(finish.driving(), {"01": 0})
        self.assertEqual(finish.line("01"), finish.LIFTED)
        with patch.object(drive, "state", return_value="running"):
            self.assertEqual(finish.line("01"), drive.RESUME)

    def test_a_paused_drive_is_never_typed_into(self):
        follow.take("01", "10", "a", "b")
        with patch.object(drive, "state", return_value="paused"), patch.object(registry, "tail", return_value=[]):
            self.assertEqual(finish.driving(), {})


class WaitTest(Seats):
    def run_wait(self, kinds, limit=0):
        """The one wait, its finishes read off `kinds`, every hear answered at once."""
        def read(n, mark=""):
            k = kinds.get(n, "working")
            return finish.found(k, "2026-10-29T17:10:00" if k in ("asking", "done") else None)
        out = io.StringIO()
        with patch.object(finish, "read", side_effect=read), \
                patch.object(hear, "until", side_effect=lambda check, *a, **k: check()), \
                patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": SID["01"]}), redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], limit)
        return out.getvalue()

    def test_a_finish_wakes_it_and_is_kept_as_read(self):
        follow.take("01", "10", "approve checks", "10 reports")
        successor.take("01", ["11"], "fix the typos")
        said = self.run_wait({"10": "asking"})
        self.assertTrue(said.startswith("Woke on 10."))
        self.assertIn("you follow it for: approve checks. It ends when: 10 reports", said)
        self.assertIn("you drive it on: fix the typos", said)
        self.assertTrue(said.rstrip().endswith("Wait again."))
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["read"], {"to": "2026-10-29T17:10:00", "by": SID["01"]})

    def test_a_stopped_session_and_a_reused_number_are_released(self):
        follow.take("01", "10", "a", "b")
        successor.take("01", ["11"], "t")
        del self.held["10"]
        self.claim("11", NEW, "11-other")
        said = self.run_wait({})
        self.assertIn("State: stopped. The wait released it.", said)
        self.assertIn("another session holds 11 now, 11-other. The wait released it.", said)
        self.assertTrue(said.rstrip().endswith("Following and driving nothing."))
        self.assertEqual((follow.records(follow.path("01")), successor.taken("01")), ({}, {}))

    def test_a_number_claimed_while_it_read_stopped_is_told_as_another_session(self):
        follow.take("01", "10", "a", "b")
        on = wait_tool.seat("01")
        self.claim("10", NEW, "10-other")
        out = io.StringIO()
        with patch.object(wait_tool, "seat_wait", return_value=(
                on, {"10": ""}, {"10": finish.found("stopped")}, ["10"], False, [])), redirect_stdout(out):
            wait_tool.seat_run("01", SID["01"], 0)
        self.assertIn("another session holds 10 now, 10-other. The wait released it.", out.getvalue())
        self.assertEqual(follow.records(follow.path("01")), {})

    def test_a_gone_session_is_told_once(self):
        follow.take("01", "10", "a", "b")
        with patch.object(wait_tool, "GRACE", 0):
            said = self.run_wait({"10": "gone"})
            self.assertIn("Woke on 10.", said)
            self.assertIn("It stays yours until it is resumed", said)
            again = self.run_wait({"10": "gone"})
        self.assertIn("at its limit", again)
        self.assertIn("As told before.", again)

    def test_a_gone_session_told_before_never_spins_the_wait(self):
        follow.take("01", "10", "a", "b")
        follow.update("01", follow.path("01"), lambda d: d["10"].update({"gone": SID["10"]}))
        asked = []

        def until(check, files=(), pids=(), seconds=0):
            asked.append(seconds)
            time.sleep(min(seconds, 0.2))
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", return_value=finish.found("gone")), \
                patch.object(hear, "until", side_effect=until), patch.object(wait_tool, "GRACE", 0.1), \
                redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 1)
        self.assertIn("at its limit", out.getvalue())
        self.assertLess(len(asked), 15)

    def idle_run(self, mark, seed=True):
        """The one wait over a followed 10 and a driven 11, both idle since
        `mark`, IDLE two seconds. Each hear's seconds are kept in self.asked."""
        if seed:
            follow.take("01", "10", "a", "b")
            successor.take("01", ["11"], "t")
            for p in (follow.path("01"), successor.path("01")):
                follow.update("01", p, lambda d: [r.update({"bookmark": mark}) for r in d.values()])
        self.asked = []

        def until(check, files=(), pids=(), seconds=0):
            self.asked.append(seconds)
            time.sleep(min(seconds, 0.3))
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", return_value=finish.found("idle")), \
                patch.object(hear, "until", side_effect=until), patch.object(wait_tool.wake, "IDLE", 2), \
                redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 3)
        return out.getvalue()

    def test_a_driven_session_idle_wakes_it_once_and_a_followed_one_never(self):
        said = self.idle_run(time.strftime(wait_tool.STAMP))
        self.assertTrue(said.startswith("Woke on 11, idle."))
        again = self.idle_run("", seed=False)
        self.assertTrue(again.startswith("Woke at its limit"))
        self.assertLess(len(self.asked), 15)

    def test_an_idle_stretch_due_while_no_wait_ran_wakes_it_at_once(self):
        said = self.idle_run(time.strftime(wait_tool.STAMP, time.localtime(time.time() - 3)))
        self.assertTrue(said.startswith("Woke on 11, idle."))
        self.assertEqual(self.asked, [])

    def test_an_idle_stretch_already_woken_on_wakes_nothing_again(self):
        mark = time.strftime(wait_tool.STAMP, time.localtime(time.time() - 3))
        self.idle_run(mark)
        said = self.idle_run(mark, seed=False)
        self.assertTrue(said.startswith("Woke at its limit"))
        self.assertLess(len(self.asked), 15)

    def test_the_named_wait_wakes_once_per_idle_stretch_too(self):
        now = time.time()
        self.assertGreater(wait_tool.idle_at(time.strftime(wait_tool.STAMP, time.localtime(now - 60)), now), now)
        self.assertEqual(wait_tool.idle_at(time.strftime(wait_tool.STAMP, time.localtime(now - 400)), now), 0)
        self.assertEqual(wait_tool.idle_at("", now), 0)

    def test_a_second_wait_on_a_seat_is_refused(self):
        follow.take("01", "10", "a", "b")
        import fcntl
        fd = os.open(os.path.join(registry.folder("01"), "wakes.log"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertIn("A wait already runs for seat 01", self.run_wait({"10": "asking"}))
        finally:
            os.close(fd)

    def test_a_seat_following_nothing_waits_on_nothing(self):
        self.assertEqual(self.run_wait({}).strip(), "Following and driving nothing.")

    def test_a_take_while_it_waits_joins_it(self):
        follow.take("01", "10", "a", "b")
        calls = []

        def until(check, *a, **k):
            if not calls:
                calls.append(1)
                follow.take("01", "12", "c", "d")
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", side_effect=lambda n, m="": finish.found(
                "asking" if n == "12" else "working", "2026-10-29T17:10:00")), \
                patch.object(hear, "until", side_effect=until), redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 60)
        self.assertTrue(out.getvalue().startswith("Woke on 12."))


class HoldTest(Seats):
    def test_the_one_wait_covers_everything_and_a_named_one_its_own(self):
        procs = {500: (100, "python3 .claude/tools/transcript.py wait --awake"),
                 501: (100, "python3 .claude/tools/transcript.py wait 12 --since 2026-10-29T17:08:34 --awake")}
        with patch.object(unwatched.ports, "table", return_value=procs):
            self.assertEqual(unwatched.waits(100), [None, {"12"}])

    def test_a_follower_with_no_wait_is_held_once(self):
        follow.take("01", "10", "a", "b")
        live = {SID["01"]: {"pid": 100}, SID["10"]: {"pid": 200}}
        out = io.StringIO()
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(unwatched, "waits", return_value=[{"12"}]), \
                patch.object(unwatched.handover, "progress", return_value={}), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"]}))), redirect_stdout(out):
            unwatched.main()
        said = json.loads(out.getvalue())
        self.assertEqual(said["decision"], "block")
        self.assertIn("session 10", said["reason"])
        self.assertIn(successor.WAIT, said["reason"])

    def test_the_one_wait_running_passes(self):
        follow.take("01", "10", "a", "b")
        live = {SID["01"]: {"pid": 100}, SID["10"]: {"pid": 200}}
        out = io.StringIO()
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(unwatched, "waits", return_value=[None]), \
                patch.object(unwatched.handover, "progress", return_value={}), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"]}))), redirect_stdout(out):
            with self.assertRaises(SystemExit):
                unwatched.main()
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
